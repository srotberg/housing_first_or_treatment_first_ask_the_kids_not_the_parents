# Calibration state -- 5 September, 03:45

## THE ECONOMY RESTARTED AT rr_homeless_hold_age=64. FOUR POINTS, AND THE LOSS IS RISING

Like-for-like over the same 23 scored moments, in solve order:

    #  point         loss    worst   in 10%       M      rr
    1  85ec3e553f    4.81   115.7%    7/23    4.505   2.867
    2  31fafe39e7   12.34   276.8%    7/23    4.505   8.000
    3  05337a267d   14.57   283.8%    8/23    6.757   7.831
    4  8d1ce8987d   14.78   299.0%    7/23   10.131   7.667

## THE WALK ANCHORED ON THE WRONG SEED, AND THE CRITERION CANNOT SEE WHY

gaps.py ranks on the STAGE-0 set of 16 moments and picks 31fafe39e7 at 2.5879.
That point carries rr = 8.0, which drives h_share5 to exactly 0.00000 against
0.075 -- and h_share5 IS NOT IN THE STAGE-0 SET, so the ranking cannot see the
damage. On the full 23 moments 85ec3e553f (rr = 2.867) is better, 4.81 against
12.34. The loop is walking away from the better of its two seeds.

This is the same shape as every other fault tonight: a criterion evaluated over
one set while the consequence lands in another.

## M IS NOT A HARD INSTRUMENT, IT IS A SELF-DEFEATING ONE

The author asked how to make SUD households homeless, and whether M only works
once b is low enough. The four points answer both:

       M   addiction_scalar_1   lambda_d       b   kappa_ued   sud_homeless
   4.505             0.036226     0.0261  0.0695       0.277         0.0000
   6.757             0.035830     0.0011  0.0072       0.423         0.0003
  10.131             0.034183     0.0025  0.0128       0.566         0.0053
  target                          0.0368  0.0890       0.1625        0.2170

RAISING M DESTROYS THE POPULATION THE MOMENT IS A SHARE OF. b falls to a fifth,
lambda_d to a tenth, while sud_homeless creeps from 0 to 0.005 against 0.217.
Drug use is a CHOICE: make the disorder catastrophic for employment and
households stop choosing it. And M has overshot the one thing it does control --
kappa_ued 0.277 -> 0.566 against a target of 0.1625 -- so M should come DOWN.

THE AUTHOR'S READING ON b IS RIGHT AND THE MODEL SHOWS THE SELECTION. Use needs
consumption above a threshold, so users are selected RICH: band 1 users have
income 2.08 times average. Bands 2-4 users are poor, 0.40-0.46 of average, and
100 per cent of them carry the disorder -- but there are almost none. The SUD
rate by income band is 0.001-0.009 against data of 0.05-0.14, so the model has
one to two per cent of the disorder population the data has, at every income
level.

21.7 per cent of the homeless cannot carry a disorder when 0.25 per cent of the
population has one. THE LEVEL COMES FIRST -- lambda_d at -29 per cent and b at
-22 per cent, via lambda_addiction and a LOWER addiction_scalar_1, which drops
the consumption threshold and lets poor households into the user pool.
sud_homeless is a composition moment and cannot be reached before the population
exists.

## TWO THINGS PUT TO THE AUTHOR AT 03:45, BOTH OPEN

  1. Bring M down; its own moment says so.
  2. Re-anchor the walk on 85ec3e553f rather than the rr = 8.0 point.

## AND THE OLD-AGE SPIKE RELOCATED RATHER THAN CLEARING

With the hold at 64 the penalty reaches age 65 -- homelessness there falls from
0.008693 to 0.000062 -- but the mass reappears at ages 63 and 64, just below the
new boundary. The spike follows whichever age the penalty starts at. h_share5 is
now 0.0002 to 0.0000 against 0.075, so rr has overshot hard in the other
direction and 8.0 is far too high.

# Calibration state -- 5 September, 03:30

## THE PROOF: EVERY OLD HOMELESS HOUSEHOLD IS AT EXACTLY AGE 65

The author's mechanism -- *"the death penalty for the old will remove the old
from being homeless...and delta will remove the workers"* -- is right in logic
and blocked by one year of indexing. Three points at delta = 0.30 differing in
NOTHING but `rr_homeless_old_level`, age profile of the homelessness rate:

    age    rr=2.867     rr=4.0      rr=8.0
     63    0.000001    0.000001    0.000001
     64    0.000038    0.000038    0.000038
     65    0.008693    0.008693    0.008693
     66    0.000000    0.000000    0.000000
     ...
     85    0.000000    0.000000    0.000000

    f56a40b55d (2.867), 45083d5a07 (4.0), 81f55164ad (8.0)

Ages 66-85 are ALREADY EMPTY, so tripling the death hazard changes nothing at
any age to six decimals. The entire old-homeless mass is at age 65, and
`rr_homeless_hold_age=65` replaces the profile only ABOVE 65. The instrument
cannot reach its own population at any multiplier -- it is not too weak, it has
nothing left to act on.

AND THEY ARE NOT RETIREES. Retirement begins at `life_span-retirement_span+1` =
age_index 41 = data age 66, so age 65 is the LAST WORKING YEAR: no wage floor
behind it, no Social Security in front of it. The whole old-homeless population
sits in that one-year gap.

WHY THE RAY MISLEADS. y_h rising with delta is measured with rr held fixed, and
the author's objection is correct in principle -- in the joint calibration rr
should rise and clear the retirees. It cannot, for the reason above, so the ray
is measuring the mechanism with one half disabled. The ray is right about what
it measured and wrong as a guide to the mechanism.

THE FIX IS ONE INTEGER: `rr_homeless_hold_age` 65 -> 64, so the penalty covers
65+. Measured at fixed delta: band 5 0.0299 -> 0.0002, y_h 0.2614 -> 0.2458, h_1
barely moves. Cost: it is a CONFIG_SWITCH, so the 669 points measured at 65 stop
pooling and the archive restarts. THE AUTHOR'S CALL, still open.

## DELTA: THE RULING STANDS, FLOORED AT 0.01

