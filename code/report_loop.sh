#!/bin/sh
# Append a progress report every ten minutes, forever.
#
# WHY A FILE AND NOT A MONITOR. An in-session monitor caps at thirty minutes
# whatever its persistent flag says, so reports lapse until it is re-armed and
# the ones in between are lost. This writes to a file that keeps accumulating,
# so re-arming a monitor over it costs nothing and no report is missed.
cd "$(dirname "$0")/.." || exit 1
while true; do
    {
        echo "----- $(date -u '+%H:%M UTC') -----"
        timeout 300 python3 code/progress_report.py 2>&1
    } >> code/progress_reports.txt
    sleep 600
done
