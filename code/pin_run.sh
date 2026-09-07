#!/usr/bin/env bash
cd /home/user/housing_first_or_treatment_first || exit 1
while read -r line; do
  echo "=== $(date -u +%H:%M:%S) $(echo "$line" | grep -o 'addiction_scalar_1=[^ ]*') $(echo "$line" | grep -o 'relative_share_of_addiction_1=[^ ]*') ==="
  eval "$line" >> code/pin_theta.log 2>&1
done < code/pin_theta.txt
echo "=== done $(date -u +%H:%M:%S) ==="
