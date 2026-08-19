# Journeys Home, and what it is for here

Journeys Home is a six wave Australian panel of 1,682 disadvantaged adults, all drawn
from Centrelink income support recipients, run by the Melbourne Institute for the
Department of Social Services. It is here to pin down one number the paper currently
states only as a bound: how much likelier the child of a homeless household is to be
homeless itself, with poverty held fixed.

## Why this dataset and not the one the paper cites

The paper quotes Flatau et al. (2013), who find that 43 per cent of non-Indigenous
homelessness assistance clients had parents who had themselves experienced
homelessness. Turning that into a risk ratio needs a base rate, and against a general
population base it implies a ratio of 5 to 6 against the model's 2.02.

That comparison is wrong, and the reason is selection. A parent who was homeless was
already poor before anything was transmitted, so a ratio taken against the whole
population carries selection AND transmission. The model computes transmission alone:
it cuts a child's income by delta_h and asks how much likelier it is to be homeless,
holding the distribution it is drawn from fixed.

Journeys Home fixes exactly that. Every respondent is on income support, so the poor
comparison group is built in rather than assumed, and the sample spans three strata:
flagged homeless, flagged at risk, and a statistically vulnerable group who were not
flagged. Comparing across those arms differences out poverty.

## What Journeys Home does NOT have

It does not ask whether the respondent's parents were homeless. The Wave 1 family
history module (F1 to F20) covers caregivers at 14, their education, unemployment,
job loss and mental health, childhood deprivation and time in state care, and never
asks about parental homelessness. So Flatau's statistic cannot be reproduced from it,
and the transmission has to be measured from the child's side instead.

## The variables that matter

| variable | meaning |
|---|---|
| `JHSTRATA` | population strata, 1/2/3: homeless, at risk, vulnerable |
| `HFHLAGE`  | age the first time without a place to live, before Journeys Home |
| `HHHIS1`-`HHHIS8`, `HHISHMLS` | history of homelessness before the survey |
| `JHWPOP`, `JHWPRS` | population weight, and the same rescaled to the sample |

The manual labels the strata only as "Strata 1/2/3". They identify themselves from the
data: the sample is 35 per cent homeless, 37 per cent at risk and 28 per cent
vulnerable, and the vulnerable arm carries much the largest population weight
(72,333 against 22,254 and 12,945 at Wave 1).

## The statistic to compute

Childhood homelessness is `HFHLAGE < 18`; adult homelessness is the homeless stratum.

    R = P(homeless stratum | first homeless before 18)
      / P(homeless stratum | not first homeless before 18)

weighted by `JHWPOP`. That is the model's `ratio_h` with poverty differenced out, and
it replaces the bound in the note with a point estimate and a standard error.

## What is here

Only the user manual, which is public. The microdata require an application through
the Australian Data Archive and may not be redistributable; if so, the derived
statistics go into `data/DATA_APPENDIX.md` and the microdata stay out of the repo.

Manual: Journeys Home User Manual, Melbourne Institute, last modified 10 December 2014.
