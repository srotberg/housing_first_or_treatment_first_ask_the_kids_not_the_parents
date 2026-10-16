#!/bin/bash
# run_paths_CA100.sh -- COPY of run_paths_C.sh (16 October) for the Costantini comparison under the CA rule at detection 1.00: Treatment
# First on cf_fix2_treatCA (treat/build_treatCA.sh, rule A's screen on rule C's build) at PDET 1.00, Housing First the
# CORRECTED one (cf_fix2_share_treatCu, internal_computations fix ungated; NET_TARGET 5.8371628), arms
# cfarm_null_2c_CA100 and cfarm_tf_2c_fixboth_CA100, work directories work_CA100, results to results/revoked_2c_CA100
# and results/revoked_2c_street_CA100. Otherwise the original, which follows.
# run_paths_C.sh -- RULE-C COPY of revoked_2c_street/run_paths.sh (12 October). Binaries from revoked_2c_street/build_C.sh
# (work_C), the arms of revoked_2c/run_arms_C.sh (cfarm_tf_2c_fixboth_CA100), results to results/revoked_2c_street_C, status
# published every 20 minutes. Two changes beyond the names: (1) it waits for revoked_2c/run_paths_C.sh to finish
# (work_C/PATHS_DONE), because memory and disk do not hold two of these pipelines at once (the original's own notes:
# plain + split at T = 3 were killed at 16 GB; a staged run holds about 5 GB); (2) the T = 3 plain and unsplit tracking
# guard runs are taken from revoked_2c/work_C when that pipeline's plain3 and track3 sources are byte-identical to this
# build's (they are the same patches on the same source), instead of being run a second time. The header follows.
# run_paths.sh -- the SMI x street split's runs (README.md). Waits for code/revoked_2c/run_arms.sh (ARMS_DONE) and build.sh,
# then: (1) T = 3 guards on ONE thread: plain3 and street3 together, then track3; (2) the T = 10 Treatment First path
# (street10, 4 threads) and, (3) from its tags, the T = 10 Housing First path; then analyse_street.py. Staging and the fixed
# paths exactly as code/revoked_2c/run_paths.sh. At most two runs at once. Detached; re-running attaches. Publishes
# results/revoked_2c_street/status.txt about every 30 minutes (commit + push of results/revoked_2c_street and this dir only).
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); REPO=$(cd "$C/.." && pwd)
W=$R/work_CA100; A=$C/revoked_2c/work_CA100; OUT=$REPO/results/revoked_2c_street_CA100; mkdir -p "$W" "$OUT"; printf "*\n" > "$W/.gitignore"   # work_CA100 is never committed
# 13 Oct: Housing First's net revenue with its own treatment spending (treat/net_target_with_treatment.py)
NET_TARGET=5.8275447063
# 16 Oct: the CORRECTED Housing First's (cf_fix2_share_treatCu)
NET_TARGET=5.8371628
P_NULL=1.0001082; V_NULL=0.067533863
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

note() { echo "run_paths_street: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/paths.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${PATHS_DETACHED:-0}" != 1 ]; then
    if alive "$W/paths.pid"; then echo "attached to pid $(cat "$W/paths.pid")"; else
        ( PATHS_DETACHED=1 setsid nohup bash "$0" > "$W/paths.detached.log" 2>&1 < /dev/null & echo $! > "$W/paths.pid" )
        echo "started detached, pid $(cat "$W/paths.pid")"
    fi
    exit 0
fi

