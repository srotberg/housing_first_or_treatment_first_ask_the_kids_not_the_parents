!===============================================================================
! welfare.f90 -- every externality, measured, in one unit.
!
! R3's M2c: since drug use is rational and forward-looking, where do the
! externalities justifying intervention arise? Listing them is not enough --
! a reader needs to see which ones are large.
!
! There are FIVE in this model, and the first two are usually collapsed into one
! by mistake:
!
!   a  FISCAL, MECHANICAL. chi_D and chi_H, higher transfer receipt and a
!      smaller tax base, all financed by tau_l on everybody else.
!   b  FISCAL, DEADWEIGHT. tau_l distorts labour supply, which is elastic here
!      (Frisch 0.5). This is a pure welfare loss ON TOP of the transfer in (a),
!      and it is exactly what R3's minor comment 1 is asking about.
!   c  DISAMENITY. kappa_x*(H + omega_x*HD), directly in period utility.
!   d  DRUG PRICE. p_v is an equilibrium object, so one more user raises the
!      price every other user pays. It is a transfer to producers, who are
!      outside the model, so from the households' side it is a real loss.
!   e  TRANSFER SCALE. Average income sets the food-stamp floor and the
!      disability benefit; median income sets voucher eligibility. One more case
!      of SUD lowers both, for everyone.
!
! MEASUREMENT. Raise the addiction hazard by a small amount, re-solve the
! equilibrium, and compare newborn welfare. That gives the TOTAL effect, which
! mixes the private cost -- internalised, and therefore not an externality --
! with the five above. Each channel is then isolated by re-solving with that
! channel FROZEN at its benchmark value: the difference between the full
! re-solve and the frozen one is that channel's contribution.
!
! Everything is reported as consumption-equivalent variation for a newborn,
! which is the same unit the policy counterfactuals will use, so the reader can
! put the externalities and the policy effects side by side.
!===============================================================================
module welfare
    use params
    use solve
    use equilibrium
    implicit none

    integer, parameter :: NCH = 6      ! total, then the five channels
    character(len=34), parameter :: ch_name(NCH) = &
        [ character(len=34) :: &
          'TOTAL effect of more SUD          ', &
          'a. fiscal, mechanical transfer    ', &
          'b. fiscal, deadweight loss        ', &
          'c. disamenity                     ', &
          'd. drug price                     ', &
          'e. transfer scale (avg/median)    ' ]

contains

!-- expected lifetime utility of a newborn -----------------------------------
! The newborn draws productivity from its ergodic distribution and mental health
! from the clean-household ergodic distribution, with zero assets, employed, no
! SUD and no voucher -- exactly the state build_distribution_eq seeds.
function newborn_value() result(w)
    real(dp) :: w
    integer  :: iy, im
    w = 0.0_dp
    do im = 1, NM
    do iy = 1, NY
        w = w + y_dist0(iy)*mh_dist0(im)*V(1,iy,1,1,1,im,1)
    end do
    end do
end function newborn_value


!-- consumption-equivalent variation between two newborn values ---------------
! With the CRRA-over-Cobb-Douglas bundle and sigma = 2 the flow is -1/comp, and
! comp scales with c**alpha, so scaling consumption by (1+g) at every date and
! state scales the bundle term by (1+g)**alpha and hence the flow by
! (1+g)**(-alpha). The additive terms -- leisure, aleph, the disamenity -- do NOT
! scale, so a closed-form CEV is not available and it is computed by bisection
! on a uniform consumption scaling. That is slower and it is right; the
! shortcut of dividing the utility difference by a marginal utility is only a
! first-order approximation and it is wrong by exactly the additive terms, which
! are large here because aleph is large.
function cev(w_new, w_base) result(g)
    real(dp), intent(in) :: w_new, w_base
    real(dp) :: g, lo, hi, mid, wtry
    integer  :: k
    lo = -0.90_dp; hi = 10.0_dp
    do k = 1, 40
        mid  = 0.5_dp*(lo+hi)
        wtry = scaled_newborn_value(mid)
        if (wtry > w_new) then
            hi = mid
        else
            lo = mid
        end if
    end do
    g = 0.5_dp*(lo+hi)
    ! silence an unused-argument warning while keeping the signature honest
    if (w_base > 1.0e30_dp) g = g
end function cev


