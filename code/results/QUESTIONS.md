# THE THREE QUESTIONS THE ARMS ANSWER

The author, 19 September, in these words:

> *"i want you to tell me what the optimal use rate and SUD are in the optimal
> omega_c=1, what the optimal homelessness is relative to the omega_c=1 case
> without internalizing the homelessness externality. and what the welfare
> results are for TF: what happens to use rate, what happens to welfare"*

Three questions, and each one names its own comparison. Fill this in from the
committed arm results; do not substitute a different comparison.

---

## Q1. THE OPTIMAL DRUG USE RATE AND SUD RATE

Arm 1, omega_c = 1, against the benchmark. Every household faces the whole cost
of its own drug use to its child, so what survives is the optimum.

| | benchmark | arm 1, omega_c = 1 | change |
|---|---|---|---|
| b, total drug users (`MOMENT b`) | | | |
| lambda_d, SUD (`model_fraction_addicted=`) | | | |
| lambda_d / b, SUD per user | | | |

NOT `model_fraction_addicted` for b. A parallel worker has already made that
exact substitution and reported it as b.

---

## Q2. THE OPTIMAL HOMELESSNESS RATE

**Arm 2 against ARM 1, not against the benchmark.** The author's question is
what internalising the homelessness externality does *holding omega_c at 1*, so
arm 1 is the control and the difference isolates the externality alone.

| | arm 1, omega_c = 1 | arm 2, + internalisation | change |
|---|---|---|---|
| H, homelessness (`model_fraction_homeless=`) | | | |
| b | | | |
| lambda_d | | | |
| pi_v, the clearing instrument | | | |

Arm 2 is the ONLY arm where kappa_x moves policy functions: the flat Pigouvian
charge on choosing the street. **H should fall.** If it does not, that is the
finding and it is reported as one, not explained away.

Also report H in arm 2 against the BENCHMARK, as a secondary line, so the two
channels -- omega_c and internalisation -- can be separated.

---

## Q3. TREATMENT FIRST: THE USE RATE AND WELFARE

Arm 3 against the benchmark. omega_c stays at 0.055; kappa_x is an externality
on everyone but is not internalised privately.

| | benchmark | arm 3, Treatment First | change |
|---|---|---|---|
| b, total drug users | | | |
| lambda_d, SUD | | | |
| H, homelessness | | | |
| pi_v | | | |
| welfare (`average_welfare_with_childhood=`) | | | |
| welfare, in consumption-equivalent terms | | | |
| govt_spending_on_drug_tests | 0 by construction | | |
| mass in the excluded voucher state | 0 by construction | | |

### CONVERTING WELFARE TO SOMETHING READABLE

Utils are not interpretable on their own -- lifetime utility of 789.381 is a
difference of two large numbers, value of life +1595.65 and the consumption
bundle -805.20, so a ratio to it is a ratio to a level normalisation. Convert:

    dW/dx at x = 0 = B_total * k = 312.237 utils per unit of x on c
    1 util  = 0.3203 per cent of c = 0.2334 per cent of total expenditure
    1 per cent of expenditure = 4.285 utils

So a welfare change of DW utils is DW / 4.285 per cent of expenditure. Report
both the utils and the per cent; the per cent is what goes in the paper.

Prefer the model's own CEV from `calculate_welfare_gains` where it is printed,
and say so when the two disagree -- that routine inverts the saved curve
properly and the linear conversion above is a first-order stand-in.

### THE THING TO SAY OUT LOUD ABOUT TF

The disamenity term is common to all arms at a given H, so a welfare difference
between Treatment First and the benchmark is NOT mostly kappa_x. It is the
voucher, the exclusion, the testing cost and whatever happens to drug use. Say
which of those moved rather than reporting a net number alone.

---

## BEFORE ANY OF THE ABOVE IS BELIEVED

1. `ECONOMY IS STILL` fired, rather than the run stopping at the 25-block cap.
   The cap is a weaker result and must be labelled one.
2. The government budget residual is small and pi_v cleared.
   `frozen_stop_tolerance` is appended to the loop condition with `.AND.`, so it
   CAN force an exit before `distance_govt_budget` is inside its own rule. A
   large residual has that cause, not an economic one.
3. Each arm's own benchmark reproduces the reference benchmark. Each cloud
   session solved its own, from the same `code/seeds/n72_frozen_seed.dat`, so
   they should agree with each other and with n90 to about 1e-4 relative -- the
   model reproduces to roughly five digits, not bit-for-bit. A larger spread
   between the three benchmarks means something other than noise moved, and the
   arms are not comparable until that is understood.
