#!/bin/bash
# run_paths.sh -- the SMI split's runs (README.md). Waits for code/revoked_2c/run_arms.sh (ARMS_DONE) and build.sh,
# then: (1) T = 3 guards on ONE thread: plain3 and smi3 together, then track3; (2) the T = 10 Treatment First path
# (smi10, 4 threads) and, (3) from its tags, the T = 10 Housing First path; then analyse_smi.py. Staging and the fixed
# paths exactly as code/revoked_2c/run_paths.sh. At most two runs at once. Detached; re-running attaches. Publishes
# results/revoked_2c_smi/status.txt about every 30 minutes (commit + push of results/revoked_2c_smi and this dir only).
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); REPO=$(cd "$C/.." && pwd)
W=$R/work; A=$C/revoked_2c/work; OUT=$REPO/results/revoked_2c_smi; mkdir -p "$W" "$OUT"
NET_TARGET=5.8918410999831181
P_NULL=1.0001082; V_NULL=0.067533863
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

note() { echo "run_paths_smi: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/paths.status"; }
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
        echo "# SMI split of the revoked-voucher experiment (code/revoked_2c_smi); $(date -u '+%d %b %H:%M UTC')"
        echo "## stage 1, the two steady states (code/revoked_2c/run_arms.sh)"; cat "$A/arms.status" 2>/dev/null
        echo "## builds"; cat "$R/work_build.log" 2>/dev/null | grep -v '^patched\|^written'
        echo "## stage 2, the runs"; cat "$W/paths.status" 2>/dev/null
        for d in g_plain3_1t g_smi3_1t g_track3_1t tf10 hf10; do
            L="$W/$d/run.log"; [ -f "$L" ] || continue
            echo "-- $d: $(grep -a -c 'REVK PERIOD DONE' "$L") forward periods done; last line: $(tail -1 "$L" | cut -c1-150)"
        done
        true
    } > "$OUT/status.txt.tmp" && mv "$OUT/status.txt.tmp" "$OUT/status.txt"
    cd "$REPO" || exit 0
    git add "$OUT" "$R" 2>/dev/null
    git commit -q -m "revoked 2c SMI split: $1$TRAILER" -- "$OUT" "$R" || return 0
    for i in 1 2 3 4; do
        git pull -q --rebase origin "$BRANCH" && git push -q -u origin HEAD:"$BRANCH" && return 0
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
        if [ $(( $(date +%s) - last )) -ge 1740 ]; then publish "${PUBMSG:-running}"; last=$(date +%s); fi
    done
}
stage() {   # <dir> <binary> <terminal arm>: code/revoked_2c/run_paths.sh's staging, verbatim
    local N=$1 BIN=$2 ARM=$3
    rm -rf "$N"
    bash "$C/transition_fix/stage_tr_fix.sh" "$N" "$BIN" "$C/$ARM" "$C/cfarm_null_2c" "$NET_TARGET" > "$N.stage.log" 2>&1 \
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
    ( cd "$1" && date +%s > START_EPOCH && OMP_NUM_THREADS=$2 REVK_MODE=$3 REVK_TAGDIR=${4:-.} ./hftf > run.log 2>&1; echo "exit $?" > EXIT ) &
    echo $! > "$1.pid"
}
done_run() { grep -q "REVK STOP" "$1/run.log" 2>/dev/null; }

: >> "$W/paths.status"
note "waiting for the arms and the builds"
while [ ! -f "$A/ARMS_DONE" ] || alive "$R/build.pid"; do sleep 60; done
for b in plain3 track3 smi3 smi10; do [ -x "$W/$b/hftf_tr" ] || { note "GUARD: build $b missing"; publish "blocked"; exit 1; }; done
for a in null_2c tf_2c_fixboth; do
    tail -5 "$C/cfarm_$a.out" | grep -q "DIST CHECK PASS" && ! grep -q GUARD "$C/cfarm_$a.out" || { note "GUARD: arm $a failed: $(tail -3 "$C/cfarm_$a.out" | tr '\n' ' ')"; publish "blocked"; exit 1; }
