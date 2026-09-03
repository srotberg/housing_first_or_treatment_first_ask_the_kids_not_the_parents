# The author's process and the dispersion target

The model can now be run on either of two productivity processes, chosen by
`fixed_productivity`:

* `fixed_productivity=1` — the **quantile grid**. Seven nodes cut at
  `p_i = (i/N)^y_grid_kappa` of a lognormal of mean one and sd
  `sd_permanent_productivity`, each node the conditional mean of its own
  interval. Frozen: no productivity risk after birth.
* `fixed_productivity=0` — **`KKK_process`**, the author's own. A fixed effect
  (persistence 0.5, innovation sd 0.309) and a persistent component
  (persistence 0.9, innovation sd 0.2), collapsed onto ONE grid whose width
  grows with age.

The second is what the author asked for on 3 September: *"yes, switch to my
process and use it. That process g creates a fanning out process... So there is
more inequality at older ages"*.

## The fanning out is real, and it is small

The process carries a variance recursion

    var(1) = sigma_eta^2 + sigma_alpha^2 / (1 - rho_alpha^2)
    var(a) = rho_shock^2 var(a-1) + sigma_eta^2

and the grid at age `a` runs from `-s_bottom*sd(a)` to `+s_top*sd(a)`, so the
same node index is a wider deviation from the mean at fifty than at twenty-six.
At the author's own numbers:

| | age 1 (26) | age 40 (65) |
|---|---|---|
| sd of log productivity | 0.4090 | 0.4588 |
| bottom node, in units of mean productivity | 0.2678 | 0.2307 |
| top node | 3.117 | 3.619 |

The variance rises by **+0.043** over the whole of working life. That is the fan.

## The problem: it misses sigma_y by a factor of two

`sd_permanent_productivity` is calibrated on one moment — the share of labour
productivity held by the bottom half of the distribution, **17.2 per cent** in
the SCF 2022 (households 26–65 with positive wage and salary income).

| process | bottom half's share, age 1 | pooled over ages | target |
|---|---|---|---|
| KKK at the author's numbers | 34.78% | 33.25% | 17.20% |
| quantile grid at sd = 1.00 | 16.5% | — | 17.20% |

**The bottom half holds twice the earnings it should.** This is not a new
finding: the comment beside `sd_permanent_productivity` in the Fortran already
records it — *"What it replaced: 0.458, which was not chosen at all. It was
whatever width the KKK process happened to leave on the frozen grid, and it gave
a bottom half share of 33 percent, an almost equal society."* The quantile grid
was built to escape exactly this.

## Why the two numbers differ, and it is not a contradiction

They measure different objects. Guvenen, Karahan, Ozkan and Song estimate the
dispersion of log earnings **residuals**, net of a rich set of controls. This
model has ONE productivity type per household, so that single number has to
carry **all** permanent heterogeneity — education, occupation, sector — which is
why `sd_permanent_productivity` is 1.00 and not 0.46. Reading a residual sd into
a total-dispersion slot understates inequality by construction.

## The fix, and it keeps the fanning

Scale both innovation sds by one factor `k`. The fan is proportional to the
level, so scaling changes the dispersion and leaves the SHAPE of the age profile
untouched.

| | sigma_fixed | sigma_shock | sd age 1 | sd age 40 | bottom-half share (pooled) |
|---|---|---|---|---|---|
| author's numbers | 0.309 | 0.200 | 0.409 | 0.459 | 33.25% |
| k = 2.209 | 0.6827 | 0.4419 | 0.904 | 1.014 | **16.89%** |

`k = 2.209` puts the moment within 2 per cent of target. Nothing about the
process changes except its scale.

## The fan slope is then a free choice, and rho_shock is what picks it

With the pooled dispersion pinned at 1.00, the persistence decides how much of
the inequality is already there at 26 and how much accumulates by 65:

