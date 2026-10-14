#!/bin/bash
# finish_tf_C.sh -- the main arm's decomposition worker (remote_decomp_shares_C.sh tf) finishes its job in three steps
# (14 October): the newborn shares (newborn_C.sh tf), the arms' logs and values at 26 (collect_shares_C.sh tf), and the
# homelessness age split the children's paragraph reads (transition_2c/age_split.py on the same two solved arms, which
# rule A took from results/transition_2c/age_split.txt). Results to results/decomp_2c_shares_C/arm_tf/.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/extra_2c/finish_tf_C.sh
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$C/.." && pwd)
R=$REPO/results/decomp_2c_shares_C/arm_tf
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
[ -s "$R/newborn_shares.json" ] || bash "$C/extra_2c/newborn_C.sh" tf
bash "$C/extra_2c/collect_shares_C.sh" tf
if [ ! -s "$R/age_split.txt" ]; then
    ( cd "$C" && python3 transition_2c/age_split.py null=cfarm_null_2c:counter_arm tf=cfarm_tf_2c_tf:counter_arm > "$R/age_split.txt" 2>&1 ) \
        || echo "age_split FAILED: $(tail -2 "$R/age_split.txt" | tr '\n' ' ')"
    echo "age split: $(grep -c 'housing policy (exact)' "$R/age_split.txt") of 2 arms exact"
fi
cd "$REPO" && git add "$R" && git commit -q -m "rule C shares tf: age split (finish_tf_C.sh)$TRAILER" || true
for i in 1 2 3 4; do git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && { echo "finish_tf_C: done and pushed"; exit 0; }; git rebase --abort 2>/dev/null; sleep $((2**i)); done
echo "finish_tf_C: push failed"
