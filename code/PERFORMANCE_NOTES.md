# Performance findings

Measured in a 4-core Linux container, gfortran 13.3, on
`housing_first_or_treatment_first_SR_v1.f90` (24,338 lines).

**Summary: four problems found, ordered by payoff-to-effort. The first is a one-line change
that is probably costing you a factor of 3–10.**

---

## 1. You are compiling with no optimization at all

`readme.txt` line 6:

```
gfortran housing_first_or_treatment_first_SR_v1.f90 -I/usr/local/include -lm -mcmodel=medium -fopenmp -g -o housing_first_or_treatment_first
```

There is no `-O` flag. **gfortran defaults to `-O0`** — no inlining, no vectorization, no
loop optimization, everything spilled to memory. `-g` adds debug symbols on top.

On tight numerical Fortran this typically costs a factor of **3–10×**.

Replace with:

```
gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
    -O3 -march=native -funroll-loops -flto -o housing_first_or_treatment_first
```

- `-O3` — full optimization
- `-march=native` — use the actual CPU's vector instructions (AVX2/AVX-512). Compile on the
  machine you run on; don't copy binaries between machines
- `-funroll-loops` — helps the tight asset-grid loops
- `-flto` — link-time optimization across the whole single-file program
- drop `-g` for production; drop `-I/usr/local/include -lm` (unused, and `-lm` is implicit)

**Verify before trusting it.** Aggressive optimization can change floating-point rounding.
Compile at `-O2` and `-O3`, run the benchmark both ways, and confirm the converged
equilibrium objects agree to your solver tolerance. If they diverge, add `-fno-fast-math`
(not currently implied, but be explicit) and re-check. `-O2` alone still buys most of the
gain and is more conservative.

*Confirmed by inspection of the readme; the speedup factor is the standard range for this
kind of code, not something measured here.*

---

## 2. `max_CPUs` is hardcoded to 40 and overrides `OMP_NUM_THREADS`

Line 768: `integer, parameter :: max_CPUs=40`, used at lines 8933, 14669, 14989, 15268 as
`number_of_threads_used=max_CPUs` followed by `CALL OMP_SET_NUM_THREADS(...)`.

Because `OMP_SET_NUM_THREADS` is called explicitly, the `OMP_NUM_THREADS` environment
variable is ignored. On this 4-core container the program launched 40 threads — 10:1
oversubscription. It also means the binary is not portable between your laptop, this
container, and the cluster.

Fix:

```fortran
integer :: max_CPUs
!$ max_CPUs = omp_get_num_procs()          ! or read an env var
number_of_threads_used = max_CPUs
```

Note `omp_get_num_procs()` may report the *host* core count rather than the cgroup
allocation inside a container, so prefer reading an environment variable with a sensible
fallback.

**Measured: at 4 threads on 4 cores the process sustained ~360% CPU. Parallel scaling is
good — the bottleneck is work volume, not parallelization.**

---

## 3. The coarse-grid mode is genuinely broken — here is why

This is the bug you noticed. It is real, and it is not a tolerance issue.

### The mechanism

The asset search is two-pass (renter block at lines 9550–9557; the same pattern repeats at
9902, 10467, 10856, 11254):

```fortran
do global_search_index=0,coarse_grid
do future_financial_index= &
    (1-gsi)*negative_financial_grid_size + gsi*max(optimal_financial_1-grid_gaps+1, negative_financial_grid_size), &
    (1-gsi)*financial_grid_size          + gsi*min(optimal_financial_1+grid_gaps-1, financial_grid_size), &
    (1-gsi)*grid_gaps + gsi
```

- Pass 0 sweeps the whole grid with step `grid_gaps`
- Pass 1 refines ±(`grid_gaps`−1) around `optimal_financial_1`

With `coarse_grid=0`: `grid_gaps=1`, the loop `do gsi=0,0` runs one exhaustive pass, and
pass 1 never executes. **The fine mode is exact — which is why only the coarse mode is
wrong.**

### Bug A: `optimal_financial_1` is stale across branches

Line 9471 initializes it **once**, outside both the addiction loop (9500) and the housing
loop (9519). Line 9707–9717 updates it only inside the improvement test:

```fortran
if (value_function_renter_renter > largest_value) then
    largest_value = value_function_renter_renter
    optimal_renter_renter_indeces(1) = future_financial_index
    if (global_search_index==0) then
        optimal_financial_1 = future_financial_index      ! only on a NEW GLOBAL MAX
    end if
```

`largest_value` is a running maximum across **all** (addiction × housing) branches. So for
every branch after the first, if that branch's coarse pass does not beat the incumbent
global max, `optimal_financial_1` never updates — and pass 1 then refines around **a
different branch's optimum**.

The failure is silent and asymmetric: a branch whose true optimum lies between coarse
gridpoints and *would* have beaten the incumbent is missed entirely, because the coarse
sample missed it and the refinement looked in the wrong place.

