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

Only channels that exist in the full model may appear here. A stylised model
resting on a shock the full model does not use is not an introduction to it.

Run:  python3 ablate.py
"""

import numpy as np
from stylized import P, with_
from calibrate import calibrate, stats


CHANNELS = [
    ('nothing removed', {}),
    ('the disorder kills you', dict(kap=0.0)),
    ('the disorder costs you a job', dict(u1=P.u0)),
    # h_hl is CALIBRATED, so setting it here and then recalibrating simply
    # resets it and the row measures nothing. It is structural in any case:
    # without the street being worse than a home there is no homelessness to
    # explain and no voucher worth having.
    ('recovery happens at all', dict(rho=0.0)),
    ('a small unit exists', dict(h_sm=P.h_lg)),
    ('income support is only half as generous', dict(repl=0.25)),
    ('income support is uncapped', dict(ycap=99.0)),
    ('households can save', dict(na=1)),
    ('life is worth much', dict(aleph=0.25)),
]


def evaluate(par, sweeps=3):
    """Full recalibration, then both counterfactuals."""
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
    print(f"{'removed':36s}{'part':>7s}{'r_use':>8s}"
          f"{'val life':>10s}{'moral hz':>10s}")
    ref = None
    for name, kw in CHANNELS:
        try:
            r = evaluate(with_(P(), **kw))
        except Exception as exc:
            print(f'{name:36s}   failed: {exc}')
            continue
        v = verdict(r, ref)
        if ref is None:
            ref = r
        print(f"{name:36s}{r['part']:7.4f}{r['r_use']:8.3f}"
              f"{r['vol']:10.2f}{r['mh']:10.2f}{v}")
    print('-' * 80)
    print('   r_use below one is result 1. The last two columns are result 2:')
    print('   a large negative value of life effect and a large positive moral')
    print('   hazard that nearly cancel.')
