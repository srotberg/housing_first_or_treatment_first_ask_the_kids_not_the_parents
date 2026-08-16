!===============================================================================
! params.f90 -- grids, parameters and shared state for the simplified model
!
! Simplified relative to housing_first_or_treatment_first_SR_v1.f90:
!   - no homeownership, no tenure choice, no mortgages, no negative assets
!   - no housing-market general equilibrium (rent is a fixed price)
!   - drug price p_v is an equilibrium object instead
!   - preferences do NOT depend on SUD status (single theta_v)
!   - no UI-expiration state; employment is a two-point state
!
! State: (j, a, y, e, d, h, eta)
!   j    age
!   a    non-negative financial assets
!   y    labour productivity (permanent x persistent, pre-combined)
!   e    employment (1 = employed, 0 = unemployed)
!   d    SUD status (0 = clean, 1 = SUD)
!   h    housing entered with (1 = homeless, 2..NH = rental sizes)
!   eta  housing voucher held (0/1)
!===============================================================================
module params
    implicit none
    integer, parameter :: dp = kind(1.0d0)

    !-- demographics ----------------------------------------------------------
    integer, parameter :: n_age      = 60      ! model ages, real age 26..85
    integer, parameter :: j_ret     = 41      ! first retirement age index
    ! Last age at which a clean household may initiate use. R1's smaller comment
    ! 1 says this is in tension with the U-shaped age profile of use in Table
    ! 4(a). It is a VARIABLE so the model can be run without it: set
    ! j_exp = n_age to remove the restriction and inspect the age profile.
    integer :: j_exp = 30

    !-- grid sizes ------------------------------------------------------------
    integer, parameter :: NA  = 60         ! non-negative asset grid
    integer, parameter :: NY  = 9          ! labour productivity states
    ! Employment / UI duration. The paper lets UI persist for the whole
    ! unemployment spell; UI in the US is time-limited, and reviewers question
    ! that assumption. Here UI is drawn on ENTRY to unemployment with
    ! probability prob_ui and lasts ONE year only.
    !   1 = employed
    !   2 = unemployed, first year, receiving UI
    !   3 = unemployed without UI (first year non-recipients AND all later years)
    !
    ! Three states suffice, not four. A first-year non-recipient and a
    ! long-term unemployed household have identical income (zero) and identical
    ! continuations (find work with p_find, otherwise stay), so their value
    ! functions are equal and the states merge exactly.
    integer, parameter :: NE  = 3
    integer, parameter :: ND  = 2          ! 1 = clean, 2 = SUD
    integer, parameter :: NH  = 4          ! 1 = homeless, 2..4 = rental sizes
    integer, parameter :: NV  = 2          ! 1 = no voucher, 2 = voucher
    integer, parameter :: NM  = 2          ! 1 = good mental health, 2 = poor

    ! Drug-use regimes. A SINGLE addiction hazard: you become addicted with the
    ! same probability however much you consume, so the only thing that matters
    ! is whether you use at all.
    !   1 = abstain (v = 0), 2 = use (v > 0)
    ! This drops vbar, the light/heavy threshold, and the 6.48 heavy-to-light
    ! ratio, and cuts the inner loop by a third.
    integer, parameter :: NREG = 2

    ! Labour supply is CONTINUOUS, pinned by the intratemporal FOC as in the
    ! original code: equate the marginal utility of the extra after-tax wage to
    ! the marginal utility of leisure, and bracket the root by the sign of the
    ! difference. Given a', hours affect only the flow payoff, never the
    ! continuation value, so the FOC is a scalar solve that never touches the EV
    ! table.
    !
    ! One thing the original does not do and this does: the residual is not
    ! monotone, because the food-stamp and voucher clawbacks kink the budget in
    ! hours, so a single bisection on [0,1] can land on the wrong local optimum.
    ! The interval is split at the kinks and each piece solved exactly. See the
    ! header of solve.f90.
    real(dp), parameter :: hours_tol = 1.0e-8_dp
    integer,  parameter :: hours_maxit = 60

    !-- preferences -----------------------------------------------------------
    real(dp), parameter :: sigma   = 2.0_dp     ! CRRA
    real(dp) :: theta_h = 0.20_dp               ! Cobb-Douglas weight on housing (calibrated)
    real(dp) :: theta_v = 0.10_dp               ! weight on drugs -- SAME for d=0 and d=1
    ! Stone-Geary shifter, BY SUD STATUS (the AE's suggestion). Cobb-Douglas
    ! weights stay invariant to SUD -- so reducing SUD does not mechanically
    ! raise utility from c and h, which is R2/R3's objection -- but b does vary.
    ! A single b cannot match both moments: large b deters clean agents by
    ! pushing the unconstrained v* below zero, which also drives SUD drug
    ! spending to the corner. b_d(1) pins participation, b_d(2) keeps the
    ! interior solution so theta_v pins the 44% expenditure share.
    ! indexed (SUD status, mental health). Poor mental health lowers b, i.e.
    ! raises the marginal utility of the first units of drug use -- the
    ! self-medication channel R1 comment 1(a) is asking about.
    real(dp) :: b_dm(ND,NM) = reshape([4.0e-1_dp, 1.0e-3_dp, &
                                       1.0e-1_dp, 1.0e-3_dp], [ND,NM])
    ! Homelessness scales b DOWN, exactly as poor mental health does: sleeping
    ! rough raises the marginal utility of the first units of use. This is the
    ! only parameter in the model that controls the ELASTICITY OF DRUG USE WITH
    ! RESPECT TO HOUSING ACCESS -- R2's "crux", also R3 and AE A13. Without it
    ! the moment cannot be targeted at all: housing a household with SUD only
    ! raises its resources, and drugs are a normal good, so the model would
    ! predict housing RAISES use, against Milby et al. (2005). Calibrated in the
    ! second stage to the Milby housed-versus-unhoused abstinence ratio.
    real(dp) :: b_hl_ratio = 1.00_dp            ! 1.0 = channel off
    real(dp) :: omega_l  = 0.30_dp              ! weight on leisure (calibrated)
    real(dp), parameter :: sigma_l = 3.0_dp     ! Frisch elasticity 0.5, Chetty (2012)
    real(dp) :: aleph   = 3.0_dp                ! flow value of being alive (VSL normalisation)
    real(dp) :: beta    = 0.96_dp

    !-- prices ----------------------------------------------------------------
    ! Rent is NORMALISED to one. Only the product p_rent*h enters the budget and
    ! utility, so the rent level and the housing grid are not separately
    ! identified; fixing the price makes the housing grid the calibrated object,
    ! which is what R2's comment D1 asks for -- every grid point is now pinned
    ! by a moment rather than asserted in a footnote.
    real(dp), parameter :: p_rent = 1.0_dp
    real(dp) :: p_v    = 1.0_dp                 ! endogenous: clears the drug market
    real(dp), parameter :: r_free = 0.03_dp

    !-- drug supply: C(V) = psi1/psi2 * V**psi2, so elasticity = 1/(psi2-1).
    !   psi1 is normalised so that p_v = 1 at the benchmark quantity, which keeps
    !   the existing calibration intact; psi2 is set from the supply elasticity.
    ! Supply elasticity. The maintained assumption in the drug-economics
    ! literature is that US supply of cocaine and heroin is VERY elastic --
    ! Rhodes et al. (2002), discussed in the National Academies' Understanding
    ! the Demand for Illegal Drugs -- on the grounds that these are agricultural
    ! products with simple, inexpensive processing, so producers can meet any
    ! demand at roughly the current price.
    !
    ! There is a natural experiment. The August 2010 abuse-deterrent
    ! reformulation of OxyContin pushed a very large mass of demand into heroin,
    ! enough to quadruple heroin death rates (Alpert, Powell and Pacula, NBER
    ! w24475). Purity-adjusted heroin prices did not rise; they fell slightly
    ! between 2010 and 2012. A demand shift of that size leaving price flat is
    ! direct evidence of a near-horizontal supply curve.
    !
    ! So a flat supply curve is the BASELINE, not an omission -- which means the
    ! submitted paper's fixed price was the field's standard assumption rather
    ! than an unjustified normalisation. Finite elasticities are the ROBUSTNESS
    ! direction. R1 1(c) and R3 M2d asked for the price to be endogenous; it now
    ! is, and the data say the flat benchmark is the right one to sit at.
    real(dp) :: psi1 = 1.0_dp
    ! Supply elasticity, BRACKETED from measured tax incidence in two legal
    ! markets. Neither is the illegal market, but together they bound it.
    !
    !   LOWER BOUND 0.79. Hansen, Miller and Weber (2017) on Washington's 2015
    !   switch from a 25% gross receipts tax at every supply-chain stage to a
    !   single 37% retail excise, in universal state traceability data.
    !   Consumers bear 44% of the additional burden and demand elasticity is
    !   about -1 within two weeks, so eps_s = rho|eps_d|/(1-rho) = 0.79.
    !   Washington CAPS licensed cultivation canopy, a supply constraint with no
    !   analogue in an illegal market, so this is a floor.
    !
    !   UPPER BOUND ~3.6. The same paper notes its result "stands in contrast to
    !   the literatures on cigarette and gasoline tax incidence ... which
    !   generally finds consumers bear the substantial majority of the tax
    !   burden". At a consumer share near 0.9 and a consensus demand elasticity
    !   near 0.4, that implies eps_s about 3.6 for unconstrained legal
    !   manufacturing. Note the two cannot be reconciled by demand elasticity
    !   alone, which is the authors' own explanation: no single supply
    !   elasticity fits both numbers, so cannabis really is steeper, and the
    !   licence cap is the obvious reason.
    !
    ! Illegal drugs sit between. No licence cap, which pushes toward 3.6; but
    ! enforcement prevents capital-intensive scaling -- Caulkins and Reuter note
    ! drugs are "diluted and packaged by hand ... because enforcement makes it
    ! risky to maintain dedicated, fixed capital equipment" -- and moving more
    ! product needs more shipments and more couriers, which pushes toward 0.79.
    !
    ! 2.0 is the midpoint of that bracket. Swept over {0.79, 2, 5, 50}, where 50
    ! is the effectively-infinite benchmark the model used to assume.
    !
    ! NOTE: with pin_pv = 1 this does NOT affect the first stage. p_v is the
    ! numeraire there and psi1 is renormalised at each clearing, so the
    ! calibrated benchmark is invariant to psi2.
    real(dp) :: drug_supply_elasticity = 2.0_dp
    real(dp) :: psi2 = 1.02_dp
    ! psi1 is a pure NORMALISATION: it has no independent meaning and is pinned
    ! by the requirement that p_v = 1 at the benchmark. During the first stage
    ! the benchmark is still moving every sweep, so pinning psi1 once at the
    ! start and then letting p_v float against it is simply wrong: participation
    ! travels from about 0.2% to 5%, and p_v drifts about 7% away from 1.
    !
    ! With pin_pv = 1 the first stage holds p_v = 1 and RE-normalises psi1 each
    ! time the equilibrium clears, so the drug price is 1 in the benchmark by
    ! construction and the second stage inherits a correctly normalised supply
    ! curve. p_v then moves only where it should: counterfactuals and the
    ! second-stage price elasticity.
    integer :: pin_pv = 1

    !-- taxes and transfers ---------------------------------------------------
    real(dp) :: tau_l = 0.85_dp                 ! level parameter, HSV form
    real(dp), parameter :: xi_tax = 0.85_dp     ! progressivity
    ! Capital income tax. The government was collecting this in the revenue
    ! identity while households received capital income gross, so the budget
    ! constraint and the government budget disagreed about the same dollar.
    real(dp), parameter :: tau_k = 0.15_dp
    ! Accidental bequests. Redistributing them as a uniform lump sum is a large
    ! unconditional transfer to the poor with welfare consequences of its own,
    ! which would contaminate every policy comparison in the paper. They go into
    ! the government budget instead, where they relax the tax constraint.
    integer  :: bequest_to_govt = 1
    real(dp) :: bequest = 0.0_dp

    !-- housing ---------------------------------------------------------------
    ! h_grid(1) is homelessness; the three rental sizes are geometric,
    ! h_small, h_small*h_spread, h_small*h_spread**2, so two parameters set the
    ! whole grid: the LEVEL is pinned by the share of households spending more
    ! than half their income on housing, the SPREAD by the share spending more
    ! than 30%. With h_homeless and theta_h that is four housing parameters
    ! against four moments of the SCF housing-burden distribution.
    real(dp) :: h_grid(NH)
    real(dp) :: h_homeless = 0.0083_dp
    real(dp) :: h_small    = 0.080_dp
    real(dp) :: h_spread   = 1.480_dp

    !-- voucher programme -----------------------------------------------------
    real(dp) :: kappa_V   = 0.5_dp              ! eligibility: income < kappa_V * median
    real(dp) :: kappa_r   = 0.3_dp              ! tenant contribution rate
    real(dp) :: prob_V    = 0.06_dp             ! lottery probability (1.0 = universal)
    integer  :: policy_TF = 0                   ! 0 = Housing First, 1 = Treatment First
    ! Enforcement under Treatment First is now COSTLY, and costly in the way the
    ! programme actually is: each voucher holder faces a per-period probability
    ! of being tested, each test costs the government money, and detection can
    ! only happen if a test happened. Effective detection is test_prob*detect_prob,
    ! so the previous behaviour is the test_prob = 1 corner.
    ! R1's comment 4(c) says the $1-2bn testing estimate is too large to relegate
    ! to a dismissive footnote; this puts it in the budget constraint where it
    ! competes with everything else the government pays for.
    ! Per-period probability that an existing voucher lapses for reasons other
    ! than failing a test. Zero in the benchmark and in every policy experiment,
    ! because a Housing Choice Voucher is held indefinitely while the household
    ! stays eligible. It is non-zero in exactly one place: the Costantini
    ! validation, where the object being replicated is the VA's Grant and Per
    ! Diem programme, which is TIME LIMITED at six months to two years. That
    ! expiry is not a detail of his setting, it is the thing his mechanism
    ! section says drives the null.
    real(dp) :: v_expire    = 0.0_dp            ! P(voucher lapses | held, eligible)
    ! Grant and Per Diem allows a stay of six months to two years, a mean of
    ! about 1.25 years, so an annual lapse hazard of 1/1.25.
    real(dp), parameter :: gpd_expire = 0.80_dp
    real(dp) :: test_prob   = 1.0_dp            ! P(tested | holds a voucher), TF
    ! Cost per test. A urine panel runs about $40; quarterly testing is roughly
    ! $160 a year against average earnings near $70,000.
    real(dp) :: test_cost   = 0.0023_dp         ! share of average income, per year
    real(dp) :: detect_prob = 1.0_dp            ! P(use detected | tested)
    real(dp) :: false_pos   = 0.0_dp            ! P(clean agent flagged | tested)

    !-- SUD process -----------------------------------------------------------
    real(dp) :: pi_d_low    = 0.02_dp           ! annual hazard of SUD given any use
    real(dp) :: recover_housed   = 0.025_dp
    real(dp) :: recover_mult_hl  = 0.5_dp       ! recovery multiplier when homeless

    !-- treatment (endogenous recovery) ---------------------------------------
    ! A clean answer to "Treatment First has no treatment": SUD agents may take
    ! up treatment at a utility cost, which raises the recovery hazard.
    integer  :: allow_treatment = 1
    ! Treatment costs UTILITY, not resources. A resource cost comes out of the
    ! same budget that buys food and rent, so the households with the strongest
    ! case for treatment -- the poorest -- are exactly the ones who cannot
    ! afford it, which is not how publicly funded treatment works. A flat
    ! utility cost is the stigma, effort and time of entering a programme whose
    ! monetary cost somebody else bears. Calibrated to treatment take-up among
    ! those with SUD.
    ! Side benefit: hours no longer depend on the treatment decision, so the
    ! labour-supply FOC is solved once rather than twice for households with SUD.
    real(dp) :: treat_ucost     = 0.05_dp       ! flat utility cost of take-up
    real(dp) :: treat_gain      = 1.35_dp       ! RCT-based; KEY SENSITIVITY

    !-- mental health ---------------------------------------------------------
    ! A persistent state, exogenous, that (i) cuts productivity conditional on
    ! working, (ii) worsens employment transitions, (iii) lowers the SUD
    ! recovery hazard, and (iv) lowers b. R1 comment 1(a). The productivity
    ! penalty is what generates EMPLOYED homeless households with positive but
    ! low income -- R1 comment 2(c)(i) -- which an unemployment effect alone
    ! cannot do.
    ! The state is SERIOUS MENTAL ILLNESS, not "any mental illness". That is the
    ! concept that drives chronic homelessness and disability, and it is the
    ! Imrohoroglu-Zhao channel: in their model labour shocks generate short
    ! homeless spells while health shocks generate chronic homelessness, with
    ! expanded disability income the effective policy for the chronic group.
    !
    ! smi_prevalence pins the ergodic share; mh_onset is DERIVED from it and
    ! mh_recover, so persistence can be calibrated without breaking prevalence.
    real(dp) :: smi_prevalence = 0.055_dp  ! SMI among US adults, NSDUH 2023
    ! EXTERNAL, following Imrohoroglu-Zhao: ten years after diagnosis about 50%
    ! of people with schizophrenia improve to the point they can work and live
    ! independently, so 1-(1-0.5)^(1/10) = 0.067 per year. IZ pin their health
    ! shock with exactly this moment plus the prevalence.
    real(dp) :: mh_recover  = 0.067_dp
    ! Onset is now CALIBRATED to the SMI prevalence rather than derived from it,
    ! because onset is no longer the same for everyone: SUD raises it.
    real(dp) :: mh_onset    = 0.0039_dp
    ! Age PROFILE of SMI onset. Same shape/level split as the mortality
    ! multipliers: the shape is data, the level stays calibrated to the 5.5%
    ! prevalence target, so identification is unchanged.
    !   mh_onset_age(j) = mh_onset * shape_mh(j)
    ! A flat onset against a flat recovery drives prevalence toward its steady
    ! state from below, so the model produced a profile that RISES with age.
    ! NSDUH has SMI falling from 11.0% at 26-29 to 1.4% at 65+, a factor of
    ! eight. The model hit the average and had the shape backwards, which
    ! misplaces the mental-health channel -- and everything it feeds, employment,
    ! homelessness and mortality -- across the life cycle.
    real(dp) :: shape_mh(n_age)
    real(dp) :: mh_onset_age(n_age)
    real(dp) :: smi_prev0 = -1.0_dp             ! SMI prevalence at age 26, from data
    ! SUD RAISES THE HAZARD OF SERIOUS MENTAL ILLNESS. Substance-induced
    ! psychosis converts to schizophrenia or bipolar disorder at a pooled rate
    ! near 25% (Murrie et al., Schizophrenia Bulletin), and in the Danish
    ! registers any substance use disorder predicts conversion to schizophrenia
    ! with a hazard ratio of 1.34, amphetamine use disorder 1.90 and opioid use
    ! disorder 2.74. Central value 2.0, range 1.3-2.7.
    !
    ! This is a channel the submitted paper did not have, and it matters twice
    ! over. Privately it is a further cost of addiction. Fiscally it is a further
    ! EXTERNALITY: SUD raises SMI, SMI raises disability receipt, lowers
    ! employment, raises mortality and raises homelessness, none of which the
    ! household internalises beyond its own utility.
    real(dp) :: mh_onset_sud = 2.0_dp
    real(dp) :: prod_pen_m  = 0.55_dp      ! calibrated: homeless income/average
    ! AE question A20. Evidence on the SUD wage penalty CONDITIONAL ON WORKING
    ! is contested -- parts of the older literature find positive effects for
    ! casual use -- while the robust findings are on the employment margin
    ! (~50% more unscheduled absence, ~44% higher turnover), which the model
    ! already captures through kappa_ue_d. Baseline: no direct wage effect.
    real(dp) :: prod_pen_d  = 1.00_dp
    ! Treatment raises the recovery hazard. 3.0 was unsupported: the only clean
    ! randomised estimate is an odds ratio near 1.22 for contingency management.
    ! The TF result runs through this parameter, so report it as a range.
    real(dp) :: treat_gain_lit = 1.35_dp
    real(dp) :: kappa_ue_m  = 0.35_dp      ! calibrated: employment rate given SMI
    ! Standardised mortality ratios for SMI are roughly 2-3, corresponding to
    ! 10-20 years of life expectancy lost. 1.3 was far too low.
    ! SMI mortality multiplier. CONSTANT in age, and that is a finding rather
    ! than a default: unlike SUD and homelessness, whose multipliers collapse
    ! with age, the mental-illness ratio is flat. Olfson et al. (2015, JAMA
    ! Psychiatry), US Medicaid schizophrenia cohort, give all-cause SMRs of 3.6
    ! at 20-34, 3.4 at 35-54 and 4.0 at 55-64 -- if anything rising.
    !
    ! The LEVEL is a judgement between three sources measuring different
    ! populations. Walker, McGee and Druss (2015) pool 148 studies of ANY mental
    ! disorder and get 2.22. Olfson's 3.4-4.0 is schizophrenia alone, roughly 1%
    ! of the population, inside Medicaid. Colton and Manderscheid (2006) get
    ! about 3.2 for public mental-health clients across eight states. This
    ! model's poor-mental-health state is SMI at 5.5% prevalence: broader than
    ! schizophrenia, far narrower than any mental disorder. 2.50 sits between
    ! Walker's broad figure and Olfson's narrow one, which is where 5.5%
    ! prevalence belongs. Worth a sensitivity run at 3.2.
    real(dp) :: kappa_phi_m = 2.50_dp
    ! SUD recovery multiplier with SMI. Dual-diagnosis cohorts relapse at 39.8%
    ! against 26.4% without a co-occurring disorder (odds ratio 1.85 for
    ! difficulty maintaining abstinence), so the probability of staying in
    ! remission is 0.602 against 0.736 -- a ratio of 0.82. Converting the odds
    ! ratio to a risk ratio at that base rate gives the same 0.82. Previously
    ! 0.50, which was invented.
    real(dp) :: rec_mult_m  = 0.82_dp      ! SUD recovery multiplier, poor MH
    ! Disability income for the non-employed with SMI. Roughly two-thirds of
    ! people with schizophrenia receive federal disability insurance, so giving
    ! this group zero income overstates their homelessness. Also the margin
    ! Imrohoroglu-Zhao find effective for the chronically homeless.
    ! SSA: the average SSDI benefit was about $1,537 a month in 2024, roughly
    ! $18,400 a year against average annual earnings near $70,000, so 0.26. The
    ! SSI federal benefit rate of $943 a month is 0.16. 0.25 sits at the SSDI
    ! figure, which is the relevant one for people with a work history.
    real(dp) :: disab_income = 0.25_dp     ! share of average income
    ! IZ pin the fraction of the homeless with mental illness using DI COVERAGE
    ! (their zeta_di), not persistence. Same here: wider coverage keeps more of
    ! the SMI population housed.
    real(dp) :: di_coverage = 0.60_dp      ! calibrated: SMI share of the homeless
    integer  :: include_disability = 1
    real(dp) :: mh_dist0(NM)               ! newborn distribution over MH
    integer  :: include_mental_health = 1

    !-- mortality and employment multipliers ----------------------------------
    ! Mortality multipliers for homelessness and for SUD, BY AGE. Both were flat
    ! constants (1.6 and 6.9) and both vary strongly with age in the data; they
    ! are also derived TOGETHER, because the homelessness ratio in the
    ! literature is measured on a population that mostly also has SUD, so
    ! netting one out depends on the other. See data/make_mortality_multipliers.py
    ! for the derivation and data/us_mortality_multipliers.csv for the values.
    !
    ! Shape of kappa_phi_d comes from CDC WONDER drug-poisoning deaths by age,
    ! concentrated on the SUD prevalence and divided by the all-cause baseline;
    ! the LEVEL is anchored to the previous flat 6.9 at its peak, so no level
    ! anyone defended has changed. Shape and level of kappa_phi_h come from
    ! Baggett et al. (2013), net of the SUD composition of their cohort.
    !
    ! A flat 6.9 implied a near-sevenfold SUD mortality penalty at 80, where the
    ! measured excess is essentially nil; a flat 1.6 was five times too small at
    ! prime ages. Both errors ran in the direction that weakens the paper's
    ! central mechanism at the ages where it does its work.
    ! SHAPE and LEVEL are separated deliberately. kappa_phi_d is still the
    ! SECOND STAGE's instrument: calibrate_kappa_phi_d brackets it inside
    ! Degenhardt et al.'s SMR range to hit a drug-price elasticity of
    ! participation of -0.63, and that elasticity is what disciplines how much
    ! drug use responds to its costs -- the object the whole policy experiment
    ! turns on. Pinning the level from mortality data would take the instrument
    ! away and leave the elasticity undisciplined.
    !
    ! So the data supplies the PROFILE and the elasticity supplies the LEVEL:
    !
    !   kappa_phi_d_age(j) = 1 + (kappa_phi_d - 1) * shape_sud(j)
    !   kappa_phi_h_age(j) = max(1, rr_homeless(j)/[(1-s) + s*kappa_phi_d_age(j)])
    !
    ! kappa_phi_h has to be rebuilt alongside it, because Baggett's ratio is
    ! measured on a population that mostly also has SUD, so netting the SUD
    ! component out depends on wherever the level lands.
    !
    ! This is now OVER-identified, which is a feature: the level that matches the
    ! price elasticity can be compared against the level implied by the mortality
    ! data, and disagreement is informative rather than hidden.
    real(dp) :: kappa_phi_h_age(n_age)
    real(dp) :: kappa_phi_d_age(n_age)
    real(dp) :: shape_sud(n_age)                ! normalised to 1 at its peak
    real(dp) :: rr_homeless(n_age)              ! Baggett all-cause RR, by age
    real(dp) :: sud_share_homeless = 0.217_dp   ! s, for netting out
    real(dp) :: kappa_phi_h = 1.6_dp            ! legacy scalar, unused in survival()
    real(dp) :: kappa_phi_d = 6.9_dp            ! SUD mortality multiplier
    real(dp) :: kappa_ue_h  = 0.8_dp
    real(dp) :: kappa_ue_d  = 0.6_dp
    real(dp) :: pi_ue_base  = 0.55_dp           ! job finding
    real(dp) :: pi_eu_base  = 0.03_dp           ! job separation
    real(dp) :: prob_ui     = 0.30_dp           ! share of entrants who draw UI
    real(dp) :: ui_replace  = 0.50_dp           ! replacement rate, first year only

    !-- externality (replaces the loss-of-consortium adjustment) --------------
    ! Enters period utility so it is internalised: it affects the value of life
    ! and therefore drug decisions, rather than being bolted on after solving.
    ! R2's wording is specific: "a large homeless population, ESPECIALLY IF MANY
    ! ARE ADDICTED TO DRUGS, creates a negative externality beyond the fiscal
    ! burden". So the disamenity is weighted by composition, not just the level:
    !
    !     disutility = kappa_ext * ( H_agg + omega_ext * HD_agg )
    !
    ! with HD_agg the share of the population both homeless and with SUD.
    ! Households take both aggregates as given -- that is what makes this an
    ! externality rather than a private cost -- but the aggregates are
    ! equilibrium objects, so the term responds to policy and feeds back into
    ! the value of life and hence into drug decisions. That is the property
    ! kappa_cons lacked and which R1 objected to in comment 3(a).
    !
    ! kappa_ext has no credible point estimate. It is reported as a bounded
    ! sensitivity with kappa_ext = 0 as the conservative case; see
    ! EXTERNALITY.md. Note zero here is a DEFENSIBLE baseline (no externality),
    ! unlike kappa_cons = 0, which reversed the paper's conclusion.
    real(dp) :: kappa_ext = 0.0_dp
    ! Composition weight on the homeless with SUD. NO direct estimate exists:
    ! R2's wording ("especially if many are addicted to drugs") implies it is
    ! positive, and the hedonic split between permanent supportive housing and
    ! emergency shelter implies composition matters, but neither pins a number.
    ! BASELINE 1.0 -- the disamenity depends on the headcount alone -- with the
    ! composition-weighted version reported as an appendix robustness.
    real(dp) :: omega_ext = 1.0_dp
    ! Willingness to pay to END homelessness, as a share of annual income.
    ! Loubiere et al.'s eight-country contingent-valuation study asked exactly
    ! this question -- what would you pay in annual taxes to end homelessness
    ! through Housing First -- and got about EUR 57 per respondent per year,
    ! roughly 0.2% of average annual earnings. That is a STATED preference over
    ! the AGGREGATE homelessness rate, which is precisely the object kappa_ext
    ! multiplies, and it is a far better fit to this model than the hedonic
    ! shelter-siting literature, which measures a local, avoidable disamenity in
    ! a model that has no geography.
    ! Caveats to state in the paper: stated rather than revealed preference;
    ! European rather than US; 30.3% protest zeros; and the elicited change is
    ! eliminating homelessness rather than a marginal change.
    real(dp) :: wtp_end_homelessness = 0.002_dp
    ! ...but that amount buys elimination of the EUROPEAN homelessness rate, not
    ! the model's. The WTP has to be normalised per unit of homelessness before
    ! it can be applied to a different rate, otherwise the same euro figure would
    ! imply a different disamenity in every economy it is transplanted into.
    !
    ! Reference rate: FEANTSA counts roughly 700,000 people sleeping rough or in
    ! shelter across the EU at the time of the survey (2017), against a
    ! population near 440 million, so about 0.16%. The 2023 overview reports
    ! ~895,000, but part of that rise is improved measurement, and the survey was
    ! fielded in 2017. Take 0.18% as the central value and sweep 0.15-0.22%: the
    ! implied kappa_ext is inversely proportional to it, so this is the single
    ! most consequential judgement in the disamenity calibration and it should be
    ! reported as a range, not a point.
    !
    ! Composition: the disamenity is weighted by omega_ext on the homeless with
    ! SUD, so the reference bundle is H_ref*(1 + omega_ext*sud_share_ref), with
    ! the drug use disorder share of the homeless taken from the same pooled
    ! high-income-country evidence used for the model's own target.
    real(dp) :: wtp_ref_homeless_rate = 0.0018_dp
    real(dp) :: wtp_ref_sud_share     = 0.217_dp
    real(dp) :: H_agg     = 0.0_dp              ! aggregate homelessness rate
    real(dp) :: HD_agg    = 0.0_dp              ! homeless AND SUD, share of population

    !-- channel switches, for the mechanism-decomposition arms ----------------
    integer :: on_mortality_d = 1               ! arm 1: SUD -> mortality
    integer :: on_employment_d = 1              ! arm 2: SUD -> employment
    integer :: on_homeless_fb = 1               ! arm 3: homelessness feedback

    !-- fiscal ----------------------------------------------------------------
    ! Fiscal cost per homeless household per year, as a share of average income.
    ! The homeless state h_1 is LITERAL homelessness -- shelters and the street,
    ! not doubling up -- so the matching figure in Abramson and Van Nieuwerburgh
    ! (2024, NBER w32582, p.30) is their $2,500 per household per month for the
    ! literally homeless, NOT the $1,775 they blend across the literally homeless
    ! and the doubled-up. $30,000 a year against the model's $70,000 average
    ! income gives 0.4286. Components, their footnote 11: shelters, social
    ! services, extra policing, hospital emergency care.
    !
    ! Note the direction of travel. R2 and R3 both judged the previous 0.252 too
    ! HIGH; the best structural number in the literature is 70% higher again, and
    ! its authors call it conservative.
    real(dp) :: chi_H = 0.4286_dp
    real(dp) :: chi_D = 0.212_dp                ! fiscal cost per person with SUD
    real(dp) :: cfloor_share = 0.10_dp          ! food-stamp consumption floor

    !-- grids and processes ---------------------------------------------------
    real(dp) :: a_grid(NA)
    real(dp) :: y_grid(NY)
    real(dp) :: y_trans(NY,NY)
    real(dp) :: y_dist0(NY)
    !-- parental warm glow (R2 C3, AE A6) -------------------------------------
    ! Section 4.1.3 of the submitted paper specifies log x' = rho_x log x + eps
    ! but newborns are drawn from the UNCONDITIONAL distribution, so rho_x is
    ! decorative. That is precisely the AE's A6. This makes it load bearing: at
    ! one parental age the household's value gains nu times the expected value
    ! of a newborn whose productivity is drawn CONDITIONAL on its own.
    !
    ! The parent cannot influence that draw, so the term is additive and changes
    ! no decision. It shifts welfare LEVELS, and therefore the policy
    ! comparison, because V_1 differs across regimes. That is exactly what R2
    ! predicts: "it would only amplify the welfare gains from reducing
    ! addiction". Nothing else breaks, because in a stationary equilibrium the
    ! unconditional newborn distribution is unchanged.
    !
    ! nu is NOT calibrated. Because it moves no behaviour there is no
    ! behavioural moment that could identify it, so it is a welfare robustness
    ! dimension and the baseline runs at zero.
    real(dp) :: rho_x        = 0.5_dp        ! intergenerational persistence
    real(dp) :: nu_parent    = 0.0_dp        ! warm glow weight; 0 = off
    integer  :: j_parent     = 5             ! model age 5 = real age 30
    real(dp) :: yg_trans(NY,NY)              ! child's y given the parent's
    real(dp) :: V_newborn(NY,NM) = 0.0_dp    ! previous pass's newborn value
    real(dp) :: warm_glow(NY)    = 0.0_dp    ! the additive term, by parent y
    real(dp) :: age_prof(n_age)
    real(dp) :: surv_base(n_age)
    real(dp) :: median_income, avg_income

    !-- solution --------------------------------------------------------------
    real(dp), allocatable :: V(:,:,:,:,:,:,:)       ! (NA,NY,NE,ND,NV,NM,n_age+1)
    integer,  allocatable :: pol_a(:,:,:,:,:,:,:)   ! index into a_grid
    integer,  allocatable :: pol_h(:,:,:,:,:,:,:)   ! index into h_grid
    integer,  allocatable :: pol_reg(:,:,:,:,:,:,:) ! drug regime
    integer,  allocatable :: pol_tr(:,:,:,:,:,:,:)  ! treatment take-up
    real(dp), allocatable :: pol_l(:,:,:,:,:,:,:)   ! hours worked (continuous)
    ! Benchmark hours, held for the deadweight-loss decomposition. When
    ! freeze_hours = 1 the household is forced to work pol_lb and re-optimises
    ! everything else, which is what shuts the labour-supply RESPONSE to the tax
    ! without touching preferences. Raising omega_l instead does NOT do this --
    ! it makes leisure overwhelmingly valuable and sends hours to the corner.
    real(dp), allocatable :: pol_lb(:,:,:,:,:,:,:)
    integer :: freeze_hours = 0
    ! Benchmark drug regime, for the safety-net experiment. freeze_drug = 1
    ! holds the use decision at its benchmark schedule while everything else
    ! re-optimises, which is what isolates the ADDICTION margin of moral hazard
    ! from the ordinary consumption-smoothing one.
    integer, allocatable :: pol_regb(:,:,:,:,:,:,:)
    integer :: freeze_drug = 0
    real(dp), allocatable :: pol_c(:,:,:,:,:,:,:)
    real(dp), allocatable :: pol_v(:,:,:,:,:,:,:)
    real(dp), allocatable :: dist(:,:,:,:,:,:,:)
    real(dp) :: mh_trans(NM,NM)          ! clean households
    real(dp) :: mh_trans_d(NM,NM)        ! households with SUD: higher onset
    ! precomputed powers, to keep pow() out of the inner loop
    real(dp) :: h_pow(NH), alpha_u, beta_u, gamma_u

contains

subroutine setup_grids()
    integer :: i, k
    real(dp) :: amax, rho, sig, m, step

    !-- assets: dense near zero, where the policy action is ------------------
    amax = 40.0_dp
    do i = 1, NA
        a_grid(i) = amax * ( real(i-1,dp)/real(NA-1,dp) )**3.0_dp
    end do

    !-- housing: homeless plus three rental sizes ----------------------------
    call build_housing_grid()

    !-- productivity: Rouwenhorst for an AR(1) in logs -----------------------
    rho = 0.90_dp
    sig = 0.20_dp
    call rouwenhorst(NY, rho, sig, y_grid, y_trans)
    do i = 1, NY
        y_grid(i) = exp(y_grid(i))
    end do
    call ergodic(NY, y_trans, y_dist0)
    ! Intergenerational chain, on the EXISTING grid.
    !
    ! NOT a second rouwenhorst call: that routine declares `grid` as intent(out)
    ! and builds its own grid whose width depends on rho, so calling it again
    ! silently OVERWROTE y_grid with a much narrower one and corrupted the whole
    ! productivity process. It also would not have delivered rho_x, because a
    ! transition matrix built for one grid does not carry its persistence onto
    ! a different one.
    !
    ! Instead: the child inherits the parent's productivity with probability
    ! rho_x and is otherwise drawn from the ergodic distribution,
    !
    !     yg_trans(i,j) = rho_x*1{i=j} + (1-rho_x)*Omega_x(j).
    !
    ! The correlation is exactly rho_x, and the unconditional distribution is
    ! preserved, sum_i Omega_x(i) yg_trans(i,j) = Omega_x(j), which is what
    ! lets the warm glow be added without disturbing the stationary newborn
    ! distribution.
    do i = 1, NY
        do k = 1, NY
            if (i == k) then
                yg_trans(i,k) = rho_x + (1.0_dp - rho_x)*y_dist0(k)
            else
                yg_trans(i,k) = (1.0_dp - rho_x)*y_dist0(k)
            end if
        end do
    end do

    !-- deterministic age profile and baseline survival ----------------------
    do i = 1, n_age
        if (i < j_ret) then
            age_prof(i) = 1.0_dp + 0.038_dp*real(i,dp) - 0.0006_dp*real(i,dp)**2
        else
            age_prof(i) = 0.0_dp
        end if
        ! fallback only; load_life_table() overwrites this if the file is present
        surv_base(i) = 1.0_dp - min(0.99_dp, 0.0005_dp*exp(0.075_dp*real(i,dp)))
    end do
    surv_base(n_age) = 0.0_dp
    call load_life_table()

    ! fallback only; load_mortality_multipliers() overwrites these if the file
    ! is present. Flat values reproduce the pre-data behaviour exactly.
    shape_sud   = 1.0_dp        ! flat fallback reproduces the old behaviour
    rr_homeless = kappa_phi_h*((1.0_dp-sud_share_homeless) &
                + sud_share_homeless*kappa_phi_d)
    call load_mortality_multipliers()
    call refresh_mortality_multipliers()

    shape_mh = 1.0_dp           ! flat fallback reproduces the old behaviour
    call load_mh_onset_shape()

    psi2 = 1.0_dp + 1.0_dp/drug_supply_elasticity

    !-- collapse the nested Cobb-Douglas into a single product, and hoist every
    !   power that does not depend on a choice out of the inner loop:
    !   comp = c**alpha_u * h**beta_u * (v+b)**gamma_u
    alpha_u = (1.0_dp-theta_h)*(1.0_dp-theta_v)
    beta_u  = theta_h*(1.0_dp-theta_v)
    gamma_u = theta_v
    do i = 1, NH
        h_pow(i) = h_grid(i)**beta_u
    end do

    !-- mental-health transition and its ergodic newborn distribution --------
    ! onset is implied by the target prevalence and the recovery rate, so
    ! calibrating persistence never moves the prevalence off its data value
    call build_mh_trans()

    m = 0.0_dp
    do i = 1, NY
        m = m + y_dist0(i)*y_grid(i)
    end do
    avg_income    = m
    median_income = m
    step = 0.0_dp
end subroutine setup_grids


!-- mental-health transitions, separately for clean and SUD households -------
!===============================================================================
! Baseline survival from a US life table, if one has been supplied.
!
! R3's comment M1b asks for the empirical basis of the survival hazards to be
! transparent, and a smooth exponential fitted to nothing is not that. The right
! source is the CDC period life table (Arias et al., United States Life Tables)
! or the SSA equivalent.
!
! Expected file: data/us_life_table.csv, one record per line,
!
!     age,qx
!
! with age in YEARS (26 through 85 is what the model uses) and qx the
! probability of dying within one year at that exact age, for the total
! population. Anything outside 26-85 is ignored; any age not supplied keeps the
! fallback. A missing file is not an error -- it prints a warning and the
! fallback stands -- because the model has to run before the file arrives.
!===============================================================================
subroutine load_life_table()
    integer  :: u, ios, age, i, nread
    real(dp) :: qx
    character(len=256) :: line
    logical  :: there

    inquire(file='../../data/us_life_table.csv', exist=there)
    if (.not. there) inquire(file='data/us_life_table.csv', exist=there)
    if (.not. there) then
        write(*,'(A)') ' NOTE: data/us_life_table.csv not found; survival is the'
        write(*,'(A)') '       smooth fallback hazard, which is NOT a data source.'
        return
    end if

    open(newunit=u, file='../../data/us_life_table.csv', status='old', iostat=ios)
    if (ios /= 0) open(newunit=u, file='data/us_life_table.csv', status='old', iostat=ios)
    if (ios /= 0) return

    nread = 0
    do
        read(u,'(A)',iostat=ios) line
        if (ios /= 0) exit
        if (len_trim(line) == 0) cycle
        if (line(1:1) < '0' .or. line(1:1) > '9') cycle      ! header
        read(line,*,iostat=ios) age, qx
        if (ios /= 0) cycle
        i = age - 25                                          ! model age 1 = real 26
        if (i >= 1 .and. i <= n_age) then
            surv_base(i) = 1.0_dp - min(1.0_dp, max(0.0_dp, qx))
            nread = nread + 1
        end if
    end do
    close(u)
    surv_base(n_age) = 0.0_dp        ! nobody survives the last model age
    write(*,'(A,I0,A)') ' life table loaded: ', nread, ' ages from data/us_life_table.csv'
end subroutine load_life_table


!===============================================================================
! Age profiles of the homelessness and SUD mortality multipliers.
!
! Expected file: data/us_mortality_multipliers.csv, with a header and
!
!     age,kappa_phi_d,kappa_phi_h,overdose_excess_ratio
!
! age in YEARS. Anything outside 26-85 is ignored; any age not supplied keeps
! the flat fallback. A missing file warns rather than aborting.
!===============================================================================
subroutine load_mortality_multipliers()
    integer  :: u, ios, age, i, nread
    real(dp) :: sh, rrh
    character(len=256) :: line
    logical  :: there

    inquire(file='../../data/us_mortality_multipliers.csv', exist=there)
    if (.not. there) then
        write(*,'(A)') ' NOTE: data/us_mortality_multipliers.csv not found;'
        write(*,'(A)') '       mortality multipliers are FLAT, which the data rejects.'
        return
    end if

    open(newunit=u, file='../../data/us_mortality_multipliers.csv', &
         status='old', iostat=ios)
    if (ios /= 0) return

    nread = 0
    do
        read(u,'(A)',iostat=ios) line
        if (ios /= 0) exit
        if (len_trim(line) == 0) cycle
        if (line(1:1) < '0' .or. line(1:1) > '9') cycle      ! header
        read(line,*,iostat=ios) age, sh, rrh
        if (ios /= 0) cycle
        i = age - 25                                          ! model age 1 = real 26
        if (i >= 1 .and. i <= n_age) then
            shape_sud(i)   = max(0.0_dp, sh)
            rr_homeless(i) = max(1.0_dp, rrh)
            nread = nread + 1
        end if
    end do
    close(u)
    write(*,'(A,I0,A)') ' mortality multipliers loaded: ', nread, ' ages'
end subroutine load_mortality_multipliers


!-- rebuild both mortality profiles from the current SUD level ---------------
! Must be called after ANY change to kappa_phi_d -- in particular by the second
! stage, which moves it to hit the price elasticity.
subroutine refresh_mortality_multipliers()
    integer :: i
    real(dp) :: s
    s = sud_share_homeless
    do i = 1, n_age
        kappa_phi_d_age(i) = 1.0_dp + (kappa_phi_d - 1.0_dp)*shape_sud(i)
        kappa_phi_h_age(i) = max(1.0_dp, rr_homeless(i) &
            / ((1.0_dp - s) + s*kappa_phi_d_age(i)))
    end do
end subroutine refresh_mortality_multipliers


!===============================================================================
! Age profile of SMI onset, and the SMI share of newborns.
!
! Expected file: data/us_mh_onset_shape.csv, header then
!     age,shape_mh_onset,implied_onset,smi_prevalence
!===============================================================================
subroutine load_mh_onset_shape()
    integer  :: u, ios, age, i, nread
    real(dp) :: sh, onset, prev
    character(len=256) :: line
    logical  :: there

    inquire(file='../../data/us_mh_onset_shape.csv', exist=there)
    if (.not. there) then
        write(*,'(A)') ' NOTE: data/us_mh_onset_shape.csv not found; SMI onset is'
        write(*,'(A)') '       FLAT in age, which inverts the observed profile.'
        return
    end if
    open(newunit=u, file='../../data/us_mh_onset_shape.csv', status='old', iostat=ios)
    if (ios /= 0) return
    nread = 0
    do
        read(u,'(A)',iostat=ios) line
        if (ios /= 0) exit
        if (len_trim(line) == 0) cycle
        if (line(1:1) < '0' .or. line(1:1) > '9') cycle
        read(line,*,iostat=ios) age, sh, onset, prev
        if (ios /= 0) cycle
        i = age - 25
        if (i >= 1 .and. i <= n_age) then
            shape_mh(i) = max(0.0_dp, sh)
            if (i == 1) smi_prev0 = min(0.9_dp, max(0.0_dp, prev))
            nread = nread + 1
        end if
    end do
    close(u)
    write(*,'(A,I0,A,F6.3)') ' SMI onset shape loaded: ', nread, &
        ' ages, prevalence at 26 = ', smi_prev0
end subroutine load_mh_onset_shape


!-- the parental warm glow term, by the parent's productivity ----------------
! Recomputed from the PREVIOUS pass's newborn value, so the circularity (the
! parent at age j_parent needs V at age 1, which is solved last) is handled as
! a fixed point iterated alongside the equilibrium loop. It converges trivially
! because the term is additive and moves no policy.
subroutine refresh_warm_glow()
    integer :: iy, iyp, imp
    warm_glow = 0.0_dp
    if (nu_parent <= 0.0_dp) return
    do iy = 1, NY
        do iyp = 1, NY
            if (yg_trans(iy,iyp) <= 0.0_dp) cycle
            do imp = 1, NM
                warm_glow(iy) = warm_glow(iy) + nu_parent*yg_trans(iy,iyp) &
                              * mh_dist0(imp)*V_newborn(iyp,imp)
            end do
        end do
    end do
