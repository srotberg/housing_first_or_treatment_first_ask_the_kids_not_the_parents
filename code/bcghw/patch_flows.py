# patch_flows.py <in cf.f90> <out cf.f90> -- PRINT-ONLY (13 October; the author, on Beauregard, Couture, Green, Hicks and
# Warburton (2026), "Pathways into Homelessness": "yes, try to incorporate what could be used in that paper").
# Adds to the stationary-distribution sweep (converge_to_stationary_equilibrium) two flows, accumulated per thread over
# each sweep (reset at its start) and printed with each pass's CF MOMENTS line:
#   FLOWS ENTRY group=g : working-age households housed this year (survivors) and those of them homeless next year,
#                         without and with a SUD this year. g = 1 all working ages, 2 employed, 3 not employed,
#                         4 the first ten adult years. Their entry-rate ratio is the model's counterpart of BCGHW's
#                         hazard ratio of a long-standing SUD for first entry into homelessness (4.56, Table 1).
#   FLOWS PERSIST       : those entrants (housed this year, homeless next year), by SUD this year, and how many of
#                         them the housing policy keeps homeless the year after: the counterpart of BCGHW's 75 per
#                         cent of first-time entrants no longer homeless twelve months later (Figure E.9).
# Nothing the model computes changes: every addition only reads the sweep's own quantities.
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, ("not exactly once", s.count(old), old[:120])
    s = s.replace(old, new)

# 1. declarations
rep("        real(8) :: distance_distribution=1\n",
    "        real(8) :: distance_distribution=1\n"
    "        ! FLOWS (code/bcghw/patch_flows.py): print-only accumulators, per thread\n"
    "        real(8) :: flows_housed_1(max_CPUs,2,4)=0,flows_enter_1(max_CPUs,2,4)=0\n"
    "        real(8) :: flows_new_1(max_CPUs,2)=0,flows_stay_1(max_CPUs,2)=0\n"
    "        real(8) :: flows_w_1=0,flows_old_1=0\n"
    "        integer :: flows_entry_1=0,flows_k_1=1,flows_g_1=1\n")

# 2. reset at the start of every sweep
rep("                distribution_implied_private(i)%vector_cpu_real(:,:,:,:,:,:,:)=0\n",
    "                distribution_implied_private(i)%vector_cpu_real(:,:,:,:,:,:,:)=0\n"
    "                flows_housed_1=0\n                flows_enter_1=0\n                flows_new_1=0\n                flows_stay_1=0\n")

# 3. the parallel loop's clauses
rep("                                    !$omp& survival_probability_for_dist_iteration) &\n",
    "                                    !$omp& survival_probability_for_dist_iteration,&\n"
    "                                    !$omp& flows_housed_1,flows_enter_1,flows_new_1,flows_stay_1) &\n")
rep("                                    !$omp& private(voucher_index_1)\n",
    "                                    !$omp& private(voucher_index_1,flows_w_1,flows_old_1,flows_entry_1,flows_k_1,flows_g_1)\n")

