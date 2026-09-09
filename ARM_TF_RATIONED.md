# Arm: RATIONED TREATMENT FIRST, drug price cleared

One equilibrium, one report. No source edits were made.

- Branch solved from: `claude/two-period-addiction-hazard-d7gb61` @ `1c28931`
- Master source md5 `b2ca2af43bbb28a6990ff2dfdf458e57`
- Save variant md5 `0c202c8f1f2ee1f6801ea598b7045fce` (matches the `SOURCE_MD5` in the committed benchmark of record)
- CF variant md5 `befa3ec146c6179d503ba9023a47d2ac`
- Benchmark log: `code/variant_save_20260909T044135Z.log` (7 min, exit 0, HANDOVER 80 of 80)
- Counterfactual log: `code/variant_cf_20260909T045054Z.log` (87 min, exit 0, HANDOVER 81 of 81)

**The run is NOT capped.** It exited at `loop_count=61` against `max_counterfactual_loops=80`,
with every one of the loop's exit conditions satisfied, not on the loop bound.

Switches changed from the benchmark, and nothing else:

    voucher_conditional_on_clean            0 -> 1
    increased_prob_of_voucher_if_homeless_and_addicted   1 -> 0

`probability_of_voucher_benchmark_used` stayed at the benchmark's rationed
`0.0433173`. That is what makes this arm rationed rather than universal.

---

## a) The three acceptance checks

**1. The frozen equilibrium converged before the state was written.** From the save log:

    FROZEN PASS  1  b= 8.4482060219518748E-002  lambda_d= 3.5819124951629713E-002  h_1= 1.2646661021303558E-002  avg_lab_inc= 0.66758257698915568  distance= 5.6154756117734461E-003
    FROZEN PASS  2  b= 8.5020704607704875E-002  lambda_d= 3.6030527843832247E-002  h_1= 1.2535530821717966E-002  avg_lab_inc= 0.66714626414085554  distance= 5.3864438818612692E-004
    FROZEN PASS  3  b= 8.5032910158520630E-002  lambda_d= 3.6040249986300309E-002  h_1= 1.2535507806259302E-002  avg_lab_inc= 0.66714718014128582  distance= 1.2205550815755362E-005
    FROZEN CONVERGED after           3 passes, distance=   1.2205550815755362E-005

No `FROZEN STALLED`, no `FROZEN NOT AT TOLERANCE`. The distance is 1.22e-5 against a
rule of 5e-4, so the benchmark is a fixed point of the equilibrium map at frozen
parameters and nothing below is provisional on that count.

**2. The verifier.** `python3 code/verify_benchmark_state.py` ends:

    VERDICT: the counterfactual imports this benchmark

with all 55 `upload_vars` names present, the state stamped at 04:49:12, the drug price
at the benchmark quantity equal to 1.000000, and the budget constraint equal to the
benchmark net revenue at 2.402312 on both sides.

**3. `inheritance_amount` prints as sixty zeros** in the counterfactual log
(line 370 and again at 387): the write statement is followed by exactly 60
fields, every one `0.0000000000000000`.

---

## b) Moments against the benchmark

The benchmark column is **my own save run**, not the committed record. My run and
the record agree to better than 0.02 per cent on every line below, so the record is
reproducible and the comparison does not turn on which one is used.

| moment | record | my benchmark | rationed TF | % change | my bench vs record |
|---|---|---|---|---|---|
| `h_1` homelessness rate | 0.012537067 | 0.012535508 | 0.016964648 | **+35.33 %** | −0.012 % |
| `b` total drug users | 0.085038271 | 0.085032910 | 0.066142544 | **−22.22 %** | −0.006 % |
| `lambda_d` disorder rate | 0.036044748 | 0.036040250 | 0.026304295 | **−27.01 %** | −0.013 % |
| `pi_eu` unemployment rate | 0.050061034 | 0.050058318 | 0.047246391 | −5.62 % | −0.005 % |
| `tau_u` treatment take up | 0.22120070 | 0.22116496 | 0.21669210 | −2.02 % | −0.016 % |
| mean age of drug users | 35.941439 | 35.940746 | 38.487227 | +7.09 % | −0.002 % |

