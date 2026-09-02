# ROUND 2 C -- `addiction_scalar_1` taken UP, two points, off `35e8286c4e`

`code/batch_round2_c.txt`, two lines, run one at a time from the repository root,
each allowed to finish before the next was started and the first committed before
the second was fired. No rebase was taken between the lines. Borrowing is off
throughout (`include_unsecured_borrowing=0`).

The base is the round-1 point `35e8286c4e`. Each line moves ONE coordinate off it
and nothing else.

| | instrument move | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | `addiction_scalar_1` 0.0360 -> **0.1000** | `72b5b308cf` | `b8dc1077ad` | solved, 11 min |
| line 2 | `addiction_scalar_1` 0.0360 -> **0.2500** | `42a4e0966f` | `b8dc1077ad` | solved, 10 min |

## LEAD: both arms break round 1, and worse than the 0.0120 arm did

The order asked to be told first if either arm did what the 0.0120 arm did, which
was to take round 1 from eight of nine to four of nine. **Both do, and both go
further.**

| point | `addiction_scalar_1` | round 1, inside ten per cent |
|---|---|---|
| `7771720a08` | 0.0120 | 4 of 9 |
| `35e8286c4e` (base) | 0.0360 | **8 of 9** |
| `72b5b308cf` | 0.1000 | **3 of 9** |
| `42a4e0966f` | 0.2500 | **2 of 9** |

`aleph` is the moment the order named, and it breaks in the opposite direction
from the 0.0120 arm: down there, **up** here.

| point | `aleph` | gap |
|---|---|---|
| 0.0120 | 43.464472 | **-45.67%** |
| 0.0360 (base) | 75.828008 | -5.21% |
| 0.1000 | 110.076351 | **+37.60%** |
| 0.2500 | 145.756728 | **+82.20%** |

`value_of_life` is untouched at 42.0 at all four points. `aleph` is monotone
increasing in `addiction_scalar_1` across the whole ladder and passes through its
target somewhere between 0.0120 and 0.1000; the base at 0.0360 is the only one of
the four inside ten per cent of it.

**Neither arm is usable as it stands.** Both leave the round-1 block in worse
shape than the arm already rejected.

## The MODEL lines agree, and that was checked rather than assumed

**Both points carry `MODEL b8dc1077ad`.** So does the base `35e8286c4e`, and so
does the working tree: `md5sum code/housing_first_or_treatment_first_SR_v1.f90`
cut to ten characters is `b8dc1077ad`. So does `7771720a08`, the 0.0120 arm quoted
alongside them. All four readings below are within-economy comparisons against a
base measured on the same source.

`code/housing_first_or_treatment_first_SR_v1.f90` was not edited at any point in
this batch. No source change landed mid-batch, no build failed and nothing
segfaulted. Both points report `HANDOVER OK: 42 of 42 parameters applied` and
`INVARIANTS: all PASS`, 16 of 16, with no `INVARIANT FAIL` line in either.

Each `VECTOR` was diffed against the base coordinate by coordinate, all
forty-three names on both sides:

    line 1 vs base:  1 difference, addiction_scalar_1 0.0360 -> 0.1000
    line 2 vs base:  1 difference, addiction_scalar_1 0.0360 -> 0.2500

So each line is a matched pair with the base in exactly its own instrument.

## The ladder: `lambda_d`, the moment `addiction_scalar_1` owns

Target 0.0368. Gaps are (model - target) / target.

| `addiction_scalar_1` | tag | `lambda_d` | gap | side of target |
|---|---|---|---|---|
| 0.0120 | `7771720a08` | 0.410701 | **+1016.03%** | above |
| 0.0360 (base) | `35e8286c4e` | 0.294785 | **+701.05%** | above |
| **0.1000** | `72b5b308cf` | **0.122914** | **+234.00%** | above |
| **0.2500** | `42a4e0966f` | **0.000000** | **-100.00%** | **below** |

**A measured pair now BRACKETS 0.0368: 0.1000 and 0.2500.** `lambda_d` is
0.122914 at 0.1000 and 0.000000 at 0.2500, so the target lies strictly between
two points that differ in one coordinate.

