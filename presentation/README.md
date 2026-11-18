# Job-market presentation

**The talk is the LaTeX Beamer deck**: `latex/slides.src.tex`, built by `latex/build.sh` into
`housing_first_or_treatment_first_slides.pdf` (44 slides: 41, a closing slide and two backup tables). Speaker notes
are in `\note{}`.

**Every number on a slide is the paper's, never typed** (since 18 November 2026; until then the deck was typed from
round r419). `latex/fill_slides.py`, which `build.sh` runs first, fills `slides.src.tex` into `slides.tex`:

- a name between double at signs is one of the paper's own names, loaded as `code/paper/splice.py` loads them and
  printed at the paper's text precision, so a slide says exactly what the paper says;
- the few numbers the paper prints only in a table or inside a generated sentence are the deck's own names (`DECK` in
  the script), read off the table file or out of the sentence; each is checked against the paper's name where one
  exists, and the build stops if the paper rewords a sentence it reads;
- every direction the slides state in words (falls, gains, loses) is asserted against the numbers, so a result that
  changes sign stops the build instead of contradicting the word beside it;
- Tables 3, 4 and 7 are written by the script from the paper's table files (`gen_*.tex`); Table 5, the weight-of-one
  table, the stylized model's two tables and the three figures are input from `writing/` directly.

So after the paper's numbers move, `latex/build.sh` brings the deck with them. Edit `slides.src.tex`, never
`slides.tex`.

The HTML version below is an earlier draft of the same talk (26 October, round r414), not kept in step with the
paper since.

*Housing First or Treatment First? Ask the Kids, Not the Parents*: 42 slides, for a talk of about an hour with questions.

The deck is published as a private Slides artifact: https://claude.ai/artifact/SEeod85RRfvQRUqTLAW2SN
(share it from the page's Share menu; present, export to PDF or PowerPoint from there).

| folder | what |
|---|---|
| `project/deck.json` | slide order, the six sections, fonts |
| `project/slides/<id>.html` | one slide each, inline styles, 1920×1080; speaker notes in `<aside>` |
| `figures/` | the three paper figures the deck shows, copied from `writing/figures/` |
| `charts.py` | writes the four results slides as charts with their explanations (28, 31, 33, 39): `python3 presentation/charts.py`, then republish those four |

The slides show the figures as uploaded copies (`/_blob/...` URLs in the HTML):
`sty-figure` is `stylized_who_uses.png` (Figure 1), `val-income` is `use_by_income.png`
(Figure 2) and `tr-figure` is `full_transition.png` (Figure 3). When a figure in the paper
changes, upload the new PNG to the artifact and swap the URL in that slide.

Every number on a slide is the paper's as of 26 October 2026 (round r414). The deck is not
generated from the number files, so a number that moves in the paper has to be changed here by
hand. `val-income` carries the by-income run's final pass (26 October, 15:09 UTC).

Sections: 1 motivation and findings (slides 1–10), 2 the stylized model (11–15),
3 the quantitative model (16–20), 4 calibration and validation (21–26),
5 long-run results (27–35), 6 the transition, robustness and lessons (36–42).
