!===============================================================================
! mech_main.f90 -- run the channel-shutdown ladder.
!===============================================================================
program mech_main
    use params
    use solve
    use equilibrium
    use calibrate
    use mechanism
    implicit none

    type(agg_t)     :: A
    type(profile_t) :: P0, P
    real(dp) :: target_p, t0, t1
    integer  :: nbisect = 22

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call wall(t0)

    write(*,'(A)') '=================================================================='
    write(*,'(A)') ' Channel-shutdown ladder'
    write(*,'(A)') ' b_clean recalibrated in every arm to hold participation fixed.'
    write(*,'(A)') ' Partial equilibrium at baseline prices.'
    write(*,'(A)') '=================================================================='

    !-- arm 0: baseline ------------------------------------------------------
    call solve_household(); call build_distribution_eq(); call compute_aggregates(A)
    target_p = 100.0_dp*A%users/max(A%pop,1.0e-12_dp)
    call profile_users(P0)
    call print_profile('ARM 0  baseline', P0, P0)
    write(*,'(A,F8.3,A)') '   -> holding participation at ', target_p, ' % in every arm'

    !-- arm 1: SUD -> mortality off -----------------------------------------
    call reset_channels()
    on_mortality_d = 0
    call recalibrate_b(target_p, nbisect); call profile_users(P)
    call print_profile('ARM 1  SUD->mortality OFF   (the headline claim)', P, P0)

    !-- arm 2: SUD -> employment off ----------------------------------------
    call reset_channels()
    on_employment_d = 0
    call recalibrate_b(target_p, nbisect); call profile_users(P)
    call print_profile('ARM 2  SUD->employment OFF  (R1 rival hypothesis)', P, P0)

    !-- arm 3: homelessness feedback off ------------------------------------
    call reset_channels()
    on_homeless_fb = 0
    call recalibrate_b(target_p, nbisect); call profile_users(P)
    call print_profile('ARM 3  homelessness feedback OFF', P, P0)

    call reset_channels()
    call wall(t1)
    write(*,'(A)') ''
    write(*,'(A,F8.1,A)') ' total wall time: ', t1-t0, ' s'

contains

subroutine reset_channels()
    on_mortality_d = 1; on_employment_d = 1; on_homeless_fb = 1
    b_dm(1,1) = P0%b_clean
    if (b_dm(1,1) <= 0.0_dp) b_dm(1,1) = 1.0e-4_dp
    b_dm(1,2) = b_dm(1,1)*mh_b_ratio
    call refresh_utility_constants()
end subroutine reset_channels

subroutine wall(t)
    real(dp), intent(out) :: t
    integer :: cnt, rate
    call system_clock(cnt, rate)
    t = real(cnt,dp)/real(rate,dp)
end subroutine wall

end program mech_main
