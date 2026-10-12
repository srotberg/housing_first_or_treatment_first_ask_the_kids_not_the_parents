# The drug price elasticity across six step sizes

One iteration on the benchmark, at each of six price steps. The benchmark
distribution is held fixed; the value function is re-solved at the new price;
the moments are read off the SAME distribution under the new policy functions.
There is no `converge_to_stationary_equilibrium` anywhere in the block, in
either direction, so what is measured is the response of the same households to
a price and not the difference between two stationary equilibria.

Run: `bash code/run_variant.sh save $V` with `$V` the `VECTOR` line of
`code/benchmark_of_record.txt`. Log `code/variant_save_20260909T160926Z.log`,
finished in 22 min, exit 0, HANDOVER 80 of 80.

## The answer in one line

**The intensive margin has a well-defined elasticity. Participation does not.**

Quantity per addict gives -0.93471 at a 1 per cent step and -0.94384 at 50 per
cent -- a spread of one per cent of itself across a fifty-fold change in the
step. Participation gives **-1.93199 at 1 per cent and -1.72816 at 50 per
cent**, and in between it is not monotone at all: it reaches -4.57790 at 2 per
cent. The headline -2.26 is the value at the ten per cent step and nothing
more; a different step would have given a different number by a factor of up to
2.4.

## Which block this is read off, and both base figures

`print_all_moments` runs twice. The FIRST call is before the frozen-equilibrium
convergence and its base reads

    ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.1482141867657870E-002  quantity per user=   5.3172997387478715E-002

The SECOND call is after it and its base reads

    ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.5286199919985095E-002  quantity per user=   5.1481613510991946E-002

**Everything reported here is the SECOND block**, base users
`0.085286199919985095`. The first block is measured on an unconverged state and
is unusable -- see the drift section, where its 1 per cent step comes out with
the WRONG SIGN.

## (a) The curve

Second block. Base users 0.085286199919985095, base quantity per user
0.051481613510991946, base quantity per addict 0.068108146314880866.

| step | new price | users | change in users | quantity per user | quantity per addict | participation elasticity | intensive elasticity (per addict) | per-user elasticity (mixed) |
|---|---|---|---|---|---|---|---|---|
| 1%  | 1.0100000000000000 | 0.083662325408957669 | -1.9040% | 0.051515135118410098 | 0.067477631281345471 | **-1.93198570316945** | -0.934710055182564 | +0.065417479938501 |
| 2%  | 1.0200000000000000 | 0.077894715573502027 | -8.6667% | 0.051468079975206069 | 0.066863028834848626 | **-4.57790487194305** | -0.931727262362868 | -0.013276799664566 |
| 5%  | 1.0500000000000000 | 0.072972137767916972 | -14.4385% | 0.049824288792988246 | 0.065068608887711391 | **-3.19603279266840** | -0.935733565087692 | -0.670670684937433 |
| 10% | 1.1000000000000001 | 0.068729888285639418 | -19.4127% | 0.048832614716420308 | 0.062277730557021460 | **-2.26448527581385** | -0.938964988520550 | -0.554256647627191 |
| 20% | 1.2000000000000000 | 0.059004998610274216 | -30.8153% | 0.048609644258951097 | 0.057358453666942845 | **-2.02055369906999** | -0.942162815592468 | -0.314843581674000 |
| 50% | 1.5000000000000000 | 0.042321949329601226 | -50.3766% | 0.042152633565689733 | 0.046451156006753633 | **-1.72815563253238** | -0.943843179375740 | -0.493082036964042 |

Data targets for reference: participation -0.63, intensive -0.55.

The arc elasticity between consecutive steps, which is where the jaggedness is
visible, runs -1.9320, -7.2502, -2.2520, -1.2875, -1.7534, -1.4892.

## (b) The drift check

After the six steps the price is put back to `val_price_base_1`, the value
function is solved again and the moments are re-read.

**Second block, the one that counts:**

    ELASTICITY_DRIFT price back at=   1.0000000000000000       base users=   8.5286199919985095E-002  users now=   8.5286279246866270E-002  per cent difference=   9.3012563873173804E-005

**9.3e-5 per cent.** The six steps do NOT contaminate each other. The concern
about `stationary_equilibrium_statistics` recomputing
`model_average_labour_income` and moving the newborn endowment through
`set_newborn_age_transfer` is real as a mechanism -- that call is at line 11971
of the master and it does fire on every one of the seven calls, with
`is_counterfactual=0` so it takes the model's own average -- but at the
converged benchmark the aggregate is a fixed point of that map, so it comes back
to itself and the endowment does not move. The elasticities above are clean.

**First block, for contrast:**

    ELASTICITY_DRIFT price back at=   1.0000000000000000       base users=   8.1482141867657870E-002  users now=   8.4999694351484426E-002  per cent difference=   4.3169612423047399

