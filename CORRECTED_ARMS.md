# The conditional arms at the corrected enforcement rates

Recorded here because `.gitignore` line 5 excludes `*.log`, so every number
below otherwise lives only on an ephemeral container's disk.

## Why these were re-run

`benchmark_of_record.txt`'s VECTOR carried `probability_of_detection=0.9` and
`probability_of_false_positive=0.05`, and its handover beats both the Fortran
declaration and `run_one_point.sh`'s defaults, so the author's chosen 0.95 /
0.005 never bound. The record regenerates from a run that echoes its own
vector, so the wrong values self-perpetuated. These arms pass the rates on the
command line, and each log is verified: `voucher_probabilities` prints
`0.995 0.995 0.05`, i.e. `1-p_fp` and `1-p_det`.

## Benchmark of record

Frozen-equilibrium converged, `FROZEN CONVERGED after 3 passes,
distance = 1.66e-5`, log `variant_save_20260909T075231Z.log`.

    b 0.0853159   lambda_d 0.0363024   h_1 0.0125524   pi_V 0.251031
    tau_l 0.207843   beta 3.49804   aleph 75.1749   price 1.0

## The arms

| | benchmark | condition, no steering | condition + steering | universal HF | universal TF |
|---|---|---|---|---|---|
| rates | -- | 0.95/0.005 | 0.95/0.005 | n/a, no condition | 0.95/0.005 |
| `b` | 0.08532 | 0.05253 (-38.4%) | 0.05036 (-41.0%) | 0.11412 (+33.8%) | -- |
| `lambda_d` | 0.03630 | 0.02097 (-42.2%) | 0.01901 (-47.6%) | 0.05067 (+39.6%) | -- |
| `h_1` | 0.01255 | 0.01531 (+22.0%) | 0.01472 (+17.3%) | 0.00019 (-98.5%) | -- |
| `pi_V` | 0.2510 | 0.1765 | 0.1790 | 0.8527 | -- |
| `tau_l` | 0.2078 | 0.2028 | 0.2028 | 0.2479 | -- |
| `beta` | 3.4980 | 3.5601 | 3.5582 | 2.6743 | -- |
| `aleph` | 75.17 | 75.55 | 75.75 | 100.91 | -- |
| welfare (CEV) | -- | -3.99% | -4.18% | +38.4% | **unusable** |
| drug price | 1.0 | 0.8033 | 0.7807 | -- | 0.6696 |
| loops | -- | 50 | 51 | 42 | 80 (the cap) |
| drug-market gap | -- | 3.85e-3 | 1.57e-3 | 1.55e-3 | **0.541** |

Tolerances: drug market 5e-3, government budget 2.5e-2, counterfactual moments
5e-4. Logs: `variant_cf_20260909T150812Z` (rationed TF),
`variant_cf_20260909T173844Z` (condition + steering, mislabelled b3_cond_only),
`variant_cf_20260909T064500Z` (universal HF),
`variant_cf_20260909T160315Z` (universal TF).

## What the arms say

**THE 19:30 CORRECTION BELOW IS ITSELF WRONG. SETTLED 21:15 AGAINST THE CODE.**

`increased_prob_of_voucher_if_homeless_and_addicted` multiplies the voucher
offer probability for households who are BOTH homeless AND addicted. At 1 they
enter the lottery on the same terms as everyone else; at **0 they are excluded
from voucher offers entirely**. The benchmark has it at 1.

**That flag IS the Treatment-First / Housing-First switch**, and the model names
the arms itself at line 9271:

| offer prob | homeless-and-addicted | the code's own file_number |
|---|---|---|
| 1 | 0 | `counter_VTE_TF` -- universal Treatment First |
| 1 | 1 | `counter_VTE_HF` -- universal Housing First |
| < 1 | 0 | `counter_TF` -- rationed Treatment First |

Each arm's own VECTOR line, read back: `b1` cond=1 flag=0 offer=0.0433173 --
**rationed TF, exactly as first labelled**. `b2` cond=1 flag=0 offer=1 --
universal TF. `a4` cond=0 flag=1 offer=1 -- universal HF. So the ORIGINAL
labels were right, the 19:30 "correction" was the error, and "steering" is a
word I invented that describes nothing in this model. Excluding the addicted
homeless from housing is what makes a policy Treatment First.

**`b3` is therefore a fourth cell nobody asked for, and it is the most
informative one in the set**: cond=1, flag=1, rationed -- the sobriety
condition applied WITHOUT the categorical exclusion.

| | rationed TF (excludes addicted homeless) | condition only (no exclusion) |
|---|---|---|
| drug use | -38.4% | **-40.8%** |
| homelessness | +22.0% | **+17.3%** |

Same sobriety test, better on both margins without the exclusion. Excluding the
addicted homeless removes their reason to get clean -- there is no voucher to
earn -- so they use more and stay homeless more.

