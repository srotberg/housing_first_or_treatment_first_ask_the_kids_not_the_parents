# Bounds-checked run, unsecured borrowing ON at limit 0.30

One diagnostic run of the model under `-fcheck=bounds,pointer`. Not a
calibration point, and no moment from it is a measurement of anything: the run
did not finish, it aborted on the first bounds violation, which is the finding.

**A violation fired.** The model died inside
`stationary_equilibrium_wealth_distribution_of_old` on the first calibration
solve, 587 seconds (9 min 47 s) in, reading `distribution_stationary(0)` on an
array whose lower bound is 1. Nothing has been fixed and nothing in the Fortran
has been touched.

## What was run

Source: `code/housing_first_or_treatment_first_SR_v1.f90` at repository HEAD
`6750c46`.

    semantic hash   17529c7177          (python3 code/model_hash.py ...)
    md5             c8233314494563be154fd6f6864decfa
    compiler        GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0

Build command, run in `code/`:

    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -fimplicit-none -O1 -ffree-line-length-none -g -fbacktrace \
        -fcheck=bounds,pointer -o hftf_bounds

`run_one_point.sh` was deliberately NOT used: it builds `-O3 -funroll-loops`
with no checks and would have measured nothing. The parameter handover it
performs was reproduced by hand instead -- `calibration_state.dat` and
`calibration_distribution*.dat` deleted, `B_SWEEP_GRID.txt` written with
`addiction_scalar_1`, `PARAM_HANDOVER.txt` written with the other 42 names --
from the script's own default block overridden by line 1 of
`code/batch_s2_00.txt`, the anchor with `include_unsecured_borrowing=1` and
`unsecured_borrowing_limit=0.30`. The model consumed all 42 handover lines
(`HANDOVER ...` echoes in the log) and reported

    DIAG unsecured borrowing limit, yrs of income   =  0.29999999999999999
    DIAG borrowing floor, model units                = -0.19117441177368164

so the configuration under test is the one intended. Run with
`OMP_NUM_THREADS=4 OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1`, `ulimit -s
unlimited`, stdout and stderr merged and captured unfiltered (246 MB, 5,059,650
lines; not committed).

## The violation, verbatim

Exactly one bounds violation appears in the output, because `-fcheck=bounds`
aborts on the first. Lines 5,059,637 onward of the log:

    At line 11791 of file housing_first_or_treatment_first_SR_v1.f90
    Fortran runtime error: Index '0' of dimension 1 of array 'distribution_stationary' below lower bound of 1

    Error termination. Backtrace:
    #0  0x150347623e59 in ???
    #1  0x150347624a71 in ???
    #2  0x150347625082 in ???
    #3  0x55e946aaee0e in stationary_equilibrium_wealth_distribution_of_old_
            at /home/user/housing_first_or_treatment_first/code/housing_first_or_treatment_first_SR_v1.f90:11791
    #4  0x55e946b23241 in calibrating_model_
            at /home/user/housing_first_or_treatment_first/code/housing_first_or_treatment_first_SR_v1.f90:36145
    #5  0x55e946b25e33 in main_program
            at /home/user/housing_first_or_treatment_first/code/housing_first_or_treatment_first_SR_v1.f90:7481
    #6  0x55e946b25e6c in main
            at /home/user/housing_first_or_treatment_first/code/housing_first_or_treatment_first_SR_v1.f90:7444

## What the source at line 11791 is doing

`housing_first_or_treatment_first_SR_v1.f90:11785-11793`, inside the do-while
that walks the old households' wealth distribution upward from the bottom:

    min_wealth=minval(wealth_matrix(time_period,:,:,:),mask=wealth_matrix(time_period,:,:,:)>&
        -housing_price(time_period)*housing_size(housing_status_grid_size-1))

    min_wealth_index=minloc(wealth_matrix(time_period,:,:,:),mask=wealth_matrix(time_period,:,:,:)>&
        -housing_price(time_period)*housing_size(housing_status_grid_size-1))

    sum_distribution_used=sum(distribution_stationary(min_wealth_index(3))%&
        vector_transition_real(time_period,life_span-retirement_span+1:life_span,min_wealth_index(1),:,:,&
        min_wealth_index(2)-2,:))

`distribution_stationary` is declared `dimension(1:2)` at line 4199.
`min_wealth_index` is `integer, dimension(3)` at line 4528, filled by `minloc`
over the rank-3 slice `wealth_matrix(time_period,:,:,:)`.

The mechanism is `minloc` over an all-false mask, which returns zero in every
component. Each pass of the do-while consumes the cell it just counted, by
writing the mask's own sentinel value back into it at lines 11820-11822:

    wealth_matrix(time_period,min_wealth_index(1),&
        min_wealth_index(2)-2,min_wealth_index(3))=&
        -housing_price(time_period)*housing_size(housing_status_grid_size-1)

and the mask is strictly `>` that value, so a counted cell is permanently
excluded. The loop's only exit is
`distance_pop_of_top_wealth_x_perc >= stopping_rule_wealth_dist_of_old`. If the
mass reachable through `wealth_matrix` cannot reach the stopping rule, the loop
consumes every cell, the mask goes all-false, and `min_wealth_index` becomes
`(0,0,0)`. `distribution_stationary(0)` is then below the declared lower bound
of 1, which is what fired.

