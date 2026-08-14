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

    integer, parameter :: NMOM = 26
    integer, parameter :: NPAR = 22   ! calibrated parameters, for the snapshot

    type :: mom_t
        character(len=28) :: name
        real(dp) :: target
        real(dp) :: model
        real(dp) :: weight
        ! UNTARGETED moments are computed and printed but no parameter is bumped
        ! on them and they are excluded from max_gap(). Letting a validation
        ! moment into the convergence statistic would report the calibration as
        ! failing on something it is deliberately not fitting.
        logical  :: targeted = .true.
    end type mom_t

    type(mom_t) :: mom(NMOM)   ! NB: not 'M' -- would shadow local scalar 'm'

contains

subroutine init_targets()
    ! NSDUH 2024, ages 26+ (the model's range), from data/nsduh_gradients.py.
    ! The paper's 4% and 2% were built for ages 18+ on a different construction.
    mom(1) = mom_t('drug participation (%)     ',  5.13_dp, 0.0_dp, 1.0_dp)
    mom(2) = mom_t('SUD rate (%)               ',  3.68_dp, 0.0_dp, 1.0_dp)
    ! HUD PIT 2024, converted to HOUSEHOLDS -- the model's agent is a household,
    ! so the person count is the wrong unit. 467,020 homeless individuals (one
    ! household each) plus 57,563 homeless family households = 524,583, against
    ! 131,332,360 occupied units (ACS B25042). The person rate is 0.195%, which
    ! is what makes this look like a doubling; it is a unit conversion, not a
    ! change of concept. 2023 vintage to match the ACS, NSDUH and HUD files.
    ! The model covers ages 26-85, ~94% of US households, and unaccompanied
    ! youth are a similar share of the homeless count, so the restriction
    ! roughly cancels in the ratio.
    mom(3) = mom_t('homelessness rate (%)      ',  0.399_dp, 0.0_dp, 1.0_dp)
    mom(4) = mom_t('unemployment rate (%)      ',  4.90_dp, 0.0_dp, 1.0_dp)
    ! MEASURED, not asserted. NSDUH 2024 microdata, ages 26+, unemployment
    ! over the labour force, weighted by analwt2_c:
    !   everyone                 6.65%
    !   no drug use disorder     6.04%
    !   any drug use disorder   12.72%
    !   moderate/severe drug UD 16.25%   <- the model's SUD concept
    ! The old 26.90% had no provenance and implied a relative risk of 5.49
    ! against an overall rate of 4.9%; the data says 2.44. So the model's
    ! SUD-to-employment channel was roughly 2.25 times too strong.
    !
    ! That matters beyond one moment. R1's rival hypothesis is that the
    ! employment channel does the work rather than mortality. The model was
    ! biased TOWARD that reading on both sides at once: this channel too
    ! strong, and the mortality channel running at about a fifth of its
    ! measured strength before today's life table and multiplier fixes.
    mom(5) = mom_t('unemp rate | SUD (%)       ', 16.25_dp, 0.0_dp, 1.0_dp)
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
    ! The two grid parameters are now identified from the SIZE distribution the
    ! grid represents, not from its budget consequences. ACS B25042 (Tenure by
    ! Bedrooms, occupied units, 2023, N = 131,332,360): 13.21 / 24.12 / 62.67
    ! per cent across {0,1}, {2} and {3+} bedrooms. All households, not renters:
    ! the model has no homeownership, housing is a pure flow at p_r*h, so an
    ! owner's analogue is imputed rent and the size distribution over occupied
    ! units is the right object. Medium is the residual and is not targeted.
    mom(10) = mom_t('housed in SMALL units (%)   ', 13.21_dp, 0.0_dp, 1.0_dp)
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
    ! Rent is normalised to one, so the housing GRID is the calibrated object
    ! and every point of it is pinned by a moment -- R2 comment D1. The level of
    ! the rental grid moves the upper tail of the housing-burden distribution
    ! and its spread moves the middle, so two points of the SCF 2022 CDF
    ! identify the two grid parameters. Both come from data/scf_housing_burden.py.
    mom(20) = mom_t('housed in LARGE units (%)   ', 62.67_dp, 0.0_dp, 1.0_dp)
    ! Treatment take-up among those with SUD. This is what disciplines the
    ! utility cost of treatment, which was previously a free parameter with no
    ! source at all -- and treatment is the mechanism the whole Treatment First
    ! result runs through. NSDUH 2023: roughly a quarter of people with a
    ! past-year SUD received any substance use treatment. VERIFY against the
    ! detailed tables before this goes in the paper.
    mom(21) = mom_t('treatment take-up | SUD (%) ', 24.00_dp, 0.0_dp, 1.0_dp)
    ! SMI prevalence is now a TARGET rather than an identity. Onset used to be
    ! derived from prevalence and the recovery rate, which only works when onset
    ! is the same for everyone. It is not: SUD raises it (see mh_onset_sud), so
    ! the base onset rate has to be calibrated to hold prevalence at its data
    ! value while the SUD multiplier operates.
    mom(22) = mom_t('SMI prevalence (%)          ',  5.50_dp, 0.0_dp, 1.0_dp)
    ! THE VALUE OF LIFE, and why it moved.
    ! aleph used to be calibrated to the SUD income ratio, which pins its effect
    ! on WHO uses drugs but says nothing about its LEVEL. The structural smoke
    ! test found that at those parameters 64.6% of the population had V < 0 --
    ! they would rather be dead. For those households the mortality cost of drug
    ! use is a mortality BENEFIT, which silently inverts the paper's central
    ! mechanism for exactly the people the policy targets.
    ! aleph is now pinned externally by the model-implied value of a statistical
    ! life, $7.5m (Viscusi and Aldy 2003; EPA 2010), which is the paper's own
    ! stated approach and which disciplines the level. The SUD income ratio moves
    ! to prod_pen_d -- the direct wage penalty the AE asks about in A20 -- so it
    ! is still targeted, and prod_pen_d = 1 becomes the robustness run.
    mom(23) = mom_t('model VSL ($m)              ',  7.50_dp, 0.0_dp, 1.0_dp)
    ! UNTARGETED from here on -- computed and printed, no parameter bumped on
    ! them. They were the identification for the housing grid until B25042
    ! arrived; demoting them turns them into an out-of-sample check, which is a
    ! stronger thing to show a referee than a moment the grid was fitted to.
    mom(25) = mom_t('[val] housing cost>50% (%)  ', 17.49_dp, 0.0_dp, 1.0_dp, .false.)
    mom(26) = mom_t('[val] housing cost>30% (%)  ', 40.62_dp, 0.0_dp, 1.0_dp, .false.)
    ! b_1 HAS A TARGET NOW. It used to be asserted small enough to keep the drug
    ! choice interior, which is a statement about numerical convenience rather
    ! than about data, and it left the Milby moment undefined: with abstention
    ! impossible for a household with SUD, the NH arm abstains 0% of the time and
    ! the housing-access ratio is 0/0.
    ! b_1 governs exactly how costly abstention is for a household that already
    ! has SUD, so the moment that identifies it is the abstinence rate in Milby's
    ! NO-HOUSING arm: 4.48 consecutive weeks abstinent out of 24, or 18.7%,
    ! among homeless adults with SUD -- the same population and the same trial
    ! that gives the housing-access ratio. One arm pins the level, the contrast
    ! between arms pins the treatment effect.
    mom(24) = mom_t('abstain rate|SUD & homeless%', 18.67_dp, 0.0_dp, 1.0_dp)
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
    real(dp) :: burden30, treated_sud, hl_sud_m, hl_sud_abst
    real(dp) :: housed_m, hsmall_m, hlarge_m

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
    burden30 = 0.0_dp; treated_sud = 0.0_dp
    housed_m = 0.0_dp; hsmall_m = 0.0_dp; hlarge_m = 0.0_dp
    hl_sud_m = 0.0_dp; hl_sud_abst = 0.0_dp

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
        if (ihp == 1 .and. id == 2) then
            hl_sud = hl_sud + m
            ! Milby's NH arm: homeless adults with SUD, abstaining or not
            hl_sud_m = hl_sud_m + m
            if (pol_v(ia,iy,ie,id,iv,im,j) <= 0.0_dp) hl_sud_abst = hl_sud_abst + m
        end if

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
            if (p_rent*h_grid(ihp) > 0.3_dp*max(ygross,1.0e-8_dp)) burden30 = burden30 + m
            ! size shares are over the HOUSED, matching the ACS universe of
            ! occupied units -- the homeless are not a housing unit
            housed_m = housed_m + m
            if (ihp == 2) hsmall_m = hsmall_m + m
            if (ihp == NH) hlarge_m = hlarge_m + m
        end if

        ! income of drug users, for the gradient moment
        if (pol_v(ia,iy,ie,id,iv,im,j) > 0.0_dp) then
            users_m   = users_m + m
            users_inc = users_inc + m*max(ygross, 1.0e-8_dp)
        end if

        if (id == 2) then
            sud_m   = sud_m + m
            sud_inc = sud_inc + m*max(ygross, 1.0e-8_dp)
            if (pol_tr(ia,iy,ie,id,iv,im,j) == 1) treated_sud = treated_sud + m
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
    mom(10)%model = 100.0_dp*hsmall_m/max(housed_m,1.0e-12_dp)
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
    mom(20)%model = 100.0_dp*hlarge_m/max(housed_m,1.0e-12_dp)
    mom(21)%model = 100.0_dp*treated_sud/max(sud_m, 1.0e-12_dp)
    mom(22)%model = 100.0_dp*A%poormh/p
    mom(23)%model = model_vsl()
    mom(24)%model = 100.0_dp*hl_sud_abst/max(hl_sud_m, 1.0e-12_dp)
    mom(25)%model = 100.0_dp*burden50/p
    mom(26)%model = 100.0_dp*burden30/p
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


!-- the share of the population that would rather be dead ---------------------
! Death is worth zero, so V < 0 means a household strictly prefers it, and drug
! mortality becomes a reward rather than a deterrent. Printed every sweep because
! it is a property no single moment guards and because it silently inverts the
! paper's central mechanism when it goes wrong.
function mass_negative_V() result(f)
    real(dp) :: f, m, tot, neg
    integer  :: j, ia, iy, ie, id, iv, im
    tot = 0.0_dp; neg = 0.0_dp
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        tot = tot + m
        if (V(ia,iy,ie,id,iv,im,j) < 0.0_dp) neg = neg + m
    end do; end do; end do
    end do; end do; end do
    end do
    f = neg/max(tot,1.0e-12_dp)
end function mass_negative_V


function max_gap() result(g)
    real(dp) :: g
    integer  :: i
    g = 0.0_dp
    do i = 1, NMOM
        if (.not. mom(i)%targeted) cycle
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
!   mh_onset           SMI prevalence                          +
!   b_dm(1,1) clean    drug participation                    -
!   b_dm(2,1) SUD      abstain rate | SUD and homeless        +
!   pi_d_low           SUD rate                              +
!   h_homeless         homelessness rate                     +
!   pi_eu_base         unemployment rate                     +
!   kappa_ue_d         unemployment rate | SUD               -
!   recover_mult_hl    SUD share of homeless                 -
!   prob_V             voucher recipients / eligible         +
!   theta_v            drug spend / income | SUD             +
!   theta_h            housing cost / income (aggregate)      +
!   h_small            share with housing cost > 50%           +
!   h_spread           share with housing cost > 30%           +
!   treat_ucost        treatment take-up given SUD             -
!   aleph              model VSL ($7.5m)                       +
!   prod_pen_d         SUD income / average income             +
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


! `nbis` is the bisection depth. Four brackets at ten iterations each is forty
! household solves per sweep, which dominates everything else; early sweeps do
! not need that precision because the other sixteen parameters are still moving
! by percent, so the caller raises it as the calibration settles.
subroutine calibration_sweep(step, nbis)
    real(dp), intent(in) :: step
    integer,  intent(in) :: nbis

    ! annual hazard of SUD from light use -- 18.7% was absurd, and raising it far
    ! enough actually LOWERS the SUD rate by deterring experimentation
    ! pi_d_low is bracketed in polish_levels, not bumped: the SUD rate is a
    ! LEVEL moment on a small target and a proportional step cannot hold it
    call bump(pi_eu_base,      gap(4), +1.0_dp, step, 1.0e-4_dp, 0.9_dp)
    call bump(kappa_ue_d,      gap(5), -1.0_dp, step, 0.02_dp,   1.0_dp)
    call bump(recover_mult_hl, gap(6), -1.0_dp, step, 0.01_dp,   1.0_dp)
    call bump(prob_V,          gap(7), +1.0_dp, step, 1.0e-4_dp, 1.0_dp)
    ! 0.6 means 60% of the consumption bundle on drugs; the bound was doing the
    ! work rather than the moment
    call bump(theta_v,         gap(8), +1.0_dp, step, 0.02_dp,  0.50_dp)
    call bump(theta_h,         gap(9), +1.0_dp, step, 0.02_dp,   0.6_dp)
    ! rent is normalised, so the GRID carries these two moments
    call bump(h_small,         gap(10),+1.0_dp, step, 5.0e-3_dp, 0.60_dp)
    call bump(h_spread,        gap(20),+1.0_dp, step, 1.05_dp,   3.00_dp)
    ! treat_ucost is NOT bumped: take-up is step-like in it (see the bracket
    ! block below), and bumping it proportionally while aleph's bracket moves the
    ! threshold underneath it pinned take-up at 99.9% for three sweeps.
    ! The SUD income ratio moves to the direct wage penalty, freeing aleph for
    ! the VSL target below. The AE asks about this penalty in A20; calibrating it
    ! is better discipline than asserting 1.0, and 1.0 becomes the robustness run.
    call bump(prod_pen_d,      gap(12),+1.0_dp, step, 0.30_dp,   1.00_dp)
    ! wider DI coverage keeps more of the SMI population housed (IZ's zeta_di)
    call bump(di_coverage,     gap(13),-1.0_dp, step, 0.05_dp,   3.00_dp)
    call bump(kappa_ue_m,      gap(14),-1.0_dp, step, 0.05_dp,   1.00_dp)
    call bump(prod_pen_m,      gap(15),+1.0_dp, step, 0.05_dp,   1.00_dp)
    call bump(cfloor_share,    gap(17),+1.0_dp, step, 1.0e-3_dp, 0.60_dp)
    call bump(mh_b_ratio,      gap(18),-1.0_dp, step, 0.02_dp,   1.00_dp)
    ! bigger Stone-Geary endowment for a household with SUD -> abstaining costs
    ! it less -> more of them abstain
    call bump(b_dm(2,1),       gap(24),+1.0_dp, step, 1.0e-5_dp, 5.0_dp)
    ! more weight on leisure -> fewer hours
    call bump(omega_l,         gap(19),-1.0_dp, step, 0.01_dp,   5.00_dp)

    call refresh_utility_constants()

    ! ---- bracket the four step-like moments LAST -----------------------------
    ! Bracketing first and bumping afterwards means every sweep undoes its own
    ! bracketing: sweep 2 set participation to its 5.13% target and then the
    ! bumps carried it to 21.6%, so the next sweep's bisection had to start over
    ! and the calibration oscillated instead of converging. Running the brackets
    ! last leaves each sweep ENDING on target for the four moments that are
    ! step-like in their own parameter, and it is also the state the next
    ! equilibrium is solved at.
    call bisect_on(3, mom(16)%target, nbis)   ! beta        -> wealth / GDP
    call bisect_on(2, mom(3)%target,  nbis)   ! h_homeless  -> homelessness rate
    call bisect_on(4, mom(22)%target, nbis)   ! mh_onset    -> SMI prevalence
    call bisect_on(5, mom(23)%target, nbis)   ! aleph       -> model VSL
    ! AFTER aleph: aleph is the value of staying alive, treatment is the
    ! technology that buys survival, so raising aleph shifts the take-up
    ! threshold in treat_ucost. Bracketing take-up before aleph would be undone
    ! within the same sweep.
    call bisect_on(6, mom(21)%target, nbis)   ! treat_ucost -> treatment take-up
    call bisect_on(1, mom(1)%target,  nbis)   ! b           -> participation
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


!===============================================================================
! Bisection for the near-threshold moments.
!
! Three moments are step-like in their own parameter and destroy a
! proportional-step sweep if they are bumped rather than bracketed:
!
!   participation in b       below a cutoff everyone uses, above it nobody does
!   homelessness in h_homeless   0.12% -> 3.29% for a 35% change in the parameter
!   wealth/GDP in beta       5.46 at beta = 0.995, 0.38 at beta = 0.85
!
! A multiplicative step of even 0.9 moves a discount factor from 0.96 to 0.864,
! which is enormous in a life-cycle model; the first attempt at this calibration
! slammed beta into its lower bound on sweep 3 and took every other moment with
! it. All three are bracketed instead, in partial equilibrium -- prices move
! slowly relative to these parameters and the outer loop re-clears them.
!===============================================================================
subroutine bisect_on(which, target_val, iters)
    integer,  intent(in) :: which          ! 1 = b, 2 = h_homeless, 3 = beta
    real(dp), intent(in) :: target_val
    integer,  intent(in) :: iters
    type(agg_t) :: A
    real(dp) :: lo, hi, mid, fmid
    integer  :: k
    logical  :: rising

    select case (which)
    case (1)
        lo = log(1.0e-6_dp); hi = log(5.0_dp);    rising = .false.  ! more b, less use
    case (2)
        lo = log(1.0e-5_dp); hi = log(h_grid(2)*0.98_dp); rising = .true.
    case (3)
        lo = log(0.900_dp);  hi = log(0.9990_dp); rising = .true.
    case (4)
        lo = log(1.0e-5_dp); hi = log(0.20_dp);   rising = .true.
    case (5)
        lo = log(1.0_dp);    hi = log(1.0e5_dp);  rising = .true.
    case (6)
        lo = log(1.0e-4_dp); hi = log(20.0_dp);   rising = .false. ! more stigma, less take-up
    case (7)
        lo = log(2.0e-3_dp); hi = log(0.60_dp);   rising = .true.  ! faster conversion, more SUD
    end select

    do k = 1, iters
        mid = 0.5_dp*(lo+hi)
        select case (which)
        case (1); b_dm(1,1)  = exp(mid)
        case (2); h_homeless = exp(mid)
        case (3); beta       = exp(mid)
        case (4); mh_onset    = exp(mid)
        case (5); aleph       = exp(mid)
        case (6); treat_ucost = exp(mid)
        case (7); pi_d_low    = exp(mid)
        end select
        call refresh_utility_constants()
        call solve_household(); call build_distribution_eq()
        call compute_aggregates(A)
        select case (which)
        case (1); fmid = 100.0_dp*A%users/max(A%pop,1.0e-12_dp)
        case (2); fmid = 100.0_dp*A%homeless/max(A%pop,1.0e-12_dp)
        case (3); fmid = A%wealth/max(A%gdp,1.0e-12_dp)
        case (4); fmid = 100.0_dp*A%poormh/max(A%pop,1.0e-12_dp)
        case (5); fmid = model_vsl()
        ! take-up conditional on SUD is accumulated inside compute_moments, not
        ! carried on agg_t; recomputing the moment here also guarantees the
        ! bracket and the printed table are reading the same number
        case (6); call compute_moments(A); fmid = mom(21)%model
        end select
        if ((fmid > target_val) .eqv. rising) then
            hi = mid
        else
            lo = mid
        end if
    end do

    mid = 0.5_dp*(lo+hi)
    select case (which)
    case (1); b_dm(1,1)  = exp(mid)
    case (2); h_homeless = exp(mid)
    case (3); beta       = exp(mid)
    case (4); mh_onset    = exp(mid)
    case (5); aleph       = exp(mid)
    case (6); treat_ucost = exp(mid)
    case (7); pi_d_low    = exp(mid)
    end select
    call refresh_utility_constants()
end subroutine bisect_on


!===============================================================================
! Polish the LEVEL moments at cleared prices.
!
! The brackets inside calibration_sweep run in partial equilibrium, and the
! solve_equilibrium that follows then moves prices and drags them off target: a
! participation rate bracketed exactly onto 5.13% was being REPORTED at 3.62%,
! and the printed moment was never the bracketed one. On a target of 5% that is
! a 29% relative miss on the single most important moment in the paper.
!
! So re-bracket at the cleared prices and re-clear. Two rounds, because b and
! pi_d_low are not independent -- a higher conversion hazard deters
! experimentation, so pinning the SUD rate moves participation and vice versa --
! and because prices move again after each pass. Two is enough: the price
! response to these is second order once the level is close.
!===============================================================================
subroutine polish_levels(nbis)
    integer, intent(in) :: nbis
    integer :: round
    do round = 1, 2
        call bisect_on(1, mom(1)%target,  nbis)   ! b          -> participation
        call bisect_on(7, mom(2)%target,  nbis)   ! pi_d_low   -> SUD rate
        call bisect_on(2, mom(3)%target,  nbis)   ! h_homeless -> homelessness
        call solve_equilibrium(12, 3.0e-3_dp, .false.)
    end do
end subroutine polish_levels


!===============================================================================
! Snapshot of every calibrated parameter, so a divergent tail cannot destroy a
! good intermediate fit: the sweep loop keeps the best vector it has seen.
!===============================================================================
subroutine save_params(v)
    real(dp), intent(out) :: v(NPAR)
    v = [ b_dm(1,1), pi_d_low, h_homeless, pi_eu_base, kappa_ue_d, &
          recover_mult_hl, prob_V, theta_v, theta_h, h_small, aleph, &
          di_coverage, kappa_ue_m, prod_pen_m, beta, cfloor_share, mh_b_ratio, &
          h_spread, treat_ucost, mh_onset, prod_pen_d, b_dm(2,1) ]
end subroutine save_params

subroutine load_params(v)
    real(dp), intent(in) :: v(NPAR)
    b_dm(1,1)=v(1);  pi_d_low=v(2);   h_homeless=v(3);  pi_eu_base=v(4)
    kappa_ue_d=v(5); recover_mult_hl=v(6); prob_V=v(7); theta_v=v(8)
    theta_h=v(9);    h_small=v(10);   aleph=v(11);      di_coverage=v(12)
    kappa_ue_m=v(13);prod_pen_m=v(14);beta=v(15);       cfloor_share=v(16)
    mh_b_ratio=v(17);h_spread=v(18);  treat_ucost=v(19); mh_onset=v(20)
    prod_pen_d=v(21); b_dm(2,1)=v(22)
    call refresh_utility_constants()
end subroutine load_params


!-- multiplicative update, clamped to [lo, hi] -------------------------------
subroutine bump(par, g, sgn, step, lo, hi)
    real(dp), intent(inout) :: par
    real(dp), intent(in)    :: g, sgn, step, lo, hi
    real(dp) :: fac
    ! model above target and dM/dpar > 0  =>  reduce the parameter
    ! parameters like b_d(1) must move orders of magnitude, so allow a wide
    ! multiplicative step rather than the +-15% a narrow clamp would permit
    fac = 1.0_dp - sgn*step*g
    fac = min(max(fac, 0.65_dp), 1.55_dp)
    par = min(max(par*fac, lo), hi)
end subroutine bump


subroutine refresh_utility_constants()
    integer :: i
    b_dm(1,2) = b_dm(1,1)*mh_b_ratio
    b_dm(2,2) = b_dm(2,1)*mh_b_ratio
    alpha_u = (1.0_dp-theta_h)*(1.0_dp-theta_v)
    beta_u  = theta_h*(1.0_dp-theta_v)
    gamma_u = theta_v
    call build_housing_grid()
    call build_mh_trans()
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
    write(*,'(A,ES12.4)') '   h_small         : ', h_small
    write(*,'(A,ES12.4)') '   h_spread        : ', h_spread
    write(*,'(A,ES12.4)') '   treat_ucost     : ', treat_ucost
    write(*,'(A,ES12.4)') '   theta_h         : ', theta_h
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
