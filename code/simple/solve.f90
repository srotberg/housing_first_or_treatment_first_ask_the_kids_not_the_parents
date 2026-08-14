!===============================================================================
! solve.f90 -- household problem for the simplified model
!
! Four design choices carry the speed:
!
! 1. HOUSING ENTERED WITH IS NOT A STATE. Survival, employment transitions and
!    the recovery hazard all condition on the CHOSEN h', and renters face no
!    adjustment cost, so the unit a household arrives in is payoff-irrelevant.
!    Carrying it replicates the whole problem NH times for nothing.
!
! 2. PRECOMPUTED EXPECTATION. The next-period expectation is built once per age
!    and read as a table. In the original code it is rebuilt inside the a' loop,
!    so it is recomputed once per current asset gridpoint. The transition
!    kernels do not depend on current assets except through the binary voucher
!    eligibility indicator, so two copies suffice rather than NA.
!
! 3. EXACT REGIME DECOMPOSITION instead of coarse-then-refine. The objective is
!    not single-peaked in a' -- voucher eligibility is a step function of income
!    (which includes r*a), the food-stamp floor kinks, and housing is discrete.
!    Within a regime the c/v split is closed-form Cobb-Douglas, so we search a'
!    exactly on the full grid and take the max over the handful of regimes. No
!    unimodality assumption, and no basin-hopping failure.
!
! 4. POWERS HOISTED. The nested Cobb-Douglas collapses to a single product, the
!    housing and Stone-Geary powers are precomputed, and sigma=2 is special-
!    cased so the CRRA transform is a reciprocal rather than a pow().
!===============================================================================
module solve
    use params
    implicit none

    ! EV(ia', ih', iy, ie, id, ireg, itr, ielig, iv, im)
    real(dp), allocatable :: EV(:,:,:,:,:,:,:,:,:,:)
    real(dp), allocatable :: VY(:,:,:,:,:,:)   ! (ia',iy,ie',id',iv',im')

contains

subroutine alloc_solve()
    allocate(EV(NA,NH,NY,NE,ND,NREG,0:1,0:1,NV,NM))
    allocate(VY(NA,NY,NE,ND,NV,NM))
end subroutine alloc_solve


!-- flow utility. hp is the PRECOMPUTED h**beta_u for the chosen unit ---------
pure function util(c, hp, v, bb) result(u)
    real(dp), intent(in) :: c, hp, v, bb
    real(dp) :: u, comp
    if (c <= 0.0_dp) then
        u = -1.0e12_dp; return
    end if
    comp = c**alpha_u * hp * (v + bb)**gamma_u
    if (comp <= 0.0_dp) then
        u = -1.0e12_dp; return
    end if
    if (abs(sigma - 2.0_dp) < 1.0e-12_dp) then
        u = -1.0_dp/comp + aleph - kappa_ext*H_agg          ! sigma = 2 fast path
    else
        u = comp**(1.0_dp-sigma)/(1.0_dp-sigma) + aleph - kappa_ext*H_agg
    end if
end function util


!-- gross labour / retirement income -----------------------------------------
! Productivity penalties apply CONDITIONAL ON WORKING. This is what lets an
! employed household have low enough income to choose homelessness, which an
! unemployment effect alone cannot deliver (R1 comment 2(c)(i)), and it answers
! the AE's question A20 on direct productivity effects of SUD.
pure function income_gross(j, iy, ie, id, im) result(y)
    integer, intent(in) :: j, iy, ie, id, im
    real(dp) :: y, prod
    prod = 1.0_dp
    if (id == 2) prod = prod * prod_pen_d
    if (im == 2) prod = prod * prod_pen_m
    if (j >= j_ret) then
        y = 0.40_dp * y_grid(iy)                       ! social security, no penalty
    else if (ie == 1) then
        y = y_grid(iy) * age_prof(j) * prod            ! employed
    else if (ie == 2) then
        y = ui_replace * y_grid(iy) * age_prof(j)      ! UI, first year only
    else
        y = 0.0_dp                                     ! no UI: food stamps only
    end if
end function income_gross


pure function after_tax(y) result(yn)
    real(dp), intent(in) :: y
    real(dp) :: yn
    yn = tau_l * max(y, 1.0e-10_dp)**xi_tax
end function after_tax


!===============================================================================
! Expectation table for age j, given V at age j+1. Staged reduction: integrate
! over y' first (independent of every choice), then over (e', d', eta').
!===============================================================================
subroutine build_EV(j)
    integer, intent(in) :: j
    integer :: ia, iy, iyp, iep, idp, ihp, ivp, ie, id, ireg, itr, ielig, iv
    integer :: im, imp
    real(dp) :: acc, pe, pd, pv_eta, pm, pfind, psep, prec, paddict
    real(dp) :: s_eta(NV), s_d(ND), s_e(NE)

    !-- stage 1: integrate over next-period productivity ---------------------
    ! NB: collapsed loop variables are private by default and must NOT appear
    ! in the private clause -- doing so is non-conforming and segfaults.
    !$omp parallel do collapse(4) private(ia,iy,acc,iyp) schedule(static)
    do imp = 1, NM
    do ivp = 1, NV
    do idp = 1, ND
    do iep = 1, NE
        do iy = 1, NY
            do ia = 1, NA
                acc = 0.0_dp
                do iyp = 1, NY
                    acc = acc + y_trans(iy,iyp) * V(ia,iyp,iep,idp,ivp,imp,j+1)
                end do
                VY(ia,iy,iep,idp,ivp,imp) = acc
            end do
        end do
    end do
    end do
    end do
    end do
    !$omp end parallel do

    !-- stage 2: integrate over employment, SUD and voucher transitions ------
    !$omp parallel do collapse(4) &
    !$omp   private(ia,ihp,ireg,itr,ielig,acc,iep,idp,ivp,imp,iy,ie, &
    !$omp           pfind,psep,prec,paddict,s_e,s_d,s_eta,pe,pd,pv_eta,pm) &
    !$omp   schedule(static)
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
        do ielig = 0, 1
        do itr = 0, 1
        do ireg = 1, NREG
        do ihp = 1, NH

            call emp_trans(ie, ihp, id, im, s_e)

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
                prec = p_recover(ihp, itr, im)
                s_d(1) = prec;             s_d(2) = 1.0_dp - prec
            end if

            call voucher_probs(iv, ielig, ireg, id, s_eta)

            do ia = 1, NA
                acc = 0.0_dp
                do iep = 1, NE
                    pe = s_e(iep)
                    if (pe <= 0.0_dp) cycle
                    do idp = 1, ND
                        pd = s_d(idp)
                        if (pd <= 0.0_dp) cycle
                        do ivp = 1, NV
                            pv_eta = s_eta(ivp)
                            if (pv_eta <= 0.0_dp) cycle
                            do imp = 1, NM
                                pm = mh_trans(im,imp)
                                if (pm <= 0.0_dp) cycle
                                acc = acc + pe*pd*pv_eta*pm*VY(ia,iy,iep,idp,ivp,imp)
                            end do
                        end do
                    end do
                end do
                EV(ia,ihp,iy,ie,id,ireg,itr,ielig,iv,im) = acc
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
    !$omp end parallel do
