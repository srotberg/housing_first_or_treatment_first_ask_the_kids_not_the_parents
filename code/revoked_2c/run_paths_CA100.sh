#!/bin/bash
# run_paths_CA100.sh -- COPY of run_paths_C.sh (16 October) for the Costantini comparison under the CA rule at detection 1.00: Treatment
# First on cf_fix2_treatCA (treat/build_treatCA.sh, rule A's screen on rule C's build) at PDET 1.00, Housing First the
# CORRECTED one (cf_fix2_share_treatCu, internal_computations fix ungated; NET_TARGET 5.8371628), arms
# cfarm_null_2c_CA100 and cfarm_tf_2c_fixboth_CA100, work directories work_CA100, results to results/revoked_2c_CA100
# and results/revoked_2c_street_CA100. Otherwise the original, which follows.
# run_paths_C.sh -- RULE-C COPY of revoked_2c/run_paths.sh (12 October). Binaries from revoked_2c/build_C.sh (work_C),
# the Treatment First end point cfarm_tf_2c_fixboth_CA100 from run_arms_C.sh, results to results/revoked_2c_C; status
# published every 20 minutes, also while the arms run. The arms are compared with rule A's accepted runs for the record
# (the null arm must match; the fixboth arm is expected to differ). Everything else as the original, whose header follows.
# run_paths.sh -- STAGE 2 of the revoked-voucher experiment (README.md): the guard runs at T = 3, then the two
# T = 10 one-pass paths, then the analysis. Waits for run_arms.sh (ARMS_DONE) and build.sh. Detached; re-running it
# attaches. Publishes results/revoked_2c/status.txt about hourly (commit + push of results/revoked_2c and
# code/revoked_2c only).
#
#   tf   start: the no-policy steady state (cfarm_null_2c); end: Treatment First with price and pi_V held
#        (cfarm_tf_2c_fixboth); price and pi_V flat at P_NULL, V_NULL in every year; adjust_taxes 0,
#        drug_market_adjuster 0; loop 0 only. REVK_MODE=tf: tags the revoked, follows them as they are.
#   hf   start and end the no-policy steady state, the same fixed paths: Housing First's own kernel in every year.
#        REVK_MODE=hf: the same tagged households, voucher kept, followed under it.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); REPO=$(cd "$C/.." && pwd)
W=$R/work_CA100; OUT=$REPO/results/revoked_2c_CA100; mkdir -p "$W" "$OUT"; printf "*\n" > "$W/.gitignore"   # work_CA100 is never committed
# 13 Oct: Housing First's net revenue with its own treatment spending (treat/net_target_with_treatment.py)
NET_TARGET=5.8275447063
# 16 Oct: the CORRECTED Housing First's (cf_fix2_share_treatCu)
NET_TARGET=5.8371628
P_NULL=1.0001082; V_NULL=0.067533863
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

note() { echo "run_paths: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/paths.status"; }
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
        echo "# revoked-voucher experiment, RULE CA, DETECTION 1.00 (code/revoked_2c/run_paths_CA100.sh); $(date -u '+%d %b %H:%M UTC')"
        echo "## stage 1, the two steady states"; cat "$W/arms.status" 2>/dev/null
        for a in null_2c_CA100 tf_2c_fixboth_CA100; do
            L="$C/cfarm_$a/cf.log"; [ -f "$L" ] && { echo "-- $a"; python3 "$C/cf_runs/passes.py" "$L" 2>/dev/null | tail -4; }
        done
        echo "## stage 2, the paths"; cat "$W/paths.status" 2>/dev/null
        for d in g_plain3_1t g_track3_1t tf10 hf10 g_hf3_1t g_track3b; do
            L="$W/$d/run.log"; [ -f "$L" ] || continue
            echo "-- $d: $(grep -a -c 'REVK PERIOD DONE' "$L") forward periods done; last line: $(tail -1 "$L" | cut -c1-150)"
        done
        true
    } > "$OUT/status.txt.tmp" && mv "$OUT/status.txt.tmp" "$OUT/status.txt"
    cd "$REPO" || exit 0
    git add "$OUT" "$R" 2>/dev/null
    git commit -q -m "revoked 2c rule CA det 1.00: $1$TRAILER" -- "$OUT" "$R" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
