# Where the calibration is, and what happens next

THIS FILE IS THE CURRENT STATE. The scheduled watch routines used to carry it
in their own prompt text and it went stale within the hour, twice: one of them
was still saying "the sweep is finished, b = 0.1202, do not restart the sweep"
long after 0.12 had been measured at zero participation. A routine's prompt is
written once and fires for days; a file in the repository is updated by the
same commit as the thing it describes. Read this first, and update it when the
state changes rather than editing the routines.

Last updated 24 August 16:35 UTC.

## What is running

A STAGED VECTOR SEARCH, driven by `code/sweep_b.py`, NOT
`supervise_calibration.py`. Do not start the joint calibration loop while it
runs.

A sweep point is a **parameter VECTOR**. `B_SWEEP_FULL.txt` holds the grid, one
point a line:

    0.047 lambda_addiction=4.5 value_of_life=11 size_homelessness=0.304

The first field is b, which the model reads from `B_SWEEP_GRID.txt`. Every other
field goes to `PARAM_HANDOVER.txt`, which the model reads after the state and
deletes as it does, so nothing outlives its point. Any name the Fortran's
handover `select case` knows may be used. A line with only a b runs everything
else at the banked value. `#` starts a comment. `done_points` is keyed on the
whole vector, so two points may share a b and differ elsewhere.

Results bank to `B_SWEEP.tsv` as each point lands, with the vector recorded in
the `set` column, and the driver pushes the branch and merges main.

### Why staged and not a five dimensional grid

Three levels each over h_1, b, lambda, aleph and the employment multiplier is
243 solves at about twenty minutes each: **eighty one hours**. Two levels each is
thirty two points and eleven hours. What the search needs is not every cell but
every parameter measured in a world where the others are not absurd. The author
has agreed to stages.

**Round 1** (running): lambda at 4.5, b swept DOWN over 0.005, 0.01, 0.02, 0.03,
with the other nine instruments pinned at their DECLARED values on every point.
b goes down because lambda rising twenty fold from 0.225 moves experimenters
into the disorder and pulls participation down with it.

**Round 2**: aleph and the employment multiplier, at whatever b and lambda round
1 lands on. Both act THROUGH use, so measuring them at a b and lambda that
produce no sensible use measures nothing.

**Then**: h_1 against the homelessness rate, once there is a population to be
homeless.

## The two moments b and lambda have to land, and what they are

**b owns TOTAL USERS, not the experimenters.** `participation_rate_data` = 0.0890
is NSDUH 2024 `svyrdudany` in (1,2,3), ANY drug use disorder INCLUDING MILD,
ages 26 and over: the data appendix calls it "whether a household uses". The
update used to compare it against `model_exprimenters`, which excludes the
disordered, and so asked for 8.90 per cent mild users PLUS 3.68 per cent
disordered, 12.58 in total against a survey figure of 8.90. Fixed; b now
brackets on `model_total_drug_users`.

    total users            -> 0.0890
    disorder               -> 0.0368
    experimenters implied  -> 0.0522
    disordered share of users -> 0.4130

**lambda owns the disordered share of users**, 0.4130. That is the cleanest way
to read it: the share is near zero when lambda is too small and near one when it
is too large, and it does not depend on getting b right first.

Two declaration comments quote 0.1013 and 0.0454 as the current cuts. Those are
the EIGHTEEN and over figures; the model's universe is 26 and over, where the
same variable gives 0.0890 and 0.0368, so the VALUES are right and the comments
are behind. One of them reads as an instruction to change 0.0368 to 0.0454. Do
not act on it; it is flagged for the author.

## The curve measured at the BANKED parameters

These three ran before the staging, at lambda 0.225139 and the banked vector,
and are kept for the shape of the b curve rather than as answers:

    b       total users   disorder    disordered share   income of users
    0.01       0.9595      0.0544         0.0567             0.675
    0.03       0.7569      0.0114         0.0150             0.544
    0.05       0.0694      0.000327       0.0047             0.477

Total users cross 0.0890 near **b = 0.0474** on this curve. The disordered share
is nowhere near 0.4130 anywhere on it, which is what lambda is for.

