!===============================================================================
! smoke.f90 -- cheap checks that must pass before any number is believed.
!
! Written after a review found that five of the eight binaries in this directory
! had been compiled and never executed, and that the transition kernel existed
! in four separate copies. The checks below are the ones that can catch a silent
! disagreement without needing a converged calibration.
!
! The invariance check is the important one. If `dist` really is the stationary
! distribution, then stepping it forward one period with newborns must return it
! unchanged. That is an exact identity, and it cross-validates
! transition.f90's advance_distribution against equilibrium.f90's
! build_distribution_eq -- two of the four routines that used to carry their own
! copy of the kernel.
!===============================================================================
program smoke
    use params
    use solve
    use equilibrium
    use calibrate
    use experiment
    use fiscal
    use transition
    implicit none

    type(agg_t) :: A
    real(dp), allocatable :: D0(:,:,:,:,:,:,:), D1(:,:,:,:,:,:,:)
    real(dp) :: tot, mx, vmin, negmass, mass
    integer  :: nfail, j, ia, iy, ie, id, iv, im

    nfail = 0
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call alloc_transition()
    allocate(D0(NA,NY,NE,ND,NV,NM,n_age), D1(NA,NY,NE,ND,NV,NM,n_age))

    write(*,'(A)') ' solving the household problem once (uncalibrated)...'
    call solve_household()
    call build_distribution_eq()
    call compute_aggregates(A)

    !-- 1. no NaN, no negative mass -----------------------------------------
    write(*,'(A)') ''
    write(*,'(A)') ' 1. value function and distribution are finite and non-negative'
    vmin = 1.0e30_dp; negmass = 0.0_dp; tot = 0.0_dp
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        vmin = min(vmin, V(ia,iy,ie,id,iv,im,j))
        tot  = tot + dist(ia,iy,ie,id,iv,im,j)
        if (dist(ia,iy,ie,id,iv,im,j) < 0.0_dp) &
            negmass = negmass + dist(ia,iy,ie,id,iv,im,j)
        if (V(ia,iy,ie,id,iv,im,j) /= V(ia,iy,ie,id,iv,im,j)) nfail = nfail + 1
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A,ES13.5)') '      min V over the distribution : ', vmin
    write(*,'(A,ES13.5)') '      total mass                  : ', tot
    write(*,'(A,ES13.5)') '      negative mass               : ', negmass
    if (vmin < -1.0e11_dp) then
        write(*,'(A)') '      FAIL: states left at the -1e13 initialisation'
        nfail = nfail + 1
    end if
    if (negmass < -1.0e-12_dp) then
        write(*,'(A)') '      FAIL: negative mass'; nfail = nfail + 1
    end if

    !-- 2. VALUE OF LIFE: is anyone better off dead? ------------------------
    write(*,'(A)') ''
    write(*,'(A)') ' 2. nobody prefers death (V < 0 makes drug mortality a REWARD)'
    mass = 0.0_dp
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        if (dist(ia,iy,ie,id,iv,im,j) > 0.0_dp .and. &
            V(ia,iy,ie,id,iv,im,j) < 0.0_dp) mass = mass + dist(ia,iy,ie,id,iv,im,j)
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A,F9.4,A)') '      mass with V < 0 : ', 100.0_dp*mass/max(tot,1.0e-12_dp), ' %'
    if (mass/max(tot,1.0e-12_dp) > 1.0e-6_dp) then
        write(*,'(A)') '      WARNING: aleph too small; for these households dying is good'
    end if

    !-- 3. INVARIANCE: stepping the stationary distribution returns it -------
    write(*,'(A)') ''
    write(*,'(A)') ' 3. the stationary distribution is invariant under one step'
    write(*,'(A)') '    (cross-checks transition.f90 against equilibrium.f90)'
    D0 = dist
    dist_t = dist
    call advance_distribution()
    mx = 0.0_dp
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        mx = max(mx, abs(dist_t(ia,iy,ie,id,iv,im,j) - D0(ia,iy,ie,id,iv,im,j)))
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A,ES13.5)') '      max |step(dist) - dist|     : ', mx
    if (mx > 1.0e-12_dp) then
        write(*,'(A)') '      FAIL: the two distribution routines disagree'
        nfail = nfail + 1
    end if

    !-- 4. the cohort push agrees with the population push, net of newborns --
    write(*,'(A)') ''
    write(*,'(A)') ' 4. push_forward (cohort) agrees with advance_distribution'
    call push_forward(D0, D1)
    mx = 0.0_dp
    do j = 2, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        mx = max(mx, abs(D1(ia,iy,ie,id,iv,im,j) - dist_t(ia,iy,ie,id,iv,im,j)))
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A,ES13.5)') '      max difference, ages 2+     : ', mx
    if (mx > 1.0e-12_dp) then
        write(*,'(A)') '      FAIL: experiment.f90 and transition.f90 disagree'
        nfail = nfail + 1
    end if

    !-- 4b. THE BELLMAN IDENTITY --------------------------------------------
    ! The strongest check available on solve_household: recompute the objective
    ! at the STORED policy -- budget, flow payoff and continuation reassembled
    ! independently of the search -- and compare it with the stored value.
    ! Anything wrong in how those three are put together shows up here. It is
    ! the check that would have caught the r/R shadowing bug on its first run
    ! rather than after a brute-force harness went looking.
    write(*,'(A)') ''
    write(*,'(A)') ' 4b. Bellman identity: V equals the objective at the stored policy'
    call check_bellman(mx, tot)
    write(*,'(A,ES13.5)') '      max |V - objective(policy)| : ', mx
    write(*,'(A,ES13.5)') '      max |budget residual|       : ', tot
    if (mx > 1.0e-8_dp) then
        write(*,'(A)') '      FAIL: the value function and the policy disagree'
        nfail = nfail + 1
    end if
    if (tot > 1.0e-9_dp) then
        write(*,'(A)') '      FAIL: c + p_v*v + a'' does not equal resources'
        nfail = nfail + 1
    end if

    !-- 5. the fiscal recursion runs and returns finite numbers -------------
    write(*,'(A)') ''
    write(*,'(A)') ' 5. the fiscal present-value recursion'
    call report_fiscal_externality()

    !-- 6. the second-stage machinery runs ----------------------------------
    write(*,'(A)') ''
    write(*,'(A)') ' 6. the second-stage experiment machinery'
    call save_benchmark()
    call report_second_stage()

    !-- 7. market clearing at the converged equilibrium ---------------------
    write(*,'(A)') ''
    write(*,'(A)') ' 7. government budget and drug market residuals'
    write(*,'(A,ES13.5)') '      govt revenue - outlay       : ', A%tax_rev - A%govt_outlay
    if (A%drugq > 0.0_dp) then
        write(*,'(A,ES13.5)') '      p_v - psi1*Q**(psi2-1)      : ', &
            p_v - psi1*A%drugq**(psi2-1.0_dp)
    end if
    write(*,'(A)') '      (these are only expected to vanish after solve_equilibrium;'
    write(*,'(A)') '       this run solves the household problem once, so they will not)'

    write(*,'(A)') ''
    if (nfail == 0) then
        write(*,'(A)') ' ===== all structural checks passed ====='
    else
        write(*,'(A,I0,A)') ' ===== ', nfail, ' STRUCTURAL CHECKS FAILED ====='
    end if
