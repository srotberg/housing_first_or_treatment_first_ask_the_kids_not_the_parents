!===============================================================================
! equilibrium.f90 -- stationary equilibrium for the simplified model
!
! Objects that clear:
!   tau_l    government budget balance (closed form given the distribution)
!   p_v      drug market, p_v = psi1 * V**(psi2-1)
!   bequest  assets of the deceased redistributed to survivors
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
        real(dp) :: homeless=0, sud=0, users=0, unemp=0, drugq=0
        real(dp) :: assets_dead=0, consumption=0, treated=0
        real(dp) :: govt_outlay=0, tax_rev=0
    end type agg_t

    real(dp) :: G_public = 0.0_dp        ! public goods, calibrated then held fixed
    logical  :: G_is_set = .false.

contains

!-- everything the equilibrium conditions need, in one pass ------------------
subroutine compute_aggregates(A)
    type(agg_t), intent(out) :: A
    integer  :: j, ia, iy, ie, id, iv, ihp, ireg, itr, iap
    real(dp) :: m, ygross, ynet, vouch, res, phi, food_j, cc, vv, capinc_j


    do j = 1, n_age
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,j)
        if (m <= 0.0_dp) cycle

        ihp  = pol_h(ia,iy,ie,id,iv,j)
        iap  = pol_a(ia,iy,ie,id,iv,j)
        ireg = pol_reg(ia,iy,ie,id,iv,j)
        itr  = pol_tr(ia,iy,ie,id,iv,j)
        cc   = pol_c(ia,iy,ie,id,iv,j)
        vv   = pol_v(ia,iy,ie,id,iv,j)

        ygross   = income_gross(j, iy, ie)
        capinc_j = r*a_grid(ia)
        phi      = survival(j, ihp, id)

        A%pop = A%pop + m

        ! income and the tax base
        if (j < j_ret) then
            A%labinc     = A%labinc     + m*ygross
            A%labinc_pow = A%labinc_pow + m*max(ygross,1.0e-10_dp)**xi_tax
            if (ie == 1) A%ui = A%ui + m*ygross     ! UI is the unemployed income flow
            if (ie == 1) A%unemp = A%unemp + m
        else
            A%ss = A%ss + m*ygross
        end if

        A%capinc = A%capinc + m*capinc_j
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

        ! outcomes
        if (ihp == 1) A%homeless = A%homeless + m
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

    A%govt_outlay = A%ss + A%food + A%vouchers &
                  + chi_H*A%homeless + chi_D*A%sud + G_public
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
    real(dp) :: tau_new, pv_new, beq_new, H_new, avg_new, med_new
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
        if (A%pop > 0.0_dp) then
            beq_new = A%assets_dead / A%pop
        else
            beq_new = bequest
        end if

        ! ---- externality and income aggregates ------------------------------
        H_new   = A%homeless / max(A%pop, 1.0e-12_dp)
        avg_new = (A%labinc + A%ss) / max(A%pop, 1.0e-12_dp)
        med_new = avg_new          ! placeholder: replace with a true median

        ! relative residuals: the discrete choice set makes threshold rules
        ! (food-stamp floor, voucher eligibility) chatter, so an absolute
        ! criterion on income aggregates never settles
        err = reldiff(tau_new, tau_l)
        err = max( err, reldiff(pv_new,  p_v) )
        err = max( err, reldiff(beq_new, bequest) )
        err = max( err, reldiff(avg_new, avg_income) )
        ! H_agg only matters when the externality is switched on
        if (kappa_ext > 0.0_dp) err = max( err, reldiff(H_new, H_agg) )

        if (verbose) then
            write(*,'(A,I3,A,F9.5,A,F8.4,A,F8.4,A,F8.5,A,F7.3,A)') &
                ' it ', it, '  err=', err, '  tau=', tau_new, '  p_v=', pv_new, &
                '  beq=', beq_new, '  homeless=', 100.0_dp*H_new, '%'
        end if

        tau_l      = tau_l      + damp*(tau_new - tau_l)
        p_v        = p_v        + damp*(pv_new  - p_v)
        bequest    = bequest    + damp*(beq_new - bequest)
        H_agg      = H_agg      + damp*(H_new   - H_agg)
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
    integer  :: j, ia, iy, ie, id, iv
    integer  :: iap, ihp, ireg, itr, iyp, iep, idp, ivp, ielig
    real(dp) :: m, phi, pfind, psep, prec, paddict, ygross
    real(dp) :: s_e(NE), s_d(ND), s_eta(NV)

    dist = 0.0_dp
    do iy = 1, NY
        dist(1,iy,2,1,1,1) = y_dist0(iy)
    end do

    do j = 1, n_age-1
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
        do iy = 1, NY
        do ia = 1, NA
            m = dist(ia,iy,ie,id,iv,j)
            if (m <= 0.0_dp) cycle

            iap  = pol_a(ia,iy,ie,id,iv,j)
            ihp  = pol_h(ia,iy,ie,id,iv,j)
            ireg = pol_reg(ia,iy,ie,id,iv,j)
            itr  = pol_tr(ia,iy,ie,id,iv,j)

            phi = survival(j, ihp, id)
            if (phi <= 0.0_dp) cycle

            ygross = income_gross(j, iy, ie)
            if (ygross + max(0.0_dp, r*a_grid(ia)) < kappa_V*median_income) then
                ielig = 1
            else
                ielig = 0
            end if

            pfind = p_find(ihp, id)
            psep  = p_sep(ihp, id)
            if (ie == 2) then
                s_e(1) = psep;           s_e(2) = 1.0_dp - psep
            else
                s_e(1) = 1.0_dp - pfind; s_e(2) = pfind
            end if

            if (id == 1) then
                if (ireg == 1) then
                    paddict = 0.0_dp
                else if (ireg == 2) then
                    paddict = pi_d_low
                else
                    paddict = pi_d_high
                end if
                s_d(1) = 1.0_dp - paddict; s_d(2) = paddict
            else
                prec = p_recover(ihp, itr)
                s_d(1) = prec;             s_d(2) = 1.0_dp - prec
            end if

            call voucher_probs(iv, ielig, ireg, id, s_eta)

            do iyp = 1, NY
                if (y_trans(iy,iyp) <= 0.0_dp) cycle
                do iep = 1, NE
                    if (s_e(iep) <= 0.0_dp) cycle
                    do idp = 1, ND
                        if (s_d(idp) <= 0.0_dp) cycle
                        do ivp = 1, NV
                            if (s_eta(ivp) <= 0.0_dp) cycle
                            dist(iap,iyp,iep,idp,ivp,j+1) = &
                                dist(iap,iyp,iep,idp,ivp,j+1) + &
                                m*phi*y_trans(iy,iyp)*s_e(iep)*s_d(idp)*s_eta(ivp)
                        end do
                    end do
                end do
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
    integer  :: iy
    W = 0.0_dp
    do iy = 1, NY
        W = W + y_dist0(iy)*V(1,iy,2,1,1,1)
    end do
end function newborn_welfare

end module equilibrium
