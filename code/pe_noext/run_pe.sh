#!/bin/bash
# run_pe.sh -- the partial-equilibrium, no-externality experiment (README.md), both arms in order.
#
#   Arm A  null_pe_noext  Housing First (no policy) on cf_fix2_share_pe, as the accepted no-policy arm
#                         ran (run_arms.sh 'null'): drug price CLEARING at adjuster 0.1 from P_NULL,
#                         pi_V at the benchmark's, adjust_taxes 0; plus the switches that remove the
#                         externalities. -> code/cfarm_null_pe_noext
#   Arm B  tf_pe_noext    Treatment First as tf85_c35 (detection 0.85, the $35 test, the three-year
#                         exclusion, no false positives) with the same switches, on cf_fix2_pe, with the
#                         drug price, pi_V and the house price HELD at the values Arm A's LAST solve used
#                         (its last PE USED line), adjust_taxes 0. Seeded from Arm A's distribution.
#                         -> code/cfarm_tf_pe_noext
#
# THE SWITCHES, both arms: weight_on_child 0 (omega_c: the parent's value carries no child term),
# penalty_child_addicted 0 and penalty_child_homeless 0 (the child's inherited productivity penalty),
# SS_NO_CLASS=1 (the class-1 nodes' Social Security benefits equal to class 0's: the benchmark's
# file carries the penalty in retirement income), kappa_x 0 (the homelessness disamenity, which
# enters welfare statistics only).
#
# Detached (setsid nohup); re-running attaches. Publishes results/pe_noext/status.txt about every 30
# minutes.   bash code/pe_noext/run_pe.sh
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
W=$C/pe_noext/work; mkdir -p "$W"
R=$REPO/results/pe_noext; mkdir -p "$R"
REF=$REPO/results/reference/hf_2c_omega_0.085
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
P_NULL=1.0001082
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
SWITCHES="weight_on_child 0;penalty_child_addicted 0;penalty_child_homeless 0"
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0 SS_NO_CLASS=1
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$REF/files/welfare_curvebaseline_benchmark.dat

note() { echo "run_pe: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/pe.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${PE_DETACHED:-0}" != 1 ]; then
    if alive "$W/pe.pid"; then echo "attached to pid $(cat "$W/pe.pid")"; else
        ( PE_DETACHED=1 setsid nohup bash "$0" > "$W/pe.detached.log" 2>&1 < /dev/null & echo $! > "$W/pe.pid" )
        echo "started detached, pid $(cat "$W/pe.pid")"
    fi
    exit 0
fi

publish() (
    {
        echo "# PE experiment without externalities (code/pe_noext); $(date -u '+%d %b %H:%M UTC')"
        [ -f "$R/QUESTION.txt" ] && cat "$R/QUESTION.txt"
        cat "$W/pe.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_pe_noext/cf.log"
            [ -f "$L" ] || continue
            echo; echo "== arm $a ($(grep -ac 'CF MOMENTS' "$L") passes done)"
            ( cd "$C" && python3 cf_runs/passes.py "$L" cf_runs/cev.py 2>/dev/null )
            grep -a "PE USED\|PE HOLD" "$L" | tail -n 2
        done
        [ -f "$W/walk.status" ] && { echo; echo "== CEV walk"; cat "$W/walk.status"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" code/pe_noext/*.sh code/pe_noext/*.py code/pe_noext/*.md 2>/dev/null
    git commit -q -m "pe_noext: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
wait_publishing() {   # <pid file> <label>
    while alive "$1"; do
        for _ in $(seq 1 180); do alive "$1" || break; sleep 10; done
        alive "$1" && publish "$2"
    done
}
arm_ok() { O="$C/cfarm_${1}_pe_noext.out"; tail -n 5 "$O" | grep -q "DIST CHECK PASS" && ! grep -q "GUARD" "$O"; }

note "free memory $(free -g | awk '/Mem/{print $7}') GiB available, cores $(nproc)"
cd "$C"

# ---- Arm A
if ! arm_ok null; then
    note "arm A (null_pe_noext) on cf_fix2_share_pe: switches '$SWITCHES', kappa_x 0, SS_NO_CLASS, price clearing from $P_NULL"
    ( env BUILD=cf_fix2_share_pe OMP_NUM_THREADS=4 DIAG_TAG=_pe_noext SEED_FROM=bench DRUG_PRICE_START=$P_NULL \
        EXTRA_SET="$SWITCHES" sh pe_noext/cf_arm_pe.sh null > "$C/cfarm_null_pe_noext.out" 2>&1 ) &
    echo $! > "$W/arm_A.pid"
    wait_publishing "$W/arm_A.pid" "arm A running"
    arm_ok null || { note "GUARD: arm A failed: $(grep -a 'GUARD' "$C/cfarm_null_pe_noext.out" | head -n 3 | tr '\n' ' ')"; publish "arm A failed"; exit 1; }
fi
note "arm A: $(grep -a 'CHECK PASS' "$C/cfarm_null_pe_noext.out" | tr '\n' ' ')"
U=$(grep -a "PE USED" "$C/cfarm_null_pe_noext/cf.log" | tail -n 1)
HP_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="housing_price=") print $(i+1)}')
P_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
PV_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="pi_V=") print $(i+1)}')
python3 -c "import sys; [float(x) for x in sys.argv[1:4]]" "$HP_A" "$P_A" "$PV_A" || { note "GUARD: no PE USED prices in arm A's log"; publish "arm A prices missing"; exit 1; }
note "arm A's last solve used: drug price $P_A, pi_V $PV_A, house price $HP_A"
publish "arm A done, p_A $P_A"

# ---- Arm B
if ! arm_ok tf; then
    note "arm B (tf_pe_noext) on cf_fix2_pe: detection 0.85, test $CTEST, held price $P_A, pi_V $PV_A, house price $HP_A, adjust_taxes 0"
    ( env BUILD=cf_fix2_pe OMP_NUM_THREADS=4 DIAG_TAG=_pe_noext SEED_FROM=cfarm_null_pe_noext PDET=0.85 \
        PV_START=$PV_A DRUG_PRICE_START=$P_A DRUG_MARKET_ADJUSTER=0 HOUSING_PRICE_HOLD=$HP_A \
        EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES" \
        sh pe_noext/cf_arm_pe.sh tf > "$C/cfarm_tf_pe_noext.out" 2>&1 ) &
    echo $! > "$W/arm_B.pid"
    wait_publishing "$W/arm_B.pid" "arm B running"
    arm_ok tf || { note "GUARD: arm B failed: $(grep -a 'GUARD' "$C/cfarm_tf_pe_noext.out" | head -n 3 | tr '\n' ' ')"; publish "arm B failed"; exit 1; }
fi
note "arm B: $(grep -a 'CHECK PASS' "$C/cfarm_tf_pe_noext.out" | tr '\n' ' ')"
publish "arm B done"
touch "$W/ARMS_DONE"
note "arms done"
