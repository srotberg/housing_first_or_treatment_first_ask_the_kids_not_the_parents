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

## Why the loss stopped falling, measured rather than guessed

Eight generations and a hundred and eighty points have moved the best loss from
0.481 to 0.421. That is not a search converging; it is a search stuck. The
decomposition of the best point says why, and it is two different problems
wearing one number:

    moment       model     target   w   rel gap   share of loss   cumulative
    lambda_d    0.00383    0.0368   3    -89.6%       22.0%          22.0%
    kappa_uem    0.9536      0.30   1   +217.9%       17.8%          39.9%
    b           0.04701     0.089   3    -47.2%       11.6%          51.5%
    lambda_m    0.00160      0.25   1    -99.4%        8.1%          59.6%
    tau_u        0.4794     0.245   1    +95.7%        7.8%          67.4%
    theta        0.1050     0.162   2    -35.2%        5.8%          73.2%

Five moments carry two thirds of it, and the remaining seventeen carry a third
between them, most of them inside fifteen per cent. The search has not been
failing at twenty two things; it has been failing at five.

**kappa_uem and lambda_m are one problem, and it was not an optimisation problem
at all.** They are 25.9 per cent of the loss and they share an instrument, which
sat pinned at its floor of 1.0 for every generation. At one, kappa_uem is the
identity: serious mental illness costs nothing on either employment margin. The
declaration block says what SMI is supposed to do -- "kappa_uem takes it out of
work, DI carries its income there, lambda_m carries its share of the homeless" --
so with the multiplier at one the poverty channel is switched off, and the SMI
share of the homeless is 0.0016 against a target of 0.25 because nothing has
pushed anyone with SMI onto the street. No method moves a clamped parameter.
Freeing it should collapse both moments at once, and that is what the probe at
8.5 in generation nine is for.

**b, lambda and theta are the other problem, and they are 39.4 per cent.** They
need a large move that has to be made TOGETHER. The evidence that one at a time
does not work is generation eight: lambda alone went from 5.06 to 9.11, in the
direction the ridge map says the answer lies, and the loss went from 0.455 to
0.527. Every other single-parameter arm was worse still, up to 2.03. The block
sits in a narrow curved valley, single-parameter arms fall off it whichever way
they go, and the trust region caps the joint move at a factor of 1.4 a round.

## Nelder-Mead, on the block and not on the vector

`code/simplex.py`. The Jacobian keeps the eighteen parameters it handles well;
the four coupled ones get a simplex.

The case for it on this block is that the block is where derivatives fail. The b
curve recorded above is 0.947, 0.759, then 0.000158 across 0.05, 0.06 and 0.12 --
flat and then a cliff -- and interpolating through it gave 0.0634 and was badly
wrong. A slope measured on the flat says nothing about the cliff. Nelder-Mead
needs no slope, tolerates the discontinuity, and moves all four parameters
together by construction.

The case AGAINST it on the whole vector is just as strong and it is why the
Jacobian stays. Twenty two parameters need twenty three vertices before the
method takes its first step, and it is known to stagnate well below that
dimension. Worse for this fleet, it is sequential: reflect, look, then decide
whether to expand or contract, one twenty-minute solve at a time, which would
leave seventeen of eighteen parallel slots idle.

**So the decision tree is evaluated in parallel instead of walked.** Every trial
the textbook could ask for -- reflection, expansion, outside contraction, inside
contraction -- goes out at once, and the standard acceptance rules then run
against four results already in hand. The logic is unchanged; only the order is.
Four points a round, one wall clock.

Two things the simplex has to get right and did not on the first attempt:

- **A vertex is only a vertex if the rest of the vector is identical.** The
  archive's hundred and eighty points each carry their own background, and
  building the first simplex from the ones whose block values were conveniently
  spread would have compared numbers that are not comparable. Only points at the
  best point's background are reused -- which turned out to be one of them, so
  four vertices are measured.
- **An emitted point names the WHOLE vector, not the four.** run_one_point.sh
  defaults to the current generation's centre and `converge.py --write` moves
  that centre every round, so a command naming only the block would be evaluated
  against a different background each time and the simplex would be tracking a
  function moving underneath it.

## THE BATCH SIZE IS SET BY A SESSION LIMIT, AND IT WAS FOUND BY BREAKING IT

Iteration zero was emitted as sixty seven points and FIVE of them ran. The other
sixty two sessions all failed with the same line:

    You've hit your session limit - resets 5:50am (UTC)

The limit is a count of SESSIONS PER FIVE HOUR WINDOW on the account, and by
03:40 the window had already absorbed twenty three vertices, four earlier
simplex points, a dispatcher and forty odd manual spawns. Everything after that
was rejected instantly. The workers were not slow and the code was not wrong;
there was no budget left to run them.

Three consequences, all standing:

