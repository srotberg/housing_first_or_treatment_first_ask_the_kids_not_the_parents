# HOW TO DO ALL OF THIS AGAIN

The author, 19 September: *"i hope you are documenting all this, so that if we
ever have to do these things again (all the calibration steps and this), then
you can do them again yourself"*.

`ENGINE.md` is the method and the accumulated mistakes. `CALIBRATION_STATE.md`
is the live state and changes every round. **This file is the procedure**: the
steps in order, the flags each one needs, and the test that says whether it
worked. It should stay true even after the state file has moved on.

Everything here has been run. Nothing is a plan.

---

## 0. THE THING THAT WILL WASTE YOUR TIME FIRST

**The calibration loop does not terminate when the parameters are frozen.** Its
exit needs every one of forty-odd distances inside its stopping rule; frozen,
no parameter moves, so no distance shrinks. Before 19 September **no run in
this project had ever reached `simulation ended`** -- n71 spun for eighty-five
blocks. That is why the benchmark's policy functions had never been written and
no consumption equivalent had ever been computed.

Use `frozen_stop_tolerance`. It leaves the loop once the largest RELATIVE move
across `b`, `lambda_d`, `h_1` and average labour income between consecutive
blocks is inside it -- ENGINE.md's own four names. `frozen_stop_after_blocks` is
a cap, not the plan.

---

## 1. BUILD

Three builds, every time, and all three must be clean:

```
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"
gfortran -O1 -fcheck=bounds,pointer -g -fbacktrace                     $COMMON src.f90 -o hftf_bounds
gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace $COMMON src.f90 -o hftf_snan
gfortran -O3 -funroll-loops                                            $COMMON src.f90 -o hftf_prod
```

About six seconds at -O1, under a minute at -O3. The out-of-bounds warnings in
the transition block (lines ~52000+, `transition_length-25`) are pre-existing
and fire because `transition_length` is 1 in a steady state.

**The model is NOT bit-reproducible.** A rebuild that only moves declarations
changes the last digits: n87 against n86 came back at 2.6e-5 relative on `b`
with average labour income identical to seventeen digits. It is thread-order
accumulation over the tiny mass in the homeless and addicted states. **Score
any no-op control at 1e-4 relative, never on exact equality.**

---

## 2. SET UP A RUN

Each run gets its own directory with its own copy of the binary, so runs cannot
tread on each other's `.dat` files.

```
N=<scratch>/nNN; mkdir -p $N
cp hftf_prod $N/hftf
# warm start: the distribution only (see below)
for f in calibration_distribution1.dat calibration_distribution2.dat \
         calibration_distribution_shape.dat newborn_parent_share.dat; do
  cp <previous run>/$f $N/$f
done
# the parameter vector, as a handover
python3 make_handover.py <a resume_seed.dat> $N/PARAM_HANDOVER.txt
cd $N && ./hftf > run.log 2>&1
```

**`PARAM_HANDOVER.txt` is consumed on read** -- `close(79,status='delete')` --
so a finished run's directory never contains it. Rebuild it from a
`resume_seed.dat` each time. Every line is `name value`; roughly 78 real and 18
integer parameters have a case.

**WHAT A WARM START ACTUALLY CARRIES: the distribution, and nothing else.** The
value function is never restored at startup -- it is read from disk only for a
counterfactual and for the welfare curve. So **every block 1, in every run,
solves policies from cold**, and no distribution warm start makes block 1
reproduce a converged `b`. Measured: starting from a distribution at b = 0.0830
instead of b = 0.1015 moved block 1 from 0.0757 to 0.0747 and changed the rest
of the path not at all. **Do not expect a warm start to shorten a run.** Register
convergence tests on block 2 or later.

---

## 3. READ THE TRACE, AND THE THREE THINGS THAT MISLEAD

Anchor every `sed`. **Four separate field bugs** have come from greedy patterns:
`s/.*weight_on_child=//` matches through `distance_weight_on_child=`, and
`s/.*exposed=//` matches through `unexposed=`. Use `s/^ weight_on_child=//`.

