#!/bin/bash
# noext_Cu_lib.sh -- noext_C_lib.sh AGAINST THE CORRECTED HOUSING FIRST (14 October; code/RULE_C_PLAN.md, '05:20 THE
# DIAGNOSTIC'). patch_treatC2's internal_computations fix was gated on the screen, so the no-externality Arm A (Housing
# First) ran the old arithmetic and the Treatment First arms the corrected one. This copy differs from noext_C_lib.sh in:
#   * Arm A (cfarm_null_pe_noext_Cu) runs on cf_fix2_share_pe_treatCu (treat/build_share_pe_treatCu.sh: the gate removed),
#     price clearing from P_NULL = the gated Arm A's price (results/pe_noext_C/arm_A/final.txt) instead of 1.0001082;
#   * NET_A, the target of the pi_V-clearing arms D and C, is NOT hard-coded: net_A() reads the corrected Arm A's own
#     final net revenue (cf_runs/finalstats.py on its log), so it is called only after wait_arm_A;
#   * its own shared dir (noext_Cu_shared), walk (pe_walk_A_Cu), launcher scripts (*_Cu.sh) and arm script
#     (pe_noext/cf_arm_pe_noext_Cu.sh, which admits the new build); results go to results/*_Cu;
#   * clean_arm <dir>: removes a finished Treatment First arm's directory once its analysis.json is written and its
#     files are saved, because one container now holds the benchmark, Arm A, four arms and the walk (about 4 GB each).
# The Treatment First arms run on cf_fix2_treatC / cf_fix2_pe_treatC as before: with the screen on the gate was already
# open, so they are bit for bit the _C arithmetic. noext_C_lib.sh's header follows.
# noext_C_lib.sh -- RULE C (12 October): the machinery the three rule-C no-externality launchers share, sourced by
# pe_noext/run_pe_C.sh (Arm B), noext_clear/run_noext_fixp_C.sh (Arm D) and noext_clear/run_noext_clear_C.sh (Arm C).
# Each launcher is its rule-A counterpart (run_pe.sh + run_walk.sh, run_noext_fixp.sh, run_noext_clear.sh) on the
# rule-C build, with three differences:
#   * ONE Arm A for all three. Arm A is Housing First, which has no screen, so rule C does not touch it; it is re-solved
#     once in this container (cfarm_null_pe_noext_C) because the walks, Arm B's seed and the analyses need its files on
#     disk. Whichever launcher comes first starts it; the others wait for it.
#   * A SOLVE GATE. At most MAXSOLVES (default 2) solves of 2 threads each run at once (4 cores, 15 GiB), counted as
#     live hftf_cf / hftf_walk processes, checked and started under one lock so two launchers cannot both take the
#     last slot. The benchmark is unpacked by Arm A alone (cf_arm_pe_noext_C.sh's stage 1 deletes cfarm_bench first).
#   * the status is published every 20 minutes, under a lock shared by the three, since they share one checkout.
# Needs, before sourcing: TAG (short name), R (results dir), W (work dir), STATUS (status file in W), HEADER.
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
SH=$C/noext_Cu_shared; mkdir -p "$SH" "$W" "$R"
REF=$REPO/results/reference/hf_2c_omega_0.085
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
THREADS=${NOEXT_THREADS:-2}   # (8 November) NOEXT_THREADS for run_noext_col.sh, one column per container
MAXSOLVES=${MAXSOLVES:-2}
P_NULL=${CU_P_NULL:-$(awk '/^  drug price /{print $NF}' "$REPO/results/pe_noext_C/arm_A/final.txt")}   # the gated Arm A's price
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
SWITCHES="weight_on_child 0;penalty_child_addicted 0;penalty_child_homeless 0"
# NET_A: the corrected Arm A's OWN final net revenue (the gated one was hard-coded at 6.3180936). set_net_A sets it;
# call it after wait_arm_A
NET_A=
set_net_A() {
    NET_A=$(cd "$C" && python3 cf_runs/finalstats.py "$A_DIR/cf.log" 2>/dev/null | awk '/net government revenue/{print $NF}')
    python3 -c "import sys; v=float('$NET_A'); sys.exit(0 if 4<v<9 else 1)" 2>/dev/null || { note "GUARD: no net revenue in arm A's final stats ('$NET_A')"; publish "arm A net revenue missing"; exit 1; }
    note "NET_A = $NET_A (the corrected arm A's final net revenue; the gated one was 6.3180936)"
}
A_DIR=cfarm_null_pe_noext_Cu       # the shared Arm A, on the ungated build
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0 SS_NO_CLASS=1
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$REF/files/welfare_curvebaseline_benchmark.dat

