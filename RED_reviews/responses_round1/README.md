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

## Second pass, 3 November 2026 (round r419)

Each letter was checked again, sentence by sentence, against its report and the paper as it now stands, with
one priority above the rest: the paper must be represented correctly. Statements the paper does not support
were removed; reasons the paper does not give are now worded as mine ("I removed ...", "I would expect ...");
"never rises" is limited to the main transition; "15 and 11 years" became Table 7's periods; Costantini is
compared on the Housing First arm only, "of the same order"; claims about the version the referees read were
checked against `writing/old/housing_first_or_treatment_first.pdf`, and one error item in the editor letter
that did not hold (the old homelessness target as a person rate against a household agent: the old model's
agent was an individual) was removed. Every request the paper does not meet now has its own plain `\open`.

## Requests the paper does not meet (each marked `\open`)

* **AE:** the stylized model derives only the income gradient (A1); the version with $b$ falling with the
  disorder is not solved (A8); mortality is not reported as an outcome (A9); no false positives, stigma or
  systematic sensitivity (A11); no Jacobian or sensitivity statistic (A12); the elasticity of homelessness to a
  SUD is not reported as such (A13); no model counterpart to Costantini's Treatment First arm, and Cohen (2024),
  Brounstein and Wieselthier (2026) and Humphries et al. (2026) are not cited (A14); no fiscal cost of
  homelessness and no comparison with Abramson and Van Nieuwerburgh (A15); Vaillant's alcoholism remission rate
  still sets baseline recovery (A17); no universal voucher experiment, and the alternative transitions stay in
  the body (A18); no direct wage penalty on users (A20).
* **R1:** no run without SMI (1(a)); the mortality against unemployment comparison is made in the stylized model
  only (1(d)); users' income and the homeless' employment, income and age are still missed (2(c)); the response
  of homelessness to voucher access, of employment to vouchers and of drug use to generosity are not compared
  with evidence such as the Family Options Study (2(d)); the model's moments are not defined in an appendix
  (2(e)); no Jacobian (2(f)); no false positives (4(b)); no stigma or administrative burden (4(c)); no results
  with the hazards changed (4(d)); the age limit on starting to use stays (S1); no column of percent changes (S2).
* **R2:** disamenity only as robustness, Corbae, Glover and Nattinger (2024) not cited (C2); no policy function
  plots (C4); no broader eligibility, more generous voucher or optimal design (C6); the two larger rental sizes
  are set without a source, a moment or a sensitivity (D1).
* **R3:** no drug use among voucher holders, and no comparison with the trials on voucher receipt and
  homelessness (M1(a)); no gradient by severity (M1(c)); welfare is not recomputed under another utility
  function (M2(a)); no use by assets or employment status (M2(b)); no optimal programme, no fiscal cost per
  homeless household and no direct externality of drug use beyond the user's own child (M2(c)); no labour supply
  elasticity (m1); no sensitivity for any parameter of the quantitative model (m2); no continuous voucher sweep (m3).

## Worded as my reading, not the paper's finding (check before sending)

* Leaving out a fiscal cost of homelessness would not favour Treatment First, since Treatment First lowers
  homelessness (AE A15, R2 C6, R3 M2(c)): each letter now says the paper does not test it.
* The reasons for: showing the mechanism in the stylized model (R2 C4), not reporting mortality separately
  (AE A9), having no rationing-free experiment (AE A18), having no counterpart to Costantini's Treatment First
  arm (AE A14), and dropping the generosity comparison (R3 m3).
* R3 M2(a): a new concession, that the drug sits in a non-separable bundle with consumption and housing at
  $\sigma=2$, so preferences still shape how use affects the value of the other goods. **Please read it.**
* R1 1(c): that the paper's price offset is more likely too large than too small, inferred from footnote 31.
