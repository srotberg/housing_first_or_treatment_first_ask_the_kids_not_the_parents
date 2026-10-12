#!/bin/bash
# remote_treatC2.sh STEP -- THE TESTS OF cf_fix2_treatC2 (code/treat/patch_treatC2.py, 12 October): rule C with the
# abstention option for a treated household with the disorder, the EV table keyed on the voucher category, the internal
# grid with the household's own treatment, use counted as v>0. remote_treatC.sh's machinery (cf_arm_C2.sh, the same
# benchmark, budget target, test cost, publishing), one step per call, each capped at MAX_PASSES and killed there:
#   inert_C    the no-policy arm (no screen) on cf_fix2_treatC,  1 pass   } test B: every printed digit must agree
#   inert_C2   the no-policy arm (no screen) on cf_fix2_treatC2, 1 pass   }
#   ruleC2     Treatment First, rule C, detection 0.85, $35 test, on cf_fix2_treatC2, 2 passes (test C)
#   ruleC2_off the same on cf_fix2_treatC2 with TC2_ABSTAIN=TC2_EVKEY=TC2_INTERNAL=0 (= cf_fix2_treatC), 1 pass: the
#              control at the same start and the same benchmark distribution
#   ruleC2_noab the same with only TC2_ABSTAIN=0 (the EV key and internal-grid fixes alone), 1 pass
# The Treatment First steps start at tf_ruleC's latest published pass (price, pi_V). Results to
# results/counterfactuals_2c/tf_ruleC2_test/<STEP>/. START WITH run_in_background=true from the repo root; a second call
# with the same STEP attaches to the running solve.
set -u
STEP=$1
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
NET_TARGET_NULL=5.8918410999831181
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
RT=$REPO/results/counterfactuals_2c/tf_ruleC2_test
R=$RT/$STEP
mkdir -p "$R"
D=$C/cf_point_c2_$STEP
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_c2_$STEP
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
case "$STEP" in
  inert_C)     ARM=null; B=cf_fix2_treatC;  MAXP=1 ;;
  inert_C2)    ARM=null; B=cf_fix2_treatC2; MAXP=1 ;;
  ruleC2)      ARM=tf;   B=cf_fix2_treatC2; MAXP=2 ;;
  ruleC2_off)  ARM=tf;   B=cf_fix2_treatC2; MAXP=1; export TC2_ABSTAIN=0 TC2_EVKEY=0 TC2_INTERNAL=0 ;;
  ruleC2_noab) ARM=tf;   B=cf_fix2_treatC2; MAXP=1; export TC2_ABSTAIN=0 ;;
  *) echo "usage: $0 inert_C|inert_C2|ruleC2|ruleC2_off|ruleC2_noab"; exit 1 ;;
esac
DIR=$C/cfarm_${ARM}_c2_$STEP

note() { echo "remote_treatC2 $STEP: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_treatC2 $STEP: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_c2_$STEP.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_treatC2 $STEP: started detached, pid $(cat "$D.pid")"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_treatC2 $STEP: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

npass() { grep -ac '^ *distance_govt_budget=' "$DIR/cf.log" 2>/dev/null || echo 0; }
publish() (
    {
        echo "# tf_ruleC2_test/$STEP: arm $ARM on $B, against results/reference/hf_2c_omega_0.085; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        if [ -f "$DIR/cf.log" ]; then
            echo; (cd "$C" && python3 cf_runs/passes.py "$DIR/cf.log" "$C/cf_runs/cev.py" 2>/dev/null)
            grep -a "TREATC2 switches" "$DIR/cf.log" | head -1
            grep -a "ABSTAIN sud" "$DIR/cf.log" | tail -2
            grep -a "MILBY SPLIT" "$DIR/cf.log" | tail -1
        fi
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    # the top-level passes.txt: the latest line of every step
    { echo "# tf_ruleC2_test: the tests of cf_fix2_treatC2 (code/treat/patch_treatC2.py); one folder per step"
      for f in "$RT"/*/passes.txt; do echo; echo "== $(basename "$(dirname "$f")")"; grep -v '^#' "$f"; done; } > "$RT/passes.txt"
    cd "$REPO"
    git add "$RT" 2>/dev/null
    git commit -q -m "tf_ruleC2_test $STEP: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git pull -q --rebase origin "$BRANCH" && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
[ -x "$C/$B/hftf_cf_prod" ] || { note "GUARD: $B/hftf_cf_prod missing (treat/build_treatC.sh, treat/build_treatC2.sh)"; publish "failed"; exit 1; }
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"

cd "$C"
EXTRA=()
if [ "$ARM" = tf ]; then
    L=$REPO/results/counterfactuals_2c/tf_ruleC/passes.txt
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {n=$1; p=$2; v=$3} END{if (p) print n, p, v}' "$L")
    set -- $LAST; NP=$1; P0=$2; V0=$3
    note "start at tf_ruleC's pass $NP: price $P0, pi_V $V0"
    EXTRA=(PDET=0.85 NET_TARGET="$NET_TARGET_NULL" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST")
fi
note "arm $ARM on $B, at most $MAXP passes; TC2_ABSTAIN=${TC2_ABSTAIN:-1} TC2_EVKEY=${TC2_EVKEY:-1} TC2_INTERNAL=${TC2_INTERNAL:-1}"
publish "starting"
env BUILD="$B" "${EXTRA[@]}" sh treat/cf_arm_C2.sh "$ARM" > "$DIR.out" 2>&1 &
P=$!
T0=$(date +%s); last=$T0; seen=0; tp=$T0
while kill -0 "$P" 2>/dev/null; do
    sleep 30
    n=$(npass)
    if [ "$n" -gt "$seen" ]; then note "pass $n done, $(( $(date +%s)-tp )) s"; seen=$n; tp=$(date +%s); fi
    if [ "$(npass)" -ge "$MAXP" ]; then
        sleep 20   # let the pass's trailing prints land
        note "pass cap $MAXP reached after $(( ($(date +%s)-T0)/60 )) min; stopping the solve"
        pkill -f "$DIR/hftf_cf" 2>/dev/null; pkill -x hftf_cf 2>/dev/null
        break
    fi
    if [ $(( $(date +%s)-last )) -ge 1500 ]; then publish "running, $(npass) passes"; last=$(date +%s); fi
done
wait "$P" 2>/dev/null
mkdir -p "$R"
gzip -c "$DIR/cf.log" > "$R/cf.log.gz" 2>/dev/null
gzip -c "$DIR.out" > "$R/run.out.gz"
grep -a "GUARD\|error wrong\|wrong_\| wrong$\|renter renter eror\|internal eror" "$DIR/cf.log" "$DIR.out" | sort | uniq -c | head -20 > "$R/guards.txt"
grep -a "DIST_DONE\|PASS_SECONDS\|^ *distance_govt_budget=" "$DIR/cf.log" > "$R/timing.txt"
note "done: $(npass) passes in $(( ($(date +%s)-T0)/60 )) min"
publish "finished"
