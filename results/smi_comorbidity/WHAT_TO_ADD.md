# What could be added to give the model an SMI-to-drug-use link

22 September. The author: "what exactly can you add to the model to capture
this?" Written after the measurement in BENCHMARK_SMI_BY_DRUG_STATE.md, and it
should be read after it.

## The gap, stated as a number

    uses drugs at all
      SMI, actual                                              2.68%
      non-SMI, actual                                          8.46%
      non-SMI REWEIGHTED to SMI's employment, income, assets  11.60%

The third line is the one that matters. Give ordinary households the EXACT
poverty, unemployment and asset profile of the mentally ill and they would use
drugs MORE than ordinary households do, because in this model low income pushes
toward drugs. So the author's budget hypothesis -- that SMI households do not
use because they cannot afford to -- is rejected: matching on income makes the
puzzle larger, from a factor of 3.2 to a factor of 4.3.

Two explanations are therefore dead, including one of mine:

  - NOT mortality thinning the comorbid group after the fact. The
    conditional-on-homeless numbers rule it out.
  - NOT the budget constraint. This reweighting rules it out.

What survives is the only SMI-specific term in the drug DECISION.

## The defect, and it is an identification problem

    real(8), parameter :: kappa_phi_m=2.50
    ! Assigned. Standardised mortality ratios for SMI run 2 to 3.

ASSIGNED, not calibrated, from the epidemiological SMR. That SMR is a TOTAL
mortality ratio: it already contains the overdoses, accidents and suicides that
come with the substance use real SMI populations have.

And survival_with_smi applies it to a probability that ALREADY carries the SUD
penalty:

    survival_with_smi = 1 - min(1, kappa_phi_m*(1-base_survival))

base_survival carries age, homelessness AND the SUD. So the model charges an
SMI household 2.5x on the drug's INCREMENTAL death risk, using a number whose
empirical content is partly produced by drug use. The high SMR exists partly
BECAUSE SMI people use more drugs; the model uses the high SMR to make them use
fewer.

## Three options, increasing cost

### A. FIX IT. Scale baseline mortality, not the drug's increment. RECOMMENDED.

Apply kappa_phi_m to the clean survival and leave the drug's incremental risk
unscaled. No new parameter, no new data target. It is an identification
argument a referee can check in one sentence, not a new mechanism to defend.
Should move SMI drug use toward the 11.6 per cent the reweighting implies.
Costs a recalibration, because survival touches everything.

### B. SELF-MEDICATION. The hook exists and is switched off.

    real(8) :: utility_improvement=include_addiction*0
    real(8) :: utility_improvement_adjuster=0
    real(8) :: distance_utility_improvement
    real(8) :: stopping_rule_utility_improvement=10.d0**(-3)

Someone built the full calibration apparatus for a drug utility benefit and set
the level to zero. Make it conditional on SMI, bracket it on the comorbidity
rate. Cheapest to build, WEAKEST to defend: a preference assumption a referee
can always question.

### C. LET SMI RAISE ADDICTION ONSET.

Nothing connects them today -- addiction onset takes no SMI argument at all. Add
a multiplier on the experimentation-to-addiction hazard for SMI households,
bracketed on the comorbidity ratio. This is literally R1's sentence, "mental
health contributing to drug use and addiction". Most work: new parameter, new
target, recalibration.

## Order

A first, because it costs no parameters and is the strongest argument. C if A
does not close enough, because C is the channel the referee named. B only if a
third lever is needed.

## What it buys, stated before it is done

ALL THREE MAKE TREATMENT FIRST LOOK WORSE. Each raises addiction among the
mentally ill, which enlarges the comorbid homeless population -- the group
conditionality hurts most, and which today is 0.0033 of 50.861, six thousandths
of one per cent. R1 predicted exactly this: linking mental health to drug use
"would weaken TF dramatically". He may be right, and that is the purchase.

Which argues for finishing the current transition first, so there is a clean
before and after rather than one number with nothing to compare it to.

## Already present, so not on the list

SMI ALREADY lowers the recovery hazard, mu_m=0.82, bracketed on
smi_ten_year_recovery_data=0.50. So SMI-to-SUD PERSISTENCE exists. What is
missing is SMI-to-SUD INITIATION.

# How to capture self-medication specifically

The author asked. Two places it can live, different economics, and the two
measured gaps identify them separately.

## What the existing hook actually is

utility_improvement is NOT a "drugs are pleasant" bonus, which is what I first
said. It enters as a MULTIPLICATIVE shifter on the whole flow utility and only
in the addicted branch:

    flow_utility_1=(1-utility_improvement)*sqrt_household_size(age_index)*(...)

So it is "how much better or worse life is WHILE ADDICTED". That is a better
starting point than a taste shifter, and it is currently zero.

## Option 1: the drug is worth more per unit to them

relative_share_of_addiction_1=0.16, _2=0.13 is the drug's weight in the
consumption aggregate. Make it higher under SMI.

  economics   a given dose delivers more utility
  acts on     how much they buy -> whether they try at all -> addiction risk
  targets     THE CASUAL USE GAP, 0.126, which is the bigger one

