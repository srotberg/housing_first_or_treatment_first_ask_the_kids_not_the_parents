# Round 1, arms A, unsecured borrowing OFF

Three points from `code/batch_r1a_off.txt`, each moving ONE round-1 instrument
off the anchor and leaving every other coordinate at the anchor's value.
`include_unsecured_borrowing=0` in all four vectors.

## The economy these were measured on

All four points below carry the SAME `MODEL` line:

    MODEL c823331449

so the four are comparable with each other.

They are NOT the repository head. The Fortran moved to `b8dc1077ad` in the
commits this branch picked up during the rebase that followed the third run, so
every number here describes the `c823331449` economy and nothing on the current
source should be compared against it without re-measuring.

The anchor is included because a point for it exists on `c823331449`:
`point_f9c16d5308.txt`, which arrived in commit 4781133 as the OFF anchor
re-measured on this same source. Its vector was checked coordinate by
coordinate against the batch's common base and is identical on all 42.

| role   | point file                | instrument moved                        | value    |
|--------|---------------------------|-----------------------------------------|----------|
| anchor | `point_f9c16d5308.txt`    | --                                      | --       |
| arm 1  | `point_690ae9b00a.txt`    | `probability_of_voucher_benchmark_used` | 0.038800 |
| arm 2  | `point_ca25f19a3f.txt`    | `max_food_cost`                         | 0.0196   |
| arm 3  | `point_81f7071729.txt`    | `value_of_life`                         | 54.5     |

All three solved cleanly, 11-12 minutes each, `HANDOVER OK: 42 of 42
parameters applied` and `INVARIANTS: all PASS` on every one.

## Arm 1 -- pi_V, owned by `probability_of_voucher_benchmark_used`

| instrument | 0.024723 (anchor) | 0.038800 (arm) | target |
|------------|-------------------|----------------|--------|
| pi_V       | 0.179364          | 0.240579       | 0.266  |

**Falls short.** The pair does not bracket: both measured values are below the
target. Raising the instrument moves pi_V toward the target, and at the arm
measured -- 0.038800 -- pi_V is still 0.025421 below it. That is the gap at
0.038800; it is not a statement about any instrument value past 0.038800.

## Arm 2 -- cbar, owned by `max_food_cost`

| instrument | 0.0136 (anchor) | 0.0196 (arm) | target |
|------------|-----------------|--------------|--------|
| cbar       | 0.008601        | 0.013520     | 0.0042 |

**Falls short, and in the direction that matters: the arm was taken the wrong
way.** The pair does not bracket. Both measured values are ABOVE the target,
and raising `max_food_cost` from 0.0136 to 0.0196 moved cbar further from it,
from 0.004401 above the target to 0.009320 above. At the arm measured --
0.0196 -- cbar overshoots by 0.009320. The target sits below both points, so
bracketing it requires an instrument value below the anchor's 0.0136, not
above it. No such point was measured here.

## Arm 3 -- aleph, owned by `value_of_life`

| instrument | 38.4 (anchor) | 54.5 (arm) | target |
|------------|---------------|------------|--------|
| aleph      | 50.667083     | 81.268076  | 80.0   |

**Brackets.** 50.667083 < 80.0 < 81.268076. The target is enclosed by the
measured pair. At the arm measured -- 54.5 -- aleph overshoots the target by
1.268076; at the anchor it falls 29.332917 short.

## A caution about reading these as three independent moves

The arms are not orthogonal in their non-owned moments. aleph, which arm 3
owns, also moved under the other two instruments on the same economy: 50.667083
at the anchor, 51.048676 under arm 1's voucher probability and 52.648394 under
arm 2's food cost, neither of which is supposed to own it. Whatever is done
next with one instrument should not assume the other two moments stay where
this table leaves them.
