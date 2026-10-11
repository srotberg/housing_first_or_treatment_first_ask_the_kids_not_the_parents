#!/bin/bash
# remote_tr70_cohort.sh -- THE PAPER'S T = 70 LOOP 2, RE-RUN WITH THE ENTRANT-BY-PARENT-AGE PRINT (11 October; the
# referee: the transition's "cohort born at the reform" is eq. 31's adult term read at t+25, the average over all
# entrants that year, and the cohort's own orphans are not followed; the author: "sure, you can measure it"). A copy
# of code/remote_transition_2c_t70.sh with four changes: the binary is tr70_src.f90 patched by
# transition_fix/patch_cohort_print.py (print-only: TRANSITION ENTRANT_MASS_BY_PARENT_AGE and
# ENTRANT_VALUE_BY_PARENT_AGE per period); the seeds are loop 1's archived paths (results/transition_2c_t70/loop1),
# the paths the paper's pinned loop 2 was solved on, so the loop reproduces loop 2 and adds the print; the first
# saved loop is archived as results/transition_2c_t70_cohort/loop2 and the binary is then stopped; status to
# results/transition_2c_t70_cohort/status.txt. The two arms are re-solved in this container as the T = 70 worker
# re-solved them (the t = 0 no-policy state on cf_fix2_share, the terminal Treatment First state on cf_fix2).
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/transition_fix/remote_tr70_cohort.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running worker.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")" && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/transition_2c_t70_cohort
mkdir -p "$R"
D=$C/tr70cohort_worker
TRAILER=$'\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
NET_TARGET=5.8918410999831181                 # the accepted no-policy run's net revenue (tf85_c35's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
P_TF=0.85551291;  V_TF=0.096152024            # results/counterfactuals_2c/tf85_c35/tf/final.txt
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
MAIN=$C/tr2c_t70_cohort
T70=$C/tr70_cohort
SEEDS=$REPO/results/transition_2c_t70/loop1   # the paths loop 2, the paper's pin, was solved on

