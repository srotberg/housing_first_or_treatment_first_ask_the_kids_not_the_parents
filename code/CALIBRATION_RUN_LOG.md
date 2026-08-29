# Calibrating the quantitative model: a running log

This file is the record of the current calibration run of
`housing_first_or_treatment_first_SR_v1.f90`. It exists because the container is
ephemeral: checkpoints, logs and the binary do not survive a restart, and the
last run's state was lost that way. What is established goes here, in git.

## The run

Started from the declared parameter values (`no calibration_state.dat`), which
is the right start rather than a resume: the rental ladder was retargeted since
the last run and the adjusters' stored gap history would be stale, and the
curvature's update changed sign.

```
cd code
gfortran housing_first_or_treatment_first_SR_v1.f90 \
    -mcmodel=medium -fopenmp -O2 -ffree-line-length-none -o hftf
ulimit -s unlimited
export OMP_NUM_THREADS=4 OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1
./hftf
```

`GFORTRAN_UNBUFFERED_ALL=1` is not optional for a watched run. gfortran block
buffers stdout, so without it the log is silent for minutes at a time and a
healthy run is indistinguishable from a hung one. A whole session was spent
once diagnosing a run that was fine.

Configuration of this run: benchmark steady state (`is_counterfactual=0`,
`solve_transition_dynamics=0`), general equilibrium (`partial_equilibrium=0`),
addiction on, homeownership off, rent fixed, `life_span=60` for ages 26 to 85.

Backward induction costs about 5 to 10 seconds per age on this 4 core box, so a
value function pass is roughly 6 minutes.

## The open problem: the stationary distribution did not converge

The previous run's distribution residual fell to about 1.5e-3, stopped
improving, and then ROSE over more than 125 iterations. The loop is

```fortran
do while (distance_distribution>stopping_rule_stationary_distribution)
```

with `stopping_rule_stationary_distribution=1e-8` and **no iteration cap**, so a
stalled loop spins forever rather than reporting.

### What has been ruled out, and how

| candidate | verdict |
|---|---|
| Aitken acceleration destabilising the endgame | **Not it.** `accelerate_distribution=0`; the acceleration is compiled out. Worth recording because the guard it carries would permit a step that moves total mass by a part in a thousand, which is the same order as the residual floor, so it would have been the first suspect had it been on. |
| The average income the policy functions are evaluated at moving between sweeps | **Not it.** `avg_income_to_use_2` reads `model_average_labour_income_by_employment`, which is written only in `stationary_equilibrium_statistics`, and that is called at lines 29177 and 29248, both OUTSIDE the `do while`. The operator is fixed for the whole loop. |
| Newborn composition feedback | Ruled out in an earlier session. |
| A thread count race in the reduction from `distribution_implied_private` | **Not it.** A single threaded run reproduced the four thread run bit for bit for 48 iterations. A race would differ from the first sweep. |

### What that leaves

A fixed linear operator applied repeatedly cannot make a residual rise
persistently, so either the operator is not fixed for a reason not yet found, or
the residual is not measuring what it appears to. Two things to measure next,
both cheap and both requiring only prints:

1. **Where the maximum sits.** `distance_distribution` is a max over the whole
   state space and nothing reports WHICH cell attains it. If the argmax is one
   cell, that cell names the mechanism; if it wanders, the sequence is noise
   around a floor and the floor is the thing to explain.
2. **The total mass each sweep.** Mass is not conserved across a sweep when
   `have_probablistic_death=1`, and the existing check is disabled in that case,
   so nothing currently watches it. A drifting total would show up as a residual
   that cannot fall.

### Also worth fixing whatever the cause

The loop has no maximum iteration count. A run that stalls should say so and
carry on with the best distribution it has, rather than spinning; as it stands
the only signal is a log that keeps printing the same number.

## Status

Run 1 launched, backward induction in progress. Nothing established beyond the
table above.

---

## Run 1: what it settled, and the defect it exposed

**The distribution converges from a cold start.** 107 sweeps to 1.61e-4. The
operative tolerance is not the declared 1e-8: `stopping_rule_stationary_distribution`
is a variable, not a parameter, and line 29220 resets it to **2e-4** whenever
`include_addiction=1`. The declared value never reaches the iteration. So the
earlier run's "residual bottomed at 1.5e-3 against a 2e-4 exit" was measured
against the right number, and the difference between the two runs is the starting
point, not the tolerance.

**The residual does not fall monotonically, and the kicks are not periodic.** It
contracts at about 0.95 a sweep, interrupted by jumps: gaps between rises of
35, 10, 7, 13, 13, 7 sweeps, the largest a factor of 3.94 at sweep 87 (7.27e-4
to 2.86e-3). Each jump is followed by one sweep of no progress and then
contraction resumes, faster than before. The jumps get further apart and the
post-jump contraction accelerates, which is what settling looks like when a
discrete choice is still moving mass between cells. Nothing prints between the
two sweeps either side of a jump, so it is generated inside the sweep and not by
an interleaved routine.

