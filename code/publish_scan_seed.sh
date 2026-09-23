#!/bin/sh
# Package the CONVERGED omega_c = 0 benchmark into code/scan_seed/ so that a
# session of its own can run one scan point without this machine.
#
# WHY THIS IS POSSIBLE AT ALL. The stationary distribution is 253 MB, which
# cannot go in the repository. It is F30.28 TEXT and mostly zeros, so it gzips
# 20x to 12.6 MB; the second file gzips 412x, 24 MB to 58 KB. Together with the
# 5 KB state file that is the whole converged benchmark in under 13 MB.
#
# WITHOUT THE WARM START a scan point would cold-solve and need ten blocks or
# more. With it, the frozen runs this morning took THREE blocks (oc00) and TWO
# (oc055).
set -e
cd "$(dirname "$0")"
SRC=${1:-oc2c0}
[ -f "$SRC/calibration_state.dat" ] || { echo "GUARD: $SRC has no state file"; exit 1; }
head -1 "$SRC/calibration_state.dat" | grep -qx 'calibration_state_v3' || { echo "GUARD: state is not v3"; exit 1; }
[ "$(stat -c%s "$SRC/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 is not the two-class size"; exit 1; }
[ "$(tr -d ' ' < "$SRC/calibration_distribution_shape.dat")" = "8564400" ] || { echo "GUARD: shape stamp is not two-class"; exit 1; }

# REFUSE WHILE THE SOURCE RUN IS STILL SOLVING. The author's instruction is to
# let the benchmark run to its own end and take that, so a seed taken from a
# live run is a mid-transient point wearing a converged label. A first version
# of this script happily published b at +28.2 per cent, which was block 3 of a
# transient that the one-class analogue carried to -8.3.
if ls -l /proc/*/cwd 2>/dev/null | grep -q "/$SRC\$"; then
    echo "GUARD: $SRC is STILL RUNNING. Let it reach its own stop (block_move"
    echo "       below frozen_stop_tolerance) and publish the point it ends on."
    exit 1
fi

# REFUSE TO PUBLISH A COLLAPSED OR DEGENERATE POINT. lambda_d at zero is the
# onset-base collapse; b above 0.5 is the degenerate corner.
last=$(grep -a "BLOCK MOVE" "$SRC/run.log" | tail -1)
[ -n "$last" ] || { echo "GUARD: no BLOCK MOVE line in $SRC/run.log"; exit 1; }
echo "$last" | awk -v force="${FORCE:-no}" '{b=$11;l=$13;gsub(/[Dd]/,"E",b);gsub(/[Dd]/,"E",l)
    if (l+0==0) { print "GUARD: lambda_d is ZERO -- collapsed point"; exit 1 }
    if (b+0>0.5) { print "GUARD: b above 0.5 -- degenerate point"; exit 1 }
    gb=100*((b+0)/0.10502-1); gl=100*((l+0)/0.043424-1)
    printf "candidate b=%.6f (%+.1f%%)  lambda_d=%.6f (%+.1f%%)  block_move=%s\n", b+0,gb,l+0,gl,$3
    if ((gb>15||gb<-15||gl>15||gl<-15) && force!="yes") {
        print  "GUARD: a moment is more than 15 per cent from target."
        print  "       The stopping rule is block_move < frozen_stop_tolerance, which means"
        print  "       THE BLOCKS STOPPED MOVING, not that the moments arrived. A run that"
        print  "       halts far from target is a premature stop, and publishing it would"
        print  "       put every scan point on a vector that is not the benchmark."
        print  "       If this point is wanted anyway:  FORCE=yes ./publish_scan_seed.sh"
        exit 1 } }' || exit 1

rm -rf scan_seed && mkdir -p scan_seed
cp "$SRC/calibration_state.dat" scan_seed/
cp "$SRC/calibration_distribution_shape.dat" scan_seed/
gzip -c "$SRC/calibration_distribution1.dat" > scan_seed/calibration_distribution1.dat.gz
gzip -c "$SRC/calibration_distribution2.dat" > scan_seed/calibration_distribution2.dat.gz
{ echo "# The converged two-class omega_c = 0 benchmark, published $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "# source run: $SRC"
  echo "$last" | cut -c1-160
  echo "# addiction_scalar_1  $(grep -a '^ addiction_scalar_1=' "$SRC/run.log" | tail -1 | awk '{print $2}')"
  echo "# addiction_onset_base $(grep -a '^ addiction_onset_base=' "$SRC/run.log" | tail -1 | awk '{print $2}')"
} > scan_seed/PROVENANCE.txt
du -sh scan_seed && ls -la scan_seed | awk '{print $5,$9}'
echo
echo "now:  git add -f code/scan_seed && git commit && git push"
echo "then each session runs:  code/remote_scan_point.sh <omega_c>"
