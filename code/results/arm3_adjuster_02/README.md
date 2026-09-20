# launch_arm.sh RAN EVERY ARM AT drug_market_adjuster = 0.2. IT SHOULD BE 0.1.

Found 20 September on a live arm 3, three blocks in, and the run was killed and
relaunched rather than allowed to finish.

## WHAT WAS WRONG

`drug_market_adjuster` is declared 0.2 in the Fortran and IS a handover name
(case at 45838, clamped to [0, 2]). `launch_arm.sh` never set it, so every arm
staged through the script ran at 0.2 -- and `results/arm3_convergence/CONVERGED.md`
is explicit that the only arm 3 run which ever met its own acceptance test was
made at **0.1**, and that *"arm 3 cycles at adjuster 0.2; the two 'converged' runs
are peak and trough"* of that cycle.

The setting was therefore remembered rather than recorded. The script is described
in the recipe as "the script that was actually used, not a tidied-up version",
which is what made the gap invisible: it looks complete.

## HOW IT WAS CAUGHT, WHICH IS THE PART WORTH KEEPING

Not by reading the script. By scoring the live trace against the acceptance test
BEFORE the run could stop:

    block 1   CF MOMENTS 1.6281      b 0.044462   lambda_d 0.017567
    block 2   CF MOMENTS 3.3814e-3   b 0.047844   lambda_d 0.018540
    block 3   CF MOMENTS 5.2347e-4   b 0.047320   lambda_d 0.018726

and the measured cycle band in CONVERGED.md is **[0.04492, 0.04732]**. Block 3's
b of 0.047320 is sitting exactly on the top of it, to five digits. At that moment
all three live rules were just outside tolerance and about to cross --
CF moments 5.2347e-4 against 5e-4, drug 7.2459e-3 against 5e-3, budget 2.9815e-2
against 2.5e-2 -- so the next block or two would have stopped the run at a phase
of the cycle and handed the transition a terminal condition with b about 4.5 per
cent high.

**That would have looked like a failed reproduction of arm 3 and it would have been
a failure to pass one setting.** The brief for this session says to STOP and report
if arm 3 does not land near the archive's numbers, so the cost was not just a bad
arm: it was a spurious halt with a real-looking cause.

The log of those three blocks is kept here as the evidence.

## WHY 0.2 IS THE WRONG SIDE OF A BOUND THAT IS ALREADY WRITTEN DOWN

Section 6a of `CALIBRATION_RECIPE.md` does the arithmetic: the price update is
`p' = p + a*gap` with `d(gap)/dp = -7.41` measured, so the multiplier is
`1 - 7.41*a` and stability needs `a < 0.270`. That is why 0.2 replaced 0.5. It
puts 0.2 inside the bound by 26 per cent of the way to the edge -- stable in
theory, and the recipe also says the 0.5-per-cent clip "converts divergence into a
slow crawl; it does not cure it", so a setting that near the edge behaves like the
clip until the price is warm and then like the slope. On this arm, warm started AT
the converged price, the clip stops binding and 0.2 is close enough to the edge to
cycle. 0.1 is not.

## THE FIX

`launch_arm.sh` takes it as a sixth optional argument, defaulting to **0.1**, and
carries the reasoning above at the top of the script so the next reader does not
have to rediscover which value the converged run used.

    launch_arm.sh <arm> <kappa_x> <benchmark dir> [price] [pi_v] [drug_market_adjuster]

The relaunched run is at 0.1, warm started at the converged price 0.833490 and
pi_v 0.076347, which is a better start than the converged run's own -- that one
was seeded at the cycle mean because it did not yet know where the cycle centred.

## THE GENERAL SHAPE, because this is the third instance in this project

A setting that a result depended on lived only in the prose of the note that
reported the result. `CONVERGED.md` says 0.1 in its first line and nothing in the
tooling did. The same class as `kappa_x`, where the seed carries the coded 0.002
and every arm runs at 0.8139, and as the rung ratios, where "the defaults were
left at the old 2.0 and 3.0 for a full day, so any batch built from a base that
did not carry them explicitly silently ran the old ladder."

**A number a result depends on belongs in the script that produces the result, not
in the file that reports it.**
