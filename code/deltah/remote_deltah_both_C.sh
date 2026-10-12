#!/bin/bash
# remote_deltah_both_C.sh -- BOTH CHILD PENALTIES, THE LONG RUN, TREATMENT FIRST ON RULE C (12 October). The design is
# remote_deltah_both.sh's (read its header); what differs is how it fits and how it survives a restart:
#
#   BUILDS: code/deltah/build_both_sp.sh -- bench_both_sp/hftf_bench (patch_both + patch_sp: value function and policies
#     stored in four bytes, integers in two, distributions double) and cf_fix2_both_spC/hftf_cf_prod (patch_both +
#     patch_treatC, rule C: a household with the disorder must be in treatment and nobody may use, + patch_sp).
#   MEMORY: the single-precision state, MEASURED on the first loop (12 October): 5.4 GiB through the backward passes, then
#     13.6 GiB of RSS and 3.7 GiB of swap (17.3 GiB) in the distribution stage, with no swap traffic there (the swapped
#     part is cold). So 10 GiB of swap (SWAP_GB), topped up if a smaller swap is already on.
#   DISK: the four-class benchmark set is about 8.9 GB of text; nothing is tarred or copied. The arms hard-link the
#     benchmark's large files (cf_arm_both_sp.sh BENCH_DIR), send their own value function and policies to /dev/null
#     (NULL_COUNTER_SET=1: 8.9 GB nothing reads; the distributions kept), and the launcher checks that no file of the
#     benchmark's set changed. Reserved on the disk besides the swap: 13 GB.
#   CHECKPOINTS: the benchmark RESUMES IN PLACE. The Fortran writes calibration_state.dat and calibration_distribution
#     {1,2}.dat at the end of each loop and reads them on start, but the handover is deleted as it is read and 69 of its
#     97 lines (the grids, the flags, frozen_stop_after_blocks, kappa_x, ...) are not in the state file, so a resume
#     re-supplies exactly those lines (PARAM_HANDOVER.resume.txt) and the state file carries the rest. After each
#     completed loop the state, the distribution and the logs go, gzipped and split under 90 MB, to the orphan branch
#     ckpt/deltah-bothC (force-pushed); a fresh container restores from it. When the benchmark is done its whole set
#     goes there too, so a fresh container skips stage A. Arms resume from their last published pass.
#
#   STAGE A, the benchmark: results/reference/hf_2c_omega_0.085's handover with penalty_child_addicted 0.24 and
#     penalty_child_homeless 0.31, every adjuster frozen, omega_c 0.085 pinned, b 0.0054222, kappa_uem 1.0, kappa_x
#     0.9342362271804227, at most 16 frozen blocks, from the age-one cross section.
#   STAGE B, Housing First re-solved against it: the drug price clears, pi_V held; its net revenue the budget target.
#   STAGE C, Treatment First on rule C: detection 0.85, the $35 test, the drug price and pi_V clearing against B's net
#     revenue, warm-started at results/counterfactuals_2c/tf_ruleC's latest pass if it has one (else 0.8555, 0.0962),
#     or at this run's own last published pass on a restart.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/deltah/remote_deltah_both_C.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running work. Every 20 minutes it
# pushes results/deltah_both_C/status.txt with the solver's RSS, the swap in use and the pace.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
CKPT=ckpt/deltah-bothC
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/deltah_both_C
mkdir -p "$R"
D=$C/deltah_bothC_run
REF=$REPO/results/reference/hf_2c_omega_0.085
BD=$C/deltah_bothC_bench
CK=$C/deltah_bothC_ckpt
URL=$(git -C "$REPO" remote get-url origin)
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=0.0004946100
python3 -c "import sys; sys.exit(0 if abs(35/(9e6/80)*1.589817990383-$CTEST)<1e-10 else 1)" || { echo "GUARD: CTEST is not \$35"; exit 1; }
KX=0.9342362271804227; BV=0.0054222; W=0.085
PENALTIES="penalty_child_addicted 0.24;penalty_child_homeless 0.31"
BLOCKS=${BLOCKS:-16}
T0=$(date +%s)

note() { echo "remote_deltah_both_C: $* ($(date -u '+%d %H:%M'))" | tee -a "$D.status"; }