The loop now has a cap, `max_distribution_sweeps=4000`, and reports
`DIST_DONE sweeps= N final_distance= X` once a loop. Neither changes the answer;
both mean a stall reports itself instead of spinning, which is what cost a day.

## The defect run 1 exposed: two moments measured on an empty set

At the declared starting values `model_fraction_homeless(1)` is **zero**. Every
moment conditional on being homeless is then computed on an empty set, and the
guards that protect the divisions set the numerators to zero, so:

- `model_fraction_of_homeless_unemployed` reads 0, hence
  **`model_employed_share_of_homeless` reads a clean 1.0**, and the gap against
  the 0.50 target is a fabricated +0.5;
- `model_smi_share_of_homeless` reads 0, and the gap against the 0.25 target is
  a fabricated -0.25.

Both drive live brackets: the first is h_2's moment since last round, the second
is lambda_m's.

**It is not self correcting, which is why it had to be guarded rather than waited
out.** A positive gap on the employed share calls for a SMALLER cheapest
dwelling. A smaller one is cheaper, so it houses MORE people, so homelessness
stays at zero and the gap never changes. In run 1 this drove
`smallest_rental_relative_to_lowest_income` from 0.0361 to 0.0111 in a single
loop and would have run it to its lower bound while the moment never moved.

Both brackets now hold the parameter when `model_mass_homeless_raw(1)` is zero
and set their distance to 1 rather than 0, so the calibration does not report
convergence on a moment it cannot measure. `h_1` is what creates homelessness,
through `size_homelessness`; until it has, neither bracket has anything to read.

## Run 2: the guards are validated

They did the thing they were written for, and the log shows both halves of it.

**Loop 1, homelessness zero.** `h_2 HELD` and `lambda_m HELD` both fired and
`smallest_rental_relative_to_lowest_income` stayed at its declared 0.0361. In run
1, with no guard, the same loop drove it to 0.0111 chasing a fabricated +0.5 gap.

**Loop 2, homelessness present.** The employed share of the homeless reads
0.9032 and their income share 0.4524, both computed on a non-empty set. The
moments are measurable, the guards release, and the brackets have something real
to read. `h_1` created the homeless population within one loop, which is what the
guard's comment predicted it would.

Two further guards of the same family were already in the file and fire on the
same loop, `mu_homeless HELD` and `omega HELD`, so this pattern is the
codebase's own convention rather than something imported.

**The distribution keeps converging.** 95 sweeps to 1.70e-4 on loop 2, against
the 2e-4 tolerance and the 4000 sweep cap. Worth watching across loops: the file
records 655 as a normal cost later in a calibration, so a count climbing toward
that is expected and a count climbing past it is the signal the cap exists for.

## Run 2 is STUCK, and stopped at loop 12. The corner, and how it was reached

Not a stall and not a crash. The calibration walked into a corner it cannot walk
out of, and every piece of the chain is in the log.

**h_2 ran to its lower bound of exactly zero.**
`smallest_rental_relative_to_lowest_income` went 0.0361, 0.0137, 0.0224, 0.0188,
0.0123, 0.0045, 0.0000. Its update is bounded by `min(max(...,0.d0),10.d0)`, so
zero is a permitted value, and `smallest_house_size = smallest_rental_relative_to
_lowest_income`. The smallest rental therefore has zero size and zero rent, which
is not a cheap dwelling but no dwelling: with `housing_size(0)=0` the grid runs
0, h_max/2^varsigma, h_max, and a rental of zero size delivers log(0) of housing
services, so nothing ever takes it.

**From there homelessness is identically zero.** 0.83 per cent, 0.042, 0.044,
0.0053, 0.0012, then exactly 0 for five consecutive loops.

**So h_1 runs away against a moment that cannot respond.** `size_homelessness`
went 0.30, 0.38, 0.41, 0.44, 0.48, 0.53, 0.59, 0.66, 0.74, 0.82, with the steps
GROWING. Its gap is a constant -0.399 percentage points every loop, so the update
pushes the same way forever and accelerates as the adjuster grows on a gap that
never flips sign.

**And the empty set guard is now part of the trap.** It holds h_2 whenever there
are no homeless households. That is right when the moment is unmeasurable, but
here h_2 sitting AT the bound is what causes the unmeasurability, so h_2 can
never come back up. One runaway was fixed and a frozen parameter created in its
place.

### What the report showed while this was happening

Against loop 4, at loop 12 three moments had improved and six had got worse, and
treatment take up had gone from 6 per cent off to 91. That is the signature to
watch for: not divergence in one place but a general drift, because the housing
block had stopped responding to anything.

### Three things to fix before restarting

