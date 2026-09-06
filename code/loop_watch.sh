#!/usr/bin/env bash
# Keep the author's method running unattended.
#
#   "let is run for a while and let's see what happens in a few hours"
#                                                   -- 6 September, 23:35
#
# WHY THIS EXISTS. three_loop stops the moment three_step returns non-zero, and
# at 22:37 it did exactly that -- a target had been added to TARGETS without the
# matching moment being added to the parser, every point failed the "carries all
# targets" test, iterates() came back empty and the loop halted after five
# iterations. Nothing restarted it and nothing said so. Over a few hours
# unattended that is the difference between fifty iterations and five.
#
# IT DOES NOT PAPER OVER A REAL FAULT. A loop that dies immediately on every
# restart is a broken step, not a transient, so consecutive fast failures back
# off and then stop, leaving the reason in the log rather than spinning.
#
# IT IDLES WITH sleep, NOT WITH read -t. The first version waited with
# "read -t 60 x < /dev/zero", which does not idle at all: /dev/zero never
# delivers a newline, so bash spins on it and the watchdog burned a full core.
# On four cores that is a quarter of the machine taken from the solver, and the
# solve running when it was found was at 27 minutes against a 3 minute median.
#
# code/STOP_LOOP stops it deliberately: the file is checked every pass and the
# watchdog exits without starting anything. code/STOP is the author's own marker
# and is honoured the same way.
set -u
D=/home/user/housing_first_or_treatment_first
cd "$D" || exit 1
LOG="$D/code/loop_watch.log"
fails=0

running() {
    ps -eo pid=,ppid=,args= | awk -v me=$$ '
        $1 == me || $2 == me { next }
        { for (f = 3; f <= 4; f++) {
              n = split($f, q, "/")
              if (q[n] == "three_loop.sh") { found = 1 }
          } }
        END { exit found ? 0 : 1 }'
}

while true; do
    if [ -f code/STOP_LOOP ] || [ -f code/STOP ]; then
        echo "$(date -u +%H:%M:%S) stop marker present; watchdog exiting" >> "$LOG"
        exit 0
    fi
    if ! running; then
        started=$(date +%s)
        echo "$(date -u +%H:%M:%S) three_loop not running; starting (failures so far $fails)" >> "$LOG"
        bash code/three_loop.sh 60 >> "$D/code/three_loop_nohup.log" 2>&1
        ran=$(( $(date +%s) - started ))
        if [ "$ran" -lt 120 ]; then
            fails=$((fails + 1))
            echo "$(date -u +%H:%M:%S) it lasted ${ran}s, which is a broken step rather than a transient (failure $fails of 5)" >> "$LOG"
            if [ "$fails" -ge 5 ]; then
                echo "$(date -u +%H:%M:%S) five fast failures; stopping. Read code/three_loop.log for the reason." >> "$LOG"
                exit 1
            fi
            sleep $((30 * fails))
        else
            fails=0
        fi
    fi
    sleep 60
done
