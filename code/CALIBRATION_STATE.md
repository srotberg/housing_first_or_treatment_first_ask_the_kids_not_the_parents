# THE TRANSITION'S STOP NOTE, AND ONE TRAP THAT REACHES EVERY RELAUNCH, 24 September 04:02

`results/transition/T60_STOPPED.md` (0e3c1e25). The session is archived. The
three findings that outlive it:

- **T = 60 fits in memory**: peak 9.820 GiB against the 13.361 GiB cgroup-v1
  cap, measured rather than extrapolated. A control solve cannot share the box
  with it (9.82 + 5.33 exceeds the cap).
- **A loop cannot restart from disk after a rebuild.** The drug-price and pi_v
  paths checkpoint per period (54892, 54901), but the value-function path and
  the distributions are never written, so a relaunch re-walks the whole backward
  pass, about 7 hours, before its first checkpoint.
- **newborn_parent_share must be fixed before any T = 60**, parts 1 and 2 of the
  groundwork's fix, and it is blocked on a newborn_parent_share.dat for the
  benchmark, which does not exist and cannot be faked.

**THE TRAP THAT REACHES THE STEADY-STATE RUNS TOO: the binary DELETES
PARAM_HANDOVER.txt as it starts.** A relaunch in the same run directory without
restaging therefore runs the Fortran DECLARATIONS -- measured, 0 HANDOVER lines
and 408,676 "budget does not clear" -- and addiction_onset_base is declared 0.
Every relaunch after a container rebuild must restage the handover, with any
extra lines added by hand re-applied, and must confirm the HANDOVER lines in the
new log. The three live counterfactual reruns each carry a block-level
reproduction control (omega_c = 1 at block 9, internalisation at block 5, the
Housing First reference at block 9) that would catch a declarations run; the
universal Treatment First has none, so its HANDOVER lines are the only guard.

