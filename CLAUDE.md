
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
and the child's inherited penalty must key on the parent's whole life rather
than on one period, or conditionality's own revocations can never reach a
child.

Section 7 of that file is the other half of the rule, and it is also standing:
**a bug found in the stylized model is checked against the quantitative model
before it is closed**, and the answer is written into the table there, whether
it carried across or not. The stylized model is small enough that its mistakes
get found; the quantitative model is not, so it inherits the search.

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