1. **A floor on h_2 strictly above zero.** The root cause, and a one line bound.
   The bracket has to stay inside the space of real dwellings.
2. **The guard must tell "unmeasurable" from "unmeasurable because I am at a
   bound".** With homelessness at zero AND h_2 at its floor, holding is wrong:
   the zero is itself evidence the bottom rung is too cheap, so h_2 should be
   backed off the bound rather than frozen against it.
3. **A loud report when any bracket sits at a bound for consecutive loops.**
   Nothing said a word while h_2 sat at zero for five loops. It was found by
   tracing the series by hand, which is not a method.

### The lesson, stated generally

A bracket bounded at a value that DESTROYS the moment it is calibrated on cannot
recover, because the gap it reads there is constant. Bounds must be chosen so
that the moment still responds at them. This is the same class as the empty set
guard: a parameter must never be updated from, or frozen by, a moment that
carries no information about it.

## Status

Run 2 stopped at loop 12, stuck. Awaiting a decision on the floor for h_2 before
run 3.

## 28 August, evening: the drug corner's attainability boundary, measured

The author's steer -- a high onset hazard against a low participation scalar --
was probed with seven dedicated points beside the simplex (A-G2, vectors in the
PROBE_*.txt files, all cold, all receipt-verified). What the surface says:

| point | lambda | scalar | uct | b (0.089) | lambda_d (0.0368) | ratio (0.413) |
|---|---|---|---|---|---|---|
| base | 3.54 | 0.0239 | 0.127 | 0.056 | 0.0042 | 0.075 |
| A | 7.07 | 0.0176 | 0.127 | 0.161 | 0.0329 | 0.204 |
| B | 10.6 | 0.0150 | 0.127 | 0.290 | 0.126 | 0.433 |
| F | 10.6 | 0.0168 | 0.127 | 0.103 | 0.0291 | 0.284 |
| G | 12.4 | 0.0168 | 0.127 | 0.070 | 0.0190 | 0.271 |
| G2 | 12.4 | 0.0168 | 0.249 | 0.068 | 0.0171 | 0.253 |

Three facts, each carried by measurements rather than a fit:

1. **The corner works up to a point.** F holds BOTH drug moments within about
   20 per cent -- against -37 and -89 at the base -- and is the best joint
   approach measured.
2. **The ratio saturates.** At participation near its target, disorder-per-user
   plateaus at 0.25-0.28 whatever the hazard does (0.284 at lambda 10.6, 0.271
   at 12.4), and B's 0.433 was a property of TRIPLE-target participation, not
   of the hazard. Raising the treatment cost lowers rather than raises it (G2).
3. **So b=0.089 and lambda_d=0.0368 are not jointly reachable through
   lambda_addiction, addiction_scalar_1 and utility_cost_of_treatment.** The
   standing disorder stock at target participation runs about 40-50 per cent
   below target.

What has NOT been tried: the OUTFLOW side. lambda_d is a stock; the probes all
worked its inflow. The stopping/recovery probabilities
(probability_of_stopping_addiction and relations) are externally assigned, and
lowering recovery would raise the stock at any inflow -- at the cost of moving
tau_u and mu_H, which their own levers would then have to re-absorb. Whether to
open a recovery-side parameter to the search, or to revisit the use-to-disorder
transition itself, is a modelling decision and the author's.

The simplex continues regardless -- the boundary binds only the drug pair, and
the other eighteen moments are converging around the treatment-cost vertex.

## 29 August, small hours: what the simplex cannot see, measured off its own archive

The contraction was accepted -- best 0.283 to 0.278, median 0.333 to 0.296, and
the widest edge halved from a factor of 3.99 to 2.00, so the whole simplex came
down rather than one vertex. The reflection is round 4.

Then a question worth asking of any stalled search: for each moment, which
measured point comes closest to its target, and how does that point's vector
differ from the leader's? The archive answers it, and the answer is that the
leader is not near the frontier on moments it could reach cheaply.

| moment | w | leader | best measured | loss recoverable | the difference that carries it |
|---|---|---|---|---|---|
| lambda_d | 3 | 87% | 11% | 0.0851 | lambda_addiction 3.54 -> 7.07 |
| b | 3 | 31% | 4% | 0.0298 | sd_permanent_productivity 0.953 -> 1.335 |
| h_2 | 1 | 74% | 1% | 0.0268 | smallest_rental 0.0343 -> 0.0207 |
| pi_eu | 1 | 74% | 3% | 0.0264 | probability_becoming_unemployed 0.0294 -> 0.013 |
| theta | 2 | 41% | 16% | 0.0188 | lambda_addiction 3.54 -> 12.4 |
| aleph | 2 | 16% | 0% | 0.0119 | utility_cost_of_treatment 0.151 -> 0.249 |
| pi_V | 1 | 31% | 11% | 0.0073 | probability_of_voucher_benchmark_used 0.0087 -> 0.0121 |
| kappa_uem | 1 | 18% | 0% | 0.0065 | largest_house_size 0.099 -> 0.117 |
| gamma | 1 | 15% | 1% | 0.0052 | largest_house_size 0.099 -> 0.117 |
| h_4 | 1 | 9% | 1% | 0.0031 | largest_house_size 0.099 -> 0.164 |
| tau_l | 1 | 25% | 17% | 0.0031 | utility_cost_of_treatment 0.151 -> 0.249 |
| mu_H | 1 | 7% | 0% | 0.0027 | utility_cost_of_treatment 0.151 -> 0.249 |
| h_1 | 2 | 4% | 0% | 0.0023 | utility_cost_of_treatment 0.151 -> 0.249 |

