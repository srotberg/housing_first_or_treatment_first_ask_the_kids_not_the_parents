"""patch_treatC2.py IN OUT -- RULE C WITH AN ABSTENTION OPTION FOR A HOUSEHOLD WITH THE DISORDER (12 October).

Everything patch_treatC.py does (rule C: a household with the disorder must be in treatment and nobody may use; the
household's own treatment choice at the two distribution screen sites; the MILBY SPLIT print), PLUS:

1. THE ABSTENTION CHOICE. Under rule C a household with the disorder in treatment keeps its voucher only if it spends
   nothing on the drug, but the household problem had no v=0 option for it: its drug spending came from the closed-form
   split in optimize_frac_spent_on_addiciton, zero only at a budget corner. renter_to_renter_problem (the only routine
   with a treatment loop: owners have no treatment choice) now nests `do abstain_choice_1=0,abstain_top_1` inside the
   treatment loop. abstain_top_1 is 1 only for a household with the disorder, in treatment, in a counterfactual with the
   screen on (voucher_conditional_on_clean==1). Abstaining untreated is dominated under rule C (the untreated disorder
   fails the screen anyway), and abstaining is dominated wherever there is no screen, so the gate loses nothing and keeps
   every no-screen arm bit for bit. calculate_addiction_spending, when abstain_now==1, charges the treatment's money cost
   as before and then sets v=0 and c to the whole of the remaining consumption, skipping the split and its child and risk
   refinements; drug utility is at b alone. The disorder state is unchanged (the use index stays 1, the recovery hazard
   and mortality key on the disorder and treatment, not on v).

2. THE EV TABLE'S KEY CARRIES THE VOUCHER CATEGORY (code/audit/AUDIT_E_household.md, Finding 1, open until now).
   fill_ev_table's sum reads voucher_probabilities(...,evx_vidx), but the cache was keyed on (use state, dwelling,
   opportunity) only and invalidated only when the household's own state moved. Under the screen the category differs
   across candidates at one node (no use: 1 or 2; use, or the disorder untreated: 3), so every candidate after the first
   at a (dwelling, opportunity) pair read the FIRST candidate's continuation. Without this fix the abstaining candidate
   reads the category-3 table filled by the treated-and-using candidate, never sees the voucher it keeps, and the new
   margin is dead; and, in every Treatment First arm so far, a clean household's use candidate read the no-use
   candidate's (category 1 or 2) continuation, so it did not foresee losing the voucher. The table's opportunity
   dimension is widened to 0:7 and indexed opp+2*category when the screen is on; with the screen off the index is opp,
   as before, so no-screen arms are unchanged.

3. internal_computations SEES THE HOUSEHOLD'S OWN TREATMENT AND ABSTENTION when the screen is on. It re-solves each node
   after the choice (secant included, which re-optimises v) and could overwrite the stored drug share; it ran with
   treatment_choice_now already reset to 0, so a treated household was re-priced as untreated (no money cost, untreated
   recovery, category 3), and an abstainer would have been re-priced as using. treatment_choice_now and abstain_now are
   set from the stored policy before the call and reset after. Gated on the screen, so no-screen arms are unchanged.

4. DRUG USE IS v>0. model_total_drug_users (passes.txt's b, CF MOMENTS b=) was model_addicted + model_exprimenters, i.e.
   every household with the disorder counted as a user whatever it spent. With the screen on, the abstainers (the
   disorder, in treatment, v=0) are subtracted. Inert when nobody abstains.

5. The 'ABSTAIN' print, once per stationary solve beside MILBY SPLIT: households with the disorder, of them in treatment,
   of them in treatment with v=0, and (for reference) of them untreated with v=0, each for voucher holders and the rest.

Runtime switches, read once from the environment (default all 1; each is also gated on the screen): TC2_ABSTAIN,
TC2_EVKEY, TC2_INTERNAL. With all three 0 the binary is cf_fix2_treatC's arithmetic. Applies to cf_fix2/cf.f90 and to
transition_fix/tr70_src.f90 (the transition's household problem is the same routine in its own source)."""
import os, subprocess, sys
src, out = sys.argv[1], sys.argv[2]
# ---- patch_treatC.py's steps, inlined so this file can replace it under its name (patch_treat.py split, then rule C)
subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'patch_treat.py'), 'split', src, out], check=True)
s = open(out).read()
old = ("            if (unemployment_index>threshold_addiction_index) fails_1=1\n"
       "            if (drug_share_1>0) fails_1=1\n")
