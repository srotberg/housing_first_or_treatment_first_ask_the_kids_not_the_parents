# Universal Housing First, drug price cleared — CAPPED, not converged

## THIS RUN IS CAPPED. DO NOT USE THE NUMBERS BELOW AS A RESULT.

The counterfactual loop exited on `loop_count=80`, which is
`max_counterfactual_loops=80`, not on its convergence test. At exit three of the
loop's own conditions were still open:

| condition | at exit | rule | over |
|---|---|---|---|
| `distance_govt_budget` | 0.20583040832192223 | 2.5e-2 | 8.2x |
| `distance_drug_market` | 2.1589305697487182e-2 | 5e-3 | 4.3x |
| `CF MOMENTS distance` | 2.8452326395964900e-3 | 5e-4 | 5.7x |

Everything in sections (b) through (h) is therefore a reading off the 80th
iterate of a map that had not reached its fixed point. It is reported because
the instruction was to report the one equilibrium obtained and to say plainly
when it is not one. **The policy question — what universal Housing First does —
is not answered by this run.** The direction of every moment is probably right;
none of the magnitudes should be quoted.

### Why it capped, and what would fix it

The binding constraint is not the drug price the source comment warned about.
It is the tax.

- The net revenue constraint is 2.4017979310470001. Early in the run, with the
  tax still at its warm start, universal vouchers left revenue at
  1.6315512735023030 — a gap of about 0.77 to close.
- The secant slope is about −26, so closing 0.77 needs the tax level to move
  about 0.029.
- `max_tax_move=0.0005d0` caps the tax at 5e-4 per loop, so that is ≈ 58 loops
  of pure tax movement.
- `tax_hold_max_loops=35` holds the tax still for the first 35 loops while the
  drug price walks up under its own 0.5 %-per-loop cap. That left 46 loops
  (35–80) for a job needing about 58.

All 46 `TAX STEP` lines took the capped step of exactly −5.0e-4. Not one was
secant-limited: the secant was never the constraint, the clip was. The tax
travelled 46 × 5e-4 = 0.0230, from its warm start of −2.5993578601628542e-3 to
−2.5599357860162871e-2, and ran out of loops.

Measured at the exit rather than the start: 0.20583 of revenue still to find at
a slope of −26.39 is a further 0.0078 of tax, or **about 16 more capped steps**.
So this arm needed roughly 62 tax loops and got 46.

**No source edit was made.** If one is wanted, the smallest that would let this
arm converge is to raise `max_counterfactual_loops` from 80 to about 110 — 16
more loops for the tax, plus margin for the price and the moments to re-settle
once it stops moving. The alternative is to raise `max_tax_move` from 5e-4 to
about 2e-3, which the observed slope stability (45 slopes between −17.6 and
−38.1) would tolerate and which costs a quarter of the wall clock. Raising the
loop cap is the safer of the two, since the 5e-4 clip is what has kept this
loop monotone throughout. Either is a change to the solve, not to the model,
and neither touches an equilibrium condition. At ~1 minute per loop, 110 loops
is under two hours.

There is also a second-order interaction worth noting: the drug price had
converged (`distance_drug_market` ran 1.58e-4, 3.20e-4 around loops 73–76) and
was then knocked back out to 1.85e-2, 8.37e-3, 6.70e-3, 2.16e-2 over the last
four loops by the tax that was still moving underneath it. The price is not
failing on its own account; it cannot settle while the tax has not.

---

## (a) The three acceptance checks

All three pass.

**1. FROZEN CONVERGED, from the save run** (`code/variant_save_20260909T044102Z.log`):

```
 FROZEN CONVERGED after           3 passes, distance=   1.4634806206351159E-005
```

against `stopping_rule_frozen_moments = 5e-4`. Neither `FROZEN STALLED` nor
`FROZEN NOT AT TOLERANCE` appears in the log.

**2. The verifier's VERDICT line** (`python3 code/verify_benchmark_state.py`):

```
VERDICT: the counterfactual imports this benchmark
```

with all 55 names present, the drug price at the benchmark quantity equal to
1.000000, and the budget constraint 2.401798 matching the benchmark's net
revenue 2.401798.

**3. inheritance_amount prints as sixty zeros.** Sixty fields, sixty of them
exactly zero, in both logs — the save run and the counterfactual. The source
check `grep -c "inheritance_amount=1\."` returns 0, and the other two greps
return 1 each, as required.

---

## (b) Moments against the benchmark

Benchmark column is **my own save run**, not the committed record.

