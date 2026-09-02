# beta above one: three arms at discount_factor > 1

Three points off `point_35e8286c4e`, moving `discount_factor` and nothing else.

    discount_factor  0.99980 -> 1.00200   point eca09faa90
                             -> 1.00500   point b8d36c0646
                             -> 1.01500   point 1ffd652557

## Headline

**The instrument was never exhausted.** `beta` was reported as unreachable
because closing the gap "wants a discount factor above one". A discount factor
above one is admissible in this model: the value function is backward induction
over a finite life span (`do age_index=life_span,1,-1`, line 15935), so the
discounted sum is finite for any `discount_factor`, and the handover has always
clamped to **[0.5, 1.05]**:

    discount_factor=min(max(handover_value,0.5d0),1.05d0)     line 35295

All three arms cleared that clamp untouched. `beta` moves from 2.4528 at the
base to **4.3665** at 1.01500 -- it crosses 2.5, crosses 3.0, and by the top arm
is most of the way to the band's upper edge of 4.5. The highest value ever tried
before tonight was 0.99995.

## The three runs are sound

|                          | eca09faa90 | b8d36c0646 | 1ffd652557 |
|--------------------------|-----------:|-----------:|-----------:|
| `discount_factor`        |    1.00200 |    1.00500 |    1.01500 |
| solve time               |     14 min |     14 min |     14 min |
| `HANDOVER`               |   42 of 42 |   42 of 42 |   42 of 42 |
| `MODEL`                  | bb2cd48b81 | bb2cd48b81 | bb2cd48b81 |
| INVARIANTS               |   all PASS |   all PASS |   all PASS |

**The three `MODEL` lines agree**: all three are `bb2cd48b81`.

Neither watched failure mode fired:

- **`beta IS PINNED AT A BOUND` did not appear** in any of the three runs. It
  should not have, and it did not: 1.01500 is well inside the 1.05 ceiling.
- **Nothing non-finite.** No `NaN`, no `Infinity`, no `Inf`, no `****` field
  overflow in any of the three outputs, and every invariant block reports
  `INVARIANTS: all PASS`. The concern that a discount factor above one would
  amplify later-life utility into a divergent solve is not borne out at these
  values.

## The ladder

`beta` at each `discount_factor`, all else equal.

| `discount_factor` | `beta` | point | MODEL | economy |
|------------------:|-------:|-------|-------|---------|
| 0.99950 | 2.4133 | 932e3cd75a | b8dc1077ad | old |
| 0.99980 | 2.4528 | 35e8286c4e | b8dc1077ad | old |
| 0.99995 | 2.4695 | 44e91bb1d7 | b8dc1077ad | old |
| 1.00200 | **2.7287** | eca09faa90 | bb2cd48b81 | measured here |
| 1.00500 | **3.1277** | b8d36c0646 | bb2cd48b81 | measured here |
| 1.01500 | **4.3665** | 1ffd652557 | bb2cd48b81 | measured here |

**The first three rows are on a different `MODEL` line and are labelled as
such.** They carry `b8dc1077ad`; the three measured here carry `bb2cd48b81`.
The two halves are NOT fitted together and no slope is taken across the
boundary. Their vectors were checked and are identical to `point_35e8286c4e`
except in `discount_factor`, so within each half the comparison is clean.

The gap between the hashes is commit `5ea693e`, which moved
`wealth_to_output_data` from 3.0 to 2.5. That commit argues the constant reaches
the solver only through a calibration block the handover disables, so the
economy "should be untouched" and only the printed target should move --
but it also says plainly that this is not assumed, and that
`batch_target_check.txt` exists to settle it. **That check has not been run.**
No point on `bb2cd48b81` shares a vector with any archive point, so the
equivalence is still open, there is no `EQUIVALENT_MODELS` record, and the two
hashes carry different semantic hashes (`2f7c317e75` against `08f8470b5d`).
Until the target check runs, the old rows are context, not data on this economy.

## What brackets what

Only same-economy pairs can bracket. On `bb2cd48b81`:

- **2.5 is NOT bracketed by any measured pair.** The lowest arm measured,
  1.00200, already returns 2.7287 -- it is **past** the target, by +9.1 per
  cent. The crossing lies somewhere below 1.00200 and was not measured.
- **3.0 IS bracketed, by 1.00200 and 1.00500** (2.7287 below, 3.1277 above).

On the old economy `b8dc1077ad`, all three archive rows sit below 2.5 and
neither figure is bracketed there.

No extrapolation past the measured arms is offered. In particular, nothing here
locates the `discount_factor` that returns exactly 2.5 or exactly 3.0; it says
only which measured pair straddles 3.0 and that the smallest step above one
already overshoots 2.5.

**The old 3.0 figure was reachable all along.** That is the substantive answer
to what these arms were for: 3.0 sits between two arms that both solve cleanly,
inside the clamp, with every invariant passing.

## The nine round-1 moments

