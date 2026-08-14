# Plan for writing the paper

The model note is the working document. This is the plan for turning it into a
paper: what the sections are, what each one needs before it can be written, and
the order the work happens in.

House rules carried over: no hyphens anywhere in the prose, "substance use
disorder" never "addicted", and every number in the paper traceable to a script
in the replication package.

---

## 0. One thing to fix before anything else

`abstain rate | SUD & homeless` reads **0.000** against a target of 18.67 at
sweep 2. This is not slow convergence, it is the wrong update rule.

`b_dm(2,1)` sits at 1.2e-3 inside bounds [1e-5, 5.0], having moved 20 per cent in
two sweeps under a proportional bump. The moment is **step like**: abstention is
impossible until `b` crosses a threshold, then the rate rises quickly. A
proportional bump cannot cross a threshold, so six more sweeps will not find it,
and every sweep spent bumping `b_dm(2,1)` in the dark drags the parameters that
interact with it.

Fix: move `b_dm(2,1)` from `bump` to `bisect_on`, the mechanism already used for
`treat_ucost` and `pi_d_low`, both of which are step like for the same reason.

This matters more than one moment. `b_dm(2,1)` is what makes abstention costly
for a household that already has the disorder, and it is the level that makes the
Milby housing access ratio well defined at all. R2's comment C1 calls that
elasticity the crux of the paper. If it is zero over zero, the crux is not
disciplined.

Cost of fixing now: restart the calibration, roughly 40 minutes of work discarded.
Cost of not fixing: six sweeps that cannot converge on the moment the paper's
central elasticity rests on. Fix it.

---

## 1. Section plan

Roman numerals are the paper. The right column is what has to exist first.

| § | Section | Feeds from |
|---|---|---|
| 1 | Introduction | written last |
| 2 | Stylised facts | NSDUH plus HUD, already in `data/` |
| 3 | A dynamic stylised model | pure theory, writable now |
| 4 | The quantitative model | the note, writable now |
| 5 | Calibration | note plus the calibration run |
| 6 | Validation | calibration plus `hftf_exper` |
| 7 | Mechanisms | `hftf_mech`, `hftf_ext` |
| 8 | Policy experiments | `hftf_exper` |
| 9 | The safety net | `hftf_net` |
| 10 | Transition | `hftf_trans` |
| 11 | Sensitivity | recalibrations at the endpoints |
| 12 | Conclusion | written last |

### §3 and §7 are a pair, and only one referee asked for §3

Be accurate about who asked for what, because it changes how much §3 is worth.

* **AE, A1**, asks for a simplified model section in the body. This is item one
  under his first heading, and the editor has said the paper returns to the same
  AE.
* **R1, 1(e)**, asks for the *existing static appendix* to be tightened and
  relabelled as intuition. That is not a request for a new section in the body.
* **R3, M1(a)**, asks for stylised **facts**, not a stylised model. That is §2.
* **R1, 1(d)**, states a preference *against* a toy model for one specific
  purpose: "I would find this more intuitive than a toy example that abstracts
  from dynamic savings decisions." He wants the channel shutdown ladder.

So §3 rests on the AE alone, and R1 actively prefers §7 for the mortality claim.
That argues for a **short** §3 whose job is different from §7's, not a long one.

**The division of labour.** §7 gives magnitude in the calibrated economy: shut
the mortality channel, the income gradient of use moves from one number to
another. No stylised model can produce that, and it is the evidence R1 asked for.
What §7 cannot give is the *reason* a mortality penalty generates a negative
gradient while a proportional income penalty generates a positive one, which is
an analytical statement about how the continuation value scales in permanent
income. Nor can it give the cross partial as a theorem rather than as one number
in one calibration, which matters because R2's C5 and R3's M2a both charged that
the old headline was an artefact of the utility function.

The other argument for §3 is **ordering, not evidence**. The AE's complaint is
that the moving parts obscure the economics. §7 arrives after twenty pages of
model and calibration, by which point a reader who was going to get lost is lost.

**So: two or three pages, proofs in the appendix, and make §3 and §7 correspond
one to one.** A table mapping proposition to prediction to the channel §7 shuts
to what the model gives. That way §3 stops being decoration and §7 stops being a
list of numbers, because the ladder becomes the test of the propositions.

Two periods, one asset, a binary use choice, a binary housing outcome, and a
survival probability that depends on both. **Keep the asset**: R1's objection to
the old appendix was that it abstracted from savings, and here savings makes the
continuation value rise faster in permanent income, so it strengthens Proposition
1 rather than complicating it. Say that explicitly and his objection becomes a
supporting argument. Three propositions:

1. **The income gradient.** Use falls in permanent income when the penalty for
   use is a mortality risk, and rises in permanent income when the penalty is a
   proportional income loss. A mortality penalty destroys the continuation value,
   which is increasing in permanent income, so the expected cost of use rises
   faster than the flow benefit. This is the paper's identification argument, and
   it says exactly why the sign of the gradient in the data is informative about
   which channel dominates. It is also the honest answer to R1's comment 1(d).

