# `mu_m` DOES NOTHING IN THE STEADY STATE. MEASURED, THEN FOUND IN THE SOURCE

23 September, 02:05. The SUD recovery multiplier for SMI households is inert in
the benchmark, the calibration and every sweep point. It is wired into ONE
accounting routine and into neither the household's problem nor the stationary
distribution.

## THE MEASUREMENT CAME FIRST

A single frozen point, identical to the sweep's `b_smi_multiple = 1.0` point in
every respect except `mu_m`, which was compiled at 0.10 instead of 1.0 -- a
tenfold cut in the SMI recovery hazard, which should raise `SUD | SMI` hard:

                       mu_m = 1.0    mu_m = 0.10
    clean, non-SMI        0.9151        0.9151
    clean, SMI            0.8794        0.8794
    experimenter, SMI     0.0306        0.0306
    SUD, non-SMI          0.0506        0.0506
    SUD, SMI              0.0900        0.0900
    r_smi                 1.7792        1.7790

Identical in every cell to four decimals. The model is not bit reproducible and
a no-op control scores at 1e-4 relative; 1.7792 against 1.7790 is 1.3e-4, which
is the no-op, not a small effect.

## THE SOURCE SAYS WHY, AND IT WARNED ABOUT ITSELF

`mu_m` is applied in `recovery_with_smi`, called at 12790 inside
`addiction_transition` with `smi_used_1`, which is ZERO unless the OPTIONAL
eighth argument `smi_1` is supplied. The declaration at 12759 says so in as many
words:

    ! OPTIONAL so that the twelve existing call sites stay valid while
    ! they are wired one at a time. Absent means no SMI, which is what
    ! the model was before, so leaving a site unwired is a silent
    ! omission rather than a compile error. Every site that has the
    ! unemployment index in scope should pass smi_of(it).

Counting the arguments at every call site:

    line 19341  8 args  WIRED      govt_revenues_calc
    line 19388  8 args  WIRED      govt_revenues_calc
    line 19405  8 args  WIRED      govt_revenues_calc
    line 19424  8 args  WIRED      govt_revenues_calc
    line 26390  7 args  unwired    renter_to_renter_problem
    line 26460  7 args  unwired    renter_to_renter_problem
    line 26932  7 args  unwired    renter_to_renter_problem
    line 27505  7 args  unwired    renter_to_renter_problem
    line 27937  7 args  unwired    renter_to_renter_problem
    line 28323  7 args  unwired    renter_to_renter_problem
    line 31478  7 args  unwired    internal_computations
    line 32849  7 args  unwired    converge_to_stationary_equilibrium
    line 33276  7 args  unwired    converge_to_stationary_equilibrium
    line 33301  7 args  unwired    converge_to_stationary_equilibrium
    line 34176  7 args  unwired    converge_to_stationary_equilibrium

FOUR of sixteen, and all four are in the GOVERNMENT REVENUE accounting. The
household's value function does not see `mu_m`, and neither does the
distribution. It cannot move an equilibrium.

## WHAT THIS OVERTURNS

**`CALIBRATION_STATE.md` said "Removing `mu_m` cost most of the rise"** in the
comorbidity ratio, from 2.062 to about 1.7. It cannot have cost anything. That
inference came from a comparison that also switched two classes to one and set
`iota_smi` to one, and it attributed the whole move to the one parameter that
was incapable of producing any of it.

**"Put `mu_m` back to get the reach" is not an available option**, which is what
this point was run to test. It would need twelve call sites wired first, and
that is a model change and the author's.

**It is a live trap rather than a harmless one.** At `mu_m = 1.0` the multiplier
is one everywhere and nothing is wrong. The moment anyone sets it away from one,
the government's revenue calculation applies a recovery hazard that the
household's problem and the distribution do not -- an accounting identity
computed off a different transition matrix from the one the economy ran on.

## `iota_smi` IS FINE, AND WAS CHECKED BECAUSE OF THIS

CLAUDE.md's standing rule is that a bug found in one place is checked in the
other before it is closed. `smi_transition` has exactly ONE call site, at 37439,
passing all four arguments including `d_c_1` as `sud_1`, inside the loop that
BUILDS the SMI transition process every reader then looks up. That is the design
`addiction_transition` should have had: a table built once, not an optional
argument at sixteen sites.

## NOT FIXED HERE

No Fortran edited. Wiring twelve call sites changes the benchmark, the
calibration and every solved point, and the model is frozen.
