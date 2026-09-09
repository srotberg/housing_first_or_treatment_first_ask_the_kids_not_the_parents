# The null test: rationed Housing First at the benchmark's own settings

**Verdict: the null FAILS.** The counterfactual path does not reproduce the
benchmark. Run through `long_run_counter_factual` with no policy change at all
-- the benchmark's own `voucher_conditional_on_clean=0`,
`increased_prob_of_voucher_if_homeless_and_addicted=1`,
`probability_of_voucher_benchmark_used=0.0433173`, at the benchmark's own vector
-- the economy arrives at a different equilibrium. The worst relative
discrepancy across the moments in (B) is **`tau_l`, the average labour income
tax: 0.224134 in the benchmark against 0.131999 in the null, -41.11 per cent.**
`beta` is next at +31.43 per cent (3.0024 -> 3.9462). The counterfactual reaches
the benchmark's net revenue only because the tax instrument is driven to do it:
at the benchmark's own tax of zero the null's net revenue is about 1.99 against
the benchmark's 0.5422, a gap of roughly 1.45, and closing that gap costs
`increase_in_labour_income_tax = +0.0783`, a large tax CUT. So the level problem
the universal Treatment First number raises is real and it is in the path, not
only in the policy: a counterfactual run on this code measures the policy plus a
path offset of the order of 1.45 in net revenue before the tax rule reacts, and
the tax rule then converts that offset into a nine-point cut in the average
labour income tax and a 31 per cent rise in the wealth-output ratio.

Both runs are on `claude/two-period-addiction-hazard-d7gb61` at commit `ca042a0`
(`grep -c "TAX STEP"` = 1, `grep -c "BUDGET bequest_residual"` = 1). No source
was edited. Everything below is read from the model logs:

- benchmark: `code/variant_save_20260909T034400Z.log` (2 min, exit 0, HANDOVER 80 of 80)
- null: `code/variant_cf_20260909T034803Z.log` (55 min, exit 2, HANDOVER 81 of 81)

The null's exit 2 is a crash **after** the equilibrium, the counterfactual
moments block and `save_vars_and_functions`, in `write_outputs`:

```
 simulation_ended
At line 34032 of file variant_cf.f90 (unit = 2)
Fortran runtime error: Cannot open file '': No such file or directory
```

It destroys no number reported here; every quantity below was printed before it.
It is still a defect worth fixing, since it means a converged counterfactual
does not finish writing its outputs.

It also leaves a mess behind. `write_outputs` opens
`"name"//trim(file_number)`, and on this path `file_number` is empty, so the run
wrote 88 extensionless files into `code/` -- `code/housing_price`,
`code/model_ss_benefits`, `code/value_function1` and so on, the same stems as
the `.dat` files but with no suffix and 264 MB in total -- before reaching the
one name that came out entirely empty and killed it. They are byproducts of the
defect, not results; this branch deletes them rather than adding them to
`.gitignore`, because ignoring them would hide the symptom. The 89
`*baseline_benchmark.dat` state files are untouched and
`verify_benchmark_state.py` still passes.

Two facts about the benchmark run itself, before the comparison:

- `code/benchmark_of_record.txt` was rewritten by this run, as instructed. The
  source has moved since the previous record: `SOURCE_MD5` is now
  `3d7ab77aafe8f2feb88a2a5a987464f2` against the old record's
  `ba3fb9e2203e4a1667b488596081b393`. The benchmark's numbers moved with it, by
  a few tenths of a per cent -- the differences are given in (B). The benchmark
  net revenue on this code is **0.542233**, not the 0.545217 quoted in the
  brief, so the universal Treatment First gap of 3.2543 against the benchmark is
  2.712 on these numbers rather than 2.709. Nothing in the argument changes.
