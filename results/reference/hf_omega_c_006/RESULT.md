# HOUSING FIRST at omega_c = 0.06 -- the reference economy

Re-solve of the point every welfare comparison in this round is measured
against. The first solve (b = 0.081242, bequest_residual 1.45135) was lost with
its container before it was committed; this is its replacement.

Run launched 2026-09-24 02:59:06Z, `sh code/remote_scan_point.sh 0.06`, frozen
on the published two-class omega_c = 0 seed in `code/scan_seed/`. The run left
the calibration loop after block 12 (`frozen_stop_after_blocks 12`), went
through the statistics and the save, and wrote `welfare_curvebaseline_benchmark.dat`
at 07:24:49Z. The process ended at 07:26Z; `run.err` is empty. The machine's
boot (02:56:13) predates the launch, so this is a single uninterrupted run.

## THE HANDOVER

The full 97-line base with exactly three lines changed (`diff` against
`code/scan_seed/PARAM_HANDOVER_base.txt`):

    23c23   kappa_x 0.8139            -> kappa_x 0.9329
    94c94   weight_on_child 0         -> weight_on_child 0.06
    97c97   frozen_stop_after_blocks 0 -> frozen_stop_after_blocks 12

All three were checked by value with `grep -qx` in the file before the solve
started. The run log shows them read:

    HANDOVER kappa_x:   2.0000000000000000E-003 ->  0.93289999999999995
    HANDOVER weight_on_child:   0.0000000000000000      ->   5.9999999999999998E-002
    HANDOVER frozen_stop_after_blocks:           0 ->          12
    resumed from calibration_state.dat, written after loop          22

The model deletes `PARAM_HANDOVER.txt` once it has read it. The
`PARAM_HANDOVER.txt` committed here is the script's `PARAM_HANDOVER.relaunch.txt`,
copied after the edits and byte-identical to what the run read. With
internalise_homelessness_cost = 0, kappa_x enters only as a constant and moves no
policy function.

## THE BLOCK TABLE

Verbatim from `run.log`. b, lambda_d, h_1, y and block_move come from each
block's `BLOCK MOVE` line. bequest_residual is the single `BUDGET bequest_residual=`
printed in that block (12 in the log, 1:1 with the blocks).

| block | b | lambda_d | bequest_residual | block_move | h_1 | y |
|---|---|---|---|---|---|---|
| 1 | 7.1895548312986293E-002 | 3.1459189664822029E-002 | 2.1219645566291052 | 1.0000000000000000 | 7.0781482743375113E-003 | 1.1459276216379350 |
| 2 | 8.5112357410527764E-002 | 3.5927783514006259E-002 | 1.8355716183183806 | 0.20610541544231853 | 6.4900775704089158E-003 | 1.3821095101624497 |
| 3 | 8.5319653948426666E-002 | 3.6355039626268973E-002 | 1.6318502921576394 | 8.5296110808944239E-002 | 6.3162608586672621E-003 | 1.4999980760913616 |
| 4 | 8.4483697243041736E-002 | 3.6109673985959642E-002 | 1.5634180328150615 | 3.9083787426043709E-002 | 6.1537788121994296E-003 | 1.5586236820367909 |
| 5 | 8.3843775681292310E-002 | 3.5839116862507993E-002 | 1.5078703731882741 | 1.8631035545152282E-002 | 6.1421104894006920E-003 | 1.5876624552583345 |
| 6 | 8.2254461957483510E-002 | 3.5458677749740382E-002 | 1.4864706831500465 | 1.8955655454378779E-002 | 6.1186668364408116E-003 | 1.6020838063507883 |
| 7 | 8.1785739667876792E-002 | 3.4935491189662576E-002 | 1.4625079103449456 | 1.4754824299155827E-002 | 6.1171519594092937E-003 | 1.6092545691594320 |
| 8 | 8.1376071384212267E-002 | 3.4798597615604214E-002 | 1.4581827529930251 | 5.0090429618677261E-003 | 6.0884059195170518E-003 | 1.6128776760279790 |
| 9 | 8.1214766344462772E-002 | 3.4681514824268830E-002 | 1.4544239896830262 | 3.3645836142224867E-003 | 6.0733105446634126E-003 | 1.6147281587198163 |
| 10 | 8.1274384639885788E-002 | 3.4647440618393012E-002 | 1.4528757232458760 | 1.4788351075113284E-003 | 6.0643291198111456E-003 | 1.6156681817770613 |
| 11 | 8.1268006444833091E-002 | 3.4620585723284199E-002 | 1.4516070818975493 | 2.3394012554017198E-003 | 6.0785160189672010E-003 | 1.6161604955039683 |
| 12 | 8.1260630474628087E-002 | 3.4616598188775979E-002 | 1.4513664692037109 | 1.5581818049324180E-004 | 6.0789275891736669E-003 | 1.6164123226917628 |

