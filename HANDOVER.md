# Handover

State as of 16 August, branch `claude/two-period-stylized-model-8ewnmt`, merged to
`main` and pushed. Everything below is committed.

---

## 1. Standing instructions

* **Merge to main and push, every time, without asking.**
* **No hyphens** anywhere in the paper or the letters. The only agreed exceptions
  are compound proper names: Stone-Geary, Cobb-Douglas.
* Comment rounds work like this: the reader sends an annotated PDF, you **strip
  the red from the reviewed part**, apply the comments, and mark **only this
  round's changes** in red. Then rebuild, push, and send the PDF back.
* **Cut exactly to the highlight.** Two rounds were lost to over removal: a
  `remove` that stopped mid sentence was treated as licence to finish the
  sentence. If a highlight is ambiguous, ask. Anything you add or restore on your
  own initiative goes in red so the reader can see it.

## 2. The last comment round: APPLIED

The reader's PDF `4e810400-stylized_note_3.pdf` carried comments on Sections 2.1
and 2.2. All are applied and the note is rebuilt and pushed. Recorded here
because the reasoning behind two of them matters:

**Section 2 opening paragraph**
* "states" -> "describes"
* remove "completely"
* remove the whole sentence beginning "Everything else is written out, because it
  is what turns a directional answer into a quantitative one", together with the
  clause listing Sections 1.2 to 1.6.2.

**2.1 Demographics, the state and the choice set**
* "don't put number yet. numbers are for the calibration section" on the ages and
  period counts: take the numerals out, they belong in the calibration section.
* "Newborns replace the dead" -> "Newborns replace the dead **exactly, so the mass
  of households is constant**".
* The state list: remove the grid point counts (40 points, 7 points, 6,720 per
  age, 403,200 total) and the sentence about assets being non negative. Rewrite as
  prose: "where assets are denoted as a, permanent productivity as y, etc (write
  it nicely)".
* Remove the whole paragraph "Two economies in that list are choices rather than
  oversights ... reinstated if moving costs were added."
* The choice list: same treatment, "where n denotes hours...".
* "treatment take up" -> "**SUD** treatment take up".
* Remove "and next period assets a' after. Every shock is drawn after all of
  that ... the choice comes first, the draw second." (reader: "I think you can
  remove this.")

**2.2 Preferences**
* In equation `eq:futil`, the shifter is written `b_{dmh'}`. The reader: "we
  decided to keep this constant." So it must be plain `b`, with no subscripts,
  everywhere in that equation and anywhere else it still carries them.
* Remove almost all the surrounding discussion: the "Four things are new"
  sentence from "Treatment costs utility ..." onward, the whole `kappa_x H`
  disamenity passage, the "flow utility is the same function" sentence, the
  "That is a restriction and it is deliberate" paragraph, and the entire
  `{\color{red}...}` block about `b` falling with homelessness and the recovery
  hazard, which runs to "the object the trial actually identifies."

One consequence worth watching. The `kappa_x H` term is still IN the utility
equation, but the prose explaining it was removed on instruction, so as it stands
the disamenity appears in the formula unexplained until Section 2.16. Either that
is intended, with the explanation living in the calibration section, or a clause
naming it needs to come back. Ask.

Also done, beyond the marked comments: `b_{dmh'}` carried its subscripts in four
more places outside 2.2, in the budget constraint and the Bellman equation. Since
`b` is constant they were simply wrong, so they are now plain `b`.

To read the next round's annotations, use the script pattern used all along: `pypdf`, read `/Annots`, match `/Contents` to the text under the
`/QuadPoints` by y coordinate, and use the x range to find which words on the line
a partial highlight covers.

## 3. The pipeline, and the one trap in it

`writing/housing_first_children_later.src.tex` holds `@@placeholder@@` markers. `fill.py`
substitutes them and writes `writing/housing_first_children_later.tex`, which is what pdflatex
builds. **Editing `housing_first_children_later.tex` directly is lost on the next fill; editing
only the source does not show up until you re-run fill.** Order is always:

```
cd code/stylized
python3 tables.py       # tab_external, tab_internal, tab_channels, tab_policy
python3 welfare.py      # tab_welfare
python3 children.py     # tab_children
python3 internalise.py  # tab_internalise
python3 run.py          # the three figures
python3 fill.py         # numbers into the note
cd ../../writing && pdflatex -interaction=nonstopmode housing_first_children_later.tex   # twice
```

Tables and figures take roughly twenty minutes each; `fill.py` about ten. If an
edit touches no placeholder you may apply it to both `.src.tex` and `.tex` and
skip the fill, which is what was done for pure wording changes.

**Red on numbers is automatic.** `code/stylized/numbers_prev.json` holds the same
dictionary computed at the calibration the reader last saw. `fill.py` marks a
number red if and only if it differs. After a reviewed version ships, refresh that
file so the next round starts clean, otherwise every number stays red forever.

