"""export_mortality.py -- the mortality consequences of the main experiment (11 November; the AE's suggestion, which the
author asked to add: "add 3"). Writes code/paper/mortality_numbers.json, read by splice.py:

  x_mort_dd0, x_mort_dd1   deaths at ages 26 to 44 caused by a SUD, percent of all deaths at those ages, under Housing First
                           and under Treatment First in the main experiment (the run's 'drug deaths, share of deaths': the
                           deaths that would not have happened at the clean hazard, with age, homelessness and SMI held)
  x_mort_le_weeks          the rise in life expectancy at 26, in weeks, in words: each cohort enters at mass one, so the
                           population's mass (the last DIST_MOM line) is the expected number of years lived from 26
"""
import gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'stylized'))
import rulec_paths as R   # noqa: E402
import fill                # noqa: E402


def read(d):
    log = gzip.open(os.path.join(d, 'cf.log.gz'), 'rt', errors='replace').read()
    dd = float(re.findall(r'UNTARGETED drug deaths, share of deaths\s+model=\s*(\S+)', log)[-1])
    mass = float(re.findall(r'DIST_MOM .*?mass=\s*(\S+)', log)[-1])
    return dd, mass


dd0, m0 = read(R.NULL_DIR)
dd1, m1 = read(R.TF_DIR)
weeks = (m1 - m0) * 365.25 / 7
out = {'x_mort_dd0': f'{100 * dd0:.1f}', 'x_mort_dd1': f'{100 * dd1:.1f}', 'x_mort_le_weeks': fill._word(int(round(weeks)))}
json.dump(out, open(os.path.join(HERE, 'mortality_numbers.json'), 'w'), indent=1)
print(out, f'(life expectancy at 26: {m0:.3f} -> {m1:.3f} years, +{weeks:.1f} weeks)')