* **BLOCK 1 IS AN ARTEFACT.** Policies are cold and the newborn class share has
  one block of lag. It always reads low.
* **BLOCK 2 IS INFLATED.** Measured: n79 read 2.2646 at block 2 against 1.4320
  converged, a factor of 0.632. Never quote a block-2 ratio.
* **A BLOCK IS NOT A LOOP.** `loop_count` advances by TWO per moment block.

Nothing is a result until `d(b)` and `d(class share)` are both flat. The series
decelerates and has been called converged early at least three times.

### The stopping test is a MAX over four series that decay at different rates

Do not read the name that is binding now as a guide to when the test trips.
Measured on n90:

    blk  d(b)        d(lambda_d) d(h_1)      d(y)        max        binding
    2    +1.519e-01  +1.474e-01  -7.405e-02  +2.059e-01  2.059e-01  y
    3    -4.710e-03  +3.818e-03  -2.385e-02  +8.497e-02  8.497e-02  y
    4    -1.064e-02  -7.125e-03  -1.876e-02  +3.885e-02  3.885e-02  y
    5    -1.213e-02  -7.596e-03  -4.824e-03  +1.859e-02  1.859e-02  y
    6    -7.761e-03  -6.165e-03  -8.046e-03  +9.079e-03  9.079e-03  y
    7    -1.660e-03  -8.973e-03  -4.982e-03  +4.442e-03  8.973e-03  lambda_d

`y` decayed by a clean factor of 0.47 a block and an estimate built on it said
the test would trip at block 12. It was an estimate of the wrong series: at
block 7 `y` handed over to `lambda_d`, which is a SLOW MONOTONE DRIFT and not a
geometric decay at all -- in levels it falls -2.51e-4, -2.66e-4, -2.14e-4,
-3.09e-4 a block with no deceleration, 700 times above the 1e-5 noise floor, so
it is a real mode rather than chatter. **At that rate lambda_d never reaches
1e-4 and the run ends at its cap.**

IT IS NOT THE CLASS SHARE. That settled by block 4 (0.03178, 0.03186, 0.03191,
0.03203) and is already at the noise floor, so the newborn-share fixed point is
not what is holding lambda_d up.

WHAT TO DO ABOUT IT. Set the cap deliberately and treat "stopped at the cap" as
a REPORTABLE OUTCOME, not a failure: a run that ends with lambda_d moving 0.7
per cent a block is still far closer to a fixed point than one stopped at block
3, and the caveat belongs in the result rather than in the decision to run. Do
not loosen the tolerance to manufacture an `ECONOMY IS STILL` line -- the line
is what tells a later reader which of the two happened.

---

## 4. THE CALIBRATION, IN ORDER

### 4.1 Freeze everything but the one parameter you are moving

`freeze_all_but_omega_c = 1` zeroes all 47 adjusters except
`weight_on_child`'s. `omega_c_is_pinned = 1` holds omega_c too, which is what
you want for a pure equilibrium solve. Both are handover parameters.

`calibrate_penalty_child_addicted` must be 0: delta_d moves the productivity
GRID, so an in-loop scan cannot converge -- the grid it is scoring against
changes underneath it.

### 4.2 delta_d

**Pinned at Nilsson's 0.24**, as a deliberate lower bound on the welfare losses
from Housing First, not calibrated. The author: *"i think we can just use deltad
as a lower bound on the welfare losses from hf"*. The SUD odds ratio is then
reported UNTARGETED (1.55 at the benchmark, against data of 1.5 to 2.5).

Check it every block: the class-1 grid factor must equal `1 - delta_d`
(0.760000 at 0.24). It is printed.

### 4.3 omega_c

Targets the child use gap, `drug_users_without_child / model_total_drug_users - 1`,
against `1/0.845 - 1 = 0.18343` from NSDUH 2024.

