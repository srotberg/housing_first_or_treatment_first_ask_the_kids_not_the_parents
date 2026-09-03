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
