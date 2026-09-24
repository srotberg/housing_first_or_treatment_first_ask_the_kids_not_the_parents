# THE COUNTERFACTUAL BINARY DOES NOT READ calibration_state.dat, 24 September 20:50

The internalise arm on the old counterfactual path ran at voucher probability
0.06, the declaration, while its own benchmark ran at 0.067533863251354. The
benchmark binary's calibrating_model calls read_calibration_state (46981);
long_run_counter_factual never does. Anything the benchmark takes from
calibration_state.dat and the handover does not carry silently reverts to its
declaration in the arm. Of the 115 handover keys, 16 were missing from the arm's
handover. probability_of_voucher_benchmark_used was the only one that is also
held in calibration_state.dat with a non-declared value. rho_intergenerational,
b_smi_multiple and zeta_DI are in neither, so both stages use their
declarations. The printed-value diff of bench.log against cf.log shows no other
parameter moving. size_of_smallest_house_hhld_can_buy does drop 0.01 in
upload_vars, but it is inert: only smallest_index_for_purchase = 2 is used.

In a no-budget-clearing arm this is an 11 per cent cut in voucher offers hidden
inside the experiment. h_1 went +2.87 per cent where the fixed-price run had
-2.45 per cent. Treatment First is not affected at convergence, because pi_V is
its budget instrument (53184).

THE RULE: before trusting an arm, diff every parameter bench.log prints against
cf.log's first pass. Policy switches and prices are the only lines that should
differ. remote_cf_arm.sh now sets the value from the benchmark's own log and
prints VOUCHER CHECK PASS or GUARD FAIL after the run.

# A SOLVED BENCHMARK IS KEPT WITH EVERY FILE THE COUNTERFACTUAL BINARY READS, 24 September 19:05

The HF omega_c = 0.06 benchmark was solved, but only its welfare curve,
distributions and handover were kept (results/reference/hf_omega_c_006/). The
counterfactual binary's upload_vars (40697 on) and the stationary-distribution
and benefits reads (32062, 39388, 39524) open about fifteen files named
<stem>baseline_benchmark.dat from the working directory: net_govt_revenues,
govt_revenues_to_use_in_tests, model_ss_benefits, rent, model_total_hours,
model_labor_supply, income_cutoffs_of_quintiles, median_income,
average_labor_income*, average_welfare_of_youngest_cohort,
welfare_by_addiction_youngest, distribution_stationary*, the drug supply
shifter and the welfare curve. None were kept, so all three counterfactuals had
to re-solve the benchmark first, costing one to three hours each. The author:
*"I thought it was done"*.

THE RULE: when a benchmark that counterfactuals will run against is solved,
keep every *baseline_benchmark.dat file its directory holds (gzipped if large)
beside RESULT.md, so an arm can start from it without a re-solve.

# EVERY GENERAL-EQUILIBRIUM CHANNEL OF A COUNTERFACTUAL IS CHECKED AGAINST THE OLD ARMS BEFORE IT RUNS, 24 September 16:35

Last night's counterfactuals -- the omega_c scan points, omega_c = 1,
internalisation, and three Treatment First runs -- were all solved on the frozen
scan path, which is the BENCHMARK binary. On that binary clear_drug_market
normalises the price to 1 every block, so drug_supply_elasticity 1.46 did
nothing. The old arms (19 September) ran the counterfactual binary, where the
price clears; arm 3's fell to 0.842. The author had to point it out: *"im
surprised that i had to tell you how to run the elasticity of drug supply
because in the old experiments that is how we did it"*. The source said so in
plain words (the comment at 46755), and the check was never made.

THE RULE: before any counterfactual runs, compare it channel by channel with
how the old arms ran -- drug market, taxes and budget, rental market, voucher
rules -- and check each against the branch the binary actually takes. A switch
being SET in the handover proves nothing; drug_supply_elasticity was set to
1.46 in every run.

THE GUARD: remote_tf_rationed.sh, remote_tf_point.sh and
remote_internalise_point.sh now refuse to run unless ALLOW_PEGGED_PRICE=1.
Counterfactuals go through remote_cf_clearing.sh. remote_scan_point.sh is left
alone: a BENCHMARK should normalise its own price.

THE TAX IS NOT THE SAME KIND OF MISS. adjust_taxes is 0 and labour income taxes
were removed on the author's instruction of 12 September ("we also dont need
labor income taxes"). The source records the unfunded residual as "the
experiment, not a bug" (line 333). The note's introduction still says the tax
rate responds, so that sentence may be stale -- the author's to decide.

