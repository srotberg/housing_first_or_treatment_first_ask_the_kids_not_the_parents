# Open issues, 3 September, after the switch to KKK_process

Written because a night's findings that live only in chat are lost at the next
compaction. Ordered by whether they are settled, and by what they block.

---

## A. Bugs in the model, found and fixed

All four of these are SILENT failures: the run completes, prints numbers, and
in three of the four cases passes its own invariants.

| # | fault | what it did | status |
|---|---|---|---|
| A1 | `get_probabilities_KKK_process` reads a local `width` it never assigns | transition rows summed to zero for middle nodes, the normalisation divided by that zero, and the economy came back NaN with the employed share of the homeless at −1.97 | **fixed** |
| A2 | `KKK_process` never fills the RETIREMENT rows of the grid | `exp()` was applied to whatever was in that memory; the retired face garbage productivity | **fixed** |
| A3 | `log_y_edge` left at its declaration initialiser of zero | every node interval empty, so `create_newborn_employment_probability` finds zero mass for every parent and puts EVERY newborn on the bottom node | **fixed** |
| A4 | `newborn_parent_share` never initialised | newborn draw zero, no newborns created, population dies out — while `sigma_y`, read off the grid rather than the distribution, still looks healthy | **fixed** |

Plus mean productivity, which is not a bug but would have shifted every level
parameter by nine per cent: `KKK_process` centres LOG productivity on zero, so
the LEVEL has mean `exp(var/2)` = 1.094. One constant is now subtracted in logs
at every age, which leaves the fanning untouched.

**Why none of these had been seen.** With `fixed_productivity=1` every one of
these outputs is discarded downstream — the masses and the grid by the quantile
construction, the transition by the identity loop that starts at age one. The
garbage was written and then covered on every run for as long as the frozen
grid was the only grid. Turning the switch off made the routine's output matter
for the first time.

**What could not have found A1.** A bounds check, which ran clean over exactly
this code. Reading an uninitialised local is not an out-of-bounds access.
`-finit-real=snan -ffpe-trap=invalid` is the flag that finds it and it is now
in the standing check in `ENGINE.md`; it has since run clean over the grid, the
newborn draw and 39 ages of the household problem.

---

## B. Economic issues with the process, established but NOT yet measured

Every one of these is closed-form arithmetic, not a solve.

**B1. `KKK_process` at its published parameters cannot produce homelessness.**
Its poorest household earns **0.232** of mean productivity. The quantile grid's
poorest earns 0.032. A household on 23 per cent of mean earnings pays the
cheapest rent out of income and never sleeps rough. The bottom-half earnings
share is 33 per cent against the SCF's 17.2.

**B2. The fix, and it preserves the fanning.** `kkk_sigma_scale` multiplies
both innovation sds. Every `var(a)` scales by k², every `sd(a)` by k, so
`sd(65)/sd(26)` is unchanged at 1.122 whatever k is. k ≈ 2.2 puts the bottom
half share on 16.9 per cent.

**B3. The grid's SHAPE cuts against the question, independently of risk.**

| node | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|
| quantile masses, % | 0.198 | 1.618 | 4.829 | 10.039 | 17.388 | 26.991 | 38.938 |
| KKK masses, % | 0.240 | 3.660 | 20.167 | 39.773 | 28.271 | 7.216 | 0.674 |

68 per cent of households sit on the middle two nodes and 3.9 per cent on the
bottom two. The quantile grid was built bottom-weighted on purpose, because the
drug, housing and homelessness margins are all at the bottom. KKK has three
nodes there where the quantile grid has five.

**B4. The fan at ρ=0.9 is small.** The within-cohort variance of log earnings
rises **+0.043** over forty years. The earnings literature puts the rise from
the mid twenties to the early sixties at roughly +0.3 to +0.5, which is ρ≈0.95.
Since the reason for adding risk was to put middle-aged households on the
street, the size of the fan is the thing being tested, and 0.043 is small.

**B5. The asset grid rescales with the top node.**
`financial_grid(top) = 3.2 × employment_grid(1, top node)`, and every rung
below is `top·((i−8)/24)^expander`. Counting positive grid points between zero
wealth and a year's rent on the cheapest unit: control 4, line 2 3, lines 3 and
4 **2**. The scaled arms have half the control's resolution at exactly the
margin that decides homelessness. `financial_grid_expander_positive=4.0`
restores it and should be a robustness check on whichever arm wins.

**B6. `sigma_y`'s moment was measuring the wrong object.** It read the AGE-26
share; the SCF number is a cross section of 26–65. Identical on a frozen grid,
not on a fanning one — at ρ=0.952 the age-26 share is 22.8 per cent while the
pooled share is 16.9. **Fixed**: it now pools over working ages.

---

## C. Blocking: `kkk_sigma_scale` cannot yet be calibrated

`freeze_fitted_internals = 1`, so `freeze_sd_permanent_productivity = 1`, so
both `sd_permanent_productivity_adjuster` and `kkk_sigma_scale_adjuster` are
zero and their shared distance is `(1−freeze)·|gap| = 0`. **Neither instrument
moves inside a point run.** Dispersion has always been calibrated by the OUTER
search across points, through `next_batch.py`'s instrument→moment table.

That table still maps `sd_permanent_productivity → sigma_y`, which is INERT
under `fixed_productivity=0`. It was left unswitched deliberately — two
instruments on one moment is a conflict, and which is live is a property of the
point — but until it keys on the point's `fixed_productivity`, the instruction
"calibrate sigma" does not bite on a KKK point. **This is the next code change
once the process choice is made.**

---

## D. Unresolved: why is a solve taking 13–32 minutes?

The archive's seven-node median is **3 minutes** over 22 points. Tonight the
CONTROL — the frozen quantile grid — was still solving at 13 minutes, and the
KKK arms at 30 and 32. So this is not the productivity transition.

Two suspects, and they are not independent:

- **`ssi_floor_takeup=0.5`.** In all four arms and in none of the 22 fast
  archive points, which all ran at 0 or absent. At 0.5 the floor is 0.0887
  against a bottom-node PIA of 0.0285, so the poorest retirees' income is
  lifted 3.1× and a block of households crosses from cannot-afford to can.
  `distance_rental_market` is an UNFROZEN term in the calibration loop.
- **The outer calibration `do while` has no iteration cap.** About forty
  distance terms and no `loop_count < max`, so a point runs until every
  distance is under its stopping rule. Most are frozen and therefore zeroed;
  what is left live is the equilibrium block, which is what the floor moves.

`batch_ssi_ab.txt` runs both vectors in ONE container, which also removes the
confound under every timing claim tonight: the archive's 3 minutes was measured
on other machines.

---

## E. Process failures, and the rules added for them

- **Three workers went idle mid-solve and could not be woken.** There is no
  send_message tool for sibling remote sessions. The fix is the Bash tool's
  `run_in_background` parameter, which re-invokes the worker when the command
  exits; foreground runs hit the 10-minute tool timeout and a hand-detached `&`
  is not tracked. In `ENGINE.md`.
- **The launch count was not checked against the batch file.**
- **`ssi_floor_takeup=0.5` was added to all four arms on the coordinator's own
  judgement**, to correct an earlier error. It is an untested value and is now
  the leading suspect for having broken the batch. Scope added to a measurement
  is scope that can invalidate it.
