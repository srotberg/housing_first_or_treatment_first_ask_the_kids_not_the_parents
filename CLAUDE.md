
## Numbers in the paper

Every number in `writing/housing_first_or_treatment_first_ask_the_kids.src.tex` is generated, never
typed. The rules and the pipeline are in `writing/NUMBERS.md`; read it before
adding a parameter, a target or a result.

In short:
- a number lives in one place and everything else reads from it: the Fortran
  declaration for the quantitative model, the model itself for the stylized one;
- the prose quotes it as `@@name@@`, filled by `code/stylized/fill.py`
  (`@@q_*@@` names come from `code/paper/sync_tables.py`);
- a sentence asserting one quantity exceeds another takes its direction word
  from `compare()` in `fill.py`, so it turns when the numbers do;
- `writing/tools/check_numbers.py` catches anything typed that a table also states;
- red marks what moved, produced by `\new{}` and by `sync_tables.py`, and is
  cleared by `writing/tools/strip_red_before_transition.py` only ahead of the
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

**The statutory social security values live in Appendix A (the standard parameters, moved out of Section 5.2 on 8 October), Block 12.** The PIA shares
$\alpha_1,\alpha_2,\alpha_3$, the bend points, the taxable maximum and the SSI floor were
moved into the Section 4 footnote on 1 October and moved back the same evening (the author:
*"If you already show it in the calibration section then just refer the reader to that
section"*). The footnote states the formula and refers to Appendix A; the values are in
the $S(y)$ item and Table A1 only.

**A parameter that only binds in a counterfactual is not a calibration
parameter.** `p_det`, `p_fp` and `c_test` do nothing in the benchmark, where
`voucher_conditional_on_clean = 0`, so they belong with the experiment rather
than in Table 5. Check what a parameter multiplies before giving it a row.

## The gaps table is `code/gaps_table.py`, and it is the table

The author, 16 September: *"i want you to remember this table, because it is
key!"*. Twenty-three parameters, five columns -- the parameter's value, the
model's moment, the data target, the gap in per cent, and which way the update
rule moves the parameter at that gap. `/gaps` runs it. Do not hand-assemble a
different table; if a row is missing, add it to the script.

**The direction column is parsed out of the Fortran, never remembered.** Two
things that parsing caught, both of which I had wrong:

- `kappa_phi_d_level`'s rule is `kappa - adjuster*(drug_user_income_data -
  model_avg_income...)`. The bracket is DATA MINUS MODEL, reversed from every
  other instrument, so reading the operator alone gives the opposite direction.
- Five updates assign through an intermediate -- the onset writes
  `onset_step_1` before it lands in `addiction_onset_base` -- so keying on the
  parameter name finds no rule at all. Key on the adjuster.

**Three rows mislead at face value** and the script labels them: `theta` is the
AGGREGATE, not the mean-of-ratios `MOMENT` row that runs three to four times
higher; `emp_homeless` has NO INSTRUMENT and only follows h_1; and "not
printed" means the update was gated that block, not that the value is missing.

**A block is not a loop.** `loop_count` advances twice per moment block.

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

**Two decimals, never three** (the author, 29 September: *"no need to put 3 decimals
in the text anywhere. please make a note of that"*). The text quotes at most two
decimals; numbers below 0.1 keep two significant figures; tables likewise unless the
third decimal matters. `fill.text_precision()` applies it at fill time; see
"Decimals" in NUMBERS.md.

## Never abbreviate the two policies

The author, 1 October: *"use the full name Treatment First, or Housing First. I wrote TF and
HF because it is easier for me"*, and *"make sure you never use TF or HF abbreviations"*. The
author's comments use TF and HF as shorthand; the paper never does, in prose, tables, captions
or equations. Translate the shorthand when applying a comment.

## A parameter's paragraph runs in a fixed order

The author, 1 October: *"In general, all the parameters should first describe what the
parameter controls, how it relates to TF, HF or drug use (if those are applicable, because
they may not always be applicable), and, then explain how things change when it rises, and
only at the end discuss the target and source."* Every item in Section 5 follows it: what it
controls, its link to TF, HF or drug use, what happens as it rises, then the value, the
moment and the source. A value or a citation in the first sentence is the mistake this
rule was written for.

## Red accumulates from Section 4 onward, and stripping it is a mistake

`writing/tools/strip_red.py` takes a file and removes every red wrapper in it. It must
NOT be run on the whole note between rounds. The stripper for a comment round is
`writing/tools/strip_red_before_transition.py`, which clears red only up to the end of
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

## Deletions are struck through, and changes carry a note

**STRIKES REINSTATED, 11 October (round r305): the author, *"if you delete something i want to see what you
deleted"*, *"show me in the paper the changes in crossed lines and updates in red"*.** The r120 waiver (*"no need to
show striked lines anymore"*) is over: every round runs `track_changes.py` against the source as the author last read
it, `\del` is defined in the preamble again (`\DeclareRobustCommand{\del}[1]{{\color{red}\sout{#1}}}`), and the
round's splice keeps the strikes it generates (the `drop_marks` call was removed from `splice_r305.py`; copy that
splice forward, not an older one). Display maths is skipped by the striker, so a deleted piece of an equation is said
in a `\why{}` note. **The abstract stays under 150 words** (the author, 11 October: *"if you update the abstract make
sure its below 150 words"*; it is 148 at r305, counting a filled number as one word).


The author, 3 October: *"deleted sentences should show as crossed so I know what you delete"*, and *"leave notes
for me in case I need to understand why you made a change"*. Both are standing.

- **Deleted text stays in the paper as `\del{...}`**, red and struck through (ulem's `\sout`), right before
  whatever replaced it. Write the round's edits with `\new{}` as usual, keep a copy of the source as the author
  last saw it, then run `python3 writing/tools/track_changes.py OLD CUR OUT`: it diffs the two word by word, strikes
  every deleted run, wraps any inserted run that is not yet marked, takes the reference list entry by entry,
  and leaves display maths, tables, figures and section titles alone (listed as SKIPPED; say those in a note).
  Generated sentences get the same treatment from the round's splice, which strikes what a moved name used to
  print. Tables stay black, so a table change goes in a note.
- **A substantive change carries `\why{...}`**, a short green note after it, listed with its page after the
  abstract. Say what was wrong and where the new number or claim comes from. Not for grammar or hyphens.
- `writing/tools/strip_red.py` removes both, contents and all (`writing/tools/marks.py`), and the checkers skip them.
  Escape `_` in anything struck (`\sout` is not verbatim), and never strike a lone control space.

## Never write unmarked prose into the paper

**Never open a `\new{}` with a space.** `\new` is `{\color{red}#1}` and the colour change eats a
leading space, so `it is\new{ in the benchmark}` prints "isin the benchmark". Put the space outside:
`it is \new{in the benchmark}`. It happened twice on 2 October.

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
- explaining something to the author: say it in chat or, for why a change was made, in a `\why{}` note,
  which the strip removes -- NOT in the paper's prose;
- noticing something the paper should say: say so in chat and ask, rather than
  writing the paragraph and letting the strip bury it a round later.

The case that produced this rule: a paragraph explaining that `ybar` and median
gross income are held at their benchmark values was written up from a
conversation about what the code does and inserted into the competitive
equilibrium definition. It was never requested, it went black after one round,
and it had to be removed in full.
