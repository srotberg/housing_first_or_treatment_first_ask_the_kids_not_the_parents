#!/bin/bash
# worker_step.sh STEP KEY... -- run_jacobian_step.sh at JAC_STEP=STEP for a worker session (11 November; the author: "You
# might need more than a 1% change for parameters to see the effects as described in the text ... Maybe you should try 2 or
# 5%"). Starts it detached on the first call, attaches on every later call, and returns only when it has finished. Run it
# with the Bash tool's run_in_background=true from the repo root, and run the SAME command again whenever the call stops:
# a finished key is skipped, a running job is attached to. Each finished solve is committed and pushed by the job itself.
C=$(cd "$(dirname "$0")/.." && pwd)
STEP=$1; shift
ID=$(echo "$STEP $*" | md5sum | cut -c1-8); PIDF=$C/jacobian/worker_step_$ID.pid; LOG=$C/jacobian/worker_step_$ID.log
alive() { [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; }
if alive; then
    echo "attached to pid $(cat "$PIDF") (step $STEP: $*)"
else
    ( cd "$C/.." && JAC_STEP=$STEP JAC_PUSH=1 setsid nohup bash "$C/jacobian/run_jacobian_step.sh" "$@" > "$LOG" 2>&1 < /dev/null & echo $! > "$PIDF" )
    echo "started pid $(cat "$PIDF") (step $STEP: $*)"
fi
while alive; do sleep 60; done
echo "finished"
tail -n 40 "$LOG"