if [ "${DELTAH_BOTHC_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_deltah_both_C: attaching to the running work, pid $(cat "$D.pid")"
    else
        ( DELTAH_BOTHC_DETACHED=1 setsid nohup bash "$0" "$@" >> /tmp/deltah_bothC.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_deltah_both_C: started detached, pid $(cat "$D.pid"); log /tmp/deltah_bothC.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_deltah_both_C: finished"; tail -30 "$D.status" 2>/dev/null
    grep -q "arm tf ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

[ -f "$D.t0" ] || date +%s > "$D.t0"     # the first launch, for the total runtime
T0=$(cat "$D.t0")
touch "$D.status"; echo "=== launch $(date -u '+%d %b %H:%M UTC')" >> "$D.status"
PEAK=$D.peak; [ -f "$PEAK" ] || echo "0 0" > "$PEAK"      # peak rss GiB, peak rss+swap GiB

digest() (
    cd "$C"
    L="cfarm_${1}_2c/cf.log"
    [ -f "$L" ] && python3 cf_runs/passes.py "$L" "$C/cf_runs/cev.py" 2>/dev/null
)
publish() (
    {
        echo "# BOTH penalties on rule C: delta_d 0.24 and delta_h 0.31, four child classes, single precision (code/deltah/remote_deltah_both_C.sh); $(date -u '+%d %b %H:%M UTC'), $(( ($(date +%s) - T0) / 3600 )) h since the first launch"
        echo "# peak rss / rss+swap (GiB): $(cat "$PEAK"); free disk $(df -h "$C" | tail -1 | awk '{print $4}')"
        cat "$D.status" 2>/dev/null
        if [ -f "$BD/bench.log" ]; then
            echo; echo "== benchmark"
            grep -a "HANDOVER penalty_child\|HANDOVER omega_c_is_pinned\|resumed from calibration_state\|warm start distribution\|DIAG child-class factors\|BLOCK MOVE\|newborn_parent_share (clean\|INVARIANT PASS\|FROZEN" "$BD/bench.log" | tail -40
        fi
        for a in null tf; do
            [ -f "$C/cfarm_${a}_2c/cf.log" ] && { echo; echo "== $a"; digest "$a"; }
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "delta_h both, rule C: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q --autostash FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
memline() {  # memline PID LOG: rss, swap, the last AGE_TIME line; keeps the peaks
    local rss sw
    rss=$(ps -o rss= -p "$1" 2>/dev/null | awk '{printf "%.1f", $1/1048576}'); sw=$(free -m | awk '/Swap/{printf "%.1f", $3/1024}')
    [ -n "$rss" ] && awk -v r="$rss" -v s="$sw" '{a=$1; b=$2; if (r>a) a=r; if (r+s>b) b=r+s; print a, b}' "$PEAK" > "$PEAK.tmp" && mv "$PEAK.tmp" "$PEAK"
    echo "rss $rss GiB, swap used $sw GiB, $(grep -a AGE_TIME "$2" 2>/dev/null | tail -1 | tr -s ' ' | sed 's/^ //')"
}

# ckpt_push LABEL DIR FILE...: gzip, split under 90 MB, force-push to the orphan branch $CKPT from a throwaway repository
# (so the checkout's own .git never holds the blobs). The branch holds ONE snapshot: what was pushed last.
ckpt_push() (
    label=$1; src=$2; shift 2
    rm -rf "$CK.push" && mkdir -p "$CK.push/files" && cd "$CK.push" || exit 1
    for f in "$@"; do
        [ -f "$src/$f" ] || continue
        gzip -c "$src/$f" | split -b 85m -d -a 3 - "files/$f.gz.part"
    done
    ( cd files && sha256sum * > ../SHA256SUMS )
    echo "$label, $(date -u '+%d %b %H:%M UTC'); restore: cat files/NAME.gz.part* | gunzip > NAME" > README
    git init -q && git checkout -q --orphan ckpt && git add -A && git commit -q -m "checkpoint: $label$TRAILER" || exit 1
    for i in 1 2 3 4; do
        git push -q -f "$URL" HEAD:refs/heads/$CKPT 2>/dev/null && { cd /; rm -rf "$CK.push"; exit 0; }
        sleep $((2 ** i))
    done
    cd /; rm -rf "$CK.push"; exit 1
)
# ckpt_fetch DIR: restore the branch's snapshot into DIR; prints the label
ckpt_fetch() (
    rm -rf "$CK.fetch"
    git clone -q --depth 1 --single-branch --branch "$CKPT" "$URL" "$CK.fetch" 2>/dev/null || exit 1
    cd "$CK.fetch" || exit 1
    [ -d files ] && grep -q "benchmark" README || exit 1
    ( cd files && sha256sum -c --quiet ../SHA256SUMS ) || exit 1
    mkdir -p "$1"
    for p in files/*.gz.part000; do
        n=$(basename "$p" .gz.part000)
        cat files/"$n".gz.part* | gunzip > "$1/$n" || exit 1
    done
    head -1 README
    cd /; rm -rf "$CK.fetch"
)

command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

cd "$C"
if [ ! -x "$C/bench_both_sp/hftf_bench" ] || [ ! -x "$C/cf_fix2_both_spC/hftf_cf_prod" ]; then
    note "building"
    bash deltah/build_both_sp.sh > /tmp/deltah_bothC_build.log 2>&1 || {
        note "GUARD: build failed: $(tail -3 /tmp/deltah_bothC_build.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "built: $(grep -h 'warnings=' /tmp/deltah_bothC_build.log | tr '\n' ' ' | cut -c1-240)"
fi
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_both_spC/cf.f90" && grep -q "jagged_matrix_transition_real4" "$C/cf_fix2_both_spC/cf.f90" \
    && grep -q "jagged_matrix_transition_real4" "$C/bench_both_sp/cf.f90" || { note "GUARD: the builds are not rule C / single precision"; publish "failed"; exit 1; }

# SWAP: the footprint is 17+ GiB on 15.7 GiB of RAM (measured, header). The disk keeps 13 GB for the runs' own files: the
# benchmark set (8.9 GB), the calibration distribution (1.2 GB, deleted once the benchmark is done), the two arms'
# distributions, the checkpoint staging. A swap already on (a re-launch in the same container) is topped up.
SWAP_GB=${SWAP_GB:-10}
ON_GB=$(swapon --show=SIZE --bytes --noheadings 2>/dev/null | awk '{s+=$1} END{printf "%d", s/1073741824+0.5}')
if [ "$ON_GB" -lt "$SWAP_GB" ]; then
    AVAIL_GB=$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)
    ADD=$((SWAP_GB - ON_GB)); [ $((AVAIL_GB - 13)) -lt "$ADD" ] && ADD=$((AVAIL_GB - 13))
    if [ "$ADD" -ge 1 ]; then
        SW=/var/tmp/deltah_bothC.swap.$(date +%s)
        fallocate -l ${ADD}G "$SW" 2>/dev/null && chmod 600 "$SW" && mkswap "$SW" >/dev/null 2>&1 \
            && swapon "$SW" 2>/dev/null && note "$ADD GiB swap added to $ON_GB (disk had $AVAIL_GB GB free)" || note "GUARD-WARN: could not add $ADD GiB of swap"
    else
        note "GUARD-WARN: swap $ON_GB GiB, and $AVAIL_GB GB of disk free leaves none to add with 13 reserved"
    fi
else
    note "swap already on: $ON_GB GiB"
fi
export GFORTRAN_UNBUFFERED_PRECONNECTED=y     # the log lines (AGE_TIME, the pace) arrive when written, not in 8 KB lumps

# STAGE A: THE BENCHMARK, every parameter fixed, resumed in place
if [ ! -f "$BD/BENCH_COMPLETE" ] && [ ! -f "$BD/calibration_state.dat" ]; then
    # a fresh container: the benchmark's finished set, or the last loop's checkpoint, from the branch
    rm -rf "$BD.restore"
    if L=$(ckpt_fetch "$BD.restore"); then
        note "checkpoint restored: $L"
        rm -rf "$BD"; mv "$BD.restore" "$BD"
        # a restored finished set is newer than its stamp: stamp it again, after the files, for the unchanged-set check
        [ -f "$BD/BENCH_COMPLETE" ] && { sleep 1; date +%s > "$BD/BENCH_COMPLETE"; }
        ln -sfn ../../data "$BD/data"
        cp "$C/bench_both_sp/hftf_bench" "$BD/hftf_bench"
    else
        rm -rf "$BD.restore"; note "no checkpoint on $CKPT, the benchmark starts from the age-one cross section"
    fi
fi
if [ -f "$BD/BENCH_COMPLETE" ]; then
    note "benchmark already solved, $BD"
else
    mkdir -p "$BD" && cd "$BD"
    [ -e data ] || ln -s ../../data data
    cp "$C/bench_both_sp/hftf_bench" ./hftf_bench
    setl() {
        if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
        grep -qx "$1 $2" PARAM_HANDOVER.txt || { note "GUARD: $1 is not $2"; publish "failed"; exit 1; }
    }
    if [ -f PARAM_HANDOVER.kept.txt ] && [ -f calibration_state.dat ] && grep -q -a "handover banked into calibration_state.dat" bench.log 2>/dev/null; then
        # RESUME IN PLACE. The state file the run banked (and rewrote after each loop) carries what it carries; the
        # handover lines it does not carry are re-supplied, with the four the design fixes (the penalties, omega_c, b,
        # kappa_uem) re-supplied as well, at their launch values. loop_count restarts at 0 on every launch (it is not
        # read back: the state's loop number goes to resumed_loop_count), so frozen_stop_after_blocks is cut by the
        # blocks already done, and the first block after a resume always counts as a move of 1 (no previous block).
        DONE=$(grep -ac "BLOCK MOVE" bench.log); LEFT=$((BLOCKS - DONE)); [ "$LEFT" -lt 2 ] && LEFT=2
        python3 - "$LEFT" <<'PYEOF' || { note "GUARD: could not make the resume handover"; publish "failed"; exit 1; }
import re, sys
s = open('../bench_both_sp/cf.f90').read()   # the state file's layout is the binary's: read it from its source
i = s.index('subroutine write_calibration_state()'); j = s.index('end subroutine', i)
state = set(re.findall(r"write\(71,'[^']*'\)\s*([A-Za-z_0-9]+)", s[i:j]))
fixed = {'penalty_child_addicted', 'penalty_child_homeless', 'weight_on_child', 'addiction_scalar_1', 'kappa_uem'}
keep = [l for l in open('PARAM_HANDOVER.kept.txt') if l.split() and (l.split()[0] not in state or l.split()[0] in fixed)]
keep = [('frozen_stop_after_blocks %s\n' % sys.argv[1]) if l.split()[0] == 'frozen_stop_after_blocks' else l for l in keep]
open('PARAM_HANDOVER.resume.txt', 'w').writelines(keep)
PYEOF
        cp PARAM_HANDOVER.resume.txt PARAM_HANDOVER.txt
        for k in penalty_child_addicted weight_on_child addiction_scalar_1 kappa_uem; do
            grep -q "^$k " PARAM_HANDOVER.txt || { note "GUARD: resume handover lacks $k"; publish "failed"; exit 1; }
        done
        for k in penalty_child_homeless frozen_stop_after_blocks freeze_all_but_omega_c omega_c_is_pinned kappa_x; do
            grep -q "^$k " PARAM_HANDOVER.txt || { note "GUARD: resume handover lacks $k"; publish "failed"; exit 1; }
        done
        grep -q "^penalty_child_addicted " PARAM_HANDOVER.kept.txt && grep -q "^weight_on_child " PARAM_HANDOVER.kept.txt || { note "GUARD: kept handover incomplete"; publish "failed"; exit 1; }
        MODE=resume
        note "benchmark: RESUMING IN PLACE, $DONE blocks done, at most $LEFT more (state $(date -u -r calibration_state.dat '+%d %H:%M'), distribution $( [ -f calibration_distribution_shape.dat ] && date -u -r calibration_distribution_shape.dat '+%d %H:%M' || echo none)), $(wc -l < PARAM_HANDOVER.txt) handover lines re-supplied"
    else
        rm -f calibration_* bench.log bench.err LOOPS_PUSHED
        cp "$C/scan_seed/calibration_state.dat" .
        cp "$REF/PARAM_HANDOVER.bench.txt" PARAM_HANDOVER.txt
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
        echo 0 > LOOPS_PUSHED
        MODE=fresh
        note "benchmark: solving from the age-one cross section, at most $BLOCKS frozen blocks"
    fi
    NH=$(grep -c . PARAM_HANDOVER.txt)
    echo "=== $MODE launch $(date -u '+%d %b %H:%M UTC'), $NH handover lines" >> bench.log
    env OMP_NUM_THREADS=4 ./hftf_bench >> bench.log 2>> bench.err < /dev/null &
    PID=$!
    START_LINE=$(grep -an "^=== $MODE launch" bench.log | tail -1 | cut -d: -f1)
    for _ in $(seq 1 60); do tail -n +"$START_LINE" bench.log | grep -q -a "HANDOVER penalty_child_homeless" && break; sleep 5; done
    tail -n +"$START_LINE" bench.log | grep -a "HANDOVER penalty_child_addicted\|HANDOVER penalty_child_homeless\|HANDOVER omega_c_is_pinned\|HANDOVER frozen_stop_after_blocks\|resumed from calibration_state\|warm start distribution\|WARM START REFUSED" | head -6 | while read -r l; do note "$l"; done
    [ "$MODE" = resume ] && ! tail -n +"$START_LINE" bench.log | grep -q -a "warm start distribution loaded" && \
        note "GUARD-WARN: the resume did not load the distribution (it rebuilds from the age-one cross section)"
    while kill -0 "$PID" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$PID" 2>/dev/null || break; sleep 10; done
        # the handover must have been applied, every line of it
        if ! tail -n +"$START_LINE" bench.log | grep -q -a "HANDOVER penalty_child_homeless"; then
            kill "$PID"; note "GUARD: no HANDOVER line in the benchmark log; killed"; publish "failed"; exit 1
        fi
        if [ "$(stat -c%s bench.log)" -gt 4000000000 ]; then
            kill "$PID"; note "GUARD: bench.log passed 4 GB (the first launch printed 975 MB of budget residuals in 30 minutes); killed"; publish "failed"; exit 1
        fi
        if tail -n +"$START_LINE" bench.log | grep -q -a "HANDOVER IGNORED"; then
            kill "$PID"; note "GUARD: a handover line was ignored: $(grep -a 'HANDOVER IGNORED' bench.log | tail -1)"; publish "failed"; exit 1
        fi
        # A COMPLETED LOOP: the distribution is written after the state, so its shape stamp newer than the last push
        if [ -f calibration_distribution_shape.dat ] && [ calibration_distribution_shape.dat -nt LOOPS_PUSHED ] && [ ! calibration_state.dat -nt calibration_distribution_shape.dat ]; then
            mkdir -p snap && rm -f snap/*
            for f in calibration_state.dat calibration_distribution1.dat calibration_distribution2.dat calibration_distribution_shape.dat newborn_parent_share.dat resume_seed.dat; do
                [ -f "$f" ] && ln "$f" snap/    # the binary writes a .tmp and renames, so a link is a consistent snapshot
            done
            cp PARAM_HANDOVER.kept.txt snap/; [ -f PARAM_HANDOVER.resume.txt ] && cp PARAM_HANDOVER.resume.txt snap/
            cp bench.log bench.err snap/
            n=$(( $(cat LOOPS_PUSHED) + 1 ))
            echo $n > snap/LOOPS_PUSHED
            if ckpt_push "benchmark loop checkpoint $n ($(grep -ac 'BLOCK MOVE' bench.log) blocks)" "$BD/snap" $(ls snap); then
                echo $n > LOOPS_PUSHED; note "checkpoint $n pushed to $CKPT"
            else
                note "checkpoint $n NOT pushed"
            fi
            rm -rf snap
        fi
        kill -0 "$PID" 2>/dev/null && publish "benchmark running, $(grep -ac 'BLOCK MOVE' bench.log) blocks; $(memline "$PID" bench.log)"
    done
    wait "$PID"; RC=$?
    note "benchmark exited $RC after $(grep -ac 'BLOCK MOVE' bench.log) blocks; bench.err: $(tail -2 bench.err | tr '\n' ' ')"
    for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat value_function1baseline_benchmark.dat distribution_stationary1baseline_benchmark.dat; do
        [ -s "$f" ] || { note "GUARD: the benchmark did not write $f"; publish "failed"; exit 1; }
    done
    [ "$RC" = 0 ] || { note "GUARD: the benchmark exited $RC"; publish "failed"; exit 1; }
    # the set's own sizes, for the record and for the next check
    note "benchmark set: $(ls *baseline_benchmark.dat | wc -l) files, $(du -cb *baseline_benchmark.dat | tail -1 | awk '{printf "%.2f GB", $1/1e9}')"
    date +%s > BENCH_COMPLETE
    gzip -c bench.log > "$R/bench.log.gz"
    cp PARAM_HANDOVER.kept.txt "$R/PARAM_HANDOVER.bench.txt"
    mkdir -p "$R/bench_small"
    for f in *baseline_benchmark.dat; do [ "$(stat -c%s "$f")" -le 1048576 ] && gzip -c "$f" > "$R/bench_small/$f.gz"; done
    publish "benchmark done"
    # the whole set to the checkpoint branch, so a fresh container skips stage A
    if ckpt_push "the solved benchmark (BENCH_COMPLETE)" "$BD" $(ls *baseline_benchmark.dat) bench.log bench.err PARAM_HANDOVER.kept.txt BENCH_COMPLETE calibration_state.dat; then
        note "the solved benchmark set pushed to $CKPT"
    else
        note "GUARD-WARN: the solved benchmark set could not be pushed to $CKPT (the run goes on)"
    fi
    rm -f calibration_distribution1.dat calibration_distribution2.dat     # 1.2 GB, no longer needed
    cd "$C"
fi
[ -e "$BD/data" ] || ln -s ../../data "$BD/data"
setcheck() {  # no file of the benchmark's set may change under an arm (they are hard-linked into it)
    local n; n=$(find "$BD" -maxdepth 1 -name '*baseline_benchmark.dat' -newer "$BD/BENCH_COMPLETE" | wc -l)
    [ "$n" = 0 ] || { note "GUARD: $n files of the benchmark set changed after it was solved: $(find "$BD" -maxdepth 1 -name '*baseline_benchmark.dat' -newer "$BD/BENCH_COMPLETE" | head -3 | tr '\n' ' ')"; return 1; }
}
setcheck || { publish "failed"; exit 1; }

export BENCH_DIR=$BD BENCH_B=$BV BENCH_OMEGA=$W BENCH_KU=1.0 KAPPA_X=$KX
export OMP_NUM_THREADS=4 SEED_FROM=bench DIAG_TAG=_2c BENCH_BIN=$C/bench_both_sp/hftf_bench NULL_COUNTER_SET=1
export CEV_CURVE=$BD/welfare_curvebaseline_benchmark.dat
export PASSES_BASE=$(awk '/INVARIANT PASS +drug users/{b=$NF} /INVARIANT PASS +disorder rate/{l=$NF} /INVARIANT PASS +homelessness rate/{h=$NF} END{print b","l","h}' "$BD/bench.log")
note "benchmark (users, SUD, h_1) $PASSES_BASE"
# cfarm_bench is rebuilt from BD (links) unless it already links to BD's current set
if [ -f "$C/cfarm_bench/BENCH_DONE" ] && [ "$(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)" = "$BD" ] && \
   [ "$(stat -c%i "$C/cfarm_bench/value_function1baseline_benchmark.dat" 2>/dev/null)" = "$(stat -c%i "$BD/value_function1baseline_benchmark.dat")" ]; then :
else rm -rf "$C/cfarm_bench"; fi

# run_arm <arm> [VAR=value ...]: on cf_fix2_both_spC, four threads, the penalties in EXTRA_SET
run_arm() (
    a=$1; shift
    cd "$C"
    note "arm $a on cf_fix2_both_spC: $*"
    env BUILD=cf_fix2_both_spC "$@" sh deltah/cf_arm_both_sp.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 &
    P=$!
    while kill -0 "$P" 2>/dev/null; do
        for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
        Q=$(pgrep -x -n hftf_cf 2>/dev/null || echo "$P")
        if [ "$(stat -c%s "$C/cfarm_${a}_2c/cf.log" 2>/dev/null || echo 0)" -gt 4000000000 ]; then
            kill "$Q"; note "GUARD: arm $a's cf.log passed 4 GB; killed"
        fi
        kill -0 "$P" 2>/dev/null && publish "$a running, $(grep -ac '^ *distance_govt_budget=' "$C/cfarm_${a}_2c/cf.log" 2>/dev/null) passes; $(memline "$Q" "$C/cfarm_${a}_2c/cf.log")"
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
    grep -q -a "HANDOVER penalty_child_addicted" "$C/cfarm_${a}_2c/cf.log" || { note "GUARD: arm $a did not apply penalty_child_addicted"; ok=1; }
    setcheck || ok=1
    [ "$rc" = 0 ] || ok=1
    if [ "$ok" = 0 ]; then note "arm $a ACCEPTED (exit $rc): $(tr '\n' ' ' < "$R/$a/checks.txt")"
    else note "arm $a NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
    publish "$a finished"
    return $ok
)
last_pass() {  # last_pass <arm>: "price pi_V" of the arm's last pass in the published status
    [ -f "$R/status.txt" ] && awk -v a="$1" '$0=="== "a{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$R/status.txt"
}

# STAGE B: HOUSING FIRST
if [ -s "$R/null/net_target.txt" ] && grep -q "arm null ACCEPTED" "$D.status" "$R/status.txt" 2>/dev/null; then
    NT=$(cat "$R/null/net_target.txt"); note "null arm already accepted, net revenue $NT"
else
    P0=1.0; LAST=$(last_pass null); [ -n "$LAST" ] && { P0=${LAST% *}; note "null resumes from its last published pass: price $P0"; }
    run_arm null DRUG_PRICE_START="$P0" EXTRA_SET="$PENALTIES" || { publish "null not accepted, stopping"; exit 1; }
    NT=$(grep -a "^ *net_govt_revenues=" "$C/cfarm_null_2c/cf.log" | tail -1 | awk '{print $2}')
    python3 -c "float('$NT')" 2>/dev/null || { note "GUARD: no net revenue in the null arm's log"; publish "failed"; exit 1; }
    echo "$NT" > "$R/null/net_target.txt"
    publish "null net revenue $NT"
fi
# the null arm's counter set is not needed any more (8.9 GB); its distribution is kept
find "$C/cfarm_null_2c" -maxdepth 1 -name '*counter_arm.dat' ! -name 'distribution_stationary*' -size +1M -delete 2>/dev/null
note "no-policy net revenue $NT is the Treatment First budget target; test cost $CTEST (\$35); free disk $(df -h "$C" | tail -1 | awk '{print $4}')"

# STAGE C: TREATMENT FIRST ON RULE C, warm-started at the rule-C main arm's latest pass, or this run's own
P0=0.8555; V0=0.0962
MAIN=$REPO/results/counterfactuals_2c/tf_ruleC/passes.txt
git -C "$REPO" fetch -q origin "$BRANCH" 2>/dev/null && git -C "$REPO" show FETCH_HEAD:results/counterfactuals_2c/tf_ruleC/passes.txt > "$D.mainpasses" 2>/dev/null && MAIN=$D.mainpasses
if [ -f "$MAIN" ]; then
    LAST=$(awk '$1 ~ /^[0-9]+$/ && NF > 3 {p=$2; v=$3} END{if (p) print p, v}' "$MAIN")
    [ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "warm start at the rule-C main arm's latest pass: price $P0, pi_V $V0"; }
fi
LAST=$(last_pass tf)
[ -n "$LAST" ] && { P0=${LAST% *}; V0=${LAST#* }; note "resuming from the last published pass: price $P0, pi_V $V0"; }
run_arm tf PDET=0.85 NET_TARGET="$NT" PV_START="$V0" DRUG_PRICE_START="$P0" EXTRA_SET="cost_per_drug_test $CTEST;$PENALTIES"
publish "complete"