Flipped to 'lower' on the ray and reverted the same hour -- *"no...delta is
moving in the wrong direction!"*. The ruling is the authority and the
measurement is a check; the flip broke that convention and it is restored.
Floored at 0.01 rather than 0 on the author's instruction, because a
proportional step cannot leave zero and a delta that reached it would be pinned
there whatever its gap did.

# Calibration state -- 5 September, 03:40

## THE DELTA RAY, CORRECTED -- AND A FABRICATED NUMBER IN A TABLE SHOWN TO THE AUTHOR

**The error first.** In the sorted gap table shown at 03:20 the y_h row was
printed by gaps.py as

    y_h  +275.4%  0.71707  0.19100  homeless_job_penalty_pp  0

and it was retyped by hand as `0.3025`, the LIVE TRACE value from a different and
still-unsolved vector. The best point `d0029f2b64` carries
`homeless_job_penalty_pp=0`; its moments are h_1 = 0.0035300, band 5 = 0.074176,
y_h = 0.717068. There is no point in the archive with delta = 0.25 and those
moments. The author caught it immediately: *"you showed me a delta of 0.25 with
y_h being 0.717, h1 giving 0.35% homelessness and h_share5 around 7.4%"*.

This is the rule against mixing points inside one table, broken in the smallest
possible way -- one cell -- and it made the model look as though delta did
something it has never done. A parameter value in a gap table comes from THE
POINT, never from the trace.

**The ray was also mis-built.** Its baseline was a delta=0.05 point differing from
the rest in TWELVE other coordinates. Rebuilt over six points identical in every
coordinate except delta:

    delta   tag              y_h        h_1    band1    band5
     0.00   43932f4d10    0.2614   0.004651   0.9080   0.0299
     0.05   2c40bae9b4    0.7105   0.002457   0.0120   0.0529
     0.15   a43cb9b416    0.7362   0.000299   0.1235   0.4465
     0.25   b24474cff8    0.7242   0.000153   0.0627   0.9354
     0.30   f56a40b55d    0.6892   0.000184   0.2003   0.7759
     0.55   59a64035ad    0.7250   0.000152   0.0603   0.9397
                 target   0.1910   0.003990            0.0750

The conclusion is unchanged and sharper: THE WHOLE MOVE HAPPENS BETWEEN 0 AND
0.05. y_h jumps 0.261 -> 0.711 on the first step, h_1 halves, band 1 collapses
0.908 -> 0.012. Everything above 0.05 is noise around a state already reached.

**And the death penalty cannot reach what is left.** At delta = 0.30, three points
with rr = 2.867, 4.0 and 8.0 are BIT-IDENTICAL -- y_h 0.6892, h_1 0.000184,
band 5 0.7759 (45083d5a07, f56a40b55d, 81f55164ad). `rr_homeless_hold_age=65`
puts the penalty on ages 66 AND UP while the model's old homeless are at age 65,
the last working year before Social Security starts at 66. So delta sweeps the
workers off, the remainder is unreachable, it becomes 90+ per cent of the
homeless, its income is Social Security, and y_h will not fall.

**The ruling to revisit.** The author said *"just keep the 65+ the way we have
been doing it"* after being told h_share5 was -1.1 per cent. That is true at
delta = 0 and false at every delta above it. The change is
`rr_homeless_hold_age` 65 -> 64, one integer; it is a CONFIG_SWITCH, so the 669
points measured at 65 stop pooling.

# Calibration state -- 5 September, 03:05

## y_h HAD NO LIVE INSTRUMENT AT ALL, AND THAT IS WHY IT SAT AT +275 PER CENT

Two separate faults, both silent, both now fixed.

**The two tables disagreed about which delta owns y_h.** `gaps.py` paired it with
`increased_prob_if_homeless` -- the SYMMETRIC multiplier, which the same file
declares exogenous at 0.2 four lines further down -- while `directions_table.py`
paired it with `homeless_job_penalty_pp`, the author's percentage-point,
separation-only form. `rules()` reads directions_table, so the WALK was right and
the REPORT was wrong; the table shown to the author named an instrument that owns
nothing. gaps.py now agrees with directions_table.

**A proportional step cannot leave zero.** `homeless_job_penalty_pp` was at
exactly 0 and the step is `adjuster * gap * |x|`, so it could never move however
large the gap. It read as a converged instrument rather than a pinned one -- the
same failure mode as a clipped bound, and harder to see, because the parameter
simply never appears in the trace's moved list.

Seeding it in `fixed_point_state.json` did NOT work, and the reason matters: the
loop warm-starts from the BEST ARCHIVE POINT, not from its own state file, so the
restart read `homeless_job_penalty_pp=0` straight back out of `d0029f2b64`. The
seed now lives in `fixed_point.py` as `SEED`, applied after the warm start and
only where the value is exactly zero, so it stops firing as soon as the archive
carries a real value. Confirmed live at 03:02:29:

    seeded homeless_job_penalty_pp at 0.25; a proportional step cannot leave zero
    it 1: homeless_job_penalty_pp 0.25 -> 0.275, gap +250.7%

## THE OLD AND THE WORKERS ARE CUT BY DIFFERENT INSTRUMENTS

The author's design, 5 September: *"the death penalty for the old will remove the
old from being homeless...and delta will remove the workers"*. That answers the
objection that raising delta pushes y_h UP by leaving retirees as the residual:
it only does so if the old are still there, and `rr_homeless_old_level` is what
stops that. The two are halves of one cut, not competing instruments, and y_h
falls because what is left after both is the poor.

It also means delta and `bottom_productivity_level` BOTH act on `emp_homeless`
(+109.9%, the binding moment): the productivity node owns it in the table, but
delta removes employed households from the street directly. Watch for the two
fighting.

## 65+ STAYS AS IT IS

`rr_homeless_hold_age` stays 65 on the author's instruction, *"just keep the 65+
the way we have been doing it"*. No archive partition; the 669 points measured at
65 keep pooling. At the best point `h_share5` is 0.0742 against 0.075, -1.1 per
cent, inside the band -- the 65+ share is not what is blocking the search.

