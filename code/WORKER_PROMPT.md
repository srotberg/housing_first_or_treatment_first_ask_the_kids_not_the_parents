# The calibration worker's procedure

Eight worker triggers fire hourly and each reads THIS FILE. The trigger prompt
carries only the worker's number; everything about how to run a point lives
here, so a correction is one commit rather than eight trigger edits. That
matters: the launch bug below cost a whole night, and fixing it in eight
places was itself part of why it took so long to land.

You are worker N of 8, where N is in your trigger prompt.
YOUR LINES ARE N, N+8, N+16, N+24, ... every 8th line of `code/ROUND.txt`
starting at line N.

## How long a point takes, so you do not give up early

Compiling the Fortran takes about ONE MINUTE (measured: 59 seconds on 4 cores)
and only on the first point in a fresh container. Solving one point takes 25 to
40 minutes on 4 cores. A point is due back within about 45 minutes of launch.

- Still running at 20 or 30 minutes: NORMAL. Never a reason to stop or to end
  your turn.
- Still running past 60 minutes: a FAULT. Report it with the tail of its log
  and move to your next line.

## Setup

    git checkout claude/two-period-addiction-hazard-d7gb61 || \
      git checkout -b claude/two-period-addiction-hazard-d7gb61 origin/claude/two-period-addiction-hazard-d7gb61
    git pull --rebase origin claude/two-period-addiction-hazard-d7gb61

Repository: https://github.com/srotberg/housing_first_or_treatment_first
If it is not already checked out in the home directory, clone it there.

## For each of your lines, in order

**1. Read it.** `sed -n "${L}p" code/ROUND.txt` — no such line means you are
done: report and stop.

**2. Run it. Never decide for yourself whether it was already measured.**
`run_one_point.sh` makes that decision itself and exactly, from the md5 of the
full parameter vector: an already-measured point prints "is already measured,
skipping" and exits within a second. A worker that judged this by hand once
compared the 19 names on a round line against the 24 on a point file's VECTOR
line, got it wrong, ran nothing at all, and ended its turn reporting success —
the worst kind of failure, because it is invisible.

**THE LAUNCH SHAPE IS THE PART THAT MATTERS.** Issue ONE Bash tool call with
`run_in_background: true` whose command is the round line running in the
FOREGROUND of that call:

    eval "$(sed -n "${L}p" code/ROUND.txt)" > /tmp/line_${L}.log 2>&1

DO NOT write `nohup ... &` inside a tool call, and do not append `&`. A
backgrounded child of a tool call is reaped the moment the launcher returns:
the model binary is killed a second or two into its build, no point file is
ever written, and you are left polling for a file that cannot appear. That is
exactly what happened on the first two automated rounds — one worker quit after
four minutes, seven hung for over an hour, and between them they measured
nothing across nine hours.

`run_in_background` keeps the command alive across turns and notifies you when
it exits, which is what a 25 to 40 minute solve needs. Wait for that
notification. Do not poll with a foreground sleep.

**3. Push the result, whatever it is.** A file appears under `code/points/`:
either `point_<hash>.txt` with the moments, or `point_<hash>.FAILED.txt` saying
why it could not run. Commit and push EITHER, before starting your next line:

    git add code/points
    git commit -m "Round worker N, line ${L}"
    git pull --rebase origin claude/two-period-addiction-hazard-d7gb61 && \
      git push origin HEAD:claude/two-period-addiction-hazard-d7gb61

If the push is rejected, pull --rebase and retry, up to four times. A failure
that leaves nothing in the repository looks exactly like a point still solving,
which is the whole reason the FAILED file is pushed too.

**4. Go on to your next line.** Do not stop after one point.

## Report

Say how many points you ran, and for each the MOMENT lines with their targets
and any DIAG lines. If you ran none, say so plainly and say why. NEVER report
success for a turn that measured nothing.

## Notes

- "OMEGA SKIPPED" in place of a "MOMENT omega" line is CORRECT, not a failure.
- If one point fails, say what the error was, push its FAILED file, and CONTINUE
  with your next line. Do not edit anything to work around it.
- Do not run simplex.py. Do not change ROUND.txt. A coordinator trigger owns
  the rounds.
- Do not edit any source file.
- Another firing of you starts in an hour; it will skip whatever is already
  measured.
