#!/bin/bash
# remote_deltah_tr.sh -- THE ROUGH delta_h TRANSITION (11 October; the author, 10 October: after the delta_h long run,
# "set up the ROUGH delta_h transition at T=60 ... not exact, enough for a sense of the numbers"). The long run
# (code/deltah/remote_deltah.sh, results/deltah) turned Treatment First's gain into a loss: newborn CEV -0.72 percent
# of lifetime consumption the paper's way against +4.52, pi_V 0.0718 against 0.0962, homelessness +12 percent. This
# run shows how that builds up over the path.
#
# THE SAME ECONOMY, ON THE PATH. delta_d 0, delta_h 0.31 on children whose parent was ever homeless while they were
# at home (patch_latch.py: the latch carried where the SUD history was, 24 unemployment states against 18), every
# other parameter at the benchmark of record's value, omega_c pinned. Stages, each skipped when its output is on disk:
#   A  the delta_h benchmark, exactly as remote_deltah.sh solves it (bench_hh, from the age-one cross section);
#   B  Housing First re-solved on cf_fix2_share_hh (the share build with the latch), the no-policy arm, which also
#      writes newborn_parent_share_counter.dat, the transition's t = 1 parent share; its net revenue is the target;
#   C  Treatment First on cf_fix2_hh (detection 0.85, the $35 test, pi_V and the price clearing), warm-started at the
#      accepted long run's price 0.87797654 and pi_V 0.071848634; both arms are compared with results/deltah;
#   D  the transition binary: the paper's T = 70 source (transition_fix/tr70_src.f90) with the latch patch and
#      transition_length 40, compiled -O3 as the paper's binary was; staged by transition_fix/stage_tr_fix.sh from the
#      two arms; the seeds are the paper's converged T = 60 path (results/transition_2c/loop1_r5) RESCALED to this
#      economy's terminal values (the price's distance from one and pi_V's distance from Housing First's, both scaled by
#      the ratio of terminal distances), periods 1 to 39.
# WHY T = 40, NOT 60: the transition holds every period's value function, so memory grows with the horizon; the
# paper's T = 70 was OOM-killed once at 15 GiB and runs with swap, and the latch adds a third to the state. Forty
# periods at four thirds the state is about the paper's T = 53. Rough, as asked: the terminal condition binds earlier.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltah/remote_deltah_tr.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running work. Every 20 minutes it
# pushes results/deltah_tr/status.txt; each completed loop is archived to results/deltah_tr/loop<N>/.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltah_tr
mkdir -p "$R"
D=$C/deltah_tr_worker
REF=$REPO/results/reference/hf_2c_omega_0.085
BD=$C/deltah_tr_bench
BREF=$C/deltah_tr_benchref
T40=$C/tr40_hh
MAIN=$C/tr_deltah_t40
SEEDS=$REPO/results/transition_2c/loop1_r5
ACC=$REPO/results/deltah
TRAILER=$'\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0;penalty_child_homeless 0.31"
BLOCKS=${BLOCKS:-16}
HORIZON=40
P_TF_HH=0.87797654; V_TF_HH=0.071848634          # results/deltah/tf/final.txt, the warm start
P_TF_MAIN=0.85551291; V_TF_MAIN=0.096152024      # results/counterfactuals_2c/tf85_c35/tf/final.txt
V_NULL=0.067533863                               # Housing First's pi_V, the same in both economies

note() { echo "remote_deltah_tr: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DELTAH_TR_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltah_tr: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DELTAH_TR_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/deltah_tr.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltah_tr: started detached, pid $(cat "$D.pid"); log /tmp/deltah_tr.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltah_tr: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
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
        echo "# the ROUGH delta_h transition, T = $HORIZON (code/deltah/remote_deltah_tr.sh; delta_d 0, delta_h 0.31 on EVER homeless while the child is at home); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        if [ -f "$BD/bench.log" ]; then echo; echo "== benchmark"; grep -a "INVARIANT PASS\|BLOCK MOVE" "$BD/bench.log" | tail -20; fi
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; digest "$a"; }
        done
        for M in "$MAIN" "$MAIN"_r*; do [ -d "$M" ] && { echo; echo "== $(basename "$M") (T = $HORIZON)"; tr_digest "$M"; }; done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_h transition: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
