#!/bin/sh
# Per-block b, lambda_d and h_1 from a run log, exponent-safe.
# A naive grep reads 9.9849E-002 as 9.98; awk's $x+0 does not.
LOG="${1:-internalise_h_oc006/run.log}"
grep -a "BLOCK MOVE" "$LOG" | awk '
{
  bm=""; b=""; ld=""; h1=""; y=""
  for (i=1;i<=NF;i++) {
    if ($i=="MOVE")     bm=$(i+1)+0
    if ($i=="b")        b =$(i+1)+0
    if ($i=="lambda_d") ld=$(i+1)+0
    if ($i=="h_1")      h1=$(i+1)+0
    if ($i=="y")        y =$(i+1)+0
  }
  n++
  printf "block %2d   b %.6f   lambda_d %.6f   h_1 %.6f   y %.5f   block_move %.5f\n", n, b, ld, h1, y, bm
}'
