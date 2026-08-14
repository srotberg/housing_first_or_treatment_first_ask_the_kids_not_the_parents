!===============================================================================
! equilibrium.f90 -- stationary equilibrium for the simplified model
!
! Objects that clear:
!   tau_l    government budget balance (closed form given the distribution)
!   p_v      drug market, p_v = psi1 * V**(psi2-1)
!   bequest  assets of the deceased -- to the government by default,
!            redistributed to survivors only if bequest_to_govt = 0
!   H_agg    aggregate homelessness, which enters period utility as an
!            externality and so must be a fixed point
!   avg/median income, which enter voucher eligibility and the food-stamp floor
!
! There is deliberately NO housing market here: rent is a fixed price. That is
! what the AE asked for -- keep the government, add the drug price, drop house
! prices and rents.
!===============================================================================
module equilibrium
    use params
    use solve
    implicit none

    ! default initialisers so an intent(out) dummy is zeroed on entry --
    ! avoids a hand-maintained structure constructor
    type :: agg_t
        real(dp) :: pop=0, mass_dead=0
        real(dp) :: labinc=0, labinc_pow=0, capinc=0, captax=0
        real(dp) :: ss=0, ui=0, food=0, vouchers=0
        real(dp) :: homeless=0, sud=0, users=0, unemp=0, drugq=0, poormh=0, hl_sud=0
        real(dp) :: assets_dead=0, consumption=0, treated=0
        real(dp) :: wealth=0, gdp=0, med=0, testing=0
        real(dp) :: govt_outlay=0, tax_rev=0
    end type agg_t

    real(dp) :: G_public = 0.0_dp        ! public goods, calibrated then held fixed
    real(dp), parameter :: us_avg_income_usd = 70000.0_dp
    logical  :: G_is_set = .false.

contains