**A LaTeX trap that bit twice.** `\new{}` is `\textcolor{red}{}` and **cannot span
a paragraph break**. Multi paragraph passages must use `{\color{red}...}`. Also:
when you strip red from a region, a `{\color{red}` block's closing brace goes with
it, so any script that searches forward for a lone `}` will run on into the next
section. That deleted the Section 2 heading once. Always verify
`grep -c "section{The quantitative model}"` after a strip.

## 4. The stylized model: done

Five parameters, five targets, converged and screened.

| moment | target | model |
|---|---|---|
| housing over non drug spending | 26.8% | 27.0% |
| homelessness rate | 0.399% | 0.43% |
| value of a statistical life | 80 | 80.0 |
| users acquiring a SUD | 33.2% | 37.1% |
| drug participation | 5.13% | 5.13% |

The channel screen passes and must be re-run after any recalibration, before any
other moment is read: with no channel users earn 2.89 times the average, mortality
alone drives it to 0.43 and to 0.19 at 125 per cent, unemployment alone leaves it
at 3.33 throughout. Minimum ex ante value of life 1.05, positive everywhere.

**The calibration order matters and is load bearing.** `gam` on the housing share,
then `h_hl` on homelessness, then `aleph` on the VSL, then `lam`, then `b` on
participation **last**. Rationale is in `calibrate.py`'s docstring, including the
two arrangements that failed: setting both gamma and the grid, and calibrating
`h_L` on the share.

## 5. The full model: two defects, one fixed

Running now from `scratchpad/hf_run` on `hftf7`. Build line is in `code/readme.txt`
and **requires `-ffree-line-length-none`**; without it the source does not compile.

**Fixed this session, all in `FORTRAN_AUDIT.md`:**
* `re_do_simulation_with_fixed_parameters` was 1, which zeroes every `distance_*`
  and skips the whole update block. The program was not calibrating at all.
* `housing_size(grid_size-2)` was being overwritten with the mortgage eligibility
  threshold regardless of `include_homeownership`, which produced **exactly zero
  homelessness** and NaN in every homeless moment.
* The grid expander was targeted on the homeownership rate, identically zero now
  that owning is out.
* The two rental sizes are calibrated to the ACS 2023 size distribution,
  13.2 / 24.1 / 62.7, from `data/us_housing_dist.csv`. `largest_house_size` was
  0.315, a leftover from the homeownership version; it converged near 0.076.
* The addiction hazard was a compile time constant holding **0.037, which is the
  NSDUH disorder PREVALENCE written in as an annual onset probability**. Against a
  recovery rate of 0.025 the flow balance pins addicted over experimenters at
  1.48, giving 32.6 per cent prevalence. It is now calibrated on
  `sud_rate_data = 0.0368`, starting at 0.0016.

**NOT fixed, and it is the important one.** The note specifies
`pi_d(v) = 1 - exp(-lambda v)`, so onset rises with how much is used. The code
indexes `addiction_probabilities` by a discrete choice and carries no quantity, so
onset is flat in `v`. The household never internalises that using more is riskier,
which is the mechanism Section 1 rests on; drug prices move quantity but not
prevalence; and the two models do not share an addiction technology, which the
note says they do. 31 read sites across the value nests, the distribution loop and
the transition. Full write up in the audit. **Fix the form, then calibrate lambda
on the disorder rate.** That is the reader's instruction.

**Also still open:** the adjusters oscillate rather than settle, so damp
`smallest_house_size_adjuster` and `largest_house_size_adjuster` once there are
enough loops to size the step. And the run does not resume after a kill: three
starting values are hardcoded as a warm start, but the proper fix is writing the
calibrated values to a file each loop.

## 6. The letters

Five letters in `RED_reviews/responses_round1`, built with `./build.sh`.
`\thisround` means **built and running in the Fortran**; `\open` means in the
written model only. That distinction was audited against the source and three
claims moved: the drug supply curve, the homelessness disamenity, and serious
mental illness are all written only. `grep` proves each. Do not promote any of
them without checking the source first.

## 7. Things the reader has decided, so do not reopen

* `b` is **constant across every state and every choice**. Not with the disorder,
  not with mental illness, not with housing. Housing is a choice, so a preference
  depending on it is a preference over a choice; and the marginal value of the
  drug goes as `1/(b+v)`, so a smaller `b` makes the drug better, which is a
  strange thing to assert. The housing access elasticity runs through the recovery
  hazard instead, six times harder on the street, which is what Milby measures.
* The Milby citation is AJPH 95(7):1259 to 65, "To House or Not to House". The
  note previously had a different paper and the wrong journal.
* The homelessness disamenity is priced on the **headcount alone**, with no extra
  weight on the homeless who carry a disorder.
* The stylized model's rental grid is **set and quoted**; gamma is **calibrated**.
  Not the other way round.
