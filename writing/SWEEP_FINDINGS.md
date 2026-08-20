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

## Round three, 19 August: the audit

Asked whether everything from the earlier messages had actually been applied. It had
not. What follows was checked in the file rather than asserted, and six things were
found still outstanding.

### Found outstanding and now fixed

| what | where it was wrong |
|---|---|
| $\rho_m$'s Moment cell wrapped onto a second line | `tab_eleven`, shortened to "Income over average, homeless, Meyer et al. (2024)" |
| $\nu_2$'s Moment cell wrapped onto a second line | `tab_eleven`, the formula moved into the table note where it already appears |
| Guvenen et al.\ (2023) without its letter | `tab_standard`, now 2023a, matching the text |
| Heathcote et al. (2017) missing the thin space after "al." | `tab_standard` |
| $\phi_0$ survived in the welfare criterion's closed form | line 2687, now $\bar\phi$ |
| a bare $\kappa$ survived in the channel decomposition | line 908, now $\kappa_{\phi d}$ |

### Checked and correct

* Every one of the twenty three data targets in Tables 5 and 6 matches the constant of
  the same name in `housing_first_or_treatment_first_SR_v1.f90` exactly, including the
  two that are written as arithmetic there: $\omega$'s 18.3 percent is `1/0.845 - 1`
  and $\mu_H$'s 1.473 is `6.60/4.48`.
* No `NSDUH 2023` survives anywhere in the text or in either live table.
* No `y_V` and no `\phi_0` survive anywhere in the paper.
* The five annotations on the page proofs are each in the file.

### Not needed after all

A footnote saying which statistics are only available for 2023. There are none: the
SMI prevalence profile was the last one and the 2024 public use file carries it through
the `AGE3` recode.

### Still open

* The internal stylized table is stale until the recalibration lands. Its descriptions
  are already corrected in `tables.py`; the file on disk is regenerated with the new
  numbers.
* The abstract asserts a result the quantitative model has not yet produced.
* $\rho_m$'s attribution to Meyer et al. (2024) is inferred from the referee's
  matching employment pair, not quoted. The table number still needs checking.

---

## Round one, 19 August

Eighteen inconsistencies and ten duplications, listed in the commit at `7507ded`.
All of them are either applied above or recorded as still open.

---

# Round four: the table sweep, 20 August

Every table the paper actually inputs was read cell by cell against the text
and against the code. Six tables are in use: `tab_external` and `tab_internal`
for the stylized model, `tab_eleven` and `tab_standard` for the quantitative
one, and `tab_welfare` and `tab_children` for the results. Nothing else in
`writing/tables/` is reachable from the paper.

## Targets: every one checks out

All twenty three target values in Tables 5 and 6 were matched to the Fortran
constant that carries them. Every one agrees, including the three that are
arithmetic rather than literals:

    mu_H          1.473    = milby_recovery_ratio_data = 6.60/4.48
    omega         18.3%    = child_use_gap_data = 1/0.845 - 1
    nu_2          1.68     = drug_supply_curvature = 1 + 1/1.46

and the external values behind the standard table: `replacement_rate_ui` 0.5,
`threshold_income_vouchers` 0.5, `rent_to_income_ratio_vouchers` 0.3,
`investment_income_tax` 0.15, `curvature_of_labor_income_taxes` 0.85,
`housing_status_grid_expander` 1.8, `max_age_to_choose_addiction` 55,
`leisure_curvature` 3, `kappa_phi_m` 2.50. The rental ladder's two ACS
shares, 13.2 and 62.7 per cent, are the first and third entries of the
housing distribution array at line 812.

## Descriptions: nine were not aligned, and now are

The same parameter appeared in two tables under two different descriptions.
Each pair is now the wording the paper's own `\item` heading uses.

| symbol | was, quantitative | was, stylized | now |
|---|---|---|---|
| `\gamma` | CD weight on housing | Weight on housing | Weight on housing services |
| `\sigma_y` | Dispersion of the fixed draw | Dispersion of the fixed draw | Dispersion of productivity |
| `\psi` | UI replacement rate | Replacement rate while unemployed | Replacement rate while unemployed |
| `\bar y` | Cap on insurance earnings | Cap on the earnings base, multiple of average income | the longer form, in both |
| `\kappa_V` | Voucher eligibility cutoff | Voucher means test, share of median income | the longer form, in both |
| `\kappa_r` | Tenant contribution rate | Tenant's share of the rent when covered | the longer form, in both |
| `\pi_V` | Voucher lottery probability | Voucher generosity in the baseline | Chance of drawing a voucher |
| `p_v` | Price of drugs | Price of a unit of drugs | Price of a unit of drugs |
| `\kappa_{ueH}` | Employment multiplier, homeless | — | Employment lost to homelessness |

`CD` was an undefined abbreviation for Cobb-Douglas sitting in a table column.

## Notation: the bars are gone

`\underline h` and `\bar h` are replaced by numbered rungs everywhere, in both
models, in the text and in both parameter tables. The stylized model's ladder
is `h_1 < h_2 < h_3`; the quantitative model's is `h_1 < h_2 < h_3 < h_4`, and
the two parameters that are set are `h_2`, the smallest rental size, and `h_4`,
the largest.

## Rounding

`tab_internal` printed the bottom half's earnings share as 17.20 per cent and
the housing share as 26.80, against 17.2 and 26.8 in `tab_standard`. Both now
print to one decimal. The homelessness target printed 0.40 against 0.399 in the
text and in `tab_eleven`; the generator already carried three decimals and the
file on disk was simply stale.

## Two things left alone, deliberately

**`avg_rent_to_income_data` is misnamed, not miscalibrated.** The constant is
0.268 and the tables call it housing over expenditure net of drugs, which is
what the paper says and what the stylized model targets. The Fortran name says
rent to income. The comment immediately below the declaration already corrects
the name and explains why the moment is an expenditure share: a Cobb-Douglas
weight equals the expenditure share exactly, and income and expenditure differ
by saving. Renaming it means recompiling, and a calibration is running.

**`\aleph` reports different units in the two tables.** `tab_internal` gives
the value of a statistical life as 80 annual incomes and `tab_eleven` gives it
as \$9m from Viscusi and Aldy (2003). These are the same target: the Fortran
constant is `vsl_data=80`, and at an average household labour income near
\$112,000 the two coincide. Each table quotes it in the units its own model
works in, which is the same convention the note to Table 5 already sets out for
`\sigma_\ell` and `\nu_2`.

## Stale by construction

`tab_internal`, `tab_welfare` and `tab_children` are stylized model output and
every number in them is regenerated by `tables.py` after a calibration. They
are stale now and will be correct after the recalibration lands. `tab_external`
is also generated: it currently prints the standard rental unit as 0.44 of mean
income, because the old grid's mean was 0.909 rather than one. With the pooled
grid the mean is exactly one, so it will print 0.40, and the text's "0.41 of
mean income" has to move with it.
