# Seven-node grid, bracket rung 3: `smallest_rental_relative_to_lowest_income = 0.060`

Line 3 of `code/batch_seed7.txt`, the top rung of the three-rung bracket.
Point file: `code/points/point_683510fadf.txt` (model `707abb5e8d`).
Solved in 4 minutes on 4 cores; 6.8 minutes wall clock including the
gfortran install and the build. The file carries a full MOMENTS block
(`ALL TARGETED MOMENTS` through `END OF MOMENTS`, 241 lines) and all
sixteen invariants PASS, so this is a measurement and not a stub.

## 1. Who is homeless, and why

| diagnostic | this run | seventeen-node grid |
|---|---|---|
| homeless by choice, share of the homeless | 0.9375 | 0.92 to 1.00 |
| homelessness rate among the UNEMPLOYED | 0.002701 | -- |
| ... over the working-age homelessness rate | 1.401 | below 1 |
| MOMENT h_1, homelessness rate (target 0.00399) | 0.002129 | -- |

**By choice has not changed.** At 0.9375 it sits inside the 0.92 to 1.00
band the seventeen-node grid produced. Cutting the grid to seven nodes and
pushing the cheapest rental up to 0.060 has not made anyone homeless for
want of income: 0.8797 of the homeless could still afford the cheapest
rental out of income alone.

**The unemployed have changed sign.** They are now 1.40 times as likely to
be homeless as the working-age average, where on the seventeen-node grid
they were *less* likely than average. This is the one qualitative move in
the run. It is the sign the data has, but the level is still far off: the
employed are 0.8988 of the homeless against 0.46 in the data, so the
composition remains overwhelmingly employed even with the unemployed now
carrying the higher rate.

`h_1` is 0.00213 against a target of 0.00399, so the model is still at
roughly half the homelessness rate it is meant to hit.

## 2. The two untargeted composition moments

| moment | this run | data | seventeen-node grid |
|---|---|---|---|
| employed share of the homeless | 0.8988 | 0.46 | 0.91 |
| income of the homeless | 0.2992 | 0.191 | 1.015 |

Employed share is unmoved: 0.899 against 0.91. The employment composition
of homelessness is not what the rental floor is reaching.

Income of the homeless is the large move. It fell from 1.015 to 0.299
against a data value of 0.191 -- from three-quarters of the way wrong on
the high side to within 0.11 of the target. The homeless are no longer
drawn from around the mean of the income distribution. Their band
composition confirms it: 0.609 of the homeless now come from band 1 and
0.348 from band 5, against 0.26 and 0.075 in the data. The mass has moved
to the bottom band, which is what the higher rental floor was meant to do,
but the model is now bimodal in a way the data is not, and bands 2 to 4
hold 0.043 of the homeless against 0.666 in the data.

## 3. The rental floor itself

    DIAG cheapest rental over lowest net income = smallest_house_size*rent(1)/net_income_lowest=   1.5604645561516837

156 per cent, not the roughly 169 per cent the rung was expected to land
on. The output carries no node-level income diagnostic, so the companion
figure for the second node cannot be read off this run; the 88 per cent
expectation is unverified here. The cheapest rental does still cost more
than half again the lowest node's whole net income, so the bottom node is
comfortably past the edge of affording it.

## 4. Calibration moments

| moment | model | target |
|---|---|---|
| `w_bot`, net worth share, bottom half | 0.06204 | 0.02500 |
| `beta`, wealth over output | 2.3836 | 3.0000 |
| `b`, total drug users | 0.06357 | 0.08900 |
| `lambda_d`, disorder rate | 0.01691 | 0.03680 |
| `sigma_y`, bottom half earnings share | 0.18035 | 0.17200 |
| `theta`, drug spending share | 0.12349 | 0.16200 |

`theta` is a real value here, not the -1.0 empty-population sentinel.
`sigma_y` is the only one of the six close to its target. Both drug
moments are short by roughly a factor of two on `lambda_d` and by a third
on `b`, and the bottom half of the distribution holds two and a half times
the net worth it should.

## 5. Timing

4 minutes of solve on 4 cores. The seven-node cut delivered the expected
speedup -- this is at or below the fast end of the 8-to-20-minute band the
run was budgeted for, once the one-off gfortran install and build are set
aside.
