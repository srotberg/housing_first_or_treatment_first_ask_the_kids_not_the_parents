#!/usr/bin/env bash
# START THE CALIBRATION LOOP IF IT IS NOT RUNNING. Idempotent, safe to call from
# every engine firing.
#
# WHY THIS EXISTS. On 8 September at 04:41 the container restarted -- uptime read
# 147 seconds at 04:44 -- and took loop_watch, three_loop and the in-flight solve
# with it. Nothing was logged, because nothing got the chance: the loop's own
# exits all write a line and this wrote none. loop_watch.sh restarts three_loop,
# but nothing restarts loop_watch, so a container restart ends the run silently
# and the next report finds an archive that stopped growing hours earlier.
#
# The ten-minute engine firings are the only thing that outlives a restart, so
# they are the outer watchdog and this is what they call.
#
# Tested positionally on the basename, never with pgrep -f, which would match
# this script's own command line and any editor open on it.
set -u
cd /home/user/housing_first_or_treatment_first || exit 1

alive=$(ps -eo pid=,args= | awk '
    { for (f = 2; f <= 4; f++) {
          n = split($f, q, "/")
          if (q[n] == "loop_watch.sh") { print $1; next }
      } }')

if [ -n "$alive" ]; then
    echo "loop_watch already running as pid(s) $alive"
    exit 0
fi

# setsid so it does not sit in the caller's process group and die with it.
setsid nohup bash code/loop_watch.sh >> code/loop_watch.out 2>&1 < /dev/null &
sleep 5
now=$(ps -eo pid=,args= | awk '
    { for (f = 2; f <= 4; f++) {
          n = split($f, q, "/")
          if (q[n] == "loop_watch.sh") { print $1; next }
      } }')
if [ -n "$now" ]; then
    echo "loop_watch STARTED as $now at $(date -u +%H:%M:%S)"
else
    echo "loop_watch FAILED TO START -- read code/loop_watch.out"
    exit 1
fi
