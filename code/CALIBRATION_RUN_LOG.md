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