note() { echo "remote_tr70_cohort: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR70C_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_tr70_cohort: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( TR70C_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr70_cohort.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_tr70_cohort: started detached, pid $(cat "$D.pid"); log /tmp/tr70_cohort.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_tr70_cohort: finished"; cat "$D.status" 2>/dev/null
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
        echo "# T = 70, loop 2 re-run with the entrant-by-parent-age print (code/transition_fix/remote_tr70_cohort.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null; }
        done
        for M in "$MAIN" "$MAIN"_r*; do [ -d "$M" ] && { echo; echo "== $(basename "$M") (T = 70)"; tr_digest "$M"; }; done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "transition T=70 cohort print: $1$TRAILER" || return 0
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

# THE BUILDS: the arms' three as in remote_transition_2c.sh, and T = 70 from the T = 60 source
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/tr70_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/tr70_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > /tmp/tr70_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 /tmp/tr70_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$T70/hftf_tr_prod" ]; then
    note "building tr70_cohort"
    mkdir -p "$T70" && python3 "$C/transition_fix/patch_cohort_print.py" "$C/transition_fix/tr70_src.f90" "$T70/tr.f90" >> "$D.status" 2>&1 || { note "GUARD: patch_cohort_print.py failed"; publish "failed"; exit 1; }
    [ "$(grep -c "TRANSITION ENTRANT_VALUE_BY_PARENT_AGE" "$T70/tr.f90")" = 1 ] || { note "GUARD: the cohort print is not in the source"; publish "failed"; exit 1; }
    grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$T70/tr.f90" \
        || { note "GUARD: transition_fix/tr70_src.f90 is not at transition_length 70"; publish "failed"; exit 1; }
    ( cd "$T70" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 \
        -o hftf_tr_prod 2> build_prod.err )
    [ -x "$T70/hftf_tr_prod" ] && ! grep -q Error "$T70/build_prod.err" || { note "GUARD: tr70_cohort did not compile: $(grep -m3 Error "$T70/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "tr70_cohort built: $(md5sum "$T70/hftf_tr_prod" | cut -c1-8)"
fi
publish "built"

# THE TWO ARMS, as in remote_transition_2c.sh
if ! arm_ok null "VOUCHER CHECK PASS"; then
    arm null cf_fix2_share DRUG_PRICE_START=$P_NULL
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_null.pid"; do sleep 10; done
fi
if ! arm_ok tf "TARGET CHECK PASS"; then
    arm tf cf_fix2 PDET=0.85 NET_TARGET="$NET_TARGET" PV_START=$V_TF DRUG_PRICE_START=$P_TF EXTRA_SET="cost_per_drug_test $CTEST"
fi
wait_publishing "$D.arm_null.pid" "arms running"
arm_ok null "VOUCHER CHECK PASS" || { note "GUARD: the no-policy re-solve failed its checks: $(tail -3 "$C/cfarm_null_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
[ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share"; publish "failed"; exit 1; }
wait_publishing "$D.arm_tf.pid" "Treatment First re-solve running"
arm_ok tf "TARGET CHECK PASS" || { note "GUARD: the Treatment First re-solve failed its checks: $(tail -3 "$C/cfarm_tf_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
for a in null tf; do
    mkdir -p "$R/arm_$a"
    python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $( [ $a = tf ] && echo "$C/cfarm_null_2c/cf.log" ) > "$R/arm_$a/final.txt" 2>&1
done
note "arms against the accepted runs: $(python3 - "$R" "$REPO/results/counterfactuals_2c" <<'PYEOF'
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
publish "arms done"

# THE T = 70 PATH: staged from the arms, then the seeds replaced by the same vectors of guesses
if [ ! -d "$MAIN" ]; then
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$T70/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr70_stage_main.log 2>&1 || { note "GUARD: staging T = 70 failed: $(tail -3 /tmp/tr70_stage_main.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=70, 69 periods" /tmp/tr70_stage_main.log || { note "GUARD: staging did not read T = 70: $(grep seeds /tmp/tr70_stage_main.log)"; publish "failed"; exit 1; }
    python3 - "$MAIN" "$SEEDS" <<'PYEOF' || { note "GUARD: seeding failed"; publish "failed"; exit 1; }
import sys
n, seeds = sys.argv[1], sys.argv[2]
for name in ('drug_price', 'pi_v'):
    vals = [float(l) for l in open(f'{seeds}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(vals) == 69, (name, len(vals))
    flat = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(flat) == 69 and max(flat) - min(flat) < 1e-15, (name, len(flat))
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: T = 70 loop 1 as archived, the paths the paper\'s loop 2 was solved on\n # periods 1 to 69\n')
        f.writelines(f'{x:25.15f}\n' for x in vals)
    print(f'{name}: t=1 {vals[0]:.6f}, t=35 {vals[34]:.6f}, t=69 {vals[68]:.6f}')
PYEOF
    note "T = 70 staged: $(tail -2 /tmp/tr70_stage_main.log | tr '\n' ' '); seeds = loop 1's archived paths"
fi
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "T = 70 already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "T = 70 running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do
            [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"
        done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "T = 70 RELAUNCH after a killed run (seeds: $(ls "$MAIN"/*_path_seed_out.txt >/dev/null 2>&1 && echo 'its last saved paths' || echo 'the staged seeds, loop 0 again'))"
    fi
    # THE HANDOVER IS CONSUMED. The binary reads PARAM_HANDOVER.txt and DELETES it, so a relaunch without this line
    # solves the model at calibration_state.dat's values instead of the arm's (10 Oct: the 00:33 relaunch did exactly
    # that -- no HANDOVER lines, 5.65 million 'budget does not clear' warnings, killed at 01:37). Restore it from the
    # copy staging keeps, and refuse to run without it.
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || { note "GUARD: no PARAM_HANDOVER.txt or .kept.txt in $MAIN"; publish "failed"; exit 1; }
    # SWAP AS INSURANCE (10 Oct: the 01:37 run was OOM-killed). Only when there is disk to spare and none is on.
    if [ -z "$(swapon --show 2>/dev/null)" ] && [ "$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)" -ge 10 ]; then
        fallocate -l 4G /var/tmp/tr70.swap 2>/dev/null && chmod 600 /var/tmp/tr70.swap && mkswap /var/tmp/tr70.swap >/dev/null 2>&1 \
            && swapon /var/tmp/tr70.swap 2>/dev/null && note "4 GiB swap on" || note "no swap (could not enable)"
    fi
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = 70 transition started, pid $(cat "$D.main.pid")"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a -c '^ HANDOVER' "$MAIN/run.log") parameters"
fi
publish "T = 70 running"

RUN_N=$(ls "$MAIN"/run.log.killed.* 2>/dev/null | wc -l)
SUF=$( [ "$RUN_N" -gt 0 ] && echo "_r$RUN_N" )
archived=-1
while alive "$D.main.pid"; do
    for _ in $(seq 1 120); do alive "$D.main.pid" || break; sleep 10; done
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        # ONE LOOP ONLY: the binary's first loop, on loop 1's paths, is the paper's loop 2 with the print
        mkdir -p "$R/loop2"
        gzip -c "$MAIN/run.log" > "$R/loop2/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$R/loop2/" 2>/dev/null
        cp "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop2/" 2>/dev/null
        archived=$last
        note "loop $last complete (the paper's loop 2 with the print), archived to results/transition_2c_t70_cohort/loop2; stopping the binary"
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        sleep 5
        note "entrant lines in the log: $(grep -a -c 'TRANSITION ENTRANT_VALUE_BY_PARENT_AGE' "$MAIN/run.log")"
        break
    fi
    publish "T = 70 running"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "T = 70 transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = 70 cohort loop ended"
