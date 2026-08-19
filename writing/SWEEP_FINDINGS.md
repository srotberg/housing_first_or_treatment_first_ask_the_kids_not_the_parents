# Two sweeps: inconsistencies and duplications

Nothing here has been changed. It is a list to decide on. Line numbers are
`writing/housing_first_children_later.src.tex` unless a table file is named.

---

## A. Inconsistencies

### A1. The model has fifty three parameters in two places and fifty four in a third
* line 259: "six state variables and fifty three parameters"
* line 1928: "The model has fifty three parameters"
* line 1952: "Twenty four of the fifty three", and 24 + 29 = 53
* **line 578: "six state variables and fifty four parameters"**

One of these is wrong. The arithmetic in the calibration section says fifty three.

### A2. The two models target different values of a statistical life
* Stylized, line 865: aleph matched to **80 times average annual income, about $9
  million** against a mean household income of $113,000, "the range surveyed by
  Viscusi and Aldy (2003)".
* Quantitative, line 2093: aleph chosen so the model generates **$7.5m**, same
  source in `tab_eleven`.

Same parameter, same paper behind it, two numbers. The stylized note also states the
dollar figure and the multiple; the quantitative one states only the dollar figure.

### A3. The two models use different voucher means tests
* Stylized, `tab_external`: `$y_V$ Voucher means test, multiple of average income =
  **1.00**`.
* Quantitative, line 2548: `$\kappa_V$` set to **half of median income**, 0.50 in
  `tab_standard`.

One is average income at one times, the other median income at a half. That is a
different rule, not a different rounding, and the stylized model is meant to be the
same programme in miniature.

### A4. Voucher generosity is 0.27 in one model and 26.6 percent in the other
* Stylized, line 843: "$\pi_V = 0.27$ is the assisted eligible share in the 2023
  Picture of Subsidized Households".
* Quantitative, line 2172: "the $26.6$ percent ratio of voucher recipients to the
  income eligible population in HUD 2023", and `tab_eleven` gives 26.6%.

Same moment, two roundings, and two different descriptions of the universe.

### A5. Three parameters are called undisciplined and given sources in the same table
* line 2639: "Three parameters remain undisciplined... the treatment effect on
  recovery $g$, the recovery multiplier for SMI $\mu_m$, and the drug supply
  curvature $\nu_2$."
* `tab_eleven` line 32: `$g$ ... Ext. & Odds ratio, Milby et al. (2005) & 1.35`
* `tab_eleven` line 29: `$\mu_m$ ... Ext. & Dual diagnosis relapse, Bradizza et al.
  (2006) & 0.82`
* `tab_eleven` line 47: `$\nu_2$ ... Ext. & Cannabis supply elasticity, Mace et al.
  (2020) & 1.46`

Each of the three has a named source and a number in the table. Either the table is
overstating their discipline or the sentence is understating it.

### A6. nu_2 is called the drug supply elasticity but is the curvature
* `tab_eleven` line 47 and the item label at line 2416 both call `$\nu_2$` "the drug
  supply elasticity".
* line 1863 and line 2639 call it the curvature, with the elasticity as
  $1/(\nu_2-1)$.
* The table then reads Data 1.46, Value 1.68, which is the elasticity against the
  curvature in the same row.

Section 2 says "Mace et al. (2020) estimate a price elasticity of supply of 1.46...
and that is the number the model uses", which reads as though 1.46 is the parameter.

### A7. sigma_ell has the same Data against Value mismatch
`tab_eleven` line 44: `Curvature on leisure & Ext. & Frisch elasticity of $0.5$,
Chetty (2012) & 0.50 & n.a. & 3.00`. The Data cell is an elasticity, the Value cell
the exponent that delivers it. Consistent arithmetic, confusing row.

### A8. rho_m is the only row with no source
`tab_eleven` line 28: `$\rho_m$ & Earnings lost to SMI & Int. & Labour income of the
homeless relative to average & 19.1\%`. Every other row names a dataset or a paper.

### A9. rho_d's source is shorter in the table than in the text
* `tab_eleven` line 17: "Employment rate of the homeless, HUD 2023"
* line 2121: "the employment rate of the homeless, $50$ percent, from HUD's 2023
  point-in-time count **and TEDS-A 2022**"

