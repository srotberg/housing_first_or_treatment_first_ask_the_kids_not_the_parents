# SEED_26: twelve controlled arms from point_9a13317e65

One coordinate moved per arm from the anchor, so each arm yields a controlled
pair `next_batch.py` can form a bracket or an elasticity from. The anchor is

```
b = 0.086789 (-2.5%)   lambda_d = 0.035791 (-2.7%)   sixteen invariants PASS
```

The **coupling** column is what the arm did to `b` and `lambda_d`, and it is the
column that decides whether a moment can be closed on its own or needs a
drug-block repair after every step.

## Arm 1 -- max_food_cost 0.007331089 -> 0.017676 (x2.411), owns cbar

`point_645ca85b44`, all sixteen invariants PASS.

| quantity | anchor | arm | predicted | measured exponent |
|---|---|---|---|---|
| food stamps / output | 0.000701 | 0.003295 | 0.004200 | **1.759** (flat density says 2) |
| recipient share | 0.048961 | 0.101666 | 0.118050 | **0.830** (flat density says 1) |

**The mechanism holds and the flat-density assumption does not, which is the
outcome that was written down in advance as the alternative.** The prediction
was that spending goes as the square of the floor and recipients as the first
power, because the benefit is `max(0, cbar - 0.30*y)` and the eligible range is
narrow. Both exponents come in below their flat-density values, which is what a
FALLING income density over that range does to both at once. The relationship
between the two survives: the ratio of the measured exponents is **2.118 against
the predicted 2.000**, six per cent out. So the formula was right about how the
two moments move together and wrong about the density, and the useful output is
a measured elasticity rather than an assumed one.

On the measured exponent, closing the rest of cbar needs `max_food_cost` x1.148
to **0.020292**, which also predicts a recipient share of 0.114 against 0.125.

### But max_food_cost is strongly coupled to the drug block

| | anchor | arm | move | vs target after |
|---|---|---|---|---|
| b | 0.086789 | 0.103693 | **+19.5%** | +16.5% |
| lambda_d | 0.035791 | 0.046292 | **+29.3%** | +25.8% |

Raising the food floor raises drug use substantially, which is economically what
it should do -- the floor relaxes the budget constraint of exactly the poorest
households, who are the marginal users -- but it means **cbar cannot be closed
by moving its own instrument and stopping**. It joins the coupled list that
`restore.py` was written for: every step on the food floor needs a drug-block
repair behind it, and the step sizes have to stay small enough for that repair
to be possible.

## Arm 2 -- utility_cost_of_treatment 0 -> 2.0, owns tau_u

`point_4150720d61`, all sixteen invariants PASS.

**The corner is broken and the target is bracketed.** `tau_u` goes from
0.9999949 at a price of zero to **0.169372** at a price of 2.0, against a target
of 0.245. It was +308 per cent and is now -30.9 per cent, on the other side, so
two measured points straddle the target and no elasticity is needed. Log-linear
in the price puts the root at `utility_cost_of_treatment` = **1.5842**.

This confirms in one run that the +308 per cent was never a fit failure. Treatment
was free, so everyone carrying the disorder took it; given a price, take-up
behaves and is if anything too sensitive rather than too flat.

### The prediction about the coupling's SIGN was wrong

Written down before the arm ran: *"Charging for treatment lowers take-up, which
lowers recovery, which raises the disorder rate: `lambda_d` should rise when this
parameter leaves zero, and `b` with it."*

It does the opposite, and by a lot:

| | anchor | arm | move |
|---|---|---|---|
| b | 0.086789 | 0.046550 | **-46.4%** |
| lambda_d | 0.035791 | 0.016748 | **-53.2%** |

The recovery channel is real but it is second order. The first-order effect runs
through the ANTICIPATION of the price: a household deciding whether to use knows
that the disorder now carries either an untreated future or a costly treatment,
so the disorder is worse ex ante and fewer households walk into it. Deterrence
beats the recovery loss by enough to cut the drug stock nearly in half. The
earlier note in CALIBRATION_STATE.md predicting a rise is wrong and is corrected
by this measurement.

