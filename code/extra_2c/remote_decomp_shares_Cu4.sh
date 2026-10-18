#!/bin/bash
# remote_decomp_shares_Cu4.sh -- A COPY of remote_decomp_shares_Cu3.sh (18 October, 14:00). Table 5's eighth column: decomp_2c_shares_Cu3/arm_fixp held pi_V
# at 0.09354 and landed past the jump in drug use (-42 per cent, net revenue 0.42 per cent BELOW the benchmark), further
# from clearing than the column it was to replace (decomp_2c_shares_Cu/arm_fixp: pi_V 0.0924, revenue 0.22 per cent
# above, but the price held at the PRE-correction 1.0001082). Run with SHARES_HOLD_PV=1 SHARES_V0=0.0924: the paper's
# pi_V with the corrected held price 0.99938969. Everything goes to results/decomp_2c_shares_Cu4/arm_<column> (worker
# files code/decomp_shares_Cu4_<column>*). Otherwise remote_decomp_shares_Cu3.sh.
# remote_decomp_shares_Cu3.sh -- A COPY of remote_decomp_shares_Cu2.sh (17 October, 22:20; the author: "I want all the numbers to be corrected"). The held
# columns of Table 5 held the drug price at P_NULL=1.0001082, the PRE-correction Housing First's price
# (counterfactuals_2c/nulltf/null); the corrected Housing First (decomp_2c_shares_Cu/arm_tf/null/final.txt) clears at
# 0.99938969, and the paper says the price is held "at its Housing First level". Here P_NULL is that price, and
# everything goes to results/decomp_2c_shares_Cu3/arm_<column> (worker files code/decomp_shares_Cu3_<column>*), so the
# paper's current files are untouched until the exporters are pointed at the new ones. Otherwise remote_decomp_shares_Cu2.sh.
# remote_decomp_shares_Cu2.sh <tf|fixboth|fixpv|fixp> -- THE CORRECTED COMPARISON (14 October, 05:20). The diagnostic
# (results/decomp_2c_shares_Cu/arm_fixboth, 05:08) showed the 24 per cent of households with a SUD better off under the
# screen alone was an artefact: with patch_treatC2's internal_computations fix ungated, so Housing First runs the same
# arithmetic as Treatment First, none is. This is remote_decomp_shares_C2.sh with Housing First solved on
# cf_fix2_share_treatCu (as remote_decomp_shares_Cu.sh), the budget target set to the corrected Housing First's net
# revenue (NET_TARGET_U, default from the diagnostic's null_final.txt), and the newborn and collect steps run at the end
# (newborn_Cu.sh, collect_shares_Cu.sh). Results to results/decomp_2c_shares_Cu/arm_<column>/.
# SHARES_P0 / SHARES_V0 set the starting drug price and pi_V of the tf column (use the accepted run's).
# remote_decomp_shares_C2.sh's header follows.
# remote_decomp_shares_C2.sh -- remote_decomp_shares_C.sh with the warm start settable (13 October, 18:30; the author:
# "Do the decompositions you suggested"). The drug price moves at most 0.5 per cent a pass (max_drug_price_move, the
# author 8 September), so a run started from the 0.85 run's price (0.86) walks for 8-18 passes before it can clear at
# 0.20. SHARES_P0 sets the starting drug price of the tf and fixpv columns and SHARES_V0 the starting pi_V of the tf
# column; unset, everything is as remote_decomp_shares_C.sh, which is left untouched (running workers execute it).
# remote_decomp_shares_C.sh <tf|fixboth|fixpv|fixp> -- RULE C (12 October; the author: "all the stuff already in the paper
# should be redone for rule C"). remote_decomp_shares.sh with the Treatment First column on the rule-C build
# (cf_fix2_treatC, treat/build_treatC.sh, through treat/cf_arm_C.sh) and one more column, tf: the paper's main arm
# itself, re-solved beside Housing First so that its shares and newborn shares are computed in the same container.
# Warm starts: tf from the rule-C main arm's latest published pass (results/counterfactuals_2c/tf_ruleC/passes.txt), the
# decomposition columns from rule A's converged values. "Against the accepted run" compares with rule A's run.
# Results to results/decomp_2c_shares_C/arm_<column>/. remote_decomp_shares.sh's header follows.
# remote_decomp_shares.sh <fixboth|fixpv|fixp> -- THE BETTER-OFF SHARES FOR ONE DECOMPOSITION COLUMN OF TABLE 5
# (9 October; the author, on 'The last three rows are not computed for the sixth to eighth columns': "why?", then
# "id like you to rerun them and remove that sentence from the notes", "you should compute them on separate sessions
# so you can parallelize"). The three decomposition runs (results/decomp_2c/arm_fixpv, arm_fixp,
# results/decomp_2c_both/arm_fixboth) ran in containers that are gone, and the shares need each run's saved value
# functions and distribution beside the no-policy run's: transition_2c/shares.py compares every state's value under
# the run with its value under Housing First, weighted by Housing First's distribution, and code/cf_kid values every
# newborn by the household it is born into in both. So one worker per column re-solves Housing First (cfarm_null_2c,
# as remote_transition_2c.sh) and the column's arm (cfarm_tf_2c_<arm>, as remote_decomp_2c.sh /
# remote_decomp_2c_both.sh, started from the accepted run's converged price and pi_V), side by side, then:
#   results/decomp_2c_shares/arm_<arm>/shares.txt            (all households, with and without a SUD; tol 1e-3, 1e-2)
#   results/decomp_2c_shares/arm_<arm>/newborn_shares.{txt,json}   (newborns by the household they are born into)
#   results/decomp_2c_shares/arm_<arm>/final.txt              (checked against the accepted run's final.txt)
# code/paper/export_longrun.py reads them into Table 5's last three rows (yellow until they are there).
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/extra_2c/remote_decomp_shares.sh <arm>
# Run it again after a container restart: a finished step is not repeated.
set -u
A=${1:-}
case "$A" in tf|fixboth|fixpv|fixp) ;; *) echo "usage: $0 tf|fixboth|fixpv|fixp"; exit 1 ;; esac
BRANCH=claude/two-period-addiction-hazard-d7gb61
E=$(cd "$(dirname "$0")" && pwd)
C=$(cd "$E/.." && pwd)
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/decomp_2c_shares_Cu4/arm_$A
mkdir -p "$R"
D=$C/decomp_shares_Cu4_$A
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
# 13 Oct: treatment is publicly funded in every arm (patch_treatC.py), so Housing First's net revenue, the target,
# carries its own treatment spending: treat/net_target_with_treatment.py gives 5.8918411 - 0.1332056 * 0.482685 ($9,426 a treated year)
NET_TARGET=5.8275447063
# (14 Oct, 05:20) the corrected Housing First's own net revenue: the gated null cleared at 5.8278 against 5.8275, the
# ungated one sits at 5.8372 (results/decomp_2c_shares_Cu/arm_fixboth/null_final.txt)
NET_TARGET=${NET_TARGET_U:-$(awk '/net government revenue/{print $NF}' "$REPO/results/decomp_2c_shares_Cu/arm_fixboth/null_final.txt")}
# 13 Oct (the author): the detection rate at which 61% of all tested users stop on impact, Mehay and Pacula's stayers
# (results/whostops_2c_C_pts_0p10_0p20: 61.6% at 0.20); RULEC_PDET overrides
PDET_C=${RULEC_PDET:-0.20}
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=0.99938969; V_NULL=0.067533863   # the corrected Housing First's cleared price and pi_V
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
# the column's settings, started from the accepted run's converged values (results/decomp_2c*/arm_*/final.txt)
# the rule-C main arm's latest pass (columns: pass price pi_V ...), else rule A's equilibrium
PC=0.85551291; VC=0.096152024
LASTC=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$REPO/results/counterfactuals_2c/tf_ruleC/passes.txt" 2>/dev/null)
[ -n "$LASTC" ] && { PC=${LASTC% *}; VC=${LASTC#* }; }
[ -n "${SHARES_P0:-}" ] && PC=$SHARES_P0
[ -n "${SHARES_V0:-}" ] && VC=$SHARES_V0
case "$A" in
  tf)      ACC=$REPO/results/counterfactuals_2c/tf85_c35/tf
           SET=(PDET=$PDET_C NET_TARGET=$NET_TARGET PV_START=$VC DRUG_PRICE_START=$PC "EXTRA_SET=cost_per_drug_test $CTEST") ;;
  fixboth) ACC=$REPO/results/decomp_2c_both/arm_fixboth
           SET=(PDET=$PDET_C PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0") ;;
  fixpv)   ACC=$REPO/results/decomp_2c/arm_fixpv
           SET=(PDET=$PDET_C PV_START=$V_NULL DRUG_PRICE_START=${SHARES_P0:-0.8742} "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0")
           # (14 October) the gated run cycled through three passes (drug use -20.7, -20.7, -21.3 percent) at a drug price
           # of 0.9442-0.9446 and never met the drift rule; SHARES_HOLD_PRICE=1 holds the price at SHARES_P0 (the cycle's
           # mean), so the column settles; across the cycle the drug market's gap was 0.8e-3 to 3.7e-3, inside its 5e-3 rule
           [ "${SHARES_HOLD_PRICE:-0}" = 1 ] && SET+=(DRUG_MARKET_ADJUSTER=0) ;;
  fixp)    ACC=$REPO/results/decomp_2c/arm_fixp
           SET=(PDET=$PDET_C NET_TARGET=$NET_TARGET PV_START=${SHARES_V0:-0.11453} DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST")
           # (14 October) NO PI_V BALANCES THIS COLUMN'S BUDGET: in the gated run drug use jumps from -48 to -42 percent as
           # pi_V crosses about 0.0930, and the budget misses by 1 to 2 percent on either side. SHARES_HOLD_PV=1 holds pi_V at
           # SHARES_V0 (the paper: where the budget came closest, 0.0924), reported with its budget gap
           [ "${SHARES_HOLD_PV:-0}" = 1 ] && SET=(PDET=$PDET_C PV_START=$SHARES_V0 DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0") ;;
esac

note() { echo "remote_decomp_shares_Cu4 $A: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${DS_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then echo "attaching to the running worker, pid $(cat "$D.pid")"; else
        ( DS_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/decomp_shares_Cu4_$A.log" 2>&1 < /dev/null & echo $! > "$D.pid" )
        echo "started detached, pid $(cat "$D.pid"); log /tmp/decomp_shares_Cu4_$A.log"
    fi
    while alive "$D.pid"; do sleep 60; done
    echo "finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

publish() (
    {
        echo "# better-off shares for the decomposition column $A (code/extra_2c/remote_decomp_shares.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for d in cfarm_null_2c cfarm_tf_2c_$A; do
            L="$C/$d/cf.log"; [ -f "$L" ] && { echo; echo "== $d"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null | tail -n 6; }
        done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "rule C shares (Cu4, corrected held price, pi_V 0.0924) $A: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null; sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
wait_publishing() { while :; do any=0; for p in "$@"; do alive "$p" && any=1; done; [ $any = 1 ] || break
    for _ in $(seq 1 120); do any=0; for p in "$@"; do alive "$p" && any=1; done; [ $any = 1 ] || break; sleep 10; done
    publish "arms running"; done; }
ok() { O="$C/$1.out"; [ -f "$O" ] && tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "$2" "$O" && ! grep -q "GUARD" "$O"; }

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"; bash "cf_runs/build_$b.sh" > "/tmp/ds_build_$b.log" 2>&1 || { note "GUARD: build $b failed"; publish "failed"; exit 1; }
done
[ -x "$C/cf_fix2_share/hftf_cf_prod" ] || { note "building cf_fix2_share"; bash transition_fix/build_cf_fix2_share.sh > /tmp/ds_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed"; publish "failed"; exit 1; }; }
[ -x "$C/cf_kid/hftf_cf_kid" ] || { note "building cf_kid"; sh cf_kid/build.sh > /tmp/ds_build_kid.log 2>&1 || { note "GUARD: build cf_kid failed: $(tail -3 /tmp/ds_build_kid.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
[ -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ] || { note "building cf_fix2_share_treatCu (Housing First with the internal_computations fix ungated)"; bash treat/build_share_treatCu.sh > /tmp/ds_build_share_treatCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/ds_build_share_treatCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/ds_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/ds_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: no held-price stopping rule"; publish "failed"; exit 1; }
publish "built"

# Housing First first, alone until it has unpacked the shared benchmark, then the column's arm beside it
if ! ok cfarm_null_2c "VOUCHER CHECK PASS"; then
    note "arm null on cf_fix2_share_treatCu (no screen: Housing First, internal_computations fix ungated)"
    ( env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_2c DRUG_PRICE_START=$P_NULL sh treat/cf_arm_Cu.sh null > "$C/cfarm_null_2c.out" 2>&1 ) &
    echo $! > "$D.null.pid"
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.null.pid"; do sleep 10; done
fi
if ! ok cfarm_tf_2c_$A "DIST CHECK PASS"; then
    note "arm $A on cf_fix2_treatC (rule C): ${SET[*]}"
    ( env BUILD=cf_fix2_treatC OMP_NUM_THREADS=2 DIAG_TAG=_2c_$A "${SET[@]}" sh treat/cf_arm_C.sh tf > "$C/cfarm_tf_2c_$A.out" 2>&1 ) &
    echo $! > "$D.arm.pid"
fi
wait_publishing "$D.null.pid" "$D.arm.pid"
ok cfarm_null_2c "VOUCHER CHECK PASS" || { note "GUARD: Housing First failed its checks: $(tail -3 "$C/cfarm_null_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
ok cfarm_tf_2c_$A "DIST CHECK PASS" || { note "GUARD: arm $A failed its checks: $(tail -3 "$C/cfarm_tf_2c_$A.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
[ "$A" = fixp ] && [ "${SHARES_HOLD_PV:-0}" != 1 ] && { grep -a "TARGET CHECK PASS" "$C/cfarm_tf_2c_$A.out" > /dev/null || { note "GUARD: fixp did not clear the budget"; publish "failed"; exit 1; }; }
[ "${SHARES_HOLD_PV:-0}" = 1 ] && note "pi_V held at $SHARES_V0: net revenue $(awk '/net government revenue/{print $4}' "$R/final.txt") against the corrected Housing First's $NET_TARGET"
python3 cf_runs/finalstats.py "cfarm_tf_2c_$A/cf.log" cfarm_null_2c/cf.log > "$R/final.txt" 2>&1
note "against the accepted run: $(python3 - "$R/final.txt" "$ACC/final.txt" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = lv(sys.argv[1]), lv(sys.argv[2])
ks = [k for k in ('drug price', 'pi_V (voucher probability)', 'drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k)]
print('worst relative difference %.1e over %s' % (max(abs(x[k] / y[k] - 1) for k in ks), ', '.join(ks)))
PYEOF
)"
publish "arms done"

# THE SHARES: households state by state, then newborns by the household they are born into
python3 transition_2c/shares.py cfarm_tf_2c_$A cfarm_null_2c counter_arm > "$R/shares.txt" 2>&1 \
    && note "shares: $(grep 'all households' "$R/shares.txt" | head -1 | tr -s ' ')" || note "GUARD: shares.py failed: $(tail -2 "$R/shares.txt" | tr '\n' ' ')"
# the newborn step with the rule-C cf_kid binary, and the files the welfare split reads (the default binary refuses
# rule-C arms: results/decomp_2c_shares_C/arm_fixboth, 22:30)
note "newborns and the welfare-split files (newborn_Cu.sh, collect_shares_Cu.sh)"
bash "$E/newborn_Cu4.sh" "$A" > "$R/newborn_Cu.out" 2>&1 && note "$(grep -m1 'newborns:' "$R/newborn_Cu.out")" || note "GUARD: newborn_Cu.sh: $(tail -2 "$R/newborn_Cu.out" | tr '\n' ' ')"
bash "$E/collect_shares_Cu4.sh" "$A" > "$R/collect_Cu.out" 2>&1 || note "collect_shares_Cu.sh: $(tail -2 "$R/collect_Cu.out" | tr '\n' ' ')"
note "done"
publish "done"
