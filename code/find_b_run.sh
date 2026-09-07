#!/usr/bin/env bash
cd /home/user/housing_first_or_treatment_first || exit 1
while read -r line; do
  echo "=== $(date -u +%H:%M:%S) $(echo "$line" | grep -o 'addiction_scalar_1=[^ ]*') ==="
  eval "$line" >> code/find_b.log 2>&1
done < code/find_b.txt
echo "=== done $(date -u +%H:%M:%S) ==="