wait_pub() {   # <pid file>... : publish about hourly while any runs
    local last; last=$(date +%s)
    while :; do
        local any=0; for p in "$@"; do alive "$p" && any=1; done
        [ $any = 1 ] || break
        sleep 60
        if [ $(( $(date +%s) - last )) -ge 1200 ]; then publish "${PUBMSG:-running}"; last=$(date +%s); fi
    done
}

# stage <dir> <binary> <terminal arm> : the stage E staging, then the experiment's settings on top
stage() {
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
    note "staged $N (T=$T, terminal $ARM): $(tail -1 "$N.stage.log" | cut -c1-80)"
}
launch() {   # <dir> <threads> <mode> [tagdir]
    ( cd "$1" && date +%s > START_EPOCH && OMP_NUM_THREADS=$2 REVK_MODE=$3 REVK_TAGDIR=${4:-.} ./hftf > run.log 2>&1; echo "exit $?" > EXIT ) &
    echo $! > "$1.pid"
}

: >> "$W/paths.status"
note "waiting for the arms and the builds"
lastpub=$(date +%s)
while [ ! -f "$W/ARMS_DONE" ] || alive "$W/build.pid"; do
    sleep 60
    if [ $(( $(date +%s) - lastpub )) -ge 1200 ]; then publish "arms running"; lastpub=$(date +%s); fi
    alive "$W/arms.pid" || [ -f "$W/ARMS_DONE" ] || { note "GUARD: run_arms_CA100.sh ended without ARMS_DONE: $(tail -2 "$W/arms.status" | tr '\n' ' ')"; publish "blocked"; exit 1; }
done
[ -x "$W/track10/hftf_tr" ] && [ -x "$W/plain3/hftf_tr" ] && [ -x "$W/track3/hftf_tr" ] || { note "GUARD: builds missing: $(tail -3 "$W/build.log" | tr '\n' ' ')"; publish "blocked"; exit 1; }
for a in null_2c_CA100 tf_2c_fixboth_CA100; do
    tail -5 "$C/cfarm_$a.out" | grep -q "DIST CHECK PASS" && ! grep -q GUARD "$C/cfarm_$a.out" || { note "GUARD: arm $a failed: $(tail -3 "$C/cfarm_$a.out" | tr '\n' ' ')"; publish "blocked"; exit 1; }
done
grep -q "VOUCHER CHECK PASS" "$C/cfarm_null_2c_CA100.out" || { note "GUARD: null arm voucher check"; publish "blocked"; exit 1; }
[ -s "$C/cfarm_null_2c_CA100/newborn_parent_share_counter.dat" ] || { note "GUARD: no parent share"; publish "blocked"; exit 1; }
mkdir -p "$OUT/arms"
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_null_2c_CA100/cf.log" > "$OUT/arms/null_final.txt" 2>&1
python3 "$C/cf_runs/finalstats.py" "$C/cfarm_tf_2c_fixboth_CA100/cf.log" "$C/cfarm_null_2c_CA100/cf.log" > "$OUT/arms/fixboth_final.txt" 2>&1
note "against earlier runs (null against the corrected Housing First, must match; fixboth against rule C at 0.20, differs): $(python3 "$R/compare_arms.py" "$OUT/arms/null_final.txt" "$REPO/results/decomp_2c_shares_Cu/arm_fixboth/null_final.txt" "$OUT/arms/fixboth_final.txt" "$REPO/results/revoked_2c_C/arms/fixboth_final.txt" 2>&1 | tr '\n' ' ')"
publish "arms re-solved"

# GUARD RUNS, T = 3, ONE THREAD. The model's forward kernel has a data race (is_addicted_1 is SHARED in the parallel
# loop of converge_to_stationary_equilibrium and every iteration writes 0 then 1 to it), so two runs of the same binary
# on 2 threads differ at about 1e-6 (README). On one thread there is no race and the plain and tracking builds must
# agree bit for bit, and the shadow kernel must reproduce the model's step to rounding.
done_run() { grep -q "REVK STOP" "$1/run.log" 2>/dev/null; }
if ! done_run "$W/g_plain3_1t" || ! done_run "$W/g_track3_1t"; then
    done_run "$W/g_plain3_1t" || { stage "$W/g_plain3_1t" "$W/plain3/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_plain3_1t" 1 off; } || { publish "blocked"; exit 1; }
    done_run "$W/g_track3_1t" || { stage "$W/g_track3_1t" "$W/track3/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_track3_1t" 1 tf; } || { publish "blocked"; exit 1; }
    note "T = 3 guard pair running, one thread each"
    PUBMSG="T = 3 guard pair running (one thread)" wait_pub "$W/g_plain3_1t.pid" "$W/g_track3_1t.pid"
