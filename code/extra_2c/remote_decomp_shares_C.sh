#!/bin/bash
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
R=$REPO/results/decomp_2c_shares_C/arm_$A
mkdir -p "$R"
D=$C/decomp_shares_C_$A
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
NET_TARGET=5.8918410999831181
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
# the column's settings, started from the accepted run's converged values (results/decomp_2c*/arm_*/final.txt)
# the rule-C main arm's latest pass (columns: pass price pi_V ...), else rule A's equilibrium
PC=0.85551291; VC=0.096152024
LASTC=$(awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$REPO/results/counterfactuals_2c/tf_ruleC/passes.txt" 2>/dev/null)
[ -n "$LASTC" ] && { PC=${LASTC% *}; VC=${LASTC#* }; }
case "$A" in
  tf)      ACC=$REPO/results/counterfactuals_2c/tf85_c35/tf
           SET=(PDET=0.85 NET_TARGET=$NET_TARGET PV_START=$VC DRUG_PRICE_START=$PC "EXTRA_SET=cost_per_drug_test $CTEST") ;;
  fixboth) ACC=$REPO/results/decomp_2c_both/arm_fixboth
           SET=(PDET=0.85 PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0") ;;
  fixpv)   ACC=$REPO/results/decomp_2c/arm_fixpv
           SET=(PDET=0.85 PV_START=$V_NULL DRUG_PRICE_START=0.8742 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0") ;;
  fixp)    ACC=$REPO/results/decomp_2c/arm_fixp
           SET=(PDET=0.85 NET_TARGET=$NET_TARGET PV_START=0.11453 DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST") ;;
esac

note() { echo "remote_decomp_shares_C $A: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${DS_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then echo "attaching to the running worker, pid $(cat "$D.pid")"; else
        ( DS_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/decomp_shares_C_$A.log" 2>&1 < /dev/null & echo $! > "$D.pid" )
        echo "started detached, pid $(cat "$D.pid"); log /tmp/decomp_shares_C_$A.log"
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
    git commit -q -m "rule C shares $A: $1$TRAILER" || return 0
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
[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/ds_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/ds_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: no held-price stopping rule"; publish "failed"; exit 1; }
publish "built"

# Housing First first, alone until it has unpacked the shared benchmark, then the column's arm beside it
if ! ok cfarm_null_2c "VOUCHER CHECK PASS"; then
    note "arm null on cf_fix2_share"
    ( env BUILD=cf_fix2_share OMP_NUM_THREADS=2 DIAG_TAG=_2c DRUG_PRICE_START=$P_NULL sh transition_2c/cf_arm_tr2c.sh null > "$C/cfarm_null_2c.out" 2>&1 ) &
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
[ "$A" = fixp ] && { grep -a "TARGET CHECK PASS" "$C/cfarm_tf_2c_$A.out" > /dev/null || { note "GUARD: fixp did not clear the budget"; publish "failed"; exit 1; }; }
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
mkdir -p "$D.newborn"
for a in null_2c tf_2c_$A; do
    [ -s "$D.newborn/$a/child_value_at_birth_partscounter_arm.dat" ] && continue
    THREADS=4 sh cf_kid/run_child_value.sh "$C/cfarm_$a" "$D.newborn/$a" > "$R/cf_kid_$a.out" 2>&1 || note "cf_kid on $a FAILED: $(tail -2 "$R/cf_kid_$a.out" | tr '\n' ' ')"
done
python3 cf_kid/share_newborns.py --tf "$D.newborn/tf_2c_$A" --hf "$D.newborn/null_2c" --json "$R/newborn_shares.json" > "$R/newborn_shares.txt" 2>&1 \
    && note "newborns: $(grep -i -m1 'better' "$R/newborn_shares.txt" | tr -s ' ')" || note "GUARD: share_newborns failed: $(tail -2 "$R/newborn_shares.txt" | tr '\n' ' ')"
note "done"
publish "done"
