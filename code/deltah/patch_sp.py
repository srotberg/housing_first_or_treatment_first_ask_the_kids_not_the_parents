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

# THE CALL SITES WHERE A NARROWED ARRAY MEETS A DOUBLE OR FOUR-BYTE DUMMY (15 in the benchmark source). Each is widened
# at the call, never by changing the dummy, which other callers pass doubles to.
import re


def sub(pat, repl, n):
    global s
    s, c = re.subn(pat, repl, s)
    assert c == n, (c, n, pat[:140])


# addiction_transition(..., choice_1, ..., treatment_1, smi): both intent(in) integers, the four recovery tallies
IX = r'\(time_period,age_index,financial_index,&\n\s*unemployment_index,employment_index,housing_status_index,&\n\s*voucher_index\)'
sub(r'(addiction_transition\(1,0,&\n\s*)(policy_function_addiction\(years_left_on_mortgage_index\)%&\n\s*vector_transition_integer'
    + IX + r')(,[12],0\.d0,1,&\n\s*)(policy_function_treatment\(years_left_on_mortgage_index\)%&\n\s*vector_transition_integer'
    + IX + r')(,smi_of\(unemployment_index\)\))', r'\1int(\2)\3int(\4)\5', 4)

# compute_voucher_index_1(is_homeless, drug_share_1, ...): drug_share_1 is real(8), intent(in)
sub(r'(call compute_voucher_index_1\(is_homeless_1,&\n\s*)(policy_function_frac_spent_on_addiction_benchmark&\n\s*'
    r'\(years_left_on_mortgage_index\)%&\n\s*vector_real\(age_index,financial_index,unemployment_index,&\n\s*'
    r'employment_index,housing_status_index,voucher_index\)),', r'\1real(\2,8),', 1)
sub(r'(call compute_voucher_index_1\(is_homeless_2,&\n\s*)\((policy_function_frac_spent_on_addiction\(years_left_on_mortgage_index\)%&'
    r'\n\s*vector_transition_real\(time_period,age_index,financial_index,&\n\s*unemployment_index,employment_index,'
    r'housing_status_index,voucher_index\))\),', r'\1real(\2,8),', 2)

# internal_computations: no intents. value_function_1 is READ AND WRITTEN (a running maximum, handed back through
# val_fun_internal, which the caller then stores), so it gets a threadprivate double copy; the housing index and the
# two tax amounts are only read, so they are widened in place.
rep("""        real(8) :: val_fun_internal
""", """        real(8) :: val_fun_internal
        real(8) :: sp_value_function_in      ! patch_sp.py: the double copy internal_computations reads and updates
""")
rep("""        !$omp threadprivate(val_fun_internal)
""", """        !$omp threadprivate(val_fun_internal)
        !$omp threadprivate(sp_value_function_in)
""")
CELL = (r'(time_period,age_index,financial_index,&\n\s*unemployment_index,employment_index,housing_status_index,'
        r'voucher_index\)')
sub(r'(\n(\s*))call internal_computations&\n(\s*)\((value_function\(years_left_on_mortgage_index\)%&\n\s*'
    r'vector_transition_real\(time_period,age_index,financial_index,&\n\s*unemployment_index,employment_index,'
    r'housing_status_index,voucher_index\)),',
    r'\1sp_value_function_in=\4\n\2call internal_computations&\n\3(sp_value_function_in,', 1)
sub(r'(space_lived_in_index_used_3,)(policy_function_housing_status_index&\n\s*\(years_left_on_mortgage_index\)%'
    r'vector_transition_integer&\n\s*\(time_period,age_index,financial_index,unemployment_index,&\n\s*'
    r'employment_index,housing_status_index,voucher_index\))(,amortization_used_dist,)', r'\1int(\2)\3', 1)
sub(r'(amortization_used_dist,&\n\s*)(policy_function_wage_income_tax_paid\(years_left_on_mortgage_index\)%&\n\s*'
    r'vector_transition_real\(time_period,age_index,financial_index,&\n\s*unemployment_index,employment_index,'
    r'housing_status_index,voucher_index\)),&\n(\s*)(policy_function_mortgage_interest_deductions'
    r'\(years_left_on_mortgage_index\)%&\n\s*vector_transition_real\(time_period,age_index,financial_index,'
    r'unemployment_index,&\n\s*employment_index,housing_status_index,voucher_index\)),',
    r'\1real(\2,8),&\n\3real(\4,8),', 1)

# THE BUDGET-IDENTITY CHECK AT FOUR-BYTE PRECISION (12 October, the first launch of remote_deltah_both_C.sh).
# check_budget_constraint_clears rebuilds the budget in double from the STORED policies and prints eleven lines whenever
# the residual exceeds 5e-8. With consumption, the drug share, total consumption and frac_mov_optimal_1 stored in four
# bytes the identity holds only to their rounding: the first loop's distribution stage printed 2.2 million residuals
# (largest 1.9e-6, residual / (eps4 * consumption) at most 7.3, the rest from the savings terms), 975 MB of log in
# 30 minutes. The check only prints, so its tolerance gets the rounding of what it reads: 4 eps4 times the sum of the
# identity's magnitudes, at least four times the worst case (c, f*tc, and frac_used times the two grid points).
rep("""        checking_criterion=5*10.d0**(-8)
""", """        checking_criterion=5*10.d0**(-8)
        ! patch_sp.py: the stored policies are four-byte, so the identity holds to their rounding, not to 5e-8
        checking_criterion=checking_criterion+4*dble(epsilon(1.0))*(&
            (1+abs(consumption_tax))*(abs(consumption_used)+abs(frac_spent_on_addiction_used*total_consumption_used))+&
            (abs(financial_grid(fin_index_frac_used))+abs(financial_grid(financial_index_used)))*max(abs(neg_scale_1),1.d0))
""")

open(dst, 'w').write(s)
print(f'patch_sp: {src} -> {dst}')