## Round 1, staged, everything else at declared values

    b       lambda   total users   disorder   disordered share   experimenters
    0.005    4.5        0.9997      0.8127        0.8130            0.1870
    0.01     4.5        0.9987      0.8071        0.8081            0.1916
    0.04     1.0        0.9652      0.4034        0.4180            0.5618
    TARGET               0.0890     0.0368        0.4130            0.0522

**lambda = 1 is SETTLED.** At b = 0.04 it gives a disordered share of users of
0.4180 against a target of 0.4130. The author read that off the 41.3 per cent
conversion before it was measured. The lambda 4.5 points are kept only as the
saturated contrast: at that hazard the share is 0.81 whatever b is.

**b has to RISE, and the reason is worth keeping.** Raising lambda ENLARGES the
user pool rather than only redistributing within it, because the disorder is
absorbing: more onset means more households stuck using. At lambda 0.225,
b = 0.05 gave 0.069 total users; at lambda 1, b = 0.04 gives 0.965. So the b
that lands 0.0890 users at lambda 1 is well above 0.05, not the 0.047 the old
curve suggested. Grid: 0.05, 0.06, 0.07, 0.08 at lambda 1.

Note the share will drift as b rises, since a larger b means less quantity and
so less onset. If it falls much below 0.4130 at the b that lands total users,
lambda comes up a little to compensate. That is a joint move of two parameters
around a point that is already close, which is what the slow updates are for.

## THE BLOCKS, and the order they are worked in

Twenty three parameters are calibrated internally. Moving them all at once is
what produced a world with 75 per cent participation, because a parameter whose
moment is measured on a population set by another parameter is not identified,
it is guessing. So they are worked in BLOCKS: within a block the members
genuinely interact and have to move together; between blocks the earlier one is
upstream of the later and is pinned once it is reasonable.

"Reasonable" here does not mean converged. It means no moment in a corner, so
the next block is measured against a population that exists.

### A. Income, hours, wealth  — upstream of everything

    sd_permanent_productivity   bottom half's share of productivity   0.172
    labor_income_tax_rate       average labour income tax             0.224
    relative_share_of_leisure   labour supply over total hours        0.400
    discount_factor (beta)      wealth to output                      3.00

Every other moment in the model is a ratio to income or to wealth, so if these
are wrong every later block is measured on the wrong scale. They barely touch
drug use, which is what makes them safe to do first. Three of the four are
already within about fifteen per cent and sd_permanent_productivity is on
target.

### B. Housing  — needs A's income distribution

    smallest_house_size (h_2)   share in the smallest unit            0.1321
    largest_house_size (h_4)    share in the largest                  0.6267
    relative_share_of_housing   housing spending share of renters     0.268
    size_homelessness (h_1)     homelessness rate                     0.00399

These four are one ladder and cannot be set apart: h_2 fixes the affordability
floor, h_4 the top rung, the spending share the whole ladder's price, and h_1
what the street is worth relative to the bottom of it. The homelessness rate is
the paper's headline moment and it is the one most sensitive to A: it is the
share of households that cannot afford the cheapest unit, so it is read off the
bottom of the income distribution.

### C. Drugs  — needs A, interacts with B

    addiction_scalar (b)        total drug users                      0.0890
    lambda_addiction            disorder rate                         0.0368
                                (equivalently, disordered share       0.4130)
    relative_share_of_addiction share of income spent on drugs        0.1620
    value_of_life (aleph)       value of life over labour income      80

The four are one margin. b sets the quantity used, the quantity drives onset
through 1-exp(-lambda*quantity), theta scales the spending that quantity
implies, and aleph prices the mortality risk that deters all of it. This is the
block being worked now.

### D. Labour market penalties and mental illness  — needs C

    separation_rate             unemployment rate                     0.0485
    employment_multiplier       unemployment among the disordered     0.1625
    kappa_uem                   employment rate given SMI             0.300
    lambda_m                    SMI share of the homeless             0.250

D is downstream of C by arithmetic, not by taste: total unemployment is the
disordered share times their rate plus everyone else's, so the separation rate
cannot be identified until the disordered share is near 3.68 per cent. At 24.67
per cent the disordered alone contributed 12.05 points against a total target of
4.85, and the separation rate was driven to its floor trying to absorb it.

### E. Programmes and transfers  — needs B and C

    voucher_probability         eligibles receiving a voucher         0.266
    max_food_cost               food stamps over labour income        0.0042
    utility_cost_of_treatment   treatment take up given a disorder    0.245
    mu_homeless                 recovery housed over recovery homeless 1.473

