#!/usr/bin/env bash
# THE STALL RESPONSE, ON A TIMER.
#
# The author, 4 September: automate a check that asks, when a target has not moved
# for many iterations, whether its parameter needs sampling extended above or
# below. expand.py answers that from the archive's own rays; this runs it and then
# solves whatever it emits.
#
# It is self-limiting by construction. expand.py emits ONLY for a moment whose
# target is outside the measured range of its parameter, at most MAX_PER_RUN
# instruments per pass, worst gap first, and nothing at all once a moment is
# bracketed or its parameter is against the bound. So a healthy calibration makes
# this loop do nothing, which is the point.
set -uo pipefail
cd "$(dirname "$0")/.."
EVERY=${1:-900}
while true; do
    {
        echo "===== $(date -u +%H:%M:%S)"
        python3 code/expand.py
    } >> code/expand.log 2>&1
    for f in code/scan/expand_*.txt; do
        [ -e "$f" ] || continue
        n=0
        while IFS= read -r line; do
            n=$((n+1)); [ -z "$line" ] && continue
            echo "$(date -u +%H:%M:%S)  $(basename "$f") line $n" >> code/expand.log
            eval "$line" >> code/expand.log 2>&1
        done < "$f"
        # CONSUMED, NOT DELETED. The file is the record of what the extension
        # actually asked for, and a rerun of the same lines would only re-solve
        # points the archive already holds.
        mv "$f" "${f%.txt}.done.$(date -u +%H%M%S).txt"
    done
    sleep "$EVERY"
done
