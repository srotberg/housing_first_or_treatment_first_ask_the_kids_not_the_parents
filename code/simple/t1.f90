program t1
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    real(dp) :: t0,t1w
    integer :: c,cr
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call system_clock(c,cr); t0=real(c,dp)/real(cr,dp)
    call solve_household()
    call system_clock(c,cr); t1w=real(c,dp)/real(cr,dp)
    write(*,'(A,F9.3,A)') 'solve_household: ', t1w-t0, ' s'
end program t1