- `python3 code/verify_benchmark_state.py` passes: 55 of 55 files present, the
  record matches the state written at 03:46:41, freshness clean, drug price 1.0
  at the benchmark quantity, and `budget constraint = 0.542233` equal to
  `benchmark net revenue = 0.542233`. **VERDICT: the counterfactual imports this
  benchmark.** The null then read exactly that state -- the null log prints
  `net_govt_revenue_constraint= 0.54223314748399998`. So the failure below is
  not a stale-state failure. The counterfactual imported the right benchmark and
  still landed somewhere else.

---

## B. The moments, side by side

Benchmark values are from **this** save run, not from the previous record. The
last column is the difference between this run and the record values quoted in
the brief, so the drift in the benchmark itself can be separated from the null's
failure. All the benchmark drift is under 0.4 per cent; none of it is of the
size of anything in the null column.

| moment | benchmark (this run) | null | diff % | this run vs the brief's record |
|---|---:|---:|---:|---:|
| `h_1` homelessness | 0.011692512 | 0.012034358 | **+2.92** | +0.37 % vs 0.011650 |
| `b` total drug users | 0.077557926 | 0.075254833 | **-2.97** | -0.18 % vs 0.077700 |
| `lambda_d` disorder rate | 0.033497987 | 0.031224570 | **-6.79** | -0.18 % vs 0.033558 |
| `pi_eu` unemployment | 0.049495459 | 0.049044065 | -0.91 | -0.01 % vs 0.049502 |
| `tau_u` treatment take-up | 0.249021886 | 0.225431529 | **-9.47** | -0.04 % vs 0.249110 |
| `tau_l` avg labour income tax | 0.224134101 | 0.131999082 | **-41.11** | +0.02 % vs 0.2241 |
| `beta` wealth over output | 3.00244232 | 3.94621649 | **+31.43** | +0.02 % vs 3.0018 |
| `sigma_y` bottom half labour income share | 0.172451239 | 0.173998466 | +0.90 | -- |
| mean age of drug users | 34.6468620 | 36.5142998 | **+5.39** | -- |

The benchmark line is the block between `===== ALL TARGETED MOMENTS =====` and
`END OF MOMENTS` in the save log; the null line is the block between
`===== COUNTERFACTUAL MOMENTS =====` and `===== END OF COUNTERFACTUAL MOMENTS
=====` in the cf log, which is the same `print_all_moments` routine, so the two
columns are measured the same way.

Two calibration targets are broken by the null: `tau_l` misses 0.224 by nine
points and `beta` misses 3.0 by nearly one. That is the same pair, and the same
direction, that the source comment at 42690 records for the inheritance
overwrite that has since been removed (`beta 3.0018 -> 4.265` and `tau_l 0.2241
-> 0.1475`). The overwrite is genuinely gone -- see (F) -- and the null still
moves those two targets by two thirds of the amount it moved them before. What
remains is a second cause with the same signature.

---

## C. The budget, line by line

Quoted verbatim. Benchmark, from `variant_save_20260909T034400Z.log` lines 889-895:

```
 net_govt_revenues=  0.54223314748399565     
 BUDGET total_revenues=   6.0367715338820283     
 BUDGET ss=   5.3561333299291434       ui=   5.4560677881384516E-002  di=   0.0000000000000000     
 BUDGET food_stamps=   9.8409551080262031E-002  vouchers=   0.0000000000000000       vouchers_2=  0.17731437478351822     
 BUDGET drug_tests=   0.0000000000000000       homeless=   0.0000000000000000       addicts=   0.0000000000000000     
 BUDGET bequests=  0.49215546089627060       initial_assets=   0.0000000000000000       inheritance_paid=  0.30027591361999506     
 BUDGET bequest_residual=  0.19187954727627554       lump_sum=   0.0000000000000000     
```

Null, from `variant_cf_20260909T034803Z.log` lines 14515-14521, the final block:

```
 net_govt_revenues=  0.54536939639699888     
 BUDGET total_revenues=   3.8807732340191228     
 BUDGET ss=   3.3963735017851269       ui=   5.4348733160363545E-002  di=   0.0000000000000000     
 BUDGET food_stamps=   9.9000358834797020E-002  vouchers=   0.0000000000000000       vouchers_2=  0.25130135858990038     
 BUDGET drug_tests=   0.0000000000000000       homeless=   0.0000000000000000       addicts=   0.0000000000000000     
 BUDGET bequests=  0.76802082340739997       initial_assets=   0.0000000000000000       inheritance_paid=  0.30240070865933605     
 BUDGET bequest_residual=  0.46562011474806392       lump_sum=   0.0000000000000000     
```

| line | benchmark | null | difference | % |
|---|---:|---:|---:|---:|
| `total_revenues` | 6.03677153 | 3.88077323 | **-2.15599830** | -35.71 |
| `ss` | 5.35613333 | 3.39637350 | **-1.95975983** | -36.59 |
| `ui` | 0.05456068 | 0.05434873 | -0.00021194 | -0.39 |
| `di` | 0.00000000 | 0.00000000 | 0 | -- |
| `food_stamps` | 0.09840955 | 0.09900036 | +0.00059081 | +0.60 |
| `vouchers` | 0.00000000 | 0.00000000 | 0 | -- |
| `vouchers_2` | 0.17731437 | 0.25130136 | **+0.07398698** | +41.73 |
| `drug_tests` | 0.00000000 | 0.00000000 | 0 | -- |
| `homeless` | 0.00000000 | 0.00000000 | 0 | -- |
| `addicts` | 0.00000000 | 0.00000000 | 0 | -- |
| `bequests` | 0.49215546 | 0.76802082 | **+0.27586536** | +56.05 |
| `initial_assets` | 0.00000000 | 0.00000000 | 0 | -- |
| `inheritance_paid` | 0.30027591 | 0.30240071 | +0.00212480 | +0.71 |
| `bequest_residual` | 0.19187955 | 0.46562011 | **+0.27374057** | +142.66 |
| `lump_sum` | 0.00000000 | 0.00000000 | 0 | -- |
| `net_govt_revenues` | 0.54223315 | 0.54536940 | +0.00313625 | +0.58 |

**Read the last row last.** `net_govt_revenues` agrees to 0.58 per cent, and
that agreement is manufactured: it is the equation the tax rule is solving, and
it cost a tax move of +0.0783 to get there. Every line above it is the actual
comparison, and four of them are large.

Which line: **`ss` is the one that cannot be a behavioural response.** The
counterfactual does not recompute social security benefits -- at 32310-32315 it
reads them straight out of the benchmark's own
`model_ss_benefitsbaseline_benchmark.dat`, and the null log prints back exactly
that file's contents, `0.115480741795 ... 0.488756942027`. The total population
mass is the same in the two runs, 50.630194 in the benchmark against 50.339442
in the null, a difference of 0.6 per cent. Same benefits, same population, and
outlays 36.6 per cent apart is arithmetically impossible unless the two paths
disagree about the level of the benefit actually used.