**+4.32 per cent**, and note where it lands: 0.084999694, which is almost
exactly the converged base 0.085286200. The drift there is not step
contamination either. It is the unconverged state walking toward its own fixed
point, one solve at a time, and that walk is the same size as the price effect
being measured. It is what makes the first block's 1 per cent step come out
POSITIVE:

    ELASTICITY_STEP participation step=   1.0000000000000000E-002  elasticity=   2.5837691404121710       observed= -0.63000000000000000

Raising the price by one per cent and getting 2.6 per cent MORE users is the
same class of null failure the author caught before with a zero-size step. The
first block should not be read for anything.

## (c) Is the elasticity stable across steps?

**No, for participation. Yes, for the intensive margin.**

- Participation: **-1.93199 at 1 per cent, -1.72816 at 50 per cent.** Those two
  are close to each other, but that is a coincidence of the endpoints and not
  stability -- the path between them goes -1.93, -4.58, -3.20, -2.26, -2.02,
  -1.73. The maximum is 2.4 times the minimum and the function is not monotone
  in the step. **The model does not have a well-defined participation
  elasticity; it has a step-dependent one.**
- Intensive: -0.93471 at 1 per cent, -0.94384 at 50 per cent, and every step in
  between inside that interval. **This one is well defined**, and it is a real
  demand response rather than an artefact.

### Why, and it is not curvature

The addict stock is EXACTLY constant across every step. Multiplying the addict
share of users by users:

| step | users | mass of addicts | mass of experimenters |
|---|---|---|---|
| base | 0.0852861999 | 0.036274310189 | 0.049011889731 |
| 1%  | 0.0836623254 | 0.036274310189 | 0.047388015220 |
| 2%  | 0.0778947156 | 0.036274310189 | 0.041620405384 |
| 5%  | 0.0729721378 | 0.036274310189 | 0.036697827579 |
| 10% | 0.0687298883 | 0.036274310189 | 0.032455578096 |
| 20% | 0.0590049986 | 0.036274310189 | 0.022730688421 |
| 50% | 0.0423219493 | 0.036274310189 | 0.006047639140 |

Twelve digits, unchanged. That is not a numerical coincidence: addiction is a
STATE in the held distribution, and one iteration cannot move anybody into or
out of it. So the whole of the measured "participation" response is
experimenters, and the model's participation elasticity is the elasticity of the
experimenter margin alone.

That margin is a discrete yes/no choice over a discretized state space, and it
is nearly exhausted by 50 per cent: experimenter mass falls from 0.04901 to
0.00605, a collapse of 87.7 per cent, leaving users pinned to the addict floor
of 0.036274. Two things follow, and they are the whole shape of the table. Mass
crosses the use/no-use threshold in lumps, which is the non-monotonicity at 1
and 2 per cent -- the arc elasticity over that single interval is -7.25. And the
approach to a floor mechanically drags the elasticity toward zero as the step
grows, which is the monotone decline from 5 per cent onward. Neither is a
demand curve.

This is also the direct answer to the objection that a large death penalty
should flatten the response. `value_of_life=177.77` with
`kappa_phi_d_level=8` prices the mortality risk for the people who face it,
which is addicts -- and the addict margin is exactly the one this measurement
cannot move. The penalty is not reaching the households that produce the -2.26.

The intensive margin behaves completely differently because it is not a
threshold: quantity per addict comes off a first order condition, it is smooth,
and it returns the same -0.94 at every step. Note also that the per-USER figure
is useless as a summary here for the reason already documented in the block --
it runs +0.065, -0.013, -0.671, -0.554, -0.315, -0.493, because the
addict share of users climbs from 0.425 to 0.857 as the experimenters leave.

## (d) The benchmark was a fixed point

From the same save run, the frozen-equilibrium loop before the second
`print_all_moments`:

    FROZEN PASS           1  b=   8.6416656403812450E-002  lambda_d=   3.6627608232277842E-002  h_1=   1.2632562931748820E-002  avg_lab_inc=  0.66723600351779200       distance=   1.4660688044297321E-002
    FROZEN PASS           2  b=   8.5297866703297004E-002  lambda_d=   3.6286696164325768E-002  h_1=   1.2551464880965178E-002  avg_lab_inc=  0.66701066171912327       distance=   1.1187897005154462E-003
    FROZEN PASS           3  b=   8.5286199919985095E-002  lambda_d=   3.6274310189276959E-002  h_1=   1.2550957981996543E-002  avg_lab_inc=  0.66702928520191329       distance=   1.8623482790025569E-005
    FROZEN CONVERGED after           3 passes, distance=   1.8623482790025569E-005

Against `stopping_rule_frozen_moments = 5e-4`. The `b` it converges to,
0.085286199919985095, is the base users figure the second block reports, which
is the same statement twice.

