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

### The attribution run: the fixes are numerically neutral on the live path

Fixed source against unfixed source, both at the production `-O3` flags, cold,
the leader's vector. All 23 moments agree to a worst relative difference of
2.3e-5 -- the size of the measured run-to-run thread wobble (2.5e-5), and on
the same wobble-prone moments (`kappa_ued`, `lambda_d`, `theta`, `tau_u`). So:

- every fix in this audit leaves the model's numbers unchanged, as each fix's
  analysis predicted -- the corruption's victim was diagnostic-only, the race
  fed an array nothing reads, the uninitialised ratio fed only profile files;
- the moment drift seen in the `-O1` bounds-checked run against the `-O3` runs
  was optimisation-level floating point amplified through the
  tolerance-stopped solver, not the fixes;
- no archived measurement needs a corruption adjustment.

### `-ffpe-trap=invalid,zero`: the IEEE_INVALID flag is a dead block's 0/0

The trapped binary aborts at startup, in `set_SS_benefits`, before the first
solve: the Bayes reversal that traces which employment state a retiree's
lifetime income came from divides by column sums of `employment_process` and
`unemployment_process`, and columns nothing transitions into sum to zero, so
the reversal is 0/0 = NaN. This is where every production run's
IEEE_INVALID_FLAG has been coming from.