end subroutine refresh_warm_glow


!-- rebuild the onset profile from the calibrated level ----------------------
subroutine refresh_mh_onset()
    integer :: i
    do i = 1, n_age
        mh_onset_age(i) = mh_onset*shape_mh(i)
    end do
end subroutine refresh_mh_onset


subroutine build_mh_trans()
    real(dp) :: on_d
    if (include_mental_health == 1) then
        on_d = min(0.99_dp, mh_onset*mh_onset_sud)
        mh_trans(1,1) = 1.0_dp - mh_onset;  mh_trans(1,2) = mh_onset
        mh_trans(2,1) = mh_recover;         mh_trans(2,2) = 1.0_dp - mh_recover
        mh_trans_d(1,1) = 1.0_dp - on_d;    mh_trans_d(1,2) = on_d
        mh_trans_d(2,1) = mh_recover;       mh_trans_d(2,2) = 1.0_dp - mh_recover
    else
        mh_trans = 0.0_dp; mh_trans(1,1) = 1.0_dp; mh_trans(2,1) = 1.0_dp
        mh_trans_d = mh_trans
    end if
    call refresh_mh_onset()
    ! Newborns enter at real age 26, so their SMI share is the DATA prevalence
    ! at 26, not the ergodic of the age-1 transition matrix. With onset now
    ! declining in age, the ergodic understates it badly -- it gives 4.7%
    ! against 11-13% observed -- and the whole profile would start from the
    ! wrong level.
    if (smi_prev0 > 0.0_dp .and. include_mental_health == 1) then
        mh_dist0(1) = 1.0_dp - smi_prev0
        mh_dist0(2) = smi_prev0
    else
        call ergodic(NM, mh_trans, mh_dist0)
    end if
