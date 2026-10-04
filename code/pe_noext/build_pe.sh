#!/bin/bash
# build_pe.sh -- the two builds of the no-externality experiment (README.md): cf_fix2_share_pe
# (cf_fix2_share plus the print-only PE USED line; Arm A) and cf_fix2_pe (cf_fix2 plus the same
# line and the house-price hold; Arm B). Needs cf_fix2 and cf_fix2_share built first. Production
# binary only. Do NOT build while a solve of the same build is running.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
for pair in "cf_fix2_share cf_fix2_share_pe print 4" "cf_fix2 cf_fix2_pe hold 14"; do
    set -- $pair
    mkdir -p "$C/$2"
    python3 "$C/pe_noext/patch_pe.py" "$C/$1/cf.f90" "$C/$2/cf.f90" "$3"
    d=$(diff "$C/$1/cf.f90" "$C/$2/cf.f90" | grep -c '^[<>]' || true)
    [ "$d" -eq "$4" ] || { echo "REFUSING: $2 expected $4 diff lines, got $d"; exit 1; }
    [ -n "$GEN_ONLY" ] && continue
    ( cd "$C/$2" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium \
        cf.f90 -o hftf_cf_prod 2> build_prod.err )
    echo "$2 errors=$(grep -c Error "$C/$2/build_prod.err" || true)"
done