- **Size the batch to the remaining window, not to what the method could use.**
  The information ceiling of an MDS iteration is 3n, and 3n is unaffordable here.
  Plain MDS -- n reflection points, then n expansions or contractions next round
  -- is TWENTY TWO points and costs two rounds of wall clock instead of one. That
  is the affordable form and it is the default now.
- **Check rate_limit_info BEFORE emitting, not before spawning.** A batch written
  larger than the budget cannot be spawned, and clearing a half-spawned batch
  costs a round: the state records points the fleet was never asked for, and the
  simplex waits for them.
- **A failed spawn is silent in the point archive.** Nothing distinguishes "never
  ran" from "still solving" except the session's own status_detail, so a batch
  that is missing most of its points after forty five minutes gets its sessions
  checked rather than its wall clock extended.

The five that did land were not wasted -- they are archive points like any other
-- but iteration zero has to be re-emitted, and it is re-emitted at twenty two.

## The SMI block, redesigned 25 August

    lambda_m           ASSIGNED     0.067, the recovery literature
    iota_smi           ASSIGNED     2.0, onset doubled by a co-occurring disorder
    zeta_DI            ASSIGNED     0.25, the SSDI and SSI replacement rate
    smi_onset_level    CALIBRATED   the SMI population share
    di_takeup          CALIBRATED   the SMI share of the homeless

**Every instrument now has a channel to the moment beside it**, which the old
arrangement did not. lambda_m owned the SMI share of the homeless and is a
RECOVERY RATE: its only route to that moment is spell length, against an outcome
that is a threshold in income. At its floor it delivered 0.0133 against 0.25.

### What was actually wrong, and it was not the search

Every non-employed household with SMI received DI: no take-up gate, no waiting
period, no work history test, no eligibility screen. UI is a first period
benefit, so from the second period out of work a household WITHOUT serious
mental illness had exactly zero income and one WITH it had a quarter of its
earnings, for ever. **Serious mental illness was the only unemployment insurance
in the model**, handed to precisely the households the calibration wants on the
street.

So the model had SMI at 1.33 per cent of the homeless against a five per cent
population share -- UNDER represented by nearly four, where the data says OVER
represented by five. A factor of nineteen, and a wrong SIGN, which no setting of
lambda_m or of the prevalence profile can repair: reaching 0.25 by prevalence
alone needs p near 0.83.

Take-up is now 0.33, from about 13.6 million US adults with SMI (5.2 per cent,
SAMHSA) against about three million receiving SSI or SSDI on a mental disorder
basis net of concurrent receipt -- 0.22 over all of them, divided by the 0.671
who are not employed, because the rule fires only for those. THE PRIMARY TABLES
WERE UNREACHABLE: ssa.gov is blocked by the container's egress proxy. Replace
0.33 from SSI Annual Statistical Report 2023 table 39.A, DI Annual Statistical
Report 2023 table 10.A, and the concurrent beneficiary total when they can be
read.

### Onset is a level on an assigned shape

`onset(j) = smi_onset_level * shape(j)`, the shape from
`data/us_mh_onset_shape.csv` and the level calibrated on the population share.

The old design backed onset out of the prevalence profile by an accounting
identity, which matched prevalence BY CONSTRUCTION at any lambda_m -- so the
model could not miss it, and lambda_m was left unidentified by the one moment it
should own. The identity also put a floor under lambda_m, because a declining
profile needs p(j+1) >= p(j)(1-lambda_m): below about 0.046 the implied onset
went negative at 59 of 60 ages, the SMI state emptied, and every SMI moment read
zero. The calibration walked straight into that cliff. No identity, no floor.

**THE SHAPE IS NOT INDEPENDENT DATA.** Solving the identity backwards from the
file's `implied_onset` and `smi_prevalence` columns returns the same lambda at
every age: 0.0670 at 26, 36, 46, 56, 66 and 76. The shape IS the identity's own
output at lambda_m = 0.067, normalised to one at age 26. Two consequences, both
standing:

- at the default level of 0.003306 the new design reproduces the old one
  exactly, so the change is not discontinuous, and 0.067 is confirmed as the
  recovery rate the data file was built around;
- **if lambda_m is ever changed, the shape must be rebuilt from the prevalence
  profile at the new value**, or the age gradient of onset belongs to a recovery
  rate the model no longer uses.

The genuine data inputs behind this block are two: the prevalence profile and
lambda_m. Everything else is a transformation of them or is calibrated.

### Two things to watch

**The calibrated level is not a citable hazard.** iota_smi doubles onset for
households with a disorder, so realised prevalence exceeds what the level alone
implies, by more as the SUD rate rises toward its 3.68 per cent target. The level
is chosen so the MIXTURE matches and must not later be quoted as the raw onset
rate for a clean household.

**The age profile is now a check rather than a guarantee.** The old design
reproduced the whole profile; this one matches its level and lets the gradient
fall where the shape and the SUD interaction put it. The model prints prevalence
by age against the profile, and that comparison is worth reading.

