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
