# THE TWO-BLOCK WELFARE PASS FAILED ITS CONTROL; A CURVE NEEDS A FRESH RUN, 24 September 03:13

I designed the welfare pass as: stop at the family rule, then RESUME from the
point's own converged state with `frozen_stop_after_blocks 2`, and score b at
1e-4 relative against the stopped run. On omega_c = 1 it missed by a factor of
346 -- b moved about 3.5 per cent in two blocks. A resume does not continue the
equilibrium; it re-enters the restart transient. The control caught it before
any CEV was quoted, which is what the control was for.

The design that stands: a FRESH run from `code/scan_seed/` with
`frozen_stop_after_blocks 12` in the handover from the start. The run goes
through the whole approach and leaves the loop at block 12 straight into
`save_welfare_curve`, with no kill and no resume. Its control is that an early
block reproduces the stopped run's b at the same block at 1e-4 relative, since
up to there it is the same solve.

Where each run stands on it (03:13):

    HF omega_c = 0.06   running this way from the start (session_015uvFUYEc5ziAB37Ckjvp5o)
    omega_c = 1         rerunning this way; block 9 must give b = 0.020193681800784184
    internalisation     killed at block 5 and relaunched this way; block 5 is its control
    Treatment First     CONVERGED at block 9, b = 0.032078509824432895 (checked:
                        0.3642% then 0.1104%), -60.51% against omega_c = 0.06.
                        Its 12-block rerun is HELD for the author, because the build
                        depends on whether TF is universal or entry-only (see below).