publish() (
    {
        [ -f "$W/QUESTION" ] && cat "$W/QUESTION"
        echo "# SMI x street split of the revoked-voucher experiment, RULE CA, DETECTION 1.00 (code/revoked_2c_street/run_paths_CA100.sh); $(date -u '+%d %b %H:%M UTC')"
        echo "## stage 1, the two steady states (code/revoked_2c/run_arms_CA100.sh)"; cat "$A/arms.status" 2>/dev/null
        echo "## builds"; cat "$W/build.log" 2>/dev/null | grep -v '^patched\|^written'
        echo "## stage 2, the runs"; cat "$W/paths.status" 2>/dev/null
        for d in g_plain3_1t g_street3_1t g_track3_1t tf10 hf10; do
            L="$W/$d/run.log"; [ -f "$L" ] || continue
            echo "-- $d: $(grep -a -c 'REVK PERIOD DONE' "$L") forward periods done; last line: $(tail -1 "$L" | cut -c1-150)"
        done
        true
    } > "$OUT/status.txt.tmp" && mv "$OUT/status.txt.tmp" "$OUT/status.txt"
    cd "$REPO" || exit 0
    git add "$OUT" "$R" 2>/dev/null
    git commit -q -m "revoked 2c street split rule CA det 1.00: $1$TRAILER" -- "$OUT" "$R" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
wait_pub() {   # <pid file>... : publish about every 30 minutes while any runs
    local last; last=$(date +%s)
    while :; do
        local any=0; for p in "$@"; do alive "$p" && any=1; done
        [ $any = 1 ] || break
        sleep 60
        if [ $(( $(date +%s) - last )) -ge 1200 ]; then publish "${PUBMSG:-running}"; last=$(date +%s); fi
    done
}
stage() {   # <dir> <binary> <terminal arm>: code/revoked_2c/run_paths.sh's staging, verbatim
    local N=$1 BIN=$2 ARM=$3
    rm -rf "$N"
    bash "$C/transition_fix/stage_tr_fix.sh" "$N" "$BIN" "$C/$ARM" "$C/cfarm_null_2c_CA100" "$NET_TARGET" > "$N.stage.log" 2>&1 \
        || { note "GUARD: staging $N failed: $(tail -3 "$N.stage.log" | tr '\n' ' ')"; return 1; }
    for f in PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt; do
        for kv in "adjust_taxes 0" "drug_market_adjuster 0"; do
            k=${kv% *}
            if grep -q "^$k " "$N/$f"; then sed -i "s|^$k .*|$kv|" "$N/$f"; else echo "$kv" >> "$N/$f"; fi
            grep -qx "$kv" "$N/$f" || { note "GUARD: $kv not set in $N/$f"; return 1; }
        done
    done
    T=$(grep -m1 "parameter :: transition_length" "$(dirname "$BIN")/tr.f90" | grep -oE "solve_transition_dynamics\*[0-9]+" | cut -d'*' -f2)
    python3 - "$N" "$T" "$P_NULL" "$V_NULL" <<'PYEOF'
import sys
n, T, p, v = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
for name, val in (("drug_price_path_seed.txt", p), ("pi_v_path_seed.txt", v)):
    with open(f"{n}/{name}", "w") as f:
        f.write(f"# HELD at the no-policy value {val} in every year (code/revoked_2c)\n# periods 1 to {T-1}\n")
        f.writelines(f"{val}\n" for _ in range(T - 1))
PYEOF
    note "staged $(basename "$N") (T=$T, terminal $ARM)"
}
launch() {   # <dir> <threads> <mode> [tagdir]
    local free; free=$(df -BG --output=avail "$1" | tail -1 | tr -dc 0-9)
    [ "$free" -ge 4 ] || { note "GUARD: only ${free} GB of disk left at the launch of $(basename "$1")"; return 1; }
    ( cd "$1" && date +%s > START_EPOCH && OMP_NUM_THREADS=$2 REVK_MODE=$3 REVK_TAGDIR=${4:-.} ./hftf > run.log 2>&1; echo "exit $?" > EXIT ) &
    echo $! > "$1.pid"
}
done_run() { grep -q "REVK STOP" "$1/run.log" 2>/dev/null; }

: >> "$W/paths.status"
note "waiting for the arms and the builds"
lastpub=$(date +%s)
while [ ! -f "$A/ARMS_DONE" ] || [ ! -f "$A/PATHS_DONE" ] || alive "$W/build.pid"; do
    sleep 60
    if [ $(( $(date +%s) - lastpub )) -ge 1200 ]; then publish "waiting for revoked_2c/run_paths_CA100.sh"; lastpub=$(date +%s); fi
    alive "$A/paths.pid" || [ -f "$A/PATHS_DONE" ] || { note "GUARD: revoked_2c/run_paths_CA100.sh is not running and did not finish"; publish "blocked"; exit 1; }
done
for b in plain3 track3 street3 street10; do [ -x "$W/$b/hftf_tr" ] || { note "GUARD: build $b missing"; publish "blocked"; exit 1; }; done
for a in null_2c_CA100 tf_2c_fixboth_CA100; do
    tail -5 "$C/cfarm_$a.out" | grep -q "DIST CHECK PASS" && ! grep -q GUARD "$C/cfarm_$a.out" || { note "GUARD: arm $a failed: $(tail -3 "$C/cfarm_$a.out" | tr '\n' ' ')"; publish "blocked"; exit 1; }
done
grep -q "VOUCHER CHECK PASS" "$C/cfarm_null_2c_CA100.out" || { note "GUARD: null arm voucher check"; publish "blocked"; exit 1; }
[ -s "$C/cfarm_null_2c_CA100/newborn_parent_share_counter.dat" ] || { note "GUARD: no parent share"; publish "blocked"; exit 1; }
mkdir -p "$OUT/arms"
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_null_2c_CA100/cf.log" > "$OUT/arms/null_final.txt" 2>&1
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_tf_2c_fixboth_CA100/cf.log" "$C/cfarm_null_2c_CA100/cf.log" > "$OUT/arms/fixboth_final.txt" 2>&1
note "against earlier runs (null against the corrected Housing First, must match; fixboth against rule C at 0.20, differs): $(python3 "$C/revoked_2c/compare_arms.py" "$OUT/arms/null_final.txt" "$REPO/results/decomp_2c_shares_Cu/arm_fixboth/null_final.txt" "$OUT/arms/fixboth_final.txt" "$REPO/results/revoked_2c_C/arms/fixboth_final.txt" 2>&1 | tr '\n' ' ')"
publish "arms re-solved"

# (1) T = 3 GUARDS, ONE THREAD (no race). MEMORY: the split build carries 18 more shadow masses (about 1.4 GB) and
# plain + split together were killed by the kernel (exit 137, 16 GB, no swap). So: plain and unsplit tracking together,
# then the split alone; then each T = 10 path alone.
# DISK: revoked_2c/run_paths_CA100.sh leaves its later guard directories' .dat files; free them (logs and tags stay)
find "$A"/g_* "$A"/tf10 "$A"/hf10 -name '*.dat' -size +10M -delete 2>/dev/null
for g in plain3 track3; do
    if ! done_run "$W/g_${g}_1t" && done_run "$A/g_${g}_1t" && cmp -s "$A/$g/tr.f90" "$W/$g/tr.f90"; then
        mkdir -p "$W/g_${g}_1t"; cp "$A/g_${g}_1t/run.log" "$A/g_${g}_1t/EXIT" "$W/g_${g}_1t/" 2>/dev/null
        note "g_${g}_1t taken from revoked_2c/work_CA100 (identical tr.f90): $(cat "$W/g_${g}_1t/EXIT" 2>/dev/null)"
    fi
done
if ! done_run "$W/g_plain3_1t" || ! done_run "$W/g_track3_1t"; then
    if ! done_run "$W/g_plain3_1t" && ! alive "$W/g_plain3_1t.pid"; then
        { stage "$W/g_plain3_1t" "$W/plain3/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_plain3_1t" 1 off; } || { publish "blocked"; exit 1; }
    fi
    if ! done_run "$W/g_track3_1t" && ! alive "$W/g_track3_1t.pid"; then
        { stage "$W/g_track3_1t" "$W/track3/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_track3_1t" 1 tf; } || { publish "blocked"; exit 1; }
    fi
    note "T = 3 plain and unsplit tracking running, one thread each"
    PUBMSG="T = 3 plain and unsplit tracking running (one thread)" wait_pub "$W/g_plain3_1t.pid" "$W/g_track3_1t.pid"
fi
if ! done_run "$W/g_street3_1t"; then
    { stage "$W/g_street3_1t" "$W/street3/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_street3_1t" 1 tf; } || { publish "blocked"; exit 1; }
    note "T = 3 split tracking running alone, one thread"
    PUBMSG="T = 3 split tracking running (one thread)" wait_pub "$W/g_street3_1t.pid"
fi
note "street3: $(cat "$W/g_street3_1t/EXIT")"
# (2) the T = 10 Treatment First path, alone, four threads
if ! done_run "$W/tf10"; then
    stage "$W/tf10" "$W/street10/hftf_tr" cfarm_tf_2c_fixboth_CA100 || { publish "blocked"; exit 1; }
    launch "$W/tf10" 4 tf; note "T = 10 Treatment First path running"
    PUBMSG="T = 10 Treatment First path running" wait_pub "$W/tf10.pid"
fi
note "tf10: $(cat "$W/tf10/EXIT"); $(grep -a -c 'REVK TAG WRITTEN' "$W/tf10/run.log") tags"
python3 "$R/analyse_street.py" guard "$W/g_plain3_1t/run.log" "$W/g_street3_1t/run.log" "$W/g_track3_1t/run.log" > "$OUT/guard_T3.txt" 2>&1
note "T = 3 guards: $(grep -a 'GUARD SUMMARY' "$OUT/guard_T3.txt")"
for d in g_plain3_1t g_street3_1t g_track3_1t; do gzip -c "$W/$d/run.log" > "$OUT/${d#g_}_run.log.gz"; done
gzip -c "$W/tf10/run.log" > "$OUT/tf10_run.log.gz"
# DISK: each staged run holds about 5 GB of .dat files; the first tf10 died at period 4 when the session's disk
# allowance ran out (ENOSPC) with the three guard directories still full. Free them, and tf10's, before hf10 (the
# tags hf10 reads are .bin files and stay).
find "$W"/g_* "$W"/tf10 -name '*.dat' -size +10M -delete 2>/dev/null
grep -q "GUARD SUMMARY: PASS" "$OUT/guard_T3.txt" || { note "GUARD: the T = 3 guards did not pass, stopping before the Housing First path"; publish "blocked at the T = 3 guards"; exit 1; }
publish "T = 3 guards passed; T = 10 Treatment First path done"
# (3) the Housing First path from the tags
if ! done_run "$W/hf10"; then
    stage "$W/hf10" "$W/street10/hftf_tr" cfarm_null_2c_CA100 || { publish "blocked"; exit 1; }
    launch "$W/hf10" 4 hf "$W/tf10"; note "T = 10 Housing First path running"
    PUBMSG="T = 10 Housing First path running" wait_pub "$W/hf10.pid"
fi
note "hf10: $(cat "$W/hf10/EXIT")"
gzip -c "$W/hf10/run.log" > "$OUT/hf10_run.log.gz"
find "$W"/tf10 "$W"/hf10 -name '*.dat' -size +10M -delete 2>/dev/null
python3 "$R/analyse_street.py" main "$W/tf10/run.log" "$W/hf10/run.log" > "$OUT/tables.md" 2>&1
note "analysis: $(grep -a 'HEADLINE' "$OUT/tables.md" | head -6 | tr '\n' ' ')"
touch "$W/PATHS_DONE"
publish "all runs done, tables written"
