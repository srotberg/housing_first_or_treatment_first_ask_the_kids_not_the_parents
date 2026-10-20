#!/bin/bash
# build_tr70_C2ck.sh [PLAIN] [OUT] -- THE RULE-C T = 70 BINARY WITH THE BACKWARD PASS CHECKPOINTED (20 October; for
# remote_tr70_Cfix.sh, the main transition with the drug price and pi_V held). build_tr70_ckpt.sh does this for the
# rule-CA sources; this is the same for rule C: transition_fix/patch_ckpt.py on top of the PLAIN build's own tr.f90
# (build_tr70_C2.sh's output, default code/tr70_C2u), so the two sources can only differ by the checkpoint's lines.
# Checked: the four TRANSITION CHECKPOINT prints are in, no line of the plain source is changed (lines added only), the
# plain build's patch_treatC2.md5 is carried over and patch_ckpt.py's md5 is written. Default OUT: code/tr70_C2uck.
# A new file: build_tr70_C2.sh and build_tr70_ckpt.sh are untouched.
set -e
C=$(cd "$(dirname "$0")/.." && pwd)
PLAIN=${1:-$C/tr70_C2u}
OUT=${2:-$C/tr70_C2uck}
[ -s "$PLAIN/tr.f90" ] && [ -s "$PLAIN/patch_treatC2.md5" ] || { echo "REFUSING: no plain rule-C build in $PLAIN (run build_tr70_C2.sh)"; exit 1; }
mkdir -p "$OUT"
python3 "$C/transition_fix/patch_ckpt.py" "$PLAIN/tr.f90" "$OUT/tr.f90"
n() { grep -c "$1" "$OUT/tr.f90" || true; }
[ "$(n 'RULE C (patch_treatC.py)')" = 1 ] || { echo "REFUSING: the source is not rule C"; exit 1; }
[ "$(n "TRANSITION CHECKPOINT loop=")" = 1 ] && [ "$(n "TRANSITION CHECKPOINT SAVED loop=")" = 1 ] \
    && [ "$(n "TRANSITION CHECKPOINT CLEARED loop=")" = 1 ] && [ "$(n "TRANSITION CHECKPOINT NOT SAVED loop=")" = 1 ] \
    || { echo "REFUSING: the checkpoint is not in the source"; exit 1; }
[ "$(diff "$PLAIN/tr.f90" "$OUT/tr.f90" | grep -c '^<')" = 0 ] || { echo "REFUSING: the checkpoint changed a line of the plain source"; exit 1; }
cp "$PLAIN/patch_treatC2.md5" "$OUT/patch_treatC2.md5"
md5sum "$C/transition_fix/patch_ckpt.py" | cut -c1-32 > "$OUT/patch_ckpt.md5"
( cd "$OUT" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium tr.f90 \
    -o hftf_tr_prod 2> build_prod.err )
[ -x "$OUT/hftf_tr_prod" ] && ! grep -q Error "$OUT/build_prod.err" || { echo "REFUSING: did not compile"; grep -m3 Error "$OUT/build_prod.err"; exit 1; }
echo "built $OUT/hftf_tr_prod $(md5sum "$OUT/hftf_tr_prod" | cut -c1-8) (rule C2 + cohort print + checkpoint, T = 70; $(diff "$PLAIN/tr.f90" "$OUT/tr.f90" | grep -c '^>') lines added to $PLAIN/tr.f90)"