### The DI parameters are collinear in the smooth form

`income = di_takeup * zeta_DI * base`, so only the PRODUCT is identified:
0.33 x 0.25, 0.165 x 0.5 and 1.0 x 0.0825 are the same model. Calibrating both
on separate moments would leave one wandering with no effect on anything.

They separate only with a third SMI state, with DI and without: take-up would
then change HOW MANY households have zero income and generosity HOW FAR above the
rent threshold the covered ones sit. That costs about twice the solve time and a
state space change. The smooth form is an approximation of a lumpy programme and
it errs toward MORE homelessness among the SMI, since nobody is left fully
insured. **If the moment overshoots, that is the first suspect and the third
state is the fix.**

### THE ARCHIVE IS STALE

All 211 points predate the DI fix and were computed with SMI fully insured.
Their losses are not comparable with anything measured after it and the simplex
restarts. That is a real cost and it is worth it: no search over the old model
could have reached the target, because the mechanism the target is about was
switched off.

## What counts as finished

The author, 25 August: "it is ok if we can't hit every single moment. It's many
moments. As long as almost all are within 5-10 per cent or so, and maybe one a
bit off it's ok."

So the target is not zero and never was. Twenty two moments against twenty two
instruments is not a system with an exact solution waiting to be found -- several
of the targets come from different surveys, different years and different
universes, and one of them (the SMI share of the homeless) is pooled across
thirty nine studies. A search driven at zero would spend itself chasing the last
per cent of moments that are already inside the noise of their own sources.

    DONE_BAND        0.10     a moment inside ten per cent is landed
    DONE_ALLOWED_OUT 1        and one may sit outside it

`simplex.py` prints this every round as ACCEPTANCE: MET or not met, and stops on
its own when the criterion holds and the simplex is tight.

**IT IS A STATEMENT ABOUT THE WORST MOMENTS, NOT THE MEAN, and the loss is a
mean.** A weighted mean of relative gaps can reach 0.10 with one moment two
hundred per cent out and everything else perfect, which is exactly the outcome
the criterion rules out. The mean stays as the thing the search minimises,
because changing the objective now would break comparability with two hundred
archive points, but it is not the thing the search is judged by. If the mean ever
starts tolerating a straggler -- the count inside ten per cent stalling while the
loss keeps falling -- that is the signal to switch the objective to a
max-flavoured one, and it should be said out loud when it happens rather than
noticed later.

Where this stood when the criterion was written, at the best point of two hundred
and four:

    within  5%:  6 of 22
    within 10%:  7 of 22
    within 25%: 12 of 22
    outside 10%: 15, worst tau_u at +149%

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

## The generation loop (from 24 August)

The calibration no longer advances one parameter at a time. Every round is a
GENERATION: a centre, plus one arm per parameter, each arm differing from the
centre in exactly one value. Each point is one worker session solving the model
once and committing its moments to `code/points/`. Twenty-odd points arrive
together, so every parameter gets a matched pair and therefore a secant in the
same twenty minutes.

  python3 code/ridge_solve.py     b and the value of life, solved together
  python3 code/converge.py        every parameter moved, next generation emitted
  python3 code/converge.py --write  the runner re-centred on the new vector

**b AND THE VALUE OF LIFE ARE ENTANGLED AND MUST BE SOLVED TOGETHER.** This cost
a generation to learn. Each of them moves both the drug margin and the value of
life, so the b that gives 0.089 total users is 0.0277 at a value of life of 30
and 0.0098 at 120, and the value of life that gives a ratio of 80 is 37.1 at
b = 0.02 and 27.3 at b = 0.06. Both relations are straight lines in logs. The
answer is where they cross, and it is on neither line taken alone: reading b off
one slice and the value of life off another put generation two at b = 0.0096
when the crossing is at b = 0.0261.

Eighteen points put the crossing at b = 0.0261, value of life 35.0. Ten points
had put it at 0.0246 and 35.1, so that pair has essentially converged.

Everything downstream of the drug margin — treatment take-up, recovery, the
child's inherited penalty — is identically zero whenever the margin is empty, so
those parameters cannot be calibrated at all until b and the value of life are
right. That is why they come first.

### The worker prompt

One session per point. Give it verbatim, substituting the arm; a worker with no
arm runs the centre. It must not be given anything else to do: a worker that
edits a file breaks every matched pair in its generation.

