#!/usr/bin/env bash
cd /home/user/housing_first_or_treatment_first || exit 1
while read -r line; do
  echo "=== $(date -u +%H:%M:%S) rel_share=$(echo "$line" | grep -o 'relative_share_of_addiction_1=[^ ]*' | cut -d= -f2) ==="
  eval "$line" >> code/probe_theta.log 2>&1
done < code/probe_theta.txt
echo "=== probes done $(date -u +%H:%M:%S) ==="
