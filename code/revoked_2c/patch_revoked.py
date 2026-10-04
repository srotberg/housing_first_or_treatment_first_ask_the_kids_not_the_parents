#!/usr/bin/env python3
"""patch_revoked.py <tr_fix_src.f90> <out_track.f90> <out_plain.f90>

Two build copies of the corrected transition source (transition_fix/patch_transition_fix.py's output) for the
revoked-voucher experiment (code/revoked_2c/README.md). NEITHER CHANGES AN EQUATION.

  out_plain   the transition, plus one line: stop after loop 0 (one forward pass on fixed paths, no updates).
              The control the tracking build is diffed against.
  out_track   out_plain plus a print-only module, revk_track, and three calls into it:
                * revk_init     before the first forward pass (reads REVK_MODE, REVK_TAGDIR from the environment);
                * revk_period   at the END of each forward period, after every line the period prints;
                * nothing else. It reads the model's arrays and writes only its own (shadow masses, tag files, REVK lines).

The shadow step (revk_step) is the forward kernel of converge_to_stationary_equilibrium written out a second time,
term for term and in the same multiplication order, applied to a shadow mass instead of distribution_guess(t-1), with
the newborn row left out. That it IS the kernel is checked every period: the whole population pushed through it
reproduces the model's own distribution at t at every age from 2 up (REVK POP ... kernel_maxabs).

REVK_MODE=tf  tag the holders revoked in years 1-3 (the flow from voucher state 1 into voucher_excl in the forward
              step that makes year t) and follow them, and the holders at the reform, under the run's own kernel;
              write the three tags to REVK_TAGDIR/revk_tag_c<c>.bin.
REVK_MODE=hf  read the tags, put each cohort back in voucher state 1 (kept its voucher, everything else identical,
              since the voucher draw is the last factor of the kernel), and follow it under the run's own kernel
              (a Housing First run); follow the holders at the reform likewise.
"""
import sys

src, out_track, out_plain = sys.argv[1:4]
s = open(src).read()


def rep(text, old, new, count=1):
    n = text.count(old)
    assert n == count, (n, old[:120])
    return text.replace(old, new)


# --- the stop after loop 0 (both copies) -------------------------------------------------------------------------
STOP_ANCHOR = ('            write(*,*) "TRANSITION PATHS SAVED after loop", loop_count, &\n'
               '                " periods=", max(transition_length-1,1)\n\n'
               '            loop_count=loop_count+1\n\n'
               '            write(*,*) "loop_count=", loop_count\n')
if STOP_ANCHOR not in s:
    # tolerate blank lines carrying spaces
    import re
    m = re.search(r'( *write\(\*,\*\) "TRANSITION PATHS SAVED after loop", loop_count, &\n'
                  r' *" periods=", max\(transition_length-1,1\)\n\s*\n'
                  r' *loop_count=loop_count\+1\n\s*\n *write\(\*,\*\) "loop_count=", loop_count\n)', s)
    assert m and s.count(m.group(1)) == 1, "stop anchor not found"
    STOP_ANCHOR = m.group(1)
STOP = ('            ! REVOKED-VOUCHER EXPERIMENT: one forward pass on the fixed paths, no updates (code/revoked_2c).\n'
        '            write(*,*) "REVK STOP after loop 0: the paths are fixed, nothing is updated"\n'
        '            stop\n')
plain = rep(s, STOP_ANCHOR, STOP_ANCHOR + STOP)
open(out_plain, 'w').write(plain)

