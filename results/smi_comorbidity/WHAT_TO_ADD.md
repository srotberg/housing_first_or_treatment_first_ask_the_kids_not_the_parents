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
