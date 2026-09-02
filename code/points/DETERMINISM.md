# Three cold runs of one vector on one source: the model is reproducible

`REPRODUCIBILITY.md` recorded that two runs of one tag do not agree exactly and
bounded the disagreement at 2.8e-04 on the worst targeted moment. Then tag
`f9c16d5308` was measured twice on `MODEL c823331449` and the two disagreed by
2.85 per cent on `w_bot` -- a hundred times the documented bound, against a
calibration objective of ten per cent. Either the earlier bound was wrong or
something else was going on. This is the experiment that decides it.

**Verdict: REPRODUCIBLE.** Worst relative spread over the 23 targeted moments is
**5.13e-05**, median **8.80e-06**, both comfortably below the 1e-3 threshold.
The 2.85 per cent disagreement did not come from the solver being
nondeterministic. It came from a bug that has since been fixed, and the
evidence for that is in the last section.

## The three runs

Same vector, same source, same container, sequential, cold, one after another.
`run_one_point.sh` deletes `calibration_state.dat` and
`calibration_distribution*.dat` before every solve, so no run warm-started off
its predecessor. Between runs the point file was moved to `RUN1_`/`RUN2_` so the
already-measured guard did not turn runs 2 and 3 into no-ops.

The vector is line 1 of `code/batch_validate.txt`, the anchor with
`include_unsecured_borrowing=0`. Its `VECTOR` line is byte-identical in all
three point files (md5 `96657e26d534200c25d17a7c8ac8d727`), and all three
record `HANDOVER OK: 42 of 42 parameters applied`.

| | `MODEL` stamp | full source md5 | wall | cores |
|---|---|---|---|---|
| RUN1 | `b8dc1077ad` | `b8dc1077adc90fe0d9b497289e93e7c5` | 14 min | 4 |
| RUN2 | `b8dc1077ad` | `b8dc1077adc90fe0d9b497289e93e7c5` | 15 min | 4 |
| RUN3 | `b8dc1077ad` | `b8dc1077adc90fe0d9b497289e93e7c5` | 14 min | 4 |

Semantic hash `2f7c317e75` for all three, via `model_hash.resolve`. The full
md5 was checked before run 1, between each pair of runs and after run 3, and
never moved. `hftf` was built ONCE, at the head of run 1, from
`b8dc1077adc90fe0d9b497289e93e7c5` (`run_one_point: built hftf from ...`);
runs 2 and 3 found `hftf.srcmd5` matching and reused that same binary, so the
three runs are one binary as well as one source. Nothing was pulled into the
working tree between runs -- the branch moved under us four times and each
merge was gated on the `.f90` being untouched, which it was.

## The targeted moments

Relative spread is `(max-min)/mean` over the three runs.

| moment | what it is | RUN1 | RUN2 | RUN3 | rel spread |
|---|---|---|---|---|---|
| `sigma_y` | bottom half earnings share | 0.169050021402 | 0.169050021402 | 0.169050021402 | 0.00e+00 |
| `tau_l` | average labour income tax | 0.234373729316 | 0.234373911240 | 0.234373098528 | 3.47e-06 |
| `omega_l` | labour supply / total hours | 0.378556375075 | 0.378555699175 | 0.378555648576 | 1.92e-06 |
| `beta` | wealth over output | 2.68468851405 | 2.68464177882 | 2.68463764712 | 1.89e-05 |
| `h_2` | above half of spending | 0.106813286400 | 0.106816224801 | 0.106817094062 | 3.56e-05 |
| `h_3` | share in the largest unit | 0.479579808142 | 0.479580213627 | 0.479581532436 | 3.60e-06 |
| `gamma` | housing over expenditure | 0.137603051807 | 0.137603204927 | 0.137603408431 | 2.59e-06 |
| `h_1` | homelessness rate | 0.0841780340867 | 0.0841766463463 | 0.0841768026376 | 1.65e-05 |
| `b` | total drug users | 0.399882640798 | 0.399892421716 | 0.399891958371 | 2.45e-05 |
| `lambda_d` | disorder rate | 0.294572489801 | 0.294582726995 | 0.294582310151 | 3.48e-05 |
| `theta` | drug spending share | 0.331141830383 | 0.331142217686 | 0.331142758611 | 2.80e-06 |
| `aleph` | value of life / income | 50.3344941142 | 50.3335256082 | 50.3335554719 | 1.92e-05 |
| `pi_eu` | unemployment rate | 0.260790491648 | 0.260795781820 | 0.260796252015 | 2.21e-05 |
| `kappa_ued` | unemployment given SUD | 0.522615250346 | 0.522616096028 | 0.522615830362 | 1.62e-06 |
| `kappa_uem` | employment given SMI | 0.0665189919567 | 0.0665185360087 | 0.0665185488582 | 6.85e-06 |
| `p_m` | SMI population share | 0.0505167144595 | 0.0505162699893 | 0.0505162904708 | 8.80e-06 |
| `lambda_m` | SMI share of the homeless | 0.0259739975409 | 0.0259740257944 | 0.0259739991914 | 1.09e-06 |
| `pi_V` | eligibles with a voucher | 0.179214233692 | 0.179213066721 | 0.179213102309 | 6.51e-06 |
| `cbar` | food stamps / income | 0.00861649303532 | 0.00861669634466 | 0.00861671435280 | 2.57e-05 |
| `tau_u` | treatment take up | 6.16367190685e-13 | 6.16335587403e-13 | 6.16336953381e-13 | 5.13e-05 |
| `mu_H` | recovery housed / homeless | 1.09171727907 | 1.09171744778 | 1.09171741474 | 1.55e-07 |
| **`w_bot`** | **net worth share, bottom half** | **0.0294872883971** | **0.0294868339801** | **0.0294872478172** | **1.54e-05** |
| `y_u` | income of drug users | 0.710111463619 | 0.710121653743 | 0.710118987212 | 1.43e-05 |

    worst   5.13e-05   tau_u, treatment take up
    second  3.56e-05   h_2
    third   3.48e-05   lambda_d
    median  8.80e-06
    identical to every printed digit in all three: sigma_y, and it is also
    identical across all four economies in the table further down, which puts
    it outside the solved equilibrium -- consistent with it being a function of
    the exogenous productivity process alone, though that was not traced in the
    source

