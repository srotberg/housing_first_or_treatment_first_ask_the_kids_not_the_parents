# Sweeps: what was found and what was done

Two earlier sweeps are recorded at the bottom under *Round one*. This file is the
running record. Line numbers are `writing/housing_first_children_later.src.tex`.

---

## Round two, 19 August: what is in the paper now

### Applied, in red

| # | What | Where |
|---|---|---|
| 1 | fifty four parameters becomes fifty three | 578 |
| 2 | Value of a statistical life is \$9m in both models | 2085, `tab_eleven` |
| 3 | Stylized means test becomes half of median income, $\kappa_V=0.50$ | 838, `tab_external` |
| 4 | Nothing is called undisciplined any more | 2639 |
| 5 | $\pi_V$ is 0.266 in both models | 839, 974, 1076, `tab_external` |
| 6 | $\nu_2$ is the drug supply curvature, with the elasticity map in the table | 551, 2416, `tab_eleven` |
| 7 | $\rho_m$ cites Meyer et al. (2024) | `tab_eleven`, references |
| 8 | Every NSDUH moment is on the 2024 vintage | throughout |
| 10 | Six unused table files deleted | `writing/tables/` |
| 11 | Thirteen duplications cut, and accepted | throughout |

### Notation, identical across the two models

| object | was | now |
|---|---|---|
| fall in survival with a SUD | $\kappa$ | $\kappa_{\phi d}$ |
| baseline survival | $\phi_0$ | $\bar\phi$ |
| the two rentals | $h_2$, $h_3$ | $\underline h$, $\bar h$ |
| eligibility threshold | $y_V$ | $\kappa_V y^{\text{med}}$, and defined where it first appears |
| SMI prevalence profile | $p_m(j)$ | $s_m(j)$, so it cannot be read as a price beside $p_v$ and $p_r$ |
| the street | $h_1$ | $h_1$, unchanged, it already matched |

Descriptions in the stylized table are now the quantitative table's words for every
parameter both carry: weight on drugs in utility, whether a household uses, SUD hazard
per unit used, dispersion of the fixed draw, weight on housing, service flow of
homelessness.

### The three data findings

**The value of a statistical life was calibrated in the wrong units.** The target was
7.5, the dollar figure in millions, compared against a model quantity that carries the
model's own numeraire. The model produced 1,068 times average labour income on the
first iteration and the block was driving it at 7.5, a tenth of one multiple. The
target is now 80, and the comparison is taken on the ratio to average labour income.

**The 30 percent employment rate given SMI is not an NSDUH number.** The table said
NSDUH 2023. In the 2024 public use file, among adults 26 and over, 58.0 percent of
those with SMI are employed against 57.5 percent of those without, and 45.8 against
47.2 percent full time. There is almost no employment gap on NSDUH's own definition.
The 30 percent is the midpoint of the range for high disability diagnoses in the
clinical literature. The paper now says so. **Open: either the target belongs to a
narrower population than NSDUH's SMI, and the paper should name it, or the target
should be the NSDUH gap.**

**$\rho_m$'s 19.1 percent has a source after all.** Referee 1's comment 2(c)(i) gives
it alongside an employment rate of 40 to 52 percent among the homeless, and that pair
is verbatim the headline of Meyer, Wyse, Meyer, Grunwaldt and Wu (2024): 52 percent of
the sheltered and 40 percent of the unsheltered in formal employment, from the 2010
Census linked to tax records. **Open: the attribution is inferred, not quoted. The
paper is blocked from this machine, so the table number behind the 19.1 needs
checking.**

### New inconsistencies found and fixed

* The drug spending share was 34.7 percent in the stylized footnote and 35 percent in
  the quantitative model and its table. Both now say 35; the data value is 34.7 and
  the appendix records it.
* The homelessness target was 0.40 in the stylized text and 0.399 in the code and in
  the quantitative model. Both now say 0.399, which is what `calibrate.py` targets.

### Repetition

"As it rises" opened 26 parameter entries in Section 5. Nineteen are now varied and
seven keep the original, so the schema is still legible without being a drumbeat. The
variants rotate through *Raise it and*, *When it rises,* and *Increase it and*. Each
change shows the old opener struck and the new one in red.

### Still open, not changed

* **The abstract asserts a result the quantitative model has not yet produced.** "The
  decisive channel is intergenerational... pricing it reverses the ranking" is
  established in the stylized model; Sections 7 and 9 are still a plan and an outline.
  The tense will have to be revisited once the experiments are run.
* **Section 5.2's schema.** One parameter per paragraph, each with a comparative
  static and a moment. Varying the opener is done; the deeper repetition of "the
  private cost rises and the externality rises with it" is inherent to the exercise.
* The two elasticity rows, $\sigma_{\ell}$ and $\nu_2$, still put an elasticity in the
  Data column and a parameter in the Value column. The table note now says so.

---

## Round one, 19 August

Eighteen inconsistencies and ten duplications, listed in the commit at `7507ded`.
All of them are either applied above or recorded as still open.