```
You are a calibration worker. Do exactly this and nothing else. Do not edit any
source file, do not change any parameter, do not run anything beyond these steps.

1. Find the repository and check out the working branch:
   cd "$(find /home/user -maxdepth 4 -name run_one_point.sh -printf '%h\n' | head -1)/.."
   git checkout claude/two-period-addiction-hazard-d7gb61 2>/dev/null || git checkout -b claude/two-period-addiction-hazard-d7gb61 origin/claude/two-period-addiction-hazard-d7gb61
   git pull --rebase origin claude/two-period-addiction-hazard-d7gb61

2. Run exactly one model point. It compiles first (a few minutes) and then solves
   for about 20 minutes, printing a table of moments at the end. Give it a
   generous timeout (2400000 ms) and let it finish:
   bash code/run_one_point.sh <ARM>

3. Commit the point file it wrote under code/points/ and push it:
   git add code/points
   git commit -m "gen<N> worker: <ARM>"
   for i in 1 2 3 4; do git pull --rebase origin claude/two-period-addiction-hazard-d7gb61 && git push origin HEAD:claude/two-period-addiction-hazard-d7gb61 && break; done

4. Reply with the ALL TARGETED MOMENTS block and stop.
```

#### Give the arm, never ask the worker to find it

The arm goes into the prompt as literal text, or as a line number into a flat
file of arms that the worker reads with `sed`:

```
bash code/run_one_point.sh $(sed -n '7p' code/arms4.txt)
```

It must never be an instruction to extract its own vertex out of `simplex.py`.
Simplex 3 was spawned that way and five of its twenty-two workers never started:
their containers had no numpy, so the import failed before the script reached a
vector, and each of them stopped to ask about it. A flat file read positionally
has no dependency to be missing. `code/ARMS4_README.md` records the same point
next to the file.

#### Name the repository when you spawn a worker

`create_session` without `source_url` gives the worker whatever the parent
session inherits, and that is not reliable: nine of simplex 4's twenty-one
workers came up with no checkout at all and stopped to ask for one. The cause
was a rename. The repository is now

    https://github.com/srotberg/housing_first_children_later

and every push from a clone that still points at the old name comes back with
`remote: This repository moved`. Pass `source_url` and `source_revision`
explicitly on every spawn so the container is provisioned with the branch
already on disk, and the worker never has to find or clone anything.

#### Do not stash in a worker

An earlier worker prompt carried `git stash -u -q` before the pull. A worker
that stashes leaves files behind it cannot judge, and it then stops to ask
whether to keep them; one of simplex 3's did exactly that and never ran. A
worker writes one point file and pushes it. If the push is rejected it rebases
and pushes again, and nothing else.

### Do not open a generation on top of one still running

A round closes only when the generation in flight has landed. Half its points is
the test. Spawning the next generation while the last one is still solving is
how this loop breaks: the arms then differ from a centre that has already moved,
and every pair they were meant to form is worthless.

### Why so few of the homeless carry serious mental illness

The SMI share of the homeless is 0.084 against a target of 0.25, and it is not
that the model is short of people with SMI: the population share is 0.0458
against 0.0482, and the age profile it reads has SMI at 12.1 per cent at age 26
falling to 0.9 per cent at 85, so the mass is working age, not retired. The
identity is

    lambda_m = p*RR / (p*RR + (1-p))

in the population share p and the relative risk RR of being homeless with SMI.
At p = 0.0458 the model produces RR = 1.92; the data wants 6.59. Nothing else
enters, so either the population share triples or the relative risk does.

WHY THE RELATIVE RISK IS SO LOW. Homelessness here is a CHOICE, the lowest point
of a housing grid, and

    housing_size(lowest) = housing_size(0) * size_homelessness

puts the street at about a tenth of the smallest rental's services. Giving that
up costs roughly gamma*ln(1/0.101) = 0.67 in flow utility, which is large, so it
is taken only when the rent is big against TOTAL RESOURCES -- assets included,
not income. Zero income is not zero resources.

That is the whole asymmetry. A SUD drains ten per cent of income every period
forever, so the disordered reach any income shock with nothing banked. SMI cuts
the chance of working but, with include_rho_m = 0, costs nothing when employed
and drains nothing when not, so an SMI household arrives at unemployment with a
full buffer and runs it down instead of taking the street. SMI is modelled as an
INCOME shock in a world where homelessness is a WEALTH phenomenon.

WHAT IS NOT PINNED. beta is bracketed on wealth over output, an aggregate, and
sits nineteen per cent above target. The bottom half's share of net worth, 2.52
per cent in the Fed distributional accounts, is in the untargeted table and is
never matched. So nothing in the loss controls how many households hold almost
nothing, which is exactly the group that can be shut out of the smallest rent. A
model can carry the right total wealth with far too little of it concentrated,
and then nobody is ever short.

MEASURE BEFORE CHOOSING A LEVER. print_all_moments now reports four DIAG lines
inside the block run_one_point.sh keeps: the share of the homeless who could
have afforded the smallest rental out of income plus assets and chose the street
anyway, the share receiving food stamps, median assets to income, and the
average assets of the homeless. If the first is near one, homelessness is a
preference rather than a constraint and no parameter that moves incomes will
move the mental illness share of the street.

