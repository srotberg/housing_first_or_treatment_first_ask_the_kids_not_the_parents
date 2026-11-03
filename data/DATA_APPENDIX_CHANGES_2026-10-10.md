# Data appendix: what changed on 10 October 2026

The author asked for `data/DATA_APPENDIX.md` to be brought fully up to date with the paper. Only the appendix and
this file were changed: no number, parameter, script, table or paper text was touched. Every value written into
the appendix was read from the filled paper, the generated JSON (`code/paper/*.json`, `code/stylized/*.json`), the
Fortran declarations, the run outputs the export scripts read, or the data scripts. Two scripts were re-run in the
scratchpad, writing their JSON there and not into the repository, and both reproduced the committed values:
`make_altruism_moment_loneparent.py` (17.48 percent) and `make_children_with_sud_parent.py` (4.6 percent).

Table numbers follow the paper as it stands: Tables 1 and 2 are the stylized model's, Table 3 the twenty-five
parameters (`tab_eleven`), Table 4 the untargeted moments (`tab_untargeted`), Table 5 the long run (`tab_longrun`) and
Table A1 the standard parameters (`tab_standard`). The task's brief called the validation table "Table 6". That is
the old numbering, and the appendix uses the paper's.

## What changed, block by block

**Header.** The structure now follows the paper: Blocks 1 to 6 are Section 5.1 and Table 3, Blocks 7 to 13 are
Appendix A and Table A1, Part II is Section 6, and Part III is Section 5.2 and Table 4. The header points to the `c_*`
exports, lists the roundings the prose applies (θ 0.17, π_V 0.068, the SSI floor 0.18) and says that
`params_numbers.json` is stale.

**Part I.**
- Block 1: θ's printed rounding. b now names the CSV it is written to and gives the 18 percent uplift with its JSON
  names (10.50 and 4.34 targets, 10.54 with the weight off, a 15.0 percent fall). κ_φd's literature range is cut to
  the two studies the paper cites (Plana-Ripoll 3.91, Heiberg 6.6); Walker and Degenhardt are dropped. The miss of
  62 against 74 is now stated. ℵ names the source of the 113,000 dollars (CPS ASEC, `gradient.py`) and the VSL
  income elasticities in the footnote (`lit_numbers.py`).
- Block 2: h₁ is 53 percent of h₂ (`c_h1_of_h2_pc`). π_V's printed 0.068 and `voucher_coverage_data`.
- Block 3: ι is now bracketed by Hjorthøj et al. (2018), 1.34, and Nielsen et al. (2017), 6.04, as the paper does.
  λ_m's declaration (0.067) is given beside the 0.066 printed.
- Block 5: **ω_c rewritten.** The target is 17.5 percent (0.1748): unmarried adults in two-person households with
  no child against lone parents with one child. Data are NSDUH 2024, 26 and over, past-year use (`ILLYR`), with lone
  parents reweighted to the other group's age × sex × marital status × family income cells (n = 573 and 3,698;
  cover 70 percent; 34.2 against 40.2 percent). The entry gives the model moment, the past-month (19.5) and disorder
  (59.3) alternatives and why neither is used. **κ_x removed** from the block (now Part VI); the Section 2 footnote
  that still cites Loubière is noted.
- Block 6: why cannabis (no direct estimate for an illicit drug).
- Block 9: ρ_z renamed ρ_y as in the paper. Grid-node names. UI wording as in Table A1.
- Blocks 11 to 13: "in line with Heathcote et al." for φ. The SSI floor's printed 0.18. The bend points' Fortran
  values. J_E's footnote.

**Part II** (rewritten; was the three screen parameters only).
- The screen: p_det 85 percent and no false positives, read from the arm's handover (the Fortran declares 0.95 and
  0.005). Detection evidence is 92.5 to 100 percent. ψ_x is 1/3. c_test is 0.00049461 against average labour income
  1.5898, 0.031 percent, and 35 dollars at 112,500 dollars per unit.
- A table of the seven columns of Table 5: what clears in each, and the run directory each is read from. The two
  runs now in footnotes are also covered: price-clears-only (moved out of the table on 9 to 10 October) and the
  no-externality run with both clearing (0.39).
- The welfare criterion: ex-ante newborn, childhood included at weight one, each policy's own newborn distribution,
  and the CEV on non-housing, non-drug consumption.
- The transition: its provisional status.

