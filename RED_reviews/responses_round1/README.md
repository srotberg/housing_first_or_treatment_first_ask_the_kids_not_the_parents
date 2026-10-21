# Round 1 response letters

Draft responses to RED-D-26-00078, submitted as *Housing First or Treatment First?*
and resubmitted as **Housing First or Treatment First? Ask the Kids, Not the Parents**. Five letters, four of them
comment by comment. Everything said back to a referee is in **red**; the black italic
block above each response is the referee's own text.

All five open by stating the title change and why it happened, because it is the
first thing a referee will notice and because the reason for it is the substance of
the revision: the case for conditionality has to rest outside the household's own
objective, and the externality that decides it is intergenerational.

| file | covers |
|---|---|
| `response_editor.tex` | Cover letter to Karabarbounis, plus the big summary of what changed |
| `response_AE.tex` | A1 to A20 |
| `response_R1.tex` | 1(a) to 1(e), 2(a) to 2(f), 3(a) to 3(d), 4(a) to 4(d), and the 10 smaller comments |
| `response_R2.tex` | C1 to C6, D1 |
| `response_R3.tex` | M1(a) to M1(c), M2(a) to M2(d), m1 to m3 |

Build with `./build.sh`. `enumitem` is not in this TeX installation, so list
spacing is set directly in `preamble.tex`.

## House rules

* **No hyphens** anywhere in my own prose. Referee quotes keep theirs, since
  they are verbatim.
* **Singular voice.** I, me, my. Not we, us, our. Referee quotes are exempt.
* **Labour supply is solved from the first order condition, not off a grid.** An
  earlier draft of these letters called it coarse in three places. Each period the
  household sets the marginal utility of leisure against the after tax marginal wage
  and the model solves that condition by a secant method; the curvature on leisure
  delivers a Frisch elasticity of 0.5 and the weight on leisure is calibrated to
  average hours.
* Every response says what was done, not what could be done.
* Four flags mark responses that need a second read before submission:
  `\concede`, `\correction`, `\newresult`, `\open`.

## Numbers still missing

`\tbd{}` marks them and they print in bold, so they cannot be missed on a read
through. Currently two, both the same object:

* the Housing First arm of the Costantini validation, in `response_editor.tex`
  and `response_AE.tex`
* the Treatment First arm of the same

Both come from `hftf_exper` once the calibration finishes.

## What was added after the first draft

`\thisround` marks every place where something that was a plan in the first draft
of these letters is **built and running in the Fortran**, not merely written into
the model. `\open` marks the reverse: in the written model, not yet in the code.
The distinction is now enforced rather than assumed, and three claims moved from
the first flag to the second when it was checked against the source:

| claim | where | status |
|---|---|---|
| the drug price clears a finite supply curve | R3, R1, AE | **built.** There is a supply curve, `drug_supply_shifter * quantity^(curvature-1)`, an implied price, and an update loop; the elasticity is 1.46 |
| serious mental illness is a state of the model | R1, editor, AE | **built.** `number_of_smi_states = 2`, and the state index carries `m` |
| the homelessness disamenity is priced | R2 C2, editor | **built.** `kappa_x` is declared at 0.002 and enters flow utility as `-kappa_x*model_fraction_homeless(1)` |
| the quantitative model solves a transition path | R1 3(d), editor | **written, not running.** `solve_transition_dynamics` is a parameter fixed at 0, so the transition branches are compiled out. The stylized model's transition IS solved and reported |

All three of the first list have closed. The fourth row is the one that has not,
and it replaced a claim that said "Done": R1's 3(d) and the editor letter now
distinguish the stylized model's transition, which is solved and carries that
section's result, from the quantitative model's, which is written and switched
off while the calibration runs. The alternative is letting a referee find the
switch.

Three further things were corrected in this pass:

* **The cannabis supply elasticity was attributed to the wrong paper.** It is Mace,
  Patel and Seegert (2020), not Hansen, Miller and Weber, and the value is 1.46
  rather than a baseline of 2 bracketed by cigarettes and gasoline. Those markets
  share none of the frictions of an illicit one, so they no longer bracket anything.
  Fixed in R1, R3, the AE letter and the editor letter.