It reaches nothing. `model_lifetime_income_conditional_on_last_period_shock`
and its average are consumed by NO other line of the file -- the benefit
actually paid is the linear `ss_replacement_rate*employment_grid` rule computed
just below (the block's own comment records replacing the PIA schedule). The
two denominators are now floored at 1e-14 so the block is defined and the trap
can scan past it; the block itself is a deletion candidate, the author's call.

The trapped run was relaunched with the floors and reached the AGGREGATION
before the next trap: `calculate_marginal_non_housing_utility`, called for
every age-one state cell to build `model_value_of_life` -- the aleph pipeline
-- raised `0**(-risk_aversion)` at zero-mass corners where the cell is
infeasible and consumption or the dwelling is zero. The Inf was discarded by
the `distribution_mass_used>0` guard sitting directly below the call, so no
number ever moved (aleph has always printed finite); the call now sits INSIDE
the guard, which is the same number with a clean FPU. The sweep continues; each
further trap gets the same treatment -- prove it masked, silence it at the
source, rerun -- until the run reaches the moments block trapped.

The third trap took three hours to reach (the run shared its four cores with
an orphaned model process for all of them): line 8131, the tenure-switcher
statistics in `stationary_equilibrium_statistics`. Twelve normalizations share
three subpopulation masses as denominators -- `model_mass_switchers`,
`model_mass_non_switcher_renters`, `model_mass_switchers_mortgages` -- and a
sweep in which nobody switches tenure makes the first of them 0, so the first
division is 0/0 (the numerators accumulate only alongside the mass). All
twelve normalized statistics are dead ends: accumulated, normalized, and never
read again anywhere in the file, so the NaN reached nothing. Same class as the
21 statistics-tail denominators, same treatment: all three masses floored at
`10.d0**(-14)` at every division site (12 sites, two of them split across a
continuation line, which the first patch attempt missed and its count assert
caught). The sweep was relaunched.

The fourth trap fell out of the third's fix: with the switcher block floored,
the same statistics call ran on to line 8185 and divided by
`mass_of_owners(time_period)` -- the diagnostic statistics run early in the
solve, when the initial distribution has everyone renting and no one yet owns,
so every owner-conditioned average is 0/0. At any converged point owners are
roughly sixty per cent of households and the floor changes nothing. Floored in
one batch, 11 sites: the four divisions by `mass_of_owners`, the four by
`model_average_owner_occupied_unit_size` (zero exactly when owners are absent;
a fifth textual match at line 8224 is inside a quoted write label and was left
alone), and -- the symmetric corner -- the two by `mass_of_renters` and one by
`total_renters`. NOT floored, deliberately: `working_age_mass`,
`model_total_income` and `model_total_net_wealth_1` are whole-population
aggregates that cannot be empty, so a zero there is a genuine fault the trap
should still catch.

The fifth trap corrected the fourth's reasoning, and this is the entry worth
reading twice. Three denominators were deliberately left unfloored on the
grounds that a whole-population aggregate cannot be empty, and one of them --
`working_age_mass` -- trapped on the next run at line 8191. It is not the
working-age population. Its single accumulator sits three conditions deep, in
the `amortization_used>1` branch under `income_1>0` under `in_retirement==0`,
so it is the mass of working-age owner-occupiers holding a mortgage with more
than one year of amortization and positive income. It empties in exactly the
all-renter corner the fourth trap was about. **The name was read instead of
the accumulation site, and the name was wrong**; every remaining judgement of
this kind in this file should be made by reading where the variable is summed.

Re-checked the other two by their accumulators rather than their names:
`model_total_income` is `model_output + investment income + bequests`, a
genuine aggregate that no live point can zero, and stays unfloored;
`model_total_net_wealth_1` sums net wealth over the whole distribution, which
is exactly zero when every household rents with no financial assets -- the
same early corner -- so it was floored at both its division sites before it
could become the sixth trap. Sites floored this round: 3.

The remaining unfloored denominators in the statistics and output routines are
inventoried and the trap is left LIVE on them deliberately: `model_GDP`,
`model_average_labour_income`, `model_average_net_wealth`, `median_income`,
`housing_price`, `model_output`, `model_total_hours` and the rental-supply
family are genuine aggregates or prices, and a zero in any of them is a real
fault the sweep should still stop on. Two are conditional and may yet trap
from the final output path -- `model_mortgages` and
`homeowners_originating_mortgage`, both at a point where nobody holds a
mortgage; if they do, they belong to the benign family and get the same floor.

## The stylized-model cross-check (TRANSITION_LESSONS section 7)

| bug found here | does the stylized model have it? |
|---|---|
| A misspelled OpenMP sentinel silently deleting a directive | **Does not arise.** The stylized model is single-threaded Python with no comment-pragmas that alter semantics; there is nothing whose misspelling degrades to a comment. |
| A mode-flag ladder not extended when a new mode was added, falling through to an uninitialised value | **Does not arise today**: `grep elif` over `stylized.py` and `calibrate.py` returns zero if/elif ladders on mode flags. The class is worth naming there anyway: in Python the same mistake raises `UnboundLocalError` -- it fails loud where the Fortran failed silent, which is the difference that let this one run for weeks. |
| A routine's local (`width`) shadowing a sibling's computed quantity and never being computed | **No.** The stylized model passes derived quantities as function arguments or recomputes them locally; there are no sibling routines sharing a convention that one forgot. |


## The SUD rate cannot be reached from the parameters we search, and here is the arithmetic

**MEASURED 29 AUGUST, over the whole 59-point post-grid-fix archive.**

`lambda_d` -- the substance use disorder rate, the share of the WHOLE population
in the disorder -- comes back at 0.7 per cent against a target of 3.68, off by
81 per cent, at EVERY point ever measured. It is the single largest term in the
loss and it has never moved. This is why.

**IT IS NOT THAT THE SEARCH HAS NOT TRIED.** `lambda_addiction` spans 4.51 to
6.93 across the archive, a range of 54 per cent, and the correlation between it
and `lambda_d` over the 54 points with a loss below 0.6 is **-0.31** -- not weak,
WRONG-SIGNED. The instrument the model names for this moment does not move it.

**WHAT IS ACTUALLY PINNED IS THE RATIO.** `lambda_d / b`, the disordered share
of users, sits between 0.077 and 0.093 at every sensible point in the archive.
It is 0.41 in the data (0.0368 / 0.089). The model is not missing the SUD rate;
it is delivering a disorder-to-use ratio five times too small, and no
combination of the twenty-odd searched parameters shifts it.

**THE FLOW BALANCE SAYS WHY.** In steady state, onset times the non-disordered
users equals the recovery hazard times the disordered:

    onset * (b - lambda_d) = probability_of_stopping_addiction * lambda_d

so the ratio `lambda_d / b` is pinned by `onset / (onset + recovery)` and nothing
else. Inverting it at the declared recovery rate of 0.025 gives the onset the
model is actually delivering, point by point:

| lambda_addiction | b | lambda_d | implied onset |
|---|---|---|---|
| 4.51 | 0.188 | 0.0157 | 0.00229 |
| 5.19 | 0.083 | 0.0067 | 0.00220 |
| 5.55 | 0.219 | 0.0185 | 0.00230 |
| 5.83 | 0.085 | 0.0070 | 0.00225 |
| 6.51 | 0.107 | 0.0082 | 0.00206 |

Over all 54 points the implied onset lies in **0.00164 to 0.00307**. A 54 per
cent range in the hazard produces a 5 per cent range in the onset it is supposed
to control.

**BECAUSE THE HAZARD IS A PRICE AND HOUSEHOLDS PAY IT BY USING LESS.** Under
`smooth_addiction_hazard=1` the onset is `1 - exp(-lambda * quantity)` and the
quantity is a CHOICE. Raise lambda and the household cuts the quantity by very
nearly the reciprocal, so the product -- and therefore the onset, and therefore
the disorder stock -- is invariant. The declared benchmark has this in plain
sight: lambda 0.027364 at a mean quantity of 0.0585 gives an onset of 0.0016;
we are running lambda at 5.5, two hundred times larger, and the implied onset is
0.0022. The quantity has absorbed essentially all of it.

**WHAT WOULD BE NEEDED.** To put `lambda_d` on 0.0368 while `b` stays on 0.089,
the ratio has to be 0.41, so onset must be 0.70 times the recovery hazard:

- **through the onset**: 0.0176, which is **8.1 times** what the model delivers,
  and unreachable through `lambda_addiction` for the reason above;
- **through the recovery hazard**: 0.0031 against the declared **0.025**, a
  factor of eight the other way.

`probability_of_stopping_addiction` is declared at 0.025 and is **not in the
search vector**. It is the only quantity in the balance that is both free and
effective. Its homeless counterpart is recomputed as
`mu_homeless * probability_of_stopping_addiction`, so it would follow, and
`mu_homeless` -- which owns the Milby ratio moment `mu_H`, currently within 1
per cent -- would not have to move.

**WHY REWEIGHTING THE LOSS DOES NOT HELP, AND WAS TESTED.** Raising
`lambda_d`'s weight from 3 to 6 while dropping `beta` and `h_2` to 0.5 leaves
the ranking of the archive COMPLETELY unchanged, top five identical in order.
A moment that is 81 per cent off at every point is a constant added to every
loss; weight cannot discriminate on it. The only points where `lambda_d` gets
above 1.9 per cent are the ones where `b` runs to 0.22 and treatment take-up to
0.59 -- the SUD rate bought by making a quarter of the population users, which
is not the trade the weight was meant to buy.

**THE HONEST STATEMENT.** The b target and the lambda_d target are, at a
recovery hazard of 0.025 and with an endogenous quantity, arithmetically
incompatible. This is not a search failure and more measurement will not fix it.
It is a scope decision and it belongs to the author.


## The identification the author proposed: a FLOW for the onset, the STOCK for recovery

**PROPOSED 29 AUGUST BY THE AUTHOR, and it is better than what this file
recommended an hour earlier.** The note above ended by suggesting
`probability_of_stopping_addiction` be opened and bracketed on the SUD rate,
and it computed that recovery would have to FALL from 0.025 to 0.0031. That
figure is right only while the onset stays broken -- it holds the model's
DELIVERED onset of 0.0022 fixed and asks recovery to absorb the whole
discrepancy. It is not the recommendation, and the direction it implies is
wrong.

**THE STRUCTURE.** Two parameters, two moments, and they separate cleanly:

    onset    <- a FLOW moment: the rate at which use converts to a disorder
    recovery <- the STOCK moment: the SUD prevalence, given that onset

Prevalence is a function of the RATIO onset/(onset+recovery) and of nothing
else, so it cannot identify both. A conversion flow identifies the onset on its
own, and the prevalence then identifies recovery. Triangular, and it is exactly
the shape the mental illness side already has: `lambda_m` is pinned by
`1-(1-lambda_m)**10 = 0.50`, a recovery-within-ten-years probability. The
addiction side has no analogue, which is the asymmetry.

**WHY RECOVERY IS THE RIGHT INSTRUMENT FOR THE STOCK AND LAMBDA IS NOT.** The
onset is `1-exp(-lambda*quantity)` and the quantity is a household CHOICE, so
lambda is a price that households pay by using less; the archive shows the
product moving 5 per cent while lambda moves 54. The recovery hazard is an
exogenous transition probability with no such offset. Bracketing prevalence on
recovery therefore works where bracketing it on lambda demonstrably does not.

**THE DIRECTION REVERSES.** With the onset pinned to a data conversion rate --
of order 0.02 to 0.05 a year, fifteen to twenty times what the model delivers --
the ratio at recovery 0.025 would land far ABOVE the data's 0.41, so recovery
must RISE to bring prevalence back down, not fall. Holding the target ratio at
0.41 gives recovery = 1.44 * onset, so an onset of 0.046 wants recovery near
0.066 and an onset of 0.023 wants 0.033. Both are above the declared 0.025.

**THE OVERIDENTIFYING CHECK, AND IT PASSES.** A recovery hazard of 0.066 implies
a median time to remission of 1-(1-0.066)**t = 0.5, or 10.1 years. The remission
literature puts the median at roughly five years for cocaine and fourteen for
alcohol, so 10.1 sits inside the band rather than at an edge. The prevalence
target, the use target, the conversion flow and the remission duration are four
numbers from three sources and they are mutually consistent at an onset near
0.03-0.05 and a recovery near 0.05-0.07. The model is at onset 0.0022 and
recovery 0.025: the onset is the broken one, by a factor of fifteen to twenty.

**THE WEAK POINT, NAMED.** A cumulative use-to-dependence probability is per
LIFETIME of use and the model's onset is per PERIOD of use, so converting one
to the other needs a window assumption, and the implied hazard moves by a factor
of two between a five year and a ten year window. An annual incidence -- past
year SUD onset among past year users -- needs no such assumption and is the
cleaner moment if one can be computed on the same universe as the 3.68 per cent.
That universe is NSDUH adults 26 and over, illicit drug use disorder other than
marijuana.

**NOT CLEAN, AND WORTH SAYING.** Recovery also moves `b`: a shorter disorder
means a different value of using, so the total user share responds too. The
system is triangular in the direct channel, not in general equilibrium. It
should still bracket, because the direct channel dominates, but the two brackets
will interact and the loop should be run to convergence rather than one pass.

**WHAT IT COSTS THE SEARCH.** `lambda_addiction` stops being searched and
becomes derived each loop from the model's own mean quantity, which the existing
secant block already computes. The vector loses a coordinate, the loss loses its
single worst term, and `probability_of_stopping_addiction` gains an adjuster and
a bracket on `sud_rate_data`. `probability_of_stopping_addiction_if_homeless`
already follows as `mu_homeless * probability_of_stopping_addiction` and needs
no change.

**STILL THE AUTHOR'S CALL: this is a model change and nothing here is
implemented.** What is needed from the author is the conversion number and its
source.


## Sharpening it: lambda is not dead, it has the wrong sign on b

**The entry above says the onset channel does not respond to lambda. That is too
strong, and the archive says something more precise.** Decompose the moment:

    lambda_d  =  (disordered share of users)  x  (share of population who use)
              =  ratio  x  b

Over the 54 sensible points, correlations with `lambda_addiction`:

    corr(lambda, ratio)     = +0.187      <- the intended effect, right sign
    corr(lambda, b)         = -0.362      <- the side effect, twice as strong
    corr(lambda, lambda_d)  = -0.385      <- the product, dominated by b

So lambda DOES raise the disordered share of users. It raises it by making use
more dangerous, which is also a reason not to use, so `b` falls harder than the
ratio rises and the product goes backwards. The lowest-lambda point in the
archive has b = 0.174 at a ratio of 0.085; the highest has b = 0.050 at a ratio
of 0.109.

**WHY RECOVERY IS A BETTER INSTRUMENT, STATED PROPERLY.** Not because lambda has
no effect, but because the two instruments differ in their side effect on `b`.
The onset is the probability that using CAUSES a disorder, so it is a direct
deterrent to using. The recovery hazard sets how LONG a disorder lasts once
acquired; it enters the value of using too, but at one remove and discounted, so
it should move `b` less per unit of ratio bought. That is a conjecture about
magnitudes, not a theorem, and it is worth measuring rather than asserting.

**THESE ARE MARGINAL CORRELATIONS OVER A SEARCH THAT MOVED TWENTY PARAMETERS AT
ONCE, so they are confounded and cannot be read as derivatives.** This file has
already made that mistake once, reading a marginal correlation of +0.07 on
lambda_addiction as a partial and being contradicted by the Jacobian. The clean
test is `LAMBDA_STRESS.txt`: two points at lambda 30 and 100, five and fifteen
times the top of the searched range, with all twenty-four other coordinates
held at the current best. That is the derivative, and until it lands the
question of whether a large enough lambda would simply work is OPEN.


## SECTION 7 CROSS-CHECK, RUNNING BACKWARDS: the stylized model found this first

**THE AUTHOR SAID THE STYLIZED MODEL NEEDED A VERY LARGE LAMBDA, AND THE
STYLIZED MODEL'S OWN CALIBRATION NOTE NOT ONLY CONFIRMS IT BUT DIAGNOSES THE
QUANTITATIVE MODEL'S PROBLEM IN ADVANCE.** From `code/stylized/calibrate.py`,
around the LAM_LO/LAM_HI bracket:

    The rate does not saturate below the target, it just gets there slowly,
    because a household that faces a steeper hazard per unit BUYS FEWER UNITS:
    v falls roughly as 1/lambda, so pi(v) = 1 - exp(-lambda v) creeps rather
    than jumps.

That is the offset mechanism this file spent the afternoon inferring from the
steady-state flow balance in the quantitative model. It was already written
down, in the other model, with the same functional form and the same
conclusion.

**THE NUMBERS.** The stylized model's calibrated hazard:

    calibrated.json            lam = 106.8
    best_drug.json             lam =  84.6
    calibrated_theta020.json   lam = 253.1

and its bracket is `LAM_LO, LAM_HI = 0.05, 20000.0`, deliberately wide because
a ceiling of 4000 BOUND: at lambda = 4000 the adult SUD rate reached 3.38 per
cent against the same 3.68 target, so the bracket walked to its ceiling and
reported a corner as a calibration.

**THE QUANTITATIVE MODEL HAS BEEN SEARCHING LAMBDA OVER 4.51 TO 6.93.** That is
twenty to fifty times below the stylized model's calibrated value for the same
hazard in the same functional form against the same target. The search was
never given room to reach the answer, and everything this file recorded about
lambda "not moving lambda_d" was measured inside a window far too narrow to
show movement. The correlations stand as facts about that window; the inference
that the channel was structurally dead does not.

**WHY THIS IS THE SECTION 7 RULE FAILING IN THE DIRECTION IT WAS NOT WRITTEN
FOR.** The rule says a bug found in the stylized model is checked against the
quantitative model before it is closed. Here the stylized model did not find a
BUG, it found a CALIBRATION FACT -- that this hazard needs to be two orders of
magnitude larger than a naive bracket allows -- and a fact is not a bug, so
nothing triggered the cross-check and the quantitative model inherited a bracket
built for the wrong scale. The rule should be read to cover both.

**THE CEILING, WHICH IS THE REAL CONSTRAINT AND IS NOT LAMBDA.** The stylized
model's SUD rate tops out at the PARTICIPATION rate: once every user
progresses, sud = part = 5.13 per cent. The quantitative analogue is
`lambda_d <= b`. Today b = 0.085 and the target is 0.0368, so the ceiling is
comfortably above the target -- but b FALLS in lambda (correlation -0.36 over
the archive, and b was already down to 0.050 at lambda 6.93). If b falls below
0.0368 before the ratio rises enough, the target becomes unreachable no matter
how large lambda is. That, and not the onset, is what the stress points have to
settle.

**STRESS POINTS NOW SPAN THREE ORDERS OF MAGNITUDE**, all with the other
twenty-four coordinates held at the current best so the result is a derivative
rather than a confounded marginal: lambda = 30, 100 and 1000, against a search
range that has never left 4.5 to 6.9. The stylized model's calibrated 106.8
sits inside that span.


## What the two targets actually require, and which instrument does which job

**FROM THE CURRENT BEST (point_56bb8e81a5, loss 0.2237):**

    b         0.0879  ->  0.0890    x1.01
    lambda_d  0.00807 ->  0.0368    x4.56
    ratio     0.0919  ->  0.4135    x4.50

**b IS ALREADY ON TARGET.** It is one per cent low, and lowering it would move
it away. The whole discrepancy is the ratio, and the ratio is the whole of
lambda_d's gap: x4.50 against x4.56. Any instrument used to move b has to move
it by one per cent and no more -- its real job is to HOLD b while lambda moves
the ratio, because lambda cuts b hard as a side effect.

**THE TWO INSTRUMENTS ARE TRIANGULAR, WHICH IS WHY THIS CAN WORK.** Over the
archive:

    corr(lambda_addiction, ratio) = +0.19    corr(lambda_addiction, b) = -0.36
    corr(discount_factor,  ratio) = +0.18    corr(discount_factor,  b) = -0.94

and the ratio is close to flat in the discount factor across the range measured
-- 0.084, 0.073, 0.066, 0.083 as the discount falls from 0.9975 to 0.9910 while
b nearly triples, 0.087 to 0.202. So lambda sets the ratio and the discount
factor puts b back, and the second does not undo the first.

**THE OVERSHOOT AND THE INTERACTION, BOTH WORTH WATCHING.**
- lambda 30 gives a ratio of 0.434 against 0.414 wanted, so it slightly
  OVERSHOOTS; the exact value is nearer 27 or 28, which is also what the
  converge.py bound comment predicted from the arithmetic.
- The discount factor also owns beta, which is +44 per cent. Restoring b from
  0.0064 to 0.089 is a factor of FOURTEEN, and the archive only shows a factor
  of 2.3 across 0.9975 to 0.9910. Reaching fourteen would take the discount far
  below anything measured and would push beta through its target rather than
  onto it. So the discount factor is unlikely to carry the b repair alone, and
  relative_share_of_addiction_1 (corr +0.49 with b, +0.09 with the ratio) and
  addiction_scalar_1 (+0.37) are the other two hands on it. That is a phase B
  job, not a single sweep.


## The SCF is in the repository, so the wealth targets are computable rather than arguable

**COMPUTED 29 AUGUST from `data/SCF_2022.dta`, weighted by `wgt`.** The author
asked whether the macro literature justifies a higher wealth to output ratio and
then pointed out the SCF could settle it. The SCF is already the paper's source
for the homeownership rate, mortgage over housing wealth, the earnings
dispersion and the bottom half wealth share, and `data/SCF_aggregate_stats_code.txt`
ALREADY opens with exactly this calculation, so nothing new had to be assumed.

**NET WORTH TO INCOME, SCF 2022:**

    all households                      7.493
    aged 26-65 (the paper's universe)   5.704
    aged 26-65, positive income         5.594

    aggregate net worth  139.1 trillion, aggregate income 18.6 trillion

**WHY THAT IS NOT DIRECTLY THE MODEL'S beta, AND THE TRAP IN THE LITERATURE.**
The model's moment is `model_total_net_wealth / model_GDP_incl_imput_rent` --
the denominator is OUTPUT, not household income. SCF aggregate income is 18.6
trillion against a 2022 GDP near 25.7, so it is about 0.72 of GDP, and the SCF
ratio converts to roughly 5.4 on a GDP basis. The same trap sits in the number
everyone quotes: Piketty and Zucman's famous four to seven is wealth over
NATIONAL INCOME, which is about 0.8 of GDP, so their US figure near four to
four and a half is nearer 3.2 to 3.6 as a wealth to GDP ratio. Quoting it as if
it were a GDP ratio would OVERSTATE the case for raising the target.

So the honest range on a GDP basis is roughly 3.2 to 3.6 from Piketty-Zucman
and roughly 5.4 from the SCF, and the model sits at 4.32 -- inside the span,
above the declared 3.0. The declared 3.0 traces to a different object again:
the code's own comment derives it from BEA private fixed assets over NIPA
output, on the argument that the rental stock sits on rental companies' books
rather than households'.

**THE THREE NUMBERS DISAGREE BECAUSE THEY HAVE THREE DIFFERENT DENOMINATORS AND
THREE DIFFERENT NUMERATORS.** Any change to the target has to say which one it
is adopting. The cleanest resolution is not to argue the target up but to make
the MOMENT match the survey: net worth over household income is computable in
both the model and the SCF on the same 26-65 universe the paper already uses,
which removes the conversion entirely. That is a moment change and it is the
author's call.

## The bottom of the wealth distribution is wrong in a way the median hid

**SHARE OF AGGREGATE NET WORTH HELD BY THE BOTTOM x PER CENT:**

    pct        model      SCF all    SCF 26-65
      1      0.00012     -0.00158     -0.00225
      5      0.00060     -0.00279     -0.00422
     10      0.00232     -0.00287     -0.00446
     20           --     -0.00226     -0.00375
     25      0.02907     -0.00133     -0.00262
     50      0.15110      0.02202      0.02257

**EVERY BOTTOM SHARE BELOW THE MEDIAN IS NEGATIVE IN THE DATA AND POSITIVE IN
THE MODEL.** The data's bottom quarter holds MINUS a quarter of one per cent of
net worth; the model's holds plus 2.9. The model has no household with negative
net worth at all, because it is constrained at or near zero, while the SCF's
bottom decile is net debtors -- student loans, underwater mortgages, revolving
credit. The bottom half gap that has been visible all along, 0.151 against
0.0252, is the mildest reading of this: it is the only one where the data is
still positive, so it understates the discrepancy by hiding the sign flip
underneath it.

**The declared bottom half target of 0.0252 checks out**: SCF 2022 gives 0.0220
over all households and 0.0226 over 26-65, so the number in the code is right
to within rounding and universe choice.

Written to `data/SCF_wealth_shares.txt`.


## beta becomes a BAND at 4.0 to 4.5, and it pins the discount factor rather than freeing it

**THE AUTHOR'S DECISION, 29 AUGUST: take the wealth to output target from
Piketty and Zucman (2014) and treat anything in 4.0 to 4.5 as a hit.**
Implemented in `score_points.BAND`: inside the band the gap is zero, outside it
the gap is measured to the nearer edge so the moment stays continuous. The
current best goes from 0.2237 to 0.2076 and the ranking does not reshuffle;
beta leaves the worst-four entirely.

**THE CONVERSION WAS PUT TO THE AUTHOR AND THE BAND WAS CONFIRMED ANYWAY.**
Piketty and Zucman measure private wealth over NATIONAL INCOME, about 0.85 of
GDP, so their US 4.0 to 4.5 converts to roughly 3.4 to 3.8 against this model's
denominator, which is output. Taking 4.0 to 4.5 directly is taking their number
without the conversion. Recorded so the choice stays visible rather than being
re-derived and doubted later; the band is implemented as given.

**THE CONSEQUENCE THAT MATTERS FOR THE SEARCH, AND IT IS NOT THE OBVIOUS ONE.**
The band does NOT free the discount factor to do the b repair. It pins it:

    discount   beta        b     in band?
    0.99180   3.030   0.2192      NO
    0.99380   3.380   0.1866      NO
    0.99580   3.779   0.1459      NO
    0.99675   3.892   0.1504      NO
    0.99810   4.188   0.0805      yes
    0.99900   4.156   0.1156      yes

Only 0.998 and above keeps beta inside 4.0 to 4.5. Under the old target of 3.0
the search was pulled DOWN toward 0.9918, where beta is 3.03 -- and b there is
0.219, two and a half times its own target. So the old target was actively
pulling b off target, and the band stops that. That is the real gain, and it is
worth more than it looks: b is the moment at weight three that the current best
has to within one per cent.

**BUT THE b REPAIR AT HIGH LAMBDA NOW HAS TO USE A DIFFERENT INSTRUMENT.** At
lambda 30, b is 0.0064 and needs 0.089, a factor of fourteen, and the discount
factor can no longer be spent on it. `addiction_scalar_1` is the candidate --
bounded (1e-10, 1.0), currently 0.0172, so it has the range, and it owns no
other headline moment. `relative_share_of_addiction_1` is boxed into
(0.45, 0.51) and is too narrow for fourteen-fold on its own.

**LAMBDA30_REPAIR.txt IS NOW PARTLY OFF THE PATH.** Its four points sweep the
discount factor to 0.984 at lambda 30, which under the band puts beta far below
4.0. They still measure the b response to the discount factor at lambda 30,
which is worth having and is not available anywhere else, so they are left to
finish -- but the point that eventually wins will not be one of them.

**EVERY LOSS IN THIS FILE BEFORE THIS ENTRY IS ON THE OLD SCALE.** Comparisons
across the change are not meaningful; the archive re-scores consistently, so
rankings are, but levels are not.


## The two b instruments pull the ratio in OPPOSITE directions

**MEASURED, both at lambda 30 with everything else held.** Raising b:

    addiction_scalar_1  0.01724 -> 0.0155   b 0.00636 -> 0.01303   ratio 0.434 -> 0.388
    rsa_1               0.4539  -> 0.50     b 0.00636 -> 0.02440   ratio 0.434 -> 0.461

    d log ratio / d log b  =  -0.155 through addiction_scalar_1
                              +0.045 through relative_share_of_addiction_1

So they are not interchangeable ways of moving the same quantity.
`addiction_scalar_1` is the Stone Geary subsistence and works on WHO uses: it
brings marginal households in, and a diluted pool has a lower disordered share.
`relative_share_of_addiction_1` works on HOW MUCH the existing users buy, and
that raises the share slightly. Same target moment, opposite side effect.

**THIS INVALIDATES THE CANDIDATE PROJECTION, WHICH HELD THE RATIO CONSTANT.**
Redone with the measured -0.155, from the lambda 12 point (b 0.2847, ratio
0.4349), the CANDIDATE batch should give:

    a_scalar 0.0185   b +58%   ratio 0.486   lambda_d +85%
    a_scalar 0.0195   b  -7%   ratio 0.529   lambda_d +19%
    a_scalar 0.0205   b -44%   ratio 0.572   lambda_d -22%

against the constant-ratio prediction of lambda_d at -3 per cent for the middle
line. b is still bracketed, which is what the batch is for, but lambda_d now
looks likely to come in HIGH, and correcting it wants a LOWER lambda rather
than the 11.8 those points carry.

**THE GENERAL LESSON, WHICH THIS FILE KEEPS RELEARNING.** A response measured
through one instrument does not transfer to another instrument that moves the
same moment. The ratio's behaviour is a property of the (instrument, moment)
PAIR, not of the moment. The archive's pooled +0.224 on log b was an average
over both channels and is the wrong number for either one.


## lambda_d lands at +10 per cent, from -78

**CANDIDATE line 1, point_08e5be251f, measured 20:23 on 29 August.**
lambda_addiction 11.8, addiction_scalar_1 0.0185, rsa_1 0.5057, discount
0.99715.

    lambda_d  0.04064  against 0.0368    +10 per cent
    b         0.13764  against 0.089     +55
    theta     0.14247  against 0.162     -12   (was -37)
    loss      0.3096                           (best is 0.2074)

The substance use disorder rate has been -78 per cent at every point in this
archive and -81 at the point the search started from. It is now +10. theta
followed it up unprompted, -37 to -12, exactly as predicted: drug spending is
measured over the disordered and was starved by the same thing.

**THE LOSS IS WORSE AND THAT IS THE DEAL THE AUTHOR ASKED FOR** -- land b and
lambda_d, tune the rest afterwards. What this point costs is tau_u at +205,
h_1 at +72, lambda_m at -57 and mu_H at +32, every one of them measured over or
driven by a drug population 55 per cent too large. They should come back as b
does, and that is the claim the next point tests.

**HOW GOOD THE PREDICTIONS WERE, WHICH IS THE PART WORTH KEEPING.**

    b         predicted +58   came in +55    the elasticity held
    lambda_d  predicted +85   came in +10    it did not

The ratio came in at 0.2953 against a predicted 0.486. Traced back:
`d log ratio / d log b` through addiction_scalar_1 was **-0.155 at lambda 30**
and is **+0.532 here at lambda 11.8**. It changed SIGN between the two regions.
So a local elasticity in this model is good for one step and no further, and
every projection in this file more than one step out has been wrong -- the b
interpolation by a factor of four, the ratio here by a factor of five. The
BRACKET is what has actually worked, every time. Design brackets, not steps.


## A misspelled variable was creating households inside unemployment

**FOUND 29 AUGUST 20:35, while asking why pi_eu had never come within 45 per
cent of its target across 84 points.** `create_unemployment_process`, line
~23931:

    unemployment_process(...,2,2,2,0,:) = 1 - probability_becoming_employed1/(1+increased_prob_if_homeless)

`probability_becoming_employed1`, with a trailing 1, is **declared nowhere in
the file** and appears exactly once. The subroutine has no `implicit none` of
its own -- the module it `use`s has one, but that does not reach a scope that
merely uses it -- so the name was accepted as an uninitialised implicit real.

**THE ROW COULD NOT SUM TO ONE.** Its companion two lines above, the find-a-job
entry for the same state, is 0.55/1.2 = 0.4583. With the undefined value at
zero the stay-unemployed entry is 1.0 and the pair sums to 1.4583. The
normalisation lines nearby rebuild only the EMPLOYED row, as one minus the sum
of its own off-diagonals; row two is written directly and never normalised, so
nothing downstream could catch it. The identical block six lines below, for
state 3, spells the name correctly -- which is what settles this as a typo
rather than a deliberate asymmetry.

**WHY IT FITS THE SYMPTOM.** The model delivered pi_eu at 1.8 to 2.6 times the
textbook flow rate `p_eu/(p_eu+0.55)` at EVERY point, including ones where the
drug population was empty, so it was never the drug channel. And pi_eu's
elasticity on its own instrument was only +0.125, which is why pushing
`probability_becoming_unemployed` around never worked: the search was fighting
a leak.

**THE CLASS SWEEP, AND IT COMES BACK CLEAN.** `-fimplicit-none` turns exactly
this into a compile error. Validated both directions: reintroducing the typo
produces `Symbol 'probability_becoming_employed1' at (1) has no IMPLICIT type;
did you mean 'probability_becoming_employed'?`, and the corrected file compiles
with **zero** such errors. So this was the ONLY instance of its class in the
whole 35,000 lines, which is worth knowing -- the worry on finding a bug like
this is always that it is one of many.

The flag is now in both build paths, `run_one_point.sh` and
`run_moment_stability.sh`, with the reasoning beside it. A full -O3 build with
it is clean. It costs nothing at run time and makes the bug unrepeatable.

**THIS IS THE THIRD BUG OF ITS SHAPE IN THIS FILE**, after the misspelled
OpenMP sentinel that silently deleted a directive and the routine-local that
shadowed a sibling's computed quantity. All three are names a compiler could
have rejected and did not. The lesson is not "be careful with names"; it is
that this codebase needs its compilers set to refuse, and two of the three
would have been caught by flags that cost nothing.

**WHAT IS NOT YET KNOWN.** That the typo CAUSED the pi_eu miss is measured by
`PIEU_VERIFY_point.txt`, which re-runs the vector of `point_08e5be251f` -- which
read pi_eu 0.08275 -- on the corrected model. If it comes back near 0.04 the
archive is stale in full, exactly as the savings grid made the previous 566
stale, and that goes to the author before anything is retired.


## Both moments are bracketed, and so is the lambda that hits them together

**AS OF 20:55 ON 29 AUGUST.** CANDIDATE line 2 closed the b bracket at
lambda 11.8, and combined with the lambda 30 slice it brackets lambda itself.

At lambda 11.8, rsa_1 0.5057, discount 0.99715:

    addiction_scalar_1 0.0185   b +55%   lambda_d +10%   ratio 0.2953
    addiction_scalar_1 0.0195   b -29%   lambda_d -71%   ratio 0.1694

so b crosses its target at about 0.01905, with an elasticity of -14.8. But the
RATIO collapses across that same interval, and interpolating each lambda-slice
separately to the point where b = 0.089:

    lambda 11.8   ratio 0.2165   ->  lambda_d -48 per cent
    WANT          ratio 0.4135
    lambda 30.0   ratio 0.5948   ->  lambda_d +44 per cent

**SO THE PAIR IS BRACKETED IN BOTH DIRECTIONS AND THE CROSSING IS AT LAMBDA
21.4**, with addiction_scalar_1 near 0.01862 to hold b at target there. That is
the first time in this calibration that a single point can be named as the
likely answer rather than a direction to walk in.

**THE THING THAT MAKES THIS HARD, STATED PLAINLY.** The two instruments fight
on the ratio. Raising lambda raises the disordered share and empties b; raising
addiction_scalar_1 to put b back lowers the disordered share again. That is why
five cycles of a search moving both at once went nowhere: every step traded one
against the other and the mean loss could not tell the difference. Bracketing
each at a FIXED value of the other is what separated them.

**A CAUTION ON EVERYTHING ABOVE.** Every number here is an interpolation, and
interpolations in this model have been wrong all day -- by a factor of four on
a b step and five on a ratio, and the ratio's own elasticity in b changes SIGN
between lambda 30 and lambda 11.8. Lambda 21.4 is where to MEASURE next, not a
result. The bracket is real; the crossing inside it is a guess.

**AND THE ARCHIVE IS NOW MIXED.** The unemployment typo was fixed at 20:35, so
every point measured from that moment on is on a different model from the 86
before it. The drug block is probably close to separable from an unemployment
transition row, which is why the brackets above are still worth reading, but a
fit pooling pre- and post-fix points is not safe. `PIEU_VERIFY_point.txt` will
say how large the difference is; nothing more should be launched into
`code/points/` until it does.


## THE TYPO WAS INERT. I was wrong about the cause of the pi_eu miss.

**MEASURED 21:20 ON 29 AUGUST.** `PIEU_VERIFY_point.txt` re-ran the vector of
`point_08e5be251f` on the corrected model. Against the broken model:

    pi_eu     0.0827458848  ->  0.0827469417     unchanged
    b         0.1376390998  ->  0.1376436823     +0.003 per cent
    lambda_d  0.0406445471  ->  0.0406499435     +0.013 per cent

Five of twenty one moments move at all and the largest move is 0.013 per cent,
against a solver reproducibility band of 2.5e-5. **Nothing changed.** The
archive is NOT stale; all 90 points stand.

**WHY IT WAS INERT, AND THE ANSWER IS COMPLETE.** Line 23943 sets
`unemployment_process(1:cutoff_age_1,2,2,2,0,:)` -- the buggy one -- and line
**24028 sets `unemployment_process(:,2,2,2,0,:)`**, the whole array, correct
spelling, eighty five lines later. The blanket assignment overwrites the
buggy one for every age. The line was dead code.

**WHAT I GOT WRONG AND HOW.** The typo is real and the reasoning about the row
sum was right in isolation: 0.4583 plus 1.0 is not 1. What I did not do was
check whether that assignment SURVIVED, in a file with 119 write sites to the
same array. I found a cause consistent with the symptom and stopped looking. I
did flag the causation as unmeasured and made the verification the gate before
retiring anything, which is the only reason this cost forty minutes rather than
an archive.

**KEEP THE FIX AND THE FLAG ANYWAY.** The code was wrong and is now right, and
`-fimplicit-none` is a real improvement independent of this: it would have
caught the typo at compile time, the class sweep it enabled came back clean,
and it costs nothing. But neither is a fix for anything that was broken.

**pi_eu IS STILL UNEXPLAINED AND STILL BLOCKS THE TEN PER CENT CRITERION.**
The facts stand and now have nothing attached to them: never better than +45 per
cent over 90 points, an elasticity of only +0.125 on its own instrument, and
1.8 to 2.6 times the flow rate `p_eu/(p_eu+0.55)` at every point including ones
where the drug population is empty. Something inflates unemployment relative to
its own two-state flow and it is not this line. Candidates not yet checked: the
job finding rate actually in force versus the declared 0.55; whether
non-participants are being counted in the unemployed numerator; and the
addicted and SMI separation multipliers, which raise the aggregate rate above
the baseline flow by construction.


## pi_eu EXPLAINED: the SMI block carries forty per cent of the unemployment and the separation rate cannot touch it

**FOUND 22:10 ON 29 AUGUST, prompted by the author asking why setting the
separation rate near zero would not drive unemployment near zero.** It would
not, and here is why.

I had been reading `create_unemployment_process`. The LIVE builder is
`employment_transition`, and it does this:

    if (m_f_1>=1) then            ! the household has SMI
        sep_1  = sep_1 * kappa_uem
        find_1 = find_1 / kappa_uem
    end if

`kappa_uem` is **11.43** in the best point. So a household with serious mental
illness faces a job finding rate of 0.55/11.43 = **4.8 per cent** instead of 55,
and a separation rate 11.4 times higher. They are close to unemployable by
construction, which is the parameter's purpose -- it is calibrated to hit
employment-given-SMI of 30 per cent.

**THE DECOMPOSITION RECONSTRUCTS THE MOMENT EXACTLY**, from the point's own
other moments and nothing else:

    SMI share            p_m       = 0.0448
    unemployment there   1-kappa_uem_moment = 0.6727
    SMI contribution     0.0448 x 0.6727    = 0.0301
    everyone else, implied                  = 0.0474
    reassembled                             = 0.07538
    measured                                = 0.07538

**SO THE SEPARATION RATE GOVERNS 95.5 PER CENT OF THE POPULATION AND IS NEARLY
POWERLESS ON THE 4.5 PER CENT THAT CARRIES FORTY PER CENT OF THE UNEMPLOYMENT.**
With a find rate of 4.8 per cent the SMI group sits deep in the flat part of
sep/(sep+find), so its unemployment barely responds to sep. That is the whole
explanation of the elasticity: 0.125 measured against 0.96 for a two-state flow.
The instrument was never weak, it was diluted.

**AND THE TARGET IS REACHABLE.** Holding the SMI block at its calibrated value:

    need pi_eu 0.0485, SMI gives 0.0301, so everyone else must be 0.0192
    p_eu = 0.55 x 0.0192 / (1 - 0.0192) = 0.01078

The author guessed 0.01 unprompted. That point is in `PEU_ZERO.txt` and solving.

**THE DECOMPOSITION MAKES THREE FALSIFIABLE PREDICTIONS**, and they differ from
the naive two-state model by a factor of twenty at the bottom, so the sweep
tests the explanation and not merely the direction:

    p_eu 0.001  ->  0.0319   (naive: 0.0018)
    p_eu 0.005  ->  0.0387   (naive: 0.0090)
    p_eu 0.010  ->  0.0472   (naive: 0.0179)

**WHY THIS TOOK SO LONG, WHICH IS THE PART TO LEARN FROM.** The answer was
sitting in the model's own moment list the whole time: p_m at 4.5 per cent and
kappa_uem at 0.33 multiply to 3.0 points of a 7.5 point total. Every hypothesis
I chased instead -- the flow rate, a typo, a definitional mismatch, the target
itself -- was reached for before doing the one arithmetic that used the model's
own published moments. Decompose the moment before theorising about it.


## The author was right about pi_eu, and my SMI decomposition was wrong

**MEASURED 22:50.** Driving `probability_becoming_unemployed` from 0.0228 to
0.001, same vector otherwise:

    pi_eu   0.07538 -> 0.00657     a factor of eleven

The measured elasticity over that range is **0.780**, against 0.96 for a
two-state flow and the **0.125** the archive marginal reported. That marginal
is the FIFTH confounded correlation today overturned by a controlled
experiment. The instrument was never weak; the archive was never a derivative.

**MY DECOMPOSITION PREDICTED 0.0319 AND WAS WRONG, and the reason generalises.**
It held the SMI block's contribution fixed at `p_m` times
unemployment-among-SMI. But that second factor is itself an equilibrium object,
`sep*k/(sep*k + find/k)`, which goes to zero with `sep` like everything else.
The accounting identity was EXACT at the point where it was computed --
reassembling 0.07538 against a measured 0.07538 -- and useless as a prediction,
because it froze a component that was never frozen. **An identity that holds at
a point says nothing about what moves when you push on it.** That it
reconstructed the moment perfectly is what made it convincing, and the perfect
reconstruction was guaranteed by construction rather than evidence of anything.

pi_eu crosses 0.0485 at `p_eu` near **0.01296**, between the 0.005 and 0.01
points already solving.

## The interaction, which is the part that changes the plan

The same move does this to everything else:

    lambda_d   0.00807 -> 0.03143   +289 per cent, and -15 against target
    b          0.08786 -> 0.21567   +145
    tau_u      0.24400 -> 0.80300   +229
    kappa_uem  0.32726 -> 0.92165   +182
    kappa_ued  0.16562 -> 0.01534    -91
    lambda_m   0.20272 -> 0.03893    -81
    cbar       0.00331 -> 0.00088    -73

**The separation rate is not a repair to apply after the drug block is set. It
is one of the largest instruments ON the drug block**, because unemployment is
what makes drug use affordable and attractive. lambda_d reaches -15 per cent
here without touching lambda_addiction or addiction_scalar_1 at all -- the
second best it has ever been, from a point launched to diagnose unemployment.

So the two-stage plan -- fix b and lambda_d, then tune the rest -- cannot hold
with p_eu in the second stage. The system is three instruments on three
moments: `lambda_addiction`, `addiction_scalar_1` and
`probability_becoming_unemployed` against `b`, `lambda_d` and `pi_eu`, and they
have to move together.
