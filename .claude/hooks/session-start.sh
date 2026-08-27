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

# AND THE OFF SWITCH HAS TO SURVIVE A STALE CHECKOUT, which the local file alone
# does not. The container is restored from a snapshot that can sit several
# commits behind the branch: the calibration was halted, CALIBRATION_ACTIVE was
# removed and the removal was pushed, and the hook STILL relaunched the
# supervisor after each of the next two restarts, because the snapshot predated
# the removal and the file was back. Each time it ran the joint loop -- rewriting
# calibration_state.dat -- in a container that was measuring points, which is the
# defect the halt existed to stop.
#
# So the marker is read from the REMOTE TIP rather than from disk. It fails
# CLOSED: no network, no branch, no answer means no supervisor, because a
# supervisor that does not start costs one loop and a supervisor that starts when
# it should not costs every measurement taken beside it.
BRANCH=$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null) || exit 0
[ -n "$BRANCH" ] && [ "$BRANCH" != "HEAD" ] || exit 0
git -C "$ROOT" fetch --quiet origin "$BRANCH" 2>/dev/null || exit 0
git -C "$ROOT" cat-file -e FETCH_HEAD:code/CALIBRATION_ACTIVE 2>/dev/null || exit 0

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
