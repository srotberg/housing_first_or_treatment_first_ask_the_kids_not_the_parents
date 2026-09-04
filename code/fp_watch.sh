#!/usr/bin/env bash
# THE FIXED POINT NEVER STOPS. The author, 4 September: *"you should allow my
# method to update all the time continuously"*.
#
# Same shape as night_watch.sh, and for the same reason: the solver must not also
# be the thing that remembers to restart itself, because when it dies the work dies
# with it. fixed_point.py writes its live vector every iteration and resumes from
# it, so a restart continues the walk rather than resetting it.
set -uo pipefail
cd "$(dirname "$0")/.."
while true; do
    if ! ps -eo args= | awk '$2 ~ /fixed_point\.py/ {f=1} END {exit f?0:1}'; then
        echo "$(date -u +%H:%M) fixed_point not running; starting" \
            >> code/fp_watch.log
        nohup python3 code/fixed_point.py >> code/fixed_point.log 2>&1 &
        sleep 30
    fi
    sleep 60
done
