# Durable checkpoints for a long run

The container is ephemeral: it is reclaimed on inactivity or when the session
ends, and the run lives in scratch. Only what is PUSHED survives. These files
are the part of a run that is small enough to push.

## What resumes from what

- `*_seed.txt` is the PARAM_HANDOVER the run was started with. A run started
  from this reproduces the run's loop 1 exactly; j04 reproduced j03 to six
  digits this way.
- `*_calibration_state.dat` is the model's own checkpoint, 165 values: the
  parameters, the adjusters, the trust regions and the loop count. The model
  reads it on startup if it is in the working directory.

## What does NOT resume, and why it matters here

`calibration_distribution1.dat` and `calibration_distribution2.dat` are the
warm-start distribution, 78 MB together. They are OPTIONAL -- without them the
model prints "no warm start distribution, initialising from the age one cross
section" and continues from the state file alone -- and they are too large to
push repeatedly.

**For a hysteretic descent that is not a full resume.** Participation is
path-dependent: b_SG around 0.0075 sits at participation 0.089 on the way DOWN,
but a COLD start at the same b_SG lands near 0.19, because the cold-start map
and the descent path are different functions. So a resume from the state file
keeps the parameters and loses the path, and restarts with b_SG already high --
which then overshoots.

Treat a state-file resume as "the parameter vector survived", not "the run
survived". Say so rather than reporting a resumed run as a continuation.

## The tell for a container restart

Every way a run exits on its own writes a line. An iteration header with
nothing after it means the process was TAKEN, not that it stopped. ENGINE.md
records the 8 September restart that was misread as the harness reaping a
process group.
