!===============================================================================
! transition.f90 -- perfect-foresight transition paths between steady states.
!
! Referee 1's comment 3(d) calls the submitted paper's several-period partial-
! equilibrium exercise "a half-measure" and asks for proper transition paths.
! This is that.
!
! WHAT NEEDS A TRANSITION AND WHAT DOES NOT. A randomised trial of two hundred
! people does not move the tax rate or the drug price, so the second-stage
! experimental moments in experiment.f90 are partial-equilibrium COHORT
! experiments and correctly hold prices fixed. A national change in the voucher
! rule is different: it moves the government budget and the drug market, and the
! households alive when it is announced face a different sequence of prices from
! the ones born later. That is what this module computes.
!
! WHAT HAS TO CLEAR, AND WHAT NO LONGER DOES. With homeownership and the housing
! market gone, and with accidental bequests going to the government rather than
! back to households, a path iterates on the labour tax and the drug price alone
! -- two sequences, not five. That is why this is tractable here and was not in
! the original model.
!
! STRUCTURE. The economy sits in the initial steady state at t = 0, the policy is
! announced and implemented at t = 1, and it has converged to the terminal steady
! state by t = T. The household problem runs BACKWARDS over (age, time) from the
! terminal steady state; the distribution runs FORWARDS from the initial one.
!
!   V_{j,t} = f( V_{j+1,t+1} ),   with V_{.,T+1} = V^{terminal}
!   Phi_{.,t+1} = g( Phi_{.,t}, policies_t )
!
! MEMORY. Storing every policy function at every date is the obvious approach and
! costs about 19 MB per date, so a fifty-period path would need a gigabyte. It is
! not needed: the backward pass stores only value functions (6.3 MB per date),
! and the forward pass re-derives each date's policy from the stored V_{.,t+1}
! immediately before using it. That doubles the household solves and cuts memory
! by a factor of three, which is the right trade when the alternative risks
! swapping.
!===============================================================================
module transition
    use params
    use solve
    use equilibrium
    implicit none

    integer :: T_path = 60             ! periods to the terminal steady state

    ! value functions along the path: Vp(:,:,:,:,:,:, j, t)
    real(dp), allocatable :: Vp(:,:,:,:,:,:,:,:)
    ! scratch for one date's solve: see the note in solve_date
    real(dp), allocatable :: Vnew(:,:,:,:,:,:,:), Vkeep(:,:,:,:,:,:)
    ! price paths
    real(dp), allocatable :: taul_t(:), pv_t(:), avg_t(:), med_t(:)
    real(dp), allocatable :: H_t(:), HD_t(:)
    ! The distribution as it walks forward. NOT named Phi: Fortran is
    ! case-insensitive, so a module array Phi collides with the local scalar phi
    ! that every distribution loop uses for the survival probability. That is the
    ! fourth collision of this kind in this codebase -- after J/j, M/mom and r/R,
    ! one of which silently corrupted capital income for months. Module-level
    ! names here are long enough that nothing shadows them by accident.
    real(dp), allocatable :: dist_t(:,:,:,:,:,:,:)

    ! endpoints
    real(dp), allocatable :: V_term(:,:,:,:,:,:,:)
    real(dp), allocatable :: dist_init(:,:,:,:,:,:,:)
    ! NB: the terminal scalars are suffixed _end, not _T. taul_T would collide
    ! with the path array taul_t -- Fortran is case-insensitive, and that is the
    ! same trap that silently broke capital income in solve_household.
    real(dp) :: taul_0, pv_0, avg_0, med_0, H_0, HD_0
    real(dp) :: taul_end, pv_end, avg_end, med_end, H_end, HD_end

contains