## Option 2: being addicted is less bad for them

Make utility_improvement conditional on SMI.

  economics   life while addicted is less miserable if you were suffering anyway
  acts on     the value of BEING addicted, so starting is more attractive AND
              quitting is less attractive
  targets     THE SUD GAP, 0.596

OPTION 2 IS THE ONE THAT BITES THE POLICY. It makes mentally ill addicts less
willing to get clean in exchange for a voucher, which is R1's mechanism exactly.

## The enabling change, and it is the real cost

calculate_flow_utility takes housing, space, frac_spent_on_addiction,
consumption, ownership and addicted_status. IT DOES NOT TAKE SMI. Either option
needs it threaded into that signature, and the routine is called from the
innermost loop, so every call site changes. The parameter is trivial; the
plumbing is not.

## Identification, and what the gap sizes say

Two measured moments -- casual use 0.126 of the population rate, SUD 0.596 --
identify two parameters exactly. And their SIZES are informative: the casual use
gap is far larger, so the model's failure is mostly at the INITIATION margin,
not at progression to addiction. Option 1 should carry most of the weight.

Do not add a third channel without a third moment.

## Sequencing, which matters for the calibration not just the order of work

DO THE MORTALITY DOUBLE COUNT FIX FIRST, re-measure both gaps, then size these
against what is left. Calibrating self-medication while 2.5x is still charged on
the drug margin produces a spuriously large parameter that exists only to cancel
an error, and a referee who then spots the double count has two problems with
the paper rather than one.

## What to leave alone

The most faithful story is that SMI imposes a flow disutility and the drug
relieves it. It is better economics and it would make the author's original
value-of-life argument real rather than working only through income. But it is
two more parameters and it moves every welfare number in the paper including the
CEV. Not worth it unless a referee demands the mechanism rather than the moment.

# THE AUTHOR'S OBJECTION, WHICH CHANGES THE RECOMMENDATION

"but making SMI require self medication means that the utility changes....and
they can attack it"

Correct, and it is not only a defensive point -- it picks the better model.

## Why the attack lands

If SMI changes the utility function then drugs are worth more to those
households BY ASSUMPTION, so any policy that cuts their use looks costly in
welfare terms and the referee can say the answer was assumed. And the CEV
aggregates across households: once preferences differ by group the aggregation
stops being clean. It hands them the "should an addict's utility from drugs
count" fight on top of everything else.

## Change the technology, not the tastes

Put the channel in the HAZARD of becoming addicted -- a transition probability,
not a preference. Everyone keeps one utility function, the CEV stays
interpretable, and nobody can say the mentally ill were assumed to enjoy drugs
more. It is also R1's literal sentence: "mental health contributing to drug use
and addiction". He asked for a causal channel into addiction, not a taste.

## It makes the welfare case STRONGER

  preferences  SMI use more because they like it more -> TF denying them
               housing is AMBIGUOUS, they chose it
  hazard       SMI become addicted more readily with no change in what they
               want -> conditionality punishes them for something they did not
               choose, and the welfare cost is UNAMBIGUOUS

The preference route muddies the very result it would be built to show.

## Revised order

  1. Fix the mortality double count. Removes an error, adds no assumption,
     no welfare implications, immune to this attack.
  2. Add an SMI multiplier on addiction ONSET, bracketed on the comorbidity
     rate. This is the substantive addition.
  3. Self-medication in preferences: LAST, and possibly never.

## The precedent is already in the model

mu_m=0.82 makes SMI lower the RECOVERY hazard, bracketed on
smi_ten_year_recovery_data=0.50. A technology parameter, no welfare objection,
already calibrated. The machinery and the precedent both exist. What is missing
is the same treatment on the way IN rather than the way out.

# THE DESIGN CONCLUSION, after the author pushed back twice

Two objections, in order, and the second produced the answer.

## Objection 1: a utility change is attackable

Right, and it also picks the worse model. Group-specific tastes make drugs worth
more to the mentally ill BY ASSUMPTION, so any policy cutting their use looks
costly and the CEV stops aggregating cleanly.

## Objection 2: a hazard does not capture NEEDING the drug

Also right, and it defeated my first correction. "so even if you did TF, they
would not comply ... since they are using to alleviate pain." A bare onset
multiplier says the mentally ill get UNLUCKY more often. Those households still
respond to incentives normally, so offered housing for sobriety they take it at
the same rate, TF still works on them, and drug use still falls 45 per cent. It
adds the comorbidity statistic WITHOUT the mechanism.

## The resolution: conditionality tests sobriety, not effort

The author framed non-compliance as UNWILLINGNESS. The policy cannot see
willingness. A household that tries to quit and FAILS loses the voucher exactly
like one that never tried. So the whole mechanism is available from INABILITY,
which lives in transition probabilities and not in utility.