The corner measurement behind that is in `directions_table.py`: at the calibrated
`rr` homelessness above age 65 is already exactly zero, so raising it removes
nothing (which is the whole of its inertness above 3.4), and dropping it to 1.0
puts 42-64 per cent of ages 66-70 on the street. It saturates below 1.5 too, so
the live region is 1.5 to 2.867.

# Calibration state — 4 September, 22:20

## h_1 IS NEAR-DISCONTINUOUS, AND THAT IS WHY THE SEARCH IS HARD

Ten points on the live economy, sorted by the homelessness rate:

         h_1   size_homelessness
    0.000407             0.41930
    0.004647             0.42224
    0.004590             0.42494
    0.000430             0.42726
    0.011550             0.43533
    0.008459             0.44371
    0.004651             0.44685
    0.004651             0.45000     target h_1 = 0.00399

h_1 is NOT MONOTONE in its own instrument and spans a factor of TWENTY-EIGHT
across a seven per cent band of it. From 0.41930 to 0.42224 -- a 0.7 per cent
parameter change -- homelessness multiplies by eleven; going UP again to 0.42726
divides it by eleven. Other parameters move between these points, so this is not a
clean ray, but no clean ray could produce a 28-fold spread over that band either.

THE CAUSE IS THE ONE ALREADY MEASURED FROM THE OTHER SIDE. Eighty-one per cent of
the model's homeless could pay rent from current income, so a mass of households
sits at indifference between the street and the cheapest rental and flips
TOGETHER on any small change. The housing choice is discrete; h_1 inherits that as
a near-discontinuity.

WHAT IT MEANS FOR THE SEARCH. The fixed point is not diverging, it is being
whipsawed: its SSR went 4.03 at the seed to 8.66 by iteration 7 while the BEST
point remained the seed, and size_homelessness is damped to half its adjuster
fighting what looks like overshoot and is actually a cliff. Damping cannot fix a
discontinuity -- no step is small enough -- which is the same conclusion reached
about rr_homeless_old_level earlier tonight, for the same underlying reason.

This is a property of the model, not of the solver, and what to do about it is the
author's call. The honest options are to accept h_1 as a moment that can only be
bracketed rather than hit, or to reduce the mass sitting at indifference -- which
means giving the street a cost that varies across households rather than one they
all face equally.

# Calibration state — 4 September, 21:50

## THE ECONOMY CHANGED TWICE TONIGHT. THE ARCHIVE IS ONE POINT.

Two model changes, both on the author's instruction, both verified as exact
no-ops at their default before anything was calibrated on them:

  max_age_to_choose_homelessness  59 -> 58, barring the street at data ages 84
                                  and 85. A config switch, so it partitions.
  homeless_job_penalty_pp         NEW. The street's labour-market penalty in
                                  PERCENTAGE POINTS: lose = pbu + delta, find =
                                  max(0, pbe - delta). Owns y_h.
  consumption_penalty_homeless    NEW, parked at 0 on the author's instruction.
  extra_job_loss_if_homeless      NEW, parked at 0; superseded by the pp form.

The live seed is 2c40bae9b4: size_homelessness 0.45, delta 0.05, cap 58.

    y_h            0.26142   target 0.191     +36.9%
    h_1            0.00465   target 0.00399   +16.6%
    emp_homeless   0.99230   target 0.46     +115.7%
    can afford     0.81343   -- was 0.995 this morning

## WHAT MOVED THE INCOME OF THE HOMELESS: size_homelessness, AND NOTHING ELSE

The separating 2x2, only two switches differing:

                              y_h   emp_hl       h_1   can afford
    size 0.343, no penalty  0.720    0.992   0.00308        0.995
    size 0.45,  no penalty  0.261    0.992   0.00465        0.813
    size 0.343, penalty A   0.714    0.996   0.00268        0.993
    size 0.45,  penalty A   0.260    0.999   0.00458        0.814

Raising the street from 0.343 to 0.45 of the cheapest rental takes the income of
the homeless from 0.720 to 0.261 and the share who could afford rent and sleep
rough anyway from 99.5 per cent to 81. The labour-market penalty on top of it
contributes 0.001.

THIS CONTRADICTS THE 04:00 FINDING, which recorded that raising size_homelessness
makes the homeless RICHER and OLDER. That was measured on the economy WITH the
age-84 spike in it and does not carry to cap 58. Do not act on it again.

## FOUR INSTRUMENTS MEASURED DEAD TONIGHT, each with a matched bracket

  rr_homeless_old_level      inert above 3.4 -- the ladder from 3.4 to 30 moves
                             every moment by under 0.05 per cent. The whole
                             old-age problem was ONE spike at data age 84, the
                             last age the street may be chosen, and it is an
                             end-of-horizon artefact: age 85 is terminal, so
                             mortality threatens a single final period. HELD at
                             the age-65 value on the author's instruction.
  increased_prob_if_homeless its two halves are a 1.3 point change in a small
                             probability and a 52 point change in a large one, a
                             forty-fold asymmetry inside one number. Raising it
                             swept the SMI and young off the street (-59 and -55
                             per cent) and moved y_h by 0.8. Back to exogenous 0.2.
  extra_job_loss_if_homeless loss side alone, 10 per cent against 20 per cent:
                             every moment moved by under 0.01 per cent.
  consumption_penalty_homeless abolishes homelessness entirely by psi = 0.3.

The common shape: every one of them DETERS someone from the street, so h_1 falls
and the composition barely moves. None of them draws anyone in. That is why the
author's prescription -- raise the penalty AND the street together -- is the only
form that can change composition rather than level.

## THE OPEN MOMENT IS emp_homeless

0.992 against 0.46, and it has not moved for any instrument tried today. The
model's homeless are low-productivity EMPLOYED households, not unemployed ones.
Its owner is bottom_productivity_level, whose own entry in directions_table says
the ray reverses, it is near-flat, and the parameter sits ON its lower bound. The
author has asked to keep it there for now. If it has not moved by morning, the
parameter is the thing to revisit, not the moment.

# Calibration state — 4 September, 20:25

