# Does anyone actually borrow now?

**Yes. Borrowing is live.** The three arms are no longer identical, the
bottom-percentile wealth shares have gone negative, and they scale with the
limit. This is the opposite of the previous economy, where the choice loop was
floored at zero and the bottom 1 per cent's share sat at +1.19e-04 with the
limit at a full year of income.

The tell is the bottom 1 per cent. Turning borrowing on at limit 0.30 moves it
from **+1.19e-04 to -2.46e-03**, which lands essentially on the data's
-2.25e-03. Raising the limit to 1.00 moves it again, to **-1.11e-02**. Three
distinct values, monotone in the limit, sign flipped: households are taking on
debt, and the amount they take on responds to how much they are allowed.

The limit is first-order, not a rounding effect. Every reported share below
scales close to proportionally with it: bottom 1 per cent, bottom 5, bottom 10
and bottom 25 all move by a factor of roughly 4.5 between limit 0.30 and limit
1.00, and `w_bot` goes from -0.104 to -0.496.

## The three points

| | OFF | ON, limit 0.30 | ON, limit 1.00 |
|---|---|---|---|
| point | `3964495db2` | `b2f80f5abb` | `f0b286b09f` |
| `w_bot` (net worth share, bottom half) | +2.948610e-02 | -1.044832e-01 | -4.961747e-01 |
| `h_1` homelessness rate | +8.417780e-02 | +1.539814e-02 | +1.548391e-02 |
| wealth share of the bottom 25 pct | +2.967790e-03 | -6.138925e-02 | -2.774531e-01 |
| UNTARGETED wealth share bottom 1 pct | +1.187116e-04 | -2.455570e-03 | -1.109812e-02 |
| UNTARGETED wealth share bottom 5 pct | +5.935579e-04 | -1.227785e-02 | -5.549062e-02 |
| UNTARGETED wealth share bottom 10 pct | +1.187116e-03 | -2.455570e-02 | -1.109812e-01 |

Data counterparts for the three untargeted shares: -2.25e-03, -4.22e-03,
-4.46e-03. `w_bot`'s target is +2.50e-02; `h_1`'s is +3.99e-03.

## What the numbers say beyond the borrowing question

Three things in the table are worth the author's attention, and none of them is
the borrowing switch itself.

**`w_bot` now overshoots downward, badly.** Off, it is +0.0295 against a target
of +0.025 -- close. On at 0.30 it is -0.104, and at 1.00 it is -0.496. So the
limit that fixes the bottom 1 per cent destroys the bottom half. At limit 0.30
the bottom 1 per cent is nearly exactly on the data while `w_bot` is off by
0.129 in absolute terms. The two moments want different limits, which makes the
limit a poor single instrument for both.

**The bottom 5 and bottom 10 shares overshoot the data at every live limit.**
Even at 0.30, bottom 5 is -1.23e-02 against -4.22e-03 and bottom 10 is
-2.46e-02 against -4.46e-03 -- roughly three and five times too negative, while
bottom 1 is right. The model is putting too much debt on households between the
1st and 10th percentiles relative to the very bottom, so the shape of the debt
distribution is wrong even where its scale is right.

**Turning borrowing on cuts `h_1` by a factor of five,** from 8.42e-02 to
1.54e-02, and the limit barely matters after that (1.54e-02 at 0.30 against
1.55e-02 at 1.00). Borrowing is doing real work on homelessness -- a household
that can run down its balance does not have to give up housing -- but almost all
of that work is done by the first bit of access, not by how much. `h_1` remains
about four times its 3.99e-03 target in every arm.

## Provenance

All three points were measured on one economy, semantic hash `6d75e61a1d`, and
all three carry zero failed invariants.

Getting all three onto one economy took three rounds. The branch moved twice
under this batch, both times on the mechanism being measured:

- `a83c07b`, "Unsecured borrowing breaks the budget identity for renters: the
  debt is dropped". The first borrowing-ON measurement, taken before this, had
  two failed invariants -- the income and wealth histograms each summed to
  1.4949 instead of 1. That measurement was discarded.
- `9023afc`, "A renter's negative position is unsecured debt, not a mortgage:
  fix three sites".

Both are declared inert for a borrowing-OFF point in `model_hash.INERT_CHANGES`,
with the reasoning recorded there, so the OFF arm (`3964495db2`, stamped
`9575c59af0`) carries forward legitimately and did not need re-solving. Both
notes are explicit that a borrowing-ON point may never pool across them, so both
ON arms were re-solved on `9d410dfdb9`. `resolve_for_point` confirms all three
resolve to `6d75e61a1d`.

One caveat on the OFF arm's label. `unsecured_borrowing_limit=0.30` is present in
its vector but inert, since `include_unsecured_borrowing=0`. Its comparability
with the 0.30 ON arm rests on the two inert-change proofs above, not on a
re-solve.

## One thing to check before reading the ladder as a calibration result

The vector gained `restrict_borrowing_to_impatient=1` as a default when the
branch moved, so in all three arms only the impatient type can reach the
negative grid. The ladder above is therefore the ladder *conditional on that
restriction*, and the share of debt it can generate is bounded by the impatient
type's population share. If the bottom 5 and bottom 10 overshoot noted above is
to be diagnosed, this flag is the first place to look: concentrating all
borrowing in one beta type is a candidate explanation for debt being too
concentrated just above the very bottom.
