# Calibration state — 3 September, 17:50

## THE AUTHOR IS RIGHT ABOUT LABOUR SUPPLY, AND IT IS MEASURED

*"It could also be that there is too little labor supply.... That's why"*. Yes,
and the size of it is already in the archive. Same economy, only
`relative_share_of_leisure` differs:

                       rsl 3.0505     rsl 1.40     target
             omega_l      0.22645      0.34708    0.40000
                 h_1      0.01311      0.00645    0.00399
        emp_homeless      0.78966      0.49017    0.46000
               w_bot      0.01988      0.03619    0.02500
               band1      0.06647      0.04131    0.26000
               band5      0.93063      0.95619    0.07500

**More labour supply, less homelessness.** `h_1` HALVES and `emp_homeless` goes
from plus 72 per cent to plus 6.6 -- inside ten per cent for the first time in
this calibration, and by an instrument that is not its own.

The mechanism is the flow threshold: a household prefers the street below an
income of 0.4579, and hours are what put working-age income above it.

**AND IT EXPLAINS WHY BAND 5 DOES NOT FOLLOW.** Band 5 gets slightly worse,
0.9306 to 0.9562. Social security is computed from
`employment_grid(life_span-retirement_span, i)` -- the household's productivity
TYPE at the last working age -- and not from hours. So raising labour supply
lifts the working age over the threshold and leaves retirement income exactly
where it was. The old are then a larger share of a smaller homeless population.

That is the cleanest statement yet of why the age profile has resisted
everything: **every instrument that works through income works only on people
who earn**, and the moment that is furthest out is about people who do not.

## WHAT THIS MEANS FOR THE ORDER OF WORK

`relative_share_of_leisure` is now doing three jobs at once -- omega_l, h_1 and
emp_homeless -- so it should be pinned BEFORE the street size rather than after,
or the street will be calibrated against a homelessness rate that the leisure
weight is about to halve. A rung at 1.40 off the new base is in flight for
exactly this.


## THE ARCHIVE IS EMPTY ON PURPOSE. READ THIS FIRST.

`next_batch.py` and `gaps.py` both report **no archive / no scoreable point**,
and 69 points skipped. That is not a fault and nothing needs repairing. Two
configuration switches moved today on the author's instruction, and a point
either side of a switch is a different economy:

    fixed_productivity  1 -> 0    the KKK process replaces the quantile grid
    use_pia_formula     0 -> 1    the statute's benefit formula and SSI floor
                                  replace a flat replacement rate

    60 points skipped on the old productivity process
     9 points skipped on the old benefit formula

`CONFIG_SWITCHES` in both files reads the live default out of
`run_one_point.sh` and refuses to pool across either. **The seed is
`batch_pia_1415.txt` and its LINE 1 is the anchor** — until one point lands in
this configuration the gate has nothing to interpolate from and any batch it
writes would be a guess.

## THE FLEET IS THE BINDING CONSTRAINT, NOT THE MODEL

**Twelve of fifteen workers lost today to `API Error: 529 Overloaded`.** The
section in `ENGINE.md` has the measurements and the two findings that came out
of them: the brief cannot fix it, because the 529 ends the worker's own turn;
and turn COUNT is the exposure, not elapsed time, so one line per worker in
three tool calls beats consolidation while the rate is this high.

Three single-line workers are out on the PIA bracket in that shape, launched
14:20: `wip/pia-l1-1418`, `-l2-`, `-l3-`.

## WHAT THE PIA BRACKET IS FOR

`h_share5` -- the share of the homeless aged 65 and over -- is the binding
moment at **0.6447 against 0.075, plus 759.7 per cent**, and it was in
`UNSCORED` until this afternoon because nothing could reach it. Its instrument
is `ssi_floor_takeup`, and the reason nothing could reach it is that the floor
sits inside `if (use_pia_formula==1)` while every point ever run carried the
flag at 0. The floor has never executed.

The three rungs are take-up 0.0, 0.5 and 1.0. The Fortran's own note predicts
the ends: at 1 nobody is priced out of the cheapest rental in retirement and
band 5 goes to about nothing; at 0 the floor is absent and 6.6 per cent of the
population is priced out on the PIA alone. **So rung 1 may be WORSE than the
flat replacement rate it replaces.** Measure before stepping.