The shape of the arm: conditioning the voucher on being clean, while leaving the
voucher rationed and removing the extra draw the homeless-and-addicted used to get,
cuts drug use by about a fifth and disorder by about a quarter, and raises
homelessness by about a third. Users left in the population are older by two and a
half years.

## c) tau_l and beta — the calibration targets

| target | my benchmark | rationed TF | % change |
|---|---|---|---|
| `tau_l` average labour income tax | 0.20786395 | 0.19183185 | **−7.71 %** |
| `beta` wealth over output | 3.4972094 | 3.8288165 | **+9.48 %** |

**Both are flagged.** These are past "a few per cent" and they should be read as
statements about the solve as much as about the policy.

`tau_l` moving −7.71 per cent is not free-floating: the government budget is closed
by the labour income tax, and the tax that clears it here is a cut (see (e)). A
−7.71 per cent move in the average labour income tax is the direct arithmetic
consequence of `increase_in_labour_income_tax` landing at +1.456e-2, so this one is
the policy paying for itself, not drift.

`beta` at +9.48 per cent is the number I would not sign off on without a second
look. Wealth over output rising by nine and a half per cent is large for a policy
that changes a voucher rule. Part of it is mechanical — the drug price falls 13.8
per cent and total drug spending falls with the user share, so saving rises — and
the `bequests` line rising 11.35 per cent in the budget block is consistent with a
genuinely wealthier stationary distribution rather than an accounting artefact. But
`beta` is a calibration target that is already missed in the benchmark (3.497
against a target of 3.000), so the arm is being read off a solve that was 16.6 per
cent high on wealth before the policy was applied at all. I am reporting the number,
not defending it.

## d) Convergence of the counterfactual loop

Final `CF MOMENTS` line:

    CF MOMENTS distance=   2.0236717958244457E-004  b=   6.6142543697167738E-002  lambda_d=   2.6304295247256030E-002  h_1=   1.6964647646289924E-002

- Final distance **2.0237e-4** against `stopping_rule_frozen_moments` = 5e-4. Inside tolerance.
- **61 loops** (61 `CF MOMENTS` lines; last `loop_count=61`), against `max_counterfactual_loops=80`.
- The loop exited on its conditions, not on the cap. **This run is converged, not capped.**

Every other exit condition at the end: `distance_govt_budget` = 2.2994e-4 against
2.5e-2, `distance_drug_market` = 1.7879e-3 against 5e-3.

## e) The labour income tax

    increase_in_labour_income_tax=   1.4559496412274105E-002

**This is a tax CUT.** `lambda = labor_income_tax_rate + increase_in_labour_income_tax`
and `T(y) = max(y - lambda*y**0.85, 0)`, so a larger `lambda` means a smaller tax
bill at every `y`. The increase is positive and therefore taxes fall — corroborated
independently by `tau_l`, the realised average labour income tax, falling from
0.20786 to 0.19183.

For scale: the null test at the benchmark's own switches put this at −3.4e-4,
essentially zero. Here it is +1.456e-2, forty-odd times that in absolute size and of
a definite sign, so the move is the policy and not the solver's noise floor.

All 28 `TAX STEP` lines, so the secant can be checked:

| # | slope | step | | # | slope | step |
|---|---|---|---|---|---|---|
| 1 | 0.0000000000000000 | 5.0000e-04 | | 15 | −37.960803863760404 | 5.0000e-04 |
| 2 | −12.139233982217945 | 5.0000e-04 | | 16 | −27.393976853351962 | 5.0000e-04 |
| 3 | −42.899629424696606 | 5.0000e-04 | | 17 | −21.824347089927070 | 5.0000e-04 |
| 4 | −19.556162364660068 | 5.0000e-04 | | 18 | −24.754819802907036 | 5.0000e-04 |
| 5 | −3.1590498519076249 | 5.0000e-04 | | 19 | −22.845435328662212 | 5.0000e-04 |
| 6 | −23.480431233935818 | 5.0000e-04 | | 20 | −25.253128882715338 | 5.0000e-04 |
| 7 | −26.909817714369819 | 5.0000e-04 | | 21 | −45.348088159338175 | 5.0000e-04 |
| 8 | −28.869582609161146 | 5.0000e-04 | | 22 | −14.124362594087879 | 5.0000e-04 |
| 9 | −28.353397385274068 | 5.0000e-04 | | 23 | −22.609696785379697 | 5.0000e-04 |
| 10 | −39.892710205884327 | 5.0000e-04 | | 24 | −20.405561279004818 | 5.0000e-04 |
| 11 | −32.994727125986472 | 5.0000e-04 | | 25 | −23.917858064159226 | 5.0000e-04 |
| 12 | −11.877128099364132 | 5.0000e-04 | | 26 | −43.018373474491298 | 1.0405e-04 |
| 13 | −23.578425281493210 | 5.0000e-04 | | 27 | −0.20564283111476411 | 5.0000e-04 |
| 14 | −26.915446930199291 | 5.0000e-04 | | 28 | −17.401039765391410 | 6.6071e-06 |

The slope is negative on every step that has one — step 1 is the seeded 0.0 before a
secant exists — and the bulk of them sit in the −20 to −30 band, which is the
expected magnitude of about −30. The two outliers worth naming are step 5 at −3.16
and step 27 at −0.206: both are near-flat secants, and in both cases the loop did not
run away on them, which is what the step column shows — the step collapses to
1.04e-4 at 26 and 6.61e-6 at 28 as the search closes. Nothing here has the wrong
sign, so the secant is not being driven backwards at any point.

## f) The drug market

- Price cleared at **0.86175640245435381** (benchmark 1.0, so **−13.82 per cent**).
- Final `distance_drug_market` = **1.7879190721729055E-003** against a rule of 5e-3. Cleared.

The price falls because the rationed clean-conditional voucher pushes users out of
the market: `b` falls 22 per cent, demand falls with it, and along an upward supply
curve with elasticity 1.46 the price has to fall to clear.

## g) The BUDGET block, benchmark vs counterfactual

Verbatim, last loop of each run.

**Benchmark** (`variant_save_20260909T044135Z.log`):

     BUDGET total_revenues=   5.8394509903473395
     BUDGET ss=   3.4304804440637757       ui=   5.5202287365050728E-002  di=   0.0000000000000000
     BUDGET food_stamps=  0.10090788354270552       vouchers=   0.0000000000000000       vouchers_2=  0.23080727295244408
     BUDGET drug_tests=   0.0000000000000000       homeless=   0.0000000000000000       addicts=   0.0000000000000000
     BUDGET bequests=  0.69017727880494895       initial_assets=   0.0000000000000000       inheritance_paid=  0.30991879412904960
     BUDGET bequest_residual=  0.38025848467589934       lump_sum=   0.0000000000000000

**Rationed Treatment First** (`variant_cf_20260909T045054Z.log`):

     BUDGET total_revenues=   5.5421628694826275
     BUDGET ss=   3.3922666175547369       ui=   5.5285759567303271E-002  di=   0.0000000000000000
     BUDGET food_stamps=   8.8252886863107310E-002  vouchers=   0.0000000000000000       vouchers_2=   6.1718354793881040E-002
     BUDGET drug_tests=   7.1051295665474929E-004  homeless=   0.0000000000000000       addicts=   0.0000000000000000
     BUDGET bequests=  0.76853201131055682       initial_assets=   0.0000000000000000       inheritance_paid=  0.30991921965142072
     BUDGET bequest_residual=  0.45861279165913610       lump_sum=   0.0000000000000000

| line | benchmark | rationed TF | change |
|---|---|---|---|
| `total_revenues` | 5.8394510 | 5.5421629 | **−5.09 %** |
| `ss` | 3.4304804 | 3.3922666 | −1.11 % |
| `ui` | 0.055202287 | 0.055285760 | +0.15 % |
| `food_stamps` | 0.10090788 | 0.088252887 | −12.54 % |
| `vouchers` | 0 | 0 | — |
| `vouchers_2` | 0.23080727 | 0.061718355 | **−73.26 %** |
| `drug_tests` | 0 | 0.00071051296 | new |
| `homeless` / `addicts` | 0 | 0 | — |
| `inheritance_paid` | 0.30991879 | 0.30991922 | +0.00 % |
| `bequests` | 0.69017728 | 0.76853201 | +11.35 % |
| `bequest_residual` | 0.38025848 | 0.45861279 | +20.6 % |
| `lump_sum` / `initial_assets` | 0 | 0 | — |