## THE OLD-AGE SPIKE IS ONE AGE, AND THE FIXED POINT HAS ALREADY CLOSED IT

Homelessness by age at point_aa0c0bd2f9 (cap 59):

    age 65        0.009996
    age 66 to 83  0.000000     eighteen consecutive zeros
    age 84        0.012926
    age 85        0.000000

It was never a distribution over the retired. It is a single spike at data age
84, the last age a household may choose the street, and age 85 is terminal
(survival is exactly zero there). A household homeless at 84 is buying one final
year of saved rent against a higher chance of losing one final year of life.

THAT IS WHY MORTALITY CANNOT REACH IT. rr_homeless_old_level runs the ladder from
3.4 to 30 -- values at which death at 84 is capped at probability ONE -- and every
moment moves by less than 0.05 per cent. The prize the risk threatens is a single
terminal period, and the rent saved beats it at any multiplier.

## BARRING AGES 84 AND 85 WORKS, BUT OVERSHOOTS

Matched pair, same vector, only max_age_to_choose_homelessness differing:

              band1    band2    band3    band4    band5      h_1
    cap 59  0.00702  0.90792  0.00005  0.04804  0.03697  0.003198
    cap 58  0.00728  0.94169  0.00006  0.04983  0.00114  0.003084
    data      0.260    0.272    0.210    0.184    0.075  0.003990

The spike is gone and, CONTRARY to what the addiction cap measured earlier, it
does NOT relocate to 83: ages 66 to 85 are all zero and the mass reappears at 63
to 64. "The spike follows the cap" is true of the addiction cap and false of this
one; the note in the declaration should not be read as covering both.

But band 5 goes from -51 per cent to -98.5 per cent, so it abolishes old
homelessness rather than sizing it, and h_1 slips from -20 to -23 per cent.

And it may not be needed: at cap 59 the fixed point took band 5 from +910 per cent
to +8.4 per cent in two iterations, unaided (point_aa0c0bd2f9, 0.08128 against
0.075).

## THE COMPOSITION FAULT HAS MOVED TO BAND 2, AND IT IS NOT A MORTALITY MARGIN

Band 2 (ages 35 to 44) holds 91 per cent of the homeless against 27 in the data.
Set against Baggett's measured relative risks, which the model uses verbatim below
age 65:

     age  Baggett rr  model uses  homeless rate
      34       9.100       9.100       0.000042
      35       8.985       8.985       0.027992
      41       7.605       7.605       0.016301
      42       7.375       7.375       0.000010
   45..62   6.7 -> 3.6        same      0.000004
   75..85       1.100       2.939            0

Two things follow.

THE SPIKE SITS WHERE MORTALITY IS HIGHEST. Ages 35 to 41 carry a relative risk of
9.0 falling to 7.6 and hold nearly all the homelessness; ages 45 to 62 carry 6.7
falling to 3.6 and hold none. There is no deterrence gradient in the profile, so
RESHAPING THE DEATH RISK BY AGE IS UNLIKELY TO MOVE IT -- the same way it did
nothing at 84 -- and it would spend the one part of the calibration that is
externally identified.

THE EDGES ARE THRESHOLDS, NOT MARGINS. Homelessness goes from 0.000042 at 34 to
0.027992 at 35, a factor of 670, and from 0.016301 at 41 to 0.000010 at 42, a
factor of 1600. A smooth trade-off against mortality cannot produce that. Find
what switches at 35 and at 42 before moving the age structure.

Note also that above 65 the model already runs at 2.939 against Baggett's 1.100,
2.7 times the measured value.

# Calibration state — 4 September, 19:55

## THE AUTHOR'S METHOD HAS OVERTAKEN NELDER-MEAD, ON NELDER-MEAD'S OWN OBJECTIVE

Six iterations of the damped fixed point, with the hold rule and the oscillation
damping both live, from a start at core-12 2.4599 / all-21 112.73:

    af5640fa89   core-12 0.1429   all-21  3.83    9 of 21 inside ten per cent
    938152d1c3   core-12 0.2354   all-21  9.46    8
    1d5780203b   core-12 0.1266   all-21  3.80   10

    NM best      ce9e6d2e03   core-12 0.1338   all-21 108.01   11

`1d5780203b` is better than NM's best on the TWELVE MOMENTS NM ACTUALLY SCORES
(0.1266 against 0.1338) and twenty-eight times better on all twenty-one. Six model
solves against roughly two hundred.

The reason is not that the fixed point searches better. It is that NM's stage-1
objective is the core twelve, so nothing charges it for what it does to the other
nine, and it has run `h_share5` out to +1022 per cent. The fixed point never
scores anything, but it updates all twenty-one from the direction rules, so it
cannot buy one moment by ruining another.

**The open question for the author: is NM still worth a container?** Its own
answer is now dominated. `STAGE_MOMENTS` being 12/4/5 is their call and stands
until they rule.

## THE HOLD BAND IS NOW STICKY, AND THAT WAS THE AUTHOR'S DIAGNOSIS

They said, 4 September: *"maybe the right way is to push them into the rule when
they pass 10%, and then only start updating them again when they leave 15%"*, and
*"so it's not so much in and out"*.

They were reading the held counts, which went 12, 9, 9, 8, 10, 9 across the run --
parameters leaving the band as fast as they entered, so something essentially
converged kept moving and kept injecting cross-effects. One threshold in both
directions makes the band a revolving door.

Both searches now hold at ten per cent and release at fifteen. `hold_test.py`
(fixed point) and `hysteresis_test.py` (Nelder-Mead) each walk one gap across the
line and count state changes: eight to two, and four rebuilds to one.

THE NUMBER HELD SHOULD NOW TREND UP. If it does not over the next several
iterations, the sticky band is not enough to break the coupling and that is worth
telling the author rather than burying.

## DAMPING, AND WHY IT WAS NEEDED