### The two coupled arms pull in OPPOSITE directions, which is useful

| arm | b | lambda_d |
|---|---|---|
| max_food_cost x2.411 | +19.5% | +29.3% |
| utility_cost_of_treatment 0 -> 2.0 | -46.4% | -53.2% |

`cbar` needs the food floor UP, which raises the drug block; `tau_u` needs the
treatment price UP, which lowers it. Moved together they partly cancel, so the
pair may be closable with a much smaller drug-block repair than either alone
would need. That is a hypothesis from two measured arms and is worth a joint
point once the cheap arms are in, but it is not yet a measurement of the joint
move.

## A structural blind spot: a parameter at exactly zero can never be calibrated

The gate now forms `max_food_cost`'s elasticity from arm 1 and writes a
correction for it (+1.76, which is the 1.759 measured above). It still reports
*no controlled pair* for `utility_cost_of_treatment`, even though arm 2 measured
one, and the reason is arithmetic rather than missing data. `elasticity()` at
line 699 discards any pair with

```
min(xa, xb, ya, yb) <= 0
```

and the anchor holds the price at exactly 0, so `log(xb/xa)` is undefined and the
pair is thrown away. `bracket()` works in logs for the same reason.

**So `tau_u` -- the worst gap in the table -- is unreachable by the search for as
long as the anchor keeps its instrument at zero**, no matter how many arms are
measured. This is not a bug in `next_batch.py`: log space is right for every
other instrument, and a multiplicative step from zero has no meaning. It is a
property of anchoring a parameter at a bound.

The remedy is the anchor, not the math. Arm 2 brackets the target between a
price of 0 and a price of 2.0 and puts the root near **1.584**, so the next
anchor should carry a non-zero price and everything downstream then works
normally. Recorded here rather than acted on immediately, because nine arms are
still measuring and moving the anchor now would strand them.

`CORRECT_27.txt` is committed as the record of what the gate proposed at this
firing. It was NOT launched: it holds a single arm on `max_food_cost`, an
instrument arm 1 has just shown moves `b` by +19.5 per cent and `lambda_d` by
+29.3 per cent, so a solo step on it would open the drug block again for a
moment that a joint step can close more cheaply. It also would have collided
with the seed batch, which is still writing points and committing on the same
four cores.

## A prediction written down BEFORE arm 4 runs: w_bot is the structural instrument

The comment at line 5881 states the mechanism, and it was written before `w_bot`
became a scored moment:

> THE LOWER TAIL OF WEALTH IS WHAT DECIDES WHO CAN BE SHUT OUT, and nothing in
> the loss pins it. [...] A model can carry the right total wealth with far too
> little of it concentrated, and then no household is ever short of the smallest
> rent.

That is exactly the state of the anchor. The bottom half holds **5.03 per cent**
of net worth against a target of 2.50 -- twice as rich as the data -- so no
household is ever short of the smallest rent, and every homeless household is
homeless by choice. `homeless by choice = 1.0000` and `homeless who could afford
it on income = 1.0000` are not two more broken moments; they are the same fact
as `w_bot` +101 per cent, seen from the housing margin.

**So `w_bot` is not one item on the list of twelve. It is the instrument for the
structural failure the author asked about**, and one causal chain ties it to
five separate misses:

```
bottom half too rich -> nobody priced out of the smallest rent
                     -> all homelessness is voluntary
                     -> only the young, who have not saved yet, choose it
                     -> they are employed, and they are clean
                     -> the homeless SUD mass is ~0, so mu_H divides by nothing
```

Arm 4 moves `discount_factor_impatient` from 0.95 to 0.90, which makes the
impatient type save less and should pull the bottom half's share down. **The
falsifiable prediction, recorded before the arm lands:** if this chain is right,
that single arm should move all of these together and in these directions --

