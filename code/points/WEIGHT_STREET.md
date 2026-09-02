# THE HOUSING WEIGHT AND THE SIZE OF THE STREET -- can `emp_homeless` and `h_1` be had at once?

Three points, run in sequence in one container on one binary, no rebase between
them. Each sets a PAIR: `relative_share_of_housing` and `size_homelessness`
together. Borrowing is off throughout (`include_unsecured_borrowing=0`).

The question comes out of the previous batch (`HOUSING_WEIGHT.md`). The weight
on housing is the first instrument found that moves `emp_homeless`, which sits
at 0.96 against a target of 0.46 -- but it moves it by **emptying the street**:
`h_1` fell 0.0828 -> 0.000522 -> exactly zero across weights 0.100, 0.200,
0.300, and at 0.300 there was no homeless population left to take a share of.

`size_homelessness` is the street's size relative to the cheapest unit. Raising
it makes the street less bad, so it should put people back on it. These three
pairs ask whether raising the two together can bring `emp_homeless` down while
leaving a street of roughly the right size behind.

## All three points are on the same model, and on the anchor's model

    point_f9c16d5308.r2a_anchor   MODEL b8dc1077ad   ANCHOR  (0.100, 0.149)
    point_f88fc8a75f              MODEL b8dc1077ad   line 1  (0.250, 0.300)
    point_496b9eee4f              MODEL b8dc1077ad   line 2  (0.250, 0.500)
    point_9bca6249e1              MODEL b8dc1077ad   line 3  (0.300, 0.500)

**The three MODEL lines agree**, at `b8dc1077ad`, and they agree with the
anchor's. This was confirmed before any number below was compared, so the
differences reported here are differences in the instruments and not differences
in the Fortran. `HANDOVER OK: 42 of 42 parameters applied` on all three.
`INVARIANTS: all PASS` on all three -- no point in this batch produced a NaN or
a failed invariant.

Each `VECTOR` line was diffed against the anchor's, coordinate by coordinate.
Each of the three differs from the anchor in **exactly two** coordinates, the
two named. The batch is also internally clean as two matched pairs:

    line 1 vs line 2   differ in exactly  size_homelessness        (0.300 -> 0.500)
    line 2 vs line 3   differ in exactly  relative_share_of_housing (0.250 -> 0.300)

### A correction on which anchor is the matched one

The batch brief quotes the anchor as `emp_homeless` 0.96557, `h_1` 0.06677.
Those are `point_9724dc31eb`, and that point is **not** a matched pair with this
batch: its vector differs from these three lines in **three** coordinates, not
two, because it carries `probability_of_voucher_benchmark_used=0.048000` against
these lines' `0.024723`. The matched anchor is `point_f9c16d5308`, which differs
in exactly the two instrument coordinates and is what every difference below is
taken against.

The two anchors are not interchangeable on the moment this note is about:

    (0.100, 0.149)  voucher 0.048000  point_9724dc31eb   emp_homeless 0.965569  h_1 0.0667653
    (0.100, 0.149)  voucher 0.024723  point_f9c16d5308   emp_homeless 0.964216  h_1 0.0828210

`emp_homeless` barely moves between them, but `h_1` differs by a quarter of its
own value, so quoting one anchor's `h_1` against the other's arms would misstate
the size of every fall reported here.

The anchor vector was also run four times (the determinism study, `RUN1`-`RUN3`
plus the plain tag). Within a container those runs agree to 3e-08 on
`emp_homeless`; across containers the anchor reads 0.964216 against 0.964191, so
**2.5e-05 is the cross-container noise floor** on that quantity, and 1.6 per
cent relative is the floor on `h_1`. Every movement below is orders of magnitude
larger.

## The three pairs