| moment | benchmark (this run) | universal HF | change |
|---|---|---|---|
| `h_1` homelessness rate | 0.012535920169055517 | 1.9138609384771564e-4 | **−98.47 %** |
| `b` total drug users | 0.085030906793874483 | 0.11350820430795371 | **+33.49 %** |
| `lambda_d` disorder rate | 0.036036893941095043 | 0.049923595376959444 | **+38.53 %** |
| `pi_eu` unemployment rate | 0.050064374161387738 | 0.052482642598229580 | +4.83 % |
| `tau_u` treatment take-up | 0.22127813927764578 | 0.19027119410100787 | −14.01 % |
| mean age of drug users | 35.940562360175150 | 33.970276120718670 | −5.48 % |

**Does my benchmark differ from the record?** Only at the level of OpenMP
reduction order. Against the vector's previously committed
`benchmark_of_record.txt`, my run gives `h_1` −0.0091 %, `b` −0.0087 %,
`lambda_d` −0.0218 %, `pi_eu` +0.0067 %, `tau_u` +0.0350 %, mean age −0.0024 %.
Every one is under four hundredths of a per cent, which is the same 1e-5-relative
band `benchmark_of_record.py` documents for two solves of one vector. The record
was regenerated from this run, so the committed file now describes it.

---

## (c) tau_l and beta — calibration targets, and both moved a lot

| target | benchmark (this run) | universal HF | change |
|---|---|---|---|
| `tau_l` average labour income tax | 0.20786449312969688 | 0.24006259657645018 | **+15.49 %** |
| `beta` wealth over output | 3.4969651449709094 | 2.6996776636097010 | **−22.80 %** |

**Both are flagged.** Both are far beyond a few per cent.

`tau_l` is the easier of the two to read: it is not free to stay put here. The
programme has to be paid for, the loop pays for it by moving
`increase_in_labour_income_tax` down by 0.0256, and `tau_l` is the average tax
that results. A +15.5 % move in the average labour income tax rate is the
financing, not a solver artefact — though its *level* is unreliable because the
budget never closed, and the true financed value is larger still, since the loop
stopped 0.206 of revenue short.

`beta` at −22.8 % is the one to be suspicious of. Wealth over output falling by
almost a quarter is a very large statement for a voucher programme to make, and
it is a statement about the solve as much as about the policy: it is measured on
an iterate whose budget is 8x its tolerance and whose distribution is still
moving at 5.7x the moment tolerance. I would not carry this number anywhere
until the arm converges.

---

## (d) The counterfactual loop

- Final `CF MOMENTS distance=` **2.8452326395964900e-3**, against
  `stopping_rule_frozen_moments = 5e-4` — 5.7x its tolerance, still open.
- **80 loops.** The loop hit `max_counterfactual_loops=80`.

Final line, verbatim:

```
 CF MOMENTS distance=   2.8452326395964900E-003  b=  0.11350820430795371       lambda_d=   4.9923595376959444E-002  h_1=   1.9138609384771564E-004
```

The moments were much better behaved than the budget for most of the run —
they touched 1.36e-4 on the second-to-last loop — but they cannot settle while
the tax steps a fixed 5e-4 every loop, because each step perturbs them afresh.
The moment distance at exit is a measure of the tax still moving, not of the
distribution failing to converge.

---

## (e) The labour income tax

**Final value: `increase_in_labour_income_tax = -2.5599357860162871e-2`.**

**This is a tax RISE.** Raising `increase_in_labour_income_tax` cuts taxes, so
a fall in it means households pay *more*. It ran from its warm start of
−2.5993578601628542e-3 down to −2.5599357860162871e-2 — a fall of 0.0230, every
bit of it the capped step — and that is a rise in taxes. It is the financing of
the universal voucher, and it is consistent with `tau_l` rising 15.5 %. And it
is an understatement: the run stopped 0.206 of revenue short of the constraint,
so the tax rise that actually balances this programme is larger, by roughly a
further 0.0078.

**Every TAX STEP line.** 46 of them. The slope is negative and around −30 in
every case where a secant existed, as expected.