# 4. the source state: housed working-age survivors, and whether the policy puts them on the street next year
ANCHOR = '                                                        do future_voucher_index=first_voucher_index_1,second_voucher_index_1\n                                                        \n                                                            distribution_implied_private(amortization_used_dist)%&\n                                                                vector_cpu_real(thread_num+1,age_index+1,financial_index_copy,&\n                                                                future_unemployment_index,future_employment_index,&\n                                                                future_housing_status_index_to_use_2,future_voucher_index)=&\n                                                                fraction_copy*survival_probability_for_dist_iteration&\n                                                                (age_index,is_homeless_2,&\n                                                                survival_sud_of(is_addicted_1,treatment_choice_dist_1),&\n                                                                smi_of(unemployment_index))*&\n                                                                voucher_probabilities(voucher_index,&\n                                                                future_voucher_index,has_opportunity_2,voucher_index_1)*&\n                                                                employment_process(age_index,employment_index,&\n                                                                future_employment_index)*unemployment_process&\n                                                                (age_index,unemployment_index,future_unemployment_index,&\n                                                                is_homeless_2,future_addiction_index_2,employment_index)*&\n                                                                addiction_transition(is_addicted_1,&\n                                                                future_addiction_index_2,addiction_choice_1,is_homeless_2,&\n                                                                drug_quantity_dist_1,0,treatment_choice_dist_1,&\n                                                                smi_of(unemployment_index))*&\n                                                                distribution_guess(years_left_on_mortgage_index)%&\n                                                                vector_transition_real(time_period-solve_transition_dynamics,&\n                                                                age_index,financial_index,unemployment_index,employment_index,&\n                                                                housing_status_index,voucher_index)+&\n                                                                distribution_implied_private(amortization_used_dist)%&\n                                                                vector_cpu_real&\n                                                                (thread_num+1,age_index+1,financial_index_copy,&\n                                                                future_unemployment_index,future_employment_index,&\n                                                                future_housing_status_index_to_use_2,future_voucher_index)\n\n'
assert s.count(ANCHOR) == 1, ("innermost anchor", s.count(ANCHOR))
i0 = s.index(ANCHOR)
k = s.rindex("                                            do future_addiction_index_2=&\n", 0, i0)
assert i0 - k < 3000, "the addiction loop is not the one enclosing the anchor"
src_block = (
"                                            ! FLOWS (patch_flows.py): housed working-age survivors by SUD now, and entries\n"
"                                            flows_entry_1=0\n"
"                                            if ((in_retirement==0) .AND. (housing_status_index/=lowest_housing_grid_point)) then\n"
"                                                flows_w_1=fraction_copy*survival_probability_for_dist_iteration&\n"
"                                                    (age_index,is_homeless_2,&\n"
"                                                    survival_sud_of(is_addicted_1,treatment_choice_dist_1),&\n"
"                                                    smi_of(unemployment_index))*&\n"
"                                                    distribution_guess(years_left_on_mortgage_index)%&\n"
"                                                    vector_transition_real(time_period-solve_transition_dynamics,&\n"
"                                                    age_index,financial_index,unemployment_index,employment_index,&\n"
"                                                    housing_status_index,voucher_index)\n"
"                                                flows_k_1=1+is_addicted_1\n"
"                                                flows_g_1=3\n"
"                                                if (emp_of(unemployment_index)==1) flows_g_1=2\n"
"                                                flows_housed_1(thread_num+1,flows_k_1,1)=flows_housed_1(thread_num+1,flows_k_1,1)+flows_w_1\n"
"                                                flows_housed_1(thread_num+1,flows_k_1,flows_g_1)=flows_housed_1(thread_num+1,flows_k_1,flows_g_1)+flows_w_1\n"
"                                                if (age_index<=10) flows_housed_1(thread_num+1,flows_k_1,4)=flows_housed_1(thread_num+1,flows_k_1,4)+flows_w_1\n"
"                                                if (future_housing_status_index_to_use_2==lowest_housing_grid_point) then\n"
"                                                    flows_entry_1=1\n"
"                                                    flows_enter_1(thread_num+1,flows_k_1,1)=flows_enter_1(thread_num+1,flows_k_1,1)+flows_w_1\n"
"                                                    flows_enter_1(thread_num+1,flows_k_1,flows_g_1)=flows_enter_1(thread_num+1,flows_k_1,flows_g_1)+flows_w_1\n"
"                                                    if (age_index<=10) flows_enter_1(thread_num+1,flows_k_1,4)=flows_enter_1(thread_num+1,flows_k_1,4)+flows_w_1\n"
"                                                end if\n"
"                                            end if\n"
"                                            \n")
s = s[:k] + src_block + s[k:]

# 5. the destination of an entry: is the household still homeless the year after?
DEST = ("distribution_implied_private(amortization_used_dist)%vector_cpu_real(thread_num+1,age_index+1,&\n"
        "                                                                    financial_index_copy,future_unemployment_index,future_employment_index,&\n"
        "                                                                    future_housing_status_index_to_use_2,future_voucher_index)")
head0, head1, stmt = ANCHOR.split("\n", 2)
new = (head0 + "\n" + head1 + "\n"
"                                                            if (flows_entry_1==1) flows_old_1=&\n"
"                                                                " + DEST + "\n"
+ stmt +
"                                                            if (flows_entry_1==1) then\n"
"                                                                flows_w_1=" + DEST + "-flows_old_1\n"
"                                                                flows_new_1(thread_num+1,flows_k_1)=flows_new_1(thread_num+1,flows_k_1)+flows_w_1\n"
"                                                                if (policy_function_housing_status_index(amortization_used_dist)%&\n"
"                                                                    vector_transition_integer(time_period,age_index+1,financial_index_copy,&\n"
"                                                                    future_unemployment_index,future_employment_index,&\n"
"                                                                    lowest_housing_grid_point,future_voucher_index)==lowest_housing_grid_point) &\n"
"                                                                    flows_stay_1(thread_num+1,flows_k_1)=flows_stay_1(thread_num+1,flows_k_1)+flows_w_1\n"
"                                                            end if\n")
rep(ANCHOR, new)

# 6. the print, with each pass's moments
rep('                write(*,*) "CF MOMENTS distance="',
    '                do flows_g_1=1,4\n'
    '                    write(*,*) "FLOWS ENTRY group=", flows_g_1, " housed_nosud=", sum(flows_housed_1(:,1,flows_g_1)), &\n'
    '                        " housed_sud=", sum(flows_housed_1(:,2,flows_g_1)), " enter_nosud=", sum(flows_enter_1(:,1,flows_g_1)), &\n'
    '                        " enter_sud=", sum(flows_enter_1(:,2,flows_g_1))\n'
    '                end do\n'
    '                write(*,*) "FLOWS PERSIST new_nosud=", sum(flows_new_1(:,1)), " new_sud=", sum(flows_new_1(:,2)), &\n'
    '                    " stay_nosud=", sum(flows_stay_1(:,1)), " stay_sud=", sum(flows_stay_1(:,2))\n'
    '                write(*,*) "CF MOMENTS distance="')
for t in ("FLOWS ENTRY group=", "FLOWS PERSIST new_nosud=", "flows_entry_1=1\n", "flows_stay_1(thread_num+1,flows_k_1)=flows_stay_1"):
    assert s.count(t) == 1, ("landed once", t, s.count(t))
open(dst, 'w').write(s)
print("patch_flows: patched", src, "->", dst)
