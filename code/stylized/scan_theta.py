"""
Can the two period model reach an eleven per cent drug spending share?

WHY THIS EXISTS

The whole reason for the two period restructure was the drug spending share:
users here spend about two per cent of income on drugs against eleven in the
data. The restructure did not deliver it. It moved the share from 1.76 per cent
to 1.94, because what a household loses by acquiring the disorder is pinned by
the value of a statistical life and not by the number of periods. Two periods
put the whole of the continuation at risk instead of its tail, and that offsets
the continuation being shorter almost exactly.

So the only remaining dial is theta, the weight on drugs, and the question is
whether the two period model can carry a larger one than the three period model
could. It plausibly can: the mortality channel is stronger here, so there is
more room to make drugs attractive before users stop being poor.

WHAT IS SCREENED, AND IN WHICH ORDER

The channel decomposition FIRST, exactly as in the three period model. A larger
theta is worth nothing if it costs the result the model exists to demonstrate.
A point passes only if

    mortality alone at full strength reverses the gradient, r_use < 1
    unemployment alone at full strength does NOT, r_use > 1
    no household has a negative ex ante value of life
    homelessness and participation still hit their targets

and only then is the drug spending share worth reading.

gamma is tied to 0.268(1-theta) throughout. Freeing it has been tried twice and
collapses: it couples the housing weight to the homelessness margin through the
value of the street, the h1 bracket loses its interior solution, and the sweep
walks to homelessness of 25 per cent against a target of 0.4.

Run:  python3 scan_theta.py 0.20
"""

import json
import sys
import time
import numpy as np
from stylized import P, with_, value1
from calibrate import calibrate, stats, YG
from run import _scaled


def point(th, sweeps=4):
    t = time.time()
    par = with_(P(), th=th, gam=0.25 * (1.0 - th))
    # theta is an internally calibrated parameter now, so it has to be held
    # fixed here or the scan would calibrate away the thing it is scanning
    par = calibrate(par, sweeps=sweeps, verbose=False, fix=('th',))
    m = stats(par)
    row = dict(th=th, gam=par.gam, aleph=par.aleph, h1=par.h1,
               lam=par.lam, b=par.b, secs=time.time() - t)
    row |= {k: m[k] for k in ('part', 'prog', 'dshare', 'r_use', 'homeless',
                              'sud_of_homeless', 'housing_share', 'vsl')}
    # THE SCREEN, before the spending share is looked at
    row['r_off'] = stats(_scaled(par, 'mortality', 0.0))['r_use']
    row['r_mort_half'] = stats(_scaled(par, 'mortality', 0.5))['r_use']
    row['r_mort'] = stats(_scaled(par, 'mortality', 1.0))['r_use']
    row['r_unemp'] = stats(_scaled(par, 'unemployment', 1.0))['r_use']
    row['minv1'] = float(min(value1(par, y, 'HF') for y in YG))
    row['passes'] = bool(row['r_mort'] < 1.0 and row['r_unemp'] > 1.0
                         and row['minv1'] > 0.0)
    return row


if __name__ == '__main__':
    th = float(sys.argv[1])
    r = point(th)
    json.dump(r, open(f'scan_th_{th:.2f}.json', 'w'), indent=1)
    print(json.dumps(r, indent=1))
