# Morbidity from homelessness and from SUD, separately

The author, 4 September, on a proposed state: *"a state like morbidity which is a
utility cost each period that rises with homelessness and with drug use... Once you
have the morbidity it stays with you throughout your life. I don't want to add it
yet, but it would be good to see if there are data on the impact of homelessness and
Sud on morbidity relative to the normal population (separately not together)."*

Nothing is added to the model. This is the evidence scan only.

## What the repository already had, and why none of it answers the question

- `Baggett et al. 2013` is MORTALITY, already used for `rr_homeless`. The proposed
  state is morbidity, which the model does not have.
- `Sadowski et al. 2009` is an RCT on homeless adults **selected for chronic
  illness**, so it cannot give homeless-versus-general morbidity.
- `data/DATA_APPENDIX.md` has a comorbidity table, but it is mood and anxiety
  disorder against SUD REMISSION, not morbidity against the general population.
- `related_lit/Long_term_health_outcomes_homelessness_link.mht` is a paywall page
  with no extractable numbers.

## Homelessness

**Multimorbidity, the closest thing to the proposed state.** A systematic review
pools multimorbidity among people experiencing homelessness at **45 per cent**,
against an age-standardised **9.3 per cent** in the general US adult population --
about a five-fold rate.

**A single condition, with a housed control at the same deprivation.** In a
cross-sectional study in London and Birmingham, COPD prevalence was **1.1 per cent**
in the least deprived housed quintile, **2.0 per cent** in the most deprived housed
quintile, and **14.0 per cent** in the homeless group. The homeless group exceeded
housed controls on every disease measured except diabetes. The comparison against the
MOST DEPRIVED housed quintile is the one that matters here, because it nets out most
of the income effect the model already has.

**Composition.** Two decades of multi-institutional electronic medical records put
the homeless comorbidity burden at depression 48.1, anxiety 45.8, hypertension 44.2,
cardiovascular disease 18.4 and hepatitis 18.1 per cent.

## Substance use disorder

Weaker for this purpose, and worth saying so.

GBD assigns **disability weights** per substance use disorder, estimated from NESARC
and the Australian Comorbidity and Trauma Study, with asymptomatic cases weighted
**zero**. That is structurally the right object for the proposed state -- a
disability weight IS a per-period utility loss on a 0 to 1 scale, which is what the
author is describing -- but the searches did not return the weight VALUES, only the
method. Getting them means the GBD disability-weight tables directly.

At the aggregate, drug use disorders were **1.3 per cent of all-cause DALYs** in GBD
2019, up from 0.8 per cent in GBD 2010. That is a population share, not a per-person
ratio against the healthy, so it does not by itself calibrate anything.

## THE CAVEAT THAT DECIDES WHETHER ANY OF THIS CAN BE USED

Almost every homeless-versus-housed morbidity figure above is CROSS-SECTIONAL. It
cannot separate

  - selection, sick people become homeless, from
  - causation, homelessness makes people sick,

and the proposed state is explicitly causal and CUMULATIVE: morbidity rises with
time spent homeless and stays. A five-fold multimorbidity ratio calibrated as if it
were all causal would overstate the accumulation, possibly by a lot, because severe
illness is a well-documented route INTO homelessness.

What would identify it is longitudinal: morbidity onset rates among people already
homeless against matched housed controls, or a housing intervention measuring
morbidity rather than mortality or service use. The At Home/Chez Soi and Sadowski
RCTs already in `related_lit/` are the right SHAPE -- randomised housing, followed up
-- but Sadowski selected on chronic illness at baseline and reports ED visits and
hospitalisations rather than a morbidity stock.

## If it is built anyway

The two numbers that would pin it, one per channel, both still to be obtained:
the GBD disability weight for drug dependence, and a longitudinal morbidity onset
rate for the homeless against housed controls at the same deprivation. The
cross-sectional ratios above bound the second from above.