Each is a rate over a population the earlier blocks define: vouchers over the
eligible, treatment over those with the disorder, the recovery ratio over the
homeless with the disorder. With any of those populations empty the moment is
not small, it is undefined, which is how the treatment cost reached its floor
while take up sat at zero.

### F. Across generations  — needs C

    penalty_child_addicted      child's disorder rate over parent's   3.00
    weight_on_child             no scalar moment
    fixed_cost_to_moving        no scalar moment

Last because the moment is a ratio of one generation's disorder rate to
another's, so it needs C settled twice over.

### Not calibrated in this configuration

    discount_factor_on_child, housing_status_grid_expander,
    minimum_inheritance         adjusters are zero
    rho_d, rho_m                include flags are off

### How a block is run

The sweep already does this: a point pins every parameter outside the block at a
sensible value through PARAM_HANDOVER.txt and varies the block's members. When
the block's moments are all out of their corners, its members are pinned in turn
and the next block's grid is written. Only when every block is reasonable does
`diagnostic_simulation` go to 0 and the joint loop move all twenty three
together at one per cent a loop.

## The order of work the author has set

1. The sweep pins b and lambda. **Report the curve; do not pick the values.**
2. Install `GOOD_START.txt` as `PARAM_HANDOVER.txt` with the chosen b and
   lambda appended. The banked parameters are the record of a chase across a
   world with 75 per cent participation and sit 6x to 106x from their declared
   values.
3. Set `diagnostic_simulation=1` and run ONCE. It freezes the parameters like a
   sweep but without the sweep's early stop, so every moment prints and the
   equilibrium can be READ.
4. Read the moments. Anything still in a corner is adjusted by hand and
   simulated again.
5. Only when nothing is cornered, `diagnostic_simulation=0` and let the slow
   updates run.

## Settled, and not to be re-litigated

- **b = 0.1202 is dead.** 0.12 has been measured at exactly zero participation,
  users and disorder. `B_SWEEP.old_mortality.tsv` and `B_SWEEP.h1_zero.tsv` are
  archives, not current.
- **`size_homelessness` has a floor of 0.01.** Zero prices the street at minus
  infinity: `h_1 = housing_size(0)*size_homelessness` and housing enters utility
  as `h**((1-sigma)*alpha)` with no shifter.
- **J_E = 55 is an age INDEX**, age = index + 25, so onset is possible to 79.
  The author has confirmed it. Do not change it.
- **`theta_hi` is 0.5**, raised because the spending share and the disorder are
  the same margin: theta up for the share, lambda down for the disorder.
- **Steps are state dependent**, through `move_factor`: a moment below a tenth
  of its target or above five times it is a CORNER and its parameter may move by
  `escape_factor` (ten for b, two for the rest); otherwise one per cent a loop.
  The log prints `MOVE MODE <param>=`. Do not hand tune these.

## Reporting

`code/CALIBRATION_TABLE.txt` is written every checkpoint by the supervisor and
`CALIBRATION_TABLE_HISTORY.txt` keeps every round. `/gaps` regenerates it. Show
**every** internally calibrated parameter every time, never a median and never a
selection. The report accounts for all of them, as a row or as a named
exclusion, and closes with `accounted for: N calibrated + M not calibrated`. If
that arithmetic does not add up, say so.

Do not read a rising income of drug users as a fault: Table 7 puts it at 0.74 of
average in the data against 0.41 in the old benchmark. Only a ratio above one is
a problem.

## Operational notes that have cost time

- Check processes with a POSITIONAL `/proc` scan, never `pgrep -f`, which
  matches the shell whose own command line carries the pattern. `argv[0]` ending
  in `hftf` is the model; `argv[0]` a python with `argv[1]` ending in
  `sweep_b.py` is the driver.
- Launch from `code/`, not the repository root.
- After a container rebuild:
  `git fetch origin claude/two-period-addiction-hazard-d7gb61 && git checkout -B claude/two-period-addiction-hazard-d7gb61 FETCH_HEAD`,
  rebuild if `./hftf` is missing or older than the source, then from `code/`:
  `ulimit -s unlimited && setsid nohup python3 sweep_b.py > sweep_b_driver.log 2>&1 < /dev/null &`
- A point is about twenty minutes, a cold solve each.
