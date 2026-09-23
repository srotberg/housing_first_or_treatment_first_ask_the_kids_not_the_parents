# The one-class calibration with the SMI channel LIVE: launch record

23 September 00:28:00 UTC. Plain benchmark solve of the committed source at
`child_penalty_classes=1`, `weight_on_child=0`, `omega_c_is_pinned=1`,
`iota_smi=1.0`, `mu_m=1.0`, all DECLARED in the Fortran and so surviving a
resume. This run REPLACES `results/oneclass_core/`, which ran the same
calibration before `b_smi_multiple`'s bracket existed; that one is archived.

    source   7ce5626, code/housing_first_or_treatment_first_SR_v1.f90
    vector   code/seeds/PARAM_HANDOVER_oneclass_core.txt
    run dir  code/oneclass_bsmi/ (gitignored)
    pid      782, sid 782 (own session), ppid 1
    launch   00:28:00 UTC, COLD
    CPU      3.79 of 4 cores, from fields 14+15 of /proc/782/stat over 10 s
    RSS      0.88 GB at 47 s and climbing

## WHAT IS NEW, AND WHY THE REBUILD

`b_smi_multiple`, an SMI-specific multiple on the Stone-Geary shifter
`addiction_scalar_1`, with its bracket live at adjuster 0.02. It is calibrated
on `MOMENT r_smi` -- the SUD rate given SMI over the SUD rate given no SMI --
against `sud_smi_ratio_data = 7.30`, NSDUH 2024 at 26+. Last measured at
1.7792, a 75.6 per cent gap.

**ITS SIGN IS REVERSED FROM EVERY OTHER BRACKET IN THE FILE**, and the source
says so at 51038. b enters flow utility as (b+q)^phi_q, so the marginal value
of the first unit goes like 1/b: a LARGER multiple makes the drug worth LESS
to an SMI household, they use less, and the ratio FALLS. The update therefore
ADDS the gap,

    b_smi_multiple = b_smi_multiple + adjuster*(sud_smi_ratio - sud_smi_ratio_data)

so a model BELOW target LOWERS the parameter. Do not "correct" it. The step is
capped at 5 per cent a loop by `b_smi_multiple_max_rel_step`, so from 1.0 it is
roughly 45 loops to 0.1. Slow by design; the cap is not to be raised without
the author.

The distance is RELATIVE, not absolute, because the ratio is order 7 rather
than order 0.05 like the shares the other brackets score.

## THE THREE BUILDS, ALL CLEAN

Seven warnings, zero errors in each -- the pre-existing `transition_length-25`
out-of-bounds notices that fire because `transition_length` is 1 in a steady
state. Same seven the predecessor recorded.

    -O3 -funroll-loops                              rc 0, 7 warnings, 0 errors
    -O1 -fcheck=bounds,pointer -g -fbacktrace       rc 0, 7 warnings, 0 errors
    -O1 -finit-real=snan -ffpe-trap=... -g          rc 0, 7 warnings, 0 errors

The -O3 binary was copied into the run directory, so the run is isolated from
later edits to the master.

## VERIFIED IN THE RUN'S OWN LOG, BEFORE ANY NUMBER WAS READ OFF IT

    HANDOVER voucher_conditional_on_clean:  0 ->  0       benchmark, NOT Treatment First
    HANDOVER freeze_all_but_omega_c:        0 ->  0
    HANDOVER omega_c_is_pinned:             1 ->  1
    HANDOVER weight_on_child:               0 ->  0
    HANDOVER b_smi_multiple:                1.0 -> 1.0
    HANDOVER b_smi_multiple_adjuster:       0 ->  0.02    THE BRACKET IS LIVE
    survival: clean housed vs SMI homeless with SUD at age 40 =
        0.98719030618667603   0.88727469276301107         the mortality fix
    survival: SMI multiplier is live, kappa_phi_m = 2.5

    no calibration_state.dat, starting from the declared values       COLD
    no warm start distribution, initialising from the age one cross section
    handover banked into calibration_state.dat before the first solve
    grep -c "HANDOVER IGNORED" -> 0
    run.err empty

## THE TWO THINGS A FRESH CONTAINER NEEDED

Both were recorded by the predecessor and both were done before launch, so
neither cost anything this time:

    apt-get install -y gfortran-13 && ln -sf /usr/bin/gfortran-13 /usr/local/bin/gfortran
    mkdir -p code/data && cp data/us_{mortality_multipliers,mh_onset_shape}.csv code/data/

`code/data/` is what the binary resolves `../data/` to from a run directory
under `code/`. It is gitignored, so every fresh container has to stage it, and
the failure comes AFTER the binary has read and DELETED `PARAM_HANDOVER.txt`.
`PARAM_HANDOVER.kept.txt` is beside it for that reason and is not ceremony.

## ON A RESUME

Relaunch `./hftf` in place; it resumes from `calibration_state.dat` and the
distributions. **DO NOT RESTORE PARAM_HANDOVER** -- it would reset every
calibrated parameter, `b_smi_multiple` included, to its starting value and
throw the loops away. The state file carries them; `b_smi_multiple` and its
adjuster persist at the tail as of 7ce5626.

## THE CONTROL THE CHANNEL HAS TO PASS

`b_smi_multiple` must move SMI households and essentially nothing else. At any
check-in where it has moved appreciably, SUD|SMI and SUD|non-SMI are reported
SEPARATELY, not only their ratio. SUD|non-SMI should barely move. If it moves
nearly as much as SUD|SMI the channel is leaking into households it must not
touch, and that is said loudly rather than filed.

## EXPECTED

~20 minutes to the first block, ~2.5 minutes a loop after. The channel is
working if `r_smi` RISES as `b_smi_multiple` FALLS.
