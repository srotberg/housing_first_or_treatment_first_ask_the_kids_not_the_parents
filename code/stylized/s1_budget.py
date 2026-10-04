"""
STAGE 1 AT THE SAME COST (round r140; the author, 4 October: "if you remove the externalities, and balance the budget
with piv, holding pv fixed, in the stylized model, could TF be better?").

Section 3's dominance result compares the two programmes at the same generosity pi_V. Treatment First then pays out
slightly less, because it withholds the voucher from those that fail the sobriety condition. This spends what it saves:
Treatment First's pi_V is raised until it costs exactly what Housing First costs at the benchmark pi_V, the drug price
p_v fixed as it always is in the stylized model, and the two are compared household by household as dominance() does.

usage:  python3 s1_budget.py   -> merges s1_bb_* into stage_numbers.json (nothing else is touched)

  s1_bb_pv_pc    how much higher pi_V is under the budget-balanced Treatment First, percent
  s1_bb_better   households strictly better off under it than under Housing First, percent (grid nodes, as s1_better_b)
  s1_bb_cevpop   the population CEV of Housing First over it, percent: what the average household would give up to
                 keep Housing First (s1_cevpop_b is the same at the same pi_V)
"""
import json
import os

import numpy as np

import stage_results as SR
from stylized import with_, value1, use_prob
import calibrate as C
from welfare import cev

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'stage_numbers.json')


def tf_pv_at_cost(par, target):
    """the pi_V at which Treatment First costs target (cost rises in pi_V)"""
    lo, hi = par.pV, min(1.0, par.pV * 1.2)
    while SR.outcomes(par, 'TF', hi)['cost'] < target and hi < 1.0:
        lo, hi = hi, min(1.0, hi * 1.2)
    while hi - lo > 1e-8:
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if SR.outcomes(par, 'TF', mid)['cost'] < target else (lo, mid)
    return 0.5 * (lo + hi)


def main():
    par, _ = SR.load(1)
    pV = par.pV
    hf = SR.outcomes(par, 'HF', pV)
    pT = tf_pv_at_cost(par, hf['cost'])
    tf = SR.outcomes(par, 'TF', pT)
    assert abs(tf['cost'] / hf['cost'] - 1) < 1e-5, (tf['cost'], hf['cost'])
    ww = C.W / C.W.sum()
    qh = SR.ready(with_(par, policy='HF', pV=pV))
    qt = SR.ready(with_(par, policy='TF', pV=pT))
    vh = np.array([value1(qh, y, 'HF') for y in C.YG])
    vt = np.array([value1(qt, y, 'TF') for y in C.YG])
    pi = np.array([par.pi_base * use_prob(qh, y, 'HF') for y in C.YG])
    lam = cev(par, vh - vt, v_level=vh, pi=pi)
    names = {
        's1_bb_pv_pc': f'{100 * (pT / pV - 1):.2f}',
        's1_bb_better': f'{100 * float((ww * (vt > vh + 1e-9)).sum()):.1f}',
        's1_bb_cevpop': f'{100 * float((ww * lam).sum()):.2g}',
    }
    d = json.load(open(OUT))
    d.update(names)
    json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
    print(f'pi_V {pV:.6f} -> {pT:.6f}; cost {hf["cost"]:.6f}; worse off '
          f'{100 * float((ww * (vt < vh - 1e-9)).sum()):.1f} percent (grid nodes)')
    for k, v in names.items():
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
