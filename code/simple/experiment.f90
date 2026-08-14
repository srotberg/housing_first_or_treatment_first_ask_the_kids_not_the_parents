!===============================================================================
! experiment.f90 -- the SECOND-STAGE calibration: short-run experimental moments
!
! The first stage matches a cross-section. It says nothing about the RESPONSES
! the paper's conclusion depends on, and every report says so:
!
!   R2 C1  "all of the welfare results rest on whether the model has an accurate
!           elasticity of drug use to housing access"
!   R3, AE A13  the same, independently
!   R1 2(d), 2(e)  match policy-relevant elasticities from the RCT literature;
!                  the price-elasticity moment is not replicable as written
!
! These are SHORT-RUN objects. An RCT hands a treatment to a selected group and
! measures them a few months later; it does not move aggregate prices and it
! does not wait for a new stationary distribution. So the experiment here holds
! prices at the benchmark, takes the benchmark distribution as the initial
! condition, restricts to the trial's eligible population, applies the arm's
! rules, and pushes forward. That is a different computation from stage one and
! it is why it lives in its own module.
!
! Three objects:
!
!   1. HOUSING-ACCESS ELASTICITY -- Milby et al. (2005), the three-arm trial of
!      196 cocaine-dependent homeless adults. Calibrates b_hl_ratio.
!   2. DRUG-PRICE PARTICIPATION ELASTICITY -- calibrates kappa_phi_d, and is
!      only computable now that p_v is an equilibrium object (R3 M2d).
!   3. MODEL-IMPLIED VSL -- reported, since aleph currently carries a
!      first-stage moment. See the note in second_stage().
!===============================================================================
module experiment
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none

    ! Milby et al. (2005), mean consecutive weeks abstinent out of 24:
    !   NH   no housing                        4.48
    !   NACH housing, no abstinence condition  6.60   <- Housing First
    !   ACH  housing contingent on abstinence  8.32   <- Treatment First
    ! Ratios rather than levels: "weeks consecutively abstinent out of 24" is
    ! not the same object as "abstains this model year", but the TREATMENT
    ! EFFECT is comparable, and the ratio is what the referees are asking the
    ! model to reproduce.
    real(dp), parameter :: milby_nh   = 4.48_dp
    real(dp), parameter :: milby_nach = 6.60_dp
    real(dp), parameter :: milby_ach  = 8.32_dp
    real(dp), parameter :: target_housing_ratio = milby_nach/milby_nh   ! 1.473
    ! NACH vs ACH is P = .091 in the raw randomised comparison and the GEE
    ! models report the two housed arms "did not differ". VALIDATION ONLY --
    ! calibrating to a point estimate the source reports as insignificant would
    ! be the same sin R1 attacked kappa_cons for.
    real(dp), parameter :: check_cond_ratio = milby_ach/milby_nach      ! 1.261

    real(dp), parameter :: target_price_elast = -0.63_dp
    real(dp), parameter :: target_vsl_musd    = 7.5_dp   ! Viscusi-Aldy, EPA

    ! benchmark state, saved so every arm starts from the same place
    real(dp), allocatable :: dist_bm(:,:,:,:,:,:,:)
    integer,  allocatable :: polh_bm(:,:,:,:,:,:,:)
    real(dp) :: pv_bm, taul_bm, beq_bm, H_bm, HD_bm
    integer  :: tf_bm
    logical  :: bm_saved = .false.

contains

subroutine save_benchmark()
    if (.not. allocated(dist_bm)) then
        allocate(dist_bm(NA,NY,NE,ND,NV,NM,n_age))
        allocate(polh_bm(NA,NY,NE,ND,NV,NM,n_age))
    end if
    dist_bm = dist
    polh_bm = pol_h
    pv_bm = p_v; taul_bm = tau_l; beq_bm = bequest
    H_bm = H_agg; HD_bm = HD_agg; tf_bm = policy_TF
    bm_saved = .true.
end subroutine save_benchmark


subroutine restore_benchmark()
    p_v = pv_bm; tau_l = taul_bm; bequest = beq_bm
    H_agg = H_bm; HD_agg = HD_bm; policy_TF = tf_bm
end subroutine restore_benchmark