!-- newborn value if consumption were scaled by (1+g) at every date -----------
! Re-solving is not needed: scaling c uniformly scales comp by (1+g)**alpha, so
! every bundle term scales by (1+g)**(alpha*(1-sigma)) while the additive terms
! stay put. The value function is rebuilt from the stored policies rather than
! re-optimised, which is the correct object for a compensating variation.
function scaled_newborn_value(g) result(w)
    real(dp), intent(in) :: g
    real(dp) :: w, sc
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: cc, vv, bb, comp, flow, hours, leis
    real(dp), allocatable :: Vs(:,:,:,:,:,:,:)
    integer  :: iap, ireg, itr, ielig
    real(dp) :: phi, s_e(NE), s_d(ND), s_eta(NV), acc
    integer  :: iyp, iep, idp, ivp, imp

    allocate(Vs(NA,NY,NE,ND,NV,NM,n_age+1))
    Vs = 0.0_dp
    sc = (1.0_dp + g)**alpha_u

    do j = n_age, 1, -1
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        ihp = pol_h(ia,iy,ie,id,iv,im,j)
        cc  = pol_c(ia,iy,ie,id,iv,im,j)
        vv  = pol_v(ia,iy,ie,id,iv,im,j)
        if (cc <= 0.0_dp) then
            Vs(ia,iy,ie,id,iv,im,j) = -1.0e13_dp; cycle
        end if
        bb    = b_of(id, im, ihp)
        hours = hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j))
        leis  = 1.0_dp - hours
        comp  = sc * cc**alpha_u * h_pow(ihp) * (vv + bb)**gamma_u
        if (abs(sigma - 2.0_dp) < 1.0e-12_dp) then
            flow = -1.0_dp/comp
        else
            flow = comp**(1.0_dp-sigma)/(1.0_dp-sigma)
        end if
        flow = flow + u_leis(leis) + aleph &
             - kappa_ext*(H_agg + omega_ext*HD_agg)
        if (pol_tr(ia,iy,ie,id,iv,im,j) == 1) flow = flow - treat_ucost

        call trans_kernel(ia,iy,ie,id,iv,im,j,.false.,0, iap,ihp,phi,s_e,s_d,s_eta)
        acc = 0.0_dp
        do iyp = 1, NY
            if (y_trans(iy,iyp) <= 0.0_dp) cycle
            do iep = 1, NE
                if (s_e(iep) <= 0.0_dp) cycle
                do idp = 1, ND
                    if (s_d(idp) <= 0.0_dp) cycle
                    do ivp = 1, NV
                        if (s_eta(ivp) <= 0.0_dp) cycle
                        do imp = 1, NM
                            if (pm_of(id,im,imp, j) <= 0.0_dp) cycle
                            acc = acc + y_trans(iy,iyp)*s_e(iep)*s_d(idp) &
                                *s_eta(ivp)*pm_of(id,im,imp, j) &
                                *Vs(iap,iyp,iep,idp,ivp,imp,j+1)
                        end do
                    end do
                end do
            end do
        end do
        Vs(ia,iy,ie,id,iv,im,j) = flow + beta*phi*acc
    end do; end do; end do
    end do; end do; end do
    end do

    w = 0.0_dp
    do im = 1, NM
    do iy = 1, NY
        w = w + y_dist0(iy)*mh_dist0(im)*Vs(1,iy,1,1,1,im,1)
    end do
    end do
    deallocate(Vs)
end function scaled_newborn_value