end subroutine build_EV


!-- voucher receipt distribution next period ---------------------------------
subroutine voucher_probs(iv, ielig, ireg, id, s)
    integer, intent(in) :: iv, ielig, ireg, id
    real(dp), intent(out) :: s(NV)
    real(dp) :: pkeep

    if (ielig == 0) then
        s(1) = 1.0_dp; s(2) = 0.0_dp; return
    end if

    if (iv == 2) then
        pkeep = 1.0_dp          ! keep an existing voucher while eligible
    else
        pkeep = prob_V          ! otherwise win the lottery
    end if

    if (policy_TF == 1) then
        if (ireg > 1) then
            pkeep = pkeep * (1.0_dp - detect_prob)   ! using: lose it if detected
        else
            pkeep = pkeep * (1.0_dp - false_pos)     ! clean: false positive risk
        end if
    end if

    s(2) = min(1.0_dp, max(0.0_dp, pkeep))
    s(1) = 1.0_dp - s(2)
end subroutine voucher_probs


!===============================================================================
! Backward induction.
!===============================================================================
subroutine solve_household()
    integer :: j, ia, iy, ie, id, iv, im
    integer :: ihp, ireg, itr, iap, ielig
    integer :: best_a, best_h, best_reg, best_tr
    real(dp) :: res, R, Rt, cc, vv, val, best, phi
    real(dp) :: ygross, ynet, vouch, cfloor, v_unc, cost_tr, bestc, bestv

    cfloor = cfloor_share * avg_income
    V(:,:,:,:,:,:,n_age+1) = 0.0_dp

    do j = n_age, 1, -1

        call build_EV(j)

        !$omp parallel do collapse(4) &
        !$omp   private(ia,iy,ihp,ireg,itr,iap,ielig, &
        !$omp           best_a,best_h,best_reg,best_tr,res,R,Rt,cc,vv,val,best, &
        !$omp           phi,ygross,ynet,vouch,v_unc,cost_tr,bestc,bestv) &
        !$omp   schedule(dynamic)
        do im = 1, NM
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
            do iy = 1, NY
            do ia = 1, NA

                ygross = income_gross(j, iy, ie, id, im)
                ynet   = after_tax(ygross) + r*a_grid(ia)

                if (ygross + max(0.0_dp, r*a_grid(ia)) < kappa_V*median_income) then
                    ielig = 1
                else
                    ielig = 0
                end if

                best = -1.0e13_dp
                best_a = 1; best_h = 1; best_reg = 1; best_tr = 0
                bestc = 0.0_dp; bestv = 0.0_dp

                do ihp = 1, NH

                    phi = survival(j, ihp, id, im)

                    ! the voucher pays only while renting, never while homeless
                    vouch = 0.0_dp
                    if (ihp > 1 .and. iv == 2) then
                        vouch = max(0.0_dp, p_rent*h_grid(ihp) - kappa_r*ygross)
                    end if

                    if (ihp == 1) then
                        res = ynet + a_grid(ia) + bequest
                    else
                        res = ynet + a_grid(ia) + bequest - p_rent*h_grid(ihp) + vouch
                    end if
                    res = res + max(0.0_dp, cfloor - (ygross + max(0.0_dp,r*a_grid(ia))))

                    do itr = 0, 1
                        if (itr == 1 .and. (id == 1 .or. allow_treatment == 0)) cycle
                        cost_tr = 0.0_dp
                        if (itr == 1) cost_tr = treat_cost*avg_income

                        do ireg = 1, NREG
                            ! a clean household past j_exp cannot initiate use
                            if (id == 1 .and. j > j_exp .and. ireg > 1) cycle

                            do iap = 1, NA
                                R = res - a_grid(iap) - cost_tr
                                if (R <= 0.0_dp) exit      ! a_grid is increasing

                                ! closed-form Cobb-Douglas split of R over (c, v)
                                Rt = R + p_v*b_dm(id,im)
                                v_unc = gamma_u/(alpha_u+gamma_u) * Rt/p_v - b_dm(id,im)

                                select case (ireg)
                                case (1)
                                    vv = 0.0_dp
                                case (2)
                                    vv = min(max(v_unc, 1.0e-8_dp), vbar)
                                case (3)
                                    vv = max(v_unc, vbar)
                                end select

                                cc = R - p_v*vv
                                if (cc <= 0.0_dp) cycle

                                val = util(cc, h_pow(ihp), vv, b_dm(id,im)) &
                                    + beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)

                                if (val > best) then
                                    best = val
                                    best_a = iap; best_h = ihp
                                    best_reg = ireg; best_tr = itr
                                    bestc = cc; bestv = vv
                                end if
                            end do
                        end do
                    end do
                end do

                V(ia,iy,ie,id,iv,im,j)      = best
                pol_a(ia,iy,ie,id,iv,im,j)  = best_a
                pol_h(ia,iy,ie,id,iv,im,j)  = best_h
                pol_reg(ia,iy,ie,id,iv,im,j)= best_reg
                pol_tr(ia,iy,ie,id,iv,im,j) = best_tr
                pol_c(ia,iy,ie,id,iv,im,j)  = bestc
                pol_v(ia,iy,ie,id,iv,im,j)  = bestv

            end do
            end do
        end do
        end do
        end do
        end do
        !$omp end parallel do

    end do
end subroutine solve_household

end module solve
