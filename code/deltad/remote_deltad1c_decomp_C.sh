#!/bin/bash
# remote_deltad1c_decomp_C.sh -- RULE C: remote_deltad1c_decomp.sh after remote_deltad1c_C.sh (TAG dd0_1c_C), with both
# decomposition arms on the rule-C one-class build (cf_fix2_1c_treatC through treat/cf_arm_C.sh, which takes
# DRUG_MARKET_ADJUSTER from the environment). Results to results/deltad/dd0_1c_C_decomp/. The original header follows.
# remote_deltad1c_decomp.sh -- THE DECOMPOSITION OF TREATMENT FIRST IN THE delta_d = 0 ECONOMY (12 October). The author, on
# the one-class delta_d = delta_h = 0 run's gain of about zero: "so the deltad penalty is key here....it generates the gain
# through the higher piv moslty?", then "sure, do these runs too". The paper's Table 6 splits its main experiment into
# three columns: the drug price and pi_V both held at Housing First's (the screen alone), pi_V clearing with the price
# held (+ recycling), and both clearing (+ the cheaper drug). This runs the first two in the delta_d = 0 economy, so its
# own clearing arm (remote_deltad1c.sh's tf) becomes the third and the three can be set beside the paper's:
#   fixboth  pi_V and the drug price held at this economy's no-policy values; the budget not cleared (adjust_taxes 0)
#   fixp     the drug price held; pi_V clears the budget against this economy's no-policy net revenue
# Both as the paper's dc_b and dc_p (code/extra_2c/remote_decomp_2c*.sh), on cf_fix2_1c with both penalties at zero.
#
# RUNS IN THE SAME CONTAINER AS remote_deltad1c.sh, AFTER IT: it reuses that run's one-class benchmark files
# (code/deltad_benchref_dd0_1c, local to the container, not in the repository) and waits for its job to end.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltad/remote_deltad1c_decomp.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running work.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
TAG=dd0_1c_C
R=$REPO/results/deltad/${TAG}_decomp
mkdir -p "$R"
D=$C/deltad_decomp_$TAG
RUN2=$C/deltad_run_$TAG                       # remote_deltad1c.sh's state prefix
BREF=$C/deltad_benchref_$TAG
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0;penalty_child_homeless 0"

