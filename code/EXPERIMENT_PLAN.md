# The policy experiments, in the order they have to be run

Written down because the order matters and because each step depends on the one
before it. Nothing here runs until the quantitative model is calibrated.

The paper's claim is that the moral hazard the debate argues about is not an
inefficiency, so the case for conditionality has to rest on something outside the
household's own objective, and that there are three such things which the debate
runs together: a genuine externality, the distortions that fund the programme, and
the programme's own distortions. These experiments are how that claim is tested
rather than asserted.

---

## Step 1. The optimal generosity of each policy, separately

Solve for the welfare maximising design of **Housing First** and, separately, of
**Treatment First**. Generosity is not one number, so the search is over the
programme's two margins:

| margin | switch |
|---|---|
| who is eligible | `threshold_income_vouchers`, currently half of median income |
| how much of the rent is covered | `rent_to_income_ratio_vouchers`, currently 0.30 |
| how many eligibles are served | `probability_of_voucher_benchmark_used_1` |

The third is the rationing margin. Referee 3's minor comment 3 asks for it to be
varied **continuously** rather than jumped from rationing to universal cover, which
is the only way to see whether there is a Laffer curve in voucher generosity or
whether the corner is optimal. Referee 2's C6 asks the same question from the
eligibility and coverage side. One search answers both.

Treatment First is the same search with `voucher_conditional_on_clean = 1`, so it
carries the detection rates and the cost of testing with it.

**The welfare criterion has to be stated, because it changes the answer.** A
utilitarian sum over the stationary distribution and the expected value of a newborn
behind the veil give different optima, and here the difference is not cosmetic: the
newborn criterion internalises the child by construction, which partly assumes the
result the paper is trying to establish. Use the **ex ante newborn** criterion as the
primary and report the utilitarian one alongside, and say which is which. A referee
who is not told will assume the flattering one was chosen.

**Output:** two optimal designs, one per policy. They will not be the same design.
Treatment First excludes people, so it can afford to be more generous to those it
serves, and it pays for testing, which pulls the other way. That is exactly why
Step 2 has to be run at both.

---

## Step 2. Compare each optimum to the other policy at the *same* generosity

This is the step that separates conditionality from generosity, and it is the whole
reason the paper can say anything clean.

1. At the optimal Housing First design, run Treatment First with the *same*
   generosity. Difference = conditionality alone.
2. At the optimal Treatment First design, run Housing First with the *same*
   generosity. Difference = conditionality alone, at the other point.

Two comparisons rather than one, because **the optimal Housing First design is not
the optimal Treatment First design**, and the answer can differ depending on which
point in generosity space it is asked at. If it does differ, that is itself a result
and the paper should say so rather than pick the comparison that reads better.

**"The same generosity" means two different things and both have to be reported.**

* **Same design.** Same eligibility cutoff, same share of rent covered, same
  probability of receipt. This is what isolates conditionality *alone*, and it is the
  primary comparison, because it is the quantitative counterpart of the stylized
  model's ranking at equal generosity.
* **Same cost.** Treatment First at the same design is a *cheaper* programme, since
  it excludes people, and it also spends on testing. Holding the design fixed
  therefore compares two programmes of different size. So run the cost matched
  comparison as well, adjusting one generosity margin until outlays match.

They cannot both be held fixed at once, which is why both are reported. And it is
worth saying in the paper that "Treatment First is cheaper" is not a welfare argument
for Treatment First: it is a different programme, and the whole point of the
separation the paper insists on is that a conclusion resting on the budget is a
different claim from one resting on an externality.

**Output:** the effect of conditionality, holding generosity fixed, at two points,
under both definitions of fixed.

---

## Step 3. Transition against the long run, for the winner

Take whichever policy wins Step 2 and solve the **transition path** as well as the
new steady state. `solve_transition_dynamics = 1`, `transition_length = 75`.

