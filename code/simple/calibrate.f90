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

    ! self-medication: poor mental health scales b down. Calibrated to the
    ! co-occurring SUD rate among adults with SMI.
    real(dp) :: mh_b_ratio = 0.25_dp

    integer, parameter :: NMOM = 19

    type :: mom_t
        character(len=28) :: name
        real(dp) :: target
        real(dp) :: model
        real(dp) :: weight
    end type mom_t

    type(mom_t) :: mom(NMOM)   ! NB: not 'M' -- would shadow local scalar 'm'

contains

subroutine init_targets()
    ! NSDUH 2024, ages 26+ (the model's range), from data/nsduh_gradients.py.
    ! The paper's 4% and 2% were built for ages 18+ on a different construction.
    mom(1) = mom_t('drug participation (%)     ',  5.13_dp, 0.0_dp, 1.0_dp)
    mom(2) = mom_t('SUD rate (%)               ',  3.68_dp, 0.0_dp, 1.0_dp)
    mom(3) = mom_t('homelessness rate (%)      ',  0.30_dp, 0.0_dp, 1.0_dp)
    mom(4) = mom_t('unemployment rate (%)      ',  4.90_dp, 0.0_dp, 1.0_dp)
    mom(5) = mom_t('unemp rate | SUD (%)       ', 26.90_dp, 0.0_dp, 1.0_dp)
    ! DRUG use disorder among the homeless, 21.7% (Gutwinski et al. 2021). The
    ! paper's 37% target sits on the ALCOHOL figure (36.7%) from the same
    ! evidence base, but the model is about drug use.
    mom(6) = mom_t('drug UD share of homeless(%)', 21.70_dp, 0.0_dp, 1.0_dp)
    mom(7) = mom_t('voucher recipients/elig (%)', 26.60_dp, 0.0_dp, 1.0_dp)
    mom(8) = mom_t('drug spend/income | SUD (%)', 44.00_dp, 0.0_dp, 1.0_dp)
    ! Housing burden over ALL households, not renters only: everyone rents in
    ! this model, so a renters-only target would import the selection in who
    ! rents. Owner housing valued at imputed rent (8.3% of value), and the
    ! AGGREGATE ratio rather than the mean of ratios, which is trim-sensitive.
    ! See data/scf_housing_burden.py.
    mom(9)  = mom_t('housing cost/income, agg (%)', 21.20_dp, 0.0_dp, 1.0_dp)
    mom(10) = mom_t('share housing cost>50% (%)  ', 17.49_dp, 0.0_dp, 1.0_dp)
    ! R1 comment 2(c)(i) attacked the user income ratio as an untargeted miss
    ! (41% model vs "roughly 74%"). That 74% is computed over people with a use
    ! DISORDER, not over people who use -- a different population. For ages 26+,
    ! NSDUH gives 0.951 for users and 0.687 for moderate/severe UD.
    !
    ! Targeting both is the sharper test: USE is close to income-neutral, and it
    ! is PROGRESSION to disorder that concentrates at the bottom. See
    ! data/nsduh_gradients.py.
    mom(11) = mom_t('drug user income / avg (%)  ', 95.10_dp, 0.0_dp, 1.0_dp)
    mom(12) = mom_t('SUD income / avg (%)        ', 68.70_dp, 0.0_dp, 1.0_dp)
    ! ---- serious mental illness -------------------------------------------
    ! SMI share of the homeless: Gutwinski et al. (2021, PLOS Medicine) pool 39
    ! studies of homeless people in high-income countries and find 12.4%
    ! schizophrenia-spectrum and 12.6% major depression, so about 25% with a
    ! severe disorder against 5.5% in the adult population -- a relative risk
    ! near 4.5. This identifies the PERSISTENCE of the SMI state.
    mom(13) = mom_t('SMI share of homeless (%)   ', 25.00_dp, 0.0_dp, 1.0_dp)
    ! WARNING -- this target is inconsistent with a 5% SMI prevalence; see
    ! MENTAL_HEALTH.md section 6. The 22-40% employment figures come from
    ! high-disability diagnoses (schizophrenia, ~1% of adults). NSDUH's SMI is a
    ! broader functional-impairment measure at 5.0% of adults 26+, and its own
    ! tables imply a far milder gradient: SMI prevalence is 8.9% among the
    ! unemployed against 5.1% among the full-time employed (Table 6.5B), which
    ! by Bayes gives an unemployment rate given SMI near 7.1% against 4%
    ! overall -- a ratio of 1.8, not 70% non-employment.
    mom(14) = mom_t('unemp rate | SMI (%)        ',  7.10_dp, 0.0_dp, 1.0_dp)
    ! Homeless income relative to average -- R1 comment 2(c)(i), 19.1% in the
    ! linked administrative data of Meyer et al.
    mom(15) = mom_t('homeless income / avg (%)   ', 19.10_dp, 0.0_dp, 1.0_dp)
    ! ---- previously unjustified parameters, now attached to moments --------
    ! beta: aggregate WEALTH-TO-GDP, with GDP measured as all factor income
    ! (labour earnings plus the return on the capital stock) and transfers
    ! excluded. Three is the standard US ratio of the private capital stock to
    ! annual output and is the moment a life-cycle discount factor is normally
    ! pinned by. It is the right target here rather than the SCF's 7.3 net
    ! worth to *household income* ratio, whose denominator is a household
    ! income concept and whose numerator is mostly housing equity that a model
    ! without homeownership cannot hold.
    mom(16) = mom_t('wealth / GDP                ',  3.00_dp, 0.0_dp, 1.0_dp)
    ! cfloor_share: SNAP benefits as a share of GDP, FY2023 (paper target 21)
    mom(17) = mom_t('food stamps / labour income ',  0.42_dp, 0.0_dp, 1.0_dp)
    ! Co-occurring SUD among adults with SMI, age-matched to the model from the
    ! 2023 NSDUH detailed tables (aged 26+, 2023):
    !   co-occurring SUD and SMI  = 2.2%   (Table 6.13B)
    !   SMI                       = 5.0%   (Table 6.4B)
    !   SUD                       = 16.6%  (Table 5.10B)
    ! so P(SUD | SMI) = 2.2/5.0 = 44.0%, a relative risk of 44.0/16.6 = 2.65.
    ! Applied to this model's SUD concept (3.68%): 2.65 x 3.68 = 9.75%.
    ! This identifies the self-medication channel, mh_b_ratio.
    mom(18) = mom_t('SUD rate given SMI (%)      ',  9.75_dp, 0.0_dp, 1.0_dp)
    ! Average fraction of time worked among the employed, Guvenen et al. (2023)
    mom(19) = mom_t('avg hours worked (%)        ', 40.00_dp, 0.0_dp, 1.0_dp)
end subroutine init_targets


!-- model moments, including the conditional ones the aggregator does not carry
subroutine compute_moments(A)
    type(agg_t), intent(in) :: A
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: m, p, ygross
    real(dp) :: sud_unemp, sud_work, hl_sud, elig, vouch_elig
    real(dp) :: spend_sud, inc_sud
    real(dp) :: hcost, totinc, burden50, users_inc, users_m, sud_inc, sud_m
    real(dp) :: hl_smi, smi_work, smi_emp, hl_inc, hl_m
    real(dp) :: wealth, exp_m, exp_light, smi_m, smi_sud, hrs, hrs_m

    p = max(A%pop, 1.0e-12_dp)
    sud_unemp = 0.0_dp; sud_work = 0.0_dp; hl_sud = 0.0_dp
    elig = 0.0_dp; vouch_elig = 0.0_dp
    spend_sud = 0.0_dp; inc_sud = 0.0_dp
    hcost = 0.0_dp; totinc = 0.0_dp; burden50 = 0.0_dp
    users_inc = 0.0_dp; users_m = 0.0_dp; sud_inc = 0.0_dp; sud_m = 0.0_dp
    hl_smi = 0.0_dp; smi_work = 0.0_dp; smi_emp = 0.0_dp
    hl_inc = 0.0_dp; hl_m = 0.0_dp
    wealth = 0.0_dp; exp_m = 0.0_dp; exp_light = 0.0_dp
    smi_m = 0.0_dp; smi_sud = 0.0_dp; hrs = 0.0_dp; hrs_m = 0.0_dp

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
        ygross = income_gross(j, iy, ie, id, im, hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j)))

        ! unemployment among those with SUD, working age only
        if (id == 2 .and. j < j_ret) then
            sud_work = sud_work + m
            if (ie >= 2) sud_unemp = sud_unemp + m
        end if

        ! SUD share of the homeless
        if (ihp == 1 .and. id == 2) hl_sud = hl_sud + m

        ! serious mental illness
        if (ihp == 1) then
            hl_m   = hl_m + m
            hl_inc = hl_inc + m*ygross
            if (im == 2) hl_smi = hl_smi + m
        end if
        if (im == 2) then
            smi_m = smi_m + m
            if (id == 2) smi_sud = smi_sud + m
        end if
        if (im == 2 .and. j < j_ret) then
            smi_work = smi_work + m
            if (ie == 1) smi_emp = smi_emp + m
        end if

        ! voucher take-up among the income-eligible
        if (ygross + max(0.0_dp, r_free*a_grid(ia)) < kappa_V*median_income) then
            elig = elig + m
            if (iv == 2) vouch_elig = vouch_elig + m
        end if

        wealth = wealth + m*a_grid(ia)
        if (j < j_ret .and. ie == 1) then
            hrs_m = hrs_m + m
            hrs   = hrs + m*hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j))
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

        if (id == 2) then
            sud_m   = sud_m + m
            sud_inc = sud_inc + m*max(ygross, 1.0e-8_dp)
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
    mom(12)%model = 100.0_dp*(sud_inc/max(sud_m,1.0e-12_dp)) &
                            /max(totinc/p, 1.0e-12_dp)
    mom(13)%model = 100.0_dp*hl_smi/max(hl_m, 1.0e-12_dp)
    mom(14)%model = 100.0_dp*(1.0_dp - smi_emp/max(smi_work, 1.0e-12_dp))
    mom(15)%model = 100.0_dp*(hl_inc/max(hl_m,1.0e-12_dp)) &
                            /max(totinc/p, 1.0e-12_dp)
    mom(16)%model = A%wealth/max(A%gdp, 1.0e-12_dp)
    mom(17)%model = 100.0_dp*exp_light/max(exp_m, 1.0e-12_dp)
    mom(17)%model = 100.0_dp*A%food/max(A%labinc, 1.0e-12_dp)
    mom(18)%model = 100.0_dp*smi_sud/max(smi_m, 1.0e-12_dp)
    mom(19)%model = 100.0_dp*hrs/max(hrs_m, 1.0e-12_dp)
