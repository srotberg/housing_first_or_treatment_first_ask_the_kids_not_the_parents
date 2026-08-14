!===============================================================================
! main.f90 -- solve one stationary equilibrium and report.
!===============================================================================
program main
    use params
    use solve
    use equilibrium
    !$ use omp_lib
    implicit none

    real(dp)    :: t0, t1
    integer     :: nthreads
    type(agg_t) :: A

    nthreads = 1
    !$ nthreads = omp_get_max_threads()

    call setup_grids()
    call alloc_all()
    call alloc_solve()

    write(*,'(A)') '======================================================'
    write(*,'(A)') ' Simplified HF/TF model -- stationary equilibrium'
    write(*,'(A)') '======================================================'
    write(*,'(A,I0)') ' threads             : ', nthreads
    write(*,'(A,I0)') ' states per age      : ', NA*NY*NE*ND*NV
    write(*,'(A,I0)') ' Bellman evaluations : ', NA*NY*NE*ND*NV*n_age*NH*NREG*2*NA
    write(*,'(A)') ''

    call wall(t0)

    ! one solve at p_v = 1 pins the drug-supply shifter, so the benchmark keeps
    ! the p_v = 1 normalisation and only counterfactuals move the price
    call normalise_drug_supply()

    call solve_equilibrium(80, 1.0e-4_dp, .true.)
    call compute_aggregates(A)

    call wall(t1)

    call report(A)
    write(*,'(A,F10.3,A)') ' total wall time      : ', t1-t0, ' s'

contains

subroutine wall(t)
    real(dp), intent(out) :: t
    integer :: cnt, rate
    call system_clock(cnt, rate)
    t = real(cnt,dp)/real(rate,dp)
end subroutine wall

subroutine report(A)
    type(agg_t), intent(in) :: A
    real(dp) :: p
    p = max(A%pop, 1.0e-12_dp)
    write(*,'(A)') ''
    write(*,'(A)') '------------------ aggregates ----------------'
    write(*,'(A,F10.4,A)') ' homelessness rate    : ', 100.0_dp*A%homeless/p, ' %'
    write(*,'(A,F10.4,A)') ' SUD rate             : ', 100.0_dp*A%sud/p,      ' %'
    write(*,'(A,F10.4,A)') ' drug participation   : ', 100.0_dp*A%users/p,    ' %'
    write(*,'(A,F10.4,A)') ' unemployment rate    : ', 100.0_dp*A%unemp/p,    ' %'
    write(*,'(A,F10.4,A)') ' in treatment         : ', 100.0_dp*A%treated/p,  ' %'
    write(*,'(A)') ''
    write(*,'(A,F10.5)')   ' drug price p_v       : ', p_v
    write(*,'(A,F10.5)')   ' tax level tau_l      : ', tau_l
    write(*,'(A,F10.5)')   ' bequest per capita   : ', bequest
    write(*,'(A,F10.5)')   ' average income       : ', avg_income
    write(*,'(A)') ''
    write(*,'(A,F10.5)')   ' govt outlay / labinc : ', A%govt_outlay/max(A%labinc,1.0e-12_dp)
    write(*,'(A,F10.5)')   ' voucher cost / labinc: ', A%vouchers/max(A%labinc,1.0e-12_dp)
    write(*,'(A,F10.5)')   ' newborn welfare      : ', newborn_welfare()
    write(*,'(A)') '----------------------------------------------'
end subroutine report

end program main
