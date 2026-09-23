#!/bin/sh
# Cold-restart the b_smi calibration in place.
#
# WHY THIS EXISTS: a resume pairs the warm distribution with a cold value
# function and lands in a different economy -- all experimenters, zero
# addiction, the SMI cell empty and the b_smi channel held. See
# results/oneclass_bsmi/RESUME_DIVERGENCE.md. Until a value function is
# checkpointed, a cold start is the ONLY sound way back, and it is cheap:
# attempt 1 reached its first moment block in about five and a half minutes.
#
# It is the STATE and the DISTRIBUTION that must go. Leaving either one behind
# is what makes the binary resume instead of starting cold.
set -e
cd "$(dirname "$0")"

if pidof hftf >/dev/null 2>&1; then
    echo "REFUSING: hftf is running. Kill it by numeric pid first."; exit 1
fi

STAMP=$(date -u '+%Y%m%dT%H%M%SZ')
mkdir -p void_$STAMP
for f in calibration_state.dat calibration_distribution1.dat \
         calibration_distribution2.dat calibration_distribution_shape.dat \
         resume_seed.dat newborn_parent_share.dat; do
    [ -f "$f" ] && mv "$f" void_$STAMP/ || true
done
[ -f run.log ] && mv run.log void_$STAMP/ || true
[ -f run.err ] && mv run.err void_$STAMP/ || true

# The handover is CONSUMED by the binary as it is read, which is why the .kept
# copy exists. Restoring it is correct for a COLD start and wrong for a resume.
cp PARAM_HANDOVER.kept.txt PARAM_HANDOVER.txt

echo "cold: moved the state and distribution to void_$STAMP/, handover restored"
echo "launch with:  setsid nohup ./hftf > run.log 2> run.err < /dev/null &"
