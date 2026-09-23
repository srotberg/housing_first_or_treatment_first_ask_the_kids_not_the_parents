# A RESUME DOES NOT COME BACK INTO THE ECONOMY IT LEFT

23 September 01:10 UTC, `code/oneclass_bsmi/`. Written down rather than acted
on, per the standing rule: the model is the author's to change, and the run is
left going.

## WHAT HAPPENED

The container was reclaimed at the end of the launching turn (see ENGINE.md's
top entry). The relaunch resumed correctly by every check the predecessor's
notes prescribe -- and landed in a different, degenerate economy.

                              COLD (attempt 1)     WARM (the resume)
    MOMENT b   drug users        0.13006              0.95251
    MOMENT lambda_d              0.052444             0.0000000  exactly
    MOMENT r_smi                 1.7792               HELD, no measurable cell
    drug quantity V              0.82021              5.72716        7x
    drug_supply_shifter          1.1454               0.30260
    emp share of the homeless    0.21692              0.92676
    SMI share of the homeless    0.24104              0.06183

The decomposition is the sharpest single fact:

    COLD   experimenters 0.077619   addicted+experimenters 0.130063  -> addicted 0.052444
    WARM   experimenters 0.952508   addicted+experimenters 0.952508  -> addicted 0

**Everyone is an experimenter and the addicted stock is empty.** That is why
lambda_d is exactly zero and why the SMI comorbidity ratio has no cell to
measure, so `b_smi_multiple` is HELD and the channel cannot move.

## WHAT THE RESUME DID RESTORE, VERIFIED

Every check in the handover notes passes. This is the point: the resume looks
healthy.

    resumed from calibration_state.dat, written after loop 2
    warm start distribution loaded, sum= 51.029103887395664
    addiction_scalar_1  4.9191800065759997E-003  against the cold run's
                        4.9191800065755218E-003  -- identical to 10 s.f.
    b_smi_multiple      0.95, the step attempt 1 took, persisted
    shape stamp         4282200, matched; 132748200/4282200 = 31 bytes a record

## TWO HYPOTHESES RAISED AND KILLED, SO THEY ARE NOT RAISED AGAIN

**Not the declared values.** `launch_arm.sh`'s comment warns that a naive
restart runs the Fortran's declared values and that this reads as "b ~ 0.95,
lambda_d = 0", which is exactly the observed signature. It is a coincidence:
`addiction_scalar_1` and every other calibrated parameter came back at their
calibrated values, not their declared ones.

**Not the drug supply shifter failing to round-trip.** The shifter differs
between the runs, but the benchmark path at 44785 RECOMPUTES it from the
current quantity every block and writes it out; only the counterfactual path
reads the file back. So the differing shifter is a SYMPTOM of the 7x quantity,
not a cause. `price_of_addictive_good_benchmark` is a compile-time
`parameter = 1`, identical in both runs, so the price is not it either.

A third reading was also wrong and is recorded so the regex is not repeated: a
grep for `lambda_addiction` matches `distance_lambda_addiction`, and the
"restored" 0.043424 was that distance, which is just
`abs(model_fraction_addicted - sud_rate_data)` at a zero disorder rate. There is
no evidence of a misaligned checkpoint field; the write and read orders agree
over the window inspected.

## WHAT IS ESTABLISHED AND WHAT IS NOT

ESTABLISHED: the first block after a resume is a different economy from the one
checkpointed, in the direction of universal experimentation and no addiction.

NOT ESTABLISHED: whether it recovers over subsequent blocks. The onset
instrument is in its cooldown -- `onset HELD: 1 of 2 cooldown blocks ... the
disorder rate reads 0.0000000000000000` -- so it cannot correct this block
whatever the cause.

THE LIKELY MECHANISM, UNPROVEN: **no value function is checkpointed.**
`calibration_state.dat` is 4818 bytes of parameters; the two distribution files
carry the distribution; nothing carries the value function, and `resume_seed.dat`
is written at 45066 and never read anywhere in the file. So a resume pairs a
WARM distribution with a COLD value function. A cold start does not have that
mismatch, which fits the cold/warm asymmetry exactly.

## WHY THIS MATTERS MORE THAN AN ORDINARY BUG

The survival strategy in this environment rests on the checkpoint: the
container is turn-scoped, so every run is a sequence of resumes. If a resume
lands in a different economy and needs blocks to climb back -- or does not climb
back -- then the calibration cannot make progress by resuming, and the cost is
paid silently, because every verification line the notes prescribe still passes.

