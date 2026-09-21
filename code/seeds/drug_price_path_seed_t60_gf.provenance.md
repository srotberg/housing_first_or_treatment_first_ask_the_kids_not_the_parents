# drug price path seed, T=60, GRANDFATHERED arm

A SHIFT of the shared construction, on ONE MEASURED number, as
results/transition_t60_gf/CONTROL.md required: the grandfathered price shift was
"to be MEASURED by that arm's T=5 probe and shifted on that, or not at all".

THE MEASUREMENT. Post-fix T=5 loop 0, both arms facing the same seeded price of
0.927387 at t=1:

    grandfathered   implied 1.019121   gap +0.091734
    control         implied 0.813246   gap -0.114141

A one-step Newton at the measured slope d(implied)/dp = -2.25 puts the roots at
0.955613 and 0.892267. So the grandfathered root is 3.0 per cent ABOVE the seed,
and 7.1 per cent above the control's root -- against the +6 per cent the
elasticity chain in CONTROL.md predicted, which was therefore accurate to about a
percentage point rather than the factor of two an earlier reading of this session
claimed by comparing it with the wrong quantity.

THE SHIFT. Every entry multiplied by 1 + 0.030*(1 - (t-1)/59), so +3.0 per cent at
t=1 tapering linearly to zero at t=60, where the boundary condition binds and the
code pins the final entry to arm 3's cleared price regardless.

WHAT IS MEASURED AND WHAT IS NOT. The t=1 shift is measured. The TAPER is not: it
is the simplest monotone path to a pinned endpoint, chosen because the exempt
cohort's demand must vanish as the cohort dies and a linear decay in t is the
least-committal way to say so. The underlying path it multiplies is itself a
construction past t=20 -- see drug_price_path_seed_t60.txt, whose entries 21 to 59
are a lambda_d-pinned geometric decay and not a measurement.

WHY SHIFT AT ALL RATHER THAN LET THE RUN WALK. max_drug_price_move caps the price
at 0.5 per cent a loop and is load bearing, so 3 per cent is six loops, and a
T=60 loop is about 7.5 hours. Starting 3 per cent closer strictly dominates as
long as the SIGN is right, and the sign is measured directly: the grandfathered
arm's implied price exceeds its faced price at t=1 by +0.0917.

DO NOT let the no-grandfathering arm read this file. A path built for an economy
with 7.1 per cent of the population exempt is the wrong seed for one where nobody
is, and as a column of numbers it is indistinguishable. That is the warning
drug_price_path_seed_t60_nogf.txt was pinned to protect against, and this is the
file it was protecting against.

NO COMMENT HEADER, DELIBERATELY. The drug-price reader is list-directed and
cannot skip '#', so a header makes the file unreadable and the run falls back to
the ramp in silence. See seeds/READ_ME_BEFORE_ADDING_A_HEADER.md.