assert s.count(old) == 1, s.count(old)
s = s.replace(old,
    "            ! RULE C (patch_treatC.py): a household with the disorder must be in treatment, and nobody may use\n"
    "            if ((unemployment_index>threshold_addiction_index) .AND. (meets_condition_1==0)) fails_1=1\n"
    "            if (drug_share_1>0) fails_1=1\n")
# THE HOUSEHOLD'S OWN TREATMENT CHOICE IN THE DISTRIBUTION (12 October, second fix). meets_condition_1 reads
# treatment_choice_now, a threadprivate that the value-function solve sets to the CANDIDATE treatment inside its choice
# loop and resets to 0 after it. The distribution (converge_to_stationary_equilibrium) and the homelessness-duration
# statistics call the screen with it still 0, so no household in treatment ever kept its voucher there and the arm
# reproduced the paper's to four digits (pass 1 welfare 789.9398 in both). Here the two distribution call sites set it
# from the household's own policy first, and put it back to 0 after.
call = ("                                                call compute_voucher_index_1(is_homeless_2,&\n"
        "                                                    (policy_function_frac_spent_on_addiction(years_left_on_mortgage_index)%&\n"
        "                                                    vector_transition_real(time_period,age_index,financial_index,&\n"
        "                                                    unemployment_index,employment_index,housing_status_index,voucher_index)),&\n"
        "                                                    voucher_index_1)\n")
assert s.count(call) == 2, s.count(call)
s = s.replace(call,
    "                                                ! THE HOUSEHOLD'S OWN TREATMENT CHOICE (patch_treatC.py)\n"
    "                                                treatment_choice_now=policy_function_treatment(years_left_on_mortgage_index)%&\n"
    "                                                    vector_transition_integer(time_period,age_index,financial_index,&\n"
    "                                                    unemployment_index,employment_index,housing_status_index,voucher_index)\n"
    + call +
    "                                                treatment_choice_now=0\n")


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    s = s.replace(old, new)


GATE = "(voucher_conditional_on_clean==1)"

# ---- declarations: abstain_now beside treatment_choice_now, threadprivate; the switches and the print's accumulators
rep("        integer :: treatment_choice_now=0\n",
    "        integer :: treatment_choice_now=0\n"
    "        ! THE ABSTENTION CANDIDATE (patch_treatC2.py): 1 while renter_to_renter_problem evaluates a household with\n"
    "        ! the disorder, in treatment, spending nothing on the drug; read in calculate_addiction_spending.\n"
    "        integer :: abstain_now=0\n"
    "        ! 1 at a node of govt_revenues_calc's distribution loop that is an abstainer (the disorder, treated, v=0)\n"
    "        integer :: tc2_ab_1=0\n"
    "        ! patch_treatC2.py's three switches, from the environment (TC2_ABSTAIN, TC2_EVKEY, TC2_INTERNAL), default 1\n"
    "        integer :: tc2_abstain_on=1,tc2_evkey_on=1,tc2_internal_on=1,tc2_env_read=0\n"
    "        ! the ABSTAIN print: (time, group, measure); group 0 all, 1 voucher holders housed, 2 housed without a\n"
    "        ! voucher, 3 homeless; measure 1 the disorder, 2 of them in treatment, 3 in treatment with v=0, 4 untreated v=0\n"
    "        real(8), dimension(transition_length,0:3,4) :: tc2_abst=0.d0\n"
    "        integer :: tc2_g_1=0\n")
rep("        !$omp threadprivate(treatment_choice_now)\n",
    "        !$omp threadprivate(treatment_choice_now)\n"
    "        !$omp threadprivate(abstain_now)\n")

