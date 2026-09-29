"""Why the SUD share of the homeless falls when u1 rises: the direct effect against the
two responses, who uses and what users save.  The author, 29 September: "if u1 is
higher, more of those with sud have no income and are more likely to be homeless".

Period-2 outcomes are always computed under the new u1.  The period-1 choices come
from the calibrated economy (BASE) or are re-chosen under the new u1 (NEW):
  FIXED        who uses from BASE, savings and housing from BASE  -> the direct effect
  SAVE         who uses from BASE, savings and housing from NEW   -> + savings respond
  WHO          who uses from NEW,  savings and housing from BASE  -> + who uses responds
  ALL          everything from NEW (b and kappa as calibrated)
  ALL REFIT    everything from NEW, b and kappa refit on participation and users'
               income (values from probe_u1_joint_s<stage>.log)
usage:  STYLIZED_WORKERS=1 python3 decompose_u1.py stage u1 [kap b]
"""
import sys
import numpy as np
import stylized as ST
import stage_results as R
from stylized import with_
from calibrate import YG, W, EDGES, CDF

stage, u1 = int(sys.argv[1]), float(sys.argv[2])
refit = dict(kap=float(sys.argv[3]), b=float(sys.argv[4])) if len(sys.argv) > 4 else None
par0, _ = R.load(stage)
_thr = ST.threshold


def thr(p):
    p = ST.solve_child_damage(p)
    return p, _thr(p, YG, p.policy, EDGES, CDF)


p0, T0 = thr(par0)


def run(tag, p_out, choices):
    ST.threshold = lambda *a, **k: choices
    try:
        m = ST.aggregates(p_out, YG, W, edges=EDGES, cdf=CDF)
    finally:
        ST.threshold = _thr
    PR, frac, VV, BU, BN, INC = choices
    w = np.asarray(W) / np.sum(W)
    ua = sum(w[i] * PR[i, s] * frac[i, s] * BU[i, s][0] for i in range(PR.shape[0])
             for s in range(PR.shape[1]) if PR[i, s] > 0) / max(m['part'], 1e-12)
    print(f'{tag:10s} u1 {p_out.u1:.4f}  SUD share of homeless {100*m["sud_of_homeless2"]:6.2f}  '
          f'P(homeless|SUD) {100*m["hl_sud"]/max(m["sud"],1e-12):5.2f}  users {100*m["part"]:5.2f}  '
          f'users/avg income {m["r_use"]:.2f}  users\' savings {ua:.3f}', flush=True)


run('BASE', p0, T0)
p1, T1 = thr(with_(par0, u1=u1))
PR0, f0, V0, BU0, BN0, I0 = T0
PR1, f1, V1, BU1, BN1, I1 = T1
run('FIXED', p1, T0)
run('SAVE', p1, (PR0, f0, V0, BU1, BN1, I1))
run('WHO', p1, (PR1, f1, V1, BU0, BN0, I0))
run('ALL', p1, T1)
if refit:
    p2, T2 = thr(with_(par0, u1=u1, **refit))
    run('ALL REFIT', p2, T2)