The candidate levers, once those land: rho_m switched on so SMI drains
resources rather than only employment; beta pushed to its own target so buffers
stop being oversized; the smallest rental tightened, which h_2 wants anyway at
fifty per cent over target; and, later and separately, the DI state below.

### After the calibration: give DI its own state

AGREED WITH THE AUTHOR, TO BE DONE ONCE THE OTHER PARAMETERS HAVE CONVERGED, not
before. zeta_DI is held externally at zero because it is an expected payment and
ten of thirteen unemployed households with serious mental illness receive
nothing, so any positive value gives all thirteen a floor that most do not have.

The honest version of that is a state, not an average: unemployment with SMI
becomes TWO states rather than one. At onset the household is awarded DI with
probability about 3/13 and then draws a replacement of about 0.25 for as long as
it stays ill, or is not awarded it and draws nothing, permanently. What the 25
per cent is a share of -- the household's own productivity or average income --
is a detail to settle when it is built, not now.

AND THE MEASUREMENTS SAY THE AVERAGE CANNOT SUBSTITUTE FOR IT. Three points now
sit on zeta_DI with everything else held: 0.0825 gives lambda_m 0.0413, 0.0250
gives 0.0759, 0.0100 gives 0.0843, against a target of 0.25. The elasticity is
-0.51 over the first step and -0.11 over the second, so the response flattens
hard; on the local slope 0.25 would want zeta_DI near 1e-6, which is to say no
positive value reaches it and zero probably does not either. h_1 meanwhile holds
at 0.0037 to 0.0039 throughout, so this is not the conditioning population
emptying -- the moment is simply out of reach through this parameter. That is
the case for the state, and it is why lambda_m is reported rather than matched
in the meantime. That recovers the dispersion the average throws away, and the
dispersion is the part that matters -- the ten with no floor are the households
that fall to zero income and lose their housing, which is the margin the paper
measures.

It is deferred because it is a whole extra dimension on every value function and
every distribution pass, and this model is slow enough that one more state costs
a large multiple of the running time. Adding it mid-search would also invalidate
every measured point at once. So: converge first on the current structure, then
add the state and refine the calibration around it.

### What each of the worst gaps is actually stuck on

Read off the 290-point archive rather than guessed, at the leader of simplex 4
(`point_b39d5273d1`, loss 0.306). A correlation here is against every point that
carries both the parameter and the moment.

| moment | gap | its own instrument | works? |
|---|---|---|---|
| `lambda_d` | 85% | `lambda_addiction` | moves it, but is NOT the binding one |
| `pi_eu` | 74% | `probability_becoming_unemployed` | corr +0.06 over 7 values; the archive minimum IS the target, so it sits on a floor |
| `lambda_m` | 68% | `lambda_m` | **corr +0.002 over 13 values from 0.046 to 0.9. Dead.** |
| `cbar` | 60% | `max_food_cost` | corr +0.91, works cleanly, just mis-set |
| `h_2` | 50% | `smallest_house_size` | not in the block at all, so nothing is calibrating it |

**CORRECTED 26 AUGUST, BY CONTROLLED PROBES.** What follows below was read off
pooled archive medians and is wrong. Five probes, each moving one parameter off
the leader and nothing else, say:

| relative_share_of_addiction_1 | b (target 0.089) | lambda_d (0.0368) | ratio (needs 0.413) |
|---|---|---|---|
| 0.470 | 0.073 | 0.0054 | 0.074 |
| 0.485 | 0.107 | 0.0075 | 0.070 |
| 0.495 | 0.154 | 0.0129 | 0.084 |
| 0.505 | 0.217 | 0.0234 | 0.108 |

The user rate triples while the ratio barely moves, and h_1 blows up with it.
There is no window here: this parameter cannot deliver lambda_d at a valid b.

`lambda_addiction` can, and it was dismissed too early. Controlled, from the
leader to its own vertex:

| lambda_addiction | b | lambda_d | ratio |
|---|---|---|---|
| 3.54 | 0.0727 | 0.00538 | 0.074 |
| 4.95 | 0.0405 | 0.00370 | 0.091 |

d ln(ratio)/d ln(lambda_addiction) = +0.63, and d ln(b)/d ln(lambda_addiction)
= **-1.74**. So the hazard raises the ratio and pushes the user rate DOWN, which
is why it looked ambiguous in the pooled pairs: it moves both, in opposite
directions. That is exactly what makes it the right instrument once b is
compensated -- lower `addiction_scalar_1` at the same time and the user rate
comes back while the ratio keeps rising. The archive already holds one such
point: lambda_addiction 9.0 with addiction_scalar_1 0.0215 gave b 0.0767 and
lambda_d 0.0309, a ratio of 0.403 against the 0.413 wanted.

