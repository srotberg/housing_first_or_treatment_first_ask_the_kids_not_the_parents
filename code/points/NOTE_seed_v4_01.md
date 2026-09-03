# batch_s2_01: the borrowing ladder, measured twice across an engine fix

## Summary

The batch is a borrowing limit-and-rate ladder. It was first run against a
model in which borrowing did nothing, and the source moved three times under
it. All three lines have since been re-measured on the repaired model. **On the
repaired model the borrowing limit is a first-order instrument on `w_bot`, and
every arm in this ladder overshoots the target by a wide margin in the negative
direction.**

## The ladder, re-measured (MODEL `9575c59af0`, all invariants PASS)

| line | limit | rate | beta_imp | point | `w_bot` | `beta` = W/Y |
|---|---|---|---|---|---|---|
| 1 | 1.00 | 0.055 | 0.55 | `point_f0b286b09f` | **-0.4871** | 2.2502 |
| 2 | 0.30 | 0.20  | 0.55 | `point_b853a25c24` | **-0.1023** | 2.5904 |
| 3 | 0.30 | 0.055 | 0.50 | `point_2035bf44dc` | **-0.1044** | 2.5832 |

Targets: `w_bot` = +0.0250, `beta` = 3.0000.

### The limit is the instrument; the rate is not

Lines 1 and 2 differ in the limit (and in the rate, which the next paragraph
shows is nearly inert). Taking the limit from 0.30 to 1.00 moves `w_bot` from
-0.102 to -0.487 -- a factor of 4.8 -- and drags W/Y from 2.59 down to 2.25.

Lines 2 and 3 differ in the rate (0.20 vs 0.055) **and** in `beta_imp` (0.55 vs
0.50) together, and between them `w_bot` moves 0.0022 and W/Y moves 0.0072.
Set against the solver noise floor measured below (about 1e-4 on shares, about
2e-3 on W/Y), the `w_bot` move is real but two orders of magnitude smaller than
the limit's, and the W/Y move sits at the noise floor and is not resolvable by
a single solve. **The rate and the impatient discount factor, jointly, are not
competitive instruments against the limit on this moment.**

### Direction for the search

All three arms sit far below the +0.025 target and the ladder brackets it from
one side only, so the crossing is outside the measured range. Both moments push
the same way -- a smaller limit raises `w_bot` toward the target *and* raises
W/Y toward 3.0 -- so there is no trade-off to price here. The next ladder should
run limits well below 0.30, and should expect the crossing near zero: at the
old inert model, which is a genuine no-borrowing economy, `w_bot` read +0.0296
against the +0.0250 target.

## What the first pass measured, and why it was discarded

| when | semantic | commit | effect on this batch |
|---|---|---|---|
| lines 1, 2 | `fdc6078859` | — | borrowing inert; limit and rate meant nothing |
| line 3 | `99752a3cab` | `307aa35` | borrowing live, mass diverged to 2.06e33 |
| re-runs | `f9048e2563` | `358057d`, `0f581bb`, +200 | repaired; all invariants pass |

`307aa35` found that `renter_to_renter_problem` pinned its search floor `a_lo_1`
at the index of zero, so no renter could ever choose a negative position: the
limit and the rate multiplied a choice no household could make. It invalidates
"every borrowing arm measured so far -- the OFF/ON twin above, and the limit and
rate ladders". This batch is such a ladder.

The size of that error is now measurable. At the identical named coordinates
(limit 0.30, rate 0.20, `beta_imp` 0.55), `w_bot` reads +0.0296 inert and
-0.1023 repaired: a swing of 0.132 in a moment whose target is 0.025. **A
feature that appeared to do nothing was, once it worked, large enough to
dominate the moment it was introduced to move.**

### The divergence on line 3, reproduced then cleared

With borrowing live but before the bounds fix, line 3 failed two invariants and
the population mass blew up. Another worker measured the identical vector
independently and got the same numbers:

```
                                              theirs            mine
pooled mass                              2.0588727e+33    2.0587580e+33
income histogram holds the distribution     1.4949252        1.4949061
wealth histogram holds the distribution     1.4949252        1.4949061
```

Deterministic to four significant figures, so not solver noise. The recorded
`beta` on that point was 7.7e12. Two further tells: the per-age `mass=` column
overflowed its format field, and the patient/impatient mass ratio read 507. The
signature is garbage read back from memory, and `0f581bb` names the cause --
the renter arrays had no negative indices to write into.

Re-measured on the repaired model, that same vector gives pooled mass 87.19 and
all invariants PASS. **The bounds fix is confirmed on the exact vector that
exposed the bug.**

Worth carrying forward: an engine failure this large showed up in exactly two of
sixteen invariant lines. `wealth histogram holds the whole of net worth` still
PASSED at 1.0000 while the two distribution invariants failed at 1.4949 -- the
net-worth invariant reads a different object and never saw the corruption.

## Two caveats on reading the pre/post comparison

Between the passes the default vector gained two entries, so the pre/post twin
above is controlled in every named coordinate but not in these:

- `financial_grid_expander_negative=2.0` -- curvature of the negative grid, which
  did not need to exist when the negative grid was unreachable;
- `restrict_borrowing_to_impatient=1` -- **only the impatient type may borrow.**
  This is a behavioural restriction, not a numerical one, and it bounds how much
  of the -0.487 at limit 1.00 is attributable to the limit alone.

The three re-runs share both defaults with each other, so the ladder among them
is internally clean. The pre/post swing of 0.132 should be read as the size of
the effect, not as a single-coordinate derivative.

## An independent cross-check that came free

Line 2's first-pass point hash collided with a point another worker had already
pushed. Two independent solves of the identical vector on the identical model:

```
                                   theirs        mine
tau_l    average labour income tax  0.23433151   0.23404792
omega_l  labour supply / hours      0.37847299   0.37848363
beta     wealth over output         2.67476621   2.67687514
h_2      above half of spending     0.10663241   0.10648282
h_3      share in largest unit      0.47970083   0.47966030
```

That is the solver's noise floor: about 1e-4 on shares, about 2e-3 on W/Y. It
is the reason the rate arm above is reported as not resolvable, and it is worth
applying to any future arm: the first-pass OFF/ON borrowing twin in `307aa35`
moved `w_bot` by 1.2e-4, which is inside this floor.

## Still open

`owner_renter_problem` carries the same floor bug at line 20552.
`include_homeownership` is 0 so nothing reaches it now, but it bars borrowing
for owners and must be fixed before homeownership is switched on. Flagged in
`307aa35`; repeated here because this batch is where it would first bite.

## Superseded points

First-pass points, kept for provenance, not to be scored as ladder arms:
`point_deef8f1e37` (MODEL `1b0babfbed`, inert), `point_65c5d119a5`
(MODEL `e55e1cc855`, diverged). The first-pass line 1 point `point_30f09ca36e`
is no longer in `code/points/`.