| quantity | anchor | prediction |
|---|---|---|
| w_bot | 0.050349 | FALLS toward 0.025 |
| h_1 | 0.001493 | RISES toward 0.00399 |
| homeless by choice | 1.0000 | FALLS below 1 |
| share of the homeless in band 1 | 0.968 | FALLS |
| employed share of the homeless | 0.967 | FALLS toward 0.46 |
| SUD share of the homeless | ~0 | RISES above 0 |

If `w_bot` falls and the other five do NOT move, the chain is wrong: the bottom
half's wealth is not what is gating the housing margin, and the missing
involuntary channel has to come from somewhere else -- which would be a model
question for the author rather than a calibration one. Either way the arm
settles it, and the answer is worth more than the elasticity it was launched for.

## Arm 3 -- probability_of_voucher_benchmark_used x1.936, owns pi_V

`point_336ada07ca`, all sixteen invariants PASS.

`pi_V` goes 0.137434 -> **0.228932** against a target of 0.266, so -48.3 per cent
becomes -13.9 per cent. The linear guess predicted 0.266046, essentially the
target exactly; the measured exponent is **0.773**, so coverage saturates in the
lottery rather than tracking it one for one. Closing the rest needs a further
x1.2144, to `probability_of_voucher_benchmark_used` = **0.029316**.

**This is the first comparatively CLEAN instrument.**

| arm | b | lambda_d |
|---|---|---|
| 1 max_food_cost x2.411 | +19.5% | +29.3% |
| 2 utility_cost_of_treatment 0 -> 2.0 | -46.4% | -53.2% |
| 3 voucher lottery x1.936 | **+5.9%** | **+8.3%** |

A near-doubling of voucher coverage moves the drug block by under nine per cent
and leaves both b and lambda_d still inside ten per cent of target (+3.3 and
+5.4). So `pi_V` can be closed on its own instrument without a repair behind it,
which is the first moment on the list of which that is true.

## Arm 4 -- discount_factor_impatient 0.95 -> 0.90, owns w_bot. THE PREDICTION FAILED.

`point_409b58e45c`, all sixteen invariants PASS. Scored against the six
directions committed before it ran:

| quantity | anchor | arm 4 | move | predicted | verdict |
|---|---|---|---|---|---|
| w_bot | 0.050349 | 0.045084 | -10.5% | falls toward 0.025 | **yes** |
| h_1 | 0.001493 | 0.002187 | **+46.5%** | rises toward 0.00399 | **yes** |
| homeless by choice | 1.0000 | 1.0000 | +0.0% | falls below 1 | **no** |
| share in band 1 | 0.968165 | 0.972387 | +0.4% | falls | **no** |
| employed share of the homeless | 0.966713 | 0.964754 | -0.2% | falls toward 0.46 | **no** |
| SUD share of the homeless | ~0 | 0.008541 | off zero | rises above 0 | trivially |

**Two of six. The chain as written is wrong**, and the way it is wrong is more
useful than the way it was right.

`w_bot` moves the LEVEL of homelessness and not its COMPOSITION. The elasticity
of `h_1` to `w_bot` is **-3.46**, which is large -- a ten per cent fall in the
bottom half's wealth share raised the homelessness rate by nearly half -- so the
wealth channel really does gate how many people are on the street. But every
compositional moment stood still: `homeless by choice` is **still exactly
1.0000**, `homeless who could afford it on INCOME ALONE` is **still exactly
1.0000**, the young still hold 97 per cent of the homeless and 96 per cent still
work. Poorer households did not get shut out of housing. More of them CHOSE it.

So the correct statement is narrower than the one committed: making the bottom
half poorer produces more voluntary homelessness among the young, not
involuntary homelessness among anyone. **The age profile, the employed share and
the SUD share of the homeless are not reachable through `w_bot`**, and on this
evidence they are not reachable through any instrument that only moves wealth.
The model has no mechanism that puts a household on the street against its will,
and the four moments that depend on one cannot be calibrated into existence.
That is a model question for the author, not a calibration question.

