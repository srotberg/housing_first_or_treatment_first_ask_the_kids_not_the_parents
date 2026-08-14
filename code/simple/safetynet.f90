!===============================================================================
! safetynet.f90 -- insurance against moral hazard, with an addiction margin.
!
! THE QUESTION
!
! Referee 3's M2c asks: if drug use is rational and forward looking, where is
! the market failure that justifies intervention? Taken to its conclusion the
! implicit position is that households internalise their own costs, so the
! supports are unnecessary and the economy would be better without them.
!
! That misses what the benchmark already contains. This economy HAS a safety
! net: vouchers, food stamps, disability. Homelessness is not an unmanaged risk
! here, it is a partially insured one, and the insurance is redistribution from
! the taxed to the destitute. The referee's position is therefore a testable
! claim about that existing net, not an abstract point about rationality, and
! this experiment tests it.
!
! THE TRADE OFF, AND WHY THIS MODEL SAYS SOMETHING NEW ABOUT IT
!
! The classic trade off is insurance against moral hazard, and the classic moral
! hazard margin is consumption smoothing: insured households save less and work
! less. This model has a second margin. Cushioning the downside of homelessness
! also cushions the downside of ADDICTION, because homelessness is the state
! addiction leads to. So the net subsidises the risk of using.
!
! That margin is worse than the savings one for a specific reason: it is
! PERSISTENT and SELF REINFORCING. Under saving less, one bad year is one bad
! year. Under using more, the household acquires a state that lowers income,
! raises mortality, raises the chance of homelessness, and feeds back into
! further use. A one period distortion becomes a trap.
!
! THE DESIGN
!
!   arm 0  benchmark
!   arm 1  no vouchers                    prob_V = 0
!   arm 2  no food stamps                 cfloor_share ~ 0
!   arm 3  no safety net at all           both, and no disability
!   arm 4  arm 3 with the DRUG CHOICE FROZEN at its benchmark schedule
!
! Arm 4 is the one that isolates the paper's contribution. Comparing arm 3 with
! arm 4 gives the part of the response that runs through the addiction margin
! specifically, because arm 4 removes the net while forbidding the household to
! change whether it uses. Everything else -- assets, housing, hours, treatment --
! still re-optimises in both. The difference is the amplification.
!
! Welfare is newborn consumption equivalent variation, computed against the
! benchmark, so insurance and moral hazard are measured in one unit and the sign
! of the total answers the referee directly.
!===============================================================================
module safetynet
    use params
    use solve
    use equilibrium
    use calibrate
    use welfare
    implicit none

    integer, parameter :: NARM = 5
    character(len=38), parameter :: arm_name(NARM) = &
        [ character(len=38) :: &
          'benchmark                             ', &
          'no vouchers                           ', &
          'no food stamps                        ', &
          'no safety net                         ', &
          'no safety net, drug choice FROZEN     ' ]

contains

subroutine run_safety_net(verbose)
    logical, intent(in) :: verbose
    type(agg_t) :: A
    real(dp) :: w0, w(NARM), cev_arm(NARM)
    real(dp) :: hl(NARM), part(NARM), sud(NARM), taul(NARM), pv(NARM), hrs(NARM)
    real(dp) :: pV0, cf0, di0
    integer  :: k

    pV0 = prob_V; cf0 = cfloor_share; di0 = di_coverage

    do k = 1, NARM
        prob_V = pV0; cfloor_share = cf0; di_coverage = di0
        freeze_drug = 0

        select case (k)
        case (2); prob_V = 0.0_dp
        case (3); cfloor_share = 1.0e-4_dp
        case (4); prob_V = 0.0_dp; cfloor_share = 1.0e-4_dp; di_coverage = 0.0_dp
        case (5); prob_V = 0.0_dp; cfloor_share = 1.0e-4_dp; di_coverage = 0.0_dp
                  freeze_drug = 1
        end select

        call refresh_utility_constants()
        call solve_equilibrium(40, 1.0e-4_dp, .false.)
        call compute_aggregates(A)

        ! the benchmark's policies are the reference for the CEV and the frozen
        ! arm, so they are stored before anything is switched off
        if (k == 1) then
            pol_regb = pol_reg
            pol_lb   = pol_l
            w0       = newborn_value()
        end if

        w(k)    = newborn_value()
        hl(k)   = 100.0_dp*A%homeless/max(A%pop,1.0e-12_dp)
        part(k) = 100.0_dp*A%users   /max(A%pop,1.0e-12_dp)
        sud(k)  = 100.0_dp*A%sud     /max(A%pop,1.0e-12_dp)
        taul(k) = tau_l
        pv(k)   = p_v
    end do

    ! restore, then price every arm against the BENCHMARK policies
    prob_V = pV0; cfloor_share = cf0; di_coverage = di0; freeze_drug = 0
    call refresh_utility_constants()
    call solve_equilibrium(40, 1.0e-4_dp, .false.)
    do k = 1, NARM
        cev_arm(k) = cev(w(k), w0)
    end do

    if (.not. verbose) return

    write(*,'(A)') ''
    write(*,'(A)') '  ================= the safety net: insurance vs moral hazard ================='
    write(*,'(A)') '   R3 M2c asks where the market failure is if use is rational. The benchmark'
    write(*,'(A)') '   already insures homelessness, so the question is testable: remove the net.'
    write(*,'(A)') '  ---------------------------------------------------------------------------'
    write(*,'(A)') '   arm                                    homeless%  use%   SUD%   tau_l   CEV%'
    do k = 1, NARM
        write(*,'(A,A,F9.3,F7.3,F7.3,F8.4,F8.3)') '   ', arm_name(k), &
            hl(k), part(k), sud(k), taul(k), 100.0_dp*cev_arm(k)
    end do
    write(*,'(A)') '  ---------------------------------------------------------------------------'
    write(*,'(A,F8.3,A)') '   moral hazard, TOTAL   (arm 3 use  - benchmark use)  : ', &
        part(4)-part(1), ' pp'
    write(*,'(A,F8.3,A)') '   of which ADDICTION margin (arm 3 - arm 4)           : ', &
        part(4)-part(5), ' pp'
    write(*,'(A,F8.3,A)') '   welfare cost of removing the net (arm 3 CEV)        : ', &
        100.0_dp*cev_arm(4), ' %'
    write(*,'(A,F8.3,A)') '   the same with the addiction margin shut (arm 4 CEV) : ', &
        100.0_dp*cev_arm(5), ' %'
    write(*,'(A)') '   A NEGATIVE arm 3 CEV says the net raises welfare on net, which answers'
    write(*,'(A)') '   R3: the insurance beats the moral hazard even with use fully rational.'
    write(*,'(A)') '   The arm 3 minus arm 4 gap is how much of the moral hazard runs through'
    write(*,'(A)') '   addiction rather than through ordinary consumption smoothing.'
    write(*,'(A)') '  ==========================================================================='
end subroutine run_safety_net

end module safetynet
