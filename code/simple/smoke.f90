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

    !-- 5. the fiscal recursion runs and returns finite numbers -------------
    write(*,'(A)') ''
    write(*,'(A)') ' 5. the fiscal present-value recursion'
    call report_fiscal_externality()

    !-- 6. the second-stage machinery runs ----------------------------------
    write(*,'(A)') ''
    write(*,'(A)') ' 6. the second-stage experiment machinery'
    call save_benchmark()
    call report_second_stage()

    write(*,'(A)') ''
    if (nfail == 0) then
        write(*,'(A)') ' ===== all structural checks passed ====='
    else
        write(*,'(A,I0,A)') ' ===== ', nfail, ' STRUCTURAL CHECKS FAILED ====='
    end if
end program smoke