The test was weak in one specific way that should be said: `w_bot` only moved
10.5 per cent and is still 80 per cent above target, so this does not prove the
composition would stay frozen all the way down at 0.025. It proves the six do
not move together, which is what was claimed.

### And this instrument is unusable as it stands

| | anchor | arm 4 | move |
|---|---|---|---|
| b | 0.086789 | 0.294197 | **+239.0%** |
| lambda_d | 0.035791 | 0.184443 | **+415.3%** |
| beta | 2.148398 | 2.316419 | +7.8%, toward its band |

`discount_factor_impatient` is by far the most coupled instrument measured --
five e-folds of damage to the drug block for a ten per cent move in its own
moment. That is economically unsurprising, since impatience is the thing that
drives households into addiction here, but it means **`w_bot` cannot be closed
with this instrument at any step size that leaves b and lambda_d usable.** Of
the four arms so far it is the only one that is not merely coupled but
prohibitive.

## Arm 5 -- size_homelessness x1.350, owns h_1. The cleanest instrument measured.

`point_00b99e6297`, all sixteen invariants PASS.

`h_1` goes 0.001493 -> **0.002084** against a target of 0.00399, so -62.6 per
cent becomes -47.8 per cent, on an elasticity of **1.111**. Closing the rest
needs `size_homelessness` x1.794 to **0.17956**, comfortably inside its bounds
of 0.01 to 5.0.

**It moves the drug block by five thousandths of one per cent.** b goes +0.0047
per cent and lambda_d +0.0039 per cent -- not small, negligible. This is the
first instrument that can be moved as far as its moment requires without any
repair at all.

| arm | instrument | b | lambda_d |
|---|---|---|---|
| 4 | discount_factor_impatient | +239.0% | +415.3% |
| 2 | utility_cost_of_treatment | -46.4% | -53.2% |
| 1 | max_food_cost | +19.5% | +29.3% |
| 3 | voucher lottery | +5.9% | +8.3% |
| 5 | size_homelessness | **+0.005%** | **+0.004%** |

### It also confirms arm 4's negative result independently

The composition of the homeless did not move here either. `homeless by choice`
is **still exactly 1.0000**, band 1 still holds 97.1 per cent, and the employed
share **rose** to 0.97299 from 0.96671.

So two different instruments, working through two different channels -- one
making the poor poorer, one making homelessness less unpleasant -- both raise
the NUMBER of homeless households by tens of per cent and leave WHO they are
completely unchanged. That is now a replicated finding rather than a single
arm's result, and it is much harder to explain away than one measurement was.

**h_1 is closable and the composition moments are not.** The homelessness rate
can be put on target with a clean instrument at no cost to anything else. The
age profile, the employed share and the SUD share of the homeless are a
different matter: nothing measured so far moves them, because every homeless
household in this model is there voluntarily and the model contains no channel
that makes a household homeless against its will.

## Arm 6 -- largest_house_size x1.350, owns h_2. It closed TWO moments.

`point_e1830a5fc6`, all sixteen invariants PASS.

| moment | anchor | arm 6 | target | was | now | elasticity |
|---|---|---|---|---|---|---|
| h_2 | 0.068423 | 0.105191 | 0.101 | -32.3% | **+4.1%** | 1.433 |
| gamma | 0.194661 | 0.244576 | 0.268 | -27.4% | **-8.7%** | 0.761 |

**Both are inside ten per cent off one arm**, and h_2 slightly overshot, so its
target is bracketed. Landing h_2 exactly needs `largest_house_size` = 0.146656,
a small step back from where the arm put it.

### gamma has two instruments, not one

