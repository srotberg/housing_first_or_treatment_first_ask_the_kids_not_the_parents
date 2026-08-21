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
| a number a figure shows | `run.py`, while it draws | `figure_numbers.json` → `fill.py` |
| a cell of Table 3 | `welfare.py`, while it writes the table | `welfare_numbers.json` → `fill.py` |
| a cell of Table 4 | `children.py`, while it writes the table | `children_numbers.json` → `fill.py` |

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

## Numbers that also appear on a figure or in a table

If the prose quotes a number that a figure or a table shows, **whatever draws
the figure or writes the table computes it, and the prose reads it**. `run.py`,
`welfare.py`, `children.py` and `transition.py` each write a small JSON beside
their output and `fill.py` merges all four. Never compute such a number twice.

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

## Still to do: the quantitative model's tables and figures

Sections 1 to 3 are fully wired: every number in the prose is an `@@name@@`
filled from the script that also draws the figure or builds the table it appears
in, so the two cannot disagree. Tables 5 and 6 are wired to the Fortran through
`code/paper/sync_tables.py`.

**What is not yet wired is everything else in Section 4 onward**: the experiment
tables, the non targeted moment tables, and the quantitative model's figures.
Those still state numbers that the prose repeats by hand. The author has asked
for the same treatment there, table by table and figure by figure.

The pattern to follow is the one that works here, and the rule that makes it
work is this: **the script that produces a table or a figure is the script that
exports the numbers the prose quotes.** Not a second script that recomputes
them from the same source, which is how an income ratio of 3.33 came to sit
beside a figure showing 4.70. Where a number is unavoidably produced twice,
`verify.py` compares the two, which is what the check on Tables 1 and 2 does.

## Acronyms

**Every acronym is spelled out in full on its FIRST use with the acronym in
brackets, and only the acronym is used after that.** Before writing an acronym,
check whether it has already appeared. If it has, use the acronym alone and do
not repeat the full name. If it has not, write the full name and put the acronym
in brackets after it.

The expansion has to account for every letter. "Consumption equivalent (CEV)"
was wrong for that reason: the V had nothing behind it. It is a consumption
equivalent VARIATION.

The acronym belongs in its own brackets, not folded into a citation. "(National
Survey on Drug Use and Health, NSDUH 2024)" defines nothing; "the 2024 National
Survey on Drug Use and Health (NSDUH)" does.

`writing/check_acronyms.py` scans the prose, ignoring comments and the
bibliography, and reports any acronym used more than once whose first
appearance is not a definition. Run it with `check_numbers.py` before sending a
draft.
