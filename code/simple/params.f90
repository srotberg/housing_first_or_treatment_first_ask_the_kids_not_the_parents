!===============================================================================
! params.f90 -- grids, parameters and shared state for the simplified model
!
! Simplified relative to housing_first_or_treatment_first_SR_v1.f90:
!   - no homeownership, no tenure choice, no mortgages, no negative assets
!   - no housing-market general equilibrium (rent is a fixed price)
!   - drug price p_v is an equilibrium object instead
!   - preferences do NOT depend on SUD status (single theta_v)
!   - no UI-expiration state; employment is a two-point state
!
! State: (j, a, y, e, d, h, eta)
!   j    age
!   a    non-negative financial assets
!   y    labour productivity (permanent x persistent, pre-combined)
!   e    employment (1 = employed, 0 = unemployed)
!   d    SUD status (0 = clean, 1 = SUD)
!   h    housing entered with (1 = homeless, 2..NH = rental sizes)
!   eta  housing voucher held (0/1)
!===============================================================================
module params
    implicit none
    integer, parameter :: dp = kind(1.0d0)

    !-- demographics ----------------------------------------------------------
    integer, parameter :: n_age      = 60      ! model ages, real age 26..85
    integer, parameter :: j_ret     = 41      ! first retirement age index
    integer, parameter :: j_exp     = 30      ! last age at which a clean agent may experiment

    !-- grid sizes ------------------------------------------------------------
    integer, parameter :: NA  = 60         ! non-negative asset grid
    integer, parameter :: NY  = 9          ! labour productivity states
    ! Employment / UI duration. The paper lets UI persist for the whole
    ! unemployment spell; UI in the US is time-limited, and reviewers question
    ! that assumption. Here UI is drawn on ENTRY to unemployment with
    ! probability prob_ui and lasts ONE year only.
    !   1 = employed
    !   2 = unemployed, first year, receiving UI
    !   3 = unemployed without UI (first year non-recipients AND all later years)
    !
    ! Three states suffice, not four. A first-year non-recipient and a
    ! long-term unemployed household have identical income (zero) and identical
    ! continuations (find work with p_find, otherwise stay), so their value
    ! functions are equal and the states merge exactly.
    integer, parameter :: NE  = 3
    integer, parameter :: ND  = 2          ! 1 = clean, 2 = SUD
    integer, parameter :: NH  = 4          ! 1 = homeless, 2..4 = rental sizes
    integer, parameter :: NV  = 2          ! 1 = no voucher, 2 = voucher
    integer, parameter :: NM  = 2          ! 1 = good mental health, 2 = poor

    ! Drug-use regimes. A SINGLE addiction hazard: you become addicted with the
    ! same probability however much you consume, so the only thing that matters
    ! is whether you use at all.
    !   1 = abstain (v = 0), 2 = use (v > 0)
    ! This drops vbar, the light/heavy threshold, and the 6.48 heavy-to-light
    ! ratio, and cuts the inner loop by a third.
    integer, parameter :: NREG = 2

    ! Labour supply is CONTINUOUS, pinned by the intratemporal FOC as in the
    ! original code: equate the marginal utility of the extra after-tax wage to
    ! the marginal utility of leisure, and bracket the root by the sign of the
    ! difference. Given a', hours affect only the flow payoff, never the
    ! continuation value, so the FOC is a scalar solve that never touches the EV
    ! table.
    !
    ! One thing the original does not do and this does: the residual is not
    ! monotone, because the food-stamp and voucher clawbacks kink the budget in
    ! hours, so a single bisection on [0,1] can land on the wrong local optimum.
    ! The interval is split at the kinks and each piece solved exactly. See the
    ! header of solve.f90.
    real(dp), parameter :: hours_tol = 1.0e-8_dp
    integer,  parameter :: hours_maxit = 60

    !-- preferences -----------------------------------------------------------
    real(dp), parameter :: sigma   = 2.0_dp     ! CRRA
    real(dp) :: theta_h = 0.20_dp               ! Cobb-Douglas weight on housing (calibrated)
    real(dp) :: theta_v = 0.10_dp               ! weight on drugs -- SAME for d=0 and d=1
    ! Stone-Geary shifter, BY SUD STATUS (the AE's suggestion). Cobb-Douglas
    ! weights stay invariant to SUD -- so reducing SUD does not mechanically
    ! raise utility from c and h, which is R2/R3's objection -- but b does vary.
    ! A single b cannot match both moments: large b deters clean agents by
    ! pushing the unconstrained v* below zero, which also drives SUD drug
    ! spending to the corner. b_d(1) pins participation, b_d(2) keeps the
    ! interior solution so theta_v pins the 44% expenditure share.
    ! indexed (SUD status, mental health). Poor mental health lowers b, i.e.
    ! raises the marginal utility of the first units of drug use -- the
    ! self-medication channel R1 comment 1(a) is asking about.
    real(dp) :: b_dm(ND,NM) = reshape([4.0e-1_dp, 1.0e-3_dp, &
                                       1.0e-1_dp, 1.0e-3_dp], [ND,NM])
    ! Homelessness scales b DOWN, exactly as poor mental health does: sleeping
    ! rough raises the marginal utility of the first units of use. This is the
    ! only parameter in the model that controls the ELASTICITY OF DRUG USE WITH
    ! RESPECT TO HOUSING ACCESS -- R2's "crux", also R3 and AE A13. Without it
    ! the moment cannot be targeted at all: housing a household with SUD only
    ! raises its resources, and drugs are a normal good, so the model would
    ! predict housing RAISES use, against Milby et al. (2005). Calibrated in the
    ! second stage to the Milby housed-versus-unhoused abstinence ratio.
    real(dp) :: b_hl_ratio = 1.00_dp            ! 1.0 = channel off
    real(dp) :: omega_l  = 0.30_dp              ! weight on leisure (calibrated)
    real(dp), parameter :: sigma_l = 3.0_dp     ! Frisch elasticity 0.5, Chetty (2012)
    real(dp) :: aleph   = 3.0_dp                ! flow value of being alive (VSL normalisation)
    real(dp) :: beta    = 0.96_dp

    !-- prices ----------------------------------------------------------------
    real(dp) :: p_rent = 2.0_dp                 ! no housing-market GE, but calibrated
    real(dp) :: p_v    = 1.0_dp                 ! endogenous: clears the drug market
    real(dp), parameter :: r_free = 0.03_dp

    !-- drug supply: C(V) = psi1/psi2 * V**psi2, so elasticity = 1/(psi2-1).
    !   psi1 is normalised so that p_v = 1 at the benchmark quantity, which keeps
    !   the existing calibration intact; psi2 is set from the supply elasticity.
    real(dp) :: psi1 = 1.0_dp
    real(dp) :: drug_supply_elasticity = 0.5_dp
    real(dp) :: psi2 = 3.0_dp

    !-- taxes and transfers ---------------------------------------------------
    real(dp) :: tau_l = 0.85_dp                 ! level parameter, HSV form
    real(dp), parameter :: xi_tax = 0.85_dp     ! progressivity
    real(dp) :: bequest = 0.0_dp

    !-- housing ---------------------------------------------------------------
    real(dp) :: h_grid(NH)
    real(dp) :: h_homeless = 0.0083_dp

    !-- voucher programme -----------------------------------------------------
    real(dp) :: kappa_V   = 0.5_dp              ! eligibility: income < kappa_V * median
    real(dp) :: kappa_r   = 0.3_dp              ! tenant contribution rate
    real(dp) :: prob_V    = 0.06_dp             ! lottery probability (1.0 = universal)
    integer  :: policy_TF = 0                   ! 0 = Housing First, 1 = Treatment First
    real(dp) :: detect_prob = 1.0_dp            ! P(drug use detected) under TF
    real(dp) :: false_pos   = 0.0_dp            ! P(clean agent flagged) under TF

    !-- SUD process -----------------------------------------------------------
    real(dp) :: pi_d_low    = 0.02_dp           ! annual hazard of SUD given any use
    real(dp) :: recover_housed   = 0.025_dp
    real(dp) :: recover_mult_hl  = 0.5_dp       ! recovery multiplier when homeless

    !-- treatment (endogenous recovery) ---------------------------------------
    ! A clean answer to "Treatment First has no treatment": SUD agents may take
    ! up treatment at a utility cost, which raises the recovery hazard.
    integer  :: allow_treatment = 1
    real(dp) :: treat_cost      = 0.05_dp       ! resource cost, share of average income
    real(dp) :: treat_gain      = 1.35_dp       ! RCT-based; KEY SENSITIVITY

    !-- mental health ---------------------------------------------------------
    ! A persistent state, exogenous, that (i) cuts productivity conditional on
    ! working, (ii) worsens employment transitions, (iii) lowers the SUD
    ! recovery hazard, and (iv) lowers b. R1 comment 1(a). The productivity
    ! penalty is what generates EMPLOYED homeless households with positive but
    ! low income -- R1 comment 2(c)(i) -- which an unemployment effect alone
    ! cannot do.
    ! The state is SERIOUS MENTAL ILLNESS, not "any mental illness". That is the
    ! concept that drives chronic homelessness and disability, and it is the
    ! Imrohoroglu-Zhao channel: in their model labour shocks generate short
    ! homeless spells while health shocks generate chronic homelessness, with
    ! expanded disability income the effective policy for the chronic group.
    !
    ! smi_prevalence pins the ergodic share; mh_onset is DERIVED from it and
    ! mh_recover, so persistence can be calibrated without breaking prevalence.
    real(dp) :: smi_prevalence = 0.055_dp  ! SMI among US adults, NSDUH 2023
    ! EXTERNAL, following Imrohoroglu-Zhao: ten years after diagnosis about 50%
    ! of people with schizophrenia improve to the point they can work and live
    ! independently, so 1-(1-0.5)^(1/10) = 0.067 per year. IZ pin their health
    ! shock with exactly this moment plus the prevalence.
    real(dp) :: mh_recover  = 0.067_dp
    real(dp) :: mh_onset                   ! derived: recover*p/(1-p)
    real(dp) :: prod_pen_m  = 0.55_dp      ! calibrated: homeless income/average
    ! AE question A20. Evidence on the SUD wage penalty CONDITIONAL ON WORKING
    ! is contested -- parts of the older literature find positive effects for
    ! casual use -- while the robust findings are on the employment margin
    ! (~50% more unscheduled absence, ~44% higher turnover), which the model
    ! already captures through kappa_ue_d. Baseline: no direct wage effect.
    real(dp) :: prod_pen_d  = 1.00_dp
    ! Treatment raises the recovery hazard. 3.0 was unsupported: the only clean
    ! randomised estimate is an odds ratio near 1.22 for contingency management.
    ! The TF result runs through this parameter, so report it as a range.
    real(dp) :: treat_gain_lit = 1.35_dp
    real(dp) :: kappa_ue_m  = 0.35_dp      ! calibrated: employment rate given SMI
    ! Standardised mortality ratios for SMI are roughly 2-3, corresponding to
    ! 10-20 years of life expectancy lost. 1.3 was far too low.
    real(dp) :: kappa_phi_m = 2.50_dp
    real(dp) :: rec_mult_m  = 0.50_dp      ! SUD recovery multiplier, poor MH
    ! Disability income for the non-employed with SMI. Roughly two-thirds of
    ! people with schizophrenia receive federal disability insurance, so giving
    ! this group zero income overstates their homelessness. Also the margin
    ! Imrohoroglu-Zhao find effective for the chronically homeless.
    real(dp) :: disab_income = 0.25_dp     ! share of average income
    ! IZ pin the fraction of the homeless with mental illness using DI COVERAGE
    ! (their zeta_di), not persistence. Same here: wider coverage keeps more of
    ! the SMI population housed.
    real(dp) :: di_coverage = 0.60_dp      ! calibrated: SMI share of the homeless
    integer  :: include_disability = 1
    real(dp) :: mh_dist0(NM)               ! newborn distribution over MH
    integer  :: include_mental_health = 1

    !-- mortality and employment multipliers ----------------------------------
    real(dp) :: kappa_phi_h = 1.6_dp            ! homelessness mortality multiplier
    real(dp) :: kappa_phi_d = 6.9_dp            ! SUD mortality multiplier
    real(dp) :: kappa_ue_h  = 0.8_dp
    real(dp) :: kappa_ue_d  = 0.6_dp
    real(dp) :: pi_ue_base  = 0.55_dp           ! job finding
    real(dp) :: pi_eu_base  = 0.03_dp           ! job separation
    real(dp) :: prob_ui     = 0.30_dp           ! share of entrants who draw UI
    real(dp) :: ui_replace  = 0.50_dp           ! replacement rate, first year only

    !-- externality (replaces the loss-of-consortium adjustment) --------------
    ! Enters period utility so it is internalised: it affects the value of life
    ! and therefore drug decisions, rather than being bolted on after solving.
    ! R2's wording is specific: "a large homeless population, ESPECIALLY IF MANY
    ! ARE ADDICTED TO DRUGS, creates a negative externality beyond the fiscal
    ! burden". So the disamenity is weighted by composition, not just the level:
    !
    !     disutility = kappa_ext * ( H_agg + omega_ext * HD_agg )
    !
    ! with HD_agg the share of the population both homeless and with SUD.
    ! Households take both aggregates as given -- that is what makes this an
    ! externality rather than a private cost -- but the aggregates are
    ! equilibrium objects, so the term responds to policy and feeds back into
    ! the value of life and hence into drug decisions. That is the property
    ! kappa_cons lacked and which R1 objected to in comment 3(a).
    !
    ! kappa_ext has no credible point estimate. It is reported as a bounded
    ! sensitivity with kappa_ext = 0 as the conservative case; see
    ! EXTERNALITY.md. Note zero here is a DEFENSIBLE baseline (no externality),
    ! unlike kappa_cons = 0, which reversed the paper's conclusion.
    real(dp) :: kappa_ext = 0.0_dp
    real(dp) :: omega_ext = 2.0_dp              ! extra weight on homeless-with-SUD
    real(dp) :: H_agg     = 0.0_dp              ! aggregate homelessness rate
    real(dp) :: HD_agg    = 0.0_dp              ! homeless AND SUD, share of population

    !-- channel switches, for the mechanism-decomposition arms ----------------
    integer :: on_mortality_d = 1               ! arm 1: SUD -> mortality
    integer :: on_employment_d = 1              ! arm 2: SUD -> employment
    integer :: on_homeless_fb = 1               ! arm 3: homelessness feedback

    !-- fiscal ----------------------------------------------------------------
    real(dp) :: chi_H = 0.252_dp                ! fiscal cost per homeless person
    real(dp) :: chi_D = 0.212_dp                ! fiscal cost per person with SUD
    real(dp) :: cfloor_share = 0.10_dp          ! food-stamp consumption floor

    !-- grids and processes ---------------------------------------------------
    real(dp) :: a_grid(NA)
    real(dp) :: y_grid(NY)
    real(dp) :: y_trans(NY,NY)
    real(dp) :: y_dist0(NY)
    real(dp) :: age_prof(n_age)
    real(dp) :: surv_base(n_age)
    real(dp) :: median_income, avg_income

    !-- solution --------------------------------------------------------------
    real(dp), allocatable :: V(:,:,:,:,:,:,:)       ! (NA,NY,NE,ND,NV,NM,n_age+1)
    integer,  allocatable :: pol_a(:,:,:,:,:,:,:)   ! index into a_grid
    integer,  allocatable :: pol_h(:,:,:,:,:,:,:)   ! index into h_grid
    integer,  allocatable :: pol_reg(:,:,:,:,:,:,:) ! drug regime
    integer,  allocatable :: pol_tr(:,:,:,:,:,:,:)  ! treatment take-up
    real(dp), allocatable :: pol_l(:,:,:,:,:,:,:)   ! hours worked (continuous)
    real(dp), allocatable :: pol_c(:,:,:,:,:,:,:)
    real(dp), allocatable :: pol_v(:,:,:,:,:,:,:)
    real(dp), allocatable :: dist(:,:,:,:,:,:,:)
    real(dp) :: mh_trans(NM,NM)
    ! precomputed powers, to keep pow() out of the inner loop
    real(dp) :: h_pow(NH), alpha_u, beta_u, gamma_u

contains

subroutine setup_grids()
    integer :: i
    real(dp) :: amax, rho, sig, m, step

    !-- assets: dense near zero, where the policy action is ------------------
    amax = 40.0_dp
    do i = 1, NA
        a_grid(i) = amax * ( real(i-1,dp)/real(NA-1,dp) )**3.0_dp
    end do

    !-- housing: homeless plus three rental sizes ----------------------------
    h_grid(1) = h_homeless
    h_grid(2) = 0.040_dp
    h_grid(3) = 0.078_dp
    h_grid(4) = 0.173_dp

    !-- productivity: Rouwenhorst for an AR(1) in logs -----------------------
    rho = 0.90_dp
    sig = 0.20_dp
    call rouwenhorst(NY, rho, sig, y_grid, y_trans)
    do i = 1, NY
        y_grid(i) = exp(y_grid(i))
    end do
    call ergodic(NY, y_trans, y_dist0)

    !-- deterministic age profile and baseline survival ----------------------
    do i = 1, n_age
        if (i < j_ret) then
            age_prof(i) = 1.0_dp + 0.038_dp*real(i,dp) - 0.0006_dp*real(i,dp)**2
        else
            age_prof(i) = 0.0_dp
        end if
        ! smooth increasing hazard, replace with US life-table input
        surv_base(i) = 1.0_dp - min(0.99_dp, 0.0005_dp*exp(0.075_dp*real(i,dp)))
    end do
    surv_base(n_age) = 0.0_dp

    psi2 = 1.0_dp + 1.0_dp/drug_supply_elasticity

    !-- collapse the nested Cobb-Douglas into a single product, and hoist every
    !   power that does not depend on a choice out of the inner loop:
    !   comp = c**alpha_u * h**beta_u * (v+b)**gamma_u
    alpha_u = (1.0_dp-theta_h)*(1.0_dp-theta_v)
    beta_u  = theta_h*(1.0_dp-theta_v)
    gamma_u = theta_v
    do i = 1, NH
        h_pow(i) = h_grid(i)**beta_u
    end do

    !-- mental-health transition and its ergodic newborn distribution --------
    ! onset is implied by the target prevalence and the recovery rate, so
    ! calibrating persistence never moves the prevalence off its data value
    mh_onset = mh_recover*smi_prevalence/(1.0_dp - smi_prevalence)
    if (include_mental_health == 1) then
        mh_trans(1,1) = 1.0_dp - mh_onset;   mh_trans(1,2) = mh_onset
        mh_trans(2,1) = mh_recover;          mh_trans(2,2) = 1.0_dp - mh_recover
    else
        mh_trans = 0.0_dp; mh_trans(1,1) = 1.0_dp; mh_trans(2,1) = 1.0_dp
    end if
    call ergodic(NM, mh_trans, mh_dist0)

    m = 0.0_dp
    do i = 1, NY
        m = m + y_dist0(i)*y_grid(i)
    end do
    avg_income    = m
    median_income = m
    step = 0.0_dp
end subroutine setup_grids


subroutine alloc_all()
    ! NOTE: housing entered with (h) is NOT a state variable here. Survival,
    ! employment transitions and the recovery hazard all condition on the
    ! CHOSEN h', and renters face no adjustment cost, so the housing a
    ! household arrives with is payoff-irrelevant. Carrying it would replicate
    ! the entire problem NH times. Reinstate it if moving costs are added.
    allocate(V     (NA,NY,NE,ND,NV,NM,n_age+1))
    allocate(pol_a (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_h (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_reg(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_tr(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_l (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_c (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_v (NA,NY,NE,ND,NV,NM,n_age))
    allocate(dist  (NA,NY,NE,ND,NV,NM,n_age))
    V = 0.0_dp; dist = 0.0_dp
    pol_a = 1; pol_h = 1; pol_reg = 1; pol_tr = 0; pol_l = 0.0_dp
    pol_c = 0.0_dp; pol_v = 0.0_dp
end subroutine alloc_all


!-- survival probability, given chosen housing and SUD status ----------------
! hours are a choice only for the employed of working age; everyone else
! supplies zero and consumes full leisure
pure function hours_of(j, ie, hstar) result(h)
    integer,  intent(in) :: j, ie
    real(dp), intent(in) :: hstar
    real(dp) :: h
    if (j < j_ret .and. ie == 1) then
        h = hstar
    else
        h = 0.0_dp
    end if
end function hours_of


!-- Stone-Geary shifter, given SUD status, mental health and CHOSEN housing --
pure function b_of(id, im, ih) result(b)
    integer, intent(in) :: id, im, ih
    real(dp) :: b
    b = b_dm(id,im)
    if (ih == 1) b = b * b_hl_ratio
end function b_of


pure function survival(j, ih, id, im) result(phi)
    integer, intent(in) :: j, ih, id, im
    real(dp) :: phi, mult, death
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_phi_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_phi_d**real(on_mortality_d,dp)
    if (im == 2) mult = mult * kappa_phi_m
    death = (1.0_dp - surv_base(j)) * mult
    phi = max(0.0_dp, 1.0_dp - min(death, 1.0_dp))
end function survival


!-- job-finding probability --------------------------------------------------
pure function p_find(ih, id, im) result(p)
    integer, intent(in) :: ih, id, im
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_ue_d**real(on_employment_d,dp)
    if (im == 2) mult = mult * kappa_ue_m
    p = min(1.0_dp, pi_ue_base*mult)
end function p_find


!-- job-separation probability -----------------------------------------------
pure function p_sep(ih, id, im) result(p)
    integer, intent(in) :: ih, id, im
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult / kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult / kappa_ue_d**real(on_employment_d,dp)
    if (im == 2) mult = mult / kappa_ue_m
    p = min(1.0_dp, pi_eu_base*mult)
end function p_sep


!-- employment transition over the four-state (employment, UI duration) grid --
! Row ie of the kernel, given chosen housing, SUD status and mental health.
pure subroutine emp_trans(ie, ih, id, im, s)
    integer,  intent(in)  :: ie, ih, id, im
    real(dp), intent(out) :: s(NE)
    real(dp) :: pf, ps
    pf = p_find(ih, id, im)
    ps = p_sep(ih, id, im)
    s = 0.0_dp
    select case (ie)
    case (1)                       ! employed
        s(1) = 1.0_dp - ps
        s(2) = ps * prob_ui        ! separate into UI
        s(3) = ps * (1.0_dp - prob_ui)
    case (2)                       ! UI year -- benefit expires now
        s(1) = pf
        s(3) = 1.0_dp - pf
    case (3)                       ! no UI, any duration
        s(1) = pf
        s(3) = 1.0_dp - pf
    end select
end subroutine emp_trans


!-- recovery hazard, given housing and treatment take-up ---------------------
pure function p_recover(ih, itr, im) result(p)
    integer, intent(in) :: ih, itr, im
    real(dp) :: p
    p = recover_housed
    if (ih == 1) p = p * recover_mult_hl**real(on_homeless_fb,dp)
    if (im == 2) p = p * rec_mult_m
    if (itr == 1) p = p * treat_gain
    p = min(1.0_dp, p)
end function p_recover


!=============================== helpers =====================================

subroutine rouwenhorst(n, rho, sig, grid, trans)
    integer, intent(in) :: n
    real(dp), intent(in) :: rho, sig
    real(dp), intent(out) :: grid(n), trans(n,n)
    real(dp) :: p, nu, t2(2,2)
    real(dp), allocatable :: tk(:,:), tn(:,:)
    integer :: k, i

    p  = (1.0_dp + rho)/2.0_dp
    nu = sig*sqrt(real(n-1,dp)/(1.0_dp-rho**2))
    do i = 1, n
        grid(i) = -nu + 2.0_dp*nu*real(i-1,dp)/real(n-1,dp)
    end do

    t2(1,:) = [p, 1.0_dp-p]
    t2(2,:) = [1.0_dp-p, p]
    allocate(tk(2,2)); tk = t2
    do k = 3, n
        allocate(tn(k,k)); tn = 0.0_dp
        tn(1:k-1,1:k-1) = tn(1:k-1,1:k-1) + p*tk
        tn(1:k-1,2:k)   = tn(1:k-1,2:k)   + (1.0_dp-p)*tk
        tn(2:k,1:k-1)   = tn(2:k,1:k-1)   + (1.0_dp-p)*tk
        tn(2:k,2:k)     = tn(2:k,2:k)     + p*tk
        tn(2:k-1,:) = tn(2:k-1,:)/2.0_dp
        deallocate(tk); allocate(tk(k,k)); tk = tn
        deallocate(tn)
    end do
    trans = tk
    deallocate(tk)
end subroutine rouwenhorst


subroutine ergodic(n, trans, d)
    integer, intent(in) :: n
    real(dp), intent(in) :: trans(n,n)
    real(dp), intent(out) :: d(n)
    real(dp) :: dn(n)
    integer :: it, i, k
    d = 1.0_dp/real(n,dp)
    do it = 1, 5000
        dn = 0.0_dp
        do i = 1, n
            do k = 1, n
                dn(k) = dn(k) + d(i)*trans(i,k)
            end do
        end do
        if (maxval(abs(dn-d)) < 1.0e-14_dp) then
            d = dn; return
        end if
        d = dn
    end do
end subroutine ergodic

end module params
