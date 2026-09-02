# Calibration plan: the bottom-half (savings-cap) model

## 1. What the model becomes

    number_of_beta_types      2 -> 1
    savings cap               |a| <= 1.5 x average income, both sides
    financial grid            ~10 points each side of zero
    rental market             does NOT clear; rent held at benchmark
    government budget         clears on the bottom half, tau_l the instrument,
                              G-bar (net_govt_revenue_constraint) held fixed
    homeless / SUD govt cost  ZERO (done)
    productivity process      same shape, dispersion retuned to the bottom half

The population is defined by the CAP, not by a sample cut. The cap admits 52.0
per cent of SCF households, so it delivers the bottom half without conditioning
on an outcome that addiction and homelessness help cause.

## 2. Targeted moments and their instruments

See `BOTTOM_HALF_TARGETS.md` for the derivations. In brief:

| moment | target | instrument |
|---|---:|---|
| net worth / their income | 0.8216 | `discount_factor` (the only beta now) |
| housing cost / their income | 0.2051 | `relative_share_of_housing` |
| >50% of income on housing | 0.1307 | `smallest_rental_relative_to_lowest_income` |
| sd(log earnings) | 0.8791 | `sd_permanent_productivity` |
| unemployment | 0.0683 | `probability_becoming_unemployed` |
| average labour income tax | 0.0546 | `labor_income_tax_rate` -- SEE OPEN DECISION 1 |
| homelessness | 0.00798 | `size_homelessness` |
| food stamps / income | 0.0209 | `max_food_cost` |
| drug users, disorder rate | x1.31 or x1.59 | `lambda_addiction`, `addiction_scalar_1` |
| conditional moments | unchanged | unchanged |

`w_bot` and `sigma_y` are retired. `beta` as wealth/GDP is retired.

## 3. UNTARGETED MOMENTS -- the part the AE actually attacked

The AE: *"The paper never shows the model fit of the quantitative model and the
model does not match up to non-targeted moments, casting doubt on any
counterfactual policy experiments."* This is the section that answers it. All of
these are computable from data already in the repo, for exactly the modelled
population, and NONE is used in the calibration.

### From SCF 2022, bottom half by wealth

    share with NEGATIVE net worth              0.1509
    share with net worth < one month of income 0.2510
    median net worth                          $27,000  (0.19 x mean income)
    net worth p25 / p75                    $3,467 / $93,333
    median rent-to-income, renters             0.2629
    homeownership rate                         0.3905   <-- SEE THE WARNING
    mean net worth by age  26-35 / 35-50 / 50-65 / 65+
                              $45k / $48k / $52k / $55k
    mean income by age        $73k / $68k / $54k / $36k

### From NSDUH 2024

    SUD prevalence by income bracket (the full gradient, not just the cut)
    SUD prevalence by age band (`age3`)
    days of use, conditional on use (`mrjydays`, `cocydays`, `herydays`,
      `methndayyr`, `hallndayyr`, `inhndayyr2`) -- an intensive margin the model
      has an analogue of in `theta`
    share of SUD cases outside the bottom half   0.203 (hard drugs, 26+)

### Already in the repo and usable

    us_homeless_by_age.csv          homelessness by age
    FRB_DFA_net_worth_levels_by_percentile   wealth percentiles over time
    CEX_housing_tenure_means_2024   housing outlay by tenure
    HUD_picture_subsidized_households_2023   voucher coverage
    us_overdose_mortality.csv       overdose deaths
    us_mortality_multipliers.csv    SMR by condition

### THE ONE THAT IS A PROBLEM RIGHT NOW

**39.05 per cent of the bottom half by wealth OWN THEIR HOME.** The model has
`include_homeownership=0` -- every household rents. So on the single largest
untargeted moment available for this population, the model would predict 0
against a data value of 0.39.

That is precisely the failure the AE named. It is also awkward because they
asked *"Why do we need the role of homeownership, and not simply the difference
between homelessness and houses?"* -- a question that reads as permission to drop
ownership, but the data says ownership is 39 per cent of this population, not a
rounding error.

Three ways out, and the choice is the author's:
1. keep `include_homeownership=0` and report the moment as a known, stated
   limitation, arguing the paper is about renters and the homeless;
2. define the population as bottom-half-by-wealth AND renters, which changes
   every target in section 2 and needs them all recomputed;
3. turn ownership back on, which reverses the simplification the design is for.

Option 2 is the coherent one if the model is going to stay all-renter, and it is
NOT free -- every SCF number above would have to be recomputed on renters only.

## 4. What I CANNOT compute, and why

- **anything about the homeless themselves from the SCF.** It surveys occupied
  housing units. The homeless are out of frame, so `h_1`'s x2 rests on an
  assumption this survey cannot test.
- **the bottom half's average income tax from survey data.** No tax variable, no
  after-tax income. 0.0546 comes from the model's own schedule.
- **drug use by WEALTH.** NSDUH has no wealth variable; the 1.31-1.59 factors
  are by income.
- **`p_m` and `aleph` targets.** SMI concentration in the bottom half is
  unmeasured, and a value of life does not shrink because a household is poor,
  so `aleph` cannot be rescaled arithmetically.

## 5. Open decisions, needed before building

1. **Does `labor_income_tax_rate` hit `tau_l`=0.0546, or clear the budget?** The
   paper has tau_l clearing the budget with G-bar fixed; the calibration has it
   hitting a tax moment. In the benchmark it cannot do both.
2. **Which drug concept `b`=0.089 and `lambda_d`=0.0368 are.** Marijuana-inclusive
   or hard drugs. A factor of five separates them in NSDUH and it sets whether
   the scaling is 1.31 or 1.59.
3. **Homeownership** -- option 1, 2 or 3 above.
4. **`h_2`** -- recompute the bottom-half burden in CEX, or move to SCF and say so.

## 6. Sequence

1. settle the four decisions;
2. measure the CURRENT model's concentration of drug use and homelessness across
   the wealth distribution -- this decides whether the restructuring helps or
   hurts `b` and `lambda_d`, and it is one solve;
3. make the code changes: one beta type, symmetric grid, cap, retarget;
4. seed, then calibrate;
5. report targeted AND untargeted fit, which is the deliverable the AE asked for.

Step 2 before step 3. It is cheap and it is the only thing that can tell us in
advance whether the restructuring makes the failing block worse.
