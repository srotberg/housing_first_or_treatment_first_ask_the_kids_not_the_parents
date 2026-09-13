"""
Which channels earn their place? Decided by ablation, not by taste.

THE PROCEDURE

For each channel: switch it off, run the FULL calibration again, and then rerun
both counterfactuals. A channel is kept only if it changes one of the two
qualitative results after the model has been refitted without it.

Recalibrating is the whole point. A channel can look important simply because
removing it throws the model off its targets, and it can look unimportant
because the other parameters have not been given the chance to compensate.
Neither tells you anything about the mechanism. Only refitting does.

    RESULT 1   users earn less than the population average
    RESULT 2   the two policy forces are large, opposite, and nearly cancel

THE CONSTRAINT

Only channels that exist in the full model may appear here. A stylized model
resting on a shock the full model does not use is not an introduction to it.

Run:  python3 ablate.py
"""

import json
import numpy as np
from stylized import P, with_
from calibrate import calibrate, stats


CHANNELS = [
    ('nothing removed', {}),
    ('the disorder kills you', dict(kap=0.0)),
    ('the disorder costs you a job', dict(u1=P.u0)),
    # h1 is CALIBRATED, so setting it here and then recalibrating simply
    # resets it and the row measures nothing. It is structural in any case:
    # without the street being worse than a home there is no homelessness to
    # explain and no voucher worth having.
    # recovery used to be a row here. rho is gone from the model: period 2 is
    # terminal, so there is no period to recover into and nothing to switch off.
    # h2 is READ OFF THE BASE at evaluation time, because the standard unit
    # is now calibrated and P.h3 is a stale starting value. Marked with a
    # sentinel and resolved in the loop.
    ('a small unit exists', 'collapse_h_sm'),
    ('income support is only half as generous', dict(repl=0.25)),
    # ('income support is uncapped', dict(ycap=99.0)) reads as 'remove' here and
    # that verdict is WRONG. This table only looks at the BASELINE, where the
    # mortality channel is on and users are poor, so the cap never binds. In
    # figure 1 the unemployment channel is scaled up on its own, users are rich,
    # and the cap is the only thing making the resource penalty less than
    # proportional to income. Uncapped, that curve is flat at 3.37 by
    # construction. The lesson is that this table is necessary and not
    # sufficient: a component also has to be tested where the figures put it.
    ('households can save', dict(na=1)),
    # This row does not calibrate and its numbers should not be read as a
    # recalibrated model. At aleph = 0.25 the continuation value goes NEGATIVE
    # for every household at or below average income, and W2(a=0, d=1) exceeds
    # W2(a=0, d=0): -0.68 against -0.70 at the mean. Having the disorder becomes
    # PREFERABLE, because it raises mortality and a shorter life is better when
    # life is worth less than nothing. Participation then sits above 60 per cent
    # at b = 0.3, 1.0 and 3.0 alike, so no value of b brings it back. aleph is
    # not a parameter that scales the results, it is what keeps their sign.
    ('life is worth much', dict(aleph=0.25)),
]


def evaluate(par, sweeps=6):
    """
    Full recalibration, then both counterfactuals.

    Six sweeps, and every row starts from the CALIBRATED point
    rather than from the defaults. Both changes exist so that the 'nothing
    removed' row reproduces the headline numbers of the note exactly. It used
    to land on -6.01 and +2.83 against a headline of -6.12 and +2.93, purely
    because it was a less converged calibration of the same model, and a reader
    comparing the two would reasonably have thought something was wrong.
    """
    par = calibrate(par, sweeps=sweeps, verbose=False)
    m = stats(par)
    p0 = stats(with_(par, pV=0.0, policy='HF'))['part']
    ph = stats(with_(par, pV=1.0, policy='HF'))['part']
    pt = stats(with_(par, pV=1.0, policy='TF'))['part']
    return dict(r_use=m['r_use'], part=m['part'], homeless=m['homeless'],
                vol=100.0 * (pt - p0), mh=100.0 * (ph - pt), par=par)


def verdict(r, ref):
    """
    Qualitative, not numerical. Result 1 is that users are poorer than average;
    result 2 is that the two forces are both large and opposite. A channel is
    removable only if neither statement changes.
    """
    if ref is None:
        return ''
    broke_1 = (r['r_use'] < 1.0) != (ref['r_use'] < 1.0) or \
              abs(r['r_use'] - ref['r_use']) > 0.25
    broke_2 = abs(r['vol'] - ref['vol']) > 1.0 or abs(r['mh'] - ref['mh']) > 1.0
    return '  KEEP' if (broke_1 or broke_2) else '  remove'


if __name__ == '__main__':
    print('=' * 80)
    print('WHICH CHANNELS EARN THEIR PLACE')
    print('   each row is FULLY recalibrated after the channel is removed,')
    print('   then both counterfactuals are rerun')
    print('=' * 80)
    # part and homeless are printed BECAUSE a row can fail to calibrate. The
    # single rental size row does: no value of h1 delivers the homelessness
    # rate once the small unit is gone, so its policy numbers come from a model
    # that missed its targets, and that has to be visible here.
    print(f"{'removed':36s}{'part':>7s}{'homeless':>10s}{'r_use':>8s}"
          f"{'val life':>10s}{'moral hz':>10s}")
    # THE TARGETS COME FROM THE DICT THE CALIBRATION BRACKETS AGAINST, not
    # typed here. Participation was retargeted from 5.13 per cent to 10.13 when
    # the two population rates were put on NSDUH's own severity split, and this
    # line went on printing 5.13 beside a model column that was fitted to 10.13.
    from calibrate import TARGET as _T
    print(f"{'   TARGETS':36s}{_T['part']:7.4f}{_T['homeless']:10.5f}")
    base = with_(P(), **json.load(open('calibrated.json')))
    ref = None
    for name, kw in CHANNELS:
        if kw == 'collapse_h_sm':
            kw = dict(h2=base.h3)
        try:
            r = evaluate(with_(base, **kw))
        except Exception as exc:
            print(f'{name:36s}   failed: {exc}')
            continue
        v = verdict(r, ref)[:2]
        if ref is None:
            ref = r
        print(f"{name:36s}{r['part']:7.4f}{r['homeless']:10.5f}"
              f"{r['r_use']:8.3f}{r['vol']:10.2f}{r['mh']:10.2f}{v}")
    print('-' * 80)
    print('   r_use below one is result 1. The last two columns are result 2:')
    print('   a large negative value of life effect and a large positive moral')
    print('   hazard that nearly cancel.')
