# LAMBDA AT LOW THETA -- the same hazard ladder at `relative_share_of_addiction_1 = 0.300`

`code/batch_lambda_at_low_theta.txt`, three lines, run one at a time from the
repository root, each allowed to finish before the next was started and each
committed before the next was fired. No `git pull` and no rebase was taken between
the lines. Borrowing is off throughout (`include_unsecured_borrowing=0`).

All three lines sit at `relative_share_of_addiction_1 = 0.300` and differ from one
another in `lambda_addiction` and nothing else.

| | `lambda_addiction` | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 (control) | 2.79953 | `729d412392` | `1b081ebc4d` | solved, 17 min |
| line 2 | 8.00000 | `9d84ecf295` | `1b081ebc4d` | solved, 16 min |
| line 3 | 20.00000 | `332bebd330` | `1b081ebc4d` | solved, 15 min |

Nothing segfaulted, no build failed, and
`code/housing_first_or_treatment_first_SR_v1.f90` was not edited at any point. All
three report `HANDOVER OK: 43 of 43 parameters applied` and `INVARIANTS: all PASS`,
16 of 16, with no `INVARIANT FAIL` line anywhere.

## The three MODEL lines agree

**All three points carry `MODEL 1b081ebc4d`, and they agree.** So does the working
tree: `md5sum code/housing_first_or_treatment_first_SR_v1.f90` cut to ten characters
is `1b081ebc4d`. The three lines are a matched set with each other on one source, in
one container, built by one `run_one_point.sh` invocation each.

Each `VECTOR` was diffed against line 1 coordinate by coordinate, all forty-four
names on both sides:

    line 2 vs line 1:  1 difference, lambda_addiction 2.79953 -> 8.00000
    line 3 vs line 1:  1 difference, lambda_addiction 2.79953 -> 20.00000

So each arm is a matched pair with the control in exactly this one instrument.

### The theta = 0.463 ladder is NOT on this source, and is quoted as indicative only

The order supplies the 0.463 readings and says to treat them as indicative because
they come from other containers. There is a second reason, and it is stronger: they
are also on a **different model source**. The archive ladder
(`35e8286c4e`, `2035b208bf`, `596012c614`, `9e225217bf`) carries `MODEL bb2cd48b81`
and the 8.00 rung `82a955b244` carries `MODEL b8dc1077ad`; this batch is on
`1b081ebc4d`. Two round-1 targets moved in between, and both are in the current
source:

| constant | archive source | this source |
|---|---|---|
| `unemployment_rate_data` (`pi_eu`) | 0.139 | **0.049** |
| `wealth_to_output_data` (`beta`) | 2.5 | **3.0** |

Those are target changes rather than model changes, but the source hash differs and
nothing in this batch re-measured the 0.463 vector here. **Every comparison inside
this file is within this container and this source; the only cross-source quantity
quoted anywhere is the 0.463 slope in section 1, and it is labelled indicative
there and used for one order-of-magnitude statement.**

## LEAD: the hypothesis holds, and line 3 lands `b` on its target

The order asks whether `lambda_addiction` bites harder once the weight on the
addiction good comes down. **It does, by about a factor of eight on the matched
interval, and the top of the ladder puts `b` on target.**

| `lambda_addiction` | tag | `b` | gap vs 0.089 |
|---|---|---|---|
| 2.79953 (control) | `729d412392` | 0.351593 | **+295.05%** |
| 8.00000 | `9d84ecf295` | 0.240576 | **+170.31%** |
| 20.00000 | `332bebd330` | **0.088738** | **-0.29%** |

`b` at `lambda_addiction = 20` is 0.088738 against a target of 0.089000. That is a
miss of 2.6e-04 in level, three orders of magnitude below the 0.263 that `b` travels
across this ladder, and it is the first reading of `b` anywhere in the drug block
that is not multiples of its target.

**This is a level statement about the measured rung, not a solve.** Nothing here
claims 20.00000 is the value that sets `b`; `theta` hits its sentinel at that rung
(section 3) and five round-1 moments are out there (section 4). What is measured is
that at `relative_share_of_addiction_1 = 0.300` the hazard is a live instrument on
`b` over the range 2.79953 to 20.00000, and that the target lies inside that range.

## 1. How much `lambda_addiction` moves `b`, at 0.300 against 0.463

As change in `b` per unit of `lambda_addiction`, over the intervals the endpoints
allow.

**At `theta = 0.300` -- my three points, one source, one container:**