The obvious suspect is the rescale at 32284-32289, which multiplies
`model_ss_benefits` by `model_average_labour_income` when `loop_count>=1`. The
benchmark's pre-loop print of the vector is `0.17740000000000000 ...
0.75082199999999988`, which is exactly the saved `.dat` divided by
`average_labor_income_calibrated = 0.650962467838` -- a factor of 1.5362. The
observed ratio of the two `ss` lines is 5.3561333 / 3.3963735 = **1.5771**. That
is 2.7 per cent off the rescale factor, which a shift in the composition of
retirees across the seven productivity nodes could cover. **I did not verify
this**: verifying it needs an instrumented build and the brief forbids source
changes. It is a hypothesis that fits the arithmetic, and it is where I would
look first.

`total_revenues` falling 35.7 per cent is the tax cut and is expected once the
tax has moved: `tau_l` falls 41.1 per cent, so labour income tax revenue falls
with it. It is a consequence of the `ss` hole, not an independent one.
`bequest_residual` more than doubling (+0.2737) and `bequests` rising 56 per
cent are the wealth response to a nine-point tax cut, consistent with `beta`
going to 3.946; with `include_bequests_in_govt_constraint` and
`residual_bequests_to_government` both at 1 the whole +0.2737 goes back into
revenue, which is what lets the tax cut go as far as it does before the budget
closes.

---

## D. The tax path in the null

Every `TAX HELD` and `TAX STEP` line, in order, with the loop it was printed on.
`tax_hold_max_loops` is 35, which is why the first 35 loops hold and every loop
from 36 steps.

```
loop  1  TAX HELD: drift=   1.7976931348623157E+308  gap=   1.9110377957024500       drug=   2.1102136840543961E-002
loop  2  TAX HELD: drift=   6.9350765745588294E-002  gap=   1.9803885614480383       drug=   7.3079836251077612E-003
loop  3  TAX STEP: slope=   0.0000000000000000       step=   2.0000000000000000E-002
loop  4  TAX HELD: drift=  0.53274635905436485       gap=   1.4467900017251552       drug=   5.7423958145498943E-002
loop  5  TAX HELD: drift=   2.5615848730260460E-003  gap=   1.4493515865981812       drug=   4.8638238058182681E-002
loop  6  TAX HELD: drift=   2.0276368830434155E-003  gap=   1.4513792234812248       drug=   4.3070919869198421E-002
loop  7  TAX HELD: drift=   6.2311731295445760E-003  gap=   1.4576103966107694       drug=   2.7386724871287682E-002
loop  8  TAX HELD: drift=   4.0104749835929709E-003  gap=   1.4535999216271764       drug=   2.9017385573119614E-002
loop  9  TAX HELD: drift=   1.6166222105642225E-002  gap=   1.4374336995215340       drug=   3.3175297570085194E-002
loop 10  TAX HELD: drift=   1.4970128295507923E-002  gap=   1.4524038278170419       drug=   2.7322718570163107E-002
loop 11  TAX HELD: drift=   6.2383097206843985E-003  gap=   1.4461655180963575       drug=   2.6038564508834905E-002
loop 12  TAX HELD: drift=   1.0304192906009924E-003  gap=   1.4451350988057565       drug=   2.5280748557751642E-002
loop 13  TAX HELD: drift=   5.6850513928217161E-003  gap=   1.4508201501985782       drug=   3.6750017732388396E-002
loop 14  TAX HELD: drift=   5.6895262873608576E-003  gap=   1.4451306239112176       drug=   2.4400318022543388E-002
loop 15  TAX HELD: drift=   5.5273346161370807E-003  gap=   1.4506579585273545       drug=   3.0264409711864615E-002
loop 16  TAX HELD: drift=   4.5208008729520355E-003  gap=   1.4461371576544026       drug=   2.8895982805990927E-002
loop 17  TAX HELD: drift=   3.4437139007408302E-003  gap=   1.4426934437536616       drug=   2.9438920244462707E-002
loop 18  TAX HELD: drift=   1.1763617110759128E-002  gap=   1.4544570608644207       drug=   3.3133853451524198E-002
loop 19  TAX HELD: drift=   1.0372902373669834E-002  gap=   1.4440841584907509       drug=   2.4879064573144816E-002
loop 20  TAX HELD: drift=   5.4308908494133945E-003  gap=   1.4495150493401643       drug=   2.9747063072555258E-002
loop 21  TAX HELD: drift=   2.1308620170272796E-003  gap=   1.4473841873231370       drug=   3.3730173650728834E-002
loop 22  TAX HELD: drift=   2.9638058307823734E-003  gap=   1.4503479931539194       drug=   2.8148432450748051E-002
loop 23  TAX HELD: drift=   4.0458705632970826E-003  gap=   1.4463021225906223       drug=   2.5269709683177766E-002
loop 24  TAX HELD: drift=   1.0457822012022167E-003  gap=   1.4452563403894203       drug=   2.3782197275112660E-002
loop 25  TAX HELD: drift=   5.1613119555005138E-003  gap=   1.4504176523449206       drug=   3.7525504265099596E-002
loop 26  TAX HELD: drift=   5.7887627849579903E-003  gap=   1.4446288895599628       drug=   2.2332412202311969E-002
loop 27  TAX HELD: drift=   5.7894735497703298E-003  gap=   1.4504183631097329       drug=   3.1371808265253986E-002
loop 28  TAX HELD: drift=   3.6504500924932071E-003  gap=   1.4467679130172399       drug=   2.8261876426815546E-002
loop 29  TAX HELD: drift=   3.2811090173296975E-003  gap=   1.4434868039999103       drug=   2.8983615832094967E-002
loop 30  TAX HELD: drift=   1.0939954388295092E-002  gap=   1.4544267583882053       drug=   3.3536419184819533E-002
loop 31  TAX HELD: drift=   1.0234451327145733E-002  gap=   1.4441923070610594       drug=   2.4401752395679099E-002
loop 32  TAX HELD: drift=   5.2493585187052272E-003  gap=   1.4494416655797648       drug=   3.0320021879898573E-002
loop 33  TAX HELD: drift=   2.4583065260124215E-003  gap=   1.4469833590537524       drug=   2.9212653047165249E-002
loop 34  TAX HELD: drift=   3.4624748213682999E-003  gap=   1.4435208842323841       drug=   2.9794827864086160E-002
loop 35  TAX HELD: drift=   1.0905542006654390E-002  gap=   1.4544264262390385       drug=   3.2818611729022895E-002
loop 36  TAX STEP: slope=  -26.764022075116987       step=   2.0000000000000000E-002
loop 37  TAX STEP: slope=  -25.047502680748025       step=   1.8830337652528974E-002
loop 38  TAX STEP: slope=  -23.078738843223999       step=   1.1021516905789237E-002
loop 39  TAX STEP: slope=  -23.642988094278707       step=   5.2477255978773058E-003
loop 40  TAX STEP: slope=  -22.688776112016271       step=   2.8445641104769058E-003
loop 41  TAX STEP: slope=  -21.342858117937450       step=   1.6016652475197189E-003
loop 42  TAX STEP: slope=  -21.885611744436194       step=   7.6111202414037220E-004
loop 43  TAX STEP: slope=  -23.070320665234323       step=   3.4147132756102370E-004
loop 44  TAX STEP: slope=  -24.271972537736254       step=   1.5383017084904334E-004
loop 45  TAX STEP: slope=  -28.156209069663920       step=   5.5693735354060254E-005
```

34 `TAX HELD` and 11 `TAX STEP`, 45 in total, one per loop.

**Final `increase_in_labour_income_tax = 7.8258558911933798E-002`.** The
benchmark's is 0 -- it is declared `is_counterfactual*0` at 4450 and the
benchmark path never touches it. The null's warm start, from the
`increased_prob_of_voucher_if_homeless_and_addicted/=0` branch at 42732, is
`-2.5993578601628542E-003`, so the loop moved it by +0.0808 from where it began
and by +0.0783 from the benchmark.

**In words: that is a tax CUT, and a large one.** `lambda =
labor_income_tax_rate + increase_in_labour_income_tax` and
`T(y)=max(y-lambda*y**0.85,0)`, so raising the increase raises lambda and lowers
the tax bill at every income. It takes lambda from 0.782021 to 0.860280, and the
realised average labour income tax from 0.224134 to 0.131999. The counterfactual
path, at the benchmark's own policy, hands every household a nine-point cut in
its average labour income tax rate for no policy reason whatsoever.

The gap sequence is the clearest single number in this report. Loops 1 and 2 open
at 1.91 and 1.98 -- that is the raw level offset, the null's net revenue against
the benchmark's own 0.542233, before the tax has moved at all. After the single
early step at loop 3 the gap parks at 1.44-1.46 and sits there, essentially
constant, for thirty-two consecutive loops. It is not transient and it is not
noise: it is a fixed level difference between the two code paths, and it only
disappears when the tax instrument is finally allowed to spend 0.08 of lambda
buying it off.

The two steps at loops 3 and 36 are both the clipped maximum, `max_tax_move =
0.02`. Loop 3's `slope= 0.0` is the fallback branch (no usable secant yet), where
`tax_step = tax_fallback_gain * gap = 0.3 * 1.98 = 0.594`, clipped to 0.02. From
loop 37 the secant is well-behaved at about -22 to -28 and the steps shrink
monotonically.

Two things follow for universal Treatment First. First, the instrument does not
saturate: the secant measured here is about -23, so the 2.71 gap that Treatment
First shows would need a lambda move of roughly 0.12, not the 3.96 the brief
estimates from a much flatter assumed slope. Second, and this is the point of
the test, a level offset of about 1.45 is present in the counterfactual path
with no policy change at all. I have not re-run Treatment First on this code, so
I cannot say the two offsets add; what I can say is that a 2.71 gap measured on
a path that is already 1.45 out at the null cannot be read as a fact about the
policy until the null is fixed.

---

## E. Convergence

**The null converged. It did not cap.**

| | |
|---|---|
| loops used | 45 |
| `max_counterfactual_loops` | 80 -- **not hit** |
| final `distance_govt_budget` | 3.1362489129989068E-003 against 2.5E-002 -- **passes**, 8.0x inside |
| final `distance_drug_market` | 3.2995509986966098E-004 against 5E-003 -- **passes**, 15.2x inside |
| final `distance_housing_market` | 0.0000000000000000 |
| final `distance_inheritance_amount` | 0.0000000000000000 |

So this is a result and not a capped run. The null test failed at a genuine
converged equilibrium of the counterfactual path, which is the worse of the two
outcomes: a capped run could be dismissed as unfinished arithmetic, and this
cannot.

Note that `distance_drug_market` sat between 0.022 and 0.058 for the whole hold
phase -- above `drug_settled_mult_for_tax * 5e-3 = 0.01` on all but loop 2 --
so the hold was doing its job and the tax was never fed an unsettled gap. The
1.45 offset was measured against a drug market that had genuinely stopped
moving.

---

## F. `inheritance_amount`

Sixty zeros, as required. First occurrence, cf log line 370, quoted:

```
 inheritance_amount=   0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000        0.0000000000000000     
