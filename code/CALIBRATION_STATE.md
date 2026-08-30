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

## Honest position, 30 August 02:20

NOT CONVERGING BY THE OLD METHOD. Over 110 points and twenty two hours the best
worst-gap went 78 -> 60 per cent, the best mean gap 16.8 -> 15.1, and the count
inside ten per cent 13 -> 14 of 20; the last twelve points moved none of them.
Dropping lambda_d, pi_eu and h_2 from the score ENTIRELY still leaves the best
point at a 35 per cent worst-gap, and the best points under different exclusions
are different vectors. There is no point close on everything.

The author approved returning to the joint solve they asked for at 23:00 on the
29th, which one-at-a-time bracketing had been substituting for.

## The current best point on the drug block

`point_2a2bebba51`: lambda_addiction 18.3, addiction_scalar_1 0.018260, rsa_1
0.5057, lambda_m 0.067. b -4.2 per cent, INSIDE the band for the first time in
the drug block, with lambda_d +24.2 and 11 of 21 moments inside ten per cent,
the best count on any single point.

Its worst gap is 168 per cent on tau_u, so on the strict minimax it is NOT the
best point -- `point_a310e2357f` still holds that at 60 per cent. What changed is
that the moment which was blocking is nearly solved: lambda_d was the worst
moment at 70 of 110 points.

## The locus, refitted on measured points

For each lambda there is one addiction_scalar_1 putting b on target; along that
curve lambda_d is a function of lambda alone, so the two-instrument solve is a
scalar root find. `locus.py` refits it from the archive -- it keeps only points
differing from a named centre in lambda_addiction and addiction_scalar_1 alone,
and interpolates between pairs that STRADDLE b = 0.089.

    lambda 18.3 -> as1 0.018260, lambda_d +24.2%   (MEASURED)
    lambda 11.8 -> as1 0.019059, lambda_d -47.7%   (interpolated)

    crossing at lambda 16.68, addiction_scalar_1 0.018459

`LOCUS.txt` line 5 is already queued at lambda 16.5, as1 0.018485, within a hair
of that. The ratio's elasticity in lambda, measured cleanly at fixed as1 from
21.4 to 18, is +0.93.

## What remains, and that it is reachable

Every moment still outside ten per cent has an instrument with a MEASURED
elasticity, and six have already spanned their target in controlled pairs.

    tau_u     +168%  utility_cost_of_treatment              e = -1.34, spanned
    pi_eu      +74%  probability_becoming_unemployed        e = +0.78, crosses near 0.013
    theta      +47%  relative_share_of_addiction_1          its true owner
    mu_H       +34%  mu_homeless                            e = -1.17, lands within 3.5%
    lambda_m   -31%  lambda_m                               NEVER MOVED in 114 points
    aleph      -29%  value_of_life                          e = +1.63, spanned
    kappa_ued  +28%  multiple_of_probabilities_..._addicted e = +0.86, spanned
    pi_V       -16%  probability_of_voucher_benchmark_used  e = +0.74, spanned

The author on 30 August 02:30: "it's ok, we can adjust the ones that are off
later" -- land b and lambda_d first, then correct the rest off the Jacobian.

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
