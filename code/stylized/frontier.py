"""
The (beta, theta) frontier: can this model carry a large drug spending share AND
a mortality channel that reverses the income gradient on its own?

The two are in tension. Raising theta makes the drug worth more, which buys the
spending share and weakens the deterrent, until past a point the users are the
rich and the result the model exists to produce runs backwards. Raising beta
makes the future matter more, which strengthens the deterrent and, at a fixed
theta, cuts the spending share because a household that fears the consequence
more buys less of the thing that causes it.

So neither dial alone does it, and the question is whether the pair does: at a
higher beta, is there a theta that puts the spending share back at 20 per cent
while the mortality channel still reverses the gradient by itself?

For each beta this solves theta on the spending share, refitting aleph on the
value of a statistical life and b on participation at every trial, and then reads
off what the mortality channel does alone at full strength.

Run:  python3 frontier.py
"""
import json
import numpy as np
from stylized import P, with_
from calibrate import stats, bracket, _b_for, TARGET
from run import _scaled

BASE = with_(P(), **json.load(open('calibrated.json')))
TH_LO, TH_HI = 0.150, 0.320


def refit(par):
    """aleph on the VSL and b on participation, which is what any theta has to
    be read at: both move when theta does."""
    q = with_(par, aleph=bracket(par, 'aleph', 'vsl', 0.05, 40.0, iters=26))
    return with_(q, b=_b_for(q, iters=24))


def at(beta_ann, th):
    q = with_(BASE, beta_ann=beta_ann, beta=beta_ann**30, R=1.0/beta_ann**30,
              th=th)
    return refit(q)


def solve_th(beta_ann, target=0.20, iters=17):
    lo, hi = TH_LO, TH_HI
    for _ in range(iters):
        mid = 0.5 * (lo + hi)
        if stats(at(beta_ann, mid))['dshare'] > target:
            hi = mid
        else:
            lo = mid
    return 0.5 * (lo + hi)


if __name__ == '__main__':
    print(f'{"beta_ann":>9}{"theta":>8}{"aleph":>8}{"dshare":>9}{"part":>8}'
          f'{"r_use":>8}{"r_mort":>8}{"r_unemp":>9}', flush=True)
    for ba in (0.9950, 0.9960, 0.9970, 0.9975, 0.9980):
        th = solve_th(ba)
        q = at(ba, th)
        m = stats(q)
        rm = stats(_scaled(q, 'mortality', 1.0))['r_use']
        ru = stats(_scaled(q, 'unemployment', 1.0))['r_use']
        print(f'{ba:9.4f}{th:8.4f}{q.aleph:8.3f}{100*m["dshare"]:8.2f}%'
              f'{100*m["part"]:7.2f}%{m["r_use"]:8.2f}{rm:8.2f}{ru:9.2f}',
              flush=True)
