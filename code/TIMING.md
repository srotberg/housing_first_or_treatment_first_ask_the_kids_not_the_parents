# How long a solve takes, measured

Measured on this 4-core container, gfortran `-O2 -fopenmp`, `OMP_NUM_THREADS=4`,
`is_counterfactual=0` so the benchmark solves from scratch rather than reading a
previous run's `.dat` files. A timestamp was printed at the head of every age of
the backward induction, and the two binaries were run **one at a time**, since
running both at once on four cores measures contention rather than the model.

## The measurement

Per age of the backward induction, averaged over the ages observed:

| | ages 41 to 60 (retired) | ages 1 to 40 (working) |
|---|---|---|
| before the changes | 11.9 s | 125.6 s |
| after | 6.9 s | 73.5 s |
| ratio | 1.72x | 1.71x |

One full backward induction pass, 20 retired ages and 40 working ages:

* **before: 5,262 s, about 88 minutes**
* **after: 3,078 s, about 51 minutes**

The working ages cost seventeen times a retired age, which is what the extra
choices cost: hours, drug use and treatment.

## A correction to my own estimate

I predicted **3 to 6x** from collapsing the productivity nest. The measured
figure is **1.7x**.

The prediction was wrong for a reason worth recording. The productivity branch is
only one factor in the innermost nest, which also runs over addiction,
unemployment and voucher branches, and a large share of the per-age cost is the
`a'` search and the flow utility evaluation, neither of which shrinks when the
productivity transition becomes the identity. The right way to read the number:
fixed productivity is worth having because it makes the newborn externality
tractable, and 1.7x is a side benefit rather than the reason to do it.

## What a calibration costs, and which parts of this are measured

**Only the backward pass above is measured.** Everything below is arithmetic on
top of it and should be read as an order of magnitude, not a result:

```
one equilibrium  =  (backward pass + distribution iteration)
                    x outer iterations for tau_l, p_v and estates

one calibration  =  one equilibrium x parameter evaluations
```

At 51 minutes a pass, a distribution iteration at roughly a fifth of that, and
five to ten outer iterations before the tax rate and the drug price settle, a
single stationary equilibrium is **5 to 10 hours on four cores**. The first stage
bisects nineteen parameters against twenty one moments over several sweeps, which
is hundreds of equilibria, so a full calibration on this container is **weeks**.
That is not a statement about the model; it is a statement about four cores. The
paper's calibration was not run here.

Scaling is healthy — the earlier profiling measured about 360 per cent CPU on
four threads — so forty cores takes the pass to roughly five minutes and the
calibration to days rather than weeks.

## What actually makes it tractable

`PERFORMANCE_NOTES.md` section 4 is still the answer and it is still untouched.
The expectation over next period's shocks is evaluated **inside** the `a'` loop,
though it depends on neither current assets nor `a'` except through the binary
voucher eligibility indicator, so it is recomputed once per current asset
gridpoint and again redundantly across housing branches. Hoisting it into a table
computed once per age is worth **10 to 50x**, keeps every feature of the model,
and would take a stationary equilibrium from hours to minutes. Everything else on
that list, including the change measured here, is small beside it.

Two items on that list can be closed. Thread count now comes from the runtime
rather than being hardcoded. And `-O2` against `-O0` makes no measurable
difference in this code, so the compiler flag item was wrong: the run time is
work volume, not missed optimisation.
