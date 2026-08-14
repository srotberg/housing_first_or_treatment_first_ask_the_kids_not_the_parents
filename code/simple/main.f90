!===============================================================================
! main.f90 -- driver: solve, simulate the stationary distribution, report,
!             and time the whole thing.
!===============================================================================
program main
    use params
    use solve
    !$ use omp_lib
    implicit none

    real(dp) :: t0, t1, t_solve, t_dist
    integer  :: nthreads

    nthreads = 1
    !$ nthreads = omp_get_max_threads()

    call setup_grids()
    call alloc_all()
    call alloc_solve()

    write(*,'(A)') '======================================================'
    write(*,'(A)') ' Simplified HF/TF model'
    write(*,'(A)') '======================================================'
    write(*,'(A,I0)')    ' threads              : ', nthreads
    write(*,'(A,I0)')    ' states per age       : ', NA*NY*NE*ND*NV
    write(*,'(A,I0)')    ' total states         : ', NA*NY*NE*ND*NV*n_age
    write(*,'(A,I0)')    ' choices per state    : ', NH*NREG*2*NA
    write(*,'(A,I0)')    ' Bellman evaluations  : ', NA*NY*NE*ND*NV*n_age*NH*NREG*2*NA
    write(*,'(A)') ''

    call cpu_wall(t0)
    call solve_household()
    call cpu_wall(t1)
    t_solve = t1 - t0

    call cpu_wall(t0)
    call build_distribution()
    call cpu_wall(t1)
    t_dist = t1 - t0

    call report()

    write(*,'(A)') ''
    write(*,'(A)') '------------------- timing -------------------'
    write(*,'(A,F10.3,A)') ' household solve      : ', t_solve, ' s'
    write(*,'(A,F10.3,A)') ' distribution         : ', t_dist,  ' s'
    write(*,'(A,F10.3,A)') ' TOTAL per equilibrium: ', t_solve+t_dist, ' s'
    write(*,'(A)') '----------------------------------------------'

contains

subroutine cpu_wall(t)
    real(dp), intent(out) :: t
    integer :: cnt, rate
    call system_clock(cnt, rate)
    t = real(cnt,dp)/real(rate,dp)
end subroutine cpu_wall


!-- push the newborn cohort forward through the policy functions -------------
subroutine build_distribution()
    integer :: j, ia, iy, ie, id, iv
    integer :: iap, ihp, ireg, itr, iyp, iep, idp, ivp, ielig
    real(dp) :: m, phi, pfind, psep, prec, paddict
    real(dp) :: s_e(NE), s_d(ND), s_eta(NV)
    real(dp) :: ygross

    dist = 0.0_dp
    ! newborns: no assets, ergodic productivity, employed, clean, homeless-entry,
    ! no voucher -- matching the original model's initialisation
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
end subroutine build_distribution


subroutine report()
    integer :: j, ia, iy, ie, id, iv
    real(dp) :: pop, homeless, sud, users, unemp, m, vouchers, drugq, treated

    pop = 0.0_dp; homeless = 0.0_dp; sud = 0.0_dp
    users = 0.0_dp; unemp = 0.0_dp; vouchers = 0.0_dp
    drugq = 0.0_dp; treated = 0.0_dp

    do j = 1, n_age
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,j)
        if (m <= 0.0_dp) cycle
        pop = pop + m
        ! homelessness is the CHOSEN unit, not a state
        if (pol_h(ia,iy,ie,id,iv,j) == 1) homeless = homeless + m
        if (id == 2) sud = sud + m
        if (ie == 1 .and. j < j_ret) unemp = unemp + m
        if (iv == 2) vouchers = vouchers + m
        if (pol_tr(ia,iy,ie,id,iv,j) == 1) treated = treated + m
        if (pol_v(ia,iy,ie,id,iv,j) > 0.0_dp) then
            users = users + m
            drugq = drugq + m*pol_v(ia,iy,ie,id,iv,j)
        end if
    end do
    end do
    end do
    end do
    end do
    end do

    if (pop <= 0.0_dp) pop = 1.0_dp

    write(*,'(A)') '------------------ aggregates ----------------'
    write(*,'(A,F10.5)')   ' population (mass)    : ', pop
    write(*,'(A,F10.4,A)') ' homelessness rate    : ', 100.0_dp*homeless/pop, ' %'
    write(*,'(A,F10.4,A)') ' SUD rate             : ', 100.0_dp*sud/pop, ' %'
    write(*,'(A,F10.4,A)') ' drug participation   : ', 100.0_dp*users/pop, ' %'
    write(*,'(A,F10.4,A)') ' unemployment rate    : ', 100.0_dp*unemp/pop, ' %'
    write(*,'(A,F10.4,A)') ' voucher holders      : ', 100.0_dp*vouchers/pop, ' %'
    write(*,'(A,F10.4,A)') ' in treatment         : ', 100.0_dp*treated/pop, ' %'
    write(*,'(A,F10.5)')   ' aggregate drug demand: ', drugq
    write(*,'(A)') '----------------------------------------------'
end subroutine report

end program main
