# Universal Housing First, refit after the inheritance defect

One run, reported as it came out. No source edits, no variants, no picking.

- **Branch run from:** `claude/two-period-addiction-hazard-d7gb61` at `04bc57b5`
  ("Counterfactual keeps the benchmark's newborn inheritance").
- **Acceptance grep:** `grep -c "inheritance_amount=1\." code/housing_first_or_treatment_first_SR_v1.f90`
  returned **0**.
- **Model log:** `code/variant_cf_20260909T030539Z.log` (the log named on the
  `run_variant: log is` line). All numbers below are read out of that file, not
  the wrapper.
- **Benchmark state:** regenerated in this container from
  `code/benchmark_of_record.txt`'s `VECTOR`; save log
  `code/variant_save_20260909T030045Z.log`.
  `verify_benchmark_state.py` ended **"VERDICT: the counterfactual imports this
  benchmark"**.
- **Arm:** universal Housing First — `probability_of_voucher_benchmark_used=1`,
  `increased_prob_of_voucher_if_homeless_and_addicted=1`,
  `voucher_conditional_on_clean=0`. Drug price **cleared**, not held.
- **Run:** 65 min, exit 0, HANDOVER 81 of 81.

## Headline

The run **converged on both conditions at loop 54 of a maximum of 80**. It is
not capped. Both market-clearing distances are inside their stopping rules and
the acceptance check on `inheritance_amount` passes.

The result that matters is in (c), and it does **not** go the way the brief's
framing anticipated. Removing the spurious transfer moved `beta` back *toward*
the benchmark (2.676 → 2.867 against 3.0019) but moved `tau_l` *further away*
(0.2208 → 0.1789 against 0.2241). The counterfactual still finances a large
labour-income tax **cut**, and it is now a bigger cut than the defective runs
showed, not a smaller one. Whatever was making universal HF cheap, the
hard-coded inheritance was not the whole of it.

## (a) Acceptance check — `inheritance_amount`

**PASSES.** First line, quoted from the log (line 370, truncated to width):

```
 inheritance_amount=   0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000
```

The log carries exactly two `inheritance_amount=` prints (lines 370 and 387).
Parsed in full, **each is 60 values, 0 of them nonzero, max |v| = 0**. The
counterfactual kept the benchmark's zero.

The other 54 matches on that string are `distance_inheritance_amount=`, one per
loop, all `0.0000000000000000` — consistent with the commit message's note that
the revision block is gated on `residual_bequests_to_government==0` and so never
fires.

## (b) Counterfactual moments, against the benchmark

Benchmark column is this container's regenerated benchmark of record; it
reproduces the brief's quoted values on every line.

| moment | benchmark | universal HF | change |
|---|---|---|---|
| `h_1` homelessness rate | 0.011649 | **0.0000278** | −99.76% |
| `b` total drug users | 0.077694 | **0.102230** | +31.58% |
| `lambda_d` disorder rate | 0.033555 | **0.044737** | +33.33% |
| `pi_eu` unemployment | 0.049501 | **0.051275** | +3.58% |
| `tau_u` treatment take-up | 0.249109 | **0.191425** | −23.16% |
| mean age of drug users | 34.655 | **33.691** | −0.96 years |

Homelessness is essentially eliminated (0.24% of its benchmark level). Drug use
still rises — `b` by 31.6% and the disorder rate by 33.3% — and treatment
take-up falls by 23.2%. So the direction of the drug-use result survives the fix
at a cleared price; the defect was not what produced it. Its magnitude is not
comparable to the pre-fix runs, which were void.

## (c) `tau_l` and `beta` — the main diagnostic

| | benchmark | universal HF | distance from benchmark | pre-fix (void) |
|---|---|---|---|---|
| `tau_l` average labour income tax | 0.224143 | **0.178896** | **−0.045247 (−4.52 pp, −20.19%)** | 0.2208 |
| `beta` wealth over output | 3.001851 | **2.866774** | **−0.135077 (−4.50%)** | 2.676 |

Both sit below the benchmark.

- `beta` **improved**: 2.676 → 2.867, so it now sits 0.135 below the benchmark
  rather than 0.326 below. That is the fix doing what it was expected to do —
  the windfall that inflated wealth is gone.
- `tau_l` **got worse**: 0.2208 → 0.1789. Before the fix the counterfactual's
  average labour income tax was 0.0033 below the benchmark; it is now 0.0452
  below — a gap nearly fourteen times larger. The counterfactual is still
  handing money back through the tax schedule, and more of it.

I am reporting this rather than explaining it away. The brief's account of the
defect predicts the `beta` move and does not predict the `tau_l` move. On the
face of the numbers the government has slack in this arm for a reason other than
the inheritance transfer: bequests still rise (see (d)) and, with
`residual_bequests_to_government=1`, that rise accrues to the government, while
`govt_spending_on_homeless` and `govt_spending_on_addicts` both print
`0.0000000000000000`. That is a candidate reading, not a finding — it needs its
own check, and I did not run one.

## (d) `model_bequests`

| benchmark | universal HF | pre-fix (void) |
|---|---|---|
| 0.492375 | **0.553323** | 0.5034 |

+0.060949 on the benchmark, +12.38%. Bequests rise **more** after the fix than
the defective run reported, not less. Value taken from the last two (identical)
`model_bequests( 1 )=` prints, i.e. the converged equilibrium.

## (e) `increase_in_labour_income_tax`

**+0.033671** (`3.3670797379683121E-002`). Benchmark is 0.

