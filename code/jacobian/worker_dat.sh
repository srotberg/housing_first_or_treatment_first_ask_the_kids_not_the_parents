#!/bin/bash
# worker_dat.sh KEY... -- run_jacobian_dat.sh for a worker session (11 November): starts it detached on the first call, attaches on
# every later call, and returns only when it has finished. Run it with the Bash tool's run_in_background=true from the repo
# root, and run the SAME command again whenever the call stops: a finished key is skipped, a running job is attached to.
# Each finished solve is committed and pushed to the branch by the job itself (JAC_PUSH=1). run_jacobian_dat.sh is not
# edited while a job runs (bash reads a running script by offset), which is why this wrapper is a separate file.
C=$(cd "$(dirname "$0")/.." && pwd)
ID=$(echo "$*" | md5sum | cut -c1-8); PIDF=$C/jacobian/worker_dat_$ID.pid; LOG=$C/jacobian/worker_dat_$ID.log
alive() { [ -f "$PIDF" ] && kill -0 "$(cat "$PIDF")" 2>/dev/null; }
if alive; then
    echo "attached to pid $(cat "$PIDF") ($*)"
else
    ( cd "$C/.." && JAC_PUSH=1 setsid nohup bash "$C/jacobian/run_jacobian_dat.sh" "$@" > "$LOG" 2>&1 < /dev/null & echo $! > "$PIDF" )
    echo "started pid $(cat "$PIDF") ($*)"
fi
while alive; do sleep 60; done
echo "finished"
tail -n 40 "$LOG"