`relative_share_of_housing` owns `gamma` in the `OWN` map, and arm 7 was launched
to move it. But `largest_house_size` moves `gamma` at an elasticity of 0.761 and
has now closed most of that gap on its own. Two instruments on one moment is the
duplicate-driver problem the map was explicitly built to avoid, and it will show
up as the two arms disagreeing about where `relative_share_of_housing` should
sit. Arm 7 measures the other half of the pair and the two together will say
which instrument should own `gamma` and which should be held -- that is a
mapping decision, and it is worth making from the two measured elasticities
rather than by assumption.

### The coupling is moderate, and it points the other way from the food floor

| | b | lambda_d |
|---|---|---|
| arm 6 largest_house_size x1.350 | -19.3% | -18.5% |
| arm 1 max_food_cost x2.411 | +19.5% | +29.3% |

Almost exactly equal and opposite on b. Three of the six arms measured so far
move the drug block in one direction and two move it in the other, which is what
makes a joint step worth measuring rather than a sequence of repairs.

## Arm 7 -- relative_share_of_housing x1.350, owns gamma. The OWN map is right after all.

`point_3c6b3c9e09`, all sixteen invariants PASS. `gamma` goes 0.194661 ->
0.218341, -27.4 per cent to -18.5 per cent.

The two housing instruments both move both housing moments, so the pair has to
be read as a two-by-two rather than as two separate arms:

| instrument | d ln h_2 | d ln gamma | ratio |
|---|---|---|---|
| largest_house_size | 1.433 | 0.761 | 1.884 |
| relative_share_of_housing | 0.195 | 0.383 | 0.509 |

**The suspicion of a duplicate driver raised after arm 6 was wrong and is
withdrawn.** `largest_house_size` is absolutely stronger on both moments, but
what decides an assignment is comparative advantage, not absolute size: it is
relatively better at `h_2` by 1.884 and `relative_share_of_housing` is
relatively better at `gamma` by 0.509. That is exactly the assignment the `OWN`
map already makes. The matrix is well conditioned -- the two ratios differ by a
factor of 3.7 -- so the two moments are jointly identified rather than
collinear.

Solving the two-by-two from the anchor lands both at once:

```
largest_house_size         0.1117662 -> 0.138801   (+0.2166 e-folds)
relative_share_of_housing  0.1527137 -> 0.228934   (+0.4049 e-folds)
```

Note this is a smaller step on `largest_house_size` than arm 6 took, because arm
6 overshot `h_2` while carrying `gamma` most of the way; the joint solve puts
some of that work back onto the instrument that owns `gamma`.

Coupling: b +20.5 per cent, lambda_d +44.0 per cent, the largest lambda_d
coupling of any arm except `discount_factor_impatient`.

## The gate crashed at 07:27, and what it proposed afterwards must not be run blind

`next_batch.py` died with a `ZeroDivisionError` in `bracket()` the moment arm 2
gave `utility_cost_of_treatment` a second value:

```
near = [y for x, y in g if abs(math.log(x / x_base)) < 1e-6]
```

`x_base` is the parameter's value at the base point and the base holds it at
zero. This is the same blind spot recorded earlier, but sharper than described:
it is not that a zero-anchored parameter is quietly skipped, it is that once a
second value exists the whole gate falls over and emits nothing at all. The
group builder above already drops every `x <= 0`, and the `d` computation forty
lines below was already written `if x_base > 0 else 0.0`, so this was the single
unguarded site. Replaced with an absolute-or-relative closeness test, which is
identical to the log form for positive `x_base` and defined at zero.

`tau_u` still gets no bracket, and that is correct rather than a residual bug: a
log interpolation from zero has no meaning, and the anchor has to move off the
bound before the moment can be searched. The fix restores the honest skip in
place of a traceback.

### CORRECT_29.txt is a record, not a plan

With the gate working it writes six arms. Five are reasonable. One is dangerous:

```
discount_factor_impatient   w_bot  +105%  +2.16   0.95 -> 0.75232
```

