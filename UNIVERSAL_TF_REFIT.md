# Universal Treatment First, refitted on the fixed inheritance

One counterfactual, run on `claude/two-period-addiction-hazard-d7gb61` at commit
`04bc57b5` ("Counterfactual keeps the benchmark's newborn inheritance"), with no
edits of any kind to the Fortran source.

**Acceptance check: PASSED.** `inheritance_amount` printed as sixty zeros. The
counterfactual now keeps the benchmark's own value instead of overwriting it with
a hard-coded transfer. Everything below is therefore a valid equilibrium of the
fixed model.

**Convergence: the run converged.** It exited on the stopping rules at loop 56 of
a cap of 80. It was NOT capped.

---

## a) The acceptance check — `inheritance_amount`

First line, quoted verbatim from the model log:

```
 inheritance_amount=   0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000
```

All sixty ages are exactly zero, on both of the two occasions the array is
printed, and `distance_inheritance_amount` is 0 at every loop. Counting the
fields: 60 zero, 0 non-zero.

## b) The counterfactual moments, against the benchmark

Read out of the block between `===== COUNTERFACTUAL MOMENTS =====` and its END
line in the model log.

| moment | benchmark | universal TF | change |
|---|---|---|---|
| `h_1` homelessness rate | 0.011650 | 0.007456 | −0.004194 (−36.0%) |
| `b` total drug users | 0.077700 | 0.071982 | −0.005718 (−7.4%) |
| `lambda_d` disorder rate | 0.033558 | 0.031186 | −0.002372 (−7.1%) |
| `pi_eu` unemployment rate | 0.049502 | 0.045075 | −0.004427 (−8.9%) |
| `tau_u` treatment take-up | 0.249110 | 0.205982 | −0.043128 (−17.3%) |
| mean age of drug users | 34.655 | 35.309 | +0.654 years |

Universal Treatment First cuts homelessness by about a third and drug use by
about seven per cent, and it *lowers* treatment take-up by seventeen per cent —
conditioning the voucher on being clean does not raise the fraction of users who
enter treatment in this equilibrium.

## c) The two aggregates that were wrong before — `tau_l` and `beta`

**This is the most important diagnostic in the report, and it does not clear the
model.**

| | benchmark | universal TF (this run) | distance | rationed TF *before* the fix |
|---|---|---|---|---|
| `tau_l` average labour income tax | 0.2241 | **0.094612** | **−0.1295** (12.95 points lower) | 0.1475 (−7.7 points) |
| `beta` wealth over output | 3.0018 | **5.412639** | **+2.4108** (80.3% higher) | 4.265 (+1.26) |

The inheritance fix did **not** remove the divergence — it made it larger on both
counts. The counterfactual still ends up with households far richer than the
benchmark (wealth over output 5.41 against 3.00) and with the labour income tax
cut by nearly thirteen points rather than the 7.7 points seen before. Whatever
was making counterfactual households rich, the hard-coded inheritance transfer
was not the whole of it, and on these two numbers it was not even the larger
part. I did not investigate further, because the instruction was to run one
counterfactual and report it; but this is the number to look at next.

## d) `model_bequests`

Two different quantities print under this name, and they must not be confused.

- **The imported value**, printed once in the start-up parameter dump as
  `model_bequests=`, is **0.49231525712099999** — the benchmark's 0.4923 exactly,
  to all sixteen printed digits. This confirms the counterfactual reads the
  benchmark's bequests rather than manufacturing its own.
- **The converged equilibrium value**, printed each loop as
  `model_bequests(1)=`, ends at **1.1805991824410531**.

Since `solve_transition_dynamics = 0`, `transition_length = 1`, so both prints
name `model_bequests(1)`; the bare one is simply the value at upload time, before
the loop runs. Against the benchmark's 0.4923 and the pre-fix rationed TF's
0.8492, the equilibrium figure of **1.1806** is higher than either. This is the
same finding as (c) in a different unit: the counterfactual economy accumulates
substantially more wealth than the benchmark, and the fix did not close that gap.

## e) `increase_in_labour_income_tax`

Final value: **+0.13101613906473555**. The benchmark is 0.

**The sign means taxes were CUT, not raised.** The schedule is
`T(y) = max(y − lambda*y^0.85, 0)` with
`lambda = labor_income_tax_rate + increase_in_labour_income_tax`, so a larger
`increase_in_labour_income_tax` raises `lambda`, raises the deduction
`lambda*y^0.85`, and therefore *lowers* the tax bill at every income. The budget
rule handed the counterfactual's surplus back to households as a **tax cut of
about thirteen points** of the average labour income tax rate (0.2241 → 0.0946),
which is what the misleadingly-named variable is recording.

## f) The government budget

| | value |
|---|---|
| `net_govt_revenues` (final) | 0.56854211833117096 |
| `net_govt_revenue_constraint` it targets | 0.54520978854600000 |
| gap | +0.02333 (revenues exceed the constraint) |
| final `distance_govt_budget` | 0.023332329785170969 |
| `stopping_rule_govt_budget` | 0.025 |