| | anchor | line 1 | line 2 | line 3 |
|---|---|---|---|---|
| `relative_share_of_housing` | 0.100 | **0.250** | **0.250** | **0.300** |
| `size_homelessness` | 0.149 | **0.300** | **0.500** | **0.500** |
| `emp_homeless` (target 0.46) | 0.964216 | **0.586962** ‡ | 0.939750 | **0.859989** ‡ |
| homeless by choice | 0.980735 | 1.000000 ‡ | 0.999982 | 1.000000 ‡ |
| homeless who could afford it on INCOME ALONE | 0.979523 | 1.000000 ‡ | 0.999982 | 1.000000 ‡ |
| `h_1` (target 0.00399) | 0.0828210 | **0.00132216** | 0.0436027 | **0.0135004** |
| `gamma` (target 0.268) | 0.137692 | 0.185431 | 0.178503 | 0.189302 |
| `w_bot` (target 0.0250) | 0.030199 | 0.022880 | 0.023602 | 0.020994 |
| working-age homeless mass (of ~88 pooled) | 5.2121 | **0.11625** | 2.8210 | 0.67067 |
| invariants | all PASS | all PASS | all PASS | all PASS |

## The empty-street check, row by row

The previous batch produced a spurious `emp_homeless` of 1.0000 from a street
with exactly zero mass on it. Every row above was checked for that corner before
being reported. **No row in this batch is that corner** -- all three have a
strictly positive homeless population, all three pass every invariant, and on all
three the homelessness rate rebuilt from the five age bands reproduces `h_1` to
within 1e-13. But two of the three rows are thin, and one of them is thin enough
that its share figures should be read with care.

‡ **Line 1 (0.250, 0.300) is the thin one.** Its `h_1` of 0.00132216 is real and
well above the resolution floor -- it is a third of the target, not a rounding of
zero -- but the mass under it is **0.11625 units against the anchor's 5.2121, a
factor of 44.8 smaller**. `emp_homeless` of 0.586962 is a ratio over that 0.116.
It is a measurement and it is used below, but the population it describes is not
the population the target describes: `homeless by choice` and `could afford it
on INCOME ALONE` are both **exactly 1.000000**. Every involuntary homeless
household is gone. What 0.586962 measures is the employed share of a purely
voluntary residual, so it should not be read as the moment in the data having
moved most of the way to target.

‡ **Line 3 (0.300, 0.500) carries the same caveat, less severely.** `h_1` is
0.0135004 on 0.67067 units of mass, and by-choice and could-afford are again
**exactly 1.000000**. The involuntary margin is gone here too.

**Line 2 (0.250, 0.500) is the one row with a street of ordinary size**: `h_1`
0.0436027 on 2.8210 units, and by-choice 0.999982 rather than exactly one. Its
`emp_homeless` of 0.939750 is the least qualified reading in the table -- and it
is essentially at the anchor's 0.964216.

So the pattern to keep in view: **on these three points the involuntary homeless
are gone wherever `emp_homeless` has moved at all.** Both rows that moved it show
by-choice at exactly 1.

## The answer: no. Nothing runs `emp_homeless` toward 0.46 with `h_1` intact

The factor-of-two band around the `h_1` target of 0.00399 is [0.001995,
0.007980]. **No pair in this batch lands inside it.**

    line 1  h_1 0.00132216   3.02x BELOW target    outside the band
    line 2  h_1 0.0436027   10.93x ABOVE target    outside the band
    line 3  h_1 0.0135004    3.38x ABOVE target    outside the band

And the row that comes closest to the `emp_homeless` target is the row that
misses `h_1` low, on a street that has lost its involuntary population entirely:

    emp_homeless closest to 0.46:  line 1, 0.586962, still 0.127 above target
                                   and h_1 three times BELOW its own target

**The target `h_1` of 0.00399 is bracketed by this batch** -- it lies between
line 1's 0.00132216 and line 3's 0.0135004, and equally between line 1's and
line 2's. That is a usable finding for `h_1` in its own right. But the two pairs
that bracket it read `emp_homeless` 0.586962 and 0.859989, and both are above
0.46. **No value is projected onto the bracket**: nothing here is interpolated,
and the batch does not contain a point where `h_1` is on target.

`w_bot` is also bracketed: the anchor's 0.030199 is above the target of 0.0250
and all three lines are below it (0.022880, 0.023602, 0.020994).