Ten undamped iterations put `rr_homeless_old_level` in a period-two limit cycle:
2.7102, 2.9813, 2.6853, 2.9538, 2.6656, 2.9322, 2.7167, 2.9884 -- every step
exactly ten per cent of the value, every step reversing the last, one model solve
per bounce. Each adjuster is now scaled by whether that parameter's own residual
changed sign, halved on a flip, relaxed back on a sign that held, floored at an
eighth. Live scales at last check: `rr_homeless_old_level` 0.75,
`bottom_productivity_level` 0.5, `kappa_uem` 0.25.

## THE HOMELESSNESS BLOCK IS PARKED BY THE AUTHOR

*"those homelessness things will be fixed later"*, 4 September. `h_share5`, `h_1`,
`sud_homeless`, `emp_homeless` and `lambda_m` are all downstream of the same
composition fault -- the model's homeless are 84 per cent aged 65-plus against 7.5
per cent in the data, and 88 per cent of them could afford rent on income alone.
Do not chase any of them with the current instruments and do not read their gaps
as evidence about the search.

## RESTARTS COST MORE THAN THE CORRECTIONS THEY CARRY

Nine sessions between 17:09 and 19:52; only one ran long enough to produce more
than a couple of solves. Each restart costs about eleven minutes before the first
iteration lands. The state file and the points are pushed every iteration, so a
restart loses no TRAJECTORY -- a new session on the worker branch resumes from
`fixed_point_state.json` -- but it loses the setup time every time. Batch
corrections; do not restart to carry one.

Two failure modes seen tonight, both mine:

  - a brief that asserted a SNAPSHOT (`must print iteration 3`) went stale within
    ninety seconds because the run advanced. Assert an invariant instead
    (`it >= 3`), never a current value.
  - `create_session` does not reliably attach the repository: fp5 came up with no
    checkout at all and stalled. Pass `source_url` explicitly.

# Calibration state — 4 September, 19:35

## THE LIVE BEST, AND WHY ONE NUMBER IS NOT ENOUGH

The archive holds 215 points on the current model hash. Two searches are running
and they are best on DIFFERENT objectives, so a single "best" line would be a
lie:

    Nelder-Mead   ce9e6d2e03   core-12 SSR 0.1338   all-21 SSR 108.01   11 of 21 inside 10%
    fixed point   28e401cb4c   core-12 SSR 0.2130   all-21 SSR   3.76   11 of 21 inside 10%

NM wins the twelve moments it SCORES and loses the twenty-one by a factor of
twenty-nine, because stage 1's objective is the core twelve and nothing stops it
wrecking the other nine. It did: `h_share5` is at +1022 per cent at NM's best.
The fixed point scores none of them but updates all twenty-one from the direction
rules, and keeps them bounded. It reached the same eleven-inside in NINE model
solves against roughly two hundred.

**This is the case for opening stage 1's objective to all twenty-one moments.**
`STAGE_MOMENTS` is 12/4/5 and marked frozen as the author's call, so it stands
until they rule.

The earlier line in this file -- `point_8c42b1f32a`, SSR 2.9430, 7 of 20 -- is
superseded and kept below only for the structural finding it carries.

## pi_eu IS RESOLVED

It was never a flow. It is the unemployment RATE, u = s/(s+f), and only s is an
instrument: `probability_becoming_employed` is hard-coded at 0.55. Reaching the
old 13.9 per cent target required every SMI worker at every productivity node to
be unemployed with probability one, because `min(pbu*kappa_uem,1)` saturates at
pbu = 1/49.05. The author retargeted to U-3 at 4.9 per cent, and the moment now
reads **+1.8 per cent** at the live best, from +66 per cent this morning.

## THE HOLD BAND IS LIVE ON BOTH SEARCHES

The author, 4 September: *"every time a parameter gets into the 10%, you hold it
fixed, and do the projections, shrink, etc, based on the ones that are outside
the 10%"*.

  fixed point  a parameter whose own moment is inside ten per cent is not
               updated, and is released the moment it drifts back out.
  Nelder-Mead  `nelder.setup()` drops held instruments from the simplex,
               `scope()` seeds only the live ones, and `stage_night` rebuilds the
               moment the live set shrinks. Currently FOUR of twelve: cbar, p_m,
               sigma_y, tau_l.

`keys` stays the whole objective in both, so a live parameter cannot buy its own
moment by pushing a held one out of the band.

## THE FIXED POINT NEEDED DAMPING, AND IT IS MEASURED

Ten iterations put `rr_homeless_old_level` in a period-two limit cycle -- 2.7102,
2.9813, 2.6853, 2.9538, 2.6656, 2.9322, 2.7167, 2.9884 -- every step exactly ten
per cent of the value, every step reversing the last, three minutes of solve per
bounce. Each adjuster is now scaled by whether that parameter's own residual
changed sign: halved on a flip, relaxed back on a sign that held, floored at an
eighth. `damp_test.py` checks it against the two measured sequences.

## max_age_to_choose_homelessness IS 59 IN THE LIVE ARCHIVE

The line further down saying all 43 points carry 45 is out of date: it is a
config switch now, the live value is 59, and the current best carries 59.

# Calibration state — 4 September, 04:00

## THE STRUCTURAL FINDING OF THE NIGHT: THE LEVEL AND THE COMPOSITION FIGHT

At `point_8c42b1f32a`, SSR 2.9430, 7 of 20 inside ten per cent:

    h_1 on target (+11.6%)  requires size_homelessness 0.2925, sevenfold up
    and at that value    old band = 0.8887 of the homeless, spike at age 84

    h_1 at 30 per cent of target (size_homelessness 0.0425)
    and at that value    old band = 0.0001 of the homeless, spike at age 33

**Neither the mortality hold nor the search can resolve this.** Making the street
big enough to hit the homelessness rate makes it attractive enough for retirees
again, and the age-65 hold no longer keeps them off. The two requirements pull in
opposite directions along the one instrument that sets the level.

The reason is the one measured earlier: for a retiree, three of the four costs of
the street are structurally zero -- no job to lose, mostly no disorder to fail to
recover from, and almost no continuation value for mortality to threaten --
leaving only the foregone housing service, which `size_homelessness` is exactly
the parameter that shrinks. So raising the level to fix `h_1` necessarily buys
back old-age homelessness.

