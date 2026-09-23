# b_smi sweep, point 0.5

INTERIM, block 1 only. Updated as further blocks land.

    b_smi_multiple      0.5
    blocks completed    1, BLOCK MOVE 1.0000 (the first block's sentinel, not a move)
    MOMENT r_smi        2.65652   against 7.30
    SUD | SMI           0.14312   derived, see below
    SUD | non-SMI       0.05388   derived, see below
    b                   0.145009  against 0.10502
    lambda_d            0.058016  against 0.043424
    model_fraction_homeless  0.0078516   NOT at zero

No corner: participation is 0.145, homelessness 0.0079, SMI share 0.0464. The
moments are measuring something.

## The two rates are DERIVED, not printed

The model prints only the ratio. `r_smi` is built at line 11127 from four
cross-tab masses (`xtab_sud_mass_smi`, `xtab_mass_smi`, `xtab_sud_mass_pop`,
`xtab_mass_pop`) and none of the four is ever written to the log, so the levels
cannot be read off directly. They are backed out of the identity

    lambda_d = p_m * (SUD|SMI) + (1 - p_m) * (SUD|non-SMI)
    SUD|SMI  = r_smi * (SUD|non-SMI)

with `MOMENT lambda_d` = 0.0580162 and `MOMENT p_m` = 0.0463871, which
reproduces lambda_d to 8 decimals by construction. This is exact only if the
cross-tab's population base is the same as `model_fraction_addicted`'s. If the
other three points want the rates on a firmer footing, the four masses need a
print, which is a source edit and was not made here.

SUD|non-SMI = 0.0539 is the control. Compare it across the four points.

## Provenance, and one thing to know about it

The cold run (pid 734, launched 00:29 UTC) completed block 1 and was killed by a
container reboot at 00:51:47 -- `uptime -s` read 00:51:47 against a process
launched at 00:29. Every number above is from that cold run's block 1, whose log
carries the full handover verification:

    HANDOVER b_smi_multiple:                1.0000000000000000  ->  0.50000000000000000
    HANDOVER b_smi_multiple_adjuster:       0.0000000000000000  ->  0.0000000000000000
    HANDOVER freeze_all_but_omega_c:                         0  ->           1
    HANDOVER voucher_conditional_on_clean:                   0  ->  0.0000000000000000
    survival: clean housed vs SMI homeless with SUD at age 40 =
        0.98719030618667603   0.88727469276301107

`HANDOVER IGNORED` count 0. Benchmark, not Treatment First. The log is kept as
`run.log.boot1` in the run directory.

The run was relaunched warm from `calibration_state.dat` (written after loop 2);
the handover was NOT restored, per the ENGINE rule. Nothing prints
`b_smi_multiple` on a resume, so the check that the value survived is that the
resumed run's `r_smi` comes back near 2.66 rather than near 1.78, which is the
multiple = 1.0 value. That check is pending the resumed run's first block.

## A DIFFERENCE BETWEEN THE COLD AND WARM PATHS, flagged not fixed

The cold run printed ZERO `budget does not clear` lines. The warm resume printed
216,937 of them in about two minutes -- 95 MB -- and then stopped of its own
accord and returned to normal output. It is not the unsecured-borrowing defect
that `code/BUDGET_DOES_NOT_CLEAR.md` records and closes: there the shortfall was
large, negative, and equal to the household's debt, whereas here every financial
position is zero and the residual is a constant

    budget does not clear by   1.9999999552965164E-002

which is float32 `0.02` promoted to double -- so it enters from a
single-precision literal or variable -- on street households
(`housing_status_index = -1`, `housing_status_index_used = 2`). The diagnostic
fires at line 31727 on a tolerance of 5e-8.

This is a pre-existing property of the warm path, not of `b_smi_multiple`, and
it is out of this sweep's scope. It is written down rather than touched. It is
worth knowing whether the other three points see it on THEIR resumes: if they
do, it belongs to the resume path; if only this one does, that is a different
question.
