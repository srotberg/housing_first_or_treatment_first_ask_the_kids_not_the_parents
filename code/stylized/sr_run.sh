#!/usr/bin/env bash
# LAUNCH THE STYLIZED CALIBRATION -- AND REFUSE TO LAUNCH A SECOND ONE.
#
# On 12 September FOUR copies of sr_calibrate.py were alive at once on a
# four-core box: sr_run_final.log, sr_run_kap.log, sr_run_11.log and
# sr_run_fixed.log, started 16, 13, 11 and 3 minutes apart.  Each launch was a
# fresh `timeout 7200 ... python3 -u sr_calibrate.py` that never checked whether
# the previous one was still alive, and each spawns a parent plus three workers,
# so the box was carrying sixteen processes with a load average of 10.3.  The
# newest run -- the only one on the current file -- was getting roughly a
# quarter of the machine, and the author was waiting on it.
#
# Worse than the slowdown: the three stale ones were running OLDER VERSIONS of
# sr_calibrate.py.  Python reads the whole file at import, so editing the script
# and relaunching leaves the old process running the old code, writing tables to
# its own log that look exactly like the new run's.  Reading the wrong log is
# then a single `ls -t` away.
#
# So: one run at a time, by name, checked positionally.  `pgrep -f` is not used
# anywhere in this repository and is not used here -- its pattern matches the
# caller's own command line.
set -u
cd "$(dirname "$0")" || exit 1

# THE GUARD MUST NOT MATCH THE CALLER'S OWN SHELL, and on 12 September it did.
# A launch was refused because the bash command that patched the driver and then
# ran this script carried the driver's name inside a heredoc, so the pattern
# found it and reported the caller as an already-live calibration.  This is the
# same self-match the kill rule in ENGINE.md warns about, in the test rather
# than in the kill.
#
# So the test is now on the COMMAND, not on a substring anywhere in the line: it
# matches only a command line that BEGINS with a python invocation of the
# driver.  A shell running -c, an editor, a grep and this script itself all
# carry the name somewhere in their arguments and none of them begins with it.
LIVE=$(ps -eo pid=,etime=,args= | awk '$3 ~ /^python3?$/ && /-u [s]r_calibrate\.py$/ {print; exit}')
if [ -n "$LIVE" ]; then
    echo "sr_run: a calibration is ALREADY ALIVE, refusing to start a second one"
    echo "sr_run:   $LIVE"
    echo "sr_run: its log is $(ls -t sr_run*.log 2>/dev/null | head -1)"
    echo "sr_run: stop that run first, or pass --force if you really want both"
    [ "${1:-}" = "--force" ] || exit 1
    echo "sr_run: --force given, starting anyway"
fi

# THE TIMEOUT HAS TO OUTLAST THE ITERATION CAP OR IT SILENTLY TRUNCATES THE RUN.
# The cap is 50000 iterations on the author's instruction of 12 September.  At
# the measured 1.25 s an iteration that is 17 hours, and about 35 with the
# branch check running on every step, so the old 3 hour default would have
# stopped it near iteration 4300 and the log would simply end -- no message, no
# FINAL table, nothing saying the run was cut rather than finished.  48 hours.
LOG="${SR_LOG:-sr_run_$(date -u +%H%M%S).log}"
echo "sr_run: starting, log $LOG"
# FOUR WORKERS, NOT THREE.  The 3 was set by hand while three stale runs were
# competing for a four-core box, and it outlived the reason for it: measured
# afterwards the run was using 223 per cent of 400.  stylized.py's own default
# is min(4, cpu_count), so this just stops overriding it downwards.
STYLIZED_WORKERS=${STYLIZED_WORKERS:-4} OMP_NUM_THREADS=1 \
    timeout "${SR_TIMEOUT:-172800}" nice -n 5 python3 -u sr_calibrate.py > "$LOG" 2>&1
echo "sr_run: finished, EXIT=$? log $LOG"