end subroutine compute_moments


!-- model vs data CDF of the housing-cost-to-income ratio --------------------
! Everyone rents in the model, so the data side is ALL households with owner
! housing valued at imputed rent (8.3% of value). From data/scf_housing_burden.py,
! SCF 2022, ages 26-85.
subroutine print_housing_cdf()
    integer, parameter :: NC = 12
    real(dp) :: cut(NC), dat(NC), mdl(NC)
    integer  :: j, ia, iy, ie, id, iv, im, ihp, k
    real(dp) :: m, y, pop, ratio
    cut = [0.05_dp,0.10_dp,0.15_dp,0.20_dp,0.25_dp,0.30_dp, &
           0.35_dp,0.40_dp,0.50_dp,0.60_dp,0.80_dp,1.00_dp]
    dat = [95.39_dp,89.25_dp,77.23_dp,63.64_dp,50.88_dp,40.62_dp, &
           32.52_dp,25.97_dp,17.49_dp,12.60_dp, 7.06_dp, 4.57_dp]
    mdl = 0.0_dp; pop = 0.0_dp

    do j = 1, n_age
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        pop = pop + m
        ihp = pol_h(ia,iy,ie,id,iv,im,j)
        y   = max(income_gross(j, iy, ie, id, im, hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j))), 1.0e-8_dp)
        if (ihp > 1) then
            ratio = p_rent*h_grid(ihp)/y
        else
            ratio = 0.0_dp                   ! homeless: no housing outlay
        end if
        do k = 1, NC
            if (ratio > cut(k)) mdl(k) = mdl(k) + m
        end do
    end do
    end do
    end do
    end do
    end do
    end do
    end do

    write(*,'(A)') ''
    write(*,'(A)') '  housing cost / income -- share ABOVE each threshold (%)'
    write(*,'(A)') '  ------------------------------------------------------'
    write(*,'(A)') '   threshold      data     model       gap'
    do k = 1, NC
        write(*,'(F12.2,F10.2,F10.2,F10.2)') cut(k), dat(k), &
            100.0_dp*mdl(k)/max(pop,1.0e-12_dp), &
            100.0_dp*mdl(k)/max(pop,1.0e-12_dp) - dat(k)
    end do
    write(*,'(A)') '  ------------------------------------------------------'
