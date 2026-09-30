#!/bin/bash
# pointrun_childfix.sh -- the benchmark of record re-run on the child-penalty fix (d45b36ea),
# at the SAME parameters: results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt (97
# lines, weight_on_child 0.06, kappa_x 0.9329, 12 frozen blocks), the SAME seed (scan_seed)
# and the SAME build (build_bench_tdm_childfix.sh: rule 5e-5, at least 70 sweeps a block).
# The author, 30 September: "see if the model calibrates very similarly to what it was
# before". Compare its moments with results/reference/hf_omega_c_006_tdm/bench.log.gz.
set -e
C=$(cd "$(dirname "$0")" && pwd)
D=$C/pointrun_childfix
[ -x $C/bench_tdm_childfix/hftf_bench ] || { echo "GUARD: build first (build_bench_tdm_childfix.sh)"; exit 1; }
mkdir -p $D && cd $D
[ -e data ] || ln -s ../../data data
cp $C/scan_seed/calibration_state.dat $C/scan_seed/calibration_distribution_shape.dat .
gunzip -c $C/scan_seed/calibration_distribution1.dat.gz > calibration_distribution1.dat
gunzip -c $C/scan_seed/calibration_distribution2.dat.gz > calibration_distribution2.dat
[ "$(stat -c%s calibration_distribution1.dat)" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
cp $C/../results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt PARAM_HANDOVER.txt
cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
cp $C/bench_tdm_childfix/hftf_bench ./hftf_bench
md5sum hftf_bench > BUILD_USED
date +%s > START_EPOCH
(setsid nohup env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null &)
sleep 5; pgrep -f "pointrun_childfix" >/dev/null || true
echo "launched in $D"
