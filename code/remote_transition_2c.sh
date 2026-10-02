#!/bin/bash
# remote_transition_2c.sh -- STAGE E: THE T = 60 TRANSITION FROM HOUSING FIRST TO TREATMENT FIRST ON THE
# omega_c = 0.085 ECONOMY, for one cloud worker (2 October; the author: "And you can start the transition",
# and earlier "make sure to include the changes we made in the transition of TF as well"). Every change of
# the long-run arms is in it because the terminal state IS the long-run arm: pi_V clearing the budget, the
# test at $35, detection 85 per cent, no false positives, the three-year exclusion, the omega_c = 0.085
# two-class benchmark (results/reference/hf_2c_omega_0.085).
#
# WHY IT RE-SOLVES THE TWO ARMS. The transition reads the reform arm's own *counter_arm.* files as its
# terminal state and the no-policy arm's distribution and newborn parent share as its t = 0
# (transition_fix/stage_tr_fix.sh, TRANSITION_LESSONS.md section 16). The accepted arms
# (results/counterfactuals_2c/nulltf/null, tf85_c35/tf) ran in containers that are gone, so both are
# solved again here from their own equilibria (one to three passes each): the no-policy run on
# cf_fix2_share, which also writes newborn_parent_share_counter.dat, and Treatment First on cf_fix2 with
# tf85_c35's settings. Each must reproduce its accepted run to the checks' tolerance (compared below).
#
# THE ORDER IS TRANSITION_LESSONS.md's: the no-policy arm, the FLAT CONTROL (T = 10, both ends the
# no-policy steady state, adjust_taxes 1; it must stay flat), then the reform path. The flat control
# passed on 26 September on the old economy; the source has changed since, so it is run again. It runs
# beside the Treatment First re-solve (2 + 2 threads); the T = 60 path runs alone, 4 threads (peak about
# 10 GiB).
#
# THE SEEDS: never flat at the terminal value (TRANSITION_LESSONS, 27 September). The price and pi_V paths
# of the old transition's loop 0 (code/trtf60/restart3g_loop0/seeds_out, copied into
# code/transition_2c/seeds_old), rescaled so each starts from the new no-policy value and ends at the new
# Treatment First value: new(t) = new_T + (old(t) - old_T) (new_0 - new_T) / (old_0 - old_T).
#
# ALSO WRITES, for the paper (the author, 2 October: "share of newborns in favor of the tf policy... and
# share of all household who gain from it"): transition_2c/shares.py on the two arms (Treatment First
# against the no-policy run, state by state, weighted by the no-policy distribution, with a tolerance), and
# the value at 26 by productivity node of both (welfare_by_employment_youngestcounter_arm.txt), which the
# long-run prose's 'times as much at the lowest as at the highest' needs.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/remote_transition_2c.sh
# Run the same command again whenever the call is stopped: it ATTACHES to the running worker. Every 20
# minutes it pushes results/transition_2c/status.txt; each completed transition loop is archived to
# results/transition_2c/loop<N>/ (run.log.gz and the seeds it wrote).
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/transition_2c
mkdir -p "$R"
D=$C/tr2c_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
NET_TARGET=5.8918410999831181                 # the accepted no-policy run's net revenue (tf85_c35's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
P_TF=0.85551291;  V_TF=0.096152024            # results/counterfactuals_2c/tf85_c35/tf/final.txt
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
FLAT=$C/tr2c_flat10
MAIN=$C/tr2c_t60

