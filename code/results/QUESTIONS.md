# THE THREE QUESTIONS THE ARMS ANSWER

The author, 19 September, in these words:

> *"i want you to tell me what the optimal use rate and SUD are in the optimal
> omega_c=1, what the optimal homelessness is relative to the omega_c=1 case
> without internalizing the homelessness externality. and what the welfare
> results are for TF: what happens to use rate, what happens to welfare"*

Three questions, and each one names its own comparison. Fill this in from the
committed arm results; do not substitute a different comparison.

---

## A WELFARE LEVEL FROM ARM 1 OR ARM 2 IS NOT COMPARABLE TO THE BENCHMARK'S

**Do not compute a CEV for arm 1 or arm 2 against the benchmark. The number is
meaningless and it is large enough to look like a headline result.**

`weight_on_child` (omega_c) is not a policy instrument, it is a term in the
OBJECTIVE. In `calculate_flow_utility` at line 27698 the flow is

    flow = [ A_parent + omega_c * A_child ] / (1 - sigma),     sigma = 2

so the bracket is divided by -1. A_child is positive, so raising omega_c from
the benchmark's 0.055 to 1 adds 0.945 times more of a NEGATIVE quantity and
drives the measured welfare level down mechanically, whether or not anybody is
worse off. omega_c also scales `child_continuation_value` at 10166 and 10175,
the same way.

MEASURED, on arm 2 before it converged: `average_welfare_with_childhood` 781.20
against the benchmark curve's W(x=0) = 791.39. Inverting the saved curve turns
that into a CEV of **-24 per cent of consumption and housing** -- for the arm
that is supposed to be the social OPTIMUM. It is an artefact of comparing two
different objective functions, not a policy evaluation.

**THE AUTHOR'S THREE QUESTIONS AVOID THIS, and that is why they are phrased as
they are.** Q1 and Q2 ask for RATES -- use, SUD, homelessness -- and never for
welfare. Q2 compares arm 2 to ARM 1, and both carry omega_c = 1, so their
objectives match and the comparison is clean. Q3 is the only welfare question,
and arm 3 keeps omega_c at the benchmark's 0.055, so it alone is comparable to
the benchmark. Answer the questions as asked and the trap never comes up.

If a welfare statement about arm 1 or arm 2 is ever wanted, it has to be
computed by evaluating BOTH allocations under ONE objective. That is a separate
exercise and it is not what any of these three arms produce.

---

## Q1. THE OPTIMAL DRUG USE RATE AND SUD RATE

Arm 1, omega_c = 1, against the benchmark. Every household faces the whole cost
of its own drug use to its child, so what survives is the optimum.

| | benchmark | arm 1, omega_c = 1 | change |
|---|---|---|---|
| b, total drug users | | | |
| lambda_d, SUD | | | |
| lambda_d / b, SUD per user | | | |

**READ ALL THREE OFF THE `CF MOMENTS distance=` LINE, not from separate prints.**
`MOMENT b` does NOT exist in an arm's log -- it is a calibration-loop print and
an arm freezes the calibration, so an instruction to read b from it cannot be
followed. The arm loop prints, at line 51518 and from one iterate:

    CF MOMENTS distance=<d>  b=<model_total_drug_users>  lambda_d=<model_fraction_addicted>  h_1=<model_fraction_homeless>

Taking them from this one line also guarantees they belong to the SAME loop,
which reading three separate prints does not -- they are written at different
points and a tail of each can straddle iterates.

Still true, and the reason the warning was there: b is
`model_total_drug_users`, NOT `model_fraction_addicted`. A parallel worker has
already made that exact substitution and reported it as b.

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

Utils are not interpretable on their own, so convert. THESE NUMBERS ARE
MEASURED BY n90's PROBE, not fitted -- an earlier version of this section
carried a figure that was wrong by a factor of 8.9, so use these:

    35.2283 utils per unit of x on c          (probe: 0.0704567 utils at x = 0.0020)
    1 per cent of c                = 0.35228 utils
    1 per cent of TOTAL expenditure = 0.48096 utils
    1 util                          = 2.0792 per cent of expenditure

