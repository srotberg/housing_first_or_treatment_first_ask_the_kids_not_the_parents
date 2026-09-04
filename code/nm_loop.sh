#!/usr/bin/env bash
# THE SEQUENTIAL NELDER-MEAD LOOP: ask, solve, tell, repeat.
#
# One model solve per turn, about 2.5 minutes, which is what makes a serial
# direct search the right shape here.  Nothing in this loop differentiates
# anything; it only ever compares two measured objective values, so the drug
# block's cliff -- a 0.35 per cent move in addiction_scalar_1 swinging lambda_d
# from -4.5 to -96.5 per cent -- costs one reflection instead of a whole step.
#
#   bash code/nm_loop.sh [max_iterations]
#
# run_one_point.sh already refuses to re-solve a tag it has measured, so a trial
# that lands on an existing vector costs seconds rather than minutes.
set -uo pipefail
cd "$(dirname "$0")/.."
N=${1:-400}
for ((i=1; i<=N; i++)); do
    echo "=== iteration $i  $(date +%H:%M:%S) ==="
    python3 code/nelder.py --ask || { echo "ask refused; stopping"; break; }
    bash code/batch_nm.txt >/dev/null 2>&1
    python3 code/nelder.py --tell || echo "  tell failed on iteration $i"
    # Commit every twelfth point so a container reclaim costs at most half an
    # hour of solves.  A measurement that is not in the repo did not happen.
    if (( i % 12 == 0 )); then
        git add -A code/points code/.nm_state.json code/nm_trace.txt >/dev/null 2>&1
        git commit -q -m "Nelder-Mead, through iteration $i

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv" >/dev/null 2>&1
        git push -q origin claude/two-period-addiction-hazard-d7gb61 >/dev/null 2>&1 \
          || echo "  push failed on iteration $i"
    fi
done
echo "=== loop finished ==="
