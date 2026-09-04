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