!-- everything the equilibrium conditions need, in one pass ------------------
subroutine compute_aggregates(A)
    type(agg_t), intent(out) :: A
    integer  :: j, ia, iy, ie, id, iv, im, ihp, ireg, itr, iap
    real(dp) :: m, ygross, ynet, vouch, res, phi, food_j, cc, vv, capinc_j
    ! income histogram, for the MEDIAN. Voucher eligibility is 50% of median
    ! income and the median was standing in as the mean, which in a skewed
    ! income distribution overstates the eligible population substantially.
    integer,  parameter :: NBIN = 4000
    real(dp) :: hist(NBIN), top, inc_j, cum
    integer  :: ib


    hist = 0.0_dp
    top  = 8.0_dp*max(avg_income, 1.0e-6_dp)

    do j = 1, n_age
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle

        ihp  = pol_h(ia,iy,ie,id,iv,im,j)
        iap  = pol_a(ia,iy,ie,id,iv,im,j)
        ireg = pol_reg(ia,iy,ie,id,iv,im,j)
        itr  = pol_tr(ia,iy,ie,id,iv,im,j)
        cc   = pol_c(ia,iy,ie,id,iv,im,j)
        vv   = pol_v(ia,iy,ie,id,iv,im,j)

        ygross   = income_gross(j, iy, ie, id, im, hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j)))
        capinc_j = r_free*a_grid(ia)
        phi      = survival(j, ihp, id, im)

        A%pop = A%pop + m
        if (im == 2) A%poormh = A%poormh + m

        ! income and the tax base
        if (j < j_ret) then
            A%labinc     = A%labinc     + m*ygross
            A%labinc_pow = A%labinc_pow + m*max(ygross,1.0e-10_dp)**xi_tax
            if (ie == 2) A%ui = A%ui + m*ygross     ! only year-1 UI recipients
            if (ie >= 2) A%unemp = A%unemp + m
        else
            A%ss = A%ss + m*ygross
        end if

        A%wealth = A%wealth + m*a_grid(ia)
        A%capinc = A%capinc + m*capinc_j

        ! the means-tested income concept: gross earnings plus gross capital income
        inc_j = ygross + max(0.0_dp, capinc_j)
        ib    = min(NBIN, 1 + int(inc_j/top*real(NBIN,dp)))
        hist(ib) = hist(ib) + m
        A%captax = A%captax + m*0.15_dp*max(0.0_dp, capinc_j)

        ! food stamps: fills the gap up to the consumption floor
        food_j = max(0.0_dp, cfloor_share*avg_income - (ygross + max(0.0_dp,capinc_j)))
        A%food = A%food + m*food_j

        ! vouchers pay only while renting
        vouch = 0.0_dp
        if (ihp > 1 .and. iv == 2) then
            vouch = max(0.0_dp, p_rent*h_grid(ihp) - kappa_r*ygross)
        end if
        A%vouchers = A%vouchers + m*vouch
        ! testing is paid on every voucher HOLDER under TF, whether or not the
        ! voucher pays out this period -- that is what makes it a real cost
        if (policy_TF == 1 .and. iv == 2) &
            A%testing = A%testing + m*test_prob*test_cost*avg_income

        ! outcomes
        if (ihp == 1) A%homeless = A%homeless + m
        if (ihp == 1 .and. id == 2) A%hl_sud = A%hl_sud + m
        if (id == 2)  A%sud      = A%sud + m
        if (itr == 1) A%treated  = A%treated + m
        if (vv > 0.0_dp) then
            A%users = A%users + m
            A%drugq = A%drugq + m*vv
        end if
        A%consumption = A%consumption + m*cc

        ! bequests: assets carried by those who do not survive
        A%mass_dead   = A%mass_dead   + m*(1.0_dp - phi)
        A%assets_dead = A%assets_dead + m*(1.0_dp - phi)*a_grid(iap)
    end do
    end do
    end do
    end do
    end do
    end do
    end do

    ! GDP = all factor income: labour earnings of the employed plus the return
    ! on the capital stock. Transfers (SS, UI, DI, food stamps, vouchers) are
    ! redistribution, not output, and are excluded. Wealth/GDP is the beta
    ! target -- see CALIBRATION.md.
    A%gdp = A%labinc + A%capinc

    ! median of the means-tested income distribution
    cum = 0.0_dp; A%med = 0.0_dp
    do ib = 1, NBIN
        cum = cum + hist(ib)
        if (cum >= 0.5_dp*A%pop) then
            A%med = (real(ib,dp) - 0.5_dp)/real(NBIN,dp)*top
            exit
        end if
    end do

    A%govt_outlay = A%ss + A%food + A%vouchers + A%testing &
                  + chi_H*A%homeless + chi_D*A%sud + G_public
    ! accidental bequests accrue to the government rather than to households
    if (bequest_to_govt == 1) A%govt_outlay = A%govt_outlay - A%assets_dead
    A%tax_rev     = A%labinc - tau_l*A%labinc_pow + A%captax
end subroutine compute_aggregates


!-- one full solve at the current prices -------------------------------------
subroutine solve_once(A)
    type(agg_t), intent(out) :: A
    call solve_household()
    call build_distribution_eq()
    call compute_aggregates(A)
end subroutine solve_once