## (e) The second block, verbatim

    ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.5286199919985095E-002  quantity per user=   5.1481613510991946E-002
    ELASTICITY_DIAG base per addict=   6.8108146314880866E-002  per experimenter=   3.9176109446279819E-002  addict share of users=  0.42532449825773994
    ELASTICITY_STEP step=   1.0000000000000000E-002  new price=   1.0100000000000000       users=   8.3662325408957669E-002  quantity per user=   5.1515135118410098E-002  quantity per addict=   6.7477631281345471E-002
    ELASTICITY_STEP participation step=   1.0000000000000000E-002  elasticity=  -1.9319857031694541       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   1.0000000000000000E-002  elasticity= -0.93471005518256423       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=   1.0000000000000000E-002  elasticity=   6.5417479938500958E-002
    ELASTICITY_STEP per EXPERIMENTER step=   1.0000000000000000E-002  elasticity=  0.30773663032410276
    ELASTICITY_STEP ADDICT SHARE  step=   1.0000000000000000E-002  elasticity=   1.9319857031694641
    ELASTICITY_DIAG step=   1.0000000000000000E-002  new per addict=   6.7477631281345471E-002  per experimenter=   3.9296253729832080E-002  addict share of users=  0.43357998970218792
    ELASTICITY_STEP step=   2.0000000000000000E-002  new price=   1.0200000000000000       users=   7.7894715573502027E-002  quantity per user=   5.1468079975206069E-002  quantity per addict=   6.6863028834848626E-002
    ELASTICITY_STEP participation step=   2.0000000000000000E-002  elasticity=  -4.5779048719430468       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   2.0000000000000000E-002  elasticity= -0.93172726236286751       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=   2.0000000000000000E-002  elasticity=  -1.3276799664565601E-002
    ELASTICITY_STEP per EXPERIMENTER step=   2.0000000000000000E-002  elasticity=  -1.4720459846642509
    ELASTICITY_STEP ADDICT SHARE  step=   2.0000000000000000E-002  elasticity=   4.5779048719430477
    ELASTICITY_DIAG step=   2.0000000000000000E-002  new per addict=   6.6863028834848626E-002  per experimenter=   3.8050595327295510E-002  addict share of users=  0.46568383904102267
    ELASTICITY_STEP step=   5.0000000000000003E-002  new price=   1.0500000000000000       users=   7.2972137767916972E-002  quantity per user=   4.9824288792988246E-002  quantity per addict=   6.5068608887711391E-002
    ELASTICITY_STEP participation step=   5.0000000000000003E-002  elasticity=  -3.1960327926684005       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   5.0000000000000003E-002  elasticity= -0.93573356508769179       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=   5.0000000000000003E-002  elasticity= -0.67067068493743265
    ELASTICITY_STEP per EXPERIMENTER step=   5.0000000000000003E-002  elasticity=  -2.4537284701269826
    ELASTICITY_STEP ADDICT SHARE  step=   5.0000000000000003E-002  elasticity=   3.1960327926684005
    ELASTICITY_DIAG step=   5.0000000000000003E-002  new per addict=   6.5068608887711391E-002  per experimenter=   3.4755898312497341E-002  addict share of users=  0.49709808837785441
    ELASTICITY_STEP step=  0.10000000000000001       new price=   1.1000000000000001       users=   6.8729888285639418E-002  quantity per user=   4.8832614716420308E-002  quantity per addict=   6.2277730557021460E-002
    ELASTICITY_STEP participation step=  0.10000000000000001       elasticity=  -2.2644852758138514       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.10000000000000001       elasticity= -0.93896498852055021       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=  0.10000000000000001       elasticity= -0.55425664762719118
    ELASTICITY_STEP per EXPERIMENTER step=  0.10000000000000001       elasticity=  -1.5469735541955665
    ELASTICITY_STEP ADDICT SHARE  step=  0.10000000000000001       elasticity=   2.2644852758138523
    ELASTICITY_DIAG step=  0.10000000000000001       new per addict=   6.2277730557021460E-002  per experimenter=   3.3805542911237205E-002  addict share of users=  0.52778072384639974
    ELASTICITY_STEP step=  0.20000000000000001       new price=   1.2000000000000000       users=   5.9004998610274216E-002  quantity per user=   4.8609644258951097E-002  quantity per addict=   5.7358453666942845E-002
    ELASTICITY_STEP participation step=  0.20000000000000001       elasticity=  -2.0205536990699877       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.20000000000000001       elasticity= -0.94216281559246806       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=  0.20000000000000001       elasticity= -0.31484358167400028
    ELASTICITY_STEP per EXPERIMENTER step=  0.20000000000000001       elasticity= -0.67367864954111056
    ELASTICITY_STEP ADDICT SHARE  step=  0.20000000000000001       elasticity=   2.0205536990699882
    ELASTICITY_DIAG step=  0.20000000000000001       new per addict=   5.7358453666942845E-002  per experimenter=   3.4648033401657251E-002  addict share of users=  0.61476673237241153
    ELASTICITY_STEP step=  0.50000000000000000       new price=   1.5000000000000000       users=   4.2321949329601226E-002  quantity per user=   4.2152633565689733E-002  quantity per addict=   4.6451156006753633E-002
    ELASTICITY_STEP participation step=  0.50000000000000000       elasticity=  -1.7281556325323788       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.50000000000000000       elasticity= -0.94384317937574025       observed= -0.55000000000000004
    ELASTICITY_STEP per USER (mixed) step=  0.50000000000000000       elasticity= -0.49308203696404174
    ELASTICITY_STEP per EXPERIMENTER step=  0.50000000000000000       elasticity=  -2.1521842780553366
    ELASTICITY_STEP ADDICT SHARE  step=  0.50000000000000000       elasticity=   1.7281556325323786
    ELASTICITY_DIAG step=  0.50000000000000000       new per addict=   4.6451156006753633E-002  per experimenter=   1.6369690376656289E-002  addict share of users=  0.85710395584037125
    ELASTICITY_DRIFT price back at=   1.0000000000000000       base users=   8.5286199919985095E-002  users now=   8.5286279246866270E-002  per cent difference=   9.3012563873173804E-005
    ELASTICITY_DRIFT base per user=   5.1481613510991946E-002  per user now=   5.1495379275246278E-002  base per addict=   6.8108146314880866E-002  per addict now=   6.8111957737755954E-002

