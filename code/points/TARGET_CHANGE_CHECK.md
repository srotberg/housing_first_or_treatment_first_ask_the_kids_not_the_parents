# Is the 2.5 target change a model change? No -- but the point did not reproduce

`wealth_to_output_data` was changed from 3.0 to 2.5 in `5ea693e`, moving the
semantic hash from `2f7c317e75` to `08f8470b5d` and nominally invalidating all
35 archived points on this economy. The claim to be tested was that it
invalidates nothing, because the constant is `beta`'s calibration TARGET and not
a model primitive. `point_35e8286c4e` was re-measured on the new source and
compared with its archived measurement, moment by moment.

## Verdict

**NOT IDENTICAL.** The archived file and the new file disagree on 22 of 23
targeted moments, on 119 of the `DIAG` lines and on 41 of the `UNTARGETED`
lines. The worst targeted moment is `w_bot` at **1.85e-02** relative -- 360
times the 5.13e-05 run-to-run bound in `DETERMINISM.md`, and an order of
magnitude past the 1e-3 that file calls real. Nothing here is at 1e-9.

**The target change is not the cause.** Two control runs settle that, and they
point at the execution environment instead:

| what differs | worst targeted moment | verdict |
|---|---|---|
| archive vs new source (old container vs this one) | `w_bot` **1.85e-02** | real |
| **same source `b8dc1077ad`**, old container vs this one | `w_bot` **1.78e-02** | real, and the constant is not involved |
| **3.0 vs 2.5**, both in this container | `w_bot` **6.86e-04** | inside this container's noise |
| **identical binary, run twice**, this container | `w_bot` **1.21e-03** | this container's noise floor |

The old source rebuilt in this container fails to reproduce the archive by
1.78e-02 -- essentially the whole 1.85e-02 gap -- with `wealth_to_output_data`
still at 3.0. And the isolated effect of the constant, 6.86e-04, is SMALLER than
the 1.21e-03 spread between two runs of one binary here. The 3.0 -> 2.5 edit is
indistinguishable from noise; the container is not.

So: the target change is a target change, exactly as `5ea693e` argued. The
archive still does not carry over, because the numbers in it cannot be
reproduced in this environment on any source.

## The stamps

| run | `MODEL` | full source md5 | semantic hash | `beta` target | where |
|---|---|---|---|---|---|
| ARCHIVE | `b8dc1077ad` | `b8dc1077adc90fe0d9b497289e93e7c5` | `2f7c317e75` | 3.0 | original container |
| CONTROL | `b8dc1077ad` | `b8dc1077adc90fe0d9b497289e93e7c5` | `2f7c317e75` | 3.0 | this container |
| NEW | `bb2cd48b81` | `bb2cd48b81256cf6b0a03f1a7d31f067` | `08f8470b5d` | 2.5 | this container |
| REPEAT | `bb2cd48b81` | `bb2cd48b81256cf6b0a03f1a7d31f067` | `08f8470b5d` | 2.5 | this container |

All four record `HANDOVER OK: 42 of 42 parameters applied`, all four solved in
14 minutes on 4 cores, and the `VECTOR` line is byte-identical in all four
(md5 `5bbadf8b21b51c1ff63fd3412c22fed3`). The two source files differ by exactly
one non-comment line:

    <         real(8), parameter :: wealth_to_output_data=3.0d0
    >         real(8), parameter :: wealth_to_output_data=2.5d0

CONTROL and REPEAT are in this directory as `TARGET_CHECK_control_b8dc1077ad.txt`
and `TARGET_CHECK_repeat_bb2cd48b81.txt`. The archived measurement is in
`points_superseded/point_35e8286c4e.20260902T125525Z.txt`, where
`run_one_point.sh` moved it. NEW is `point_35e8286c4e.txt`.

## Why the constant cannot move the economy

`wealth_to_output_data` has seven references. Five of them -- lines 36307,
36347, 36416, 36441 and 36453 -- sit inside the `else` arm of

    if (re_do_simulation_with_fixed_parameters==1) then

at line 36234, and that flag is

    integer, parameter :: re_do_simulation_with_fixed_parameters=&
        max(sweep_addiction_scalar,diagnostic_simulation)