This also corrects a finding recorded this morning. The A/B that set
`ssi_floor_takeup` to 0.5 against 0 returned results identical to five decimals
and was written up as "the SSI floor does nothing under KKK, the PIA exceeds it
for essentially everyone". That was wrong. It does nothing because it is
unreachable.

## THE ONE MEASUREMENT THAT SURVIVED TODAY, AND WHAT IT CHANGED

`point_adc68903db`, the only point ever measured on `MODEL ecf692ab24`:

    MOMENT sigma_y  bottom half labour income share  0.05424  target 0.172  -68.5%

The old moment was the bottom half's share of PRODUCTIVITY and read 0.16272 at
the same dispersion -- minus 5.4 per cent, and it looked finished. Same
economy, two measurements: the new one carries labour supply and the age
efficiency profile and is read off the model's own distribution. **The earnings
distribution is three times more unequal than the productivity distribution**,
because low productivity households also work fewer hours. That is what the
author asked to be measured and it was not a refinement.

**IT REVERSES kkk_sigma_scale.** The scale was raised to 2.20949 to bring the
old productivity share DOWN from 0.329 to 0.172. The new moment is BELOW target
at that scale, so it wants LESS dispersion and the answer is plausibly below
1.0. The measurement that brackets it is scale 1.0 at the same base and it has
been lost to 529s four times.

## OPEN, WITH NO INSTRUMENT AND BY DECISION

- **`h_share1`**, the young share, minus 7.3 per cent. The author, 3 September:
  *"If you don't need an endowment for the youngest to get the right share of
  homeless young, that's ok too!"* `newborn_endowment_scale` stays at 0.0. It
  could only push the share DOWN and the share is already below target.
- **`y_u`**, drug users' income. Mortality pinned at 8 by the author; goes to a
  robustness run.

## THE OTHER TWO THINGS THE AUTHOR RAISED AND WHERE THEY STAND

**`omega_l` is minus 40 per cent and they asked for it fixed.** The bracket is
`batch_omegal_1400.txt`, `relative_share_of_leisure` at 0.80, 1.40 and 2.00
against 3.050529 now. Every attempt has been lost to 529s. NOTE: those three
lines carry `use_pia_formula=0` and will not pool now -- the rsl-to-omega_l
SHAPE they would measure is still worth having to narrow the bracket before
re-running it in this configuration, which is cheaper than guessing at a 20 per
cent worker yield.

**`net_income_lowest` is productivity, not income.**

    net_income_lowest = labor_income_tax_rate*employment_grid(1,1)**curvature

No labour supply, no age-efficiency profile. So the printed
`cheapest rental over lowest net income` of 16.55 is about 73 once the model's
own `omega_l` of 0.228 is applied. The author raised this directly: *"you can't
go off by productivity alone and the rent, you have to account for the labor
supply reducing the income below what the productivity itself reads"*. The
normalisation that used it is commented out so it survives only as a printed
number. NOT FIXED -- it is a one-line Fortran change to a write statement and
was deferred rather than made under a running batch.

## HOMELESSNESS IS A TASTE MARGIN HERE, WHICH IS STILL UNRESOLVED

    DIAG homeless who could afford it on INCOME ALONE = 0.932
    DIAG homeless by choice, share of the homeless    = 0.940

Measured at the scaled base. `bottom_productivity_level` moved `emp_homeless`
only 0.8598 -> 0.8247 across its whole range for that reason. But the moment
DOES straddle its target across bases -- 0.3733 at scale 1.0 against 0.8247 at
2.209 -- so the composition moves with dispersion even though its own
instrument barely touches it. Not escalated to the author, because a story
about a wall is not a measurement and the bracket says the wall has a door.

## Solve time, measured on this economy

3 to 4 minutes, median 3. The four drug points took 3 minutes each on 4 cores.

## Not in the calibration

`code/points_pregrid/` is PRESERVED and never scored or seeded from.
`p_det`, `p_fp` and `c_test` do nothing in the benchmark and belong with the
experiment, not Table 5.
