#!/bin/bash
# pointrun_childsplit.sh -- the benchmark of record re-run on the child-penalty fix (d45b36ea) PLUS
# the child in the drug split (30 September: "the child term has to count in both whether to use
# and how much to use", "and the parent counts it with omega_c"), and then the same economy at
# omega_c = 0, which is omega_c's moment: the rise in drug use when the child's terms are switched
# off with every other parameter held (NSDUH: 18.3 per cent).
#
# Both at the SAME parameters as the benchmark of record
# (results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt: 97 lines, weight_on_child 0.06,
# kappa_x 0.9329, 12 frozen blocks), the SAME seed (scan_seed) and the SAME build rules
# (build_bench_tdm_childsplit.sh: rule 5e-5, at least 70 sweeps a block). The only difference
# between the two runs is weight_on_child in the handover.
#
# ONE AFTER THE OTHER, NOT SIDE BY SIDE: the container has 4 cores and each run uses all four.
# The omega_c = 0 run starts when the benchmark run exits, from its own fresh copy of the seed.
set -e
C=$(cd "$(dirname "$0")" && pwd)
[ -x $C/bench_tdm_childsplit/hftf_bench ] || { echo "GUARD: build first (build_bench_tdm_childsplit.sh)"; exit 1; }
stage() {  # stage <dir> <weight_on_child>
    D=$C/$1; mkdir -p $D && cd $D
    [ -e data ] || ln -s ../../data data
    cp $C/scan_seed/calibration_state.dat $C/scan_seed/calibration_distribution_shape.dat .
    gunzip -c $C/scan_seed/calibration_distribution1.dat.gz > calibration_distribution1.dat
    gunzip -c $C/scan_seed/calibration_distribution2.dat.gz > calibration_distribution2.dat
    [ "$(stat -c%s calibration_distribution1.dat)" = "265496400" ] || { echo "GUARD: distribution 1 wrong size in $1"; exit 1; }
    sed -e "s/^weight_on_child .*/weight_on_child $2/" \
        $C/../results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt > PARAM_HANDOVER.txt
    [ "$(grep -c "^weight_on_child $2\$" PARAM_HANDOVER.txt)" = 1 ] || { echo "GUARD: weight_on_child not $2 in $1"; exit 1; }
    [ "$(wc -l < PARAM_HANDOVER.txt)" = "$(wc -l < $C/../results/reference/hf_omega_c_006_tdm/PARAM_HANDOVER.bench.txt)" ] || { echo "GUARD: handover length changed in $1"; exit 1; }
    cp PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt
    cp $C/bench_tdm_childsplit/hftf_bench ./hftf_bench
    md5sum hftf_bench > BUILD_USED
}
stage pointrun_childsplit 0.06
stage pointrun_childsplit_omega0 0.0
cd $C
(setsid nohup bash -c "cd $C/pointrun_childsplit && date +%s > START_EPOCH && \
    env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null; \
    cd $C/pointrun_childsplit_omega0 && date +%s > START_EPOCH && \
    env OMP_NUM_THREADS=4 ./hftf_bench > bench.log 2> bench.err < /dev/null" > $C/pointrun_childsplit.chain.out 2>&1 &)
sleep 5
echo "launched: pointrun_childsplit (omega_c 0.06), then pointrun_childsplit_omega0 (omega_c 0)"
