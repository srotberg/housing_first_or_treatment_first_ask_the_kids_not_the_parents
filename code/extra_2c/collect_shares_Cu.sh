#!/bin/bash
# collect_shares_Cu.sh: collect_shares_C.sh for the corrected comparison (14 October, 05:20): results/decomp_2c_shares_Cu, run by
# remote_decomp_shares_Cu2.sh in its own container. collect_shares_C.sh's header follows.
# collect_shares_C.sh <tf|fixboth|fixpv|fixp> -- run AFTER remote_decomp_shares_C.sh <arm> has finished, in the same
# container. That script keeps final.txt, the shares and the newborn shares, but not the two files the welfare split
# (code/paper/export_welfare.py, welfare_nok.parts) reads for each arm: the arm's cf.log.gz and its value at 26 by entry
# node (welfare_by_employment_youngestcounter_arm.txt, kept as value_at_26_by_node.txt). This copies them, for the arm
# and for its Housing First re-solve, into results/decomp_2c_shares_C/arm_<arm>/{tf,null}/ and pushes.
set -u
A=${1:?arm}
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$C/.." && pwd)
R=$REPO/results/decomp_2c_shares_Cu/arm_$A
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
for pair in "tf cfarm_tf_2c_$A" "null cfarm_null_2c"; do
    set -- $pair; out=$R/$1; d=$C/$2; mkdir -p "$out"
    [ -f "$d/cf.log" ] && gzip -c "$d/cf.log" > "$out/cf.log.gz" || echo "MISSING $d/cf.log"
    [ -f "$d/welfare_by_employment_youngestcounter_arm.txt" ] && cp "$d/welfare_by_employment_youngestcounter_arm.txt" "$out/value_at_26_by_node.txt" || echo "MISSING $d/welfare_by_employment_youngestcounter_arm.txt"
    [ -f "$d/PARAM_HANDOVER.arm.txt" ] && cp "$d/PARAM_HANDOVER.arm.txt" "$out/"
    python3 "$C/cf_runs/finalstats.py" "$d/cf.log" > "$out/final.txt" 2>&1 || true
    grep -a "MILBY SPLIT" "$d/cf.log" 2>/dev/null | tail -1 > "$out/milby_split.txt"
done
cd "$REPO" && git add "$R" && git commit -q -m "rule C shares (corrected Housing First) $A: the arms' logs and values at 26 by node (collect_shares_C.sh)$TRAILER" || true
for i in 1 2 3 4; do git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && { echo "collected and pushed"; exit 0; }; git rebase --abort 2>/dev/null; sleep $((2**i)); done
echo "push failed"