* **The homelessness disamenity had the wrong figure as its baseline.** The paper
  takes the higher of Loubiere et al.'s two numbers, 0.20 per cent of average
  earnings, because setting it high favours Housing First and a ranking that
  survives that is the stronger claim. R2's C2 said the opposite.
* **The stylized model is Section 3 of the new paper**, not section 2, and it is
  calibrated rather than only derived.

What IS built and running: the taste for drugs no longer changes with addiction,
the housing access elasticity has a parameter of its own, children are valued at
every age rather than at a terminal date, four hazards vary with age,
homeownership is out, the rental grid is calibrated to the ACS size distribution,
and three numbers were wrong and are corrected.

**The Stone-Geary shifter no longer varies at all.** This is the one place where
these letters now promise something different from the first draft, so it is worth
knowing before reading them. We had said the shifter would fall with the disorder,
with mental illness and with homelessness. It does none of those: flow utility is
the same function of consumption, housing and drugs in every state and after every
choice. Housing is a *choice*, so a preference depending on it is a preference over
a choice, and it would give a user a reason to pick the street because the drug is
worth more there. The elasticity R2 asked for in C1 runs through the recovery
hazard instead, which is six times worse on the street, is a transition
probability rather than a taste, and is what Milby actually measures. The upshot is
that C1 and C5 turn out to be the same request, which the letters now say.

**The homelessness disamenity is back, and now in the code.** An earlier draft
dropped it, which was a change of mind against Referee 2 who had asked for it. It
is carried again, priced from Loubiere et al.'s contingent valuation and on the
headcount alone with no extra weight on the homeless who carry a disorder, since
that is what the survey asked about. The baseline is the HIGHER of their two
figures, 0.20 per cent of average earnings, because a larger disamenity favours
whichever policy houses more people and a ranking that survives it is the stronger
claim. The editor letter had that backwards and now does not.

**The Stone-Geary shifter is now constant too**, which goes further than R2's C5
and R3's M2(a) asked. Flow utility is the same function of consumption, housing
and drugs in every state and after every choice. The housing access elasticity R2
asked for in C1 runs through the recovery hazard instead, which is six times worse
on the street, is a transition probability rather than a taste, and is what Milby
reports. So C1 and C5 turn out to be the same request.

## Still to do before submission

* **The editor letter's overview belongs in the other four as well.** The summary
  of what changed, and why the title changed with it, is currently only in
  `response_editor.tex`. Each referee and the AE should eventually get a version of
  it, tailored to what they asked for. Deliberately not done yet: the four letters
  now carry only the two sentence title note.

## The four places we push back

Worth reviewing together, because pushing back after a rejection is the part
most likely to go wrong in tone.

1. **Costantini (AE, A14).** Neither of his coefficients is our Experiment 1:
   both are local average treatment effects against no housing intervention, so
   both live on the generosity margin. And his Treatment First is Grant and Per
   Diem, time limited transitional housing, whose null he himself attributes to
   the expiry. We do not rest on the argument: we run both of his experiments in
   the model.
2. **Abramson and Van Nieuwerburgh (AE, A15).** Their 2,500 dollars a month is
   an assumption inside their calibration, stated as such, with the components
   in their footnote 11. It cannot validate our number. We report the comparison
   and describe it accurately.
3. **R1 comment 2(c)(i).** His 74 per cent is measured over people with a use
   disorder; the model figure he compares it against is over people who use.
   Different populations. We target both, separately, which is a sharper test.
   His underlying complaint was right.
4. **R1 smaller comment 1.** The cap was on initiation, not on use, so it is not
   inconsistent with the age profile of use. But the previous draft used one word
   for both, so the confusion is ours, and a hard truncation was a poor way to
   represent a smooth regularity in any case. Replaced by an age profile.

## Things we tell them we got wrong

Listed in `response_editor.tex` section 3. Six items. Two of them, the
unemployment rate given a substance use disorder and the homelessness mortality
multiplier, biased the previous version toward R1's rival hypothesis in comment
1(d), which is worth stating plainly rather than burying.
