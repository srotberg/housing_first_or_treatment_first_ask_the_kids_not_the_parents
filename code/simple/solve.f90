!===============================================================================
! solve.f90 -- household problem for the simplified model
!
! Five design choices carry the speed:
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
! 4. CONTINUOUS LABOUR SUPPLY FROM THE INTRATEMPORAL FOC, by bisection on
!    [0,1] -- the method used in the original code. Given a', hours never touch
!    the EV table, so the FOC is a scalar solve over a handful of flops.
!    Voucher eligibility is a STEP in hours, so it is handled by the same exact
!    decomposition as everything else: the unconstrained root is computed once
!    and then clamped into each of the two eligibility branches, which is exact
!    under single crossing and costs one extra flow evaluation rather than a
!    second bisection.
!
! 5. POWERS HOISTED. The nested Cobb-Douglas collapses to a single product, the
!    housing and Stone-Geary powers are precomputed, and sigma = sigma_l = 2,3
!    are special-cased so the CRRA and leisure transforms are reciprocals rather
!    than pow() calls.
!===============================================================================
module solve
    use params
    implicit none

    integer, parameter :: NCAND  = 8  ! hours pieces x eligibility branches
    integer, parameter :: NBPMAX = 4  ! budget breakpoints in hours: 0, hF, hV, 1

    ! everything about the hours problem that does not depend on a'
    type :: hpts_t
        integer  :: n                        ! number of breakpoints
        real(dp) :: h(NBPMAX)                ! the breakpoints, ascending
        real(dp) :: res(NBPMAX)              ! resources there
        real(dp) :: dL(NBPMAX), dR(NBPMAX)   ! one-sided d(res)/d(hours)
        real(dp) :: lp(NBPMAX)               ! (1-h)**sigma_l there
        real(dp) :: hE, res_hE               ! eligibility threshold, resources there
        real(dp) :: w, base, vcap, cfl_net   ! carried for the root solve
    end type hpts_t

    ! EV(ia', ih', iy, ie, id, ireg, itr, ielig, iv, im)
    real(dp), allocatable :: EV(:,:,:,:,:,:,:,:,:,:)
    real(dp), allocatable :: VY(:,:,:,:,:,:)   ! (ia',iy,ie',id',iv',im')

contains

subroutine alloc_solve()
    allocate(EV(NA,NH,NY,NE,ND,NREG,0:1,0:1,NV,NM))
    allocate(VY(NA,NY,NE,ND,NV,NM))
end subroutine alloc_solve


!-- leisure terms, special-cased for sigma_l = 3 ------------------------------
! U_leisure = omega_l * leis**(1-sigma_l)/(1-sigma_l);  its derivative with
! respect to LEISURE is omega_l * leis**(-sigma_l), which is MU_1 in the
! original code's `objective`.
pure function u_leis(leis) result(ul)
    real(dp), intent(in) :: leis
    real(dp) :: ul, x, l2
    x = max(leis, 1.0e-8_dp)
    if (abs(sigma_l - 3.0_dp) < 1.0e-12_dp) then
        l2 = x*x
        ul = -0.5_dp*omega_l/l2
    else
        ul = omega_l * x**(1.0_dp-sigma_l)/(1.0_dp-sigma_l)
    end if
end function u_leis


! leis**sigma_l -- the RECIPROCAL of the marginal utility of leisure, up to
! omega_l. The FOC is solved multiplied through by this, which is what keeps the
! residual bounded as hours approach one; see the header of hfoc.
pure function leis_pow(leis) result(p)
    real(dp), intent(in) :: leis
    real(dp) :: p, x
    x = max(leis, 1.0e-8_dp)
    if (abs(sigma_l - 3.0_dp) < 1.0e-12_dp) then
        p = x*x*x
    else
        p = x**sigma_l
    end if
end function leis_pow


!-- flow utility. hp is the PRECOMPUTED h**beta_u for the chosen unit ---------
pure function util(c, hp, v, bb, leis) result(u)
    real(dp), intent(in) :: c, hp, v, bb, leis
    real(dp) :: u, comp
    if (c <= 0.0_dp) then
        u = -1.0e12_dp; return
    end if
    comp = c**alpha_u * hp * (v + bb)**gamma_u
    if (comp <= 0.0_dp) then
        u = -1.0e12_dp; return
    end if
    if (abs(sigma - 2.0_dp) < 1.0e-12_dp) then
        u = -1.0_dp/comp + u_leis(leis) + aleph - kappa_ext*(H_agg + omega_ext*HD_agg)
    else
        u = comp**(1.0_dp-sigma)/(1.0_dp-sigma) + u_leis(leis) + aleph &
          - kappa_ext*(H_agg + omega_ext*HD_agg)
    end if
end function util


!-- gross labour / retirement income -----------------------------------------
! Productivity penalties apply CONDITIONAL ON WORKING. This is what lets an
! employed household have low enough income to choose homelessness, which an
! unemployment effect alone cannot deliver (R1 comment 2(c)(i)), and it answers
! the AE's question A20 on direct productivity effects of SUD.
pure function income_gross(j, iy, ie, id, im, hours) result(y)
    integer, intent(in) :: j, iy, ie, id, im
    real(dp), intent(in) :: hours
    real(dp) :: y, prod
    prod = 1.0_dp
    if (id == 2) prod = prod * prod_pen_d
    if (im == 2) prod = prod * prod_pen_m
    if (j >= j_ret) then
        y = 0.40_dp * y_grid(iy)                       ! social security, no penalty
    else if (ie == 1) then
        y = hours * y_grid(iy) * age_prof(j) * prod    ! employed
    else if (ie == 2) then
        y = ui_replace * y_grid(iy) * age_prof(j)      ! UI, first year only
    else if (im == 2 .and. include_disability == 1) then
        y = di_coverage * disab_income * avg_income    ! disability, SMI only
    else
        y = 0.0_dp                                     ! no UI: food stamps only
    end if
end function income_gross


!-- the wage per unit of hours for an employed household of working age -------
pure function wage_rate(j, iy, id, im) result(w)
    integer, intent(in) :: j, iy, id, im
    real(dp) :: w, prod
    prod = 1.0_dp
    if (id == 2) prod = prod * prod_pen_d
    if (im == 2) prod = prod * prod_pen_m
    w = y_grid(iy) * age_prof(j) * prod
end function wage_rate


pure function after_tax(y) result(yn)
    real(dp), intent(in) :: y
    real(dp) :: yn
    yn = tau_l * max(y, 1.0e-10_dp)**xi_tax
end function after_tax


!===============================================================================
! CONTINUOUS LABOUR SUPPLY FROM THE INTRATEMPORAL FOC
!
!   MU_1 = omega_l*(1-hours)**(-sigma_l)            marginal utility of leisure
!   MU_2 = u_c(c) * d(resources)/d(hours)           marginal utility of working
!   F    = MU_2 - MU_1;  F > 0 means "work more", which is the sign the original
!          code brackets on.
!
! u_c is one expression in both drug regimes. At an interior drug choice the
! Cobb-Douglas split gives c = alpha/(alpha+gamma)*(R + p_v*b) and
! comp = AK*(R+p_v*b)**(alpha+gamma), so u_c = (alpha+gamma)/(AK*Rt**(a+g+1))
! when sigma = 2. At the corner v = 0, comp = A1*R**alpha and
! u_c = alpha/(A1*R**(alpha+1)). Either way ONE pow per evaluation.
!
! F is NOT monotone on [0,1), so a single bisection is wrong. Resources are
! kinked in hours at two points, both of the form w*hours = constant:
!
!   hF = cfl_net/w          food stamps exhausted   (clawback rate 1)
!   hV = vcap/(kappa_r*w)   voucher exhausted       (clawback rate kappa_r)
!
! d(res)/d(hours) JUMPS UP at hF and hV, so F jumps up there and can cross zero
! more than once. That is not a numerical nuisance, it is the welfare trap: with
! a 100% food-stamp clawback the return to work is near zero below hF, so "work
! a little and keep the transfer" and "work properly" are distinct local optima
! and the model has to compare them. So [0,1] is split at the kinks and each
! piece solved exactly -- inside a piece F is continuous and strictly
! decreasing, hence single-crossing -- and every local optimum is returned as a
! candidate. Same exact-decomposition logic as the a' search, applied to hours.
!
! A third threshold, hE, is where voucher ELIGIBILITY is lost. It kinks nothing
! in the budget, so F is continuous across it and it needs no piece of its own;
! it is a jump in the CONTINUATION value, so the piece optimum is simply clamped
! to each side of it and both are evaluated.
!
! Speed. The breakpoints, the resources at them, the one-sided slopes and the
! marginal utility of leisure at them depend on (a, h') but NOT on a', the drug
! regime or treatment. They are built once per (a, h') in `build_hpoints`, so
! testing a piece inside the a' loop costs one pow (the marginal utility of
! consumption) rather than a full budget evaluation. Only a piece that actually
! brackets a root pays for a root solve, and that uses Illinois false position,
! which needs a handful of evaluations where bisection to 1e-8 would need 27.
!===============================================================================


!-- resources and their slope, for an arbitrary hours value ------------------
!   base    hours-independent part:  a + r*a + bequest - rent(h')
!   vcap    p_rent*h' if the voucher is actually paid on this unit, else 0
!   cfl_net cfloor - max(0, r*a): food stamps are positive iff w*hours < cfl_net
! The original code carries the voucher clawback in the labour-supply FOC; the
! food-stamp clawback is carried here too.
pure subroutine res_slope(hours, w, base, vcap, cfl_net, res, dres)
    real(dp), intent(in)  :: hours, w, base, vcap, cfl_net
    real(dp), intent(out) :: res, dres
    real(dp) :: yg, atax, vch, fs
    yg   = max(hours*w, 1.0e-10_dp)
    atax = tau_l * yg**xi_tax
    vch  = max(0.0_dp, vcap - kappa_r*yg)
    fs   = max(0.0_dp, cfl_net - yg)
    res  = base + atax + vch + fs
    ! d(atax)/d(hours) = tau_l*xi*w*yg**(xi-1) = xi*w*atax/yg -- no second pow
    dres = xi_tax*w*atax/yg
    if (vch > 0.0_dp) dres = dres - kappa_r*w
    if (fs  > 0.0_dp) dres = dres - w
end subroutine res_slope


!-- everything about the hours problem that does not depend on a' ------------
pure subroutine build_hpoints(w, base, vcap, cfl_net, h_elig, G)
    real(dp), intent(in)  :: w, base, vcap, cfl_net, h_elig
    type(hpts_t), intent(out) :: G
    real(dp) :: hF, hV, x, yg, atax, smooth
    integer  :: k, i

    G%w = w; G%base = base; G%vcap = vcap; G%cfl_net = cfl_net
    G%hE = h_elig

    hF = 2.0_dp; hV = 2.0_dp
    if (w > 0.0_dp) then
        if (cfl_net > 0.0_dp) hF = cfl_net/w
        if (vcap    > 0.0_dp) hV = vcap/(kappa_r*w)
    end if

    G%n = 2; G%h(1) = 0.0_dp; G%h(2) = 1.0_dp
    call insert_bp(G%h, G%n, hF)
    call insert_bp(G%h, G%n, hV)

    do k = 1, G%n
        x    = G%h(k)
        yg   = max(x*w, 1.0e-10_dp)
        atax = tau_l * yg**xi_tax
        G%res(k) = base + atax + max(0.0_dp, vcap - kappa_r*yg) &
                        + max(0.0_dp, cfl_net - yg)
        smooth   = xi_tax*w*atax/yg
        ! just BELOW x the transfer is still positive when x <= threshold;
        ! just ABOVE it only when x < threshold
        G%dL(k) = smooth
        if (x <= hV) G%dL(k) = G%dL(k) - kappa_r*w
        if (x <= hF) G%dL(k) = G%dL(k) - w
        G%dR(k) = smooth
        if (x <  hV) G%dR(k) = G%dR(k) - kappa_r*w
        if (x <  hF) G%dR(k) = G%dR(k) - w
        G%lp(k)  = leis_pow(1.0_dp - x)
    end do

    ! resources at the eligibility threshold, for the clamped candidate
    G%res_hE = 0.0_dp
    if (h_elig > 0.0_dp .and. h_elig < 1.0_dp) then
        yg   = max(h_elig*w, 1.0e-10_dp)
        atax = tau_l * yg**xi_tax
        G%res_hE = base + atax + max(0.0_dp, vcap - kappa_r*yg) &
                        + max(0.0_dp, cfl_net - yg)
    end if
    i = 0
end subroutine build_hpoints


!-- insert x into a sorted breakpoint list, if it lies strictly inside (0,1) --
pure subroutine insert_bp(bp, n, x)
    real(dp), intent(inout) :: bp(:)
    integer,  intent(inout) :: n
    real(dp), intent(in)    :: x
    integer :: i, k
    if (x <= 1.0e-7_dp .or. x >= 1.0_dp - 1.0e-7_dp) return
    k = n
    do i = 1, n
        if (x < bp(i)) then
            k = i - 1; exit
        end if
    end do
    do i = n, k+1, -1
        bp(i+1) = bp(i)
    end do
    bp(k+1) = x
    n = n + 1
end subroutine insert_bp


!-- RECIPROCAL marginal utility of consumption out of resources R ------------
! The FOC is solved in the form
!
!     G(h) = d(res)/d(hours) - MU_leisure / u_c   ==  0,
!
! not  u_c*d(res)/d(hours) - MU_leisure == 0. The two have the same sign, so
! the bracketing logic is identical, but u_c has a pole at R = 0 (it grows like
! R**-(alpha+1)) and false position on a function with a pole crawls: profiling
! the unscaled version showed 22 iterations per root, because one endpoint
! carried a residual six orders of magnitude larger than the other. 1/u_c is a
! POLYNOMIAL in R, so G is smooth and well scaled, and the same solver converges
! in a handful of steps.
!
! It also removes the infeasibility sentinel: at R <= 0 nothing can be bought,
! 1/u_c = 0, and G reduces to d(res)/d(hours), which points in the direction
! that makes the household feasible again.
pure function invmuc_of(R, A1, AK, bb, ireg) result(w)
    real(dp), intent(in) :: R, A1, AK, bb
    integer,  intent(in) :: ireg
    real(dp) :: w, Rt, vv, cc, comp
    if (R <= 0.0_dp) then
        w = 0.0_dp; return
    end if
    vv = -1.0_dp
    if (ireg > 1) vv = gamma_u/(alpha_u+gamma_u) * (R + p_v*bb)/p_v - bb
    if (vv > 1.0e-8_dp) then
        Rt = R + p_v*bb
        if (abs(sigma - 2.0_dp) < 1.0e-12_dp) then
            w = AK*Rt**(alpha_u+gamma_u+1.0_dp)/(alpha_u+gamma_u)
        else
            comp = AK*Rt**(alpha_u+gamma_u)
            w    = Rt/((alpha_u+gamma_u)*comp**(1.0_dp-sigma))
        end if
    else
        cc = R
        if (ireg > 1) cc = R - p_v*1.0e-8_dp
        if (cc <= 0.0_dp) then
            w = 0.0_dp; return
        end if
        if (abs(sigma - 2.0_dp) < 1.0e-12_dp) then
            w = A1*cc**(alpha_u+1.0_dp)/alpha_u
        else
            comp = A1*cc**alpha_u
            w    = cc/(alpha_u*comp**(1.0_dp-sigma))
        end if
    end if
end function invmuc_of


!-- one FOC residual at an arbitrary hours value (two pows) ------------------
! The FOC   u_c * d(res)/d(hours) = omega_l*(1-h)**(-sigma_l)   is solved in the
! equivalent form
!
!   G(h) = d(res)/d(hours) * (1-h)**sigma_l  -  omega_l / u_c   ==  0,
!
! obtained by multiplying through by (1-h)**sigma_l / u_c, both positive, so the
! sign -- and hence every bracketing decision -- is unchanged. This matters a
! lot numerically. In the raw form one side of the bracket carries a pole in
! u_c (which grows like R**-(alpha+1) as resources run out) and the other a pole
! in the marginal utility of leisure (which blows up as hours approach one), and
! false position on a function whose endpoint residuals differ by six orders of
! magnitude crawls: profiling showed 22 iterations per root. Multiplied through,
! both terms are bounded and smooth and the same solver converges in about five.
pure subroutine hfoc(h, G, A1, AK, bb, acost, ireg, res, F)
    real(dp), intent(in)  :: h, A1, AK, bb, acost
    type(hpts_t), intent(in) :: G
    integer,  intent(in)  :: ireg
    real(dp), intent(out) :: res, F
    real(dp) :: dres
    call res_slope(h, G%w, G%base, G%vcap, G%cfl_net, res, dres)
    F = dres*leis_pow(1.0_dp - h) - omega_l*invmuc_of(res - acost, A1, AK, bb, ireg)
end subroutine hfoc


!-- Anderson-Bjorck false position on a piece where G(lo) > 0 > G(hi) --------
! Plain Illinois (always halve the stale endpoint) is not enough here. The
! residual still carries one pole, at hours = 0, because the HSV tax function
! tau*y**xi has infinite slope at zero earnings, so the left endpoint of the
! first piece can carry a residual two hundred times the right endpoint's and
! Illinois spends eight iterations just halving it away -- measured at 16
! evaluations per root. Anderson-Bjorck scales the stale endpoint by
! 1 - f_new/f_old instead of by 1/2, which collapses that asymmetry in one step.
! `warm` is the root found at the previous (smaller) a'. Hours are increasing in
! a' inside a piece -- saving more raises the marginal utility of consumption
! and so the return to working -- so the previous root is a good first trial and
! cuts the iteration count roughly in half. It is used only as a starting point,
! never as a bound, so the bracket still guarantees convergence.
pure subroutine hroot(lo, hi, flo, fhi, G, A1, AK, bb, acost, ireg, warm, hstar, rstar)
    real(dp), intent(in)  :: lo, hi, flo, fhi, A1, AK, bb, acost, warm
    type(hpts_t), intent(in) :: G
    integer,  intent(in)  :: ireg
    real(dp), intent(out) :: hstar, rstar
    real(dp) :: a, b, fa, fb, c, cprev, fc, rc, mscale
    integer  :: k

    a = lo; fa = flo; b = hi; fb = fhi
    rc = 0.0_dp; cprev = -1.0_dp

    if (warm > lo .and. warm < hi) then
        c = warm
    else
        c = b - fb*(b-a)/(fb-fa)
    end if

    ! Illinois converges the ITERATE superlinearly but can leave the bracket
    ! wide, so the stopping test is on the step, not on b-a.
    do k = 1, hours_maxit
        if (k > 1) then
            if (fa > fb) then
                c = b - fb*(b-a)/(fb-fa)
            else
                c = 0.5_dp*(a+b)
            end if
        end if
        if (c <= a .or. c >= b) c = 0.5_dp*(a+b)

        call hfoc(c, G, A1, AK, bb, acost, ireg, rc, fc)

        if (abs(c - cprev) < hours_tol .or. fc == 0.0_dp) exit
        cprev = c

        if (fc > 0.0_dp) then
            mscale = 1.0_dp - fc/fa
            if (mscale <= 0.0_dp) mscale = 0.5_dp
            fb = mscale*fb
            a  = c; fa = fc
        else
            mscale = 1.0_dp - fc/fb
            if (mscale <= 0.0_dp) mscale = 0.5_dp
            fa = mscale*fa
            b  = c; fb = fc
        end if
        if (b - a < hours_tol) exit
    end do

    hstar = c; rstar = rc
end subroutine hroot


!-- every local optimum of hours, with its eligibility branch attached -------
pure subroutine hours_candidates(G, A1, AK, bb, acost, ireg, warm, nc, hc, rc, ec)
    type(hpts_t), intent(in) :: G
    real(dp), intent(in)     :: A1, AK, bb, acost
    integer,  intent(in)     :: ireg
    real(dp), intent(inout)  :: warm(NBPMAX)      ! previous root in each piece
    integer,  intent(out) :: nc, ec(NCAND)
    real(dp), intent(out) :: hc(NCAND), rc(NCAND)

    real(dp) :: iw(NBPMAX), fR, fL, hstar, rstar
    integer  :: k
    logical  :: split

    do k = 1, G%n
        iw(k) = invmuc_of(G%res(k) - acost, A1, AK, bb, ireg)
    end do

    nc = 0
    do k = 1, G%n - 1
        ! residual just inside each end of the piece
        fR = G%dR(k)  *G%lp(k)   - omega_l*iw(k)
        fL = G%dL(k+1)*G%lp(k+1) - omega_l*iw(k+1)

        if (fR <= 0.0_dp) then
            hstar = G%h(k);   rstar = G%res(k)       ! wants less work than the floor
        else if (fL >= 0.0_dp) then
            hstar = G%h(k+1); rstar = G%res(k+1)     ! wants more work than the cap
        else
            call hroot(G%h(k), G%h(k+1), fR, fL, G, A1, AK, bb, acost, ireg, &
                       warm(k), hstar, rstar)
            warm(k) = hstar
        end if

        ! clamp to each side of the eligibility threshold when it splits this piece
        split = (G%hE > G%h(k) .and. G%hE < G%h(k+1))
        if (.not. split) then
            nc = nc + 1
            hc(nc) = hstar; rc(nc) = rstar
            if (hstar < G%hE) then
                ec(nc) = 1
            else
                ec(nc) = 0
            end if
        else
            if (hstar < G%hE) then
                nc = nc + 1; hc(nc) = hstar;  rc(nc) = rstar;    ec(nc) = 1
                nc = nc + 1; hc(nc) = G%hE;   rc(nc) = G%res_hE; ec(nc) = 0
            else
                nc = nc + 1; hc(nc) = G%hE - 1.0e-9_dp
                             rc(nc) = G%res_hE; ec(nc) = 1
                nc = nc + 1; hc(nc) = hstar;  rc(nc) = rstar;    ec(nc) = 0
            end if
        end if
        if (nc >= NCAND - 1) exit
    end do
end subroutine hours_candidates


!===============================================================================
! Expectation table for age j, given V at age j+1. Staged reduction: integrate
! over y' first (independent of every choice), then over (e', d', eta').
!===============================================================================
subroutine build_EV(j)
    integer, intent(in) :: j
    integer :: ia, iy, iyp, iep, idp, ihp, ivp, ie, id, ireg, itr, ielig, iv
    integer :: im, imp
    real(dp) :: acc, pe, pd, pv_eta, pm, prec, paddict
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
    !$omp           prec,paddict,s_e,s_d,s_eta,pe,pd,pv_eta,pm) &
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
                else
                    paddict = pi_d_low          ! single hazard, any use
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
    integer :: ihp, ireg, itr, iap, ielig, ic, nc
    integer :: best_a, best_h, best_reg, best_tr
    real(dp) :: res, R, Rt, cc, vv, val, best, phi
    real(dp) :: ynet, vouch, cfloor, v_unc, cost_tr, bestc, bestv, bestl
    real(dp) :: hours, w, base, vcap, cfl_net, res_ub, y0, bb
    real(dp) :: h_elig, acost, A1, AK, akcon
    real(dp) :: hc(NCAND), rc(NCAND), warm(NBPMAX)
    integer  :: ec(NCAND)
    type(hpts_t) :: G
    logical  :: working

    cfloor = cfloor_share * avg_income
    ! the Cobb-Douglas constant in comp = AK*(R+p_v*b)**(alpha+gamma), net of
    ! the housing term, which is h_pow(ihp)
    akcon = (alpha_u/(alpha_u+gamma_u))**alpha_u &
          * (gamma_u/((alpha_u+gamma_u)*p_v))**gamma_u

    V(:,:,:,:,:,:,n_age+1) = 0.0_dp

    do j = n_age, 1, -1

        call build_EV(j)

        !$omp parallel do collapse(4) &
        !$omp   private(ia,iy,ihp,ireg,itr,iap,ielig,ic,nc, &
        !$omp           best_a,best_h,best_reg,best_tr,res,R,Rt,cc,vv,val,best, &
        !$omp           phi,ynet,vouch,v_unc,cost_tr,bestc,bestv,bestl,hours, &
        !$omp           w,base,vcap,cfl_net,res_ub,y0,bb,h_elig,acost,A1,AK, &
        !$omp           hc,rc,ec,working,G,warm) &
        !$omp   schedule(dynamic)
        do im = 1, NM
        do iv = 1, NV
        do id = 1, ND
        do ie = 1, NE
            do iy = 1, NY
            do ia = 1, NA

                best = -1.0e13_dp
                best_a = 1; best_h = 1; best_reg = 1; best_tr = 0
                bestc = 0.0_dp; bestv = 0.0_dp; bestl = 0.0_dp
                bb = b_dm(id,im)

                ! hours are a choice only for the employed of working age
                working = (j < j_ret .and. ie == 1)

                if (working) then
                    w  = wage_rate(j, iy, id, im)
                    y0 = 0.0_dp
                else
                    w  = 0.0_dp
                    y0 = income_gross(j, iy, ie, id, im, 0.0_dp)
                end if

                ! food stamps are positive iff w*hours < cfl_net
                cfl_net = cfloor - max(0.0_dp, r*a_grid(ia))

                ! voucher eligibility is a STEP in hours:
                !   eligible  <=>  w*hours + max(0,r*a) < kappa_V*median_income
                ! h_elig <= 0 : never eligible;  h_elig >= 1 : always eligible
                if (working) then
                    h_elig = (kappa_V*median_income - max(0.0_dp, r*a_grid(ia))) / w
                else
                    if (y0 + max(0.0_dp, r*a_grid(ia)) < kappa_V*median_income) then
                        h_elig = 2.0_dp
                    else
                        h_elig = -1.0_dp
                    end if
                end if

                do ihp = 1, NH

                    phi = survival(j, ihp, id, im)

                    ! the voucher pays only while renting, never while homeless
                    if (ihp > 1 .and. iv == 2) then
                        vcap = p_rent*h_grid(ihp)
                    else
                        vcap = 0.0_dp
                    end if

                    base = a_grid(ia) + bequest + r*a_grid(ia)
                    if (ihp > 1) base = base - p_rent*h_grid(ihp)

                    A1 = h_pow(ihp) * bb**gamma_u
                    AK = akcon * h_pow(ihp)

                    ! Upper bound on resources over all hours: full after-tax
                    ! earnings, the full voucher and the full food-stamp top-up,
                    ! ignoring the clawbacks that make them mutually exclusive.
                    ! Only used to terminate the a' loop, so a loose bound is
                    ! safe -- infeasible a' are skipped below.
                    if (working) then
                        res_ub = base + after_tax(w) + vcap + max(0.0_dp, cfl_net)
                        call build_hpoints(w, base, vcap, cfl_net, h_elig, G)
                    else
                        res_ub = base + after_tax(y0) &
                               + max(0.0_dp, vcap - kappa_r*y0) &
                               + max(0.0_dp, cfl_net - y0)
                    end if

                    do itr = 0, 1
                        if (itr == 1 .and. (id == 1 .or. allow_treatment == 0)) cycle
                        cost_tr = 0.0_dp
                        if (itr == 1) cost_tr = treat_cost*avg_income

                        do ireg = 1, NREG
                            ! a clean household past j_exp cannot initiate use
                            if (id == 1 .and. j > j_exp .and. ireg > 1) cycle

                            warm = -1.0_dp     ! hours are increasing in a'

                            do iap = 1, NA
                                acost = a_grid(iap) + cost_tr
                                if (res_ub - acost <= 0.0_dp) exit   ! a_grid increasing

                                !-- hours: every local optimum, with its
                                !   eligibility branch attached
                                if (working) then
                                    call hours_candidates(G, A1, AK, bb, acost, ireg, &
                                                          warm, nc, hc, rc, ec)
                                else
                                    nc    = 1
                                    hc(1) = 0.0_dp
                                    rc(1) = res_ub
                                    if (h_elig > 1.0_dp) then
                                        ec(1) = 1
                                    else
                                        ec(1) = 0
                                    end if
                                end if

                                do ic = 1, nc
                                    hours = hc(ic)
                                    res   = rc(ic)
                                    ielig = ec(ic)

                                    R = res - acost
                                    if (R <= 0.0_dp) cycle

                                    ! closed-form Cobb-Douglas split of R over (c, v)
                                    Rt = R + p_v*bb
                                    v_unc = gamma_u/(alpha_u+gamma_u) * Rt/p_v - bb

                                    if (ireg == 1) then
                                        vv = 0.0_dp
                                    else
                                        vv = max(v_unc, 1.0e-8_dp)   ! interior optimum
                                    end if

                                    cc = R - p_v*vv
                                    if (cc <= 0.0_dp) cycle

                                    val = util(cc, h_pow(ihp), vv, bb, 1.0_dp-hours) &
                                        + beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)

                                    if (val > best) then
                                        best = val
                                        best_a = iap; best_h = ihp
                                        best_reg = ireg; best_tr = itr
                                        bestl = hours
                                        bestc = cc; bestv = vv
                                    end if
                                end do
                            end do
                        end do
                    end do
                end do

                V(ia,iy,ie,id,iv,im,j)      = best
                pol_a(ia,iy,ie,id,iv,im,j)  = best_a
                pol_h(ia,iy,ie,id,iv,im,j)  = best_h
                pol_reg(ia,iy,ie,id,iv,im,j)= best_reg
                pol_tr(ia,iy,ie,id,iv,im,j) = best_tr
                pol_l(ia,iy,ie,id,iv,im,j)  = bestl
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