Two further indices in that same expression go out of range on the same
iteration and were not reached only because the array selection is evaluated
first: `min_wealth_index(1)` is 0 against a lower bound of 1 (or of
`renter_array_floor`), and `min_wealth_index(2)-2` is **-2** against a lower
bound of `lowest_housing_grid_point = -1`. The write-back at 11820 has the same
`-2`.

This exact failure is described in the comment block at lines 11681-11695 of the
source -- "the loop consumes every cell in the array, `minloc` over an all-false
mask returns zero, and `min_wealth_index(2)-2` indexes at MINUS TWO" -- as
something the guard change recorded there was meant to close. It is still live,
and it fired on the FIRST pass through the routine (the string "begining wealth
distribution for old" appears exactly once in the whole log), not on the second
pass that comment is about. So the cause recorded there is not the cause here.

## What the run showed about why the mass falls short

Recorded as observation, not as a diagnosis, and no fix was attempted.

`wealth_matrix` is declared at lines 4506-4508 as

    real(8), dimension(transition_length,financial_grid_size,&
        lowest_housing_grid_point:housing_status_grid_size-1,1:max_amortization_years) :: &
        wealth_matrix,wealth_matrix_saved,wealth_matrix_gini

Its financial dimension therefore runs `1:financial_grid_size` and its fourth
dimension is `1:1`, because `max_amortization_years=1` (line 3422). The fill
loop at 11726-11762 walks `financial_index` from
`renter_floor_by_age(min(max(age_index,1),life_span))` and marks only cells
carrying positive mass. The divisor it is later compared against,
`sum_of_distribution_of_old` at 11713-11720, sums
`distribution_stationary(i)` for **i=1,2** over the same retirement ages, while
the fill loop indexes `distribution_stationary(years_left_on_mortgage_index)`
for `years_left_on_mortgage_index=1,max_amortization_years`, i.e. slot 1 only.
Anything held in slot 2 is in the denominator and unreachable in the numerator.

`renter_floor_by_age` (lines 11330-11346) is `negative_financial_grid_size`,
which is 4, except that with `include_unsecured_borrowing==1` ages
`1:life_span-1` are lowered to 1. `age_index` is not set inside this routine, so
which of those two floors the fill loop uses depends on what the previously
called routine left in it; at the floor of 4 the three deepest debt points of
the financial grid are never entered into `wealth_matrix` at all while their
mass stays in the divisor. This is the class the borrowing switch opens.

The economy this fired in has no homeowners. From the moments block immediately
preceding the abort:

    model_fraction_of_homeowners_with_mortgage(time_period)=   0.0000000000000000
    aggregate_housing_consumption=           1 =   0.0000000000000000
    model_average_rental_unit_size(time_period)/model_average_owner_occupied_unit_size(time_period)=   365106353437486.06
    model_total_income-model_total_expenditure=  -9.1187985036103818

## Compile-time bounds warnings

The same build emitted seven static out-of-bounds warnings, all in
`transition_simulation` (the subroutine beginning at line 39833). They are
recorded because they are the same class of defect found by the same flag, but
none of them was reached at run time: `transition_simulation` is called only
from line 7493 under `is_counterfactual==1 .AND. solve_transition_dynamics==1`,
and both are compile-time parameters set to 0 (`is_counterfactual` at line 5,
`solve_transition_dynamics` at line 1528), which is also
why they are out of bounds as compiled -- `transition_length` collapses to 1
(line 1530) and the transition arrays become rank-1 of extent 1.

    :39981:26:  housing_price(transition_length-25:transition_length-1)=housing_price(transition_length)
                Warning: Lower array reference at (1) is out of bounds (-24 < 1) in dimension 1
    :40002:30:  lump_sum_transfer(transition_length-25:transition_Length-1)=lump_sum_transfer(transition_length)
                Warning: Lower array reference at (1) is out of bounds (-24 < 1) in dimension 1
    :40297:56:  write(2,'(F10.8)') homeownership_by_age(2,:)
                Warning: Array reference at (1) is out of bounds (2 > 1) in dimension 1
    :40244:54:  write(1,'(F15.12)') housing_price(i)              [loop do i=0,transition_length]
                Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
    :40257:54:  write(1,'(F15.12)') housing_stock(i)-total_housing_demand(i)   [same loop]
                Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
    :40257:78:  write(1,'(F15.12)') housing_stock(i)-total_housing_demand(i)   [same loop, second reference]
                Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)
    :40284:58:  write(2,'(F15.12)') lump_sum_transfer(i)          [loop do i=0,transition_length]
                Warning: Array reference at (1) out of bounds (0 < 1) in loop beginning at (2)

The first two sit inside `if (use_old_transition_results==1)`; the rest are the
transition write-out block. If `solve_transition_dynamics` is ever switched to
1 these bounds change and the warnings may not survive; they are reported as
they stand under the configuration built here.

## How far it got

Wall time 587 s (9 min 47 s) from process start to `Error termination`, exit
status 2, on 4 cores at `-O1` with checks. It completed a full stationary
equilibrium solve and the whole downstream statistics chain -- government
revenues, aggregate consumption, welfare, housing spending, welfare and
homeownership by characteristics -- and died in the next call,
`stationary_equilibrium_wealth_distribution_of_old(1)` at line 36145, on the
first calibration iteration. Nothing after that line was exercised, so this run
says nothing about the rest of the model: the first violation ends the search,
it does not bound it.
