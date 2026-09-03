# Calibration state — 3 September, 18:33

## THE CONFIGURATION, settled today and not to be changed without the author

    number_of_beta_types  1          one beta for everyone
    discount_factor       0.945      calibrated on W/Y = 3
    fixed_productivity    0          the KKK stochastic process
    use_pia_formula       1          the US statute, with the SSI floor live
    ssi_floor_level       0.1774     the 2024 federal benefit rate
    ssi_floor_takeup      1.0        HELD, so the level is the effective floor

Both are CONFIG_SWITCHES in next_batch.py and gaps.py: a point that differs on
`number_of_beta_types` or `use_pia_formula` does not pool. 91 points are skipped
for the first and 617 are on older source revisions.

## BLOCK 1 IS ONE JOINT ROUND, AND IT IS CONVERGING

The open round's worst gap today: **1188% -> 175% -> 154% -> 70%**.

Best point `point_538b363d6e`, 46 points in this economy, 5 of 21 inside ten.

    cbar          -70.2%   max_food_cost = 0.0130        <- binding, open
    lambda_d      -55.1%   addiction_scalar_1 = 0.03680
    theta         -50.8%   relative_share_of_addiction_1 = 0.463
    pi_eu         -48.3%   probability_becoming_unemployed = 0.0122
    sigma_y       -39.2%   kkk_sigma_scale = 2.20949
    aleph         -36.3%   value_of_life = 42.0
    h_share1      -35.9%   newborn_endowment_scale = 0.0 (one-sided, at floor)
    emp_homeless  +35.0%   bottom_productivity_level = 0.004
    tau_l         +33.1%   labor_income_tax_rate = 0.7522432
    b             -30.3%   lambda_addiction = 2.69141
    h_1           -29.9%   size_homelessness = 0.0425
    pi_V          +17.1%   probability_of_voucher_benchmark_used = 0.052
    h_2           -11.2%   smallest_rental_relative_to_lowest_income = 0.114
    beta           +8.2%   discount_factor = 0.945                      *
    p_m            -8.2%   smi_onset_level = 0.002761206                *
    gamma          -6.7%   relative_share_of_housing = 0.100            *
    omega_l      inside 10 -- relative_share_of_leisure = 0.9693        *

`CORRECT_67.txt`, 12 lines, running on three workers.

## WHAT IS PARKED, AND WHY

`h_share5`, old-age homelessness, on the author's instruction: *"Ignore the old
homelessness for now. Just calibrate the rest of the block first."* It was 765
per cent out and dominates a MINIMAX, so nothing else could be ranked while it
was scored. `ssi_floor_level` still owns it and is idle. Restoring it is
deleting one line from UNSCORED.

`w_bot` is unscored: with one beta there is no second factor to aim at it. It
reads 0.021 against 0.025 anyway.

## THE THREE THINGS THE AUTHOR HAS ASKED FOR AND NOT YET GOT

1. **The SSI asset test.** Real SSI has a $2,000 limit, about 0.03 of the
   average wage index. The floor lives in `model_ss_benefits(employment_index)`,
   a function of the productivity type only, so an asset test means threading
   wealth through `calculate_income` -- **19 call sites** -- or applying the
   floor at each site where assets are known. Deferred to the age-profile work,
   which is where it bites, on the author's own sequencing.
2. **Their third instruction of 18:20**, which arrived truncated at "Third,".
3. **State SSI supplements**, worth about +0.02 on the floor. Measured at 0.195
   in `batch_joint2_1820.txt` line 4.

## THE FINDING THAT WILL DECIDE THE AGE PROFILE

The street carries **no disutility at all**. Housing enters preferences only as
`housing_size**((1-sigma)*gamma)`, and `mu_homeless` is the addiction recovery
hazard, not a homelessness penalty. So a household prefers the street below an
income of **0.4579** -- 0.72 of average labour income -- and retiree income runs
0.400 to 0.510. That is why the old are homeless here, and why no transfer
programme closes it: at a floor above 0.75082 every retiree gets the same
benefit, because PIA is capped there.

Full argument in `SSI_FLOOR_ANALYSIS.md` and `US_RETIREE_TRANSFERS.md`.

## THE CLIFF, which the age profile has to be read off

At the calibrated leisure weight, across a step of 0.0116 in the street's size:

    street 0.0384 -> h_1 0.00068, band1 0.6804, band5 0.2725
    street 0.0500 -> h_1 0.01420, band1 0.0335, band5 0.9640

h_1's target is inside that interval and the composition inverts across it.
Rungs at 0.0425, 0.0448 and 0.0470 are in the archive or in flight.

## Solve time

About 2.5 minutes at one beta type; 5 minutes 0 seconds was measured at two.
