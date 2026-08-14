! diag2.f90 -- does the mental-health productivity channel produce EMPLOYED
! homeless households? R1 comment 2(c)(i): the model has 100% of the homeless
! unemployed, against 40-52% in the data.
program diag2
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    type(agg_t) :: A
    integer  :: k
    real(dp) :: pvals(5), hl, hl_emp, hl_mh, hl_inc, pop, avinc

    pvals = [2.0_dp, 5.0_dp, 8.0_dp, 12.0_dp, 18.0_dp]   ! p_rent

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    theta_v = 0.30_dp; b_dm(1,1) = 0.15_dp; b_dm(1,2) = 0.04_dp
    b_dm(2,1) = 1.0e-3_dp; b_dm(2,2) = 1.0e-3_dp
    aleph = 60.0_dp

    write(*,'(A)') '=== rent level vs homeless composition (prod_pen_m = 0.55) ==='
    write(*,'(A)') ' data targets:  homeless 0.30% | employed 40-52% | income/avg 19.1%'
    write(*,'(A)') ''
    write(*,'(A)') '     p_rent   homeless%   %hl employed   %hl poor MH   hl income/avg  rent/inc'
    do k = 1, 5
        p_rent = pvals(k)
        call refresh_utility_constants()
        call solve_once(A)
        call comp(hl, hl_emp, hl_mh, hl_inc, pop, avinc)
        write(*,'(F11.2,F12.4,F15.2,F14.2,F16.3,F10.3)') p_rent, &
            100.0_dp*hl/max(pop,1.0e-12_dp), &
            100.0_dp*hl_emp/max(hl,1.0e-12_dp), &
            100.0_dp*hl_mh/max(hl,1.0e-12_dp), &
            (hl_inc/max(hl,1.0e-12_dp))/max(avinc/max(pop,1.0e-12_dp),1.0e-12_dp), &
            p_rent*h_grid(2)/max(avinc/max(pop,1.0e-12_dp),1.0e-12_dp)
    end do

contains

subroutine comp(hl, hl_emp, hl_mh, hl_inc, pop, avinc)
    real(dp), intent(out) :: hl, hl_emp, hl_mh, hl_inc, pop, avinc
    integer  :: j, ia, iy, ie, id, iv, im
    real(dp) :: m, y
    hl=0; hl_emp=0; hl_mh=0; hl_inc=0; pop=0; avinc=0
    do j = 1, n_age
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        y = income_gross(j, iy, ie, id, im)
        pop = pop + m; avinc = avinc + m*y
        if (pol_h(ia,iy,ie,id,iv,im,j) == 1) then
            hl = hl + m
            hl_inc = hl_inc + m*y
            if (ie == 2) hl_emp = hl_emp + m
            if (im == 2) hl_mh  = hl_mh  + m
        end if
    end do
    end do
    end do
    end do
    end do
    end do
    end do
end subroutine comp

end program diag2