!===============================================================================
! Stationary equilibrium by damped fixed point.
!===============================================================================
subroutine solve_equilibrium(maxit, tol, verbose)
    integer,  intent(in) :: maxit
    real(dp), intent(in) :: tol
    logical,  intent(in) :: verbose
    type(agg_t) :: A
    integer  :: it
    real(dp) :: tau_new, pv_new, beq_new, H_new, HD_new, avg_new, med_new
    real(dp) :: err, damp

    damp = 0.25_dp

    do it = 1, maxit
        call solve_once(A)

        ! ---- government budget: closed form for tau_l -----------------------
        ! revenue = labinc - tau_l*labinc_pow + captax  must equal outlay
        if (.not. G_is_set) then
            ! benchmark: back G out as the residual so the budget balances at
            ! the calibrated tau_l, then hold G fixed in counterfactuals
            G_public = A%labinc - tau_l*A%labinc_pow + A%captax &
                     - (A%ss + A%food + A%vouchers + chi_H*A%homeless + chi_D*A%sud)
            G_is_set = .true.
            tau_new  = tau_l
        else
            if (A%labinc_pow > 0.0_dp) then
                tau_new = (A%labinc + A%captax - A%govt_outlay)/A%labinc_pow
            else
                tau_new = tau_l
            end if
            tau_new = min(max(tau_new, 0.05_dp), 1.5_dp)
        end if

        ! ---- drug market ----------------------------------------------------
        ! psi1 is normalised at the benchmark so that p_v = 1 there; thereafter
        ! p_v moves with demand at the calibrated supply elasticity.
        if (A%drugq > 0.0_dp) then
            pv_new = psi1 * A%drugq**(psi2 - 1.0_dp)
        else
            pv_new = p_v
        end if
        pv_new = min(max(pv_new, 0.05_dp), 20.0_dp)

        ! ---- bequests -------------------------------------------------------
        ! When accidental bequests go to the government there is no fixed point
        ! left to solve here: households receive nothing and the estate simply
        ! relaxes the tax constraint. Keeping the lump-sum version behind a
        ! switch preserves the old behaviour for a robustness run.
        if (bequest_to_govt == 1) then
            beq_new = 0.0_dp
        else if (A%pop > 0.0_dp) then
            beq_new = A%assets_dead / A%pop
        else
            beq_new = bequest
        end if

        ! ---- externality and income aggregates ------------------------------
        H_new   = A%homeless / max(A%pop, 1.0e-12_dp)
        HD_new  = A%hl_sud   / max(A%pop, 1.0e-12_dp)
        avg_new = (A%labinc + A%ss) / max(A%pop, 1.0e-12_dp)
        med_new = A%med

        ! relative residuals: the discrete choice set makes threshold rules
        ! (food-stamp floor, voucher eligibility) chatter, so an absolute
        ! criterion on income aggregates never settles
        err = reldiff(tau_new, tau_l)
        err = max( err, reldiff(pv_new,  p_v) )
        err = max( err, reldiff(beq_new, bequest) )
        err = max( err, reldiff(avg_new, avg_income) )
        ! H_agg only matters when the externality is switched on
        if (kappa_ext > 0.0_dp) then
            err = max( err, reldiff(H_new,  H_agg) )
            err = max( err, reldiff(HD_new, HD_agg) )
        end if

        if (verbose) then
            write(*,'(A,I3,A,F9.5,A,F8.4,A,F8.4,A,F8.5,A,F7.3,A)') &
                ' it ', it, '  err=', err, '  tau=', tau_new, '  p_v=', pv_new, &
                '  beq=', beq_new, '  homeless=', 100.0_dp*H_new, '%'
        end if

        tau_l      = tau_l      + damp*(tau_new - tau_l)
        ! p_v needs its own, heavier damping: with a small drug market the
        ! supply curve p_v = psi1*V^(psi2-1) is hypersensitive to V, and at the
        ! shared damping the price limit-cycles instead of settling
        p_v        = p_v        + 0.08_dp*(pv_new - p_v)
        bequest    = bequest    + damp*(beq_new - bequest)
        H_agg      = H_agg      + damp*(H_new   - H_agg)
        HD_agg     = HD_agg     + damp*(HD_new  - HD_agg)
        avg_income = avg_income + damp*(avg_new - avg_income)
        median_income = median_income + damp*(med_new - median_income)

        if (err < tol) then
            if (verbose) write(*,'(A,I0,A)') ' converged in ', it, ' iterations'
            call solve_once(A)
            return
        end if
    end do

    if (verbose) write(*,'(A)') ' WARNING: equilibrium did not converge'
end subroutine solve_equilibrium


