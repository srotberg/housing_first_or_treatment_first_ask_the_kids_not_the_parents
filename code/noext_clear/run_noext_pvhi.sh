#!/bin/bash
# run_noext_pvhi.sh -- TREATMENT FIRST WITHOUT THE EXTERNALITIES, PARTIAL EQUILIBRIUM: THE DRUG PRICE HELD AT HOUSING
# FIRST'S AND pi_V SET TO 7.61 PER CENT (9 October). The author: "cant you just raise pi_v to 7.61% and keep the price at
# the benchmark and see?", "it should just be a PE run". 7.61 is pi_V where both clear (results/noext_clear/arm_C,
# 0.076132869); here the price does not fall, so this is what that larger voucher programme is worth on its own. Nothing
# clears and the budget is not balanced (adjust_taxes 0). Everything else is run_noext_pvhi.sh's.
#
# (the header of the script this was copied from follows)
# run_noext_pvhi.sh -- TREATMENT FIRST WITHOUT THE EXTERNALITIES, THE DRUG PRICE CLEARING AND pi_V HELD (9 October).
# The author, on the fourth column of Table 5 (both clearing, newborns +0.39 per cent as adults): "Is the gain about
# piv or the cheaper drug? Can you test?". Between the third column (pi_V clears at Housing First's drug price,
# -1.31) and the fourth (both clear, +0.39) two things move at once: the price falls 12 per cent and pi_V ends at
# 7.61 rather than 6.89 per cent. This arm moves only the price: the drug market clears and pi_V stays at Housing
# First's 6.75 per cent, the budget NOT cleared (adjust_taxes 0), as the with-externality decomposition's fixpv arm
# (code/extra_2c/remote_decomp_2c.sh). Set beside the second column (both held, -1.50) it is the cheaper drug alone;
# set beside the fourth it is what the higher pi_V adds.
#
#   Arm A  cfarm_null_pe_noext    Housing First without the externalities, exactly as in run_noext_clear.sh (re-solved:
#                                 the walk needs its policies, which are on no disk).
#   Arm E  cfarm_tf_noext_pvhi  Treatment First as tf85_c35 (detection 0.85, the $35 test, the three-year exclusion)
#                                 with the same switches, on cf_fix2: the drug price CLEARING from arm C's 0.907, pi_V
#                                 HELD at the benchmark's 0.067533863 (adjust_taxes 0).
#   THE SWITCHES, both arms (code/pe_noext/README.md): weight_on_child 0, penalty_child_addicted 0,
#   penalty_child_homeless 0, SS_NO_CLASS=1, kappa_x 0.
#   Then the consumption-equivalent walk on Arm A's policies and pe_noext/analyse.py A against E.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/noext_clear/run_noext_pvhi.sh
# Re-running attaches to a live worker; a finished step is not repeated. Publishes results/noext_pvhi/status.txt.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
W=$C/noext_clear/work_pvhi; mkdir -p "$W"
R=$REPO/results/noext_pvhi; mkdir -p "$R"
REF=$REPO/results/reference/hf_2c_omega_0.085
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
THREADS=${THREADS:-$(python3 -c "import os; print(max(1, min(4, os.cpu_count() // 2)))")}
P_NULL=1.0306231                  # arm A starts at its own converged price (results/noext_pclear/arm_A/final.txt), so it needs few passes
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
SWITCHES="weight_on_child 0;penalty_child_addicted 0;penalty_child_homeless 0"
V_NULL=0.076132869                 # pi_V where both clear (results/noext_clear/arm_C/final.txt), SET in arm E
P_E0=1.0306231                     # Housing First's drug price without externalities (results/noext_pclear/arm_A/final.txt), HELD
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1 0.15 0.2 0.3"
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0 SS_NO_CLASS=1
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$REF/files/welfare_curvebaseline_benchmark.dat

note() { echo "run_noext_pvhi: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/nc.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${NC_DETACHED:-0}" != 1 ]; then
    if alive "$W/nc.pid"; then echo "attached to pid $(cat "$W/nc.pid")"; else
        ( NC_DETACHED=1 setsid nohup bash "$0" > "$W/nc.detached.log" 2>&1 < /dev/null & echo $! > "$W/nc.pid" )
        echo "started detached, pid $(cat "$W/nc.pid")"
    fi
    while alive "$W/nc.pid"; do sleep 60; done
    echo "run_noext_pvhi: finished"; cat "$W/nc.status" 2>/dev/null
    exit 0