TWO THINGS FALL OUT OF THE RIGHT-HAND COLUMN, and neither is visible from the
loss alone.

**Instruments are shared, and the moments sharing one agree on the direction.**
Four moments -- aleph, tau_l, mu_H and h_1 -- all want the treatment cost at
0.249361, and three -- kappa_uem, gamma and h_4 -- all want the largest house
size at 0.117139. They stack instead of competing, so a single point can carry
0.035 of loss that reads as seven separate misses.

**Every one of these is a LARGE single-coordinate move, which is exactly what
the search cannot make.** Multi-directional search reflects all vertices through
the best and accepts only if a vertex beats it, and each vertex differs from the
best in one coordinate by a bounded step. A move of minus 56 per cent in the
unemployment probability is several rounds of that away, and a point needing two
such moves at once is unreachable no matter how many rounds run. The simplex is
not stuck because it is badly placed; it is stuck because the geometry it walks
in cannot express the step.

Six probes, nested so an interaction shows rather than being inferred: A is the
leader with the unemployment probability, the smallest rental and the voucher
probability moved; B and C isolate the first two from the leader's own location;
D is that pair; E adds the largest house size, all four non-drug; F adds the
treatment cost, which is a drug-block parameter and therefore the one likeliest
to buy its four moments by giving up lambda_d or b.

If the non-drug instruments are independent, E lands near 0.18 -- which is the
whole of what the search can deliver without touching the drug corner, arriving
in one point rather than in weeks of rounds. If they interact, the nesting says
which pair does it. Either way the answer is measured tonight.

## 29 August, small hours: the wealth distribution, investigated and accepted

The author raised the lower tail: the bottom half holds too much. It does. The
model puts it at 16.8 per cent of net worth against 2.52 in the Fed
distributional accounts, and the run's own diagnostic has printed that
comparison all along. Three fixes were proposed and each was tested against the
archive before anything was changed. **The decision, on the author's word, is
that beta keeps targeting wealth over output at 3.0 and the asset side is not
touched.** What follows is what was measured, so the choice reads as a choice.

**Retarget the discount factor onto the bottom-half share: cannot reach.**
Closing 0.169 to 0.0252 needs a log move of -1.91 against a fitted elasticity of
+6.3, which asks for a discount factor near 0.73. At the existing lower bound of
0.90 the share is still 0.089 -- three and a half times target -- and wealth over
output has collapsed to 0.88 against 3.0. Wiring in a target nothing can reach is
the lambda_m mistake this project already made once.

**Lower the unemployment risk, so the bottom saves less: right sign, wrong size.**
Nineteen archived points already sit at probability_becoming_unemployed = 0.013
against the leader's 0.0294. The bottom-half share moves from 0.1685 to 0.1633 --
three per cent, where eighty-five is needed. At that setting the unemployment
rate is 0.055 against a target of 0.0485, so unemployment is essentially FIXED
there and the wealth distribution barely notices. The precautionary channel is
real and it is not what holds wealth at the bottom.

**Where the wealth actually is.** Not at the destitute end: the bottom tenth
holds 0.28 per cent, which is right, and the bottom quarter 3.1. The whole
discrepancy is the band between the twenty-fifth and fiftieth percentiles, which
holds 13.7 per cent of net worth against roughly 2 in the data. Households just
below the median are several times too wealthy, and no parameter moved tonight
touched it.

**The number that says what this costs the paper.** Average assets of the
homeless: 0.1376, about eleven per cent of the top point on the savings grid. A
homeless household with that much banked is not on the street because it ran out
of money, and the model duly reports that 98 per cent of homelessness is BY
CHOICE. That is a known limitation of the benchmark as it stands rather than a
bug, and it is written here so nobody has to rediscover it.

**Still open, and cheap:** whether the savings grid is a binding cap. It runs to
1.2853 in forty positive points against sixty-one negative ones, so saving is
resolved eleven times more coarsely than debt. Bunching on the last point would
inflate every share above by cutting the total short. Two diagnostics were added
to measure it and the reading is pending; it changes no number either way.