```

All sixty ages are zero, matching the benchmark's own
`inheritance_amountbaseline_benchmark.dat`, and `distance_inheritance_amount` is
0 on every loop as the comment at 42675 predicts. The hard-coded 0.0133
overwrite is genuinely gone and is not a cause of anything reported here.

---

## What did not work, and what this means

- **The null fails.** Any counterfactual this project has produced on this path
  is the policy difference plus a path offset. The offset is large: about 1.45
  in net revenue at fixed taxes, or equivalently about 0.078 of lambda, 9.2
  points of average labour income tax, and 0.94 of the wealth-output ratio once
  the tax rule has absorbed it.
- **Two calibration targets do not survive the path.** `tau_l` and `beta` are
  targeted in the benchmark and are missed badly in an economy that is supposed
  to be the benchmark. A counterfactual that breaks the calibration with no
  policy change is not comparable to the benchmark on any margin, welfare
  included.
- **`ss` is where I would look.** It is the largest line that cannot be
  explained by the tax instrument, and the counterfactual reads its benefits
  frozen from the benchmark's own file, so the two paths should agree on it
  exactly and do not. My arithmetic points at the `model_average_labour_income`
  rescale at 32284-32289 being applied a different number of times on the two
  paths, but I could not test that without editing the source and the brief
  forbids it.
- **What I would want to run next**, and did not, because the brief asks for one
  equilibrium and no variant-picking: the same null with a print of
  `model_ss_benefits` and the retiree mass immediately before `govt_revenues_calc`
  on both paths. That is a two-line diagnostic print and it would settle the `ss`
  line in one pair of runs. **This needs a source edit**, which I have not made.
- **The `write_outputs` crash at 34032** should be fixed independently. A
  counterfactual that converges and then dies before finishing its outputs is
  one restart away from being read as a failed solve.
