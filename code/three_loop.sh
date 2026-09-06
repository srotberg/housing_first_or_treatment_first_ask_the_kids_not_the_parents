#!/usr/bin/env bash
# The author's three-instrument fixed point, iterated.
#
#   "I think you need to let my method run for a while and see if the model
#    converges"   -- 6 September
#
# Each pass asks three_step.py for the next iterate and solves it, so the loop
# feeds on its own output, which is the whole point: every round before this one
# was a sample off a base picked by hand that firing, never an iteration.
#
# THE STEP NO LONGER TAKES THE NEWEST CONFIGURED POINT AS ITS BASE, and this
# comment used to say that it did. The correction round's arms carry the same
# configuration -- they are one-coordinate variations off a base that shares it --
# so on 6 September the newest of them became the base and the iteration was
# handed to a search that is not this one. three_step.py now records every vector
# it asks for in code/three_step_iterates.txt and bases itself only on points
# solved from one of them.
#
# SERIAL, ON PURPOSE. run_one_point.sh takes a flock and rebuilds from the working
# tree on every line, so two of these at once would race on the handover file and
# could split one iteration across two builds. One at a time, four cores each.
#
# IT WRITES ITS OWN TRACE to three_loop.log: the step reasoning on stderr and the
# resulting moments after each solve, so the question the author actually asked --
# does it converge -- can be answered by reading the file rather than by trusting
# a summary.
set -u
D=/home/user/housing_first_or_treatment_first
cd "$D" || exit 1
N=${1:-40}
LOG="$D/code/three_loop.log"

# ONE LOOP AT A TIME, ENFORCED HERE. A manual start once collided with an armed
# wrapper and two loops iterated the same archive against each other for several
# minutes. Tested positionally on the basename, never with pgrep -f, which would
# match this script's own command line and every editor open on it.
# BOTH FIELDS, because the basename lands in a different one depending on how it
# was started: "bash code/three_loop.sh" puts it in $3, "./code/three_loop.sh"
# in $2.
alive=$(ps -eo pid=,args= | awk -v me=$$ '
    $1 == me { next }
    { for (f = 2; f <= 3; f++) {
          n = split($f, q, "/")
          if (q[n] == "three_loop.sh") { print $1; next }
      } }')
if [ -n "$alive" ]; then
    echo "three_loop already running as pid(s) $alive; refusing to start a second" >> "$LOG"
    exit 1
fi

echo "=== three_loop start $(date -u +%H:%M:%S), up to $N iterations ===" >> "$LOG"

for i in $(seq 1 "$N"); do
    echo "--- iteration $i, $(date -u +%H:%M:%S) ---" >> "$LOG"

    # stderr carries the step reasoning, stdout the line to run. Keep them apart.
    line=$(python3 code/three_step.py 2>>"$LOG")
    rc=$?
    if [ "$rc" != "0" ] || [ -z "$line" ]; then
        echo "three_step returned $rc with no line; stopping" >> "$LOG"
        break
    fi

    echo "$line" >> "$LOG"
    eval "$line" >> "$D/code/batch_run.log" 2>&1

    # The moments of whatever just landed, so the trace is readable on its own.
    newest=$(ls -t code/points/point_*.txt 2>/dev/null | head -1)
    if [ -n "$newest" ]; then
        {
          echo "  solved $(basename "$newest" .txt)"
          grep -aE "MOMENT (h_1|h_2|emp_homeless|gamma|beta) " "$newest" |
              sed 's/^/    /'
        } >> "$LOG"
    fi
done

echo "=== three_loop done $(date -u +%H:%M:%S) ===" >> "$LOG"