**Part III.**
- Table 4 and Section 5.2 references replace "Table 6". The prose's 27.2 and 25.9 for the homeless by age are added.
- The drug-death note is updated (the paper no longer names a year).
- Renter burden: `renter_burden_30_data` added.
- New entries:
  - Children living with a parent who has a SUD: 4.6 percent, `make_children_with_sud_parent.py`.
  - Block 7, losing a voucher: Costantini (2025), 4.6 points, against the model's 3.6 (`export_revoked.py`,
    `results/revoked_2c_street`).
  - Block 8, deterrence: Mehay and Pacula (1999), 1 − (13.2/48.5)/(32.0/45.8) = 61 percent (`lit_numbers.py`),
    against the model's 59 percent of users without a SUD, a 67 percent SUD share and 19 percent overall
    (`export_whostops.py`, `results/whostops_2c`).
  - Other data the text quotes: HUD PiT 2024 total of 771,480, checked against the workbook. NSFG 75 against 81
    percent. NSDUH 40 against 48 percent children at home.
- Flatau and Cobb-Clark are now marked as appendix-only.

**Part IV** (rewritten for `gradient.py` as Section 3 now states it).
- Saving, food assistance, and no UI or housing.
- φ̄ comes from Arias via the Fortran. σ_y is pinned by Φ(−σ_y) = 0.172.
- The truncation at y_min = 0.24 is documented. The paper does not state it. It cuts 20.1 percent of the
  distribution, the model's bottom half holds 21.5 percent, and the value of being alive is zero at about 0.17. Users
  sit in one band at 0.68 to 0.81.
- π_d is 0.0368/0.08901. u₁ prints as 0.16. c̄ is 0.098 and prints as 0.10.
- The five internal parameters and their sources.
- The log-utility footnote's runs. The older staged-model numbers behind the "version with housing" footnote.

**Part V.**
- g is marked resolved.
- 113,000 is now partly sourced: CPS ASEC, year unknown.
- The progressivity item is reworded.
- Added: the 70 percent and elastic-supply robustness, and Mehay and Pacula not being in `related_lit/`.

**Part VI.** Added:
- the old ω_c target (parents against non-parents, 18.3 percent, `make_altruism_moment.py`);
- κ_x;
- ι's old sources;
- κ_φd's dropped citations;
- the Table 5 column moved to a footnote;
- the stylized model's old use of y_min as income out of work.

## Numbers in the paper I could not trace to a source or script in the package

- **"with a detection rate of 70 percent"** (`writing/housing_first_children_later.src.tex:869`, footnote). It is
  typed. The only runs are on the earlier benchmark (`results/counterfactuals_cf_fix2/tf70_cycle`,
  `tf70_damp_partial`, `tf70_remote_*`), and whether they converged is not recorded. The same footnote's
  "more elastic supply" rests on `elast5_85`, which is also from the earlier benchmark.
- **Literature values typed in the prose, with no file in the package to check them against:**
  - ι's 1.34 (Hjorthøj et al., 2018) and 6.04 (Nielsen et al., 2017) (`src.tex:802`);
  - κ_φd's 3.91 and 6.6 (`src.tex:785`);
  - "more than a third of removals" (AFCARS);
  - Altonji's "thirteen cents";
  - 92.5 and 100 percent for the screens (also hard-coded in `export_results.py`).

  They are quoted correctly as far as the appendix's earlier entries go, but nothing in the package regenerates
  them.
- **771,480** (`src.tex:185`) is typed rather than generated. It does match the HUD PiT 2024 workbook.
- **The 113,000-dollar mean household income** (CPS ASEC, year unknown) and the 9 million VSL are constants in
  `gradient.py`, not data in the package.
- The five open items carried over from before: the h₁ ceiling, π_V's denominator, the SNAP year, the SMI share's
  diagnoses, and Meyer et al.'s table. See Part V.

## Inconsistencies between the paper, the code and the data

1. **The log-utility footnote against its own runs.** `src.tex:289` says "All the qualitative results of this section
   hold with log utility as well". `results/referee_item7/LOG_UTILITY.md` and
   `results/referee_item7/log_utility/figure1_scans_main_session.txt` show four things under log:
   - users form two bands (the bottom 8.44 percent and the top 0.46 percent), not one;
   - κ_φd = 11.95 lies outside the cited 3.91 to 6.6;
   - the mortality channel alone leaves users at the top (3.51) up to its calibrated strength;
   - the unemployment channel without saving never reverses the gradient. The write-up's own words are "the paper's
     no-saving demonstration does not survive log".
2. **The welfare computation against the stated criterion.** The paper's own `\upd` note (`src.tex:895`) says every
   CEV is still computed with the child at home for the full J_K years, without the parent's death that equation
   (eq:newbornw) states. The fix is in the Fortran's `calculate_childhood_utility` and `childhood_comparison`, and in
   `cohort_cev.py`.
3. **Drug deaths, 25 to 44.** Table 4 and the prose print 20.0. That value is typed in the Fortran as
   `observed=0.20d0` (`code/housing_first_or_treatment_first_SR_v1.f90:11757`). The CDC WONDER 2024 export in the
   package gives 20.8 (`data/make_overdose.py`).
