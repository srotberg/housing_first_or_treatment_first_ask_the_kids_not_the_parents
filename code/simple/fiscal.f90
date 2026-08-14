!===============================================================================
! fiscal.f90 -- the FISCAL externality of substance use disorder, decomposed.
!
! R3's M2c is the sharpest question in any of the reports: since drug use is
! rational and forward-looking, where do the externalities justifying
! intervention arise? The answer has four parts, three of them fiscal and
! already inside the model but never reported:
!
!   1. Households with SUD work less and pay less tax.
!   2. They are likelier to be voucher-eligible and to receive one.
!   3. SUD raises homelessness, which raises the direct fiscal cost AND makes
!      work harder to find and easier to lose (kappa_ue_H = 0.80, Desmond and
!      Gershenson 2016), which feeds back into 1; and early death truncates the
!      whole stream of future revenue.
!   4. The disamenity, which is not fiscal -- see kappa_ext_from_wtp in
!      experiment.f90.
!
! Channel 3 compounds: SUD -> homelessness -> unemployment -> less tax, on top
! of the direct costs. It is separated below by re-evaluating the SUD stream
! with homelessness carrying NO employment penalty.
!
! Points 1-3 are MEASURED here rather than assumed. Define the expected present
! discounted value of a household's net contribution to the government,
!
!   N_j(s) = taxes_j(s) - transfers_j(s) - chi_H*1{homeless} - chi_D*1{SUD}
!            + phi_j(s) / (1+r) * E[ N_{j+1}(s') ],
!
! discounted at the government's rate. Given the benchmark policy functions this
! is a LINEAR recursion, so it costs one backward pass and no optimisation. Four
! components are carried separately so the difference can be decomposed.
!
! The externality of one more case of SUD is then
!
!   E[ N(a,y,e,d=0,m,eta) ] - E[ N(a,y,e,d=1,m,eta) ]
!
! over the benchmark distribution of clean households: what one additional
! addiction costs everybody else, in present value, holding everything else at
! that household's own state.
!
! The mortality channel is separated by recomputing the SUD stream with CLEAN
! survival probabilities. The gap between the two is what early death alone
! contributes, which is the third of the user's channels and the one that is
! easiest to overlook because it works by shortening the stream rather than by
! changing any flow.
!===============================================================================
module fiscal
    use params
    use solve
    use equilibrium
    implicit none

    integer, parameter :: NCOMP = 4     ! taxes, vouchers, other transfers, chi
    character(len=26), parameter :: comp_name(NCOMP) = &
        [ character(len=26) :: 'labour and capital taxes  ', &
                               'housing vouchers          ', &
                               'other transfers (SS/UI/DI/SNAP)', &
                               'direct costs chi_H, chi_D ' ]

contains

!-- present value of each fiscal component, by state and age -----------------
! mode 0  as the model is
! mode 1  survival evaluated as if clean      -> isolates EARLY DEATH
! mode 2  homelessness carries no employment penalty
!                                             -> isolates HOMELESSNESS -> WORK
subroutine fiscal_pv(N, mode)
    real(dp), intent(out) :: N(NA,NY,NE,ND,NV,NM,n_age+1,NCOMP)
    integer,  intent(in)  :: mode
    integer  :: ih_emp
    integer  :: j, ia, iy, ie, id, iv, im, k
    integer  :: iap, ihp, ireg, itr, iyp, iep, idp, ivp, imp, ielig
    real(dp) :: ygross, capinc, phi, food_j, vouch, hours, disc
    real(dp) :: s_e(NE), s_d(ND), s_eta(NV), prec, paddict, cont(NCOMP)
    real(dp) :: cfloor

    cfloor = cfloor_share*avg_income
    disc   = 1.0_dp/(1.0_dp + r_free)
    N(:,:,:,:,:,:,n_age+1,:) = 0.0_dp

    do j = n_age, 1, -1
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
    do ie = 1, NE
    do iy = 1, NY
    do ia = 1, NA
        iap  = pol_a(ia,iy,ie,id,iv,im,j)
        ihp  = pol_h(ia,iy,ie,id,iv,im,j)
        ireg = pol_reg(ia,iy,ie,id,iv,im,j)
        itr  = pol_tr(ia,iy,ie,id,iv,im,j)
        hours  = hours_of(j, ie, pol_l(ia,iy,ie,id,iv,im,j))
        ygross = income_gross(j, iy, ie, id, im, hours)
        capinc = r_free*a_grid(ia)

        ! survival: optionally evaluated as if the household were clean, which
        ! isolates how much of the fiscal gap is early death alone
        if (mode == 1) then
            phi = survival(j, ihp, 1, im)
        else
            phi = survival(j, ihp, id, im)
        end if

        ! employment transitions: mode 2 evaluates them as if the household
        ! were housed, so the gap is the homelessness-to-unemployment link
        ih_emp = ihp
        if (mode == 2 .and. ihp == 1) ih_emp = 2

        food_j = max(0.0_dp, cfloor - (ygross + max(0.0_dp, capinc)))
        vouch  = 0.0_dp
        if (ihp > 1 .and. iv == 2) &
            vouch = max(0.0_dp, p_rent*h_grid(ihp) - kappa_r*ygross)

        !-- this period's flow, by component ---------------------------------
        ! 1: taxes paid
        N(ia,iy,ie,id,iv,im,j,1) = ygross - tau_l*max(ygross,1.0e-10_dp)**xi_tax &
                                 + tau_k*max(0.0_dp, capinc)
        ! 2: voucher outlay
        N(ia,iy,ie,id,iv,im,j,2) = -vouch
        ! 3: other transfers
        if (j >= j_ret) then
            N(ia,iy,ie,id,iv,im,j,3) = -ygross - food_j     ! social security
        else if (ie == 2) then
            N(ia,iy,ie,id,iv,im,j,3) = -ygross - food_j     ! UI
        else if (ie == 3 .and. im == 2 .and. include_disability == 1) then
            N(ia,iy,ie,id,iv,im,j,3) = -ygross - food_j     ! disability
        else
            N(ia,iy,ie,id,iv,im,j,3) = -food_j
        end if
        ! 4: direct programme costs
        N(ia,iy,ie,id,iv,im,j,4) = 0.0_dp
        if (ihp == 1) N(ia,iy,ie,id,iv,im,j,4) = N(ia,iy,ie,id,iv,im,j,4) - chi_H
        if (id  == 2) N(ia,iy,ie,id,iv,im,j,4) = N(ia,iy,ie,id,iv,im,j,4) - chi_D

        !-- continuation ------------------------------------------------------
        if (ygross + max(0.0_dp, capinc) < kappa_V*median_income) then
            ielig = 1
        else
            ielig = 0
        end if
        call emp_trans(ie, ih_emp, id, im, s_e)
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

        cont = 0.0_dp
        do iyp = 1, NY
            if (y_trans(iy,iyp) <= 0.0_dp) cycle
            do iep = 1, NE
                if (s_e(iep) <= 0.0_dp) cycle
                do idp = 1, ND
                    if (s_d(idp) <= 0.0_dp) cycle
                    do ivp = 1, NV
                        if (s_eta(ivp) <= 0.0_dp) cycle
                        do imp = 1, NM
                            if (mh_trans(im,imp) <= 0.0_dp) cycle
                            do k = 1, NCOMP
                                cont(k) = cont(k) + y_trans(iy,iyp)*s_e(iep) &
                                    *s_d(idp)*s_eta(ivp)*mh_trans(im,imp) &
                                    *N(iap,iyp,iep,idp,ivp,imp,j+1,k)
                            end do
                        end do
                    end do
                end do
            end do
        end do
        do k = 1, NCOMP
            N(ia,iy,ie,id,iv,im,j,k) = N(ia,iy,ie,id,iv,im,j,k) + disc*phi*cont(k)
        end do
    end do
    end do
    end do
    end do
    end do
    end do
    end do
end subroutine fiscal_pv


!-- the fiscal cost of one more case of SUD, decomposed ----------------------
subroutine report_fiscal_externality()
    real(dp), allocatable :: N(:,:,:,:,:,:,:,:), Nc(:,:,:,:,:,:,:,:)
    real(dp), allocatable :: Nh(:,:,:,:,:,:,:,:)
    integer  :: j, ia, iy, ie, id, iv, im, k
    real(dp) :: m, mass, clean(NCOMP), sud(NCOMP), sudc(NCOMP), sudh(NCOMP)
    real(dp) :: tot_clean, tot_sud, tot_sudc, tot_sudh

    allocate(N (NA,NY,NE,ND,NV,NM,n_age+1,NCOMP))
    allocate(Nc(NA,NY,NE,ND,NV,NM,n_age+1,NCOMP))
    allocate(Nh(NA,NY,NE,ND,NV,NM,n_age+1,NCOMP))
    call fiscal_pv(N,  0)
    call fiscal_pv(Nc, 1)
    call fiscal_pv(Nh, 2)

    clean = 0.0_dp; sud = 0.0_dp; sudc = 0.0_dp; sudh = 0.0_dp; mass = 0.0_dp
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        id = 1
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        mass = mass + m
        do k = 1, NCOMP
            clean(k) = clean(k) + m*N(ia,iy,ie,1,iv,im,j,k)
            sud(k)   = sud(k)   + m*N(ia,iy,ie,2,iv,im,j,k)
            sudc(k)  = sudc(k)  + m*Nc(ia,iy,ie,2,iv,im,j,k)
            sudh(k)  = sudh(k)  + m*Nh(ia,iy,ie,2,iv,im,j,k)
        end do
    end do; end do; end do
    end do; end do
    end do

    clean = clean/max(mass,1.0e-12_dp)
    sud   = sud  /max(mass,1.0e-12_dp)
    sudc  = sudc /max(mass,1.0e-12_dp)
    sudh  = sudh /max(mass,1.0e-12_dp)
    tot_clean = sum(clean); tot_sud = sum(sud)
    tot_sudc  = sum(sudc);  tot_sudh = sum(sudh)

    write(*,'(A)') ''
    write(*,'(A)') '  =========== the FISCAL externality of one more case of SUD ==========='
    write(*,'(A)') '  Present value of net contribution to the government, per household,'
    write(*,'(A)') '  in units of average income, over the benchmark distribution of clean'
    write(*,'(A)') '  households -- the same household, counterfactually with and without SUD.'
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A)') '   component                          clean       SUD    cost of SUD'
    do k = 1, NCOMP
        write(*,'(A,A,3F11.4)') '   ', comp_name(k), clean(k), sud(k), clean(k)-sud(k)
    end do
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A,3F11.4)') '   TOTAL                            ', tot_clean, tot_sud, &
        tot_clean - tot_sud
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A,F11.4)') '   of which EARLY DEATH alone       : ', tot_sudc - tot_sud
    write(*,'(A)') '     (SUD flows at CLEAN survival: the gap is purely the truncation'
    write(*,'(A)') '      of the revenue stream)'
    write(*,'(A,F11.4)') '   of which HOMELESSNESS -> WORK     : ', tot_sudh - tot_sud
    write(*,'(A)') '     (homelessness carrying no employment penalty: the gap is the'
    write(*,'(A)') '      compounding through kappa_ue_H, Desmond and Gershenson 2016)'
    write(*,'(A,F11.4)') '   remainder (direct + take-up)     : ', &
        (tot_clean - tot_sud) - (tot_sudc - tot_sud) - (tot_sudh - tot_sud)
    write(*,'(A)') '  ======================================================================'

    !-- what it is worth, in consumption ----------------------------------
    ! The fiscal loss has to be financed by somebody. Divided across the
    ! population and expressed against average consumption it is directly
    ! comparable with the disamenity, which is the only way a reader can see
    ! which channel actually matters.
    call report_welfare_units(tot_clean - tot_sud)

    deallocate(N, Nc, Nh)
