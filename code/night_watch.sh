#!/usr/bin/env bash
# THE WATCHDOG. stage_night.py died at 06:00 and nothing noticed for twenty-two
# minutes, which on a night run is twenty-two minutes of nothing. This restarts
# it whenever it is not running, and pushes on its own clock so a container
# reclaim costs at most one point.
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61
while true; do
    # code/PAUSE_NM holds the Nelder-Mead solver off while something else owns
    # the CPU -- a coordinate scan, a bracket -- without stopping the pusher,
    # which still has to commit whatever those runs produce. The file is removed
    # to resume. code/STOP is the author's marker and is not touched here.
    if [ ! -f code/PAUSE_NM ] && \
       ! ps -eo args= | awk '$2 ~ /stage_night/ {f=1} END {exit f?0:1}'; then
        echo "$(date -u +%H:%M) stage_night not running; starting" >> code/night_watch.log
        nohup python3 code/stage_night.py >> code/stage_night.log 2>&1 &
        sleep 30
    fi
    sleep 60
    # ADD THE WHOLE DIRECTORY, NOT A LIST OF PATHS.
    #
    # A named path that does not exist makes `git add` fail for the WHOLE call,
    # so nothing is staged and the commit that follows is a silent no-op. This
    # pusher listed code/night_watch.log, which is only created when a restart
    # happens, so on a healthy night it never existed and the pusher never
    # pushed anything -- seven solved points sat uncommitted while the log said
    # nothing was wrong. The same trap cost three separate commits tonight.
    git add -A code >/dev/null 2>&1
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