**Fix:** use a separate per-branch variable for the coarse argmax, reset inside the housing
loop, and updated on the branch's own best value rather than the global one:

```fortran
do future_housing_status_index = ...
    coarse_argmax_1  = negative_financial_grid_size
    coarse_best_1    = large_negative_num          ! per-branch, NOT largest_value
    do global_search_index=0,coarse_grid
    ...
        if (global_search_index==0 .AND. value_function_renter_renter > coarse_best_1) then
            coarse_best_1   = value_function_renter_renter
            coarse_argmax_1 = future_financial_index
        end if
```

and centre pass 1 on `coarse_argmax_1`.

### Bug B: the method assumes unimodality, and this model violates it

Even with Bug A fixed, a coarse-then-refine search is only exact if the objective is
single-peaked in `a′`. This model has at least four sources of non-concavity in `a′`:

1. **Voucher eligibility** is a step function of pre-tax income, which includes capital
   income `r·a`. So `V_{j+1}` jumps discontinuously in `a′`.
2. **The food-stamp rule** `c ≥ ω_food` creates a kink.
3. **Discrete housing** and the LTV constraint create branch boundaries.
4. **The addiction step function** π_d(v) interacts with the budget.

Sources 1 and 2 sit exactly where this paper's action is — near the eligibility threshold
and the consumption floor. That is the worst possible place for a search heuristic to fail,
and it is consistent with coarse mode reaching a different equilibrium.

### Recommendation: don't fix the heuristic, remove the need for it

Fix Bug A anyway, but do **not** rely on coarse mode for anything reported. The welfare
margins in this paper are 0.1–1%, and R1 already flagged "the narrow margins of the welfare
comparison" as a robustness concern. A search that can land in the wrong basin cannot be
trusted at that resolution.

The principled replacement is **regime decomposition**: within each regime — voucher
eligible / not, food stamp binding / not, `v` ∈ {0, ≤v̄, >v̄} — the problem *is* concave.
Solve each regime exactly with a fast concave method (golden section, or EGM on the c/a′
margin), then take the max over the handful of regimes. That recovers the global optimum
**exactly** while still being fast, and it composes with the model simplification.

---

## 4. The biggest algorithmic win: stop recomputing the expectation inside the `a′` loop

Loop nesting in the renter block:

```
9552:  do future_financial_index            <- a' loop
9650:    do future_employment_index
9656:      do future_addiction_index_2
9668:        do future_unemployment_index
9679:          do future_voucher_index      <- expectation over shocks
9705:  value = flow_utility_vector(ffi) + future_utility_vector(ffi)
```

The expectation over next-period shocks is being evaluated **inside** the `a′` loop, and the
whole thing sits inside outer loops over current assets, productivity, employment, and so on.

The transition kernels depend on the *current* state and the *choices* — not on current
assets, except through the binary voucher-eligibility indicator:

| Kernel | Depends on |
|---|---|
| Ω_z(z′\|z) | current z |
| Ω_e(e′\|e,h′,d) | current e, chosen h′, d |
| Ω_κ(κ′\|e,e′,κ) | current e, κ |
| Ω_d(d′\|d,v,h′) | current d, chosen v, h′ |
| Ω_η(η′\|η,I^V,I^B) | current η, eligibility **(binary)**, sobriety |

So the conditional expected continuation value

```
EV[a′ ; z, e, κ, d, η, h′, v-regime, eligible]
```

can be **precomputed once per age** and then read as a table lookup in the Bellman loop.
Currently it is recomputed once per current asset gridpoint — 91 times for renters — and
again redundantly across housing and tenure branches.

Eligibility enters as a binary, so you need two copies, not 91.

**This is a large win — plausibly 10–50× on its own — and it is independent of language,
compiler, and model size.** Combined with §1 it likely dominates everything else on this list.

Implementation sketch: hoist a `precompute_EV(age)` routine that fills a rank-2 array over
(a′ × conditioning-index), called once at the top of each age iteration, then replace the
9650–9702 nest with an indexed read.

---

## 5. Should you switch language?

**No.** Keep Fortran.

- Fortran with `-O3` is at or near the ceiling for this workload. C++ or Rust would match it,
  not beat it. Julia can approach it but rarely exceeds it, and adds JIT warm-up and
  type-stability pitfalls.
- A rewrite of 24k lines would take months and would introduce bugs into a model whose
  results you are trying to defend.
- Your actual losses are `-O0` (§1), a broken search heuristic (§3), and a redundant
  expectation (§4). None of those are language problems. Fixing them in Fortran gets you
  everything a rewrite would, at a fraction of the risk.

The one defensible reason to move would be if you wanted GPU acceleration, which is a
different project and not warranted here.

**Worth doing instead of a rewrite:** split the single 24,338-line file into modules. It
compiles in 23s so build time is not the issue, but the monolith is why bugs like §3 hide —
`optimal_financial_1` being live across 2,000 lines of nested loops is only possible because
everything shares one scope.