4. **ι's sources.** The Fortran comment (`f90:2150-2152`) still says 1.34 for any SUD and 2.74 for opioid use
   disorder, while the paper says Hjorthøj et al. (2018) 1.34 and Nielsen et al. (2017) 6.04.
5. **λ_m.** It is declared as 0.067 (`f90:2141`), but Table 3 and the prose print 0.066, the value the benchmark
   carries. 0.066 implies 49.5 percent recovered within ten years, not the 50 percent the item states.
6. **The screen's parameters.** The declarations (`f90:487-488`) say `probability_of_detection = 0.95` and
   `probability_of_false_positive = 0.005`. The experiment ran at 0.85 and 0 through the arm's handover. The paper is
   right; the declarations are not what was run.
7. **Stale exports.**
   - `code/paper/fortran_numbers.json:306` has `f_child_use_gap_data = 0.183432`, against the declaration's 0.1748
     (`f90:887`).
   - `code/paper/params_numbers.json` still carries old targets (`q_omega_c` 18.3, `q_g` 1.35, `q_kappa_x` 0.002 and
     others). The paper quotes neither file for these, but `writing/NUMBERS.md:13,114` still describes `@@q_*@@` as
     the route, and calls the calibration tables "Tables 5 and 6".
8. **Stale docstrings.**
   - `data/make_altruism_moment_loneparent.py:3` and `:60` describe past-month use as what the paper quotes; the
     identifying moment is past-year use (`:72-83`).
   - `code/stylized/gradient.py:17` and `:126` say a household out of work lives on y_min. The code (`W`) gives it
     savings plus c̄, as the paper says.
   - `code/paper/export_longrun.py:10` says "Four steady states"; the table has seven columns.
9. **Children with a SUD parent.** The 4.6 percent the paper quotes is the "either parent" figure, with the
   respondent's spouse imputed independently. The script itself calls it an upper bound if partners' disorders go
   together. The surveyed parent alone gives 3.2 percent (`code/paper/nsduh_kids_sud.json`).
10. **The military's testing rate.** The paper says the military tested "10 to 20 percent of a unit every month"
    (`src.tex:224`). `data/lit_numbers.py:11` records that this was the requirement for Navy and Marine Corps
    commanders (Mehay and Pacula, p. 6), and notes that the Army tested less.
11. **Table 5, sixth column.** Three welfare rows print `\tocheck{--}` (`writing/tables/tab_longrun.tex:30-32`).
12. **The transition.** The text says seventy years (`\tocheck`, `src.tex:969`), while the numbers come from the
    sixty-year run's loop 0, as the paper's own note says.
13. **κ_φd misses its target** by twelve points (62 against 74). This is already visible in Table 3; it is listed
    here because the paper calls the parameter "calibrated to the average income of users".

---

## Second pass (10 October, later)

The author: "Just finish the data appendix". Only `data/DATA_APPENDIX.md` and this file were changed: no paper text,
code, JSON or data script was touched. Sources were the repository and its full git history, unshallowed for this
pass. That history includes the paper's first draft, LaTeX added in commit dc5b53f8 on 14 August, with its
bibliography, and the referee reports in `HF_or_TF_RED_reviews` (a separate private repository). Web searches were also used, accessed 10 October 2026. From
this environment the web could be searched but no page could be fetched (bls.gov, census.gov, nber.org and PMC all
refused), so a value that only lives inside a PDF table could not be read, and the appendix says so wherever that
mattered.

### Closed, and moved into their blocks

- **h₁'s ceiling (Part I, Block 2).** Burt, Aron and Lee (2001) report the 1996 NSHAPC estimate: at least 2.3 million
  adults and children, "nearly 1 percent of the U.S. population", likely to be homeless at least once in a year, and
  perhaps 3.5 million. Sources: https://webarchive.urban.org/publications/900050.html and
  https://webarchive.urban.org/publications/900302.html. It is a share of **people**, all ages, in 1996. The band's
  floor is a share of households in 2023.
- **π_V's 26.6 percent (Block 2).** It is not from the Picture of Subsidized Households. It is HUD's *Worst Case Housing
  Needs: 2023 Report to Congress*, on the 2021 AHS: 5.14 million of 19.3 million very low-income renter households
  received federal rental assistance of any kind, and 5.14/19.3 = 26.6. The construction is from the first draft
  (dc5b53f8), and 0.266 has been in the Fortran since 0d5e4bcf (16 August). The 19.3 million is confirmed at
  https://housingmatters.urban.org/research-summary/worst-case-housing-needs-reach-new-high. The 5.14 million could
  not be read from the report itself.
