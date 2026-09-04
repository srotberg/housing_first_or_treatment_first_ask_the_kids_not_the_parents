#!/usr/bin/env bash
# THE WATCHDOG. stage_night.py died at 06:00 and nothing noticed for twenty-two
# minutes, which on a night run is twenty-two minutes of nothing. This restarts
# it whenever it is not running, and pushes on its own clock so a container
# reclaim costs at most one point.
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61
while true; do
    if ! ps -eo args= | awk '$2 ~ /stage_night/ {f=1} END {exit f?0:1}'; then
        echo "$(date -u +%H:%M) stage_night not running; starting" >> code/night_watch.log
        nohup python3 code/stage_night.py >> code/stage_night.log 2>&1 &
        sleep 30
    fi
    sleep 60
    git add -A code/points code/.nm_state.json code/nm_trace.txt code/batch_nm.txt \
        code/nm_stage.txt code/stage_night.log code/night_watch.log \
        code/nm_run.log code/calibration_state.dat code/B_SWEEP_GRID.txt \
        code/batch_stage*_seed.txt >/dev/null 2>&1
    git commit -q -m "Night run, $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
    git pull --rebase -q origin $B >/dev/null 2>&1 || {
        for f in $(git ls-files -u | awk '{print $4}' | sort -u); do
            git checkout --theirs "$f" >/dev/null 2>&1; git add "$f" >/dev/null 2>&1
        done
        git -c core.editor=true rebase --continue >/dev/null 2>&1
    }
    git push -q origin $B >/dev/null 2>&1
done
