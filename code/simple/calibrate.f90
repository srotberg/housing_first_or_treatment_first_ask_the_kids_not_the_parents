!===============================================================================
! calibrate.f90 -- internal calibration by coordinate descent
!
! The parameter-to-moment mapping is close to triangular: each internally
! calibrated parameter has one moment it dominates. So instead of a generic
! simplex search in 15 dimensions, sweep the parameters one at a time, moving
! each in the known direction of its own moment gap, and repeat until every
! moment is inside tolerance. This is the same "adjuster" pattern the original
! code uses, but organised so the whole set is visible in one table.
!
! Each entry declares the sign of d(moment)/d(parameter); getting a sign wrong
! shows up immediately as a moment that walks away from its target.
!===============================================================================
module calibrate
    use params
    use solve
    use equilibrium
    implicit none

    integer, parameter :: NMOM = 11

    type :: mom_t
        character(len=28) :: name
        real(dp) :: target
        real(dp) :: model
        real(dp) :: weight
    end type mom_t

    type(mom_t) :: mom(NMOM)   ! NB: not 'M' -- would shadow local scalar 'm'

contains

subroutine init_targets()
    mom(1) = mom_t('drug participation (%)     ',  4.00_dp, 0.0_dp, 1.0_dp)
    mom(2) = mom_t('SUD rate (%)               ',  2.00_dp, 0.0_dp, 1.0_dp)
    mom(3) = mom_t('homelessness rate (%)      ',  0.30_dp, 0.0_dp, 1.0_dp)
    mom(4) = mom_t('unemployment rate (%)      ',  4.90_dp, 0.0_dp, 1.0_dp)
    mom(5) = mom_t('unemp rate | SUD (%)       ', 26.90_dp, 0.0_dp, 1.0_dp)
    mom(6) = mom_t('SUD share of homeless (%)  ', 37.00_dp, 0.0_dp, 1.0_dp)
    mom(7) = mom_t('voucher recipients/elig (%)', 26.60_dp, 0.0_dp, 1.0_dp)
    mom(8) = mom_t('drug spend/income | SUD (%)', 44.00_dp, 0.0_dp, 1.0_dp)
    ! Housing burden over ALL households, not renters only: everyone rents in
    ! this model, so a renters-only target would import the selection in who
    ! rents. Owner housing valued at imputed rent (8.3% of value), and the
    ! AGGREGATE ratio rather than the mean of ratios, which is trim-sensitive.
    ! See data/scf_housing_burden.py.
    mom(9)  = mom_t('housing cost/income, agg (%)', 21.20_dp, 0.0_dp, 1.0_dp)
    mom(10) = mom_t('share housing cost>50% (%)  ', 17.49_dp, 0.0_dp, 1.0_dp)
    ! R1 comment 2(c)(i) attacked this as an untargeted miss (41% model vs 74%
    ! data). Target it: it is also the moment that identifies the flow value of
    ! life, which is what generates the income gradient.
    mom(11) = mom_t('drug user income / avg (%)  ', 74.00_dp, 0.0_dp, 1.0_dp)
end subroutine init_targets


