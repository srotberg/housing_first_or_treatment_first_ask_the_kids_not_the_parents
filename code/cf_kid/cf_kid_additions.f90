
    ! =========================================================================
    ! >>> CF_KID ADDITIONS (code/cf_kid, 2 October) -- everything from here to
    ! the matching "<<< CF_KID ADDITIONS" line is new; nothing above it changed
    ! except the one-line hook in long_run_counter_factual. <<<
    !
    ! THE NEWBORN'S OWN EX-ANTE VALUE, BY THE HOUSEHOLD IT IS BORN INTO.
    !
    ! The paper's newborn welfare is an AVERAGE: the cross-sectional childhood
    ! average of calculate_childhood_utility plus beta^J_K times the average
    ! value of the households entering at model age one. There is no value per
    ! newborn in it, so "what share of newborns is better off under Treatment
    ! First" cannot be read off it. This builds one.
    !
    ! For the parent's state s at parent ages j = J_K down to 1:
    !
    !   W(J_K,s) = c(J_K,s) + beta*A(J_K,s)
    !   W(j,s)   = c(j,s)   + beta*[ phi_j(s)*E[W(j+1,s')|s] + (1-phi_j(s))*A(j,s) ]
    !
    ! c(j,s) is the child's own flow at that state under the parent's policy,
    ! child_flow_out exactly as calculate_childhood_utility computes it, less
    ! kappa_x*H. phi_j(s) is survival_probability_for_dist_iteration, the
    ! survival the forward law of motion uses. E[.|s] is the TRANSPOSE of the
    ! law of motion in converge_to_stationary_equilibrium: the same policy
    ! reads, the same two-point asset split, the same voucher, employment,
    ! unemployment and addiction branches, with mass accumulation turned into
    ! expectation accumulation. A(j,s) is the child's expected value on entry at
    ! model age one given the parent's state when it leaves: the productivity
    ! draw newborn_employment_probability(.,e,ever_sud(s),homeless(s)), the SMI
    ! draw at birth and the entry asset point the law of motion uses, valued at
    ! the child's OWN value function at age one (not weighted by omega_c).
    !
    ! TIMING, read off the code rather than assumed:
    !   * calculate_childhood_utility discounts the child's own age a by
    !     beta^(a-1) and the adult value at age one by beta^J_K, so the child
    !     enters one period after its last childhood period: W(J_K) carries
    !     beta*A. A parent that dies between j and j+1 sends the child in at
    !     j+1, so the death branch is beta*(1-phi_j)*A(j,s) -- the same beta and
    !     the same (1-phi) child_continuation_value prices in the parent's
    !     problem.
    !   * the penalty keys on ever_sud_of(u) of the parent's state AT THE START
    !     of the period it dies in or reaches J_K (newborn_parent_share_acc and
    !     child_continuation_value), and the homeless dimension on the housing
    !     the parent's policy chooses in that period.
    !   * phi is the law of motion's survival, so mass and expectation agree;
    !     survival_sud_of(d,t)=d, so treatment does not enter it.
    !   * compute_voucher_index_1 reads the module treatment_choice_now, which
    !     every renter branch of the solve resets to 0 before returning, so the
    !     law of motion always sees 0. That is mirrored by setting it to 0 here.
    !
    ! THREE COMPANION RECURSIONS RUN IN THE SAME PASS, for validation only:
    !   Wnd -- W with the parent's mortality before J_K set to zero (phi=1, no
    !          early entry), the object the cross-sectional measure is closest to;
    !   Wc  -- the childhood-flow part of W alone (death ends the flows), so
    !          W - Wc is the discounted expected entry value;
    !   K   -- c(j,s)/M_j + beta*phi*E[K(j+1)]: its Phi_1-weighted sum equals the
    !          code's own average_childhood_utility EXACTLY if the saved
    !          distribution is a fixed point of this transpose's law of motion.
    ! And a FORWARD PUSH of the saved distribution through the same weights,
    ! age by age, compared with the saved distribution at the next age.
    ! =========================================================================

    subroutine cf_kid_open_read(unit_1,name_1)

        implicit none

        integer, intent(in) :: unit_1
        character(len=*), intent(in) :: name_1
        integer :: ios_1

        open(unit=unit_1,file=trim(name_1),status='old',action='read',iostat=ios_1)

        if (ios_1/=0) then

            write(*,*) "CF_KID GUARD: cannot open ", trim(name_1)
            stop 2

        end if

    end subroutine cf_kid_open_read

    ! A saved array is a bare list of numbers. Too few records is an error
    ! (iostat), and so is one too MANY: a file from a bigger state space read
    ! whole into a smaller array would otherwise succeed and return a prefix of
    ! another layout (TRANSITION_LESSONS.md section 7).
    subroutine cf_kid_check_end(unit_1,name_1,ios_1)

        implicit none

        integer, intent(in) :: unit_1,ios_1
        character(len=*), intent(in) :: name_1
        character(len=80) :: extra_1
        integer :: ios_2

        if (ios_1/=0) then

            write(*,*) "CF_KID GUARD: short or unreadable file ", trim(name_1), " iostat=", ios_1
            stop 2

        end if

        read(unit_1,'(A)',iostat=ios_2) extra_1

        if ((ios_2==0) .AND. (len_trim(extra_1)>0)) then

            write(*,*) "CF_KID GUARD: ", trim(name_1), " has MORE records than the array -- wrong layout"
            stop 2

        end if

        close(unit_1)

    end subroutine cf_kid_check_end

    subroutine cf_kid_load_equilibrium(read_tag_1)

        use Global_Vars

        implicit none

        character(len=*), intent(in) :: read_tag_1
        character*1 :: s_1
        character(len=300) :: f_1
        integer :: i_1,ios_1

        do i_1=1,2

            write(s_1,'(i1)') i_1

            f_1="value_function"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F35.13)',iostat=ios_1) value_function(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="distribution_stationary"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F30.28)',iostat=ios_1) distribution_stationary(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_space_lived_in_size"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F25.20)',iostat=ios_1) policy_function_space_lived_in_size(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_labor_supply"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F22.20)',iostat=ios_1) policy_function_labor_supply(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_total_consumption"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F26.20)',iostat=ios_1) policy_function_total_consumption(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_consumption"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F26.20)',iostat=ios_1) policy_function_consumption(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_frac_spent_on_addiction"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F25.20)',iostat=ios_1) policy_function_frac_spent_on_addiction(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_years_of_amortization_index"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I2)',iostat=ios_1) policy_function_years_of_amortization_index(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_housing_status_index"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I2)',iostat=ios_1) policy_function_housing_status_index(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_financial_index"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I3)',iostat=ios_1) policy_function_financial_index(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="fin_index_frac_mov_to_optimal"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I3)',iostat=ios_1) fin_index_frac_mov_to_optimal(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_addiction"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I1)',iostat=ios_1) policy_function_addiction(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="policy_function_treatment"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(I1)',iostat=ios_1) policy_function_treatment(i_1)%vector_transition_integer(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            f_1="frac_mov_optimal_1"//s_1//trim(read_tag_1)//".dat"
            call cf_kid_open_read(91,f_1)
            read(91,'(F22.20)',iostat=ios_1) frac_mov_optimal_1(i_1)%vector_transition_real(:,:,:,:,:,:,:)
            call cf_kid_check_end(91,f_1,ios_1)

            write(*,*) "CF_KID loaded slot ", i_1, " of the saved equilibrium ", trim(read_tag_1)

        end do

    end subroutine cf_kid_load_equilibrium

    ! Called from long_run_counter_factual in place of its loop, after every
    ! initialiser the loop needs has run (handover, grids, processes, benchmark
    ! imports), so the economy is set up exactly as the arm's own run set it up.
    ! The drug price and pi_V of the arm's LAST SOLVE arrive through the
    ! handover (drug_price_start, probability_of_voucher_benchmark_used), which
    ! run_child_value.sh reads out of the arm's cf.log.
    subroutine child_value_from_saved_equilibrium(time_period)

        use Global_Vars

        implicit none

        integer, intent(in) :: time_period
        character(len=200) :: read_tag_1,out_tag_1,env_1
        integer :: st_1
        real(8) :: t0_1,t1_1

        call cpu_time(t0_1)

        if (number_of_beta_types/=1) then

            write(*,*) "CF_KID GUARD: number_of_beta_types=", number_of_beta_types, &
                " -- the recursion is written for one discount factor"
            stop 2

        end if

        if (max_amortization_years/=1) then

            write(*,*) "CF_KID GUARD: owners are back in the model; the recursion covers renters only"
            stop 2

        end if

        read_tag_1=trim(file_number)
        call get_environment_variable("CF_KID_READ_TAG",env_1,status=st_1)
        if ((st_1==0) .AND. (len_trim(env_1)>0)) read_tag_1=trim(env_1)

        out_tag_1=trim(read_tag_1)
        call get_environment_variable("CF_KID_OUT_TAG",env_1,status=st_1)
        if ((st_1==0) .AND. (len_trim(env_1)>0)) out_tag_1=trim(env_1)

        write(*,*) "CF_KID: price_of_addictive_good=", price_of_addictive_good
        write(*,*) "CF_KID: probability_of_voucher_benchmark_used_1=", probability_of_voucher_benchmark_used_1
        write(*,*) "CF_KID: increase_in_labour_income_tax=", increase_in_labour_income_tax
        write(*,*) "CF_KID: discount_factor=", discount_factor, " kappa_x=", kappa_x, &
            " weight_on_child=", weight_on_child
        write(*,*) "CF_KID: reading the saved equilibrium tagged ", trim(read_tag_1)

        call cf_kid_load_equilibrium(read_tag_1)

        call cpu_time(t1_1)
        write(*,*) "CF_KID TIMING load (cpu s)=", t1_1-t0_1

        ! THE CODE'S OWN WELFARE ON THE LOADED STATE, as the loop calls it:
        ! statistics (for H and the parent shares), then the two welfare routines.
        ! These must reproduce the arm's last printed numbers, which is the check
        ! that the reload is the equilibrium.
        call stationary_equilibrium_statistics(time_period)
        call calculate_welfare(time_period)
        call calculate_childhood_utility(time_period)

        write(*,'(A,ES24.16)') " CF_KID RECON model_fraction_homeless=", model_fraction_homeless(time_period)
        write(*,'(A,ES24.16)') " CF_KID RECON average_welfare_of_youngest_cohort=", &
            average_welfare_of_youngest_cohort(time_period)
        write(*,'(A,ES24.16)') " CF_KID RECON average_childhood_utility=", average_childhood_utility(time_period)
        write(*,'(A,ES24.16)') " CF_KID RECON average_welfare_with_childhood=", &
            average_welfare_with_childhood(time_period)

        call compute_child_value_at_birth(time_period,out_tag_1)

        call cpu_time(t1_1)
        write(*,*) "CF_KID TIMING total (cpu s, summed over threads)=", t1_1-t0_1
        write(*,*) "CF_KID DONE"

        stop

    end subroutine child_value_from_saved_equilibrium

    subroutine compute_child_value_at_birth(time_period,out_tag_1)

        use Global_Vars
        use, intrinsic :: ieee_exceptions
        !$ use omp_lib

        implicit none

        integer, intent(in) :: time_period
        character(len=*), intent(in) :: out_tag_1

        integer, parameter :: JK=child_at_home_last_index
        real(8), parameter :: sentinel_1=-9999999999.d0

        real(8), allocatable, dimension(:,:,:,:,:,:) :: w_a,wc_a,wnd_a,k_a,c_a
        integer(1), allocatable, dimension(:,:,:,:,:,:) :: ok_a
        real(8), allocatable, dimension(:,:,:,:,:,:) :: fwd_a
        real(8), allocatable, dimension(:,:,:,:,:) :: fwdsum_a

        real(8), dimension(employment_grid_size) :: vchild_1
        real(8), dimension(employment_grid_size,0:1,1:2) :: ea_1
        real(8), dimension(threshold_addiction_index) :: state_w_1
        real(8), dimension(JK) :: mass_age_1,l1_age_1,maxd_age_1,fmass_age_1
        real(8) :: smi_birth_1,w_ie_1,w_neg_1,tot_1,beta_1,kh_1,mass_1,flow_discard_1
        real(8) :: avg_w_1,avg_wc_1,avg_wnd_1,avg_k_1,avg_v1_1,m1_1,eamix_1,avg_ea1_1
        real(8) :: d_1,dd_1,sum_n_1,sum_dw_1,rel_1
        integer :: fl_1,fh_1,flo_1,hhi_1,j_1,u_1,e_1,v_1,h_1,fin_1,node_1,d_i,h_i,ue_1
        integer :: nthr_1,tid_1,t_1,newborn_1,years_1,housing_1,addiction_used_1
        integer :: n_bad_cons_1,n_nonfinite_1,n_viol_1,n_cmp_1,n_lower_1,cls_1,emp_1,smi_1
        integer :: unit_1,st_1
        real(8) :: space_1,frac_spent_1,total_consumption_1,consumption_1,bad_cons_mass_1
        character(len=300) :: f_1,env_1
        logical :: all_ages_1
        real(8) :: t0_1,t1_1
        integer(8) :: c0_1,c1_1,crate_1
        logical :: invalid_before_1,invalid_after_1
        integer :: n_nonfinite_all_1,n_nonfinite_c_1,n_unreached_dev_1
        real(8) :: max_ptot_dev_all_1
        real(8) :: sum_dwnd_1
        integer :: n_lower_nd_1

        ! per-state temporaries of the parallel region
        integer :: choose_l,track_l,amort_l,hp_l,ish_l,vidx_l,opp_l,fv1_l,fv2_l,ach_l,trt_l
        integer :: isadd_l,loopadd_l,m_l,finp_l,fa_l,chk_l,up_lo_l,up_hi_l,ep_lo_l,ep_hi_l
        integer :: upr_l,epr_l,vpr_l,smi_l,ever_l
        real(8) :: inc_l,ls_l,dq_l,frac_l,phi_l,at_l,upp_l,epp_l,vpp_l,wgt_l,mass_l
        real(8) :: ew_l,ewc_l,ewnd_l,ek_l,ptot_l,lost_l,eas_l,cK_l,avg1_l,avg2_l
        real(8) :: max_ptot_dev_1,lost_total_1,lost_mass_1
        real(8), allocatable, dimension(:,:,:,:,:) :: ptot_a,lost_a

        call system_clock(c0_1,crate_1)
        call cpu_time(t0_1)

        ! Whether THIS routine raises the IEEE invalid flag (master thread). A
        ! procedure that uses ieee_exceptions starts with its flags quiet and
        ! restores the caller's on return, so the "Note: ... IEEE_INVALID_FLAG"
        ! printed at STOP, if any, comes from the code's own initialisers and
        ! statistics run before this point, not from here.
        invalid_before_1=.FALSE.

        fl_1=lbound(value_function(1)%vector_transition_real,3)
        fh_1=financial_grid_size
        beta_1=discount_factor
        kh_1=kappa_x*model_fraction_homeless(time_period)

        if (track_renters_housing/=0) then

            write(*,*) "CF_KID GUARD: track_renters_housing=1 -- the housing domain below assumes 0"
            stop 2

        end if

        nthr_1=1
        !$ nthr_1=max(1,omp_get_max_threads())

        all_ages_1=.FALSE.
        call get_environment_variable("CF_KID_ALL_AGES",env_1,status=st_1)
        if ((st_1==0) .AND. (trim(env_1)=="1")) all_ages_1=.TRUE.

        allocate(w_a(fl_1:fh_1,unemployment_grid_size,employment_grid_size,&
            lowest_housing_grid_point:housing_status_grid_size-1,0:voucher_state_max,JK))
        allocate(wc_a,mold=w_a)
        allocate(wnd_a,mold=w_a)
        allocate(k_a,mold=w_a)
        allocate(c_a,mold=w_a)
        allocate(ok_a(fl_1:fh_1,unemployment_grid_size,employment_grid_size,&
            lowest_housing_grid_point:housing_status_grid_size-1,0:voucher_state_max,JK))
        allocate(fwd_a(fl_1:fh_1,unemployment_grid_size,employment_grid_size,&
            lowest_housing_grid_point:housing_status_grid_size-1,0:voucher_state_max,0:nthr_1-1))
        allocate(fwdsum_a(fl_1:fh_1,unemployment_grid_size,employment_grid_size,&
            lowest_housing_grid_point:housing_status_grid_size-1,0:voucher_state_max))
        allocate(ptot_a,mold=fwdsum_a)
        allocate(lost_a,mold=fwdsum_a)

        w_a=sentinel_1
        wc_a=sentinel_1
        wnd_a=sentinel_1
        k_a=sentinel_1
        c_a=0
        ok_a=0

        ! ---------------------------------------------------------------
        ! 1. THE CHILD'S FLOW AT EVERY STATE OF AGES 1..J_K, as
        !    calculate_childhood_utility computes it, less kappa_x*H. The domain
        !    is the law of motion's: renters, the housing state collapsed to
        !    {street, housed} (track_renters_housing=0), assets from the age's
        !    floor. A cell whose policy is unsolved (consumption<=0) is outside.
        ! ---------------------------------------------------------------
        want_child_flow=.TRUE.
        n_bad_cons_1=0
        bad_cons_mass_1=0
        mass_age_1=0
        years_left_on_mortgage_index=1

        do j_1=1,JK

            age_index=j_1
            in_retirement=0
            if (age_index>(life_span-retirement_span)) in_retirement=1
            newborn_1=0
            if (j_1==1) newborn_1=1
            flo_1=newborn_1*negative_financial_grid_size+(1-newborn_1)*renter_floor_by_age(j_1)
            hhi_1=0

            do u_1=1,unemployment_grid_size
                unemployment_index=u_1
                do e_1=1,employment_grid_size
                    employment_index=e_1
                    do v_1=0,voucher_state_max
                        voucher_index=v_1
                        do fin_1=flo_1,fh_1
                            do h_1=lowest_housing_grid_point,hhi_1

                                mass_1=distribution_stationary(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                consumption_1=policy_function_consumption(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                if (consumption_1<=0.d0) then
                                    n_bad_cons_1=n_bad_cons_1+1
                                    bad_cons_mass_1=bad_cons_mass_1+max(mass_1,0.d0)
                                    cycle
                                end if

                                years_1=policy_function_years_of_amortization_index(1)%vector_transition_integer(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                housing_1=policy_function_housing_status_index(1)%vector_transition_integer(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                addiction_used_1=policy_function_addiction(1)%vector_transition_integer(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                total_consumption_1=policy_function_total_consumption(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                frac_spent_1=policy_function_frac_spent_on_addiction(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                space_1=policy_function_space_lived_in_size(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                flow_discard_1=0
                                child_flow_out=0
                                call calculate_flow_utility(0,housing_1,space_1,frac_spent_1,total_consumption_1,&
                                    consumption_1,merge(1,0,years_1>1),addiction_used_1,flow_discard_1,0)

                                c_a(fin_1,u_1,e_1,h_1,v_1,j_1)=child_flow_out-kh_1
                                ok_a(fin_1,u_1,e_1,h_1,v_1,j_1)=1
                                if (mass_1>0.d0) mass_age_1(j_1)=mass_age_1(j_1)+mass_1

                            end do
                        end do
                    end do
                end do
            end do

        end do

        want_child_flow=.FALSE.

        write(*,*) "CF_KID cells in the domain with no solved policy (consumption<=0):", n_bad_cons_1, &
            " their mass:", bad_cons_mass_1
        write(*,*) "CF_KID mass by child age (M_a), a=1,5,10,25:", mass_age_1(1), mass_age_1(5), &
            mass_age_1(10), mass_age_1(JK)

        ! ---------------------------------------------------------------
        ! 2. THE CHILD'S VALUE ON ENTERING AS A HOUSEHOLD, by its own node and
        !    then by its parent's (node, ever-SUD, homeless). The entry point is
        !    the law of motion's newborn row: model age one, housing 0, voucher
        !    0, the SMI draw at birth, and the endowment rule (fraction
        !    fraction_with_positive_wealth at initial_endowment, the rest at the
        !    zero asset point -- with the code's overwrite when the two points
        !    coincide). Normalised, so A is an expectation.
        ! ---------------------------------------------------------------
        smi_birth_1=0
        if ((number_of_smi_states>1) .AND. (allocated(smi_prevalence_by_age))) smi_birth_1=smi_prevalence_by_age(1)
        state_w_1=0
        state_w_1(idx_of(1,0,0,0))=1-smi_birth_1
        if (number_of_smi_states>1) state_w_1(idx_of(1,1,0,0))=smi_birth_1

        do node_1=1,employment_grid_size

            w_ie_1=0
            w_neg_1=1-fraction_with_positive_wealth(node_1)

            if ((include_exogenous_endowment==1) .AND. &
                (initial_endowment(node_1)/=negative_financial_grid_size)) then

                w_ie_1=fraction_with_positive_wealth(node_1)

            end if

            tot_1=w_ie_1+w_neg_1

            if (tot_1<=0.d0) then

                write(*,*) "CF_KID WARNING: the newborn row puts no mass at node", node_1, &
                    " (endowment overwrite); valuing it at the zero asset point"
                w_neg_1=1
                w_ie_1=0
                tot_1=1

            end if

            vchild_1(node_1)=0

            do u_1=1,threshold_addiction_index

                if (state_w_1(u_1)<=0.d0) cycle

                vchild_1(node_1)=vchild_1(node_1)+state_w_1(u_1)*(w_neg_1*&
                    value_function(1)%vector_transition_real(1,1,negative_financial_grid_size,u_1,node_1,0,0))/tot_1

                if (w_ie_1>0.d0) vchild_1(node_1)=vchild_1(node_1)+state_w_1(u_1)*(w_ie_1*&
                    value_function(1)%vector_transition_real(1,1,initial_endowment(node_1),u_1,node_1,0,0))/tot_1

            end do

        end do

        ea_1=0

        do d_i=0,1
            do h_i=1,2
                do e_1=1,employment_grid_size
                    ea_1(e_1,d_i,h_i)=sum(newborn_employment_probability(:,e_1,d_i,h_i)*vchild_1(:))
                end do
            end do
        end do

        ! The newborn mixture the law of motion actually draws from, priced at A.
        ! It should equal the cross-sectional average V at age one up to the
        ! distribution tolerance (it is the same mixture, one pass apart).
        eamix_1=0
        do d_i=0,1
            do h_i=1,2
                eamix_1=eamix_1+sum(newborn_parent_share(:,d_i,h_i)*ea_1(:,d_i,h_i))
            end do
        end do

        write(*,*) "CF_KID smi at birth=", smi_birth_1, " entry asset point=", negative_financial_grid_size
        write(*,*) "CF_KID fraction_with_positive_wealth(1)=", fraction_with_positive_wealth(1), &
            " initial_endowment(1)=", initial_endowment(1)
        write(*,'(A,26F12.4)') " CF_KID Vchild(node)=", vchild_1
        write(*,'(A,26F12.4)') " CF_KID A(parent node, clean, housed)=", ea_1(:,0,1)
        write(*,'(A,26F12.4)') " CF_KID A(parent node, ever-SUD, housed)=", ea_1(:,1,1)

        ! ---------------------------------------------------------------
        ! 3. THE BACKWARD PASS. Terminal at J_K, then the transposed law of
        !    motion from J_K-1 down to 1, with the forward push alongside.
        ! ---------------------------------------------------------------
        max_ptot_dev_1=0
        max_ptot_dev_all_1=0
        n_unreached_dev_1=0
        lost_total_1=0
        lost_mass_1=0
        l1_age_1=0
        maxd_age_1=0
        fmass_age_1=0
        treatment_choice_now=0

        do j_1=JK,1,-1

            age_index=j_1
            in_retirement=0
            if (age_index>(life_span-retirement_span)) in_retirement=1
            at_least_one_period_before_retirement=0
            if (age_index>=(life_span-retirement_span)) at_least_one_period_before_retirement=1
            one_period_before_death=0
            if (age_index==life_span) one_period_before_death=1
            newborn_1=0
            if (j_1==1) newborn_1=1
            newborn_household=newborn_1
            years_left_on_mortgage_index=1
            flo_1=newborn_1*negative_financial_grid_size+(1-newborn_1)*renter_floor_by_age(j_1)
            hhi_1=0

            fwd_a=0
            ptot_a=1
            lost_a=0

            do u_1=1,unemployment_grid_size

                unemployment_index=u_1

                do e_1=1,employment_grid_size

                    employment_index=e_1
                    avg1_l=average_labor_income_calibrated
                    avg2_l=average_labor_income_by_employment_calibrated(e_1)

                    do v_1=0,voucher_state_max

                        voucher_index=v_1

                        !$omp parallel do default(none) schedule(dynamic,1) &
                        !$omp& shared(j_1,u_1,e_1,v_1,flo_1,fh_1,hhi_1,fl_1,beta_1,mass_age_1,&
                        !$omp& w_a,wc_a,wnd_a,k_a,c_a,ok_a,fwd_a,ptot_a,lost_a,ea_1,avg1_l,avg2_l,&
                        !$omp& distribution_stationary,policy_function_years_of_amortization_index,&
                        !$omp& policy_function_labor_supply,policy_function_housing_status_index,&
                        !$omp& policy_function_frac_spent_on_addiction,policy_function_addiction,&
                        !$omp& policy_function_treatment,policy_function_total_consumption,&
                        !$omp& policy_function_financial_index,fin_index_frac_mov_to_optimal,frac_mov_optimal_1,&
                        !$omp& financial_grid,risk_free_rate,unsecured_borrowing_rate,median_income_calibrated,&
                        !$omp& in_retirement,at_least_one_period_before_retirement,one_period_before_death,&
                        !$omp& survival_probability_for_dist_iteration,voucher_probabilities,employment_process,&
                        !$omp& unemployment_process,price_of_addictive_good,renter_floor_by_age) &
                        !$omp& private(fin_1,h_1,tid_1,choose_l,track_l,amort_l,hp_l,ish_l,vidx_l,opp_l,fv1_l,fv2_l,&
                        !$omp& ach_l,trt_l,isadd_l,loopadd_l,m_l,finp_l,fa_l,chk_l,up_lo_l,up_hi_l,ep_lo_l,ep_hi_l,&
                        !$omp& upr_l,epr_l,vpr_l,smi_l,ever_l,inc_l,ls_l,dq_l,frac_l,phi_l,at_l,upp_l,epp_l,vpp_l,&
                        !$omp& wgt_l,mass_l,ew_l,ewc_l,ewnd_l,ek_l,ptot_l,lost_l,eas_l,cK_l)
                        do fin_1=flo_1,fh_1

                            tid_1=0
                            !$ tid_1=omp_get_thread_num()
                            treatment_choice_now=0

                            do h_1=lowest_housing_grid_point,hhi_1

                                if (ok_a(fin_1,u_1,e_1,h_1,v_1,j_1)==0) cycle

                                mass_l=distribution_stationary(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                ! ---- the law of motion's per-state block, verbatim in substance ----
                                choose_l=0
                                if (policy_function_years_of_amortization_index(1)%vector_transition_integer&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1)>1) choose_l=1

                                inc_l=2*median_income_calibrated

                                if (choose_l==0) then

                                    ls_l=policy_function_labor_supply(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                    call calculate_income(u_1,e_1,inc_l,avg1_l,avg2_l,ls_l,in_retirement)

                                    inc_l=inc_l+(risk_free_rate(1)*max(financial_grid(fin_1),0.d0)+&
                                        unsecured_borrowing_rate*min(financial_grid(fin_1),0.d0))

                                end if

                                track_l=1
                                if ((choose_l==0) .AND. (track_renters_housing==0)) track_l=0

                                amort_l=policy_function_years_of_amortization_index(1)%vector_transition_integer&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                hp_l=policy_function_housing_status_index(1)%vector_transition_integer&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1)

                                if ((track_l==0) .AND. (hp_l>second_lowest_housing_grid_point)) hp_l=0

                                ish_l=1
                                if (hp_l==lowest_housing_grid_point) ish_l=2

                                ! is_homeless as the PARENT-SHARE accumulator sees it (housing
                                ! policy, before the tracking collapse; identical for the street)
                                eas_l=ea_1(e_1,ever_sud_of(u_1),ish_l)

                                isadd_l=0
                                if (u_1>threshold_addiction_index) isadd_l=1

                                ach_l=policy_function_addiction(1)%vector_transition_integer(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                trt_l=policy_function_treatment(1)%vector_transition_integer(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                smi_l=smi_of(u_1)

                                phi_l=survival_probability_for_dist_iteration(j_1,ish_l,survival_sud_of(isadd_l,trt_l),smi_l)

                                if (j_1==JK) then

                                    ! THE CHILD LEAVES AT J_K WHETHER OR NOT THE PARENT SURVIVES.
                                    w_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)+beta_1*eas_l
                                    wc_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)
                                    wnd_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)+beta_1*eas_l
                                    k_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)/&
                                        max(mass_age_1(j_1),10.d0**(-300))
                                    cycle

                                end if

                                call compute_voucher_index_1(ish_l,&
                                    policy_function_frac_spent_on_addiction(1)%vector_transition_real&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1),vidx_l)

                                call calculate_future_voucher_index_and_opportunity&
                                    (opp_l,fv1_l,fv2_l,1,0,choose_l,vidx_l,inc_l)

                                dq_l=(policy_function_frac_spent_on_addiction(1)%vector_transition_real&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1)*&
                                    policy_function_total_consumption(1)%vector_transition_real&
                                    (1,j_1,fin_1,u_1,e_1,h_1,v_1))/price_of_addictive_good

                                loopadd_l=0
                                if (u_1>threshold_addiction_index) then
                                    loopadd_l=1
                                elseif ((ach_l>=1) .AND. (u_1<=threshold_addiction_index) .AND. &
                                    (include_probability_of_becoming_addicted==1)) then
                                    loopadd_l=1
                                end if

                                ew_l=0
                                ewc_l=0
                                ewnd_l=0
                                ek_l=0
                                ptot_l=0
                                lost_l=0

                                do m_l=1,2

                                    if (m_l==1) then
                                        finp_l=policy_function_financial_index(1)%vector_transition_integer&
                                            (1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                        frac_l=1-frac_mov_optimal_1(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                    else
                                        finp_l=fin_index_frac_mov_to_optimal(1)%vector_transition_integer&
                                            (1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                        frac_l=frac_mov_optimal_1(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                    end if

                                    if (frac_l==0.d0) cycle

                                    do fa_l=(1-loopadd_l)*ach_l+loopadd_l*0,&
                                        (1-loopadd_l)*ach_l+loopadd_l*include_addiction

                                        at_l=addiction_transition(isadd_l,fa_l,ach_l,ish_l,dq_l,0,trt_l,smi_l)

                                        if (at_l==0.d0) cycle

                                        chk_l=0
                                        if (fa_l==1) chk_l=1

                                        up_lo_l=include_addiction*((1-chk_l)*1+chk_l*(threshold_addiction_index+1))+&
                                            (1-include_addiction)*(at_least_one_period_before_retirement*&
                                            (one_period_before_death*1+(1-one_period_before_death)*u_1)+&
                                            (1-at_least_one_period_before_retirement)*1)
                                        up_hi_l=include_addiction*&
                                            ((1-chk_l)*threshold_addiction_index+chk_l*unemployment_grid_size)+&
                                            (1-include_addiction)*(at_least_one_period_before_retirement*&
                                            (one_period_before_death*unemployment_grid_size+&
                                            (1-one_period_before_death)*u_1)+&
                                            (1-at_least_one_period_before_retirement)*unemployment_grid_size)

                                        ep_lo_l=at_least_one_period_before_retirement*e_1+&
                                            (1-at_least_one_period_before_retirement)*1
                                        ep_hi_l=at_least_one_period_before_retirement*e_1+&
                                            (1-at_least_one_period_before_retirement)*employment_grid_size

                                        do upr_l=up_lo_l,up_hi_l

                                            upp_l=unemployment_process(j_1,u_1,upr_l,ish_l,fa_l,e_1)

                                            if (upp_l==0.d0) cycle

                                            do epr_l=ep_lo_l,ep_hi_l

                                                epp_l=employment_process(j_1,e_1,epr_l)

                                                if (epp_l==0.d0) cycle

                                                do vpr_l=fv1_l,fv2_l

                                                    vpp_l=voucher_probabilities(v_1,vpr_l,opp_l,vidx_l)

                                                    wgt_l=frac_l*vpp_l*epp_l*upp_l*at_l

                                                    if (wgt_l==0.d0) cycle

                                                    ptot_l=ptot_l+wgt_l

                                                    ! the forward push, for sources the law of motion moves
                                                    if ((finp_l>=fl_1) .AND. (finp_l<=fh_1) .AND. &
                                                        (mass_l>negligible_mass)) then
                                                        fwd_a(finp_l,upr_l,epr_l,hp_l,vpr_l,tid_1)=&
                                                            fwd_a(finp_l,upr_l,epr_l,hp_l,vpr_l,tid_1)+&
                                                            phi_l*wgt_l*mass_l
                                                    end if

                                                    if ((finp_l<fl_1) .OR. (finp_l>fh_1)) then
                                                        lost_l=lost_l+wgt_l
                                                        cycle
                                                    end if

                                                    if (ok_a(finp_l,upr_l,epr_l,hp_l,vpr_l,j_1+1)==0) then
                                                        lost_l=lost_l+wgt_l
                                                        cycle
                                                    end if

                                                    ew_l=ew_l+wgt_l*w_a(finp_l,upr_l,epr_l,hp_l,vpr_l,j_1+1)
                                                    ewc_l=ewc_l+wgt_l*wc_a(finp_l,upr_l,epr_l,hp_l,vpr_l,j_1+1)
                                                    ewnd_l=ewnd_l+wgt_l*wnd_a(finp_l,upr_l,epr_l,hp_l,vpr_l,j_1+1)
                                                    ek_l=ek_l+wgt_l*k_a(finp_l,upr_l,epr_l,hp_l,vpr_l,j_1+1)

                                                end do

                                            end do

                                        end do

                                    end do

                                end do

                                cK_l=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)/max(mass_age_1(j_1),10.d0**(-300))

                                w_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)+&
                                    beta_1*(phi_l*ew_l+(1-phi_l)*eas_l)
                                wc_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)+beta_1*phi_l*ewc_l
                                wnd_a(fin_1,u_1,e_1,h_1,v_1,j_1)=c_a(fin_1,u_1,e_1,h_1,v_1,j_1)+beta_1*ewnd_l
                                k_a(fin_1,u_1,e_1,h_1,v_1,j_1)=cK_l+beta_1*phi_l*ek_l

                                ptot_a(fin_1,u_1,e_1,h_1,v_1)=ptot_l
                                lost_a(fin_1,u_1,e_1,h_1,v_1)=lost_l

                            end do

                        end do
                        !$omp end parallel do

                    end do

                end do

            end do

            ! diagnostics for this age: transition weights sum to one, nothing
            ! falls outside the domain, and the push of Phi_j lands on Phi_{j+1}
            if (j_1<JK) then

                do u_1=1,unemployment_grid_size
                    do e_1=1,employment_grid_size
                        do v_1=0,voucher_state_max
                            do fin_1=flo_1,fh_1
                                do h_1=lowest_housing_grid_point,hhi_1
                                    if (ok_a(fin_1,u_1,e_1,h_1,v_1,j_1)==0) cycle
                                    ! the weights of a MASSED cell must sum to one; a cell nobody
                                    ! reaches (e.g. the excluded voucher state when exclusion is
                                    ! off) can have an empty voucher range and is only counted
                                    max_ptot_dev_all_1=max(max_ptot_dev_all_1,abs(ptot_a(fin_1,u_1,e_1,h_1,v_1)-1))
                                    if (distribution_stationary(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)>0.d0) then
                                        max_ptot_dev_1=max(max_ptot_dev_1,abs(ptot_a(fin_1,u_1,e_1,h_1,v_1)-1))
                                    elseif (abs(ptot_a(fin_1,u_1,e_1,h_1,v_1)-1)>10.d0**(-10)) then
                                        n_unreached_dev_1=n_unreached_dev_1+1
                                    end if
                                    lost_total_1=max(lost_total_1,lost_a(fin_1,u_1,e_1,h_1,v_1))
                                    lost_mass_1=lost_mass_1+lost_a(fin_1,u_1,e_1,h_1,v_1)*&
                                        max(distribution_stationary(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1),0.d0)
                                end do
                            end do
                        end do
                    end do
                end do

                fwdsum_a=sum(fwd_a,dim=6)
                fmass_age_1(j_1+1)=sum(fwdsum_a)
                l1_age_1(j_1+1)=sum(abs(fwdsum_a-distribution_stationary(1)%vector_transition_real(1,j_1+1,:,:,:,:,:)))
                maxd_age_1(j_1+1)=maxval(abs(fwdsum_a-distribution_stationary(1)%vector_transition_real(1,j_1+1,:,:,:,:,:)))

            end if

        end do

        call cpu_time(t1_1)
        call system_clock(c1_1)
        write(*,*) "CF_KID TIMING recursion: cpu s=", t1_1-t0_1, " wall s=", real(c1_1-c0_1)/real(crate_1), &
            " threads=", nthr_1

        ! ---------------------------------------------------------------
        ! 4. AVERAGES OVER THE NEWBORNS (Phi_1) AND THE VALIDATION
        ! ---------------------------------------------------------------
        avg_w_1=0
        avg_wc_1=0
        avg_wnd_1=0
        avg_k_1=0
        avg_v1_1=0
        m1_1=0
        n_nonfinite_1=0

        do u_1=1,unemployment_grid_size
            do e_1=1,employment_grid_size
                do v_1=0,voucher_state_max
                    do fin_1=fl_1,fh_1
                        do h_1=lowest_housing_grid_point,housing_status_grid_size-1

                            mass_1=distribution_stationary(1)%vector_transition_real(1,1,fin_1,u_1,e_1,h_1,v_1)

                            if (ok_a(fin_1,u_1,e_1,h_1,v_1,1)==1) then
                                if (.NOT. ieee_finite_cfkid(w_a(fin_1,u_1,e_1,h_1,v_1,1))) n_nonfinite_1=n_nonfinite_1+1
                            end if

                            if (mass_1<=0.d0) cycle

                            if (ok_a(fin_1,u_1,e_1,h_1,v_1,1)==0) then
                                write(*,*) "CF_KID WARNING: newborn mass at a cell with no policy", fin_1,u_1,e_1,h_1,v_1,mass_1
                                cycle
                            end if

                            m1_1=m1_1+mass_1
                            avg_w_1=avg_w_1+mass_1*w_a(fin_1,u_1,e_1,h_1,v_1,1)
                            avg_wc_1=avg_wc_1+mass_1*wc_a(fin_1,u_1,e_1,h_1,v_1,1)
                            avg_wnd_1=avg_wnd_1+mass_1*wnd_a(fin_1,u_1,e_1,h_1,v_1,1)
                            avg_k_1=avg_k_1+mass_1*k_a(fin_1,u_1,e_1,h_1,v_1,1)
                            avg_v1_1=avg_v1_1+mass_1*value_function(1)%vector_transition_real(1,1,fin_1,u_1,e_1,h_1,v_1)

                        end do
                    end do
                end do
            end do
        end do

        n_nonfinite_all_1=0
        n_nonfinite_c_1=0
        do j_1=1,JK
            do v_1=0,voucher_state_max
                do h_1=lowest_housing_grid_point,housing_status_grid_size-1
                    do e_1=1,employment_grid_size
                        do u_1=1,unemployment_grid_size
                            do fin_1=fl_1,fh_1
                                if (ok_a(fin_1,u_1,e_1,h_1,v_1,j_1)==0) cycle
                                if (.NOT. ieee_finite_cfkid(c_a(fin_1,u_1,e_1,h_1,v_1,j_1))) n_nonfinite_c_1=n_nonfinite_c_1+1
                                if ((.NOT. ieee_finite_cfkid(w_a(fin_1,u_1,e_1,h_1,v_1,j_1))) .OR. &
                                    (.NOT. ieee_finite_cfkid(wnd_a(fin_1,u_1,e_1,h_1,v_1,j_1))) .OR. &
                                    (.NOT. ieee_finite_cfkid(k_a(fin_1,u_1,e_1,h_1,v_1,j_1)))) &
                                    n_nonfinite_all_1=n_nonfinite_all_1+1
                            end do
                        end do
                    end do
                end do
            end do
        end do

        avg_w_1=avg_w_1/m1_1
        avg_wc_1=avg_wc_1/m1_1
        avg_wnd_1=avg_wnd_1/m1_1
        avg_v1_1=avg_v1_1/m1_1
        ! K is already normalised by M_a inside; Phi_1-weighting it gives the sum
        ! over ages of beta^(a-1) times the age-a cross-section average.

        write(*,*) "CF_KID ================= VALIDATION ================="
        write(*,'(A,ES24.16)') " CF_KID code average_welfare_with_childhood      =", average_welfare_with_childhood(time_period)
        write(*,'(A,ES24.16)') " CF_KID code average_childhood_utility           =", average_childhood_utility(time_period)
        write(*,'(A,ES24.16)') " CF_KID code adult part beta^J_K * avg V(1)        =", &
            average_welfare_with_childhood(time_period)-average_childhood_utility(time_period)
        write(*,'(A,ES24.16)') " CF_KID avg_Phi1 W(1,s)            [newborn value]  =", avg_w_1
        write(*,'(A,ES24.16)') " CF_KID   of which childhood flows Wc               =", avg_wc_1
        write(*,'(A,ES24.16)') " CF_KID   of which discounted entry value W-Wc      =", avg_w_1-avg_wc_1
        write(*,'(A,ES24.16)') " CF_KID avg_Phi1 Wnd(1,s) [no parent death < J_K]   =", avg_wnd_1
        write(*,'(A,ES24.16)') " CF_KID avg_Phi1 K(1,s)   [transpose check]         =", avg_k_1
        write(*,'(A,ES24.16)') " CF_KID K check: (K - code childhood)/code childhood =", &
            (avg_k_1-average_childhood_utility(time_period))/abs(average_childhood_utility(time_period))
        write(*,'(A,ES24.16)') " CF_KID gap W - code                                =", &
            avg_w_1-average_welfare_with_childhood(time_period)
        write(*,'(A,ES24.16)') " CF_KID gap Wnd - code                              =", &
            avg_wnd_1-average_welfare_with_childhood(time_period)
        write(*,'(A,ES24.16)') " CF_KID avg V(1) over Phi_1                         =", avg_v1_1
        write(*,'(A,ES24.16)') " CF_KID newborn mixture priced at A (parent shares) =", eamix_1
        write(*,'(A,ES24.16)') " CF_KID beta^J_K                                    =", beta_1**JK
        write(*,'(A,ES24.16)') " CF_KID max |sum of transition weights - 1| (massed)=", max_ptot_dev_1
        write(*,'(A,ES24.16,I10)') " CF_KID same over all cells, and unmassed cells off =", max_ptot_dev_all_1, n_unreached_dev_1
        write(*,'(A,ES24.16)') " CF_KID max weight to cells outside the domain      =", lost_total_1
        write(*,'(A,ES24.16)') " CF_KID mass-weighted weight outside the domain     =", lost_mass_1
        write(*,'(A,I12)')     " CF_KID non-finite W at valid age-1 cells           =", n_nonfinite_1
        write(*,'(A,I12)')     " CF_KID non-finite W/Wnd/K at valid cells, ages 1-JK=", n_nonfinite_all_1
        write(*,'(A,I12)')     " CF_KID non-finite child flow at valid cells        =", n_nonfinite_c_1
        write(*,*) "CF_KID forward push of Phi_j vs saved Phi_{j+1}: age, mass pushed, mass saved, L1, max|d|"
        do j_1=2,JK
            write(*,'(A,I4,4ES14.6)') " CF_KID PUSH", j_1, fmass_age_1(j_1), &
                sum(distribution_stationary(1)%vector_transition_real(1,j_1,:,:,:,:,:)), l1_age_1(j_1), maxd_age_1(j_1)
        end do

        ! ---------------------------------------------------------------
        ! 5. SANITY: monotone in the parent's productivity at birth, and lower
        !    behind a parent who has the disorder (ages 2..J_K; at birth no
        !    parent has it -- every household enters clean).
        ! ---------------------------------------------------------------
        n_viol_1=0
        n_cmp_1=0
        do cls_1=0,child_penalty_classes-1
            do ue_1=1,2
                u_1=idx_of(1,ue_1-1,0,0)
                if ((ue_1==2) .AND. (number_of_smi_states<2)) cycle
                do node_1=1,employment_base_size-1
                    e_1=cls_1*employment_base_size+node_1
                    if ((ok_a(negative_financial_grid_size,u_1,e_1,0,0,1)==0) .OR. &
                        (ok_a(negative_financial_grid_size,u_1,e_1+1,0,0,1)==0)) cycle
                    n_cmp_1=n_cmp_1+1
                    if (w_a(negative_financial_grid_size,u_1,e_1+1,0,0,1)<=&
                        w_a(negative_financial_grid_size,u_1,e_1,0,0,1)) n_viol_1=n_viol_1+1
                end do
            end do
        end do
        write(*,*) "CF_KID SANITY monotone in parent node at birth: violations", n_viol_1, " of", n_cmp_1

        ! parent with the disorder now vs the same parent never having had it
        do j_1=2,JK,1
            n_cmp_1=0
            n_lower_1=0
            n_lower_nd_1=0
            sum_n_1=0
            sum_dw_1=0
            sum_dwnd_1=0
            do emp_1=1,3
                do smi_1=0,number_of_smi_states-1
                    do e_1=1,employment_grid_size
                        do v_1=0,voucher_state_max
                            do fin_1=renter_floor_by_age(j_1),fh_1
                                do h_1=lowest_housing_grid_point,0
                                    u_1=idx_of(emp_1,smi_1,1,1)
                                    ue_1=idx_of(emp_1,smi_1,0,0)
                                    mass_1=distribution_stationary(1)%vector_transition_real(1,j_1,fin_1,u_1,e_1,h_1,v_1)
                                    if (mass_1<=0.d0) cycle
                                    if ((ok_a(fin_1,u_1,e_1,h_1,v_1,j_1)==0) .OR. (ok_a(fin_1,ue_1,e_1,h_1,v_1,j_1)==0)) cycle
                                    d_1=w_a(fin_1,u_1,e_1,h_1,v_1,j_1)-w_a(fin_1,ue_1,e_1,h_1,v_1,j_1)
                                    n_cmp_1=n_cmp_1+1
                                    if (d_1<0.d0) n_lower_1=n_lower_1+1
                                    sum_n_1=sum_n_1+mass_1
                                    sum_dw_1=sum_dw_1+mass_1*d_1
                                    dd_1=wnd_a(fin_1,u_1,e_1,h_1,v_1,j_1)-wnd_a(fin_1,ue_1,e_1,h_1,v_1,j_1)
                                    if (dd_1<0.d0) n_lower_nd_1=n_lower_nd_1+1
                                    sum_dwnd_1=sum_dwnd_1+mass_1*dd_1
                                end do
                            end do
                        end do
                    end do
                end do
            end do
            if ((j_1==2) .OR. (mod(j_1,5)==0)) write(*,'(A,I4,A,I8,A,I8,A,ES14.6,A,I8,A,ES14.6)') " CF_KID SANITY age", j_1, &
                " SUD-parent cells lower than never-SUD twin:", n_lower_1, " of", n_cmp_1, &
                "  mass-weighted mean W(SUD)-W(never)=", sum_dw_1/max(sum_n_1,10.d0**(-300)), &
                "  | Wnd lower:", n_lower_nd_1, " mean Wnd(SUD)-Wnd(never)=", sum_dwnd_1/max(sum_n_1,10.d0**(-300))
        end do

        ! ---------------------------------------------------------------
        ! 6. OUTPUT. W(1,s) in the order of the age-one slice of
        !    value_function1<tag>.dat (financial, unemployment, employment,
        !    housing, voucher; column major). Cells outside the law of motion's
        !    domain carry the sentinel -9999999999. The newborn distribution at
        !    the same cells, normalised to one, goes beside it.
        ! ---------------------------------------------------------------
        unit_1=92

        f_1="child_value_at_birth"//trim(out_tag_1)//".dat"
        open(unit=unit_1,file=trim(f_1),status='replace',action='write')
            write(unit_1,'(F35.13)') w_a(:,:,:,:,:,1)
        close(unit_1)

        f_1="child_value_at_birth_mass"//trim(out_tag_1)//".dat"
        open(unit=unit_1,file=trim(f_1),status='replace',action='write')
            write(unit_1,'(ES24.16)') max(distribution_stationary(1)%vector_transition_real(1,1,:,:,:,:,:),0.d0)/m1_1
        close(unit_1)

        f_1="child_value_at_birth_parts"//trim(out_tag_1)//".dat"
        open(unit=unit_1,file=trim(f_1),status='replace',action='write')
            write(unit_1,'(A)') "# W Wc Wnd K V1 (age-one slice, same order as child_value_at_birth)"
            do v_1=0,voucher_state_max
                do h_1=lowest_housing_grid_point,housing_status_grid_size-1
                    do e_1=1,employment_grid_size
                        do u_1=1,unemployment_grid_size
                            do fin_1=fl_1,fh_1
                                write(unit_1,'(5ES24.16)') w_a(fin_1,u_1,e_1,h_1,v_1,1),wc_a(fin_1,u_1,e_1,h_1,v_1,1),&
                                    wnd_a(fin_1,u_1,e_1,h_1,v_1,1),k_a(fin_1,u_1,e_1,h_1,v_1,1),&
                                    value_function(1)%vector_transition_real(1,1,fin_1,u_1,e_1,h_1,v_1)
                            end do
                        end do
                    end do
                end do
            end do
        close(unit_1)

        if (all_ages_1) then

            ! ages fastest, as value_function1<tag>.dat orders them, ages 1..J_K only
            f_1="child_value_by_age"//trim(out_tag_1)//".dat"
            open(unit=unit_1,file=trim(f_1),status='replace',action='write')
                do v_1=0,voucher_state_max
                    do h_1=lowest_housing_grid_point,housing_status_grid_size-1
                        do e_1=1,employment_grid_size
                            do u_1=1,unemployment_grid_size
                                do fin_1=fl_1,fh_1
                                    do j_1=1,JK
                                        write(unit_1,'(F35.13)') w_a(fin_1,u_1,e_1,h_1,v_1,j_1)
                                    end do
                                end do
                            end do
                        end do
                    end do
                end do
            close(unit_1)

        end if

        f_1="child_value_summary"//trim(out_tag_1)//".txt"
        open(unit=unit_1,file=trim(f_1),status='replace',action='write')
            write(unit_1,'(A)') "# cf_kid summary: key value"
            write(unit_1,'(A,I6)') "fin_lo ", fl_1
            write(unit_1,'(A,I6)') "fin_hi ", fh_1
            write(unit_1,'(A,I6)') "n_unemployment ", unemployment_grid_size
            write(unit_1,'(A,I6)') "n_employment ", employment_grid_size
            write(unit_1,'(A,I6)') "employment_base_size ", employment_base_size
            write(unit_1,'(A,I6)') "housing_lo ", lowest_housing_grid_point
            write(unit_1,'(A,I6)') "housing_hi ", housing_status_grid_size-1
            write(unit_1,'(A,I6)') "voucher_max ", voucher_state_max
            write(unit_1,'(A,I6)') "number_of_smi_states ", number_of_smi_states
            write(unit_1,'(A,I6)') "J_K ", JK
            write(unit_1,'(A,ES24.16)') "discount_factor ", beta_1
            write(unit_1,'(A,ES24.16)') "kappa_x_times_H ", kh_1
            write(unit_1,'(A,ES24.16)') "price_of_addictive_good ", price_of_addictive_good
            write(unit_1,'(A,ES24.16)') "probability_of_voucher_benchmark_used_1 ", probability_of_voucher_benchmark_used_1
            write(unit_1,'(A,ES24.16)') "weight_on_child ", weight_on_child
            write(unit_1,'(A,ES24.16)') "code_average_welfare_with_childhood ", average_welfare_with_childhood(time_period)
            write(unit_1,'(A,ES24.16)') "code_average_childhood_utility ", average_childhood_utility(time_period)
            write(unit_1,'(A,ES24.16)') "code_model_fraction_homeless ", model_fraction_homeless(time_period)
            write(unit_1,'(A,ES24.16)') "avg_W ", avg_w_1
            write(unit_1,'(A,ES24.16)') "avg_Wc ", avg_wc_1
            write(unit_1,'(A,ES24.16)') "avg_Wnd ", avg_wnd_1
            write(unit_1,'(A,ES24.16)') "avg_K ", avg_k_1
            write(unit_1,'(A,ES24.16)') "avg_V1 ", avg_v1_1
            write(unit_1,'(A,ES24.16)') "newborn_mixture_A ", eamix_1
            write(unit_1,'(A,ES24.16)') "max_transition_weight_dev ", max_ptot_dev_1
            write(unit_1,'(A,ES24.16)') "max_weight_outside_domain ", lost_total_1
            write(unit_1,'(A,I12)') "nonfinite_W_age1 ", n_nonfinite_1
            write(unit_1,'(A,I12)') "nonfinite_W_all_ages ", n_nonfinite_all_1
            do j_1=2,JK
                write(unit_1,'(A,I3,3ES24.16)') "push_age ", j_1, fmass_age_1(j_1), l1_age_1(j_1), maxd_age_1(j_1)
            end do
            do e_1=1,employment_grid_size
                write(unit_1,'(A,I3,2ES24.16)') "node_productivity_age1 ", e_1, employment_grid(1,e_1), vchild_1(e_1)
            end do
        close(unit_1)

        write(*,*) "CF_KID wrote child_value_at_birth"//trim(out_tag_1)//".dat and companions"

        call ieee_get_flag(ieee_invalid,invalid_after_1)
        write(*,*) "CF_KID IEEE invalid flag raised by this routine (master thread)=", invalid_after_1

        deallocate(w_a,wc_a,wnd_a,k_a,c_a,ok_a,fwd_a,fwdsum_a,ptot_a,lost_a)

    contains

        logical function ieee_finite_cfkid(x_1)
            real(8), intent(in) :: x_1
            ieee_finite_cfkid=(x_1==x_1) .AND. (abs(x_1)<huge(x_1))
        end function ieee_finite_cfkid

    end subroutine compute_child_value_at_birth

    ! <<< CF_KID ADDITIONS <<<
