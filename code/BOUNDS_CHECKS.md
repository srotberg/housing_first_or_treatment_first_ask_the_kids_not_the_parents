# Debug-build gates on the Fortran

Each entry records ONE run of the model under a compiler configuration chosen to
catch a class of fault the ordinary `-O3` build cannot see, on a named parameter
vector. The verdict is recorded whether it passed or trapped, and the backtrace
is recorded VERBATIM. Judging whether a trap is real is not done here.

---

## 2026-09-03 -- uninitialised-memory gate, KKK live, line 2 of `code/batch_kkklive.txt`

**Why.** `get_probabilities_KKK_process` once read a local array it never
assigned and every KKK run came back NaN. A bounds check cannot find that:
reading an uninitialised local is not an out-of-bounds access. The Fortran has
since changed on this path -- `bottom_productivity_level` now applies under KKK,
at every age -- so the gate was re-run before any KKK point was measured.

**Build.** gfortran 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1):

    gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow \
        -fcheck=bounds,pointer -g -fbacktrace -fimplicit-none \
        -ffree-line-length-none -mcmodel=medium -fopenmp \
        code/housing_first_or_treatment_first_SR_v1.f90 -o /tmp/snan_kkk

Compiled clean in 26 s. The only warnings are three `Array reference at (1) out
of bounds (0 < 1)` on `housing_stock(i)`, `total_housing_demand(i)` and
`lump_sum_transfer(i)` at lines 41491 and 41518, inside the TRANSITION writer,
which this run never enters.

**Vector.** Line 2 of `code/batch_kkklive.txt` -- the current best point
`6d1662b473` with `fixed_productivity=0` and `kkk_sigma_scale=2.20949`.
`PARAM_HANDOVER.txt` (60 lines) and `B_SWEEP_GRID.txt` (`0.033204`) were written
by hand in a scratch directory, reproducing exactly what `run_one_point.sh` does,
with `../data` symlinked to the repository's `data/`.

**Source at the head of this run:** `df20399`.

### VERDICT: the gate PASSES. It then trapped LATER, in the moments code.

Everything the gate was asked to clear was cleared:

| stage | result |
| --- | --- |
| grid construction (`employment_grid`, `employment_process`) | passed, no trap |
| `create_newborn_employment_probability` | passed, no trap |
| `verify_newborn_process` | passed: `rows not summing to one=0`, `rows off p(1)=0` |
| backward induction, at least 25 ages | passed ALL 60 ages -- the run went on to solve the stationary distribution to convergence, `DIST_DONE sweeps=47 final_distance=5.9148728701911043E-004` |

Not one `snan` fired anywhere in grid construction, the newborn draw, the value
function, or the distribution sweep. Under `-finit-real=snan` with
`-ffpe-trap=invalid` an uninitialised real is a trap on first use, so the class
of fault that produced the all-NaN KKK runs is not present on this path at this
vector.

### The trap that did occur, verbatim

It fires AFTER the equilibrium is solved, in
`stationary_equilibrium_statistics`, and is reported here without judgement:

```
 parents replaced by newborns: clean housed=  0.99180892770212692       clean homeless=   6.2036153518999840E-003  disordered housed=   1.3586999600003770E-003  disordered homeless=   6.2875698597243776E-004

Program received signal SIGFPE: Floating-point exception - erroneous arithmetic operation.

Backtrace for this error:
#0  0x1485d0823e59 in ???
#1  0x1485d0822e75 in ???
#2  0x1485d044532f in ???
	at ./signal/../sysdeps/unix/sysv/linux/x86_64/libc_sigaction.c:0
#3  0x55da8e1f5234 in stationary_equilibrium_statistics_
	at code/housing_first_or_treatment_first_SR_v1.f90:10368
#4  0x55da8e253499 in calibrating_model_
	at code/housing_first_or_treatment_first_SR_v1.f90:37370
#5  0x55da8e2567fc in main_program
	at code/housing_first_or_treatment_first_SR_v1.f90:7748
#6  0x55da8e25683f in main
	at code/housing_first_or_treatment_first_SR_v1.f90:7711
```

The statement at the trap site:

```
10366:         percentiles_homeless_income(time_period,1)=&
10367:             (model_average_rent(time_period)*model_average_rental_unit_size(time_period))/&
10368:             rent_to_income_ratios(time_period,max(median_index(1),1))
```

Process exit status 136 (128+8, SIGFPE). No bounds or pointer check fired at
any point in the run; the only trap is this floating-point one.

### The four lines the KKK path prints, verbatim

```
 KKK productivity process live. sd of log y at age 1 =  0.90375433643397307     
   masses at age 1:   2.3949540690481608E-003   3.6597474122084861E-002  0.20167206526564946       0.39772851514611357       0.28270559605195122        7.2161464031761047E-002   6.7399313133916783E-003
   mean productivity at age 1 =  0.99999999999999989     
 KKK grid: bottom half's share of productivity =  0.16275923888780452       target =  0.17199999999999999     
```

For context, the two grid lines that bracket the masses:

```
   grid age 1  :   3.1102024679000362E-002   8.0943085429258169E-002  0.21065455212090595       0.54822892028303272        1.4267669319682932        3.7131639773897165        9.6635171548053655     
   grid last working age:   2.1515403349096952E-002   6.2907180957477243E-002  0.18392931574684548       0.53777633453278584        1.5723615607941972        4.5973032264632634        13.441690183124422     
```

Because the trap is not in grid construction and not in the newborn draw, the
measurement runs were allowed to proceed.
