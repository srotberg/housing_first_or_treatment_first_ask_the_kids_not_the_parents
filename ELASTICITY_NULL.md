# The drug price elasticity, measured against a zero price step

**At a zero price step the number of drug users moves by +8.6661 per cent.**
The base is 0.077555323720327488 and the "new price" point is
0.084276339432534667, at a price that is 1.0000000000000000 in both. Nothing
about the price changed; the price line in the two `ELASTICITY_DIAG` records is
byte-identical. If that movement were attributed to a ten per cent price step it
would read as a participation elasticity of

    log(0.084276339432534667 / 0.077555323720327488) / log(1.1) = +0.87199

That is the noise floor. The ten per cent step measured on the same binary the
same day gives a reported participation elasticity of **-3.2074**, so the
measurement clears its own noise floor in magnitude by a factor of about 3.7,
but 0.87199 of pure drift is sitting inside it — and it is sitting there with
the *wrong sign*, since at an unchanged price the model gains users rather than
losing them. The measurement is not holding everything fixed except the price.

The intensive margin is worse in proportion. At a zero price step quantity per
addict falls 2.8396 per cent, a spurious elasticity of **-0.30224**, against a
reported ten per cent figure of **-1.4821**. One fifth of the reported intensive
elasticity is present before the price is touched.

## The table

Both columns come from a `save` variant run at the vector on the `VECTOR` line
of `code/benchmark_of_record.txt`, on branch
`claude/two-period-addiction-hazard-d7gb61` at commit `4075635b`, with
`measure_price_elasticity=1`. The only difference between the columns is
`elasticity_price_step`.

* zero step: `code/variant_save_20260909T032035Z.log`, source md5 `bd680dd32002d64d330355724d943f71`
* ten per cent step: `code/variant_save_20260909T032530Z.log`, source md5 `235da2d3011834b065a3ef932ad7fe9c`

| | zero step | ten per cent step |
|---|---|---|
| base price | 1.0000000000000000 | 1.0000000000000000 |
| new price | 1.0000000000000000 | 1.1000000014901161 |
| base users | 7.7555323720327488E-002 | 7.7556971390729298E-002 |
| new users | 8.4276339432534667E-002 | 5.7129074686701704E-002 |
| ratio new/base users | 1.0866609200993584 | 0.73660785951642482 |
| base quantity per user | 5.3377756749205918E-002 | 5.3377587692598247E-002 |
| new quantity per user | 5.1286977934448370E-002 | 4.5350236039057183E-002 |
| base quantity per addict | 6.9911705773363586E-002 | 6.9910511197349937E-002 |
| new quantity per addict | 6.7926518437032429E-002 | 6.0700578856354201E-002 |
| reported participation elasticity | Infinity | -3.2074181511182185 |
| reported intensive elasticity | -Infinity | -1.4821373397010011 |

The two reported elasticities in the zero-step column are `Infinity` and
`-Infinity` because the model divides by `log(1+elasticity_price_step)`, which
is exactly zero when the step is zero. That is arithmetic, not a failure: the
signs are the informative part. `+Infinity` says users ROSE at an unchanged
price; `-Infinity` says quantity per addict FELL at an unchanged price. The two
contaminations run in opposite directions.

### The lines, verbatim

Zero step, `variant_save_20260909T032035Z.log`:

```
 ELASTICITY_DIAG base price=   1.0000000000000000       users=   7.7555323720327488E-002  quantity per user=   5.3377756749205918E-002
 ELASTICITY_DIAG base per addict=   6.9911705773363586E-002  per experimenter=   4.0808156735193203E-002  addict share of users=  0.43189234404118437
 ELASTICITY_DIAG new price=   1.0000000000000000       users=   8.4276339432534667E-002  quantity per user=   5.1286977934448370E-002
 UNTARGETED price elasticity, participation   model=                  Infinity  observed= -0.63000000000000000
 UNTARGETED price elasticity, intensive       model=                 -Infinity  observed= -0.55000000000000004
 DIAG elasticity, quantity per USER (mixed)      =                 -Infinity
 ELASTICITY_DIAG new per addict=   6.7926518437032429E-002  per experimenter=   3.9133907439523045E-002  addict share of users=  0.42208990688541193
 DIAG elasticity, quantity per ADDICT            =                 -Infinity
 DIAG elasticity, quantity per EXPERIMENTER      =                 -Infinity
 DIAG elasticity, ADDICT SHARE of users          =                 -Infinity
```

