#!/usr/bin/env python3
"""Give b an SMI-specific value: b_smi_multiple.

    patch_b_smi.py <master .f90> <output .f90>

THE CHANNEL. Flow utility carries (b+q)^phi_q with phi_q = 0.27 and
u(X)=X^(1-sigma)/(1-sigma) at sigma = 2. The marginal value of the first unit
of the drug is proportional to 1/b, so a SMALLER b raises it and raises
participation. b_smi_multiple below one therefore makes SMI households more
likely to use, which is the margin the data says is missing: the model's use
ratio is 1.39 against 4.51.

    ratio below target -> LOWER b_smi_multiple
    ratio above target -> RAISE it

WHY IT READS THE INDEX RATHER THAN TAKING AN ARGUMENT, and what that costs.

The alternative is an smi argument on b_shifter (30 call sites), on
calculate_flow_utility (9) and on calculate_marginal_non_housing_utility (1).
Forty hand edits to a frozen model, each of which fails silently.

unemployment_index is module level, it appears in shared() in every OpenMP
clause and never in private(), and the parallel loop runs over the FINANCIAL
index -- so every thread sees the same, correct value. It is the household's
own state at every site that evaluates flow utility: calculate_childhood_utility
sets it with "do unemployment_index=1,unemployment_grid_size",
calculate_aggregate_consumption indexes its arrays by it at the call site, and
the other four routines inherit the caller's, all of which have it in scope.

THE COST IS REAL AND IS STATED HERE: b_shifter stops being a pure function of
its arguments, which its own comment valued. The SUD argument is still passed
explicitly, and as a LITERAL 0 or 1, because flow utility is evaluated under
both hypothetical addiction states. SMI is not varied that way -- the
household's SMI is its current state and next period's uncertainty lives in
the continuation value, not in flow utility -- so reading it is correct where
reading SUD would not be.

THE GATE. b_smi_multiple = 1 is arithmetically identical and proves nothing
about the index. The test that does is DIRECTIONAL: set it away from one and
check that SMI SUD moves hard while NON-SMI SUD barely moves. If both move,
the index is wrong and the channel is leaking into households it must not
touch.
"""
import sys

DECL_ANCHOR = "        real(8), parameter :: iota_smi=1.0\n"
DECL_NEW = DECL_ANCHOR + """
        ! b FOR HOUSEHOLDS WITH SMI, AS A MULTIPLE OF b.
        !
        ! Calibrated on sud_smi_ratio_data = 7.30, the SUD rate given SMI over
        ! the SUD rate given no SMI, NSDUH 2024 at 26 and over.
        !
        ! ONE at the declaration so the channel is off until it is asked for,
        ! and so the no-op control is the default rather than a thing to
        ! remember to set. It is settable through PARAM_HANDOVER.
        !
        ! WELL POSED ONLY BECAUSE SMI IS EXOGENOUS. With iota_smi above one,
        ! carrying a SUD raised the hazard of SMI onset, so an SMI-specific
        ! preference would have been a preference responding to the agent's own
        ! choices. iota_smi is one, so SMI is a pure age-Markov state and this
        ! is ordinary type heterogeneity in a Stone-Geary subsistence level.
        real(8) :: b_smi_multiple=1.d0
"""

BODY_ANCHOR = "            b_shifter=addiction_scalar_1\n"
BODY_NEW = """            ! SMI IS READ FROM THE STATE INDEX, NOT PASSED. See the header of
            ! patch_b_smi.py for why, and for what it costs: this function is no
            ! longer a pure function of its arguments. unemployment_index is
            ! module level, shared in every OpenMP clause, and is the
            ! household's own state wherever flow utility is evaluated.
            if (smi_of(unemployment_index)==1) then

                b_shifter=addiction_scalar_1*b_smi_multiple

            else

                b_shifter=addiction_scalar_1

            end if
"""

src = open(sys.argv[1]).read()
for anchor, new in ((DECL_ANCHOR, DECL_NEW), (BODY_ANCHOR, BODY_NEW)):
    n = src.count(anchor)
    if n != 1:
        sys.exit("REFUSED: anchor appears %d times, expected 1:\n%r" % (n, anchor))
    src = src.replace(anchor, new)

if "iota_smi=1.0" not in src:
    sys.exit("REFUSED: iota_smi is not 1; b_smi_multiple is only well posed with SMI exogenous")

open(sys.argv[2], "w").write(src)
print("added b_smi_multiple and made b_shifter read the SMI state")
