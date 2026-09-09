#!/usr/bin/env bash
# Run a VARIANT binary at a given vector, in code/, under the same lock as
# run_one_point.sh.
#
#   bash code/run_variant.sh save <name=value ...>
#   bash code/run_variant.sh cf   <name=value ...>
#
# WHY IT SHARES THE DIRECTORY. The counterfactual reads the benchmark's
# *baseline_benchmark.dat, which the save run writes, so both must run where
# those files are. It shares the lock for the reason run_one_point.sh documents
# at length: PARAM_HANDOVER.txt consumes itself as it is read, so two runs in
# one directory can hand the model the wrong vector with nothing downstream
# able to tell.
#
# WHY IT DOES NOT WRITE A POINT FILE. A counterfactual has no target, so it has
# no gap, and putting it in points/ would let the calibration machinery score
# it. Its log is the record.
set -uo pipefail
cd "$(dirname "$0")"

VARIANT=${1:?"usage: run_variant.sh save|cf name=value ..."}
shift
case "$VARIANT" in save|cf) ;; *) echo "variant must be save or cf" >&2; exit 1 ;; esac

fail() { echo "run_variant: $*" >&2; exit 1; }

python3 make_variant.py "$VARIANT" || fail "the variant would not generate"

SRC="variant_${VARIANT}.f90"
BIN="hftf_${VARIANT}"
SRC_MD5=$(md5sum "$SRC" | cut -d" " -f1)
BUILT=""
[ -f "${BIN}.srcmd5" ] && BUILT=$(cat "${BIN}.srcmd5")

# THE VECTOR. Defaults come from run_one_point.sh so there is ONE list of
# eighty names and not two that drift apart. It is sourced with a guard that
# stops it before it locks, builds or runs anything.
RUN_ONE_POINT_DEFAULTS_ONLY=1
export RUN_ONE_POINT_DEFAULTS_ONLY
declare -A P
eval "$(awk '/^declare -A P=\(/{f=1} f{print} /^\)/{if(f)exit}' run_one_point.sh)"
[ "${#P[@]}" -gt 40 ] || fail "only ${#P[@]} defaults parsed out of run_one_point.sh"

for kv in "$@"; do
    k=${kv%%=*}; v=${kv#*=}
    [ "$k" = "$kv" ] && fail "argument is not name=value: $kv"
    [ -n "${P[$k]+x}" ] || fail "unknown parameter: $k"
    P[$k]=$v
done

if command -v flock >/dev/null 2>&1; then
    exec 9>".run_one_point.lock"
    flock -n 9 || { echo "run_variant: waiting for the checkout lock"; flock 9; }
fi

# THE STAMP CARRIES THE FLAGS, NOT JUST THE SOURCE, and that is not fussiness.
# It used to hold SRC_MD5 alone. Run the standing -ffpe-trap check, then run an
# ordinary solve on unchanged source, and this test says "already built" and
# silently reuses the DEBUG binary: the flat-supply benchmark exited 136 on a
# floating-point trap that has nothing to do with the economics, and a less
# obvious flag difference -- -O1 against -O3 -funroll-loops -- would have
# produced a plausible answer from the wrong build with nothing to notice.
BUILD_TAG="$SRC_MD5 ${HFTF_OPT:--O3 -funroll-loops}"
if [ ! -x "$BIN" ] || [ "$BUILT" != "$BUILD_TAG" ]; then
    echo "run_variant: building $BIN from $SRC_MD5 [${HFTF_OPT:--O3 -funroll-loops}]"
    rm -f "$BIN" "${BIN}.srcmd5"
    gfortran "$SRC" -mcmodel=medium -fopenmp -fimplicit-none ${HFTF_OPT:--O3 -funroll-loops} \
        -ffree-line-length-none -g -fbacktrace -o "$BIN" 2> "build_${VARIANT}.log" \
        || { tail -20 "build_${VARIANT}.log" >&2; fail "the build failed"; }
    printf '%s\n' "$BUILD_TAG" > "${BIN}.srcmd5"
fi

# The state file carries the PREVIOUS run's parameters and adjusters, and the
# handover consumes itself, so a stale one silently re-measures the last run.
rm -f calibration_state.dat calibration_distribution*.dat

# b reaches the model through the sweep grid on the benchmark path and through
# the handover on the counterfactual path, which never reaches the sweep block.
printf '%s\n' "${P[addiction_scalar_1]}" > B_SWEEP_GRID.txt
: > PARAM_HANDOVER.txt
for k in "${!P[@]}"; do
    if [ "$VARIANT" = save ] && [ "$k" = addiction_scalar_1 ]; then continue; fi
    printf '"%s" %s\n' "$k" "${P[$k]}" >> PARAM_HANDOVER.txt
done
WANT=$(wc -l < PARAM_HANDOVER.txt)

LOG="variant_${VARIANT}_$(date -u +%Y%m%dT%H%M%SZ).log"
ulimit -s unlimited
echo "run_variant: $VARIANT on $(nproc) cores, $WANT parameters, log $LOG"
{
    echo "VARIANT $VARIANT"
    echo "SOURCE_MD5 $SRC_MD5"
    echo -n "VECTOR"
    for k in $(echo "${!P[@]}" | tr ' ' '\n' | sort); do printf ' %s=%s' "$k" "${P[$k]}"; done
    echo
} > "$LOG"
START=$(date +%s)
GFORTRAN_UNBUFFERED_ALL=1 "./$BIN" 2>&1 | grep -av "labor supply secant" >> "$LOG"
STATUS=${PIPESTATUS[0]}
MINS=$(( ($(date +%s) - START) / 60 ))

GOT=$(grep -ac "^ HANDOVER " "$LOG" || true)
echo "run_variant: finished in ${MINS} min, exit ${STATUS}, HANDOVER ${GOT} of ${WANT}"
[ "$GOT" = "$WANT" ] || echo "run_variant: HANDOVER MISMATCH -- the model did not take the vector it was given" >&2
echo "run_variant: log is code/${LOG}"