done
grep -q "VOUCHER CHECK PASS" "$C/cfarm_null_2c.out" || { note "GUARD: null arm voucher check"; publish "blocked"; exit 1; }
[ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no parent share"; publish "blocked"; exit 1; }
mkdir -p "$OUT/arms"
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_null_2c/cf.log" > "$OUT/arms/null_final.txt" 2>&1
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_tf_2c_fixboth/cf.log" "$C/cfarm_null_2c/cf.log" > "$OUT/arms/fixboth_final.txt" 2>&1
note "against the accepted runs: $(python3 "$C/revoked_2c/compare_arms.py" "$OUT/arms/null_final.txt" "$REPO/results/counterfactuals_2c/nulltf/null/final.txt" "$OUT/arms/fixboth_final.txt" "$REPO/results/decomp_2c_both/arm_fixboth/final.txt" 2>&1 | tr '\n' ' ')"
publish "arms re-solved"

# (1) T = 3 GUARDS, ONE THREAD (no race): plain and split together, then the unsplit tracking
if ! done_run "$W/g_plain3_1t" || ! done_run "$W/g_smi3_1t"; then
    done_run "$W/g_plain3_1t" || { stage "$W/g_plain3_1t" "$W/plain3/hftf_tr" cfarm_tf_2c_fixboth && launch "$W/g_plain3_1t" 1 off; } || { publish "blocked"; exit 1; }
    done_run "$W/g_smi3_1t"   || { stage "$W/g_smi3_1t" "$W/smi3/hftf_tr" cfarm_tf_2c_fixboth && launch "$W/g_smi3_1t" 1 tf; } || { publish "blocked"; exit 1; }
    note "T = 3 guard pair (plain, split) running, one thread each"
    PUBMSG="T = 3 guard pair running (one thread)" wait_pub "$W/g_plain3_1t.pid" "$W/g_smi3_1t.pid"
fi
# (2) the unsplit tracking at T = 3 (one thread) beside the T = 10 Treatment First path (four threads)
if ! done_run "$W/g_track3_1t"; then
    stage "$W/g_track3_1t" "$W/track3/hftf_tr" cfarm_tf_2c_fixboth && launch "$W/g_track3_1t" 1 tf || { publish "blocked"; exit 1; }
fi
if ! done_run "$W/tf10"; then
    stage "$W/tf10" "$W/smi10/hftf_tr" cfarm_tf_2c_fixboth || { publish "blocked"; exit 1; }
    launch "$W/tf10" 4 tf; note "T = 10 Treatment First path running; T = 3 unsplit tracking beside it"
    PUBMSG="T = 10 Treatment First path running" wait_pub "$W/tf10.pid" "$W/g_track3_1t.pid"
fi
note "tf10: $(cat "$W/tf10/EXIT"); $(grep -a -c 'REVK TAG WRITTEN' "$W/tf10/run.log") tags"
python3 "$R/analyse_smi.py" guard "$W/g_plain3_1t/run.log" "$W/g_smi3_1t/run.log" "$W/g_track3_1t/run.log" > "$OUT/guard_T3.txt" 2>&1
note "T = 3 guards: $(grep -a 'GUARD SUMMARY' "$OUT/guard_T3.txt")"
for d in g_plain3_1t g_smi3_1t g_track3_1t; do gzip -c "$W/$d/run.log" > "$OUT/${d#g_}_run.log.gz"; done
gzip -c "$W/tf10/run.log" > "$OUT/tf10_run.log.gz"
find "$W"/g_* -name '*.dat' -size +10M -delete 2>/dev/null
grep -q "GUARD SUMMARY: PASS" "$OUT/guard_T3.txt" || { note "GUARD: the T = 3 guards did not pass, stopping before the Housing First path"; publish "blocked at the T = 3 guards"; exit 1; }
publish "T = 3 guards passed; T = 10 Treatment First path done"
# (3) the Housing First path from the tags
if ! done_run "$W/hf10"; then
    stage "$W/hf10" "$W/smi10/hftf_tr" cfarm_null_2c || { publish "blocked"; exit 1; }
    launch "$W/hf10" 4 hf "$W/tf10"; note "T = 10 Housing First path running"
    PUBMSG="T = 10 Housing First path running" wait_pub "$W/hf10.pid"
fi
note "hf10: $(cat "$W/hf10/EXIT")"
gzip -c "$W/hf10/run.log" > "$OUT/hf10_run.log.gz"
find "$W"/tf10 "$W"/hf10 -name '*.dat' -size +10M -delete 2>/dev/null
python3 "$R/analyse_smi.py" main "$W/tf10/run.log" "$W/hf10/run.log" > "$OUT/tables.md" 2>&1
note "analysis: $(grep -a 'HEADLINE' "$OUT/tables.md" | head -3 | tr '\n' ' ')"
touch "$W/PATHS_DONE"
publish "all runs done, tables written"