fi

publish() (
    {
        echo "# Treatment First without externalities, price clearing, pi_V held (code/noext_clear/run_noext_pvhi.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$W/nc.status" 2>/dev/null
        for d in cfarm_null_pe_noext cfarm_tf_noext_pvhi; do
            L="$C/$d/cf.log"; [ -f "$L" ] || continue
            echo; echo "== $d ($(grep -ac 'CF MOMENTS' "$L") passes done)"
            ( cd "$C" && python3 cf_runs/passes.py "$L" cf_runs/cev.py 2>/dev/null | tail -n 6 )
        done
        [ -f "$R/analysis.txt" ] && { echo; echo "== analysis"; head -n 40 "$R/analysis.txt"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" code/noext_clear/*.sh 2>/dev/null
    git commit -q -m "noext_pvhi: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
wait_publishing() {   # <label> <pid file>...
    l=$1; shift
    while :; do
        any=0; for p in "$@"; do alive "$p" && any=1; done
        [ $any = 1 ] || break
        for _ in $(seq 1 180); do any=0; for p in "$@"; do alive "$p" && any=1; done; [ $any = 1 ] || break; sleep 10; done
        publish "$l"
    done
}
arm_ok() { O="$C/$1.out"; [ -f "$O" ] && tail -n 5 "$O" | grep -q "DIST CHECK PASS" && ! grep -q "GUARD" "$O"; }

command -v gfortran >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc), threads per solve $THREADS"
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && [ "$C/$b/hftf_cf_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ] && continue
    note "building $b"; bash "cf_runs/build_$b.sh" > "/tmp/nc_build_$b.log" 2>&1 || { note "GUARD: build $b failed"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ] || [ "$C/cf_fix2_share/hftf_cf_prod" -ot "$C/cf_fix2/hftf_cf_prod" ]; then
    note "building cf_fix2_share"; bash transition_fix/build_cf_fix2_share.sh > /tmp/nc_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_share_pe/hftf_cf_prod" ] || [ "$C/cf_fix2_share_pe/hftf_cf_prod" -ot "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building the pe builds"; bash pe_noext/build_pe.sh > /tmp/nc_build_pe.log 2>&1 || { note "GUARD: pe builds failed: $(tail -2 /tmp/nc_build_pe.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_walk/hftf_cf_prod" ] || [ "$C/cf_walk/hftf_cf_prod" -ot "$C/cf_fix2_share_pe/hftf_cf_prod" ]; then
    note "building cf_walk"; mkdir -p "$C/cf_walk"
    python3 pe_noext/patch_walk.py cf_fix2_share_pe/cf.f90 cf_walk/cf.f90 > /tmp/nc_patch_walk.log 2>&1 || { note "GUARD: patch_walk failed"; publish "failed"; exit 1; }
    ( cd cf_walk && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ -x "$C/cf_walk/hftf_cf_prod" ] || { note "GUARD: cf_walk did not compile"; publish "failed"; exit 1; }
fi
publish "built"

# ---- Arm A, alone until the benchmark is unpacked; then Arm C beside it
if ! arm_ok cfarm_null_pe_noext; then
    note "arm A (null_pe_noext) on cf_fix2_share_pe, switches '$SWITCHES', price clearing from $P_NULL"
    ( env BUILD=cf_fix2_share_pe OMP_NUM_THREADS=$THREADS DIAG_TAG=_pe_noext SEED_FROM=bench DRUG_PRICE_START=$P_NULL \
        EXTRA_SET="$SWITCHES" sh pe_noext/cf_arm_pe.sh null > "$C/cfarm_null_pe_noext.out" 2>&1 ) &
    echo $! > "$W/arm_A.pid"
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$W/arm_A.pid"; do sleep 10; done
fi
if ! arm_ok cfarm_tf_noext_pvhi; then
    note "arm E (tf_noext_pvhi) on cf_fix2: detection 0.85, test $CTEST, price HELD at $P_E0, pi_V SET at $V_NULL"
    ( env BUILD=cf_fix2 OMP_NUM_THREADS=$THREADS DIAG_TAG=_noext_pvhi SEED_FROM=bench PDET=0.85 \
        PV_START=$V_NULL DRUG_PRICE_START=$P_E0 DRUG_MARKET_ADJUSTER=0 EXTRA_SET="cost_per_drug_test $CTEST;adjust_taxes 0;$SWITCHES" \
        sh pe_noext/cf_arm_pe.sh tf > "$C/cfarm_tf_noext_pvhi.out" 2>&1 ) &
    echo $! > "$W/arm_E.pid"
fi
wait_publishing "arms running" "$W/arm_A.pid" "$W/arm_E.pid"
for a in cfarm_null_pe_noext cfarm_tf_noext_pvhi; do
    arm_ok $a && note "$a: $(grep -a 'CHECK PASS' "$C/$a.out" | tr '\n' ' ')" || note "GUARD: $a failed: $(grep -a 'GUARD' "$C/$a.out" | head -n 3 | tr '\n' ' ')"
done
arm_ok cfarm_null_pe_noext && arm_ok cfarm_tf_noext_pvhi || { publish "an arm failed"; exit 1; }
# THE CHECK THAT MATTERS: pi_V never moved in arm E (the budget was not cleared)
PVS=$(grep -a "^ *probability_of_voucher=" "$C/cfarm_tf_noext_pvhi/cf.log" | awk '{print $2}' | sort -u | tr '\n' ' ')
python3 -c "import sys; v=[float(x) for x in '$PVS'.split()]; sys.exit(0 if v and all(abs(x-$V_NULL)<=1e-8 for x in v) else 1)" \
    && note "PI_V CHECK PASS: arm E ran at pi_V $PVS" || { note "GUARD: arm E's pi_V moved: $PVS"; publish "pi_V moved"; exit 1; }
for a in A:cfarm_null_pe_noext E:cfarm_tf_noext_pvhi; do
    k=${a%%:*}; d=${a#*:}; mkdir -p "$R/arm_$k"
    python3 cf_runs/finalstats.py "$d/cf.log" > "$R/arm_$k/final.txt" 2>&1
    gzip -c "$d/cf.log" > "$R/arm_$k/cf.log.gz"; cp "$d/PARAM_HANDOVER.arm.txt" "$R/arm_$k/" 2>/dev/null
done
note "arm A's net revenue $(grep 'net government revenue' "$R/arm_A/final.txt" | awk '{print $4}'), arm E's $(grep 'net government revenue' "$R/arm_E/final.txt" | awk '{print $4}') (not cleared)"
publish "arms done"

# ---- the walk on Arm A's policies, then the analysis
U=$(grep -a "PE USED" "$C/cfarm_null_pe_noext/cf.log" | tail -n 1)
P_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
python3 -c "float('$P_A')" || { note "GUARD: no PE USED price in arm A's log"; publish "walk failed"; exit 1; }
WD=$C/pe_walk_A
if ! grep -aq "PE WALK done" "$WD/walk.log" 2>/dev/null; then
    note "walk on arm A's policies at drug price $P_A"
    rm -rf "$WD" && cp -a "$C/cfarm_null_pe_noext" "$WD" && cd "$WD"
    rm -f walk_V*.bin
    cp PARAM_HANDOVER.arm.txt PARAM_HANDOVER.txt
    sed -i "s/^drug_price_start .*/drug_price_start $P_A/" PARAM_HANDOVER.txt
    grep -qx "drug_price_start $P_A" PARAM_HANDOVER.txt || { note "GUARD: drug_price_start not set"; publish "walk failed"; exit 1; }
    set -- $XS; { echo $#; for x in "$@"; do echo "$x"; done; } > pe_walk.dat
    cp "$C/cf_walk/hftf_cf_prod" ./hftf_walk
    OMP_NUM_THREADS=$THREADS ./hftf_walk > walk.log 2> walk.err
    grep -aq "PE WALK done" walk.log || { note "GUARD: the walk did not finish: $(tail -n 3 walk.err | tr '\n' ' ')"; publish "walk failed"; exit 1; }
    cd "$C"
fi
note "walk done"
python3 pe_noext/analyse.py cfarm_null_pe_noext cfarm_tf_noext_pvhi pe_walk_A --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written: $(grep -i 'newborn' "$R/analysis.txt" | head -n 3 | tr -s ' ' | tr '\n' ';')" \
    || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
gzip -c "$WD/walk.log" > "$R/walk_A.log.gz" 2>/dev/null
note "done"
publish "done"
