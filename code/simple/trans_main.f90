!===============================================================================
! trans_main.f90 -- transition path for a policy change.
!
! Argument 1: 0 = Housing First benchmark -> Treatment First
!             1 = benchmark -> universal vouchers (prob_V = 1)
!===============================================================================
program trans_main
    use params
    use solve
    use equilibrium
    use calibrate
    use transition
    implicit none
    type(agg_t) :: A0, A1
    type(agg_t), allocatable :: A_t(:)
    integer :: which, prob_keep_tf, neq, nit
    real(dp) :: prob_keep_V
    character(len=32) :: arg

    which = 0; neq = 40; nit = 30
    if (command_argument_count() >= 1) then
        call get_command_argument(1, arg); read(arg,*) which
    end if
    ! T_path, path iterations and steady-state iterations, so the solver can be
    ! exercised structurally at a fraction of the cost before a real run
    if (command_argument_count() >= 2) then
        call get_command_argument(2, arg); read(arg,*) T_path
    end if
    if (command_argument_count() >= 3) then
        call get_command_argument(3, arg); read(arg,*) nit
    end if
    if (command_argument_count() >= 4) then
        call get_command_argument(4, arg); read(arg,*) neq
    end if

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call alloc_transition()
    allocate(A_t(T_path))

    !-- initial steady state --------------------------------------------------
    write(*,'(A)') ' solving the INITIAL steady state...'
    call normalise_drug_supply()
    call solve_equilibrium(neq, 1.0e-4_dp, .false.)
    call compute_aggregates(A0)
    call compute_moments(A0)
    call print_moments('initial steady state')
    call set_initial()
    prob_keep_tf = policy_TF
    prob_keep_V  = prob_V

    !-- terminal steady state -------------------------------------------------
    if (which == 0) then
        policy_TF = 1
        write(*,'(A)') ' solving the TERMINAL steady state: Treatment First...'
    else
        prob_V = 1.0_dp
        write(*,'(A)') ' solving the TERMINAL steady state: universal vouchers...'
    end if
    call solve_equilibrium(neq, 1.0e-4_dp, .false.)
    call compute_aggregates(A1)
    call compute_moments(A1)
    call print_moments('terminal steady state')
    call set_terminal()

    !-- the path --------------------------------------------------------------
    write(*,'(A)') ''
    write(*,'(A,I0,A)') ' solving the transition over ', T_path, ' periods...'
    call solve_path(nit, 1.0e-3_dp, .true.)
    call forward_pass(A_t)
    call print_path(A_t, 2)
end program trans_main
