# The one-class core calibration: launch record, 22 September 23:40:49 UTC

Plain benchmark solve of the committed source at `child_penalty_classes=1`,
`weight_on_child=0`, `omega_c_is_pinned=1`, `iota_smi=1.0`, `mu_m=1.0`,
`b_smi_multiple=1.0`, all DECLARED in the Fortran and so surviving a resume.
Run directory `code/oneclass_core/`, gitignored; this note is the part that has
to outlive the container.

    source   0ef8caf, code/housing_first_or_treatment_first_SR_v1.f90
    vector   code/seeds/PARAM_HANDOVER_oneclass_core.txt
    pid      1180, sid 1180 (own session), ppid 1177 whose own parent is 1
    launch   23:40:49 UTC, cold
    CPU      3.77 of 4 cores, measured from /proc/1180/stat over 10 s

## THE THREE BUILDS, ALL CLEAN

Seven warnings and zero errors in each, the warnings being the pre-existing
`transition_length-25` out-of-bounds notices that fire because
`transition_length` is 1 in a steady state.

    -O3 -funroll-loops                              rc 0, 7 warnings, 0 errors
    -O1 -fcheck=bounds,pointer -g -fbacktrace       rc 0, 7 warnings, 0 errors
    -O1 -finit-real=snan -ffpe-trap=... -g          rc 0, 7 warnings, 0 errors

All three took 57 seconds together on 4 cores. The -O3 binary was copied into
the run directory, so the run is isolated from further edits to the master.

## VERIFIED IN THE RUN'S OWN LOG

    HANDOVER voucher_conditional_on_clean:  0 ->  0    benchmark, NOT Treatment First
    HANDOVER freeze_all_but_omega_c:        0 ->  0
    HANDOVER omega_c_is_pinned:             1 ->  1
    HANDOVER weight_on_child:               0 ->  0
    survival: clean housed vs SMI homeless with SUD at age 40 =
        0.98719030618667603   0.88727469276301107      the mortality fix
    no calibration_state.dat, starting from the declared values    COLD
    grep -c "HANDOVER IGNORED"  ->  0   over all names

## TWO THINGS A FRESH CONTAINER NEEDS, AND THE SECOND COST A LAUNCH

**gfortran is not in the image.** Only gcc is. `apt-get install -y gfortran-13`
and `ln -sf /usr/bin/gfortran-13 /usr/local/bin/gfortran`; it took 40 seconds
here, not the fifteen minutes an older note quotes. Already written down in
`code/results/transition_t60_gf/COLD_START.md` section 0.

**`code/data/` must exist before the binary starts.** The model opens
`../data/us_mortality_multipliers.csv` and `../data/us_mh_onset_shape.csv`,
which from a run directory under `code/` resolves to `code/data/`, not to the
repository's `data/`. It is gitignored, so a fresh container does not have it.
`launch_arm.sh` stages it and says why; this run was launched by hand and did
not, so the first launch died at

    us_mortality_multipliers.csv not found. stopping.

after 165 log lines -- and, exactly as `launch_arm.sh`'s comment warns, AFTER
the binary had read and DELETED `PARAM_HANDOVER.txt`. The `.kept.txt` copy is
what made that a two-minute event instead of a silent run on the Fortran's
declared values. **Keep the `.kept.txt` copy; it is not ceremony.**

The relaunch cleared `calibration_state.dat`, `resume_seed.dat` and
`newborn_parent_share.dat` written by the aborted start, so the run is genuinely
cold rather than resuming from an abort.

## WHY NO BENCHMARK .dat SET WAS STAGED

`frac_of_households_in_support_of_policy` reads
`value_function{1,2}baseline_benchmark.dat` and
`distribution_stationary{1,2}baseline_benchmark.dat` unguarded, and is called at
the end of every block, which reads like a cold benchmark cannot run without
them. It can: `code/results/benchmark_coldstart/RESULT.md` records a fully cold
benchmark that reached block 14 with none of the 4.71 GB of .dat inputs present.
The benchmark writes those names itself under `vf_simulation` before the read.

Staging the committed `code/seeds/benchmark_dat/` set would have been WRONG
here in any case: it is the TWO-class benchmark, and one class halves the
employment dimension from 26 to 13, so the arrays are smaller and a formatted
read would have taken a prefix of the wrong file without erroring.

## EXPECTED

~20 minutes to the first block, ~5 minutes a block after that. `MOMENT r_smi`
-- the SUD rate given SMI over the SUD rate given no SMI, target 7.30 from
NSDUH 2024 -- will print with no parameter beside it, because its instrument
`b_smi_multiple` has no bracket yet. That is the honest state.
