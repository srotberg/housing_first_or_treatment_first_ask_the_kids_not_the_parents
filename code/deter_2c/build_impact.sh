#!/bin/bash
# build_impact.sh -- <base>_impact: a build (IMPACT_BASE, default cf_fix2; cf_fix2_permban for the permanent ban) with
# fixed_to_benchmark_dis = 1, so a run never moves the
# distribution: it solves the arm's policies at its (held) prices and computes every statistic on the saved
# benchmark distribution (distribution_stationary<i>baseline_benchmark.dat, i.e. Housing First's). The author,
# 8 October: "use the benchmark distribution of HF and then check how many respond to it". Needs cf_fix2 built
# (or generated) first. Production binary only.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
B=${IMPACT_BASE:-cf_fix2}; O=${B}_impact
mkdir -p "$C/$O"
sed 's/^        integer, parameter :: fixed_to_benchmark_dis=0$/        integer, parameter :: fixed_to_benchmark_dis=1/' \
    "$C/$B/cf.f90" > "$C/$O/cf.f90"
d=$(diff "$C/$B/cf.f90" "$C/$O/cf.f90" | grep -c '^[<>]' || true)
[ "$d" -eq 2 ] || { echo "REFUSING: $O expected 2 diff lines, got $d"; exit 1; }
[ -n "$GEN_ONLY" ] && { echo "generated $O/cf.f90"; exit 0; }
( cd "$C/$O" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
    cf.f90 -o hftf_cf_prod 2> build_prod.err )
echo "$O errors=$(grep -c Error "$C/$O/build_prod.err" || true)"