cd "$C"
git -C "$REPO" config user.name >/dev/null 2>&1 || git -C "$REPO" config user.name "Claude"
git -C "$REPO" config user.email >/dev/null 2>&1 || git -C "$REPO" config user.email "noreply@anthropic.com"

# THE BUILDS: the benchmark and cf_fix2 with the latch (build_hh.sh), the share build with the latch, the T = 40 binary
if [ ! -x "$C/bench_hh/hftf_bench" ] || [ ! -x "$C/cf_fix2_hh/hftf_cf_prod" ]; then
    note "building bench_hh and cf_fix2_hh"
    bash deltah/build_hh.sh both > /tmp/deltah_tr_build_hh.log 2>&1 || { note "GUARD: build_hh failed: $(tail -3 /tmp/deltah_tr_build_hh.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_share_hh/hftf_cf_prod" ]; then
    note "building cf_fix2_share_hh"
    [ -s "$C/cf_fix2/cf.f90" ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh > /dev/null 2>&1; GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh > /dev/null 2>&1; }
    GEN_ONLY=1 bash transition_fix/build_cf_fix2_share.sh > /tmp/deltah_tr_build_share.log 2>&1 || { note "GUARD: generating cf_fix2_share failed: $(tail -3 /tmp/deltah_tr_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    mkdir -p "$C/cf_fix2_share_hh"
    python3 deltah/patch_latch.py "$C/cf_fix2_share/cf.f90" "$C/cf_fix2_share_hh/cf.f90" > /tmp/deltah_tr_patch_share.log 2>&1 || { note "GUARD: the latch patch did not apply to cf_fix2_share: $(tail -2 /tmp/deltah_tr_patch_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q 'unit=421' "$C/cf_fix2_share_hh/cf.f90" || { note "GUARD: cf_fix2_share_hh lost the share write"; publish "failed"; exit 1; }
    ( cd "$C/cf_fix2_share_hh" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ -x "$C/cf_fix2_share_hh/hftf_cf_prod" ] && ! grep -q Error "$C/cf_fix2_share_hh/build_prod.err" || { note "GUARD: cf_fix2_share_hh did not compile: $(grep -m3 Error "$C/cf_fix2_share_hh/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$T40/hftf_tr_prod" ]; then
    note "building the T = $HORIZON transition with the latch"
    mkdir -p "$T40"
    python3 deltah/patch_latch.py transition_fix/tr70_src.f90 "$T40/tr_patched.f90" > /tmp/deltah_tr_patch_tr.log 2>&1 || { note "GUARD: the latch patch did not apply to the transition source: $(tail -2 /tmp/deltah_tr_patch_tr.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    n=$(grep -c "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$T40/tr_patched.f90")
    [ "$n" = 1 ] || { note "GUARD: transition_length 70 found $n times in the patched source"; publish "failed"; exit 1; }
    sed "s/parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$/parameter :: transition_length=(1-solve_transition_dynamics)*1+solve_transition_dynamics*$HORIZON/" "$T40/tr_patched.f90" > "$T40/tr.f90"
    grep -q "solve_transition_dynamics\*$HORIZON$" "$T40/tr.f90" || { note "GUARD: transition_length not set to $HORIZON"; publish "failed"; exit 1; }
    ( cd "$T40" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 -o hftf_tr_prod 2> build_prod.err )
    [ -x "$T40/hftf_tr_prod" ] && ! grep -q Error "$T40/build_prod.err" || { note "GUARD: the transition did not compile: $(grep -m3 Error "$T40/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "tr40_hh built: $(md5sum "$T40/hftf_tr_prod" | cut -c1-8)"
fi
publish "built"

# SWAP AS INSURANCE: the latch adds a third to the state, and the transition holds every period's value function
if [ -z "$(swapon --show 2>/dev/null)" ]; then
    G=$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)
    SW=0; [ "$G" -ge 14 ] && SW=8; [ "$SW" = 0 ] && [ "$G" -ge 10 ] && SW=4
    if [ "$SW" != 0 ]; then
        fallocate -l ${SW}G /var/tmp/deltah_tr.swap 2>/dev/null && chmod 600 /var/tmp/deltah_tr.swap && mkswap /var/tmp/deltah_tr.swap >/dev/null 2>&1 \
            && swapon /var/tmp/deltah_tr.swap 2>/dev/null && note "$SW GiB swap on" || note "no swap (could not enable)"
    else note "no swap (disk ${G}G)"; fi
fi

# STAGE A: THE BENCHMARK, every parameter fixed (remote_deltah.sh's stage A)
if [ -s "$BREF/bench_files.tar.gz" ] && [ -s "$BREF/bench.log.gz" ]; then
    note "benchmark already solved, $BREF"
else
    [ -d "$BD" ] && mv "$BD" "$BD.dead_$(date -u +%H%M%S)"
    mkdir -p "$BD" && cd "$BD"
    [ -e data ] || ln -s ../../data data
    cp "$C/scan_seed/calibration_state.dat" .
    cp "$REF/PARAM_HANDOVER.bench.txt" PARAM_HANDOVER.txt
    setl() {
        if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
        grep -qx "$1 $2" PARAM_HANDOVER.txt || { note "GUARD: $1 is not $2"; publish "failed"; exit 1; }
    }
    setl penalty_child_addicted 0
    setl penalty_child_homeless 0.31
    setl omega_c_is_pinned 1
    setl freeze_all_but_omega_c 1
    setl weight_on_child $W
    setl addiction_scalar_1 $BV
    setl kappa_uem 1.0
    setl kappa_x $KX
    setl frozen_stop_after_blocks $BLOCKS
    cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
    cp "$C/bench_hh/hftf_bench" ./hftf_bench
    note "benchmark: solving from the age-one cross section, at most $BLOCKS frozen blocks"
    env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null &
    PID=$!
    for _ in $(seq 1 60); do grep -q -a "HANDOVER penalty_child_homeless" bench.log 2>/dev/null && break; sleep 5; done
    grep -a "HANDOVER penalty_child_addicted\|HANDOVER penalty_child_homeless\|HANDOVER omega_c_is_pinned" bench.log | head -3 | while read -r l; do note "$l"; done
    while kill -0 "$PID" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
        if ! grep -q -a "HANDOVER penalty_child_homeless" bench.log; then
            kill "$PID"; note "GUARD: no HANDOVER line in the benchmark log; killed"; publish "failed"; exit 1
        fi
        kill -0 "$PID" 2>/dev/null && publish "benchmark running, $(grep -ac 'BLOCK MOVE' bench.log) blocks"
    done
    wait "$PID"; RC=$?
    note "benchmark exited $RC after $(grep -ac 'BLOCK MOVE' bench.log) blocks; bench.err: $(tail -2 bench.err | tr '\n' ' ')"
    for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
        [ -s "$f" ] || { note "GUARD: the benchmark did not write $f"; publish "failed"; exit 1; }
    done
    mkdir -p "$BREF"
    tar czf "$BREF/bench_files.tar.gz" *baseline_benchmark.dat
    gzip -c bench.log > "$BREF/bench.log.gz"
    gzip -c bench.log > "$R/bench.log.gz"
    cp PARAM_HANDOVER.kept.txt "$R/PARAM_HANDOVER.bench.txt"
    gzip -c welfare_curvebaseline_benchmark.dat > "$R/welfare_curvebaseline_benchmark.dat.gz"
    publish "benchmark done"
    cd "$C"
fi

export BENCH_FROM=$BREF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export OMP_NUM_THREADS=2 SEED_FROM=bench DIAG_TAG=_2c BENCH_BIN=$C/bench_hh/hftf_bench
export CEV_CURVE=$D.welfare_curve.dat
tar xzf "$BREF/bench_files.tar.gz" -O welfare_curvebaseline_benchmark.dat > "$CEV_CURVE"
export PASSES_BASE=$(zcat "$BREF/bench.log.gz" | awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}')
note "benchmark (users, SUD, h_1) $PASSES_BASE (the accepted delta_h benchmark: 0.0911094944,0.0387626501,0.0062202157)"

# run_arm <arm> <build> [VAR=value ...]: as remote_deltah.sh's, the penalties in EXTRA_SET
run_arm() (
    a=$1; b=$2; shift 2
    cd "$C"
    note "arm $a on $b: $*"
    env BUILD=$b "$@" sh deltah/cf_arm_hh_tr.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        kill -0 "$P" 2>/dev/null && publish "$a running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_${a}_2c/cf.log" 2>/dev/null) passes"
    done
    wait "$P"; rc=$?
    O="$C/cfarm_${a}_2c.out"
    mkdir -p "$R/arm_$a"
    gzip -c "$O" > "$R/arm_$a/run.out.gz"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R/arm_$a/cf.log.gz"
    [ -f "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" ] && cp "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" "$R/arm_$a/"
    grep -a "CHECK PASS\|GUARD" "$O" > "$R/arm_$a/checks.txt"
    NULLLOG=""; [ "$a" != null ] && [ -f "$C/cfarm_null_2c/cf.log" ] && NULLLOG="$C/cfarm_null_2c/cf.log"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $NULLLOG > "$R/arm_$a/final.txt" 2>&1
    digest "$a" > "$R/arm_$a/passes.txt"
    ok=0
    tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
    case "$a" in
        tf) grep -q "TARGET CHECK PASS" "$O" || ok=1 ;;
        *)  grep -q "VOUCHER CHECK PASS" "$O" || ok=1 ;;
    esac
    grep -q "GUARD" "$O" && ok=1
    grep -q -a "HANDOVER penalty_child_homeless" "$C/cfarm_${a}_2c/cf.log" || { note "GUARD: arm $a did not apply penalty_child_homeless"; ok=1; }
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/arm_$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)
arm_done() {   # <name> <check>: an earlier run of this arm passed its checks
    O="$C/cfarm_${1}_2c.out"
    [ -f "$O" ] && tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "$2" "$O" && ! grep -q "GUARD" "$O"
}

# STAGE B: HOUSING FIRST on the share build, so the parent share at t = 1 is this economy's own
if arm_done null "VOUCHER CHECK PASS" && [ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ]; then
    note "null arm already accepted"
else
    run_arm null cf_fix2_share_hh DRUG_PRICE_START=1.0 EXTRA_SET="$PENALTIES" || { publish "null not accepted, stopping"; exit 1; }
    [ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share_hh"; publish "failed"; exit 1; }
fi
NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
echo "$NT" > "$R/arm_null/net_target.txt"
note "no-policy net revenue $NT is the TF budget target (the accepted delta_h null arm's: $(cat "$ACC/null/net_target.txt" 2>/dev/null)); test cost $CTEST (\$35)"

# STAGE C: TREATMENT FIRST, warm-started at the accepted delta_h long run
if arm_done tf "TARGET CHECK PASS"; then
    note "tf arm already accepted"
else
    run_arm tf cf_fix2_hh PDET=0.85 NET_TARGET="$NT" PV_START=$V_TF_HH DRUG_PRICE_START=$P_TF_HH EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES" || { publish "tf not accepted, stopping"; exit 1; }
fi
note "arms against the accepted delta_h runs: $(python3 - "$R" "$ACC" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
r, a = sys.argv[1], sys.argv[2]
out = []
for mine, acc in (('arm_null', 'null'), ('arm_tf', 'tf')):
    try:
        x, y = lv(f'{r}/{mine}/final.txt'), lv(f'{a}/{acc}/final.txt')
        worst = max(abs(x[k] / y[k] - 1) for k in ('drug price', 'pi_V (voucher probability)', 'drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k))
        out.append(f'{mine} worst relative difference {worst:.1e}')
    except Exception as e:
        out.append(f'{mine}: could not compare ({e})')
print('; '.join(out))
PYEOF
)"
publish "arms done"

# STAGE D: THE PATH, staged from the arms, the seeds the paper's converged T = 60 path rescaled to this economy
if [ ! -d "$MAIN" ]; then
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$T40/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NT" > /tmp/deltah_tr_stage.log 2>&1 || { note "GUARD: staging failed: $(tail -3 /tmp/deltah_tr_stage.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=$HORIZON, $((HORIZON - 1)) periods" /tmp/deltah_tr_stage.log || { note "GUARD: staging did not read T = $HORIZON: $(grep seeds /tmp/deltah_tr_stage.log)"; publish "failed"; exit 1; }
    python3 - "$MAIN" "$SEEDS" "$HORIZON" "$P_TF_MAIN" "$V_TF_MAIN" "$V_NULL" <<'PYEOF' || { note "GUARD: seeding failed"; publish "failed"; exit 1; }
import sys
n, seeds, T, p_main, v_main, v0 = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
for name, kind in (('drug_price', 'p'), ('pi_v', 'v')):
    vals = [float(l) for l in open(f'{seeds}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(vals) == 59, (name, len(vals))
    flat = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(flat) == T - 1 and max(flat) - min(flat) < 1e-15, (name, len(flat))
    term = flat[0]                       # this economy's terminal value, from the re-solved arm
    if kind == 'p':
        k = (term - 1.0) / (p_main - 1.0)
        new = [1.0 + (x - 1.0) * k for x in vals[:T - 1]]
    else:
        k = (term - v0) / (v_main - v0)
        new = [v0 + (x - v0) * k for x in vals[:T - 1]]
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: the paper\'s T = 60 loop 1_r5 path for periods 1 to {T-1}, its distance from {"one" if kind == "p" else "Housing First"} scaled by {k:.6f} to this economy\'s terminal value {term:.12f}\n # periods 1 to {T-1}\n')
        f.writelines(f'{x:25.15f}\n' for x in new)
    print(f'{name}: scale {k:.4f}, t=1 {new[0]:.6f}, t={T-1} {new[-1]:.6f}, terminal {term:.6f}')
PYEOF
    note "T = $HORIZON staged: $(tail -2 /tmp/deltah_tr_stage.log | tr '\n' ' '); seeds rescaled from the paper's loop 1_r5 path"
fi
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "transition already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "transition running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do
            [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"
        done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "RELAUNCH after a killed run (seeds: $(ls "$MAIN"/*_path_seed_out.txt >/dev/null 2>&1 && echo 'its last saved paths' || echo 'the staged seeds, loop 0 again'))"
    fi
    # the binary reads PARAM_HANDOVER.txt and DELETES it: restore it from the copy staging keeps, never run without it
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || { note "GUARD: no PARAM_HANDOVER.txt or .kept.txt in $MAIN"; publish "failed"; exit 1; }
    grep -q "^penalty_child_homeless 0.31" "$MAIN/PARAM_HANDOVER.txt" || { note "GUARD: the transition's handover lacks penalty_child_homeless 0.31"; publish "failed"; exit 1; }
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = $HORIZON transition started, pid $(cat "$D.main.pid")"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a -c '^ HANDOVER' "$MAIN/run.log") parameters; penalty lines: $(grep -a 'HANDOVER penalty_child' "$MAIN/run.log" | tr -s ' ' | tr '\n' ';')"
fi
publish "T = $HORIZON running"

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
        cp "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop$last$SUF/" 2>/dev/null
        archived=$last
        note "loop $last complete, archived to results/deltah_tr/loop$last$SUF"
    fi
    publish "T = $HORIZON running"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = $HORIZON ended"
