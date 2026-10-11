#!/bin/bash
# remote_deltah_both.sh -- BOTH CHILD PENALTIES, THE LONG RUN (11 October). The author: "remove deltad is a big
# problem....we need to bring it back in. can you actually solve the model with both deltad=0.24 and deltah=0.31?",
# "only solve it for the long run", "it is a very heavy simulation", "you have to first solve the benchmark with both
# deltad=0.24 and deltah=0.31 (and you can fix the parameters to what the benchmark with deltad=0.24 and deltah=0
# are). and then do TF full GE with piv and pv adjusting in the long run".
#
# The build is code/deltah/patch_both.py (build_both.sh): the SUD history keeps delta_d and a homelessness latch,
# homeless at some point while the child was at home, carries delta_h beside it, so the child's class is four-valued
# (neither, SUD parent, homeless parent, both: factors 1, 1 - delta_d, 1 - delta_h and their product); the unemployment
# grid grows from 18 to 36 states and the productivity grid from 26 to 52 nodes, about four times the paper's state.
#
#   STAGE A, the benchmark: the benchmark of record's handover (results/reference/hf_2c_omega_0.085,
#     omega_c 0.085, b 0.0054222, kappa_uem 1.0) with penalty_child_addicted 0.24 and penalty_child_homeless 0.31,
#     every adjuster frozen and omega_c pinned, on code/bench_both/hftf_bench, from the age-one cross section.
#   STAGE B, Housing First re-solved on code/cf_fix2_both against that benchmark (the null arm: the drug price
#     clears, pi_V held), its net revenue the budget target.
#   STAGE C, Treatment First as the paper's arm: detection 0.85, the $35 test, the drug price and pi_V clearing,
#     warm-started at the paper's arm (price 0.8555, pi_V 0.0962), or at the last published pass on a restart.
# No transition. kappa_x is the benchmark of record's. The welfare numbers are read the paper's way afterwards
# (code/paper/welfare_nok.Bench on results/deltah_both, childhood at xi - 1, no kappa_x term).
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltah/remote_deltah_both.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running work. Every 20 minutes
# it pushes results/deltah_both/status.txt; a restart skips what is done (the benchmark, then the null arm).
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltah_both
mkdir -p "$R"
D=$C/deltah_both_run
REF=$REPO/results/reference/hf_2c_omega_0.085
BD=$C/deltah_both_bench
BREF=$C/deltah_both_benchref
TRAILER=$'\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0.24;penalty_child_homeless 0.31"
BLOCKS=${BLOCKS:-16}

