! diag2.f90 -- does the mortality channel reverse the income gradient of drug use?
! This is the paper's central claim, tested directly in the new model.
program diag2
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    type(agg_t) :: A
    integer  :: k, iq
    real(dp) :: avals(5), q_use(3), q_pop(3)

    avals = [1.0_dp, 10.0_dp, 40.0_dp, 150.0_dp, 600.0_dp]

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    theta_v = 0.30_dp; b_d(1) = 1.0e-4_dp; b_d(2) = 1.0e-4_dp

    write(*,'(A)') '=== scan aleph with TINY b (mortality does the deterring) ==='
    write(*,'(A)') '     aleph   particip%    SUD%   |  use% low   use% mid  use% high'
    do k = 1, 5
        aleph = avals(k); call refresh_utility_constants()
        call solve_once(A); call compute_moments(A)
        call use_by_income(q_use, q_pop)
        write(*,'(F10.2,2F10.3,A,3F11.3)') aleph, mom(1)%model, mom(2)%model, '  |', &
            100.0_dp*q_use(1)/max(q_pop(1),1.0e-12_dp), &
            100.0_dp*q_use(2)/max(q_pop(2),1.0e-12_dp), &
            100.0_dp*q_use(3)/max(q_pop(3),1.0e-12_dp)
    end do

contains

! split working-age households into three productivity bins and report the
! fraction using drugs in each
subroutine use_by_income(qu, qp)
    real(dp), intent(out) :: qu(3), qp(3)
    integer  :: j, ia, iy, ie, id, iv, bin
    real(dp) :: m
    qu = 0.0_dp; qp = 0.0_dp
    do j = 1, j_ret-1
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,j)
        if (m <= 0.0_dp) cycle
        if (iy <= 3) then
            bin = 1
        else if (iy <= 6) then
            bin = 2
        else
            bin = 3
        end if
        qp(bin) = qp(bin) + m
        if (pol_v(ia,iy,ie,id,iv,j) > 0.0_dp) qu(bin) = qu(bin) + m
    end do
    end do
    end do
    end do
    end do
    end do
end subroutine use_by_income

end program diag2