end subroutine print_housing_cdf


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
!   aleph              SUD income / average income            -
!   di_coverage        SMI share of the homeless              -
!   mh_b_ratio         SUD rate given SMI                     -
!   kappa_ue_m         unemployment rate given SMI            -
!   prod_pen_m         homeless income / average income       +
!   beta               wealth / GDP                           +
!   cfloor_share       food stamps / labour income            +
!   omega_l            average hours worked                   -
!===============================================================================
! Participation is a near-threshold function of b: below a cutoff everyone
! uses, above it nobody does, and in the dead zone every drug moment reads zero
! and every drug parameter is pushed to a bound by a gap of -1. So pin the level
! by bisection BEFORE touching composition. In partial equilibrium -- the point
! is the household problem, not prices.
subroutine bisect_participation(target_p, iters)
    real(dp), intent(in) :: target_p
    integer,  intent(in) :: iters
    type(agg_t) :: A
    real(dp) :: lo, hi, mid, pmid
    integer  :: k
    lo = log(1.0e-6_dp); hi = log(5.0_dp)
    do k = 1, iters
        mid = 0.5_dp*(lo+hi)
        b_dm(1,1) = exp(mid)
        call refresh_utility_constants()
        call solve_household(); call build_distribution_eq()
        call compute_aggregates(A)
        pmid = 100.0_dp*A%users/max(A%pop,1.0e-12_dp)
        if (pmid > target_p) then
            lo = mid
        else
            hi = mid
        end if
    end do
    b_dm(1,1) = exp(0.5_dp*(lo+hi))
    call refresh_utility_constants()