Arm 4 measured that instrument at 0.95 -> 0.90 and it moved b by +239 per cent
and lambda_d by +415 per cent. The gate is proposing a step **five times
larger**, because it steps every coordinate independently and has no model of
coupling at all. Run as written it would put the drug block orders of magnitude
off target to buy one moment.

That is the general lesson from this seed round, and it is why the arms were
worth measuring before any batch was launched: **the gate's arms are correct
one-at-a-time steps for a system it assumes is diagonal, and the coupling
measurements say it is not.** The joint step has to be built from the couplings,
not read off the batch file.

A cross-check that the fix is sound: the gate's own bracket for
`largest_house_size` returns 0.14664, against 0.146656 computed independently
from arm 6's elasticity here. The same number to five significant figures.

## Arm 8 -- kappa_phi_d_level 8.0 -> 6.0, owns y_u. y_u IS NOT REACHABLE IN BOUNDS.

`point_320a774e5a`, all sixteen invariants PASS.

The step went the wrong way and that is the useful part. `y_u` moves 0.906337 ->
**0.954940**, from +22.5 per cent to +29.0 per cent, so lowering the mortality
multiplier RAISES the income of drug users. The elasticity is **-0.182**: to cut
`y_u`, `kappa_phi_d_level` has to go UP.

It cannot go up far enough.

```
required from the anchor : +1.1166 e-folds  ->  kappa_phi_d_level = 24.44
authorised bounds        : (4.0, 10.0)
at the ceiling of 10.0   : y_u = 0.870348, still +17.6 per cent
```

**So `y_u` cannot be brought inside ten per cent by its own instrument at any
value the evidence permits.** The bound is not arbitrary: standardised mortality
ratios for opioid use disorder run 6 to 10 in the literature, 8 is the assigned
midpoint, and the author authorised 4 as a floor. Reaching `y_u` needs 24.4,
which is two and a half times the top of the published range.

A second measurement says the ceiling is already too high rather than too low.
At `kappa_phi_d_level` = 6 the model puts **42.8 per cent of deaths on drugs
against 20 per cent observed**, already more than double. Pushing the parameter
toward 10 to chase `y_u` would drive that further out. The instrument is being
asked to serve a moment it barely moves while badly distorting one it moves a
great deal.

Coupling is severe as well: b **+87.9 per cent**, lambda_d **+157.1 per cent**.

**This needs the author's decision.** Either `y_u` gets a different instrument,
or it joins `h_3` as a concession, or the mortality bound is reopened against
the evidence. It is the second moment in this round with no usable path --
`w_bot` is the other -- and unlike `w_bot` this one is blocked by an externally
assigned bound rather than by coupling, which makes it a scope question rather
than a search question.

## Arm 9 -- probability_becoming_unemployed x0.861, owns pi_eu. Nearly clean, and it lands.

`point_debfb4e931`, all sixteen invariants PASS.

`pi_eu` goes 0.053542 -> **0.050076** against 0.0485, so +10.4 per cent becomes
**+3.3 per cent** and the moment is inside ten per cent in a single step. The
elasticity is 0.446; landing it exactly needs
`probability_becoming_unemployed` = **0.0049995**.

Coupling is moderate and tolerable: b +6.1 per cent and lambda_d +9.3 per cent,
which leaves both still inside ten per cent of their own targets (+3.4 and +6.3).
This is the third usable instrument, after `size_homelessness` and the voucher
lottery.

## Arm 10 -- mu_homeless 0.8047 -> 0.95, owns mu_H. And a correction to the record.

`point_0d88184946`, all sixteen invariants PASS.

**First, a figure that was reported wrong.** `mu_H` was described in several
status reports as +754 per cent and as one of the two worst gaps in the table.
That value, 12.5896, was measured at `point_ccd590735a` and was never re-read
after the anchor moved. **At the anchor `point_9a13317e65` `mu_H` is 1.2579,
which is -14.6 per cent** -- one of the closer moments, not one of the worst.
The +754 per cent figure should not have been carried forward and the status
lines that repeated it were wrong.