**Inside tolerance** (0.02333 < 0.025). The benchmark's net revenue is 0.545217;
the constraint the counterfactual targets, 0.5452098, is that same number as
written to and re-read from the benchmark state, and the verifier confirmed the
two agree to six decimals before the run began.

Note that the budget is the *binding* condition: it is the one still sitting
just under its stopping rule at exit, while the drug market cleared two orders of
magnitude tighter than its own. The tolerance of 2.5e-2 on a revenue level of
0.545 is about 4.3 per cent, which is loose; the equilibrium should be read with
that in mind.

## g) The drug market

| | value |
|---|---|
| price it cleared at, `price_of_addictive_good` | 0.95381567789487309 |
| implied supply price | 0.95383689629408197 |
| drug quantity `V` | 0.19576918202986943 |
| final `distance_drug_market` | 4.2436798417755384e-05 |
| `stopping_rule_drug_market` | 5e-3 |

**Cleared, and comfortably** — the distance is 118 times inside its stopping
rule. The price was not held: it was allowed to move and settled at 0.9538,
about 4.6 per cent below the benchmark's normalisation of 1. Quantity fell from
the benchmark's 0.209755 to 0.195769, a drop of 6.7 per cent, consistent with the
7.4 per cent fall in the number of users.

## h) Loop count

**56 loops**, against `max_counterfactual_loops = 80`.

**The cap was NOT hit.** The run exited because every stopping rule was
satisfied, not because it ran out of loops. This is a converged equilibrium, not
a capped one. Wall clock was 84 minutes on 4 cores.

## i) Newborn welfare

`welfare_of_gains_by_addiction` **did** print, and the bracket on
x ∈ [−0.5, +0.5] held — `calculate_welfare_gains` did not stop.

**Newborn CEV = −0.20669555664062500**, i.e. a **20.7 per cent
consumption-equivalent LOSS** for a newborn under universal Treatment First,
relative to the benchmark. The bisection converged to a final bracket width of
6.1e-05 against its stopping rule of 1e-04.

This number should be read alongside (c) and (d) rather than on its own. The
counterfactual it is measured against is one where wealth over output is 5.41
instead of 3.00 and the labour income tax is thirteen points lower, so the
welfare comparison is not a clean read of the policy alone.

---

## What was run, and what was checked first

1. Checked out `claude/two-period-addiction-hazard-d7gb61` at `04bc57b5`.
   `grep -c "inheritance_amount=1\." code/housing_first_or_treatment_first_SR_v1.f90`
   returned **0**, confirming the four hard-coded assignments are gone.
2. Regenerated the benchmark state with `bash code/run_variant.sh save $V` at the
   vector from `code/benchmark_of_record.txt` (3 minutes, exit 0, HANDOVER 80 of
   80), then `benchmark_of_record.py` and `verify_benchmark_state.py`.
   The verifier ended with **"VERDICT: the counterfactual imports this
   benchmark"**: all 55 files present, fresh, the supply shifter putting the drug
   price at 1.000000 at the benchmark quantity V = 0.209755, and the budget
   constraint equal to the benchmark's net revenue at 0.545210.
   The regenerated benchmark reproduces the record exactly — `tau_l` 0.224145,
   `beta` 3.001764, `h_1` 0.011650, `b` 0.077700, `lambda_d` 0.033557,
   `pi_eu` 0.049502, `tau_u` 0.249102, mean age 34.655.
3. Ran the counterfactual with the drug price cleared, not held, and no source
   edits:
   ```
   bash code/run_variant.sh cf $V \
       probability_of_voucher_benchmark_used=1 \
       increased_prob_of_voucher_if_homeless_and_addicted=0 \
       voucher_conditional_on_clean=1
   ```
   84 minutes, exit 0, HANDOVER 81 of 81. Model log:
   `code/variant_cf_20260909T030500Z.log`. Every number above is read from that
   log, not from the wrapper log.

Only this one solve was run in `code/`, sequentially under the flock, as required.

## What did not work, stated plainly

Nothing failed mechanically: the state verified, the run converged inside its
cap, both markets cleared, and the acceptance check passed. But **the run does
not vindicate the fix as a fix for the richness problem.** The inheritance
transfer was real and removing it was correct, yet with it gone the
counterfactual is *further* from the benchmark on both diagnostics the commit
was meant to repair — `tau_l` 12.95 points below the benchmark rather than 7.7,
`beta` 5.41 rather than 4.27, equilibrium bequests 1.18 rather than 0.85. Those
earlier figures were for rationed TF and this run is universal TF, so they are
not a like-for-like pair and the comparison cannot settle how much of the
movement is the fix and how much is the arm; a rationed-TF run on the fixed
source would settle it. I did not run one, because the instruction was to report
the one equilibrium I got rather than to run variants.

I made no edits to the Fortran source, and I do not think one is warranted on the
evidence of a single arm. The next diagnostic is a rationed-TF re-run on this
same commit, compared against its own pre-fix numbers.