# ---- the switches, read at the top of initialize_variables_and_grids
rep("    subroutine initialize_variables_and_grids()\n    \n        use Global_Vars\n        \n        implicit none\n",
    "    subroutine initialize_variables_and_grids()\n    \n        use Global_Vars\n        \n        implicit none\n"
    "        character(len=32) :: tc2_buf_1\n"
    "        integer :: tc2_len_1,tc2_st_1\n"
    "\n"
    "        if (tc2_env_read==0) then\n"
    "            call get_environment_variable('TC2_ABSTAIN',tc2_buf_1,tc2_len_1,tc2_st_1)\n"
    "            if ((tc2_st_1==0) .AND. (tc2_len_1>0)) read(tc2_buf_1,*) tc2_abstain_on\n"
    "            call get_environment_variable('TC2_EVKEY',tc2_buf_1,tc2_len_1,tc2_st_1)\n"
    "            if ((tc2_st_1==0) .AND. (tc2_len_1>0)) read(tc2_buf_1,*) tc2_evkey_on\n"
    "            call get_environment_variable('TC2_INTERNAL',tc2_buf_1,tc2_len_1,tc2_st_1)\n"
    "            if ((tc2_st_1==0) .AND. (tc2_len_1>0)) read(tc2_buf_1,*) tc2_internal_on\n"
    "            tc2_env_read=1\n"
    "            write(*,*) 'TREATC2 switches abstain evkey internal', tc2_abstain_on, tc2_evkey_on, tc2_internal_on\n"
    "        end if\n")

# ---- 1. the abstention loop in renter_to_renter_problem
rep("            treatment_choice_1,treatment_top_1\n",
    "            treatment_choice_1,treatment_top_1,abstain_choice_1,abstain_top_1,ev_col_1\n")
rep("        optimal_treatment_renter_renter=0\n        treatment_choice_now=0\n",
    "        optimal_treatment_renter_renter=0\n        treatment_choice_now=0\n        abstain_now=0\n")
rep("            do treatment_choice_1=0,treatment_top_1\n\n            treatment_choice_now=treatment_choice_1\n",
    "            do treatment_choice_1=0,treatment_top_1\n\n            treatment_choice_now=treatment_choice_1\n"
    "\n"
    "            ! THE ABSTENTION CANDIDATE (patch_treatC2.py). Under rule C a household with the disorder that is in\n"
    "            ! treatment keeps its voucher only at v=0, which the drug split never chooses away from a corner. Open\n"
    "            ! only where it can matter: the screen on, the disorder, in treatment.\n"
    "            abstain_top_1=0\n"
    "\n"
    "            if ((tc2_abstain_on==1) .AND. (is_counterfactual==1) .AND. " + GATE + " .AND. &\n"
    "                (addiction_index==1) .AND. (treatment_choice_1==1) .AND. (include_treatment==1)) then\n"
    "\n"
    "                abstain_top_1=1\n"
    "\n"
    "            end if\n"
    "\n"
    "            do abstain_choice_1=0,abstain_top_1\n"
    "\n"
    "            abstain_now=abstain_choice_1\n")
rep("            end do\n\n            end do\n\n            treatment_choice_now=0\n        \n        end do\n",
    "            end do\n\n            end do\n\n            end do\n\n            abstain_now=0\n            treatment_choice_now=0\n        \n        end do\n")

# ---- 2. the EV table keyed on the voucher category when the screen is on
rep("                allocate(ev_table(renter_array_floor:financial_grid_size,&\n"
    "                    0:ev_addiction_top,lowest_housing_grid_point:housing_status_grid_size,0:1,max_CPUs))\n"
    "                allocate(ev_table_valid(0:ev_addiction_top,&\n"
    "                    lowest_housing_grid_point:housing_status_grid_size,0:1,max_CPUs))\n",
    "                ! 0:7, not 0:1 (patch_treatC2.py): opp+2*category when the screen is on, opp otherwise\n"
    "                allocate(ev_table(renter_array_floor:financial_grid_size,&\n"
    "                    0:ev_addiction_top,lowest_housing_grid_point:housing_status_grid_size,0:7,max_CPUs))\n"
    "                allocate(ev_table_valid(0:ev_addiction_top,&\n"
    "                    lowest_housing_grid_point:housing_status_grid_size,0:7,max_CPUs))\n")
# ensure_ev_table
rep("            evx_fv,evx_sv,evx_loopadd,evx_addidx\n\n        if ((ev_table_key(1,evx_slot)/=age_index) .OR. &\n",
    "            evx_fv,evx_sv,evx_loopadd,evx_addidx\n"
    "        integer :: evx_oc\n"
    "\n"
    "        ! THE COLUMN CARRIES THE VOUCHER CATEGORY when the screen is on (patch_treatC2.py; AUDIT_E Finding 1)\n"
    "        evx_oc=evx_opp\n"
    "        if ((tc2_evkey_on==1) .AND. " + GATE + ") evx_oc=evx_opp+2*evx_vidx\n"
    "\n        if ((ev_table_key(1,evx_slot)/=age_index) .OR. &\n")
