# Calibration state — 3 September, 12:05

## THE GATE IS OPEN

`GATE` was lowered from 0.05 to 0.10 on the author's decision, because b and
lambda_d are **not separately identified** by the instruments in this model —
Jacobian condition number 36,711 in their two-parameter plane, and the steepest
of 452 measured directions is 5.92 against the 10 required. The argument is in
`code/GAP_TABLE.md`; the note beside the constant carries it too.

    GATE OPEN at point_6d1662b473: b +6.0%, lambda_d -7.7%

The drug block is finished, inside the author's ten per cent standard, after
going 70.4 -> 53.5 -> 38.1 -> 16.2 -> 10.3 -> 7.7 across the night.

## ROUND 1 IS RUNNING: 17 moments, 23 lines, 8 workers

`CORRECT_63.txt`, launched 12:02. A bracket either side of every instrument
owning an out-of-target moment. The staging discipline holds:
`utility_cost_of_treatment`, `multiple_of_probabilities_of_employment_if_addicted`,
`kappa_uem` and `mu_homeless` are still HELD because their stage is not open.

Worst moments going in: `emp_homeless` +92.8, `pi_eu` +54.5, `h_share1` +48.4,
`pi_V` +44.8, `aleph` +42.9, `omega_l` -35.3, `w_bot` +29.2, `theta` +21.4,
`h_1` +20.0, `beta` -19.1, `tau_l` +12.6, `h_2` -12.3, `cbar` +10.7,
`gamma` -10.4. Inside ten: `b`, `lambda_d`, `sigma_y`, `h_3`, `p_m`, `y_u`.

**Line 1 is the one to watch.** It carries `bottom_productivity_level = 0.004`,
the mean-preserving bottom-node override, which owns `emp_homeless` — the worst
moment in the model — and has never been measured away from zero.

## SIX HOURS WERE LOST, 05:55 to 11:50

`CORRECT_63.txt` was emitted when the gate opened and not launched: the
coordinator's push was rejected on a concurrent update and the turn ended on the
rebase. Thirty-six trigger firings queued unserviced. The batch was correct all
along — the gate re-ran at 12:01 and returned "identical to CORRECT_63.txt".

**The lesson, and it is general:** a firing that emits a batch is not finished
until the batch is LAUNCHED. Committing it is not launching it. Check the worker
count against the batch's line count before the turn ends.

## Two defects in the emitted batch

Lines 1 and 2 of `CORRECT_63.txt` are byte-identical, and 19/20 may be. The
duplicate was skipped rather than solved twice; one worker was told to `diff`
its pair before spending on it.

## Not in the calibration, and waiting

The four KKK arms of `batch_kkk0.txt` — the author's own productivity process —
have never produced a valid measurement. Every attempt was lost to the
background-brief failure. `fixed_productivity=1` is the committed default so
none of it touches the running calibration. `code/OPEN_ISSUES.md` has the six
economic findings established in closed form, including that KKK at its
published parameters has a poorest household earning 0.232 of mean productivity
and so cannot generate homelessness at all.