subroutine alloc_transition()
    if (allocated(Vp)) return
    allocate(Vp(NA,NY,NE,ND,NV,NM,n_age+1,T_path+1))
    allocate(taul_t(T_path), pv_t(T_path), avg_t(T_path), med_t(T_path))
    allocate(H_t(T_path), HD_t(T_path))
    allocate(dist_t(NA,NY,NE,ND,NV,NM,n_age))
    allocate(V_term(NA,NY,NE,ND,NV,NM,n_age+1))
    allocate(dist_init(NA,NY,NE,ND,NV,NM,n_age))
    allocate(Vnew(NA,NY,NE,ND,NV,NM,n_age+1))
    allocate(Vkeep(NA,NY,NE,ND,NV,NM))
end subroutine alloc_transition


!===============================================================================
! Solve every age at one date, against the NEXT DATE's value function.
!
! This needs care that the stationary solver does not. In a steady state
! V_j = f(V_{j+1}) within the same value function, so solving ages downwards in
! place is fine: age j's answer overwrites a slice nobody reads again. Along a
! path V_{j,t} = f(V_{j+1,t+1}), and solving in place destroys exactly the slice
! the NEXT age needs -- writing V_{j,t} over V_{j,t+1} means build_EV(j-1) then
! reads a date-t continuation where it should read date t+1. The path would look
! plausible and be wrong.
!
! So each slice of the continuation is saved before solve_age clobbers it and
! restored immediately after, with the answers accumulated separately.
!===============================================================================
subroutine solve_date(t)
    integer, intent(in) :: t
    integer :: j
    call load_prices(t)
    V = Vp(:,:,:,:,:,:,:,t+1)              ! the continuation, date t+1
    do j = n_age, 1, -1
        call build_EV(j)                   ! reads V(...,j+1), still date t+1
        Vkeep = V(:,:,:,:,:,:,j)           ! date t+1's slice j
        call solve_age(j)                  ! writes date t into V(...,j)
        Vnew(:,:,:,:,:,:,j) = V(:,:,:,:,:,:,j)
        V(:,:,:,:,:,:,j)    = Vkeep        ! put t+1 back for build_EV(j-1)
    end do
    Vnew(:,:,:,:,:,:,n_age+1) = 0.0_dp
end subroutine solve_date


!-- record the current stationary equilibrium as the INITIAL condition --------
subroutine set_initial()
    dist_init = dist
    taul_0 = tau_l;  pv_0 = p_v
    avg_0  = avg_income; med_0 = median_income
    H_0    = H_agg;  HD_0 = HD_agg
end subroutine set_initial


!-- record the current stationary equilibrium as the TERMINAL condition -------
subroutine set_terminal()
    V_term = V
    taul_end = tau_l;  pv_end = p_v
    avg_end  = avg_income; med_end = median_income
    H_end    = H_agg;  HD_end = HD_agg
end subroutine set_terminal


!-- put the module-level prices at their date-t path values -------------------
subroutine load_prices(t)
    integer, intent(in) :: t
    if (t > T_path) then
        tau_l = taul_end; p_v = pv_end; avg_income = avg_end
        median_income = med_end; H_agg = H_end; HD_agg = HD_end
    else
        tau_l = taul_t(t); p_v = pv_t(t); avg_income = avg_t(t)
        median_income = med_t(t); H_agg = H_t(t); HD_agg = HD_t(t)
    end if
end subroutine load_prices


!===============================================================================
! One backward pass over (age, time).
!
! At date t the household of age j solves against V_{j+1,t+1}, so the sweep runs
! t = T down to 1 and, within each t, j = J down to 1. `solve_age` is the single
! age-step of the stationary solver, factored out so it can be reused here
! against an arbitrary continuation rather than only against next period's own
! value function.
!===============================================================================
subroutine backward_pass()
    integer :: t

    Vp(:,:,:,:,:,:,:,T_path+1) = V_term

    do t = T_path, 1, -1
        call solve_date(t)
        Vp(:,:,:,:,:,:,:,t) = Vnew
    end do
end subroutine backward_pass


