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
}
