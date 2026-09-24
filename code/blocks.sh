#!/bin/sh
# Per-block b, lambda_d, h_1 and the bequest_residual standing at that block.
#
# EXPONENT-SAFE. A naive grep reads 9.9849E-002 as 9.98; awk's $x+0 does not.
#
# bequest_residual is printed by the BUDGET block, many times per block, so the
# reading carried here is the LAST one before the block's BLOCK MOVE line --
# the residual standing when the block's moments were taken. It is reported
# because b moves with the restart transient as well as with the policy: the
# 0.07 point read -28.06% at block 1 with a residual of 2.1197, against a
# settled -18.65% at 1.4496. Benchmark 1.4771; converged omega_c=0.06 1.45135.
LOG="${1:-internalise_h_oc006/run.log}"
grep -aE "BLOCK MOVE|BUDGET bequest_residual=" "$LOG" | awk '
/bequest_residual/ {
  for (i=1;i<=NF;i++) if ($i=="bequest_residual=") { br=$(i+1)+0 }
  # the value can also land in the same token when the field is wide
  if (br=="") { sub(/.*bequest_residual=/,""); br=$1+0 }
  next
}
/BLOCK MOVE/ {
  bm=""; b=""; ld=""; h1=""; y=""
  for (i=1;i<=NF;i++) {
    if ($i=="MOVE")     bm=$(i+1)+0
    if ($i=="b")        b =$(i+1)+0
    if ($i=="lambda_d") ld=$(i+1)+0
    if ($i=="h_1")      h1=$(i+1)+0
    if ($i=="y")        y =$(i+1)+0
  }
  n++
  printf "block %2d   b %.6f   lambda_d %.6f   h_1 %.6f   bequest_residual %.5f   y %.5f   block_move %.5f\n", n, b, ld, h1, br, y, bm
}'
