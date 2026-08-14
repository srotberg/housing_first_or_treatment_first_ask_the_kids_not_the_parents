!===============================================================================
! check_hours.f90 -- validate the continuous labour-supply solver.
!
! The FOC solver is only worth anything if the hours it returns really are the
! argmax. So for a sample of states, redo the household problem by BRUTE FORCE:
! scan hours on a very fine grid, evaluate the identical objective, and compare
! the best value found that way with what solve_household reports.
!
! A fine grid cannot beat the FOC by more than the grid's own resolution error,
! so `brute - foc` should be <= 0 up to rounding. A POSITIVE vgap means the FOC
! solver missed a local optimum -- which is exactly what a single bisection on
! [0,1] does when the food-stamp clawback splits the objective in two.
!===============================================================================
program check_hours
    use params
    use solve
    use equilibrium
    use calibrate
    implicit none

    integer, parameter :: NHG = 4001          ! brute-force hours grid
    integer :: j, ia, iy, ie, id, iv, im
    integer :: ihp, ireg, itr, iap, ielig, ig, nbad, ntot
    real(dp) :: cfloor, phi, w, base, vcap, cfl_net, cost_tr, acost
    real(dp) :: hours, res, dres, Rres, Rt, vv, cc, val, brute, bh
    real(dp) :: worst, vgap, bb, hgap
    integer  :: seedstep

    call setup_grids(); call alloc_all(); call alloc_solve(); call init_targets()
    call refresh_utility_constants()
    call solve_household()

    cfloor = cfloor_share * avg_income
    worst  = 0.0_dp; nbad = 0; ntot = 0; hgap = 0.0_dp
    seedstep = 7

    ! a spread-out sample of working-age employed states, where hours bind.
    ! NB: EV is a single table overwritten once per age inside solve_household,
    ! so it must be REBUILT for the age under test -- V(:,...,j+1) survives, so
    ! this reproduces exactly the table the solve used at that age.
    do j = 2, j_ret-1, 6
    call build_EV(j)
    do im = 1, NM
    do iv = 1, NV
    do id = 1, ND
        ie = 1
        do iy = 1, NY, 2
        do ia = 1, NA, seedstep

            w       = wage_rate(j, iy, id, im)
            cfl_net = cfloor - max(0.0_dp, r_free*a_grid(ia))

            brute = -1.0e13_dp; bh = 0.0_dp
            do ihp = 1, NH
                phi = survival(j, ihp, id, im)
                bb  = b_of(id, im, ihp)
                if (ihp > 1 .and. iv == 2) then
                    vcap = p_rent*h_grid(ihp)
                else
                    vcap = 0.0_dp
                end if
                base = a_grid(ia) + bequest + r_free*a_grid(ia)
                if (ihp > 1) base = base - p_rent*h_grid(ihp)

                do itr = 0, 1
                    if (itr == 1 .and. (id == 1 .or. allow_treatment == 0)) cycle
                    cost_tr = 0.0_dp
                    if (itr == 1) cost_tr = treat_ucost      ! utility cost
                    do ireg = 1, NREG
                        if (id == 1 .and. j > j_exp .and. ireg > 1) cycle
                        do iap = 1, NA
                            acost = a_grid(iap)
                            do ig = 1, NHG
                                hours = real(ig-1,dp)/real(NHG-1,dp)
                                call res_slope(hours, w, base, vcap, cfl_net, res, dres)
                                Rres = res - acost
                                if (Rres <= 0.0_dp) cycle
                                if (hours*w + max(0.0_dp,r_free*a_grid(ia)) &
                                    < kappa_V*median_income) then
                                    ielig = 1
                                else
                                    ielig = 0
                                end if
                                Rt = Rres + p_v*bb
                                if (ireg == 1) then
                                    vv = 0.0_dp
                                else
                                    vv = max(gamma_u/(alpha_u+gamma_u)*Rt/p_v - bb, &
                                             1.0e-8_dp)
                                end if
                                cc = Rres - p_v*vv
                                if (cc <= 0.0_dp) cycle
                                val = util(cc, h_pow(ihp), vv, bb, 1.0_dp-hours) &
                                    - cost_tr &
                                    + beta*phi*EV(iap,ihp,iy,ie,id,ireg,itr,ielig,iv,im)
                                if (val > brute) then
                                    brute = val; bh = hours
                                end if
                            end do
                        end do
                    end do
                end do
            end do

            ntot = ntot + 1
            vgap  = brute - V(ia,iy,ie,id,iv,im,j)
            if (vgap > 1.0e-7_dp) then
                nbad = nbad + 1
                if (vgap > worst) then
                    worst = vgap
                    hgap  = bh - pol_l(ia,iy,ie,id,iv,im,j)
                end if
            end if

        end do
        end do
    end do
    end do
    end do
    end do

    write(*,'(A)') ''
    write(*,'(A)') ' continuous labour supply: FOC solver vs brute-force hours grid'
    write(*,'(A,I6)')    '   states checked            : ', ntot
    write(*,'(A,I6,A)')  '   brute force strictly better: ', nbad, &
                         '   (should be 0)'
    write(*,'(A,ES12.4)')'   worst value vgap           : ', worst
    write(*,'(A,ES12.4)')'   hours vgap at the worst    : ', hgap
    write(*,'(A)') '   (a 4001-point grid resolves hours to 2.5e-4, so a value gap'
    write(*,'(A)') '    below ~1e-6 is the grid''s own error, not a solver failure)'
    ! NOTE: the brute force uses a 4001-point grid, so a vgap below ~1e-6 is the
    ! grid's own resolution, not a solver failure.
end program check_hours