THE LESSON, WHICH IS THE ONE SECTION 7 KEEPS MAKING: a pooled correlation over
points that differ in everything is not evidence about an instrument. Both wrong
readings here -- that relative_share_of_addiction_1 had a usable window, and
that probability_becoming_unemployed was a dead lever at +0.06 -- came from
pooling, and both were overturned by a single pair that differed in one
parameter.

**Superseded, kept for the record: lambda_d is stuck on
relative_share_of_addiction_1, not lambda_addiction.** At
the leader's own `lambda_addiction` the share of users who become disordered
still spans 0.020 to 0.565 across points, which brackets the 0.413 the data
needs, so `lambda_addiction` is not what holds it. Against
`relative_share_of_addiction_1` the correlation is 0.913, and nothing else is
above 0.17. The catch is a cliff: median b runs 0.077 at 0.470, 0.220 at 0.498,
0.848 at 0.550 and 0.961 at 0.658. `lambda_d` reaches its target around 0.50,
by which point b is already 2.5 times its own. Closing it needs
`relative_share_of_addiction_1` and `addiction_scalar_1` to move TOGETHER, which
no single vertex of a multi-directional search can do -- it only appears after a
reflection combines directions. `theta` is 35 per cent low and shares the
instrument, so two of the five worst gaps want the same move.

### lambda_m IS reachable; the dead-lever finding tested the wrong parameter

**Retracted 26 August.** What follows below tested `lambda_m`, the chance of
recovering from SMI, against the SMI-share-of-the-homeless moment. That is not
the instrument. `suggest_next.OWNS` says the moment is bracketed by **`zeta_DI`**,
the disability payment, and it always did. Moving `lambda_m` and finding the
moment unmoved says nothing about whether the moment can be reached.

Controlled on the right parameter -- the simplex 4 base against its leader, which
differ in `zeta_DI` and nothing else:

| zeta_DI | lambda_m | h_1 |
|---|---|---|
| 0.0825 | 0.0413 | 0.00369 |
| 0.0250 | 0.0795 | 0.00385 |

d ln(lambda_m)/d ln(zeta_DI) = **-0.55**, and h_1 barely moves, so the homeless
population the share conditions on stays real. Extrapolated, 0.25 wants zeta_DI
near 0.0031, which is an eightfold move and has to be bracketed rather than
trusted -- but the lever is alive and the 70 per cent gap is attackable.

The same round mislabelled `h_2` as having no instrument in the block. It has
one: the Fortran sets `smallest_house_size` from
`smallest_rental_relative_to_lowest_income`, which is in the block, and OWNS
records the pairing. Controlled, d ln(h_2)/d ln(smallest_rental) = +0.80.

TWO MISLABELS IN ONE TABLE, BOTH THE SAME MISTAKE: a moment was matched to a
parameter by NAME rather than by reading OWNS. `lambda_m` the moment is not
`lambda_m` the parameter, and `h_2` is not owned by the variable it sets. OWNS
is the one place that states what a parameter brackets, and anything that
re-derives it by hand will eventually re-derive it wrong.

### Superseded: lambda_m is not reachable, and the loss already knows it

`lambda_m` at 0.50 and at 0.90 return the SAME moment, 0.044038, and they do it
where `h_1` is 0.000338 -- a homeless population of three in ten thousand
against a target of four in a thousand. Every one of the eleven archive points
that reaches `lambda_m` above 0.20 has `h_1` collapsed to 0.0004 or below. The
moment is only ever "hit" by emptying the population it conditions on.

`score_points.py` gates `lambda_m` on `h_1` and scores those as misses, so the
loss is honest and no leader has been bought this way. But the standing
position must be stated plainly: **a 25 per cent SMI share among the homeless
has never been produced at a valid homelessness rate**, and no arm will fix
that. It is a question about how SMI enters the homelessness loop in the
Fortran, and it wants a code investigation rather than another point.

### A conditional moment is refused until its population is real

Most of these targets are conditional — the disordered share of USERS, the
mental-illness share of THE HOMELESS, take-up among THE DISORDERED. While the
conditioning population is far from its own target the conditional moment is
measured over almost nobody, and calibrating against it moves a parameter for no
reason at all.

The case that produced the rule: lambda_m at 0.50 and at 0.90 returned the SAME
share of the homeless with mental illness, 0.0440, identical to seventeen
figures, against a target of 0.25. It looked like a parameter that saturates and
cannot reach its target. It was neither — homelessness in those points was 0.034
per cent, so the share was being read off almost nobody.

converge.py now refuses a reading whose conditioning moment is more than a factor
of three from its own target, and says which moment gated it. That is what
orders the calibration: b and the value of life first, then the homelessness
rate, and only then the eight parameters that live inside those populations.

### A round is not closed until the generation is accounted for

`converge.py --write` records the generation it emits in `code/GENERATION.txt`,
centre and arms both, and the next run checks each arm against the points on
disk and prints the ones that never came back.