pure function reldiff(x, y) result(d)
    real(dp), intent(in) :: x, y
    real(dp) :: d
    d = abs(x-y)/max(1.0_dp, abs(y))
end function reldiff


!===============================================================================
! Model-implied value of a statistical life.
!
! VSL is the marginal rate of substitution between consumption and the survival
! probability. Along the household's own optimum, dV/dphi = beta*EV and
! dV/dc = u_c, so VSL = beta*EV/u_c in model consumption units; converting at
! the model's own average income against US average labour income puts it in
! dollars. Mass-weighted over the working-age population.
!
! EV is a single table overwritten once per age, so it is rebuilt age by age
! here, working backwards exactly as the solve does.
!
! This lives here rather than in experiment.f90 because the CALIBRATION targets
! it. The smoke test found that at the previous parameters 64.6% of the
! population had V < 0 -- they would rather be dead -- which turns the mortality
! cost of drug use into a mortality BENEFIT for exactly the households the policy
! is aimed at, and silently inverts the paper's central mechanism. aleph cannot
! be left to a moment that does not discipline its level.
!===============================================================================
function model_vsl() result(vsl_musd)
    real(dp) :: vsl_musd
    integer  :: j, ia, iy, ie, id, iv, im, iap, ihp, ireg, itr, ielig
    real(dp) :: m, mass, acc, cc, vv, comp, uc, ygross, bb

    mass = 0.0_dp; acc = 0.0_dp

    do j = n_age-1, 1, -1
        call build_EV(j)
        do im = 1, NM
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
        do iy = 1, NY
        do ia = 1, NA
            if (j >= j_ret) cycle
            m = dist(ia,iy,ie,id,iv,im,j)
            if (m <= 0.0_dp) cycle
            iap  = pol_a(ia,iy,ie,id,iv,im,j)
            ihp  = pol_h(ia,iy,ie,id,iv,im,j)
            ireg = pol_reg(ia,iy,ie,id,iv,im,j)
            itr  = pol_tr(ia,iy,ie,id,iv,im,j)
            cc   = pol_c(ia,iy,ie,id,iv,im,j)
            vv   = pol_v(ia,iy,ie,id,iv,im,j)
            if (cc <= 0.0_dp) cycle
            bb   = b_of(id, im, ihp)

            ygross = income_gross(j, iy, ie, id, im, hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j)))
            if (ygross + max(0.0_dp, r_free*a_grid(ia)) < kappa_V*median_income) then
                ielig = 1
            else
                ielig = 0
            end if

            comp = cc**alpha_u * h_pow(ihp) * (vv + bb)**gamma_u
            if (comp <= 0.0_dp) cycle
            uc = alpha_u * comp**(1.0_dp - sigma) / cc

            acc  = acc + m*beta*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)/uc
            mass = mass + m
        end do
        end do
        end do
        end do
        end do
        end do
    end do

    ! model consumption units -> dollars, at the model's own average income
    vsl_musd = (acc/max(mass,1.0e-12_dp)) * us_avg_income_usd &
             / max(avg_income, 1.0e-12_dp) / 1.0e6_dp
end function model_vsl


