# Universal Treatment First with the drug price held at the benchmark

A diagnostic, not a result to report. The point is to separate the general
equilibrium price feedback from the two things the policy does directly — the
transfer, and the removal of the homelessness penalty on the voucher.

## What was run

`clear_drug_market` was edited in its `is_counterfactual` branch so that the
last line of the update,

```fortran
price_of_addictive_good=max(step_1,10.d0**(-6))
```

became

```fortran
distance_drug_market=0
```

The price is therefore never moved off the benchmark's 1.0, and the drug market
can never bind the convergence test. Everything above it is untouched: the gap,
the secant, the trust region and the half-per-cent cap all still compute, and
the diagnostics still print the price the market *would* have cleared at. One
line changed, nothing else in the source. **The edit is not committed.**

The arm:

```
bash code/run_variant.sh cf <benchmark vector> \
    probability_of_voucher_benchmark_used=1 \
    increased_prob_of_voucher_if_homeless_and_addicted=0 \
    voucher_conditional_on_clean=1
```

Log: `code/variant_cf_20260909T010027Z.log`, 49 minutes on 4 cores.

## Convergence

| | |
|---|---|
| loops | **41** |
| loop cap | 80 — **not hit** |
| final `distance_govt_budget` | **0.0227546** (stopping rule 2.5e-2) |
| final `distance_drug_market` | 0 by construction |

The run exited on the genuine stopping rules with 39 loops of headroom, so this
is a converged solve and not a capped one. The budget was the last condition to
clear, falling monotonically at roughly 10 per cent a loop from loop 20 onward.

## Moments

| moment | benchmark | fixed-price UTF | change |
|---|---|---|---|
| homelessness rate `h_1` | 0.01165 | **0.010609** | −0.10 pp (−8.9%) |
| total drug users `b` | 0.07770 | **0.124029** | +4.63 pp (**+59.6%**) |
| disorder rate `lambda_d` | 0.03356 | **0.053988** | +2.04 pp (**+60.9%**) |
| unemployment `pi_eu` | 0.04950 | **0.049720** | +0.02 pp (+0.4%) |
| treatment take-up `tau_u` | 0.24911 | **0.195909** | −5.32 pp (−21.4%) |
| mean age of drug users | 34.65 | **35.03** | +0.38 years |

## The price that was held

| | |
|---|---|
| drug quantity `V` | **0.334950** (benchmark 0.209757, **+59.7%**) |
| implied supply price | **1.3779** |
| price actually faced | **1.0000** (held) |

Had the market been allowed to clear, the price would have had to rise **37.8
per cent** to absorb the extra quantity.

## Welfare

Newborn CEV, `welfare_of_gains_by_addiction` = **−0.15848**, i.e. a newborn
behind the veil would give up 15.8 per cent of consumption to avoid this
policy. Note this is the fixed-price world, in which users buy 60 per cent more
of the good at an unchanged price — the transfer is being spent, and the
resource cost of supplying that quantity is not being charged back to anyone.

## Reading it

**Holding the price fixed makes the drug response larger, not smaller.** Use
rises 59.6 per cent above the benchmark and the disorder rate 60.9 per cent,
both on an unchanged price. That is the response to the transfer and to the
removal of the homelessness penalty alone, with the general equilibrium channel
switched off.

The sign of the price gap settles the direction of the channel. The market
would have cleared at 1.378, not 1.0, so the price feedback here is
contractionary: letting it clear taxes exactly the households whose demand
went up, and chokes off part of the quantity response. **The cleared-price
universal Treatment First arm must therefore show a smaller rise in use than
the 59.6 per cent here** — this run is the upper bound on the response, and the
difference between the two is what the 37.8 per cent price rise is doing.

So the answer to the question that prompted this: the price rise in the
cleared version is *not* masking part of the response. It is working the other
way — it is damping a response that is larger still underneath it. The channel
raising use above the benchmark in the cleared-price arm is the transfer and
the unconditional voucher, not the price.

Two things worth flagging alongside it, both consistent with that reading:

- **Treatment take-up falls 21 per cent** while use rises 60 per cent. The
  conditionality is binding on a much larger base of users, and the arm is
  losing people from treatment at the same time as it gains them into use.
  Homelessness falls only 8.9 per cent for that price.
- **Unemployment is flat** (+0.02 pp), so the extra use is not coming through
  the employment margin in this arm.

## Caveat on the benchmark state

`code/drug_supply_shifterbaseline_benchmark.dat` is not tracked in the repo, so
`verify_benchmark_state.py` failed its consistency check on a fresh clone. The
save run was re-run at the benchmark vector to regenerate the state, per the
documented fallback. It reproduced the benchmark of record exactly —
`h_1` 0.011650, `b` 0.077697, `lambda_d` 0.033556, `pi_eu` 0.049502, `tau_u`
0.249111, mean user age 34.654 — and `verify_benchmark_state.py` then returned
`VERDICT: the counterfactual imports this benchmark`, with the shifter
normalising the price to 1.000000 at the benchmark quantity. The counterfactual
below is imported from that state.

No record of the cleared-price universal Treatment First arm's moments exists
in the repo, so the comparison against that arm is stated by direction only,
from the sign of the price gap. Its numbers would need to be dropped in for a
side-by-side.
