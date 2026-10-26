# Round 1 response letters

Responses to RED-D-26-00078, submitted as *Housing First or Treatment First?* and resubmitted as
**Housing First or Treatment First? Ask the Kids, Not the Parents**. Five letters, four of them comment by
comment. Everything said back to a referee is in **red**; the black italic block above each response is the
referee's own text, untouched.

| file | covers |
|---|---|
| `response_editor.tex` | Cover letter to Karabarbounis: what the paper now finds, what was built, cut and added, errors in the previous version, calibration and validation, Costantini, push-back and what the paper does not do |
| `response_AE.tex` | A1 to A20, plus the AE's closing paragraph on simplifying secondary dimensions |
| `response_R1.tex` | 1(a) to 1(e), 2(a) to 2(f), 3(a) to 3(d), 4(a) to 4(d), and the ten smaller comments |
| `response_R2.tex` | C1 to C6, D1 |
| `response_R3.tex` | M1(a) to M1(c), M2(a) to M2(d), m1 to m3 |

Build with `./build.sh` (it deletes every letter's aux files, so never run it while another build is going).
`enumitem` is not in this TeX installation, so list spacing is set directly in `preamble.tex`.

## Revised against the paper of 26 October 2026 (round r414)

The letters had been drafted against a much earlier version of the new paper, and every response was
re-checked against the current one. Every number in a response is now one the paper states, and every
section, table, figure and footnote number is as printed in the r414 PDF. **Footnote numbers will shift if
footnotes are added before them**, and the transition numbers quoted (1.45, 81, 11, 67, 74 and so on) are
still marked for refresh in the paper; if either moves, the letters must follow.

What changed most, because the paper changed:

* **Labour supply is gone from the model** (footnote 19). The letters used to defend keeping it, solved from
  the first order condition; they now concede A3 and answer R3's m1 accordingly.
* **The quantitative transition is solved and reported** (Sections 6.4 and 6.5, Figure 3, Table 7), where
  the letters used to say it was switched off.
* **The homelessness disamenity is not in the benchmark**, only a robustness run (footnote 4: no long-run
  gain moves by more than 0.14 points). The letters used to call it the baseline.
* **Costantini:** the paper compares only his Housing First arm (Validation Block 7, 3.6 against 4.6
  percentage points); the `\tbd` table is gone, and the letters say there is no counterpart to his Treatment
  First arm.
* **R1's 2(c)(i) is now a concession, not a push-back.** The paper targets his 74 percent (users' income over
  the average); the model reaches 62, and Figure 2 shows why.
* **Abramson and Van Nieuwerburgh (A15):** the push-back is gone; the model no longer has a fiscal cost of
  homelessness, so no comparison is made.
* The "errors in the previous version" list is down to four items that the paper supports.

## House rules

* **No hyphens** in my own prose. Referee quotes keep theirs, since they are verbatim.
* **Singular voice.** I, me, my. Never we, us, our.
* Never "TF" or "HF"; "percent", not "per cent"; British spelling, except "stylized", which follows the
  paper's section title.
* Every response says what was done, not what could be done, and ends by saying where in the paper it is.
* Flags, in bold, for a second read before submission: `\concede`, `\correction`, `\newresult`, and `\open`
  for a request the paper does not meet. `\thisround` and `\tbd` are retired.

## Requests the paper does not meet (each marked `\open` where it is answered)

* **AE:** mortality as a separate outcome (A9); Costantini's Treatment First arm, and Cohen (2024),
  Brounstein and Wieselthier (2026), Humphries et al. (2026) not cited (A14); no comparison with Abramson and
  Van Nieuwerburgh or the Council of Economic Advisers (A15); Vaillant's alcoholism remission rate still sets
  baseline recovery (A17); no universal voucher experiment (A18); no direct wage penalty on users (A20).
* **R1:** the mortality against unemployment comparison is made in the stylized model, not the full one
  (1(d)); no run without SMI (1(a)); misses on users' income and the homeless (2(c)); no Jacobian or
  sensitivity statistic (2(f)); no false positives (4(b)); no stigma or administrative burden (4(c)); no
  systematic sensitivity (4(d)); the age limit on starting to use stays (S1).
* **R2:** disamenity only as robustness, Corbae, Glover and Nattinger (2024) not cited (C2); no policy
  function plots (C4); no generosity or optimal design (C6); the two larger rental sizes are set, without a
  moment or a sensitivity (D1).
* **R3:** no drug use among voucher holders (M1(a)); no gradient by severity (M1(c)); no use by assets or
  employment (M2(b)); no optimal programme (M2(c)); no labour supply elasticity (m1); no graphs against the
  value of life (m2); no continuous voucher sweep (m3).

## Statements in the letters that are inference, not the paper's words (check before sending)

* Leaving out a fiscal cost of homelessness does not favour Treatment First, since Treatment First lowers
  homelessness (AE A15, R2 C6, R3 M2(c)); and the editor letter's reason for removing it.
* A parent's choices reach its child's adult life only through productivity (R2 C3).
* The reasons given for not citing Corbae (R2 C2), for showing the mechanism in the stylized model (R2 C4),
  for not reporting mortality separately (AE A9), and for having no rationing-free experiment (AE A18).
* A household that already has a SUD risks nothing further by using in the benchmark (R3 M2(b)); the Meyer
  comparison is with households of similar means (R3 M1(b)).
* The description of Costantini's design (AE A14), checked against his paper in `related_lit`, and the
  previous draft's source for the 37 percent, Kuhn and Culhane (1998) (AE A16, editor letter).