rep("        if (.NOT. ev_table_valid(evx_fai,evx_fhsi,evx_opp,evx_slot)) then\n",
    "        if (.NOT. ev_table_valid(evx_fai,evx_fhsi,evx_oc,evx_slot)) then\n")
# fill_ev_table: writes go to the keyed column, the sum keeps the true opportunity
rep("        integer :: ffi_1,fei_1,fai_1,fui_1,fvi_1,evx_check,evx_lo,evx_hi,evx_col\n        real(8) :: acc,haz_1\n",
    "        integer :: ffi_1,fei_1,fai_1,fui_1,fvi_1,evx_check,evx_lo,evx_hi,evx_col,evx_oc\n        real(8) :: acc,haz_1\n"
    "\n"
    "        evx_oc=evx_opp\n"
    "        if ((tc2_evkey_on==1) .AND. " + GATE + ") evx_oc=evx_opp+2*evx_vidx\n")
rep("                ev_table(:,evx_col,evx_fhsi,evx_opp,evx_slot)=0\n",
    "                ev_table(:,evx_col,evx_fhsi,evx_oc,evx_slot)=0\n", n=2)
rep("                ev_table(ffi_1,evx_col,evx_fhsi,&\n                    evx_opp,evx_slot)=ev_table(ffi_1,evx_col,evx_fhsi,&\n                    evx_opp,evx_slot)+acc\n",
    "                ev_table(ffi_1,evx_col,evx_fhsi,&\n                    evx_oc,evx_slot)=ev_table(ffi_1,evx_col,evx_fhsi,&\n                    evx_oc,evx_slot)+acc\n")
rep("            ev_table_valid(:,evx_fhsi,evx_opp,evx_slot)=.TRUE.\n",
    "            ev_table_valid(:,evx_fhsi,evx_oc,evx_slot)=.TRUE.\n")
rep("            ev_table_valid(evx_fai,evx_fhsi,&\n                evx_opp,evx_slot)=.TRUE.\n",
    "            ev_table_valid(evx_fai,evx_fhsi,&\n                evx_oc,evx_slot)=.TRUE.\n")
# the readers in renter_to_renter_problem: the column from the candidate's own category
rep("                    call calculate_future_voucher_index_and_opportunity&\n"
    "                        (has_opportunity_1,first_voucher_index,second_voucher_index,&\n"
    "                        time_period,0,0,voucher_index_1,gross_wage_income+investment_income)\n",
    "                    call calculate_future_voucher_index_and_opportunity&\n"
    "                        (has_opportunity_1,first_voucher_index,second_voucher_index,&\n"
    "                        time_period,0,0,voucher_index_1,gross_wage_income+investment_income)\n"
    "\n"
    "                    ! the EV table's column for this candidate (patch_treatC2.py), as ensure_ev_table forms it\n"
    "                    ev_col_1=has_opportunity_1\n"
    "                    if ((tc2_evkey_on==1) .AND. " + GATE + ") ev_col_1=has_opportunity_1+2*voucher_index_1\n")
assert s.count("has_opportunity_1,ev_slot)") == 4, s.count("has_opportunity_1,ev_slot)")
s = s.replace("has_opportunity_1,ev_slot)", "ev_col_1,ev_slot)")

# ---- 1 (cont.). calculate_addiction_spending: the abstainer spends nothing
rep("            total_consumption_choice_2=total_consumption_choice_1\n"
    "                    \n"
    "            call optimize_frac_spent_on_addiciton&\n"
    "                (total_consumption_choice_2,consumption_choice,frac_spent_on_addiction,&\n"
    "                price_of_addictive_good,food_stamps_1,housing_size_1,addiction_index_1)\n",
    "            total_consumption_choice_2=total_consumption_choice_1\n"
    "\n"
    "            ! THE ABSTAINER (patch_treatC2.py): treatment paid above, then nothing on the drug and all the rest on\n"
    "            ! consumption; drug utility at b alone. The food-stamp check below applies unchanged.\n"
    "            if (abstain_now==1) then\n"
    "\n"
    "                consumption_choice=total_consumption_choice_2\n"
    "                frac_spent_on_addiction=0\n"
    "\n"
    "            else\n"
    "                    \n"
    "            call optimize_frac_spent_on_addiciton&\n"
    "                (total_consumption_choice_2,consumption_choice,frac_spent_on_addiction,&\n"
    "                price_of_addictive_good,food_stamps_1,housing_size_1,addiction_index_1)\n"
    "\n"
    "            end if\n")

