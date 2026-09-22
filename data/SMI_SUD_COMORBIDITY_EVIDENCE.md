# How much more likely are people with SMI to use drugs and to carry a disorder

22 September, the author's question. Scanned because the SMI channel needs a
target and `data/NSDUH_2024.dta` carries no mental-health variable.

**The headline: the published ratio runs from about 1.5 to about 7.5, and what
moves it is not measurement error. It is which population "SMI" names.** The
model has already committed to one answer for its prevalence target and to the
other for its employment penalty, and this is where that comes due.

## The model's own denominators, so the ratios are comparable

Everything below is converted against the model's cut, `svyrdudany`, 26+, from
`SMI_BY_SUD_UNIVERSE.md`:

    "drug user"  any drug use disorder incl. mild    0.0890
    "SUD"        moderate or severe                  0.0368

## The evidence

**Hunt et al. (2018), Drug and Alcohol Dependence 191:234-258.** Systematic
review and meta-analysis, 123 articles, 165,811 subjects, schizophrenia spectrum
disorders, community and clinical settings 1990-2017.

    any SUD        41.7%
    illicit drugs  27.5%      <- the comparable one
    cannabis       26.2%
    alcohol        24.3%
    stimulants      7.3%

    males 48.0% vs females 22.1%, OR 3.43 (3.01, 3.92)
    prevalence of ILLICIT drug use rose over time; alcohol did not

Against 0.0368 the illicit figure is a ratio of about **7.5**. Two caveats, both
of which cut the same way: 86 of the 123 studies are in- or out-patient clinical
samples, which over-select comorbidity, and the estimates are largely lifetime
while the model's state is current.

**Nesvag et al. (2015), Soc Psychiatry Psychiatr Epidemiol.** Norwegian
registry, so a whole-population denominator rather than a clinical sample:

    any SUD      schizophrenia 25.1%   bipolar 20.1%   depressive 10.9%
    bipolar      AUD 8.1%   DUD 7.6%   both 4.4%

The bipolar DUD figure, 7.6%, is the closest like-for-like in this scan: a drug
use disorder, current, whole-population ascertainment. Against 0.0368 that is a
ratio of about **2.1**.

**Regier et al. (1990), JAMA, the ECA study.** The landmark, and the source of
the number most often quoted in this literature. Among people with a mental
disorder, the odds of any addictive disorder were **OR 2.7**, lifetime
prevalence about 29%. Running the other way, among those with a drug disorder
other than alcohol, 53% had a mental disorder, **OR 4.5**. Lifetime, any mental
disorder rather than SMI.

**NSDUH itself.** SAMHSA's Detailed Tables carry co-occurrence of mental
disorders with SUD broken out by SMI and by age band, so this number is
published and does not need the microdata. It could not be fetched here --
samhsa.gov is blocked by the egress proxy -- and the secondary sources found
give only broad-definition figures: around a quarter of SMI adults with a
co-occurring opioid use disorder by one estimate, "nearly half" with any SUD by
another, against 17.1% of the population 12+ with any SUD in 2023. Alcohol
included and all adults 18+, so the implied ratio near **1.5 to 1.8** is not on
the model's denominator and should not be used as one.

## Why the range is a definitional choice and not a measurement problem

    SMI = NSDUH's SMI          about 5.6% of adults      ratio ~1.5-2
    SMI = schizophrenia spectrum  about 0.5-1% of adults  ratio ~7.5

`DATA_APPENDIX.md` already carries this tension and states which side each
existing parameter sits on. `s_m(j)` is matched to NSDUH's SMI age profile at
5.6 per cent. `kappa_uem` is NOT: it is set to a 30 per cent employment rate
from the clinical high-disability literature, explicitly because *"In the 2024
public use file, among adults 26 and over, 58.0 percent of those with SMI are
employed against 57.5 percent of those without"* -- on NSDUH's own definition
there is almost no employment gap, so NSDUH's SMI cannot be the state that loses
work.

So the model currently takes its SMI POPULATION from NSDUH and its SMI SEVERITY
from the clinical literature. A comorbidity target has to pick one, and the two
picks differ by a factor of four.

## What this implies for the channel, given where the fix has got to

The mortality double-count fix is at a ratio of **2.207 at block 3** and still
rising (0.596 -> 1.928 -> 2.028 -> 2.207), not converged.

    if the target is the NSDUH reading, ~1.5-2     the fix has already passed it
    if the target is the clinical reading, ~7.5    the fix closes under a third

On the first reading the honest conclusion may be that no SMI channel is needed
and the comorbidity was an arithmetic error all along. On the second a channel
is needed and has to be large. **The extract decides it, and the extract has to
be run on NSDUH's SMI because that is the only definition the survey can give.**

If the answer comes back near 2 and the author wants the clinical reading
instead, that is an argument for a target from a registry study on a defined
severe population -- Nesvag is the template -- rather than from NSDUH at all.

## What was NOT found

No study in this scan reports drug use or drug use disorder among people with
SMI on the NSDUH `svyrdudany` definition at 26 and over, which is the only
figure that is directly a model moment. That is what
`NSDUH_2024_SMI_by_SUD_code.txt` computes.
