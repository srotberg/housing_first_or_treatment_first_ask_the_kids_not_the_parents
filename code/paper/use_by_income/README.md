# The benchmark's drug use by income (Section 5.3, Block 2, Figure fig:usebyincome)

The author, 26 October: *"So for each income to average income showing the use rate. Data and model"*, then *"This is
fantastic and should be in the validation"*.

The model has no correct by-income output of its own: `model_drug_use_by_income_quintile` reads
`income_cutoffs_of_quintiles`, which is never set, so every household lands in the top fifth. Instead,
`patch_useinc.py` adds a print-only block to `govt_revenues_calc`: every household's mass and interest-inclusive income
(`income_2`, the concept of the y_u numerator) in 400 bins of width 0.025 from -1, and the users under the y_u guard,
character for character, printed as `DIAG USEINC` once per call at `time_period == 1`. Nothing the run computes reads
these arrays.

How the 26 October run was made:

1. the source: the `cf_fix2_share_treatCu` counterfactual build (as `code/transition_2c/cf_arm_tr2c_Cu.sh` builds it),
   already carrying the print-only delta_h band diagnostic of the odds-ratio check;
2. `python3 patch_useinc.py cf.f90 cf_useinc.f90`, then
   `gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf_useinc.f90 -o hftf_cf`;
3. the null arm staged as `cf_arm_tr2c_Cu.sh` stages it (`BENCH_FROM=results/reference/hf_2c_omega_0.085`,
   `SEED_FROM=bench`), with `results/decomp_2c_shares_Cu/arm_tf/null/PARAM_HANDOVER.arm.txt` verbatim except
   `drug_price_start 0.99934793452138859` (the price its last pass was solved at) and `drug_market_adjuster 0`;
4. `python3 code/paper/use_by_income_figure.py --from-log <run>/cf.log` copies the last block to
   `results/use_by_income/benchmark_useinc.txt` and draws `writing/figures/use_by_income.pdf`.

The run's passes agree to within half a point in every band (pass 1: 17.6, 13.2, 5.4, 5.8, 5.9, 6.2, 4.2 percent;
pass 2: 18.2, 12.8, 5.8, 6.1, 5.9, 6.3, 4.2), and the users' income over the mean is 0.628 in both, against the
benchmark's 0.62 in Table 5.
