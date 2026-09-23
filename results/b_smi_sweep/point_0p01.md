# b_smi_multiple = 0.01 — BLOCKED, NO BLOCK COMPLETED

**Final for this container, 01:38 UTC, 23 September. No moment is reportable.**
Four launches, two of them resumes that each failed to close a single loop.
Nothing below is a number to put in the sweep table.

    b_smi_multiple      0.01
    blocks completed    0
    MOMENT r_smi        NOT MEASURED
    SUD | SMI           NOT MEASURED
    SUD | non-SMI       NOT MEASURED
    SMI participation   NOT MEASURED  (so the corner question is open)
    b                   NOT MEASURED
    lambda_d            NOT MEASURED
    model_fraction_homeless   NOT MEASURED

The point is not guessed and not interpolated. The sweep's worth is four
comparable points, and an invented one is worse than a missing one.

## Configuration, verified live on every start

    CONFIG b_smi_multiple= 1.0000000000000000E-002  b_smi_multiple_adjuster= 0.0000000000000000
           freeze_all_but_omega_c= 1  voucher_conditional_on_clean= 0

Benchmark, not Treatment First. The point is held: its adjuster is zero and the
other 47 are frozen.

## Why it is blocked

The solve is reaped externally after ~5 minutes, every time, with `run.err`
empty, no OOM record and no Fortran fault. Four launches:

    00:30  cold    died ~00:37      checkpoint written, "after loop 2"
    00:55  cold    died  00:59:59   checkpoint written, "after loop 2"
    01:21  resume  died  01:26:49   checkpoint NOT rewritten, still loop 2
    01:30  resume  died  01:33:45   checkpoint NOT rewritten, still loop 2

The last two lines are the decisive test. `calibration_state.dat` has been
stamped 00:59:56 throughout both resumes, so neither closed a loop and neither
banked anything. Longest contiguous run observed: ~7 minutes. Compute needed for
the six blocks asked for: 35+ minutes contiguous, or a checkpoint that survives
a mid-loop kill. Neither is available here.

Container reboots compound it but are NOT the cause — the reaps land several
minutes BEFORE each reboot (boots at 00:28:04, 00:52:35, 01:14:30, 01:28:16,
01:37:40).

`calibration_state.dat` is only rewritten at the END of a loop — the source says
so itself at lines 46709 and 52206 ("a kill costs one loop instead of all of
them"). A resume spends most of its ~5 minutes re-reading state and redoing the
newborn and distribution setup, so loop 3 never closes and nothing is banked.
A block needs ~20 minutes for the first and ~5 after (`results/oneclass_core/LAUNCH.md`).
The run is on a treadmill at loop 2.

**An auto-restart supervisor would not fix this**, and should not be requested:
a restart cannot preserve an in-flight loop, so it would resume from loop 2
forever at full CPU. What is missing is a container that does not kill the
process every five minutes, not a permission.

## Two findings that hold regardless, and the first is urgent for the other points

**1. `freeze_all_but_omega_c` does not survive a resume.** It is declared `0` at
source line 946 and is set ONLY from `PARAM_HANDOVER`; it is never written to or
read back from `calibration_state.dat`, unlike `b_smi_multiple` and its adjuster
(written at 45283/45284, read at 45651/45664). So a sweep point that reboots and
is relaunched in place comes back with all 47 adjusters LIVE, its own point still
pinned, and nothing in the log saying so. The brief's "just relaunch the binary
in place, it resumes from its checkpoint" is unsafe for this sweep.

Any sibling point that has been relaunched in place should check its log for a
`HANDOVER freeze_all_but_omega_c` line on the CURRENT launch. If there is none,
the adjusters were live and that point's numbers are contaminated.

**2. The fix is to declare the sweep's switches in the source** — the remedy
`code/ENGINE.md` already prescribes ("PUT SWITCHES IN THE SOURCE, NOT ONLY IN THE
VECTOR"). Done here in a PRIVATE copy, `code/b_smi_0p01/hftf_src.f90`, which is
inside the gitignored run directory:

    line  946   freeze_all_but_omega_c = 0  ->  1
    line 2149   b_smi_multiple = 1.d0       ->  0.01d0
    + a CONFIG print, after the state file and the handover and before the
      freeze is applied, so it reports the live configuration on a cold start
      and on a resume alike

The shared `code/housing_first_or_treatment_first_SR_v1.f90` is UNTOUCHED — three
sibling points build from it. Both builds off the patched copy are clean, 7
warnings and 0 errors, identical to the unpatched source. No economics changed.
The `CONFIG` line is what makes a resumed run verifiable at all; the `HANDOVER`
lines cannot do it, because the handover is consumed on the first read.
