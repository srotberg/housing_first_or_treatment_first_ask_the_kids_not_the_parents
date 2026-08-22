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

## Status

Run 2 in progress, past loop 1. No stall so far.