end subroutine bisect_participation


subroutine calibration_sweep(step)
    real(dp), intent(in) :: step

    call bisect_participation(mom(1)%target, 14)

    ! annual hazard of SUD from light use -- 18.7% was absurd, and raising it far
    ! enough actually LOWERS the SUD rate by deterring experimentation
    call bump(pi_d_low,        gap(2), +1.0_dp, step, 5.0e-3_dp, 0.15_dp)
    call bump(h_homeless,      gap(3), +1.0_dp, step, 1.0e-5_dp, h_grid(2)*0.95_dp)
    call bump(pi_eu_base,      gap(4), +1.0_dp, step, 1.0e-4_dp, 0.9_dp)
    call bump(kappa_ue_d,      gap(5), -1.0_dp, step, 0.02_dp,   1.0_dp)
    call bump(recover_mult_hl, gap(6), -1.0_dp, step, 0.01_dp,   1.0_dp)
    call bump(prob_V,          gap(7), +1.0_dp, step, 1.0e-4_dp, 1.0_dp)
    ! 0.6 means 60% of the consumption bundle on drugs; the bound was doing the
    ! work rather than the moment
    call bump(theta_v,         gap(8), +1.0_dp, step, 0.02_dp,  0.50_dp)
    call bump(theta_h,         gap(9), +1.0_dp, step, 0.02_dp,   0.6_dp)
    call bump(p_rent,          gap(10),+1.0_dp, step, 0.1_dp,    50.0_dp)
    ! Higher flow value of life makes the rich abstain, so both income ratios
    ! fall. aleph is assigned to the SUD ratio because that gradient is the
    ! steep one and so is the more informative of the two.
    call bump(aleph,           gap(12),-1.0_dp, step, 0.5_dp,    5.0e3_dp)
    ! wider DI coverage keeps more of the SMI population housed (IZ's zeta_di)
    call bump(di_coverage,     gap(13),-1.0_dp, step, 0.05_dp,   3.00_dp)
    call bump(kappa_ue_m,      gap(14),-1.0_dp, step, 0.05_dp,   1.00_dp)
    call bump(prod_pen_m,      gap(15),+1.0_dp, step, 0.05_dp,   1.00_dp)
    call bump(beta,            gap(16),+1.0_dp, step, 0.85_dp,   0.995_dp)
    call bump(cfloor_share,    gap(17),+1.0_dp, step, 1.0e-3_dp, 0.60_dp)
    call bump(mh_b_ratio,      gap(18),-1.0_dp, step, 0.02_dp,   1.00_dp)
    ! more weight on leisure -> fewer hours
    call bump(omega_l,         gap(19),-1.0_dp, step, 0.01_dp,   5.00_dp)

    ! keep derived quantities consistent with the parameters just moved
    ! keep SMI prevalence at its data value while persistence moves
    mh_onset = mh_recover*smi_prevalence/(1.0_dp - smi_prevalence)
    mh_trans(1,1) = 1.0_dp - mh_onset;  mh_trans(1,2) = mh_onset
    mh_trans(2,1) = mh_recover;         mh_trans(2,2) = 1.0_dp - mh_recover
    call ergodic(NM, mh_trans, mh_dist0)
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
    b_dm(1,2) = b_dm(1,1)*mh_b_ratio
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
    write(*,'(A,ES12.4)') '   mh_recover (ext): ', mh_recover
    write(*,'(A,ES12.4)') '   di_coverage     : ', di_coverage
    write(*,'(A,ES12.4)') '   mh_b_ratio      : ', mh_b_ratio
    write(*,'(A,ES12.4)') '   mh_onset (deriv): ', mh_onset
    write(*,'(A,ES12.4)') '   kappa_ue_m      : ', kappa_ue_m
    write(*,'(A,ES12.4)') '   prod_pen_m      : ', prod_pen_m
    write(*,'(A,ES12.4)') '   beta            : ', beta
    write(*,'(A,ES12.4)') '   cfloor_share    : ', cfloor_share
    write(*,'(A,ES12.4)') '   omega_l         : ', omega_l
    write(*,'(A)') '  ----------------------------------------------------'
end subroutine print_params

end module calibrate