**AND THE 22 SEPTEMBER RESUME WAS VALIDATED ONLY ON THE DISTRIBUTION SUM.**
ENGINE.md records it coming back "with `warm start distribution loaded, sum=
50.537513340218254` -- the same sum as the last DIAG line before the reboot".
A matching sum does not test the moments, and this divergence would have passed
that check. Whether that run was also diverged is worth knowing before its
numbers are used.

## WHAT IS NOT BEING DONE

No Fortran is being edited. The run is left going so the recovery question gets
its answer. If the author wants the mechanism settled, the cheap decisive test
is the one-parameter kind the engine already prefers: checkpoint the value
function, or re-run a cold start to the same loop and compare block by block.

---

# THE ANSWER: IT DOES NOT RECOVER. IT OSCILLATES BETWEEN CORNERS.

Block 3 settled the open question, and not the way the onset step promised.

    block 1   b = 0.95251      quantity 5.7272       everyone uses
    block 2   b = 0.95267      quantity 8.7880       everyone uses
    block 3   b = 0.0000077    quantity 0.0000023    nobody uses

The onset instrument came off its cooldown and stepped `addiction_onset_base`
to 0.0827, printing "RAISED: lambda_d is below target". That is the right
direction by its own rule and it emptied the drug market completely -- the
counterintuitive sign ENGINE.md already documents, where making use riskier
deters use at the extensive margin instead of converting users. The run went
from one corner to the other in a single block. It never passed through
anything resembling the economy it was checkpointed from.

**THE RUN WAS STOPPED** at 01:16, by numeric pid, and cold-restarted. Stopping
was within the standing bar -- a state that provably cannot produce a usable
point -- and the second finding below is why it could not simply be left going.

# A SECOND DEFECT, AND THIS ONE CORRUPTS THE PARAMETER

At block 3 the bracket printed a MEASURABLE ratio and stepped on it:

    b_smi_multiple= 0.9025   distance= 0.6566   SUD ratio SMI over non-SMI= 2.5066

That 2.5066 was computed over a drug-using population of **7.66e-06**. The
corner guard in front of it tests the three denominators against `1e-12`:

    if ((xtab_mass_smi(1)<=10.d0**(-12)) .OR. &
        ((xtab_mass_pop(1)-xtab_mass_smi(1))<=10.d0**(-12)) .OR. &
        ((xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1))<=10.d0**(-12))) then

A mass of 7.66e-06 clears 1e-12 by seven orders of magnitude, so the guard
passes, the ratio is fabricated out of a handful of households, and
`b_smi_multiple` takes a real 5 per cent step on it -- 0.95 -> 0.9025.

**So an emptied drug market does not merely stall the channel, it moves the
parameter on noise.** The guard is doing what it was written to do, which is to
catch an exactly empty cell; it was not written to catch a cell that is
populated but negligible. A guard on a SHARE -- the SUD rate, or the SMI mass,
against something like 1e-4 of the population -- would have held the bracket
here. That is a source change and it is the author's call.

**AND IT IS WHY THE OBVIOUS READING OF BLOCK 3 IS WRONG.** r_smi went 1.7792 at
b_smi_multiple = 1.0 to 2.5066 at 0.95, which is exactly the "r_smi RISES as
b_smi_multiple FALLS" the channel is supposed to show. It is not evidence of
anything. The two numbers come from two different economies, neither of them
the calibrated one, and the second was measured on 7.66e-06 of the population.
Reporting that pair as the channel working would have been the mistake this
whole note exists to prevent.

# WHAT WAS DONE

Cold-restarted at 01:16:40 from `PARAM_HANDOVER.kept.txt`, which carries
`b_smi_multiple 1.0` -- deliberately NOT the 0.9025 the diverged run left in
the state file, since that step was taken on a fabricated ratio. The diverged
run's log is kept as `run_attempt2_diverged.log` and its state under
`void_20260923T011640Z/`.

Cold start verified: `no calibration_state.dat, starting from the declared
values`, the benchmark switches, the adjuster at 0.02, the survival pair, zero
`HANDOVER IGNORED`, empty stderr.

# THE WORKING RULE UNTIL THE AUTHOR RULES OTHERWISE

**Do not resume this model. Cold start.** A cold start reaches its first moment
block in about five and a half minutes, measured on attempt 1 -- not the twenty
minutes the launch notes predicted -- so the resume is not even buying much.
`cold_restart.sh` in the run directory does it safely: it moves the state AND
the distribution aside, since leaving either behind is what makes the binary
resume, and it refuses to run while `hftf` is alive.