`lambda_d` is monotone DECREASING in `addiction_scalar_1` over the whole ladder,
which is the direction the Stone-Geary reading gives and the reverse of the
direction the 0.0120 arm was aimed in. That much is now confirmed on four points
rather than two.

### The bracket's lower end is a corner, not an interior point

**At 0.2500 the drug block is extinguished, not merely small.** This has to be
stated next to the bracket, because a bracket whose lower end is a corner is not
the same object as a bracket between two interior points.

At `42a4e0966f`:

    MOMENT b        total drug users            = 0.000000   target 0.089
    MOMENT lambda_d disorder rate               = 0.000000   target 0.0368
    MOMENT theta    drug spending share         = -1.000000  target 0.162
    MOMENT y_u      income of drug users        = 0.000000
    MOMENT kappa_ued unemployment given SUD     = 0.000000
    MOMENT mu_H     recovery housed / homeless  = 0.000000
    DIAG users band 1..5, use rate              = 0.000000 at every band
    DIAG mean drug quantity, users              = 0.000000
    UNTARGETED drug deaths, share of deaths     = 0.000000   observed 0.20
    DIAG carriers of the disorder consuming no drugs = NaN

Nobody uses at any income band. `-1` in the `theta` row is the sentinel
`weighted_drug_share_now()` returns when neither the experimenter branch nor the
addict branch is valid (line 6505 onward); it is **not** a measured spending share
and must not be read as a number. The `NaN` is a 0/0 in a diagnostic ratio over
an empty mass. The invariants still pass because they check identities, and every
identity holds trivially at zero.

So `lambda_d` = 0 at 0.2500 is the value at the boundary of the region where the
instrument admits any drug use at all, not a point on a smooth interior curve.
The bracket is arithmetically real and it is the first one this instrument has
produced; what it is a bracket *on* is the interval between the last measured
interior point and the corner.

## `theta` moves at least as hard as `lambda_d`, so the two cannot be set one at a time

The order asked this to be quantified, because `addiction_scalar_1` and
`relative_share_of_addiction_1` both enter the drug threshold
`(phi/theta)*p*b` at line 5493.

### `theta` at each point, target 0.162

| `addiction_scalar_1` | `theta` | gap | side of target |
|---|---|---|---|
| 0.0120 | 0.213803 | +31.98% | above |
| 0.0360 (base) | 0.304601 | +88.03% | above |
| **0.1000** | **0.120853** | **-25.40%** | **below** |
| **0.2500** | -1.000000 | sentinel, undefined | no users |

**`theta` also brackets its target, on 0.0360 and 0.1000**, and it does so on a
pair of interior points rather than against a corner. That is a stronger bracket
than the one on `lambda_d`.

### The threshold is exactly linear in the instrument

`DIAG drug threshold, (phi/theta)*p*b` at the four points:

| `addiction_scalar_1` | threshold | threshold / instrument |
|---|---|---|
| 0.0120 | 0.012526 | 1.043844 |
| 0.0360 | 0.037578 | 1.043844 |
| 0.1000 | 0.104384 | 1.043844 |
| 0.2500 | 0.260961 | 1.043844 |

The ratio is constant to six digits, as it must be: the other two factors in
`(phi/theta)*p*b` are held fixed across the ladder. The threshold is a strictly
proportional read-out of the instrument, so a 6.9-fold move in
`addiction_scalar_1` is a 6.9-fold move in the price-relevant threshold.

### The elasticities, on the segment that is interior at both ends

Log elasticities with respect to `addiction_scalar_1`, computed segment by
segment. The last segment is not computable in logs because both moments reach
zero (or the sentinel) at its right end.

| segment | d ln instrument | `lambda_d` elasticity | `theta` elasticity | ratio abs(theta)/abs(lambda_d) |
|---|---|---|---|---|
| 0.0120 -> 0.0360 | +1.0986 | **-0.302** | **+0.322** | 1.07 |
| **0.0360 -> 0.1000** | +1.0217 | **-0.856** | **-0.905** | **1.06** |
| 0.1000 -> 0.2500 | +0.9163 | not computable (0) | not computable (sentinel) | -- |

