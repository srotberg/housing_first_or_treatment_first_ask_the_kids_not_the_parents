#!/usr/bin/env bash
# Run one batch file of run_one_point.sh lines, in sequence, logging to
# code/batch_run.log.  For workers: nohup this, poll the log, commit the points.
cd "$(dirname "$0")/.."
f="$1"
n=0
while IFS= read -r line; do
  n=$((n+1))
  [ -z "$line" ] && continue
  echo "$(date -u +%H:%M:%S)  $f line $n" >> code/batch_run.log
  eval "$line" >> code/batch_run.log 2>&1
done < "$f"
echo "$(date -u +%H:%M:%S)  BATCH DONE $f" >> code/batch_run.log