Ten per cent step, `variant_save_20260909T032530Z.log`:

```
 ELASTICITY_DIAG base price=   1.0000000000000000       users=   7.7556971390729298E-002  quantity per user=   5.3377587692598247E-002
 ELASTICITY_DIAG base per addict=   6.9910511197349937E-002  per experimenter=   4.0808129862199331E-002  addict share of users=  0.43190478764076523
 ELASTICITY_DIAG new price=   1.1000000014901161       users=   5.7129074686701704E-002  quantity per user=   4.5350236039057183E-002
 UNTARGETED price elasticity, participation   model=  -3.2074181511182185       observed= -0.63000000000000000
 UNTARGETED price elasticity, intensive       model=  -1.4821373397010011       observed= -0.55000000000000004
 DIAG elasticity, quantity per USER (mixed)      =  -1.7099492244585175
 ELASTICITY_DIAG new per addict=   6.0700578856354201E-002  per experimenter=   3.3776704721096493E-002  addict share of users=  0.42986129187122701
 DIAG elasticity, quantity per ADDICT            =  -1.4821373397010011
 DIAG elasticity, quantity per EXPERIMENTER      =  -1.9841528486158784
 DIAG elasticity, ADDICT SHARE of users          =  -4.9759483305159488E-002
```

## The movement is the extra convergence pass, not run-to-run noise

The two runs' bases agree to **0.0021 per cent** (0.077555323720327488 against
0.077556971390729298), and quantity per addict at the base agrees to 0.0017 per
cent. So the model is reproducible at the base to four decimal places in
relative terms. The 8.6661 per cent move at a zero price step is therefore not
scatter between runs; it is what the extra `converge_to_stationary_equilibrium`
call does to a distribution the main loop had already declared converged.

The distribution diagnostics say why. Each log carries exactly two `DIST_DONE`
lines, one for the main loop's convergence and one for the elasticity block's:

| | zero step | ten per cent step |
|---|---|---|
| base pass | `DIST_DONE sweeps= 43  final_distance= 5.7700085974071724E-004` | `DIST_DONE sweeps= 43  final_distance= 5.7772562159663643E-004` |
| new-price pass | `DIST_DONE sweeps= 30  final_distance= 5.3722696137710468E-004` | `DIST_DONE sweeps= 30  final_distance= 5.8149742980721786E-004` |

Neither run printed `DIST_STALL`, so neither hit the 200-sweep cap. The
stopping rule in force is `stopping_rule_stationary_distribution=6*10.d0**(-4)`,
set at line 39381 because `include_addiction==1`. The base stops at 5.77e-4,
just under that rule — and 30 further sweeps from there, at an unchanged price,
move total drug users by 8.7 per cent. A tolerance of 6e-4 on the largest
per-sweep change in the distribution is not tight enough to pin a share that is
itself 7.8e-2 and is read to four decimals.

## What the number would be if the drift were removed

Taking the drift as additive in logs, which is an assumption this run does not
test:

| | ten per cent | zero step | difference |
|---|---|---|---|
| participation | -3.207418 | +0.871991 | **-4.079409** |
| intensive (per addict) | -1.482137 | -0.302240 | **-1.179897** |

So the contamination is not flattering the participation elasticity — it is
masking it. Corrected this way the participation elasticity moves further from
the -0.63 data target, to about -4.08, not closer. The five-times-too-large
diagnosis stands and gets worse; what the null overturns is the idea that the
number as printed is a clean measurement of anything.

