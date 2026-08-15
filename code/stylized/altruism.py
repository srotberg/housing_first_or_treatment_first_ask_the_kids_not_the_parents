"""
Calibrate the weight parents put on their children, and check it is small.

THE CALIBRATION CONDITION

data/make_altruism_moment.py measures, in NSDUH 2024 among adults 26 and over,
the difference in past month illicit drug use between households with and
without a child, reweighting parents to the non parents' joint distribution over
age, income, sex and marital status. The ratio is 0.845, so switching the child
off would raise use by 18.4 per cent.

Every household in this model has a child, so there is no parent and non parent
comparison to run. The mapping is the counterfactual: omega is the entire reason
a household here uses less than it otherwise would, so at the calibrated
parameters, setting omega to zero must raise drug use by 18.4 per cent. That is
one equation in one unknown.

THE PROCEDURE

For a candidate omega, b is refitted so participation is on target WITH altruism
on, since that is the world the data describe. Then omega is set to zero at that
same b and participation is read off. The condition is

    participation(omega = 0, b(omega))  /  participation(omega, b(omega))  =  1.184

DELTA, the child's loss in lifetime utility from the income penalty, is held at
its baseline value rather than recomputed at each omega. The feedback is second
order: omega turns out to be small, so the child's world barely moves.

WHAT THIS IS FOR

The number is not itself a result. It is a check, before the same calibration is
run in the quantitative model, that the moment identifies omega at all and that
the answer lands somewhere a reader can accept. Altonji, Hayashi and Kotlikoff
(1997) reject operative altruism at the margin, so an omega anywhere near one
would mean the moment is picking up something other than altruism.

Run:  python3 altruism.py
"""

import json
import numpy as np
from stylized import P, with_
from calibrate import stats, _b_for
from internalise import delta_utility

# From data/make_altruism_moment.py. Past month is the headline; past year gives
# 1.236 and is reported as a range rather than a second calibration.
RISE_IF_OFF = 1.184
RISE_PY = 1.236


def use_ratio(par, omega, dlt, iters=18):
    """participation with altruism off, over participation with it on."""
    q = with_(par, omega=omega, chdmg=dlt)
    q = with_(q, b=_b_for(q, iters=iters))
    on = stats(q)['part']
    off = stats(with_(q, omega=0.0))['part']
    return off / max(on, 1e-12), q.b, on, off


def bracket_omega(par, dlt, target=RISE_IF_OFF, lo=1e-4, hi=0.30, iters=14):
    """omega is the unique weight delivering the observed counterfactual rise."""
    print(f'   target rise with altruism off : {100*(target-1):.1f}%')
    print(f'   {"omega":>9s}{"b":>11s}{"use on":>10s}{"use off":>10s}{"rise":>9s}')
    for _ in range(iters):
        mid = np.sqrt(lo * hi)
        r, b, on, off = use_ratio(par, mid, dlt)
        print(f'   {mid:9.5f}{b:11.6f}{100*on:9.3f}%{100*off:9.3f}%'
              f'{100*(r-1):8.1f}%')
        if r > target:
            hi = mid
        else:
            lo = mid
    return float(np.sqrt(lo * hi))


if __name__ == '__main__':
    base = with_(P(), **json.load(open('calibrated.json')))
    dlt = delta_utility(base)
    print('=' * 72)
    print('CALIBRATING THE WEIGHT ON THE CHILD')
    print('=' * 72)
    print(f'\n   child\'s loss in lifetime utility from the penalty : {dlt:.4f}')
    print()
    w = bracket_omega(base, dlt)
    print(f'\n   omega = {w:.4f}   (past month moment)')
    w2 = bracket_omega(base, dlt, target=RISE_PY, iters=12)
    print(f'\n   omega = {w2:.4f}   (past year moment)')
    print(f'\n   For reference, the stylized model\'s ranking between the two')
    print(f'   policies reverses back to Housing First only near omega = 0.43,')
    print(f'   so the calibrated weight is far inside the region where the')
    print(f'   externality still decides the comparison.')
