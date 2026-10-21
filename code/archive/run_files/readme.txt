This file shows you how to run the simulations in "Housing First or Treatment First? Ask the Kids, Not the Parents", by Shahar Rotberg.

Before running each simulation you will have to run the following commands:

Write the command in the line below and press enter:
gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp -O2 -ffree-line-length-none -o housing_first_or_treatment_first

(-ffree-line-length-none is REQUIRED, not optional. Free form Fortran truncates at column
132 and gfortran makes that an error, and the source has 97 lines past it, most of them
predating this revision. Without the flag the build stops with a syntax error inside a
truncated line, which reads as a code error and is not one.

The old line used -g and no -O flag, so gfortran defaulted to -O0. Measured on a 4-core
machine, -O0 and -O3 reached the same point in the same wall time, so this is not where the
run time goes -- but -O2 costs nothing and is the sane default. Drop -march=native unless
you compile on the same machine you run on.

Thread count is now taken from the runtime rather than hardcoded: max_CPUs remains a
compile-time parameter because it dimensions vector_cpu_real, but it is used only as an
upper bound. Set OMP_NUM_THREADS to control the actual thread count; with nothing set the
behaviour is unchanged.)

Write the command in the line below and press enter:
./housing_first_or_treatment_first

At the very top of the Fortran code there is a module titled "Global_Vars". At the top of this module you will see six variables, which we describe below how to set for each simulation.

For generating the benchmark, please set:

		is_counterfactual=0
        partial_equilibrium=0
        probability_of_voucher_benchmark_used=0.06
        increased_prob_of_voucher_if_homeless_and_addicted=1
        how_many_iterations_to_do_on_distribution=0
		compare_to_original_benchmark=1

Experiments 1, 2, 3, and 4

1. For Experiment 1, please set:
	
	a. GE (LR)

		is_counterfactual=1
        partial_equilibrium=0
        probability_of_voucher_benchmark_used=0.06
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=0
		compare_to_original_benchmark=1

	b. PE (1)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=0.06
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=1
		compare_to_original_benchmark=1

	c. PE (5)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=0.06
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=5
		compare_to_original_benchmark=1

	d. PE (LR)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=0.06
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=100
		compare_to_original_benchmark=1

2. Experiment 2:

	a. GE (LR)

		is_counterfactual=1
        partial_equilibrium=0
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=1
        how_many_iterations_to_do_on_distribution=0
		compare_to_original_benchmark=1

	b. PE (1)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=1
        how_many_iterations_to_do_on_distribution=1
		compare_to_original_benchmark=1

	c. PE (5)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=1
        how_many_iterations_to_do_on_distribution=5
		compare_to_original_benchmark=1

	d. PE (LR)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=1
        how_many_iterations_to_do_on_distribution=100
		compare_to_original_benchmark=1

3. Experiment 3:
	
	a. GE (LR)

		is_counterfactual=1
        partial_equilibrium=0
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=0
		compare_to_original_benchmark=0

	b. PE (1)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=1
		compare_to_original_benchmark=0

	c. PE (5)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=5
		compare_to_original_benchmark=0

	d. PE (LR)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=100
		compare_to_original_benchmark=0

4. Experiment 4:

	a. GE (LR)

		is_counterfactual=1
        partial_equilibrium=0
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=0
		compare_to_original_benchmark=1	

	b. PE (1)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=1
		compare_to_original_benchmark=1

	c. PE (5)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=5
		compare_to_original_benchmark=1

	d. PE (LR)

		is_counterfactual=1
        partial_equilibrium=1
        probability_of_voucher_benchmark_used=1
        increased_prob_of_voucher_if_homeless_and_addicted=0
        how_many_iterations_to_do_on_distribution=100
		compare_to_original_benchmark=1


	


	
