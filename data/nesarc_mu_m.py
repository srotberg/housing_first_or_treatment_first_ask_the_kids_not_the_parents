"""
mu_m from NESARC-III, which is the population sample the model wants.

WHY THIS SCRIPT. mu_m, the multiplier mental illness puts on the SUD recovery
hazard, was set at 0.82 from Bradizza et al. (2006), a review of TREATMENT
samples. The model applies it to the whole disordered population, not to people
entering treatment, so the universe is wrong even though the number may not be.
McCabe, West, Strobbe and Boyd (2018) run the same comparison on NESARC-III --
8,503 US adults with a prior-to-past-year DSM-5 SUD -- and this recovers the
multiplier from their Table 1.

THE INVERSION IS THE WHOLE POINT. Their Table 1 reports the composition of each
past-year outcome group BY comorbidity, which is P(comorbid | outcome). What
mu_m needs is P(outcome | comorbid), so the table is inverted against the
weighted outcome prevalences in their abstract. Reading the table the other way
round would give the answer to a different question.

Run:  python3 nesarc_mu_m.py
"""

# Weighted prevalence of each past-year outcome among adults with a prior SUD,
# from the abstract. They sum to 1.001 as published.
OUTCOME = {'abstinence': 0.142, 'asymptomatic': 0.369,
           'partial': 0.109, 'persistent': 0.381}

# Table 1: the share of each outcome group in each comorbidity category, and the
# category's share of the whole sample.
TABLE = {
    'mood': {
        'base_none': 0.609,
        'none': {'abstinence': 0.585, 'asymptomatic': 0.637,
                 'partial': 0.670, 'persistent': 0.573},
        'base_comorbid': 0.220,
        'comorbid': {'abstinence': 0.220, 'asymptomatic': 0.162,
                     'partial': 0.180, 'persistent': 0.288},
    },
    'anxiety': {
        'base_none': 0.715,
        'none': {'abstinence': 0.714, 'asymptomatic': 0.723,
                 'partial': 0.752, 'persistent': 0.696},
        'base_comorbid': 0.219,
        'comorbid': {'abstinence': 0.217, 'asymptomatic': 0.200,
                     'partial': 0.179, 'persistent': 0.248},
    },
}


def by_comorbidity(share_by_outcome, base):
    """Bayes: P(outcome | group) = P(group | outcome) P(outcome) / P(group)."""
    return {k: share_by_outcome[k] * OUTCOME[k] / base for k in OUTCOME}


def main():
    print(f'{"":34} {"none":>8} {"comorbid":>9} {"ratio":>7}')
    for name, t in TABLE.items():
        none = by_comorbidity(t['none'], t['base_none'])
        com = by_comorbidity(t['comorbid'], t['base_comorbid'])
        # TWO DEFINITIONS, because remission is not one object in that table.
        # "abstinent or asymptomatic" is the state with no symptoms; "not
        # persistent" also counts partial remission as out of the disorder.
        for label, f in (('abstinent or asymptomatic',
                          lambda d: d['abstinence'] + d['asymptomatic']),
                         ('not persistent/recurrent',
                          lambda d: 1 - d['persistent'])):
            a, b = f(none), f(com)
            print(f'{name + ", " + label:34} {a:8.3f} {b:9.3f} {b / a:7.3f}')
    print(f'\nBradizza et al. (2006), treatment samples: '
          f'{(1 - 0.398) / (1 - 0.264):.3f}')
    print('The model\'s SMI is the high-disability end, so the mood rows are the '
          'analogue;\n0.82 sits inside the range and next to them.')


if __name__ == '__main__':
    main()
