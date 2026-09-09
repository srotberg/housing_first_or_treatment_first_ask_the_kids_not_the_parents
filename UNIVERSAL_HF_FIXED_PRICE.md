# Universal Housing First with the drug price held at 1.0

The missing cell of the 2x2. Universal Treatment First moves two things at once
against the benchmark -- it makes the voucher universal, which is a large
transfer and removes the homelessness risk that is the main cost of using, and
it adds a `v=0` sobriety condition. This run makes the voucher universal and
adds no condition, at the SAME held price, so the difference between the two
arms is the condition and nothing else.

    bash code/run_variant.sh cf <benchmark_of_record VECTOR> \
        probability_of_voucher_benchmark_used=1 \
        increased_prob_of_voucher_if_homeless_and_addicted=1 \
        voucher_conditional_on_clean=0

Log: `code/variant_cf_20260909T021551Z.log`, 17 minutes on 4 cores, exit 0,
HANDOVER 81 of 81.

## The one source change, which is not committed

In `clear_drug_market`, in its `is_counterfactual` branch, the single line

    price_of_addictive_good=max(step_1,10.d0**(-6))

was replaced by

    distance_drug_market=0

so the price is never moved off 1.0 and the drug market cannot bind the
convergence test. Everything above it still computes, so the diagnostics still
print `implied supply price=`, which is what the market WOULD have cleared at.
Exactly one line changed; `price_of_addictive_good=max(step_1` no longer appears
in the source. The rent and housing-price pegs, the budget rule, the stopping
rules and the voucher condition are untouched.

## The benchmark this imports

The `.dat` state files are not tracked, so the fresh clone had none of them.
The benchmark was regenerated from the record's own vector
(`bash code/run_variant.sh save <VECTOR>`, log
`code/variant_save_20260909T021147Z.log`), and
`python3 code/benchmark_of_record.py` re-derived the record. The regenerated
solve reproduces the record's moments to about seven significant figures --
`b` 0.077700109 against 0.077699947, `h_1` 0.011650266 against 0.011650106,
`lambda_d` 0.033557770 against 0.033557680, `tau_u` 0.249111240 against
0.249110389 -- i.e. it is the same benchmark up to compiler and core-count
rounding (gfortran 13.3.0, 4 cores). `python3 code/verify_benchmark_state.py`
then ends with

    VERDICT: the counterfactual imports this benchmark

with the consistency checks passing: the supply shifter puts the drug price at
1.000000 at the benchmark quantity V = 0.209759, and the budget constraint
equals the benchmark net revenue at 0.545234.

## Moments

From the block between `===== COUNTERFACTUAL MOMENTS =====` and its END line.

| | universal HF, price held at 1.0 |
|---|---|
| homelessness rate `h_1` | 0.000084858 |
| total drug users `b` | 0.142970 |
| disorder rate `lambda_d` | 0.063002 |
| unemployment `pi_eu` | 0.055477 |
| treatment take-up `tau_u` | 0.175772 |
| mean age of drug users | 34.865 |

Unemployment is up 12.1 per cent on the benchmark's 0.049502; the mean age of
users is essentially unchanged (34.865 against 34.655).

## The price that was held, and the price that was not reached

    drug quantity V         = 0.450672      (benchmark V = 0.209759, a factor of 2.15)
    implied supply price    = 1.688469
    price faced by households = 1.000000    (held)

The market would have cleared at 1.688, so the held price understates the
equilibrium price by 68.8 per cent. This is a diagnostic decomposition, not an
equilibrium: at a cleared price the quantity response would be much smaller.
For scale, universal HF WITH the price cleared is a different object entirely --
0.111547 users at p_v = 1.2421172746621805 -- and is not comparable with
anything in the table below, which is why this run exists.

## Newborn CEV: not produced, and it is above +0.50

`welfare_of_gains_by_addiction=` never printed. `calculate_welfare_gains`
brackets the consumption-equivalent on `x` in `[-0.5, +0.5]` and stops the
program when the target falls outside it, which is what happened:

    target welfare not bracketed by x in [-1,1].
    w0=   2084.8331436665399       w2=   2253.8826147019454       target=   2254.2366791084842

(the message says `[-1,1]`; the code actually sets `x_0 = -0.5d0`,
`x_2 = 0.5d0`.) The counterfactual's newborn welfare, 2254.2367, exceeds the
benchmark newborn's welfare with consumption raised by half, 2253.8826. So the
newborn CEV is **greater than +0.50** and the model cannot report a number for
it without widening the bracket, which would be a second source change and was
not made. What can be said is the sign and a lower bound: universal HF at a held
price is a large newborn welfare GAIN, against universal TF's -0.15848.