**THE TRAP, AND IT HAS CAUGHT BOTH OF US.** 0.18343 is the RISE when the child
term is off, which is a 15.5 per cent FALL. "Reduce drug use by 18 per cent" is
a DIFFERENT eighteen. omega_c = 0.055 delivers an 18.3 per cent fall and a gap
of 0.2233 -- it hits the wrong one. **Read the band on the GAP.**

The response is linear through the origin. Two converged points give the slope;
the crossing is the answer. Pinned at **0.055** on the author's instruction
(*"keep omega_c as is. 0.2233 doesnt change anything"*), which is above the band
of [0.1779, 0.1889] and is a known, accepted approximation.

### 4.4 Converge, then save

Set `frozen_stop_tolerance = 1e-4` and a cap. Expect ten to thirteen blocks at
roughly nine minutes each. The loop leaves, `save_vars_and_functions` writes the
`baseline_benchmark` policy functions and distribution (about 1.2 GB), and
`save_welfare_curve` runs.

**Watch the disk.** The save wants over a gigabyte and old runs hold 279 MB each
in distributions that are re-derivable. Delete those, keep the logs.

---

## 5. THE WELFARE CURVE AND kappa_x

### 5.1 What the curve is

21 points on x in [-0.5, 0.5], where x scales NON-HOUSING, NON-DRUG consumption:
`consumption_1 = (1-frac_addiction)*total_consumption_1*(1+x)`. Each point is a
policy-fixed walk over the saved benchmark, integrated over the stationary
distribution at age one -- every state a household can be born into -- then
carried forward with its own survival, plus the twenty five childhood years.

**It costs about three minutes for all 21 points.** The blocks are the expense,
not the welfare machinery. Re-pricing anything off a saved benchmark is cheap.

### 5.2 The curve is exactly `A + B(1+x)^k`, and that is worth using

Utility is a power in c, so scaling c multiplies the whole consumption-carrying
bracket by `(1+x)^((1-sigma)*alpha_c)`. Fitted on n88's 21 points:

```
k fitted     -0.387775      against -alpha_c = -0.387770      0.001% apart
rms residual  1.4e-5 utils over 21 points
```

**`inelastic_labor_supply = 1`, so leisure utility is identically zero.** That
leaves `A = (value_of_life - kappa_x*H) * D_adult` with nothing else in it, and
`D_adult` -- the discounted, survival-weighted count of adult periods -- falls
straight out of the fit:

```
D_adult = A / (value_of_life - kappa_x*H) = 17.107
          against a no-mortality cap of 18.011, so survival costs 5.0%
```

`value_of_life` is CALIBRATED (87.198, not the 11.0 in the declaration) -- read
it from `value_of_lifebaseline_benchmark.dat`, never from the source.

**THE CHILD'S FLOW DOES NOT CARRY value_of_life, AND ASSUMING IT DOES COSTS A
FACTOR OF 8.5 ON kappa_x.** `child_flow_out` is set inside
calculate_flow_utility at lines 27652 and 27675; `value_of_life` is added to
`flow_utility_1` at 27816, AFTER both. So the childhood curve is not
`B_child + value_of_life*D_child`, and reconstructing `B_child` that way put
kappa_x at 6.94 where the measured value is 0.81. The adult decomposition IS
right -- `A = value_of_life*D_adult` gives D_adult = 17.107, which the probe's
own `D_total` confirms to 0.004 per cent -- which is what made the wrong answer
look well-checked.

**SO USE THE PROBE, NOT A DECOMPOSITION.** The probe evaluates the actual walk
at the actual x and needs no assumption about what is in which flow. Its two x
points are a built-in check: their costs must be in the same ratio as the x
(measured 2.50209 against 2.50000, 0.08 per cent).

The childhood half is the same shape: `W_child(0) = B_child + value_of_life*D_child`
with `D_child = sum_{i=1..25} beta^(i-1)`.

### 5.3 kappa_x

The author's definition, 19 September: be compensated by 0.2 per cent of
consumption AND housing such that, with the benchmark homelessness rate, you are
indifferent to having no homelessness and no compensation.

Housing and the addictive good are held fixed in the walk, so **c carries the
whole 0.2 per cent**:

