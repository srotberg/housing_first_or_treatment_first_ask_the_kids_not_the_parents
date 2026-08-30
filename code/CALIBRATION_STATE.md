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

## Where it stands, 30 August 12:20

BEST ON THE AUTHOR'S MINIMAX: `point_051d242e11`, worst gap 37 per cent on h_1,
and EVERY moment inside 37. Across the morning the worst went 164, 120, 82, 70,
68, 65, 37, and the gaps now cluster instead of having one outlier:

    h_1 -37, h_2 +35 (conceded), lambda_m -33, tau_u +31, kappa_uem +28,
    kappa_ued -28, theta +26, aleph -21, pi_eu +17, b -11, cbar -11,
    with ten moments already inside ten.

BEST WITH A CLEAN DRUG BLOCK: `point_7add914d47` -- b -7.5, lambda_d -1.7,
pi_eu +4.1, thirteen of twenty one inside ten per cent, worst 65 on kappa_uem.

point_051d242e11 is not admissible as a base, its b being -10.9 and the bound
ten. REPAIR3 runs from it to recover b, lambda_d and pi_eu without losing the 37.

## The drug block is closed and pi_eu is SOLVED

b and lambda_d were closed at lambda_addiction 15.89 with addiction_scalar_1
0.018367, by fitting BOTH surfaces on BOTH instruments over a band narrow enough
to be locally log-linear and checking the condition number before stepping. Every
earlier aimed step had chained an elasticity from one region into another and
missed by three to five times.

pi_eu bound every round after tau_u came down, was never better than +45 per cent
over ninety points, and this file once called it unexplained. The instrument was
never weak. probability_becoming_unemployed crosses its target near 0.0085 and
BOTH bracketing points were already in the archive; they were unusable only
because they carry b at +155 and +187 per cent. p_eu cannot move without taking
the drug block with it, so the answer was to move it and repair the block in the
same point, which is what the ladder and the secant did.

## The tools, and which to reach for

  `locus.py`      traces the b-on-target curve; right when the drug block is far
                  out, superseded by local 2-D fitting for stepping.
  `next_batch.py` the gate. Opens at five per cent on b and lambda_d, then picks
                  the best base within ten, emits one damped single-coordinate
                  arm per off-target moment, prefers a measured BRACKET to an
                  elasticity, compensates any arm that drags the drug block, and
                  adds a repair line when the base itself has drifted.
  `restore.py`    two-moment repair, b and lambda_d on the two drug instruments.
  `repair3.py`    THREE-moment repair, adding probability_becoming_unemployed and
                  pi_eu. Prefer this now: the kappa_uem arm took pi_eu from +4 to
                  +17 in one step, because two employment moments move together.
  `compensate.py` the gate's compensation, standalone, for hand-built batches.
  `joint_step.py` full least squares over everything. TRIED AND WORSE -- kept so
                  the negative result is not rediscovered.

## What still binds, and whether it has an instrument

    h_1       -37%  size_homelessness             overshot by a bracket, step back
    lambda_m  -33%  lambda_m                      FLOOR-BOUND, see below
    tau_u     +31%  utility_cost_of_treatment     bracketed [0.6031, 0.6308]
    kappa_uem +28%  kappa_uem                     elasticity -1.05, moves freely
    kappa_ued -28%  multiple_of_prob..._addicted  coupled, compensate
    theta     +26%  relative_share_of_addiction_1 coupled, compensate
    aleph     -21%  value_of_life                 coupled, compensate
    h_2       +35%  conceded by the author

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
