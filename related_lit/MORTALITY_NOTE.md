# Mortality references for the disorder's excess death risk

Added 13 September 2026 on the author's instruction, after they noted that
*"the increased risk of death from heroin and cocaine is close to 1.27-2.5 and
2.4-6.3...so i think we can easily justify lower increased mortality risks"*.

## walker_2017_excess_mortality_illegal_drug_use.pdf

Walker, Pratt, Schoenborn and Druss, *Excess mortality among people who report
lifetime use of illegal drugs in the United States: A 20-year follow-up of a
nationally representative survey*, Drug and Alcohol Dependence.

Hazard ratios, adjusted for demographic characteristics:

    heroin     HR = 2.40    95% CI  1.65 - 3.48
    cocaine    HR = 1.27    95% CI  1.04 - 1.55

Hallucinogens, inhalants and marijuana were not significantly elevated.

## nihms243803_drug_mortality.pdf

The second paper the author supplied, for the 2.4-6.3 range. It is a scanned
PDF with no text layer, so its identity and figures have NOT been verified here
and it is filed under its NIHMS id until they are. Do not cite a number from it
on the strength of this note.

## WHY THIS MATTERS FOR THE CALIBRATION

`kappa_phi_d_level` is the excess mortality of drug users in the quantitative
model. It stands at 8.0 with declared bounds of 2 to 9, sourced from Hjorthoj et
al. (2023)'s six-to-ten widened on the author's *"There are more studies that
find anywhere between 2-9"*.

**Walker's entire heroin confidence interval, 1.65 to 3.48, lies below the
current value's lower bound.** The point estimates are 2.40 and 1.27.

That has a direct consequence for a moment that is badly off. The comment at
the parameter's declaration records the measurement: taking the level from 8.0
to 6.5 moved `y_u`, the income of drug users, from 0.333 to 0.533 against a
target of 0.74. A lower death risk leaves less desperate households using, so
users are richer. The moment has been running far below target for the whole
calibration, and the literature says the instrument should be far lower than
where it sits.

The stylized model is already consistent with these papers: its calibrated
`kap` implies an SMR of **2.10**, which sits between Walker's cocaine and heroin
estimates.