| # | slope | step | | # | slope | step |
|---|---|---|---|---|---|---|
| 1 | 0.0000000000000000 | −5.0e-4 | | 24 | −38.133521947529360 | −5.0e-4 |
| 2 | −29.083018093279733 | −5.0e-4 | | 25 | −19.990136593523093 | −5.0e-4 |
| 3 | −29.464195753390321 | −5.0e-4 | | 26 | −27.529626869371413 | −5.0e-4 |
| 4 | −25.004458015442065 | −5.0e-4 | | 27 | −29.173506169386496 | −5.0e-4 |
| 5 | −24.719475577442008 | −5.0e-4 | | 28 | −26.221205485366617 | −5.0e-4 |
| 6 | −25.392697816306132 | −5.0e-4 | | 29 | −22.810391784555662 | −5.0e-4 |
| 7 | −20.886059456450816 | −5.0e-4 | | 30 | −31.522913822705306 | −5.0e-4 |
| 8 | −20.299560703414414 | −5.0e-4 | | 31 | −30.850175813241759 | −5.0e-4 |
| 9 | −21.995176213963834 | −5.0e-4 | | 32 | −17.619805892115522 | −5.0e-4 |
| 10 | −24.567660358756328 | −5.0e-4 | | 33 | −29.028990355542714 | −5.0e-4 |
| 11 | −25.702174042490956 | −5.0e-4 | | 34 | −29.151676748685215 | −5.0e-4 |
| 12 | −24.910611412461293 | −5.0e-4 | | 35 | −31.316904459178978 | −5.0e-4 |
| 13 | −25.480558603292437 | −5.0e-4 | | 36 | −30.468747864731831 | −5.0e-4 |
| 14 | −28.010657382309986 | −5.0e-4 | | 37 | −22.365928356120591 | −5.0e-4 |
| 15 | −26.069634620990964 | −5.0e-4 | | 38 | −23.814050106483165 | −5.0e-4 |
| 16 | −24.234912707015145 | −5.0e-4 | | 39 | −25.819912335984775 | −5.0e-4 |
| 17 | −25.147517388127017 | −5.0e-4 | | 40 | −28.067944800980602 | −5.0e-4 |
| 18 | −28.775567684283107 | −5.0e-4 | | 41 | −29.668058117482385 | −5.0e-4 |
| 19 | −31.347537340128600 | −5.0e-4 | | 42 | −26.745934396153334 | −5.0e-4 |
| 20 | −28.945604183294702 | −5.0e-4 | | 43 | −25.292468074335140 | −5.0e-4 |
| 21 | −22.711901471666330 | −5.0e-4 | | 44 | −22.549351710060762 | −5.0e-4 |
| 22 | −25.461977405979198 | −5.0e-4 | | 45 | −26.693285966517852 | −5.0e-4 |
| 23 | −27.598319500788257 | −5.0e-4 | | 46 | −26.735898890892759 | −5.0e-4 |

Line 1 has slope exactly 0 because no secant existed yet — that is the
`have_tax_secant==0` path, which falls back to `tax_fallback_gain`, and its step
was clipped to the cap as well. Of the 45 real slopes: **all negative**, mean
−26.39, min −38.13, max −17.62. The secant checks out.

The thing the table shows most clearly is that **the step column never varies**.
Every one of the 46 steps is exactly the `max_tax_move` clip. The secant was
never allowed to take the step it computed.

---

## (f) The drug price

- **Cleared at `price_of_addictive_good = 1.1996515095693006`** — about +20 %
  on the benchmark's normalised 1.0.
- **Final `distance_drug_market = 2.1589305697487182e-2`**, against
  `stopping_rule_drug_market = 5e-3`. **4.3x its tolerance — not cleared at
  exit.**

The price is not the thing that failed here. It walked up from 1.0 under its
0.5 %-per-loop cap and had genuinely settled by the mid-70s loops:

```
 distance_drug_market=   4.2328622738452282E-004
 distance_drug_market=   3.6031677836478870E-004
 distance_drug_market=   1.5843276409133189E-004
 distance_drug_market=   3.1997348701495731E-004
 distance_drug_market=   1.8526048375030690E-002
 distance_drug_market=   8.3667818537451755E-003
 distance_drug_market=   6.7034879319725071E-003
 distance_drug_market=   2.1589305697487182E-002
```

The last four lines are the price being pushed back off its own supply curve by
the tax that was still stepping −5e-4 underneath it. So 1.1996 is close to the
right price for this arm, but it is not a cleared price at the moment the run
stopped, and the comparability with the parallel universal Treatment First arm
that this matched pair exists for is exactly what the cap costs.

---

## (g) The BUDGET block, side by side

**Benchmark** — last block of `variant_save_20260909T044102Z.log`, from the
frozen-converged pass:

