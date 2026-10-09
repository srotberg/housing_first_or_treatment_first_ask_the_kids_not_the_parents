#!/bin/bash
# remote_cf_nishiyama.sh <bench dir> <b> <kappa_x> [omega_c] -- STAGE 3 OF THE omega_c = 0.686 SENSITIVITY
# (9 October; the author: "a sensitivity test where omega_c = [Nishiyama's value] in the benchmark ... and show
# whether the long run welfare effects are similar"). Housing First (the null arm) and then Treatment First at
# the new two-class benchmark, exactly as the paper's arms were run: remote_cf_point.sh nulltf for the null arm
# (results/counterfactuals_2c/nulltf/null) and remote_cf_tf_c35.sh for Treatment First
# (results/counterfactuals_2c/tf85_c35/tf): detection 0.85, the drug test at $35, drug price clearing, pi_V
# clearing the budget against the new null's net revenue. Only the benchmark differs: BENCH_FROM is the new
# benchmark's directory (results/omega_nishiyama_2c/bench_<TAG>, with files/ sent by remote_omega_point.sh),
# BENCH_B its b, BENCH_OMEGA its omega_c, KAPPA_X its first KAPPA_X PROBE IMPLIED x 1.5076, PASSES_BASE its
# drug users, disorder rate and homelessness (its log's INVARIANT PASS lines). Results to
# results/omega_nishiyama/cf/{null,tf}. The paper's welfare number is CEV(tf) - CEV(null), each the arm's
# cf.log 'CEV from the saved benchmark curve' line.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run the same command again
# whenever the call is stopped: it ATTACHES to the running solve. A restart after the null arm was accepted
# does not solve it again (its net revenue is kept in results/omega_nishiyama/cf/null/net_target.txt and its
# solved directory stays in the container); a restart of Treatment First resumes from its last published pass.
set -u
BREL="$1"; BV="$2"; KX="$3"; W="${4:-0.686}"
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/$BREL
R=$REPO/results/omega_nishiyama/cf
mkdir -p "$R"
D=$C/cf_nishiyama
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
export BENCH_FROM=$REF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export OMP_NUM_THREADS=2 SEED_FROM=bench DIAG_TAG=_2c
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_cf_nishiyama: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_cf_nishiyama: attaching to the running solve, pid $(cat "$D.pid")"
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_nishiyama.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_cf_nishiyama: started detached, pid $(cat "$D.pid"); log /tmp/cf_nishiyama.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_cf_nishiyama: finished"; cat "$D.status" 2>/dev/null
    grep -q "arm tf ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

[ -s "$REF/bench.log.gz" ] || { echo "GUARD: $REF/bench.log.gz missing"; exit 1; }
[ -s "$REF/files/welfare_curvebaseline_benchmark.dat.gz" ] || { echo "GUARD: $REF/files missing"; exit 1; }
# the new benchmark's drug users, disorder rate and homelessness, for the passes digest
PB=$(zcat "$REF/bench.log.gz" | awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}')
export PASSES_BASE="$PB"

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# omega_c $W sensitivity, Housing First and Treatment First against $BREL (b $BV, kappa_uem 1.0, kappa_x $KX; base $PB); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest "$a"; }
        done
        true
    } > "$R/passes.txt.tmp"; mv "$R/passes.txt.tmp" "$R/passes.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "omega_c $W sensitivity, counterfactuals: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# run_arm <cf_arm.sh arm> <build> [VAR=value ...]: as remote_cf_point.sh's
run_arm() (
    a=$1; b=$2; shift 2
    cd "$C"
    note "arm $a on $b: $*"
    env BUILD="$b" "$@" sh cf_runs/cf_arm_set.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        kill -0 "$P" 2>/dev/null && publish "$a running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_${a}_2c/cf.log" 2>/dev/null) passes"
    done
    wait "$P"; rc=$?
    O="$C/cfarm_${a}_2c.out"
    mkdir -p "$R/$a"
    gzip -c "$O" > "$R/$a/run.out.gz"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R/$a/cf.log.gz"
    [ -f "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" ] && cp "$C/cfarm_${a}_2c/PARAM_HANDOVER.arm.txt" "$R/$a/"
    grep -a "CHECK PASS\|GUARD" "$O" > "$R/$a/checks.txt"
    NULLLOG=""; [ "$a" != null ] && [ -f "$C/cfarm_null_2c/cf.log" ] && NULLLOG="$C/cfarm_null_2c/cf.log"
    [ -f "$C/cfarm_${a}_2c/cf.log" ] && python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $NULLLOG > "$R/$a/final.txt" 2>&1
    digest "$a" > "$R/$a/passes.txt"
    ok=0
    tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
    case "$a" in
        tf) grep -q "TARGET CHECK PASS" "$O" || ok=1 ;;
        *)  grep -q "VOUCHER CHECK PASS" "$O" || ok=1 ;;
    esac
    grep -q "GUARD" "$O" && ok=1
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "benchmark $BREL: omega_c $W, b $BV, kappa_x $KX, base (users, SUD, h_1) $PB"

cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/cf_point_build_$b.log" 2>&1 || {
        note "GUARD: build $b failed: $(tail -3 /tmp/cf_point_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
publish "built, starting"

# HOUSING FIRST, as remote_cf_point.sh nulltf; skipped on a restart once accepted in this container
if [ -s "$R/null/net_target.txt" ] && [ -f "$C/cfarm_null_2c/cf.log" ]; then
    NT=$(cat "$R/null/net_target.txt"); note "null arm already accepted, net revenue $NT"
else
    run_arm null cf_fix2 DRUG_PRICE_START=1.0 || { publish "null not accepted, stopping"; exit 1; }
    NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
    echo "$NT" > "$R/null/net_target.txt"
fi
note "no-policy net revenue $NT is the TF budget target"
note "test cost $CTEST in model units (\$35)"

# TREATMENT FIRST, as remote_cf_tf_c35.sh, warm-started at the paper's tf85_c35 equilibrium (or the last
# published pass of a killed solve)
P0=0.8555; V0=0.0962
if [ -f "$R/passes.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/passes.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
run_arm tf cf_fix2 PDET=0.85 NET_TARGET="$NT" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST"
publish "complete"
