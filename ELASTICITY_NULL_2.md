# The zero-step null, re-run on the fixed code

## A. Headline: the fix did NOT work

**At a price step of exactly ZERO, the number of drug users still moves by
+2.5394 per cent** — from 8.4279767453417642E-002 at a price of 1.0000000 to
8.6419989474221387E-002 at a price of 1.0000000. The threshold set for this test
was 0.01 per cent. The movement is 254 times that threshold. **The fix reduced
the contamination but did not remove it.**

Before the fix the same null moved users by +8.6661 per cent. After the fix it
moves them by +2.5394 per cent. The asymmetry the fix targeted was real and
about two thirds of the problem went with it, but a spurious price response of
the wrong sign remains, and it is still large enough to matter for the number
the paper quotes.

Expressed the way the model expresses it, the residual is a spurious
participation elasticity of **+0.26311** — positive, i.e. the wrong sign — and a
spurious intensive elasticity of **-0.053333**, both scaled by the log(1.1) the
ten-per-cent run divides by. Set against the ten-per-cent results below, the
residual drift is 7.1 per cent of the reported participation elasticity and 4.6
per cent of the reported intensive one.

### What the residual says about the cause

The fix assumed the whole error was an asymmetry: base read off the main loop,
raised point given an extra solve-and-converge. It made the two points
symmetric, and the null shows the two points are indeed now produced by the same
procedure — the base is reproducible to 1.6e-06 across the two independent runs
below (8.4279767453417642E-002 against 8.4279635439243342E-002, a difference of
-0.000157 per cent, which is what solver noise actually looks like here). The
+2.5394 per cent is 16,000 times that noise floor. It is not noise.

What it is, is that **the solve does not stop moving when you solve again.**
Line up the three measurements of the same object at the same unchanged price:

| passes past the main loop | users | move from previous |
| --- | --- | --- |
| 0 (main loop distribution, pre-fix base) | 7.7555323720327488E-002 | -- |
| 1 (pre-fix raised point; this run's base) | 8.4276339432534667E-002 / 8.4279767453417642E-002 | +8.6661 per cent |
| 2 (this run's zero-step "new" point) | 8.6419989474221387E-002 | +2.5394 per cent |

The pre-fix one-pass figure and this run's base agree to 4.1e-05, which
confirms the two runs are measuring the same sequence. Each additional
solve-and-converge at an unchanged price moves participation again, by a
decaying but not-yet-negligible amount. The extra base solve did not put both
points on a converged object; it moved both points one step further along a
sequence that has not converged. Making the two points symmetric cannot fix
that, because the two points are one step apart on that sequence by
construction — which is exactly the price step's job, and exactly what
contaminates it.

The note left in the source ("one more pass at an unchanged price moving
participation by 8.7 per cent says the main loop's own convergence is loose in
the moment that matters most here") turns out to be the whole finding rather
than a footnote to it. The remedy is a tighter convergence tolerance on the
distribution, or iterating the base to a fixed point before the step is taken,
not a symmetric pair of loose solves.

## B. Both runs, ELASTICITY_DIAG quoted verbatim

| | zero step | ten-per-cent step |
| --- | --- | --- |
| base price | 1.0000000000000000 | 1.0000000000000000 |
| new price | 1.0000000000000000 | 1.1000000014901161 |
| base users | 8.4279767453417642E-002 | 8.4279635439243342E-002 |
| new users | 8.6419989474221387E-002 | 5.9109519245373457E-002 |
| ratio new/base users | 1.0253942564 | 0.7013499636 |
| base quantity per user | 5.1287673249306207E-002 | 5.1287437917398232E-002 |
| new quantity per user | 5.0948330271334323E-002 | 4.5222006249521711E-002 |
| base quantity per addict | 6.7927757423862214E-002 | 6.7926729832346572E-002 |
| new quantity per addict | 6.7583341719207324E-002 | 6.0800752643980320E-002 |
| reported participation elasticity | Infinity | -3.7220397384536730 |
| reported intensive elasticity | -Infinity | -1.1628081337323659 |

The zero-step column reports Infinity and -Infinity because the model divides by
log(1+elasticity_price_step) and that denominator is zero. The arithmetic is
uninformative; the **signs** are not. Participation reports `+Infinity`: users
went UP when the price did not change. Quantity per addict reports `-Infinity`:
it went DOWN. Those are the signs of the two spurious components, and the
participation one is opposite to the sign the price response is supposed to have.

Zero-step log, verbatim:

```
 ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.4279767453417642E-002  quantity per user=   5.1287673249306207E-002
 ELASTICITY_DIAG base per addict=   6.7927757423862214E-002  per experimenter=   3.9133684605013180E-002  addict share of users=  0.42210036491735980
 ELASTICITY_DIAG new price=   1.0000000000000000       users=   8.6419989474221387E-002  quantity per user=   5.0948330271334323E-002
 UNTARGETED price elasticity, participation   model=                  Infinity  observed= -0.63000000000000000
 UNTARGETED price elasticity, intensive       model=                 -Infinity  observed= -0.55000000000000004
 DIAG elasticity, quantity per USER (mixed)      =                 -Infinity
 ELASTICITY_DIAG new per addict=   6.7583341719207324E-002  per experimenter=   3.8827941133065973E-002  addict share of users=  0.42149957542618893
 DIAG elasticity, quantity per ADDICT            =                 -Infinity
 DIAG elasticity, quantity per EXPERIMENTER      =                 -Infinity
 DIAG elasticity, ADDICT SHARE of users          =                 -Infinity
```

Ten-per-cent log, verbatim:

```
 ELASTICITY_DIAG base price=   1.0000000000000000       users=   8.4279635439243342E-002  quantity per user=   5.1287437917398232E-002
 ELASTICITY_DIAG base per addict=   6.7926729832346572E-002  per experimenter=   3.9134010819288488E-002  addict share of users=  0.42210070860614773
 ELASTICITY_DIAG new price=   1.1000000014901161       users=   5.9109519245373457E-002  quantity per user=   4.5222006249521711E-002
 UNTARGETED price elasticity, participation   model=  -3.7220397384536730       observed= -0.63000000000000000
 UNTARGETED price elasticity, intensive       model=  -1.1628081337323659       observed= -0.55000000000000004
 DIAG elasticity, quantity per USER (mixed)      =  -1.3205516291029400
 ELASTICITY_DIAG new per addict=   6.0800752643980320E-002  per experimenter=   3.3347972380940012E-002  addict share of users=  0.43252573163117014
 DIAG elasticity, quantity per ADDICT            =  -1.1628081337323659
 DIAG elasticity, quantity per EXPERIMENTER      =  -1.6786764702094397
 DIAG elasticity, ADDICT SHARE of users          =  0.25598407070202300
```

In the zero-step run the addict share of users also moves, 0.42210036491735980
to 0.42149957542618893, -0.14233 per cent, at an unchanged price. The
composition of the user pool drifts along with its size.

## C. The ten-per-cent elasticities on the fixed code

| | fixed code | pre-fix | move | data target | model / target |
| --- | --- | --- | --- | --- | --- |
| participation | **-3.7220397384536730** | -3.2074 | -0.514640 | -0.63 | 5.9080 |
| intensive (per addict) | **-1.1628081337323659** | -1.4821 | +0.319292 | -0.55 | 2.1142 |
| quantity per user (mixed, diagnostic) | -1.3205516291029400 | -- | -- | -- | -- |

Removing the asymmetry moved participation **0.514640 further from zero** and
intensive **0.319292 closer to zero**. The two moved in opposite directions,
which is what the pre-fix decomposition predicted: the spurious component was
+0.87199 on participation (wrong sign, so removing it makes the number more
negative) and -0.30224 on intensive (right sign, so removing it makes the number
less negative). The realised moves are smaller than those two figures on
participation and slightly larger on intensive, because the fix moved the base
point as well as removing the asymmetry.

Both numbers remain far from the data. Participation is 5.9080 times the
observed -0.63; the intensive margin is 2.1142 times the observed -0.55. The
intensive figure of -1.1628 is now inside the roughly -1.3 bound the first order
condition puts on an individual, which the earlier per-user statistic of -5.06
was not; the per-user diagnostic here is -1.3206, still at that bound, and the
gap between -1.3206 and -1.1628 is the composition effect, worth 0.15776.

**These numbers are not yet clean.** Section A shows a residual +0.26311 of
spurious participation response and -0.053333 of spurious intensive response
still sitting inside them, with the participation contamination pushing in the
wrong direction. Subtracting the null's residual gives -3.985151 participation
and -1.109475 intensive as an indication of where a converged measurement would
sit. That subtraction is an estimate, not a measurement — the drift need not be
additive in logs across a genuine price change — and it should not be quoted as
a result. What should be taken from it is the sign and the size: the paper's
participation elasticity is, if anything, understated in magnitude by the
remaining contamination, and no version of these two numbers should go into the
paper until the null returns zero.

## D. ELASTICITY HELD / ELASTICITY SKIPPED

Neither run printed either line. Counts are 0 and 0 in both logs, checked
directly:

```
variant_save_20260909T034507Z.log  (zero step)   ELASTICITY HELD: 0   ELASTICITY SKIPPED: 0
variant_save_20260909T035316Z.log  (ten per cent) ELASTICITY HELD: 0   ELASTICITY SKIPPED: 0
```

Both runs also reported `HANDOVER 80 of 80` and exit status 0, so both took the
vector they were given.

## E. Solve times, and what the extra base solve cost

Four cores. Both runs took the same wall clock to the second-and-a-bit.

| | zero step | ten-per-cent step |
| --- | --- | --- |
| log opened | 2026-09-09 03:45:07Z | 2026-09-09 03:53:16Z |
| log closed | 2026-09-09 03:51:22Z | 2026-09-09 03:59:31Z |
| wall clock | 375 s (6 min 15 s) | 375 s (6 min 15 s) |
| value-function solves | 4 | 4 |
| wall seconds per solve | 71.4, 70.8, 70.6, 71.0 | 71.3, 71.0, 70.5, 70.9 |
| total in value-function solves | 283.9 s | 283.6 s |
| everything else (distribution passes, statistics, revenues, I/O) | 91.1 s | 91.4 s |
| gfortran -O3 build (not counted above) | ~81 s | ~76 s |

The fix adds one `solve_value_function_and_policy_functions` plus one
`converge_to_stationary_equilibrium` at the base price. That is one of the four
solves above: **about 71 s of value-function time**, plus its share of the 91 s
of distribution and statistics work, on a run that would otherwise have made
three solves. The run is roughly a quarter longer than it was before the fix.

That is a cheap price for a symmetric measurement and it should be kept. It is
simply not sufficient — the same 71 s spent iterating the base to convergence
instead of taking one more step along an unconverged sequence is where the
remaining +2.5394 per cent has to be attacked.

## Provenance

- Repository `srotberg/housing_first_or_treatment_first`, branch
  `claude/two-period-addiction-hazard-d7gb61`, commit
  `ca042a05adc224409572b93b9ece43fc50a7c8ca` ("Measure both elasticity points
  the same way"). `grep -c "MEASURE BOTH POINTS THE SAME WAY"` on
  `code/housing_first_or_treatment_first_SR_v1.f90` returned 1 before either run.
- Two source edits only, neither committed: `measure_price_elasticity` 0 to 1
  for both runs, and `elasticity_price_step` 0.10 to 0.0d0 for the first run,
  restored to 0.10 for the second. Both `grep -c` checks returned 1 each time.
- Vector: the `VECTOR` line of `code/benchmark_of_record.txt`, 80 parameters,
  passed to `bash code/run_variant.sh save`.
- Logs: `code/variant_save_20260909T034507Z.log` (zero step) and
  `code/variant_save_20260909T035316Z.log` (ten per cent). Both are run outputs
  and are not committed.
