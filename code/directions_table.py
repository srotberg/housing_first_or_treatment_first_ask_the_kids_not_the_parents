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
    # gamma's INSTRUMENT MOVES FROM THE TASTE TO THE TOP RUNG, 5 September, on the
    # author's instruction: *"maybe we need to set h2, h3, h4 such that at
    # relativel_share_of_housing=0.268 the spending on houising is 26.8%?"*
    #
    # In Cobb-Douglas the housing expenditure share EQUALS the weight identically,
    # so relative_share_of_housing = 0.268 IS gamma's target and is now pinned as
    # data rather than searched. What made the two differ is the discrete ladder,
    # and the ladder is what gets calibrated.
    #
    # THE TASTE COULD NOT DO IT ANYWAY, measured over 226 archived points: sweeping
    # it 0.02 -> 0.60 carries gamma only 0.2239 -> 0.3323, a slope of 0.167 where a
    # continuous Cobb-Douglas gives 1.0. Both ends are corners of a three-rung
    # ladder -- the share in the largest unit is already 0.52 at 0.02 and 0.98 at
    # 0.60 -- so the moment saturates and the parameter is barely identified.
    #
    # DIRECTION. rung_ratio_h4 sets the top rung, where 60 per cent of renters
    # live, so it dominates aggregate housing expenditure: a bigger top rung means
    # more spent on housing and gamma rises. Parameter and moment move TOGETHER,
    # which is 'lower'. The archive's cleanest pair agrees, 2.5 -> 3.0 carrying
    # gamma 0.2046 -> 0.2291, and a one-coordinate bracket is being run to size it.
    # DIRECTION. h2 is the level of every rental rung and of the street, so
    # raising it raises housing outlay across the whole distribution and gamma
    # rises with it: parameter and moment move TOGETHER, which is 'lower'.
    # THE TWO HOUSING RUNGS, one moment each, on the author's instruction of
    # 5 September: *"is there a way to set h2 so that the share of spending over
    # 50% of their income on housing is like in the data? and choose h3 so that
    # at the housing spending is 26.8% at the chosen relative_share_of_housing of
    # 0.268?"*, and *"and h2 to match the share spending over 50% on housing"*.
    #
    # WHY TWO RUNGS AND NOT ONE. With a single rental, gamma and the cost-burden
    # share are both functions of h2 alone -- one instrument, two targets, no
    # solution. The second rung is the missing degree of freedom, and the two
    # moments load on different margins: the bottom rung decides who is priced
    # into paying over half their income, the top rung decides how much housing
    # the bulk of households buy and therefore the aggregate share.
    #
    # DIRECTION, gamma. rung_ratio_h3 is the top rung as a multiple of the bottom
    # one. Raising it means more housing bought where most households sit, so
    # gamma rises with it: parameter and moment move TOGETHER, which is 'lower'.
    # Measured on a fixed bottom rung, the ladder 1.5/2.0 -> 2.0/3.0 carried gamma
    # 0.3156 -> 0.3902.
    # gamma's INSTRUMENT IS THE ABSOLUTE TOP RUNG, not a ratio, from 5 September.
    # The author: *"adjust h2 down until it hits 17.5%. and adjust h3
    # independently of h2"*, and *"just adjust them independently"*.
    #
    # WHY THE RATIO COULD NOT DO IT. With h3 = rung_ratio_h3*h2 the two knobs were
    # MECHANICALLY chained: cutting the bottom rung cut the top rung with it, so
    # both moments fell together. Measured on three points, h2 delivered +3.04
    # burden50 per unit gamma and the ratio +4.12, while the target needed -0.57.
    # The 2x2 solve asked for a rung ratio of -0.50. Infeasible, and mechanical
    # rather than economic -- which is why unchaining them fixes it.
    #
    # largest_house_size was already assigned straight into
    # housing_size(housing_status_grid_size-1) and then overwritten by the ratio.
    # The overwrite now runs only from three rungs up, so at two rungs the ladder
    # is two independent absolute sizes.
    #
    # DIRECTION. A bigger top rung means more housing bought where most households
    # sit, so gamma rises with it: 'lower'.
    # h3 OWNS h_3, NOT gamma, from 5 September. The author: *"I think first you
    # need h3 to raise so that only 64% of renters are in the largest unit. And h2
    # needs to be such that 17.5% of renters spend over 50% on housing (and they
    # live in the smallest rental)"*.
    #
    # ONE MOVE DOES BOTH JOBS, which is why the ordering is theirs and not mine.
    # Raising h3 makes the top unit dearer, so fewer choose it and h_3 falls from
    # 0.99 toward 0.627 -- and the households it pushes out land in h2, where they
    # can be cost burdened. The crossover is measured: with h2 = 0.060 the cost of
    # downsizing grows as ratio**0.366 while the income it frees grows roughly
    # linearly, so they cross at a ratio near 4.5. Every ladder tested before this
    # was at or below 3.11, which is why burden50 looked immovable.
    #
    # DIRECTION. Raising h3 LOWERS the share sitting in it, so parameter and moment
    # move in opposite directions: 'raise'.
    # gamma GETS ITS INSTRUMENT BACK, 5 September. The author's full assignment:
    # *"Share of housing to match 26.8% spending on housing. H2 to get the share
    # spending over 50% on housing. H3 to match the share in the largest unit. And
    # h1 to match the share homeless. And delta to match the share to employed
    # homeless. And you also need to pick b and base addiction to match the share
    # users and Sud, and theta to match share spent on drugs by users."*
    #
    # relative_share_of_housing was PINNED at 0.268 as data earlier today, on the
    # reasoning that Cobb-Douglas makes the weight and the expenditure share the
    # same object. Measured, they are not: with the taste held at 0.268 gamma ran
    # 0.244 to 0.378 across ladder configurations, so the discreteness error is
    # large and gamma needs a handle of its own. It gets this one back.
    #
    # DIRECTION. A bigger weight on housing means more spent on it: parameter and
    # moment move together, which is 'lower'.
    'gamma': ('relative_share_of_housing', 'lower', 'un-pinned 5 Sept; discreteness error is large'),
    'h_3': ('largest_house_size', 'raise', 'crossover at ratio ~4.5, measured'),
    # gamma HAS NO INSTRUMENT while this holds, and that is stated rather than
    # hidden. With relative_share_of_housing pinned at 0.268 as data, h3 taken by
    # h_3 and h2 by burden50, nothing is left aimed at the aggregate housing share.
    # It read 0.268 to 0.280 across the working configurations, so it may simply
    # come out right; if it does not, it needs a fourth handle rather than one of
    # these three back.
    # 'gamma': ('largest_house_size', 'lower', 'independent of h2 from 5 Sept'),
    # DIRECTION, burden50. h2 is what the cheapest unit costs. Raising it prices
    # more households into paying over half their income for it, so the moment
    # rises with the parameter: 'lower' again. Measured on a fixed ladder,
    # h2 0.1243 -> 0.0710 carried burden50 0.719 -> 0.473.
    'burden50': ('smallest_rental_relative_to_lowest_income', 'lower', 'measured pair agrees'),
    # h_2, the CEX severe cost burden headcount, target 0.101, over half of
    # EXPENDITURE rather than income. Raising the cheapest rung prices more
    # households into paying over half for it, so parameter and moment move
    # together: 'lower'. Same sign as burden50, measured on the street scan.
    'h_2': ('smallest_rental_relative_to_lowest_income', 'lower', 'same sign as burden50, measured'),
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
  # lambda_d NOW BELONGS TO addiction_onset_base, not lambda_addiction. The
  # hazard is base + (1-exp(-lambda v)): the base sets the LEVEL of onset and
  # lambda sets how fast it RISES with quantity, so the level moment belongs to
  # the level parameter. Parameter and moment move together, so 'lower'.
  #
  # lambda_addiction is left without a moment on purpose. Its identifying moment
  # is the SUD rate BY USE INTENSITY -- NSDUH 2024 gives 0.134, 0.428, 0.577,
  # 0.717, 0.819 across the five frequency categories for hard drugs pooled --
  # and the model does not yet report a gradient to compare against. Until it
  # does, lambda has no scored moment and must not be handed one that is already
  # implied: the share of the SUD who are homeless is
  # P(SUD|homeless)*P(homeless)/P(SUD), an identity in three targets the
  # calibration already hits.
    # DIRECTION CORRECTED, 5 September, and it was measured the other way. The rule
    # said 'lower' -- parameter and moment moving together. A one-coordinate pair
    # says the opposite:
    #
    #     addiction_onset_base 0.0151 -> 0.018   (+19 per cent)
    #     lambda_d             0.0216 -> 0.0144  (-33 per cent)
    #     b                    0.1006 -> 0.0544  (-46 per cent)
    #
    # The base is the probability that using leads to the disorder, so raising it
    # makes using DANGEROUS and fewer people use. With fewer users there are fewer
    # disorders, and the deterrence swamps the mechanical effect. Parameter and
    # moment move in OPPOSITE directions, which is 'raise'.
    #
    # It cost two collapsed points before it was measured: raising the base and the
    # scalar together drove b to 8.9e-08 because BOTH lower participation. The
    # working pair is base UP for the disorder rate among users, scalar DOWN to pay
    # back the level on b.
    'lambda_d': ('addiction_onset_base', 'raise', 'measured pair: base +19% -> lambda_d -33%'),
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
    # h_2 HAS NO INSTRUMENT from 5 September. Its owner, the bottom rung, was
    # moved to gamma on the author's instruction; see next_batch.py. An
    # instrument that cannot reach its moment does not sit still, it runs, so the
    # moment is left unowned rather than pointed at a parameter that cannot move
    # it.
    # 'h_2': ('smallest_rental_relative_to_lowest_income', 'lower', 'agrees'),
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
  # h_share5's INSTRUMENT IS THE SSI FLOOR from 5 September, on the author's
  # instruction: *"i also want the bottom ssi to be set such that the old share
  # of homeless is 7.5%"*. 0.075 is already the target in the Fortran -- it is
  # val_hud_share_1(5), the HUD count's 65-and-over share -- so this changes the
  # instrument, not the number.
  #
  # rr_homeless_old_level cannot own it any more and is FROZEN in fixed_point.py:
  # at homeless_death_risk_flat_in_age=2, which run_one_point.sh now defaults to,
  # the mortality branch is 1+increased_risk_of_death_homeless at every age and
  # rr_homeless_profile is never read, so the level this parameter writes into
  # that profile's tail reaches nothing.
  #
  # THE SSI FLOOR IS THE RIGHT HANDLE ON ARITHMETIC. Band 5 is age_index 40 to 60,
  # data ages 65 to 85 -- exactly the retired -- and the SSI floor is retirement
  # income and nothing else, so it acts on band 5's budget and on no other band's.
  # It is also live now in a way it was not before: the floor sits inside
  # `if (use_pia_formula==1)` and the vectors that made it unreachable carried
  # use_pia_formula=0. Every current vector carries 1.
  #
  # DIRECTION. A higher floor buys retirement income, so fewer of the old are
  # priced out of the cheapest rental and band 5's share falls: parameter and
  # moment move in OPPOSITE directions, which is 'raise'. The Fortran's own note
  # says the same -- "at 1 nobody is priced out of the cheapest rental in
  # retirement and band 5 homelessness goes to about nothing; at 0 the floor is
  # absent and 6.6 per cent of the population is priced out on the PIA alone".
  #
  # THE MEASURED RAY IS STALE AND SAYS SO. The bracket recorded in next_batch.py
  # -- h_share5 0.935 at a floor of 0.1774 and 0.518 at 0.60 -- agrees on sign but
  # was measured under mode 0 mortality and rr_homeless_hold_age=65. At the SAME
  # floor of 0.1774 today the model gives h_share5 = 2.2e-06. The floor's handle
  # in THIS economy is unmeasured, and a bracket is being run rather than assumed.
  'h_share5': ('ssi_floor_level', 'raise', 'sign agrees; magnitude stale, bracket pending'),
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
  # THE RULING AND THE MEASUREMENT DISAGREE, recorded 5 September 03:45 rather
  # than resolved silently, which is this table's convention.
  #
  # Six points identical in every coordinate except delta:
  #
  #     delta   tag              y_h        h_1    band1    band5
  #      0.00   43932f4d10    0.2614   0.004651   0.9080   0.0299
  #      0.05   2c40bae9b4    0.7105   0.002457   0.0120   0.0529
  #      0.15   a43cb9b416    0.7362   0.000299   0.1235   0.4465
  #      0.25   b24474cff8    0.7242   0.000153   0.0627   0.9354
  #      0.30   f56a40b55d    0.6892   0.000184   0.2003   0.7759
  #      0.55   59a64035ad    0.7250   0.000152   0.0603   0.9397
  #                  target   0.1910   0.003990            0.0750
  #
  # y_h RISES with delta and its minimum over the ray is at delta = 0. Under
  # 'raise' the rule walks delta up and the gap climbs with it -- measured live,
  # +250.7 -> +289.0 -> +290.6 -> +292.5 per cent over four iterations while
  # delta went 0.25 -> 0.366 toward its bound of 0.60.
  #
  # SO DELTA IS ONE-SIDED AT ITS FLOOR for y_h, not an instrument for it, and the
  # reason is mechanical: delta removes WORKERS from the street (band 1 falls
  # 0.908 -> 0.012 on the first step), the retirees left behind are 90+ per cent
  # of the homeless, and their Social Security income is what y_h then measures.
  # rr_homeless_old_level cannot remove them because rr_homeless_hold_age=65 puts
  # the death penalty on ages 66 AND UP while the model's old homeless sit at
  # age 65, the last working year.
  #
  # The author's design -- *"the death penalty for the old will remove the old
  # from being homeless...and delta will remove the workers"* -- is coherent and
  # needs BOTH halves. Only one can currently act. Delta becomes an instrument
  # for y_h if and only if rr can reach age 65, which is rr_homeless_hold_age
  # 65 -> 64. Left as the author's call; the ruling below is UNCHANGED until they
  # rule, per this table's convention that a ruling is the authority.
  # FLIPPED TO 'lower' AND REVERTED THE SAME HOUR. The flip was made on the
  # measured ray plus *"0.366 is too high"*; the author corrected it at once --
  # *"no...delta is moving in the wrong direction!"* -- and 'raise' is restored.
  #
  # THE RULING IS THE AUTHORITY AND THE MEASUREMENT IS A CHECK. That is this
  # table's own convention, stated at the top, and the flip broke it: a
  # disagreement gets RECORDED, which it already was in the block above, not
  # resolved in favour of the ray overnight. The ray is not thereby wrong -- y_h
  # still rises with delta over every point measured -- and the reason it can be
  # right while the ruling stands is in that block: delta cannot lower y_h while
  # rr_homeless_hold_age=65 leaves the age-65 homeless beyond the death penalty's
  # reach, so the ray measures a mechanism with one half disabled.
    # y_h HAS NO INSTRUMENT, 5 September. homeless_job_penalty_pp has been moved
    # to emp_homeless, which it demonstrably brackets, and y_h is left unscored by
    # any parameter rather than given one that does not move it. The measured ray
    # in the block above already said delta cannot lower y_h: y_h RISES with delta
    # over every point on it and its minimum is at delta = 0.
    # SUPERSEDED, kept as a comment rather than a dead dict key:
    # '_y_h_superseded': ('homeless_job_penalty_pp', 'raise',
    #         "the author's ruling, restored; see the measured-ray block above"),
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
  # sud_homeless GOES TO lambda_addiction, 5 September, on the author's scheme:
  # *"the base is chosen to match the SUD rate and lambda the share of homeless
  # with SUD, M is fixed at 4 now since we dont need it as a target anymore"*.
  #
  # In base + (1-exp(-lambda v)) the base sets the LEVEL of onset and lambda sets
  # how fast it rises with QUANTITY. A higher lambda means the disordered are
  # selected from heavier users, who spend more and hold less, so more of them
  # end up on the street. Parameter and moment move together, so 'lower'.
  #
  # M IS OUT, and it was never in: measured over 69 archive pairs differing ONLY
  # in M, sud_homeless is 0.000010 at M=1, 0.000003 at M=4 and 0.000002 at M=32,
  # while b collapses 0.234 -> 0.004 across the same range. M deters the choice
  # to use and is no handle at all on who is homeless. It is frozen at 4.
  #
  # AND THIS IS NOT THE IDENTITY THAT WAS REJECTED. P(homeless|SUD) is
  # P(SUD|homeless)*P(homeless)/P(SUD), implied by three moments already
  # targeted, so adding it would carry no information. sud_homeless is
  # P(SUD|homeless) itself, the composition of the homeless, and is not implied
  # by h_1 and lambda_d.
  # DIRECTION IS 'raise', on the author's own reasoning, 5 September: *"if the
  # SUD homeless is high, you need to raise lambda, because this makes them use
  # less, and raises theta, which brings more high wealth people"*.
  #
  # A higher lambda makes each unit of the drug riskier, so users cut quantity;
  # the marginal risk term lambda*exp(-lambda*v)*(EV_clean - EV_disorder) in the
  # drug first-order condition is what does it. Cutting quantity per user raises
  # the spending share needed to sustain use and pulls the user population toward
  # households with more wealth, who are the ones who can bear it -- and they are
  # not the ones who end up on the street. So the SUD share of the homeless
  # FALLS as lambda rises: parameter and moment move in OPPOSITE directions.
  #
  # This reverses the first wiring, which had 'lower' on the opposite mechanism
  # -- that a higher lambda selects the disordered from heavier and therefore
  # poorer users. The author's is the ruling.
  # AND IT WORKS THROUGH GENERAL EQUILIBRIUM, the author, 5 September: *"lambda
  # works through GE here"*. Lambda does not move sud_homeless directly. It moves
  # quantity per user, which moves who finds using worthwhile, which moves the
  # wealth distribution of users, which moves who ends up on the street. A fixed
  # direction can therefore be right locally and wrong further along that chain,
  # which is what the sign-flip damping is for; and a measured elasticity from
  # archive pairs is a valid reading of a full GE solve but will not be constant
  # across the space.
    'sud_homeless': ('lambda_addiction', 'raise',
                     "the author's ruling; works through GE, so the sign is local"),
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
    # emp_homeless's INSTRUMENT IS delta, 5 September, on the author's reading:
    # *"maybe we need to set the bottom productivity exogenously, and set delta to
    # match the emp_homeless?"*, *"before when delta was high, emp_homeless was
    # very low"*, *"now it is very high"*.
    #
    # MEASURED ON THE LIVE MODEL, ONE COORDINATE APART, and it brackets the target:
    #
    #     point         delta   emp_homeless   h_1        y_h
    #     cd3ee03441    1       0.0473         0.000848   0.4475
    #     43bbce4f05    0       0.9965         0.2390     0.7188
    #     target                0.4600         0.00399    0.1910
    #
    # 0.46 is strictly inside [0.0473, 0.9965], which no other labour-market
    # parameter has managed. bottom_productivity_level was ruled onto this moment
    # and MEASURED not to move it -- the 7-point ray reverses at a near-flat
    # -0.0146 and on an earlier day it moved emp_homeless by two parts in a
    # million -- so it goes exogenous, which is the other half of the author's
    # instruction.
    #
    # DIRECTION 'raise': emp_homeless above the data means too many of the
    # homeless are working, so raise the job penalty. Parameter and moment move in
    # OPPOSITE directions, as the bracket shows.
    #
    # THE LIVE RANGE IS [0, 0.55], NOT [0, 1]. find_mult = max(0,(p_find-delta)/
    # p_find) with probability_becoming_employed = 0.55, so job finding is EXACTLY
    # ZERO at and above 0.55 and delta only raises separations after that. That
    # dead ground above 0.55 is where the walk ran to when this parameter was
    # pointed at y_h.
    'emp_homeless': ('homeless_job_penalty_pp', 'raise',
                     'measured bracket: delta 0 -> 0.9965, delta 1 -> 0.0473, '
                     'target 0.46 strictly inside; live range [0, 0.55]'),
    # SUPERSEDED, kept as a comment rather than a dead dict key:
    # '_emp_homeless_superseded': ('bottom_productivity_level', 'raise',
    #                  'ray reverses and is near-flat; parameter sits ON its lower bound'),
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
  # kappa_uem NOW OWNS ITS OWN MOMENT, the employment rate given SMI, target
  # 0.30 (employment_rate_given_smi_data, line 1250). The author, 5 September:
  # *"we need to set the unemployment rate of those with SMI to 30%"*.
  #
  # IT DOES NOT DRIVE lambda_m WHERE THE STREET IS REAL. Measured over 56 archive
  # pairs differing ONLY in kappa_uem, split on the homelessness rate:
  #
  #     h_1 far below target (<0.0030)   n=41   elasticity +0.82   73% ruled sign
  #     h_1 realistic        (>=0.0030)  n=15   elasticity -0.07   47% ruled sign
  #
  # The 48-fold ray that made it look like a strong handle -- lambda_m 0.015 at
  # kappa_uem 6.1 to 0.712 at 100 -- runs entirely through h_1 = 0.0007 to
  # 0.0025, the degenerate region where almost nobody is homeless and the
  # composition moves with the level. Where h_1 is realistic the instrument is
  # inert and its sign is a coin flip. The old note here, "agrees, and the handle
  # is strong", was read off that ray and is withdrawn.
  #
  # The parameter is the SMI employment penalty, sep*kappa and find/kappa, so a
  # higher kappa LOWERS employment: parameter and moment move in opposite
  # directions, hence 'raise'.
    'kappa_uem': ('kappa_uem', 'raise',
                         "the SMI employment rate, the moment the parameter is named for"),
  # lambda_m, the SMI share of the homeless, HAS NO INSTRUMENT. It becomes an
  # outcome of the SMI employment rate and the housing choice, in the same way
  # sud_homeless and emp_homeless now are. Nothing measured tonight moves it in
  # the region that matters.

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