| rho_shock | sigma_shock | sd 26 -> 65 | rise in variance |
|---|---|---|---|
| 0.90 (the author's) | 0.442 | 0.904 -> 1.014 | +0.211 |
| 0.952 (Storesletten, Telmer, Yaron 2004) | 0.376 | 0.763 -> 1.066 | +0.555 |
| 0.98 | 0.331 | 0.648 -> 1.162 | +0.931 |

All three hit the bottom-half share (16.9%); they differ only in how the
dispersion is distributed over the life cycle. The empirical literature on the
rise in the within-cohort variance of log earnings from the mid twenties to the
early sixties puts it at roughly +0.3 to +0.5, which is the region around
rho = 0.95.

**This matters for the homelessness question, not just for realism.** The reason
for adding risk at all was that the model has nobody homeless in the middle of
the age distribution: bands 2–4 carry 0.00030 against 0.00879 observed, a factor
of 29. A household becomes homeless in this model by falling far enough, and a
variance rise of +0.043 is not a fall. +0.55 might be.

## The bottom node's mass

`kkk_s_deviation_bottom` is the KKK grid's version of `y_grid_kappa` and it is
invariant to the scaling above, because it works in standardised units:

| kkk_s_deviation_bottom | bottom node mass |
|---|---|
| 3.00 | 0.621% |
| 3.25 | 0.318% |
| 3.50 | 0.155% |
| 3.75 | 0.072% |

The design target from the homelessness bands is 0.198 per cent, which is
`kkk_s_deviation_bottom` of about **3.35**.

## What the switch cost, mechanically

Four things the quantile branch does are not part of `KKK_process` and had to be
added for the flag to be flippable at all. Each is a silent failure, not a crash:

1. **The retirement rows of the grid are never assigned.** `KKK_process` declares
   `z_grid_by_age` over the whole life span and fills only working ages;
   `employment_grid=exp(...)` then exponentiated whatever was in that memory.
   Invisible under `fixed_productivity=1` because every row is later overwritten
   with row one. Now frozen at the last working age.
2. **`log_y_edge` stays at zero**, so every node interval is empty,
   `create_newborn_employment_probability` finds zero mass for every parent and
   falls into its else branch: **every newborn on the bottom node**. No stop, no
   NaN. Now built from the midpoints of the age-one log grid, which is the same
   partition the process used for its own masses.
3. **Mean productivity is 1.094, not 1.** The process centres log productivity on
   zero, so the level has mean `exp(var/2)`. Every level parameter in the model
   is quoted in units of mean productivity. One constant is now subtracted in
   logs at every age, so the units are right and the fan is untouched.
4. **`newborn_parent_share` is never initialised**, which zeroes
   `newborn_productivity_draw`, creates no newborns and kills the population —
   while `sigma_y`, read off the grid rather than the distribution, still looks
   healthy.

Two more things were repointed rather than added:

* **Social security reads the last working age**, not age one, which is the
  author's *"the ss is based on the average income of the type you retire as"*.
  A no-op under the quantile grid, where every row is identical.
* **The unemployment tilt is renormalised on the live masses.** The BLS vector
  averages to one under the quantile masses; the KKK grid puts different mass on
  the same seven nodes, so without renormalising the AGGREGATE separation rate
  would move and `probability_becoming_unemployed` would be silently
  recalibrated by a change meant to be purely distributional.

And one instrument was switched off: `sd_permanent_productivity` moves no moment
under KKK, so its internal adjuster is skipped and its distance zeroed. Left
running it would step a number that changes nothing and the calibration loop
would never terminate.

---

# What the four arms will look like before they land

Computed in closed form from the process itself, so it can be checked against
what the runs report rather than believed. `kkk_s_deviation_bottom=3.35`,
`kkk_s_deviation_top=3.0` in every KKK arm.

## The masses are the same in all three KKK arms, and they are not the quantile masses

Scaling the innovation sds moves the NODES and leaves the masses exactly where
they are, because the grid is defined in standardised units. So the three KKK
arms are a clean bracket. But the shape is nothing like the grid they replace:

| node | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| quantile masses, % | 0.198 | 1.618 | 4.829 | 10.039 | 17.388 | 26.991 | 38.938 |
| KKK masses, % | 0.240 | 3.660 | 20.167 | 39.773 | 28.271 | 7.216 | 0.674 |

**This is the most consequential difference between the two processes and it is
not about risk at all.** The quantile grid is bottom-weighted by construction:
resolution is bought where the drug, housing and homelessness margins sit, and
the top node is one fat 39 per cent lump holding everything above the 61st
percentile. The KKK grid is a symmetric bell: 68 per cent of households sit on
nodes 3 and 4, and the two bottom nodes together carry 3.9 per cent.

The homelessness margin is at the bottom, and the KKK grid has three nodes there
where the quantile grid has five. Whatever the risk does, this cuts the other
way, and it should be read as part of any difference the four arms show.

## The nodes

| | node 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| control (quantile) | 0.0317 | 0.0676 | 0.1214 | 0.2032 | 0.3386 | 0.6089 | 1.9245 |
| line 2, age 26 | 0.2319 | 0.3576 | 0.5512 | 0.8499 | 1.3102 | 2.0200 | 3.1143 |
| line 2, age 65 | 0.1963 | 0.3190 | 0.5184 | 0.8425 | 1.3692 | 2.2250 | 3.6160 |
| line 3, age 26 | 0.0311 | 0.0809 | 0.2107 | 0.5482 | 1.4268 | 3.7132 | 9.6635 |
| line 3, age 65 | 0.0215 | 0.0629 | 0.1839 | 0.5378 | 1.5724 | 4.5974 | 13.4419 |
| line 4, age 26 | 0.0567 | 0.1270 | 0.2847 | 0.6381 | 1.4301 | 3.2053 | 7.1842 |
| line 4, age 65 | 0.0205 | 0.0634 | 0.1958 | 0.6051 | 1.8695 | 5.7759 | 17.8454 |

Line 2's bottom node is 0.232 of mean productivity. **Nobody at 0.232 is priced
out of anything** — the control's bottom node is 0.0317, seven times poorer.
That alone predicts line 2 will have very little homelessness at the bottom, and
it is the dispersion miss showing up as a level.

Mean productivity is exactly 1 at age 26 by construction and drifts to 1.024
(line 2), 1.120 (line 3) and 1.348 (line 4) by age 65. That drift IS the fan —
a wider spread of logs has a higher mean in levels — and it sits on top of the
deterministic age profile of earnings, which is worth remembering when reading
the lifecycle income profile.

## Two things the runs will report that need reading with care

**1. The bottom-half share the Fortran prints is the AGE-26 one, and the SCF
number is pooled over 26 to 65.** Under a frozen grid these are the same
quantity; under a fanning one they are not.

| | reported (age 26) | pooled 26–65 | target |
|---|---|---|---|
| line 2 | 34.52% | 33.25% | 17.20% |
| line 3 | 18.77% | 16.89% | 17.20% |
| line 4 | 22.77% | 16.89% | 17.20% |

So line 4 will report a 32 per cent miss on `sigma_y` while its pooled
dispersion is within 2 per cent of target. Do not read that as a failure of line
4. `compute_bottom_half_earnings_share` should pool over working ages when the
KKK grid is live, and it does not yet — deliberately not changed while four
solves were in flight, since changing the source mid-batch changes the model
hash under them.

**2. `kkk_s_deviation_bottom=3.35` puts 0.2395 per cent on the bottom node, not
the 0.198 the design asks for.** 3.42 is the value that hits 0.198. The three
KKK arms all carry 3.35, so nothing in the comparison between them turns on it,
but it is 21 per cent more mass on the bottom node than the control carries.

## The asset grid quietly rescales with the top node, and it costs resolution at the bottom

`financial_grid(top) = 3.2 * employment_grid(1, top node)`, and every rung below
it is `top * ((i-8)/24)^expander`. So a wider top node stretches the WHOLE
positive grid, including the rungs near zero where the decision to sleep rough
is actually taken.

Counting positive grid points between zero wealth and one year's rent on the
cheapest unit (about 0.03 of mean productivity):

| | top of the asset grid | points below a year's cheapest rent |
|---|---|---|
| control | 6.16 | 4 |
| line 2 | 9.97 | 3 |
| line 3 | 30.92 | 2 |
| line 4 | 22.99 | 2 |

Lines 3 and 4 have half the resolution the control has at exactly the margin
that decides homelessness. `financial_grid_expander_positive` at 4.0 instead of
3.0 restores it (five points below the threshold at line 3's grid top), and if
either arm looks promising it should be re-run that way as a robustness check
before anything is concluded from it.

---

# The first result: a bug in `get_probabilities_KKK_process`

`batch_kkk.txt` line 4 came back a NaN economy — most moments NaN, the employed
share of the homeless at **−1.97**, and bands 1–3 at 0.46–0.50 against a target
near 0.003. The run exited 0 and 14 of 16 invariants failed.

**Cause: `get_probabilities_KKK_process` reads a local array `width` that it
never assigns.** The loop that fills it exists in `KKK_process` and does not
exist in the second routine, so all six uses — the three transition cells and
all three branches of the unconditional distribution it writes back into
`unconditional_employment_probability` — read uninitialised memory.

Fresh pages come back zeroed, so `width = 0`, and then every interior cell of
the transition collapses to `temp_upper − temp_lower = 0`. A row's whole mass is
whatever its two tail cells hold, and for a node in the middle of the grid both
tails are essentially nothing. Row sums before the normalisation, at line 4's
parameters:

| | node 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| age 26, `width=0` | 2.4e−1 | 1.1e−3 | 3.2e−8 | **1.3e−14** | 4.9e−8 | 1.4e−3 | 2.6e−1 |
| age 45, `width=0` | 2.9e−1 | 1.0e−4 | 3.1e−12 | **0.0e+00** | 4.7e−12 | 1.3e−4 | 3.1e−1 |
| any age, fixed | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

The line immediately below divides the row by its sum. At age 45 the middle
node divides by **exactly zero**. That is where the NaN comes from, and renter
income at the first age is where it first surfaced.

## Why it had never been seen

With `fixed_productivity=1` both of that routine's outputs are discarded
downstream: the masses are rebuilt by the quantile construction, and the
identity transition loop starts at age one and overwrites the whole of
`employment_process`. The garbage was written and then covered, every run, for
as long as the frozen grid was the only grid. Turning the switch off is what
made the routine's output matter for the first time.

## Why the bounds check did not catch it

It ran clean. Reading an uninitialised local is not an out-of-bounds access, so
`-fcheck=bounds,pointer` is blind to it by construction. `-finit-real=snan`
with `-ffpe-trap=invalid` is the flag that finds it, and it is now part of the
standing check in `ENGINE.md`.

## The fix

`width` is recovered from the grid itself — the nodes are equally spaced within
each age, so `(z(i,N) − z(i,1))/(N−1)` is exactly the width `KKK_process`
computed, and it needs no argument the routine was not given. Every row then
sums to 1.0000 before normalisation, as it should.

## What it invalidates

**All three KKK arms.** Lines 2, 3 and 4 every one ran on the garbage
transition; none of them measured anything and all three are being re-run.
Line 1, the control, is unaffected — at `fixed_productivity=1` the identity loop
overwrote the corrupted transition before it was ever used.
