# Job-market presentation

*Housing First or Treatment First? Ask the Kids, Not the Parents*: 42 slides, for a talk of about an hour with questions.

The deck is published as a private Slides artifact: https://claude.ai/artifact/SEeod85RRfvQRUqTLAW2SN
(share it from the page's Share menu; present, export to PDF or PowerPoint from there).

| folder | what |
|---|---|
| `project/deck.json` | slide order, the six sections, fonts |
| `project/slides/<id>.html` | one slide each, inline styles, 1920×1080; speaker notes in `<aside>` |
| `figures/` | the three paper figures the deck shows, copied from `writing/figures/` |

The slides show the figures as uploaded copies (`/_blob/...` URLs in the HTML):
`sty-figure` is `stylized_who_uses.png` (Figure 1), `val-income` is `use_by_income.png`
(Figure 2) and `tr-figure` is `full_transition.png` (Figure 3). When a figure in the paper
changes, upload the new PNG to the artifact and swap the URL in that slide.

Every number on a slide is the paper's as of 26 October 2026 (round r414). The deck is not
generated from the number files, so a number that moves in the paper has to be changed here by
hand; `val-income` will move when the final pass of the by-income run lands.

Sections: 1 motivation and findings (slides 1–10), 2 the stylized model (11–15),
3 the quantitative model (16–20), 4 calibration and validation (21–26),
5 long-run results (27–35), 6 the transition, robustness and lessons (36–42).