So a welfare change of DW utils is DW * 2.0792 per cent of expenditure. Report
both the utils and the per cent; the per cent is what goes in the paper.

DO NOT RE-DERIVE THIS FROM A DECOMPOSITION OF THE CURVE. That is exactly how
the 8.9 error happened: the childhood half was reconstructed as
B_child = W_child(0) - value_of_life*D_child, and THE CHILD'S FLOW DOES NOT
CARRY value_of_life -- child_flow_out is set inside calculate_flow_utility at
lines 27652 and 27675, and value_of_life is added at 27816, after them. The
probe measures the walk directly and needs no decomposition.

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

These three checks replace an earlier set that was written for the BENCHMARK's
stopping rule and does not apply to an arm. The two mistakes in it were worth
correcting rather than leaving: an arm does NOT print `ECONOMY IS STILL` -- that
line is at 50888, inside the CALIBRATION loop, and the arm loop is a separate
`do while` at 51432 on the six market rules -- and `frozen_stop_tolerance` is
wired into the calibration loop too, so it cannot force an arm to exit early
either.

0. **THREE OF THE SIX RULES ARE VACUOUS HERE, so do not report "all six held".**
   MEASURED on the running arm, not assumed: `distance_rental_market`,
   `distance_housing_market` and `distance_inheritance_amount` are identically
   0.0 on every loop. The rent is pinned at 1 on the author's own instruction
   (*"the rent is pinned at 1 and does not need to clear the market at all"*),
   and rental supply is set equal to demand -- the two print the same sixteen
   digits, 15.403145377173294. Nothing is being cleared, so nothing is being
   checked.

   The LIVE rules are `distance_counterfactual_moments`, `distance_govt_budget`
   and `distance_drug_market`. Convergence rests on those three. Say three, not
   six. `code/collect_arm.py` detects this automatically -- it labels a series
   that is identically zero on every loop VACUOUS rather than scoring it "ok".

1. **THE LIVE RULES HELD AT ONCE, on the same loop.** An arm has converged only
   when every one of these is inside its rule simultaneously:

        distance_counterfactual_moments <= 5e-4
        rental market      <= 1e-2
        housing market     <= 2e-2
        government budget  <= 2.5e-2
        drug market        <= 5e-3
        inheritance        <= 2e-3

   A run that stopped at `max_counterfactual_loops` = 250 has NOT converged,
   whatever its last loop says. Label it as unconverged and report which rules
   were still open.

2. **THE DRUG MARKET IS THE ONE THAT FAILS, AND IT FAILS QUIETLY.** Check it by
   name rather than trusting the loop to have exited for the right reason, and
   check the SIGNED gap, not the printed `distance_drug_market`, which is
   `abs(gap)`:

        implied = 1.6200147899 * V**(1/1.46)      gap = implied - price

   A converged arm has |gap| <= 5e-3. See CALIBRATION_RECIPE.md section 6a.

3. **ALL THREE ARMS READ THE SAME BENCHMARK, so there is nothing to reconcile.**
   An earlier version of this check asked whether each session's own benchmark
   reproduced the reference to 1e-4, because each was solving its own from
   `code/seeds/n72_frozen_seed.dat`. That is no longer how it works: the
   benchmark is COMMITTED at `code/results/n90_benchmark/` and every arm copies
   the same files, so the arms are comparable by construction rather than by
   agreement. Verify it cheaply -- the benchmark scalars in each arm's directory
   should be byte-identical to the committed ones.

   The model is still not bit-reproducible between REBUILDS (about 1e-5
   relative, thread-order accumulation), so score any no-op control at 1e-4
   relative and never on exact equality.

4. **REPORT ONE EQUILIBRIUM.** Never a best-of across loops or across points.