!===============================================================================
! One trial arm.
!
!   give_voucher = 1  the treated are handed a voucher at enrolment
!   tf           = 1  the voucher is conditional on abstinence
!
! Prices, taxes and bequests are held at the benchmark: a trial of 196 people
! does not move them. The household problem IS re-solved, because the arm
! changes the rules the treated face and a forward-looking household responds to
! the rules, not to the realisation.
!
! Returns the mass-weighted share of the treated who abstain, averaged over
! `horizon` periods from enrolment.
!===============================================================================
subroutine run_arm(give_voucher, tf, horizon, abstain, homeless_rate)
    integer,  intent(in)  :: give_voucher, tf, horizon
    real(dp), intent(out) :: abstain, homeless_rate
    real(dp), allocatable :: D(:,:,:,:,:,:,:), Dn(:,:,:,:,:,:,:)
    integer  :: j, ia, iy, ie, id, iv, im, ivt, t
    real(dp) :: m, mass, absm, hlm

    allocate(D (NA,NY,NE,ND,NV,NM,n_age))
    allocate(Dn(NA,NY,NE,ND,NV,NM,n_age))

    policy_TF = tf
    call solve_household()

    !-- enrolment: the trial population is the homeless with SUD of working age,
    !   selected on the BENCHMARK policy, which is who Milby recruited
    D = 0.0_dp
    do j = 1, j_ret-1
    do im = 1, NM
    do iv = 1, NV
    do id = 2, 2
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        if (polh_bm(ia,iy,ie,id,iv,im,j) /= 1) cycle
        m = dist_bm(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        if (give_voucher == 1) then
            ivt = 2
        else
            ivt = 1
        end if
        D(ia,iy,ie,id,ivt,im,j) = D(ia,iy,ie,id,ivt,im,j) + m
    end do
    end do
    end do
    end do
    end do
    end do
    end do

    absm = 0.0_dp; hlm = 0.0_dp; mass = 0.0_dp
    do t = 1, horizon
        do j = 1, n_age
        do im = 1, NM
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
        do iy = 1, NY
        do ia = 1, NA
            m = D(ia,iy,ie,id,iv,im,j)
            if (m <= 0.0_dp) cycle
            mass = mass + m
            if (pol_v(ia,iy,ie,id,iv,im,j) <= 0.0_dp) absm = absm + m
            if (pol_h(ia,iy,ie,id,iv,im,j) == 1)      hlm  = hlm  + m
        end do
        end do
        end do
        end do
        end do
        end do
        end do
        if (t < horizon) then
            call push_forward(D, Dn)
            D = Dn
        end if
    end do

    abstain       = absm/max(mass, 1.0e-12_dp)
    homeless_rate = hlm /max(mass, 1.0e-12_dp)

    deallocate(D, Dn)
    call restore_benchmark()
end subroutine run_arm


!-- push an arbitrary distribution forward one period under current policies --
! Same kernel as build_distribution_eq, but applied to a cohort rather than
! recursively to the stationary distribution, and with no newborns: a trial
! follows the people it enrolled.
subroutine push_forward(D, Dn)
    real(dp), intent(in)  :: D (NA,NY,NE,ND,NV,NM,n_age)
    real(dp), intent(out) :: Dn(NA,NY,NE,ND,NV,NM,n_age)
    integer  :: j, ia, iy, ie, id, iv, im, iap, ihp
    real(dp) :: m, phi, s_e(NE), s_d(ND), s_eta(NV)

    Dn = 0.0_dp
    do j = 1, n_age-1
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = D(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        call trans_kernel(ia,iy,ie,id,iv,im,j,.false.,0, iap,ihp,phi,s_e,s_d,s_eta)
        if (phi <= 0.0_dp) cycle
        call add_mass(Dn, iap, iy, id, im, j, m, phi, s_e, s_d, s_eta)
    end do
    end do
    end do
    end do
    end do
    end do
    end do
end subroutine push_forward


!===============================================================================
! The three arms of Milby et al. (2005).
!===============================================================================
subroutine milby_arms(a_nh, a_nach, a_ach, h_nh, h_nach, h_ach)
    real(dp), intent(out) :: a_nh, a_nach, a_ach, h_nh, h_nach, h_ach
    integer, parameter :: horizon = 1     ! the trial ran 24 weeks
    call run_arm(0, 0, horizon, a_nh,   h_nh)     ! no housing
    call run_arm(1, 0, horizon, a_nach, h_nach)   ! housing, unconditional  = HF
    call run_arm(1, 1, horizon, a_ach,  h_ach)    ! housing, conditional    = TF
end subroutine milby_arms


function housing_access_ratio() result(ratio)
    real(dp) :: ratio, a_nh, a_nach, a_ach, h1, h2, h3
    call milby_arms(a_nh, a_nach, a_ach, h1, h2, h3)
    ratio = a_nach/max(a_nh, 1.0e-8_dp)
end function housing_access_ratio


!===============================================================================
! Drug-price participation elasticity.
!
! R1 2(e) said this moment was not replicable. It now has an unambiguous model
! counterpart: perturb p_v, hold everything else at the benchmark, re-solve the
! household problem, and read the arc elasticity of the participation rate. It
! is a PARTIAL-equilibrium perturbation on purpose -- the empirical estimates
! come from price variation, not from a new steady state.
!===============================================================================
function price_elasticity() result(eps)
    real(dp) :: eps, dlp, p0, q0, q1
    type(agg_t) :: A
    dlp = 0.10_dp
    p0  = p_v

    call solve_household(); call build_distribution_eq(); call compute_aggregates(A)
    q0 = A%users/max(A%pop, 1.0e-12_dp)

    p_v = p0*(1.0_dp + dlp)
    call solve_household(); call build_distribution_eq(); call compute_aggregates(A)
    q1 = A%users/max(A%pop, 1.0e-12_dp)

    p_v = p0
    call solve_household(); call build_distribution_eq()

    if (q0 <= 0.0_dp .or. q1 <= 0.0_dp) then
        eps = 0.0_dp
    else
        eps = log(q1/q0)/log(1.0_dp + dlp)
    end if
end function price_elasticity




!===============================================================================
! Second-stage calibration.
!
! Each parameter is bisected in logs against its own moment, and the ORIENTATION
! is discovered from the bracket ends rather than asserted: the sign of
! d(moment)/d(parameter) is not obvious for either of these, and a wrong
! declared sign would silently drive the parameter to a bound.
!===============================================================================
subroutine calibrate_b_hl(iters, verbose)
    integer, intent(in) :: iters
    logical, intent(in) :: verbose
    real(dp) :: lo, hi, mid, f_lo, f_hi, f_mid, keep
    integer  :: k
    logical  :: rising

    keep = b_hl_ratio
    lo = log(0.02_dp); hi = log(1.0_dp)

    b_hl_ratio = exp(lo); f_lo = housing_access_ratio()
    b_hl_ratio = exp(hi); f_hi = housing_access_ratio()
    rising = (f_hi > f_lo)

    if (verbose) write(*,'(A,2F9.4,A,L2)') '   b_hl bracket ratios: ', f_lo, f_hi, &
        '   rising:', rising

    if (f_lo <= 0.0_dp .or. f_hi <= 0.0_dp) then
        if (verbose) write(*,'(A)') &
            '   WARNING: the Milby ratio is undefined (no abstention in the NH arm);'
        if (verbose) write(*,'(A)') &
            '   b_hl_ratio left unchanged. Calibrate b_1 first.'
        b_hl_ratio = keep
        return
    end if
    if ((f_lo - target_housing_ratio)*(f_hi - target_housing_ratio) > 0.0_dp) then
        ! target outside the bracket -- take the closer end and say so
        if (abs(f_lo - target_housing_ratio) < abs(f_hi - target_housing_ratio)) then
            b_hl_ratio = exp(lo)
        else
            b_hl_ratio = exp(hi)
        end if
        if (verbose) write(*,'(A)') &
            '   WARNING: Milby ratio not attainable in [0.02, 1.0]; clamped'
        return
    end if

    do k = 1, iters
        mid = 0.5_dp*(lo+hi)
        b_hl_ratio = exp(mid)
        f_mid = housing_access_ratio()
        if ((f_mid > target_housing_ratio) .eqv. rising) then
            hi = mid
        else
            lo = mid
        end if
    end do
    b_hl_ratio = exp(0.5_dp*(lo+hi))
    if (keep < 0.0_dp) b_hl_ratio = keep
end subroutine calibrate_b_hl


subroutine calibrate_kappa_phi_d(iters, verbose)
    integer, intent(in) :: iters
    logical, intent(in) :: verbose
    real(dp) :: lo, hi, mid, f_lo, f_hi, f_mid
    integer  :: k
    logical  :: rising

    ! Degenhardt et al. (2011) put the standardised mortality ratio for drug
    ! dependence between about 2.5 and 9.8; the bracket is that range.
    lo = log(2.5_dp); hi = log(9.8_dp)

    kappa_phi_d = exp(lo); call refresh_mortality_multipliers(); f_lo = price_elasticity()
    kappa_phi_d = exp(hi); call refresh_mortality_multipliers(); f_hi = price_elasticity()
    rising = (f_hi > f_lo)

    if (verbose) write(*,'(A,2F9.4,A,L2)') '   kappa_phi_d bracket elasticities: ', &
        f_lo, f_hi, '   rising:', rising

    if ((f_lo - target_price_elast)*(f_hi - target_price_elast) > 0.0_dp) then
        if (abs(f_lo - target_price_elast) < abs(f_hi - target_price_elast)) then
            kappa_phi_d = exp(lo)
        else
            kappa_phi_d = exp(hi)
        end if
        call refresh_mortality_multipliers()
        if (verbose) write(*,'(A)') &
            '   WARNING: -0.63 not attainable inside the Degenhardt SMR range; clamped'
        return
    end if

    do k = 1, iters
        mid = 0.5_dp*(lo+hi)
        kappa_phi_d = exp(mid); call refresh_mortality_multipliers()
        f_mid = price_elasticity()
        if ((f_mid > target_price_elast) .eqv. rising) then
            hi = mid
        else
            lo = mid
        end if
    end do
    kappa_phi_d = exp(0.5_dp*(lo+hi)); call refresh_mortality_multipliers()
end subroutine calibrate_kappa_phi_d


!===============================================================================
! The homelessness disamenity, calibrated rather than assumed.
!
! R2's C2 asked for the externality and noted it "would require a new
! calibration moment". Here is one. Loubiere et al.'s eight-country contingent
! valuation study asked people what they would pay in annual taxes to END
! homelessness through Housing First and got roughly EUR 57 per respondent per
! year, about 0.2% of average annual earnings. That is a stated preference over
! the AGGREGATE homelessness rate -- exactly the object kappa_ext multiplies.
!
! It is a much better fit to this model than the hedonic shelter-siting
! literature, which measures a LOCAL, AVOIDABLE disamenity: what people pay to
! live further from a facility. This model has no geography, so nobody can move
! away, and a capitalisation coefficient cannot be ported into it. The
! contingent-valuation number is non-spatial and is about the aggregate, which
! is what the model has.
!
! The mapping, and the correction that matters. Removing the disamenity is worth
! kappa_ext*(H + omega_ext*HD) utils and the household would pay wtp*c of
! consumption for it, so
!
!     kappa_ext = wtp * E[c*u_c] / (H_ref + omega_ext*HD_ref).
!
! The denominator is the EUROPEAN homelessness rate the survey respondents were
! valuing, NOT the model's own. Using the model's rate would be wrong: the same
! EUR 57 would then imply a different disamenity in every economy it was
! transplanted into, mechanically making the externality small wherever
! homelessness is rare and large wherever it is common, which is the opposite of
! what a per-unit valuation means. Normalising by the reference rate gives a
! price per unit of homelessness, which is transferable.
!
! Since kappa_ext enters period utility additively and is zero at the benchmark,
! E[c*u_c] does not depend on it, so this is one calculation rather than a fixed
! point.
!===============================================================================
function kappa_ext_from_wtp() result(kx)
    real(dp) :: kx
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: m, mass, acc, cc, vv, comp, bb, H, HD

    mass = 0.0_dp; acc = 0.0_dp; H = 0.0_dp; HD = 0.0_dp

    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        mass = mass + m
        ihp  = pol_h(ia,iy,ie,id,iv,im,j)
        if (ihp == 1) then
            H = H + m
            if (id == 2) HD = HD + m
        end if
        cc = pol_c(ia,iy,ie,id,iv,im,j)
        vv = pol_v(ia,iy,ie,id,iv,im,j)
        if (cc <= 0.0_dp) cycle
        bb   = b_of(id, im, ihp)
        comp = cc**alpha_u * h_pow(ihp) * (vv + bb)**gamma_u
        if (comp <= 0.0_dp) cycle
        ! c*u_c = alpha*comp**(1-sigma); for sigma = 2 that is alpha/comp
        acc = acc + m*alpha_u*comp**(1.0_dp - sigma)
    end do; end do; end do
    end do; end do; end do
    end do

    ! the model's own rates, kept for the report
    H  = H /max(mass,1.0e-12_dp)
    HD = HD/max(mass,1.0e-12_dp)

    ! ...but the price per unit of homelessness is set by the rate the
    ! respondents were actually valuing
    kx = wtp_end_homelessness * (acc/max(mass,1.0e-12_dp)) &
       / max(wtp_ref_homeless_rate*(1.0_dp + omega_ext*wtp_ref_sud_share), 1.0e-12_dp)
end function kappa_ext_from_wtp


subroutine report_second_stage()
    real(dp) :: a_nh, a_nach, a_ach, h_nh, h_nach, h_ach
    real(dp) :: eps, vsl, kx

    call milby_arms(a_nh, a_nach, a_ach, h_nh, h_nach, h_ach)
    eps = price_elasticity()
    vsl = model_vsl()

    write(*,'(A)') ''
    write(*,'(A)') '  ============ second stage: short-run experiments ============'
    write(*,'(A)') '  Milby et al. (2005), homeless adults with SUD, one period'
    write(*,'(A)') '  ------------------------------------------------------------'
    write(*,'(A)') '   arm                       abstaining   homeless   (model, %)'
    write(*,'(A,F12.2,F11.2)') '   NH   no housing         ', 100*a_nh,   100*h_nh
    write(*,'(A,F12.2,F11.2)') '   NACH housing, uncond.   ', 100*a_nach, 100*h_nach
    write(*,'(A,F12.2,F11.2)') '   ACH  housing, cond.     ', 100*a_ach,  100*h_ach
    write(*,'(A)') '  ------------------------------------------------------------'
    ! Guard the ratios. If nobody abstains in an arm the ratio is 0/0, not zero,
    ! and printing 0.000 or a field of asterisks would look like a result. It
    ! happens whenever b_1 is small enough that a household with SUD never
    ! abstains, which is exactly the uncalibrated corner.
    if (a_nh > 1.0e-6_dp) then
        write(*,'(A,F8.3,A,F8.3,A)') '   housing access  NACH/NH : ', &
            a_nach/a_nh, '   target ', target_housing_ratio, '  (TARGETED)'
    else
        write(*,'(A,F8.3,A)') '   housing access  NACH/NH : UNDEFINED   target ', &
            target_housing_ratio, '  (nobody abstains in the NH arm)'
    end if
    if (a_nach > 1.0e-6_dp) then
        write(*,'(A,F8.3,A,F8.3,A)') '   conditionality  ACH/NACH: ', &
            a_ach/a_nach, '   data   ', check_cond_ratio, '  (P=.091, sign only)'
    else
        write(*,'(A,F8.3,A)') '   conditionality  ACH/NACH: UNDEFINED   data   ', &
            check_cond_ratio, '  (nobody abstains in the NACH arm)'
    end if
    write(*,'(A,F8.3,A,F8.3,A)') '   drug-price participation elasticity: ', eps, &
        '   target ', target_price_elast, '  (TARGETED)'
    write(*,'(A,F8.2,A,F8.2,A)') '   model-implied VSL ($m)            : ', vsl, &
        '   ref    ', target_vsl_musd, '  (reported)'
    write(*,'(A)') '  ------------------------------------------------------------'
    write(*,'(A,ES12.4)') '   b_hl_ratio  : ', b_hl_ratio
    write(*,'(A,ES12.4)') '   kappa_phi_d : ', kappa_phi_d
    kx = kappa_ext_from_wtp()
    write(*,'(A)') '  ------------------------------------------------------------'
    write(*,'(A,ES12.4)') '   kappa_ext implied by WTP to end homelessness: ', kx
    write(*,'(A,F8.3,A)') '     from ', 100.0_dp*wtp_end_homelessness, &
        '% of annual income (Loubiere et al. contingent valuation),'
    write(*,'(A,F8.3,A)') '     normalised by a European reference rate of ', &
        100.0_dp*wtp_ref_homeless_rate, '% homeless'
    write(*,'(A,ES12.4)') '   kappa_ext currently in force                : ', kappa_ext
    write(*,'(A)') '  ============================================================'
end subroutine report_second_stage

end module experiment