**What would resolve it** is a cost of the street that binds on a retiree: a
morbidity state, which the author has already proposed and parked. Nothing in the
current instrument set can do it, and this should not be chased further with the
existing parameters.

## THE SEARCH, AND WHY BOTH METHODS ARE ON THE SHELF

`nelder_test.py` drives the real Nelder-Mead state machine against known minima:

    quadratic bowl, 20-dim   1200 evals   1.2e-09   PASS
    Rosenbrock,      8-dim    900 evals   4.6e-14   PASS
    Rosenbrock,     20-dim   3000 evals   0.187     FAIL

The implementation is right; the method is weak at this dimension on a curved
objective. But it HAS improved: the shrink took 3.1555 to 2.9430, so it is not
stuck, and the author's call is to let it run overnight and assess in the
morning. `code/overnight.sh nm` does that -- restarts the loop if it dies and
pushes every five minutes.

`code/sweep.py` is the alternative, written and ready but NOT running: measured
coordinate brackets on all twenty instruments per round, assembled with damping
and accepted only against a measurement. Switch with `bash code/overnight.sh
sweep` after stopping the current driver. THE TWO MUST NOT RUN TOGETHER on one
container -- run_one_point.sh writes PARAM_HANDOVER.txt in `code/`, so two
solvers interleave their handovers and each measures the other's vector. That
happened once tonight and was caught within a minute.

## IN FLIGHT ON THE FLEET

- **size_homelessness 0.07 to 0.22**, to find where h_1 reaches 0.00399 from
  0.00121. Measured already: 0.0425 to 0.0560 raises h_1 by 45 per cent and
  leaves the age composition untouched, so the young dominance is NOT an
  artefact of the level -- the author's hypothesis, measured false.
- **M from 6 to 40**, testing the author's claim that a large enough SUD
  employment penalty must lift sud_homeless off zero. The penalty keys on
  d_f_1>=1, the DISORDER state rather than consumption, so the mechanism is the
  right one. Watch for sud_homeless staying at EXACTLY zero, which would mean no
  disorder-holder reaches the street by any route and no value of M helps.

Young and old composition is parked on the author's instruction: *"i think we
can deal with the young homelessness later if needed"*.

## THE MORTALITY HOLD IS LIVE AND THE AGE PROFILE HAS FLIPPED

`rr_homeless_hold_age = 65`, on the author's instruction: *"i think we can just
hold it at the 65 number.... and say that.... that would fix it"*.

**The sentence for the paper.** The model holds the relative risk of death from
sleeping rough at its age-65 value for all older ages, because beyond 65 the
observed ratio is dominated by survivor selection and does not identify the
causal effect the model needs. The homeless who reach 65 are unusually robust
and the comparison group includes the frail and institutionalised, so the
observed ratio is biased toward one; read literally Baggett's 1.1 at 65-84 says
the street PROTECTS the old, which is why the code floors it at one.

Sixty-five is where the ratio stops being USABLE, not where it stops being
measured. The 1.100 above 75 is Baggett's own 65-84 figure extended past its
band midpoint at 74.5 — an earlier note here calling it padding was wrong.

| | before (hold 70) | now (hold 65) | data |
|---|---|---|---|
| young band, share of the homeless | 0.1117 | 0.8589 | 0.2600 |
| old band, share of the homeless | 0.8821 | 0.0001 | 0.0750 |
| retired 66+ share | 88.2% | 0.0% | — |
| spike | age 80, 71.9% | age 33, 47.7% | — |

The age-80 spike is gone. It now overshoots the other way, and both errors are
large, but homelessness is at working ages where the employment deterrent
actually operates.

**THE RESPONSE SATURATES ABOVE A MULTIPLIER OF ABOUT 2.7.** Measured at one
vector: hold 70 gives an old share of 0.882, hold 65 gives 0.0003, hold 45 gives
0.00024 and hold 26 gives 0.00021. Nothing is bought by going below 65, so 65 is
the cheapest point on the plateau — the best place to sit for a number that has
to be defended.

**A moment the hold broke.** `sud_homeless` is now EXACTLY zero: no homeless
household carries the disorder. The old homeless were meeting that moment — 18.9
per cent of them had SUD — and removing them removed it. That is the worst gap in
the table at −100 per cent and the reason SSR reads 3.16 here against 1.46 on the
old economy. It is the objective correctly registering a moment that used to be
met by the wrong population.

## THE CONFIGURATION, unchanged

    number_of_beta_types  1          one beta for everyone
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor
    newborn_endowment_scale  0.0     HELD at zero by the author
    homeless_death_risk_flat_in_age  0   the Baggett age profile

Model hash **b2530947f0**, 117 points. The 22:00 cap patch (`4df7be4132`, the
street barred at `max_age_to_choose_addiction`) was **REVERTED** on the author's
instruction — *"You should revert to allow the 80 year olds to be homeless
again"* — and its points are orphaned. Any earlier section of this file that
describes that economy as live is out of date.

## THE SEARCH

**Twenty instruments**, all stages unioned. Of the 23 parameter/moment pairs in
`next_batch.OWN`, three are out and each for a different reason:

| parameter | moment | why it is out |
|---|---|---|
| `weight_on_child` | `omega_c` | held: *"since omega_c is so close, just keep it fixed for now, we can adjust it at the end"* — it reads 0.1622 against 0.1834 |
| `newborn_endowment_scale` | `h_share1` | the author holds it at 0 |
| `ssi_floor_level` | `h_share5` | the author holds the floor to the 2024 federal rate |

### Three scorer bugs found on 4 September, all fixed

1. **`sud_homeless` was never parsed.** The model prints
   `UNTARGETED SUD share of the homeless` on every point ever solved and
   `gaps.py` had no pattern for it, so its instrument
   (`multiple_of_probabilities_of_employment_if_addicted`) looked like a
   parameter with no moment and sat outside the search. It reads 0.1166 against
   Gutwinski's 0.217. Now scored retroactively on all 155 points, no model time.

2. **`omega` vs `omega_c`.** The Fortran prints `MOMENT omega`; `OWN` calls it
   `omega_c`. Even with `measure_child_gap=1` the scorer would have filed it
   under a key nothing reads. Aliased, so `omega_c` will work first time when it
   is taken up at the end.

