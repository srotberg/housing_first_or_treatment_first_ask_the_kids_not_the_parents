#!/bin/bash
# newborn_Cu4.sh -- A COPY of newborn_Cu3.sh (18 October, 14:00). Table 5's eighth column: decomp_2c_shares_Cu3/arm_fixp held pi_V
# at 0.09354 and landed past the jump in drug use (-42 per cent, net revenue 0.42 per cent BELOW the benchmark), further
# from clearing than the column it was to replace (decomp_2c_shares_Cu/arm_fixp: pi_V 0.0924, revenue 0.22 per cent
# above, but the price held at the PRE-correction 1.0001082). Run with SHARES_HOLD_PV=1 SHARES_V0=0.0924: the paper's
# pi_V with the corrected held price 0.99938969. Everything goes to results/decomp_2c_shares_Cu4/arm_<column> (worker
# files code/decomp_shares_Cu4_<column>*). Otherwise newborn_Cu3.sh.
# newborn_Cu3.sh -- A COPY of newborn_Cu.sh (17 October, 22:20; the author: "I want all the numbers to be corrected"). The held
# columns of Table 5 held the drug price at P_NULL=1.0001082, the PRE-correction Housing First's price
# (counterfactuals_2c/nulltf/null); the corrected Housing First (decomp_2c_shares_Cu/arm_tf/null/final.txt) clears at
# 0.99938969, and the paper says the price is held "at its Housing First level". Here P_NULL is that price, and
# everything goes to results/decomp_2c_shares_Cu3/arm_<column> (worker files code/decomp_shares_Cu3_<column>*), so the
# paper's current files are untouched until the exporters are pointed at the new ones. Otherwise newborn_Cu.sh.
# newborn_Cu.sh: newborn_C.sh for the corrected comparison (14 October, 05:20): results/decomp_2c_shares_Cu, run by
# remote_decomp_shares_Cu2.sh in its own container. newborn_C.sh's header follows.
# newborn_C.sh <tf|fixboth|fixpv|fixp> -- the newborn shares of a rule-C decomposition column, run AFTER
# remote_decomp_shares_C.sh (or _C2.sh) <arm> has finished, in the same container (13 October). That script's newborn
# step called cf_kid/run_child_value.sh with the default cf_kid binary, whose build guard refuses arms solved on the
# rule-C builds (cf_fix2_treatC, cf_fix2_share_treatC), so both arms' newborn values failed and newborn_shares.txt holds
# a FileNotFoundError (results/decomp_2c_shares_C/arm_fixboth, 22:30). Here both arms are valued with cf_kid/build_C.sh's
# binary, which mirrors rule C's law of motion (the household's own treatment choice at the screen call), as
# transition_fix/remote_tr70_C.sh does for the rule-C terminal arm; the Housing First re-solve runs the same rule-C code
# with voucher_conditional_on_clean = 0, so the same binary values it under Housing First's law. FORCE_BUILD=1 is that
# check, made here. Writes results/decomp_2c_shares_C/arm_<arm>/newborn_shares.{txt,json} and pushes.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/extra_2c/newborn_C.sh <arm>
set -u
A=${1:?arm}
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$C/.." && pwd)
R=$REPO/results/decomp_2c_shares_Cu4/arm_$A; D=$C/decomp_shares_Cu4_$A
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
cd "$C"
for a in null_2c tf_2c_$A; do
    [ -f "$C/cfarm_$a/cf.log" ] || { echo "GUARD: $C/cfarm_$a is gone (the container was reset?): rerun the column"; exit 1; }
done
[ -x "$C/cf_kid_C/hftf_cf_kid" ] || { echo "building cf_kid_C"; bash cf_kid/build_C.sh "$C/cf_kid_C" > /tmp/newborn_C_build.log 2>&1 || { echo "GUARD: cf_kid/build_C.sh failed: $(tail -3 /tmp/newborn_C_build.log)"; exit 1; }; }
mkdir -p "$D.newborn"
for a in null_2c tf_2c_$A; do
    [ -s "$D.newborn/$a/child_value_at_birth_partscounter_arm.dat" ] && continue
    rm -rf "$D.newborn/$a"
    echo "cf_kid_C on $a ($(date -u +%H:%M))"
    BIN=$C/cf_kid_C/hftf_cf_kid FORCE_BUILD=1 THREADS=4 sh cf_kid/run_child_value.sh "$C/cfarm_$a" "$D.newborn/$a" > "$R/cf_kid_$a.out" 2>&1 \
        || { echo "GUARD: cf_kid_C on $a failed: $(tail -3 "$R/cf_kid_$a.out")"; exit 1; }
done
python3 cf_kid/share_newborns.py --tf "$D.newborn/tf_2c_$A" --hf "$D.newborn/null_2c" --json "$R/newborn_shares.json" > "$R/newborn_shares.txt" 2>&1 \
    || { echo "GUARD: share_newborns failed: $(tail -3 "$R/newborn_shares.txt")"; exit 1; }
echo "newborns: $(grep -i -m1 'better' "$R/newborn_shares.txt" | tr -s ' ')"
cd "$REPO" && git add "$R" && git commit -q -m "rule C shares (corrected Housing First) $A: newborn shares with the rule-C cf_kid binary (newborn_C.sh)$TRAILER" || true
for i in 1 2 3 4; do git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && { echo "newborn_C: done and pushed"; exit 0; }; git rebase --abort 2>/dev/null; sleep $((2**i)); done
echo "newborn_C: push failed"