2. **Vouchers pull in two directions.** Guaranteed housing raises the
   continuation value and lowers use; unconditional transfers relax the
   constraint and raise it. Opposite signs, so the net is quantitative. This is
   why the paper needs the quantitative model at all.

3. **The cross partial is positive.** Conditionality raises the gap in
   continuation value between clean and disorder, and that gap is proportional to
   the value of the voucher, which scales with generosity. So the deterrent
   effect of conditionality is larger when the benefit is guaranteed than when it
   is rationed.

Proposition 3 is the paper's headline stated as a comparative static, and it is
the reason the old Experiment 1, conditionality under rationing, produced the
least attractive of the four regimes. It also lets the headline soften in the way
R1's comment 3(c) demands: the claim becomes a statement about an interaction
rather than about a winner, and it does not need a welfare ranking between two
universal regimes to survive.

### §6 Validation, in four parts

1. Targeted fit: target, model, gap, for all 24. Nothing is described as closely
   matching anything.
2. Untargeted: the two housing burden moments, the age profile of the homeless
   population, the wealth distribution.
3. Mortality: model implied standardised mortality ratios against Baggett and
   Degenhardt. Not a target; disagreement is a finding.
4. **Costantini, two arms.** The permanent unconditional voucher against his
   $-4.6$pp, and the expiring sobriety conditioned voucher against his null. Both
   as Wald ratios, both untargeted.

### §7 Mechanisms is where the intuition is actually established

Three parts: the drug use policy function by income and wealth (R2's C4), the
channel shutdown ladder (R1's 1d, R3's M2b), and the externality decomposition
(R3's M2c). Never run. This is the largest single block of unexecuted compute.

It opens with the correspondence table, so the reader sees the ladder as a test
rather than a list:

| §3 | Prediction | Channel shut in §7 | Model |
|---|---|---|---|
| Prop 1 | gradient of use in income is negative under a mortality penalty, positive under a proportional income penalty | mortality not affected by use | |
| Prop 2 | vouchers move use in two directions, opposite signs | value of life effect, then the budget effect, separately | |
| Prop 3 | the conditionality effect grows with generosity | the generosity sweep run with and without the sobriety condition | |

Row 3 is also §8's main figure, so the exhibit does double duty.

### §8 keeps two experiments, plus the sweep

Experiment 1 and Experiment 3 in the body, as A18 asks. Plus the continuous
generosity sweep run **twice**, with and without the sobriety condition, so
Proposition 3 appears as the widening gap between two curves rather than as four
table cells. That figure answers R3's m3 and R2's C6 at once and is probably the
paper's best single exhibit.

---

## 2. Dependency graph

```
calibration (running)
   |
   +--> §5 calibration table
   +--> hftf_exper  --> §6 validation, §8 experiments
   +--> hftf_mech   --> §7 mechanisms
   +--> hftf_ext    --> §7 externality decomposition
   +--> hftf_net    --> §9 safety net
   +--> hftf_trans  --> §10 transition
   |
   +--> recalibrations at elasticity endpoints --> §11
```

Everything below the calibration is blocked. Everything beside it is not.

---

## 3. Order of work

**Now, while the calibration runs.** These need no new numbers.

1. §3, the stylised model. Longest pure writing task and the highest return.
2. §4, the quantitative model. The note already has environment, preferences,
   budget, every transition, the household problem and the equilibrium. This is
   a rewrite for an academic reader, not a fresh draft.
3. §5 prose. Targets and sources are fixed; only the model column is missing.
   Organised by identification argument, with a column separating parameters
   standard in the literature from those new here (A17).
4. §2, stylised facts, and the data appendix.
5. §1 skeleton, no numbers.

**When the calibration lands.** Fill §5, then run `hftf_exper`, `hftf_mech`,
`hftf_ext`, `hftf_net`, `hftf_trans` in that order. Exper first because §6 and §8
are the sections a referee turns to first, and because the Costantini numbers are
the two placeholders in the response letters.

**Then.** §6, §7, §8, §9, §10 in order. §11 last, because the sensitivity runs are
recalibrations and are the most expensive thing in the plan.

**Last.** §1 and §12, written once the results are known, and the response
letters updated to match what the paper actually says.

---

## 4. Decisions still open

These need a call and none of them blocks writing.

- **ν, the warm glow weight.** Currently zero. The literature on altruism towards
  children can discipline it (Nishiyama 2000 is in the bib). Needed for §8's
  robustness row, not before.
- **How ω_x, the homelessness externality, is presented.** It replaces the loss
  of consortium parameter, so it will attract the same scrutiny R1 gave that one.
  The calibration moment has to be defensible before §7 is written.
- **The drug supply elasticity.** Baseline 2, bracketed by 0.79 from the
  Washington marijuana reform and roughly 3.6 from cigarettes and gasoline. The
  range is reported, so this is a presentation decision rather than an open
  parameter.
- **Whether §9, the safety net, sits in the body or the appendix.** A18 asks for
  fewer experiments in the body. It is the answer to the sharpest theoretical
  question in the reports, which argues for the body.
