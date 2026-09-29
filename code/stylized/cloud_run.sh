#!/usr/bin/env bash
# Run one stylized job in a cloud worker and publish its log and outputs on a timer, with
# no agent involvement after launch.  Workers used to be told to run the job and then push
# every N minutes themselves; several ended their turn after starting the job and never
# pushed again, and two lost their runs because the job was started with nohup/& from a
# shell that exited, or wrote its log into a tracked file that git pull --rebase replaced.
#
# usage (start it with the Bash tool's run_in_background=true, from code/stylized):
#   bash cloud_run.sh <log name> "<extra files to commit>" <minutes between pushes> -- <command...>
# e.g.
#   bash cloud_run.sh stage1_sep29_cloud.log "calibrated_stage1.json" 10 -- python3 stages.py 1 start_stage1_sep29.json
set -u
LOG="$1"; EXTRA="$2"; EVERY="$3"; shift 4
BRANCH=claude/two-period-addiction-hazard-d7gb61
HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"
TMP="/tmp/$LOG"
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

publish() {
    cp "$TMP" "$HERE/$LOG"
    git add "$HERE/$LOG" $(for f in $EXTRA; do echo "$HERE/$f"; done) 2>/dev/null
    git commit -q -m "$1$TRAILER" || return 0
    # FROM A DETACHED HEAD TOO: some containers check the branch out detached, and a push
    # by branch name then has no local branch to send (the 1.5 x 0 scan, 23:45).  Rebase
    # onto the fetched tip and push HEAD to the branch.  -X theirs keeps this worker's own
    # version of a file on a conflict (in a rebase "theirs" is the commit being replayed).
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    echo "cloud_run: push failed after 4 tries" >> "$TMP"
}

STYLIZED_WORKERS=${STYLIZED_WORKERS:-4} "$@" > "$TMP" 2>&1 &
PID=$!
while kill -0 "$PID" 2>/dev/null; do
    for _ in $(seq 1 $((EVERY * 6))); do
        kill -0 "$PID" 2>/dev/null || break
        sleep 10
    done
    kill -0 "$PID" 2>/dev/null && publish "$LOG: partial output"
done
wait "$PID"; RC=$?
echo "cloud_run: exit code $RC at $(date -u +%H:%M)" >> "$TMP"
publish "$LOG: complete output (exit $RC)"
