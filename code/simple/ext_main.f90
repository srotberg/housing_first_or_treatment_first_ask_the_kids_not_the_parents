!===============================================================================
! ext_main.f90 -- quantify every externality and report it in one currency.
!===============================================================================
program ext_main
    use params
    use solve
    use equilibrium
    use calibrate
    use experiment
    use fiscal
    use welfare
    implicit none
    type(agg_t) :: A
    real(dp) :: cevs(NCH)
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call normalise_drug_supply()
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    call compute_aggregates(A)
    call compute_moments(A)
    call print_moments('benchmark')
    kappa_ext = kappa_ext_from_wtp()
    call report_fiscal_externality()

    ! and the full welfare decomposition: five channels, one unit
    write(*,'(A)') ''
    write(*,'(A)') ' decomposing the externalities (six equilibrium solves)...'
    call decompose_externalities(0.10_dp, .true., cevs)
end program ext_main
