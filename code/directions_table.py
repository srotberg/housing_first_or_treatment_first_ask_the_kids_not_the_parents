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
    # SIGN CORRECTED 4 September. The author first ruled *"lower if higher than
    # data"*, then reached the right answer from the other direction: *"if raising
    # M lowers addiction, you just have to lower b so more want to be addicted"*.
    #
    # b IS addiction_scalar_1 -- B_SWEEP_GRID.txt holds 0.0368, exactly its value
    # -- and the Fortran states the mechanism at line 1485: *"the marginal value of
    # the first unit is theta/b, so participation FALLS in b"*. Parameter and
    # moment move in OPPOSITE directions.
    #
    # THE MEASUREMENT SAID SO AND I OVERRODE IT. The ray reads 0.0368 -> lambda_d
    # 0.038198 and 0.04048 -> 0.000223, and I recorded it as "a cliff, unusable,
    # the ruling stands". The cliff is real -- a ten per cent rise collapses the
    # moment 99.4 per cent -- but the SIGN was right, and dismissing a measurement
    # because its magnitude is implausible threw away the part that was sound.
    #
    # What it cost: the fixed point drove lambda_d AWAY from target for its whole
    # run, 0.0333 down to 0.0193 against a target of 0.0368, lowering b whenever
    # the moment was above target and raising it whenever below.
    # lambda_d IS THE HAZARD'S MOMENT. pi_d(v) = 1 - exp(-lambda v), so a bigger
    # lambda_addiction means a higher chance of developing the disorder at any
    # quantity: parameter and moment move TOGETHER. Above target, lower it.
    'lambda_d': ('lambda_addiction', 'lower', 'hazard: pi_d(v) = 1 - exp(-lambda v)'),
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
    # b IS THE THRESHOLD'S MOMENT. A household buys only if C > (phi/theta) p b,
    # so raising addiction_scalar_1 raises the bar and fewer households buy:
    # parameter and moment move OPPOSITELY. Above target, raise it.
    #
    # AND THIS THRESHOLD IS WHY NO HOMELESS HOUSEHOLD HAS THE DISORDER. It requires
    # consumption ABOVE a bar to use at all, and homelessness is consumption below
    # the rental margin, far under it. The two are mutually exclusive by
    # construction, which is why sud_homeless reads 6e-07 at every parameter
    # setting tried. Lowering b is what brings the bar down to where poor
    # households clear it.
    'b': ('addiction_scalar_1', 'raise', 'threshold: C > (phi/theta) p b'),
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
    # h_share5 HAS NO INSTRUMENT FROM 4 September, 21:00. The author:
  # *"for the old, you hold the probability of death at its value at age 65"*.
  # rr_homeless_old_level is set to 0, which is the Fortran's own branch for
  # holding rr_homeless_profile at the age-65 value (2.715, Baggett's number)
  # rather than replacing the tail with a calibrated flat level.
  #
  # It should never have been carrying this moment. Measured: the ladder from
  # 3.4 to 30 moves every moment by under 0.05 per cent, so it is INERT above
  # 3.4; its only live window is about 2.4 to 3.0, where h_share5 swings from
  # 0.99 to 0.00; and it limit-cycled there for a dozen iterations. The old-age
  # spike it was chasing was one age -- data age 84, the last age the street may
  # be chosen -- and max_age_to_choose_homelessness=58 removes it directly.
  #
  # RESTORED 5 September on the author's instruction: *"i think you can also let
  # the death risk after age 65 to be adjusted to hit the share of the homeless
  # who are old"*. Starting from 2.715, which is Baggett's own measured value at
  # age 65 and therefore continuous with the hold it replaces.
  #
  # WHAT IS KNOWN ABOUT IT, so its behaviour is not a surprise: it is INERT above
  # 3.4 -- the ladder from 3.4 to 30 moves every moment by under 0.05 per cent --
  # and its whole live window is roughly 2.4 to 3.0, where h_share5 swings from
  # 0.99 to 0.00. It limit-cycled there for a dozen iterations earlier, which is
  # what the sign-flip damping is for. ZERO IS NOT A VALUE, it is the switch into
  # the hold-at-65 branch; the bound floor of 1.0 in next_batch keeps the solver
  # away from it.
  #
  # WHY 2.867 -> 4.0 -> 8.0 WAS BIT-IDENTICAL, measured 5 September from base
  # point 43932f4d10 (delta=0, size_homelessness=0.45), two extra solves at
  # rr=1.0 (point_5fa805933c) and rr=1.5 (point_c718a182fa):
  #
  #     rr      age 65      66        67        68        70      b5 65+
  #     2.867   0.008454  0.000000  0.000000  0.000000  0.000000  0.0299
  #     1.0     0.000071  0.421641  0.494990  0.552101  0.638281  0.9740
  #     1.5     0.000071  0.421642  0.494979  0.552101  0.638281  0.9740
  #
  # THE PARAMETER IS AT A CORNER, not disconnected. At the calibrated value it
  # has ALREADY driven homelessness at 66+ to exactly zero, so raising it
  # further has nothing left to remove -- which is the whole of the inertness
  # above 3.4. Drop it and 66-70 goes from 0 to 42-64 per cent and the 65+
  # share goes 0.0299 -> 0.9740. The author's reading is confirmed: the death
  # penalty is what keeps the model's retirees off the street, NOT their
  # Social Security income. It also SATURATES at the low end -- 1.0 and 1.5
  # agree to six figures -- so the live region is between 1.5 and 2.867.
  #
  # AND THE ONE AGE IT CANNOT REACH IS THE ONE THAT MATTERS. Band 5 is
  # age_index 40-60, data ages 65-85 (see val_band_1 in the Fortran, ~17619).
  # rr_homeless_hold_age=65 replaces the profile ABOVE data age 65, i.e. 66+.
  # Every old homeless household in the model sits at exactly age 65 -- the
  # LAST WORKING YEAR, since retirement starts at life_span-retirement_span+1
  # = age_index 41 = data age 66 -- so the instrument acts on 66-85 while its
  # target population is entirely at 65. Setting rr_homeless_hold_age=64 makes
  # it bite: b5 0.0299 -> 0.0002 at the same rr, y_h 0.2614 -> 0.2458, h_1
  # barely moves. That is a config switch and it partitions the archive, so it
  # is the author's call.
  'h_share5': ('rr_homeless_old_level', 'raise', 'live window 2.4-3.0, inert above 3.4'),
  #
  # THE INCOME OF THE HOMELESS, from 4 September, on the author's instruction:
  # *"if you have an income too high for the homeless, you raise the probability
  # of losing your job if homeless, so regaining is lower too"*.
  #
  # The parameter is symmetric by construction -- job loss runs at
  # (1+increased_prob_if_homeless) times the housed rate and job finding at
  # (1-increased_prob_if_homeless) times it -- so one number sets both halves of
  # what the author described. Raising it makes the street costly for anyone with
  # a job to lose, which deters the middle-income households who currently make up
  # 99.4 per cent of the model's homeless, leaving the genuinely poor. So the
  # moment above target calls for a RISE.
  # y_h HAS NO INSTRUMENT, 4 September 21:40. It was assigned to
  # increased_prob_if_homeless on the author's ruling, and then MEASURED not to
  # work -- four brackets, all reported:
  #
  #   increased_prob_if_homeless 0.2 -> 0.95 (its whole range): y_h moved 0.8 per
  #     cent, because the parameter's two halves are a 1.3 point change in a small
  #     probability and a 52 point change in a large one, and the large one lands
  #     on households ALREADY unemployed. The SMI share of the homeless fell 59
  #     per cent instead.
  #   extra_job_loss_if_homeless, loss side alone, 10 per cent vs 20 per cent:
  #     every moment moved by under 0.01 per cent.
  #   consumption_penalty_homeless 0.1/0.3/0.6: abolishes homelessness by 0.3.
  #   size_homelessness 0.343 -> 0.45: y_h 0.720 -> 0.261, and the labour-market
  #     penalty on top of it contributes 0.001.
  #
  # So size_homelessness is what moves y_h, and it already owns h_1. One parameter
  # cannot bracket two moments, and which of them it should own is the author's
  # call, not a thing to guess overnight. Left unscored until they rule.
  #
  # increased_prob_if_homeless goes back to exogenous 0.2, which is the author's
  # instruction of 1 September and what it was before tonight.
  #
  # SUPERSEDED 21:50: y_h's instrument is homeless_job_penalty_pp, the author's
  # percentage-point form. *"the job loss chance is what we use to match the income
  # of the homeless... so if the chance went up 10 p.p., you reduce the chance of
  # regaining by 10 p.p. too (capped below at 0%)"*. One number moves both sides by
  # the same points, which is what makes it interpretable where the multiplier was
  # not. A homeless household with income above target is one that should be losing
  # work faster, so the moment above target calls for a RISE.
  # y_h HAS NO INSTRUMENT. homeless_job_penalty_pp was ruled onto it and then
  # MEASURED not to move it: delta 0.05 -> 0.30, which is job loss +25 percentage
  # points and job finding -25 points, changes every moment by under 0.006 per
  # cent. Both points applied 67 of 67 handover parameters, so the parameter
  # reaches the model and the model does not care.
  #
  # That is the FOURTH labour-market bracket with the same answer tonight, and the
  # reason looks structural rather than about magnitudes: the penalty acts on
  # transitions OUT of the homeless state. A household enters homelessness
  # employed, and the raised separation rate reaches it in the FOLLOWING period, by
  # which time it has re-chosen housing. No labour-market parameter can change the
  # composition of the current homeless STOCK, however large it is made -- which is
  # also why emp_homeless sits at 0.99 in every configuration tried today.
  #
  # What does move y_h is size_homelessness, measured: 0.343 -> 0.45 takes it from
  # 0.720 to 0.261. But that parameter already owns h_1, and one parameter cannot
  # bracket two moments. Which of them it should own is the author's call.
  #
  # RESTORED 5 September on the author's confirmation: *"We set delta to match the
  # average income of the homeless"*. THE MEASUREMENT ABOVE IS VOID -- it was taken
  # on the SYMMETRIC delta, which cut job finding as well as raising separation,
  # and the finding side is what deters the unemployed. Removing it entirely
  # (iph 0.2 -> 0) raises homelessness among the unemployed FIVE-FOLD, so the
  # symmetric version was pricing the poor off the street while we read it as
  # having no effect on their income. Delta now acts on separation alone.
  #
  # DIRECTION: income of the homeless ABOVE target means too many comfortable
  # households are choosing the street, so RAISE the separation penalty.
    'y_h': ('homeless_job_penalty_pp', 'raise',
            "the author's ruling; separation-only form, the symmetric bracket is void"),
    # pi_V, the share of eligible households receiving a housing voucher in the
    # benchmark, target 0.266. The author: *"lower if higher than data"*. Direct:
    # more voucher probability, more take-up. Measured 7-point ray agrees at slope
    # +1.717 and is monotone.
    'pi_V': ('probability_of_voucher_benchmark_used', 'lower', 'agrees'),
    # sud_homeless, the share of the homeless with a substance use disorder,
    # target 0.217. The author: *"lower if higher than data"*. M is the SUD
    # employment penalty on both margins -- job loss times M, job finding divided
    # by M -- so a harsher penalty puts more of the disordered on the street.
    #
    # THE INSTRUMENT IS DEAD AND THE RULE CANNOT BE ACTED ON. The model reads
    # 6.1e-07 against a target of 0.217: the homeless population has essentially
    # NO substance use disorder in it. The measured 8-point ray spans M from 1 to
    # 32, its whole bound range, and the slope is -1.2e-07 -- the moment does not
    # move at all.
    #
    # So a fixed-point update on this rule walks M to a bound while the moment
    # stays at zero, which looks like a stuck parameter and is actually a
    # structural problem: something prevents households with the disorder from
    # becoming homeless. Flagged to the author 4 September; it is not a
    # calibration failure to be adjusted away.
    'sud_homeless': ('multiple_of_probabilities_of_employment_if_addicted',
                     'lower', 'INSTRUMENT DEAD, slope -1.2e-07 over the whole range'),
    # emp_homeless, the employed share of the homeless, target 0.46.
    # The author: *"raise it if higher than data"*, so parameter and moment move in
    # OPPOSITE directions: raising the bottom productivity level lifts the poorest
    # types out of homelessness, leaving a homeless population that is less
    # employed rather than more.
    #
    # TWO PROBLEMS. Its current value 0.004 IS ITS LOWER BOUND, so it can only move
    # up -- which happens to be the ruled direction, but it means the rule can
    # never correct an undershoot. And the measured 7-point ray reverses at a
    # near-flat -0.0146; earlier the same day it moved pi_eu by exactly zero and
    # emp_homeless by two parts in a million.
    #
    # THE MODEL READS 0.938 AGAINST 0.46. Nearly every homeless household has a
    # job. With sud_homeless at 6.1e-07 this says the same thing twice: the model's
    # homeless are employed people without a disorder, close to the opposite of the
    # data, and no adjuster on these two instruments will fix that.
    'emp_homeless': ('bottom_productivity_level', 'raise',
                     'ray reverses and is near-flat; parameter sits ON its lower bound'),
    # lambda_m, the SMI share of the homeless, target 0.250.
    # The author: *"lower it if it is higher than the data... it would then have
    # fewer unemployed with SMI"*. kappa_uem is the SMI employment penalty on both
    # margins -- sep_1 = sep_1*kappa_uem and find_1 = find_1/kappa_uem -- so
    # lowering it keeps the mentally ill in work and off the street. Parameter and
    # moment move together.
    #
    # CORRECTION, and it was told to the author twice before being caught: this is
    # NOT a weak instrument. The fitted slope of +0.0071 is PER UNIT of kappa_uem,
    # which runs from 6 to 100, so 0.0071 * 94 is roughly the whole range. The ray:
    #
    #     kappa_uem   6.13 -> lambda_m 0.0149      39.43 -> 0.4012
    #                 9.76 -> 0.0845               49.05 -> 0.3743  (current)
    #                15.55 -> 0.1434               62.80 -> 0.5604
    #                24.76 -> 0.3961              100.00 -> 0.7115
    #
    # A 48-fold move in the moment. Reading a small per-unit slope as a weak handle
    # was the error; slopes have units.
    #
    # TWO THINGS THE RAY SHOWS THAT THE SLOPE HID. p_m barely moves across it,
    # 0.04458 to 0.04446, so kappa_uem changes WHICH mentally ill households end up
    # homeless without changing how many are ill -- exactly what this instrument
    # should do. And h_1 more than triples across the range, so it competes with
    # size_homelessness for the homelessness level.
    #
    # THE INSTRUMENT IS POINTED AT A MOMENT IT WAS NOT BUILT FOR. The Fortran
    # prints "MOMENT kappa_uem employment given SMI" -- the parameter is named for
    # the EMPLOYMENT RATE given SMI, not the SMI share of the homeless, and the
    # comment at line 290 flags the mismatch from the other direction. Worth
    # revisiting once the calibration is closer.
    'lambda_m': ('kappa_uem', 'lower', 'agrees, and the handle is strong'),
    # tau_u, treatment take-up among those with a substance use disorder,
    # target 0.245. The author: *"raise it if higher than the data"*.
    # utility_cost_of_treatment is what a household bears to enter treatment, so
    # costlier treatment means less of it -- parameter and moment move in OPPOSITE
    # directions. Measured 8-point ray agrees at slope -0.1082 and is monotone.
    #
    # SECOND-LARGEST GAP IN THE CALIBRATION at -38.7 per cent, behind pi_eu.
    'tau_u': ('utility_cost_of_treatment', 'raise', 'agrees'),
    # mu_H, recovery housed divided by recovery homeless, target 1.4732 --
    # Milby et al. (2005), 6.60/4.48 weeks abstinent.
    # The author: *"overshooting means you have to raise it"*. mu_homeless
    # multiplies the street's recovery hazard, so raising it brings street recovery
    # closer to housed recovery and the RATIO falls. Opposite directions, close to
    # a 1/mu relationship.
    #
    # THE CLEANEST INSTRUMENT IN THE TABLE. Its 8-point ray moves its own moment
    # nine-fold while b, lambda_d and h_1 do not budge past the fifth decimal:
    #
    #     mu_homeless 0.1139 -> mu_H 12.283      0.4847 -> 2.886
    #                 0.1636 ->      8.552       0.6962 -> 2.009
    #                 0.2349 ->      5.954       0.9110 -> 1.535  (current)
    #                 0.3375 ->      4.145       1.0000 -> 1.399
    #
    # The target sits between the last two rows, so the crossing is near
    # mu_homeless 0.94 -- a three per cent move. This moment is solvable in one step.
    #
    # A RESULT FOR THE PAPER, not just for the calibration: at mu_homeless = 1,
    # where the street carries NO recovery penalty at all, mu_H is still 1.399
    # rather than 1. The housed and homeless populations differ in composition, so
    # the model attributes part of Milby's measured gap to WHO ENDS UP WHERE rather
    # than to housing itself.
    'mu_H': ('mu_homeless', 'raise', 'agrees, cleanest ray in the table'),
}
