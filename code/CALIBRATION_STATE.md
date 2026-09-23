# WHY A RESTART COSTS TWO HOURS: IT IS THE BEQUEST BLOCK, NOT THE VALUE
# FUNCTION, 23 September

Eight separate runs of the two-class benchmark, 55 blocks of real compute, and
no converged point, because every restart throws the run back into a transient.
The cause was nearly misdiagnosed and the wrong fix nearly built.

## IT IS NOT THE VALUE FUNCTION

The obvious suspect is a cold value function, and the author asked for a
value-function warm start this morning. But the log says `CHILD V CONVERGED
after 2 passes`: the household problem is a FINITE-HORIZON backward induction,
exact in one pass, wrapped in a two-pass fixed point for the child's value. A
warm start there saves at most one pass of about fifteen minutes. It does not
explain a thirty-point swing in the moments.

## IT IS THE BEQUEST BLOCK, MEASURED ACROSS THE 16:50 REBOOT

    bequest_residual   settled before the reboot   1.4737, 1.4762, 1.4771
                       after the restart           2.1528, 1.8655, 1.6459
    model_bequests     1.6542 -> 2.2275            +35 per cent
    inheritance_paid   0.177  -> 7.47

These are model OUTPUTS built from the distribution by the aggregation, not
parameters, so `calibration_state.dat` cannot carry them -- it banks
`inheritance_amount` and `minimum_inheritance`, which are the parameters, and
those do survive. Bequests set newborn assets, newborn assets set the wealth
distribution, and the wealth distribution sets drug use. A 46 per cent jump in
the residual is therefore a large shock to the targeted moment, and it decays
over several blocks as the aggregate re-converges.

The source already records this class of failure for a sibling object: the
comment at the state writer explains that `newborn_parent_share` is built by
the aggregation, which runs AFTER the distribution, so a fresh process used the
declared default and "switched the intergenerational channel off at every
restart" until it was given its own file.

## THE USABLE CONSEQUENCE: A CONVERGENCE INDICATOR THAT LEADS THE MOMENTS

`bequest_residual` walks back monotonically toward its settled value while b
and lambda_d swing. Watch it instead of the moments when judging whether a
restart has finished re-settling. On this run the pre-reboot settled value was
**1.4771**.

## AND THE RULE THAT FOLLOWS

**Do not restart a benchmark that is making progress.** The cost is not the
minute of relaunch, it is several blocks of bequest re-convergence plus the
moment transient behind it. Five of today's eight restarts were chosen rather
than forced, and three of those were errors -- the wrong handover filename, the
handover-less resume, the full-handover resume.

# THE ONSET DOES NOT FOLLOW ITS OWN GAP, AND THAT IS NOT A BUG, 23 September

`oc2c0` fell for six straight blocks -- b through -8.7, -12.8, -15.1, -20.3,
-21.8, -27.2 -- while `addiction_scalar_1` was UNWINDING, which should have
raised use. The reason is the other instrument, and it took three wrong calls
on "the bottom is close" to go and look.

## THE RULE IS AN ASSIGNMENT, NOT AN INCREMENT

At 49052:

    cap_old_1 = addiction_onset_base
    addiction_onset_base = onset_at_mean_1
    addiction_onset_base = cap_step_rel(addiction_onset_base, cap_old_1,
                                        drug_block_max_rel_step)

`addiction_onset_base` is SET to `onset_at_mean_1`, the onset evaluated at the
model's mean drug quantity, and then capped to a relative step. It is not
`parameter +/- adjuster * gap` like every other instrument.

## SO THE PRINTED DIRECTION WORD IS A LABEL, NOT THE MOTION

The `RAISED` / `LOWERED` text in the same write is computed separately, from
`model_fraction_addicted(1) < sud_rate_data`. It says what the rule WANTS.
The value moves toward `onset_at_mean_1`. **The two can disagree with nothing
wrong**, and they currently do:

    0.033094  LOWERED
    0.032929  RAISED   <- lower than the line above
    0.032764  RAISED   <- lower again
    0.032600  RAISED   <- lower again

The same pattern is in `oc1c0`, so it is not specific to this run.
CLAUDE.md already warns that the onset's sign LOOKED backwards once, was very
nearly "fixed", and was measured correct, with an earlier round having spent
nineteen loops paying for exactly that mistake. **Do not "fix" it.**

## WHAT IT MEANS FOR THE CALIBRATION

There is a self-reinforcing loop: use falls, the mean drug quantity falls,
`onset_at_mean_1` falls, the onset base follows it down, fewer households
develop a disorder, and use falls further. The disorder stock is part of b, so
this shows up directly in the targeted moment.

The scalar's unwinding fights it, and at the observed 0.37 per cent a block
against the onset's 0.5 per cent it is currently LOSING. That is the whole
explanation for a descent that outran three predictions of its bottom.

**A COOLDOWN GATES THE ONSET.** `blocks_since_onset_step < b_step_cooldown`
holds it for some blocks between steps, and the comment at that gate records
why: the counter was added to stop the onset stepping every block when the
model needs four to settle, and "it overshot to never". So the onset moves in
bursts, which is another reason block-to-block pattern reading misleads.

## THE LESSON, WHICH IS THE THIRD TIME TODAY

Watching one instrument and inferring the dynamics from the moment is how all
three wrong "the bottom is close" calls happened. When a moment moves against
the instrument you are watching, ANOTHER instrument is moving -- look at all of
them before reading the pattern.

# THE ONE-CLASS omega_c = 0 POINT, ACCEPTED BY THE AUTHOR, 23 September

*"These are ok. Both within 10%"*.

    instrument             value
    addiction_scalar_1     5.4623508156177907E-003
    addiction_onset_base   3.2890778075819450E-002

    moment                 model      target     gap
    b, total drug users    0.096256   0.10502    -8.3%
    lambda_d, disorder     0.039614   0.043424   -8.8%