This exists because nineteen of generation three's thirty workers came back with
NOTHING: their containers had no clone of the repository — "repo not found;
/home/user empty", "git clone denied by auto-mode classifier" — and they sat
blocked while the round read the result as "no pair". That is a statement about
the data, and this was a statement about the fleet. The centre itself was among
the nineteen, which is why almost every arm appeared to have no partner.

Two consequences, both standing:

- **The worker prompt clones the repository if the container does not have it**,
  and the session is created with `source_url` and `source_revision` set
  explicitly rather than inherited. A worker that still cannot find the repo
  says so in one line and stops instead of improvising.
- **Missing arms are re-run before the round closes.** A generation with holes
  in it does not produce a centre; it produces a smaller generation that has to
  be finished first.

### The sessions cannot be reused

A routine bound to an existing worker session, fired with `fire_trigger`, does
not wake it: the target sat idle for twelve minutes with no change of state, and
there is no `send_message` for these sessions. Each generation therefore creates
its own workers. They are tagged `simulations`, so `list_sessions` with that tag
is the roster of every point ever run.

## The round, start to finish

This is the whole procedure. A triggered check-in follows it without asking.

1. `git pull --rebase origin claude/two-period-addiction-hazard-d7gb61`
2. `python3 code/converge.py`. Its first line says how many of the emitted arms
   came back and names any that did not.
   - Arms missing and the generation is under forty minutes old: they are still
     solving. Change nothing, say nothing, re-arm for ten minutes, stop.
   - Arms missing and older than that: those workers failed. Re-run exactly those
     arms as fresh sessions, then wait for them. A generation with holes in it
     does not produce a centre.
3. `python3 code/ridge_solve.py` for the entangled pair.
4. `python3 code/converge.py --write`. This moves every parameter, re-centres
   run_one_point.sh, and records the new generation in GENERATION.txt.
5. Commit the new centre together with this file and push to the branch and to
   main.
6. Spawn one session per emitted arm, plus the centre. Every session:
   `source_url=https://github.com/srotberg/housing_first_children_later`,
   `source_revision=claude/two-period-addiction-hazard-d7gb61`,
   `tags=["simulations"]`, and the worker prompt above with the arm substituted
   and the commit message labelled `gen<N> worker: <arm>`.
7. Report to the author, in this order and every round without being asked:
   `python3 code/loss_history.py` first, because the loss between iterations is
   what they asked to see; then `python3 code/gap_table.py`; then the new centre.
   Never ask them to approve a round.
8. Re-arm for twenty five minutes and stop.

### What is being calibrated, exactly

The paper's table marks twenty four rows internally calibrated. Of those:

- **twenty two are free instruments the search sets**, every one of them reachable
  through the handover and given an arm by converge.py;
- **gamma is calibrated but tied**, at `0.28*(1-theta)`, so it moves when theta
  does and gets no arm of its own;
- **varsigma is not calibrated at all.** The table's Set column says internal, and
  the prose in the parameter list says the opposite: the three housing shares sum
  to one, so matching the smallest with h_2 and the largest with h_4 matches the
  middle as well, and a third instrument would have no moment of its own. The
  table and the prose disagree and the prose is right. THIS IS FOR THE AUTHOR TO
  FIX; do not edit the table without being asked.

Three of the twenty two were unreachable until 24 August: `max_food_cost` and
`mu_homeless` had no handover case, and `weight_on_child` had one but was absent
from the runner. All three own a targeted moment and were being carried at their
declared values while those moments were scored as misses.

### What a generation costs, and why it costs that

A generation is now about eighteen sessions, not thirty-seven. Three rules got
it there, and none of them slows the search:

- **The centre is a measured point, so one arm per parameter is enough.**
  Two-sided brackets were redundant from the start: the pair a secant needs is
  the centre and the arm. Bracketing both ways bought a second point on a curve
  the centre had already anchored, at the price of a worker session each time.
- **A parameter already within three per cent of its target gets no arm.**
  Re-measuring what is already known is the purest waste in the loop.
- **The arm's size is scaled to how wrong the moment is**, from a fifth of a step
  at ten per cent off up to the full factor of three at a hundred per cent or
  worse. A fixed factor barely moved the badly-wrong parameters and overshot the
  nearly-right ones.

THE CENTRE MUST BE SPAWNED EVERY ROUND. It is not one point among many; it is
the other half of every pair in the generation. Generation four's was forgotten
and every arm in it lost its partner.

## lambda and b are the second entangled pair

Measured 24 August, at lambda 22, sweeping b over six decades:

    b        users     disordered share
    1e-7     0.99995   0.893
    1e-4     0.99993   0.889
    1e-3     0.99987   0.885
    3e-3     0.99905   0.869
    1e-2     0.760     0.832
    (target) 0.089     0.413

Three things follow, and two of them contradict what was believed here before.