**ALSO RECORDED: the three-year exclusion is NOT in the model.** A search for
any multi-period ban state (`years_excluded`, `consecutive`, `reinstate`, and
the rest) returns nothing. The sanction that actually runs is ONE PERIOD: fail a
test, lose the voucher that period with probability `p_det`, and re-enter the
lottery the next period. A three-year exclusion would be a materially stronger
policy than anything measured here.

---

~~WRONG, AND CORRECTED 9 SEPTEMBER 19:30. The arm labelled "conditionality
only" is not conditionality only.~~ Its launch flags are
`voucher_conditional_on_clean=1` PLUS
`increased_prob_of_voucher_if_homeless_and_addicted=1`, and the arm labelled
"rationed TF" is `voucher_conditional_on_clean=1` with that steering flag at
**0**. So the pair is not condition-alone against condition-plus-steering with
the steering on the wrong side; it is the exact reverse of how it was read.
The claim struck through below -- that the sobriety condition is the whole
mechanism and steering buys nothing -- was taken from the FILENAMES without
checking the flags, and it is backwards.

**What the two arms actually say.** `b1` is the condition with no steering;
`b3` is the condition plus steering toward the homeless-and-addicted. Adding
steering:

| | condition alone (`b1`) | condition + steering (`b3`) |
|---|---|---|
| `b` | -38.4% | **-40.8%** |
| `h_1` | +22.0% | **+17.3%** |
| `pi_V` | 0.1765 | 0.1790 |
| welfare | -3.99% | -4.18% |

**Steering helps on both real margins** -- more drug-use reduction and less of
the homelessness the condition causes -- at a welfare cost of 0.2 points. That
is the opposite of "buys nothing".

**But read it against the resolution.** Four benchmark saves put `b` in a band
of 2.8e-4, inside the frozen loop's own 5e-4 rule, so the benchmark is pinned
to roughly +/-0.6 per cent on `b`. The 2.4-point gap between -38.4 and -40.8
is close to that floor. The DIRECTION is a result; the size is not yet one, and
both arms are due a re-run against the corrected eligibility cutoff anyway.

~~The sobriety condition is the whole mechanism. Conditionality alone gets MORE
drug-use reduction than rationed treatment first (-41.0 against -38.4), LESS
homelessness (+17.3 against +22.0), the same tax to four digits and welfare
within 0.2 points. The steering machinery on top of the condition buys
nothing.~~

**`beta`'s rise was the false-positive rate.** Two independent converged arms
put it at 3.5601 and 3.5582 against a benchmark 3.4980 -- up 1.7 to 1.8 per
cent. At the buggy rates the same rationed arm gave 3.8320 (+9.6%) and
universal TF gave 4.3296 (+23.8%). `p_fp = 0.05` was a five per cent annual
chance of wrongful voucher removal for every CLEAN eligible household, an
uninsurable shock to exactly the households with the least buffer; they
self-insured by saving. At 0.005 the motive nearly disappears. Bequests move
the same way: 0.6907 benchmark, 0.7693 at the old rates, 0.6993 corrected.

**Treatment first loses on welfare by construction, and that is a modelling
choice rather than a defect.** The addictive good enters utility at line 23044
as `(b_shifter + addiction/price)**relative_share_of_addiction_1` with weight
0.27, and the compensating variation scales ONLY non-drug consumption (line
17903). Conditionality destroys utility from a good carrying a 27 per cent
weight and the CEV must buy it back in the one good it may move. Whether the
paper's welfare criterion should count addicts' drug consumption at full
weight is the author's call.

## UNIVERSAL TF DID NOT CONVERGE. DO NOT USE ITS NUMBER.

It exited on `max_counterfactual_loops = 80` with the drug market at 0.541,
price 0.6696 against an implied supply price of 0.1323 -- a market five times
from clearing. It nevertheless printed
`welfare_of_gains_by_addiction = +0.1269`, which looks like a result and is
not one.

WHY. Correcting `p_fp` collapses demand in that arm to `V = 0.0072`, so the
market clears at a small fraction of the benchmark price.
`max_drug_price_move = 0.005` -- the author's half a per cent a loop, set 8
September -- cannot walk from 1.0 to there inside 80 loops. The cap bound on
every one of the 80 loops.

This is specific to the collapsed-demand regime and NOT general to the
corrected rates: conditionality only converged in 51 loops because its
quantity RISES as the price falls (0.1023, 0.1054, 0.1063) so the implied
price climbs to meet it, which is an ordinary demand curve. A prediction that
it would hit the cap too was made and withdrawn on the evidence.

THE FIX IS A WARM START, not a bigger cap: seed the counterfactual's starting
price near the answer. It changes no equilibrium condition and leaves
`max_drug_price_move` exactly as the author set it. `relative_price_change` at
line 22 is a compile-time `parameter`, so this needs a `drug_price_start`
handover case.