`gamma` is not bracketed. All four points are below the target of 0.268; the
best is line 3's 0.189302, which closes 39.6 per cent of the anchor's gap.

## The trade-off that was actually measured

The two instruments do not act on the two moments independently. Each was moved
alone in a matched pair, and each moves `emp_homeless` and `h_1` in the SAME
direction as the other -- so raising one to undo the other's damage undoes its
help as well.

**The street, at a fixed weight of 0.250** (line 1 -> line 2, the only coordinate
that changes is `size_homelessness`, 0.300 -> 0.500):

    h_1           0.00132216  ->  0.0436027     x 32.98
    emp_homeless    0.586962  ->    0.939750     +0.352788

The hypothesis in the brief is confirmed on the first line and refuted on the
second. A bigger street does put people back on it -- by a factor of 33 -- but
**the people it puts back are employed**, and `emp_homeless` goes back up by
0.353. Measured against the anchor, line 1 closes 74.8 per cent of the gap to
0.46 and line 2 closes 4.9 per cent, so widening the street gives back **93.5 per
cent** of the distance line 1 had covered.

**The weight, at a fixed street of 0.500** (line 2 -> line 3, the only coordinate
that changes is `relative_share_of_housing`, 0.250 -> 0.300):

    h_1           0.0436027  ->  0.0135004     / 3.23
    emp_homeless   0.939750  ->   0.859989     -0.079761

The weight behaves here exactly as it did in the previous batch: it brings
`emp_homeless` down and it empties the street while doing it. A larger street
does not change that character, it only moves where the emptying starts from.

**The four points lie on one increasing relation between the two moments**,
whichever instrument was the one that moved:

    h_1  0.00132216   emp_homeless  0.586962     line 1   (weight 0.250, street 0.300)
    h_1  0.0135004    emp_homeless  0.859989     line 3   (weight 0.300, street 0.500)
    h_1  0.0436027    emp_homeless  0.939750     line 2   (weight 0.250, street 0.500)
    h_1  0.0828210    emp_homeless  0.964216     anchor   (weight 0.100, street 0.149)

Sorted by `h_1`, `emp_homeless` is strictly increasing, and the ordering does not
respect which coordinate was changed: line 3 sits between line 1 and line 2
though it shares its street with line 2 and neither its weight nor its street
with line 1. This is an observation about four measured points, not a fitted
curve, and nothing is read off between them. What it says is that on the region
these three pairs cover, **`emp_homeless` comes down only as far as the street
empties, and pairing the two instruments did not break that link.**

## Summary

1. **No pair delivers both moments.** None of the three lands `h_1` within a
   factor of two of 0.00399, and the pair that gets `emp_homeless` closest --
   line 1, at 0.586962, still 0.127 above target -- misses `h_1` three times low
   on a street 44.8 times smaller than the anchor's.
2. **The empty-street corner did not recur.** All three points have positive
   homeless mass, pass every invariant, and rebuild `h_1` from the age bands.
   But lines 1 and 3 have `homeless by choice` and `could afford it on INCOME
   ALONE` at **exactly 1.000000**: the involuntary margin is gone on both rows
   that moved `emp_homeless`, and their employed shares are shares of a
   voluntary residual.
3. **A bigger street refills with the employed.** At weight 0.250, taking the
   street 0.300 -> 0.500 multiplied `h_1` by 33 and pushed `emp_homeless` back
   up 0.353. `size_homelessness` is a working instrument on `h_1` and works
   against the target on `emp_homeless`.
4. **The weight keeps its character at a larger street.** At street 0.500,
   taking the weight 0.250 -> 0.300 cut `h_1` by 3.23 and `emp_homeless` by
   0.080. Pairing did not separate the two effects.
5. **`h_1` is bracketed by this batch** (0.00399 lies between 0.00132216 and
   0.0135004) and so is **`w_bot`** (0.0250 lies between the anchor's 0.030199
   and line 1's 0.022880). **`gamma` is not** -- all four points are below 0.268.
6. **Nothing is extrapolated past the three pairs run.** The batch contains no
   point with `h_1` on target, and no instrument value is projected here.