This matters because the two horizons answer different questions and the reports
disagreed about which one the experimental literature speaks to. A randomised trial
runs six to twenty four months, so it sees the first periods of a transition and
not the steady state. If housing responds immediately and the disorder adjusts
slowly, a short trial is well powered for the first and not the second, whatever
the long run effect turns out to be. Referee 1's comment 3(d) asks for proper
transition paths for exactly this reason.

**Output:** the winning policy's path and its new steady state.

---

## Step 4. The channel shutdown ladder, at the optimum, in both horizons

Break the welfare change down by channel, **at the optimal design**, reported
separately for **period 1 of the transition** and for **the long run**. Reporting it
at the optimum rather than at an arbitrary policy is what makes it say how much of
the optimal design each channel is responsible for.

| rung | switch | what it isolates |
|---|---|---|
| full counterfactual | — | everything |
| child externality off | `child_penalty_off = 1` | the intergenerational externality |
| aggregate externality off | `kappa_x = 0` | the disamenity of the headcount |
| labour supply frozen | `freeze_labor_supply = 1` | the distortion from the tax that funds it |
| drug price fixed | `fix_drug_price = 1` | general equilibrium |
| testing cost off | `cost_per_drug_test = 0` | the programme's own distortion |

Two things to state in the paper rather than let a reader find:

**The rungs do not commute.** Switching the externality off changes who is poor and
therefore how far the tax base moves, so the split depends on the order. Report a
fixed order *and the interaction term explicitly*. A residual buried inside whichever
channel happens to go last is exactly the conflation this paper argues against.

**The drug price rung is neither an externality nor a distortion.** A policy that
cures households takes them out of the market, the price falls, and a cheaper drug
draws others in. That is general equilibrium. Without a rung of its own it would be
attributed to whichever channel is switched last.

**Both columns are a newborn, and that is what makes them comparable.** Report the
transition column as the consumption equivalent for a **newborn on the date of
implementation**, and the long run column for a **newborn in the new steady state**.
The two are then the same object, the ex ante value of a household at age one, and
the only thing that differs between them is the path it lives through: the first is
born into the transition, the second into the new steady state. Any difference
between the columns is therefore the transition itself rather than a change in who is
being counted.

This also keeps one criterion running through the whole design, since Step 1 chooses
the optimum on the same ex ante newborn value.

The alternative, averaging over households alive at the reform, does not work here
and it is worth recording why. That population is a mix of ages and states, so its
average moves with the age and state composition as well as with the policy, and the
composition itself responds to the reform. A channel could then look as though it
grows with the horizon when what actually changed is the mix of people in the
average. It is the artefact the split is meant to detect, so the measure must not be
capable of generating it.

Splitting the ladder across the two horizons is the point of doing Step 3 first. The
externality is intergenerational, so it is almost absent from period 1 and grows with
the horizon; the tax distortion bites immediately. If that pattern holds it is the
cleanest statement the paper can make about why the trials and the model disagree,
and it is a prediction rather than a hope, so it is worth writing down now and
checking against the numbers later.

**Output:** a welfare decomposition by channel, twice, at the optimum.

---

## What each referee comment this answers

| comment | asks for | step |
|---|---|---|
| R1 3(d) | proper transition paths | 3 |
| R2 C2 | the homelessness disamenity priced | 4 |
| R2 C6 | optimal voucher design, broader eligibility or coverage | 1 |
| R3 M2(c) | where the externalities come from, numerically | 4 |
| R3 m3 | the voucher probability varied continuously | 1 |
| AE A9 | welfare and mortality consequences separately | 4 |
| AE A18 | fewer counterfactuals in the body | the four steps are the body |

---

## What is not built yet

* `freeze_labor_supply` and `fix_drug_price` are declared and not yet read anywhere.
  Freezing hours must hold the choice at its benchmark schedule, not penalise the
  disutility of labour: penalising it drives hours to a corner, which is a different
  experiment. Freezing the choice set preserves the Bellman identity.
* The search in Step 1 needs an outer loop over the three generosity margins. Each
  evaluation is a full solve, so the grid has to be coarse first and refined around
  the optimum.
* `solve_transition_dynamics` is off and has not been exercised since the model was
  rebuilt. Step 3 is where it gets tested.