!===============================================================================
! Stationary equilibrium with named objects HELD at supplied values.
!
! Used by the externality decomposition: freezing one equilibrium object and
! re-solving isolates the channel that works through it. Freezing is not the same
! as switching the channel off in preferences -- the household still faces the
! same problem, it simply does not see the aggregate move -- which is exactly the
! counterfactual an externality is defined against.
!===============================================================================
subroutine solve_equilibrium_frozen(taul0, pv0, avg0, med0, fix_tax, fix_pv, fix_scale)
    real(dp), intent(in) :: taul0, pv0, avg0, med0
    logical,  intent(in) :: fix_tax, fix_pv, fix_scale
    type(agg_t) :: A
    integer  :: it
    real(dp) :: tau_new, pv_new, H_new, HD_new, avg_new, med_new, err, damp

    damp = 0.25_dp
    if (fix_tax)   tau_l = taul0
    if (fix_pv)    p_v   = pv0
    if (fix_scale) then
        avg_income = avg0; median_income = med0
    end if

    do it = 1, 40
        call solve_once(A)
        err = 0.0_dp

        if (.not. fix_tax) then
            if (A%labinc_pow > 0.0_dp) then
                tau_new = (A%labinc + A%captax - A%govt_outlay)/A%labinc_pow
            else
                tau_new = tau_l
            end if
            tau_new = min(max(tau_new, 0.30_dp), 1.20_dp)
            err = max(err, reldiff(tau_new, tau_l))
            tau_l = tau_l + damp*(tau_new - tau_l)
        end if

        if (.not. fix_pv) then
            if (A%drugq > 0.0_dp) then
                pv_new = psi1 * A%drugq**(psi2 - 1.0_dp)
            else
                pv_new = p_v
            end if
            pv_new = min(max(pv_new, 0.05_dp), 20.0_dp)
            err = max(err, reldiff(pv_new, p_v))
            p_v = p_v + 0.08_dp*(pv_new - p_v)
        end if

        if (.not. fix_scale) then
            avg_new = (A%labinc + A%ss)/max(A%pop, 1.0e-12_dp)
            med_new = A%med
            err = max(err, reldiff(avg_new, avg_income))
            avg_income    = avg_income    + damp*(avg_new - avg_income)
            median_income = median_income + damp*(med_new - median_income)
        end if

        H_new  = A%homeless/max(A%pop, 1.0e-12_dp)
        HD_new = A%hl_sud  /max(A%pop, 1.0e-12_dp)
        H_agg  = H_agg  + damp*(H_new  - H_agg)
        HD_agg = HD_agg + damp*(HD_new - HD_agg)

        if (err < 1.0e-4_dp) exit
    end do
end subroutine solve_equilibrium_frozen


!-- normalise the drug supply shifter so that p_v = 1 at the current demand --
subroutine normalise_drug_supply()
    type(agg_t) :: A
    call solve_once(A)
    if (A%drugq > 0.0_dp) then
        psi1 = 1.0_dp / A%drugq**(psi2 - 1.0_dp)
        p_v  = 1.0_dp
    end if
end subroutine normalise_drug_supply


!===============================================================================
! Stationary distribution. Lives here rather than in main so the equilibrium
! loop can call it.
!===============================================================================
subroutine build_distribution_eq()
    integer  :: j, ia, iy, ie, id, iv, im, iap, ihp
    real(dp) :: m, phi, s_e(NE), s_d(ND), s_eta(NV)

    dist = 0.0_dp
    do im = 1, NM
    do iy = 1, NY
        dist(1,iy,1,1,1,im,1) = y_dist0(iy)*mh_dist0(im)
    end do
    end do

    do j = 1, n_age-1
        do im = 1, NM
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
        do iy = 1, NY
        do ia = 1, NA
            m = dist(ia,iy,ie,id,iv,im,j)
            if (m <= 0.0_dp) cycle
            call trans_kernel(ia,iy,ie,id,iv,im,j,.false.,0, iap,ihp,phi,s_e,s_d,s_eta)
            if (phi <= 0.0_dp) cycle
            call add_mass(dist, iap, iy, id, im, j, m, phi, s_e, s_d, s_eta)
        end do
        end do
        end do
        end do
        end do
        end do
    end do
end subroutine build_distribution_eq


!-- ex-ante expected lifetime utility of a newborn ---------------------------
function newborn_welfare() result(W)
    real(dp) :: W
    integer  :: iy, im
    W = 0.0_dp
    do im = 1, NM
    do iy = 1, NY
        W = W + y_dist0(iy)*mh_dist0(im)*V(1,iy,1,1,1,im,1)
    end do
    end do
end function newborn_welfare

end module equilibrium