```
 BUDGET total_revenues=   5.8391232336033418     
 BUDGET ss=   3.4304367251601415       ui=   5.5199703851630963E-002  di=   0.0000000000000000     
 BUDGET food_stamps=  0.10091040078950354       vouchers=   0.0000000000000000       vouchers_2=  0.23096616815188958     
 BUDGET drug_tests=   0.0000000000000000       homeless=   0.0000000000000000       addicts=   0.0000000000000000     
 BUDGET bequests=  0.69010516253997545       initial_assets=   0.0000000000000000       inheritance_paid=  0.30991746714346330     
 BUDGET bequest_residual=  0.38018769539651215       lump_sum=   0.0000000000000000     
```

**Universal Housing First** — last block of `variant_cf_20260909T044729Z.log`,
loop 80:

```
 BUDGET total_revenues=   6.3733692485142450     
 BUDGET ss=   3.3950841622929619       ui=   5.4775357044376104E-002  di=   0.0000000000000000     
 BUDGET food_stamps=  0.13773178423730384       vouchers=   0.0000000000000000       vouchers_2=  0.82840855449848205     
 BUDGET drug_tests=   0.0000000000000000       homeless=   0.0000000000000000       addicts=   0.0000000000000000     
 BUDGET bequests=  0.54851838620496596       initial_assets=   0.0000000000000000       inheritance_paid=  0.30992025392100880     
 BUDGET bequest_residual=  0.23859813228395715       lump_sum=   0.0000000000000000     
```

**`vouchers_2` is clearly larger, as a universal programme must be:**
0.23096616815188958 → 0.82840855449848205. That is **+0.597442 in level,
+258.67 per cent, a factor of 3.59**. This is the single line that says the
policy switch actually bit, and it is the one number here least contaminated by
the cap, since it is a direct cost of a rule that was fully on from loop 1.

Other movements: `total_revenues` +9.15 % (the tax rise, still incomplete);
`food_stamps` +36.49 %, which is the same population being made eligible on
income once vouchers change their housing costs; `ss` and `ui` essentially flat;
`drug_tests` zero in both, as it must be with `voucher_conditional_on_clean=0`;
`bequests` down 20.5 %, consistent with `beta` falling.

---

## (h) Newborn CEV

`welfare_of_gains_by_addiction` **did** print, once, after the loop:

```
 welfare_of_gains_by_addiction=  0.39932250976562500
```

It did **not** overflow the bracket this time. `calculate_welfare_gains` searches
`x` on `[-0.5, +0.5]` and stops with `"target welfare not bracketed by x in
[-1,1]."` when the target lies outside; that message does not appear in the log,
and neither does `NaN welfare`. So the fixes have moved this arm back inside the
bracket, which was the point of asking.

Two cautions on the number itself:

1. **0.3993 sits at 80 % of the way to the +0.5 edge.** It is inside, but not
   comfortably. A converged run of this arm could still push it out, and if the
   arm is re-run with the loop cap raised, this is worth watching.
2. **It is a CEV computed against a non-equilibrium.** The newborn cohort is
   being valued in an economy whose budget is 8x out of tolerance. A +39.9 %
   consumption-equivalent gain is not a credible welfare number; it is a
   welfare number measured on the 80th iterate. Do not quote it.

---

## What was run

- Branch `claude/two-period-addiction-hazard-d7gb61` at commit
  `1c289316fc6426ba4970a3fea3045f206a1d95c7`.
- Source greps: `FROZEN CONVERGED` 1, `CF MOMENTS distance` 1,
  `inheritance_amount=1\.` 0. As required.
- Benchmark: `bash code/run_variant.sh save $V` at the record's vector — 4 min,
  exit 0, `HANDOVER 80 of 80`, log `code/variant_save_20260909T044102Z.log`.
  Then `benchmark_of_record.py` and `verify_benchmark_state.py`.
- Counterfactual: `bash code/run_variant.sh cf $V
  probability_of_voucher_benchmark_used=1
  increased_prob_of_voucher_if_homeless_and_addicted=1
  voucher_conditional_on_clean=0` — 72 min, exit 0, `HANDOVER 81 of 81`, log
  `code/variant_cf_20260909T044729Z.log`.
- **No source edits.** `make_variant.py` reports the master unchanged at
  `b2ca2af43bbb28a6990ff2dfdf458e57` for both variants, and the save variant's
  md5 `0c202c8f1f2ee1f6801ea598b7045fce` matches the record's `SOURCE_MD5`.
- Nothing else ran in `code/`. One environment change outside the repo: the
  container had no Fortran compiler, so gfortran 13.3.0 was installed from apt.
- One equilibrium was run and it is the one reported. No variants were tried and
  none were selected between.
