#!/bin/bash
# worker_rungtwin.sh STEP KEY... -- run_jacobian_rungtwin.sh (h_2 alone, h_3 and h_4 held, the child's weight at zero) at JAC_STEP=STEP for a worker session (11 November). Starts it
# detached on the first call, attaches on every later call, and returns only when it has finished; run the SAME command
# again whenever the call stops. Each finished solve is committed and pushed by the job itself.
C=$(cd "$(dirname "$0")/.." && pwd)
STEP=$1; shift
ID=$(echo "$STEP $*" | md5sum | cut -c1-8); PIDF=$C/jacobian/worker_rungtwin_$ID.pid; LOG=$C/jacobian/worker_rungtwin_$ID.log
alive() { [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; }
if alive; then
    echo "attached to pid $(cat "$PIDF") (step $STEP: $*)"
else
    ( cd "$C/.." && JAC_STEP=$STEP JAC_PUSH=1 setsid nohup bash "$C/jacobian/run_jacobian_rungtwin.sh" "$@" > "$LOG" 2>&1 < /dev/null & echo $! > "$PIDF" )
    echo "started pid $(cat "$PIDF") (step $STEP: $*)"
fi
while alive; do sleep 60; done
echo "finished"
tail -n 40 "$LOG"