### A10. Two employment rates of the homeless, both from TEDS-A
* Targeted, line 2121: the employment rate of the homeless, 50 percent.
* Untargeted, validation table: "Working at all, homeless in treatment, 6.6 percent,
  TEDS-A 2022".

Different universes and the appendix says so, but the paper puts 50 and 6.6 next to
each other without a word.

### A11. NSDUH vintages are mixed
2024 for participation, the SUD rate, the drug spending share, the unemployment rate
given a SUD and the omega moment; **2023** for `$\kappa_{uem}$` (`tab_eleven` line
27), `$\bar\tau^{u}$` (line 33) and `$p_m(j)$` (`tab_standard` line 26).

### A12. Guvenen et al. now needs its letter in the table
`tab_standard` line 12 still reads "Guvenen et al.\ (2023)". The text now says 2023a,
since the wealth taxation paper is 2023b.

### A13. Spacing after "et al." in one table cell
`tab_standard` line 31: "Heathcote et al. (2017)" without the `\ ` every other cell
uses, so it sets a wider space.

### A14. h_3 means different things in the two models
* Stylized, `tab_external`: `$h_3$` is the **standard** rental, `$h_2$` the small one,
  and the ladder has three rungs with `$h_1$` the street.
* Quantitative, line 1236: the housing choice is `$\{h_1,h_2,h_3,h_4\}$`, four rungs,
  so `$h_3$` is a **middle** rental.

### A15. tab_external lists the rental ladder in descending order
`$h_3$ Standard rental unit` is listed before `$h_2$ Small rental unit`, against the
ascending order everywhere else.

### A16. theta is set in one model and calibrated in the other
`tab_external`: `$\theta$ Weight on drug use, Set; see the text, 0.20`. In the
quantitative model theta is internally calibrated to a drug spending share of 35
percent. Defensible, but the paper never says why the same parameter is disciplined
in one place and asserted in the other.

### A17. The utility function and the choice vector order the same objects differently
`eq:futil` is `u(c,h',v,n,\tau;d,m)`; `eq:fchoice` is `(n,h',v,\tau,a')`.

### A18. Unused table files carry contradictory numbers
`tables/tab_full_external.tex` and `tables/tab_paper.tex` are not input by the paper
and give `$\nu_2 = 1.50$` with an elasticity of 2, against the live 1.68 and 1.46,
and cite Hansen, Miller and Weber (2018) and Chaloupka (1991), who are in no
reference list. They are a trap for whoever reads the repository next.

---

## B. Duplications

### B1. Verbatim, in two places
"Housing First is better for every household taken one at a time, and worse once one
counts the children of the households it fails to deter." Introduction and
Section 3.6.

### B2. The trial citation list, twice
"(Tsemberis et al., 2004; Padgett et al., 2006; Larimer et al., 2009; Goering et al.,
2014; Aubry et al., 2016)" at line 136 and again at line 330.

### B3. The short trial power argument, three times
Lines 309, 339 and 2731, each a near paraphrase of the others: housing responds
immediately, the disorder slowly, so a short trial is well powered for the first and
not the second.

### B4. The McGovern two to four statement, three times
Introduction, and twice inside Section 2 (lines 181, 400, 424).

### B5. Nilsson's in utero experiment, twice
Introduction and Section 2, both with the twenty four percent.

### B6. Chetty's lower poverty neighbourhood and its 31 percent, three times
Introduction, Section 1.3 and Section 2.

### B7. Bassuk's caretaker percentages, three times
14.2 against 8.3 and 10.3 against 4.4 appear in Section 2, Section 3.6 and the
validation section.

### B8. "a household under Housing First can reproduce its Treatment First outcome
exactly by not using", twice
Introduction and Section 3.5.

### B9. The formula sentences of Section 5.2
* "As it rises..." 23 times
* "Its value is chosen so the model generates..." 5 times
* "It is set externally..." 7 times, "It is calibrated internally..." 5 times
* "the externality rises" or "falls" 10 times

One parameter per paragraph and the same three sentences in each. It reads as a
schema, which may be what is wanted for a parameter list, or may be worth varying.

### B10. "the mass of newborns equals the mass of the dead", twice
Line 1862 in the law of motion and line 1912 in the equilibrium definition.
