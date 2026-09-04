"""THE AUTHOR'S RULING ON EVERY MOMENT'S DIRECTION.

Built one moment at a time on 4 September, the author ruling on each. This is the
authority the fixed-point solver uses; the measured rays in the archive are kept
as a CHECK on it, not as its source.

The author, 4 September: *"you dont need the slope to determine the adjuster....
you can reason it out"*. Requiring a measured ray had frozen nine of twenty-one
instruments -- including discount_factor, max_food_cost and addiction_scalar_1,
all of them stage 1 -- for no better reason than that the scan had not reached
them yet.

RULE reads: what to do to the PARAMETER when the MODEL MOMENT IS ABOVE TARGET.
'raise' means the parameter and the moment move in OPPOSITE directions;
'lower' means they move together.

`check` is the sign of the measured least-squares slope over the archive's ray,
where one exists. Agreement is recorded; a DISAGREEMENT is a finding -- either the
ray is contaminated or the economics is not what it seems -- and is never quietly
resolved in favour of either side.
"""

RULES = {
    # sigma_y, bottom half's share of labour income, target 0.172.
    # The author: *"if model has too much income at the bottom 50%, then raise
    # sigma_y"*. kkk_sigma_scale is the common scale on both innovation standard
    # deviations, so raising it widens the productivity distribution and shrinks
    # the bottom half's share. Measured ray agrees: slope -0.0975 over 13 points.
    'sigma_y': ('kkk_sigma_scale', 'raise', 'agrees'),
    # pi_eu, the employment-to-unemployment flow rate, target 0.139.
    # The author: *"if model has too much unemployment, lower it"*.
    # probability_becoming_unemployed is the baseline separation probability for a
    # household without the disorder, so parameter and moment move together.
    # Measured ray agrees: slope +4.458, though over only 2 points.
    #
    # ITS OWN HANDLE IS WEAK, which is the reason this moment has not closed. A
    # matched pair moved the parameter 0.0122 -> 0.0173777, up 42 per cent, and
    # pi_eu went 0.08001 -> 0.08491, up 6. Most of this model's unemployment
    # arrives through addiction rather than through the baseline rate.
    'pi_eu': ('probability_becoming_unemployed', 'lower', 'agrees'),
    # tau_l, the average labour income tax the model produces, target 0.224.
    # The author: *"if the model has too much income tax, then raise tau_ell"*.
    #
    # NOTE THE NAME POINTS THE WRONG WAY. Despite being called
    # labor_income_tax_rate the parameter behaves as the LEVEL term in a
    # Heathcote-Storesletten-Violante tax function, so raising it LOWERS the
    # average tax collected. Measured 8-point ray agrees: slope -1.044. Anyone
    # reading the name and reasoning from it alone would get this backwards.
    'tau_l': ('labor_income_tax_rate', 'raise', 'agrees'),
    # beta, wealth over output, target 3.0.
    # The author: *"lower if higher than data"*. Less patience, less saving, less
    # wealth -- parameter and moment move together. No measured ray yet; the
    # discount_factor scan was still running when this was ruled, so the ruling is
    # the only source and the ray will be a check when it lands.
    'beta': ('discount_factor', 'lower', 'no ray yet'),
    # gamma, the housing share of expenditure, target 0.268.
    # The author: *"lower if higher than data"*. relative_share_of_housing is the
    # weight on housing in utility, so parameter and moment move together.
    # Measured 8-point ray agrees: slope +0.1819.
    'gamma': ('relative_share_of_housing', 'lower', 'agrees'),
    # omega_l, labour supply over total hours, target 0.40.
    # The author: *"raise if higher than data"*. relative_share_of_leisure is the
    # weight on leisure, so more of it means less work -- parameter and moment move
    # in OPPOSITE directions. Measured 8-point ray agrees: slope -0.04635.
    'omega_l': ('relative_share_of_leisure', 'raise', 'agrees'),
    # theta, the share of spending on the addictive good, target 0.162.
    # The author: *"lower if higher than data"*. relative_share_of_addiction_1 is
    # the weight on the addictive good in the utility of a household with the
    # disorder, so parameter and moment move together. Measured 8-point ray agrees
    # and it is the STRONGEST own-slope in the table: +5.635.
    'theta': ('relative_share_of_addiction_1', 'lower', 'agrees'),
    # aleph, the model's implied value of a statistical life, target 80.
    # The author: *"lower if higher than data"*. value_of_life is the flow utility
    # of being alive traded against mortality risk, so it sets the scale the moment
    # reads off and the two move together. Measured 7-point ray agrees: slope
    # +2.007. Below target the street's mortality cost does not deter enough,
    # which is why the author called this one very important.
    'aleph': ('value_of_life', 'lower', 'agrees'),
    # lambda_d, the share of the population with a substance use disorder,
    # target 0.0368. The author: *"lower if higher than data"*. addiction_scalar_1
    # scales the hazard of developing the disorder, so parameter and moment move
    # together. No measured ray yet -- its scan was still running when this was
    # ruled.
    #
    # IT IS ALSO pi_eu'S STRONGEST HANDLE, elasticity -1.05 to -1.11 from matched
    # pairs, against +0.15 to +0.51 for pi_eu's own instrument. So this rule moves
    # the unemployment rate harder than the unemployment rule does, and the two
    # will fight unless the adjuster is damped.
    'lambda_d': ('addiction_scalar_1', 'lower', 'no ray yet'),
    # b, total drug users as a share of the population, target 0.089.
    # The author: *"raise if higher than data"* -- so parameter and moment move in
    # OPPOSITE directions, which the name does not suggest.
    #
    # lambda_addiction is the DISORDER-ONSET hazard coefficient, calibrated on the
    # NSDUH disorder rate through the onset evaluated at the mean quantity used.
    # Raising it moves users out of the plain-user pool and into the disorder
    # state faster, and the disorder state is the shorter-lived one, so the stock
    # of users falls. That is the reading that squares the ruling with the
    # mechanism; the measured 8-point ray agrees in SIGN at -0.024.
    #
    # BUT THE RAY REVERSES inside the sampled range and is nearly flat, so this is
    # a weak handle whichever way it points, and it overlaps lambda_d's population:
    # total users 0.089 against disorder 0.0368, two instruments pulling on nested
    # groups. Expect these two to fight.
    'b': ('lambda_addiction', 'raise', 'agrees in sign, ray reverses'),
    # p_m, the SMI POPULATION SHARE -- the stock, not the flow -- target 0.048270.
    # The author: *"lower if higher than data"*. smi_onset_level is the flow, an
    # onset hazard multiplying an age profile, and p_m is the prevalence it
    # accumulates into, so the two move together. Measured 7-point ray agrees and
    # is clean, slope +3.749:
    #
    #     onset 0.000345 -> p_m 0.0345      onset 0.005522 -> p_m 0.0556
    #     onset 0.000690 -> p_m 0.0360      onset 0.011045 -> p_m 0.0760
    #     onset 0.001381 -> p_m 0.0389      onset 0.022090 -> p_m 0.1161
    #     onset 0.002761 -> p_m 0.0446  (current)
    #
    # HEAVILY DAMPED: 64 times the hazard buys 3.4 times the prevalence, so
    # corrections here have to be large in percentage terms to move anything.
    # The crossing sits just above the current value, near onset 0.0034.
    # lambda_d, REVISITED: the ray DISAGREED and the ray is what is wrong.
    #
    # Its two points are addiction_scalar_1 0.0368 -> lambda_d 0.038198 and
    # 0.04048 -> 0.000223. A ten per cent rise in the parameter collapses the
    # moment by 99.4 per cent. That is not a slope, it is a CLIFF -- the same one
    # that killed the Newton attempt earlier the same day, where a 0.35 per cent
    # nudge swung lambda_d from -4.5 to -96.5 per cent. A fitted slope of -10.32
    # across a discontinuity carries no information about direction.
    #
    # WORSE: many archived points sit at addiction_scalar_1 = 0.0368 EXACTLY and
    # read lambda_d = 0.000000, while one reads 0.038198. Same parameter value,
    # the moment either on target or completely dead, so lambda_d is switched on
    # and off by something else in the vector rather than moved smoothly by its
    # own instrument.
    #
    # CONSEQUENCE FOR THE SOLVER: addiction_scalar_1 needs a far harder damped
    # adjuster than anything else here, or a fixed-point step will cross that
    # cliff into the dead region -- which LOOKS like convergence, because the
    # moment stops responding at all.
    'p_m': ('smi_onset_level', 'lower', 'agrees'),
    # cbar, food stamps as a share of income, target 0.0042.
    # The author: *"lower if higher than data"*. max_food_cost sets subsistence,
    # which is what the food-stamp formula is scaled against, so parameter and
    # moment move together. No measured ray yet -- its scan was still running when
    # this was ruled -- so the ray will be a check when it lands.
    'cbar': ('max_food_cost', 'lower', 'no ray yet'),
    # h_1, the homelessness rate, target 0.00399.
    # The author: *"lower if higher than data"*. size_homelessness scales the
    # STREET'S HOUSING SERVICES -- the model computes h_1 = housing_size(0) *
    # size_homelessness -- so a bigger value makes the street better and more
    # people choose it. Parameter and moment move together; measured 7-point ray
    # agrees at slope +0.0193.
    #
    # NAME COLLISION worth knowing: h_1 is BOTH the model's street housing size and
    # the homelessness-rate moment.
    #
    # IT FIGHTS h_share5. Measured earlier the same day: raising size_homelessness
    # 32 per cent raised h_1 45 per cent and left the age composition IDENTICAL.
    # The level moves without the composition following, so these two must be
    # driven together rather than in turn.
    'h_1': ('size_homelessness', 'lower', 'agrees'),
    # h_2, the share of renters spending above half their income on housing,
    # target 0.101. The author: *"lower if higher than data"*.
    # smallest_rental_relative_to_lowest_income sets the cheapest unit's cost
    # against the lowest income, so a dearer floor puts more households over the
    # half-of-income line. Parameter and moment move together; measured 8-point ray
    # agrees at slope +1.088.
    'h_2': ('smallest_rental_relative_to_lowest_income', 'lower', 'agrees'),
    # h_share5, the oldest band's share of the homeless, target 0.075.
    # The author: *"raise if higher than data"*. rr_homeless_old_level is the
    # relative risk of death for an old homeless person -- Baggett's age-65 value
    # held flat above 65 on the author's instruction -- so raising it removes old
    # homeless households and the share falls. Parameter and moment move in
    # OPPOSITE directions.
    #
    # THE RAY IS THE DENSEST WE HAVE AND IT REVERSES. Twelve points from 1 to 30:
    # h_share5 runs 0.996 at rr=1 down to 0.332 at rr=4.66, which is the ruled
    # direction, but the whole-range fit is -0.024 and non-monotone, so the
    # reversal is measured rather than noise. The ruling is right about the near
    # region; a constant adjuster will push the wrong way somewhere above it.
    #
    # AND IT FIGHTS h_1. Raising size_homelessness 32 per cent raised the level 45
    # per cent and left the age composition IDENTICAL, so the level and the
    # composition do not respond to the same handle.
    'h_share5': ('rr_homeless_old_level', 'raise', 'agrees near the anchor, ray reverses'),
    # pi_V, the share of eligible households receiving a housing voucher in the
    # benchmark, target 0.266. The author: *"lower if higher than data"*. Direct:
    # more voucher probability, more take-up. Measured 7-point ray agrees at slope
    # +1.717 and is monotone.
    'pi_V': ('probability_of_voucher_benchmark_used', 'lower', 'agrees'),
}