!===============================================================================
! One forward pass, re-deriving each date's policy immediately before using it.
!
! This is where the doubled household-solve cost is paid, and it is why memory
! stays at value functions only. The distribution starts from the initial steady
! state, which is NOT the terminal one, so the first cohorts alive at the
! announcement carry the old distribution into the new rules.
!===============================================================================
subroutine forward_pass(A_t)
    type(agg_t), intent(out) :: A_t(T_path)
    integer :: t

    dist_t = dist_init
    do t = 1, T_path
        call solve_date(t)     ! leaves the date-t POLICIES in the pol_* arrays
        ! aggregates use the CURRENT distribution and the date-t policies
        dist = dist_t
        call compute_aggregates(A_t(t))
        call advance_distribution()
    end do
end subroutine forward_pass


!-- push dist_t one period forward under the policies now in the pol_* arrays ----
! Newborns enter each period, so unlike the cohort experiments in experiment.f90
! this is a full population update.
subroutine advance_distribution()
    real(dp), allocatable :: Pn(:,:,:,:,:,:,:)
    integer  :: j, ia, iy, ie, id, iv, im
    integer  :: iap, ihp, ireg, itr, iyp, iep, idp, ivp, imp, ielig
    real(dp) :: m, phi, prec, paddict, ygross
    real(dp) :: s_e(NE), s_d(ND), s_eta(NV)

    allocate(Pn(NA,NY,NE,ND,NV,NM,n_age))
    Pn = 0.0_dp

    ! newborns
    do im = 1, NM
    do iy = 1, NY
        Pn(1,iy,1,1,1,im,1) = y_dist0(iy)*mh_dist0(im)
    end do
    end do

    do j = 1, n_age-1
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist_t(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle

        iap  = pol_a(ia,iy,ie,id,iv,im,j)
        ihp  = pol_h(ia,iy,ie,id,iv,im,j)
        ireg = pol_reg(ia,iy,ie,id,iv,im,j)
        itr  = pol_tr(ia,iy,ie,id,iv,im,j)

        phi = survival(j, ihp, id, im)
        if (phi <= 0.0_dp) cycle

        ygross = income_gross(j, iy, ie, id, im, hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j)))
        if (ygross + max(0.0_dp, r_free*a_grid(ia)) < kappa_V*median_income) then
            ielig = 1
        else
            ielig = 0
        end if

        call emp_trans(ie, ihp, id, im, s_e)
        if (id == 1) then
            if (ireg == 1) then
                paddict = 0.0_dp
            else
                paddict = pi_d_low
            end if
            s_d(1) = 1.0_dp - paddict; s_d(2) = paddict
        else
            prec = p_recover(ihp, itr, im)
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
                        do imp = 1, NM
                            if (pm_of(id,im,imp) <= 0.0_dp) cycle
                            Pn(iap,iyp,iep,idp,ivp,imp,j+1) = &
                                Pn(iap,iyp,iep,idp,ivp,imp,j+1) + &
                                m*phi*y_trans(iy,iyp)*s_e(iep)*s_d(idp) &
                                *s_eta(ivp)*pm_of(id,im,imp)
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
    end do
    end do

    dist_t = Pn
    deallocate(Pn)
end subroutine advance_distribution


