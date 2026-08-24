# Where the calibration is, and what happens next

THIS FILE IS THE CURRENT STATE. The scheduled watch routines used to carry it
in their own prompt text and it went stale within the hour, twice: one of them
was still saying "the sweep is finished, b = 0.1202, do not restart the sweep"
long after 0.12 had been measured at zero participation. A routine's prompt is
written once and fires for days; a file in the repository is updated by the
same commit as the thing it describes. Read this first, and update it when the
state changes rather than editing the routines.

Last updated 24 August 15:25 UTC.

## What is running

The b sweep, driven by `code/sweep_b.py`, NOT `supervise_calibration.py`. Do not
start the joint calibration loop while it runs.

A sweep point is a **(b, lambda) PAIR**. `B_SWEEP_FULL.txt` holds the grid, one
point a line, `b` alone or `b lambda`. lambda is handed to the model through
`PARAM_HANDOVER.txt`, which the model reads after the state and deletes as it
does, so it cannot outlive its point. A line with one number runs at the banked
lambda, which is 0.225139.

Results bank to `B_SWEEP.tsv` as each point lands, and the driver pushes the
branch and merges main.

## The curve so far

    b       participation   users     disorder     income of users   lambda
    0.01       0.9051       0.9595    0.0544          0.675          0.225139
    0.03       0.7456       0.7569    0.0114          0.544          0.225139
    0.05       0.0690       0.0694    0.000327        0.477          0.225139

Targets: participation 0.0890, disorder 0.0368.

**b alone cannot land both.** Participation crosses its target near b = 0.047;
the disorder crosses ITS target near b = 0.015. Onset is
`1 - exp(-lambda*quantity)` and b sets the quantity, so the two moments are one
margin and need two instruments. Hence the pair grid.

Remaining: 0.045 and 0.047 to finish the b curve, then b held at 0.047 while
lambda goes 2.25, 7.5 and 25 (x10, x33, x111). Raising lambda moves
experimenters into the disorder and pulls participation DOWN, so b comes back
down in a second round. Measure lambda's response at fixed b first, then
re-solve for b: two rounds of five points, not a blind two dimensional grid.

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
