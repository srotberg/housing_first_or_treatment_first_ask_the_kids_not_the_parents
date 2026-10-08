"""Numbers the paper quotes from published studies, each with its page, so the prose reads them as @@name@@ like
every other number (writing/NUMBERS.md). Writes code/paper/lit_numbers.json.

Mehay, S. L. and R. L. Pacula (1999), "The effectiveness of workplace drug prevention policies: does 'zero tolerance'
work?", NBER Working Paper 7383 (the author's copy, 8 October). Any illicit drug use in the past year, ages 17-49:
  military 1995 6.5, civilians 1995 14.7 (Table 1, p. 25); military 1980 35.7, civilians 1979 27.6 (Table 4, p. 28).
  "the deterrence effect for the military program would range between 4% and 16%" (p. 21): percentage points, as the
  4 is their 30-day difference in differences "about 4 percentage points (10.12 - 14.97 = -4.85)" (p. 15).
  NLSY, past-year marijuana, those who stayed in the military 1980-84: 48.5 -> 13.2; stayed civilian: 45.8 -> 32.0
  (Table 6, p. 30).
Viscusi, W. K. and J. E. Aldy (2003), J. Risk and Uncertainty 27(1): income elasticity of the value of a statistical life
  about 0.5 to 0.6 (cross-section). Costa, D. L. and M. E. Kahn (2004), J. Risk and Uncertainty 29(2), "Changes in the
  value of life, 1940-1980": 1.5 to 1.7 (over time).
"""
import json, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'code', 'paper', 'lit_numbers.json')
mp = dict(mp_mil_py95_pc=6.5, mp_civ_py95_pc=14.7, mp_mil_py80_pc=35.7, mp_civ_py79_pc=27.6, mp_lo_pp=4, mp_hi_pp=16,
          mp_stay_mil80_pc=48.5, mp_stay_mil84_pc=13.2, mp_stay_civ80_pc=45.8, mp_stay_civ84_pc=32.0)
# the stayers' relative fall net of the civilian trend: 1 - (13.2/48.5)/(32.0/45.8)
mp['mp_stay_rel_pc'] = round(100 * (1 - (mp['mp_stay_mil84_pc'] / mp['mp_stay_mil80_pc']) /
                                    (mp['mp_stay_civ84_pc'] / mp['mp_stay_civ80_pc'])))
mp.update(va_el_lo=0.5, va_el_hi=0.6, ck_el_lo=1.5, ck_el_hi=1.7)
out = {k: (f'{v:.1f}' if isinstance(v, float) else f'{v}') for k, v in mp.items()}
json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(out)
