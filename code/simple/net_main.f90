!===============================================================================
! net_main.f90 -- the safety-net experiment (R3 M2c).
!===============================================================================
program net_main
    use params
    use solve
    use equilibrium
    use calibrate
    use safetynet
    implicit none
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call normalise_drug_supply()
    call run_safety_net(.true.)
end program net_main