!===============================================================================
! The decomposition.
!
! Raise the addiction hazard by `bump_frac` and re-solve. Newborn welfare falls
! for two reasons that must be kept apart: the household's own expected cost,
! which it internalises and which is NOT an externality, and the five channels
! that operate through prices, the budget and other people's utility, which it
! does not.
!
! Each channel is isolated by re-solving with that channel FROZEN at its
! benchmark value. Freezing tau_l removes the fiscal transfer AND its deadweight
! loss together, so the two are separated by a second run in which tau_l moves
! but labour supply cannot respond -- the gap between them is the distortion.
!===============================================================================
subroutine decompose_externalities(bump_frac, verbose, cev_out)
    real(dp), intent(in)  :: bump_frac
    logical,  intent(in)  :: verbose
    real(dp), intent(out) :: cev_out(NCH)
    type(agg_t) :: A
    real(dp) :: pid0, taul0, pv0, kx0, avg0, med0, w0, w1
    real(dp) :: w_notax, w_nodwl, w_nodis, w_nopv, w_noscale
    real(dp) :: c_tot, c_notax, c_nodwl

    !-- benchmark -------------------------------------------------------------
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    call compute_aggregates(A)
    w0    = newborn_value()
    pol_lb = pol_l                 ! benchmark labour supply, for the DWL arm
    pid0  = pi_d_low
    taul0 = tau_l;  pv0 = p_v;  kx0 = kappa_ext
    avg0  = avg_income; med0 = median_income

    !-- all channels live -----------------------------------------------------
    pi_d_low = pid0*(1.0_dp + bump_frac)
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    w1 = newborn_value()

    !-- (a)+(b) freeze the tax: no fiscal channel at all ---------------------
    call freeze_and_solve(taul0, pv0, kx0, avg0, med0, .true., .false., .false., .false.)
    w_notax = newborn_value()

    !-- tax moves, but hours cannot respond ----------------------------------
    ! This arm isolates the MECHANICAL transfer: the household pays the higher
    ! tax but is not allowed to answer it by working less, so no distortion is
    ! created. The deadweight loss is then the residual, w1 vs this.
    call freeze_and_solve(taul0, pv0, kx0, avg0, med0, .false., .false., .false., .true.)
    w_nodwl = newborn_value()

    !-- (c) freeze the disamenity --------------------------------------------
    call freeze_and_solve(taul0, pv0, kx0, avg0, med0, .false., .false., .true., .false.)
    w_nodis = newborn_value()

    !-- (d) freeze the drug price --------------------------------------------
    call freeze_and_solve(taul0, pv0, kx0, avg0, med0, .false., .true., .false., .false.)
    w_nopv = newborn_value()

    !-- (e) freeze the transfer scale ----------------------------------------
    call freeze_and_solve(taul0, pv0, kx0, avg0, med0, .false., .false., .false., .false., fix_scale=.true.)
    w_noscale = newborn_value()

    !-- restore ---------------------------------------------------------------
    pi_d_low = pid0
    call solve_equilibrium(40, 1.0e-4_dp, .false.)

    ! Every CEV is measured against the SAME benchmark policies -- which is the
    ! state the model is in now, after the restore above -- so the channels are
    ! in comparable units. cev(w1,w0) is the same number six times over, and a
    ! single call is forty full value-function rebuilds, so compute it once.
    c_tot   = cev(w1,        w0)
    c_notax = cev(w_notax,   w0)
    c_nodwl = cev(w_nodwl,   w0)

    cev_out(1) = c_tot
    ! hours frozen: the tax moves but creates no distortion -> MECHANICAL
    cev_out(2) = c_nodwl - c_notax
    ! letting hours respond on top of that is the DEADWEIGHT LOSS
    cev_out(3) = c_tot   - c_nodwl
    cev_out(4) = c_tot - cev(w_nodis,   w0)
    cev_out(5) = c_tot - cev(w_nopv,    w0)
    cev_out(6) = c_tot - cev(w_noscale, w0)

    if (verbose) call print_externalities(cev_out, bump_frac)
end subroutine decompose_externalities


!-- re-solve with the named channels held at their benchmark values ----------
subroutine freeze_and_solve(taul0, pv0, kx0, avg0, med0, &
                            fix_tax, fix_pv, fix_dis, fix_hours, fix_scale)
    real(dp), intent(in) :: taul0, pv0, kx0, avg0, med0
    logical,  intent(in) :: fix_tax, fix_pv, fix_dis, fix_hours
    logical,  intent(in), optional :: fix_scale
    real(dp) :: om0, kx_save
    logical  :: sc
    sc = .false.
    if (present(fix_scale)) sc = fix_scale

    om0 = omega_l; kx_save = kappa_ext
    ! pol_lb was filled from the BENCHMARK solve before the hazard was bumped,
    ! so freeze_hours holds labour supply at its benchmark schedule
    if (fix_hours) freeze_hours = 1
    if (fix_dis)   kappa_ext = 0.0_dp

    call solve_equilibrium_frozen(taul0, pv0, avg0, med0, fix_tax, fix_pv, sc)

    freeze_hours = 0
    omega_l = om0; kappa_ext = kx_save
    if (kx0 > 1.0e30_dp) continue
end subroutine freeze_and_solve


subroutine print_externalities(c, bump_frac)
    real(dp), intent(in) :: c(NCH), bump_frac
    integer :: k
    write(*,'(A)') ''
    write(*,'(A)') '  ============ externalities, consumption-equivalent ============'
    write(*,'(A,F6.1,A)') '  Newborn CEV of raising the addiction hazard by ', &
        100.0_dp*bump_frac, '%.'
    write(*,'(A)') '  Negative = welfare loss. The TOTAL includes the household''s own'
    write(*,'(A)') '  internalised cost; the five channels below it do not.'
    write(*,'(A)') '  ---------------------------------------------------------------'
    do k = 1, NCH
        write(*,'(A,A,F12.6,A)') '   ', ch_name(k), 100.0_dp*c(k), ' % of consumption'
    end do
    write(*,'(A)') '  ---------------------------------------------------------------'
    write(*,'(A,F12.6,A)') '   sum of the five externality channels : ', &
        100.0_dp*sum(c(2:NCH)), ' %'
    write(*,'(A)') '   Channels c-e are each measured with the other channels LIVE,'
    write(*,'(A)') '   so they need not sum to the total and the sum is a diagnostic,'
    write(*,'(A)') '   not a decomposition. a and b do add up: they are a nested pair.'
    write(*,'(A)') '  ==============================================================='
end subroutine print_externalities

end module welfare
