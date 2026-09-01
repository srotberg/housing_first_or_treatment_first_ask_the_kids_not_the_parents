#!/bin/bash
# Run a seed batch sequentially on this box, committing each point as it lands.
# One arm at a time: the model uses all four cores, so there is no parallelism
# to win locally, and a sequential run cannot strand a container the way the
# worker fleet has repeatedly done.
BATCH="${1:?usage: run_seed_batch.sh <batch file>}"
ROOT=/home/user/housing_first_or_treatment_first
cd "$ROOT" || exit 1
BR=claude/two-period-addiction-hazard-d7gb61
N=$(wc -l < "$BATCH")
i=0
while IFS= read -r LINE; do
    i=$((i+1))
    [ -z "$LINE" ] && continue
    echo "=== arm $i of $N === $(date -u +%H:%M:%S)"
    before=$(ls code/points/point_*.txt 2>/dev/null | wc -l)
    eval "$LINE"
    status=$?
    after=$(ls code/points/point_*.txt 2>/dev/null | wc -l)
    echo "=== arm $i exit $status, points $before -> $after"
    if [ "$after" -gt "$before" ]; then
        git add -A code/points/ >/dev/null 2>&1
        git commit -q -m "seed arm $i of $N from $(basename "$BATCH")" >/dev/null 2>&1
        for a in 2 4 8 16; do
            git push -q -u origin "$BR" >/dev/null 2>&1 && break
            sleep $a
        done
    fi
done < "$BATCH"
echo "=== seed batch complete $(date -u +%H:%M:%S)"
