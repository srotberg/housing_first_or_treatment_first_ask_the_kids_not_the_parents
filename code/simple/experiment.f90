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
    integer  :: keep_pin
    type(agg_t) :: A
    dlp = 0.10_dp
    p0  = p_v
    ! the whole point here is to MOVE p_v, so the first-stage pin has to come
    ! off; solve_household is called directly rather than through the
    ! equilibrium loop, but unpinning keeps the intent explicit and protects
    ! against anyone routing this through solve_equilibrium later
    keep_pin = pin_pv; pin_pv = 0

    call solve_household(); call build_distribution_eq(); call compute_aggregates(A)
    q0 = A%users/max(A%pop, 1.0e-12_dp)

    p_v = p0*(1.0_dp + dlp)
    call solve_household(); call build_distribution_eq(); call compute_aggregates(A)
    q1 = A%users/max(A%pop, 1.0e-12_dp)

    p_v = p0
    pin_pv = keep_pin
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


!===============================================================================
! Validity check on the mortality profiles.
!
! kappa_phi_d and kappa_phi_h vary by age, but the literature reports a SINGLE
! standardised mortality ratio. The comparable object is therefore the model's
! own age-weighted SMR: total deaths in the group divided by the deaths that
! same group would suffer at baseline hazards. Weighting by the MODEL's age
! distribution of SUD and of homelessness is the point -- an unweighted average
! over ages would compare a profile against a statistic computed on a
! population that is heavily concentrated in its young end.
!
! Reported against the two sources the profiles were built from, so a reader can
! see whether the level the price elasticity chose is consistent with the
! mortality evidence. These are NOT targets; disagreement is the finding.
!===============================================================================
!===============================================================================
! Does the model deliver Costantini's short-run health effect?
!
! Costantini (2025) finds Housing First cuts 3-year mortality by 4.6pp
! (s.e. 1.7) in roughly 300,000 VA veterans, by IV. That is the single most
! directly comparable estimate to this model's central mechanism, and it is
! UNTARGETED: nothing in the calibration is fitted to it.
!
! MATCHING HIS EXPERIMENT MATTERS, and the obvious analogue is the wrong one.
! Costantini does not compare Housing First against Treatment First, and he does
! not ask what would happen if a given homeless household were housed. He
! instruments RECEIPT of a voucher, so his estimate is a local average treatment
! effect over households the instrument moves into housing, with every
! behavioural response left free.
!
! So the model analogue is a WALD RATIO, not a hazard calculation. Expand
! voucher access, re-solve the equilibrium, and divide the change in aggregate
! 3-year mortality by the change in the housed share:
!
!     LATE = d(3-year mortality) / d(share housed)
!
! That is the effect per household actually moved into housing, which is what
! his IV estimates. Behaviour responds throughout: households that gain housing
! may use more or less, work more or less, and the drug price moves. A pure
! hazard difference would hold all of that fixed and would therefore overstate
! the mortality gain if housing raises use, or understate it if housing lowers
! use.
!
! The hazard version is still reported alongside, because the gap between the
! two IS the behavioural response, and that gap is informative in its own right.
!
! Weighting by the model's own distribution rather than by HUD's age profile is
! the point: if the model puts its homeless at the wrong ages, this diagnostic
! is supposed to reveal that, and a hand calculation on external weights would
! hide it.
!===============================================================================
subroutine report_health_effect()
    integer  :: j, ia, iy, ie, id, iv, im, k, ihp
    real(dp) :: m, mass, s_hl, s_ho, cum_hl, cum_ho, acc_hl, acc_ho
    real(dp) :: age_acc, sud_acc, smi_acc

    mass = 0.0_dp; acc_hl = 0.0_dp; acc_ho = 0.0_dp
    age_acc = 0.0_dp; sud_acc = 0.0_dp; smi_acc = 0.0_dp

    do j = 1, n_age-3
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        if (pol_h(ia,iy,ie,id,iv,im,j) /= 1) cycle      ! the homeless only

        ! three years at the homeless hazard, versus three years housed in the
        ! smallest unit, ageing properly in both
        cum_hl = 1.0_dp; cum_ho = 1.0_dp
        do k = 0, 2
            s_hl = survival(j+k, 1, id, im)
            s_ho = survival(j+k, 2, id, im)
            cum_hl = cum_hl*s_hl
            cum_ho = cum_ho*s_ho
        end do

        acc_hl = acc_hl + m*(1.0_dp - cum_hl)
        acc_ho = acc_ho + m*(1.0_dp - cum_ho)
        mass   = mass + m
        age_acc = age_acc + m*real(j+25,dp)
        if (id == 2) sud_acc = sud_acc + m
        if (im == 2) smi_acc = smi_acc + m
    end do; end do; end do
    end do; end do; end do
    end do

    write(*,'(A)') ''
    write(*,'(A)') '  ========= short-run health: the model vs Costantini (2025) ========='
    if (mass <= 0.0_dp) then
        write(*,'(A)') '   UNDEFINED: no homeless mass in the benchmark'
        write(*,'(A)') '  ==================================================================='
        return
    end if
    write(*,'(A,F7.2)') '   mean age of the model''s homeless        : ', age_acc/mass
    write(*,'(A,F7.2,A)') '   share with SUD                          : ', &
        100.0_dp*sud_acc/mass, ' %'
    write(*,'(A,F7.2,A)') '   share with poor mental health           : ', &
        100.0_dp*smi_acc/mass, ' %'
    write(*,'(A)') '  -------------------------------------------------------------------'
    write(*,'(A,F7.2,A)') '   3-year mortality, staying homeless      : ', &
        100.0_dp*acc_hl/mass, ' %'
    write(*,'(A,F7.2,A)') '   3-year mortality, if housed             : ', &
        100.0_dp*acc_ho/mass, ' %'
    write(*,'(A,F7.2,A)') '   MODEL effect of housing                 : ', &
        100.0_dp*(acc_ho-acc_hl)/mass, ' pp'
    write(*,'(A)')        '   Costantini (2025), HF, IV               :   -4.60 pp (s.e. 1.7)'
    write(*,'(A)')        '   95% interval                            :   -7.93 to -1.27 pp'
    write(*,'(A)') '  -------------------------------------------------------------------'
    write(*,'(A)') '   The above is the HAZARD difference: behaviour held fixed.'
    call report_health_late(acc_ho-acc_hl, mass)
