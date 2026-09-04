#!/usr/bin/env bash
# Run the fixed-point solver and push what it produces, on its own clock.
# Mirrors night_watch.sh: the solver must never be the thing that also has to
# remember to commit, because when it dies the points die with it.
set -uo pipefail
cd "$(dirname "$0")/.."
B=claude/two-period-addiction-hazard-d7gb61
nohup python3 code/fixed_point.py >> code/fixed_point.log 2>&1 &
while true; do
    sleep 60
    git add -A code >/dev/null 2>&1
    git commit -q -m "fixed point, $(date -u +%H:%M) UTC

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
    git pull --rebase -q origin $B >/dev/null 2>&1 || {
        for f in $(git ls-files -u | awk '{print $4}' | sort -u); do
            git checkout --theirs "$f" >/dev/null 2>&1; git add "$f" >/dev/null 2>&1
        done
        git -c core.editor=true rebase --continue >/dev/null 2>&1
    }
    git push -q origin HEAD:refs/heads/fixed-point-run >/dev/null 2>&1
    ps -eo args= | awk '$2 ~ /fixed_point\.py/ {f=1} END {exit f?0:1}' || {
        echo "$(date -u +%H:%M) fixed_point.py exited" >> code/fixed_point.log
        exit 0
    }
done
