# The fix-only benchmark: the mortality fix alone, no recalibration

Stopped 22:45:48 at block 12, `BLOCK MOVE 0.000282` against a rule of 1e-4 --
2.8 times tolerance, so this did NOT meet its stopping rule and is recorded as
converged to 1e-3, not 1e-4. The ratio was flat to within 0.02 for the last ten
blocks while the move fell by three and a half orders of magnitude, so the
answer is not in doubt; the rule is simply not met and should not be claimed.

Run: `code/bench_fixonly`, benchmark vector `seeds/PARAM_HANDOVER_bm_n90repro`,
switches verified IN THE RUN'S OWN LOG before anything was read off it, warm
started from the archive benchmark (md5 c35f79f5..., sum 50.861206888360229),
patched survival, no parameter moved.

                          reference   fix-only     target
    SUD | SMI              0.02043    0.09684        --
    SUD | non-SMI          0.03428    0.04697        --
    ratio                  0.596      2.062         7.30
    mild-only ratio        0.419      0.746          --
    aggregate SUD          0.033609   0.049390     0.043424
    SMI share              0.048291   0.048551       --

## What it establishes

**The mortality double count was suppressing the comorbidity and its removal
flips the sign.** 0.596 to 2.062, with no parameter moved. That is about 28 per
cent of the way to the measured target of 7.30.

**It is not enough, and it overshoots the level.** Aggregate SUD goes from 23
per cent below target to 14 per cent above it, so the drug block needs
refitting whatever else is done.

**The remaining gap is at entry.** Like for like against the data, the model's
persistence ratio is 1.47 against 1.62 -- nearly right -- while its use ratio is
1.39 against 4.51. See `data/SMI_SUD_TARGET.md`.

## Its status now

Superseded as a configuration: the model has moved to one class with omega_c
pinned at zero, and SMI has been made exogenous by setting iota_smi and mu_m to
one. This file is kept as the decomposition step between the archive benchmark
and whatever the new calibration produces, and it is the only point at which
the mortality fix is observed ALONE.
