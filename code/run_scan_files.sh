#!/usr/bin/env bash
# Run named scan files, in order: bash code/run_scan_files.sh instrument [instrument...]
cd "$(dirname "$0")/.."
for name in "$@"; do
  f="code/scan/$name.txt"
  [ -f "$f" ] || { echo "no such scan file: $f" >> code/scan_run.log; continue; }
  n=0
  while IFS= read -r line; do
    n=$((n+1)); [ -z "$line" ] && continue
    echo "$(date -u +%H:%M:%S)  $name line $n" >> code/scan_run.log
    eval "$line" >> code/scan_run.log 2>&1
  done < "$f"
  echo "$(date -u +%H:%M:%S)  DONE $name" >> code/scan_run.log
done
echo "$(date -u +%H:%M:%S)  ALL DONE" >> code/scan_run.log