end subroutine report_health_effect


!===============================================================================
! The two-armed Costantini validation, and why it is two-armed.
!
! The AE writes that Costantini finds Housing First cuts three-year mortality by
! 4.6pp while Treatment First has no effect, "in contrast with the model
! simulations of this paper". Two things in that sentence do not survive
! contact with his design.
!
! FIRST, NEITHER OF HIS NUMBERS IS THIS PAPER'S EXPERIMENT 1. Both of his
! estimates are local average treatment effects against NO HOUSING
! INTERVENTION. He instruments entry into HUD-VASH and entry into Grant and Per
! Diem separately, with two instruments, against a control arm that receives
! nothing. So his estimates live on the GENEROSITY margin -- assistance versus
! none -- while Experiment 1 holds the number of assisted households fixed and
! varies only CONDITIONALITY. His pair of coefficients does not identify the
! difference between two rationed regimes; he says so himself, and reports a
! separate F test to compare them.
!
! SECOND, HIS TREATMENT FIRST IS NOT THIS PAPER'S TREATMENT FIRST. Grant and
! Per Diem is TIME LIMITED transitional housing: a stay of six months to two
! years, after which the veteran must find their own housing. That expiry is
! what his own mechanism section identifies as the cause of the null. His
! Figure 4 has transitional housing recipients MORE likely to be housed than
! voucher recipients in quarter 1, because a bed is available at once while a
! voucher has to find a landlord, and then decaying to 9pp by quarter 12 while
! the voucher arm peaks at 34pp. The programme does not fail to house people.
! It stops housing them. This paper's Treatment First is a permanent voucher
! whose RETENTION is conditional on sobriety, which is a different object.
!
! So the honest test is to ask the model both of his questions, in his units,
! at his margin, and see whether it produces both of his answers.
!
!   arm HF   expand access to an unconditional permanent voucher
!   arm TF   expand access to a sobriety-conditioned voucher that EXPIRES at
!            the Grant and Per Diem rate
!
! Each arm is its own baseline and its own expansion, so each Wald ratio is the
! marginal effect of adding a household to THAT programme's rolls, which is what
! an instrument that pushes compliers into one programme estimates. Neither is
! contaminated by the other. The expiry hazard is 0.8 a year, the reciprocal of
! the 1.25 year mean stay implied by his six month to two year window.
!
! If the model reproduces a large negative LATE for the first and a small one
! for the second, the AE's contradiction is not a contradiction: the same
! mechanism that makes universal Treatment First attractive in the long run --
! conditionality raising the private cost of use while housing is still
! guaranteed to the sober -- also predicts that a programme which withdraws the
! housing after a year buys no three-year mortality gain.
!===============================================================================
subroutine report_health_late(hazard_gap, hl_mass)
    real(dp), intent(in) :: hazard_gap, hl_mass
    real(dp) :: pv_keep, late_hf, late_tf, dh_hf, dh_tf, dm_hf, dm_tf
    integer  :: tf_keep
    real(dp) :: ve_keep

    pv_keep = prob_V; tf_keep = policy_TF; ve_keep = v_expire

    ! arm HF: unconditional, permanent -- HUD-VASH
    policy_TF = 0; v_expire = 0.0_dp
    call late_arm(pv_keep, dh_hf, dm_hf, late_hf)

    ! arm TF: sobriety conditioned, expiring -- Grant and Per Diem
    policy_TF = 1; v_expire = gpd_expire
    call late_arm(pv_keep, dh_tf, dm_tf, late_tf)

    ! restore and re-solve, so whatever runs next sees the benchmark
    prob_V = pv_keep; policy_TF = tf_keep; v_expire = ve_keep
    call solve_equilibrium(40, 1.0e-4_dp, .false.)

    write(*,'(A)') '  -------------------------------------------------------------------'
    write(*,'(A)') '   WALD RATIOS, which is what Costantini''s two IVs actually estimate.'
    write(*,'(A)') '   Both are marginal expansions of ACCESS against that programme''s own'
    write(*,'(A)') '   baseline, because his control arm is no housing intervention.'
    write(*,'(A)') ''
    write(*,'(A)') '   arm                          d(housed) d(mort3)     LATE      data'
    write(*,'(A,F9.4,F9.4,F9.3,A)') &
        '   HF  permanent, unconditional', 100.0_dp*dh_hf, 100.0_dp*dm_hf, &
        100.0_dp*late_hf, '    -4.60'
    write(*,'(A,F9.4,F9.4,F9.3,A)') &
        '   TF  expiring, sobriety-cond.', 100.0_dp*dh_tf, 100.0_dp*dm_tf, &
        100.0_dp*late_tf, '     ~0  '
    write(*,'(A)') '   all figures in percentage points'
    write(*,'(A)') '  -------------------------------------------------------------------'
    write(*,'(A,F9.3,A)') '   hazard-only version of the HF arm, no behaviour : ', &
        100.0_dp*hazard_gap/max(hl_mass,1.0e-12_dp), ' pp'
    write(*,'(A)') '   the gap between that and the HF LATE IS the behavioural response'
    write(*,'(A)') ''
    write(*,'(A)') '   Costantini (2025): HF -4.60 pp (s.e. 1.7), 95% [-7.93, -1.27];'
    write(*,'(A)') '   TF point estimate near zero, and he rejects equality at F = 4.06.'
    write(*,'(A)') '   The model passes if the HF arm lands inside his interval AND the'
    write(*,'(A)') '   TF arm is much smaller. It is NOT fitted to either number.'
    write(*,'(A)') '  ==================================================================='