with `sweep_addiction_scalar=1` (line 1433) and `diagnostic_simulation=0`
(line 1477). It is a compile-time `parameter` equal to 1, so the `then` arm
runs, `distance_discount_factor` is set to zero, and the whole `else` arm --
the `beta` bisection, the only place the constant enters arithmetic -- is dead
code. The remaining two references, at lines 5390 and 38741, are `write`
statements. Under this configuration the constant is print-only.

The reading in `5ea693e`'s message is therefore right. Note that the comment at
line 1486 contradicts it -- it says `sweep_addiction_scalar` and
`diagnostic_simulation` are "both zero", which was true when it was written and
is not true now. The declaration at line 1433 is what the compiler reads.

## Every targeted moment, line by line

`rel A vs N` is the comparison the check asked for: archive against the new
source. `rel C vs N` isolates the constant, both runs in this container.
`rel N vs R` is two runs of one binary here, the noise floor to judge the other
two against.

| moment | what it is | ARCHIVE (old env) | NEW 2.5 (this env) | rel A vs N | CONTROL 3.0 (this env) | rel C vs N | REPEAT 2.5 (this env) | rel N vs R |
|---|---|---|---|---|---|---|---|---|
| `sigma_y` | bottom half earnings share | 0.169050021402 | 0.169050021402 | 0.00e+00 | 0.169050021402 | 0.00e+00 | 0.169050021402 | 0.00e+00 |
| `tau_l` | average labour income tax | 0.226320585498 | 0.225739190229 | 2.57e-03 | 0.225735266164 | 1.74e-05 | 0.225738387985 | 3.55e-06 |
| `omega_l` | labour supply / total hours | 0.363505000284 | 0.363507308275 | 6.35e-06 | 0.363482909632 | 6.71e-05 | 0.363506376787 | 2.56e-06 |
| `beta` | wealth over output | 2.45282633409 | 2.4531742323 | 1.42e-04 | 2.45308408622 | 3.67e-05 | 2.4532856474 | 4.54e-05 |
| `h_2` | above half of spending | 0.037082403227 | 0.0371784274882 | 2.58e-03 | 0.037177505097 | 2.48e-05 | 0.0371889143864 | 2.82e-04 |
| `h_3` | share in the largest unit | 0.436444894824 | 0.436131818138 | 7.17e-04 | 0.43621632032 | 1.94e-04 | 0.436058970386 | 1.67e-04 |
| `gamma` | housing over expenditure | 0.122699708835 | 0.122704037376 | 3.53e-05 | 0.122713289321 | 7.54e-05 | 0.12269688156 | 5.83e-05 |
| `h_1` | homelessness rate | 0.0451469723591 | 0.0446952855589 | 1.00e-02 | 0.044668239953 | 6.05e-04 | 0.0446944688055 | 1.83e-05 |
| `b` | total drug users | 0.408622447309 | 0.407289770912 | 3.26e-03 | 0.407370196041 | 1.97e-04 | 0.407170070667 | 2.94e-04 |
| `lambda_d` | disorder rate | 0.294785417386 | 0.293935977117 | 2.88e-03 | 0.293945495913 | 3.24e-05 | 0.293886904103 | 1.67e-04 |
| `theta` | drug spending share | 0.304600998293 | 0.30501928179 | 1.37e-03 | 0.305029631115 | 3.39e-05 | 0.305026624322 | 2.41e-05 |
| `aleph` | value of life / income | 75.8280078863 | 76.0677289571 | 3.15e-03 | 76.0638147025 | 5.15e-05 | 76.0832792213 | 2.04e-04 |
| `pi_eu` | unemployment rate | 0.134279134627 | 0.134264807601 | 1.07e-04 | 0.134252620106 | 9.08e-05 | 0.1342687632 | 2.95e-05 |
| `kappa_ued` | unemployment given SUD | 0.244468745824 | 0.244472114745 | 1.38e-05 | 0.244466359561 | 2.35e-05 | 0.24449761062 | 1.04e-04 |
| `kappa_uem` | employment given SMI | 0.147680965255 | 0.147742871977 | 4.19e-04 | 0.147742598914 | 1.85e-06 | 0.147741602328 | 8.59e-06 |
| `p_m` | SMI population share | 0.0501667619886 | 0.0502949072768 | 2.55e-03 | 0.0502888786994 | 1.20e-04 | 0.0503056420793 | 2.13e-04 |
| `lambda_m` | SMI share of the homeless | 0.0262580453375 | 0.0264867917466 | 8.64e-03 | 0.0264982837324 | 4.34e-04 | 0.0264923565428 | 2.10e-04 |
| `pi_V` | eligibles with a voucher | 0.255977544628 | 0.25560605917 | 1.45e-03 | 0.255729779373 | 4.84e-04 | 0.255486932826 | 4.66e-04 |
| `cbar` | food stamps / income | 0.00393490612653 | 0.00393426094126 | 1.64e-04 | 0.00393454041633 | 7.10e-05 | 0.00393436627271 | 2.68e-05 |
| `tau_u` | treatment take up | 0 | 0 | 0.00e+00 | 0 | 0.00e+00 | 0 | 0.00e+00 |
| `mu_H` | recovery housed / homeless | 1.09178837854 | 1.09177934813 | 8.27e-06 | 1.09178299782 | 3.34e-06 | 1.09177860751 | 6.78e-07 |
| `w_bot` | net worth share, bottom half | 0.024269801123 | 0.0247265384957 | 1.85e-02 | 0.0247095751043 | 6.86e-04 | 0.0247565218947 | 1.21e-03 |
| `y_u` | income of drug users | 0.839032833276 | 0.838548678197 | 5.77e-04 | 0.838446973132 | 1.21e-04 | 0.838670879538 | 1.46e-04 |