## THESE SIT ON A BENCHMARK THAT IS NOT CALIBRATED

Eight of twenty-five moments miss by more than the author's ten per cent
rule: `w_bot` +268%, `kappa_uem` +174%, `h_3` -89%, `kappa_ued` +27%,
`h_2` +25%, `lambda_m` -24%, `y_u` -23%, `beta` +17%. Of those:

- **`w_bot` is the newborn endowment and no refit will reach it.** Splitting
  2,785 archived points on that switch alone: `newborn_endowment_scale = 0`
  gives median `w_bot` 0.0351, `> 0` gives 0.0848, against a 0.025 target.
  Cross-tabulated against `kappa_uem` to rule out confounding: holding
  `kappa_uem > 10`, endowment 0 -> positive moves `w_bot` 0.0342 -> 0.094;
  holding the endowment positive, `kappa_uem > 10` -> `<= 1.5` moves it only
  0.0936 -> 0.0911. The target and the author's fixed newborn endowment are in
  direct conflict.
- **`kappa_uem` is a regression, not an unexplored lever.** The archive holds
  points at 12 and 34; the benchmark of record carries 1, so SMI households
  separate at exactly the same rate as everyone else and the channel is off.
  One archived point has `kappa_uem = 12` and `w_bot = 0.0230` together.
- **`beta` is ordinary.** The `endowment > 0` bucket has median `beta` 3.000,
  exactly on target; 3.498 is a point in the spread, reachable by
  `discount_factor`.

## The scoring tools carried targets the Fortran had stopped using

`code/suggest_next.py` and `code/converge.py` scored against `h_1` 0.00399
(live `fraction_homeless_data` 0.01160), `h_2` 0.132065 (live
`severe_cost_burden_data` 0.08), `theta` 0.1620 (live
`drug_spending_share_data` 0.14098), `p_m` 0.0 (live 0.0484785) and `pi_eu`
0.0485 (live `unemployment_rate_data` 0.049). The Fortran calibrates against
its own `_data` parameters and was never affected, but a refit that used these
tools to choose directions would have driven `h_1` down by a factor of three.

## The standing two-build check, 9 September 18:35

`.gitignore` line 5 excludes `*.log`, so this section is where the debug builds
are recorded; the logs themselves do not survive the container.

### Why it was run

`w_bot` reads 0.0919 against a target of 0.025. The source carries a table
measured on 2 September (line 3251) where `w_bot` sat at 0.0247-0.0251 across
discount factors from 0.9998 to 1.015 -- on target, and close to orthogonal to
that instrument. A moment that was pinned and is now 3.7 times its old value
has the shape of the defect documented at line 20240, where an over-wide table
fill moved `w_bot` from 0.0295 to 3.27, homelessness from 0.084 to 0.011 and
drug use to exactly zero -- in that comment's own words, numbers that "look
like an economy".

### What it says: nothing is wrong with the build

`-O1 -fcheck=bounds,pointer`, exit 0, no out-of-bounds, no backtrace, and it
REPRODUCES the production run:

| | `-O3` production | `-O1 -fcheck=bounds,pointer` |
|---|---|---|
| `beta` | 3.49804 | 3.49718 |
| `w_bot` | 0.091926 | 0.091891 |
| `kappa_uem` | 0.821334 | 0.821362 |
| frozen loop | CONVERGED, 3 passes | CONVERGED, 3 passes |

So the numbers are not an optimisation artefact and not a memory error, and the
archive's parametric explanation for `w_bot` -- `newborn_endowment_scale`, which
takes the median from 0.0351 at zero to 0.0848 when positive across 2,286
recent points -- stands unchallenged.

### The first attempt was worthless, and that was a design fault

It deleted the binary immediately, to stop a later production run inheriting a
debug build. So when the time came to check that `-fcheck=bounds` had actually
been compiled in, there was nothing to inspect. **"No error from a build that
cannot be shown to have been checking" is not evidence.** The driver now
fingerprints the binary WHILE the run is in flight -- 1497 bounds-check strings,
against 0 in a production build -- and deletes it only at the end.
`run_variant.sh` now takes an `HFTF_OPT` override so this check is repeatable
rather than a one-off script.

### Still open

The run ends with `IEEE_INVALID_FLAG IEEE_DIVIDE_BY_ZERO are signalling`.
Invalid operations and divide-by-zero do occur somewhere. Masked NaNs in dead
branches are ordinary and this is not yet a finding, but it has not been
localised. The `-ffpe-trap=invalid,zero,overflow` build that would localise it
died mid-run and was relaunched.

**A strings fingerprint CANNOT verify the fpe build** -- `-ffpe-trap` embeds no
strings, it installs a handler. The check that works is `nm -D` for
`feenableexcept` / `set_fpe`, which returns 1 for that binary and is what the
rerun records.