The arm itself:

| | anchor | arm 10 | target |
|---|---|---|---|
| mu_H | 1.2579 (-14.6%) | 1.0491 (-28.8%) | 1.4732 |

It moved **away** from target, which pins the sign: the elasticity is **-1.093**,
so raising `mu_homeless` raises the recovery hazard of the homeless and lowers
the housed-to-homeless ratio, exactly as the parameter's meaning implies. Closing
`mu_H` needs `mu_homeless` to go DOWN, to **0.69646**, comfortably inside its
bounds of 0.05 to 1.0.

Coupling is negligible -- b -0.0005 per cent, lambda_d -0.0015 per cent -- so
this is the second instrument, with `size_homelessness`, that can be moved
freely.

### The moment is still measured on almost nobody

The caveat stands and is worth keeping separate from the arithmetic. The SUD
share of the homeless is 3.37e-10 at the anchor and 5.16e-5 here, against 0.217
observed, on a homeless mass of 0.1506 out of about 100. So the homeless leg of
this ratio is an average over a mass of order 1e-5 of the homeless. The
instrument works and the root is real, but **matching `mu_H` at this anchor means
matching the recovery hazard of a group that barely exists**, and the number will
move sharply if the composition problem is ever fixed. Worth closing because it
is free, not because it is informative.

## Arm 11 -- increased_prob_if_homeless 0.2 -> 3.8. The formula fails and SELECTION is the reason.

`point_b640a5352d`, all sixteen invariants PASS.

A **nineteen-fold** increase in the job-loss risk of being homeless moved the
employed share of the homeless by **-0.61 per cent**, from 0.966713 to 0.960854,
against a target of 0.46.

The value 3.8 was not a guess. It came from the steady-state formula
`1/(1+(1+x)^2*(s/f))`, which was checked at the assigned x = 0.2 and predicted
0.9316 against 0.9252 measured -- a good fit -- and then solved for the x that
would deliver 0.46. **The formula is right where it was checked and worthless
where it was used**, which is the standing rule about not extrapolating past the
pair that produced it, failing on exactly the case it was written for.

The reason it fails is the reason everything else in this family has failed.
The formula treats the homeless as a population whose employment evolves by a
transition process. In this model homelessness is a CHOICE, and the choice is
made by employed young workers. Raise the risk of losing a job while homeless and
the households exposed to that risk simply stop choosing homelessness: `h_1` fell
**-21.9 per cent** in this arm. Fewer people are homeless and the ones who remain
are the same employed young households as before. **Selection undoes the
mechanical channel.**

### Three independent channels, three failures, one explanation

| arm | channel | employed share | band 1 | by choice | SUD share |
|---|---|---|---|---|---|
| 4 | make the poor poorer | 0.9667 -> 0.9648 | 0.968 -> 0.972 | 1.0000 | ~0 |
| 5 | make homelessness less unpleasant | 0.9667 -> 0.9730 | 0.968 -> 0.971 | 1.0000 | ~0 |
| 11 | make homelessness cost your job, x19 | 0.9667 -> 0.9609 | 0.968 -> 0.953 | 1.0000 | ~0 |

Wealth, amenity and employment risk are three different doors into the housing
margin and all three are shut. `homeless by choice` reads **exactly 1.0000** at
every point measured in this entire round.

**This is now a settled negative result rather than a suspicion.** The
compositional moments -- the age profile, the employed share of the homeless, and
the SUD share of the homeless -- cannot be calibrated in this model, because the
model contains no way to make a household homeless against its will, and any
instrument that makes homelessness worse for a group merely stops that group from
choosing it. It requires a modelling decision from the author, not a better
search.

Coupling is negligible: b -0.0085 per cent, lambda_d -0.0102 per cent.
