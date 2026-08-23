#!/bin/bash
# Put the calibration back on the machine when the container comes up.
#
# WHY THIS EXISTS. The container rebuilds itself roughly every half hour and each
# rebuild kills the run. The supervisor banks its state to git every loop, so a
# rebuild costs one loop rather than the whole calibration -- but only once
# something relaunches it, and until this hook existed that was a scheduled check
# up to thirty minutes later. The idle time was costing more than the rebuild.
#
# THE OFF SWITCH IS A FILE. This hook launches a job that takes four cores for
# hours, and it fires on every session in this repository. It refuses to do that
# unless code/CALIBRATION_ACTIVE is present, so stopping it is `rm` and starting
# it again is `touch`. A hook whose only off switch is editing the hook is a trap.
set -euo pipefail

# Remote only: on a laptop this would seize the machine without being asked.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

ROOT="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
[ -f "$ROOT/code/CALIBRATION_ACTIVE" ] || exit 0

# Idempotent: never a second supervisor beside the first.
#
# POSITIONAL, NOT A SUBSTRING. `ps -eo args | grep supervise_calibration.py`
# matches any command line that merely mentions the script -- an editor, a grep,
# the shell that is launching it -- and the hook would then decline to start the
# thing it exists to start. The same self match has killed a loop mid launch and
# made a progress report claim the supervisor was up when it was not. Match a
# process whose argv[0] is a python and whose argv[1] is the script.
if ps -eo args= | awk '{ n = split($1, p, "/"); m = split($2, q, "/");
                         if (p[n] ~ /^python/ && q[m] == "supervise_calibration.py") found = 1 }
                       END { exit found ? 0 : 1 }'; then
  exit 0
fi

cd "$ROOT/code" || exit 0
setsid nohup python3 supervise_calibration.py \
  > "$ROOT/code/supervisor_launch.out" 2>&1 < /dev/null &
exit 0
