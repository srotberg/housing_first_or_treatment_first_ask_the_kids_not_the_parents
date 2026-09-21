#!/bin/bash
# restart_transition.sh <run dir>
#
# Promotes the five *_out.txt paths a running transition writes every loop to
# the five seed files the next run reads, so a restart resumes from the latest
# guesses instead of from the level-and-slope ramp.
#
# WHY THIS IS A SCRIPT AND NOT AUTOMATIC. The writer deliberately does NOT
# overwrite the seed files it read. t30_loop1_pivcollapse is the reason: pi_v
# went through zero to its floor in every period in one step, h_1 went to NaN,
# and as a file that is 29 plausible decimals. A run that automatically
# inherited its own last loop would have inherited that. So promotion is a
# deliberate act, and this script is where the guards live.
#
# The Fortran readers guard too -- pi_v on a bound is refused, a house price or
# rent at or below zero is refused, a short file keeps the ramp for the periods
# it could not read -- but a guard that fires after four hours of staging is
# worth firing here instead.
set -e
N=${1:?usage: restart_transition.sh <run dir>}
[ -d "$N" ] || { echo "REFUSING: no run dir at $N"; exit 1; }
cd "$N"

PAIRS="drug_price_path_seed pi_v_path_seed house_price_path_seed rent_path_seed lump_sum_path_seed"

# NOTHING IS PROMOTED UNTIL EVERYTHING HAS BEEN CHECKED. A half-promoted set --
# a new price path against an old pi_v path -- is a state no loop ever produced
# and is worse than either.
bad=0
for b in $PAIRS; do
  f="${b}_out.txt"
  if [ ! -f "$f" ]; then echo "  MISSING $f"; bad=1; continue; fi
  n=$(grep -cv '^[[:space:]]*\(#\|$\)' "$f" || true)
  if [ "$n" -eq 0 ]; then echo "  EMPTY $f"; bad=1; continue; fi
  if grep -qi 'nan\|infinity' "$f"; then echo "  NaN or Infinity in $f"; bad=1; continue; fi
  case "$b" in
    pi_v_path_seed)
      if awk '!/^[[:space:]]*(#|$)/ {if ($1+0 <= 0.000010000011 || $1+0 >= 0.999999) exit 1}' "$f"; then :; else
        echo "  $f has an entry on a bound -- this is the collapse the clip exists to stop"; bad=1; fi ;;
    drug_price_path_seed|house_price_path_seed|rent_path_seed)
      if awk '!/^[[:space:]]*(#|$)/ {if ($1+0 <= 0) exit 1}' "$f"; then :; else
        echo "  $f has a non-positive entry"; bad=1; fi ;;
  esac
  echo "  ok $f  ($n entries, loop $(grep -m1 'after loop' "$f" | awk '{print $NF}'))"
done

[ "$bad" -eq 0 ] || { echo; echo "REFUSING to promote: fix or delete the files above."; exit 1; }

echo
for b in $PAIRS; do
  [ -f "${b}.txt" ] && cp "${b}.txt" "${b}.previous.txt"
  cp "${b}_out.txt" "${b}.txt"
  echo "promoted ${b}_out.txt -> ${b}.txt"
done
echo
echo "the previous seeds are kept as *_path_seed.previous.txt"
echo "restart with: cd $N && ./hftf > run.log 2>&1"