end subroutine report_health_late


!-- one arm of the validation: baseline, expand access, Wald ratio ------------
! Called with the policy design already set. Leaves prob_V restored.
subroutine late_arm(pv_base, dhoused, dmort, late)
    real(dp), intent(in)  :: pv_base
    real(dp), intent(out) :: dhoused, dmort, late
    type(agg_t) :: A0, A1
    real(dp) :: mort0, mort1, hs0, hs1

    prob_V = pv_base
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    call compute_aggregates(A0)
    mort0 = mortality_3yr(); hs0 = 1.0_dp - A0%homeless/max(A0%pop,1.0e-12_dp)

    ! expand access by a tenth: small enough to stay local, large enough to
    ! move a measurable mass
    prob_V = min(1.0_dp, pv_base*1.10_dp)
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    call compute_aggregates(A1)
    mort1 = mortality_3yr(); hs1 = 1.0_dp - A1%homeless/max(A1%pop,1.0e-12_dp)

    prob_V  = pv_base
    dhoused = hs1 - hs0
    dmort   = mort1 - mort0
    if (abs(dhoused) > 1.0e-10_dp) then
        late = dmort/dhoused
    else
        late = 0.0_dp           ! expansion moved nobody; reported as a zero row
    end if
end subroutine late_arm


!-- population 3-year cumulative mortality at current policies ----------------
function mortality_3yr() result(m3)
    real(dp) :: m3
    integer  :: j, ia, iy, ie, id, iv, im, k, ih
    real(dp) :: m, mass, cum
    mass = 0.0_dp; m3 = 0.0_dp
    do j = 1, n_age-3
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        ih = pol_h(ia,iy,ie,id,iv,im,j)
        cum = 1.0_dp
        do k = 0, 2
            cum = cum*survival(j+k, ih, id, im)
        end do
        m3 = m3 + m*(1.0_dp - cum); mass = mass + m
    end do; end do; end do
    end do; end do; end do
    end do
    m3 = m3/max(mass,1.0e-12_dp)