note() { echo "remote_deltad1c_decomp: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DECOMP1C_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltad1c_decomp: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DECOMP1C_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/deltad1c_decomp_C.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltad1c_decomp: started detached, pid $(cat "$D.pid"); log /tmp/deltad1c_decomp_C.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltad1c_decomp: finished"; cat "$D.status" 2>/dev/null
    grep -q "decompositions done" "$D.status" 2>/dev/null
    exit $?
fi

publish() (
    {
        echo "# delta_d = delta_h = 0, one class: Treatment First with pi_V and the price held (fixboth), and with the price held (fixp) (code/deltad/remote_deltad1c_decomp.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in fixboth fixp; do
            L="$C/cfarm_tf_2c_$a/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null; }
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_d 0 rule C decomposition: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
dist_ok() { tail -5 "$C/cfarm_tf_2c_$1.out" 2>/dev/null | grep -q "DIST CHECK PASS" && ! grep -q "GUARD" "$C/cfarm_tf_2c_$1.out"; }

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"

# WAIT FOR remote_deltad1c.sh: the two would share the container's four cores and cfarm_bench
if alive "$RUN2.pid"; then
    note "waiting for remote_deltad1c.sh (pid $(cat "$RUN2.pid")) to finish"
    publish "waiting for the clearing arm"
    while alive "$RUN2.pid"; do sleep 60; done
fi
[ -s "$BREF/bench_files.tar.gz" ] || { note "GUARD: no one-class benchmark files in $BREF: this container is not remote_deltad1c.sh's"; publish "failed"; exit 1; }
[ -x "$C/cf_fix2_1c_treatC/hftf_cf_prod" ] || { note "GUARD: no cf_fix2_1c_treatC binary"; publish "failed"; exit 1; }
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_1c_treatC/cf.f90" \
    || { note "GUARD: cf_fix2_1c_treatC lacks the held-price stopping rule"; publish "failed"; exit 1; }
NULLLOG=$C/cfarm_null_2c/cf.log
[ -f "$NULLLOG" ] || { note "GUARD: no no-policy arm log in $C/cfarm_null_2c"; publish "failed"; exit 1; }
NT=$(cat "$REPO/results/deltad/$TAG/null/net_target.txt")
P_NULL=$(grep -a "^ *price_of_addictive_good=" "$NULLLOG" | tail -1 | awk '{print $2}')
V_NULL=$(grep -a "^ *probability_of_voucher=" "$NULLLOG" | tail -1 | awk '{print $2}')
# pi_V starts the fixp arm at the clearing arm's last value, the price at the no-policy one
V_TF=$(grep -a "^ *probability_of_voucher=" "$C/cfarm_tf_2c/cf.log" 2>/dev/null | tail -1 | awk '{print $2}')
[ -n "$V_TF" ] || V_TF=0.0759
note "no-policy: price $P_NULL, pi_V $V_NULL, net revenue $NT; fixp starts pi_V at $V_TF"

export BENCH_FROM=$BREF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export SEED_FROM=bench
export CEV_CURVE=$D.welfare_curve.dat
tar xzf "$BREF/bench_files.tar.gz" -O welfare_curvebaseline_benchmark.dat > "$CEV_CURVE"
export PASSES_BASE=$(zcat "$BREF/bench.log.gz" | awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}')

arm() {
    a=$1; shift
    note "arm $a: $*"
    ( cd "$C" && env BUILD=cf_fix2_1c_treatC OMP_NUM_THREADS=2 DIAG_TAG="_2c_$a" "$@" sh treat/cf_arm_C.sh tf \
        > "$C/cfarm_tf_2c_$a.out" 2>&1 ) &
    echo $! > "$D.arm_$a.pid"
}
# fixboth first, alone until it has staged cfarm_bench (already there from the clearing run), then fixp beside it
if ! dist_ok fixboth; then
    arm fixboth PDET=0.85 PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 \
        EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$PENALTIES"
    sleep 120
fi
if ! dist_ok fixp; then
    arm fixp PDET=0.85 NET_TARGET="$NT" PV_START=$V_TF DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 \
        EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES"
fi
while alive "$D.arm_fixboth.pid" || alive "$D.arm_fixp.pid"; do
    for _ in $(seq 1 120); do { alive "$D.arm_fixboth.pid" || alive "$D.arm_fixp.pid"; } || break; sleep 10; done
    publish "arms running"
done

# THE CHECKS, as the paper's: fixboth's pi_V and price never moved and its budget was not cleared; fixp's price never
# moved and its budget cleared against the target; both solved the distribution every pass and applied the penalties
for a in fixboth fixp; do
    O="$C/cfarm_tf_2c_$a.out"; L="$C/cfarm_tf_2c_$a/cf.log"
    dist_ok $a && note "$a: $(grep -a 'DIST CHECK PASS' "$O")" || note "GUARD: $a failed its distribution check: $(tail -3 "$O" | tr '\n' ' ')"
    grep -a -q "HANDOVER penalty_child_addicted" "$L" || note "GUARD: $a did not apply penalty_child_addicted"
    mkdir -p "$R/$a"
    python3 "$C/cf_runs/finalstats.py" "$L" "$NULLLOG" > "$R/$a/final.txt" 2>&1
    gzip -c "$L" > "$R/$a/cf.log.gz"
    gzip -c "$O" > "$R/$a/run.out.gz"
    [ -f "$C/cfarm_tf_2c_$a/PARAM_HANDOVER.arm.txt" ] && cp "$C/cfarm_tf_2c_$a/PARAM_HANDOVER.arm.txt" "$R/$a/"
    grep -a "CHECK PASS\|GUARD" "$O" > "$R/$a/checks.txt"
    pv=$(grep -a "^ *probability_of_voucher=" "$L" | awk '{print $2}' | sort -u | tr '\n' ' ')
    pr=$(grep -a "^ *price_of_addictive_good=" "$L" | awk '{print $2}' | sort -u | head -3 | tr '\n' ' ')
    note "$a: pi_V values printed: $pv; first drug prices printed: $pr"
done
grep -a "TARGET CHECK PASS" "$C/cfarm_tf_2c_fixp.out" >/dev/null && note "fixp: $(grep -a 'TARGET CHECK PASS' "$C/cfarm_tf_2c_fixp.out")" \
    || note "GUARD: fixp did not clear the budget against $NT"
note "decompositions done"
publish "decompositions done"
