#!/usr/bin/env bash
# WAIT FOR THE SIMPLEX ROUND, THEN SEED AND RUN. One less thing to babysit.
#
# The fleet is landing the vertices of a rebuilt simplex. This waits until they
# have stopped arriving -- either the full count, or no new point for a while,
# because a worker can stall and the search should not wait on it forever --
# then seeds from whatever is there and starts the serial loop.
set -uo pipefail
cd "$(dirname "$0")/.."
WANT=${1:-21}
count() { python3 -c "
import sys; sys.path.insert(0,'code')
import newton as N, next_batch as NB
NB._apply_process_mapping()
print(len(N.archive()))" 2>/dev/null || echo 0; }
last=-1; still=0
for i in $(seq 1 120); do
    git pull --rebase -q origin claude/two-period-addiction-hazard-d7gb61 >/dev/null 2>&1
    n=$(count)
    echo "$(date +%H:%M:%S)  $n of $WANT vertices"
    [ "$n" -ge "$WANT" ] && break
    if [ "$n" -eq "$last" ]; then still=$((still+1)); else still=0; fi
    # Six quiet checks in a row -- three minutes -- means the round has drained.
    [ "$still" -ge 6 ] && [ "$n" -ge 12 ] && { echo "round drained at $n"; break; }
    last=$n
    sleep 30
done
python3 code/nelder.py --init
exec bash code/nm_loop.sh 400
