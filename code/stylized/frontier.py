"""
The (beta, theta) frontier, scanned rather than solved.

THE QUESTION. The stylized model has to do two things at once and they pull
against each other. It has to put a serious amount of drug spending in the hands
of users, because a model where users buy a hair above nothing is not a model of
drug use. And the mortality channel has to reverse the income gradient BY ITSELF
at its calibrated strength, because that reversal is the mechanism the paper
rests on: what makes the poor the users is that a SUD destroys a continuation
value, and the continuation value rises with permanent income.

Raising theta makes the drug worth more, which buys the spending share and
weakens the deterrent, until past a point the users are the rich and the result
runs backwards. Raising beta makes the future matter more, which strengthens the
deterrent and, at a fixed theta, CUTS the spending share, because a household
that fears the consequence more buys less of what causes it. So the two dials do
not substitute for each other and the question is what the pair can reach.

WHAT IS SCREENED. A point is admissible only if

    r_mort  < 1     mortality alone at full strength reverses the gradient
    r_unemp > 1     the resource channel alone does NOT, which is the contrast
    r_use   < 1     users are poorer than average at the full calibration
    minv1   > 0     no household prefers death: the VSL pins the discounted
                    continuation, so a larger beta buys a SMALLER aleph, and
                    aleph is the part of the continuation that does not shrink
                    with consumption. At beta = 1 this already fails.

and among the admissible points the best is the one with the LARGEST drug
spending share, since that is the moment being traded away.

WHERE THE SCREEN FAILS. TH_BREAK below is the theta at which r_mort first rises
above one, so it is the point past which the paper's mechanism is gone. The
footnote in Section 3.3 quotes it, and quotes it from here rather than typing
it, so a rerun of this scan that moves the crossing moves the sentence too.

WHY A SCAN AND NOT A SOLVE. Solving theta on a spending share target and then
reading the deterrent off answers one target at a time and hides the shape. The
share is bimodal in theta and the admissible window is narrow, so the useful
object is the whole curve: it shows where the branch jumps, how much share is
available just below the jump, and how far the window moves when beta does.

Run:  python3 frontier.py <beta_ann> <th> [<th> ...]
      One JSON file per point, so points can be split across processes.
"""
import json
import sys
import numpy as np
from stylized import P, with_, value1
from calibrate import stats, bracket, _b_for, YG, calibrate
from run import _scaled

# THE THETA AT WHICH THE MORTALITY SCREEN FAILS, read off the scan below rather
# than solved for: r_mort crosses one between 0.22 and 0.23 at the calibrated
# dispersion, so 0.23 is the first grid point where the model no longer says
# what it exists to say. Reproduce with `python3 frontier.py` and read the
# r_mort column. fill.py quotes it as @@th_break@@.
# MEASURED AT THE CURRENT CALIBRATION, not the one this file's scan was first
# run at. r_mort, the income ratio among users with the mortality channel alone
# at full strength, has to stay below one. At fully recalibrated points it runs
# 0.322 at theta 0.2334, 0.837 at 0.2429 and 1.285 at 0.2494, so it crosses at
# about 0.245. The old 0.23 was read off a scan at sigma_y = 0.75, a lambda
# targeting the use-to-disorder conversion rather than the adult rate, and h_2
# pinned at a quarter of h_3; all three have since changed.
TH_BREAK = 0.245

# THE DRUG SPENDING SHARE IS DISCONTINUOUS IN THETA, and both edges of that are
# quoted in the note, so both live here. Measured with lambda and b refit at
# every point: the share climbs 18.04, 18.39, 18.77, 18.84, 18.96 per cent over
# theta 0.2400 to 0.2460 and is 29.13 at 0.2480, so the lower branch tops out
# just under nineteen and the far branch starts near thirty. Twenty per cent,
# which the quantitative model targets, is in the gap.
DSHARE_TOP = 0.1896       # the top of the lower branch, at theta 0.2460

# WHERE THE MECHANISM GIVES OUT, which binds before the branch top does. r_mort
# crosses one at theta 0.245 and the share there, interpolated between the
# fully recalibrated points at 0.2429 and 0.2494, is 18.4 per cent.
DSHARE_CEIL = 0.184
# LAZY, NOT AT IMPORT. This used to read calibrated.json at module level, so
# importing anything from this file did file I/O against a relative path and
# failed from any other directory. fill.py imports TH_BREAK from here, so it has
# to be importable without touching the disk.
def _base():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    return with_(P(), **json.load(open(os.path.join(here, 'calibrated.json'))))


def at(beta_ann, th, sweeps=2):
    """
    theta with the WHOLE model recalibrated around it.

    Refitting aleph and b only is not enough, and the first version of this scan
    was wrong for that reason. lambda is bracketed on the adult SUD rate, and at
    a lower theta households use less, so a stale lambda leaves the disorder rate
    at half a per cent against a target of 3.68 and the drug spending share is
    then read off a model that is not calibrated. gamma and the street move too.
    Every point here is therefore a full calibration at a fixed theta, which is
    what makes the points comparable with each other and with the baseline.
    """
    q = with_(_base(), beta_ann=beta_ann, beta=beta_ann**30, R=1.0/beta_ann**30,
              th=th)
    return calibrate(q, sweeps=sweeps, verbose=False, fix=('th',),
                     checkpoint=f'checkpoint_front_{beta_ann}_{th:.3f}.json')


if __name__ == '__main__':
    ba = float(sys.argv[1])
    ths = [float(x) for x in sys.argv[2:]]
    rows = []
    print(f'beta_ann = {ba}', flush=True)
    print(f'{"theta":>7}{"aleph":>8}{"dshare":>9}{"part":>8}{"sud":>7}'
          f'{"r_use":>8}{"r_mort":>8}{"r_unemp":>9}{"minv1":>8}  ok', flush=True)
    for th in ths:
        q = at(ba, float(th))
        m = stats(q)
        rm = stats(_scaled(q, 'mortality', 1.0))['r_use']
        ru = stats(_scaled(q, 'unemployment', 1.0))['r_use']
        mv = float(min(value1(q, y, 'HF') for y in YG))
        ok = bool(rm < 1.0 and ru > 1.0 and m['r_use'] < 1.0 and mv > 0.0)
        rows.append(dict(beta_ann=ba, th=float(th), aleph=q.aleph, b=q.b,
                         dshare=m['dshare'], part=m['part'], sud=m['sud'],
                         r_use=m['r_use'], r_mort=rm, r_unemp=ru, minv1=mv,
                         ok=ok))
        print(f'{th:7.3f}{q.aleph:8.3f}{100*m["dshare"]:8.2f}%'
              f'{100*m["part"]:7.2f}%{100*m["sud"]:6.2f}%{m["r_use"]:8.2f}'
              f'{rm:8.2f}{ru:9.2f}{mv:8.2f}  {"YES" if ok else "no"}',
              flush=True)
        json.dump(rows[-1], open(f'front_{ba}_{th:.3f}.json', 'w'),
                  indent=1)
