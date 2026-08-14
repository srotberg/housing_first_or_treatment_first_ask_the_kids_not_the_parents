!===============================================================================
! mechanism.f90 -- the channel-shutdown ladder.
!
! Shut one channel off at a time, RECALIBRATE b_d(1) so drug participation
! returns to its baseline value, and report who uses drugs in each arm.
!
! The recalibration is what makes the comparison meaningful. Without it,
! removing the mortality penalty simply raises drug use everywhere and the
! level change swamps any compositional change. Holding participation fixed
! separates sorting from level, and yields two distinct statistics per arm:
!
!   how far b had to move   -> HOW MUCH deterrence the channel was providing
!   the income gradient     -> WHOM it deterred
!
! Run in partial equilibrium at baseline prices: the point is to isolate the
! behavioural mechanism, not equilibrium feedback, and it is ~50x cheaper.
!===============================================================================
module mechanism
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none

    integer, parameter :: NQ = 5      ! income quintiles
    ! poor mental health scales b down (self-medication); the ratio is held
    ! fixed while b_dm(1,1) is recalibrated, so the arms differ only in the
    ! channel switched off
    real(dp) :: mh_b_ratio = 0.25_dp

    type :: profile_t
        real(dp) :: particip, sud, homeless
        real(dp) :: use_by_q(NQ)          ! drug-use rate within each income quintile
        real(dp) :: inc_ratio_users       ! mean user income / mean income
        real(dp) :: share_unemp_users
        real(dp) :: share_homeless_users
        real(dp) :: mean_age_users
        real(dp) :: mean_assets_users
        real(dp) :: exp_inc_ratio         ! same, experimenters only (d=0, v>0)
        real(dp) :: sud_inc_ratio         ! same, SUD only
        real(dp) :: b_clean               ! recalibrated value
    end type profile_t

contains

!-- who uses drugs, in detail ------------------------------------------------
subroutine profile_users(P)
    type(profile_t), intent(out) :: P
    integer  :: j, ia, iy, ie, id, iv, im, q
    real(dp) :: m, y, pop, users, uinc, uunemp, uhl, uage, uass
    real(dp) :: q_use(NQ), q_pop(NQ), totinc
    real(dp) :: e_mass, e_inc, s_mass, s_inc, homeless, sud

    pop=0; users=0; uinc=0; uunemp=0; uhl=0; uage=0; uass=0; totinc=0
    q_use=0; q_pop=0; e_mass=0; e_inc=0; s_mass=0; s_inc=0; homeless=0; sud=0

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

        pop    = pop + m
        totinc = totinc + m*y
        if (id == 2) sud = sud + m
        if (pol_h(ia,iy,ie,id,iv,im,j) == 1) homeless = homeless + m

        ! income quintile by productivity state
        q = 1 + int( real(iy-1,dp)*real(NQ,dp)/real(NY,dp) )
        q = min(max(q,1),NQ)
        q_pop(q) = q_pop(q) + m

        if (pol_v(ia,iy,ie,id,iv,im,j) > 0.0_dp) then
            users   = users + m
            q_use(q)= q_use(q) + m
            uinc    = uinc + m*y
            uage    = uage + m*real(j,dp)
            uass    = uass + m*a_grid(ia)
            if (ie == 1) uunemp = uunemp + m
            if (pol_h(ia,iy,ie,id,iv,im,j) == 1) uhl = uhl + m
            if (id == 1) then
                e_mass = e_mass + m;  e_inc = e_inc + m*y
            else
                s_mass = s_mass + m;  s_inc = s_inc + m*y
            end if
        end if
    end do
    end do
    end do
    end do
    end do
    end do
    end do

    P%particip = 100.0_dp*users/max(pop,1.0e-12_dp)
    P%sud      = 100.0_dp*sud/max(pop,1.0e-12_dp)
    P%homeless = 100.0_dp*homeless/max(pop,1.0e-12_dp)
    do q = 1, NQ
        P%use_by_q(q) = 100.0_dp*q_use(q)/max(q_pop(q),1.0e-12_dp)
    end do
    P%inc_ratio_users     = (uinc/max(users,1.0e-12_dp)) / max(totinc/max(pop,1.0e-12_dp),1.0e-12_dp)
    P%share_unemp_users   = 100.0_dp*uunemp/max(users,1.0e-12_dp)
    P%share_homeless_users= 100.0_dp*uhl/max(users,1.0e-12_dp)
    P%mean_age_users      = 25.0_dp + uage/max(users,1.0e-12_dp)
    P%mean_assets_users   = uass/max(users,1.0e-12_dp)
    P%exp_inc_ratio       = (e_inc/max(e_mass,1.0e-12_dp)) / max(totinc/max(pop,1.0e-12_dp),1.0e-12_dp)
    P%sud_inc_ratio       = (s_inc/max(s_mass,1.0e-12_dp)) / max(totinc/max(pop,1.0e-12_dp),1.0e-12_dp)
    P%b_clean             = b_dm(1,1)