3. **`archive()` enforced ONE config switch out of the table.**
   `homeless_death_risk_flat_in_age` was added to `CONFIG_SWITCHES` on
   4 September and had no effect at all: the two points solved with the flat 1.6
   mortality multiplier POOLED with the 150 solved on Baggett's age profile and
   were ranked against them as one economy. All switches enforced now, with a
   point predating a name falling back to the Fortran's compile-time default
   rather than the live value.

### `measure_child_gap` costs 9 per cent, not 100

Reported here first as a doubling, because the block runs a second solve and
converge. Measured on the same vector: **4m06s off, 4m30s on**. The
counterfactual starts from the converged baseline distribution. It is off again
because `omega_c` is held, and turning it off restores the archive: it is a
CONFIG SWITCH, so with it on exactly one point pooled and the simplex needed
twenty-two fresh solves to rebuild.

### The tension in `M`, worth knowing before it is spent

`multiple_of_probabilities_of_employment_if_addicted` is the SUD employment
penalty on both margins — job loss `× M`, job finding `÷ M`. Its target is
`sud_homeless`, which wants it UP. The moment it controls mechanically,
`kappa_ued`, is an untargeted OUTPUT on the author's own instruction
(*"we don't truly know what they are so we calibrate them"*) and already reads
0.2217 against 0.1625, **36 per cent high**. Closing `sud_homeless` drives
`kappa_ued` further from its data counterpart. Offered to the author on
4 September and NOT reversed: `kappa_ued` stays an output.

    simplex complete, 20 vertices
    best      827aa52172   SSR 2.1441
    worst vertex           SSR 19.0389   (the smi_onset_level fill)

## PARKED BY THE AUTHOR

- **Young and old homelessness.** *"Ignore young and old homelessness for now. We
  will fix that later."* `h_share1` and `h_share5` are UNSCORED. The best stage-0
  point puts 87.0 per cent of the homeless in retirement against 25.5 per cent of
  the population, spiking at age 80.
- **The flat 1.6× mortality multiplier** (`homeless_death_risk_flat_in_age=2`) was
  measured as a matched pair, `047afb7487` → `d2e58e6afb`: retired share 0.8 → 0.0
  per cent, SSR 3.0511 → 3.0636. **That test does not answer the question it was
  set**, because at that vector the spike was already at age 26, not 80. It would
  have to be rerun at `9a9c749a75` to learn anything.
- **The morbidity state.** *"keep calibrating the rest and we'll deal with
  morbidity later"*. Evidence scan is in `data/MORBIDITY_EVIDENCE.md`.
- **The newborn endowment double count**, two options offered, no decision taken.

### The seed only ever displaced UPWARD, and it cost `sigma_y` the whole search

Found 4 September, 14:45. `stage_night.seed()` built every vertex as `x + d`.
Across **1245 archived points, `kkk_sigma_scale` was never once measured below
its anchor value 2.20949**, against a lower bound of 0.8. The one clean matched
pair -- kkk alone, 2.20949 -> 3.09114 -- takes `sigma_y` from 0.10337 DOWN to
0.03536, and `sigma_y` has to RISE from 0.103 to 0.172. The search had never
sampled the direction the instrument needs to go, which is why the moment looked
frozen at -40 per cent through every restart.

Fixed by alternating the sign across instruments so the initial simplex straddles
the anchor. Nelder-Mead does reach both sides on its own, by making the up-vertex
the worst and reflecting through the centroid, but that costs solves and moves
every coordinate at once.

**The general lesson: a seeded simplex that is one-sided is not a simplex around
the anchor, it is a simplex in one orthant.** Check the sign coverage of any
seeding rule before trusting a moment that will not move.

### `pi_eu` is weakly handled by its own instrument

Matched pair, 4 September: `probability_becoming_unemployed` 0.0122 -> 0.0173777
(+42 per cent) moves `pi_eu` 0.08001 -> 0.08491, **+6 per cent, elasticity 0.15**
-- below the 0.27-0.51 measured earlier, so the elasticity is falling as pbu
rises. Closing a 74 per cent gap at that slope needs pbu near 0.075, six times
its value. It is inside the bounds (1e-06, 0.5) so it is reachable, but not at
this step size.

`pi_eu` is NOT structurally capped near 0.08: `6624095c1b` reaches 0.1407 and
`c35f6e74a9` reaches 0.1834. **Both are confounded** -- each carries
`discount_factor` pulled to 0.9075/0.92625 from 0.945 AND the invalid
pre-guard `rr_homeless_old_level = 0`, at SSR 53 and 164. A lead to test, not
evidence: the clean test is `discount_factor` alone at the current anchor.

### THE SEARCH WAS ON THE WRONG ECONOMY FROM 13:18 TO 15:00

`max_age_to_choose_homelessness` bars the homelessness choice above an age index:
45 is "nobody over 70 can be homeless", 59 is "nobody over 84 can be". Those are
two models of old-age homelessness. It is a HANDOVER parameter, so it moves
neither the source hash nor the semantic hash, and it was not in CONFIG_SWITCHES,
so nothing separated them and `best()` ranked all of them as one economy.

The cap-walk batches (`batch_capwalk.txt`, `batch_cw_01.txt`) carried 45. The
model change at 13:18 emptied the archive; the first points on the new hash came
from that batch; a 45-point won the pooled ranking; `stage_night` took it as the
anchor and the seed copied 45 into all eleven vertices. **The retired share
reading 0.0 per cent of the homeless was MECHANICAL, not behavioural.**

