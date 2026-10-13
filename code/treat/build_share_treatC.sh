#!/bin/bash
# build_share_treatC.sh [share|share_pe|both] -- the Housing First (no-policy) arms' builds with the rule-C patch:
#   cf_fix2_share_treatC    = cf_fix2_share    (transition_fix/build_cf_fix2_share.sh) + treat/patch_treatC.py
#   cf_fix2_share_pe_treatC = cf_fix2_share_pe (pe_noext/build_pe.sh)                  + treat/patch_treatC.py
# WHY (the author, 13 Oct: "Count those in treatment with 0 drug use as non users"): the patch counts a household with the
# disorder that is in treatment and spends nothing as a non-user in EVERY arm, so the Housing First arms the experiments are
# compared with must run on a patched build too. With no screen the patch changes no choice (the one-thread inert check of
# 12 Oct, results/counterfactuals_2c/tf_ruleC2_test: bit for bit), only the drug-use statistic and the ABSTAIN print.
set -e
C=$(cd "$(dirname "$0")/.." && pwd); cd "$C"
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
WHICH=${1:-both}
build() {   # $1 base dir, $2 out dir
    mkdir -p "$2"
    python3 treat/patch_treatC.py "$1/cf.f90" "$2/cf.f90"
    grep -q "RULE C (patch_treatC.py)" "$2/cf.f90" || { echo "REFUSING: rule C did not land in $2"; exit 1; }
    ( cd "$2" && gfortran -O3 -funroll-loops $COMMON cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ "$(grep -c Error "$2/build_prod.err")" = 0 ] && [ -x "$2/hftf_cf_prod" ] || { echo "REFUSING: $2 did not compile"; grep -m3 Error "$2/build_prod.err"; exit 1; }
    echo "built $2/hftf_cf_prod"
}
if [ "$WHICH" = share ] || [ "$WHICH" = both ]; then
    [ -f cf_fix2_share/cf.f90 ] || bash transition_fix/build_cf_fix2_share.sh
    build cf_fix2_share cf_fix2_share_treatC
fi
if [ "$WHICH" = share_pe ] || [ "$WHICH" = both ]; then
    [ -f cf_fix2_share_pe/cf.f90 ] || bash pe_noext/build_pe.sh
    build cf_fix2_share_pe cf_fix2_share_pe_treatC
fi