---

## 6. Measured baseline

| | |
|---|---|
| Compile, `-O2` | 23 s |
| Threads launched | 40 (hardcoded), on 4 cores |
| CPU utilization at 4 threads | ~360% — parallelism is healthy |
| Resident memory | 612 MB |
| Progress | ~4 retirement-age backward-induction steps in ~3.5 min wall / 12.5 min CPU |

Retirement ages are the *cheap* ones — no labor supply choice, no drug choice. Working ages
carry the full choice set. So a single backward pass is hours, and a full calibration is
many passes over that. This is consistent with the paper's acknowledgement of needing a
borrowed high-powered machine.

**The order of attack, by expected payoff:**

1. `-O3 -march=native` (§1) — minutes of work, likely 3–10×
2. Precompute the expectation (§4) — a day of work, plausibly 10–50×
3. Model simplification (drop homeownership etc.) — 15–25×
4. Regime decomposition replacing the coarse heuristic (§3) — exactness *and* speed
5. Thread count from the environment (§2) — portability

These multiply. Together they plausibly take a solve from hours to well under a minute,
which is the threshold at which the whole revision can be run interactively on 4 cores.

---

## 7. What was built, and what still has to be checked

Three changes, in descending order of what they are worth.

### The a' search starts where it ended last loop

`warm_start_asset_search=1`. Between calibration loops the parameters move a
little, so the policy moves a little. The a' a household chose last loop is a
much better guess than anything a coarse sweep of the same grid produces, and
storing it costs about 34 MB.

The window is the previous argmax plus or minus `warm_start_half_width`, three
points out of forty one. If the window's own argmax lands on an edge the optimum
was trying to leave, the window is discarded and the full grid searched, so
escape from the window is exact.

**This required fixing section 3's Bug A first**, because the two are the same
bug. Refining around `optimal_financial_1` refines around the running maximum
across branches; a branch that does not beat the incumbent never updates it. The
per branch `branch_argmax_1` is what the warm start stores and what coarse mode
should always have used, so coarse mode is repaired as a side effect.

**What it does not do.** Edge detection catches an optimum leaving the window. It
does not catch a second peak sitting far outside it, and section 3's non
concavities are real: voucher eligibility is a step in capital income and the
food stamp floor is a kink, both where this paper's action is. One of the four
sources listed there is gone, the addiction step, because the hazard is smooth in
`v` now. Three remain.

**So verify before reporting anything.** `verify_asset_search=1` forces the full
sweep everywhere. Run the converged parameters both ways and diff the
`policy_function_*` files. At welfare margins of 0.1 to 1 percent that is not
optional, and it costs one equilibrium.

### The rental market clears by secant

`rent += 0.01 x excess demand` was tatonnement with a step nobody chose, inside
the loop the whole calibration multiplies by. Excess demand is monotone in rent,
so two (rent, excess) pairs give the root. Clipped to a doubling or a halving,
falling back to the fixed step when the two excesses are too close to divide by.

The housing price is left alone: it already updates with a weight of 0.02 on a
supply function rather than by a fixed step on an excess, and a secant on a fixed
point is a different and riskier object.

`labor_income_tax_rate` is a calibration target here, not the budget clearing
variable, so it is not part of this.

### lambda by secant, from a flow balance first step

In the stationary distribution onset times the mass using equals recovery times
the mass carrying the disorder, so prevalence is nearly proportional to onset.
The first update scales the onset by target over model, which crosses most of the
gap at once; the model opened at nine times the data, which a fixed step would
have taken about twenty loops to walk.

### What is measured and what is not

Nothing here is timed. The estimates are read off the code paths: the a' search
is the largest block of work in the solve and the window cuts it from 41 points
to 7, which should be worth 3 to 4x on the backward pass once the flow utility
and budget solve that do not shrink are allowed for. The rest is arithmetic on
TIMING.md. **Time a few ages before believing any of it.**

## 8. The previous dwelling was being solved twice

`include_homeownership`, `track_renters_housing` and `max_amortization_years`
were all switched off or collapsed in an earlier session, but the loop bounds
did not follow them. The backward induction still ran

```
do housing_status_index = lowest_housing_grid_point, track_housing_1*(housing_status_grid_size-1)
```

which with `track_housing_1=0` is two values, homelessness and the smallest
rental, and solved the same problem at each.

The same, provably, for a renter:

* `fixed_cost_to_moving` is zero
* `changing_homes` is assigned in three places and read in none, so the moving
  cost machinery is dead
* inside `calculate_after_tax_wealth`, `housing_status_index` appears only under
  `is_current_owner`, which requires `years_left_on_mortgage_index > 1` and never
  gets it with owning off

So one slice is solved and `copy_housing_state_slice` writes it into the others,
which the distribution and the moments still read. **Exact, and it halves the
backward pass.**