```
x = 0.002 / (1 - s_h - s_b)
```

with `s_h` from `MOMENT gamma` (housing over expenditure) and `s_b` from drug
spending over `total_expendifure`. At the benchmark that is x = 0.00275.

Then bisect on:

```
(B_child + beta^25 * B_adult) * [(1+x)^k - 1]  =  kappa_x * H * (D_child + beta^25 * D_adult)
```

**WHO IS CHARGED IS WORTH A FACTOR OF 22.** The consumption response is 95.6 per
cent childhood, because a child's twenty five years are undiscounted while an
adult's sixty sit behind beta^25 = 0.2532. Charging adults only gave 29.31;
charging everyone gives 6.94. The author chose everyone (*"i think kappa_x
should fall on everyone including children"*), so the subtraction now sits in
BOTH childhood sums -- `calculate_childhood_utility` and the walk in
`compute_value_function_comparison`, which the CEV null test compares to 1e-6.

The coded default was 0.002, entered as though a util were a consumption share.
It is not, and the deduction is `kappa_x*H` with H = 0.0065, so the old value
made the whole disamenity worth about one part in four million of the flow.

### 5.4 The probe

`save_welfare_curve` ends with four `KAPPA_X PROBE` lines. It measures
`H*(D_child + beta^25*D_adult)` from two evaluations at x = 0, one at the coded
kappa_x and one at zero -- exact, because the dependence is linear -- and the
cost of the compensation evaluated AT x rather than fitted off a grid of step
0.05. Its implied kappa_x should reproduce the analytic solve above. **Two
independent routes to the same number is the test.**

---

## 6. WHAT THE CURVE CHECKS, AND WHAT IT USED TO CHECK WRONG

`CEV NULL at x=0` prints all three halves against what the model reported. All
three must match. The childhood half has a HARD STOP at 1e-6 and the lifetime
identity has a 5 per cent tolerance with a shift applied inside it.

The identity used to compare the LIFETIME curve to `average_welfare_of_youngest
_cohort`, the ADULT half, and read a 41 per cent difference. The target is
`average_welfare_with_childhood`. Fixed 19 September; recorded because two of
`calculate_welfare_gains`' four callers still pass an adult object
(`welfare_by_addiction_youngest`) into the lifetime curve. That one stops loudly
rather than returning a wrong number, and fixing it needs a childhood-inclusive
welfare BY ADDICTION STATUS, which does not exist.

---

## 6a. THE DRUG MARKET IS THE HARD PART OF ANY ARM

The benchmark never exercises this: with `is_counterfactual = 0`
`clear_drug_market` normalises the supply shifter, takes the price as given and
sets `distance_drug_market` to zero. Everything below bites only in an arm.

**The price moves 0.5 per cent a loop and no faster.** `max_drug_price_move =
0.005`, and it is LOAD BEARING -- the iteration's gain is
|eps_d|/eps_s = 3.14/1.46 = 2.15 and the secant diverged on universal Treatment
First. Its own declaration says: *"Loosening this alone hides the problem; it
does not fix it."* Do not loosen it. If an arm needs a big price move, give it
LOOPS, not a bigger step. `max_counterfactual_loops` is 250 for that reason.

**Warm start the price, and the handover name is `drug_price_start`.** NOT
`price_of_addictive_good` -- that is reported as `HANDOVER IGNORED, unknown
name` and silently leaves the price at 1.0, which costs about sixty loops of
pure walking. `drug_price_start` is gated on `is_counterfactual == 1`, so it
exists for exactly this.

**BRACKET THE PRICE, DO NOT ESTIMATE IT.** The supply side is exact and can be
checked: recovering the exponent from the benchmark's own normalisation,
1 = shifter*V^k, gave k = 0.684931 against 1/eps_s = 0.684932, six digits. The
DEMAND side is not -- `stopping_rule_drug_market`'s comment ties the
convergence difficulty and the failed elasticity validation together as one
defect. So an equilibrium price computed from a remembered elasticity is not
trustworthy: measured at 0.727 that way, and the bracket put it near 0.886.

Two runs at different starting prices give the bracket for free, because
`distance_drug_market` is |gap| and the gap changes sign across the fixed
point. But **interpolate only between CONVERGED gaps.** The first bracket taken
here was read off two unconverged runs:

    p = 1.00   gap -0.620   implied 0.381   the price must FALL
    p = 0.75   gap +0.737   implied 1.487   the price must RISE

and it put the crossing at 0.886. The converged measurement puts it at 0.871.
That looks like a small miss and is not: the gap function's slope is about
-7.4, so being 0.015 out in the price is 0.11 in the gap, twenty-two times the
5e-3 tolerance. An arm warm started at 0.886 is not near the answer.

**THE CONVERGED GAP FUNCTION**, measured on the omega_c = 1 plus
internalisation arm. The second point costs a run with
`drug_market_adjuster = 0` handed over, which PINS the price and lets
everything else -- pi_v, the budget, the distribution -- converge around it, so
the gap that is finally printed is a property of the price and not of an
unfinished solve:

    p = 1.00   V 0.1139   implied 0.3659   gap -0.634087   (CF dist 4.9e-5)
    p = 0.87   V 0.4122   implied 0.8829   gap +0.012910   (CF dist 2.2e-4)
    ---------------------------------------------------------------
    crossing   p* = 0.8717 (local slope) to 0.8726 (secant)

Take the CONVERGED gap and no earlier one. The same probe read +0.008977 four
loops before it finished, while the budget residual was still at 5.5e-2 -- a
number that looks settled and is not. Both readings happen to give nearly the
same crossing here, which is luck and not a reason to trust the early read.

The sign is NOT in the log -- `distance_drug_market = abs(gap_1)`. Recover it
from `drug quantity V=`, which IS printed, and the benchmark's own shifter in
`drug_supply_shifterbaseline_benchmark.dat`:

    implied = shifter * V**(1/eps_s)        shifter = 1.6200147899, V_bench = 0.494427
    gap     = implied - price

That reproduces the Fortran's printed `distance_drug_market` to six digits, so
it is a reconstruction and not a guess.

**THE DEMAND ELASTICITY IS ABOUT -9, NOT -3.14.** From the two converged
points, dlnV/dlnp over [0.87, 1.00] is -9.23. The 3.14 quoted above is the
remembered number and it understates the gain by a factor of three. This is the
whole reason the arms would not solve, and it is checkable by the same
arithmetic used on the three other unstable loops in this solver:

    d(implied)/dp = (1/eps_s)*(dlnV/dlnp)*implied/p = -6.41
    d(gap)/dp     = -7.41
    the update is p' = p + a*gap, so dp'/dp = 1 - 7.41*a

    a = 0.5  ->  -2.70   DIVERGENT   (this was the setting, and it oscillated)
    a = 0.2  ->  -0.48   stable
    a < 0.270 required.

`drug_market_adjuster` is therefore 0.2, not 0.5. Note that changing it proved
INERT in the run that first tested it, because the 0.5 per cent clip was
binding on every loop and both settings clipped to the same step -- two runs
agreed to seven digits. The clip converts divergence into a slow crawl; it does
not cure it. The setting only becomes operative once the price is warm started
close enough that the clip stops binding, which at p* = 0.872 it does: the
clip spans [0.86764, 0.87636] and contains the root.

So: bracket with a pinned-price probe, warm start INSIDE the bracket with
`drug_price_start`, and keep the adjuster at 0.2.

**WHAT AN ARM'S CONVERGENCE ACTUALLY REQUIRES**, all at once, capped at
`max_counterfactual_loops`:

    distance_counterfactual_moments <= 5e-4   b, lambda_d, h_1, y between iterates
    rental market      <= 1e-2
    housing market     <= 2e-2
    government budget  <= 2.5e-2
    drug market        <= 5e-3
    inheritance        <= 2e-3

An arm prints `CF MOMENTS distance=`, NOT `BLOCK MOVE`, and
`frozen_stop_tolerance` does not apply to it at all -- that flag is wired into
the CALIBRATION loop, which an arm never enters.

---

## 7. THE ARMS

See `ARMS.md`. All three need a counterfactual BUILD, because `is_counterfactual`
and `use_revenues_to_increase_voucher_probability` are compile-time parameters;
one binary serves all three. `code/build_cf.sh` makes it -- the counterfactual
source differs from the benchmark's in exactly those two lines, and the script
REFUSES if the diff is not exactly two, which is the guard against the
parameters being renamed underneath it.

All read the `baseline_benchmark` files, so the benchmark has to be converged
and saved first. **`code/results/n90_benchmark/` is a saved one**, so an arm can
be run from a fresh checkout with no benchmark run in front of it. What that
directory leaves out is the warm-start distribution, which costs an arm a few
blocks and changes nothing.

Before running any of them, check the benchmark files exist -- 62 of them, 3 per
beta type and 59 scalars. A missing one kills an arm an hour in.

**`code/launch_arm.sh` stages one**, and it is the script that was actually
used, not a tidied-up version:

    launch_arm.sh <arm: 1|2|3> <kappa_x> <benchmark run dir> [price] [pi_v]
    launch_arm.sh 2 0.8139 /path/to/n90 0.8720 0.073955

It copies every `baseline_benchmark` file out of the benchmark run and REFUSES
to continue if fewer than 60 arrive, copies the four distribution files for the
warm start, and writes `PARAM_HANDOVER.txt` from the resume seed with the arm's
own overrides on top. Then start it in the foreground of a background task:
`cd <dir> && ./hftf > run.log 2>&1`.

The two optional arguments are the warm starts that decide whether an arm
converges in twenty blocks or not at all: the drug price from section 6a's
bracket, and pi_v from wherever the probe left it. Neither is a result; both
are starting points the solver is free to move.

**Check the handover took.** `grep -c "HANDOVER IGNORED" run.log` must return 0,
and the arm's own defining names must appear with the values you meant:

    kappa_x, weight_on_child, internalise_homelessness_cost,
    adjust_taxes, drug_price_start, voucher probability

A misspelt name is not an error -- it prints `HANDOVER IGNORED, unknown name`
and the run continues against a model nobody chose.

---

## 8. OPERATIONAL RULES THAT WERE PAID FOR

* **NEVER `pkill -f` from the coordinator.** It matched the coordinator's own
  shell and killed every watcher with it. `TaskStop` is the tool.
* **A kill must never share a command line with anything naming the files it
  matches.**
* Test for a live solve positionally: `ps -eo args= | awk '/\.\/hftf/&&!/awk/'`.
  Never `pgrep -f`.
* **Never edit `code/*.f90` while a solve is running.** Write the patch to the
  scratchpad and apply it when the box is clear.
* **Compute happens only while a turn is open.** A hand-detached `&` or `nohup`
  is fatal; use the harness's background task.
* **Report ONE equilibrium, never a best-of across points.**
* **Prefer a measured bracket to an elasticity.** And when a change is meant to
  be a no-op somewhere, state the reference value BEFORE the run.
* Runs live in per-run scratch directories; `CONTROL.md` in each says what it is
  for and what must be true for it to be believed. **The scratchpad does not
  survive the container** -- anything that matters goes in the repo.

---

## 9. THE ORDER, END TO END

1. Build three ways.
2. Benchmark at delta_d = 0.24, omega_c = 0.055, everything frozen,
   `frozen_stop_tolerance = 1e-4`. Saves the policy functions, builds the curve,
   prints the probe.
3. Pin kappa_x from the probe, cross-checked against the analytic solve.
4. Build the counterfactual binary.
5. Arm 1, optimal drug use: omega_c = 1.
6. Arm 2, optimal homelessness: omega_c = 1 and
   `internalise_homelessness_cost = 1`.
7. Arm 3, Treatment First: detection 0.70, false positive 0, three-year
   exclusion, pi_v clearing.
8. The transition, against `TRANSITION_LESSONS.md`, which is a standing
   instruction and not notes.