end subroutine profile_users


!-- bisection on log b_d(1) so participation returns to `target_p` -----------
! b spans orders of magnitude, so bisect in logs. Participation is decreasing
! in b, which pins the bracket orientation.
subroutine recalibrate_b(target_p, iters)
    real(dp), intent(in) :: target_p
    integer,  intent(in) :: iters
    type(agg_t) :: A
    real(dp) :: lo, hi, mid, pmid
    integer  :: k

    lo = log(1.0e-6_dp)
    hi = log(2.0e+1_dp)

    do k = 1, iters
        mid = 0.5_dp*(lo+hi)
        b_dm(1,1) = exp(mid)
        b_dm(1,2) = exp(mid)*mh_b_ratio
        call refresh_utility_constants()
        call solve_household()
        call build_distribution_eq()
        call compute_aggregates(A)
        pmid = 100.0_dp*A%users/max(A%pop,1.0e-12_dp)
        if (pmid > target_p) then
            lo = mid          ! too much use -> need larger b
        else
            hi = mid
        end if
    end do
    b_dm(1,1) = exp(0.5_dp*(lo+hi))
    b_dm(1,2) = b_dm(1,1)*mh_b_ratio
    call refresh_utility_constants()
    call solve_household()
    call build_distribution_eq()
end subroutine recalibrate_b


subroutine print_profile(label, P, P0)
    character(len=*), intent(in) :: label
    type(profile_t), intent(in)  :: P
    type(profile_t), intent(in)  :: P0     ! baseline, for the b comparison
    integer :: q
    write(*,'(A)') ''
    write(*,'(A)') ' == '//trim(label)//' =='
    write(*,'(A,ES11.3,A,F8.2,A)') '   b_clean          : ', P%b_clean, &
        '   (x', P%b_clean/max(P0%b_clean,1.0e-30_dp), ' vs baseline)'
    write(*,'(A,F8.3,A)') '   participation    : ', P%particip, ' %'
    write(*,'(A,F8.3,A)') '   SUD rate         : ', P%sud, ' %'
    write(*,'(A,F8.3,A)') '   homelessness     : ', P%homeless, ' %'
    write(*,'(A)',advance='no') '   use by income Q1..Q5 (%): '
    do q = 1, NQ
        write(*,'(F8.2)',advance='no') P%use_by_q(q)
    end do
    write(*,'(A)') ''
    write(*,'(A,F8.3)') '   user income / avg      : ', P%inc_ratio_users
    write(*,'(A,F8.3)') '     experimenters only   : ', P%exp_inc_ratio
    write(*,'(A,F8.3)') '     SUD only             : ', P%sud_inc_ratio
    write(*,'(A,F8.2,A)') '   users unemployed       : ', P%share_unemp_users, ' %'
    write(*,'(A,F8.2,A)') '   users homeless         : ', P%share_homeless_users, ' %'
    write(*,'(A,F8.2)')   '   mean age of users      : ', P%mean_age_users
    write(*,'(A,F8.3)')   '   mean assets of users   : ', P%mean_assets_users
end subroutine print_profile

end module mechanism
