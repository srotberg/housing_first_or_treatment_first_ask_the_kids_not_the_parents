# bn_on090 -- NO MEASUREMENT OBTAINED

**Status: FAILED. This file reports a failure to measure, not a measurement.**
No scored moment below is filled in, because the solve never produced output.
Do not read any number into this point.

## What was asked

Measure the single point in `code/batch_bn_on090.txt`: the borrowing-ON,
`discount_factor_impatient=0.90` arm of the borrowing triple that commit
`ed8e7e2` split one line per worker out of `code/batch_borrow_now.txt`.

The instruction said to run "line 3". `code/batch_bn_on090.txt` has exactly
one line; there is no line 3, and `sed -n '3p'` on it returns empty. The
reference is to the pre-split shared file. This was checked rather than
assumed, and the right vector was run:

    diff <(sed -n '3p' code/batch_borrow_now.txt) \
         <(sed -n '1p' code/batch_bn_on090.txt)   -> IDENTICAL

The triple, by its distinguishing parameters:

| file | `include_unsecured_borrowing` | `discount_factor_impatient` |
|---|---|---|
| `batch_bn_off.txt`   | 0 | 0.75 |
| `batch_bn_on075.txt` | 1 | 0.75 |
| `batch_bn_on090.txt` | 1 | 0.90 |  <- this worker

The vector was typed out character by character in every attempt. No command
substitution, no backticks, no `sed ... | bash`, no `xargs` was used to launch
any of them. The vector was never altered between attempts; the solver
independently confirms this by hashing it to the same point id, `a2778b36aa`,
on all four runs.

## Why there is no measurement

The container running this session is reclaimed before the solve finishes.
Four attempts, four kills, none reaching output:

| # | outcome | log at kill |
|---|---|---|
| 1 | container restarted mid-solve | `running a2778b36aa on 4 cores` |
| 2 | container restarted mid-solve | `running a2778b36aa on 4 cores` |
| 3 | worker killed, exit 137 (SIGKILL), ~10-11 min in | `running a2778b36aa on 4 cores` |
| 4 | launched; see git history for whether it landed | -- |

`code/points/point_a2778b36aa.txt` was never written. The complete log of the
last attempt is `code/run_bn_on090.log`; it is one line long, which is the
whole of the evidence:

    running a2778b36aa on 4 cores

Attempt 1 additionally had to install gfortran (absent from a fresh container)
and build; it built cleanly, `hftf` from source hash
`1b081ebc4d54ffc28733415fe67f5989`. The build is not the problem. The solve is
simply longer-lived than the container.

Two environment facts behind this, neither fixable from inside the session:

- The instruction specified a 4-hour foreground timeout. The harness caps
  foreground Bash at 600 s regardless of the timeout passed, so a multi-hour
  solve cannot be held in the foreground here at all. Attempts ran as
  background/detached processes instead.
- Holding the session active with in-turn polling (~9.5 min of it on attempt 3)
  did not prevent the kill either, so the reclaim is not simply idle-timeout.

The commit message of `ed8e7e2` puts a solve at "ten minutes on the median of
493". This point exceeded 10-11 minutes without writing output, so it is
above that median -- consistent with borrowing-ON being the slower arm, and
consistent with it needing a container that outlives ~10 minutes.

## What was NOT done

Per instruction, on failure the vector was not changed and nothing was
retried differently. Specifically:

- the Fortran source was not modified;
- `supervise_calibration.py` was not run;
- `code/points_pregrid/` was not touched;
- nothing was pushed to `claude/two-period-addiction-hazard-d7gb61`;
- no rebase, no merge.

## The questions this point was to answer -- all still OPEN

These are the deliverables, and none of them can be answered:

1. **`w_bot`** (bottom wealth share) and its gap to target **0.0250** -- UNKNOWN.
2. **Every bottom-percentile wealth share, and: IS ANY NEGATIVE?** -- UNKNOWN.
   This is the direct test that unsecured borrowing is actually held in
   equilibrium; the data values it is tested against are -2.250e-03,
   -4.220e-03 and -4.460e-03. Until a solve completes, whether this arm holds
   negative wealth at the bottom is **untested**. It must not be recorded
   anywhere as passing or failing.
3. **`beta`** (wealth/GDP) against the target band **3.0-4.5** -- UNKNOWN.
4. Every other scored moment and its per-cent gap -- UNKNOWN.

## What would finish it

The point is deterministic and cheap to re-launch; it needs an execution
environment that survives longer than one solve. Any of: a container that is
not reclaimed for ~30+ minutes, a checkpoint/resume in `run_one_point.sh`, or
running this arm where its sibling arms (`bn_off`, `bn_on075`) are being run.
Re-launching is a single command -- line 1 of `code/batch_bn_on090.txt`.
