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

## What is pinned while block C is swept

Block A is HELD, not left where the corner put it. The handover could not name
these until 24 August, so they had been drifting under every point measured
before then:

    value_of_life (aleph)        120      3.5x the banked 34.4153. That gave a
                                          value of life over labour income of
                                          30.09 against a target of 80, and the
                                          sweep had been pinning aleph at its
                                          DECLARED 11.0, lower still. Aleph
                                          prices the mortality risk that deters
                                          use, so every b measured before this
                                          was compensating for a death penalty
                                          several times too cheap.
    discount_factor (beta)       0.99     wealth over output was 4.23 against 3
    relative_share_of_leisure    3.0      labour supply 0.4567 against 0.400
    labor_income_tax_rate        0.7537   gives 0.2127, inside 20 to 24 per cent
    sd_permanent_productivity    0.9534   bottom half share on target
    relative_share_of_housing    TIED     see below

**gamma is tied to theta**: `gamma = 0.28*(1-theta)`, so housing takes 28 per
cent of what the drug does not. They are exponents in the same Cobb Douglas
bundle and calibrating them independently lets the housing share drift as theta
moves. `apply_gamma_tie` is called after the state is read, after a handover and
after theta's own update, because theta moves in all three places; gamma's own
bracket and distance are off while the tie holds. At theta 0.38 gamma is 0.1736
and the housing spending share should come back near 27 per cent.
`tie_gamma_to_theta = 0` frees it again.

ONLY OUTSTANDING POINTS BELONG IN B_SWEEP_FULL.txt. Measured points were listed
there too, which was harmless while the pinned vector never changed. It changed,
every historical row's vector stopped matching its grid line, and the driver
began re-measuring b = 0.005.

## Block C so far

    b       lambda  theta    users     disorder   d.share   drug share
    0.005    4.5    0.4265   0.9997    0.8127     0.8130      --
    0.01     4.5    0.4265   0.9987    0.8071     0.8081      --
    0.04     1.0    0.4265   0.9652    0.4034     0.4179      --
    0.05     1.0    0.4265   0.9474    0.3507     0.3702    0.2111
    0.06     1.0    0.35     0.7585    0.1117     0.1472    0.0943
    0.12     1.0    0.35     0.000158  7.7e-07    0.0049    0.0084
    TARGET                   0.0890    0.0368     0.4130    0.1620

Every one of those ran at aleph 11 and an unpinned block A, so they say more
about the shape of the curves than about where the answer is.

**The b curve is not log linear.** 0.947, 0.759, then 0.000158 across 0.05, 0.06
and 0.12: flat, then a cliff somewhere above 0.06. Interpolating through it gave
0.0634 and was badly wrong.

**theta is bracketed**: 0.4265 gave a spending share of 0.2111 and 0.35 gives
0.0943, against 0.1620, so it sits near 0.38 to 0.40. Both readings come from
b's with far too many users, so hold that loosely.

**The disordered share is very sensitive to b**: 0.4179 at b = 0.04 and 0.1472
at 0.06. lambda 1 was right AT b = 0.04, so at the b that lands the pool lambda
comes UP.

**Homelessness is alive**: 0.0110 against 0.00399 at h_1 = 0.304, the first time
this session it was neither zero nor nine per cent.

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