## THE BLOCK-9 CONTROL: FAILS AT 1e-4

Up to block 9 this is the same solve as the lost run: same seed, same
parameters, and kappa_x moves no policy function. The stated control was that
block 9's b reproduces the lost run's b = 0.081242 at 1e-4 relative.

    block 9 b = 0.081214766344462772
    (0.0812147663 - 0.081242) / 0.081242 = -3.35e-4 relative

**It misses by a factor of about 3.** The frozen path is not landing exactly
where the lost run did. It is close, but outside the stated tolerance. For
comparison, the other blocks against 0.081242:

    block 10  +3.99e-4    block 11  +3.20e-4    block 12  +2.28e-4

The final bequest_residual, 1.4513664692, is 1.1e-5 relative from the lost run's
1.45135. It is not stated at which block the lost run's 0.081242 was read. If
it was the lost run's final b rather than its block 9, the relevant comparison
is block 12, at +2.28e-4, which is also outside 1e-4.

## THE FAMILY STOP RULE: FIRED AT BLOCK 10

The rule is |b(k)-b(k-1)|/b(k-1) < 0.5% for two consecutive blocks.

    1 -> 2   +18.38%
    2 -> 3    +0.243%   (under; count 1)
    3 -> 4    -0.980%   (reset)
    4 -> 5    -0.757%
    5 -> 6    -1.896%
    6 -> 7    -0.570%
    7 -> 8    -0.5009%  (0.000409668 / 0.0817857 = 0.0050090; misses by 0.0009 points)
    8 -> 9    -0.198%   (under; count 1)
    9 -> 10   +0.0734%  (under; count 2 -> FIRES at block 10)
   10 -> 11   -0.0079%
   11 -> 12   -0.0091%

The run was not stopped at block 10. It ran to block 12 as set by
`frozen_stop_after_blocks`, and blocks 11 and 12 stayed inside the band. The
state and curve are therefore those after block 12.

## HEADLINE OUTCOMES (model units, after block 12)

From the final `MOMENT` and `BUDGET` lines:

    b                 8.1260630474628087E-002   (target 0.10502)
    lambda_d          3.4616598188775979E-002   (target 0.043424)
    h_1               6.0789275891736669E-003   (target 0.004)
    tau_u             0.25057768576255840       (target 0.245)
    theta, AGGREGATE  0.15274010250771367       (DIAG drug share, sum spend / sum income)
    theta, MOMENT row 0.54255372258949652       (mean of ratios; NOT the aggregate, runs 3-4x higher)
    bequest_residual  1.4513664692037109
    y                 1.6164123226917628

`THETA GATE SHUT` prints at every block: b is outside 0.1 of its target, so theta
is HELD at 0.165. This is expected in a frozen run.

## WELFARE CURVE

    WELFARE CURVE identity check: w(0)=   789.44046337451550       against average_welfare_of_youngest_cohort=   789.34880389187708       relative difference=   1.1612037946531824E-004
    WELFARE CURVE shift applied:  -9.1659482638419831E-002  utils, which is  -2.2970882765880238E-003  of consumption
    WELFARE CURVE: written, identity check passed

## KAPPA_X PROBE, verbatim

    KAPPA_X PROBE: H*beta^K*D_adult=  0.11040274998795059       measured at kappa_x=  0.93289999999999995
    KAPPA_X PROBE: H=   6.0789275891736669E-003  so beta^K*D_adult=   18.161550432772646
    KAPPA_X PROBE: giving up x=   2.0000000000000000E-003  of consumption for life costs   6.8278762895374712E-002  utils
    KAPPA_X PROBE: IMPLIED kappa_x=  0.61845165000714830       against the coded  0.93289999999999995
    KAPPA_X PROBE: giving up x=   8.0000000000000004E-004  of consumption for life costs   2.7288744764291550E-002  utils
    KAPPA_X PROBE: IMPLIED kappa_x=  0.24717450215026218       against the coded  0.93289999999999995

## ENVIRONMENT NOTE

gfortran was NOT present in this container, although the brief said it was at
/usr/bin/gfortran. apt-get was not used. The four matching packages
(gfortran-13, gfortran-13-x86-64-linux-gnu, libgfortran-13-dev
13.3.0-6ubuntu2~24.04.1, and libgfortran5 14.2.0-4ubuntu2~24.04.1) were fetched
from archive.ubuntu.com with curl and installed with `dpkg -i`. The build showed
7 warnings and 0 errors, as expected. OMP_NUM_THREADS=2.

## FILES

This commit: `RESULT.md`, `PARAM_HANDOVER.txt`, `calibration_state.dat`.
Next commit: `welfare_curvebaseline_benchmark.dat`, `calibration_distribution1.dat.gz`,
`calibration_distribution2.dat.gz`, `newborn_parent_share.dat`, `resume_seed.dat`,
`run.log.gz`.