| interval in `lambda_addiction` | change in `b` | width | **d b / d lambda** |
|---|---|---|---|
| 2.79953 -> 8.00000 | -0.111017 | 5.20047 | **-0.021348** |
| 8.00000 -> 20.00000 | -0.151838 | 12.00000 | **-0.012653** |
| 2.79953 -> 20.00000 (whole ladder) | -0.262855 | 17.20047 | **-0.015282** |

**At `theta = 0.463` -- from the archive, INDICATIVE, other containers and other
sources:**

| interval in `lambda_addiction` | change in `b` | width | d b / d lambda |
|---|---|---|---|
| 2.79953 -> 8.00000 | -0.013781 | 5.20047 | -0.002650 |
| 1.00000 -> 2.79953 | -0.046326 | 1.79953 | -0.025743 |
| 1.00000 -> 8.00000 | -0.060107 | 7.00000 | -0.008587 |

**The comparable interval is 2.79953 -> 8.00000, which both ladders contain.** On
it:

| | d b / d lambda | move in `b` |
|---|---|---|
| `theta` = 0.300 (this batch) | **-0.021348** | **0.111017** |
| `theta` = 0.463 (indicative) | -0.002650 | 0.013781 |
| ratio | **8.06 x** | **8.06 x** |

**The instrument is about eight times stronger at the lower weight on the same
interval.** The comparison is between one within-container ladder and one
cross-container, cross-source figure, so the factor of eight should be read as an
order of magnitude and not as eight to two decimal places. The within-container
half of it stands on its own without the 0.463 numbers at all: over 2.79953 ->
8.00000 the hazard moves `b` by 0.111, which is 31.6 per cent of `b`'s own level at
the control, and over the whole ladder it moves `b` by 0.263, which is 75 per cent
of it. That is not a feeble instrument on any reading.

The slope is not constant. It is steepest on the lower interval (-0.021348) and
flatter on the upper one (-0.012653), which is the expected shape for a hazard
`pi_d(v) = 1 - exp(-lambda*v)` flattening as `lambda*v` grows -- and section 5
reads it off the model's own printed rows. **No slope is claimed outside 2.79953 to
20.00000.**

## 2. Brackets

**`b` = 0.089: YES, a bracket, though a narrow one at the far side.**

    lambda 8.00000  ->  b = 0.240576   ABOVE 0.089000
    lambda 20.00000 ->  b = 0.088738   BELOW 0.089000

The pair (8.00000, 20.00000) brackets the target. The lower endpoint clears it by
only 2.6e-04, so 20.00000 is essentially on the target rather than comfortably past
it; the bracket is real but the crossing sits at or just under the top rung. This is
the first bracket on `b` found anywhere in the drug block -- the whole 0.463 ladder,
five rungs from 0.05 to 8.00, lies above the target with the closest reading a
factor of 4.4 away.

**`lambda_d` = 0.0368: NO. All three points lie above the target.**

| `lambda_addiction` | `lambda_d` | gap vs 0.0368 |
|---|---|---|
| 2.79953 | 0.186318 | **+406.30%** |
| 8.00000 | 0.158907 | **+331.81%** |
| 20.00000 | 0.076570 | **+108.07%** |

Monotone decreasing and moving toward the target throughout, closing from +406% to
+108%, but it does not cross. Nothing above 20.00000 is measured and no crossing
point is claimed.

**`theta` = 0.162: NO, and it cannot be read at the top rung.** See section 3.

## 3. Is `theta` readable at all three points?

**No. Two of three are readable; the top rung hits the sentinel.**

| `lambda_addiction` | `theta` | gap vs 0.162 |
|---|---|---|
| 2.79953 | 0.058505 | -63.89% |
| 8.00000 | 0.044251 | -72.68% |
| 20.00000 | **-1.000000 (SENTINEL)** | not a reading |

Two things follow, and they pull in opposite directions.

- **The two readable rungs are readable, and they sit BELOW the target.** This is
  the change the order was reaching for. At 0.463 the same moment read 0.169 to
  0.305 across the archive ladder, above 0.162 at every rung; at 0.300 it reads
  0.0585 and 0.0443, below 0.162 at both. `theta`'s own moment therefore has the
  target between the two weights, which the 0.463 ladder alone never showed.
- **The sentinel is back at 20.00000, one rung lower in `theta` than the order
  expected it.** The order chose 0.300 over 0.200 because 0.200 returns -1. It does
  not follow that 0.300 is safe: -1 is returned here at 0.300 as soon as
  `lambda_addiction` is pushed to 20.