**IT IS A POINT, NOT A CROSSING**, which is the distinction that matters and
that this session got wrong once already. Its last three blocks:

    block_move 0.03877   b 0.096133   lambda_d 0.039707
    block_move 0.00330   b 0.095816   lambda_d 0.039638
    block_move 0.00459   b 0.096256   lambda_d 0.039614

The block move fell by an order of magnitude and the moments held within half a
point while `addiction_scalar_1` sat frozen at 5.4623508156177907E-003. Compare
block 14 of the same run, which read b -4.9 per cent and lambda_d +0.1 per cent
and was reported here as converged: the instrument was frozen there too and the
distribution was still FALLING, and two blocks later the same model was at
-11.9 and -8.0. A moment near its target on a moving sequence is not a
calibrated moment.

## THE STOPPING STANDARD FOR THE TWO-CLASS RUN FOLLOWS FROM THIS

The author's test is BOTH MOMENTS WITHIN TEN PER CENT WITH THE SEQUENCE FLAT,
not `block_move` under the Fortran's `frozen_stop_tolerance` of 1e-3. The
one-class point was accepted at a block move of 0.0033 to 0.0046, three to five
times the Fortran's rule, so chasing 1e-3 on the two-class run would spend many
hours buying precision the author has said is not needed.

`oc2c0` is judged the same way: b and lambda_d both inside ten per cent, held
across three consecutive blocks with the block move an order of magnitude below
its opening value.

## WHAT THE ONE-CLASS RUN WAS FOR, AND WHAT IT SETTLED

1. One class and two classes track each other to within a point or two at the
   same `omega_c` through the whole transient, so carrying `b` across the class
   count is legitimate. That was its purpose.
2. The converged scalar is WELL BELOW 0.0055 -- the model settles about 8.5 per
   cent under target at that value -- which is why the two-class run's rise to
   0.0056 was flagged here as an overshoot before it turned into one.

# A BENCHMARK RUN ENDS AT TWENTY LOOPS, AND THEN THE WELFARE CURVE HALTS IT,
# 23 September

Two separate things, and the first is not a fault at all.

## TWENTY LOOPS IS TEN BLOCKS, AND THE RUN STOPS THERE

`oc2c0` ended after 10 moment blocks with an EMPTY stderr, which looked exactly
like the 05:14:52 silent death. It was not. `loop_count` reached 20 and a block
is TWO loops, so the run had simply finished its allotment. It wrote the
COMPLETE benchmark first -- every `*baseline_benchmark.dat`, the value
functions, the policy functions, the stationary distribution, every aggregate,
stamped 09:29 to 09:30 -- so nothing is lost and the calibration resumes.

**RESUMING IS ONE COMMAND IN THE RUN DIRECTORY.** The state file and the
distributions are already there and the handover has been consumed, so
`nohup ./hftf > run.log 2> run.err &` continues it. Confirm with:

    grep -a "resumed from calibration_state" run.log   # "written after loop 20"
    grep -a "addiction_scalar_1=" run.log | head -1    # the CALIBRATED value

Preserve the old log first; the relaunch truncates `run.log`.

