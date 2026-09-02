# Round 1 arms A: three single-instrument arms, two measured, one lost to a segfault

`code/batch_r1a.txt`, run line by line. Each line moves ONE round-1 instrument
off the anchor and leaves the other thirty-nine alone.

**Read the model hashes before reading the numbers.** The three lines did NOT
run on one economy. The push of line 1 was rejected, the rebase that unblocked
it pulled `358057d` ("the EV fill range broke the economy; both floors now key
on the ARRIVING age") into the tree, and lines 2 and 3 therefore built a
different source than line 1:

| line | arm | tag | MODEL | outcome |
|---|---|---|---|---|
| 1 | `probability_of_voucher_benchmark_used` 0.024723 -> 0.038800 | `f0635d6f87` | `e55e1cc855` | solved, 13 min |
| 2 | `max_food_cost` 0.0136 -> 0.0196 | `f62a932c11` | `d2563e97f3` | **SIGSEGV, 0 min, no moments** |
| 3 | `value_of_life` 38.4 -> 54.5 | `9c386ccf18` | `d2563e97f3` | solved, 13 min |

So there is no three-arm comparison here and there cannot be one from these
runs. Line 1 is on the pre-`358057d` source; line 3 is on the post-`358057d`
source; line 2 has no measurement at all.

## The anchor exists for arm 1 only

The anchor is the same vector with `probability_of_voucher_benchmark_used=0.024723`,
`max_food_cost=0.0136`, `value_of_life=38.4`.

- On `e55e1cc855` (line 1's own model) `point_4659380b40.txt` matches the anchor
  vector **exactly**, all forty-two parameters. Arm 1 is a matched pair.
- On `d2563e97f3` (line 3's own model) there is **no anchor point**. The nearest,
  `point_f9c16d5308.txt`, differs in `include_unsecured_borrowing` (0 against the
  anchor's 1), which is a different economy, not a different point in this one.
  Arm 3 is therefore reported as a single point, not compared to anything.

The other four same-hash candidates each differ in one parameter and are not the
anchor: `31e7181863` and `65c5d119a5` in `discount_factor_impatient` (0.90, 0.50),
`8967680c10` in `discount_factor` (0.99800), `f4a40be627` in
`unsecured_borrowing_limit` (0.60).

## Arm 1 -- pi_V, owned by `probability_of_voucher_benchmark_used`

Model `e55e1cc855`. Anchor `4659380b40`, arm `f0635d6f87`.

| `probability_of_voucher_benchmark_used` | pi_V, eligibles with a voucher |
|---|---|
| 0.024723 (anchor) | 0.012290 |
| 0.038800 (arm) | 0.017682 |
| target | 0.266 |

**The pair does not bracket the target; both fall short of it, badly.** At the arm
I measured, 0.038800, pi_V reads 0.017682 against a target of 0.266 -- short by
0.248318, and 6.6 per cent of the target. Moving the instrument by 0.014077
moved the moment by 0.005392. I am not projecting where the target would be hit;
the pair that produced this covers 0.024723 to 0.038800 and nothing beyond it.

## Arm 2 -- cbar, owned by `max_food_cost`: NOT MEASURED

`max_food_cost=0.0196` died with exit status 139 (SIGSEGV) after 0 min on the
post-`358057d` source. Recorded in `point_f62a932c11.txt`, which carries the full
backtrace. Not patched, per the batch instructions.

The crash is inside the routine `358057d` rewrote:

    #3  fill_ev_table_      housing_first_or_treatment_first_SR_v1.f90:18414
    #4  ensure_ev_table_    ...:18258
    #5  renter_to_renter_problem_  ...:18868

**It is that vector's crash, not the source's.** Line 3 ran the same source
`d2563e97f3` with borrowing on and solved in 13 min, so `d2563e97f3` is not
broken for every vector. What separates the two lines is `max_food_cost`,
0.0196 against 0.0136. `358057d`'s own check was a borrowing-OFF control; every
line of this batch has `include_unsecured_borrowing=1`.

No pair for cbar, so no bracketing statement is available for it. Target 0.0042.

## Arm 3 -- aleph, owned by `value_of_life`

Model `d2563e97f3`. Arm `9c386ccf18`. **No anchor on this hash**, so this is one
point, reported alone.

| `value_of_life` | aleph, value of life / income |
|---|---|
| 54.5 (arm) | 4.05e+216 |
| target | 80.0 |

There is no pair, so the question of bracketing does not arise. The single
reading is not short of 80 -- it is 214 orders of magnitude above it, which is
not a measurement of aleph but a symptom of the next section.

## Both solved points are degenerate, and that qualifies every number above

Neither surviving point is a healthy solve. Both fail the same two invariants
and both have aggregates that have blown up:

| | anchor `4659380b40` | line 1 `f0635d6f87` | line 3 `9c386ccf18` | target |
|---|---|---|---|---|
| `tau_l` average labour income tax | NaN | NaN | NaN | 0.224 |
| `beta` wealth over output | 7.70e+12 | 7.73e+12 | 3.41e+12 | 3.0 |
| `aleph` value of life / income | 6.11e+219 | 6.72e+219 | 4.05e+216 | 80.0 |
| `cbar` food stamps / income | 2.99e+08 | 2.99e+08 | 6.30e+08 | 0.0042 |
| invariants failed | 2 | 2 | 2 | 0 |

Both failures are the same pair at all three points -- "income histogram holds
the whole distribution" and "wealth histogram holds the whole distribution",
each reading about 1.495 where 1.0 is wanted.

pi_V is the one moment above that comes back on a plausible scale, which is why
arm 1 gets a bracketing verdict at all. But it is measured in an economy whose
output, wealth and value of life have all diverged, and the anchor it is
differenced against is degenerate in exactly the same way. Treat the arm-1
verdict as a statement about two degenerate solves that share a defect, not as a
clean elasticity of pi_V with respect to its instrument.

`cbar` at 3e+08 and `aleph` at 1e+216 against targets of 0.0042 and 80.0 are not
near-misses to be closed by moving an instrument. Their scale says the
denominator (output) has diverged, so neither of those two moments is being
measured at any of these points, the anchor included.

## What would have to happen before these arms mean anything

1. The divergence behind `beta` = 3e+12, `tau_l` = NaN and the two histogram
   invariants has to be found. Until then no arm on this vector measures its
   moment.
2. `max_food_cost=0.0196` has to stop segfaulting in `fill_ev_table`, or the
   cbar arm cannot be taken at all.
3. The three lines have to be re-run on ONE source. As it stands the batch
   straddles `358057d` the way `batch_s2_01` straddled the borrowing fix.