**Sign, in words: this is a TAX CUT, and a large one.** The schedule is
`T(y) = max(y − lambda*y^0.85, 0)` with
`lambda = labor_income_tax_rate + increase_in_labour_income_tax`. A *larger*
`lambda` subtracts more from `y`, so tax falls. The counterfactual raises
`lambda` by 0.0337 above its benchmark value, which is what shows up as `tau_l`
falling 4.52 pp in (c). The name of the variable is the opposite of its effect.

## (f) Government budget

| quantity | value |
|---|---|
| `net_govt_revenues` (counterfactual) | **0.552575** |
| `net_govt_revenue_constraint` (target it must hit) | **0.545998** |
| difference | +0.006576 |
| `distance_govt_budget`, final | **0.0065763** |
| `stopping_rule_govt_budget` | 0.025 |

**Converged**: 0.0065763 < 0.025.

Note on the constraint: it is 0.545998, which is this container's regenerated
benchmark `net_govt_revenues` exactly. The brief quotes the benchmark's net
revenue as 0.545217. That does not match, and it is the only one of the ten
benchmark numbers in the brief that does not — h_1, b, lambda_d, pi_eu, tau_u,
mean age, tau_l, beta and model_bequests all reproduce to the digits given.

Three things say the regenerated benchmark is sound and the quoted figure is the
odd one out:

1. `verify_benchmark_state.py` checks the written state's budget constraint
   against the save log's own net revenue **to 1e-9** and passed
   (`budget constraint = 0.545998   benchmark net revenue = 0.545998`), so the
   state and the record here come from one solve.
2. The benchmark record already committed on this branch was produced by a
   different build (`SOURCE_MD5 ba3fb9e2…` against this run's `86e25f42…`) and
   agrees with the regeneration on **every** moment to about 1e-5 relative —
   `tau_l` 0.22414449 against 0.22414299, `beta` 3.0017653 against 3.0018509,
   `h_1` 0.011650106 against 0.011649483. That is the OpenMP reduction-order
   band the code's own comments document, and it is 80× smaller than the
   0.545217/0.545998 gap.
3. `0.545217` does not appear anywhere in the repository.

So the counterfactual was held to the right constraint. Flagging the number
because the budget arithmetic above is only meaningful against the constraint
actually used, and because anyone re-deriving the benchmark will hit the same
mismatch.

## (g) Drug market

| quantity | value |
|---|---|
| cleared drug price `price_of_addictive_good` | **1.187376** |
| drug quantity `V` | **0.270732** |
| `distance_drug_market`, final | **0.0039391** |
| `stopping_rule_drug_market` | 0.005 |

**Converged**: 0.0039391 < 0.005. The price cleared at 1.1874 against the
benchmark's normalisation of 1, i.e. 18.7% higher. The price was moved, not
held: `max_drug_price_move` caps each step at 0.5%, and the final
`implied supply price` was 1.190978 against the posted 1.187376.

## (h) Loops

`loop_count` reached **54**. `max_counterfactual_loops = 80`.

**The cap was NOT hit. The run is converged, not capped.** Both stopping rules
were satisfied at exit and the run printed `simulation_ended`.

For the record, convergence was not monotone in the price: `distance_drug_market`
was 0.0133 at loop 38, rose to 0.0192 by loop 45 and 0.0658 by loop 53, then fell
to 0.0039 at loop 54. The budget condition settled earlier and stayed inside
tolerance from about loop 38.

## (i) Newborn CEV

**It printed.** `welfare_of_gains_by_addiction= 0.46023559570312500`, i.e. a
newborn consumption-equivalent gain of **+46.0%**, bracketed cleanly
(`x_1= 0.4602  distance_1= 6.1035e-05`).

This is the other half of the fix working: before the fix this arm's CEV
overflowed the bracket, i.e. exceeded +0.50, and the solve stopped. It no longer
does.

But it sits at 0.4602 against a ceiling of 0.5 — it has used 92% of the bracket.
`calculate_welfare_gains` brackets on `x` in `[-0.5, +0.5]`
(`x_0 = -0.5d0`, `x_2 = 0.5d0` in the source). Any arm with a larger gain than
this one will still hit the ceiling and `stop`. Worth knowing before the matched
Treatment First run is read.

One inaccuracy in the source, noted since it would mislead whoever hits it: the
failure message reads `"target welfare not bracketed by x in [-1,1]."` while the
code actually brackets on `[-0.5, 0.5]`. Cosmetic, and I have not changed it —
this run made no source edits.

## What did not work

- **No Fortran compiler in the container.** `gfortran` was absent and had to be
  installed (13.3.0) before anything could be built. No source or build-flag
  changes; `run_variant.sh` compiled the model with its own flags unmodified.
- **The benchmark `net_govt_revenues` in the brief (0.545217) does not
  reproduce here (0.545998).** See (f). Everything else in the brief's benchmark
  column does reproduce, and the mismatch is 80x too large to be solve noise.
- **`code/benchmark_of_record.txt` was rewritten in the working tree** by step
  2, as instructed, and I have **restored it to its committed version** so this
  branch carries only the report. The regenerated record is reproduced in the
  numbers above; the save log it came from is
  `code/variant_save_20260909T030045Z.log` (not tracked).
- **The `tau_l` result does not go the way the brief's framing anticipated.**
  See (c). This is the run's real finding and it is stated as-is; I have not
  re-run anything to try to move it.
- Nothing was run in `code/` alongside the solve. One save run, then one
  counterfactual, serialised.
