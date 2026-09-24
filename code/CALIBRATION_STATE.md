# omega_c = 1 HAS LANDED, AND IT SHOWS US HOW TO GET THE CEV, 24 September 02:25

## THE POINT

`results/counterfactuals/omega_c_1/`, stopped at block 9 on the family rule.
I checked the arithmetic myself rather than taking the worker's word:

    |b(8)-b(7)|/b(7) = 0.088370%
    |b(9)-b(8)|/b(8) = 0.064590%

Two consecutive blocks under 0.5 per cent, so the rule fired at block 9 and
NOT on `block_move`, which was still 2.18e-3 against its own 1e-3. That is the
rule working the way it was written to work.

    b         0.020193681800784184     -79.59% against the benchmark 0.098916
    lambda_d  0.0086396190579697343    -80.17% against 0.043579
    h_1       0.0050674582045910242
    bequest_residual                   1.3251517352725006

Not a corner: b was approached FROM BELOW (0.0121 -> 0.0209 -> 0.0198 ->
0.0202), h_1 is not zero, unemployment is normal.

The caveat the worker raises is real and I am recording it rather than
smoothing it: the residual settled at 1.3252, BELOW the 1.45-1.48 band every
other settled point in this family lands in, and fell monotonically across all
nine blocks without turning. Against reading it as unconverged, b itself is
firm to 1.3e-5 over the last three blocks while the residual still moves -- b
and the residual have decoupled, which the restart-transient account does not
predict. `weight_on_child = 1` acts directly on the bequest motive, so the
residual has a real reason to rest elsewhere. One run cannot separate the two.

## THE CEV IS MISSING FROM EVERY HAND-STOPPED RUN, AND THE FIX IS IN THE SOURCE

`save_welfare_curve` did NOT run. Verified, not assumed: `run.err` contains
exactly `Terminated`, no welfare file exists in the run directory, and the
string "CEV" appears zero times in the 1.17 MB log.

This is not specific to omega_c = 1. **It will hit every counterfactual in this
family**, because the family stop rule stops the run BY HAND and the welfare
curve is written after the calibration loop exits:

    line 52324   if (use_old_results==0) call save_welfare_curve(1)

and a frozen run never exits that loop on its own. The source says so at line
948 in terms: frozen, no parameter moves and no distance shrinks, so "the loop
never ends and the run never reaches save_vars_and_functions -- which is what
writes the policy functions save_welfare_curve reads. No run in this line has
ever got past that loop."

**The machinery already exists and needs NO model edit.**
`frozen_stop_after_blocks` is a HANDOVER NAME -- line 97 of
`PARAM_HANDOVER_base.txt`, currently 0 -- read at 46569 and used at 47401:

    .AND. ((frozen_stop_after_blocks==0) .OR. (loop_count<2*frozen_stop_after_blocks))

Set it above zero and the run leaves the loop after that many blocks and goes
on to the statistics, the save and the welfare curve. The doubling is there
because `loop_count` advances TWICE per block.

Use `frozen_stop_after_blocks`, NOT `frozen_stop_tolerance`, which is the other
handover name on that line. The tolerance stops on `block_move`, and stopping
on `block_move` alone is the thing this family does not do.

### THE WELFARE PASS, AND ITS CONTROL

For each counterfactual, after the stop rule fires: resume from that point's
OWN converged state and distributions with the same 97-line handover and
`frozen_stop_after_blocks 2`, and let it exit into the welfare curve. Two
blocks rather than one so the pass carries its own control.

Stating the reference values BEFORE the run, which is the corollary ENGINE.md
requires. The welfare pass must not move the equilibrium, so for omega_c = 1:

    b         0.020193681800784184
    lambda_d  0.0086396190579697343
    h_1       0.0050674582045910242

at 1e-4 relative, never on equality -- the model is not bit-reproducible. If
the pass moves b by more than that, the resume is not landing on the point and
the CEV it produces belongs to a different equilibrium.

## I WAS WRONG ABOUT WHAT THE TRANSITION NEEDS FROM THIS POINT

I told the worker to deprioritise its distribution binaries because "the
transition solves its own terminal steady state from the parameter vector, so
PARAM_HANDOVER.txt is what the next run needs and the distribution is not."

The worker checked and I was wrong. The point was FROZEN
(`freeze_all_but_omega_c 1`, `omega_c_is_pinned 1`), so no adjuster moved and
the handover OUT is the handover IN. I confirmed the diff myself: it differs
from `code/scan_seed/PARAM_HANDOVER_base.txt` by exactly one line,
`weight_on_child 0` -> `weight_on_child 1`. It therefore carries NO information
about the converged equilibrium at all.

The terminal equilibrium lives in `calibration_state.dat` and the two
distributions. Those are the deliverable for the T = 60 transition's terminal
state, and they have to be pushed, gzipped -- raw
`calibration_distribution1.dat` is 265 MB against GitHub's hard 100 MB blob
limit, and the gz is 13.6 MB.

What survives from the earlier note is only the narrow half: text artefacts go
in their own commit, named explicitly, because a broad `git add` is what the
classifier stops.

