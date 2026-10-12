#!/usr/bin/env python3
"""patch_sp.py SRC OUT -- THE BOTH-PENALTIES STATE IN LESS MEMORY (12 October). The author, on the both-penalties run
dying three times in the benchmark's first block: "do 1 and 2 together" -- single-precision value functions, and
checkpoints (the second is remote_deltah_both_sp.sh's).

WHERE THE MEMORY WENT. The four-class state is about 66 million cells per renter array, 0.53 GB in double precision.
The backward pass holds the value function and the nine real policies (5.3 GB) and the seven integer policies (1.9 GB):
the 7.1 GiB the run logged then. The distribution stage adds six distributions and a private copy per thread (5.3 GB),
and the statistics stage the benchmark copies (8 real, 5 integer: 5.5 GB), which put the run at 13.3 GiB of memory and
9.3 GiB of swap on a 15 GiB machine, where it spent hours in the statistics stage and was killed there twice.

WHAT CHANGES. The value function, the real policies and their benchmark copies are stored in single precision, the
integer policies and their copies in two bytes. The DISTRIBUTIONS STAY DOUBLE (distribution_guess, _implied,
_stationary, _forward, the two Aitken buffers, the per-thread copies, distribution_stationary_benchmark and _to_fetch):
they are summed over 66 million cells, where single precision would lose mass. Every computation still runs in double;
only what is stored between ages and between stages is narrowed, and the component names are kept, so no line that
reads or writes them changes. The value function holds about seven digits, against values near 1300, so a stored value
is good to 1e-4 utils, far finer than the welfare differences read from it.

Refuses unless each anchor is found exactly once."""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old[:140])
    s = s.replace(old, new)


# the narrow types, beside the double ones; the component names are the double ones' so every access is unchanged
rep("""        type :: jagged_matrix_transition_integer
            integer, dimension(:,:,:,:,:,:,:), allocatable  :: vector_transition_integer
        end type jagged_matrix_transition_integer
""", """        type :: jagged_matrix_transition_integer
            integer, dimension(:,:,:,:,:,:,:), allocatable  :: vector_transition_integer
        end type jagged_matrix_transition_integer

        ! SINGLE PRECISION AND TWO-BYTE STORAGE (patch_sp.py): the value function and the policies, not the distributions
        type :: jagged_matrix_transition_real4
            real(4), dimension(:,:,:,:,:,:,:), allocatable  :: vector_transition_real
        end type jagged_matrix_transition_real4

        type :: jagged_matrix_transition_int2
            integer(2), dimension(:,:,:,:,:,:,:), allocatable  :: vector_transition_integer
        end type jagged_matrix_transition_int2

        type :: jagged_matrix_real4
            real(4), dimension(:,:,:,:,:,:), allocatable  :: vector_real
        end type jagged_matrix_real4

        type :: jagged_matrix_int2
            integer(2), dimension(:,:,:,:,:,:), allocatable  :: vector_integer
        end type jagged_matrix_int2
""")

rep("""        type(jagged_matrix_transition_real), dimension(1:2) :: value_function,policy_function_wage_income_tax_paid,&
            policy_function_mortgage_interest_deductions,policy_function_consumption,policy_function_space_lived_in_size,&
            policy_function_labor_supply,policy_function_cutoff_taxable_income,policy_function_frac_spent_on_addiction,&
            frac_mov_optimal_1,distribution_guess,distribution_implied,distribution_stationary,distribution_forward,&
            policy_function_total_consumption
""", """        type(jagged_matrix_transition_real4), dimension(1:2) :: value_function,policy_function_wage_income_tax_paid,&
            policy_function_mortgage_interest_deductions,policy_function_consumption,policy_function_space_lived_in_size,&
            policy_function_labor_supply,policy_function_cutoff_taxable_income,policy_function_frac_spent_on_addiction,&
            frac_mov_optimal_1,policy_function_total_consumption
        type(jagged_matrix_transition_real), dimension(1:2) :: distribution_guess,distribution_implied,&
            distribution_stationary,distribution_forward
""")

rep("""        type(jagged_matrix_transition_integer), dimension(1:2) :: &
            policy_function_financial_index,policy_function_housing_status_index,policy_function_space_lived_in_index,&
            policy_function_years_of_amortization_index,fin_index_frac_mov_to_optimal,policy_function_addiction,&
            policy_function_treatment
""", """        type(jagged_matrix_transition_int2), dimension(1:2) :: &
            policy_function_financial_index,policy_function_housing_status_index,policy_function_space_lived_in_index,&
            policy_function_years_of_amortization_index,fin_index_frac_mov_to_optimal,policy_function_addiction,&
            policy_function_treatment
""")

rep("""        type(jagged_matrix_real), dimension(1:2) ::  value_function_benchmark,distribution_stationary_benchmark,&
            policy_function_labor_supply_benchmark,policy_function_total_consumption_benchmark,&
            policy_function_consumption_benchmark,policy_function_frac_spent_on_addiction_benchmark,&
            value_function_comparison,frac_mov_optimal_1_benchmark
""", """        type(jagged_matrix_real4), dimension(1:2) ::  value_function_benchmark,&
            policy_function_labor_supply_benchmark,policy_function_total_consumption_benchmark,&
            policy_function_consumption_benchmark,policy_function_frac_spent_on_addiction_benchmark,&
            value_function_comparison,frac_mov_optimal_1_benchmark
        type(jagged_matrix_real), dimension(1:2) ::  distribution_stationary_benchmark
""")

rep("""        type(jagged_matrix_integer), dimension(1:2) :: policy_function_housing_status_index_benchmark,&
            policy_function_years_of_amortization_index_benchmark,policy_function_financial_index_benchmark,&
            fin_index_frac_mov_to_optimal_benchmark,policy_function_addiction_benchmark
""", """        type(jagged_matrix_int2), dimension(1:2) :: policy_function_housing_status_index_benchmark,&
            policy_function_years_of_amortization_index_benchmark,policy_function_financial_index_benchmark,&
            fin_index_frac_mov_to_optimal_benchmark,policy_function_addiction_benchmark
""")

open(dst, 'w').write(s)
print(f'patch_sp: {src} -> {dst}')