!-- model moments, including the conditional ones the aggregator does not carry
subroutine compute_moments(A)
    type(agg_t), intent(in) :: A
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: m, p, ygross
    real(dp) :: sud_unemp, sud_work, hl_sud, elig, vouch_elig
    real(dp) :: spend_sud, inc_sud
    real(dp) :: hcost, totinc, burden50, users_inc, users_m

    p = max(A%pop, 1.0e-12_dp)
    sud_unemp = 0.0_dp; sud_work = 0.0_dp; hl_sud = 0.0_dp
    elig = 0.0_dp; vouch_elig = 0.0_dp
    spend_sud = 0.0_dp; inc_sud = 0.0_dp
    hcost = 0.0_dp; totinc = 0.0_dp; burden50 = 0.0_dp
    users_inc = 0.0_dp; users_m = 0.0_dp

    do j = 1, n_age
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        ihp    = pol_h(ia,iy,ie,id,iv,im,j)
        ygross = income_gross(j, iy, ie, id, im)

        ! unemployment among those with SUD, working age only
        if (id == 2 .and. j < j_ret) then
            sud_work = sud_work + m
            if (ie == 1) sud_unemp = sud_unemp + m
        end if

        ! SUD share of the homeless
        if (ihp == 1 .and. id == 2) hl_sud = hl_sud + m

        ! voucher take-up among the income-eligible
        if (ygross + max(0.0_dp, r*a_grid(ia)) < kappa_V*median_income) then
            elig = elig + m
            if (iv == 2) vouch_elig = vouch_elig + m
        end if

        ! housing burden, over ALL households
        totinc = totinc + m*max(ygross, 1.0e-8_dp)
        if (ihp > 1) then
            hcost = hcost + m*p_rent*h_grid(ihp)
            if (p_rent*h_grid(ihp) > 0.5_dp*max(ygross,1.0e-8_dp)) burden50 = burden50 + m
        end if

        ! income of drug users, for the gradient moment
        if (pol_v(ia,iy,ie,id,iv,im,j) > 0.0_dp) then
            users_m   = users_m + m
            users_inc = users_inc + m*max(ygross, 1.0e-8_dp)
        end if

        ! drug spending as a share of income, conditional on SUD
        if (id == 2) then
            spend_sud = spend_sud + m*p_v*pol_v(ia,iy,ie,id,iv,im,j)
            inc_sud   = inc_sud   + m*max(ygross, 1.0e-8_dp)
        end if
    end do
    end do
    end do
    end do
    end do
    end do
    end do

    mom(1)%model = 100.0_dp*A%users/p
    mom(2)%model = 100.0_dp*A%sud/p
    mom(3)%model = 100.0_dp*A%homeless/p
    mom(4)%model = 100.0_dp*A%unemp/p
    mom(5)%model = 100.0_dp*sud_unemp/max(sud_work, 1.0e-12_dp)
    mom(6)%model = 100.0_dp*hl_sud/max(A%homeless, 1.0e-12_dp)
    mom(7)%model = 100.0_dp*vouch_elig/max(elig, 1.0e-12_dp)
    mom(8)%model = 100.0_dp*spend_sud/max(inc_sud, 1.0e-12_dp)
    mom(9)%model  = 100.0_dp*hcost/max(totinc, 1.0e-12_dp)
    mom(10)%model = 100.0_dp*burden50/p
    mom(11)%model = 100.0_dp*(users_inc/max(users_m,1.0e-12_dp)) &
                            /max(totinc/p, 1.0e-12_dp)
end subroutine compute_moments


subroutine print_moments(header)
    character(len=*), intent(in) :: header
    integer :: i
    write(*,'(A)') ''
    write(*,'(A)') '  '//trim(header)
    write(*,'(A)') '  ------------------------------------------------------------'
    write(*,'(A)') '  moment                          target     model      gap'
    write(*,'(A)') '  ------------------------------------------------------------'
    do i = 1, NMOM
        write(*,'(A,A,F9.3,F10.3,F10.3)') '  ', mom(i)%name, mom(i)%target, &
            mom(i)%model, mom(i)%model - mom(i)%target
    end do
    write(*,'(A,F9.4)') '   max abs relative gap: ', max_gap()
    write(*,'(A)') '  ------------------------------------------------------------'
end subroutine print_moments


function max_gap() result(g)
    real(dp) :: g
    integer  :: i
    g = 0.0_dp
    do i = 1, NMOM
        g = max(g, abs(mom(i)%model - mom(i)%target)/max(abs(mom(i)%target), 1.0e-8_dp))
    end do
end function max_gap