**On the segment that contains both of my measured interior points, the
instrument moves `theta` slightly HARDER than it moves the moment it owns:
-0.905 against -0.856.** The ratio is 1.06. There is no sense in which
`addiction_scalar_1` is a `lambda_d` instrument that happens to touch `theta`; it
is, locally, an equally strong instrument for both.

Note that the two moments do not even keep the same relative sign across the
ladder. On 0.0120 -> 0.0360 they move in OPPOSITE directions (`lambda_d` down,
`theta` up); on 0.0360 -> 0.1000 they move together, both down. So the sign
structure is local, and it turns somewhere inside the 0.0120-0.1000 span.

### Against the other instrument in the pair

Round 2 arm 3 (`e7c7daf5ca`) moved `relative_share_of_addiction_1` 0.463 -> 0.400
off the same base, so its elasticities are directly comparable:

| | d ln `lambda_d` | d ln `theta` | ratio abs(theta)/abs(lambda_d) |
|---|---|---|---|
| `addiction_scalar_1` (0.0360 -> 0.1000) | **-0.856** | **-0.905** | **1.06** |
| `relative_share_of_addiction_1` (0.463 -> 0.400) | +0.616 | +1.627 | 2.64 |

The 2x2 log Jacobian, rows instruments, columns moments, has determinant
**-0.835**. It is non-singular, so the pair is not degenerate: the two moments
are in principle jointly reachable by moving the two instruments together.

But neither row is close to diagonal. `relative_share_of_addiction_1` is the more
`theta`-loaded of the two (ratio 2.64), and `addiction_scalar_1` is very nearly
balanced (1.06). Both instruments move both moments, and both move them in the
SAME direction as each other within each instrument -- raising
`addiction_scalar_1` lowers both, raising `relative_share_of_addiction_1` raises
both.

**Answer to the question the order posed: they must be set TOGETHER, not one at a
time.** Setting `addiction_scalar_1` on `lambda_d` alone and then
`relative_share_of_addiction_1` on `theta` alone would have the first step move
`theta` by more than it moves `lambda_d`, and the second step move `lambda_d` back
by 0.62 for every unit it moves `theta`. A sequential search on this pair does not
converge on this evidence; a joint two-by-two solve is what the Jacobian supports.

The determinant and the elasticities above are LOCAL, measured on the
0.0360 -> 0.1000 and 0.463 -> 0.400 segments respectively. They are not claimed
to hold anywhere else on the ladder, and the sign turn noted above is a direct
demonstration that they do not.

## Round 1's nine moments at each point

Levels. `beta` is a BAND, 3.0 to 4.5.

| moment | target | 0.0120 | 0.0360 (base) | **0.1000** | **0.2500** |
|---|---|---|---|---|---|
| `aleph` value of life / income | 80.0 | 43.464472 | 75.828008 | 110.076351 | 145.756728 |
| `beta` wealth over output | BAND 3.0-4.5 | 2.513934 | 2.452826 | 1.946905 | 1.543983 |
| `omega_l` labour supply / hours | 0.40 | 0.405819 | 0.363505 | 0.292851 | 0.229050 |
| `sigma_y` bottom half earnings share | 0.172 | 0.169050 | 0.169050 | 0.169050 | 0.169050 |
| `tau_l` average labour income tax | 0.224 | 0.231784 | 0.226321 | 0.225854 | 0.236425 |
| `pi_eu` unemployment rate | 0.139 | 0.154858 | 0.134279 | 0.098913 | 0.067727 |
| `pi_V` eligibles with a voucher | 0.266 | 0.228969 | 0.255978 | 0.313040 | 0.322117 |
| `cbar` food stamps / income | 0.0042 | 0.003953 | 0.003935 | 0.004195 | 0.004716 |
| `w_bot` net worth share, bottom half | 0.0250 | 0.027980 | 0.024270 | 0.013102 | 0.013231 |

