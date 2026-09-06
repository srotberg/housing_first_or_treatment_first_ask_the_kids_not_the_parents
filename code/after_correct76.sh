#!/usr/bin/env bash
# Start the author's method once the CORRECT_76 correction round is finished.
#
# WHY IT WAITS. The round's fifteen arms are one-coordinate variations off
# point_36412aab69, which is to say they are exactly the CONTROLLED PAIRS the
# extended step needs: sixteen of the twenty-three instruments currently report
# "NO CONTROLLED PAIR YET -- not stepping" and will keep reporting it until those
# arms land. Starting the loop first would also put two solves on four cores and
# violate the serial rule in ENGINE.md, which suspends everything else while the
# serial search is alive.
#
# IT WAITS ON THE WRAPPER'S PIDS, not on a pattern. The round is a bash -c whose
# command line is the whole batch script, so any pattern test would have to match
# a substring of it -- the thing the standing rule forbids. The pids are known,
# they are ours, and kill -0 sends no signal.
set -u
D=/home/user/housing_first_or_treatment_first
cd "$D" || exit 1
LOG="$D/code/three_loop.log"

for p in "$@"; do
    while kill -0 "$p" 2>/dev/null; do sleep 60; done
done

# The wrapper can exit a moment before its last arm does. Wait that out too,
# tested positionally on the basename as ENGINE.md requires.
while ps -eo pid=,ppid=,args= | awk -v me=$$ '
        $1 == me || $2 == me { next }
        { for (f = 3; f <= 4; f++) {
              n = split($f, q, "/")
              if (q[n] == "run_one_point.sh") { found = 1 }
          } }
        END { exit found ? 0 : 1 }'; do
    sleep 60
done

echo "=== CORRECT_76 finished $(date -u +%H:%M:%S); starting the method ===" >> "$LOG"
exec bash code/three_loop.sh 40
