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

## THE WALL: b and the ratio are in tension, and it is narrowing

Seventeen points now sit on the clean lambda/addiction_scalar_1 surface -- the
points differing from a named centre in those two coordinates and nothing else.
Laid out together they show why the drug block has never closed.

    lambda   as1        b        ratio (target 0.4135)
     21.4  0.017800    +13%       +48%
     20.0  0.018057     +5%       +41%
     18.3  0.018050    +10%       +26%
     18.3  0.018260     -4%       +30%
     18.3  0.018470    -36%       -26%
     15.0  0.017800    +80%       +10%
     12.0  0.017237   +220%        +5%
     21.4  0.018950    -72%        -3%

WHERE b IS RIGHT THE RATIO IS +26 TO +48 PER CENT; WHERE THE RATIO IS RIGHT b IS
OFF BY 70 TO 300. This is the same wall the search hit from a worse place -- 47
of 48 points with b near target had a ratio near 0.09 and one had 0.61 -- but it
has moved a long way, and the tension NARROWS as lambda falls: +48 per cent at
lambda 21.4, +30 at 18.3, +10 at 15.

## The fold, and why aimed steps keep missing here

addiction_scalar_1 does not have one elasticity, it has two regimes. At lambda
18.3, measured:

    0.018050 -> 0.018260   d ln b/d ln as1 = -11.9,  d ln lambda_d/d ln as1 =  -9.7
    0.018260 -> 0.018470   d ln b/d ln as1 = -35.2,  d ln lambda_d/d ln as1 = -84.8

A plateau, then a cliff. Across the plateau the ratio is flat (+26 to +30 per
cent) while b falls from +10 to -4; across the cliff the ratio collapses to -26.
Any step sized on the plateau elasticity and taken across the cliff overshoots by
a factor of three, which is what has happened repeatedly.

THE OPEN QUESTION, and `LAMBDA15.txt` is measuring it: does lambda 15 have the
same plateau-then-cliff shape? If it does, there is room to bring b down by 80
per cent while the ratio stays near +10, and the drug block closes. Three points
at addiction_scalar_1 0.01810, 0.01845 and 0.01880 locate the b crossing AND say
which regime it is in.

CAUTION ON LOCUS2.txt, already running. Its addiction_scalar_1 values came from a
locus slope fitted before the cliff was measured, so its three lines are expected
to land b near -11, -22 and -31 per cent rather than on target. Their ratios are
still information; the batch is not the closing bracket it was built to be.

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
- NEVER tell a worker to run its line through command substitution. A worker told
  to run `bash code/run_one_point.sh $(sed -n "1p" FILE ...)` stalls on a
  permission prompt and is lost silently; one sat blocked for forty minutes on
  the batch measuring lambda_m. Tell it to `cat -n` the file, read the line, and
  issue a separate Bash call whose command is that line verbatim.
