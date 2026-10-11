#!/bin/bash
# remote_deltah_both_tr25.sh -- A ROUGH T = 25 TRANSITION WITH BOTH CHILD PENALTIES (11 October; the author: "after the
# deltah benchmark and TF runs finish, maybe we can try to do 1 T=30 transition, but it doesnt have to be exact. even
# just 1-2 runs using the converged T=70 transition without deltah to have it close to the true transition...and we
# can see if then if the welfare gain persists"; then "ok, we can do T=25 instead. it's just for a robustness check").
#
# RUN IT IN THE SAME CONTAINER AS code/deltah/remote_deltah_both.sh, AFTER that script reports 'arm tf ACCEPTED': it
# reuses the solved benchmark (code/cfarm_bench), the accepted Housing First arm (code/cfarm_null_2c) and the accepted
# Treatment First arm (code/cfarm_tf_2c), so nothing is re-solved but one short no-policy pass. Stages, each skipped
# when its output is on disk:
#   B' Housing First re-solved on cf_fix2_share_both (cf_fix2 plus the one write of newborn_parent_share_counter.dat,
#      with deltah/patch_both.py), STARTED FROM the accepted null arm's distribution and price, so it converges in a
#      pass or two; it gives the path its t = 1 parent share. The accepted arm is kept as code/cfarm_null_2c_acc and
#      the two arms' net revenues are compared.
#   D  the transition binary: the paper's T = 70 source (transition_fix/tr70_src.f90) with patch_both and
#      transition_length 25, compiled -O3 as the paper's binary was; staged by transition_fix/stage_tr_fix.sh with
#      SHARE_LEN=208 (four child classes: 52 employment states x 2 x 2); the seeds are the paper's T = 70 loop 2 path
#      (results/transition_2c_t70/loop2, the paper's pin) for periods 1 to 24, each price's distance from its Housing
#      First value scaled by the ratio of this economy's terminal distance to the paper's.
#   E  the path, stopped after loop MAX_LOOP (default 1: two loops, as the author asked); each loop archived to
#      results/deltah_both_tr25/loop<N>/.
# WHY T = 25: the transition keeps every period's value function; at four times the paper's state that is about
# 0.35 GiB a period on top of about 18 GiB fixed, so T = 25 is about 27 GiB, inside 15 GiB of RAM plus the 24 GiB of
# swap remote_deltah_both.sh made. Rough, as asked: the SUD stock is only nine tenths of the way down by year 27 on the
# paper's path, so the terminal condition binds before the path is done.
#
# START IT FROM THE REPO ROOT IN THE BACKGROUND:  nohup bash code/deltah/remote_deltah_both_tr25.sh > /tmp/tr25.front.log 2>&1 &
# and run the same command again whenever it is stopped: it ATTACHES to the running work. Every 20 minutes it pushes
# results/deltah_both_tr25/status.txt with 'delta_h both T=25:' commits.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltah_both_tr25
mkdir -p "$R"
D=$C/deltah_both_tr25_worker
BREF=$C/deltah_both_benchref
T25=$C/tr25_both
MAIN=$C/tr_both_t25
SEEDS=$REPO/results/transition_2c_t70/loop2
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0.24;penalty_child_homeless 0.31"
HORIZON=25
MAX_LOOP=${MAX_LOOP:-1}
P_TF_MAIN=0.85551291; V_TF_MAIN=0.096152024      # the paper's Treatment First long run, the T = 70 path's terminal values
V_NULL=0.067533863                               # Housing First's pi_V, the benchmark's in both economies