contains

!-- reassemble the objective at the stored policy and compare with V ---------
subroutine check_bellman(worst_v, worst_b)
    real(dp), intent(out) :: worst_v, worst_b
    integer  :: j, ia, iy, ie, id, iv, im, iap, ihp, ireg, itr, ielig
    real(dp) :: cc, vv, bb, hours, res, dres, obj, phi, cfloor
    real(dp) :: w, base, vcap, cfl_net, y0, ygross, resid

    worst_v = 0.0_dp; worst_b = 0.0_dp
    cfloor = cfloor_share*avg_income

    do j = n_age-1, 1, -1
        call build_EV(j)
        do im = 1, NM; do iv = 1, NV; do id = 1, ND
        do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
            if (dist(ia,iy,ie,id,iv,im,j) <= 0.0_dp) cycle
            iap  = pol_a  (ia,iy,ie,id,iv,im,j)
            ihp  = pol_h  (ia,iy,ie,id,iv,im,j)
            ireg = pol_reg(ia,iy,ie,id,iv,im,j)
            itr  = pol_tr (ia,iy,ie,id,iv,im,j)
            cc   = pol_c  (ia,iy,ie,id,iv,im,j)
            vv   = pol_v  (ia,iy,ie,id,iv,im,j)
            if (cc <= 0.0_dp) cycle
            bb   = b_of(id, im, ihp)
            hours = hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j))

            ! rebuild the budget exactly as solve_household does
            if (j < j_ret .and. ie == 1) then
                w  = wage_rate(j, iy, id, im); y0 = 0.0_dp
            else
                w  = 0.0_dp; y0 = income_gross(j, iy, ie, id, im, 0.0_dp)
            end if
            cfl_net = cfloor - max(0.0_dp, r_free*a_grid(ia))
            if (ihp > 1 .and. iv == 2) then
                vcap = p_rent*h_grid(ihp)
            else
                vcap = 0.0_dp
            end if
            base = a_grid(ia) + bequest + (1.0_dp-tau_k)*r_free*a_grid(ia)
            if (ihp > 1) base = base - p_rent*h_grid(ihp)

            if (j < j_ret .and. ie == 1) then
                call res_slope(hours, w, base, vcap, cfl_net, res, dres)
                ygross = hours*w
            else
                res = base + after_tax(y0) + max(0.0_dp, vcap - kappa_r*y0) &
                    + max(0.0_dp, cfl_net - y0)
                ygross = y0
            end if

            ! budget residual
            resid = abs(cc + p_v*vv + a_grid(iap) - res)
            worst_b = max(worst_b, resid)

            ! eligibility, then the objective
            if (ygross + max(0.0_dp, r_free*a_grid(ia)) < kappa_V*median_income) then
                ielig = 1
            else
                ielig = 0
            end if
            phi = survival(j, ihp, id, im)
            obj = util(cc, h_pow(ihp), vv, bb, 1.0_dp-hours)
            if (itr == 1) obj = obj - treat_ucost
            obj = obj + beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)

            worst_v = max(worst_v, abs(obj - V(ia,iy,ie,id,iv,im,j)))
        end do; end do; end do
        end do; end do; end do
    end do
end subroutine check_bellman

end program smoke