Worst `rel A vs N` is `w_bot` at 1.85e-02. Worst `rel C vs N` -- the constant's
own effect -- is `w_bot` at 6.86e-04, below the 1.21e-03 noise floor in the last
column. Only `sigma_y` and `tau_u` are bit-identical everywhere: `sigma_y` is
frozen by `freeze_sd_permanent_productivity` and `tau_u` is identically zero
because treatment take-up is off in this vector.

## DIAG, UNTARGETED and INVARIANT lines

Counts are of numeric fields differing by more than 1e-9 relative, over all
`DIAG`, `UNTARGETED` and `INVARIANT` lines including the 60-row age profile.

| comparison | DIAG lines differing (of 564 fields) | largest DIAG | UNTARGETED (of 124) | largest UNTARGETED | INVARIANT (of 16) | largest INVARIANT |
|---|---|---|---|---|---|---|
| ARCHIVE vs NEW | 119 | 1.805e-01 | 41 | 4.407e-02 | 10 | 1.000e-02 |
| ARCHIVE vs CONTROL (same source) | 124 | 1.853e-01 | 41 | 4.397e-02 | 10 | 1.060e-02 |
| CONTROL vs NEW (3.0 vs 2.5) | 121 | 2.784e-02 | 41 | 2.236e-03 | 10 | 6.051e-04 |
| NEW vs REPEAT (same binary) | 119 | 2.772e-02 | 41 | 2.643e-03 | 10 | 2.939e-04 |

The pattern is the same as for the targeted moments. Archive-against-anything is
an order of magnitude worse than either within-container comparison, and the
constant's own effect is no larger than re-running one binary.

The largest single `DIAG` difference between archive and new is on the last row
of the age profile:

      OLD  DIAG age  85  ... sud=  0.012758  mass=    0.463982
      NEW  DIAG age  85  ... sud=  0.010455  mass=    0.452451

at 1.805e-01 relative on `sud`. It is the oldest cohort, where the surviving
mass is smallest and a small shift in the death-and-recovery path is amplified.
The old source in this container gives 0.010394 there, so this is environment,
not the constant.

All 16 `INVARIANT` lines read `PASS` in all four runs, and every run ends
`INVARIANTS: all PASS`. Nothing here is a broken solve; the runs simply do not
agree to the precision the archive was assumed to have.

## The `beta` target field, and one that also moved

`beta`'s printed target is the one thing that SHOULD differ, and it does:

| | ARCHIVE | CONTROL | NEW | REPEAT |
|---|---|---|---|---|
| `beta` target | 3.0000000000 | 3.0000000000 | 2.5000000000 | 2.5000000000 |

It tracks the source and nothing else, which is what a print-only constant looks
like.

`p_m`'s printed target ALSO moved, and that is not a second edited constant. It
is `model_smi_prevalence_target(1)`, a model-computed quantity, not a `data`
parameter -- line 5657 prints it where every other moment prints a `_data`
name. It moves between two runs of the identical binary (0.05225461332 vs
0.05226137009), which settles it: it is a symptom of the economy moving, not a
cause.

| | ARCHIVE | CONTROL | NEW | REPEAT |
|---|---|---|---|---|
| `p_m` target | 0.05213447656 | 0.05225158935 | 0.05225461332 | 0.05226137009 |

No other `target=`, `data=` or `observed=` field differs anywhere in the four
files.

## `DETERMINISM.md`'s bound does not hold in this container

This is the part that matters beyond the question asked. `DETERMINISM.md`
records a worst relative spread of **5.13e-05** over the targeted moments across
three cold runs, and uses it to argue 1e-3 is a real difference. Two cold runs of
one binary here spread by **1.21e-03** on `w_bot` -- 24 times that bound, and
past the threshold the same file calls real.

So the 1e-3 rule and the 5.13e-05 bound cannot both be carried into this
container. Either the noise floor is environment-dependent and has to be
re-measured wherever points are scored, or something about this container --
`gfortran` was absent from it and I installed 13.3.0 to build at all, where the
archive was built by an unrecorded compiler -- makes the model noisier than it
was. Both readings mean the same thing for the archive: a point measured
elsewhere cannot be compared here at 1e-3, and `w_bot`, the moment the search has
been fighting, is the worst-behaved of them.

Three cold runs would pin this down properly, as `DETERMINISM.md` did. Two is
enough to show the old bound does not transfer.

## What this means for the 35 points

- **The 3.0 -> 2.5 edit is not a model change.** It is provably print-only under
  this configuration, and measurement agrees: its isolated effect is smaller
  than re-running one binary. `2f7c317e75` and `08f8470b5d` describe the same
  economy, and an `EQUIVALENT_MODELS` entry pairing them would be correct on the
  merits.
- **That does not rescue the archive.** The 35 points were measured in a
  different container, and this one does not reproduce them on the source that
  produced them -- 1.78e-02 on `w_bot`, 1.06e-02 on `h_1`, with
  `wealth_to_output_data` untouched at 3.0. Carrying them forward would be
  carrying numbers that cannot be reproduced where the next ones are measured.
- The honest position is that the archive resets for a reason that has nothing
  to do with `beta`'s target, and that the reset is worth less than knowing why:
  until the noise floor here is re-measured, no point measured in this container
  can be compared with one measured in another at better than about 2e-02.

## A note on the branch

While these runs were in flight, `b03b86b` ("seven negative grid points on an
accordion") changed the source again, to `64d52d8b6a`. That is a genuine model
change -- the negative asset grid and the borrowing limit -- and it is a separate
question from this one. Everything above is about `b8dc1077ad` against
`bb2cd48b81`, and every file it refers to records which source measured it.

## How to reproduce

`code/housing_first_or_treatment_first_SR_v1.f90` was not edited. The two
control runs used copies of the tree outside the repository, with the historical
source dropped in by `git show`:

    git show 5ea693e^:code/housing_first_or_treatment_first_SR_v1.f90   # 3.0, b8dc1077ad
    git show 5ea693e:code/housing_first_or_treatment_first_SR_v1.f90    # 2.5, bb2cd48b81

Each copy needs `../data` to resolve -- the model reads
`../data/us_mortality_multipliers.csv` and `../data/us_mh_onset_shape.csv`
relative to its working directory, and a copy placed without them exits cleanly
after printing `us_mortality_multipliers.csv not found. stopping.`, which
`run_one_point.sh` records as `NO MOMENTS BLOCK; hftf exit status 0`.

The vector is the single line of `code/batch_target_check.txt`.