`tau_u` is worst on a relative scale and is 6.16e-13 in absolute terms -- it is
zero to any purpose, and its relative spread is the ratio of two numbers that
are both noise. The same shape `REPRODUCIBILITY.md` described holds here: the
large relative differences sit on small quantities.

## `w_bot`, against the two runs that disagreed

    RUN1                                  0.0294872883971
    RUN2                                  0.0294868339801
    RUN3                                  0.0294872478172
    spread over the three                 1.54e-05

    the pair that disagreed, on c823331449:
      point_f9c16d5308.on_c823331449      0.029486027
      the 17 min run (now ...045754Z)     0.030328095
    spread over that pair                 2.82e-02   (2.82 per cent)

The brief quotes this as 2.85 per cent; that is the same gap over the smaller
value instead of the mean. The table above uses (max-min)/mean throughout, so
2.82e-02 is the figure on this page's metric. Nothing turns on the choice.

The disagreement is **1827 times** the spread of these three runs. Whatever
produced it, it is not the run-to-run variability of the solver on this source.

Two things turned up while checking this that are worth recording, because
neither is visible from the two files named in the brief.

**There are six measurements of this tag in the repository, not two**, across
four semantically distinct economies. On `c823331449` alone there are three,
and they are bimodal rather than scattered:

| file | economy | wall | `w_bot` |
|---|---|---|---|
| `point_f9c16d5308.20260902T034843Z` | `fdc6078859` | 11 min | 0.0294867054 |
| `point_f9c16d5308.20260902T041500Z` | `fdc6078859` | 14 min | 0.0294855758 |
| `point_f9c16d5308.20260902T041536Z` | `99752a3cab` | 8 min | 0.0032694523 |
| `point_f9c16d5308.on_c823331449` | `17529c7177` | 11 min | 0.0294860272 |
| `point_f9c16d5308.20260902T045414Z` | `17529c7177` | 11 min | 0.0303241662 |
| `point_f9c16d5308.20260902T045754Z` | `17529c7177` | 17 min | 0.0303280954 |

Two of the three `c823331449` runs land at 0.03032 and agree with each other to
1.3e-04; the third sits 2.8 per cent below. So the brief's framing of "one of
these two is right" understates it -- the pre-fix economy had two attractors,
not a spread, which is the signature of an execution-path difference rather
than accumulated rounding.

**`DIST_DONE` is not in the point files.** It is printed before the
`ALL TARGETED MOMENTS` block that `run_one_point.sh` extracts, so the sweep
counts and convergence distances of those historical runs are not recoverable
from the repository. The mechanism below is therefore established on the
post-fix runs and on the source, not by re-reading the disagreeing pair's logs.

## Why -- and the part that is not determined

The solver is not the source of the 2.85 per cent. Three things were held and
checked rather than assumed, and all three were identical across the runs:

- **Iteration count.** `DIST_DONE sweeps= 51` and `sweeps= 30`, in all three
  runs, for the two distribution solves.
- **Convergence distance.** `final_distance= 5.9971205036415606E-004` and
  `5.9165113130462636E-004`, identical to all seventeen digits in all three.
- **Thread count.** `number of threads = 4` at each of the three parallel
  regions, in all three runs; `OMP_NUM_THREADS=$(nproc)` on a 4-core container.