end subroutine build_mh_trans


!-- P(m' | m, d): SUD raises the onset hazard --------------------------------
pure function pm_of(id, im, imp, j) result(p)
    integer, intent(in) :: id, im, imp, j
    real(dp) :: p, on
    if (include_mental_health /= 1) then
        if (imp == 1) then; p = 1.0_dp; else; p = 0.0_dp; end if
        return
    end if
    if (im == 1) then
        on = mh_onset_age(j)
        if (id == 2) on = min(0.99_dp, on*mh_onset_sud)
        if (imp == 1) then; p = 1.0_dp - on; else; p = on; end if
    else
        if (imp == 1) then; p = mh_recover; else; p = 1.0_dp - mh_recover; end if
    end if
end function pm_of


subroutine build_housing_grid()
    integer :: i
    h_grid(1) = h_homeless
    h_grid(2) = h_small
    do i = 3, NH
        h_grid(i) = h_grid(i-1)*h_spread
    end do
end subroutine build_housing_grid


subroutine alloc_all()
    ! NOTE: housing entered with (h) is NOT a state variable here. Survival,
    ! employment transitions and the recovery hazard all condition on the
    ! CHOSEN h', and renters face no adjustment cost, so the housing a
    ! household arrives with is payoff-irrelevant. Carrying it would replicate
    ! the entire problem NH times. Reinstate it if moving costs are added.
    allocate(V     (NA,NY,NE,ND,NV,NM,n_age+1))
    allocate(pol_a (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_h (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_reg(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_tr(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_l (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_lb(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_regb(NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_c (NA,NY,NE,ND,NV,NM,n_age))
    allocate(pol_v (NA,NY,NE,ND,NV,NM,n_age))
    allocate(dist  (NA,NY,NE,ND,NV,NM,n_age))
    V = 0.0_dp; dist = 0.0_dp
    pol_a = 1; pol_h = 1; pol_reg = 1; pol_tr = 0; pol_l = 0.0_dp
    pol_lb = 0.0_dp; pol_regb = 1
    pol_c = 0.0_dp; pol_v = 0.0_dp
end subroutine alloc_all


!-- survival probability, given chosen housing and SUD status ----------------
! hours are a choice only for the employed of working age; everyone else
! supplies zero and consumes full leisure
pure function hours_of(j, ie, hstar) result(h)
    integer,  intent(in) :: j, ie
    real(dp), intent(in) :: hstar
    real(dp) :: h
    if (j < j_ret .and. ie == 1) then
        h = hstar
    else
        h = 0.0_dp
    end if
end function hours_of


!-- Stone-Geary shifter, given SUD status, mental health and CHOSEN housing --
pure function b_of(id, im, ih) result(b)
    integer, intent(in) :: id, im, ih
    real(dp) :: b
    b = b_dm(id,im)
    if (ih == 1) b = b * b_hl_ratio
end function b_of


pure function survival(j, ih, id, im) result(phi)
    integer, intent(in) :: j, ih, id, im
    real(dp) :: phi, mult, death
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_phi_h_age(j)**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_phi_d_age(j)**real(on_mortality_d,dp)
    if (im == 2) mult = mult * kappa_phi_m
    death = (1.0_dp - surv_base(j)) * mult
    phi = max(0.0_dp, 1.0_dp - min(death, 1.0_dp))
end function survival


!-- job-finding probability --------------------------------------------------
pure function p_find(ih, id, im) result(p)
    integer, intent(in) :: ih, id, im
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult * kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult * kappa_ue_d**real(on_employment_d,dp)
    if (im == 2) mult = mult * kappa_ue_m
    p = min(1.0_dp, pi_ue_base*mult)
end function p_find


!-- job-separation probability -----------------------------------------------
pure function p_sep(ih, id, im) result(p)
    integer, intent(in) :: ih, id, im
    real(dp) :: p, mult
    mult = 1.0_dp
    if (ih == 1) mult = mult / kappa_ue_h**real(on_homeless_fb,dp)
    if (id == 2) mult = mult / kappa_ue_d**real(on_employment_d,dp)
    if (im == 2) mult = mult / kappa_ue_m
    p = min(1.0_dp, pi_eu_base*mult)
end function p_sep


!-- employment transition over the four-state (employment, UI duration) grid --
! Row ie of the kernel, given chosen housing, SUD status and mental health.
pure subroutine emp_trans(ie, ih, id, im, s)
    integer,  intent(in)  :: ie, ih, id, im
    real(dp), intent(out) :: s(NE)
    real(dp) :: pf, ps
    pf = p_find(ih, id, im)
    ps = p_sep(ih, id, im)
    s = 0.0_dp
    select case (ie)
    case (1)                       ! employed
        s(1) = 1.0_dp - ps
        s(2) = ps * prob_ui        ! separate into UI
        s(3) = ps * (1.0_dp - prob_ui)
    case (2)                       ! UI year -- benefit expires now
        s(1) = pf
        s(3) = 1.0_dp - pf
    case (3)                       ! no UI, any duration
        s(1) = pf
        s(3) = 1.0_dp - pf
    end select
end subroutine emp_trans


!-- recovery hazard, given housing and treatment take-up ---------------------
pure function p_recover(ih, itr, im) result(p)
    integer, intent(in) :: ih, itr, im
    real(dp) :: p
    p = recover_housed
    if (ih == 1) p = p * recover_mult_hl**real(on_homeless_fb,dp)
    if (im == 2) p = p * rec_mult_m
    if (itr == 1) p = p * treat_gain
    p = min(1.0_dp, p)
end function p_recover


!=============================== helpers =====================================

subroutine rouwenhorst(n, rho, sig, grid, trans)
    integer, intent(in) :: n
    real(dp), intent(in) :: rho, sig
    real(dp), intent(out) :: grid(n), trans(n,n)
    real(dp) :: p, nu, t2(2,2)
    real(dp), allocatable :: tk(:,:), tn(:,:)
    integer :: k, i

    p  = (1.0_dp + rho)/2.0_dp
    nu = sig*sqrt(real(n-1,dp)/(1.0_dp-rho**2))
    do i = 1, n
        grid(i) = -nu + 2.0_dp*nu*real(i-1,dp)/real(n-1,dp)
    end do

    t2(1,:) = [p, 1.0_dp-p]
    t2(2,:) = [1.0_dp-p, p]
    allocate(tk(2,2)); tk = t2
    do k = 3, n
        allocate(tn(k,k)); tn = 0.0_dp
        tn(1:k-1,1:k-1) = tn(1:k-1,1:k-1) + p*tk
        tn(1:k-1,2:k)   = tn(1:k-1,2:k)   + (1.0_dp-p)*tk
        tn(2:k,1:k-1)   = tn(2:k,1:k-1)   + (1.0_dp-p)*tk
        tn(2:k,2:k)     = tn(2:k,2:k)     + p*tk
        tn(2:k-1,:) = tn(2:k-1,:)/2.0_dp
        deallocate(tk); allocate(tk(k,k)); tk = tn
        deallocate(tn)
    end do
    trans = tk
    deallocate(tk)
end subroutine rouwenhorst


subroutine ergodic(n, trans, d)
    integer, intent(in) :: n
    real(dp), intent(in) :: trans(n,n)
    real(dp), intent(out) :: d(n)
    real(dp) :: dn(n)
    integer :: it, i, k
    d = 1.0_dp/real(n,dp)
    do it = 1, 5000
        dn = 0.0_dp
        do i = 1, n
            do k = 1, n
                dn(k) = dn(k) + d(i)*trans(i,k)
            end do
        end do
        if (maxval(abs(dn-d)) < 1.0e-14_dp) then
            d = dn; return
        end if
        d = dn
    end do
end subroutine ergodic

end module params
