#!/usr/bin/env bash
# The two decisive brackets, run locally so the answer is guaranteed to land
# whatever the fleet does.  run_one_point.sh takes a flock, so these interleave
# with the Nelder-Mead solver safely: a point is archived under the md5 of its
# own vector or not at all.
cd "$(dirname "$0")/.."
for f in code/batch_sigma_bracket.txt code/batch_pieu_bracket.txt; do
  n=0
  while IFS= read -r line; do
    n=$((n+1))
    [ -z "$line" ] && continue
    echo "$(date -u +%H:%M:%S)  $f line $n" >> code/brackets.log
    eval "$line" >> code/brackets.log 2>&1
  done < "$f"
done
echo "$(date -u +%H:%M:%S)  brackets done" >> code/brackets.log
