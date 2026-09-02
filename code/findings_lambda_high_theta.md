# lambda_addiction at high theta: the missing cell of the 2x2

Point `9d6e69228d`, solved in 16 min on 4 cores against model `1b081ebc4d`,
43 of 43 parameters applied, all invariants PASS.
Vector: `relative_share_of_addiction_1=0.463`, `lambda_addiction=8.00000`,
everything else as in the control.

## The six moments

| moment | description | model | target | gap |
|---|---|---:|---:|---:|
| `b` | total drug users | 0.39456 | 0.08900 | +343.3% |
| `lambda_d` | disorder rate | 0.33349 | 0.03680 | +806.2% |
| `theta` | drug spending share | 0.25376 | 0.16200 | +56.6% |
| `h_1` | homelessness rate | 0.03436 | 0.00399 | +761.0% |
| `beta` | wealth over output | 2.49173 | 3.00000 | -16.9% |
| `w_bot` | net worth share, bottom half | 0.02689 | 0.02500 | +7.5% |

`theta` is 0.2538, a real value, not the -1.0 empty-population sentinel.
(That sentinel does occur in the archive -- `point_42a4e0966f.txt` carries it
at this same rsa1 -- so the check was worth making.)

## The square

|  | lambda=2.79953 | lambda=8.0 |
|---|---|---|
| rsa1=0.463 (high theta) | b 0.4072, lambda_d 0.2939 | **b 0.3946, lambda_d 0.3335** |
| rsa1=0.300 (low theta) | b 0.3516, lambda_d 0.1863 | b 0.2406, lambda_d 0.1589 |

All four cells are exact vector matches differing only in `lambda_addiction`
and `relative_share_of_addiction_1`:
`point_de322e4659`, `point_9d6e69228d`, `point_729d412392`, `point_9d84ecf295`.
The three pre-existing cells reproduce the brief's numbers to four decimals.

## The answer

Raising `lambda_addiction` from 2.79953 to 8.0:

| | high theta (rsa1=0.463) | low theta (rsa1=0.300) |
|---|---:|---:|
| `b` | **-3.1%** | -31.6% |
| `lambda_d` | **+13.5%** | -14.7% |

**`b`: yes, far less.** -3.1% against -31.6%, a gap of 28.5 points. The
replicate spread on `b` is 0.5%, so -3.1% is itself a real movement and the
difference between the two cells is an order of magnitude beyond noise. At
high theta the same lambda change is close to inert on the extensive margin.

**`lambda_d`: no -- it does not move less, it moves the other way.** +13.5% at
high theta against -14.7% at low theta. In absolute size the two are 13.5
versus 14.7, a 1.2-point difference that sits inside the 3.9% replicate
spread and is therefore not a difference. The sign is the finding: +13.5% is
three and a half spreads clear of zero, so the flip is real and not noise.
Answering the question as posed ("less?") on magnitude alone would be
misleading -- the magnitudes are indistinguishable; the direction is not.

So the square does not show a single attenuation story. At high theta
lambda's grip on the extensive margin (`b`) nearly vanishes, while its effect
on the intensive margin (`lambda_d`) survives at full strength and reverses.

## Independent corroboration of this cell

`point_82a955b244` sits at the same rsa1 and lambda with b=0.3935,
lambda_d=0.3327. Its vector differs from this one only in that it predates
`financial_grid_expander_negative` and carries no value for it. Against this
solve that is 0.3% on `b` and 0.24% on `lambda_d` -- inside the replicate
spread, so the cell reproduces across two independent solves.

## Two cautions for whoever reads the square next

1. **Every cell is far from target.** `b` is 343% high and `lambda_d` 806%
   high here, and the other three cells are comparably off. The square
   measures a local derivative in a region the calibration has not reached;
   it does not say what lambda does near the solution.
2. **Neither lambda in the square is near the archive's calibrated range.**
   Points at rsa1=0.463 that land close to target on `b` and `lambda_d`
   (0.09 and 0.037) carry lambda around 21-24, not 2.8-8. Both columns of
   this square are well below that range.

Neither is a reason to distrust the cell; both are reasons not to read the
comparison as a statement about the calibrated model.
