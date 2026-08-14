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
    integer, parameter :: NE  = 2          ! 1 = unemployed, 2 = employed
    integer, parameter :: ND  = 2          ! 1 = clean, 2 = SUD
    integer, parameter :: NH  = 4          ! 1 = homeless, 2..4 = rental sizes
    integer, parameter :: NV  = 2          ! 1 = no voucher, 2 = voucher

    ! drug-use regimes: the addiction hazard is a step function of v, so the
    ! continuous choice only ever matters through which regime it lands in.
    ! 1 = abstain (v=0), 2 = light (0 < v <= vbar), 3 = heavy (v > vbar)
    integer, parameter :: NREG = 3

    !-- preferences -----------------------------------------------------------
    real(dp), parameter :: sigma   = 2.0_dp     ! CRRA
    real(dp), parameter :: theta_h = 0.20_dp    ! Cobb-Douglas weight on housing
    real(dp) :: theta_v = 0.10_dp               ! weight on drugs -- SAME for d=0 and d=1
    ! Stone-Geary shifter, BY SUD STATUS (the AE's suggestion). Cobb-Douglas
    ! weights stay invariant to SUD -- so reducing SUD does not mechanically
    ! raise utility from c and h, which is R2/R3's objection -- but b does vary.
    ! A single b cannot match both moments: large b deters clean agents by
    ! pushing the unconstrained v* below zero, which also drives SUD drug
    ! spending to the corner. b_d(1) pins participation, b_d(2) keeps the
    ! interior solution so theta_v pins the 44% expenditure share.
    real(dp) :: b_d(ND) = [4.0e-1_dp, 1.0e-3_dp]
    real(dp) :: aleph   = 3.0_dp                ! flow value of being alive (VSL normalisation)
    real(dp) :: beta    = 0.96_dp

    !-- prices ----------------------------------------------------------------
    real(dp) :: p_rent = 1.0_dp                 ! FIXED: no housing-market GE
    real(dp) :: p_v    = 1.0_dp                 ! endogenous: clears the drug market
    real(dp), parameter :: r = 0.03_dp

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
    real(dp) :: vbar        = 0.05_dp           ! light/heavy threshold
    real(dp) :: pi_d_low    = 0.02_dp
    real(dp), parameter :: heavy_ratio = 6.48_dp
    real(dp) :: pi_d_high
    real(dp) :: recover_housed   = 0.025_dp
    real(dp) :: recover_mult_hl  = 0.5_dp       ! recovery multiplier when homeless

    !-- treatment (endogenous recovery) ---------------------------------------
    ! A clean answer to "Treatment First has no treatment": SUD agents may take
    ! up treatment at a utility cost, which raises the recovery hazard.
    integer  :: allow_treatment = 1
    real(dp) :: treat_cost      = 0.05_dp       ! resource cost, share of average income
    real(dp) :: treat_gain      = 3.0_dp        ! multiplies the recovery hazard

    !-- mortality and employment multipliers ----------------------------------
    real(dp) :: kappa_phi_h = 1.6_dp            ! homelessness mortality multiplier
    real(dp) :: kappa_phi_d = 6.9_dp            ! SUD mortality multiplier
    real(dp) :: kappa_ue_h  = 0.8_dp
    real(dp) :: kappa_ue_d  = 0.6_dp
    real(dp) :: pi_ue_base  = 0.55_dp           ! job finding
    real(dp) :: pi_eu_base  = 0.03_dp           ! job separation

    !-- externality (replaces the loss-of-consortium adjustment) --------------
    ! Enters period utility so it is internalised: it affects the value of life
    ! and therefore drug decisions, rather than being bolted on after solving.
    real(dp) :: kappa_ext = 0.0_dp
    real(dp) :: H_agg     = 0.0_dp              ! aggregate homelessness rate

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
    real(dp), allocatable :: V(:,:,:,:,:,:)       ! (NA,NY,NE,ND,NV,n_age+1)
    integer,  allocatable :: pol_a(:,:,:,:,:,:)   ! index into a_grid
    integer,  allocatable :: pol_h(:,:,:,:,:,:)   ! index into h_grid
    integer,  allocatable :: pol_reg(:,:,:,:,:,:) ! drug regime
    integer,  allocatable :: pol_tr(:,:,:,:,:,:)  ! treatment take-up
    real(dp), allocatable :: pol_c(:,:,:,:,:,:)
    real(dp), allocatable :: pol_v(:,:,:,:,:,:)
    real(dp), allocatable :: dist(:,:,:,:,:,:)
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

    pi_d_high = heavy_ratio * pi_d_low
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
    allocate(V     (NA,NY,NE,ND,NV,n_age+1))
    allocate(pol_a (NA,NY,NE,ND,NV,n_age))
    allocate(pol_h (NA,NY,NE,ND,NV,n_age))
    allocate(pol_reg(NA,NY,NE,ND,NV,n_age))
    allocate(pol_tr(NA,NY,NE,ND,NV,n_age))
    allocate(pol_c (NA,NY,NE,ND,NV,n_age))
    allocate(pol_v (NA,NY,NE,ND,NV,n_age))
    allocate(dist  (NA,NY,NE,ND,NV,n_age))
    V = 0.0_dp; dist = 0.0_dp
    pol_a = 1; pol_h = 1; pol_reg = 1; pol_tr = 0
    pol_c = 0.0_dp; pol_v = 0.0_dp
end subroutine alloc_all


!-- survival probability, given chosen housing and SUD status ----------------
pure function survival(j, ih, id) result(phi)
    integer, intent(in) :: j, ih, id
    real(dp) :: phi, mult, death
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_phi_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_phi_d**real(on_mortality_d,dp)
    death = (1.0_dp - surv_base(j)) * mult
    phi = max(0.0_dp, 1.0_dp - min(death, 1.0_dp))
end function survival


!-- job-finding probability --------------------------------------------------
pure function p_find(ih, id) result(p)
    integer, intent(in) :: ih, id
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_ue_d**real(on_employment_d,dp)
    p = min(1.0_dp, pi_ue_base*mult)
end function p_find


!-- job-separation probability -----------------------------------------------
pure function p_sep(ih, id) result(p)
    integer, intent(in) :: ih, id
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult / kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult / kappa_ue_d**real(on_employment_d,dp)
    p = min(1.0_dp, pi_eu_base*mult)
end function p_sep


!-- recovery hazard, given housing and treatment take-up ---------------------
pure function p_recover(ih, itr) result(p)
    integer, intent(in) :: ih, itr
    real(dp) :: p
    p = recover_housed
    if (ih == 1) p = p * recover_mult_hl**real(on_homeless_fb,dp)
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