- **SNAP over output, 0.42 percent (Block 2).** Fiscal year 2023, 113 billion dollars against GDP of "about 27.0
  trillion", 113/27,000 = 0.42 (first draft, dc5b53f8, citing ERS and BEA). ERS gives FY 2023 federal SNAP spending as
  112.8 billion (https://www.ers.usda.gov/data-products/charts-of-note/109300). The Fortran comment's 27.7 trillion is
  calendar-year GDP and gives 0.41, the discrepancy the first pass found.
- **The 25 percent SMI share of the homeless (Block 3).** Gutwinski et al. (2021): schizophrenia spectrum 12.4 percent
  plus major depression 12.6 percent gives 25.0. This is recorded in commits 29b4400d and 36688011 (14 August) and
  confirmed by search against https://journals.plos.org/plosmedicine/article?id=10.1371%2Fjournal.pmed.1003750.
  Bipolar disorder is not included, and summing the two treats them as disjoint.
- **φ = 0.85 (Block 11).** It is not attributed to a single study. The first draft said "based on estimates from"
  Heathcote et al. (2017). The author said "many papers use 0.85" (`CALIBRATION_STATE.md`, r206 and r207). The 2014
  AER's 0.845 is not a tax parameter.
- **ϖ(y)'s BLS table (Block 9).** CPS annual averages 2019, Table 7 (https://www.bls.gov/cps/aa2019/cpsaat07.pdf).
  The appendix now gives the eight values the Fortran carries. The 5.4 percent is confirmed at
  https://www.bls.gov/careeroutlook/2020/data-on-display/education-pays.htm.
- **Wealth over output (Block 7).** There is no BEA extract to name. The 3 is a round figure: the Fortran comment calls
  all private fixed assets "roughly three" years of GDP, the author reset it on 2 September, and the first draft set it
  "as in" Guvenen et al. (2023). The appendix now says so instead of implying a computed ratio.
- **McDaniel (2007) (Block 11).** The full title and series years (1950–2003) are now given. The target has been 22.4
  since the first draft.
- **Meyer et al. (2024), 19.1 percent (Part III, Block 1).** It is traced to the submitted paper's untargeted-moments
  table ("0.191 × avg. income") and to Referee 1's comment 2(c)(i), which quotes it. Its table in the working paper is
  still open (below).
- **The 70 percent robustness (Part II, Part V).** The first pass said whether those runs converged was not recorded.
  It is recorded: the `NOTE.md` in each run directory says **none of the four 70 percent runs converged**.
  - `tf70_cycle` ended in a two-pass cycle.
  - `tf70_damp_partial` was lost at pass 7.
  - `tf70_remote_damp_cycle` stopped at pass 12 when the cycle returned.
  - `tf70_remote_partial` behaved the same way to pass 8.

  On every pass drug use is 28 to 29 percent below Housing First and the newborn CEV is +1.43 to +1.76 percent. So the
  footnote's sign holds pass by pass, but there is no equilibrium behind "the qualitative results hold". `elast5_85`
  converged (CEV +2.77). All of these runs are on the earlier benchmark.
- **The transition (Part II).** The paper's numbers now come from the T = 60 run's loop 1_r5
  (`results/transition_2c/loop1_r5`, 9 October 21:51). It has converged: budget residual median 9.3 × 10⁻⁴ and drug
  gap median 0.08 percent. The T = 70 run (`results/transition_2c_t70`) is in progress and will replace it. This
  supersedes item 12 of the first pass's list, which described loop 0.

### Still open (Part V)

1. The year and table of the 113,000-dollar CPS ASEC mean household income. It is not in the repository or its
   history, and the Census tables could not be read.
2. The BEA table behind GDP of 27.0 trillion in the SNAP target.
3. The table of Meyer et al. (2024) behind 19.1 percent.
4. Which year or years of McDaniel (2007) give 22.4 percent.
5. The BLS 2019 shares and the three rates other than 5.4, which are unchecked against the table.
6. The 5.14 million assisted renters, read from the first draft, not from the HUD report.
7. The 70 percent and elastic-supply robustness, which has only earlier-benchmark runs, none of them converged at
   70 percent.
8. Mehay and Pacula (1999), which is not in `related_lit/`.

### New inconsistencies between the paper and its sources (not fixed; the paper was not to be edited)

14. **π_V's source.** Table 3 ("Recipients over eligible, HUD 2023") and the π_V item ("the 26.6 percent in HUD's
    Picture of Subsidized Households (PSH), 2023") attribute 26.6 percent to the PSH. It is the *Worst Case Housing
    Needs 2023* ratio, which covers all federal rental assistance among very low-income renters in 2021, not
    vouchers. The PSH tenant-based row would need a denominator of 7.4 million to give 26.6.
15. **SNAP's denominator.** 0.42 percent rests on GDP of 27.0 trillion. Calendar-2023 GDP, as the Fortran comment has
    it, gives 0.41.
16. **The 70 percent footnote** says the qualitative results hold. No 70 percent run converged, even on the earlier
    benchmark (above).
17. **h₁'s band** mixes a household floor (2023) with a person ceiling (1996).
