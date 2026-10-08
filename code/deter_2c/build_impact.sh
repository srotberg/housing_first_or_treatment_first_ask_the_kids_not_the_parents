#!/bin/bash
# build_impact.sh -- cf_fix2_impact: cf_fix2 with fixed_to_benchmark_dis = 1, so a run never moves the
# distribution: it solves the arm's policies at its (held) prices and computes every statistic on the saved
# benchmark distribution (distribution_stationary<i>baseline_benchmark.dat, i.e. Housing First's). The author,
# 8 October: "use the benchmark distribution of HF and then check how many respond to it". Needs cf_fix2 built
# (or generated) first. Production binary only.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$C/cf_fix2_impact"
sed 's/^        integer, parameter :: fixed_to_benchmark_dis=0$/        integer, parameter :: fixed_to_benchmark_dis=1/' \
    "$C/cf_fix2/cf.f90" > "$C/cf_fix2_impact/cf.f90"
d=$(diff "$C/cf_fix2/cf.f90" "$C/cf_fix2_impact/cf.f90" | grep -c '^[<>]' || true)
[ "$d" -eq 2 ] || { echo "REFUSING: cf_fix2_impact expected 2 diff lines, got $d"; exit 1; }
[ -n "$GEN_ONLY" ] && { echo "generated cf_fix2_impact/cf.f90"; exit 0; }
( cd "$C/cf_fix2_impact" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
    cf.f90 -o hftf_cf_prod 2> build_prod.err )
echo "cf_fix2_impact errors=$(grep -c Error "$C/cf_fix2_impact/build_prod.err" || true)"