Homelessness essentially disappears (0.0000849), and with it the excess death
risk, which is what puts the gain outside the bracket in a model where the value
of life dominates the welfare level.

## Convergence

    final distance_govt_budget = 0.024327436
    stopping_rule_govt_budget  = 0.025
    loops                      = 16
    max_counterfactual_loops   = 80        -- NOT hit

The run converged on its own terms and is a result, not a capped diagnostic.
Two caveats on the budget, both worth stating: it cleared only just inside a
loose tolerance (0.0243 against 0.0250), and at that point net government
revenue is 0.520906 against the benchmark constraint of 0.545234, a 4.5 per cent
shortfall. The labour income tax adjustment that clears it is
`increase_in_labour_income_tax = -0.0092749`, i.e. the tax FALLS. The drug market
by construction reports `distance_drug_market = 0.0` at every loop.

## THE DECOMPOSITION

All three rows at a held drug price of 1.0.

| | users `b` | homelessness `h_1` | disorder `lambda_d` | newborn CEV | take-up `tau_u` |
|---|---|---|---|---|---|
| benchmark | 0.077698 | 0.011650 | 0.033556 | 0 | 0.249110 |
| universal HF (this run) | 0.142970 | 0.000085 | 0.063002 | > +0.50 | 0.175772 |
| universal TF | 0.124029 | 0.010609 | 0.053988 | -0.15848 | 0.196797 (derived) |

### (i) The TRANSFER channel = universal HF minus benchmark

| | level | per cent |
|---|---|---|
| users | +0.065272 | +84.0 |
| homelessness | -0.011565 | -99.3 |
| disorder | +0.029446 | +87.8 |
| treatment take-up | -0.073339 | -29.4 |

The transfer on its own raises drug use by 84 per cent. It is a large income
transfer AND it removes the homelessness risk that is the main cost of using,
and both push the same way. It also all but eliminates homelessness, cutting it
by 99.3 per cent to 0.000085.

### (ii) The CONDITION channel = universal TF minus universal HF

| | level | per cent |
|---|---|---|
| users | -0.018941 | -13.2 |
| homelessness | +0.010524 | a factor of 125 (0.000085 to 0.010609) |
| disorder | -0.009014 | -14.3 |
| treatment take-up | +0.021025 | +12.0 |

### Does the `v=0` condition reduce use once the transfer is held constant?

**Yes.** Holding the transfer constant and the price at 1.0, adding the sobriety
condition takes drug users from 0.142970 to 0.124029: a fall of 0.018941, which
is 13.2 per cent. The disorder rate falls alongside it, from 0.063002 to
0.053988, by 0.009014 or 14.3 per cent.

The two channels have opposite signs and the transfer is by far the larger, so
the NET that universal TF reports -- +0.046331 users, +59.6 per cent on the
benchmark -- is a transfer effect of +0.065272 partly undone by a condition
effect of -0.018941. The condition claws back 29 per cent of what the transfer
adds and no more. **The condition works in the direction it is meant to and is
nowhere near strong enough to offset the transfer that carries it.**

The cost side of the condition is the homelessness column. The transfer alone
takes homelessness to 0.000085; attaching the condition puts it back to 0.010609,
125 times higher and only 8.9 per cent below the benchmark. Nearly all of the
homelessness reduction that universal housing buys is given back by conditioning
it on sobriety, in exchange for a 13 per cent reduction in use.

## Treatment take-up, for all three

The 21 per cent fall under universal TF is the TRANSFER, not the condition, and
the condition works against it.

| | `tau_u` | vs benchmark |
|---|---|---|
| benchmark | 0.249110 | -- |
| universal HF (this run) | 0.175772 | -29.4 per cent |
| universal TF | 0.196797 (derived) | -21.0 per cent |

The transfer alone cuts take-up by 29.4 per cent -- more than universal TF's
total 21 per cent fall. Adding the condition RAISES take-up by 0.021025, or 12.0
per cent relative to universal HF. So the condition does not depress treatment;
it is the universal voucher that does, and the sobriety requirement partly
offsets that.

One honesty note on this row: universal TF's take-up level is not a number this
run produced. It is derived from the stated "-21 per cent" against the
benchmark's 0.249110, giving 0.196797. The level and per cent figures for the
condition channel in this table therefore carry that derivation; the universal HF
and benchmark figures are measured. If universal TF's held-price log is to hand,
substituting its `MOMENT tau_u` line would firm this row up. The SIGN of the
condition channel does not depend on the derivation: any universal TF take-up
above 0.175772 -- and 21 per cent below the benchmark is well above it -- makes
the condition channel positive.
