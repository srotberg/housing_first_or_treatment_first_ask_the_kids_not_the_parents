#!/usr/bin/env bash
cd /home/user/housing_first_or_treatment_first || exit 1
until [ "$(ps -eo args= | awk '{n=split($2,q,"/"); if(q[n]=="run_one_point.sh") f=1} END {print f?1:0}')" = "0" ]; do sleep 5; done
while read -r line; do
  echo "=== $(date -u +%H:%M:%S) $(echo "$line" | grep -o 'addiction_scalar_1=[^ ]*') ==="
  eval "$line" >> code/final_root.log 2>&1
done < code/final_root.txt
echo "=== done $(date -u +%H:%M:%S) ==="
