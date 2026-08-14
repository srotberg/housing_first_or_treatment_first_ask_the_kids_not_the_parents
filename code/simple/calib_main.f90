!===============================================================================
! calib_main.f90 -- run the calibration sweep loop.
!
! The inner equilibrium is solved to a loose tolerance during calibration and
! tightened only for the final report: there is no point converging prices to
! 1e-4 while the parameters are still moving by percent.
!===============================================================================
program calib_main
    use params
    use solve
    use equilibrium
    use calibrate
    !$ use omp_lib
    implicit none

    type(agg_t) :: A
    integer  :: sweep, max_sweeps, nthreads
    real(dp) :: t0, t1, step, best_gap
    real(dp) :: best_par(NPAR)
    character(len=64) :: arg

    max_sweeps = 25
    if (command_argument_count() >= 1) then
        call get_command_argument(1, arg); read(arg,*) max_sweeps
    end if

    nthreads = 1
    !$ nthreads = omp_get_max_threads()

    call setup_grids()
    call alloc_all()
    call alloc_solve()
    call init_targets()
    call refresh_utility_constants()

    write(*,'(A)') '======================================================'
    write(*,'(A)') ' Calibration -- simplified HF/TF model'
    write(*,'(A,I0,A,I0,A)') ' threads: ', nthreads, '   sweeps: ', max_sweeps, ''
    write(*,'(A)') '======================================================'

    call wall(t0)
    call normalise_drug_supply()

    best_gap = 1.0e30_dp
    ! Gentler than 0.35. With the level moments now BRACKETED rather than
    ! bumped, the proportional steps only carry composition moments, so there is
    ! no longer any reason to move fast: large steps were what made the sweep
    ! overshoot and oscillate. Slower and monotone beats fast and thrashing.
    step = 0.20_dp
    call save_params(best_par)

    do sweep = 1, max_sweeps
        ! loose inner solve while parameters are still moving
        call solve_equilibrium(20, 3.0e-3_dp, .false.)
        ! the small-target level moments are re-bracketed AT cleared prices, so
        ! the number reported is the one actually hit
        ! Polish only once parameters have stopped moving fast. Early sweeps
        ! are transporting parameters and their reported moments do not matter;
        ! polishing them costs about 60 extra household solves a sweep for a
        ! number nobody reads. From sweep 3 the level moments are worth pinning.
        if (sweep >= 3) call polish_levels(min(10, 6 + sweep/4))
        call compute_aggregates(A)
        call compute_moments(A)

        call wall(t1)
        write(*,'(A,I3,A,F9.4,A,F7.3,A,F8.1,A)') ' sweep ', sweep, &
            '   max rel gap = ', max_gap(), '   step = ', step, &
            '   [', t1-t0, ' s elapsed]'
        call print_moments('sweep moments')
        call print_params()

        if (max_gap() < best_gap) then
            best_gap = max_gap()
            call save_params(best_par)     ! keep the best vector, not the last
        else
            step = max(0.06_dp, step*0.7_dp)   ! back off when it stops improving
        end if

        if (max_gap() < 0.02_dp) then
            write(*,'(A)') ' calibration tolerance reached'
            exit
        end if

        call calibration_sweep(step, min(12, 6 + sweep/4))
    end do

    ! final tight solve at the BEST parameter vector seen, not the last one
    write(*,'(A)') ''
    write(*,'(A,F9.4)') ' restoring the best sweep, max rel gap = ', best_gap
    write(*,'(A)') ' final solve at tight tolerance...'
    call load_params(best_par)
    call solve_equilibrium(80, 1.0e-4_dp, .false.)
    call compute_aggregates(A)
    call compute_moments(A)
    call wall(t1)

    call print_moments('calibration result')
    call print_housing_cdf()
    call print_params()
    write(*,'(A,F10.2,A)') ' total wall time: ', t1-t0, ' s'

contains

subroutine wall(t)
    real(dp), intent(out) :: t
    integer :: cnt, rate
    call system_clock(cnt, rate)
    t = real(cnt,dp)/real(rate,dp)
end subroutine wall

end program calib_main
