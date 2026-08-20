
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
  cleared only before Section 3.7, by `writing/strip_red_before_transition.py`.

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