and the same as gaps. `beta`'s shortfall is quoted against the 3.0 floor. **Bold
marks a moment outside ten per cent.**

| moment | 0.0120 | 0.0360 (base) | **0.1000** | **0.2500** |
|---|---|---|---|---|
| `aleph` | **-45.67%** | -5.21% | **+37.60%** | **+82.20%** |
| `beta` | **OUT -0.4861** | **OUT -0.5472** | **OUT -1.0531** | **OUT -1.4560** |
| `omega_l` | +1.45% | -9.12% | **-26.79%** | **-42.74%** |
| `sigma_y` | -1.72% | -1.72% | -1.72% | -1.72% |
| `tau_l` | +3.48% | +1.04% | +0.83% | +5.55% |
| `pi_eu` | **+11.41%** | -3.40% | **-28.84%** | **-51.28%** |
| `pi_V` | **-13.92%** | -3.77% | **+17.68%** | **+21.10%** |
| `cbar` | -5.87% | -6.31% | -0.13% | **+12.28%** |
| `w_bot` | **+11.92%** | -2.92% | **-47.59%** | **-47.07%** |

**Inside ten per cent, out of nine:**

| point | `addiction_scalar_1` | count | out |
|---|---|---|---|
| `7771720a08` | 0.0120 | 4 of 9 | `aleph`, `beta`, `pi_eu`, `pi_V`, `w_bot` |
| `35e8286c4e` (base) | 0.0360 | **8 of 9** | `beta` |
| `72b5b308cf` | **0.1000** | **3 of 9** | `aleph`, `beta`, `omega_l`, `pi_eu`, `pi_V`, `w_bot` |
| `42a4e0966f` | **0.2500** | **2 of 9** | `aleph`, `beta`, `omega_l`, `pi_eu`, `pi_V`, `cbar`, `w_bot` |

### What each arm costs

**0.1000 loses five of the eight the base held**: `aleph`, `omega_l`, `pi_eu`,
`pi_V` and `w_bot`. `w_bot` is the worst single reading, -47.59%, nearly halving
the bottom-half net worth share from an already-short base. `omega_l` was at
-9.12% at the base with very little room and falls straight through to -26.79%.
The one improvement is `cbar`, which lands at -0.13%, the best reading of that
moment on the ladder.

**0.2500 loses six of the eight**, adding `cbar` to that list at +12.28%. It is
the worst point of the four on `beta` (1.543983, 1.4560 below the floor), on
`omega_l` (-42.74%), on `pi_eu` (-51.28%), on `pi_V` (+21.10%) and on `aleph`
(+82.20%).

`beta` is out at all four points and is the round-1 moment already open at the
base. **`beta` degrades monotonically as `addiction_scalar_1` rises**: 2.513934,
2.452826, 1.946905, 1.543983. The instrument moves the one open round-1 moment
steadily further from its band.

`sigma_y` is identical to all sixteen digits at all four points, as it was across
the earlier round-2 arms. No drug-block instrument touches it.

`h_1`, round 1's tenth moment and far out at the base, is the one place both arms
improve on the base: 0.075067, 0.045147, 0.022220, 0.010347 against a target of
0.00399. It is still 2.6x the target at 0.2500, and it gets there by removing the
drug block that drives homelessness in this economy.

## What was not done

The order said not to extrapolate past the arms measured, and nothing above does.
In particular:

- No value of `addiction_scalar_1` between 0.1000 and 0.2500 is proposed, and no
  interpolated `lambda_d` is quoted inside that interval. The bracket is stated;
  the root is not estimated. The corner at 0.2500 is a reason for caution about
  the shape of the curve there, not a reason to guess it.
- The 2x2 Jacobian is reported as measured on two specific segments and is not
  solved for the joint step that would reach `lambda_d` 0.0368 and `theta` 0.162.
  The sign turn between the 0.0120 -> 0.0360 and 0.0360 -> 0.1000 segments is
  direct evidence that the local Jacobian does not travel.
- Nothing from the archive's other economies is quoted as a prediction for this
  one.