note() { echo "remote_deltah_both_tr25: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR25_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltah_both_tr25: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( TR25_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr25.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltah_both_tr25: started detached, pid $(cat "$D.pid"); log /tmp/tr25.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltah_both_tr25: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

tr_digest() (
    L=$1/run.log; [ -f "$L" ] || exit 0
    python3 - "$L" <<'PYEOF'
import re, sys
L = open(sys.argv[1], errors='replace').read().splitlines()
loops = {}
for l in L:
    m = re.search(r'TRANSITION BUDGET loop=\s*(\d+)\s+t=\s*(\d+).*residual=\s*(\S+)', l)
    if m:
        d = loops.setdefault(int(m.group(1)), {'t': 0, 'bud': 0.0, 'drug': 0.0})
        t = int(m.group(2)); d['t'] = max(d['t'], t)
        if t > 1: d['bud'] = max(d['bud'], abs(float(m.group(3))))
    m = re.search(r'TRANSITION DRUG t=\s*(\d+)\s+distance=\s*(\S+)', l)
    if m and loops:
        d = loops[max(loops)]; d['drug'] = max(d['drug'], abs(float(m.group(2))))
saved = [int(x) for x in re.findall(r'TRANSITION PATHS SAVED after loop\s+(\d+)', '\n'.join(L))]
cev = [l for l in L if 'TRANSITION CEV t=           1 ' in l]
better = [l for l in L if 'TRANSITION BETTER OFF t=           1 ' in l]
for k in sorted(loops):
    d = loops[k]
    print(f"  loop {k}: periods to {d['t']}, worst budget residual (t>1) {d['bud']:.2e}, worst drug gap {d['drug']:.2e}"
          + ('  [paths saved]' if k in saved else ''))
if cev: print('  latest', cev[-1].strip())
if better: print('  latest', better[-1].strip())
PYEOF
)
memline() { echo "rss $(ps -o rss= -p "$1" 2>/dev/null | awk '{printf "%.1f", $1/1048576}') GiB, swap used $(free -m | awk '/Swap/{printf "%.1f", $3/1024}') GiB"; }
publish() (
    {
        echo "# a rough T = $HORIZON transition with BOTH child penalties (code/deltah/remote_deltah_both_tr25.sh; delta_d 0.24, delta_h 0.31); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -d "$MAIN" ] && { echo; echo "== T = $HORIZON"; tr_digest "$MAIN"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_h both T=25: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
cd "$C"
git -C "$REPO" config user.name >/dev/null 2>&1 || git -C "$REPO" config user.name "Claude"
git -C "$REPO" config user.email >/dev/null 2>&1 || git -C "$REPO" config user.email "noreply@anthropic.com"

# WHAT THIS STAGE NEEDS FROM remote_deltah_both.sh, IN THIS CONTAINER
grep -q "arm tf ACCEPTED" "$C/deltah_both_run.status" 2>/dev/null || { note "GUARD: remote_deltah_both.sh has not reported 'arm tf ACCEPTED' in this container"; publish "failed"; exit 1; }
[ -d "$C/cfarm_null_2c_acc" ] || [ -d "$C/cfarm_null_2c" ] || { note "GUARD: no accepted null arm (code/cfarm_null_2c)"; publish "failed"; exit 1; }
for f in "$C/cfarm_tf_2c/cf.log" "$C/cfarm_tf_2c/PARAM_HANDOVER.arm.txt" "$C/cf_fix2/cf.f90" "$C/bench_both/hftf_bench" "$BREF/bench_files.tar.gz"; do
    [ -s "$f" ] || { note "GUARD: $f missing"; publish "failed"; exit 1; }
done
for k in "penalty_child_addicted 0.24" "penalty_child_homeless 0.31"; do
    grep -q "^$k" "$C/cfarm_tf_2c/PARAM_HANDOVER.arm.txt" || { note "GUARD: the tf arm's handover lacks '$k'"; publish "failed"; exit 1; }
done
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, swap $(free -g | awk '/Swap/{print $2}') GiB, cores $(nproc)"

# THE BUILDS: the share build with both penalties, the T = 25 binary with both penalties
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
if [ ! -x "$C/cf_fix2_share_both/hftf_cf_prod" ]; then
    note "building cf_fix2_share_both"
    [ -s "$C/cf_fix2_share/cf.f90" ] || GEN_ONLY=1 bash transition_fix/build_cf_fix2_share.sh > /tmp/tr25_build_share.log 2>&1 || { note "GUARD: generating cf_fix2_share failed: $(tail -3 /tmp/tr25_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    mkdir -p "$C/cf_fix2_share_both"
    python3 deltah/patch_both.py "$C/cf_fix2_share/cf.f90" "$C/cf_fix2_share_both/cf.f90" > /tmp/tr25_patch_share.log 2>&1 || { note "GUARD: patch_both did not apply to cf_fix2_share: $(tail -3 /tmp/tr25_patch_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q 'unit=421' "$C/cf_fix2_share_both/cf.f90" || { note "GUARD: cf_fix2_share_both lost the share write"; publish "failed"; exit 1; }
    ( cd "$C/cf_fix2_share_both" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ -x "$C/cf_fix2_share_both/hftf_cf_prod" ] && ! grep -q Error "$C/cf_fix2_share_both/build_prod.err" || { note "GUARD: cf_fix2_share_both did not compile"; publish "failed"; exit 1; }
fi
if [ ! -x "$T25/hftf_tr_prod" ]; then
    note "building the T = $HORIZON transition with both penalties"
    mkdir -p "$T25"
    python3 deltah/patch_both.py transition_fix/tr70_src.f90 "$T25/tr_patched.f90" > /tmp/tr25_patch_tr.log 2>&1 || { note "GUARD: patch_both did not apply to the transition source: $(tail -3 /tmp/tr25_patch_tr.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    n=$(grep -c "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$T25/tr_patched.f90")
    [ "$n" = 1 ] || { note "GUARD: transition_length 70 found $n times in the patched source"; publish "failed"; exit 1; }
    sed "s/parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$/parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*$HORIZON/" "$T25/tr_patched.f90" > "$T25/tr.f90"
    grep -q "solve_transition_dynamics\*$HORIZON$" "$T25/tr.f90" || { note "GUARD: transition_length not set to $HORIZON"; publish "failed"; exit 1; }
    grep -q "integer, parameter :: child_penalty_classes=4" "$T25/tr.f90" || { note "GUARD: the transition is not the four-class build"; publish "failed"; exit 1; }
    ( cd "$T25" && gfortran -O3 -funroll-loops $COMMON tr.f90 -o hftf_tr_prod 2> build_prod.err )
    [ -x "$T25/hftf_tr_prod" ] && ! grep -q Error "$T25/build_prod.err" || { note "GUARD: the transition did not compile: $(grep -m3 Error "$T25/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "tr25_both built: $(md5sum "$T25/hftf_tr_prod" | cut -c1-8)"
fi
publish "built"

# STAGE B': HOUSING FIRST ON THE SHARE BUILD, from the accepted null arm, for the t = 1 parent share
[ -d "$C/cfarm_null_2c_acc" ] || mv "$C/cfarm_null_2c" "$C/cfarm_null_2c_acc"
NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c_acc/cf.log" | tail -1 | awk '{print $2}')
P0=$(grep -a "^ *price_of_addictive_good=" "$C/cfarm_null_2c_acc/cf.log" | tail -1 | awk '{print $2}')
python3 -c "import sys; float('$NT'); p=float('$P0'); sys.exit(0 if 0.3<p<1.5 else 1)" || { note "GUARD: no net revenue or price in the accepted null arm ('$NT', '$P0')"; publish "failed"; exit 1; }
if [ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] && tail -5 "$C/cfarm_null_2c.out" 2>/dev/null | grep -q "DIST CHECK PASS"; then
    note "share null arm already done"
else
    sed 's/cf_fix2_both) ;;/cf_fix2_both|cf_fix2_share_both) ;;/' deltah/cf_arm_both.sh > deltah/cf_arm_both_tr25.sh
    grep -q "cf_fix2_share_both) ;;" deltah/cf_arm_both_tr25.sh || { note "GUARD: could not admit cf_fix2_share_both"; publish "failed"; exit 1; }
    export BENCH_FROM=$BREF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
    export OMP_NUM_THREADS=4 SEED_FROM=cfarm_null_2c_acc DIAG_TAG=_2c BENCH_BIN=$C/bench_both/hftf_bench
    note "null arm on cf_fix2_share_both, seeded from the accepted null arm, price $P0"
    env BUILD=cf_fix2_share_both DRUG_PRICE_START=$P0 EXTRA_SET="$PENALTIES" sh deltah/cf_arm_both_tr25.sh null > "$C/cfarm_null_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        kill -0 "$P" 2>/dev/null && publish "share null arm running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_null_2c/cf.log" 2>/dev/null) passes; $(memline "$(pgrep -f hftf_cf | head -1)")"
    done
    wait "$P"
    O="$C/cfarm_null_2c.out"
    tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "VOUCHER CHECK PASS" "$O" && ! grep -q GUARD "$O" || { note "GUARD: the share null arm was not accepted: $(tail -3 "$O" | tr '\n' ' ')"; publish "failed"; exit 1; }
    [ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share_both"; publish "failed"; exit 1; }
fi
NT2=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
note "share null arm net revenue $NT2 against the accepted null arm's $NT (relative $(python3 -c "print('%.1e' % (float('$NT2')/float('$NT')-1))")); the budget target is the accepted one"
mkdir -p "$R/arm_null_share"; gzip -c "$C/cfarm_null_2c/cf.log" > "$R/arm_null_share/cf.log.gz"
publish "share null arm done"

# STAGE D: THE PATH, staged from the accepted Treatment First arm and the share null arm, seeded from the paper's T = 70
if [ ! -d "$MAIN" ]; then
    SHARE_LEN=208 bash transition_fix/stage_tr_fix.sh "$MAIN" "$T25/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NT" > /tmp/tr25_stage.log 2>&1 || { note "GUARD: staging failed: $(tail -3 /tmp/tr25_stage.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=$HORIZON, $((HORIZON - 1)) periods" /tmp/tr25_stage.log || { note "GUARD: staging did not read T = $HORIZON: $(grep seeds /tmp/tr25_stage.log)"; publish "failed"; exit 1; }
    python3 - "$MAIN" "$SEEDS" "$HORIZON" "$P_TF_MAIN" "$V_TF_MAIN" "$V_NULL" <<'PYEOF' || { note "GUARD: seeding failed"; publish "failed"; exit 1; }
import sys
n, seeds, T, p_main, v_main, v0 = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
for name, kind in (('drug_price', 'p'), ('pi_v', 'v')):
    vals = [float(l) for l in open(f'{seeds}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(vals) == 69, (name, len(vals))
    flat = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(flat) == T - 1 and max(flat) - min(flat) < 1e-15, (name, len(flat))
    term = flat[0]                       # this economy's terminal value, from the accepted tf arm
    if kind == 'p':
        k = (term - 1.0) / (p_main - 1.0)
        new = [1.0 + (x - 1.0) * k for x in vals[:T - 1]]
    else:
        k = (term - v0) / (v_main - v0)
        new = [v0 + (x - v0) * k for x in vals[:T - 1]]
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f" # {name} path: the paper's T = 70 loop 2 path for periods 1 to {T-1}, its distance from "
                f"{'one' if kind == 'p' else 'Housing First'} scaled by {k:.6f} to this economy's terminal value {term:.9f}\n")
        f.writelines(f'{x:25.15f}\n' for x in new)
    print(f'{name}: scale {k:.4f}, t=1 {new[0]:.6f}, t={T-1} {new[-1]:.6f}, terminal {term:.6f}')
PYEOF
    note "T = $HORIZON staged: $(tail -2 /tmp/tr25_stage.log | tr '\n' ' '); seeds from the paper's T = 70 loop 2 path, rescaled"
fi

# STAGE E: THE PATH, two loops
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "transition already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "transition running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"; done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "RELAUNCH after a killed run"
    fi
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    for k in "penalty_child_addicted 0.24" "penalty_child_homeless 0.31"; do
        grep -q "^$k" "$MAIN/PARAM_HANDOVER.txt" || { note "GUARD: the transition's handover lacks '$k'"; publish "failed"; exit 1; }
    done
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = $HORIZON transition started, pid $(cat "$D.main.pid"); it will be stopped after loop $MAX_LOOP"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER penalty_child_homeless" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no penalty HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a 'HANDOVER penalty_child' "$MAIN/run.log" | tr -s ' ' | tr '\n' ';')"
fi
publish "T = $HORIZON running"
archived=-1
while alive "$D.main.pid"; do
    for _ in $(seq 1 120); do alive "$D.main.pid" || break; sleep 10; done
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        mkdir -p "$R/loop$last"
        gzip -c "$MAIN/run.log" > "$R/loop$last/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop$last/" 2>/dev/null
        archived=$last
        note "loop $last complete, archived to results/deltah_both_tr25/loop$last"
        if [ "$last" -ge "$MAX_LOOP" ]; then
            pkill -P "$(cat "$D.main.pid")" 2>/dev/null; pkill -f "$MAIN/hftf" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
            note "stopped after loop $last, as planned"
            break
        fi
    fi
    alive "$D.main.pid" && publish "T = $HORIZON running; $(memline "$(pgrep -f "$MAIN/hftf\|./hftf" | head -1)")"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz" 2>/dev/null
note "transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null || echo "stopped after loop $archived")"
publish "T = $HORIZON ended"