end subroutine report_fiscal_externality


!-- every externality in one currency: share of average annual consumption ---
subroutine report_welfare_units(pv_per_case)
    real(dp), intent(in) :: pv_per_case
    integer  :: j, ia, iy, ie, id, iv, im, ihp
    real(dp) :: m, mass, cons, sudmass, H, HD, flow_per_case
    real(dp) :: fisc_pc, disam_pc, cbar

    mass=0; cons=0; sudmass=0; H=0; HD=0
    do j = 1, n_age
    do im = 1, NM; do iv = 1, NV; do id = 1, ND
    do ie = 1, NE; do iy = 1, NY; do ia = 1, NA
        m = dist(ia,iy,ie,id,iv,im,j)
        if (m <= 0.0_dp) cycle
        mass = mass + m
        cons = cons + m*pol_c(ia,iy,ie,id,iv,im,j)
        if (id == 2) sudmass = sudmass + m
        ihp = pol_h(ia,iy,ie,id,iv,im,j)
        if (ihp == 1) then
            H = H + m
            if (id == 2) HD = HD + m
        end if
    end do; end do; end do
    end do; end do; end do
    end do

    cbar    = cons/max(mass,1.0e-12_dp)
    H       = H  /max(mass,1.0e-12_dp)
    HD      = HD /max(mass,1.0e-12_dp)
    sudmass = sudmass/max(mass,1.0e-12_dp)

    ! annuitise the present value at the government's discount rate, so the
    ! fiscal cost of a case is expressed as a permanent flow
    flow_per_case = pv_per_case * r_free/(1.0_dp + r_free)
    fisc_pc  = flow_per_case*sudmass          ! spread over the whole population
    disam_pc = kappa_ext*(H + omega_ext*HD)   ! utils, converted below

    write(*,'(A)') ''
    write(*,'(A)') '  ============== every externality in the same currency ================'
    write(*,'(A)') '  Per head of population, per year, as a share of average consumption.'
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A,F9.3,A)') '   SUD rate                                     : ', &
        100.0_dp*sudmass, ' %'
    write(*,'(A,F9.3,A)') '   homelessness rate                            : ', &
        100.0_dp*H, ' %'
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A,F11.4)') '   fiscal cost per CASE of SUD, present value    : ', pv_per_case
    write(*,'(A,F11.4)') '     annuitised                                 : ', flow_per_case
    write(*,'(A,F9.3,A)') '   FISCAL externality, per capita               : ', &
        100.0_dp*fisc_pc/max(cbar,1.0e-12_dp), ' % of average consumption'
    write(*,'(A,F9.3,A)') '   DISAMENITY, per capita                       : ', &
        100.0_dp*wtp_end_homelessness, ' % of income (contingent valuation)'
    write(*,'(A)') '  ----------------------------------------------------------------------'
    write(*,'(A)') '   Read the two together: the fiscal channel is measured inside the'
    write(*,'(A)') '   model and needs no free parameter; the disamenity rests on a stated'
    write(*,'(A)') '   preference number and is reported as a bounded sensitivity.'
    write(*,'(A)') '  ======================================================================'
end subroutine report_welfare_units

end module fiscal
