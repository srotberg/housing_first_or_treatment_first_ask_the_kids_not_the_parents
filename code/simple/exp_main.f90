!===============================================================================
! exp_main.f90 -- second-stage calibration and report.
!
! Assumes the first stage has been run and its parameters are in params.f90.
! Solves the benchmark equilibrium, saves it, then calibrates the two
! second-stage parameters against their experimental moments and reports every
! second-stage object including the ones used only for validation.
!===============================================================================
program exp_main
    use params
    use solve
    use equilibrium
    use calibrate
    use experiment
    !$ use omp_lib
    implicit none

    type(agg_t) :: A
    integer  :: iters, nthreads
    character(len=64) :: arg
    real(dp) :: t0, t1

    iters = 12
    if (command_argument_count() >= 1) then
        call get_command_argument(1, arg); read(arg,*) iters
    end if

    nthreads = 1
    !$ nthreads = omp_get_max_threads()

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()

    write(*,'(A)') '======================================================'
    write(*,'(A)') ' Second-stage calibration -- short-run experiments'
    write(*,'(A,I0,A,I0)') ' threads: ', nthreads, '   bisection iters: ', iters
    write(*,'(A)') '======================================================'

    call wall(t0)
    call normalise_drug_supply()
    call solve_equilibrium(40, 1.0e-4_dp, .true.)
    call compute_aggregates(A)
    call compute_moments(A)
    call print_moments('benchmark, before the second stage')
    call save_benchmark()
    call wall(t1)
    write(*,'(A,F9.1,A)') ' benchmark equilibrium: ', t1-t0, ' s'

    write(*,'(A)') ''
    write(*,'(A)') ' -- before calibration --'
    call report_second_stage()

    write(*,'(A)') ''
    write(*,'(A)') ' calibrating b_hl_ratio to the Milby housing-access ratio...'
    call wall(t0)
    call calibrate_b_hl(iters, .true.)
    call wall(t1)
    write(*,'(A,F9.1,A)') '   done, ', t1-t0, ' s'

    write(*,'(A)') ' calibrating kappa_phi_d to the drug-price elasticity...'
    call wall(t0)
    call calibrate_kappa_phi_d(iters, .true.)
    call wall(t1)
    write(*,'(A,F9.1,A)') '   done, ', t1-t0, ' s'

    ! the second-stage parameters move behaviour, so the benchmark has to be
    ! re-cleared before the final report
    call solve_equilibrium(40, 1.0e-4_dp, .true.)
    call compute_aggregates(A)
    call compute_moments(A)
    call save_benchmark()

    call print_moments('first-stage moments after the second stage')
    write(*,'(A)') ''
    write(*,'(A)') ' -- after calibration --'
    call report_second_stage()

contains
    subroutine wall(t)
        real(dp), intent(out) :: t
        integer :: c, cr
        call system_clock(c, cr)
        t = real(c,dp)/real(cr,dp)
    end subroutine wall
end program exp_main