# ---- 3. internal_computations with the household's own treatment and abstention
anchor = "                                            call internal_computations&\n"
rep(anchor,
    "                                            ! THE HOUSEHOLD'S OWN TREATMENT AND ABSTENTION (patch_treatC2.py)\n"
    "                                            if ((tc2_internal_on==1) .AND. " + GATE + ") then\n"
    "                                                treatment_choice_now=policy_function_treatment(years_left_on_mortgage_index)%&\n"
    "                                                    vector_transition_integer(time_period,age_index,financial_index,&\n"
    "                                                    unemployment_index,employment_index,housing_status_index,voucher_index)\n"
    "                                                if ((tc2_abstain_on==1) .AND. (treatment_choice_now==1) .AND. &\n"
    "                                                    (unemployment_index>threshold_addiction_index) .AND. &\n"
    "                                                    (frac_spent_on_addiction_3<=0.d0)) abstain_now=1\n"
    "                                            end if\n"
    "\n" + anchor)
rep("                                                frac_spent_on_addiction_3,addiction_used)\n",
    "                                                frac_spent_on_addiction_3,addiction_used)\n"
    "                                            treatment_choice_now=0\n"
    "                                            abstain_now=0\n")

# ---- 4 and 5. use is v>0; the ABSTAIN accumulators and print (govt_revenues_calc)
rep("        if (accumulating_beta_types==0) model_addicted(time_period)=0\n",
    "        if (accumulating_beta_types==0) model_addicted(time_period)=0\n"
    "        if (accumulating_beta_types==0) tc2_abst(time_period,:,:)=0.d0\n")
rep("                                        total_addited_1=total_addited_1+distribution_mass_used\n",
    "                                        total_addited_1=total_addited_1+distribution_mass_used\n"
    "\n"
    "                                        ! THE ABSTAIN PRINT'S ACCUMULATORS (patch_treatC2.py): Milby's arms, as MILBY SPLIT\n"
    "                                        ! draws them (housed: housing_status_index_used>=second_lowest_housing_grid_point)\n"
    "                                        tc2_g_1=3\n"
    "                                        if (housing_status_index_used>=second_lowest_housing_grid_point) then\n"
    "                                            tc2_g_1=2\n"
    "                                            if (voucher_index==1) tc2_g_1=1\n"
    "                                        end if\n"
    "                                        tc2_abst(time_period,0,1)=tc2_abst(time_period,0,1)+distribution_mass_used\n"
    "                                        tc2_abst(time_period,tc2_g_1,1)=tc2_abst(time_period,tc2_g_1,1)+distribution_mass_used\n"
    "                                        if (policy_function_treatment(years_left_on_mortgage_index)%vector_transition_integer&\n"
    "                                            (time_period,age_index,financial_index,unemployment_index,employment_index,&\n"
    "                                            housing_status_index,voucher_index)==1) then\n"
    "                                            tc2_abst(time_period,0,2)=tc2_abst(time_period,0,2)+distribution_mass_used\n"
    "                                            tc2_abst(time_period,tc2_g_1,2)=tc2_abst(time_period,tc2_g_1,2)+distribution_mass_used\n"
    "                                            if (frac_spent_on_addiction_used<=0.d0) then\n"
    "                                                tc2_abst(time_period,0,3)=tc2_abst(time_period,0,3)+distribution_mass_used\n"
    "                                                tc2_abst(time_period,tc2_g_1,3)=tc2_abst(time_period,tc2_g_1,3)+distribution_mass_used\n"
    "                                            end if\n"
    "                                        elseif (frac_spent_on_addiction_used<=0.d0) then\n"
    "                                            tc2_abst(time_period,0,4)=tc2_abst(time_period,0,4)+distribution_mass_used\n"
    "                                            tc2_abst(time_period,tc2_g_1,4)=tc2_abst(time_period,tc2_g_1,4)+distribution_mass_used\n"
    "                                        end if\n")
