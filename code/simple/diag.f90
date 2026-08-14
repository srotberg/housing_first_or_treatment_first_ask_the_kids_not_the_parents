! diag.f90 -- scan a parameter and report the moments it is supposed to move.
! Partial equilibrium (prices fixed) so each point costs one household solve.
program diag
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    type(agg_t) :: A
    integer  :: k
    real(dp) :: bvals(9), tvals(5)
    bvals = [1.0e-4_dp, 1.0e-3_dp, 5.0e-3_dp, 2.0e-2_dp, 5.0e-2_dp, &
             1.5e-1_dp, 4.0e-1_dp, 1.0_dp, 3.0_dp]
    tvals = [0.05_dp, 0.15_dp, 0.30_dp, 0.45_dp, 0.60_dp]

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()

    write(*,'(A)') '=== scan b_d(1) clean  (theta_v=0.30, b_d(2)=1e-3) ==='
    write(*,'(A)') '   b_d(1)     particip%     SUD%   spend|SUD%   homeless%'
    theta_v = 0.30_dp; b_d(2) = 1.0e-3_dp
    do k = 1, 9
        b_d(1) = bvals(k); call refresh_utility_constants()
        call solve_once(A); call compute_moments(A)
        write(*,'(ES11.3,4F12.4)') b_d(1), mom(1)%model, mom(2)%model, mom(8)%model, mom(3)%model
    end do

    write(*,'(A)') ''
    write(*,'(A)') '=== scan theta_v  (b_d(1)=0.4, b_d(2)=1e-3) ==='
    write(*,'(A)') '   theta_v     particip%     SUD%   spend|SUD%   homeless%'
    b_d(1) = 0.4_dp; b_d(2) = 1.0e-3_dp
    do k = 1, 5
        theta_v = tvals(k); call refresh_utility_constants()
        call solve_once(A); call compute_moments(A)
        write(*,'(F11.3,4F12.4)') theta_v, mom(1)%model, mom(2)%model, mom(8)%model, mom(3)%model
    end do
end program diag