Three routes, none touching preferences:

  1. SMI MAKES QUITTING FAIL. mu_m=0.82 already does this, bracketed on
     smi_ten_year_recovery_data=0.50, and it is mild. Strengthen it.
  2. SMI MAKES THE TREATMENT WORK LESS WELL. treatment_effect_on_recovery=2.0
     doubles the hazard for everyone in treatment; make it lower under SMI.
     MOST POLICY-RELEVANT of the three -- it says the treatment TF offers does
     not work on this group -- and worse dual-diagnosis outcomes are documented,
     so it is calibratable rather than assumed.
  3. SMI RAISES RELAPSE, so even compliers cycle back off eligibility.

Each produces the author's outcome: vouchers lost, homelessness persistent, drug
use falling by less than the 45 to 47 per cent now claimed. No utility function
is touched, so the CEV stays clean.

AND THE WELFARE CASE IS STRONGER under inability than under unwillingness. If
they need the drug, a referee can say they chose it over the housing. If they
tried and could not, they are punished for something that was never a choice.

## What each route does and does not close

The recovery routes act on EXITS, so they close the SUD gap (0.596) and not the
experimentation gap (0.126), which is about ENTRIES and is the larger failure.
Pair them with the mortality double count fix, which removes an artificial
suppressor rather than adding an assumption.

## The package, zero utility change

  1. fix the mortality double count      stops suppressing their use artificially
  2. SMI into recovery or treatment
     efficacy                            they cannot get clean -> they fail
                                         conditionality -> the mechanism
  3. onset multiplier if needed          closes any remaining initiation gap

Step 2 delivers the mechanism and is the SMALLEST change of the three: the
parameter exists and is already calibrated, just set mild.

# WHERE IT LANDED: the drug has to have value, and the author was right twice

## The error the author caught, which is why the design is what it is

I proposed lowering the recovery hazard under SMI so they could not quit. The
author: "but if you raise the hazard, they will use even less....what you need
is for the drug to have some value to them."

CORRECT, AND MY PROPOSAL WAS BACKWARDS. Addiction is a trap and agents see the
trap coming. Making it harder to escape makes it more frightening to ENTER, so
lowering mu_m under SMI DETERS initiation and pushes their use DOWN.

And it worsens the larger failure. The measurement says the model fails worst at
initiation -- casual use off by 8x (0.126) against addiction off by 1.7x
(0.596). The hazard route would have damaged the big gap to fix the small one,
and it pushes the same direction as the existing 2.5x over-charge. I was piling
on.

THE ONE NON-PREFERENCE LEVER THAT MOVES THEIR USE UP is the mortality double
count fix, because it makes the drug CHEAPER for them. It can restore correct
pricing; it cannot make the drug worth MORE to them than to anyone else.
Instrumental routes -- drugs improving their employment or health -- are
empirically indefensible.

So value it is, and value lives in preferences. "they need it to feel better."

## The structure

    flow_utility = [as now] - chi_m * 1{SMI} * (1 - relief(drug))

Nothing else changes. b, the drug's weight in the aggregate, the housing terms,
all identical across households.

## Why this survives attack when "they like drugs more" does not

It is not that they enjoy drugs more. It is that they are suffering and the drug
reduces the suffering. Two checkable consequences:

  - They are WORSE OFF THAN EVERYONE ELSE THROUGHOUT, using or not. Relief only
    partly restores them, never puts them ahead. Nothing assumes they gain
    relative to anybody, so "you assumed the answer" has nothing to grip.
  - THE MODEL ALREADY DOES THIS FOR HOMELESSNESS, through
    housing_status_utility_function. State-dependent utility is a welfare cost
    of a bad state, not a taste. SMI becomes the same kind of object.

## What it delivers that the hazard could not

  necessity        inelastic demand, bought even when poor, because it relieves
                   rather than pleases
  the right margin raises casual use AND addiction, and casual use is the bigger
                   failure
  NON-COMPLIANCE   quitting means returning to untreated suffering, so the
                   sobriety-for-housing trade is far more expensive for them and
                   conditionality fails on exactly the group it should not

## Identification: keep only one parameter free

  chi_m          ASSIGN from health-economics disability weights for severe
                 mental disorders. External, defensible the way kappa_phi_m=2.50
                 is assigned from mortality ratios.
  relief         CALIBRATE to the comorbidity rate.

One free parameter, one moment, and the casual-use gap held in reserve to CHECK
the fit rather than to fit.

## Cost to the results, stated before it is built

Drug use falls by less than the current 45 to 47 per cent. Homelessness stays
higher longer, because this group never regains eligibility. CEV at t=1 comes
down from +1.955 per cent, possibly through zero, which would put the
grandfathered arm back on the table.

One reassurance on the CEV: it compares two economies and a constant state cost
appears in both, so chi_m largely differences out. What does NOT difference out
is the relief -- under TF they lose the drug and therefore the relief -- and
that is exactly the effect that should be measured rather than assumed away.

## Sequencing

Mortality fix first, re-measure both gaps, then size relief against what is
left. Otherwise relief is calibrated partly to cancel the 2.5x over-charge, and
a referee who spots the double count then has two problems instead of one.
