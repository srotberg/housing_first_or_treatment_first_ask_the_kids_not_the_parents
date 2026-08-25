
## Numbers in the paper

Every number in `writing/housing_first_children_later.src.tex` is generated, never
typed. The rules and the pipeline are in `writing/NUMBERS.md`; read it before
adding a parameter, a target or a result.

In short:
- a number lives in one place and everything else reads from it: the Fortran
  declaration for the quantitative model, the model itself for the stylized one;
- the prose quotes it as `@@name@@`, filled by `code/stylized/fill.py`
  (`@@q_*@@` names come from `code/paper/sync_tables.py`);
- a sentence asserting one quantity exceeds another takes its direction word
  from `compare()` in `fill.py`, so it turns when the numbers do;
- `writing/check_numbers.py` catches anything typed that a table also states;
- red marks what moved, produced by `\new{}` and by `sync_tables.py`, and is
  cleared by `writing/strip_red_before_transition.py` only ahead of the
  quantitative model's section, so Section 4 onward accumulates red until the
  author has read it.

## The full model's transition

`code/stylized/TRANSITION_LESSONS.md` is a standing instruction, not notes.
The stylized model's transition was built, found materially wrong, and
corrected; the quantitative model's must end up aligned with it on every point
listed there, and it is far easier to build it that way than to retrofit it.
The two that cost the most to find: a transition must integrate over the whole
age distribution alive at the reform rather than following newborn cohorts,
and the child's inherited penalty must key on the period the parent DIES in,
which is also the period conditionality acts in. Keyed on the first period
alone, conditionality's own revocations can never reach a child; keyed on
either period, a parent transmits a penalty picked up before the reform even
when the new programme housed it for the whole of its second period. Both
errors were made and both were invisible in the output.

Section 7 of that file is the other half of the rule, and it is also standing:
**a bug found in the stylized model is checked against the quantitative model
before it is closed**, and the answer is written into the table there, whether
it carried across or not. The stylized model is small enough that its mistakes
get found; the quantitative model is not, so it inherits the search.

## The model section states the model, the calibration section states the numbers

**No calibration number appears in Section 4.** The model section names a
parameter and says what it does; the value belongs in Section 5 and in the
tables, and nowhere else. This is easy to break by accident, because a sentence
explaining what a parameter is reads naturally with its value attached, and it
was broken twice in one round: a bare `0.40` inside the income equation, and the
detection rates quoted beside the policy rule that uses them.

**A parameter that only binds in a counterfactual is not a calibration
parameter.** `p_det`, `p_fp` and `c_test` do nothing in the benchmark, where
`voucher_conditional_on_clean = 0`, so they belong with the experiment rather
than in Table 5. Check what a parameter multiplies before giving it a row.

## Prose conventions

`writing/NUMBERS.md` carries three standing rules with a checker each, and
`code/stylized/build.sh` runs all three:

- **numbers** are generated, never typed (`check_numbers.py`);
- **acronyms** are spelled out with the acronym in brackets on first use and
  only the acronym after (`check_acronyms.py`);
- **compound modifiers** are hyphenated in front of a noun and not when the same
  words are a noun phrase: a long-run equilibrium, but in the long run
  (`check_hyphens.py`).

The hyphenation rule applies to ANY multi-word modifier, not only the ones
already in the list. Read the section in NUMBERS.md before adding prose.

## Red accumulates from Section 4 onward, and stripping it is a mistake

`writing/strip_red.py` takes a file and removes every red wrapper in it. It must
NOT be run on the whole note between rounds. The stripper for a comment round is
`writing/strip_red_before_transition.py`, which clears red only up to the end of
Section 3.6 and leaves everything from the transition onward alone, because the
quantitative half is still being audited and the author reads it by looking at
everything that has changed since they last saw it, not only at the most recent
round's edits.

This was got wrong once, in the round that collapsed eta_DI into zeta_DI: the
whole file was stripped, several rounds of accumulated red in Sections 4 and 5
went black in one step, and the author noticed and asked for it back. It was
recoverable only because the red version was still in the last commit. Restore
from git if it happens again -- and note that the four frozen baselines
(`params_prev.json`, `numbers_prev.json`, `tables_prev.json` and the tables
themselves) have to be restored with it, or the next build re-marks everything
as moved.

## Never write unmarked prose into the paper

**Anything I add to the paper goes in `\new{}`, and anything I add that the
author did not ask for should not go in at all.** The author reads the paper
between rounds by looking at what is red; text that arrives in black is text
they have no way of knowing I wrote.

The rule has a trap in it that has already sprung once. Red is stripped at the
START of a round, so a block added in round $n$ is red exactly once, in the PDF
sent at the end of round $n$. If the author's round $n+1$ comments do not
mention it, the strip turns it black and it becomes indistinguishable from
prose they wrote themselves. **A paragraph I authored is therefore only ever
visible for one round**, which is why the second half of the rule matters more
than the first:

- responding to a comment: edit, mark it `\new{}`, that is the job;
- explaining something to the author: say it in chat, NOT in the paper;
- noticing something the paper should say: say so in chat and ask, rather than
  writing the paragraph and letting the strip bury it a round later.

The case that produced this rule: a paragraph explaining that `ybar` and median
gross income are held at their benchmark values was written up from a
conversation about what the code does and inserted into the competitive
equilibrium definition. It was never requested, it went black after one round,
and it had to be removed in full.