### The first block, verbatim, so the difference is on the record

    ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.1482141867657870E-002  quantity per user=   5.3172997387478715E-002
    ELASTICITY_DIAG base per addict=   6.9730580326411898E-002  per experimenter=   4.0591121786882095E-002  addict share of users=  0.43178137931178262
    ELASTICITY_STEP participation step=   1.0000000000000000E-002  elasticity=   2.5837691404121710       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   1.0000000000000000E-002  elasticity=  -3.9598001684950730       observed= -0.55000000000000004
    ELASTICITY_STEP participation step=   2.0000000000000000E-002  elasticity=  -2.3370190312666157       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   2.0000000000000000E-002  elasticity=  -2.4603202010882232       observed= -0.55000000000000004
    ELASTICITY_STEP participation step=   5.0000000000000003E-002  elasticity=  -2.2396803706590158       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=   5.0000000000000003E-002  elasticity=  -1.5470312946358424       observed= -0.55000000000000004
    ELASTICITY_STEP participation step=  0.10000000000000001       elasticity=  -1.7784371199873983       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.10000000000000001       elasticity=  -1.2523460316096249       observed= -0.55000000000000004
    ELASTICITY_STEP participation step=  0.20000000000000001       elasticity=  -2.2815686941918552       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.20000000000000001       elasticity=  -1.1076323037682529       observed= -0.55000000000000004
    ELASTICITY_STEP participation step=  0.50000000000000000       elasticity=  -1.6834511546469861       observed= -0.63000000000000000
    ELASTICITY_STEP intensive     step=  0.50000000000000000       elasticity=  -1.0174929853671901       observed= -0.55000000000000004
    ELASTICITY_DRIFT price back at=   1.0000000000000000       base users=   8.1482141867657870E-002  users now=   8.4999694351484426E-002  per cent difference=   4.3169612423047399

## How it was measured, and what is not in the tree

Two source edits to `code/housing_first_or_treatment_first_SR_v1.f90`, NEITHER
committed:

1. the single step in the `HOLD THE BENCHMARK DISTRIBUTION AND ITERATE ONCE`
   block became a loop over the six, with the base recorded once before the
   loop, a `solve_value_function_and_policy_functions(1)` /
   `stationary_equilibrium_statistics(1)` / `govt_revenues_calc(1)` per step and
   no `converge_to_stationary_equilibrium` anywhere in it, followed by the drift
   check;
2. `measure_price_elasticity` set from 0 to 1.

Only this report is committed.

One honest note on the output. The loop was written to re-emit the ten per cent
step under the old `UNTARGETED price elasticity` names as well, guarded by
`abs(elasticity_step_now-elasticity_price_step)<1e-12`. That guard never fired,
because `elasticity_price_step` is declared as `0.10` -- a default-real literal
promoted to double, so it carries 0.100000001490116 -- while the step grid uses
`0.10d0`. The two differ by about 1.5e-9. No `UNTARGETED price elasticity` line
appears in the log. Nothing is lost: the ten per cent row of the table above is
that same quantity, and it reads -2.26448527581385, which is the -2.26 the model
has been reporting.