note() { echo "remote_transition_2c: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR2C_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_transition_2c: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( TR2C_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr2c.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_transition_2c: started detached, pid $(cat "$D.pid"); log /tmp/tr2c.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_transition_2c: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

# the transition's progress: per loop, the periods done, the worst drug-market and budget gaps, CEV at t=1
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
publish() (
    {
        echo "# stage E, the T = 60 transition on the omega_c = 0.085 arms; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null; }
        done
        [ -d "$FLAT" ] && { echo; echo "== flat control (T = 10)"; tr_digest "$FLAT"; }
        for M in "$MAIN" "$MAIN"_r*; do [ -d "$M" ] && { echo; echo "== $(basename "$M") (T = 60)"; tr_digest "$M"; }; done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "transition 2c: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# arm <name> <build> [VAR=value ...]: one steady state in code/cfarm_<name>_2c, in the background
arm() {
    a=$1; b=$2; shift 2
    note "arm $a on $b: $*"
    ( cd "$C" && env BUILD="$b" OMP_NUM_THREADS=2 "$@" sh transition_2c/cf_arm_tr2c.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 ) &
    echo $! > "$D.arm_$a.pid"
}
arm_ok() {   # <name> <check>: the arm exited with its checks passed
    O="$C/cfarm_${1}_2c.out"
    tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "$2" "$O" && ! grep -q "GUARD" "$O"
}
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
wait_publishing() {   # <pid file> <label>: publish every 20 minutes while it runs
    while alive "$1"; do
        for _ in $(seq 1 120); do alive "$1" || break; sleep 10; done
        alive "$1" && publish "$2"
    done
}

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

# THE BUILDS, one at a time: the two counterfactual builds, the parent-share copy, T = 60 and T = 10
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/tr2c_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/tr2c_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > /tmp/tr2c_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 /tmp/tr2c_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/tr60_fix/hftf_tr_prod" ] || [ ! "$C/tr60_fix/hftf_tr_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ]; then
    note "building tr60_fix"
    bash transition_fix/build_tr60_fix.sh > /tmp/tr2c_build_tr60.log 2>&1 || { note "GUARD: build tr60_fix failed: $(tail -3 /tmp/tr2c_build_tr60.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "tr60_fix: $(tail -3 /tmp/tr2c_build_tr60.log | tr '\n' ' ')"
fi
if [ ! -x "$C/tr10_fix/hftf_tr_prod" ] || [ ! "$C/tr10_fix/hftf_tr_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ]; then
    note "building tr10_fix"
    bash transition_2c/build_tr10_fix2.sh > /tmp/tr2c_build_tr10.log 2>&1 || { note "GUARD: build tr10_fix failed: $(tail -3 /tmp/tr2c_build_tr10.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "tr10_fix: $(tail -3 /tmp/tr2c_build_tr10.log | tr '\n' ' ')"
fi
publish "built"

# THE TWO ARMS. The no-policy run first, alone until it has unpacked the shared benchmark (cfarm_bench),
# then Treatment First beside it.
if ! arm_ok null "VOUCHER CHECK PASS"; then
    arm null cf_fix2_share DRUG_PRICE_START=$P_NULL
    # until the no-policy arm has compiled the shared binaries and unpacked the shared benchmark: two arms
    # compiling bench/hftf_bench or cf/hftf_cf_prod at once would write the same files
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_null.pid"; do sleep 10; done
fi
if ! arm_ok tf "TARGET CHECK PASS"; then
    arm tf cf_fix2 PDET=0.85 NET_TARGET="$NET_TARGET" PV_START=$V_TF DRUG_PRICE_START=$P_TF EXTRA_SET="cost_per_drug_test $CTEST"
fi
wait_publishing "$D.arm_null.pid" "arms running"
arm_ok null "VOUCHER CHECK PASS" || { note "GUARD: the no-policy re-solve failed its checks: $(tail -3 "$C/cfarm_null_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
[ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share"; publish "failed"; exit 1; }
note "no-policy re-solve ACCEPTED: $(grep -a 'CHECK PASS' "$C/cfarm_null_2c.out" | tr '\n' ' ')"
publish "no-policy arm done"

# THE FLAT CONTROL, beside the Treatment First re-solve
if [ ! -f "$FLAT/FLAT_DONE" ]; then
    rm -rf "$FLAT"
    bash transition_fix/stage_tr_fix.sh "$FLAT" "$C/tr10_fix/hftf_tr_prod" "$C/cfarm_null_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr2c_stage_flat.log 2>&1 || { note "GUARD: staging the flat control failed: $(tail -3 /tmp/tr2c_stage_flat.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    # the budget test on, as in the 26 September control (the no-policy arm itself ran with adjust_taxes 0)
    for f in PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt; do sed -i 's/^adjust_taxes .*/adjust_taxes 1/' "$FLAT/$f"; done
    grep -qx "adjust_taxes 1" "$FLAT/PARAM_HANDOVER.txt" || { note "GUARD: adjust_taxes not set in the flat control"; publish "failed"; exit 1; }
    note "flat control staged: $(tail -2 /tmp/tr2c_stage_flat.log | tr '\n' ' ')"
    ( cd "$FLAT" && OMP_NUM_THREADS=2 ./hftf > run.log 2>&1; echo "exit $?" > FLAT_EXIT ) &
    echo $! > "$D.flat.pid"
    wait_publishing "$D.flat.pid" "flat control running"
    python3 - "$FLAT/run.log" > "$R/flat10.txt" <<'PYEOF'
import re, sys
L = open(sys.argv[1], errors='replace').read()
W = [(int(t), float(w)) for t, w in re.findall(r'TRANSITION WELFARE loop=\s*\d+\s+t=\s*(\d+)\s+with_childhood=\s*(\S+)', L)]
B = [abs(float(r)) for t, r in re.findall(r'TRANSITION BUDGET loop=\s*\d+\s+t=\s*(\d+).*residual=\s*(\S+)', L) if int(t) > 1]
G = [abs(float(g)) for g in re.findall(r'TRANSITION DRUG t=\s*\d+\s+distance=\s*(\S+)', L)]
ss = 787.49609051968014   # the accepted no-policy run's welfare with childhood
w1 = [w for t, w in W if t == 1]
dw = max(abs(w - ss) for t, w in W) if W else float('nan')
ok = bool(W) and bool(w1) and abs(w1[-1] - ss) < 0.01 and dw < 0.05 and (max(B) if B else 0) < 1e-3 and (max(G) if G else 0) < 5e-3
print(f"FLAT CONTROL {'PASS' if ok else 'FAIL'}: welfare at t=1 {w1[-1] if w1 else float('nan'):.5f} against the steady state's {ss:.5f}, "
      f"largest deviation {dw:.5f} utils (1 per cent CEV is about 0.34); worst budget residual {max(B) if B else 0:.2e} (rule 1e-3); "
      f"worst drug gap {max(G) if G else 0:.2e} (rule 5e-3)")
PYEOF
    gzip -c "$FLAT/run.log" > "$R/flat10_run.log.gz"
    note "$(cat "$R/flat10.txt")"
    touch "$FLAT/FLAT_DONE"
    # its copies of the two steady states are no longer needed (disk): the log and the paths stay
    find "$FLAT" -name '*.dat' -size +10M -delete
    publish "flat control done"
fi

wait_publishing "$D.arm_tf.pid" "Treatment First re-solve running"
arm_ok tf "TARGET CHECK PASS" || { note "GUARD: the Treatment First re-solve failed its checks: $(tail -3 "$C/cfarm_tf_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
note "Treatment First re-solve ACCEPTED: $(grep -a 'CHECK PASS' "$C/cfarm_tf_2c.out" | tr '\n' ' ')"
for a in null tf; do
    mkdir -p "$R/arm_$a"
    python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $( [ $a = tf ] && echo "$C/cfarm_null_2c/cf.log" ) > "$R/arm_$a/final.txt" 2>&1
    gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R/arm_$a/cf.log.gz"
    cp "$C/cfarm_${a}_2c/welfare_by_employment_youngestcounter_arm.txt" "$R/arm_$a/value_at_26_by_node.txt" 2>/dev/null
done
note "against the accepted runs: $(python3 - "$R" "$REPO/results/counterfactuals_2c" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
r, a = sys.argv[1], sys.argv[2]
out = []
for mine, acc in (('arm_null', 'nulltf/null'), ('arm_tf', 'tf85_c35/tf')):
    x, y = lv(f'{r}/{mine}/final.txt'), lv(f'{a}/{acc}/final.txt')
    worst = max(abs(x[k] / y[k] - 1) for k in ('drug price', 'pi_V (voucher probability)', 'drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k))
    out.append(f'{mine} worst relative difference {worst:.1e}')
print('; '.join(out))
PYEOF
)"
( cd "$C" && python3 transition_2c/shares.py cfarm_tf_2c cfarm_null_2c counter_arm > "$R/shares.txt" 2>&1
  python3 transition_2c/shares.py cfarm_tf_2c cfarm_tf_2c baseline_benchmark > "$R/shares_vs_benchmark_strict.txt" 2>&1 )
note "shares written: $(grep 'all households' "$R/shares.txt" | head -1)"
# HOMELESSNESS BY ANY AGE RANGE (the author, 2 October: 26-38 and 39-50 rather than the log's ten-year bands):
# exact from each arm's distribution and housing policy; reads only, about a minute
( cd "$C" && python3 transition_2c/age_split.py null=cfarm_null_2c:counter_arm tf=cfarm_tf_2c:counter_arm \
    > "$R/age_split.txt" 2>&1 ) || note "age_split FAILED: $(tail -2 "$R/age_split.txt" | tr '\n' ' ')"
note "age split: $(grep -c 'housing policy (exact)' "$R/age_split.txt") of 2 arms exact"
# THE NEWBORN'S VALUE AT BIRTH BY THE HOUSEHOLD IT IS BORN INTO (the author, 2 October: "restart" the age-1
# approval): code/cf_kid, from each arm's saved equilibrium, no re-solve. The large outputs stay in $C/newborn_2c
# (publish adds $R to git); only the summaries, the runs' output and the shares are copied into $R/newborn.
if [ ! -f "$C/newborn_2c/DONE" ]; then
    mkdir -p "$C/newborn_2c" "$R/newborn"
    if sh "$C/cf_kid/build.sh" > /tmp/tr2c_build_kid.log 2>&1; then
        for a in null tf; do
            THREADS=4 sh "$C/cf_kid/run_child_value.sh" "$C/cfarm_${a}_2c" "$C/newborn_2c/$a" > "$R/newborn/run_$a.out" 2>&1 \
                || note "cf_kid on $a FAILED: $(tail -2 "$R/newborn/run_$a.out" | tr '\n' ' ')"
            cp "$C/newborn_2c/$a"/child_value_summary*.txt "$R/newborn/summary_$a.txt" 2>/dev/null
        done
        python3 "$C/cf_kid/share_newborns.py" --tf "$C/newborn_2c/tf" --hf "$C/newborn_2c/null" \
            --json "$R/newborn/shares.json" > "$R/newborn/shares.txt" 2>&1 || note "share_newborns FAILED"
        ( cd "$C" && python3 cf_kid/value_shares.py --tf cfarm_tf_2c --null cfarm_null_2c > "$R/value_shares.txt" 2>&1 ) \
            || note "value_shares FAILED"
        touch "$C/newborn_2c/DONE"
        note "newborn values written: $(grep -i -m1 'better' "$R/newborn/shares.txt")"
    else
        note "cf_kid build FAILED: $(tail -3 /tmp/tr2c_build_kid.log | tr '\n' ' ')"
    fi
fi
publish "arms done, shares written"

# THE T = 60 PATH. Staged from the re-solved Treatment First arm (terminal) and the no-policy arm (t = 0),
# then the seeds replaced by the rescaled old paths.
if [ ! -d "$MAIN" ]; then
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$C/tr60_fix/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr2c_stage_main.log 2>&1 || { note "GUARD: staging the T = 60 path failed: $(tail -3 /tmp/tr2c_stage_main.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    python3 - "$MAIN" "$C/transition_2c/seeds_old" $P_NULL $P_TF $V_NULL $V_TF <<'PYEOF' || { note "GUARD: seeding failed"; publish "failed"; exit 1; }
import sys
n, old, p0, pT, v0, vT = sys.argv[1], sys.argv[2], *map(float, sys.argv[3:])
OLD = {'drug_price': (1.0000321, 0.86736396), 'pi_v': (0.06753386, 0.081411203)}   # the old no-policy and TF steady states
NEW = {'drug_price': (p0, pT), 'pi_v': (v0, vT)}
for name in OLD:
    vals = [float(l) for l in open(f'{old}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(vals) == 59, (name, len(vals))
    (o0, oT), (n0, nT) = OLD[name], NEW[name]
    k = (n0 - nT) / (o0 - oT)
    new = [nT + (x - oT) * k for x in vals]
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: the old transition loop 0 (restart3g) rescaled, start {n0:.6f}, end {nT:.6f}, factor {k:.4f}\n # periods 1 to 59\n')
        f.writelines(f'{x:25.15f}\n' for x in new)
    print(f'{name}: t=1 {new[0]:.6f}, t=30 {new[29]:.6f}, t=59 {new[-1]:.6f}')
PYEOF
    note "T = 60 staged: $(tail -2 /tmp/tr2c_stage_main.log | tr '\n' ' '); seeds $(head -c 300 "$MAIN/drug_price_path_seed.txt" | sed -n 1p)"
fi
# LAUNCH, OR RELAUNCH AFTER A CONTAINER RESTART (2 October 21:46: the container restarted at period 39 of loop 0's
# backward pass; the old test was 'stage and launch only if $MAIN is missing', so the second run of this script
# found the directory, launched nothing, read the dead pid as the end and published 'T = 60 ended' with no exit
# code). A run that finished wrote MAIN_EXIT; one that was killed did not, so: no MAIN_EXIT and no live process
# means relaunch. Loop 0 has no checkpoint, so it starts over; after a completed loop the run's own
# *_path_seed_out.txt are the newest paths and become the seeds.
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "T = 60 already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "T = 60 running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do
            [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"
        done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "T = 60 RELAUNCH after a killed run (seeds: $(ls "$MAIN"/*_path_seed_out.txt >/dev/null 2>&1 && echo 'its last saved paths' || echo 'the staged seeds, loop 0 again'))"
    fi
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = 60 transition started, pid $(cat "$D.main.pid")"
fi
publish "T = 60 running"

# archive each completed loop as it lands; a relaunch numbers its loops from 0 again, so its archives carry _r<n>
RUN_N=$(ls "$MAIN"/run.log.killed.* 2>/dev/null | wc -l)
SUF=$( [ "$RUN_N" -gt 0 ] && echo "_r$RUN_N" )
archived=-1
while alive "$D.main.pid"; do
    for _ in $(seq 1 120); do alive "$D.main.pid" || break; sleep 10; done
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        mkdir -p "$R/loop$last$SUF"
        gzip -c "$MAIN/run.log" > "$R/loop$last$SUF/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$R/loop$last$SUF/" 2>/dev/null
        archived=$last
        note "loop $last complete, archived to results/transition_2c/loop$last$SUF"
    fi
    publish "T = 60 running"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "T = 60 transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = 60 ended"
