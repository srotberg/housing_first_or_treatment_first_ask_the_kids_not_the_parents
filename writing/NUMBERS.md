# Where the paper's numbers come from

Every number in the paper is generated. None is typed. This file says how that
works, and what to do when a parameter or a result is added.

## The rule

A number appears in the repository **once**. Everything that quotes it reads
from that one place.

| kind of number | lives in | reaches the paper via |
|---|---|---|
| a target of the quantitative model | the `*_data` declaration in the Fortran | `code/paper/sync_tables.py` → Tables 5 and 6, and `@@q_*@@` in the prose |
| an externally set parameter of the quantitative model | its Fortran declaration, or the table cell if it has none | the same |
| anything the stylized model computes | the model itself | `code/stylized/fill.py` → `@@name@@` |
| a stylized parameter or target | `stylized.py` / `calibrate.py` | `code/stylized/tables.py` → Tables 1 and 2 |
| a transition number | `transition.py` | `transition_numbers.json` → `fill.py` |

## Adding a parameter or a result

1. Add the row to `writing/tables/tab_eleven.tex` or `tab_standard.tex`, or to
   the generator for the stylized tables.
2. If it has a Fortran declaration, add the symbol to `code/paper/links.py`.
   **Do not** let anything match it by value: the replacement rate and the
   employment rate of the homeless are both 0.50, the discount factor's target
   and the child's SUD ratio are both 3.00, and a value matcher paired all four
   the wrong way round when this was tried.
3. Run `python3 code/paper/sync_tables.py`. It exports a placeholder named
   `q_<symbol>`.
4. Quote it in the prose as `@@q_<symbol>@@`, never as a digit.
5. Run `python3 writing/check_numbers.py`. It should stay clean.

## Numbers that also appear on a figure

If the prose quotes a number that a figure shows, **the figure computes it and
the prose reads it**. `run.py` writes `figure_numbers.json` while it draws, and
`fill.py` loads that file rather than recomputing. Never compute such a number
twice.

This is not a tidiness rule. The note went to press saying the income ratio was
"unchanged at 3.33" at half the mortality channel's strength, beside a figure
that showed 4.70 at that point and 4.70 with the channel off; the sentence
contradicted the picture above it and the arithmetic inside it. Two of the
scan's points also fail to hit the participation target, which the figure's own
note used to deny; `partnote` now states it.

The other half of the same rule: **build with `code/stylized/build.sh` and
nothing else.** A hand-maintained substituter that filled `@@name@@` from a JSON
of typed values was used once to save a rebuild, and it silently replaced
generated numbers with stale ones throughout the note. It has been deleted. If
a rebuild is too slow, wait for it.

## Sentences that assert an inequality

A sentence that says one quantity is larger than another is stating a
**result**, and results move. Take the direction word from `compare()` in
`fill.py` rather than typing it:

```
out.update(compare(mt['cost'], mh['cost'], 'cost', more='more', less='less'))
```

gives `@@costdir@@`, so "Treatment First is slightly *@@costdir@@* expensive"
turns by itself. The two voucher outlays differ by under half a percent, so
which is the larger is not robust to a recalibration; a sweep that flipped the
sign and left the paragraph reading "more expensive" would be a contradiction
no reader could resolve and no compiler would catch. Do this for any comparison
whose sign is not guaranteed by theory.

## Red

`fill.py` compares every number against `numbers_prev.json` and wraps whatever
moved in `\new{}`, which is red. `sync_tables.py` does the same against
`params_prev.json` for the table cells. So an update shows up as an update
without anyone deciding to mark it. Freeze a new baseline with `--freeze` on
each, and only once the reader has seen the current round.

Red is cleared at the start of a round only up to the start of the quantitative
model's section, by `writing/strip_red_before_transition.py`. From Section 4
onward it accumulates until the reader says otherwise.

## The checker

`writing/check_numbers.py` reports any literal in the prose that a table also
states. It prints rather than fails, because ages, sample sizes, years,
bibliography page numbers and other papers' odds ratios all collide with
parameter values. A genuine collision goes in `ALLOW` with a reason; anything
else gets a placeholder. Run it whenever a number is added, and after every
sweep.