note() { echo "$TAG: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/$STATUS"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
nsolves() { echo $(( $(pgrep -xc hftf_cf || true) + $(pgrep -xc hftf_walk || true) )); }
# arm_ok <dir> [target]: DIST CHECK PASS at the end, no GUARD, and with 'target' TARGET CHECK PASS too
arm_ok() { O="$C/$1.out"; [ -f "$O" ] && tail -n 5 "$O" | grep -q "DIST CHECK PASS" && ! grep -q "GUARD" "$O" \
    && { [ "${2:-}" != target ] || grep -q "TARGET CHECK PASS" "$O"; }; }

publish() (
    {
        echo "# $HEADER; $(date -u '+%d %b %H:%M UTC')"
        cat "$W/$STATUS" 2>/dev/null
        for d in $ARMS_SHOWN; do
            L="$C/$d/cf.log"; [ -f "$L" ] || continue
            echo; echo "== $d ($(grep -ac 'CF MOMENTS' "$L") passes done)"
            ( cd "$C" && python3 cf_runs/passes.py "$L" cf_runs/cev.py 2>/dev/null | tail -n 8 )
            grep -a "PE USED" "$L" | tail -n 1
            grep -a "MILBY SPLIT" "$L" | tail -n 1
        done
        [ -f "$R/analysis.txt" ] && { echo; echo "== analysis"; head -n 40 "$R/analysis.txt"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    exec 8> "$SH/git.lock"; flock 8
    git add "$R" code/noext_clear/*_Cu.sh code/noext_clear/noext_Cu_lib.sh code/pe_noext/*_Cu.sh code/treat/build_share_pe_treatCu.sh 2>/dev/null
    git commit -q -m "$TAG: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
# wait_publishing <label> <pid file>...: every 20 minutes while any of them lives
wait_publishing() {
    l=$1; shift
    while :; do
        any=0; for p in "$@"; do alive "$p" && any=1; done
        [ $any = 1 ] || break
        for _ in $(seq 1 120); do any=0; for p in "$@"; do alive "$p" && any=1; done; [ $any = 1 ] || break; sleep 10; done
        publish "$l"
    done
}
# start_gated <pid file> <output file> <command...>: waits for a free slot (publishing meanwhile), starts the command
# in the background with its output in the file, and holds the lock until its solver process is up (or it has died)
start_gated() {
    pf=$1; of=$2; shift 2
    t=0
    exec 9> "$SH/slot.lock"
    while :; do
        flock 9
        if [ "$(nsolves)" -lt "$MAXSOLVES" ]; then break; fi
        flock -u 9; sleep 30; t=$((t + 30))
        [ $((t % 1200)) = 0 ] && publish "waiting for a slot"
    done
    n0=$(nsolves)
    ( "$@" ) > "$of" 2>&1 &
    echo $! > "$pf"
    for _ in $(seq 1 120); do [ "$(nsolves)" -gt "$n0" ] && break; alive "$pf" || break; sleep 10; done
    flock -u 9; exec 9>&-
}
# the shared Arm A: start it if nobody has (and it is not done), and wait until the benchmark is unpacked
start_arm_A() {
    exec 7> "$SH/armA.lock"; flock 7
    if ! arm_ok $A_DIR && ! alive "$SH/arm_A.pid"; then
        note "arm A ($A_DIR) on cf_fix2_share_pe_treatCu (internal_computations fix ungated), switches '$SWITCHES', price clearing from $P_NULL"
        start_gated "$SH/arm_A.pid" "$C/$A_DIR.out" env BUILD=cf_fix2_share_pe_treatCu OMP_NUM_THREADS=$THREADS DIAG_TAG=_pe_noext_Cu SEED_FROM=bench \
            DRUG_PRICE_START=$P_NULL EXTRA_SET="$SWITCHES" sh "$C/pe_noext/cf_arm_pe_noext_Cu.sh" null
        while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$SH/arm_A.pid"; do sleep 10; done
    fi
    flock -u 7; exec 7>&-
    until [ -f "$C/cfarm_bench/BENCH_DONE" ] || arm_ok $A_DIR; do
        alive "$SH/arm_A.pid" || { note "GUARD: arm A is not running and the benchmark is not unpacked"; publish "arm A failed"; exit 1; }
        sleep 30
    done
}
wait_arm_A() {
    wait_publishing "arm A running" "$SH/arm_A.pid"
    arm_ok $A_DIR || { note "GUARD: arm A failed: $(grep -a 'GUARD' "$C/$A_DIR.out" | head -n 3 | tr '\n' ' ')"; publish "arm A failed"; exit 1; }
}
build_all() {
    command -v gfortran >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
    command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
    python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
    exec 6> "$SH/build.lock"; flock 6
    if [ ! -x "$C/cf_fix2_pe_treatC/hftf_cf_prod" ] || [ ! -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || [ ! -x "$C/cf_walk/hftf_cf_prod" ]; then
        note "building (pe_noext/build_pe_C.sh)"
        bash "$C/pe_noext/build_pe_C.sh" > "$W/build.log" 2>&1 || { note "GUARD: build failed: $(tail -n 2 "$W/build.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
    fi
    # after build_pe_C.sh, which makes cf_fix2_share_pe (the base this patches)
    [ -x "$C/cf_fix2_share_pe_treatC/hftf_cf_prod" ] || bash "$C/treat/build_share_treatC.sh" share_pe > "$W/build_share_pe_treatC.log" 2>&1 || { note "GUARD: build cf_fix2_share_pe_treatC failed: $(tail -n 2 "$W/build_share_pe_treatC.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
    [ -x "$C/cf_fix2_share_pe_treatCu/hftf_cf_prod" ] || bash "$C/treat/build_share_pe_treatCu.sh" > "$W/build_share_pe_treatCu.log" 2>&1 || { note "GUARD: build cf_fix2_share_pe_treatCu failed: $(tail -n 2 "$W/build_share_pe_treatCu.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
    flock -u 6; exec 6>&-
    grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_pe_treatCu/cf.f90" || { note "GUARD: the ungated fix is not in cf_fix2_share_pe_treatCu"; publish "failed"; exit 1; }
    for b in cf_fix2_treatC cf_fix2_pe_treatC; do
        grep -q "RULE C (patch_treatC.py)" "$C/$b/cf.f90" || { note "GUARD: rule C is not in $b"; publish "failed"; exit 1; }
    done
}
# save_arm <letter> <dir>: final.txt, cf.log.gz and the handover, as the rule-A results hold them
save_arm() {
    mkdir -p "$R/arm_$1"
    ( cd "$C" && python3 cf_runs/finalstats.py "$2/cf.log" > "$R/arm_$1/final.txt" 2>&1 )
    gzip -c "$C/$2/cf.log" > "$R/arm_$1/cf.log.gz"; cp "$C/$2/PARAM_HANDOVER.arm.txt" "$R/arm_$1/" 2>/dev/null
    cp "$C/$2.out" "$R/arm_$1/arm.out" 2>/dev/null
    true
}
# run_walk <walk dir> <xs>: the consumption-equivalent walk on Arm A's policies at Arm A's last drug price
run_walk() {
    WD=$C/$1; XS=$2
    exec 5> "$SH/$1.lock"; flock 5
    if ! grep -aq "PE WALK done" "$WD/walk.log" 2>/dev/null; then
        U=$(grep -a "PE USED" "$C/$A_DIR/cf.log" | tail -n 1)
        P_A=$(echo "$U" | awk '{for(i=1;i<=NF;i++) if($i=="drug_price=") print $(i+1)}')
        python3 -c "float('$P_A')" || { note "GUARD: no PE USED price in arm A's log"; publish "walk failed"; exit 1; }
        note "walk ($1) on arm A's policies at drug price $P_A"
        rm -rf "$WD" && cp -a "$C/$A_DIR" "$WD"
        ( cd "$WD" && rm -f walk_V*.bin && cp PARAM_HANDOVER.arm.txt PARAM_HANDOVER.txt \
          && sed -i "s/^drug_price_start .*/drug_price_start $P_A/" PARAM_HANDOVER.txt )
        grep -qx "drug_price_start $P_A" "$WD/PARAM_HANDOVER.txt" || { note "GUARD: drug_price_start not set"; publish "walk failed"; exit 1; }
        set -- $XS; { echo $#; for x in "$@"; do echo "$x"; done; } > "$WD/pe_walk.dat"
        cp "$C/cf_walk/hftf_cf_prod" "$WD/hftf_walk"
        start_gated "$W/walk.pid" "$WD/walk.out" bash -c "cd '$WD' && OMP_NUM_THREADS=$THREADS ./hftf_walk > walk.log 2> walk.err"
        while alive "$W/walk.pid"; do sleep 10; done
        grep -aq "PE WALK done" "$WD/walk.log" || { note "GUARD: the walk did not finish: $(tail -n 3 "$WD/walk.err" | tr '\n' ' ')"; publish "walk failed"; exit 1; }
    fi
    flock -u 5; exec 5>&-
    note "walk done ($1)"
}
# detach: re-running attaches to a live worker and follows it until it ends
detach() {
    if [ "${NC_C_DETACHED:-0}" != 1 ]; then
        if alive "$W/run.pid"; then echo "attached to pid $(cat "$W/run.pid")"; else
            ( NC_C_DETACHED=1 setsid nohup bash "$1" > "$W/run.detached.log" 2>&1 < /dev/null & echo $! > "$W/run.pid" )
            echo "started detached, pid $(cat "$W/run.pid")"
        fi
        while alive "$W/run.pid"; do sleep 60; done
        echo "$TAG: finished"; cat "$W/$STATUS" 2>/dev/null
        exit 0
    fi
}
# clean_arm <dir>: the arm's directory goes once the launcher's analysis.json is written and its files are in $R
clean_arm() {
    [ -s "$R/analysis.json" ] && [ -s "$R/arm_$2/final.txt" ] && [ -s "$R/arm_$2/cf.log.gz" ] || { note "keeping $1 (analysis or saved files missing)"; return 0; }
    rm -rf "${C:?}/$1" && note "removed $1 (saved in $R/arm_$2; free disk now $(df -h "$C" | tail -1 | awk '{print $4}'))"
}
