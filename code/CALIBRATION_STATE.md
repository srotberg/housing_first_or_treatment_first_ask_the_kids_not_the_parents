# Where the calibration is

Rewritten whenever a point changes the picture. The hourly engine trigger reads
this rather than carrying the state in its own prompt, because the prompt went
stale three times in one evening and a stale prompt sends the search backwards.

## The objective

The author's ten per cent rule: EVERY target within ten per cent. They conceded
the model is hard to calibrate and will say so in the paper. That is a MINIMAX,
not a mean -- `score_points.worst()` with `ACCEPT = 0.10`. The mean is what once
led the search to a point with b exact and lambda_d at minus seventy eight.

`beta` is banded (3.0, 4.5) on the author's instruction and scores zero inside
it. `h_2`, the smallest-rental share, is conceded and need not be chased.

## THE DRUG BLOCK IS CLOSED, 30 August 03:50

`point_1855f8103d`: lambda_addiction 15.89, addiction_scalar_1 0.018367, rsa_1
0.5057, lambda_m 0.067. **b +1.4 per cent, lambda_d +2.7** -- both inside the
author's five per cent gate. 11 of 21 moments inside ten per cent.

WHAT FINALLY WORKED, because it is the method to keep using. Every aimed step
before this missed by factors of three to five, and all of them chained an
elasticity measured in one region into another. This one fitted BOTH surfaces on
BOTH instruments at once, over a band narrow enough to be locally log-linear --
eight points with lambda between 16 and 18.5 --

    ln b        : d/d ln lambda = -1.43,  d/d ln as1 = -15.4,  rms resid 0.068
    ln lambda_d : d/d ln lambda = -0.99,  d/d ln as1 = -20.3,  rms resid 0.216

solved the two together, and checked the condition number (47) so the
instruments were known not to be collinear BEFORE the step was taken. It
predicted both moments on target; the model returned +1.4 and +2.7. First time
all night a prediction and a measurement agreed.

The earlier one-dimensional locus construction got the search into this band and
was worth it, but it is superseded: fit locally in two dimensions, do not chain
slopes.

`next_batch.py` opened on its own and spawned nine correction arms from this
point. That gate stays the right shape for any future re-solve.

## The SMI block needs a decision, not more search

lambda_m (the SMI share of the homeless) is at -54 per cent and is the first
moment that looks genuinely OUT OF REACH through its own instrument. The
parameter needs to fall to 0.035 to close the gap; its floor is 0.046. The
damped step lands on the floor.

Worse, the parameter moves BOTH SMI moments the same way -- 0.067 to 0.12 took
the share of the homeless 0.154 to 0.105 AND the population share 0.045 to 0.028
-- so pulling it down to lift the first will push the second, currently inside
ten per cent at -8, out of it. smi_onset_level is now listed as the second
instrument and owns the population share, which lets the next round repair what
this one costs instead of oscillating. But if the share of the homeless is still
far out after this round, it is a question for the author -- a floor to move or a
target to concede -- and not something more points will solve.

## What remains, and how each moment has to be reached

The first correction round measured a single-coordinate arm for all nine
remaining instruments at base point_1855f8103d. Eight of nine moved their own
moment toward target. Four moments crossed into the band, and pi_eu -- recorded
all night as the unexplained blocker, never better than +45 per cent over ninety
points -- moved twenty five points in one step.

The arms also say what each instrument does to b and lambda_d, which are
finished and must stay that way. THAT is what decides how each moment is
reached:

    moment     now    instrument                       effect on b / lambda_d
    ------------------------------------------------------------------------
    h_1       +11%    size_homelessness                 +2  /  +0    move freely
    mu_H      +10%    mu_homeless                       +2  /  +5    move freely
    tau_u    +120%    utility_cost_of_treatment         -4  /  -7    move freely
    pi_V       -5%    probability_of_voucher...          0  /  +2    in band
    lambda_m  -53%    lambda_m                          -3  /  -8    FLOOR-BOUND
    kappa_ued +10%    multiple_of_prob..._addicted     +42  / +61    needs repair
    pi_eu     +45%    probability_becoming_unemployed  +44  / +64    needs repair
    theta     +52%    relative_share_of_addiction_1    -74  / -83    needs repair
    aleph     -10%    value_of_life                    -85  / -91    needs repair

THE NESTED LOOP FOR A COUPLED INSTRUMENT. Step it SMALL, run `restore.py <tag>`
to get the lambda_addiction and addiction_scalar_1 that put b and lambda_d back,
measure, repeat. Small is not timidity: the fit that closed the drug block is
local and log-linear over lambda 16 to 19 and cannot undo an 85 per cent move in
b, so keep b inside roughly twenty per cent per step, where the repair has been
verified. restore.py refits from the archive every call because the same
elasticity reads -12 and -35 a few thousandths of addiction_scalar_1 apart.

A JOINT LEAST SQUARES OVER ALL NINE IS WORSE AND HAS BEEN TRIED. joint_step.py
solves the full measured 11-by-9 Jacobian with b and lambda_d weighted twelvefold
to protect them. Its own predictions are inferior to the individual arms almost
everywhere -- aleph -29 to -31 per cent where the arm alone reached -10, mu_H +36
to +33 where the arm reached +10 -- and it still pushes lambda_d to +14. The
condition number is 617; the solve spends its freedom on the hardest moments and
degrades the easy ones. Do not re-run it expecting a different answer.