What -1 means, from `weighted_drug_share_now` at line 6564: the moment is built from
an experimenter branch and an addict branch, each admitted only if its mass is
positive, its spending share is non-negative, and its group's total income exceeds
one tenth of average labour income times its mass. If neither branch is admitted the
function returns -1. At the top rung buyers are 1.32 per cent of clean households
against 20.31 per cent at the control, so a mass guard is the plausible binder --
but the printed incomes there (drug users at 0.505 of labour income, experimenters
at 0.515 of average) are five times the one-tenth floor, so **the income floor is
not what fires it.** Which of the remaining guards binds is not printed in the point
file and is not asserted here.

**So `b` is bracketed at exactly the rung where `theta` stops being measurable.**
Both facts are about the same point and neither should be quoted without the other.

## 4. Round 1, all nine moments, with a count inside ten per cent

`beta` is a BAND, 3.0 to 4.5; a point outside it is scored against the nearer edge
and counts as inside ten per cent if the shortfall is within ten per cent of that
edge. All three points are below the band, so all three are scored against the 3.0
floor. Percentages elsewhere are (model - target) / target. **Bold marks a moment
outside ten per cent.**

| moment | target | 2.79953 | 8.00000 | 20.00000 |
|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 78.979297 | 76.968848 | 73.198793 |
| `beta` wealth over output | BAND 3.0-4.5 | 2.205910 | 2.179070 | 1.983507 |
| `omega_l` labour supply / hours | 0.40 | 0.356670 | 0.355880 | 0.353252 |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 |
| `tau_l` average labour income tax | 0.224 | 0.227990 | 0.230599 | 0.240689 |
| `pi_eu` unemployment rate | 0.049 | 0.111351 | 0.107515 | 0.087507 |
| `pi_V` eligibles with a voucher | 0.266 | 0.258093 | 0.258351 | 0.251564 |
| `cbar` food stamps / income | 0.0042 | 0.003369 | 0.003255 | 0.002580 |
| `w_bot` net worth share, bottom half | 0.0250 | 0.021822 | 0.018974 | 0.013405 |

and the same as gaps:

| moment | 2.79953 | 8.00000 | 20.00000 |
|---|---|---|---|
| `aleph` | -1.28% | -3.79% | -8.50% |
| `beta` | **OUT -26.47%** | **OUT -27.36%** | **OUT -33.88%** |
| `omega_l` | **-10.83%** | **-11.03%** | **-11.69%** |
| `sigma_y` | -1.72% | -1.72% | -1.72% |
| `tau_l` | +1.78% | +2.95% | +7.45% |
| `pi_eu` | **+127.25%** | **+119.42%** | **+78.59%** |
| `pi_V` | -2.97% | -2.88% | -5.43% |
| `cbar` | **-19.79%** | **-22.49%** | **-38.57%** |
| `w_bot` | **-12.71%** | **-24.10%** | **-46.38%** |

**Inside ten per cent, out of nine:**

| point | `lambda_addiction` | count | out |
|---|---|---|---|
| `729d412392` | 2.79953 | **4 of 9** | `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |
| `9d84ecf295` | 8.00000 | **4 of 9** | `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |
| `332bebd330` | 20.00000 | **4 of 9** | `beta`, `omega_l`, `pi_eu`, `cbar`, `w_bot` |

**Four of nine at every rung, and the SAME five moments out at every rung.** That
matters for reading the table: the round-1 damage here is not something
`lambda_addiction` did.

- **The control is already 4 of 9 before any arm is taken.** The control differs
  from the archive base only in `relative_share_of_addiction_1` (0.463 -> 0.300),
  and it is scored against two targets that moved after the archive ladder was
  measured -- `pi_eu` from 0.139 to 0.049 and `beta` from 2.5 to 3.0. `pi_eu` at
  +127.25% and `beta` at -26.47% are the two largest misses in the table and both
  are of that kind: this vector still carries
  `probability_becoming_unemployed=0.0122`, which was tuned to 0.139. **Whatever is
  wrong at the control is wrong before `lambda_addiction` is touched at all**, and
  attributing it to the arms would be a misreading.
- **Three moments do worsen monotonically with the instrument**: `w_bot` -12.71% ->
  **-46.38%**, `cbar` -19.79% -> **-38.57%**, and `aleph` -1.28% -> -8.50%. `aleph`
  is the only one of the three that stays inside ten per cent across the whole
  ladder, and at 20.00000 it is 1.5 points from the edge.
- **`pi_eu` IMPROVES with the instrument**, +127.25% -> +78.59%, because raising the
  hazard shrinks the drug-using population and unemployment falls with it. It is far
  outside ten per cent at every rung regardless.