**SO AN EMPTY STDERR PROVES NOTHING ON ITS OWN.** Before calling a stop a
crash, read the END of run.log. A run that reached its loop limit says
`loop_count= 20`; a run that failed the welfare curve's null says `CEV NULL
FAILED`; both leave stderr at zero bytes because both are `stop`, not a signal.

## THE WELFARE CURVE'S NULL CHECK FAILS, AND IT BLOCKS kappa_x

After `save_vars_and_functions(1)`, a benchmark calls `save_welfare_curve(1)`
at 52325, gated only on `use_old_results==0`. That is the 21-point curve of
CALIBRATION_RECIPE.md section 5 -- the `kappa_x` probe. At x = 0 nothing is
scaled, so the curve must reproduce the welfare the model just reported. It
does not:

    adult      curve 1363.2055   reported 1351.7308   0.85 per cent
    childhood  curve  454.1325   reported  451.2884   0.63 per cent
    lifetime   curve  788.7948   reported  780.0421   1.12 per cent

The tolerance is `10.d0**(-6)` relative and the code does a hard `stop` at
22858. ALL THREE disagree, not only the childhood half the message names --
which matters, because the comment at 22843 says both halves are checked
precisely so that a curve matching on the total while the halves are wrong
cannot pass.

**CONSEQUENCES.** `kappa_x` cannot be recomputed until this is understood, so
task 10 is blocked on it rather than on the benchmark. Every benchmark run will
halt here, which is harmless for the calibration -- the `.dat` files are
written BEFORE the check -- but means a run must be resumed rather than left to
finish. The `omega_c` scan is NOT blocked by it: a scan point reads the
benchmark's saved vector and never needs the curve.

**NOT YET INVESTIGATED, AND THE OBVIOUS FIRST QUESTIONS.** Whether this predates
today, since the archive has a benchmark of record that must once have passed;
whether it is peculiar to `omega_c` = 0, since the message names the childhood
half and `weight_on_child` is zero here; and whether a NON-CONVERGED point can
fail it legitimately, since `oc2c0` stopped mid-calibration at b +1.4 per cent
rather than at a fixed point. The note at 22880 records that
`save_welfare_curve` once had NO CALLER at all, so this path is young.

# SIX THREADS ON FOUR CORES LIVELOCKS THE DISTRIBUTION LOOP, 23 September

**Every launch script caps threads at two.** `oc00_run.sh:22`,
`oc055_bounds_run.sh:13` and `oc1c0_run.sh:19` all carry
`export OMP_NUM_THREADS=2`. The first version of `oc2c0_run.sh` did not, so
libgomp took its default of `nproc` = 4, and with `oc1c0`'s two that put SIX
threads on FOUR cores.

**THE SYMPTOM IS NOT A CRASH AND NOT A SLOWDOWN. IT IS A DEAD STOP.** The run
burned 2.3 cores for twenty-five minutes and produced not one line of output.
The value function had already finished two full age sweeps at 14 seconds an
age; the hang was in `converge_to_stationary_equilibrium`, the DISTRIBUTION
iteration. It resumed within seconds of the other solve being stopped, and the
diagnosis is not an inference -- three `gdb` samples minutes apart all showed:

    #2  GOMP_parallel
    #3  converge_to_stationary_equilibrium (time_period=1) at 32652
    #4  calibrating_model () at 47794

with ALL FOUR threads parked in `libgomp`. Master finished its chunk, every
worker finished its chunk, and everyone spun at the implicit barrier waiting
for a thread the kernel had descheduled to make room for the other solve's
threads. Spinners eat the core the straggler needs to arrive on.

**WHAT THIS RULES OUT, WHICH MATTERS BECAUSE IT WAS ABOUT TO BE BLAMED.** It is
NOT the optimiser: `oc00/hftf` is byte-identical to `build2c/hftf`, the plain
`-O3` build, and it ran three blocks. It is NOT the joint loop: `oc055_bounds`
is joint and completed a block. It is NOT two classes: all of the above are.
The pattern "joint under -O3 fails" was a coincidence of which runs happened to
be staged by hand without the cap.

**THE RULE.** No solve starts without `OMP_NUM_THREADS=2`, and the box takes at
most TWO solves -- four cores, two threads each, no oversubscription. A run
already holding four threads blocks any second solve until it ends.

**HOW TO TELL A LIVELOCK FROM A LONG BLOCK.** A healthy solve writes an
`AGE_TIME` line every ~14 seconds through the value function; through the
distribution it writes less often, so use CPU and the stack, not the log:

    ps -o pid,etime,time -p <pid>        # cpu climbing, wall climbing: it is burning
    grep -c AGE_TIME <dir>/run.log       # compare against 118 at the first moment
    gdb -p <pid> -batch -ex "bt 6" -ex detach

All threads in `libgomp` with no frame in the model's own code is the signature.
This is what `build2c/hftf_trace` and its `-g` were built for, and it earned
its keep here on a hang rather than the crash it was made for.

**THE 05:14:52 SILENT DEATH IS STILL OPEN.** A livelock does not kill a
process, so this does not explain that one. What is settled about it: not a
bounds or pointer fault (`oc055_bounds` completed a block under
`-fcheck=bounds,pointer`), and mute because the standing `-O3` build carries no
`-fbacktrace`.

# CORRECTION: THE ONE-CLASS POINT WAS NOT CONVERGED, 23 September 07:15

The section below this one calls the one-class `omega_c` = 0 point converged on
both drug moments at `addiction_scalar_1` = 0.0054962. **That was wrong and is
withdrawn.** The next two blocks kept falling:

    block 10   b  +3.2%   lambda_d  +8.0%
    block 11   b  +1.5%   lambda_d  +5.7%
    block 12   b  -0.6%   lambda_d  +3.9%
    block 13   b  -0.4%   lambda_d  +2.8%
    block 14   b  -4.9%   lambda_d  +0.1%
    block 15   b  -9.2%   lambda_d  -4.5%

`addiction_scalar_1` was frozen at 0.0054962 across blocks 14 and 15, so this
is the SAME settling that closed the gap from +23.5 per cent -- it simply did
not stop at the target. Blocks 12 to 14 looked converged only because a falling
path sits near zero while it crosses.

**THE LESSON, WHICH IS GENERAL.** A moment near its target is not a converged
moment. On a monotone trajectory with the instrument frozen, proximity says
nothing; the test is whether the SEQUENCE has flattened, not whether the latest
value is small. Three readings near zero on a falling path are three points on
the way past.

So the one-class answer is NOT 0.0055. That scalar is too HIGH -- the sign is
reversed, a higher scalar means less use -- which is why b now undershoots. The
converged value lies between the declared 0.0049192 and 0.0055, and the loop
has begun walking it back down.

None of this touches the two-class benchmark `oc2c0`, which calibrates its own
`addiction_scalar_1` from the declared value and was never going to inherit
this one.

# THE ONE-CLASS omega_c = 0 POINT IS CONVERGED, 23 September 07:05

Step 1 of the author's run order -- *"go back to the one-class model, play with
b a bit to bring down the use rate to target with omega_c=0"* -- is answered.

    moment                     model       target      gap
    b, total drug users        0.099849    0.10502     -4.9%
    lambda_d, disorder rate    0.043484    0.043424    +0.14%

    instrument             calibrated     declared     move
    addiction_scalar_1     0.0054962      0.0049192    +11.7%
    addiction_onset_base   0.0330975      0.0336007    -1.5%

Both moved the way the Fortran's own rules say: the scalar UP to cut use
(remember the sign is reversed -- lower b means MORE use), the onset DOWN to
cut the disorder rate. The loop now oscillates inside a few per cent of both
rather than travelling.

**THE APPROACH WAS THE SETTLING, NOT THE ADJUSTER.** Blocks 6 to 12 closed b
from +23.5 per cent to -0.6 while `addiction_scalar_1` moved 0.4 per cent. The
instrument's real move was made in the noisy opening blocks; everything after
was the stationary distribution settling toward the post-`mu_m`-wiring point.
Do not read an elasticity off those blocks -- it is the settling.

## THE SCAN CANNOT START UNTIL oc2c0 CONVERGES, AND NOT FOR A CAPACITY REASON

A JOINT run refits b to 0.10502 whatever `omega_c` is -- that is what
`oc055_bounds` was doing -- so two joint runs at different `omega_c` measure NO
reduction, by construction. The experiment is: calibrate ONCE at `omega_c` = 0,
then HOLD every parameter and raise `omega_c`. The scan's input is `oc2c0`'s
converged vector.

This also re-reads `oc00` against `oc055`: those two ARE a held-parameter pair,
the same vector at `omega_c` 0 and 0.055, and they give a fall of 11 to 21 per
cent depending which blocks are taken. The author's 18 sits inside that range.
Too noisy to quote, but the right shape.

## A READOUT BUG THAT WAS MINE, NOT THE MODEL'S

Block 14 was first reported as `b = 9.98`. The monitor's pattern was
`model= *[0-9.]*`, with no exponent in it, and b prints as
`9.9849024975901174E-002` once it falls below 0.1 -- so the readout dropped the
exponent and multiplied by a hundred. It had never bitten because b had never
been under 0.1. `paper/calibration_report.py` does NOT have this bug: it parses
`([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)` everywhere, exponent included,
so the gaps table is sound. Any ad-hoc log scraper needs that pattern.

## THE HANDOVER FILE IS CONSUMED BY THE READER

`PARAM_HANDOVER.txt` is gone from a run directory after startup: the reader
consumes it and each block end writes `PARAM_HANDOVER.relaunch.txt` for the
next relaunch. That is WHY every launch script copies the `.relaunch.txt` to
the `.txt` first, and why a directory holding only the `.relaunch.txt` looks
correctly staged when it is not.

# TWO CLASSES IN THE SOURCE, AND THE omega_c = 0 BENCHMARK IS RUNNING, 23 September

`child_penalty_classes` is back to **2** in
`housing_first_or_treatment_first_SR_v1.f90` at line 6205. It was 1 for the
one-class b search and the search is now a side run, not the master.

## WHAT THE FOUR RUNS SAY ABOUT omega_c

Against b's target of 0.10502 and lambda_d's of 0.043424:

    run            classes  omega_c  loop     b                lambda_d
    oc1c0          1        0        joint    0.1297 - 0.1343  0.0552 - 0.0569
    oc00           2        0        frozen   0.1354 - 0.1370  0.0565 - 0.0569
    oc055          2        0.055    frozen   0.1070 -> 0.1205 0.0431 -> 0.0500
    oc055_bounds   2        0.055    joint    0.1097           0.0457

**Like for like at omega_c = 0, one class and two classes are within three per
cent**, so the author's plan -- tune b cheaply at one class, carry it to two --
is sound. An earlier reading that the two-class model needed far less
adjustment compared 0.055 against 0 and is WITHDRAWN: the gap is omega_c, not
the number of classes.

**NO REDUCTION IS QUOTED FROM THESE.** `oc055` moves 0.1070 to 0.1205 between
its own two blocks, as far as the distance between the two omega_c values.
All four warm-started from the pre-wiring distribution and `mu_m` has since
changed the SUD recovery hazard, so the stock is still settling and the
block-to-block drift is the settling, not the instrument.

## WHAT IS RUNNING

    oc1c0   1 class, omega_c 0, joint, -O3          the b search, pid 569
    oc2c0   2 classes, omega_c 0, joint, TRACEBACK  the benchmark of record

`oc2c0` starts from the DECLARED `addiction_scalar_1` and is not seeded toward
the value b's gap implies; the loop's own bracket is the measurement.

## THE CRASH HUNT

The silent death of 23 September at 05:14:52 is **not a bounds or pointer
fault**: `oc055_bounds` re-ran that configuration under
`-O1 -fcheck=bounds,pointer` and completed a full moment block. The mute part
is explained -- the standing `-O3` build carries no `-fbacktrace`, so there was
no handler to print anything. `build2c/hftf_trace` is `-O3 -funroll-loops -g
-fbacktrace`, and it is what `oc2c0` runs under.

# THE MODEL IS RESTORED AND TWO CLASSES AGAIN, 23 September 04:10

The SMI block is settled and the source now carries it. Everything below this
section predates the restoration and is kept for the record.

## THE CONFIGURATION

    iota_smi               2.0    a SUD raises the hazard of SMI onset
    mu_m                   0.82   SMI lowers the SUD recovery hazard, AND WIRED
    b_smi_multiple         1.0    b_smi = b, no SMI-specific drug preference
    zeta_DI                0      no disability income for SMI
    child_penalty_classes  2
    penalty_child_addicted 0.24
    omega_c                pinned, run at 0 and at 0.055

`iota_smi` and `mu_m` are the values git records before 875750f4 made SMI
exogenous: the paper's external two from Nielsen et al. (2017), and Bradizza's
relapse rates at (1-0.398)/(1-0.264) = 0.818. Neither was invented here.

## THE BUG THAT MADE ANY OF THIS NECESSARY

`mu_m` was never wired. `addiction_transition` takes `smi_1` as an OPTIONAL
eighth argument and ELEVEN OF FIFTEEN call sites dropped it; the four that
passed it are all in `govt_revenues_calc`, so the household's value function and
the stationary distribution never saw it and no value of `mu_m` had ever moved
an equilibrium. Measured: `mu_m` at 0.10 against 1.0 reproduced every cell of
the drug-state table to four decimals and moved `r_smi` from 1.7792 to 1.7790.
`code/patch_wire_mu_m.py` closed it and refuses to run twice.

**So the two-class fix-only benchmark's `r_smi` of 2.062 was produced by `iota`
alone.** Wiring `mu_m` is new ground and should lift it.

## WHY `b_smi` IS OFF, WHICH IS THE RESULT THAT SETTLED THE WHOLE QUESTION

At `b_smi = 1`, no SMI-specific preference anywhere, the model produces a drug
USE ratio of **2.715 against the data's 2.44**. It overshoots rather than falls
short. The SMI drug-use gradient is ENTIRELY ENDOGENOUS -- SMI lowers employment
and income, poorer households use more -- so it is a prediction, not a fitted
moment, and it goes in the UNTARGETED table on the author's instruction.

The whole `b_smi` ladder was driving a moment that was already on target past
it, to 7.82. Six points, 0.20 down to 1e-12, settle the SUD ratio at 3.58 and
cannot reach 7.30; `b_smi = 0` exactly is a crash, not a corner.

## WHY 7.30 WAS THE WRONG TARGET, WHICH IS THE AUTHOR'S FINDING

*"maybe it's the death rate?"* It is. Exit from the disorder runs 0.1137 a year
for SMI users against 0.0420 for non-SMI users, and exit is recovery PLUS
DEATH: the survival print at age 40 puts a clean housed household at 0.0128 and
an SMI homeless household with a SUD at 0.1127, a gap of 0.0999 that accounts
for essentially all of it. NSDUH measures LIVING RESPONDENTS, so a model with
honest excess mortality undershoots a survey-based severe prevalence ratio by
construction.

Making them poor does not fix it either: `kappa_uem` at 23.5 drove employment
given SMI from 0.81 to 0.15 and more than doubled homelessness, and `r_smi`
went DOWN, 4.014 to 3.924. Extra entry and extra death cancel.

## THE RUN ORDER, AND WHERE IT IS

    1. omega_c = 0 and omega_c = 0.055, two classes      <- RUNNING, warm started
    2. read the gaps tables; continue unless materially different from before
    3. compute kappa_x
    4. omega_c = 1
    5. full internalisation of homelessness, kappa_x borne by the homeless
    6. Treatment First
    7. the transition at T = 60

Both runs are warm started from `seeds/benchmark_dat`, whose stationary
distribution is byte-exact against the warm-start reader at 265,496,400 and
23,894,676, with the shape stamp written beside it because an unstamped pair is
refused. Both loaded, `sum = 50.861206888360229`.

**STILL OPEN AND WORTH DOING: the steady state has no value-function warm
start.** It reads `calibration_distribution1/2.dat` and nothing else, so a
restart pairs a warm distribution with a cold value function. The archive
carries `value_function1/2baseline_benchmark.dat.gz`, but `use_old_results` is
1 only for a counterfactual, so a benchmark solve never reads them. The author
asked for both the steady state and the transition to read the old files. It is
a starting guess, so it cannot change a converged equilibrium -- only how fast
it arrives.

# THE 20 SEPTEMBER T=30 IS VOID. THE FAIR-MARKET-RENT CAP WAS BROKEN

21 September. The archive disagrees with what this file said yesterday, and the
archive wins. Everything below the first two sections is what survives.

## WHAT WAS WRONG

The counterfactual's housing voucher is capped by a fair-market-rent standard.
The benchmark builds that standard from its own calibrated average rent times
its own calibrated average rental unit size. The counterfactual was rebuilding
it every period from `model_average_rent(t)*model_average_rental_unit_size(t)`
-- its OWN drifting product -- so the cap moved with the equilibrium it was
supposed to discipline, and in a transition it collapsed. Four defects, all
closed and each committed separately:

    a65b9dd4  median_income was never declared for the transition
    c463dd20  the eligibility cutoff's median income was computed off the
              wrong denominator
    cbc96395  the standard now reads the BENCHMARK's calibrated rent and
              calibrated unit size in every counterfactual
    f05451d5  the same two are pinned at the source, after the normalisation,
              so nothing downstream can re-derive a drifting one

The author's instruction was the whole of it: *"No, the formula has to be the
same as the benchmark... The rent is identical..."* and *"use the same model
average rental size as the benchmark. Pin it so the counterfactual uses the
same rule."*

## THE CONTROLLED PAIR, T=5, ONE SOURCE CHANGE

Same benchmark, same handover, same binary settings, controls stated before the
run:

                      pre-fix      post-fix
    vouchers t=1      0.63943      0.65572
    vouchers t=2      0.000000     0.66355
    lifetime t=1      790.873      792.194     (benchmark 791.39464)
    lifetime t=2         --        792.521
    CEV      t=1       -9.272%      +2.306%
    CEV      t=2          --        +3.273%    (long run +3.249%)
    budget residual     0.445       0.0327 / 0.0241 against a rule of 5e-2

    FMR standard, both periods: avg_rent 1.0000000
                                avg_unit_size 0.30208980094400001

At t=2 the pre-fix path paid NO vouchers at all. **Treatment First is welfare
improving at t=1 once the cap is fixed.** The -9.27 per cent that this file
reported yesterday, and that the grandfathering arm's entire rationale rested
on, was the collapsing cap and not the reform.

## WHAT THIS VOIDS

- The welfare column of the 20 September T=30 -- -9.272%, -11.46%, -12.15%,
  recovering to -2.223% at t=29 -- in full. There is no trough.
- The grandfathering brief. Its question has inverted from *how much of the t=1
  loss does it recover* to *how much of the t=1 gain does it forgo*, and the
  pre-fix evidence already had homelessness HIGHER under grandfathering
  (0.008747 against 0.007713 at t=1) because the exempt lose the deterrent.
  Its `CONTROL.md` acceptance numbers were measured on the broken cap and are
  stale.
- The quantity path -- h_1, b, lambda_d by period -- is not known to be wrong,
  but it is not verified either. At T=5 the quantities barely moved (h_1 +18.75%
  at t=1 post-fix against +19.4% pre-fix at T=30) while welfare inverted. Do not
  quote the 20 September quantity path as a result until the rerun lands.

## IN FLIGHT

**THE MODEL HAS CHANGED THREE TIMES SINCE THE 20 SEPTEMBER BENCHMARK.** The SMI
mortality double count is fixed; the model is one class with omega_c pinned at
zero; and SMI is exogenous, `iota_smi` and `mu_m` both at one. All of these are
DECLARED values in the Fortran, not vector entries, which is what makes a
resume come back as the same experiment.

**THE COMORBIDITY TARGET IS 7.30**, computed from the repo's own NSDUH file at
26+ on the same `svyrdudany` cut the level targets use, universe check passing
at 0.0890 and 0.0368. Full account and the whole verification trail in
`data/SMI_SUD_TARGET.md`. Data decomposes as entry 4.51 times persistence 1.62.

**WHERE THE RATIO HAS BEEN**, all measured, all on the benchmark switches:

    archive benchmark, two class                        0.596
    + mortality fix only, two class                     2.062
    + one class, iota_smi=1, mu_m=1, mid-calibration    1.656   loop 12 checkpoint
    same, the worker's block 1                          1.779
    TARGET                                              7.30

**THE AUTHOR'S DECISION, 23 September: BOTH SMI-SUD MULTIPLIERS STAY AT ONE.**
*"ok, we say it stays at 1"* on `mu_m`, and *"and no extra SMI risk with SUD"*
on `iota`. So SMI is exogenous to everything a policy does, a SUD does not
raise the hazard of SMI, and SMI does not slow recovery from a SUD. The whole
comorbidity ratio has to come from the endogenous employment and income route
plus `b_smi`.

**THIS FILE PREVIOUSLY SAID "Removing `mu_m` cost most of the rise" IN THE
RATIO, FROM 2.062 TO ABOUT 1.7. THAT IS WRONG AND IT IS WITHDRAWN.** `mu_m`
cannot have cost anything: it is not wired into the household's problem or into
the stationary distribution, only into `govt_revenues_calc`, so no value of it
has ever moved an equilibrium. Measured on a controlled point -- same vector,
`mu_m` compiled at 0.10 against 1.0 -- every cell of the drug-state table is
identical to four decimals and `r_smi` moves 1.7792 to 1.7790, which is the
no-op threshold. Full account in
`results/smi_comorbidity/MU_M_IS_NOT_WIRED.md`. The earlier claim came from a
comparison that also switched two classes to one and set `iota_smi` to one, and
attributed the whole move to the one parameter incapable of producing any of
it.

`iota_smi` was checked for the same fault and is fine: `smi_transition` has one
call site, passes all four arguments, and builds the table everything else
reads.

**THE PAPER NOW ASSERTS SEVERAL THINGS THESE TWO DECISIONS MAKE FALSE**, and
they are listed for the author rather than edited, because the model section is
theirs. `\iota>1` at 1616; `\mu_m<1` at 1564; the `\iota` entry at 2351 which
calls it "the hinge of the whole block" and states it is set externally at two;
the `\mu_m` entry at 2415; `\rho_m` at 2389, whose only route to the
comparison is through `\iota`; the SMI channel list at 1626; and 2687, "what
this paper adds is `\iota` ... and that is where the interaction lives".

**THE CHANNEL IS BUILT AND LIVE.** `b_smi_multiple`, an SMI-specific multiple on
`addiction_scalar_1`, with its moment `MOMENT r_smi`, its gaps row, its bracket
and its persistence in `calibration_state.dat`. Three things about it that are
easy to get wrong and are written at the code rather than only here:

  - **THE BRACKET'S SIGN IS REVERSED.** b enters as (b+q)^phi_q so the marginal
    value of the first unit goes like 1/b: a LARGER multiple means LESS use and
    a LOWER ratio. Parameter and moment move in opposite directions and the
    update ADDS the gap. Same trap as `kappa_phi_d_level`.
  - **IT READS `smi_of(unemployment_index)` RATHER THAN TAKING AN ARGUMENT**, to
    avoid forty silent hand edits. The cost is that `b_shifter` is no longer a
    pure function of its arguments. The gate is DIRECTIONAL, not a no-op: move
    the parameter and check SUD|SMI moves hard while SUD|non-SMI barely does.
  - **IT PERSISTS AT THE TAIL OF `calibration_state.dat`, WITH ITS ADJUSTER.**
    Without that every resume reset it to 1.0; without the adjuster a resume
    came back HELD while still looking like it was running.

**WHERE THE SMI BLOCK STANDS AT 03:25, 23 September.** The ladder is finished
and settled, DI income has been tested, and one question is open.

    b_smi_multiple   r_smi block 1   r_smi settled
        0.20             3.2589          --
        0.01             3.5506          --
        0.001            4.0057        3.5752   block 4
        1e-5             4.0094        3.5769   block 4
        1e-12            4.0140        3.5809   block 4
        0 exactly        VOID -- value_of_life NaN, 94 per cent homeless
                                      TARGET 7.30

Seven decades of `b_smi` and three settled ratios inside 0.16 per cent of each
other. The channel is exhausted at about 3.58.

**DI INCOME DOES NOT MOVE IT.** `zeta_DI = 0.25` leaves `SUD | SMI` at 0.2278
against 0.2278 at zero; the ratio slips two per cent only because the
denominator rises. The author has since set the expected payment the parameter
was built for, `3/12 * 0.25 = 0.0625`, and that run is in flight -- for the
model's realism, not for the ratio, since four times the payment did nothing.

**THE LEAD IS `kappa_uem`.** `MOMENT kappa_uem employment given SMI` prints
0.80826 against a target of 0.30000. `kappa_uem` is 1.0554 where one means no
penalty at all, and `kappa_uem_adjuster` is zero IN THE DECLARATION, so nothing
moves it in any configuration. With `iota` and `mu_m` both fixed at one, the
endogenous employment-and-income route is the ONLY SMI-to-SUD channel left, and
it is being fed a group that is employed four fifths of the time against three
tenths in the data. That is the referee's concern in the model's own numbers.

**OPEN, AND IT IS A POSSIBLE BUG RATHER THAN A RESULT.** At `b_smi = 1e-12` an
abstaining SMI household's flow factor is 170 times a buyer's, and 81 per cent
of them are employed, so on the author's argument essentially all of them should
buy. Two inferences from stocks disagree on how many do -- 0.59 from
`r_smi = u_SMI/u_non`, 0.34 from the never-disordered stock and the flat 0.0336
onset hazard. `code/u_probe` is measuring it: `xtab_exp_mass_smi` is accumulated
at 19305 every block and printed only on the transition path at 54973, so three
WRITE statements in a private copy put it in the steady-state block. If
participation comes back near a third with 81 per cent employed, look for a bug
before reaching for an explanation.

**THE SWEEP WAS RUN AND IT SETTLES THE QUESTION: `b_smi` CANNOT REACH 7.30.**
Five points, every one of them with the other forty seven adjusters frozen, so
each is the single-parameter test ENGINE.md's phase 3 rule 1 asks for:

    b_smi_multiple   r_smi   SUD|SMI   SUD|non-SMI   read at
        1.00         1.779    0.0900      0.0506     block 1
        0.50         2.384    0.1436      0.0602     block 6, BLOCK MOVE 1.4e-2
        0.20         3.259    0.1809      0.0555     block 1
        0.05         3.300    0.2093      0.0634     block 8, BLOCK MOVE 9.4e-3
        0.01         3.886    0.2229      0.0574     block 1
                              TARGET 7.30

`SUD|SMI` SATURATES. A twentyfold cut in the multiple, 0.20 to 0.01, buys
twenty three per cent on it. A ratio of 7.30 against a non-SMI rate of 0.057
needs `SUD|SMI` at 0.42 and the SMI rate is levelling off near 0.22. The 1e-6
floor in the update is not what stops it.

THE MARGIN IS THE REASON. `b` enters as `(b+q)^phi_q`, so cutting it raises the
marginal value of the first unit and raises USE. Whether a user becomes
DISORDERED is the onset hazard, and at `iota_smi = 1` an SMI household faces the
population's. At a multiple of 0.20 the model already has
`model_experimenters/model_total_drug_users` at 0.604: the extra use `b_smi`
buys arrives as experimentation, which the ratio does not count.

**SO THE INSTRUCTION OF 22 SEPTEMBER CANNOT BE CARRIED OUT AS STATED** --
remove the higher SUD risk with SMI, remove the lower recovery with SMI, and
pick `b` to match 7.30. The first two removals are what make the third
impossible. Three ways forward are written out in
`results/smi_comorbidity/B_SMI_SWEEP.md` and the choice is the author's; nothing
has been changed pending it.

**THE 0.20 AND 0.01 RATES ARE READ, NOT DERIVED.** `code/smi_sud_xtab.py`
decodes `calibration_distribution1.dat` into the four masses `r_smi` is built
from. The 0.5 and 0.05 rows had to be backed out of `lambda_d`, `p_m` and
`r_smi`, which is exact only if the cross-tab's population base coincides with
`model_fraction_addicted`'s -- accumulated in different subroutines and never
checked. The decode is controlled against the model's own print: 3.2589 against
3.2588654628626594 at 0.20, and 3.8856 against 3.8855666636818813 at 0.01.

**READ A POINT AT ITS BLOCK COUNT.** The ratio drifts DOWN as the equilibrium
settles -- 2.657 at block 1 against 2.384 at block 6 on the 0.5 point -- and the
drift is entirely in the DENOMINATOR: `SUD|non-SMI` rose eleven per cent over
the 0.05 point's eight blocks while `SUD|SMI` sat inside half a per cent. It
does not touch the finding, because the saturation is in the column that does
not drift.

**`b_smi_multiple` HAS A GAPS ROW NOW**, which it did not before: its distance
is RELATIVE so `pairs()` never discovered it, its adjuster is DECLARED zero and
turned on from the handover so the held test dropped it, and it prints on the
same line as its own distance so its value column was empty. All three are
closed in `code/paper/calibration_report.py`, each with a before-and-after
control on a frozen log and a joint log.

**THE CONTAINERS REBOOT, BUT NOT AT THE FIRING TIMES** -- that reading was
measured false and corrected at the top of ENGINE.md. This container booted at
01:28 and has carried two solves through several turn boundaries since. Nothing survives a kernel reboot, so every solve
runs in a worker session and this one coordinates only. See the entry at the top
of ENGINE.md.

## THE HORIZON IS NOT SETTLED. T=45 IS NOT ENOUGH, AND I SAID IT WAS.

This section said, at 08:11, that "everything is at or past its terminal value
by the early twenties", that T=45 had twenty periods to spare and that post-fix
even T=30 would have sufficed. **That was wrong.** The completed 43-period path
says so plainly:

                  t=44        terminal      gap    closing at    needs
    h_1         -0.39%        +1.31%       1.70    0.155/period   ~11 more
    b          -47.65%       -44.65%       3.00    0.095/period   ~32 more
    lambda_d   -51.23%       -45.20%       6.03    0.260/period   ~23 more

**None of the three has arrived at the last free period.** They CROSS their
terminal values in the early twenties, overshoot by several points, and then
crawl back. I read the crossing as the arrival. Crossing is the start of the
approach, not the end of it.

On those rates participation binds and wants about **T=76**; lambda_d wants ~67
and homelessness ~55.

**So `CALIBRATION_STATE.md`'s original instinct -- "the reported result should be
T=75" -- was right, and I overturned it on a misreading.** What was genuinely
wrong in the old section was the explanation of h_1's +63.9 per cent stall,
which WAS the fair-market-rent cap; the horizon conclusion was not.

The T=30 run was still correctly killed at 02:44 on the author's instruction
(*"i suggest to just go to T=45"*): T=30 is further from enough, not closer.

Caveat: loop 0 of an unconverged run, so the rates may shift as the price path
settles. The overshoot-and-slow-return shape should be robust, since it is
cohort turnover rather than prices.

**The horizon is an open scope question for the author.** T=76 is about 8 hours
a loop against 4.7, so roughly 40 hours for five loops against 24. Whether it is
worth it depends on whether the paper reports a converged lambda_d or a welfare
path over the first few decades; the second is unaffected by a tail still
settling.

## WHAT THE AUTHOR ESTABLISHED ABOUT THE MODEL, 21 September

**The transition solves for TWO objects, not five.** *"rent and housing price
and lump sum transfer are not equilibrium objects, they are constant"*, and
*"i can only think of 2: pi_v and p_v"*. `peg_prices_in_counterfactual=1` pins
the house price and rent and ZEROES their distances, so two of the four stopping
rules never bind; lump_sum_transfer is never assigned inside the loop. I had
claimed three of four rules belonged to them. See
`results/transition_t30_nogf/TWO_OBJECTS_NOT_FIVE.md`.

**And homelessness is not one either.** *"once pi_v and p_v converge,
homelessness is what it is and is applied to the welfare"*. The code already
does this: h_1 is written every loop as a reference and never read back.

## WHAT SURVIVES FROM THE 20 SEPTEMBER RUN

**The secant seed.** `distance_drug_market` at t=1 came in at 0.031346 against a
test of 0.21730, and the mean across 29 periods was 0.01351 -- fifteen times
better than the ramp's 0.2027 and the supply curve's 0.4878. The cap stopped
binding, so no fourth reseed was needed. This is a property of the seeding, not
of the voucher, and the fix does not touch it.

**The control on the drug price, which is a result in itself.** h_1 at t=1 was
0.0077265 at p=0.777 and 0.0077137 at p=0.927: a 0.17 per cent move in
homelessness across a 19 per cent move in the price. Homelessness at
implementation is conditionality revoking housing from people still using, and
the price is not a competing explanation. Participation is the opposite --
b went 0.092053 to 0.059749 over the same price move, a 35 per cent fall for a
19 per cent rise, an implied demand elasticity near -1.8 against the -2.3 slope
measured on the supply side. **This model's drug market clears through
participation, not through homelessness.**

**The horizon problem.** At t=29 the price was already the boundary condition,
0.83349, and yet h_1 sat at +63.9 per cent on the benchmark where the terminal
steady state is +1.3. Whether that survives the fix is exactly what the rerun
answers; if it does, the reported result needs a longer horizon and that is a
scope decision for the author.

## CLOSED SINCE THIS FILE LAST SAID OTHERWISE

- **The windowing was compared bit for bit**: 6.075e-05 relative against a rule
  of 1e-4. Windowing the policies to one slot is a no-op on the path.
- **pi_v's update is no longer a fixed damped step.** It carries per-period
  secant state, falls back to a damped 0.05 of the residual, abandons the
  secant when the gap grows, holds a four-step trust region, and applies the
  existing quarter-of-pi_v clip last.
- **The transition's stopping rules were loosened by the author's instruction**
  (*"the convergence rule can be less tight than the long run"*): a factor of
  two on all four, applied only when `solve_transition_dynamics` is on.
- **Paths save and restore**, in Fortran and in `code/save_transition_paths.py`,
  and both refuse a path carrying NaN or a pi_v on a bound.
- **The benchmark `.dat` set is shared**, 90 files, 2.06 GB compressed to 124 MB
  in `code/seeds/benchmark_dat/`, retiring the four-and-a-half-hour cold start.

## THE RUNNING T=30 CARRIES A PRE-FIX TERMINAL CONDITION. QUANTIFIED, NOT FATAL

Found 21 September 02:05, by reading the file the run actually loads. The
transition does not solve its terminal steady state -- it reads `counter_TF`,
and the set in `trans_bench_to_tf/` is dated 19 September 19:21, before any of
the five voucher fixes:

    counter_TF.txt  probability_of_voucher          0.0763466554594919
                    govt_spending_on_housing_vouchers_2  0.68483690499099070

The post-fix arm 3 re-solve gives 0.0768762 and 0.67956504, so the terminal
pi_v this run is anchored to is **0.69 per cent low** and the terminal voucher
spending 0.77 per cent high.

**Why the run continues anyway.** The same controlled re-solve moves the
terminal quantities the backward pass actually needs by almost nothing: b
+0.031 per cent, h_1 +0.153, lambda_d -0.190, and **lifetime welfare by 0.001
per cent** -- four orders of magnitude inside anything that could change a t=1
CEV. A 0.69 per cent error in one instrument's terminal level sits far inside
the transition's own stopping rules and inside the noise of a first,
unconverged loop, and re-solving arm 3 here first would cost hours before the
diagnostic the author asked for could even start.

**What it does mean.** The pi_v panel's last periods inherit a slightly low
anchor, so read the END of that panel as approximate.

**The anchor is now fixed for the NEXT run, 02:11.** A sibling committed
`seeds/PARAM_HANDOVER_trans_postfix.txt` and made `stage_transition.sh` default
to it: `probability_of_voucher_benchmark_used` 0.076876159888350143 against the
old 0.076347, and `drug_price_start` 0.83283631757376753 against 0.83349. Those
two scalars ARE the terminal pin, so a run staged from here carries the
corrected one without needing the `counter_TF` `.dat` set rebuilt.

**The running job was NOT restarted for it, and that is a decision, not an
oversight.** It is thirty minutes into a three-hour loop; the change is 0.69 per
cent on one instrument and 0.079 per cent on the price; and nothing the author
asked this loop to show -- whether homelessness rises, whether use falls,
whether the CEV is positive, whether the path flattens by t=30 -- turns on
either. Paying thirty minutes to move a tail anchor by two thirds of a per cent
in a loop that will not have converged anyway is churn. The next T=30 stages
from the post-fix handover.

## STILL OPEN

- Nothing has converged. No number in the "in flight" section is a result yet.
- pi_v's budget update switches on at loop 1 and has still never run to
  convergence on a path.
- Whether the t=1 gain is the right SIZE. A recipient's voucher is about 67 per
  cent of their income and recipients are 6.3 per cent of the population, so
  abolishing the programme outright is worth roughly 3 per cent of population
  average consumption -- that is the bound the t=1 number has to sit inside.
- The grandfathered arm's voucher code has not been run since any of the five
  fixes.
- `penalty_child_homeless` is 0, so the "children on the street" channel
  transmits no inherited penalty at all. Whether that is intended is the
  author's call and it is not a bug to fix unasked.
- The child's inherited penalty must key on the period the parent DIES in.
  Read, not verified.
- Arms 1 and 2 were run under the loose stopping rules and not re-checked.
