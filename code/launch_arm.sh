#!/bin/bash
# launch_arm.sh <arm: 1|2|3> <kappa_x> <benchmark run dir> [drug_price_start] [pi_v]
#
# Stages and starts one counterfactual arm. The benchmark run dir supplies the
# baseline_benchmark files every arm reads -- 62 of them -- and must be a run
# that reached "simulation ended", not one that was stopped.
set -e
ARM=$1; KX=$2; BM=$3; P0=${4:-0.8720}; PIV=${5:-}
S=$(cd "$(dirname "$0")" && pwd)
N=$S/arm$ARM; rm -rf $N; mkdir -p $N
cp $S/cf/hftf_cf_prod $N/hftf; chmod +x $N/hftf

# every benchmark file the counterfactual opens for reading
cp $BM/*baseline_benchmark.dat $N/ 2>/dev/null || true
cp $BM/*baseline_benchmark.txt $N/ 2>/dev/null || true
n=$(ls $N/*baseline_benchmark.* 2>/dev/null | wc -l)
echo "copied $n baseline_benchmark files from $BM"
[ "$n" -lt 60 ] && { echo "REFUSING: expected at least 60, got $n"; exit 1; }

# the warm start, so the arm does not solve from a cold distribution
for f in calibration_distribution1.dat calibration_distribution2.dat \
         calibration_distribution_shape.dat newborn_parent_share.dat; do
  cp $BM/$f $N/$f
done

python3 - "$S/n72_params/resume_seed.dat" "$N/PARAM_HANDOVER.txt" "$ARM" "$KX" "$P0" "$PIV" <<'PY'
import sys
src,dst,arm,kx,p0,piv = sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5],sys.argv[6]
common = {
  "penalty_child_addicted":"0.24",      # delta_d, Nilsson, pinned
  "omega_c_is_pinned":"1",
  "freeze_all_but_omega_c":"1",         # nothing is calibrated in an arm
  "frozen_stop_tolerance":"0.0001",
  "frozen_stop_after_blocks":"25",
  "adjust_taxes":"1",                   # without it distance_govt_budget is
                                        # identically zero and pi_v never clears
  "kappa_x":kx,
  # WARM START FOR THE DRUG PRICE. The handover name is drug_price_start, NOT
  # price_of_addictive_good -- that one is reported as "HANDOVER IGNORED,
  # unknown name" and silently leaves the price at 1.0. drug_price_start is
  # gated on is_counterfactual==1, so it exists for exactly this.
  #
  # WHY IT MATTERS: max_drug_price_move caps the price at 0.5 per cent a loop
  # and that cap is load bearing (see its declaration). Starting at 1.0 when
  # the answer is near 0.73 costs about 60 loops of pure walking.
  # MEASURED, not guessed: two CONVERGED points on the gap function,
  #   p=1.00 gap -0.634087   p=0.87 gap +0.012910   slope -7.41
  # put the crossing at 0.8717 (local slope) to 0.8726 (secant). See
  # CALIBRATION_RECIPE.md section 6a for how the sign is recovered -- the log
  # prints |gap| only.
  "drug_price_start":p0,
}
if piv: common["probability_of_voucher_benchmark_used"]=piv
arms = {
 "1": {"weight_on_child":"1.0"},
 "2": {"weight_on_child":"1.0","internalise_homelessness_cost":"1"},
 "3": {"weight_on_child":"0.055",
       "voucher_conditional_on_clean":"1",
       "include_voucher_exclusion":"1",
       "probability_of_detection":"0.70",
       "probability_of_false_positive":"0.0",
       "increased_prob_of_voucher_if_homeless_and_addicted":"0"},
}
over = dict(common); over.update(arms[arm])
out=[];seen=set()
for line in open(src):
    p=line.split()
    if p and p[0] in over: out.append("%s %s\n"%(p[0],over[p[0]])); seen.add(p[0])
    else: out.append(line)
for k,v in over.items():
    if k not in seen: out.append("%s %s\n"%(k,v))
open(dst,"w").writelines(out)
print("  handover for arm %s:" % arm)
for k in sorted(over): print("    %-50s %s" % (k, over[k]))
PY
cd $N && date +%s > START_EPOCH
echo "arm$ARM staged at $N -- start with: cd $N && ./hftf > run.log 2>&1"