!===============================================================================
! One calibration sweep. Each parameter moves in the direction that closes its
! own moment gap, with a step proportional to the gap and a multiplicative
! update so parameters stay positive.
!
!   parameter          primary moment                 sign of dM/dparam
!   -----------------  -----------------------------  -----------------
!   b_dm(1,1) clean    drug participation                    -
!   pi_d_low           SUD rate                              +
!   h_homeless         homelessness rate                     +
!   pi_eu_base         unemployment rate                     +
!   kappa_ue_d         unemployment rate | SUD               -
!   recover_mult_hl    SUD share of homeless                 -
!   prob_V             voucher recipients / eligible         +
!   theta_v            drug spend / income | SUD             +
!   theta_h            housing cost / income (aggregate)      +
!   p_rent             share with housing cost > 50%          +
!   aleph              drug user income / average income      -
!===============================================================================
subroutine calibration_sweep(step)
    real(dp), intent(in) :: step

    call bump(b_dm(1,1),       gap(1), -1.0_dp, step, 1.0e-5_dp, 20.0_dp)
    call bump(pi_d_low,        gap(2), +1.0_dp, step, 1.0e-6_dp, 0.9_dp)
    call bump(h_homeless,      gap(3), +1.0_dp, step, 1.0e-5_dp, h_grid(2)*0.95_dp)
    call bump(pi_eu_base,      gap(4), +1.0_dp, step, 1.0e-4_dp, 0.9_dp)
    call bump(kappa_ue_d,      gap(5), -1.0_dp, step, 0.02_dp,   1.0_dp)
    call bump(recover_mult_hl, gap(6), -1.0_dp, step, 0.01_dp,   1.0_dp)
    call bump(prob_V,          gap(7), +1.0_dp, step, 1.0e-4_dp, 1.0_dp)
    call bump(theta_v,         gap(8), +1.0_dp, step, 1.0e-3_dp, 0.6_dp)
    call bump(theta_h,         gap(9), +1.0_dp, step, 0.02_dp,   0.6_dp)
    call bump(p_rent,          gap(10),+1.0_dp, step, 0.1_dp,    50.0_dp)
    ! higher flow value of life -> the rich abstain more -> user income falls
    call bump(aleph,           gap(11),-1.0_dp, step, 0.5_dp,    5.0e3_dp)

    ! keep derived quantities consistent with the parameters just moved
    pi_d_high = heavy_ratio * pi_d_low
    call refresh_utility_constants()
end subroutine calibration_sweep


function gap(i) result(g)
    integer, intent(in) :: i
    real(dp) :: g
    ! TRUE relative gap. Normalising by max(1, target) understates misses on
    ! small targets -- homelessness at 0.3% looked like a gap of 0.29 when the
    ! model was off by a factor of 40.
    g = (mom(i)%model - mom(i)%target)/max(abs(mom(i)%target), 1.0e-8_dp)
    g = min(max(g, -1.0_dp), 1.0_dp)
end function gap


!-- multiplicative update, clamped to [lo, hi] -------------------------------
subroutine bump(par, g, sgn, step, lo, hi)
    real(dp), intent(inout) :: par
    real(dp), intent(in)    :: g, sgn, step, lo, hi
    real(dp) :: fac
    ! model above target and dM/dpar > 0  =>  reduce the parameter
    ! parameters like b_d(1) must move orders of magnitude, so allow a wide
    ! multiplicative step rather than the +-15% a narrow clamp would permit
    fac = 1.0_dp - sgn*step*g
    fac = min(max(fac, 0.4_dp), 2.5_dp)
    par = min(max(par*fac, lo), hi)
end subroutine bump


subroutine refresh_utility_constants()
    integer :: i
    alpha_u = (1.0_dp-theta_h)*(1.0_dp-theta_v)
    beta_u  = theta_h*(1.0_dp-theta_v)
    gamma_u = theta_v
    h_grid(1) = h_homeless
    do i = 1, NH
        h_pow(i) = h_grid(i)**beta_u
    end do
end subroutine refresh_utility_constants


subroutine print_params()
    write(*,'(A)') '  -------------------- parameters --------------------'
    write(*,'(A,ES12.4)') '   b_dm(1,1) clean/goodMH : ', b_dm(1,1)
    write(*,'(A,ES12.4)') '   b_dm(1,2) clean/poorMH : ', b_dm(1,2)
    write(*,'(A,ES12.4)') '   b_dm(2,1) SUD          : ', b_dm(2,1)
    write(*,'(A,ES12.4)') '   pi_d_low        : ', pi_d_low
    write(*,'(A,ES12.4)') '   h_homeless      : ', h_homeless
    write(*,'(A,ES12.4)') '   pi_eu_base      : ', pi_eu_base
    write(*,'(A,ES12.4)') '   kappa_ue_d      : ', kappa_ue_d
    write(*,'(A,ES12.4)') '   recover_mult_hl : ', recover_mult_hl
    write(*,'(A,ES12.4)') '   prob_V          : ', prob_V
    write(*,'(A,ES12.4)') '   theta_v         : ', theta_v
    write(*,'(A,ES12.4)') '   theta_h         : ', theta_h
    write(*,'(A,ES12.4)') '   p_rent          : ', p_rent
    write(*,'(A,ES12.4)') '   aleph           : ', aleph
    write(*,'(A)') '  ----------------------------------------------------'
end subroutine print_params

end module calibrate