# --- the tracking module -------------------------------------------------------------------------------------------
MODULE = r'''
    ! ===============================================================================================================
    ! REVOKED-VOUCHER TRACKING (code/revoked_2c). PRINT-ONLY: reads the model's arrays, writes only its own.
    ! ===============================================================================================================
    module revk_track

        use Global_Vars

        implicit none

        integer, parameter :: revk_ng=4
        ! groups: 1..3 the holders whose voucher is revoked in year 1, 2, 3; 4 every holder at the reform
        type(jagged_matrix_real), dimension(1:2,1:revk_ng) :: revk_s
        type(jagged_matrix_real), dimension(1:2) :: revk_new,revk_p,revk_tagbuf
        integer :: revk_mode=0
        integer, dimension(1:revk_ng) :: revk_active=0,revk_start=0
        real(8), dimension(1:revk_ng) :: revk_mass0=0,revk_cum_h=0,revk_cum_e=0,revk_step_h=0,revk_step_e=0,revk_acct=0
        real(8) :: revk_pop_h=0,revk_pop_e=0
        logical :: revk_ready=.false.
        character(len=400) :: revk_tagdir='.'
        ! THE CELLS THE MODEL'S REDUCTION COPIES. converge_to_stationary_equilibrium sums the per-thread arrays into
        ! distribution_implied only over each age's own state range (the renter floor by age above all), so mass the
        ! kernel sends outside it is dropped by the model. The shadow drops the same mass and books it as an exit.
        logical, dimension(:,:,:,:,:,:), allocatable :: revk_mask_1,revk_mask_2
        real(8) :: revk_leak_last=0

    contains

        subroutine revk_alloc(a)
            type(jagged_matrix_real), dimension(1:2), intent(inout) :: a
            integer :: rk_k
            do rk_k=1,2
                if (allocated(a(rk_k)%vector_real)) deallocate(a(rk_k)%vector_real)
                allocate(a(rk_k)%vector_real(&
                    lbound(distribution_guess(rk_k)%vector_transition_real,2):ubound(distribution_guess(rk_k)%vector_transition_real,2),&
                    lbound(distribution_guess(rk_k)%vector_transition_real,3):ubound(distribution_guess(rk_k)%vector_transition_real,3),&
                    lbound(distribution_guess(rk_k)%vector_transition_real,4):ubound(distribution_guess(rk_k)%vector_transition_real,4),&
                    lbound(distribution_guess(rk_k)%vector_transition_real,5):ubound(distribution_guess(rk_k)%vector_transition_real,5),&
                    lbound(distribution_guess(rk_k)%vector_transition_real,6):ubound(distribution_guess(rk_k)%vector_transition_real,6),&
                    lbound(distribution_guess(rk_k)%vector_transition_real,7):ubound(distribution_guess(rk_k)%vector_transition_real,7)))
                a(rk_k)%vector_real=0
            end do
        end subroutine

        subroutine revk_init()
            character(len=40) :: rk_mode_s
            integer :: rk_g,rk_len,rk_st
            if (revk_ready) return
            rk_mode_s='off'
            call get_environment_variable('REVK_MODE',rk_mode_s,rk_len,rk_st)
            if (rk_st/=0) rk_mode_s='off'
            revk_mode=0
            if (trim(rk_mode_s)=='tf') revk_mode=1
            if (trim(rk_mode_s)=='hf') revk_mode=2
            call get_environment_variable('REVK_TAGDIR',revk_tagdir,rk_len,rk_st)
            if ((rk_st/=0) .OR. (rk_len==0)) revk_tagdir='.'
            write(*,*) "REVK INIT mode=", trim(rk_mode_s), " (", revk_mode, ") tagdir=", trim(revk_tagdir)
            write(*,*) "REVK INIT voucher_conditional_on_clean=", voucher_conditional_on_clean, &
                " include_voucher_exclusion=", include_voucher_exclusion, " probability_of_detection=", &
                probability_of_detection, " probability_of_false_positive=", probability_of_false_positive, &
                " voucher_excl=", voucher_excl, " voucher_state_max=", voucher_state_max, &
                " remove_increased_death=", remove_increased_death, " adjust_taxes=", adjust_taxes, &
                " drug_market_adjuster=", drug_market_adjuster, " max_amortization_years=", max_amortization_years
            write(*,'(A,100F20.15)') " REVK INIT price path=", price_of_addictive_good_path(1:max(transition_length-1,1))
            write(*,'(A,100F20.15)') " REVK INIT pi_v path=", probability_of_voucher_path(1:max(transition_length-1,1))
            if (revk_mode==0) then
                revk_ready=.true.
                return
            end if
            do rk_g=1,revk_ng
                call revk_alloc(revk_s(:,rk_g))
            end do
            call revk_alloc(revk_new)
            call revk_alloc(revk_p)
            call revk_alloc(revk_tagbuf)
            call revk_build_mask()
            revk_ready=.true.
        end subroutine

        ! the reduction loop's ranges, verbatim
        subroutine revk_build_mask()
            integer :: rk_a,rk_y,rk_u,rk_e,rk_v,rk_f,rk_h,rk_nb,rk_hh,rk_t1
            allocate(revk_mask_1(lbound(revk_new(1)%vector_real,1):ubound(revk_new(1)%vector_real,1),&
                lbound(revk_new(1)%vector_real,2):ubound(revk_new(1)%vector_real,2),&
                lbound(revk_new(1)%vector_real,3):ubound(revk_new(1)%vector_real,3),&
                lbound(revk_new(1)%vector_real,4):ubound(revk_new(1)%vector_real,4),&
                lbound(revk_new(1)%vector_real,5):ubound(revk_new(1)%vector_real,5),&
                lbound(revk_new(1)%vector_real,6):ubound(revk_new(1)%vector_real,6)))
            allocate(revk_mask_2(lbound(revk_new(2)%vector_real,1):ubound(revk_new(2)%vector_real,1),&
                lbound(revk_new(2)%vector_real,2):ubound(revk_new(2)%vector_real,2),&
                lbound(revk_new(2)%vector_real,3):ubound(revk_new(2)%vector_real,3),&
                lbound(revk_new(2)%vector_real,4):ubound(revk_new(2)%vector_real,4),&
                lbound(revk_new(2)%vector_real,5):ubound(revk_new(2)%vector_real,5),&
                lbound(revk_new(2)%vector_real,6):ubound(revk_new(2)%vector_real,6)))
            revk_mask_1=.false.
            revk_mask_2=.false.
            do rk_a=1,life_span
                rk_nb=0
                if (rk_a==1) rk_nb=1
                do rk_y=1,rk_nb*1+(1-rk_nb)*max_amortization_years
                    rk_hh=0
                    if (rk_y>1) rk_hh=1
                    rk_t1=1
                    if ((rk_hh==0) .AND. (track_renters_housing==0)) rk_t1=0
                    do rk_u=1,unemployment_grid_size
                        do rk_e=1,employment_grid_size
                            do rk_v=0,(1-rk_hh)*voucher_state_max
                                do rk_f=rk_nb*negative_financial_grid_size+&
                                    (1-rk_nb)*(rk_hh*1+(1-rk_hh)*renter_floor_by_age(min(max(rk_a,1),life_span))),&
                                    include_exogenous_endowment*financial_grid_size+(1-include_exogenous_endowment)*&
                                    (rk_nb*negative_financial_grid_size+(1-rk_nb)*financial_grid_size)
                                    do rk_h=(1-rk_hh)*lowest_housing_grid_point+&
                                        rk_hh*index_of_smallest_house_hhld_can_buy,&
                                        rk_t1*(1-rk_nb)*(housing_status_grid_size-1)
                                        if (rk_y==1) then
                                            revk_mask_1(rk_a,rk_f,rk_u,rk_e,rk_h,rk_v)=.true.
                                        else
                                            revk_mask_2(rk_a,rk_f,rk_u,rk_e,rk_h,rk_v)=.true.
                                        end if
                                    end do
                                end do
                            end do
                        end do
                    end do
                end do
            end do
            write(*,*) "REVK MASK cells copied by the reduction: block 1", count(revk_mask_1), " of", size(revk_mask_1), &
                " block 2", count(revk_mask_2), " of", size(revk_mask_2), " renter floor by age (1, life_span-1, life_span)=", &
                renter_floor_by_age(1), renter_floor_by_age(life_span-1), renter_floor_by_age(life_span)
        end subroutine

        ! THE FORWARD KERNEL OF converge_to_stationary_equilibrium, on a shadow mass, without the newborn row.
        ! deaths_h: mass that dies on the survival draw (ages 1..life_span-1); deaths_e: mass at life_span and above,
        ! which the kernel does not carry forward (end of life). do_tag=1 also copies every term that moves a holder
        ! (voucher state 1) into voucher_excl -- a revocation -- into tagbuf.
        subroutine revk_step(time_period,src,dst,deaths_h,deaths_e,thresh,tagbuf,do_tag)
            integer, intent(in) :: time_period,do_tag
            type(jagged_matrix_real), dimension(1:2), intent(in) :: src
            type(jagged_matrix_real), dimension(1:2), intent(inout) :: dst,tagbuf
            real(8), intent(out) :: deaths_h,deaths_e
            real(8), intent(in) :: thresh
            integer :: rk_fin,rk_has_house,rk_track1,rk_vi1,rk_isadd,rk_k
            real(8) :: rk_avg1,rk_avg2,rk_mass,rk_w,rk_surv

            do rk_k=1,2
                dst(rk_k)%vector_real=0
                deaths_e=0
            end do
            deaths_h=0
            deaths_e=0
            do rk_k=1,2
                deaths_e=deaths_e+sum(src(rk_k)%vector_real(life_span:,:,:,:,:,:))
            end do

            rk_avg1=is_counterfactual*average_labor_income_calibrated+&
                (1-is_counterfactual)*model_average_labour_income(time_period)
            thread_num=0

            do m=1,2
                do age_index=1,life_span-1
                    if (age_index>(life_span-retirement_span)) then
                        in_retirement=1
                    else
                        in_retirement=0
                    end if
                    if (age_index>=(life_span-retirement_span)) then
                        at_least_one_period_before_retirement=1
                    else
                        at_least_one_period_before_retirement=0
                    end if
                    one_period_before_death=0
                    if (age_index==life_span) then
                        one_period_before_death=1
                    end if
                    if (age_index==1) then
                        newborn_household=1
                    else
                        newborn_household=0
                    end if
                    do years_left_on_mortgage_index=1,newborn_household*1+(1-newborn_household)*max_amortization_years
                        if (years_left_on_mortgage_index>1) then
                            rk_has_house=1
                        else
                            rk_has_house=0
                        end if
                        rk_track1=1
                        if (rk_has_house==0) then
                            if (track_renters_housing==0) then
                                rk_track1=0
                            end if
                        end if
                        do unemployment_index=1,unemployment_grid_size
                            do employment_index=1,employment_grid_size
                                rk_avg2=is_counterfactual*&
                                    average_labor_income_by_employment_calibrated(employment_index)+&
                                    (1-is_counterfactual)*model_average_labour_income_by_employment(time_period,employment_index)
                                do voucher_index=0,(1-rk_has_house)*voucher_state_max
                                    do rk_fin=newborn_household*negative_financial_grid_size+&
                                         (1-newborn_household)*(rk_has_house*1+(1-rk_has_house)*renter_floor_by_age(min(max(age_index,1),life_span))),&
                                         include_exogenous_endowment*financial_grid_size+(1-include_exogenous_endowment)*&
                                         (newborn_household*negative_financial_grid_size+(1-newborn_household)*financial_grid_size)
                                        do housing_status_index=(1-rk_has_house)*lowest_housing_grid_point+&
                                            rk_has_house*index_of_smallest_house_hhld_can_buy,&
                                            rk_track1*(1-newborn_household)*(housing_status_grid_size-1)

                                            rk_mass=src(years_left_on_mortgage_index)%vector_real(age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)
                                            if (rk_mass<=thresh) cycle

                                            if (policy_function_years_of_amortization_index(years_left_on_mortgage_index)%&
                                                vector_transition_integer(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)>1) then
                                                choose_to_own=1
                                            else
                                                choose_to_own=0
                                            end if

                                            income_to_use_4=2*((1-is_counterfactual)*median_income(time_period)+&
                                                is_counterfactual*median_income_calibrated)

                                            if (choose_to_own==0) then
                                                labor_supply_to_use=&
                                                    policy_function_labor_supply(years_left_on_mortgage_index)%&
                                                    vector_transition_real(time_period,age_index,rk_fin,&
                                                    unemployment_index,employment_index,housing_status_index,voucher_index)
                                                call calculate_income(unemployment_index,employment_index,income_to_use_4,&
                                                    rk_avg1,rk_avg2,labor_supply_to_use,in_retirement)
                                                income_to_use_4=income_to_use_4+&
                                                    (risk_free_rate(time_period)*max(financial_grid(rk_fin),0.d0)+unsecured_borrowing_rate*min(financial_grid(rk_fin),0.d0))
                                            end if

                                            track_housing_2=1
                                            if (choose_to_own==0) then
                                                if (track_renters_housing==0) then
                                                    track_housing_2=0
                                                end if
                                            end if

                                            if (m==1) then
                                                financial_index_copy=policy_function_financial_index&
                                                    (years_left_on_mortgage_index)%vector_transition_integer&
                                                    (time_period,age_index,rk_fin,unemployment_index,&
                                                    employment_index,housing_status_index,voucher_index)
                                                fraction_copy=(1-frac_mov_optimal_1(years_left_on_mortgage_index)%&
                                                    vector_transition_real(time_period,age_index,&
                                                    rk_fin,unemployment_index,employment_index,&
                                                    housing_status_index,voucher_index))
                                            elseif (m==2) then
                                                financial_index_copy=fin_index_frac_mov_to_optimal&
                                                    (years_left_on_mortgage_index)%vector_transition_integer&
                                                    (time_period,age_index,rk_fin,unemployment_index,&
                                                    employment_index,housing_status_index,voucher_index)
                                                fraction_copy=frac_mov_optimal_1(years_left_on_mortgage_index)%&
                                                    vector_transition_real(time_period,&
                                                    age_index,rk_fin,unemployment_index,employment_index,&
                                                    housing_status_index,voucher_index)
                                            end if

                                            amortization_used_dist=policy_function_years_of_amortization_index&
                                                (years_left_on_mortgage_index)%vector_transition_integer&
                                                (min(time_period,transition_length),age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)

                                            future_housing_status_index_to_use_2=&
                                                policy_function_housing_status_index(years_left_on_mortgage_index)%&
                                                vector_transition_integer(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)

                                            if (track_housing_2==0) then
                                                if (future_housing_status_index_to_use_2>second_lowest_housing_grid_point) then
                                                    future_housing_status_index_to_use_2=0
                                                end if
                                            end if

                                            is_homeless_2=1
                                            if (future_housing_status_index_to_use_2==lowest_housing_grid_point) then
                                                is_homeless_2=2
                                            end if

                                            call compute_voucher_index_1(is_homeless_2,&
                                                (policy_function_frac_spent_on_addiction(years_left_on_mortgage_index)%&
                                                vector_transition_real(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)),&
                                                rk_vi1)

                                            call calculate_future_voucher_index_and_opportunity&
                                                (has_opportunity_2,first_voucher_index_1,second_voucher_index_1,&
                                                time_period,rk_has_house,choose_to_own,rk_vi1,income_to_use_4)

                                            addiction_choice_1=&
                                                policy_function_addiction(years_left_on_mortgage_index)%&
                                                vector_transition_integer(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)

                                            treatment_choice_dist_1=&
                                                policy_function_treatment(years_left_on_mortgage_index)%&
                                                vector_transition_integer(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)

                                            drug_quantity_dist_1=&
                                                (policy_function_frac_spent_on_addiction(years_left_on_mortgage_index)%&
                                                vector_transition_real(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index)*&
                                                policy_function_total_consumption(years_left_on_mortgage_index)%&
                                                vector_transition_real(time_period,age_index,rk_fin,&
                                                unemployment_index,employment_index,housing_status_index,voucher_index))/&
                                                price_of_addictive_good

                                            rk_isadd=0
                                            loop_over_addiction_2=0
                                            if (unemployment_index>threshold_addiction_index) then
                                                rk_isadd=1
                                                loop_over_addiction_2=1
                                            elseif ((addiction_choice_1>=1) .AND. &
                                                (unemployment_index<=threshold_addiction_index) .AND. &
                                                (include_probability_of_becoming_addicted==1)) then
                                                loop_over_addiction_2=1
                                            end if

                                            rk_surv=survival_probability_for_dist_iteration&
                                                (age_index,is_homeless_2,&
                                                survival_sud_of(rk_isadd,treatment_choice_dist_1),&
                                                smi_of(unemployment_index))
                                            if (m==1) deaths_h=deaths_h+rk_mass*(1-rk_surv)

                                            do future_addiction_index_2=&
                                                (1-loop_over_addiction_2)*addiction_choice_1+loop_over_addiction_2*0,&
                                                (1-loop_over_addiction_2)*addiction_choice_1+loop_over_addiction_2*include_addiction
                                                check_2=0
                                                if (future_addiction_index_2==1) then
                                                    check_2=1
                                                end if
                                                do future_unemployment_index=include_addiction*&
                                                    ((1-check_2)*1+check_2*(threshold_addiction_index+1))+&
                                                    (1-include_addiction)*(at_least_one_period_before_retirement*&
                                                    (one_period_before_death*1+(1-one_period_before_death)*unemployment_index)+&
                                                    (1-at_least_one_period_before_retirement)*1),include_addiction*&
                                                    ((1-check_2)*threshold_addiction_index+check_2*unemployment_grid_size)+&
                                                    (1-include_addiction)*(at_least_one_period_before_retirement*&
                                                    (one_period_before_death*unemployment_grid_size+&
                                                    (1-one_period_before_death)*unemployment_index)+&
                                                    (1-at_least_one_period_before_retirement)*unemployment_grid_size)
                                                    do future_employment_index=&
                                                        at_least_one_period_before_retirement*employment_index+&
                                                        (1-at_least_one_period_before_retirement)*1,&
                                                        at_least_one_period_before_retirement*employment_index+&
                                                        (1-at_least_one_period_before_retirement)*employment_grid_size
                                                        do future_voucher_index=first_voucher_index_1,second_voucher_index_1
                                                            ! the kernel's product, in the kernel's order
                                                            rk_w=fraction_copy*survival_probability_for_dist_iteration&
                                                                (age_index,is_homeless_2,&
                                                                survival_sud_of(rk_isadd,treatment_choice_dist_1),&
                                                                smi_of(unemployment_index))*&
                                                                voucher_probabilities(voucher_index,&
                                                                future_voucher_index,has_opportunity_2,rk_vi1)*&
                                                                employment_process(age_index,employment_index,&
                                                                future_employment_index)*unemployment_process&
                                                                (age_index,unemployment_index,future_unemployment_index,&
                                                                is_homeless_2,future_addiction_index_2,employment_index)*&
                                                                addiction_transition(rk_isadd,&
                                                                future_addiction_index_2,addiction_choice_1,is_homeless_2,&
                                                                drug_quantity_dist_1,0,treatment_choice_dist_1,&
                                                                smi_of(unemployment_index))*rk_mass
                                                            dst(amortization_used_dist)%vector_real(age_index+1,&
                                                                financial_index_copy,future_unemployment_index,&
                                                                future_employment_index,future_housing_status_index_to_use_2,&
                                                                future_voucher_index)=dst(amortization_used_dist)%vector_real&
                                                                (age_index+1,financial_index_copy,future_unemployment_index,&
                                                                future_employment_index,future_housing_status_index_to_use_2,&
                                                                future_voucher_index)+rk_w
                                                            if ((do_tag==1) .AND. (voucher_index==1) .AND. &
                                                                (future_voucher_index==voucher_excl) .AND. (voucher_excl>=2)) then
                                                                tagbuf(amortization_used_dist)%vector_real(age_index+1,&
                                                                    financial_index_copy,future_unemployment_index,&
                                                                    future_employment_index,future_housing_status_index_to_use_2,&
                                                                    future_voucher_index)=tagbuf(amortization_used_dist)%vector_real&
                                                                    (age_index+1,financial_index_copy,future_unemployment_index,&
                                                                    future_employment_index,future_housing_status_index_to_use_2,&
                                                                    future_voucher_index)+rk_w
                                                            end if
                                                        end do
                                                    end do
                                                end do
                                            end do
                                        end do
                                    end do
                                end do
                            end do
                        end do
                    end do
                end do
            end do
            ! what the reduction would not copy leaves the model: an exit, booked with the end of life
            revk_leak_last=sum(dst(1)%vector_real,mask=.NOT.revk_mask_1)+sum(dst(2)%vector_real,mask=.NOT.revk_mask_2)
            where (.NOT. revk_mask_1) dst(1)%vector_real=0
            where (.NOT. revk_mask_2) dst(2)%vector_real=0
            if (do_tag==1) then
                where (.NOT. revk_mask_1) tagbuf(1)%vector_real=0
                where (.NOT. revk_mask_2) tagbuf(2)%vector_real=0
            end if
            deaths_e=deaths_e+revk_leak_last
        end subroutine

        subroutine revk_stats(x,alive,sud,hom,vhold,vexcl,meanage)
            type(jagged_matrix_real), dimension(1:2), intent(in) :: x
            real(8), intent(out) :: alive,sud,hom,vhold,vexcl,meanage
            integer :: rk_k,rk_a
            alive=0; sud=0; hom=0; vhold=0; vexcl=0; meanage=0
            do rk_k=1,2
                alive=alive+sum(x(rk_k)%vector_real)
                sud=sud+sum(x(rk_k)%vector_real(:,:,threshold_addiction_index+1:,:,:,:))
                if (lbound(x(rk_k)%vector_real,5)<=lowest_housing_grid_point) &
                    hom=hom+sum(x(rk_k)%vector_real(:,:,:,:,lowest_housing_grid_point,:))
                if (ubound(x(rk_k)%vector_real,6)>=1) vhold=vhold+sum(x(rk_k)%vector_real(:,:,:,:,:,1))
                if ((voucher_excl>=2) .AND. (ubound(x(rk_k)%vector_real,6)>=voucher_excl)) &
                    vexcl=vexcl+sum(x(rk_k)%vector_real(:,:,:,:,:,voucher_excl))
                do rk_a=lbound(x(rk_k)%vector_real,1),ubound(x(rk_k)%vector_real,1)
                    meanage=meanage+rk_a*sum(x(rk_k)%vector_real(rk_a,:,:,:,:,:))
                end do
            end do
            if (alive>0) then
                sud=sud/alive; hom=hom/alive; vhold=vhold/alive; vexcl=vexcl/alive; meanage=meanage/alive
            end if
        end subroutine

        subroutine revk_print_group(time_period,g)
            integer, intent(in) :: time_period,g
            real(8) :: alive,sud,hom,vhold,vexcl,meanage
            call revk_stats(revk_s(:,g),alive,sud,hom,vhold,vexcl,meanage)
            write(*,'(A,I3,A,I2,A,I3,13(A,ES23.15))') " REVK GROUP t=", time_period, " g=", g, " start=", revk_start(g), &
                " mass0=", revk_mass0(g), " alive=", alive, " cum_deaths_h=", revk_cum_h(g), &
                " cum_deaths_e=", revk_cum_e(g), " step_deaths_h=", revk_step_h(g), " step_deaths_e=", revk_step_e(g), &
                " sud=", sud, " homeless=", hom, " holding=", vhold, " excluded=", vexcl, " mean_age=", meanage, &
                " acct=", revk_acct(g), " acct_close=", (alive+revk_cum_h(g)+revk_cum_e(g)-revk_mass0(g))/max(revk_mass0(g),1.d-300)
        end subroutine

        subroutine revk_tagfile(c,mode_rw)
            integer, intent(in) :: c,mode_rw
            integer :: rk_u,rk_ios
            character(len=420) :: rk_name
            write(rk_name,'(A,A,I1,A)') trim(revk_tagdir), '/revk_tag_c', c, '.bin'
            if (mode_rw==1) then
                open(newunit=rk_u,file=trim(rk_name),access='stream',form='unformatted',status='replace',action='write')
                write(rk_u) revk_tagbuf(1)%vector_real, revk_tagbuf(2)%vector_real
                close(rk_u)
                write(*,*) "REVK TAG WRITTEN c=", c, " file=", trim(rk_name), " mass=", &
                    sum(revk_tagbuf(1)%vector_real)+sum(revk_tagbuf(2)%vector_real)
            else
                open(newunit=rk_u,file=trim(rk_name),access='stream',form='unformatted',status='old',action='read',iostat=rk_ios)
                if (rk_ios/=0) then
                    write(*,*) "REVK STOP: tag file missing: ", trim(rk_name)
                    stop
                end if
                read(rk_u,iostat=rk_ios) revk_s(1,c)%vector_real, revk_s(2,c)%vector_real
                close(rk_u)
                if (rk_ios/=0) then
                    write(*,*) "REVK STOP: tag file short: ", trim(rk_name)
                    stop
                end if
                write(*,*) "REVK TAG READ c=", c, " file=", trim(rk_name), " mass=", &
                    sum(revk_s(1,c)%vector_real)+sum(revk_s(2,c)%vector_real)
            end if
        end subroutine

        ! END OF FORWARD PERIOD t. price_faced: the price the period was solved and pushed at.
        subroutine revk_period(time_period,price_faced)
            integer, intent(in) :: time_period
            real(8), intent(in) :: price_faced
            integer :: rk_g,rk_k,rk_dotag
            real(8) :: rk_price_keep,rk_maxabs,rk_sumabs,rk_maxmass,rk_stat,rk_mass_prev
            real(8) :: alive,sud,hom,vhold,vexcl,meanage
            real(8) :: rk_cpu0,rk_cpu1

            if (.NOT. revk_ready) call revk_init()
            if (revk_mode==0) return
            if (loop_count/=0) return
            call cpu_time(rk_cpu0)
            rk_price_keep=price_of_addictive_good
            price_of_addictive_good=price_faced

            ! the holders at the reform: voucher state 1 in the t = 0 distribution (slot 0 is still in the window at t = 1)
            if (time_period==1) then
                do rk_k=1,2
                    revk_s(rk_k,4)%vector_real=0
                end do
                revk_s(1,4)%vector_real(:,:,:,:,:,1)=distribution_guess(1)%vector_transition_real(0,:,:,:,:,:,1)
                revk_mass0(4)=sum(revk_s(1,4)%vector_real)
                revk_active(4)=1
                revk_start(4)=0
                call revk_print_group(0,4)
            end if

            ! 1. every group already started moves one year on this period's kernel
            do rk_g=1,revk_ng
                if ((revk_active(rk_g)==1) .AND. (revk_start(rk_g)<time_period)) then
                    rk_mass_prev=sum(revk_s(1,rk_g)%vector_real)+sum(revk_s(2,rk_g)%vector_real)
                    call revk_step(time_period,revk_s(:,rk_g),revk_new,revk_step_h(rk_g),revk_step_e(rk_g),&
                        0.d0,revk_tagbuf,0)
                    revk_cum_h(rk_g)=revk_cum_h(rk_g)+revk_step_h(rk_g)
                    revk_cum_e(rk_g)=revk_cum_e(rk_g)+revk_step_e(rk_g)
                    write(*,'(A,I3,A,I2,A,ES23.15)') " REVK LEAK t=", time_period, " g=", rk_g, &
                        " dropped by the reduction (in deaths_e)=", revk_leak_last
                    do rk_k=1,2
                        revk_s(rk_k,rk_g)%vector_real=revk_new(rk_k)%vector_real
                    end do
                    revk_acct(rk_g)=(rk_mass_prev-revk_step_h(rk_g)-revk_step_e(rk_g)-&
                        sum(revk_s(1,rk_g)%vector_real)-sum(revk_s(2,rk_g)%vector_real))/max(revk_mass0(rk_g),1.d-300)
                end if
            end do

            ! 2. the whole population at t-1 through the same kernel: deaths, the kernel check, and (Treatment First,
            !    years 1-3) the revocation tag
            do rk_k=1,2
                revk_p(rk_k)%vector_real=distribution_guess(rk_k)%vector_transition_real(time_period-1,:,:,:,:,:,:)
                revk_tagbuf(rk_k)%vector_real=0
            end do
            rk_dotag=0
            if ((revk_mode==1) .AND. (time_period<=3)) rk_dotag=1
            call revk_step(time_period,revk_p,revk_new,revk_pop_h,revk_pop_e,negligible_mass,revk_tagbuf,rk_dotag)
            write(*,'(A,I3,A,ES23.15)') " REVK LEAK t=", time_period, " population, dropped by the reduction (in deaths_e)=", &
                revk_leak_last
            rk_maxabs=0; rk_sumabs=0; rk_maxmass=0; rk_stat=0
            do rk_k=1,2
                rk_maxabs=max(rk_maxabs,maxval(abs(revk_new(rk_k)%vector_real(2:,:,:,:,:,:)-&
                    distribution_guess(rk_k)%vector_transition_real(time_period,2:,:,:,:,:,:))))
                rk_sumabs=rk_sumabs+sum(abs(revk_new(rk_k)%vector_real(2:,:,:,:,:,:)-&
                    distribution_guess(rk_k)%vector_transition_real(time_period,2:,:,:,:,:,:)))
                rk_maxmass=max(rk_maxmass,maxval(distribution_guess(rk_k)%vector_transition_real(time_period,:,:,:,:,:,:)))
                rk_stat=rk_stat+sum(abs(distribution_guess(rk_k)%vector_transition_real(time_period,:,:,:,:,:,:)-&
                    distribution_guess(rk_k)%vector_transition_real(time_period-1,:,:,:,:,:,:)))
            end do
            do rk_k=1,2
                revk_p(rk_k)%vector_real=distribution_guess(rk_k)%vector_transition_real(time_period,:,:,:,:,:,:)
            end do
            call revk_stats(revk_p,alive,sud,hom,vhold,vexcl,meanage)
            write(*,'(A,I3,13(A,ES23.15))') " REVK POP t=", time_period, " alive=", alive, &
                " deaths_h=", revk_pop_h, " deaths_e=", revk_pop_e, " sud=", sud, " homeless=", hom, &
                " holding=", vhold, " excluded=", vexcl, " mean_age=", meanage, &
                " newborn_mass=", sum(distribution_guess(1)%vector_transition_real(time_period,1,:,:,:,:,:))+&
                    sum(distribution_guess(2)%vector_transition_real(time_period,1,:,:,:,:,:)), &
                " kernel_maxabs=", rk_maxabs, " kernel_sumabs=", rk_sumabs, " max_cell=", rk_maxmass, &
                " moved_from_tminus1_sumabs=", rk_stat

            ! 3. the cohort revoked in this year starts here
            if ((time_period>=1) .AND. (time_period<=3)) then
                rk_g=time_period
                if (revk_mode==1) then
                    do rk_k=1,2
                        revk_s(rk_k,rk_g)%vector_real=revk_tagbuf(rk_k)%vector_real
                    end do
                    call revk_tagfile(rk_g,1)
                else
                    call revk_tagfile(rk_g,2)
                    ! KEPT THE VOUCHER: the same mass, voucher state 1 instead of voucher_excl
                    if (voucher_excl>=2) then
                        revk_s(1,rk_g)%vector_real(:,:,:,:,:,1)=revk_s(1,rk_g)%vector_real(:,:,:,:,:,1)+&
                            revk_s(1,rk_g)%vector_real(:,:,:,:,:,voucher_excl)
                        revk_s(1,rk_g)%vector_real(:,:,:,:,:,voucher_excl)=0
                    end if
                end if
                revk_mass0(rk_g)=sum(revk_s(1,rk_g)%vector_real)+sum(revk_s(2,rk_g)%vector_real)
                revk_active(rk_g)=1
                revk_start(rk_g)=time_period
                revk_step_h(rk_g)=0; revk_step_e(rk_g)=0; revk_acct(rk_g)=0
            end if

            do rk_g=1,revk_ng
                if (revk_active(rk_g)==1) call revk_print_group(time_period,rk_g)
            end do

            price_of_addictive_good=rk_price_keep
            call cpu_time(rk_cpu1)
            write(*,*) "REVK PERIOD DONE t=", time_period, " cpu seconds=", rk_cpu1-rk_cpu0
        end subroutine

    end module revk_track

'''

PROG = '    program main_program\n'
t = rep(plain, PROG, MODULE + PROG)

# use the module in transition_simulation
TS = '    subroutine transition_simulation()\n'
i = t.index(TS)
j = t.index('use Global_Vars', i)
k = t.index('\n', j)
assert j - i < 200
t = t[:k + 1] + '        use revk_track\n' + t[k + 1:]

# init before the forward pass
t = rep(t, '            write(*,*) "computing distributions and statistics"\n',
        '            write(*,*) "computing distributions and statistics"\n'
        '            if (loop_count==0) call revk_init()\n')

# at the end of each forward period
import re
m = re.search(r'\n( *end do\n\s*\n *! EACH YEAR\'S PRICE STEP BLENDED WITH ITS NEIGHBOURS\' \(transition fix item 10b\)\.\n)', t)
assert m and t.count(m.group(1)) == 1, "period-end anchor"
t = t.replace(m.group(1), '                call revk_period(time_index,tr_price_before_1(time_index))\n\n' + m.group(1))
open(out_track, 'w').write(t)
print("written", out_plain, out_track)