| moment | target | 0.99950 (old) | 0.99980 (old) | 0.99995 (old) | 1.00200 | 1.00500 | 1.01500 |
|--------|-------:|---:|---:|---:|---:|---:|---:|
| `aleph`   | 80.0        | 75.5229 | 75.8280 | 76.3429 | 78.6669 | 81.6898 | **95.0551** |
| `beta`    | BAND 2.5-4.5| 2.4133 | 2.4528 | 2.4695 | 2.7287 | 3.1277 | 4.3665 |
| `omega_l` | 0.40        | 0.3634 | 0.3635 | 0.3636 | 0.3646 | 0.3660 | 0.3709 |
| `sigma_y` | 0.172       | 0.1691 | 0.1691 | 0.1691 | 0.1691 | 0.1691 | 0.1691 |
| `tau_l`   | 0.224       | 0.2266 | 0.2263 | 0.2257 | 0.2242 | 0.2219 | 0.2152 |
| `pi_eu`   | 0.139       | 0.1343 | 0.1343 | 0.1343 | 0.1343 | 0.1343 | 0.1343 |
| `pi_V`    | 0.266       | 0.2557 | 0.2560 | 0.2556 | 0.2553 | 0.2476 | 0.2474 |
| `cbar`    | 0.0042      | 0.0039 | 0.0039 | 0.0039 | 0.0039 | 0.0038 | **0.0036** |
| `w_bot`   | 0.0250      | 0.0239 | 0.0243 | 0.0248 | 0.0250 | 0.0251 | 0.0250 |

Per cent gaps. `beta` follows the repository's own `gap()` in `gaps.py`: a
banded moment scores zero anywhere inside 2.5-4.5 and otherwise the distance to
the nearer edge, so 0.0 below means in band, not on target.

| moment | 0.99950 | 0.99980 | 0.99995 | 1.00200 | 1.00500 | 1.01500 |
|--------|--------:|--------:|--------:|--------:|--------:|--------:|
| `aleph`   |  -5.6 |  -5.2 |  -4.6 |  -1.7 |  +2.1 | **+18.8** |
| `beta`    |  -3.5 |  -1.9 |  -1.2 |   0.0 |   0.0 |   0.0 |
| `omega_l` |  -9.2 |  -9.1 |  -9.1 |  -8.9 |  -8.5 |  -7.3 |
| `sigma_y` |  -1.7 |  -1.7 |  -1.7 |  -1.7 |  -1.7 |  -1.7 |
| `tau_l`   |  +1.1 |  +1.0 |  +0.8 |  +0.1 |  -0.9 |  -3.9 |
| `pi_eu`   |  -3.4 |  -3.4 |  -3.4 |  -3.4 |  -3.4 |  -3.4 |
| `pi_V`    |  -3.9 |  -3.8 |  -3.9 |  -4.0 |  -6.9 |  -7.0 |
| `cbar`    |  -6.1 |  -6.3 |  -6.4 |  -7.2 |  -8.4 | **-13.1** |
| `w_bot`   |  -4.3 |  -2.9 |  -0.9 |  +0.2 |  +0.2 |  -0.2 |
| **inside ten per cent** | **9/9** | **9/9** | **9/9** | **9/9** | **9/9** | **7/9** |

### w_bot did not break

`w_bot` was the moment flagged as most likely to break, on the reasoning that a
more patient population saves more. **It did not break. It improved, and then
held.** It runs -4.3 per cent at 0.99950, -2.9 at the base, -0.9 at 0.99995,
and then sits essentially exactly on its 0.0250 target across all three arms
above one: +0.2, +0.2, -0.2 per cent. It is the single best-matched of the nine
at every arm measured here.

The reasoning was right about the direction and wrong about the consequence.
More patience does raise saving, but `w_bot` is a *share* -- net worth of the
bottom half over total net worth -- and the extra saving accrues across the
distribution, so the ratio barely moves while `beta`, a level ratio, rises 78
per cent from base to top arm.

### What breaks instead is aleph

The binding cost of pushing `discount_factor` this far is `aleph`, not `w_bot`.
`aleph` is monotone in `discount_factor` across every row and goes out of range
between 1.00500 (+2.1 per cent) and 1.01500 (**+18.8 per cent**). `cbar` follows
it out at the top arm (-13.1 per cent). Both are inside ten per cent at 1.00200
and 1.00500 and only fail at 1.01500.

That makes **1.00200 and 1.00500 both nine of nine**, and 1.01500 seven of nine.

### The best of the arms

`1.00200` (`point_eca09faa90`) is nine of nine with the largest margin: its
worst moment is `omega_l` at -8.9 per cent, and `omega_l` is the long-standing
near-miss that is roughly -9 per cent at every row in the table, above and below
one alike -- it does not respond to `discount_factor` and is not this
parameter's to fix. Setting `omega_l` aside, every other moment at 1.00200 is
inside 7.2 per cent, and four of the nine are inside 2.

`1.00500` is also nine of nine and is the arm that puts `beta` nearest the old
3.0 figure (3.1277, +4.3 per cent against 3.0), at the cost of `aleph` crossing
from below to above its target and `cbar` and `pi_V` drifting further out.

## Caveats

- Three arms, one parameter, no search. Nothing here says the vector at
  1.00200 or 1.00500 is a better calibration overall -- only that it is nine of
  nine on the round-1 moments, as the base is.
- The old-economy rows are not comparable point-for-point until
  `batch_target_check.txt` is run and the hashes are either declared equivalent
  or the archive resets.
- `omega_l` is short at every arm and is untouched by this instrument.
