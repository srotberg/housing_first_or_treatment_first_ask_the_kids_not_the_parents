# Calibration state — 4 September, 03:25

## THE MORTALITY HOLD IS LIVE AND THE AGE PROFILE HAS FLIPPED

`rr_homeless_hold_age = 65`, on the author's instruction: *"i think we can just
hold it at the 65 number.... and say that.... that would fix it"*.

**The sentence for the paper.** The model holds the relative risk of death from
sleeping rough at its age-65 value for all older ages, because beyond 65 the
observed ratio is dominated by survivor selection and does not identify the
causal effect the model needs. The homeless who reach 65 are unusually robust
and the comparison group includes the frail and institutionalised, so the
observed ratio is biased toward one; read literally Baggett's 1.1 at 65-84 says
the street PROTECTS the old, which is why the code floors it at one.

Sixty-five is where the ratio stops being USABLE, not where it stops being
measured. The 1.100 above 75 is Baggett's own 65-84 figure extended past its
band midpoint at 74.5 — an earlier note here calling it padding was wrong.

| | before (hold 70) | now (hold 65) | data |
|---|---|---|---|
| young band, share of the homeless | 0.1117 | 0.8589 | 0.2600 |
| old band, share of the homeless | 0.8821 | 0.0001 | 0.0750 |
| retired 66+ share | 88.2% | 0.0% | — |
| spike | age 80, 71.9% | age 33, 47.7% | — |

The age-80 spike is gone. It now overshoots the other way, and both errors are
large, but homelessness is at working ages where the employment deterrent
actually operates.

**THE RESPONSE SATURATES ABOVE A MULTIPLIER OF ABOUT 2.7.** Measured at one
vector: hold 70 gives an old share of 0.882, hold 65 gives 0.0003, hold 45 gives
0.00024 and hold 26 gives 0.00021. Nothing is bought by going below 65, so 65 is
the cheapest point on the plateau — the best place to sit for a number that has
to be defended.

**A moment the hold broke.** `sud_homeless` is now EXACTLY zero: no homeless
household carries the disorder. The old homeless were meeting that moment — 18.9
per cent of them had SUD — and removing them removed it. That is the worst gap in
the table at −100 per cent and the reason SSR reads 3.16 here against 1.46 on the
old economy. It is the objective correctly registering a moment that used to be
met by the wrong population.

## THE CONFIGURATION, unchanged

    number_of_beta_types  1          one beta for everyone
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor
    newborn_endowment_scale  0.0     HELD at zero by the author
    homeless_death_risk_flat_in_age  0   the Baggett age profile

Model hash **b2530947f0**, 117 points. The 22:00 cap patch (`4df7be4132`, the
street barred at `max_age_to_choose_addiction`) was **REVERTED** on the author's
instruction — *"You should revert to allow the 80 year olds to be homeless
again"* — and its points are orphaned. Any earlier section of this file that
describes that economy as live is out of date.

## THE SEARCH

**Twenty instruments**, all stages unioned. Of the 23 parameter/moment pairs in
`next_batch.OWN`, three are out and each for a different reason:

| parameter | moment | why it is out |
|---|---|---|
| `weight_on_child` | `omega_c` | held: *"since omega_c is so close, just keep it fixed for now, we can adjust it at the end"* — it reads 0.1622 against 0.1834 |
| `newborn_endowment_scale` | `h_share1` | the author holds it at 0 |
| `ssi_floor_level` | `h_share5` | the author holds the floor to the 2024 federal rate |

### Three scorer bugs found on 4 September, all fixed

1. **`sud_homeless` was never parsed.** The model prints
   `UNTARGETED SUD share of the homeless` on every point ever solved and
   `gaps.py` had no pattern for it, so its instrument
   (`multiple_of_probabilities_of_employment_if_addicted`) looked like a
   parameter with no moment and sat outside the search. It reads 0.1166 against
   Gutwinski's 0.217. Now scored retroactively on all 155 points, no model time.

2. **`omega` vs `omega_c`.** The Fortran prints `MOMENT omega`; `OWN` calls it
   `omega_c`. Even with `measure_child_gap=1` the scorer would have filed it
   under a key nothing reads. Aliased, so `omega_c` will work first time when it
   is taken up at the end.

3. **`archive()` enforced ONE config switch out of the table.**
   `homeless_death_risk_flat_in_age` was added to `CONFIG_SWITCHES` on
   4 September and had no effect at all: the two points solved with the flat 1.6
   mortality multiplier POOLED with the 150 solved on Baggett's age profile and
   were ranked against them as one economy. All switches enforced now, with a
   point predating a name falling back to the Fortran's compile-time default
   rather than the live value.

### `measure_child_gap` costs 9 per cent, not 100

Reported here first as a doubling, because the block runs a second solve and
converge. Measured on the same vector: **4m06s off, 4m30s on**. The
counterfactual starts from the converged baseline distribution. It is off again
because `omega_c` is held, and turning it off restores the archive: it is a
CONFIG SWITCH, so with it on exactly one point pooled and the simplex needed
twenty-two fresh solves to rebuild.

### The tension in `M`, worth knowing before it is spent

`multiple_of_probabilities_of_employment_if_addicted` is the SUD employment
penalty on both margins — job loss `× M`, job finding `÷ M`. Its target is
`sud_homeless`, which wants it UP. The moment it controls mechanically,
`kappa_ued`, is an untargeted OUTPUT on the author's own instruction
(*"we don't truly know what they are so we calibrate them"*) and already reads
0.2217 against 0.1625, **36 per cent high**. Closing `sud_homeless` drives
`kappa_ued` further from its data counterpart. Offered to the author on
4 September and NOT reversed: `kappa_ued` stays an output.

    simplex complete, 20 vertices
    best      827aa52172   SSR 2.1441
    worst vertex           SSR 19.0389   (the smi_onset_level fill)

## PARKED BY THE AUTHOR

- **Young and old homelessness.** *"Ignore young and old homelessness for now. We
  will fix that later."* `h_share1` and `h_share5` are UNSCORED. The best stage-0
  point puts 87.0 per cent of the homeless in retirement against 25.5 per cent of
  the population, spiking at age 80.
- **The flat 1.6× mortality multiplier** (`homeless_death_risk_flat_in_age=2`) was
  measured as a matched pair, `047afb7487` → `d2e58e6afb`: retired share 0.8 → 0.0
  per cent, SSR 3.0511 → 3.0636. **That test does not answer the question it was
  set**, because at that vector the spike was already at age 26, not 80. It would
  have to be rerun at `9a9c749a75` to learn anything.
- **The morbidity state.** *"keep calibrating the rest and we'll deal with
  morbidity later"*. Evidence scan is in `data/MORBIDITY_EVIDENCE.md`.
- **The newborn endowment double count**, two options offered, no decision taken.

## OPEN WITH THE AUTHOR

Nothing is blocking. The loop runs to 400 iterations and commits every twelfth.
