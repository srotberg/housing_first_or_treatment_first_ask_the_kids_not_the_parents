!===============================================================================
! diag_check.f90 -- two diagnostics the model has to pass before its numbers
! mean anything.
!
! 1. VALUE OF LIFE. Death gives a continuation of zero. If any household in the
!    benchmark has V < 0 it strictly prefers to die, and for that household
!    using drugs and dying is a GOOD outcome -- which would invert the paper's
!    central mechanism for exactly the people the policy targets. Reports the
!    minimum V, the mass with V < 0, and who they are.
!
! 2. AGE PROFILE OF USE, with and without the maximum experimentation age.
!    R1's smaller comment 1 says j_exp is in tension with the U-shaped age
!    profile of use. The test is whether removing it produces a sensible profile
!    or piles use onto the old, who have least to lose.
!===============================================================================
program diag_check
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none
    type(agg_t) :: A
    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call normalise_drug_supply()
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    call compute_aggregates(A)

    write(*,'(A)') ''
    write(*,'(A)') ' ===== diagnostic 1: is life worth living? ====='
    call value_of_life()

    write(*,'(A)') ''
    write(*,'(A)') ' ===== diagnostic 2: age profile of drug use ====='
    write(*,'(A,I3)') ' with the maximum experimentation age, j_exp = ', j_exp
    call age_profile()

    j_exp = n_age
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    write(*,'(A)') ''
    write(*,'(A)') ' with NO maximum experimentation age'
    call age_profile()

contains

subroutine value_of_life()
    integer  :: j, ia, iy, ie, id, iv, im
    real(dp) :: m, mass, neg, vmin, negsud, neghl, negold
    mass=0; neg=0; vmin=1.0e30_dp; negsud=0; neghl=0; negold=0
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        mass = mass + m
        vmin = min(vmin, V(ia,iy,ie,id,iv,im,j))
        if (V(ia,iy,ie,id,iv,im,j) < 0.0_dp) then
            neg = neg + m
            if (id == 2) negsud = negsud + m
            if (pol_h(ia,iy,ie,id,iv,im,j) == 1) neghl = neghl + m
            if (j >= j_ret) negold = negold + m
        end if
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A,ES13.5)') '   min V over the benchmark distribution : ', vmin
    write(*,'(A,F9.4,A)') '   mass with V < 0 (prefers death)       : ', &
        100.0_dp*neg/max(mass,1.0e-12_dp), ' %'
    if (neg > 0.0_dp) then
        write(*,'(A,F9.2,A)') '     of whom with SUD                    : ', &
            100.0_dp*negsud/neg, ' %'
        write(*,'(A,F9.2,A)') '     of whom homeless                    : ', &
            100.0_dp*neghl/neg, ' %'
        write(*,'(A,F9.2,A)') '     of whom retired                     : ', &
            100.0_dp*negold/neg, ' %'
        write(*,'(A)') '   WARNING: for these households dying is a good outcome,'
        write(*,'(A)') '   so drug use is REWARDED by mortality. Raise aleph.'
    end if
end subroutine value_of_life

subroutine age_profile()
    integer  :: j, ia, iy, ie, id, iv, im, k
    real(dp) :: m, pop(6), usr(6), sud(6)
    pop=0; usr=0; sud=0
    do j = 1, n_age
    k = min(6, 1 + (j-1)/10)
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        pop(k) = pop(k) + m
        if (pol_v(ia,iy,ie,id,iv,im,j) > 0.0_dp) usr(k) = usr(k) + m
        if (id == 2) sud(k) = sud(k) + m
    end do; end do; end do
    end do; end do; end do; end do
    write(*,'(A)') '    real age    26-35   36-45   46-55   56-65   66-75   76-85'
    write(*,'(A)',advance='no') '    using (%) '
    do k = 1, 6
        write(*,'(F8.2)',advance='no') 100.0_dp*usr(k)/max(pop(k),1.0e-12_dp)
    end do
    write(*,'(A)') ''
    write(*,'(A)',advance='no') '    SUD   (%) '
    do k = 1, 6
        write(*,'(F8.2)',advance='no') 100.0_dp*sud(k)/max(pop(k),1.0e-12_dp)
    end do
    write(*,'(A)') ''
end subroutine age_profile

end program diag_check
