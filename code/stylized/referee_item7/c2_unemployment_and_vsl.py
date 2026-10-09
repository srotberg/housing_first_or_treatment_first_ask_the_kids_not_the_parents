"""Referee item 7, claim C, the other half of the paper's insurability argument: the unemployment channel
alone (kappa = 1), with and without saving, under the same specifications as c_curvature_scan.py, b refitted
to hold participation.  Also the VSL at mean income in each specification at the calibrated kappa.
usage: python3 code/stylized/referee_item7/c2_unemployment_and_vsl.py
"""
import json, os, sys
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c_curvature_scan import G, Q, PART, VARIANTS  # noqa: E402

XS = [round(0.05 * i, 2) for i in range(161)]   # u1 = u0 + x (u1 - u0), steps of 0.05 as Figure 1; x = 8.4 is u1 = 1
SHOW = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0)


def run(job):
    var, save = job
    q0 = {**Q, **VARIANTS[var], 'kappa': 1.0, 'save': save}
    dist = G.Dist(q0['sig_y'], q0['y_min'])
    b = q0['theta'] * dist.quantile(1.0 - PART) / ((1.0 - q0['theta']) * q0['p_v'])
    out = []
    for x in XS:
        g = {**q0, 'u1': Q['u0'] + x * (Q['u1'] - Q['u0'])}
        try:
            g['b'] = b = G.b_for_part(g, PART, b)
            m = G.moments(g)
            if x not in SHOW:
                continue
            out.append((x, round(m['r_use'], 3), [(round(100 * float(dist.F(lo)), 1), round(100 * float(dist.F(hi)), 1))
                                                   for lo, hi in m['intervals']]))
        except Exception as e:  # noqa: BLE001
            out.append((x, None, repr(e)[:80]))
            break
    return job, out


if __name__ == '__main__':
    for v in ('base', 'log', 'vslprop'):
        print(f'VSL at mean income, calibrated kappa, {v}: {G.vsl({**Q, **VARIANTS[v]}):.1f} annual incomes')
    jobs = [(v, s) for v in ('base', 'log', 'vslprop') for s in (True, False)]
    with Pool(os.cpu_count()) as pool:
        for (v, s), out in pool.map(run, jobs, chunksize=1):
            print(f'\nunemployment channel alone, {v}, saving {"on" if s else "off"}: (x, users income/mean, band percentiles)')
            for r in out:
                print('  ', r)
