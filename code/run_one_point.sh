#!/usr/bin/env bash
# Run ONE model point at an ARBITRARY parameter vector and record its moments.
#
#   bash code/run_one_point.sh name=value name=value ...
#
# Any name the Fortran's PARAM_HANDOVER select case knows may be given; anything
# not given keeps the default below. Example:
#
#   bash code/run_one_point.sh addiction_scalar_1=0.005 value_of_life=31 \
#                              lambda_addiction=2.2 size_homelessness=0.5
#
# WHY key=value AND NOT POSITIONAL. The first version took b and aleph and three
# optional extras, which meant a secant could only ever be taken on those five.
# Twenty four parameters are calibrated, every one of them owns a moment, and a
# search that can only move five of them is not a search of the space. Naming
# them makes every parameter a candidate and costs nothing.
#
# gamma is NOT settable: it is tied to theta inside the model as 0.28*(1-theta),
# and setting it by hand breaks the tie.
#
# The point file records the vector on a VECTOR line, machine readable, so the
# coordinator reads what was actually run rather than parsing a filename.
set -euo pipefail
cd "$(dirname "$0")"

# THE DEFAULTS ARE THE CENTRE OF THE CURRENT GENERATION, so an arm of the search
# is one name=value pair and nothing else, and every arm is a matched pair with
# the centre. b and the value of life are where the users ridge and the value of
# life ridge cross (code/ridge_solve.py); the rest is the vector generation one
# held fixed.
declare -A P=(
    [addiction_scalar_1]=0.0224532
    # A FREE SCALE ON NEWBORN WEALTH, calibrated on the newborn homelessness
    # rate. Every newborn receives newborn_endowment_scale x average labour
    # income; 1.0 is one year's average earnings.
    # THE RENTAL LADDER: h_3 = rung_ratio_h3 x h_2, h_4 = rung_ratio_h4 x h_2.
    # 2 and 3 are what the author specified; they are settable so a different
    # ladder costs a vector change rather than a model hash.
    # 1.5 AND 2.0 ON THE AUTHOR'S INSTRUCTION, 1 September: "i wonder, maybe h3
    # has to be 50% larger than h2 and h4 double h2" and then "I think you have
    # to shift h2 to be around 0.165....and then h3 to be 50% higher and h4 to be
    # double". The defaults were left at the old 2.0 and 3.0 for a full day, so
    # any batch built from a base that did not carry them explicitly silently ran
    # the old ladder. Found in the parameter audit of 2 September.
    [rung_ratio_h3]=2.0
    [rung_ratio_h4]=3.0
    # OFF, on the author's instruction of 2 September: "Dont even target
    # anything for newborns with the endowment for now. Let's see if you can
    # match the bottom 50% share of wealth." It handed every newborn
    # newborn_endowment_scale times one year of average earnings, and four
    # controlled arms show it inflating w_bot -- 1.25 gives 0.105, 1.6 gives
    # 0.121 -- which is the moment the author is now trying to reach.
    [newborn_endowment_scale]=0.0
    # UNSECURED BORROWING, on the author's instruction of 2 September. The
    # negative grid already existed for mortgages and was unreachable for
    # renters, so with include_homeownership=0 nobody could owe anything. The
    # limit is in years of average labour income; the rate is charged on a
    # negative balance against a risk-free 0.03 and is expected to be revisited,
    # because the 5.5 per cent the author named was a debt-to-income quantity
    # rather than a rate.
    [include_unsecured_borrowing]=0
    [unsecured_borrowing_limit]=0.30
    [unsecured_borrowing_rate]=0.055
    [restrict_borrowing_to_impatient]=1
    # THE CURVATURE OF THE POSITIVE ASSET GRID. grid(i)=top*((i-61)/24)**e, so a
    # bigger exponent pushes the rungs toward zero. At the inherited 1.5 there
    # was ONE grid point between zero wealth and a year's rent on the cheapest
    # unit; at 3.0 there are five. The author asked for "around 2 or 3 in
    # general". The cost is at the top, where the last gap widens from 0.611 to
    # 1.184 and mass had already been found piling against the edge.
    [financial_grid_expander_positive]=3.0
    [financial_grid_expander_negative]=1.0
    [value_of_life]=35.1001
    # ZERO, on the author's instruction of 5 September: *"remove lambda
    # completely for now. Set it to 0 and fix it."* At zero the onset hazard
    # base+(1-exp(-lambda*v)) collapses to the flat base at every quantity.
    # The 5.0554 this replaces predates the two-part hazard.
    [lambda_addiction]=0
    [relative_share_of_addiction_1]=0.530445
    # AN ABSOLUTE SIZE FROM 5 September, not a ratio of the bottom rung. The
    # author: "you should disentangle the homeless size from the smallest rental.
    # it should be free to move alone".
    #
    # 0.048 is 0.40 of a bottom rung of 0.12, which is where h_1 = 0.399 per cent
    # interpolates on the measured street bracket: at h2 = 0.12 a ratio of 0.30
    # gave h_1 = 0.000548 and 0.5757 gave 0.0575, an elasticity of 7.14.
    #
    # EVERY OLD VECTOR CARRIES 0.5757 AND THAT IS NOW AN ABSOLUTE SIZE larger than
    # both rungs, which would inverting the ladder silently. The guard below
    # refuses it.
    [size_homelessness]=0.048
    [discount_factor]=0.993881
    [relative_share_of_leisure]=2.76316
    [labor_income_tax_rate]=0.720039
    [sd_permanent_productivity]=0.953392
    [kappa_uem]=1.01931
    # kappa_find_smi splits SMI's job-finding penalty off kappa_uem's separation
    # penalty. At 1.0 finding is unpenalised; the old economy is kappa_find_smi
    # equal to kappa_uem.
    [kappa_find_smi]=1.0
    # multiple_find_if_addicted splits the disorder's job-finding penalty off the
    # separation penalty the employment multiplier carries, exactly as
    # kappa_find_smi does for SMI. At 1.0 finding is unpenalised; the old economy
    # is multiple_find_if_addicted equal to the multiplier.
    [multiple_find_if_addicted]=1.0
    [lambda_m]=0.067
    [zeta_DI]=0.0
    [smi_onset_level]=0.003306
    [multiple_of_probabilities_of_employment_if_addicted]=2.43741
    [penalty_child_addicted]=0.24
    [penalty_child_homeless]=0.31
    [probability_becoming_unemployed]=0.0294178
    [probability_of_voucher_benchmark_used]=0.0121367
    # ONE DISCOUNT FACTOR BY DEFAULT. Two is reachable by passing 2 here, but
    # the two-pass path does not yet reproduce the one-pass economy at equal
    # betas, so anything measured at 2 is provisional.
    # THE FLAT EXCESS DEATH RISK FROM THE STREET, per period. Default is
    # Baggett's implied excess at age 26, so only the age gradient is removed.
    # 0 Baggett ratios, 1 flat excess risk, 2 flat 1.6 multiplier.
    # THE STREET'S DEATH PENALTY IS A FLAT 1.6 AT EVERY AGE, on the author's
    # instruction of 5 September: *"maybe the death rate is too high....try 60%
    # uniform death rate across everyone"*. Setting 2 is that setting: it bypasses
    # rr_homeless_profile entirely and uses 1+increased_risk_of_death_homeless,
    # which is fixed at 0.6 in the Fortran (Meyer, Wyse and Logani).
    #
    # WHAT SETTING 0 WAS CHARGING. Baggett's ratio over the SUD term, measured at
    # point a1a0bf3fe6: 7.99 at data age 26, 7.89 at 35, 5.87 at 45, 3.88 at 55 and
    # 5.19 above 64. An eightfold death hazard on a twenty six year old sleeping
    # rough, against value_of_life 45. That is what made size_homelessness inert:
    # the street's size moves the HOUSING term and never the MORTALITY term.
    #
    # MEASURED IN ISOLATION, one coordinate, model 375aed92cf:
    #
    #                    mode 0      mode 2      target
    #   h_1              0.000149    0.000543    0.00399
    #   lambda_m         0.884       0.342       0.25
    #   band 5 rate      8.7e-3      0.0         7.7e-4
    #
    # and the street becomes an instrument again: under mode 2, 0.10 -> 0.494 takes
    # h_1 from 0.000165 to 0.000543, an elasticity of 0.745, where under mode 0 it
    # did not move across the same range.
    #
    # rr_homeless_old_level IS INERT AT THIS SETTING and is frozen in fixed_point.py.
    [homeless_death_risk_flat_in_age]=2
    [homeless_excess_death_risk]=0.00396
    # ONE TYPE AGAIN, on the author's instruction of 1 September: "Maybe we don't
    # even need the two betas. Go back having just one. I think we don't need the
    # second anymore since we have other things that pin down the homelessness of
    # the newborns, and the unemployment of the homeless."
    #
    # The second type existed to move w_bot, the wealth share of the bottom half,
    # and the measurement is what killed it: closing w_bot needs an impatient
    # discount factor near 0.27, a 270 per cent annual discount rate, and even at
    # the search bound of 0.50 the moment only reaches 0.053 against a target of
    # 0.025. A parameter that has to be absurd to work is not an instrument.
    #
    # It is a runtime value with a handover case, so this costs no model change
    # and the archive stays scoreable.
    # ONE TYPE, on the author's instruction of 3 September: *"Yes, totally ok for
    # the bottom 50% the have less than 2.5% of wealth. Just use one beta!"*
    #
    # It halves the solve. The distribution is accumulated once per beta type --
    # DIAG pooled mass reads 101.87 at two types against 51.42 at one -- and a
    # solve was measured at 5 minutes 0 seconds with two.
    #
    # WHAT IT DOES TO w_bot IS THE OPPOSITE OF WHAT WAS FEARED, and the author's
    # concession is aimed the wrong way round. With two types the impatient half
    # holds almost nothing and drags the bottom half's share DOWN; removing them
    # raises it. Measured at one type: 0.03203 at discount_factor 0.965 and
    # 0.05032 at 0.99980, both ABOVE the 0.025 target. The 0.00883 that prompted
    # the worry came from point_6f1372662f, where both factors are 0.95 -- the
    # impatient type is present and identical there, not absent, so that point
    # says nothing about running one type.
    #
    # discount_factor_impatient and restrict_borrowing_to_impatient are inert
    # from here. They stay in the vector so every point records what it ran.
    [number_of_beta_types]=1
    [utility_cost_of_treatment]=0.0908753
    # THE PRICE OF TREATMENT, HELD AT ZERO. It replaced the utility cost on 31
    # August and was switched back the same day on the author's instruction, so
    # treatment is charged in utility again and not on resources.
    [money_cost_of_treatment]=0
    [smallest_rental_relative_to_lowest_income]=0.0244763
    # THE ABSOLUTE TOP RUNG, and gamma's instrument from 5 September. Seeded at
    # 1.5 times the bottom rung's current value, which is what the author asked
    # for: *"set h3 to whatever it is at 1.5 currently"*. It is a level now, not
    # a multiple, so it does not move when h2 moves.
    [largest_house_size]=0.1863876
    [weight_on_child]=0.007
    [max_food_cost]=0.00498294
    [mu_homeless]=0.708003
    # THE TWO THAT MADE A POINT UNDER-SPECIFIED. Both are internally calibrated,
    # both are handover cases the model has accepted all along, and neither was
    # in the vector, so their values rode in on whatever calibration_state.dat
    # the container carried -- which is bug two of REPRODUCIBILITY_INVESTIGATION.
    # relative_share_of_housing owns gamma and is searched; the grid expander's
    # adjuster is declared zero, so it is pinned here at its declared value and
    # every point now states it explicitly.
    # PINNED AT THE DATA EXPENDITURE SHARE, 5 September, on the author's
    # instruction: *"maybe we need to set h2, h3, h4 such that at
    # relativel_share_of_housing=0.268 the spending on houising is 26.8%?"*
    #
    # In Cobb-Douglas the housing expenditure share EQUALS this weight
    # identically -- w_h/(w_h+w_c) = gamma_h for any prices -- so 0.268 is not a
    # free dial, it is the same number as gamma's target. Calibrating it to hit
    # gamma was calibrating a parameter to equal a moment it already equals in
    # theory, and the only reason the two ever differed is that the discrete
    # housing ladder forces expenditure the household would not choose. The
    # LADDER is what gets calibrated now; this is data.
    [relative_share_of_housing]=0.268
    [housing_status_grid_expander]=1.0
    # THE SUD MORTALITY LEVEL, ADDED 30 AUGUST. It was settable in the Fortran
    # and not handable, so every point so far solved at its declared 8.0 --
    # which is why 8.0 is the default here and why next_batch.py fills it in
    # for a point whose VECTOR line predates it. Adding a name changes the md5
    # of every future vector, so a point measured before today will not be
    # recognised as already measured and will re-run once if it is asked for.
    # That is the price of the name, and it is paid once.
    [kappa_phi_d_level]=8.0
    # OPENED ON THE AUTHOR'S INSTRUCTION, both previously compile-time constants.
    # increased_prob_if_homeless is the labour market cost of the street and the
    # instrument for the employed share of the homeless; rho_d is the earnings
    # penalty of a substance use disorder and the instrument for the SUD share of
    # them. Their defaults are the values they were assigned at.
    # ZERO ON THE AUTHOR'S INSTRUCTION, 6 September: *"I only want delta to be
    # adjusted to match the share of homelessness employed... I don't want that
    # 20% penalty on top"*. It penalised the homeless on BOTH margins --
    # separation up by iph and job finding down by iph -- which left
    # homeless_job_penalty_pp sharing emp_homeless with a second, symmetric
    # penalty. delta now stands alone on that moment.
    # ZERO ON THE AUTHOR'S INSTRUCTION, 6 September: *"I only want delta to be
    # adjusted to match the share of homelessness employed... I don't want that
    # 20% penalty on top"*. It penalised the homeless on BOTH margins --
    # separation up by iph, job finding down by iph -- so homeless_job_penalty_pp
    # shared emp_homeless with a second, symmetric penalty. delta stands alone
    # on that moment now.
    # ON AT 0.20 AND EXOGENOUS SINCE 6 September, on the author's instruction:
    # *"Set delta=0. And recalibrate based on the 20% penalty when homeless being
    # exogenous"*, and *"add the 20% higher chance of unemployment and 20% higher
    # chance of not regaining employment as well"*. With delta at zero the
    # multiplicative branch runs and applies BOTH halves: job loss x1.20, job
    # finding x0.80. It is not calibrated -- it is a statement about the world.
    [increased_prob_if_homeless]=0.2
    # THE NON-HOUSING CONSUMPTION PENALTY OF THE STREET. Zero reproduces the
    # model exactly; it owns y_h, the income of the homeless. See its declaration
    # in the Fortran for why the employment-transition instruments cannot reach
    # that moment.
    [consumption_penalty_homeless]=0
    # THE EXTRA JOB-LOSS MULTIPLIER OF THE STREET, loss side only. Zero
    # reproduces the model exactly; it owns emp_homeless, the employed share of
    # the homeless, 0.46 in the data against 0.99 here.
    [extra_job_loss_if_homeless]=0
    # THE STREET'S LABOUR-MARKET PENALTY IN PERCENTAGE POINTS. Zero reproduces
    # the model exactly and leaves increased_prob_if_homeless in charge; positive
    # overrides both sides with lose+delta and find-delta. Owns y_h.
    # 0.001 ON THE AUTHOR'S INSTRUCTION, 5 September: *"set delta=0.001 and allow
    # it to adjust after b and base are correct"*. It is FROZEN in fixed_point.py
    # until then.
    #
    # It had been driven to 0.19945, which on a baseline separation probability of
    # 0.0046844 is 20.41 per cent a year homeless against 0.47 housed, a 43.6-fold
    # hazard. The declaration is 0.d0 and the Fortran's own note says "DELTA ZERO
    # REPRODUCES THE MODEL EXACTLY", so the author's original paper ran without it.
    # 0.001 rather than 0 keeps the percentage-point branch live, so releasing it
    # later is a step and not a regime change.
    # ZERO SINCE 6 September: *"Set delta=0"*. The 0.001 above was chosen to keep
    # the percentage-point branch live, and that turned out to be the problem
    # rather than the safeguard -- ANY positive delta sets find_mult_homeless to
    # exactly one, so it silently switched off the job-finding half of the
    # penalty. At zero the multiplicative branch runs and both halves apply.
    [homeless_job_penalty_pp]=0
    # THE BOTTOM OF THE PRODUCTIVITY GRID, two instruments for the two moments
    # that say who the homeless are: the employed share (0.46) and their income
    # (0.191 of average). y_grid_kappa sets the bottom node's mass, exactly
    # (1/employment_grid_size)**y_grid_kappa, which at seven nodes and 3.2 is
    # 0.198 per cent. bottom_productivity_level overrides its level as a multiple
    # of mean productivity; 0 leaves the quantile construction alone and is the
    # default. See the block beside employment_grid_size in the Fortran.
    [y_grid_kappa]=3.2
    # SOCIAL SECURITY, now the US statute. use_pia_formula=1 gives the SSA 2024
    # 90/32/15 bend-point schedule; 0 restores the flat 0.40 x productivity that
    # was regressive against the net wage. ssi_floor_takeup is the DIAL for how
    # many of the old are priced out of the cheapest rental: 0 leaves 6.6 per
    # cent of the population priced out on the PIA alone, 1 leaves none.
    # THE NEWBORN ENDOWMENT IS A TRANSFER, not a stock. At 1 the newborn enters
    # at the financial grid's zero index and receives the endowment as cash on
    # hand in its first period, so only what it CHOOSES to save is measured
    # wealth. At 0 it is placed on the grid point nearest the endowment and the
    # full amount counts as wealth before any decision, which is what inflated
    # w_bot and got newborn_endowment_scale parked on 2 September.
    [endowment_is_a_transfer]=1
    # PERSISTENT INCOME RISK over working life, discretised onto the SAME
    # quantile grid so y_grid_kappa, the bottom node and the stationary
    # dispersion all survive -- which fixed_productivity=0 would not do, since it
    # abandons the quantile construction for KKK_process. rho_productivity is the
    # persistence; the innovation is pinned by it and sd_permanent_productivity,
    # so there is nothing else to set. 0.98 gives 0.9651*sqrt(1-0.98^2)=0.1921.
    [persistent_income_risk]=0
    [rho_productivity]=0.98
    # THE PRODUCTIVITY PROCESS ITSELF, on the author's instruction of 3
    # September: "yes, switch to my process and use it". 1 is the quantile grid
    # built from y_grid_kappa and sd_permanent_productivity, frozen over the life
    # cycle. 0 is the author's own KKK_process: a two component process -- a
    # fixed effect with persistence 0.5 and innovation sd 0.309, and a persistent
    # component with persistence 0.9 and innovation sd 0.2 -- collapsed onto ONE
    # grid whose WIDTH grows with age. That is the fanning out: the same node
    # index is a wider deviation from the mean at fifty than at twenty six, so
    # within cohort inequality grows over the life cycle.
    #
    # NOTHING IS SHARED BETWEEN THE TWO. y_grid_kappa, bottom_productivity_level
    # and sd_permanent_productivity are inert under KKK; the four process numbers
    # and kkk_s_deviation_bottom are inert under the quantile grid. A point is
    # therefore run at one or the other, never at a blend.
    # STOCHASTIC, ON THE AUTHOR'S INSTRUCTION OF 3 SEPTEMBER: "Flip it to
    # stochastic and calibrate everything there."
    #
    # Their argument, and it is the right one. The macro block was never finished
    # on the frozen grid -- one of its nine moments was inside ten per cent -- and
    # every one of those moments is a different number once productivity varies
    # over the life cycle. pi_eu is the unemployment rate; w_bot and beta are
    # wealth aggregates that a fanning income process moves through the savings
    # motive; sigma_y is DEFINED on the productivity grid and changes instrument
    # from sd_permanent_productivity to kkk_sigma_scale. Calibrating them at
    # fixed_productivity=1 was work that would have to be done again.
    #
    # WHAT THIS COSTS: the archive has no point in this economy. All 666 carry
    # fixed_productivity=1, so the gate has nothing to interpolate from and
    # ENGINE.md's step 2 applies -- SEED, with an anchor at the best known
    # vector, rather than trust a batch written from nothing.
    [fixed_productivity]=0
    # THE KKK GRID'S BOTTOM WIDTH, which is what y_grid_kappa is on the quantile
    # grid: the instrument for the mass poor enough to be priced out of the
    # cheapest rental. 3.00 puts 0.621 per cent on the bottom node, 3.25 gives
    # 0.318, 3.50 gives 0.155, against a design target of 0.198 from the
    # homelessness bands. 3.35 puts 0.2395 there, which is the closest to what
    # y_grid_kappa=3.2 delivered on the quantile grid; 3.0 is a grid width rather
    # than a calibrated choice.
    [kkk_s_deviation_bottom]=3.35
    [kkk_s_deviation_top]=3.0
    # THE FOUR NUMBERS OF THE PROCESS, at the author's own values. Settable
    # because the dispersion they deliver is not the dispersion sigma_y is
    # calibrated to -- see KKK_VS_SIGMA_Y.md -- not because anything says they
    # should be moved without a reason.
    [persistence_fixed_employment_newborn]=0.5
    [sd_fixed_employment_newborn]=0.309
    [persistence_employment_surviving]=0.9
    [sd_employment_surviving]=0.2
    # THE COMMON SCALE OF THE TWO INNOVATION SDS, calibrated inside the model
    # against the bottom half's share of earnings, on the author's instruction of
    # 3 September: "Ok, you can calibrate sigma then". It multiplies BOTH sds, so
    # the ratio between them -- which is what decides how much of the dispersion
    # is a birth endowment and how much accumulates with age, the fanning out --
    # is untouched. 1.0 is the published GKOS numbers; about 2.2 is what puts the
    # bottom half share on the SCF's 17.2 per cent. Setting it here pins the
    # starting value; the internal loop moves it from there.
    #
    # NOTE the equivalence: kkk_sigma_scale=2.20949 and the two sds at their
    # defaults is the SAME economy as sd_fixed_employment_newborn=0.68273 with
    # sd_employment_surviving=0.44190 and the scale at 1. Set one or the other,
    # never both, or the scaling is applied twice.
    #
    # 2.20949 AND NOT 1.0, now that the process is live. At the published sds the
    # bottom half holds 33 per cent of earnings against 17.2 in the SCF and the
    # poorest household earns 0.232 of mean productivity -- rich enough to pay
    # the cheapest rent out of income, so that economy cannot produce
    # homelessness at all. This is a starting value from closed-form arithmetic
    # rather than a calibrated one; kkk_sigma_scale IS sigma_y's instrument under
    # KKK and next_batch.py owns it from here.
    [kkk_sigma_scale]=2.20949
    [use_pia_formula]=1
    # HELD AT ONE, so that ssi_floor_level IS the effective floor. The benefit
    # is max(PIA_i, takeup*ssi_floor_level), so only the PRODUCT of the two is
    # identified by any moment -- calibrating both would be one object with two
    # names. The author asked for the LEVEL to be calibrated, so the take-up is
    # the one that is pinned, and pinning it at 1 makes the calibrated number
    # read directly as the guaranteed minimum retirement income.
    #
    # The empirical take-up among eligible elderly is roughly a half, so a
    # benchmark that wants real SSI should carry takeup 0.5 and level 0.1774,
    # whose product is 0.0887. Any calibrated product above 0.1774 is a more
    # generous policy than the statute, which is the author's call to make and
    # to justify in the paper -- not a free parameter.
    [ssi_floor_takeup]=1.0
    # THE FLOOR'S LEVEL, not just its take-up. 0.1774 is the 2024 federal
    # benefit rate of $943 a month over the average wage index, so this default
    # is the DATA and a point that carries it is running real SSI. It is
    # handed in so the level can be measured at all: the take-up dial is
    # clamped to [0,1], which capped the effective floor at 0.1774, below the
    # PIA of node 4 -- 39.8 per cent of the mass -- so the floor could never
    # reach the retirees who are actually homeless. See the HANDOVER case.
    [ssi_floor_level]=0.1774
    # UNEMPLOYMENT BY PRODUCTIVITY, from BLS 2019 by education. 1 applies the
    # profile, 0 leaves the separation rate flat across types. Derivation in
    # data/UNEMPLOYMENT_BY_PRODUCTIVITY.md.
    [use_unemployment_by_productivity]=1
    # 0.0668 AND FROZEN, on the author's instruction of 5 September: *"set bottom
    # productivity to 0.0668 and freeze it"*, *"also freeze the bottom
    # productivity. do not use anything to target it"*.
    #
    # WHY. The KKK grid is geometric with ratio 2.1492 from node 2 upward, and the
    # bottom node was overridden to 0.006611187 -- ten times BELOW where the grid
    # itself puts it, 0.143629/2.1492 = 0.066829. That made the top-to-bottom
    # productivity spread 996-fold. At 0.0668 it is 99-fold, and node 1 goes from
    # 0.66 per cent of mean productivity to 6.68.
    #
    # Only the bottom node moves: it holds 0.2395 per cent of people, so the
    # compensating rescale on the upper nodes is 0.999856 and mean productivity
    # stays exactly 1.0000000000, verified both sides.
    #
    # IT WAS THE THIRD INSTRUMENT AIMED AT emp_homeless. delta was driven to a
    # 43.6-fold job-loss hazard for the same moment, and the housing taste pinned
    # at 0.268 moves it by a third route. All three were pointed at one moment at
    # different times.
    [bottom_productivity_level]=0.0668
    # HOW MANY BOTTOM NODES bottom_productivity_level COVERS. 1 is the old
    # behaviour exactly; 2 merges nodes 1 and 2 into one node of their
    # combined mass, because neither can afford the cheapest rental.
    [merge_bottom_nodes]=1
    [merge_from_node]=1
    # psi and its cap. 0.5 and 1 reproduce the model as it stood before
    # 6 September, when both were compile-time constants.
    [replacement_rate_ui]=0.5
    [max_ui_as_perc_of_avg_inc]=1
    # HELD AT ONE, ON THE AUTHOR'S INSTRUCTION. rho_d enters as
    # rho_d**(sud*include_rho_d), so one is exactly no penalty. The switch stays
    # on so the parameter is live and honest rather than a silent no-op, and the
    # value carries the decision: a substance use disorder costs earnings by
    # costing the JOB and not by cutting the wage of a household that keeps one.
    # See CALIBRATION_STATE.md for why -- it is a double counting argument and
    # the code had already reached it for rho_m.
    [rho_d]=1.0
    # rho_m, THE SAME DECISION FOR SERIOUS MENTAL ILLNESS. It enters as
    # rho_m**(min(smi,1)*include_rho_m) with include_rho_m zero, so the factor is
    # exactly one whatever the value -- but the declaration held 0.55, which
    # READS as a forty five per cent earnings penalty the model does not apply.
    # The author's instruction of 2 September: "rho_d=1, rho_m=1. do not lower
    # them."
    [rho_m]=1.0
    # THE CHILD GAP, ON since 4 September, on the author's instruction: *"yes,
    # include omega_c as well"*.  It was off by default and reserved for a final
    # round, so no point had EVER been solved with it and omega_c had never been
    # measured -- which is why weight_on_child looked like a parameter with no
    # moment and sat outside the search.
    #
    # IT COSTS 9 PER CENT, NOT 100. The block runs a second
    # solve_value_function_and_policy_functions and converge_to_stationary_
    # equilibrium, so it reads as a doubling, and it was reported here as one.
    # Measured on the same vector: 4m06s off, 4m30s on. The counterfactual
    # starts from the converged baseline distribution and converges quickly.
    #
    # It displaces the price-elasticity block, which prints "ELASTICITY SKIPPED
    # omega ran first and left its distribution behind". Nothing in gaps.py
    # scores the elasticity, so that costs no moment.
    #
    # BACK OFF, an hour later, on the author's instruction: *"since omega_c is so
    # close, just keep it fixed for now, we can adjust it at the end"*.  It read
    # 0.1622 against 0.1834 on the one point solved with it on, a gap of 11.6 per
    # cent, and weight_on_child is held rather than calibrated.
    #
    # Turning it off also restores the archive.  measure_child_gap is a CONFIG
    # SWITCH, so with it on only the single point solved that way pooled and the
    # simplex had to be rebuilt from scratch; with it off the 155 points already
    # solved pool again and the seed is free.  Nothing is lost: the two scorer
    # bugs found while turning it on -- the omega/omega_c name mismatch and
    # archive() enforcing only one switch out of the table -- are fixed and stay
    # fixed, so when omega_c is taken up at the end it will work first time.
    [measure_child_gap]=0
    # HOLD BAGGETT'S RELATIVE RISK FLAT ABOVE DATA AGE 70, on the author's
    # instruction of 4 September: "we just hold it after age 70, let's see if
    # it works".
    #
    # NOT BECAUSE THE TAIL IS PADDING -- it is not, and saying so here was an
    # error. rr_homeless is built from Baggett's 9.1 / 4.5 / 1.1 band ratios
    # interpolated between midpoints, so the 1.100 above 75 is his own 65-84
    # figure extended past its midpoint at 74.5.
    #
    # It is overridden because it is the WRONG OBJECT. Baggett's 1.1 is the
    # OBSERVED ratio for homeless 65-84 year olds; the model needs the CAUSAL
    # effect of putting a seventy five year old on the street. Selection biases
    # the observed ratio toward one at this age -- the homeless who reach 65 are
    # unusually robust, and the comparison group includes the frail and the
    # institutionalised -- and make_mortality_multipliers.py already says so:
    # "at 65+ the arithmetic returns less than one, which read literally says
    # homelessness protects the old. That is survivor selection, not causation."
    #
    # Averaged over 65 to 85 the effective multiplier goes from 1.44 to 1.92,
    # against the 1.6 the note's external table already carries in
    # increased_risk_of_death_homeless. Over the ages actually replaced, 71 to
    # 85, it goes from 1.17 to 1.84. Nothing at or below 70 changes.
    # SIXTY-FIVE, on the author's instruction of 4 September: "i think we can
    # just hold it at the 65 number.... and say that.... that would fix it".
    #
    # Sixty-five is where Baggett's ratio stops being USABLE, not where it stops
    # being measured, and that distinction is the sentence for the paper: beyond
    # 65 the observed ratio is dominated by survivor selection and does not
    # identify the causal effect the model needs.
    # 64, NOT 65, from 5 September. The Fortran holds the profile flat over
    # hold_i_1+1..life_span, so 65 puts the calibrated old-age death hazard on
    # ages 66 AND UP while the moment it is calibrated on, h_share5, is the 65+
    # band. Every old homeless household the model produces is at exactly age 65
    # -- the last working year, since retirement starts at 66 -- so at 65 the
    # instrument acted only on ages that were already empty and was inert at any
    # multiplier: three points at delta=0.30 with rr = 2.867, 4.0 and 8.0 are
    # bit-identical at every age to six decimals. 64 makes the hold cover 65+.
    # THE BASELINE ONSET, base + (1-exp(-lambda v)), zero by default so a run
    # that does not set it is bit-identical to the pure smooth hazard.
    [addiction_onset_base]=0
    [rr_homeless_hold_age]=64
    # THE LAST AGE AT WHICH THE STREET MAY BE CHOSEN, index not data age; 59 is
    # data age 84. Settable since 4 September so a different cap costs a vector
    # line rather than a model hash.
    #
    # 58 SINCE 4 SEPTEMBER, 20:40, BARRING DATA AGES 84 AND 85. This REVERSES the
    # author's earlier instruction (*"Make sure you allow homelessness at age
    # 84-85 still"*), on their instruction after seeing the age profile:
    #
    #     age 65        0.009996
    #     age 66 to 83  0.000000     eighteen consecutive zeros
    #     age 84        0.012926
    #     age 85        0.000000
    #
    # The old-age problem was never a distribution over the retired. It was one
    # spike at the last age the street may be chosen, and it is an end-of-horizon
    # artefact: age 85 is terminal (survival is exactly zero), so a household
    # homeless at 84 buys a final year of saved rent against losing a final year
    # of life. That is why MORTALITY CANNOT REACH IT -- rr_homeless_old_level runs
    # the whole ladder from 3.4 to 30, values at which death at 84 is capped at
    # probability one, and every moment moves by less than 0.05 per cent.
    #
    # MEASURED, matched pair, only this switch differing:
    #
    #           band1    band2    band3    band4    band5      h_1
    #   cap 59  0.00702  0.90792  0.00005  0.04804  0.03697  0.003198
    #   cap 58  0.00728  0.94169  0.00006  0.04983  0.00114  0.003084
    #   data      0.260    0.272    0.210    0.184    0.075  0.003990
    #
    # The spike is gone and, CONTRARY to what the addiction cap measured, it does
    # NOT relocate to 83: ages 66 to 85 are all zero and the mass reappears at 63
    # to 64. "The spike follows the cap" holds for the addiction cap and not for
    # this one. It does overshoot -- band 5 goes from -51 to -98.5 per cent -- so
    # h_share5 is a moment to watch, not to trust, on this economy.
    #
    # IT MUST BE LISTED HERE, not only in the Fortran. Making it a handover
    # parameter without adding it to this table made run_one_point reject every
    # vector that set it -- "unknown parameter:
    # max_age_to_choose_homelessness" -- and the overnight run then "solved"
    # twenty-one vertices in twenty-one seconds and promoted through all three
    # stages without measuring anything. The Fortran's PARAM_HANDOVER case and
    # this array have to be added in the same commit.
    [max_age_to_choose_homelessness]=58
    # THE OLD-AGE RELATIVE RISK, CALIBRATED. Zero keeps the hold behaviour, so
    # the default reproduces what ran before this name existed. Its moment is
    # h_share5, the old band's share of the homeless, target 0.075.
    #
    # ADDED TO THIS TABLE IN THE SAME COMMIT AS THE FORTRAN'S HANDOVER CASE.
    # Doing one without the other is what made run_one_point reject every vector
    # that set max_age_to_choose_homelessness and "solve" twenty-one vertices in
    # twenty-one seconds.
    # 2.715 IS rr_homeless AT AGE 65, so the default reproduces exactly what
    # holding at 65 produced and the parameter is continuous with the economy it
    # replaces. Its bounds are (1.0, 30.0); a value below 1 is treated as "off"
    # by the Fortran and is unreachable by the search, which is intended.
    [rr_homeless_old_level]=2.715
    # THE IMPATIENT DISCOUNT FACTOR, ADDED WITH THE TWO-TYPE MODEL. The commit
    # that split households into a patient and an impatient type taught the
    # Fortran's PARAM_HANDOVER and next_batch.py the name and did NOT teach it
    # to this script, so TWOBETA.txt line 1 -- the equal-beta validation the
    # whole two-type change rests on -- died at the argument loop with "unknown
    # parameter" before a single point was solved.
    #
    # The default is the Fortran's DECLARED value, 0.900 at
    # perceived_probability_lower=0, not a search centre: nothing has calibrated
    # it yet, and matching the declaration means handing it over explicitly
    # changes nothing. It is not added to LEGACY_DEFAULT below, deliberately.
    # Every point in points/ was measured on the ONE-type model under a
    # different MODEL hash, and the already-measured check does not compare
    # model hashes -- so a legacy tag here would let a stale one-type point be
    # served in place of a two-type run. The new name changing every tag is what
    # keeps that from happening, and it also keeps this script in step with
    # next_batch.py's IMPLICIT table, which the same commit left alone.
    [discount_factor_impatient]=0.900
)
for a in "$@"; do
    k=${a%%=*}; v=${a#*=}
    [ -n "${P[$k]+x}" ] || { echo "unknown parameter: $k" >&2; exit 2; }
    P[$k]=$v
done

# THE HOUSING GRID INVERTS IF THE SMALLEST UNIT IS NOT SMALLER THAN THE LARGEST.
#
# housing_size(0)=smallest_rental..., housing_size(n-1)=largest_house_size, and
# the interior points are laid out by
#
#   housing_status_grid_distance(i) = i*(largest-smallest)^(1/expander)/(n-1)
#   housing_size = smallest + distance^expander
#
# so at smallest>largest the grid runs DOWNWARD and index n-1, which every
# moment calls "the largest unit", is the CHEAPEST one. Nothing in the Fortran
# notices: the run completes and prints a share in the largest unit that is
# really the share in the smallest.
#
# This happened. The ladder point at smallest_rental=0.15 was solved against
# largest_house_size=0.1118 and reported h_3 = 0.295 against a target of 0.627,
# which reads as a large miss and is not a measurement of anything. Fail here
# instead, and leave the FAILED file so it is visible.
# THE MODEL HASH, COMPUTED HERE because the script cd'd to its own directory at
# the top, which made an earlier "$(dirname "$0")" resolve to code/code and
# stamp an EMPTY hash on two points before it was caught. An empty stamp is
# nearly as bad as none, so fail loudly rather than write one.
#
# IT MUST BE COMPUTED AT TOP LEVEL. This block was pasted INSIDE the inverted
# grid failure branch below, which is the one path that never reaches the point
# file, so MODEL_HASH was set only when the grid inverted and was unset on every
# run that actually solved. Under set -u the "MODEL ${MODEL_HASH}" line then
# killed the script AFTER the solve, mid-write, leaving a point file holding a
# header and no moments -- twenty minutes of compute recorded as a truncated
# file. Keep this above the first exit path.
MODEL_HASH=$(md5sum ./housing_first_or_treatment_first_SR_v1.f90 | cut -c1-10)
if [ -z "$MODEL_HASH" ]; then
    echo "FATAL: could not hash the source; refusing to write an unidentifiable point" >&2
    exit 1
fi

# THE GUARD IS RETIRED, BECAUSE THE THING IT GUARDED NO LONGER EXISTS.
#
# It required smallest_rental_relative_to_lowest_income < largest_house_size,
# because the grid used to run from the first to the second and would invert if
# they crossed. Since 1 September the rental ladder is ASSIGNED off the bottom
# rung -- housing_size is h, 2h, 3h -- so largest_house_size determines nothing
# and cannot be crossed. The ladder is monotone by construction for any h > 0.
#
# Left as a comment rather than deleted: the failure it caught was real (a point
# at smallest_rental=0.15 against largest_house_size=0.1118 reported h_3 = 0.295
# and looked like a measurement), and if the assigned ladder is ever reverted the
# guard has to come back with it.
#
# It fired once after the ladder change, refusing h_2 = 0.20 against an inert
# largest_house_size of 0.162568 -- a false positive that cost a run.

# THE LADDER INVERTS IF THE TOP RUNG IS NOT ABOVE THE BOTTOM, and nothing in
# the Fortran notices: the run completes and reports the share in "the largest
# unit" when it is really the smallest. The guard was retired on 1 September when
# the ladder became a ratio ladder and could not cross; it comes back now that the
# two rungs are independent absolute sizes again and can.
if [ "$(awk -v a="${P[smallest_rental_relative_to_lowest_income]}" \
        -v b="${P[largest_house_size]}" 'BEGIN{print (a<b)?1:0}')" != "1" ]; then
    fail "inverted housing ladder: smallest_rental_relative_to_lowest_income=${P[smallest_rental_relative_to_lowest_income]} is not below largest_house_size=${P[largest_house_size]}"
fi

# THE STREET MUST BE BELOW THE BOTTOM RUNG, now that it is an absolute size and
# not a ratio of it. Nothing in the Fortran notices an inverted ladder: the run
# completes and reports the share in "the largest unit" when it is really the
# smallest, which ENGINE.md records as having once looked like a measurement.
if [ "$(awk -v a="${P[size_homelessness]}" -v b="${P[smallest_rental_relative_to_lowest_income]}" 'BEGIN{print (a<b)?1:0}')" != "1" ]; then
    fail "inverted ladder: size_homelessness=${P[size_homelessness]} is not below smallest_rental_relative_to_lowest_income=${P[smallest_rental_relative_to_lowest_income]} (it is an ABSOLUTE size now, not a ratio)"
fi

TAG=$(for k in "${!P[@]}"; do echo "$k=${P[$k]}"; done | sort | md5sum | cut -c1-10)

# THE TAG OF THE SAME ECONOMICS BEFORE A NAME WAS ADDED TO THE VECTOR.
#
# Adding kappa_phi_d_level changed the md5 of every vector, so an arm measured
# yesterday no longer matches its own file and would be solved a second time to
# produce a byte-identical answer. Five of the eight arms of one batch were in
# exactly that position, which is two and a half hours of compute for nothing.
#
# So a name whose value is still the default it had when it was introduced is
# dropped, and the resulting LEGACY_TAG is checked as well. A point that moved
# the parameter has a different value, does not qualify, and is measured -- which
# is right, because it IS a different point. This mirrors next_batch.py's
# IMPLICIT table and the two must be kept in step.
# THE EIGHT KKK NAMES ARE LEGACY-DEFAULTED, AND THAT IS WHAT SAVES THE ARCHIVE.
# Adding a name to the vector changes the md5 of every future point, so a point
# already measured is no longer recognised and is re-run. That is the right
# price for a name that CHANGES the economy -- use_pia_formula did, and its
# points had to be re-measured. It is the wrong price for a name that does not.
#
# At the eight values below the economy is exactly the one that was being
# measured before the productivity switch existed: fixed_productivity=1 is what
# the compile-time parameter held, and the other seven are the declared values
# KKK_process was already being called with. A point that carries them at these
# values IS the point that was measured without them, so it keeps its tag and
# the archive stays readable.
#
# The one thing that is not bit-identical: the BLS unemployment tilt is now
# divided by its mass-weighted mean, which on the quantile masses is 1.000017.
# The tilt therefore moves by 1.7 parts in a hundred thousand. That is inside
# any moment's reporting precision and far inside the 10 per cent bands, and it
# buys the guarantee that the aggregate separation rate does not drift when the
# grid's masses change.
declare -A LEGACY_DEFAULT=( [ssi_floor_level]=0.1774 [kappa_phi_d_level]=8.0 [increased_prob_if_homeless]=0.2 [rho_d]=0.85 \
    [fixed_productivity]=1 [kkk_sigma_scale]=1.0 \
    [kkk_s_deviation_bottom]=3.0 [kkk_s_deviation_top]=3.0 \
    [persistence_fixed_employment_newborn]=0.5 [sd_fixed_employment_newborn]=0.309 \
    [persistence_employment_surviving]=0.9 [sd_employment_surviving]=0.2 )
LEGACY_TAG=$(for k in "${!P[@]}"; do
    if [ -n "${LEGACY_DEFAULT[$k]+x}" ] && [ "${P[$k]}" = "${LEGACY_DEFAULT[$k]}" ]; then continue; fi
    echo "$k=${P[$k]}"
done | sort | md5sum | cut -c1-10)

# A FAILURE THAT WRITES NOTHING IS INDISTINGUISHABLE FROM NOT HAVING STARTED.
# Worker 2 of the first automated round ended its turn four minutes after firing
# with no file in points/ and a status of SUCCEEDED. From outside there was no
# way to tell whether it had skipped its line, failed to build, or never run --
# and the health check's "has the point count moved" test reads a silent failure
# as a point still solving. Every exit below now leaves a file behind.
fail () {
    mkdir -p points
    {
        echo "point $TAG FAILED: $1"
        echo "FAILEDVECTOR (deliberately not a VECTOR line, so nothing treats"
        echo "this as a measured point and skips re-running it)"
        for k in $(echo "${!P[@]}" | tr ' ' '\n' | sort); do printf '  %s=%s\n' "$k" "${P[$k]}"; done
    } > "points/point_${TAG}.FAILED.txt"
    echo "run_one_point: $1" >&2
    exit 1
}

# ALREADY MEASURED? THE SCRIPT DECIDES, NOT THE WORKER. The worker prompt used
# to ask each worker to compare the parameter vector on its ROUND.txt line with
# the VECTOR line of every file in points/ and skip on a match. Those two lists
# are formatted differently and the round line carries 19 names against the
# vector's 24, so the comparison was a judgement call, and a worker that judged
# it wrong silently ran nothing. TAG is the md5 of the full sorted vector, which
# is the same comparison done exactly, so the check belongs here.
# ...AND THE ECONOMY HAS TO MATCH TOO. TAG is the md5 of the parameter vector
# ALONE, so it does not move when the model does. This guard used to test the tag
# and nothing else, and relied on a parameter RENAME to change every tag whenever
# the Fortran changed -- see the discount_factor_impatient note above. A change
# that renames nothing defeats that entirely: after the net-worth fix at ca9479b
# the reseed of an already-measured vector printed "already measured, skipping"
# and handed back the file measured on the OLD economy, silently, for as long as
# anyone kept asking. A worker whose solve merely STRADDLES a model-changing push
# leaves such a file behind, so this is not a rare case on a branch with a fleet
# on it.
#
# So resolve BOTH the stored stamp and the current source to a semantic hash and
# require them to agree. Going through model_hash.resolve rather than comparing
# the raw stamps is what keeps a genuinely behaviour-preserving edit -- a comment,
# an OpenMP clause -- from throwing away a perfectly good point.
point_is_current () {
    python3 - "$1" <<'PYEOF'
import sys, re, model_hash
try:
    text = open(sys.argv[1], errors='surrogateescape').read()
except OSError:
    sys.exit(1)
m = re.search(r'^MODEL ([0-9a-f]+)', text, re.M)
if not m:
    sys.exit(1)
# resolve_for_point: a change gated on a flag is inert for a point that ran
# with the flag off, so such a point is still current and must not be moved
# to points_superseded.
sys.exit(0 if model_hash.resolve_for_point(m.group(1), text) == model_hash.current() else 1)
PYEOF
}

if [ -f "points/point_${TAG}.txt" ] && grep -aq "END OF MOMENTS" "points/point_${TAG}.txt"; then
    if point_is_current "points/point_${TAG}.txt"; then
        echo "run_one_point: $TAG is already measured on this economy, skipping"
        exit 0
    fi
    echo "run_one_point: $TAG exists but was measured on a superseded economy"
    mkdir -p points_superseded
    mv "points/point_${TAG}.txt" "points_superseded/point_${TAG}.$(date -u +%Y%m%dT%H%M%SZ).txt"
    echo "run_one_point: moved it to points_superseded/ and re-solving"
fi
if [ "$LEGACY_TAG" != "$TAG" ] && [ -f "points/point_${LEGACY_TAG}.txt" ] &&
   grep -aq "END OF MOMENTS" "points/point_${LEGACY_TAG}.txt" &&
   point_is_current "points/point_${LEGACY_TAG}.txt"; then
    echo "run_one_point: $TAG was measured as $LEGACY_TAG before the vector"
    echo "run_one_point: gained a name it is still at the default of, skipping"
    exit 0
fi

# ONE POINT AT A TIME PER CHECKOUT. Everything below this line is shared state
# in the working directory -- the hftf binary, PARAM_HANDOVER.txt,
# B_SWEEP_GRID.txt, calibration_state.dat -- and none of it is keyed to the tag.
# Two runs started in the SAME directory therefore race, and the race is silent:
# the handover is consumed as it is read, so a second run that rewrites
# PARAM_HANDOVER.txt between the first run's write and the first run's read
# hands the model the WRONG VECTOR. The count assertion below cannot catch it,
# because it counts HANDOVER lines and the wrong vector has just as many. The
# point is then archived under the md5 of the vector it was ASKED for while
# holding the moments of the vector it was GIVEN -- a mislabelled point, which
# is worse than a missing one, because nothing downstream can tell.
#
# This was reached on 31 August by running a batch through local subagents,
# which share one checkout, instead of one container per worker. Four runs were
# live in this directory at once; B_SWEEP_GRID.txt held a different point's
# addiction_scalar_1 and PARAM_HANDOVER.txt had already been consumed. No point
# was archived from it and the archive was verified clean afterwards, but only
# because the runs were stopped before they finished.
#
# The lock makes the failure impossible rather than unlikely. Parallelism across
# CONTAINERS is untouched -- each has its own directory and its own lock -- and
# parallelism within one container was never real anyway: the solver takes every
# core it can get, so two runs sharing four cores take longer than the same two
# runs one after another.
if command -v flock >/dev/null 2>&1; then
    exec 9>".run_one_point.lock"
    if ! flock -n 9; then
        echo "run_one_point: another point is running in this checkout, waiting for it"
        flock 9
    fi
else
    echo "run_one_point: flock absent, cannot serialise; do not run two points here at once" >&2
fi

# REBUILD ON THE SOURCE'S CONTENT, NOT ON ITS TIMESTAMP.
#
# The old test was `source -nt hftf`, and it is defeated by anything that leaves
# a binary newer than the source it did not come from. That happened on 31
# August: a supervise_calibration.py running in this checkout was killed
# mid-flight and left an hftf dated 28 seconds after the source. A 38,000 line
# -O3 build takes twenty five minutes, so 28 seconds is not a build -- but it is
# newer, so the test said nothing to do, and the point ran on a binary from an
# older source. It failed loudly only because that source predated six of the
# handover names.
#
# It could have failed SILENTLY, and that is the reason for this change. MODEL_HASH
# is computed from the SOURCE while the moments come from the BINARY, so a stale
# binary that merely wins on mtime archives a point stamped with a model it was
# never measured on. Nothing downstream can tell.
#
# hftf.srcmd5 records the md5 of the source the binary was actually built from.
# A binary with no sidecar, or one whose sidecar disagrees, is not this source's.
SRC_MD5=$(md5sum housing_first_or_treatment_first_SR_v1.f90 | cut -d" " -f1)
BUILT_MD5=""
[ -f hftf.srcmd5 ] && BUILT_MD5=$(cat hftf.srcmd5)
if [ ! -x hftf ] || [ "$BUILT_MD5" != "$SRC_MD5" ]; then
    if [ -x hftf ] && [ -n "$BUILT_MD5" ]; then
        echo "run_one_point: hftf was built from $BUILT_MD5, source is $SRC_MD5"
    elif [ -x hftf ]; then
        echo "run_one_point: hftf carries no source stamp, treating it as stale"
    fi
    rm -f hftf hftf.srcmd5
    echo "building..."
    # THE COMPILER IS NOT ALWAYS THERE. Worker containers built from the
    # 2.1.245 image arrived without gfortran and the run died at the build step
    # with nothing measured; earlier images had it. Install it rather than fail,
    # and say which happened, because a silent reinstall on every point would
    # hide an image regression worth knowing about.
    if ! command -v gfortran >/dev/null 2>&1; then
        echo "run_one_point: gfortran absent from this container, installing"
        (apt-get update -qq && apt-get install -y -qq gfortran) >/dev/null 2>&1 \
            || (sudo apt-get update -qq && sudo apt-get install -y -qq gfortran) >/dev/null 2>&1
        if ! command -v gfortran >/dev/null 2>&1; then
            fail "gfortran absent and could not be installed"
        fi
        echo "run_one_point: gfortran installed, $(gfortran --version | head -1)"
    fi

    # -fimplicit-none IS NOT COSMETIC AND IT IS NOT OPTIONAL.
    # On 29 August create_unemployment_process was found reading
    # probability_becoming_employed1, with a trailing 1, declared nowhere in the
    # file. That subroutine has no implicit none of its own -- the module it
    # uses has one, but that does not reach a scope that merely uses it -- so
    # the misspelling was accepted as an uninitialised implicit real and an
    # unemployment transition row summed to about 1.46 instead of 1. The model
    # had been creating households inside unemployment for as long as anyone
    # can tell, and pi_eu was never within 45 per cent of its target.
    # This flag turns exactly that into a compile error. Verified both ways:
    # reintroducing the typo gives "Symbol 'probability_becoming_employed1' has
    # no IMPLICIT type; did you mean 'probability_becoming_employed'?", and the
    # corrected file compiles with ZERO such errors, so the typo was the only
    # instance of its class in the whole 35,000 lines. It costs nothing at run
    # time and it makes this bug unrepeatable.
    gfortran housing_first_or_treatment_first_SR_v1.f90 -mcmodel=medium -fopenmp \
        -fimplicit-none -O3 -funroll-loops -ffree-line-length-none -g -fbacktrace -o hftf \
        2> build_${TAG}.log || {
            tail -20 "build_${TAG}.log" >&2
            fail "the build failed; see build_${TAG}.log"
        }
    # Stamp it only after a build that succeeded, so a failed build never leaves
    # a sidecar vouching for a binary that is not there.
    printf '%s\n' "$SRC_MD5" > hftf.srcmd5
    echo "run_one_point: built hftf from $SRC_MD5"
fi

# EVERY POINT STARTS FROM THE DECLARATIONS PLUS ITS OWN HANDOVER, so a point is
# a function of its vector and nothing else. Left in place, calibration_state.dat
# carries the PREVIOUS point's parameters and its adjusters, its trust regions
# and its loop counter into this one, and the handover -- which consumes itself
# as it is read -- is gone by the second run, so the second point would silently
# re-measure the first. The warm start goes with it for the same reason: it is
# keyed to the distribution the previous vector produced.
rm -f calibration_state.dat calibration_distribution*.dat

# b reaches the model through the sweep grid; everything else through the handover.
printf '%s\n' "${P[addiction_scalar_1]}" > B_SWEEP_GRID.txt
: > PARAM_HANDOVER.txt
for k in "${!P[@]}"; do
    [ "$k" = addiction_scalar_1 ] && continue
    printf '"%s" %s\n' "$k" "${P[$k]}" >> PARAM_HANDOVER.txt
done
WANT=$(wc -l < PARAM_HANDOVER.txt)

ulimit -s unlimited
echo "running $TAG on $(nproc) cores"
START=$(date +%s)

# THE LABOR-SUPPLY SECANT WARNING FILLS THE DISK, so it is dropped before it
# lands. 84c1ee5 "Fix two undefined reads in the secant" changed the guard on
# the non-convergence warning at line ~20497 from abs(MU_1-MU_1), which is
# identically zero and so could never fire, to abs(MU_1-MU_2), which is the
# quantity the warning is about. That is the right condition. But the warning
# sits in the household's INNER labor-supply solve, it is not throttled, and it
# emits eleven write statements per occurrence, so on the first point actually
# solved on that source it wrote past 800,000,000 lines and roughly 22 GB, ran
# the container out of disk, and killed the run mid-solve -- after the model had
# been solving for twenty minutes and before a single moment was written. The
# point file was created at zero bytes and no moment was recorded.
#
# NO POINT IN points/ CARRIES A MODEL HASH FROM ON OR AFTER 84c1ee5 (the three
# hashes since are cd64b3a190, 163f49d500 and 8e0688e2d4, and none of them
# appears in the archive), so nothing had been solved on the live warning before
# and this is why it went unnoticed for thirteen commits.
#
# THE FILTER IS MEASUREMENT-NEUTRAL. It drops only the twelve debug lines this
# warning and its neighbours emit, all of which begin at column two because
# write(*,*) leads with a space. Checked against every archived point: the
# pattern matches 0 of the 48,144 lines in points/*.txt, so nothing it drops has
# ever appeared in a moments block, a DIAG line, an INVARIANTS line or a
# HANDOVER line. The model's arithmetic is untouched; only its stdout is.
#
# THIS IS A WORKAROUND AND NOT THE FIX. The fix is in the Fortran -- fire the
# warning once, or count it and report the count with the invariants -- and it
# belongs to whoever owns that file.
# EVERY grep THAT READS THE MODEL'S OUTPUT CARRIES -a, AND THIS IS NOT COSMETIC.
#
# THE MODEL'S STDOUT CONTAINS A BYTE GNU grep CALLS BINARY. Without -a, grep
# stops printing matching lines and emits "binary file matches" instead. In a
# PIPELINE that means the filter below silently throws away everything after the
# offending byte, and the log ends mid-run with no error anywhere.
#
# That is exactly what happened. A point ran to completion, printed its moments,
# and its log came out at 50,120 bytes ending in the middle of the distribution
# sweep, while the same binary run WITHOUT the pipe produced 305,670 bytes
# including the full moments block. Proof, on the raw log:
#
#   grep -Ev "$SPAM" raw_control.log | wc -c   ->  grep: binary file matches
#                                                   0
#
# Zero bytes out of a 305 KB file. The runner then reported NO MOMENTS BLOCK and
# hftf's own exit status of 0, which is true and was the tell: the model exited
# cleanly because it HAD finished. Nothing was wrong with it at all.
#
# Hours went into the model looking for a fault that was in this line. The
# symptom was visible the whole time -- "binary file matches" appeared in this
# session's own greps of the log repeatedly -- and was read as a nuisance to work
# around with -a rather than as the thing destroying the measurements.
SPAM='^ (labor|labor_supply_1=|distance_secant=|loop_1=|MU_1=|MU_2=|x_0=|x_1=|x_2=|addiction_index_1=|consumption_choice=|frac_spent_on_addiction=|taxable_income_1=)'
set +o pipefail
# A CAP ON THE LOG, BECAUSE ONE RUN WROTE 24 GB AND NEARLY FILLED THE DISK.
    #
    # On 31 August a point at discount_factor_impatient=0.91 was still going
    # after forty two minutes with worker_727034dc25.log at 24,216,288,407
    # bytes, on a container whose writable allowance was down to 3.3 GB. A
    # normal log for this model is under 200 KB, so that is five orders of
    # magnitude out and something was looping. Killing it and deleting the file
    # took the disk from 92 per cent to 31.
    #
    # WHAT WAS LOOPING IS NOT KNOWN, because the file was deleted for space
    # before its tail was sampled. That was the wrong order and the reason this
    # cap exists rather than a diagnosis: head -c stops reading at the limit and
    # the SIGPIPE takes the model down with it, so a runaway costs a bounded
    # 2 GB and a failed point instead of the whole container. The next one also
    # leaves its last 2 GB on disk to be read.
    #
    # 2 GB is ten thousand times a normal log, so nothing legitimate is clipped.
    #
    # AND THE COMMENT BLOCK GOES ABOVE THE COMMAND, NOT INSIDE IT. When this cap
    # was added the whole block was pasted BETWEEN the line-continuation
    # backslash and ./hftf. Bash joins a trailing backslash to the next physical
    # line, so the environment assignments joined a COMMENT and became a
    # no-op statement, and ./hftf then ran with none of them:
    #
    #   OMP_NUM_THREADS unset  -- harmless, OpenMP defaults to the core count
    #   OMP_STACKSIZE unset    -- NOT harmless. The threads get the system
    #                             default stack instead of 512M, and this model
    #                             has large thread-private arrays.
    #   GFORTRAN_UNBUFFERED_ALL unset -- stdout goes block buffered, so the log
    #                             stops updating and a live run looks stalled
    #                             when it is working. That is exactly how it
    #                             presented: last write at 01:25, still at 154
    #                             per cent CPU half an hour later.
    #
    # Nothing warns about this. The script runs, the model runs, and the only
    # symptom is a log that goes quiet and a stack size nobody set.
OMP_NUM_THREADS=$(nproc) OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1 \
    ./hftf 2>&1 | grep -a -Ev "$SPAM" | head -c 2000000000 > "worker_${TAG}.log" || true
# THE `|| true` DOES NOT DESTROY PIPESTATUS, WHICH WAS CHECKED RATHER THAN
# ASSUMED. It was rewritten once on the theory that `true` overwrites the array
# and made the captured status meaningless. Tested both ways in this shell:
#
#   set +o pipefail; (exit 139) | cat >/dev/null || true; echo ${PIPESTATUS[0]}
#     -> 139
#   set +o pipefail; (exit 139) | cat >/dev/null;         echo ${PIPESTATUS[0]}
#     -> 139
#
# Identical. PIPESTATUS is set by pipelines and a following simple command does
# not clear it, so the capture below reports hftf's own status and the form above
# is left alone. Recorded because the theory was plausible and wrong, and the
# next reader will have it too.
HFTF_STATUS=${PIPESTATUS[0]}

    if [ "$(stat -c %s "worker_${TAG}.log" 2>/dev/null || echo 0)" -ge 2000000000 ]; then
        echo "run_one_point: the log hit its 2 GB cap; the model was looping" >&2
        fail "log exceeded 2 GB, point abandoned -- see worker_${TAG}.log"
    fi
set -o pipefail
MINS=$(( ($(date +%s) - START) / 60 ))

# DID THE PARAMETERS ACTUALLY REACH THE MODEL? This is the check that was
# missing, and its absence cost a night and an archive. The handover used to be
# read at the foot of read_calibration_state, below two early returns, so on a
# freshly cloned container -- which has no calibration_state.dat, because that
# file is not in the repository -- it was never reached. The run then solved at
# the values written in the Fortran declarations and printed a complete moments
# block. Nothing anywhere said the vector had been discarded: three archived
# points with different vectors re-ran to the same loss to four decimals before
# anyone thought to count the HANDOVER lines, and there were none. The model
# prints one line per parameter it applies, so the count is the proof, and a run
# that cannot prove it must not be recorded as a point.
GOT=$(grep -ac "HANDOVER " "worker_${TAG}.log" 2>/dev/null || true)
IGNORED=$(grep -ac "HANDOVER IGNORED" "worker_${TAG}.log" 2>/dev/null || true)
GOT=$((GOT - IGNORED))
if [ "$IGNORED" -ne 0 ]; then
    grep -a "HANDOVER IGNORED" "worker_${TAG}.log" >&2 || true
    fail "the model did not recognise $IGNORED of the names it was handed"
fi
if [ "$GOT" -ne "$WANT" ]; then
    fail "handover applied $GOT of $WANT parameters; this run did not measure the vector it was given"
fi

mkdir -p points
{
    echo "point $TAG solved in ${MINS} min on $(nproc) cores"
    echo "HANDOVER OK: $GOT of $WANT parameters applied"
    # WHICH MODEL MEASURED THIS POINT. The tag is the md5 of the PARAMETER
    # vector alone, so re-measuring the same vector on a changed model
    # reproduces the tag and silently replaces a real measurement. That hazard
    # is in the standing rules and has no detector; this is the detector. A
    # worker that pulls a source change mid-round and rebuilds now stamps the
    # new hash, so the point can be identified and discarded instead of trusted.
    echo "MODEL ${MODEL_HASH}"
    echo -n "VECTOR"
    for k in $(echo "${!P[@]}" | tr ' ' '\n' | sort); do printf ' %s=%s' "$k" "${P[$k]}"; done
    echo
    # THE COST OF THE CHEAPEST RENTAL AT THE BOTTOM OF THE INCOME GRID.
    # The model prints this during grid setup, long before the moments block, so
    # the awk below never saw it and it was absent from all 583 points. It was
    # recovered on 2 September only from a run that had been SIGKILLed with its
    # full log intact, and it turned out to be the number the author had been
    # asking for: at the cheapest rung ever measured the smallest rental costs
    # 1.4955 times the LOWEST net income in the economy.
    #
    # Note also that `smallest_rental_relative_to_lowest_income` no longer means
    # what it is called. It is assigned straight into smallest_house_size; the
    # division by net_income_lowest that once made it a ratio is commented out
    # beside it. The parameter is a SIZE. This line is the ratio.
    grep -a "smallest_house_size\*rent" "worker_${TAG}.log" | head -1 |
        sed 's/^ */DIAG cheapest rental over lowest net income = /'
    awk '/===== ALL TARGETED MOMENTS =====/{f=1} f{print} /===== END OF MOMENTS =====/{if(f)exit}' \
        "worker_${TAG}.log"
} > "points/point_${TAG}.txt"

grep -aq "END OF MOMENTS" "points/point_${TAG}.txt" || {
    # HOW THE MODEL DIED, NOT JUST THAT IT DID.
    #
    # The pipeline carries `|| true` and runs under `set +o pipefail`, so the
    # shell's status is grep's and hftf's is thrown away. A point that ended in a
    # segfault, one killed by the OOM reaper and one that reached a `stop`
    # statement all looked identical: "NO MOMENTS BLOCK" and exit 0. That cost a
    # round of guessing at what a single number states.
    #
    # 139 is SIGSEGV, 137 is SIGKILL which usually means the OOM reaper, 136 is
    # SIGFPE, 134 is abort. A small non-zero status is the model's own `stop`.
    echo "NO MOMENTS BLOCK; hftf exit status ${HFTF_STATUS}" >> "points/point_${TAG}.txt"
    case "${HFTF_STATUS}" in
        139) echo "  139 = SIGSEGV, a segmentation fault" >> "points/point_${TAG}.txt" ;;
        137) echo "  137 = SIGKILL, usually the OOM reaper" >> "points/point_${TAG}.txt" ;;
        136) echo "  136 = SIGFPE, an arithmetic exception" >> "points/point_${TAG}.txt" ;;
        134) echo "  134 = SIGABRT" >> "points/point_${TAG}.txt" ;;
        0)   echo "  0 = the model exited cleanly WITHOUT printing its moments" \
                 >> "points/point_${TAG}.txt" ;;
        *)   echo "  a stop statement or a runtime error; see the log" \
                 >> "points/point_${TAG}.txt" ;;
    esac
    echo "tail of the log follows" >> "points/point_${TAG}.txt"
    tail -30 "worker_${TAG}.log" >> "points/point_${TAG}.txt"; }

cat "points/point_${TAG}.txt"