Reading it against the rule that spending lines should agree closely and a
`total_revenues` difference is the tax doing its job:

- `total_revenues` down 5.09 per cent **is** the tax doing its job. That is the tax
  cut of (e) showing up on the revenue side.
- `ss` (−1.11 %), `ui` (+0.15 %) and `inheritance_paid` (+0.00 %) agree closely, as
  they should.
- **Two spending lines do not agree closely, and both are the policy rather than a
  defect.** `vouchers_2` collapses 73 per cent because that is exactly what this arm
  does: the voucher is now conditional on being clean and the addicted no longer get
  the extra draw, so far fewer vouchers are paid out. `drug_tests` goes from exactly
  zero to 7.11e-4 because testing does not exist in the benchmark and does exist
  under Treatment First — the benchmark's zero is the switch being off, not a
  missing number.
- `food_stamps` down 12.54 per cent is the one I would not attribute to the policy
  design directly; it follows from the distribution shifting, and it is small in
  levels (0.0127 out of revenues of 5.5).
- `bequests` and `bequest_residual` rise together with `beta`, and are the same
  observation as the `beta` flag in (c).

## h) Newborn CEV

`welfare_of_gains_by_addiction` printed:

    welfare_of_gains_by_addiction=  -9.9945068359375000E-002

**Newborn CEV = −9.99 per cent.** A newborn behind the veil would need about ten per
cent more consumption in the rationed Treatment First economy to be as well off as
in the benchmark.

The bisection bracketed and converged cleanly — no `target welfare not bracketed by
x in [-1,1].` and no `NaN welfare` message appears in the log. The last few
iterations, showing the search closing:

     x_1= -0.10058593750000000   distance_1= 1.9531250000000000E-003  welfare_adjusted_1= 2184.9963732348538
     x_1= -0.10009765625000000   distance_1= 9.7656250000000000E-004  welfare_adjusted_1= 2184.8344461396996
     x_1= -9.9853515625000000E-002  distance_1= 4.8828125000000000E-004  welfare_adjusted_1= 2184.9154441404489
     x_1= -9.9975585937500000E-002  distance_1= 2.4414062500000000E-004  welfare_adjusted_1= 2184.9559172949444
     x_1= -9.9914550781250000E-002  distance_1= 1.2207031250000000E-004  welfare_adjusted_1= 2184.9356828702703
     x_1= -9.9945068359375000E-002  distance_1= 6.1035156250000000E-005  welfare_adjusted_1= 2184.9458006206551

against a stopping rule of 1e-4, so the number is pinned to about five decimal
places.

---

## Source edits I would want, written here rather than made

No edits were made and none is required for this arm to run. Two are worth recording.

1. **`beta` is not in the counterfactual loop's convergence test.** The loop
   measures `b`, `lambda_d`, `h_1` and `average_labour_income`. Wealth over output
   moved 9.48 per cent in this arm and nothing in the exit condition would have
   noticed if it were still drifting at loop 61. Adding `beta` — or the aggregate
   capital stock — to `distance_counterfactual_moments` would make the (c) flag
   answerable from the log instead of by argument. This is the one I would actually
   make.

2. **`TAX STEP` does not print the level it is stepping from.** It prints slope and
   step but not the current `increase_in_labour_income_tax`, so the secant can be
   checked for sign and magnitude, as done in (e), but the trajectory has to be
   reconstructed from the separate `increase_in_labour_income_tax=` lines. Adding
   the level to the same line would make the tax search auditable from one grep.

## Environment note

`gfortran` was not present in this container and was installed from the distribution
package (`gfortran 13.3.0`) before anything would build. No repository file was
changed to accomplish that.