## The three checks that were asked for

**Did the zero-step run print `ELASTICITY HELD` or `ELASTICITY SKIPPED`?** No.
Neither string appears in either log (`grep -c` returns 0 in both). The block
ran to completion in both runs; the only `SKIPPED` line in either log is
`OMEGA SKIPPED    child counterfactual off by measure_child_gap`, which is the
child-gap block and is expected, since the vector sets `measure_child_gap=0`.

**Distribution convergence diagnostics.** Reported in the table above. Both
runs: 43 sweeps to 5.77e-4 at the base, 30 sweeps to 5.4e-4 / 5.8e-4 at the new
price, no stall, against a stopping rule of 6e-4.

**Does `model_total_drug_users` at the base equal the `MOMENT b` line in the
same log?** Yes, exactly, in both runs — same bits, no disagreement to report.
`MOMENT b` is printed at line 6976 of the source and the elasticity base is read
at line 7557; both are `model_total_drug_users(1)` inside the same
`print_all_moments` call, and nothing between them rebuilds it, because the
`measure_child_gap` block that would have is switched off.

| | log line | value |
|---|---|---|
| zero step, `MOMENT b` | 1111 | 7.7555323720327488E-002 |
| zero step, `ELASTICITY_DIAG base` | 1198 | 7.7555323720327488E-002 |
| ten per cent, `MOMENT b` | 1111 | 7.7556971390729298E-002 |
| ten per cent, `ELASTICITY_DIAG base` | 1198 | 7.7556971390729298E-002 |

Against the benchmark of record's `MOMENT b` of 7.7699947162643626E-002, both
runs come in 0.186 per cent low. That is a separate, much smaller
reproducibility gap between this container and the recorded run, and it does not
bear on the null.

## One thing found on the way

The elasticity block restores `price_of_addictive_good` when it finishes but
does **not** restore the distribution, and `save_vars_and_functions(1)` runs
after it, at the sweep's stop. So a `save` run with `measure_price_elasticity=1`
writes a benchmark state that carries the perturbed distribution. It shows in
the last line of each log:

```
zero step:      B SWEEP POINT DONE at b= 2.5498800000000000E-003  participation= 4.8704147168812745E-002
ten per cent:   B SWEEP POINT DONE at b= 2.5498800000000000E-003  participation= 3.2571496838468300E-002
```

Same vector, same b, and the reported sweep participation differs by 49.5 per
cent between the two — entirely because of which price the elasticity block left
the distribution at. The comment at the head of the block already records this
hazard for the child-gap counterfactual ("a counterfactual leaves its
distribution behind and this is one") and guards against omega running first,
but the guard runs one way only: it stops omega from contaminating the
elasticity, not the elasticity from contaminating everything printed and saved
after it. `measure_price_elasticity` should not be left at 1 for any run whose
state or whose `B SWEEP POINT DONE` row is going to be used.

## How to reproduce

On `claude/two-period-addiction-hazard-d7gb61` at `4075635b`, with
`grep -c "TAX STEP" code/housing_first_or_treatment_first_SR_v1.f90` returning 1:

```
sed -i 's/integer, parameter :: measure_price_elasticity=0/integer, parameter :: measure_price_elasticity=1/' \
    code/housing_first_or_treatment_first_SR_v1.f90
sed -i 's/real(8), parameter :: elasticity_price_step=0.10/real(8), parameter :: elasticity_price_step=0.0d0/' \
    code/housing_first_or_treatment_first_SR_v1.f90
V=$(grep -m1 '^VECTOR' code/benchmark_of_record.txt | sed 's/^VECTOR //')
bash code/run_variant.sh save $V
# then restore elasticity_price_step to 0.10 and run the same line again
```

Each `sed` matches exactly one line. Neither edit is committed here; only this
report is. Each run took 3 minutes on 4 cores and reported
`HANDOVER 80 of 80`, exit 0.