!===============================================================================
! Solve the path.
!
! Damped Gauss-Seidel on the two price sequences, exactly as the stationary
! solver does but date by date. The damping has to be gentler than in the
! stationary problem because an error at one date propagates to every earlier
! date through the backward pass.
!===============================================================================
subroutine solve_path(maxit, tol, verbose)
    integer,  intent(in) :: maxit
    real(dp), intent(in) :: tol
    logical,  intent(in) :: verbose
    type(agg_t) :: A_t(T_path)
    integer  :: it, t
    real(dp) :: err, damp, dpv, taul_new, pv_new

    damp = 0.20_dp

    ! start from a linear interpolation between the endpoints -- with the drug
    ! supply near-horizontal the price barely moves, so this is already close
    do t = 1, T_path
        taul_t(t) = taul_0 + (taul_end-taul_0)*real(t,dp)/real(T_path,dp)
        pv_t(t)   = pv_0   + (pv_end  -pv_0  )*real(t,dp)/real(T_path,dp)
        avg_t(t)  = avg_0  + (avg_end -avg_0 )*real(t,dp)/real(T_path,dp)
        med_t(t)  = med_0  + (med_end -med_0 )*real(t,dp)/real(T_path,dp)
        H_t(t)    = H_0    + (H_end   -H_0   )*real(t,dp)/real(T_path,dp)
        HD_t(t)   = HD_0   + (HD_end  -HD_0  )*real(t,dp)/real(T_path,dp)
    end do

    do it = 1, maxit
        call backward_pass()
        call forward_pass(A_t)

        err = 0.0_dp
        do t = 1, T_path
            ! labour tax: closed form from the date-t government budget
            if (A_t(t)%labinc_pow > 0.0_dp) then
                taul_new = (A_t(t)%labinc + A_t(t)%captax - A_t(t)%govt_outlay) &
                         / A_t(t)%labinc_pow
            else
                taul_new = taul_t(t)
            end if
            taul_new = min(max(taul_new, 0.30_dp), 1.20_dp)

            ! drug price from the supply curve
            if (A_t(t)%drugq > 0.0_dp) then
                pv_new = psi1 * A_t(t)%drugq**(psi2 - 1.0_dp)
            else
                pv_new = pv_t(t)
            end if
            pv_new = min(max(pv_new, 0.05_dp), 20.0_dp)

            err = max(err, abs(taul_new - taul_t(t))/max(1.0_dp, abs(taul_t(t))))
            err = max(err, abs(pv_new   - pv_t(t)  )/max(1.0_dp, abs(pv_t(t))))

            taul_t(t) = taul_t(t) + damp*(taul_new - taul_t(t))
            pv_t(t)   = pv_t(t)   + damp*(pv_new   - pv_t(t))
            avg_t(t)  = avg_t(t)  + damp*((A_t(t)%labinc + A_t(t)%ss)/max(A_t(t)%pop,1.0e-12_dp) - avg_t(t))
            med_t(t)  = med_t(t)  + damp*(A_t(t)%med - med_t(t))
            H_t(t)    = H_t(t)    + damp*(A_t(t)%homeless/max(A_t(t)%pop,1.0e-12_dp) - H_t(t))
            HD_t(t)   = HD_t(t)   + damp*(A_t(t)%hl_sud /max(A_t(t)%pop,1.0e-12_dp) - HD_t(t))
        end do

        if (verbose) write(*,'(A,I3,A,ES11.3,A,F8.4,A,F8.4)') &
            '  path iter ', it, '   err = ', err, &
            '   tau_l(1) = ', taul_t(1), '   tau_l(T) = ', taul_t(T_path)

        if (err < tol) then
            if (verbose) write(*,'(A,I0,A)') '  path converged in ', it, ' iterations'
            return
        end if
    end do

    if (verbose) write(*,'(A)') '  WARNING: transition path did not converge'
end subroutine solve_path


!-- report the path of the objects the paper cares about ---------------------
subroutine print_path(A_t, every)
    type(agg_t), intent(in) :: A_t(T_path)
    integer,     intent(in) :: every
    integer :: t
    write(*,'(A)') ''
    write(*,'(A)') '  ================== transition path =================='
    write(*,'(A)') '    t   homeless%    SUD%   users%   unemp%    tau_l     p_v'
    do t = 1, T_path, every
        write(*,'(I5,4F9.3,2F9.4)') t, &
            100.0_dp*A_t(t)%homeless/max(A_t(t)%pop,1.0e-12_dp), &
            100.0_dp*A_t(t)%sud     /max(A_t(t)%pop,1.0e-12_dp), &
            100.0_dp*A_t(t)%users   /max(A_t(t)%pop,1.0e-12_dp), &
            100.0_dp*A_t(t)%unemp   /max(A_t(t)%pop,1.0e-12_dp), &
            taul_t(t), pv_t(t)
    end do
    write(*,'(A)') '  ===================================================='
end subroutine print_path

end module transition