## Flat supply and the three-year exclusion, 9 September 23:10

`.gitignore` excludes `*.log`, so this section is the record; the logs do not
survive the container.

### The change of specification

The author, 9 September: 1.46 is "way too low", the drug price "fluctuates way
too much", and with a participation elasticity of -2 to -3 that translates into
a lot of spurious addiction. Also: a failed test should carry a FUTURE
exclusion, geometric with a three-year mean, not the one-period removal the
model had.

`drug_supply_elasticity` is now a handover parameter, passed as 1e6. The
curvature becomes 1.000001, so `implied_price = shifter * q**1e-6 = shifter`,
the benchmark normalises the shifter to 1, and the price is pinned at 1 for any
quantity. Clearing is a step only when the curve slopes up; flat supply clears
by construction. Verified in the run: shifter normalised to 1.0000015, price
0.99999749, `distance_drug_market = 7.2e-9`, converged in THREE loops rather
than fifty.

### Rationed Treatment First, against the flat-supply benchmark

Benchmark: `b` 0.084902, `lambda_d` 0.035920, `h_1` 0.012529, `pi_V` 0.251825,
`beta` 3.497412. `FROZEN CONVERGED` in 3 passes.

| | flexible price, 1-year sanction | flat price, 3-year exclusion |
|---|---|---|
| `b` | 0.051527 (-39.3%) | **0.012160 (-85.7%)** |
| `lambda_d` | 0.019985 (-44.4%) | **0.003855 (-89.3%)** |
| `h_1` | 0.015185 (**+21.2%**) | **0.012513 (-0.1%)** |
| `pi_V` | 0.176946 (-29.7%) | 0.224890 (-10.7%) |
| welfare | -4.30% | **-2.14%** |
| drug price | 0.797 | 0.99999749 |
| loops | 46 | 3 |

### The price was doing two thirds of the work, and that is measured

At loop 11 of the flexible-price arm, with the price still at 0.975, `b` read
0.0123795. The flat-price arm converges at 0.0121604. So the deterrent at an
unchanged price was always about -86 per cent, and the falling price clawed back
two thirds of it. That is the author's hypothesis, confirmed against the log
rather than argued.

**Homelessness stops rising**, +21.2% becoming -0.1%, and the chain is visible
in the same table: use collapses, so almost nobody fails a test, so almost
nobody is sanctioned -- which is why coverage falls only 10.7 per cent here
against 29.7 per cent before. The deterrent works well enough that the
punishment rarely lands.

### What is NOT established

- **Flat supply and the exclusion moved together.** The loop-11 comparison
  suggests the price dominates and the exclusion adds little, but that is a
  comparison against an unconverged iterate, not a decomposition. One arm at
  flat supply with `include_voucher_exclusion=0` settles it, and is owed.
- **Three loops is few.** The budget finished at 1.35e-2 -- inside the 2.5e-2
  rule but ten times looser than the flexible-price arms reached -- so `tau_l`
  and the welfare number are the least reliable entries above.
- Eight benchmark moments are still outside the author's 10 per cent rule.

### The exclusion state, and the null that guarded it

A third voucher value, entered by failing a test, left with probability 1/3 a
year. Applies to holders and to applicants who are offered and then caught; a
false positive excludes too, since the programme cannot tell one from the other.

It is the sanction that bites, and the one-period removal was not: a homeless
household's voucher pays exactly ZERO -- `calculate_housing_voucher_2` caps the
payment by actual rent spending -- so confiscating this period's voucher from
the households the policy targets costs them nothing. Only a bar on future
offers destroys the option value, which is all they hold.

THE NULL EARNED ITS KEEP TWICE. First it caught `first_voucher_index` being set
to `voucher_state_max` in the holder branch: that index means "has a voucher",
not "top of the state space", so with the third slice present a holder
integrated its future only over the EXCLUDED state, whose probability is zero
with the flag off. `pi_V` fell from 0.2518 to 0.0245 and `b` from 0.0849 to
0.0253 -- and it compiled clean, converged in 3 frozen passes and passed the
bounds build, because nothing was out of bounds. A wrong number in a valid
index. Second, it established that this model is NOT bit-reproducible: the same
binary on the same vector differs by 3.8e-9 run to run, from OpenMP reduction
order, so no null can ever be exact and the working threshold is about 1e-8.

RESIDUAL, HONESTLY: with the flag off the three-state build agrees with the
two-state one to 1.0e-5, not to 3.8e-9. That is 600 times inside the frozen
tolerance and about a thousand times below the resolution at which arm effects
mean anything, but it is not explained. The signalling-NaN build would localise
it and cannot yet run: it dies on the pre-existing `X/mass` divisions, of which
59 are unguarded, three now fixed.