fi
python3 "$R/analyse.py" pair3 "$W/g_plain3_1t/run.log" "$W/g_track3_1t/run.log" "$W/g_plain3_2t/run.log" "$W/g_track3_2t/run.log" > "$OUT/guard_T3_pair.txt" 2>&1
note "T = 3 pair: $(grep -a 'GUARD SUMMARY' "$OUT/guard_T3_pair.txt")"
for d in g_plain3_1t g_track3_1t g_plain3_2t g_track3_2t; do gzip -c "$W/$d/run.log" > "$OUT/${d#g_}_run.log.gz"; done
find "$W"/g_* -name '*.dat' -size +10M -delete 2>/dev/null
grep -q "GUARD SUMMARY: PASS" "$OUT/guard_T3_pair.txt" || { note "GUARD: the T = 3 pair did not pass, stopping before T = 10"; publish "blocked at the T = 3 guards"; exit 1; }
publish "T = 3 pair passed"

# THE TWO T = 10 PATHS, one after the other, 4 threads each
if ! done_run "$W/tf10"; then
    stage "$W/tf10" "$W/track10/hftf_tr" cfarm_tf_2c_fixboth_CA100 || { publish "blocked"; exit 1; }
    launch "$W/tf10" 4 tf; note "T = 10 Treatment First path running"
    PUBMSG="T = 10 Treatment First path running" wait_pub "$W/tf10.pid"
fi
note "tf10: $(cat "$W/tf10/EXIT"); $(grep -a -c 'REVK TAG WRITTEN' "$W/tf10/run.log") tags"
gzip -c "$W/tf10/run.log" > "$OUT/tf10_run.log.gz"; publish "T = 10 Treatment First path done"
if ! done_run "$W/hf10"; then
    stage "$W/hf10" "$W/track10/hftf_tr" cfarm_null_2c_CA100 || { publish "blocked"; exit 1; }
    launch "$W/hf10" 4 hf "$W/tf10"; note "T = 10 Housing First path running"
    PUBMSG="T = 10 Housing First path running" wait_pub "$W/hf10.pid"
fi
note "hf10: $(cat "$W/hf10/EXIT")"
gzip -c "$W/hf10/run.log" > "$OUT/hf10_run.log.gz"
publish "T = 10 Housing First path done"
find "$W"/tf10 "$W"/hf10 -name '*.dat' -size +10M -delete 2>/dev/null
# the Housing First kernel on one thread (tags from the one-thread T = 3 run) and the bounds-checked tracking build
if ! done_run "$W/g_hf3_1t" || ! done_run "$W/g_track3b"; then
    done_run "$W/g_hf3_1t" || { stage "$W/g_hf3_1t" "$W/track3/hftf_tr" cfarm_null_2c_CA100 && launch "$W/g_hf3_1t" 1 hf "$W/g_track3_1t"; } || { publish "blocked"; exit 1; }
    done_run "$W/g_track3b" || { stage "$W/g_track3b" "$W/track3b/hftf_tr" cfarm_tf_2c_fixboth_CA100 && launch "$W/g_track3b" 2 tf; } || { publish "blocked"; exit 1; }
    note "T = 3 Housing First (one thread) and bounds-checked runs"
    PUBMSG="T = 3 hf and bounds runs" wait_pub "$W/g_hf3_1t.pid" "$W/g_track3b.pid"
fi
for d in g_hf3_1t g_track3b; do gzip -c "$W/$d/run.log" > "$OUT/${d#g_}_run.log.gz"; done
python3 "$R/analyse.py" rest3 "$W/g_track3_1t/run.log" "$W/g_hf3_1t/run.log" "$W/g_track3b/run.log" > "$OUT/guard_T3_rest.txt" 2>&1
note "T = 3 hf and bounds: $(grep -a 'GUARD SUMMARY' "$OUT/guard_T3_rest.txt")"
python3 "$R/analyse.py" main "$W/tf10/run.log" "$W/hf10/run.log" > "$OUT/tables.md" 2>&1
note "analysis: $(grep -a 'HEADLINE' "$OUT/tables.md" | head -2 | tr '\n' ' ')"
touch "$W/PATHS_DONE"
publish "all runs done, tables written"
