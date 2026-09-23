# b_smi sweep, point b_smi_multiple = 0.2

Benchmark solve, `freeze_all_but_omega_c = 1`, `b_smi_multiple_adjuster = 0`, so
the point is held and nothing else moves. Run dir `code/b_smi_0p2/`, source
`code/housing_first_or_treatment_first_SR_v1.f90`, vector
`code/seeds/PARAM_HANDOVER_oneclass_core.txt` with the three lines overridden.

    b_smi_multiple            0.2
    blocks completed          6, last BLOCK MOVE   1.5027622927147476E-002
    MOMENT r_smi              2.9152435        against 7.30
    SUD | SMI                 0.180804         (18.08 per cent)
    SUD | non-SMI             0.062020         ( 6.20 per cent)   THE CONTROL
    MOMENT b                  0.16492844       against 0.10502
    MOMENT lambda_d           0.067653904      against 0.043424
    model_fraction_homeless   0.0072086633     not zero

NO CORNER. Participation is 16.5 per cent, disorder 6.77 per cent and
homelessness 0.72 per cent; nothing is at zero and nothing is near one, so the
moments are measuring something.

## THE TWO RATES ARE DERIVED, NOT READ, AND HERE IS THE ARITHMETIC

The benchmark prints the RATIO only. The four masses it is built from are
printed on the transition path alone (`TRANSITION SMIDRUG`), so a steady-state
log carries no `SUD | SMI` line to read. Both rates follow exactly from three
printed moments, because `r_smi`, `lambda_d` and `p_m` accumulate over the same
base -- all three sit inside `do age_index=1,life_span`, with SUD the same
`unemployment_index > threshold_addiction_index` test in each:

    SUD | non-SMI = lambda_d / (p_m * r_smi + 1 - p_m)
    SUD | SMI     = r_smi * SUD | non-SMI

The identity reproduces `lambda_d` to twelve digits at every block, which is the
check that it is the right decomposition and not an approximation. Anyone
comparing the four points should apply the same two lines to their `lambda_d`,
`p_m` and `r_smi` rather than compare a derived rate against a read one.

## PER BLOCK, SO THE DRIFT IS VISIBLE

    blk   BLOCK MOVE     r_smi     SUD|SMI    SUD|non-SMI   b          lambda_d
    1     1.0000         3.2589    0.180885   0.055505      0.154927   0.061301
    2     0.20789        2.9300    0.181522   0.061953      0.167414   0.067618
    3     0.085442       2.8882    0.181602   0.062877      0.167603   0.068505
    4     0.039261       2.8846    0.181133   0.062792      0.166987   0.068404
    5     0.018853       2.8959    0.181022   0.062509      0.165945   0.068130
    6     0.015028       2.9152    0.180804   0.062020      0.164928   0.067654

Stopped at six blocks on the brief's rule, not at 1e-2: the last move is
1.50e-2 and still falling. `r_smi` over the last four blocks is 2.885, 2.885,
2.896, 2.915, so read the point as 2.9 with about 0.03 of drift left in it,
not as 2.9152.

`SUD | SMI` is flat from block 2 onward -- 0.1815, 0.1816, 0.1811, 0.1810,
0.1808 -- while `SUD | non-SMI` climbs 0.0555 to 0.0629 and settles back to
0.0620. So within this point the ratio's remaining movement is the CONTROL
moving, not the treated group.

## VERIFIED IN THIS RUN'S OWN LOG

    no calibration_state.dat, starting from the declared values
    HANDOVER b_smi_multiple:                1.0  ->  0.20000000000000001
    HANDOVER b_smi_multiple_adjuster:       0.0  ->  0.0000000000000000
    HANDOVER freeze_all_but_omega_c:          0  ->  1
    HANDOVER voucher_conditional_on_clean:    0  ->  0.0000000000000000
    survival: clean housed vs SMI homeless with SUD at age 40 =
        0.98719030618667603   0.88727469276301107
    grep -c "HANDOVER IGNORED"  ->  0

## WHAT THE LAUNCH COST, AND ONE TRAP WORTH THE NEXT SESSION'S TIME

Two container reboots took the first two attempts, both before any block. Each
is the signature `code/ENGINE.md` describes: `uptime -s` equal to the check-in
firing time to the second, 00:51:45 against a 00:51:46 firing and 01:15:54
against 01:15:55. The run that produced this file was held inside an open turn
instead and ran 31 minutes without interruption, which is ENGINE.md's phase-3
rule 3 -- superseded in September on a different environment, and true again
here on its own one-line test.

**`freeze_all_but_omega_c` DOES NOT SURVIVE A RESUME.** It is declared 0 at
line 946, set only by the handover case at 46566, and is not in
`calibration_state.dat`. A bare relaunch brings it back 0, which puts all 48
adjusters live and turns a held point into a calibration wearing the point's
name. Nothing in the log says so beyond the `0 -> 1` that is then missing.

The second resume trap is the one the source already documents at line 44924:
`calibration_state.dat` is positional and drops parameters it has no slot for.
Restoring only the switches left the rest at compile-time defaults and the
survival line moved to 0.86883920827449246. That line is a real canary -- it is
the only thing that showed the run was solving a different model -- and it is
why the brief's instruction to check it before reading any number off the log
is worth following literally.

`resume_seed.dat` was no help: it had been written before the handover was
applied, carrying `addiction_onset_base 0.0` against the handover's 3.36e-2.

Since no block had completed, the fix was to clear `calibration_state.dat`,
`resume_seed.dat` and `newborn_parent_share.dat` and restore the full handover,
which is `results/oneclass_core/LAUNCH.md`'s precedent for an aborted start.
The standing rule "on a resume do NOT restore PARAM_HANDOVER" protects
completed loops; at loop 0 there are none and it is the opposite of correct.