rep("        model_total_drug_users(time_period)=model_addicted(time_period)+model_exprimenters(time_period)\n",
    "        model_total_drug_users(time_period)=model_addicted(time_period)+model_exprimenters(time_period)\n"
    "\n"
    "        ! DRUG USE IS v>0 (patch_treatC2.py): the abstainers carry the disorder but do not use. In EVERY arm, screen or\n"
    "        ! not (the author, 13 Oct: \"Count those in treatment with 0 drug use as non users\"), so that Housing First and\n"
    "        ! Treatment First count use the same way; a statistic only, no choice reads it.\n"
    "        if (tc2_abstain_on==1) model_total_drug_users(time_period)=&\n"
    "            model_total_drug_users(time_period)-tc2_abst(time_period,0,3)\n")
rep('            write(*,*) "MILBY SPLIT voucher mass rec treat smi", xtab_mass_voucher(time_period), &\n',
    '            write(*,*) "ABSTAIN", &\n'
    '                " sud=", tc2_abst(time_period,0,1), " treated=", tc2_abst(time_period,0,2), " treated_v0=", tc2_abst(time_period,0,3), &\n'
    '                " untreated_v0=", tc2_abst(time_period,0,4), &\n'
    '                " holder_treated=", tc2_abst(time_period,1,2), " holder_v0share=", tc2_abst(time_period,1,3)/max(tc2_abst(time_period,1,2),1.d-30), &\n'
    '                " housednov_treated=", tc2_abst(time_period,2,2), " housednov_v0share=", tc2_abst(time_period,2,3)/max(tc2_abst(time_period,2,2),1.d-30), &\n'
    '                " homeless_treated=", tc2_abst(time_period,3,2), " homeless_v0share=", tc2_abst(time_period,3,3)/max(tc2_abst(time_period,3,2),1.d-30)\n'
    '            write(*,*) "MILBY SPLIT voucher mass rec treat smi", xtab_mass_voucher(time_period), &\n')
# the OpenMP region around the household problem is default(none)
rep("                                !$omp& warm_start_a_prime,warm_start_ready,renter_floor_by_age)\n",
    "                                !$omp& warm_start_a_prime,warm_start_ready,renter_floor_by_age,&\n"
    "                                !$omp& tc2_abstain_on,tc2_internal_on,voucher_conditional_on_clean,policy_function_treatment)\n")

# ---- 6. TREATMENT IS PAID FOR BY THE GOVERNMENT (the author, 13 Oct: "I think it should be add to the benchmark too...
# And all the runs. You need to add it as a cost in the budget"). Each household with the disorder that is in treatment
# costs the government public_cost_of_treatment a year, charged in govt_spending_on_addicts (whose old per-head cost the
# author set to zero on 8 September), so it enters net revenue, the budget pi_V clears, every spending total and the
# transition's budget, in every arm with treatment, Housing First included. Treatment's utility cost to the household is
# unchanged. VALUE (the author, 13 Oct: "I would go with the 9000-9400"): $9,426 a treated year, the average cost of a
# residential treatment episode in Roebuck, French and McLellan (2003, J. Substance Abuse Treatment 25(1); DATCAP), at face
# value on the paper's dollar scale, as the $35 test is: average labour income is $9m / vsl_data = $112,500, so the model
# value is 9426/112500 * 1.589818 (the benchmark's average labour income) = 0.1332056. (First set at $3,000, Medicaid's
# 2008 spending per user of any treatment, ASPE; the author: too low for a year.) Settable by the handover.
rep("        real(8) :: cost_per_drug_test=0.00049461d0",
    "        real(8) :: cost_per_drug_test=0.00049461d0\n"
    "        ! patch_treatC.py (13 Oct): the government's cost of a year of treatment, $9,426 (Roebuck, French and McLellan\n"
    "        ! 2003, a residential episode) at the paper's dollar scale, 9426/(9e6/vsl_data)*1.589818, the benchmark's average labour income\n"
    "        real(8) :: public_cost_of_treatment=0.1332056d0")
rep('                case ("cost_per_drug_test")\n',
    '                case ("public_cost_of_treatment")\n'
    '                    write(*,*) "HANDOVER public_cost_of_treatment:",&\n'
    '                        public_cost_of_treatment, "->", handover_value\n'
    '                    public_cost_of_treatment=max(handover_value,0.d0)\n'
    '\n'
    '                case ("cost_per_drug_test")\n')
