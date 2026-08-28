# The mechanical audit of the Fortran, 28 August

Requested by the author: "go through the code and do the debugging needed to
make sure there are no mistakes." This file is the ledger of that pass. It is a
CODE audit -- races, uninitialised reads, out-of-bounds references, dead
diagnostics -- not the model-vs-paper audit, which is `FORTRAN_AUDIT.md`.

Method, in order, each step producing evidence rather than a reading:
compile with `-Wall -Wextra` and triage all 109 warnings; compile at `-O1` with
`-Wuninitialized -Wmaybe-uninitialized` for the dataflow class; run the leader's
vector cold under `-fcheck=bounds,do,mem,pointer`; run it again under
`-ffpe-trap=invalid,zero`; fix what is real; cross-check each find against the
stylized model as TRANSITION_LESSONS section 7 requires.

## Fixed in this pass

### 1. `!$omo threadprivate(cutoff_taxable_income)` -- a misspelled OpenMP sentinel

One character. A misspelled sentinel is a comment, so the directive silently
vanished and `cutoff_taxable_income` was the ONE work variable of its family
left shared across threads. Every thread writes it inside the budget routine
(line ~18205) and reads it back into its threadprivate `optimal_*` record, so
the recorded value could be another thread's household -- a data race in the
value-solve's hot loop. No number ever moved because the racy readback feeds
only `policy_function_cutoff_taxable_income`, which nothing reads; the value
function itself recomputes taxable income from the same formula inside the
callee. Fixed because the first consumer of that array would have inherited the
race. The 206 correctly-spelled threadprivate declarations, the `max_CPUs`
slot arrays (`ev_table*`, `interp_counters`, `vector_cpu_real`) and the four
`default(none)` parallel regions were checked and are race-free by
construction; this typo was the one outlier.

### 2. `income_to_avg_income` read uninitialised, every aggregation pass, live

`use_income_or_income_plus_assets=4` is the live configuration, and the ladder
in `stationary_equilibrium_statistics` that maps income to the wide
income-to-average CDF covered only cases 1, 2, 3. Case 4 fell through and the
ratio was read uninitialised at every state of the sweep -- caught by
`-Wuninitialized`, invisible in the output because the garbage bin index feeds
only the three income-profile output files (`income_to_avg_income_pdf_*`,
`profile_by_income_to_avg_income_wide_*`), no targeted moment. Those files have
been garbage in every run under flag 4. Fixed by routing 4 into the existing
case-3 branch, which already computes income plus financial assets plus home
equity -- the meaning flag 4 carries at its other two sites (the income CDF and
the quintile cut). The ladder was evidently not extended when 4 was invented.
**Author should confirm the case-4 numerator/denominator is the intended one.**

### 3. The `discount_factor_on_child` adjuster's dead branch armed a 0/garbage update

With `target_HO_of_old=0` it would steer the parameter by
`model_median_assets_to_income(1)/model_median_assets_to_income(3)` -- an array
of size `num_percentiles=1`, so index 3 is out of bounds, and assigned NOWHERE
in the file, so index 1 is the zero it was initialised to. Dead today only
because `discount_factor_on_child_adjuster=0`. Now stops with a message instead
of running, per the smooth-hazard guard's reasoning: a model that still
produces numbers is exactly how this would go unnoticed.

### 4. Two hardening fixes

- `intent(out) :: unconditional_probability_distribution` in `KKK_process` and
  `get_probabilities_KKK_process` changed to `intent(inout)`: neither routine
  assigns it (`KKK_process` writes the module variable
  `unconditional_employment_probability` directly instead -- note this aliases
  the dummy when the caller passes that very variable), and `intent(out)`
  makes the actual argument formally undefined, so a compiler that poisons
  intent(out) would hand the caller garbage.
- `thread_num=0` uncommented at both distribution-sweep sites: the only
  assignment was the `!$`-conditional line, so a build without `-fopenmp`
  would index the per-thread slice with an uninitialised integer.

## Found, live only in configurations not currently run -- NOT fixed, recorded

### `width` in `get_probabilities_KKK_process` is never assigned

`KKK_process` computes `width(i)` from its grid; `get_probabilities_KKK_process`
declares its own `width`, never sets it, and uses it throughout the
construction of `transition_prob_by_age` -- whose actual argument is
`employment_process`, the model's employment transition matrix. In the live
build this garbage is fully buried: `fixed_productivity=1` immediately
overwrites the whole of `employment_process` with the identity at every age,
and the equal-mass block rebuilds `unconditional_employment_probability`. **The
day someone runs `fixed_productivity=0`, working-age employment transitions
are built from uninitialised memory.** Left unfixed because the fix is a
design question (the routine exists so a hand-edited grid can be re-processed;
it should recompute width from the grid it is handed, as `KKK_process` does) --
flagged for the author rather than decided here.