So no run took a different path through the equilibrium loop. What residual
there is enters after it: filtering wall-clock lines out of the worker logs,
the first numeric divergence between any pair of runs is at log line 782, the
line immediately after the first `DIST_DONE`, where `mass_homeless` reads
1.33768544438916 against 1.33768544629036 -- 1.4e-09 relative -- while
`inc_homeless` on the same line is bit-identical. That 1e-09 is what grows to
1e-05 in the moments through the outer secants.

`distance_distribution` is a max-norm (`maxval(abs(implied-guess))`, 25501), so
it is set by the single worst cell and is blind to a 1e-09 wobble in every other
cell. That is how the stopping metric can be bit-identical while aggregates
taken from the distribution are not.

**The origin of that 1e-09 is not determined, and is stated as such.**
`stationary_equilibrium_statistics` contains no OpenMP directives, so the
accumulation is serial and the difference must already be in the distribution
array. The obvious explanations were checked and do not hold: the per-thread
slices are summed in a fixed ordered loop (`do thread_index=1,
total_number_of_threads`, 25443), no `!$omp parallel do` in the file carries a
`schedule()` clause so libgomp assigns iterations statically, and
`total_number_of_threads` is set correctly inside `!$omp parallel/!$omp master`
at 24567. The unsynchronised shared `is_addicted_1` that `REPRODUCIBILITY.md`
flagged at 24528 remains a candidate and was not ruled in or out here. At 1e-09
it does not matter for anything the calibration does; it is recorded so nobody
re-derives it.

### The 2.85 per cent, which does have an answer

This is a controlled comparison, and it is clean:

    c823331449  =  the .f90 at d9ff1a8^     (both disagreeing runs)
    b8dc1077ad  =  the .f90 at d9ff1a8      (these three runs)

`d9ff1a8` -- "the bounds checker found a real one: three wealth walks keyed on
an unset age" -- is the *only* source commit between the two economies. So the
pre-fix and post-fix runs differ by exactly that fix and nothing else.

The old-age renter wealth profile, the quantity `w_bot` is a share of:

| age | pre-fix spread, 3 runs on `c823331449` | post-fix spread, 3 runs on `b8dc1077ad` |
|---|---|---|
| 74 | 2.94e-02 | 0 |
| 76 | 2.96e-02 | 1.41e-05 |
| 78 | 2.87e-02 | 0 |
| 80 | 2.60e-02 | 0 |
| 82 | 2.29e-02 | 0 |
| 84 | 2.04e-02 | 0 |
| 85 | 2.00e-02 | 0 |

Every age from 74 to 85 moved by 2.0 to 3.0 per cent before the fix, which is
the 2.8 per cent seen in `w_bot`. After it, nine of those twelve ages are
identical to every digit printed and the worst of the other three is 3.4e-05. Three orders of
magnitude, on exactly the quantity that disagreed, from exactly one commit.

That fix was made for an unrelated reason -- a bounds checker aborted in
`stationary_equilibrium_wealth_distribution_of_old`, where the walk's stopping
rule was bounded on `renter_floor_by_age(age_index)` with `age_index` unset in
that routine. Different leftover values on different execution paths stopped
the walk in different places, which is also why the pre-fix runs are bimodal
rather than scattered.

## What this means for the calibration

- **Single runs are trustworthy on this source.** A targeted moment is good to
  about 5e-05 relative, four orders of magnitude inside the ten per cent
  objective. The brackets measured before this test do not need re-measuring
  *for determinism* -- but anything measured on `c823331449` or earlier carries
  the old-age wealth bug, and that is a correctness question, not this one.
- **Quote a targeted moment to four significant figures, not more.** Unchanged
  from `REPRODUCIBILITY.md`, and this test is consistent with it: the earlier
  pair's 2.8e-04 worst and this triple's 5.1e-05 worst sit within a factor of
  six of each other, well inside four significant figures either way.
- **Re-running a point still will not reproduce it byte for byte.** 262 of the
  667 numbers in the point file differ across these three runs (39 per cent),
  much as `REPRODUCIBILITY.md` found. The worst over all 667 is 1.12e-03, on an
  untargeted `DIAG` line at age 49 -- a small quantity printed to six decimals.
  The targeted moments are the tight end, and they are the ones that matter.

## Reproducing this

    git checkout d9ff1a8            # or any commit with .f90 md5 b8dc1077ad...
    bash code/run_one_point.sh <line 1 of code/batch_validate.txt>
    mv code/points/point_f9c16d5308.txt code/points/RUN1_f9c16d5308.txt
    # repeat twice more, moving the file aside each time

The three point files are committed beside this note as
`RUN1_f9c16d5308.txt`, `RUN2_f9c16d5308.txt` and `RUN3_f9c16d5308.txt`.
