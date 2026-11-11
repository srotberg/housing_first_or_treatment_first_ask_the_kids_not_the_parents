#!/bin/bash
# remote_universal.sh -- TREATMENT FIRST AGAINST HOUSING FIRST WITH UNIVERSAL VOUCHERS (11 November; the author: "you can
# do the universal one and put in a footnote, sure"). The previous draft's third experiment, which this version dropped
# (the AE's comment and Referee 2's on the optimal programme), as a robustness check of the main result.
#
# Both arms set probability_of_voucher_benchmark_used = 1: every household eligible on income draws a voucher. At its
# ceiling pi_V cannot clear the budget, so neither arm balances it (adjust_taxes 0), as in Table 5's 'Price clears'
# column, where pi_V is held at Housing First's value; the drug price clears in both. The arms are the paper's:
#   Housing First on the corrected build (cf_fix2_share_treatCu, treat/cf_arm_Cu.sh null);
#   Treatment First on the rule-C build (cf_fix2_treatC, treat/cf_arm_C.sh tf), detection 0.20 and the $35 test, as
#   extra_2c/remote_decomp_shares_Cu2.sh sets the main arm.
# Every other parameter is the benchmark's. The welfare gain is CEV(tf) - CEV(null), each the arm's cf.log 'CEV from the
# saved benchmark curve' line, as in deltad/remote_deltad_Cu.sh. Both arms fail cf_arm's voucher check BY DESIGN (they
# run at 1, not the benchmark's 0.0675); the check here asks instead that each printed probability_of_voucher= 1 and
# that its distribution converged (DIST CHECK PASS).
#
# Results: results/universal_C/{null,tf}/ (cf.log.gz, run.out, PARAM_HANDOVER.txt) and results/universal_C/summary.txt,
# pushed to the branch. START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:
#     bash code/universal/remote_universal.sh
# and run the same command again whenever the call stops: it attaches to the running work.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
R=$REPO/results/universal_C
mkdir -p "$R"
D=$C/universal_run
REF=$REPO/results/reference/hf_2c_omega_0.085
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082
P_TF0=${UNIV_P0:-0.95}
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat

note() { echo "remote_universal: $* ($(date -u '+%d %b %H:%M UTC'))" | tee -a "$D.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
if [ "${UNIV_DETACHED:-0}" != 1 ]; then
    if alive "$D.pid"; then echo "attaching to the running worker, pid $(cat "$D.pid")"; else
        ( UNIV_DETACHED=1 setsid nohup bash "$0" "$@" > "$D.log" 2>&1 < /dev/null & echo $! > "$D.pid" )
        echo "started detached, pid $(cat "$D.pid"); log $D.log"
    fi
    while alive "$D.pid"; do sleep 60; done
    echo "finished"; cat "$D.status" 2>/dev/null; cat "$R/summary.txt" 2>/dev/null
    exit 0
fi

publish() (
    cp "$D.status" "$R/status.txt" 2>/dev/null
    cd "$REPO" || exit 0
    git add "$R" 2>/dev/null
    git commit -q -m "universal vouchers: $1$TRAILER" || exit 0
    for i in 1 2 3 4 5 6; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && exit 0
        git rebase --abort 2>/dev/null; sleep $((2 ** i))
    done
    note "push failed: $1"
)

: > "$D.status"
command -v gfortran >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"; bash "cf_runs/build_$b.sh" > "/tmp/univ_build_$b.log" 2>&1 || { note "GUARD: build $b failed"; publish "failed"; exit 1; }
done
[ -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ] || { note "building cf_fix2_share_treatCu"; bash treat/build_share_treatCu.sh > /tmp/univ_build_shareCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/univ_build_shareCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
[ -x "$C/cf_fix2_treatC/hftf_cf_prod" ] || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/univ_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/univ_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
[ -x "$C/cf/hftf_cf_prod" ] || sh build_cf.sh "$C/cf" > /tmp/univ_build_cf.log 2>&1
if [ ! -f cfarm_bench/BENCH_DONE ]; then
    note "stage 1: the benchmark"
    env BUILD=cf_fix2_share_treatCu STAGE1_ONLY=1 sh treat/cf_arm_Cu.sh null > "$C/universal_stage1.out" 2>&1 \
        || { note "GUARD: stage 1 failed: $(tail -2 "$C/universal_stage1.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
publish "built"

ok() { [ -s "$C/$1/cf.log" ] && grep -q "DIST CHECK PASS" "$C/$1.out" \
       && awk '/^ *probability_of_voucher=/{v=$2} END{exit !(v+0 > 0.999999)}' "$C/$1/cf.log"; }
if ! ok cfarm_null_univ; then
    note "Housing First with universal vouchers (cf_fix2_share_treatCu, pi_V 1, the price clearing)"
    ( env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_univ DRUG_PRICE_START=$P_NULL PV_START=1 \
        sh treat/cf_arm_Cu.sh null > "$C/cfarm_null_univ.out" 2>&1 ) &
    echo $! > "$D.null.pid"
    sleep 90
fi
if ! ok cfarm_tf_univ; then
    note "Treatment First with universal vouchers (cf_fix2_treatC, detection 0.20, \$35 test, pi_V held at 1, the price clearing from $P_TF0)"
    ( env BUILD=cf_fix2_treatC OMP_NUM_THREADS=2 DIAG_TAG=_univ PDET=0.20 PV_START=1 DRUG_PRICE_START=$P_TF0 \
        "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0" sh treat/cf_arm_C.sh tf > "$C/cfarm_tf_univ.out" 2>&1 ) &
    echo $! > "$D.tf.pid"
fi
while alive "$D.null.pid" || alive "$D.tf.pid"; do
    for _ in $(seq 1 120); do { alive "$D.null.pid" || alive "$D.tf.pid"; } || break; sleep 10; done
    for a in null tf; do L="$C/cfarm_${a}_univ/cf.log"; [ -f "$L" ] && note "$a: $(grep -a -c 'expected_child_value=' "$L") passes, last price $(grep -a 'price_of_addictive_good=' "$L" | tail -1 | awk '{print $NF}')"; done
    publish "running"
done

for a in null tf; do
    mkdir -p "$R/$a"
    [ -s "$C/cfarm_${a}_univ/cf.log" ] && gzip -c "$C/cfarm_${a}_univ/cf.log" > "$R/$a/cf.log.gz"
    cp "$C/cfarm_${a}_univ.out" "$R/$a/run.out" 2>/dev/null
    cp "$C/cfarm_${a}_univ/PARAM_HANDOVER.txt" "$R/$a/" 2>/dev/null
done
ok cfarm_null_univ || { note "GUARD: Housing First did not converge at pi_V 1: $(tail -3 "$C/cfarm_null_univ.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
ok cfarm_tf_univ || { note "GUARD: Treatment First did not converge at pi_V 1: $(tail -3 "$C/cfarm_tf_univ.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
python3 - "$C/cfarm_null_univ/cf.log" "$C/cfarm_tf_univ/cf.log" > "$R/summary.txt" <<'PYEOF'
import re, sys
def rd(p):
    L = open(p, errors='replace').read()
    g = lambda pat: float(re.findall(pat, L)[-1])
    return {'cev': g(r'CEV from the saved benchmark curve.*?x=\s*([-+0-9.Ee]+)'),
            'use': g(r'MOMENT b\s+total drug users\s+model=\s*(\S+)'),
            'sud': g(r'(?:MOMENT|UNTARGETED)\s+lambda_d disorder rate\s+model=\s*(\S+)') if re.search(r'lambda_d disorder rate', L) else float('nan'),
            'hl': g(r'MOMENT h_1\s+homelessness rate\s+model=\s*(\S+)'),
            'price': g(r'price_of_addictive_good=\s*(\S+)'),
            'pv': g(r'probability_of_voucher=\s*(\S+)')}
n, t = rd(sys.argv[1]), rd(sys.argv[2])
print('universal vouchers (pi_V = 1 in both arms, the drug price clearing, the budget not balanced)')
for k in ('use', 'sud', 'hl', 'price', 'pv'):
    print(f'  {k:6s} Housing First {n[k]:.6f}  Treatment First {t[k]:.6f}  change {100*(t[k]/n[k]-1):+.2f} percent')
print(f'  CEV of a newborn, Treatment First against Housing First: {100*(t["cev"]-n["cev"]):+.3f} percent of lifetime consumption')
print(f'    (each against the benchmark curve: Housing First {100*n["cev"]:+.3f}, Treatment First {100*t["cev"]:+.3f})')
PYEOF
note "done: $(tail -2 "$R/summary.txt" | head -1)"
publish "done"