### Dead code with its own defects

`rouwenhorst` and `linspace` are never called. `linspace` never assigns
`grid(n)`. The `-Wmaybe-uninitialized` descriptor warnings (`p12.offset` etc.)
all come from `rouwenhorst`'s allocation loop. Harmless while dead; delete or
fix before reviving.

## Triaged as not bugs

- **11 remaining out-of-bounds warnings**: all in `transition_simulation()` and
  the transition restart code, whose arrays are declared
  `dimension(1-solve_transition_dynamics:transition_length)`. In this
  steady-state build that collapses to `1:1` and the transition code indexing
  `0` and `transition_length-25` looks out of bounds; in a transition build the
  bounds are `0:75` and every flagged reference is legal. The code is only
  reachable when `solve_transition_dynamics=1`.
- **3 zero-trip loops**: `do ...=2,max_amortization_years` with
  `max_amortization_years=1` -- amortization deliberately configured off.
- **64 real-comparison warnings**: the `x .NE. x` family are deliberate NaN
  tests; the `==0`/`==1` sites compare flags assigned exact literals; the
  equality early-exit at line ~5733 can only cost wasted iterations, not a
  wrong number; the sentinel-equality tests at ~11198 gate diagnostics only.
- **`age_cpu_prev_1`/`age_wall_prev_1` maybe-uninitialised**: first-iteration
  timer diagnostics.
- **`-Wampersand` at 14103**: a debug print label split across lines.
- **Tabs, unused variables, unused label**: cosmetic.

## The runtime evidence

### The bounds checker caught a live out-of-bounds WRITE in the first pass

`-fcheck=bounds,do,mem,pointer`, leader's vector, cold. The value solve and the
first hundred distribution sweeps ran clean; the first firing of the
`diagnose_distribution_max` diagnostic then aborted:

    At line 21426: Index '-1' of dimension 1 of array 'dist_housing_1'
    below lower bound of 0

`dist_housing_1` was declared `0:housing_status_grid_size-1`, but the housing
dimension of the distribution starts at `lowest_housing_grid_point=-1` --
homelessness -- and the filling loop correctly runs over that dimension's own
lbound/ubound. So on EVERY 100th distribution sweep of EVERY production run
(`diagnose_distribution_max=1`), the homeless mass was read-modify-written into
the 8 bytes below the array. The victim is whatever the compiler placed there,
so the damage is layout- and optimisation-dependent; what is certain is that
the homeless column of the DIST_MOM by_housing diagnostic never received its
mass. This is the only defect found so far that corrupts memory on the live
path. Fixed by declaring the array from `lowest_housing_grid_point`; the
bounds-checked run was relaunched from the fixed source to scan the remainder
of the path (aggregation, moment construction).

### The relaunched bounds-checked run scanned the WHOLE path clean

Exit 0, 23 of 23 handover lines, a full moments block, zero violations: value
solve, distribution iteration with the fixed diagnostic firing, aggregation,
moment construction. The live path is certified free of out-of-bounds
references under `-fcheck=bounds,do,mem,pointer`.

Its moments differ from the unfixed binary's cold runs by more than the 2.5e-5
thread wobble (b 0.05814 against 0.05788, cbar 0.002529 against 0.002451).
Two explanations are possible and the run cannot tell them apart: `-O1` against
`-O3` floating-point differences amplified through the tolerance-stopped
solver, or the dist_housing_1 corruption having been numerically consequential.
The attribution run -- same `-O3` flags, fixed against unfixed source -- is
recorded below.

- `-ffpe-trap=invalid,zero`: RESULT RECORDED BELOW.

## The stylized-model cross-check (TRANSITION_LESSONS section 7)

| bug found here | does the stylized model have it? |
|---|---|
| A misspelled OpenMP sentinel silently deleting a directive | **Does not arise.** The stylized model is single-threaded Python with no comment-pragmas that alter semantics; there is nothing whose misspelling degrades to a comment. |
| A mode-flag ladder not extended when a new mode was added, falling through to an uninitialised value | **Does not arise today**: `grep elif` over `stylized.py` and `calibrate.py` returns zero if/elif ladders on mode flags. The class is worth naming there anyway: in Python the same mistake raises `UnboundLocalError` -- it fails loud where the Fortran failed silent, which is the difference that let this one run for weeks. |
| A routine's local (`width`) shadowing a sibling's computed quantity and never being computed | **No.** The stylized model passes derived quantities as function arguments or recomputes them locally; there are no sibling routines sharing a convention that one forgot. |