note() { echo "remote_deltah_both: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${DELTAH_BOTH_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltah_both: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DELTAH_BOTH_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/deltah_both.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltah_both: started detached, pid $(cat "$D.pid"); log /tmp/deltah_both.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltah_both: finished"; cat "$D.status" 2>/dev/null
    grep -q "arm tf ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# BOTH penalties: delta_d 0.24 and delta_h 0.31 on EVER homeless while the child is at home, four child classes (code/deltah/remote_deltah_both.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        if [ -f "$BD/bench.log" ]; then
            echo; echo "== benchmark"
            grep -a "HANDOVER penalty_child\|HANDOVER omega_c_is_pinned\|DIAG child-class factors\|BLOCK MOVE\|newborn_parent_share (clean\|INVARIANT PASS\|FROZEN" "$BD/bench.log" | tail -40
        fi
        for a in null tf; do
            [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest "$a"; }
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_h both: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

cd "$C"
if [ ! -x "$C/bench_both/hftf_bench" ] || [ ! -x "$C/cf_fix2_both/hftf_cf_prod" ]; then
    note "building"
    bash deltah/build_both.sh both > /tmp/deltah_both_build.log 2>&1 || {
        note "GUARD: build failed: $(tail -3 /tmp/deltah_both_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "built: $(grep -h 'latch flips' /tmp/deltah_both_build.log | tr '\n' ' ' | cut -c1-200)"
fi

# SWAP IS THE MEMORY, NOT INSURANCE (11 October 18:13): the first run was OOM-killed (exit 137) at age 3 of its
# first backward pass, three hours in, with 15 GiB of RAM and 4 GiB of swap: the four-class, six-block state is
# about four times the paper's, and the paper's benchmark holds about 4 to 5 GB. The VM's cgroup limit is
# unbounded, so RAM plus swap is the ceiling; give it the disk (29 GB free on a fresh container), and the
# publish line below reports RSS, swap in use and the pace so the next check can judge fit and speed.
SWAP_GB=${SWAP_GB:-24}
AVAIL_GB=$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)
if [ -z "$(swapon --show 2>/dev/null)" ]; then
    [ "$AVAIL_GB" -lt $((SWAP_GB + 4)) ] && SWAP_GB=$((AVAIL_GB - 4))
    if [ "$SWAP_GB" -ge 8 ]; then
        fallocate -l ${SWAP_GB}G /var/tmp/deltah_both.swap 2>/dev/null && chmod 600 /var/tmp/deltah_both.swap && mkswap /var/tmp/deltah_both.swap >/dev/null 2>&1 \
            && swapon /var/tmp/deltah_both.swap 2>/dev/null && note "$SWAP_GB GiB swap on (disk had $AVAIL_GB GB free)" || note "GUARD: no swap (could not enable $SWAP_GB GiB)"
    else
        note "GUARD: only $AVAIL_GB GB of disk free, too little for swap"
    fi
fi
memline() { echo "rss $(ps -o rss= -p "$1" 2>/dev/null | awk '{printf "%.1f", $1/1048576}') GiB, swap used $(free -m | awk '/Swap/{printf "%.1f", $3/1024}') GiB, $(grep -a AGE_TIME "$2" 2>/dev/null | tail -1 | tr -s ' ' | sed 's/^ //')"; }

# STAGE A: THE BENCHMARK, every parameter fixed
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
    setl penalty_child_addicted 0.24
    setl penalty_child_homeless 0.31
    setl omega_c_is_pinned 1
    setl freeze_all_but_omega_c 1
    setl weight_on_child $W
    setl addiction_scalar_1 $BV
    setl kappa_uem 1.0
    setl kappa_x $KX
    setl frozen_stop_after_blocks $BLOCKS
    cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
    cp "$C/bench_both/hftf_bench" ./hftf_bench
    note "benchmark: solving from the age-one cross section, at most $BLOCKS frozen blocks"
    env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null &
    PID=$!
    for _ in $(seq 1 60); do grep -q -a "HANDOVER penalty_child_homeless" bench.log 2>/dev/null && break; sleep 5; done
    grep -a "HANDOVER penalty_child_addicted\|HANDOVER penalty_child_homeless\|HANDOVER omega_c_is_pinned" bench.log | head -3 | while read -r l; do note "$l"; done
    while kill -0 "$PID" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
        # THE CHECK THE 00:33 T = 70 RUN WOULD HAVE FAILED: the handover must have been applied
        if ! grep -q -a "HANDOVER penalty_child_homeless" bench.log; then
            kill "$PID"; note "GUARD: no HANDOVER line in the benchmark log; killed"; publish "failed"; exit 1
        fi
        kill -0 "$PID" 2>/dev/null && publish "benchmark running, $(grep -ac 'BLOCK MOVE' bench.log) blocks; $(memline "$PID" bench.log)"
    done
    wait "$PID"; RC=$?
    note "benchmark exited $RC after $(grep -ac 'BLOCK MOVE' bench.log) blocks; bench.err: $(tail -2 bench.err | tr '\n' ' ')"
    gzip -c bench.log > "$R/bench.log.gz"
    for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
        [ -s "$f" ] || { note "GUARD: the benchmark did not write $f"; publish "failed"; exit 1; }
    done
    mkdir -p "$BREF"
    tar czf "$BREF/bench_files.tar.gz" *baseline_benchmark.dat
    gzip -c bench.log > "$BREF/bench.log.gz"
    cp PARAM_HANDOVER.kept.txt "$R/PARAM_HANDOVER.bench.txt"
    gzip -c welfare_curvebaseline_benchmark.dat > "$R/welfare_curvebaseline_benchmark.dat.gz"
    publish "benchmark done"
    cd "$C"
fi

export BENCH_FROM=$BREF BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export OMP_NUM_THREADS=2 SEED_FROM=bench DIAG_TAG=_2c BENCH_BIN=$C/bench_both/hftf_bench
export CEV_CURVE=$D.welfare_curve.dat
tar xzf "$BREF/bench_files.tar.gz" -O welfare_curvebaseline_benchmark.dat > "$CEV_CURVE"
# the benchmark's drug users, disorder rate and homelessness, for the passes digest
export PASSES_BASE=$(zcat "$BREF/bench.log.gz" | awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}')
note "benchmark (users, SUD, h_1) $PASSES_BASE"

# run_arm <arm> [VAR=value ...]: on cf_fix2_both, four threads (one arm at a time), the penalties in EXTRA_SET
run_arm() (
    a=$1; shift
    cd "$C"
    note "arm $a on cf_fix2_both: $*"
    env BUILD=cf_fix2_both OMP_NUM_THREADS=4 "$@" sh deltah/cf_arm_both.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        kill -0 "$P" 2>/dev/null && publish "$a running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_${a}_2c/cf.log" 2>/dev/null) passes; $(memline "$P" "$C/cfarm_${a}_2c/cf.log")"
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
    grep -q -a "HANDOVER penalty_child_homeless" "$C/cfarm_${a}_2c/cf.log" || { note "GUARD: arm $a did not apply penalty_child_homeless"; ok=1; }
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)

# STAGE B: HOUSING FIRST
if [ -s "$R/null/net_target.txt" ] && [ -f "$C/cfarm_null_2c/cf.log" ]; then
    NT=$(cat "$R/null/net_target.txt"); note "null arm already accepted, net revenue $NT"
else
    run_arm null DRUG_PRICE_START=1.0 EXTRA_SET="$PENALTIES" || { publish "null not accepted, stopping"; exit 1; }
    NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
    echo "$NT" > "$R/null/net_target.txt"
fi
note "no-policy net revenue $NT is the TF budget target; test cost $CTEST (\$35)"

# STAGE C: TREATMENT FIRST, warm-started at the paper's tf85_c35 equilibrium (or the last published pass)
P0=0.8555; V0=0.0962
if [ -f "$R/status.txt" ]; then
    LAST=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/status.txt")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
fi
run_arm tf PDET=0.85 NET_TARGET="$NT" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES"
publish "complete"
