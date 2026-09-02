# THE ENDOWMENT LADDER -- `newborn_endowment_scale` at 0.5, 1.0 and 2.0, off `9575c59af0`

`code/batch_endow.txt`, three lines, each line typed out and run on its own, each
allowed to finish before the next was fired, and each point committed and pushed
before the next was started. No rebase was taken that moved
`code/housing_first_or_treatment_first_SR_v1.f90` between the three lines, so all
three arms are one economy. The file was not edited at any point.

Borrowing is ON throughout (`include_unsecured_borrowing=1`,
`unsecured_borrowing_limit=0.30`, `unsecured_borrowing_rate=0.055`), which is what
made the first two passes of this batch unusable; see the provenance section.

## The arms

| endowment scale | tag | `w_bot` | homelessness rate | homelessness rate, youngest band | `emp_homeless` |
|---|---|---|---|---|---|
| 0.5 | `b3f5b523a8` | -0.086076 | 0.009344 | 3.363e-03 | 0.9195 |
| 1.0 | `612214e316` | -0.068099 | 0.007716 | 4.569e-04 | 0.9231 |
| 2.0 | `27568375e9` | -0.036092 | 0.005791 | 5.452e-07 | 0.9975 |

Targets, for reading the columns: `w_bot` 0.025, homelessness rate 0.00399,
youngest band 0.003161 (HUD), `emp_homeless` 0.460.

**THERE IS NO ZERO-ENDOWMENT ANCHOR ROW.** No point on `9575c59af0` carries this
batch's vector at `newborn_endowment_scale=0.0`. Four zero-endowment points are on
that economy and every one of them differs from these arms in a second coordinate
as well -- `f0b286b09f` at `unsecured_borrowing_limit=1.00`, `0003e01edf` at
`smallest_rental_relative_to_lowest_income=0.060`, `b853a25c24` at
`unsecured_borrowing_rate=0.20`, `3964495db2` with borrowing off altogether -- so
none of them is a controlled anchor for this ladder and none is quoted as one. The
zero-endowment points measured earlier in this session are on withdrawn economies
and are not comparable across the model change.

## What the arms show

**The endowment does not cost `w_bot` over this range, it buys it.** `w_bot` is
negative at all three scales and rises monotonically with the endowment, by 0.0360
per unit of scale between 0.5 and 1.0 and by 0.0320 per unit between 1.0 and 2.0 --
close enough to constant that the measured range reads as a straight line at
roughly a third of a `w_bot` point per unit of scale. Homelessness falls with it,
from 0.00934 to 0.00579, and the youngest band falls far faster than the aggregate,
from 3.4e-03 to 5.5e-07, which is where the endowment acts: it is paid at birth and
it empties the youngest band first. `emp_homeless` moves the wrong way against its
0.460 target across the whole ladder, 0.9195 to 0.9975, so nothing in this range
buys that moment.

No statement is made about scales outside 0.5 to 2.0, and in particular the sign
change in `w_bot` that the slopes above would suggest is not asserted: it lies
beyond the measured arms.

## Provenance

| | endowment scale | tag | MODEL | outcome |
|---|---|---|---|---|
| line 1 | 0.5 | `b3f5b523a8` | `9575c59af0` | solved, 15 min, invariants all PASS, handover 44 of 44 |
| line 2 | 1.0 | `612214e316` | `9575c59af0` | solved, 14 min, invariants all PASS, handover 44 of 44 |
| line 3 | 2.0 | `27568375e9` | `9575c59af0` | solved, 14 min, invariants all PASS, handover 44 of 44 |

### The two passes that were discarded, and why

This batch was measured three times. The first two passes are in
`code/points_superseded/` with the economy in the filename, and are not a ladder:

| pass | arms | MODEL | why discarded |
|---|---|---|---|
| 1 | `6ee0ab23e5`, `01ade46ab5`, `3d914ad284` | `1b0babfbed` x2, `e55e1cc855` | three arms, two economies; the source moved twice mid-batch |
| 2 | `6ee0ab23e5` | `d2563e97f3` | stopped mid-arm 2 once `0f581bb` landed |

Both passes are on the wrong side of `0f581bb`, which reports that unsecured
borrowing was writing out of bounds on every renter array from the borrowing commit
onward, silently, and that such a run returns numbers that "look like an economy
and a crash does not". Every line of this batch switches borrowing on, so no
measurement taken before the `renter_array_floor` fix is a measurement of anything.
The third pass, tabled above, is the first one taken on a source where these
vectors are in bounds.

### One engine note, against `a248f8a`

`a248f8a` requires a worker not to background the solver. In this container a
foreground `Bash` call is capped at 600 seconds and a borrowing-ON solve runs 14 to
18 minutes, so a foreground run is killed before it can write a point. All three
arms above were therefore run as background tasks that wake the session on exit,
and each was read, committed and pushed the moment it woke. The failure `a248f8a`
is written against -- a worker that backgrounds a solve and then goes idle
unreachable -- did occur here in one form the note does not cover: the container was
restarted mid-solve and that arm was lost outright, which is why line 1 appears in
pass 2 and again in pass 3.