rep("                                        govt_spending_on_addicts(time_period)=govt_spending_on_addicts(time_period)+&\n"
    "                                            addict_cost_govt_as_perc_of_avg_inc*avg_income_to_use_1*distribution_mass_used\n",
    "                                        govt_spending_on_addicts(time_period)=govt_spending_on_addicts(time_period)+&\n"
    "                                            addict_cost_govt_as_perc_of_avg_inc*avg_income_to_use_1*distribution_mass_used\n"
    "                                        ! TREATMENT IS PUBLICLY FUNDED (patch_treatC.py, the author 13 Oct): every arm\n"
    "                                        if (include_treatment==1) then\n"
    "                                            if (policy_function_treatment(years_left_on_mortgage_index)%vector_transition_integer&\n"
    "                                                (time_period,age_index,financial_index,unemployment_index,employment_index,&\n"
    "                                                housing_status_index,voucher_index)==1) &\n"
    "                                                govt_spending_on_addicts(time_period)=govt_spending_on_addicts(time_period)+&\n"
    "                                                public_cost_of_treatment*distribution_mass_used\n"
    "                                        end if\n")

# ---- 4 (cont.). THE USER RULE AT EVERY SITE: the disorder half excludes the abstainers (screen on only)
import re
# the per-node flag, set in govt_revenues_calc right after its own spending line (the first such block after its header)
blk = ("                                        addiction_consumption_1=&\n"
       "                                            max(total_consumption_used-consumption_used,0.d0)\n")
h = s.index("    subroutine govt_revenues_calc(time_period)")
i = s.index(blk, h)
assert i < s.index("    end subroutine", h)
s = s[:i] + blk + (
    "                                        ! AN ABSTAINER IS NOT A USER (patch_treatC2.py): the disorder, treated, v=0, in every arm\n"
    "                                        tc2_ab_1=0\n"
    "                                        if ((tc2_abstain_on==1) .AND. &\n"
    "                                            (unemployment_index>threshold_addiction_index) .AND. (addiction_consumption_1<=0.d0)) then\n"
    "                                            if (policy_function_treatment(years_left_on_mortgage_index)%vector_transition_integer&\n"
    "                                                (time_period,age_index,financial_index,unemployment_index,employment_index,&\n"
    "                                                housing_status_index,voucher_index)==1) tc2_ab_1=1\n"
    "                                        end if\n") + s[i+len(blk):]
pat = re.compile(r"(if \(\(\(addiction_consumption_1>0\) \.AND\. \(unemployment_index<=threshold_addiction_index\)\) \.OR\. &\n\s*)\(unemployment_index>threshold_addiction_index\)\)")
s, k = pat.subn(r"\1((unemployment_index>threshold_addiction_index) .AND. (tc2_ab_1==0)))", s)
k0 = s.count("if (((addiction_consumption_1>0) .AND. (unemployment_index<=threshold_addiction_index)) .OR. &\n")
assert k >= 3 and k == k0, (k, k0)
print('user rule gated at', k, 'sites')
rep("                                    if ((unemployment_index>threshold_addiction_index) .OR. (is_addicted==1)) then\n",
    "                                    if (((unemployment_index>threshold_addiction_index) .AND. (tc2_ab_1==0)) .OR. (is_addicted==1)) then\n")
tm = '                    " mass_homeless=", model_sud_mass_homeless(time_index)\n'
if s.count(tm) == 1:
    s = s.replace(tm, tm + (
    '                write(*,*) "TRANSITION ABSTAIN t=", time_index, "", &\n'
    '                    " sud=", tc2_abst(time_index,0,1), " treated=", tc2_abst(time_index,0,2), " treated_v0=", tc2_abst(time_index,0,3), &\n'
    '                    " untreated_v0=", tc2_abst(time_index,0,4), &\n'
    '                    " holder_treated=", tc2_abst(time_index,1,2), " holder_v0share=", tc2_abst(time_index,1,3)/max(tc2_abst(time_index,1,2),1.d-30), &\n'
    '                    " housednov_treated=", tc2_abst(time_index,2,2), " housednov_v0share=", tc2_abst(time_index,2,3)/max(tc2_abst(time_index,2,2),1.d-30), &\n'
    '                    " homeless_treated=", tc2_abst(time_index,3,2), " homeless_v0share=", tc2_abst(time_index,3,3)/max(tc2_abst(time_index,3,2),1.d-30)\n'))
    print('TRANSITION ABSTAIN t= added')
open(out, 'w').write(s)
print(f'treatC2: patched {src} -> {out}')