- **`sigma_y` is identical to all sixteen digits at all three points.** This
  instrument does not touch it, as on the 0.463 ladder;
  `TARGET_CHANGE_CHECK.md` records that it is frozen by
  `freeze_sd_permanent_productivity`.
- **`omega_l` is marginal everywhere**, -10.83% to -11.69%, never more than 1.7
  points outside the edge and moving by 0.9 points across the whole ladder.

`h_1`, round 1's tenth moment, is far out at all three and improves slightly with
the instrument: 0.030749 (2.79953), 0.030012 (8.00), 0.028292 (20.00), against a
target of 0.00399.

## 5. Why it bites harder here, from the model's own printed rows

Not an argument, a reading of the diagnostics. The mechanism is the same extensive
margin the 0.463 ladder showed, but it has much further to travel at the lower
weight.

| `lambda_addiction` | onset at the mean quantity | mean drug quantity, users | buyers as a share of clean households | carriers consuming no drugs |
|---|---|---|---|---|
| 2.79953 | 0.143090 | 0.055160 | 0.203120 | 0.051065 |
| 8.00000 | 0.387892 | 0.061356 | 0.097099 | 0.040248 |
| 20.00000 | 0.644241 | 0.051675 | 0.013177 | 0.014312 |

Onset at the mean quantity rises 4.5-fold across the ladder and the share of clean
households that buy falls by a factor of **15.4**, from 20.3 per cent to 1.3 per
cent. `b` counts users, so that extensive collapse is the whole of the movement in
`b`. Mean quantity among users barely moves -- 0.0552, 0.0614, 0.0517, non-monotone,
and each within 11.2 per cent of the control's 0.055160 -- so the intensive
offset the drug block was once expected to show is again small and again swamped.

The contrast with 0.463 is in the starting quantity, and it is what makes the hazard
strong here. `pi_d(v) = 1 - exp(-lambda*v)` acts on the product `lambda*v`. At the
control here the mean quantity is 0.055160, less than half the 0.114511 the archive
base carries at 0.463, so at equal `lambda` the exponent is less than half as large
and the hazard sits far lower on its own curve -- 0.143090 here against 0.274269
there. Low on the curve is where the exponential is steep. Raising `lambda` at 0.463
was pushing on an onset probability already at 0.27 and flattening; raising it at
0.300 starts at 0.14, on the part of the curve that still has slope. **The order's
reading of why the instrument was weak is borne out: it was weak because `theta` put
agents high on a flattening hazard, and lowering `theta` puts them back where the
hazard has bite.**

The buyer threshold `(phi/theta)*p*b` is **0.075600 at all three rungs, identical to
sixteen digits**, as it must be -- it is four parameters and none of them is
`lambda_addiction`. It is twice the 0.037578 the archive base carries, which is the
direct effect of halving-ish the weight, and it is the same at all three of my
points, so it plays no part in the movement reported here.

## What this leaves

Stated as what was measured, not as a plan.

- **`lambda_addiction` is not a weak instrument at any `theta`.** It is weak at
  `theta` = 0.463 and strong at `theta` = 0.300, about eight times stronger on the
  matched interval. The drug block has two working levers over this range, not one.
  The finding the order was prepared to accept -- feeble at the lower weight too --
  is not what the measurement shows.
- **`b` = 0.089 is bracketed for the first time**, by (8.00000, 20.00000), with
  20.00000 reading 0.088738, essentially on target.
- **`lambda_d` = 0.0368 is not bracketed.** All three points are above it, closing
  from +406% to +108% but not crossing.
- **`theta` = 0.162 is not bracketed and is not readable at the top rung.** It reads
  below target at the two rungs where it reads at all, and returns the sentinel -1 at
  20.00000. The order's premise that 0.300 escapes the sentinel holds only at
  moderate `lambda_addiction`.
- **Round 1 is 4 of 9 at every rung, the same five moments out at each**, and the
  two worst misses (`pi_eu`, `beta`) are already there at the control, against
  targets that moved after this vector was tuned. Three moments worsen with the
  instrument: `w_bot`, `cbar` and `aleph`.

## What was not done

No extrapolation past the measured rungs. No value of `lambda_addiction` between,
below or above 2.79953, 8.00000 and 20.00000 is estimated, and no crossing point is
claimed for `b`, `lambda_d` or `theta` -- the `b` bracket is stated as the pair of
measured rungs that straddles the target, not as a solved value. The `theta` = 0.463
ladder was not re-run on this source; its slope is quoted once, labelled indicative,
and no conclusion in this file rests on it alone. `relative_share_of_addiction_1` =
0.200 was not measured. `code/housing_first_or_treatment_first_SR_v1.f90` was not
edited.