Now a CONFIG SWITCH, live 59 per the author (*"Make sure you allow homelessness
at age 84-85 still"*), PREDATE 59 (the Fortran default at line 509). This EMPTIES
the live archive: all 43 points on the current model hash carry 45.

### THE COORDINATE SCAN REPLACES THE SEEDED SIMPLEX AS THE WAY IN

The author, 4 September: *"all parameters should be sampled across many values so
they have a range to go off of"*, and on `sigma_y`: *"since share of income is too
low for bottom 50%, it means probably that sigma_y needs to be lower... Not
higher. You need to extend it from below"*.

`code/scan.py` writes one batch file per instrument, seven values spanning a wide
range inside the hard bounds, everything else at the anchor, on the 59 economy.
21 instruments, 139 points. `kkk_sigma_scale` now spans 0.8 to 4.0.

`weight_on_child` is left out: `omega_c` is held and `measure_child_gap` is off,
so its moment is not measured on these points.

**`bottom_productivity_level` cannot be scanned downward**: its anchor 0.004 IS
its lower bound, so the scan only samples up. That is a bounds question for the
author, not a scan defect.

`night_watch` takes a `code/PAUSE_NM` marker so the scan owns the CPU while the
pusher keeps committing. Remove it to resume Nelder-Mead, which should then seed
from a spanning archive rather than a one-sided simplex.

### FOUR WAYS TO SEARCH TWENTY-ONE PARAMETERS, AND NONE OF THEM WORKS

Measured 4 September with `code/stage_test.py`, Rosenbrock at 21 parameters, same
total budget, every method graded on all 21 moments at the end:

    method                                   900 evals   3000 evals   vs one-shot
    ONE SHOT, all 21 open                      7.61696      4.42097      --
    STAIRCASE 12 -> 16 -> 21 (cumulative)      9.37109      8.51109      1.93
    LADDER, block-only objective               9.86351      9.86351      2.23
    LADDER, full objective, 12/4/5 blocks      9.40621      6.28463      1.42

**The block-only ladder is unchanged to six figures between 900 and 3000
evaluations.** Not slow -- FROZEN. While block 2 is open nothing scores block 1's
moments, so block 2 wrecks them for free, block 1 undoes it, and the cycle closes
exactly. Reading the author's *"open only stage 2"* literally would have spent a
night going nowhere with a busy-looking trace.

The full-objective form -- all 21 moments always scored, only the block of
PARAMETERS allowed to move changes -- does progress, 9.41 -> 6.28. That is the
difference between a method that moves and one that is precisely stuck, and it is
the form to use if a ladder is used at all.

**But the tolerance is 1e-3 and the best of four is 4.42. Every one of them
fails.** The ranking is a ranking of failures.

### WHAT THE MEASUREMENTS ACTUALLY SUPPORT

    dimension   Rosenbrock       verdict
    4           0                PASS
    5           6.42e-14         PASS
    12          5.22e-13         PASS      -- twelve orders inside tolerance
    21          4.42             FAIL

Twelve works and is not marginal. Twenty-one does not work by ANY arrangement
tried. So: **search the twelve, measure the rest.** `expand.py` bracketed
`sigma_y` (crossing in kkk 1.5..2.2095) and `tau_l` (crossing in 0.718..0.827)
from rays alone, with no optimiser -- brackets do not care about dimension,
curvature, or the discrete choices that make the model's moments jump.

The author's premise was right and is what the evidence supports: never search
twenty-one. What the evidence adds is that the answer to *"then what searches the
other nine"* is *nothing does -- they get measured one at a time.*

**PRODUCTION IS STILL THE CUMULATIVE STAIRCASE**, which measured 1.93 times worse
than one-shot, and its stage 3 opens all 21. That has to change before stage 1
promotes. It has not been changed yet because which way to change it is the
author's call, and the choice is between the full-objective ladder and dropping
the search past stage 1 entirely in favour of brackets.

### A RAY IS A PARTIAL DERIVATIVE, AND THE PAPER'S ECONOMICS IS NOT

The author, 4 September: *"your rays are not correct because they are not based on
the economics of the paper"*. They are right, and it invalidates a day's worth of
conclusions drawn from `scan.py` and `expand.py`.

Every ray holds the other twenty parameters PINNED. In this model the parameters
are jointly identified -- `M` only means anything alongside `b`, `kkk_sigma_scale`
alongside `discount_factor` and `max_food_cost`, the housing block alongside the
income distribution. A ray freezes exactly the adjustment that constitutes the
mechanism.

**`M` IS THE PROOF.** Its ray reads slope -1.2e-07 on `sud_homeless` across the
whole range 1 to 32, which is arithmetically right and economically empty: with `b`
held, raising `M` does not punish addiction, it ABOLISHES it -- the disorder rate
collapses 34-fold between M=4 and M=5.66. With `b` free the pair is a different
object entirely. The author saw it in one line after the ray had been treated as
evidence for hours.

WHAT IT INVALIDATES, listed rather than left to surface later:

- "M is a dead instrument" -- wrong, corrected.
- "mu_homeless does nothing to sud_homeless" -- same defect.
- "bottom_productivity_level moves emp_homeless by two parts in a million" -- same.
- "rr_homeless_old_level's ray reverses" -- measured with the income distribution
  pinned, and that distribution decides who sits near the homelessness margin.
- "kkk_sigma_scale crosses sigma_y at 1.63" -- measured with beta and cbar frozen,
  both of which then broke by 20 and 13 points when kkk moved. The joint crossing
  is elsewhere.
- EVERY ADJUSTER MAGNITUDE, since size_adjusters.py derived them from ray
  crossings. The signs survive; the distances do not.

WHAT RAYS ARE STILL GOOD FOR: a sanity check on DIRECTION, and a warning when a
moment does not respond at all. Not magnitudes, and not proof that an instrument is
dead.

AND EVEN SIGNS NEED THE ECONOMICS. `b`'s sign was got wrong in both directions on
the same day: the author ruled it from the name, the measured ray disagreed, the
ray was dismissed as "a cliff, unusable", and the Fortran's own comment at line 1485
-- *"the marginal value of the first unit is theta/b, so participation FALLS in b"*
-- settled it against both. Three sources, and only the one nobody consulted was
right.

THE CONSEQUENCE FOR METHOD. The fixed point moves all twenty-one parameters from a
single solve, so its trajectory IS the joint response and it never forms a partial
derivative. Nelder-Mead likewise. That is a better argument for both than any made
earlier today.

## OPEN WITH THE AUTHOR

Nothing is blocking. The loop runs to 400 iterations and commits every twelfth.
