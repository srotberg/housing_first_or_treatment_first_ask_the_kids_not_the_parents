#!/bin/bash
# launch_arm.sh <arm: 1|2|3> <kappa_x> <benchmark run dir> [drug_price_start] [pi_v]
#
# Stages and starts one counterfactual arm. The benchmark run dir supplies the
# baseline_benchmark files every arm reads -- 62 of them -- and must be a run
# that reached "simulation ended", not one that was stopped.
set -e
ARM=$1; KX=$2; BM=$3; P0=${4:-0.8720}; PIV=${5:-}
S=$(cd "$(dirname "$0")" && pwd)

# The binary: $HFTF if set, else the conventional spot beside this script.
# build_cf.sh puts it wherever you told it to, so from a fresh checkout set
# HFTF rather than moving files around.
BIN=${HFTF:-$S/cf/hftf_cf_prod}
[ -x "$BIN" ] || { echo "REFUSING: no counterfactual binary at $BIN."; \
                   echo "  build one with  bash code/build_cf.sh <dir>  and set HFTF=<dir>/hftf_cf_prod"; exit 1; }

# The resume seed: beside this script if a working copy is around, otherwise
# the one committed with the benchmark.
SEED=$S/n72_params/resume_seed.dat
[ -f "$SEED" ] || SEED=$BM/resume_seed.dat
[ -f "$SEED" ] || { echo "REFUSING: no resume_seed.dat in $S/n72_params or $BM"; exit 1; }

N=$S/arm$ARM; rm -rf $N; mkdir -p $N
cp "$BIN" $N/hftf; chmod +x $N/hftf
echo "binary $BIN"
echo "seed   $SEED"

# every benchmark file the counterfactual opens for reading
cp $BM/*baseline_benchmark.dat $N/ 2>/dev/null || true
cp $BM/*baseline_benchmark.txt $N/ 2>/dev/null || true
n=$(ls $N/*baseline_benchmark.* 2>/dev/null | wc -l)
echo "copied $n baseline_benchmark files from $BM"
[ "$n" -lt 60 ] && { echo "REFUSING: expected at least 60, got $n"; exit 1; }

# the warm start, so the arm does not solve from a cold distribution
# Optional. Absent, the arm solves block 1 from a cold distribution as well as
# a cold value function -- slower by a few blocks, identical answer. The
# committed benchmark carries the two small ones only; the 265 MB distribution
# is not in git.
for f in calibration_distribution1.dat calibration_distribution2.dat \
         calibration_distribution_shape.dat newborn_parent_share.dat; do
  [ -f "$BM/$f" ] && cp $BM/$f $N/$f
done
true

python3 - "$SEED" "$N/PARAM_HANDOVER.txt" "$ARM" "$KX" "$P0" "$PIV" <<'PY'
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
# THE TWO CSVs THE MODEL OPENS AS "../data/<f>.csv".
#
# Relative to the ARM DIRECTORY, so $N/../data, i.e. $S/data. In the scratchpad
# this happened to exist and the dependency was invisible; run from the repo,
# $S is code/ and code/data/ does not exist, so the arm dies -- and it dies
# AFTER the binary has read and DELETED PARAM_HANDOVER.txt, so the seed is gone
# and a naive restart silently runs the Fortran's declared values (b ~ 0.95,
# lambda_d = 0) while looking perfectly healthy. Found by the arm 1 worker.
REPO_DATA=$(cd "$S/.." && pwd)/data
mkdir -p "$S/data"
for f in us_mortality_multipliers.csv us_mh_onset_shape.csv; do
  if [ ! -f "$S/data/$f" ]; then
    if [ -f "$REPO_DATA/$f" ]; then cp "$REPO_DATA/$f" "$S/data/$f"
    else echo "REFUSING: $f not found in $REPO_DATA and not already in $S/data"; exit 1; fi
  fi
done
echo "data   $S/data (us_mortality_multipliers.csv, us_mh_onset_shape.csv)"

# THE FOUR LARGE BENCHMARK FILES. An arm reads these every loop in
# frac_of_households_in_support_of_policy (cf 23895/23898, called
# unconditionally at 51689). They are 596 MB and are NOT in git, so check for
# them HERE rather than letting the run die at the end of block 1 with the
# handover already eaten.
missing=""
for f in value_function1 value_function2 distribution_stationary1 distribution_stationary2; do
  [ -f "$N/${f}baseline_benchmark.dat" ] || missing="$missing ${f}baseline_benchmark.dat"
done
if [ -n "$missing" ]; then
  echo "REFUSING: the benchmark directory is missing files an arm reads every loop:"
  for f in $missing; do echo "    $f"; done
  echo "  These are 596 MB and are not in git. Point BM at a directory holding a"
  echo "  converged benchmark's FULL output. See code/results/n90_benchmark/README.md."
  exit 1
fi

cd $N && date +%s > START_EPOCH
echo "arm$ARM staged at $N -- start with: cd $N && ./hftf > run.log 2>&1"
