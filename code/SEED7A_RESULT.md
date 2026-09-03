# The first calibration point on the seven-node productivity grid

Point `points/point_ebea22f14f.txt`, model `707abb5e8d`, line 1 of
`batch_seed7.txt`. Seven productivity nodes in place of seventeen,
`smallest_rental_relative_to_lowest_income = 0.036100`. Solved in 4 minutes on
4 cores; 46 of 46 parameters applied; the file carries a full MOMENTS block
(lines 6 to 241, 25 `MOMENT` lines) and all 17 invariants pass.

## 1. Homelessness is still entirely a choice, and still not the unemployed's

| quantity | seven nodes | seventeen nodes |
| --- | --- | --- |
| homeless by choice, share of the homeless | 0.999950 | 0.92 to 1.00 |
| homelessness rate among the UNEMPLOYED | 0.00144149 | — |
| ... over the working-age homelessness rate | 0.382764 | below 1 |
| MOMENT h_1, homelessness rate (target 0.003990) | 0.00287151 | — |

**Neither has changed.** By-choice sits at 0.99995, at the very top of the old
grid's 0.92-to-1.00 band rather than below it, and the identity
`homeless who could afford it on INCOME ALONE = 0.99995` holds to the same
digit: every homeless household in the model could rent out of current income
and does not. The unemployed remain *less* likely to be homeless than the
working-age average, by a factor of 0.383 — the same sign and a decisive
magnitude, not a marginal one. Cutting the grid to seven nodes did not touch
the mechanism.

## 2. The two untargeted homelessness moments split

| moment | seven nodes | seventeen nodes | data |
| --- | --- | --- | --- |
| employed share of the homeless | 0.971975 | 0.91 | 0.460 |
| income of the homeless | 0.232350 | 1.015 | 0.191 |

Income of the homeless is the one thing that moved, and it moved almost all the
way: 1.015 to 0.2324 against a target of 0.191. The employed share went the
wrong way, 0.91 to 0.9720 against 0.46. The homeless are now poor and still
almost all working, which is the by-choice result restated — a low-income
household that works and sleeps rough, rather than a household priced out.

## 3. The rent rung did not land where the design put it

    DIAG cheapest rental over lowest net income = 0.93887950795126307

The design for this rung was about 1.01 of the lowest node's income (bottom node
cannot rent at all) and about 0.53 of the second node's. The realised ratio is
0.939, so the cheapest rental is affordable at the bottom node on wages, and the
bottom node is not excluded from the rental market as intended. Band 1 still
carries 0.920 of the homeless, so this has not by itself broken the
concentration, but the rung is 7 per cent below where it was meant to be and
`smallest_rental_relative_to_lowest_income` needs to rise to hit 1.01.

## 4. The requested moments

| moment | model | target |
| --- | --- | --- |
| w_bot, net worth share bottom half | 0.0537673 | 0.0250000 |
| beta, wealth over output | 2.26675 | 3.00000 |
| b, total drug users | 0.0836467 | 0.0890000 |
| lambda_d, disorder rate | 0.0209043 | 0.0368000 |
| sigma_y, bottom half earnings share | 0.180345 | 0.172000 |
| theta, drug spending share | 0.104744 | 0.162000 |

`theta` is a real value here, not the -1.0 empty-population sentinel. `b` and
`sigma_y` are close; `lambda_d` and `theta` are both roughly 57 to 65 per cent
of target and `w_bot` is more than twice its target.