## pi_eu IS REACHABLE, and this is the route

It bound at every step once tau_u came down -- the worst gap went 164, 120, 82,
70, 69, 68 per cent with pi_eu binding throughout -- and it was recorded all
night as unexplained. It is not.

Across 179 points, probability_becoming_unemployed at 0.006 gives pi_eu -17 per
cent and at 0.010 gives +14, so THE CROSSING SITS NEAR 0.0085. What hid this is
that both of those points carry b at +187 and +155 per cent: p_eu drags the drug
block with it, so every earlier attempt either left pi_eu alone or destroyed b.

The compensated path works and is measured. point_7ec662e9d1 sits at p_eu
0.019140 with b -4 per cent, lambda_d +7 and pi_eu +53 -- instrument moved, drug
block held. The first ladder rung then took p_eu to 0.017 and pi_eu to +44, a
gain of twenty four points in one step, at the cost of b +23 and lambda_d +27
because the compensation is halved while the base's own slice is too thin to fit.

So the remaining work on pi_eu is arithmetic, not discovery: walk p_eu from
0.0228 down towards 0.0085 in compensated steps, repairing the drug block after
each. PEU_LADDER.txt runs the rungs in parallel rather than one per round, since
they do not depend on each other.

## The one thing that needs the author, not more search

relative_share_of_addiction_1 is contested. theta needs it UP (elasticity -4.64,
re-measured on this round's own pair). The SMI share of the homeless needs it
DOWN: that arm moved the moment +108 per cent, which would carry it from -54 to
about -4, essentially on target. Its own parameter lambda_m cannot do the job --
elasticity -0.08, and the step it wants lands on the floor of 0.046.

So one parameter is the only effective instrument for two moments that want
opposite directions, and it is also violently coupled into the drug block. The
options are the author's: concede one of the two moments, move lambda_m's floor,
or add an instrument to the SMI block. More points will not resolve it.

## Rules that came out of specific mistakes

BUILD THE NEXT STEP FROM MEASURED CROSSINGS, NOT FROM A LOCAL ELASTICITY. The
addiction_scalar_1 elasticity of b is about -26 at the centre's neighbours and
-14 across the wider grid; the local number carried to lambda 11.8 predicts
b = 0.060 where the model returns 0.138. Interpolate between straddling points;
never extrapolate a slope past the pair that produced it.

BRACKET, DO NOT AIM. A one per cent error in addiction_scalar_1 is a twenty per
cent error in b. Every new lambda gets a THREE-POINT bracket. When two estimates
disagree, widen rather than average. Every wide bracket has worked and four
aimed steps have missed, by factors of 4, 5, 3.2 and 2.3.

RELATIVE_SHARE_OF_ADDICTION_1 IS THETA'S INSTRUMENT AND NOTHING ELSE'S. The
Fortran adjusts it against `drug_share_weighted_1 - drug_spending_share_data`
and clamps it between `theta_lo` and `theta_hi`. The search had been using it to
reach the disorder ratio, where it is violent -- 0.45 to 0.51 multiplies b by
5.7 and lambda_d by 18.6 -- and it takes the SMI share of the homeless from
0.256 to 0.085 on the way, because it floods the homeless with drug users. That
is the mechanism behind the flat loss: every gain on the ratio was paid for in
theta and lambda_m. The ratio belongs to lambda_addiction, b to
addiction_scalar_1, theta to this.

CHECK WHICH LINES LANDED, NOT HOW MANY. A count hides a worker stalled on a
permission prompt; two hours went that way. Compare vectors in `points/` against
the batch file line by line and respawn the specific lines missing.

REPORT MOMENTS WITHIN TEN PER CENT AT ONE POINT. "Nineteen of twenty one have
been inside ten per cent" is each moment at its own best point, is not a result,
and the author challenged it directly.

THE UNEMPLOYMENT TYPO WAS INERT. `probability_becoming_employed1` was real and
undeclared, but line 24028 overwrites the slice eighty five lines later. Every
point stands. Do not re-litigate it.

PREFERENCES ARE CONSTANT ACROSS STATES and `recompute_derived_parameters` now
asserts it. The author asked; the model was already correct, but the diagnostic
printed `_1` under the `_2` label and would have hidden a divergence.

## Standing operational rules

- Every point runs through `run_one_point.sh`, cold, with the HANDOVER assertion.
- NO supervisor beside measurements, ever; test positionally, not with pgrep -f.
- `points_pregrid/` is history from the savings-grid bug. Never score or seed it.
- Re-measuring a vector on a changed model reproduces its md5 tag and would
  overwrite a real measurement. Move `points/` aside first and verify it back.
- A scope change -- opening an externally assigned parameter, moving a target --
  is the author's call. Fixing an outright bug is not, but say what it
  invalidates and MEASURE before believing it.
- NEVER tell a worker to run its line through command substitution. A worker told
  to run `bash code/run_one_point.sh $(sed -n "1p" FILE ...)` stalls on a
  permission prompt and is lost silently; one sat blocked for forty minutes on
  the batch measuring lambda_m. Tell it to `cat -n` the file, read the line, and
  issue a separate Bash call whose command is that line verbatim.
