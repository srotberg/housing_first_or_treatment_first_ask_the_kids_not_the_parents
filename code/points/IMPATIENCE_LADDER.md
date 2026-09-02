# The impatience ladder: w_bot against `discount_factor_impatient`

Three points measured here (`code/batch_impatient.txt`, lines 1-3) plus every
other point in `code/points/` that sits on the SAME anchor -- the batch vector
with `discount_factor_impatient` taken out. That anchor is md5 `ef718859` over
the sorted VECTOR line less the impatient beta; matching on it is the whole
point, because five other points in the archive carry
`discount_factor_impatient=0.55` and NOT ONE of them is a rung of this ladder.
They are single-parameter arms off a different question and each moves a name
this ladder holds fixed:

| point | `discount_factor_impatient` | what it actually varies |
|---|---|---|
| `point_01ade46ab5` | 0.55 | `newborn_endowment_scale` 0.0 -> 1.0 |
| `point_6ee0ab23e5` | 0.55 | `newborn_endowment_scale` 0.0 -> 0.5 |
| `point_30f09ca36e` | 0.55 | `unsecured_borrowing_limit` 0.30 -> 1.00 |
| `point_f4a40be627` | 0.55 | `unsecured_borrowing_limit` 0.30 -> 0.60 |
| `point_deef8f1e37` | 0.55 | `unsecured_borrowing_rate` 0.055 -> 0.20 |
| `point_f9c16d5308` | 0.55 | `include_unsecured_borrowing` 1 -> 0 |

Their w_bot ranges from 0.0033 to 0.0546 at one and the same impatient beta,
which is the measurement of how little the impatient beta explains about them.
Reading any of them as the 0.55 rung would put a spurious bracket around the
target. **No 0.50 or 0.55 rung of this ladder exists.** The workers assigned
those values have not landed a point on this anchor.

## The ladder

| `discount_factor_impatient` | w_bot | homelessness rate `h_1` | model hash | point | invariants |
|---|---|---|---|---|---|
| 0.70 | 0.04178 | 0.07244 | `1b0babfbed` | `point_5168ca9757` | all PASS |
| 0.80 | 0.05324 | 0.06083 | `1b0babfbed` | `point_8639fc153e` | all PASS |
| 0.90 | -0.00735 | 0.12523 | `e55e1cc855` | `point_31e7181863` | **2 FAILED** |
| 0.95 | 0.07383 | 0.02978 | `1b0babfbed` | `point_6aadbe9c3d` | all PASS |

Targets: w_bot = 0.025, h_1 = 0.00399.

The 0.95 rung is another worker's and is on the same anchor and the same model
hash as lines 1 and 2, so it is included.

## Line 3 is not on the same model as lines 1 and 2, and it is not usable

Lines 1 and 2 were measured on model `1b0babfbed`. Between line 2 and line 3
the rebase required to push line 2 brought in `307aa35`, "unsecured borrowing
was inert: the state opened, the CHOICE never did", which edits
`code/housing_first_or_treatment_first_SR_v1.f90`. `run_one_point.sh` compares
the source md5 against `hftf.srcmd5`, correctly found the binary stale,
and rebuilt -- so line 3 solved a DIFFERENT MODEL, `e55e1cc855`, and says so on
its MODEL line. Nothing was mislabelled; the guard did its job. But the point
cannot be set beside the other three.

It fails on its own terms as well. Two invariants are red:

    INVARIANT FAIL  income histogram holds the whole distribution = 1.4948  want 1.0000
    INVARIANT FAIL  wealth histogram holds the whole distribution = 1.4948  want 1.0000

w_bot is a wealth-histogram moment, so the -0.00735 it reports is a number
produced by a histogram carrying half again as much mass as it should. It is
not a measurement of w_bot at `discount_factor_impatient=0.90` on either model.
The 0.55 point on `e55e1cc855` (`point_f9c16d5308`) passes all invariants, so
whatever is wrong is not the new model failing everywhere; it is this point.

The source was not touched to investigate, per instruction. The 0.90 rung of
this ladder is therefore UNMEASURED and needs re-running on one chosen model.

## Does a measured pair bracket w_bot = 0.025?

**No.** On the three comparable rungs -- 0.70, 0.80 and 0.95, all on model
`1b0babfbed`, all invariants passing -- w_bot is 0.04178, 0.05324 and 0.07383,
and every one of them lies ABOVE the target of 0.025. w_bot rises with the
impatient discount factor across them, so the target sits BELOW the bottom of
the measured range and would need a `discount_factor_impatient` under 0.70. No
arm was run there, and none is reported here: the value is outside the range
that was measured and nothing in this file estimates it.

The only measured number below 0.025 is the -0.00735 of the 0.90 point, and it
brackets nothing -- it is on a different model hash and its wealth histogram
does not sum to one. Pairing it with 0.80 would also make the ladder
non-monotone between 0.80 and 0.95, which is a second sign the two are not
measurements of the same thing.