end function mortality_3yr


subroutine report_mortality_validation()
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: m, q0, q1
    real(dp) :: d_num, d_den, h_num, h_den, m_num, m_den, mass_d, mass_h

    d_num = 0.0_dp; d_den = 0.0_dp; mass_d = 0.0_dp
    h_num = 0.0_dp; h_den = 0.0_dp; mass_h = 0.0_dp
    m_num = 0.0_dp; m_den = 0.0_dp

    do j = 1, n_age-1
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        ihp = pol_h(ia,iy,ie,id,iv,im,j)
        q0  = 1.0_dp - surv_base(j)                      ! baseline hazard
        q1  = 1.0_dp - survival(j, ihp, id, im)          ! actual hazard
        if (id == 2) then
            d_num = d_num + m*q1; d_den = d_den + m*q0; mass_d = mass_d + m
        end if
        if (ihp == 1) then
            h_num = h_num + m*q1; h_den = h_den + m*q0; mass_h = mass_h + m
        end if
        if (im == 2) then
            m_num = m_num + m*q1; m_den = m_den + m*q0
        end if
    end do; end do; end do
    end do; end do; end do
    end do

    write(*,'(A)') ''
    write(*,'(A)') '  ============ mortality profiles: model vs data ============'
    write(*,'(A)') '   Age-weighted SMR, using the model''s own age distribution.'
    write(*,'(A)') '   UNTARGETED -- the profiles are data, the SUD level is set by'
    write(*,'(A)') '   the price elasticity, so agreement here is a real check.'
    write(*,'(A)') '  -----------------------------------------------------------'
    if (d_den > 0.0_dp) then
        write(*,'(A,F7.2,A)') '   SUD, model SMR          : ', d_num/d_den, &
            '   data 2.5-9.8 (Degenhardt et al. 2011)'
    else
        write(*,'(A)') '   SUD, model SMR          : UNDEFINED (no SUD mass)'
    end if
    if (h_den > 0.0_dp) then
        write(*,'(A,F7.2,A)') '   homeless, model SMR     : ', h_num/h_den, &
            '   data ~9.1 at 25-44, 4.5 at 45-64, 1.1 at 65+ (Baggett 2013)'
    else
        write(*,'(A)') '   homeless, model SMR     : UNDEFINED (nobody homeless)'
    end if
    if (m_den > 0.0_dp) &
        write(*,'(A,F7.2,A)') '   poor mental health SMR  : ', m_num/m_den, &
            '   flat kappa_phi_m, not yet age-varying'
    write(*,'(A,F7.3,A,F7.3,A)') '   mass: SUD ', 100.0_dp*mass_d, &
        ' %,  homeless ', 100.0_dp*mass_h, ' %'
    write(*,'(A,F7.2)') '   peak-age SUD multiplier (the calibrated level) : ', kappa_phi_d
    write(*,'(A)') '  ==========================================================='
end subroutine report_mortality_validation


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
    call report_mortality_validation()
    call report_health_effect()
end subroutine report_second_stage

end module experiment