**lambda reaches the disorder share comfortably.** It overshoots: 0.89 against a
target of 0.413. The earlier reading that lambda had no traction was taken
entirely at lambda 1.5 and was worthless. The share runs 0.028 at lambda 1.5 and
0.89 at lambda 22, so the target is bracketed and the answer is near lambda 8 to
12.

**b does not need to be small.** Everything from 1e-7 to 1e-3 is a flat plateau
at essentially total use; going lower buys nothing. The cliff is between 0.01,
where 76 per cent use, and 0.038, where 0.0035 per cent do -- four orders of
magnitude of user rate across a 3.8-fold change in b.

**They must be solved together.** Each moves both the user rate and the
disordered share, exactly as b and the value of life do. A ridge in (lambda, b)
is being measured now at lambda 5.5, 8, 12, 16 and 22, with b set at each to put
the user rate on target, which gives the share along the ridge and so the lambda
that hits 0.413 with the user rate where it belongs.

## Judge a round by its centre, never by its luckiest arm

The best-loss column stayed near 0.48 for four rounds and looked like a search
that had stalled. It had not stalled; it was drifting. The CENTRE, which is the
vector the search itself chose, went

    gen 3   0.528
    gen 4   0.782      homelessness thirty-two times its target
    gen 5   0.795
    gen 6   0.856      the three hand-pinned parameters failed to compose

The best point in a generation is whichever arm happened to carry a lucky
combination, often one inherited from an older centre, so reporting it hid three
consecutive rounds of degradation. loss_history.py now prints the centre beside
it, and the centre is the number that decides whether a round helped.

RESET, 25 August, on the author's instruction. The centre goes back to the best
vector ever measured, loss 0.480, and the step is cut from a factor of three to
1.4 with a floor of 1.10. A step of three is what let size_homelessness cross its
cliff in one move at generation four and take homelessness to thirty-two times
target, and the two rounds after that inherited the wreck. Nothing measured is
wasted: generation six's arms still give a Jacobian, it is simply applied at a
point that is 0.48 rather than 0.86.

## Two things that make the step trustworthy

**The Jacobian comes from every nearby point, not from this generation's arms.**
A hundred and fifty-five measured points carry a full vector and a full set of
moments; the finite-difference assembly used one arm per parameter and ignored
the rest, so every round re-measured what the archive already held. That is what
made a round cost fifteen sessions. A weighted regression in log-parameter space
now fits all of them, ninety-seven within the kernel at the current centre,
which also removes the worse problem: an arm sized to how wrong a moment is
probes furthest exactly where the response is least linear, so those
"derivatives" were secants across the steepest part of a cliff.

**A step is held to what it promised.** The solve predicts the residual after the
step; the next round measures it. Their ratio is the trust-region gain: above
0.75 the linearisation is holding and both the step and the moment cap widen,
below 0.25 it is not and both tighten. Nothing else here can tell a wrong
derivative from a long step, and the two need opposite responses -- three rounds
of drift were treated as a step-length problem when the derivatives were the
thing at fault.

**The moment cap is the direct expression of "derivatives are off when far from
target".** The parameter step is bounded, but what matters is how far the
linearisation claims a MOMENT will move: a derivative measured where a moment is
two hundred per cent off says nothing about the whole distance home. No moment
may be predicted to move by more than the cap, which starts at 1.5 and earns its
width back only by making predictions that come true.

### lambda_m's moment carries the weight h_1 carries

The SMI share of the homeless was weighted one while the homelessness rate was
weighted two, and the search noticed. Two vertices of the initial simplex
returned an identical loss of 0.329 with that share at 0.095 and at 0.021, a
factor of five apart: the moment eta_DI exists to own was not disciplining
eta_DI at all, because a large miss on it cost less than a small miss on
anything weighted higher. It is now 2.0, the same as h_1. The level of
homelessness and its composition by mental illness are one claim seen from two
sides and the paper turns on both.

Re-weighting is cheap and safe here because no loss is stored anywhere:
score_points.loss is recomputed from code/points/*.txt on every call, and
simplex.py and jacobian.py both read score_points.WEIGHT rather than a copy. The
LEVELS of the new series are not comparable with the old, only the ordering.

What it changed: di_takeup=0.1 and max_food_cost were tied at 0.329 and are now
0.338 and 0.348, so the tie broke toward the vertex that moves the moment. The
only vertex whose loss FELL was addiction_scalar_1, whose SMI share of 0.185 is
the closest to 0.25 anything has reached.

Two typed copies of the weighting were found beside the dict they describe, in
score_points.py and gap_table.py, both still naming three moments at 2x after
lambda_m became the fourth. Both are generated from WEIGHT now.

gap_table.py's WHAT was a hand-copied second copy of suggest_next.OWNS and had
drifted the same way: it still listed lambda_m as a calibrated parameter and knew
nothing of di_takeup or smi_onset_level, so it died on KeyError the first time it
was run after the redesign. It is derived from OWNS now.