The lesson is the one the audit keeps repeating: switching a feature off at its
parameter does not remove the work, it removes the meaning of the work. Check the
bounds every time a switch moves.

### What the other proposed removals are worth

* **The negative asset grid: nothing.** Renter arrays are already allocated
  `negative_financial_grid_size:financial_grid_size`, that is 61 to 101, and the
  `a'` search already runs over exactly those 41 points. The 60 negative points
  exist only in owner arrays.
* **Deleting the owner routines: no run time**, since they are never called.
  Worth doing for clarity and compile time, not speed.
* **`track_renters_housing`: already zero**, and section 8 above is what was
  still being paid for it.

---

## 9. The distribution iteration, which became four fifths of the cost

Once the backward induction was fixed (sections 4, 7 and 8 together took it from
205s to 131s and then to 66s of the loop's 1,561s), the profile inverted. A
timed loop:

| stage | wall seconds | share |
|---|---|---|
| backward induction, all 60 ages | 262 | 17% |
| stationary distribution | ~1,300 | 83% |
| everything else | ~0 | |

655 sweeps, still contracting at 5.4e-3 when the loop ended.

**Why it is slow is structural, not incidental.** The operator moves mass one
age at a time and mass turns over once per lifetime, so the contraction factor
is roughly the per period survival rate, near 0.99. Nothing in the operator is
faster than that. At 0.99 per sweep it takes about 230 sweeps per order of
magnitude, so the last two orders cost as much as everything before them.

Three changes, in increasing order of how much thought they need before you
trust them.

### 9.1 The tolerance: no win here, and the reason is worth recording

`stopping_rule_stationary_distribution` is declared 1e-8, and the obvious move
is to loosen it: the moments are shares to three or four decimals and the
calibration's own rules are 1e-3 and 1e-4.

**That was tried and it did nothing, because the declared value never reaches
the iteration.** It is overwritten twice on the way in. There was a block at the
head of the calibration sweep resetting it to 1e-8 in both arms of an `if` whose
two branches were identical, and then, unconditionally since `include_addiction`
is a parameter equal to one, a second assignment to **2e-4** at the call site.

So the operative tolerance was already 2e-4 the whole time. The 655 sweeps a
loop takes are the cost of reaching 2e-4, not of reaching 1e-8, and there is no
slack left in the number. The dead 1e-8 block is removed and both surviving
sites now say which one is operative.

The general lesson, which is the same one section 8 taught: a value declared in
one place and assigned in three is not a setting, it is a guess. Grep every
assignment before concluding a constant does anything.

### 9.2 States with no mass propagate no mass

The distribution is extremely concentrated: over half of it sits at the lowest
asset point alone. Every empty state was still paying for a policy lookup, an
income calculation and a four deep accumulation. The skip is at
`negligible_mass = 1e-18`, fourteen orders below the operative 2e-4 stopping
rule, so the mass discarded cannot reach the convergence test let alone a
reported moment.

This is a per sweep saving, not a reduction in the number of sweeps, so it
cannot be read off the distance sequence. It is being measured against a twin
binary with `negligible_mass` set negative, which skips nothing; the number
goes here when that finishes. **Of the three changes in this section it is the
only one that survived.**

### 9.3 Aitken extrapolation: built, measured, rejected

Three iterates of a linearly converging sequence identify the limit: with
`d1 = x1 - x0`, `d2 = x2 - x1`, the ratio `d2/d1` estimates the contraction
factor and `x2 + d2*rho/(1-rho)` is the limit. Elementwise on the distribution
this is the ordinary delta squared step. It is implemented, guarded, and
**switched off, because the A/B says it makes things worse.**

Two binaries differing in nothing but `accelerate_distribution`, from identical
inputs, 2 threads each:

| sweep | accelerated | plain |
|---|---|---|
| 20 | 1.999e-2 | 1.999e-2 |
| 30 | 1.085e-2 | 2.464e-3 |
| 40 | 2.554e-3 | 6.412e-4 |
| 100 | 2.047e-3 | 5.421e-4 |

Identical to sweep 21, then three to four times *further* from the target at the
same sweep count. The steps are being accepted, not rejected by the guards, so
the extrapolation is genuinely running and genuinely hurting.

**Why, and it should have been predictable.** Delta squared assumes a single
dominant geometric mode. This operator moves mass one age per sweep, so for the
first sixty sweeps it behaves nilpotently rather than geometrically and an
estimated rho is meaningless; past that, a scalar rho is still compressing a
whole spectrum into one number. What the step does is knock the distribution off
a path that was converging, after which the plain sweeps repair it.

If anyone revisits it, the two things to try are gating the step until the sweep
count exceeds the life span, so the age transient is past, and requiring rho to
agree across two consecutive estimates first. Neither is implemented.

Two implementation choices are still worth keeping in the record, because the
obvious version of each is wrong. rho is estimated from **sums** of absolute
differences, not pointwise: a pointwise ratio is noisy exactly where mass is
near zero and extrapolates wildly in the states that matter least. And a bad
step is **rejected, not repaired** — thrown away on negative mass or a total
moving more than a part in a thousand, since negative mass in a distribution is
far worse than a slow iteration and a rejected step costs one vector operation.

`accelerate_distribution = 0` reproduces the plain sweep exactly. That is what
made the A/B possible, and it is the reason to leave the code in place rather
than delete it.

---

## 10. Two things that were built and then never connected

Both of these are the same failure, and it is a cheap one to make: the code is
written, it compiles, it looks finished in a diff, and nothing calls it. Neither
was a performance bug in the sense of a slow loop. Each was a facility that cost
nothing to add and gave nothing back because the last wire was missing.

### 10.1 The asset lottery counted its refusals into a threadprivate variable

`compute_asset_lottery` refuses in several cases rather than extrapolating, and
it counted the branch mismatch refusals so the refusal rate could be read before
the asset grid was cut. The counter was `threadprivate`.

A threadprivate counter cannot be read after the fact. Every thread but the
master gets its copy discarded when the parallel region ends, so the number that
reaches serial code is one thread's share of the work, and only by luck is it
even that. The counter was incremented tens of millions of times and printed
never.

The fix is a shared array with one row per thread and a stride wide enough to put
the rows on separate cache lines. No synchronisation, because no two threads
touch the same element, and no atomic, because an atomic on one word in a
subroutine called once per state per housing branch per age would serialise the
search that the parallelism exists to speed up.

The slot index is resolved on **first use by each thread**, not once in a
parallel region of its own. Threadprivate data is only guaranteed to survive
between two parallel regions when the thread count matches and dynamic
adjustment is off; a slot that quietly failed to persist would put two threads on
one element and lose counts to a race, which is the failure mode that produces a
plausible wrong number rather than an obvious one.

Four counts are kept: calls, refusals on the branch guard, refusals on the
geometry, and calls that returned a positive fraction. They are printed once per
equilibrium solve. **Read them before touching the grid.** A high fire share says
the grid is the wrong place to be spending points and can be cut. A high branch
mismatch share says the guard is refusing rather than the geometry, and the fix
is to fill the vectors from the winning branch instead of cutting the grid. A
high geometry share is the objective's own shape, and no amount of guard work
will change it — that is section 3's non concavity showing up in a second place.

### 10.2 The calibration checkpoint was written for the one loop that never called it

`write_calibration_state` and `read_calibration_state` are a pair, and the read
half sits at the top of `calibrating_model`. The write half was called only from
`transition_simulation`. So the calibration — the run that takes days, and the
only run anyone ever kills — wrote nothing, and the read at the top of it was
reading a file that it never produced. On a fresh machine it printed "no
calibration_state.dat" and started from the declared values, which is exactly
what the checkpoint existed to prevent, and it printed it so quietly that the
resume looked like it was working.

Three changes:

**The write is called from the calibration loop**, once per completed loop, so a
kill costs one loop instead of all of them.

**The four SMI parameters are in the file**, and the version tag went to v2 so a
v1 file is ignored rather than read short and misaligned. They had been wired
into the update block and not into the state, so a resumed run picked the housing
and drug parameters up where they left off and sent lambda_m, kappa_uem, rho_m
and rho_d back to their declared values. That is worse than not resuming: the
parameters that resume are the ones the SMI parameters have to be consistent
with.

**The converged distribution is checkpointed too**, which is the expensive half.
Recovering the parameters alone still pays 655 sweeps to rebuild the distribution
from the age one cross section, and those sweeps are most of a loop. Consecutive
parameter vectors differ by a damped step, so the last converged distribution is
a much better guess than a fresh initialisation. Loading it also means
`initialize_feasible_distribution` has to be skipped on that first loop, since it
would otherwise overwrite the warm start with everyone at age one holding
nothing — the flag is cleared immediately afterwards, so from the second loop on
the behaviour is unchanged.

The positional state file has one real failure mode, which is a write list and a
read list that drift out of step. It is checked mechanically rather than by
reading: 40 entries each, formats identical, names identical except the one
deliberate difference, `loop_count` written and `resumed_loop_count` read, since
a resumed run counts its own loops from zero.

---

## 11. The asset grid cannot be cut, and the lottery is why not

**The lottery is now OFF, because it broke the household budget constraint.**
Read section 15 before reading the rest of this section: everything below
describes a mechanism that is no longer active, and the reason it is not active
is not the one this section was written about.


The plan was: the two point lottery puts `a'` between grid points, so coarseness
stops costing accuracy, so the grid can go from 41 points to about 25 and the
backward induction gets proportionally cheaper. Section 10.1 built the counters to
check the premise before acting on it. Measured over one backward induction, ten
ages in:

```
calls                 =  177120
fired                 =      12   0.0068 %
refused branch match  =  160995  90.90   %
refused geometry      =   16113   9.10   %
```

**The lottery does not fire.** Twelve times in a hundred and seventy seven
thousand. Cutting the grid to 25 points on the strength of it would have been a
straight loss of accuracy in exchange for nothing, and the loss would have shown
up as a worse savings policy with no obvious cause.

**The reason is the guard, not the geometry**, which is the distinction the four
counters exist to draw. Nine refusals in ten are the branch match test. The `a'`
search loops over housing choices and refills `flow_utility_vector` and
`future_utility_vector` on each branch, so on return they describe the LAST branch
searched rather than the one that won. The guard notices and refuses, which is
correct — fitting a parabola to another branch would put the lottery in a
different basin entirely — but it means the machinery is inert.

**The fix is cheap and it is not "keep the whole vector".** The lottery needs the
objective at exactly three points, the argmax and its two neighbours, for the
winning branch. So either the winning branch's three values are kept as the search
goes, or they are recomputed once the housing choice is known. Recomputing three
points per state is nearly free next to the search itself. What must not happen is
another attempt to use the vectors as they stand.

Until that is done, `interpolate_a_prime` is effectively off whatever its value
says, and **the grid stays at 41 points.** The remaining 9 per cent, the geometry
refusals, are section 3's non concavity in `a'` showing up for the third time, and
no amount of guard work will remove those.

Worth stating plainly, because the opposite conclusion was one commit away: the
diagnostic did not confirm the plan, it killed it, and that is the whole reason
for measuring before cutting.

---

## 12. Five copies of the model were running at once, and it looked like something else

Worth recording because it produced a wrong diagnosis that survived several
attempts, and because the wrong diagnosis was about the machine rather than the
code, which is the kind that does not get checked.

Runs kept stopping partway through the first backward induction, at ages 13, 38
and 22 of sixty, with no error in the log, no exit code, and memory nowhere near
exhausted. The conclusion drawn was that the harness was reaping long background
tasks, and the response was to make the lottery diagnostic print every tenth age
so an interrupted run would still yield its number.

What was actually happening: **each launch left the previous one running.** By the
time this was noticed there were five `./hftf` processes alive, each asking for
four OpenMP threads on a four core box. Per age wall time was about 18 seconds. On
a single clean run it is about 4 seconds. So the box was oversubscribed roughly
five to one, everything crawled, and logs that had merely slowed to a crawl looked
like logs that had stopped.

Three things to take from it:

**`pgrep -f` and `pkill -f` match the shell that is running them**, because the
pattern appears in that shell's own command line. One `pkill -f 'lot/hftf'` killed
the compound command that was setting up the next run, which is how a setup step
died before `mkdir` had finished and left a missing directory as the only symptom.
Kill by PID, listed with `ps -eo pid,args` and an exact match on the program name.

**"The log stopped growing" is not evidence the process died.** Check `ps` for the
program by name before concluding anything, and check for *more than one*.

**The incremental reporting added in section 11 was the right change for the wrong
reason.** It is still worth having, since the counts are cumulative and a partial
run answers the question, but it was not needed to survive reaping. The lottery
numbers it produced stand: 177,120 calls and 12 fires is a property of the
objective, not of how fast the run was going.

The one real performance note in all this: **the model gets about 4 seconds an age
at 41 asset points and twelve joint states on four cores**, so a full backward
induction is roughly four minutes and a calibration loop is that plus the 655
distribution sweeps. Earlier timings in this file that look slower than that were
measured under contention and should not be compared with anything.

## 13. Treatment is never evaluated for an owner, and nobody owns, so it has not bitten yet

`policy_function_treatment` is written as

    policy_function_treatment(...) = (1-is_owner_better)*optimal_treatment_renter

with no owner term, while the line directly above it writes the addiction policy
the correct way, `is_owner_better*..._owner + (1-is_owner_better)*..._renter`. One
level down, the renter's choice between staying a renter and buying sets
`optimal_treatment_renter=0` in the buy branch. There is no
`optimal_treatment_owner` anywhere in the file: grep returns only the renter
variants.

So the treatment choice exists only in the renter stays renter branch. Any
household that owns, or that becomes an owner this period, is recorded as
declining treatment whatever it would have chosen, and its choice is never even
computed.

This is currently harmless, and that is the only reason it has not shown up as a
wrong number. In this calibration `model_homeownership_rate(1)` is exactly zero:
the smallest buyable house is 0.23 while the largest housing size consumed in
equilibrium is grid index 2, so no household ever buys, essentially all mass is
renter to renter, and the branch that works is the branch that carries everybody.

It becomes a real bug the moment the housing side moves. Anything that makes
ownership attainable, a larger rental ladder, a smaller
`size_of_smallest_house_hhld_can_buy`, a richer distribution, silently biases
treatment take up downward, and biases it hardest for exactly the households that
have assets. Fixing it means computing an `optimal_treatment_owner` through the
owner comparison routines and carrying it into the same two write sites, which is
a change to the owner branch and should be done when the owner branch is being
exercised rather than blind.

Noted here rather than fixed for that reason. If homeownership ever prints above
zero, fix this before reading any treatment moment.

## 14. The silent deaths were a stack overflow, not memory and not the compiler

Four calibration runs died with no error, no crash line and no message, the log
simply stopping partway through a backward induction. The first explanation
written here was that a concurrent `gfortran` invocation had pushed the machine
into swap and the kernel had reaped the run. That was wrong, and it is worth
saying why, because it sent two hours in the wrong direction.

The evidence against it accumulated in this order. A run died with no compile
anywhere near it. `dmesg` showed no OOM kill. There was no cgroup memory limit
in force and 15 GB free at the moment of death. The clincher was that a
bounds checked build died at the identical point, 83 ages into the backward
induction at age 37, on the same iteration, which is the signature of a
deterministic fault rather than of a kernel deciding at random which process is
biggest.

It was the stack. The parallel region allocates large automatic arrays per
thread, and the default OpenMP thread stack is a few megabytes. A thread walks
off the end of its stack, and there is no handler and no message: the process
dies where it stands. That is exactly a log that stops mid line.

The fix is two settings at launch, not a code change:

    ulimit -s unlimited
    export OMP_STACKSIZE=512M

With those in place the same binary on the same seeds passed the point it had
died at four times running and went on to solve 118 ages and complete a
distribution sweep.

So: if a run stops with no error, set the stack before you look for a bug in the
model, and before you blame whatever else happened to be running at the time.
Building while a run is going is still worth avoiding on a 15 GB box, but it was
not what killed these runs.

## 15. The asset lottery was violating the budget constraint

The model's own budget check had been firing about ten thousand times per
backward induction, and every single one of those states was a homeless
household. Not most of them: all of them, ten thousand out of ten thousand.
That is not what a numerical tolerance looks like, so it was worth chasing.

`compute_asset_lottery` finds the true optimum between two grid points by
fitting a parabola through the objective at the argmax and its neighbours, then
sets the lottery weight so that the MEAN asset holding equals that vertex.
Moving the mean off the grid point is the entire purpose of the routine.

Consumption never moved with it. It is computed once, in
`internal_computations`, as

    c = (resources - a(fin_index_1)) / (1 + tau_c)

from the grid point, and nothing recomputes it at the vertex. So the household
was recorded consuming as though it had saved `a(fin_index_1)` while saving
`frac*a(neighbour) + (1-frac)*a(fin_index_1)` in expectation. The budget then
fails by exactly

    frac * (a(neighbour) - a(fin_index_1))

which is the grid gap scaled by the weight.

That is measured rather than argued. Instrumenting the check to print the
weight, both grid points, consumption and resources gave 105 records matching
that expression to eleven decimal places, and every record whose weight was zero
cleared exactly. The violations ran to eight per cent of consumption.

Why only the homeless: the parabola refuses unless the argmax has a bracket and
the fit is concave, and homelessness is where the savings policy sits between
grid points often enough for it to pass those tests.

The fix is `interpolate_a_prime=0`. Over the same forty age steps of the same
backward induction, the unfixed build produced 443 violations and the fixed
build produced none.

To put the lottery back, consumption has to come from the lottery's mean rather
than from the grid point, which means the lottery has to sit INSIDE the `a'`
search rather than be applied after it: the flow utility changes with
consumption, so the argmax can move. That is a real change to the search, not a
one line fix, and the accuracy it buys should be measured against the grid it
would let you cut before anyone attempts it.

### The residual was a shared variable

While chasing the above: `x`, the budget residual in
`check_budget_constraint_clears`, was declared at module scope with no
`threadprivate`, and the check runs inside the parallel region. One thread could
overwrite it between another computing it and testing it, which is why some
printed records had a residual that did not match their own operands. It is a
local now, renamed `budget_residual_1`. Nothing in the model reads it, so the
race only ever corrupted the diagnostic, but a diagnostic you cannot trust is
worse than no diagnostic.


---

## 16. The lottery's branch-match bug is fixed, and the lottery still should not be on

Section 11 diagnosed the asset lottery firing twelve times in 177,120 calls and
named the cause: the `a'` search loops over housing choices refilling
`flow_utility_vector` and `future_utility_vector` on each branch, so on return
they hold the LAST branch searched rather than the one that won, and the guard
refused. Nine refusals in ten were that test.

**Fixed, and the counters say so exactly.** The three values the parabola needs
are captured at the moment a branch becomes the new global best, which is where
the winner is known, in threadprivate storage alongside the vectors they
replace. Measured over one backward induction:

```
                     before          after
calls                177,120         177,120
fired                     12 (0.007%)  159,822 (90.2%)
refused branch match 160,995 (90.9%)        0 (0.0%)
refused geometry      16,113 (9.1%)    17,298 (9.8%)
```

**And it still should not be switched on**, for a reason neither section 11 nor
section 15 states. `internal_computations` already refines `a'` on a sub grid of
`fin_num_of_internal = 50` points spanning the interval around the coarse point.
The policy's `a'` is therefore ALREADY off grid and already fine, and the lottery
adds a second, coarser estimate of the same quantity, fitted to a parabola
through three COARSE points. The policy then carries the refined `a'` and the
distribution carries the lottery's, they disagree, and the disagreement is
exactly the budget residual section 15 measured: with the lottery on and the
branch match bug fixed, the check still fired 31,530 times.

Section 15's fix was `interpolate_a_prime=0` and that remains right. The branch
match fix is kept because it is a real bug and because the counters are the only
evidence that would ever justify turning the lottery on.

### What this means for the asset grid

Section 11 wanted the grid cut from 41 points to 25 on the strength of the
lottery. The lottery is not the argument. **The refinement is**: the coarse grid
is a SEARCH grid whose job is to bracket the optimum, and the fifty point
refinement is what sets precision. A coarser search grid means fewer refinements
run, each spanning a wider interval at the same fifty points, so precision falls
but does not fall to the coarse spacing.

The `a'` search is quadratic in the coarse grid, so forty positive points to
twenty five is 2.56x, which on the measured loop cost takes a calibration from
about 130 hours to about 50. That is worth having and it is NOT free: the
budget's own warning applies, that the notches which make the objective not
single peaked live here, voucher eligibility as a step in income and the food
stamp floor, and that is where the welfare comparison happens. Any cut has to be
validated at both sizes against the targeted moments and both counterfactuals.

## 17. The warm start had no shape stamp, and it voided a grid comparison

`read_calibration_distribution` loaded `calibration_distribution{1,2}.dat` on
nothing but their existence. The files are a bare list of numbers with nothing
in them saying what array they came out of, and the reader fills whatever array
the running build happens to declare. So a build at a different asset grid reads
them anyway, and which way it fails depends on which direction the grid moved:

- **smaller array, silent corruption.** A cut from 40 positive asset points to
  25 takes the array from 101 points to 86. The read succeeds, having taken the
  first 86/101 of each slice of somebody else's distribution. The log said
  `warm start distribution loaded, sum= 45.718` where the file had been written
  with 51.362.
- **larger array, loud death.** Going the other way, 40 to 50, the read runs off
  the end: `Fortran runtime error: End of file`. That is the same bug wearing a
  louder coat, and it is the better of the two.

**What it cost.** The 25 point build's first moment block was compared against
the 40 point build's and read as evidence about the grid: average net wealth
10.7 per cent lower, bequests 12.9 per cent lower, the first distribution solve
taking 2445 sweeps against 340. All of it was the corrupt warm start. The 2445
sweeps are the distribution grinding back from a guess that was missing an
eighth of its mass, and the wealth gap is what that leaves behind at a tolerance
of 2e-4.

**The fix.** `write_calibration_distribution` writes the element count to
`calibration_distribution_shape.dat`, and the reader refuses a warm start whose
count does not match — and refuses an unstamped pair too, because a pair from
before the stamp existed cannot be told apart from a pair written at another
grid. Refusing costs one cold distribution solve. Accepting costs a wrong
answer that looks like a right one.

**The general form, which is worth more than the instance.** A restart file that
does not carry the shape of what it holds is not a restart file, it is a length
of tape. Every one of them in this program should say what it is: the parameter
state file happens to be safe, because it is scalars read one at a time with
`iostat`, but that is luck rather than design.

## 18. What the grid comparison has to look like to mean anything

The comparison that was voided is worth redoing, and this is the shape it has to
have. Three things have to be held down or it measures the wrong thing.

**Both sides cold.** Delete the warm start on every side. Otherwise the two
builds start their distributions from different places and the difference in
where they end up at a finite tolerance is start dependence, not discretisation.

**Both sides at the declared parameters.** Only the FIRST moment block, the one
printed after the first distribution solve, is comparable. Every later block
sits behind a parameter update that used the previous block's moments, so by
loop one the two builds are answering different questions. `grid_check.py` reads
the first block and nothing else for exactly this reason, and it prints the
parameters next to the moments so that a run which is not in fact like for like
shows itself.

**The sub grid held fixed.** `fin_num_of_internal` is set so that
`positive_financial_grid_size * fin_num_of_internal` is 2500 at every grid: 25 x
100, 40 x 62, 50 x 50. The refinement spans the two coarse gaps either side of
the search's answer and those gaps scale as 1/n, so this holds the sub grid's
spacing fixed, and it holds the refinement's cost fixed as well. What is left
varying is the state grid, which is the thing under test.

Forty is in that comparison rather than assumed. The model was built at fifty;
forty is an earlier unvalidated cut of mine whose own comment says in as many
words that it must be validated, and it never was.
