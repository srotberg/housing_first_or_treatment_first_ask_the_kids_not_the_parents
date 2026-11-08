"""
WHY THE PARTIAL-EQUILIBRIUM FALL IN DRUG USE IS NOT THE 61 PER CENT (8 November; the author: "where the PE drug use
decline is different, put a footnote explaining why they are different than the 61% in calibration of p_det").

The detection rate is set to the share of the users who FACE the screen and stop on impact (x_ws_tested_all_pc,
export_whostops.py), against Mehay and Pacula's 61. The experiments report the long-run fall in drug use over ALL
households. Both come from the same impact runs, so this reads them again, for each experiment's calibrated rate:

    x_<e>_tested_users_pc   the users who face the screen, as a share of all users under Housing First (t_used over
                            drug use b times the population mass, the reference's voucher-state masses)
    x_<e>_impact_drop_pc    the fall in drug use over all households on impact (MOMENT b, the screen's run against
                            the reference's, on the same fixed distribution)
    x_<e>_untested_drop_pc  the same fall among the users who do NOT face the screen
    x_<e>_lr_vs_impact      'larger' or 'smaller': the long-run fall against the impact fall, from the long-run name

for e = ws (the main experiment, 0.20, results/whostops_2c_C_pts_0p10_0p20), om1 (omega_c = 1, 0.15,
results/whostops_omega1_pts_0p15_0p20) and nx (the first experiment, its own rate: results/noext_pdet/columns_pdet.txt,
the point's run in results/noext_pdet, noext_pdet_x or noext_pdet_1_p<rate>, each with its own reference). For nx also
x_nx_pdet_pc and x_nx_stop_pc. The long-run falls are x_dcb_b_pc (export_longrun.py), x_om1_bdrop_held
(export_omega1.py) and x_pe_b_pc (export_longrun.py): RUN THIS AFTER THEM.

usage: python3 code/paper/export_impact.py   -> merged into code/paper/results_numbers.json
"""
import glob
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RES = os.path.join(ROOT, 'results')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')


def last(path, key):
    with gzip.open(path, 'rt', errors='replace') as f:
        L = [l for l in f if key in l]
    assert L, (path, key)
    return L[-1]


def nums(line):
    return [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', line.replace('=', ' = '))]


def impact(ref, tf):
    mass = sum(nums(last(ref, 'DIAG voucher-state mass')))
    b_ref = nums(last(ref, 'MOMENT b '))[0]
    b_tf = nums(last(tf, 'MOMENT b '))[0]
    v = nums(last(tf, 'DIAG who stops'))
    assert len(v) == 13 and v[0] == 1, v
    t_used, t_stop = v[7], v[8]
    users = b_ref * mass
    return {'stop': 100 * t_stop / t_used,
            'tested_users': 100 * t_used / users,
            'impact_drop': 100 * (1 - b_tf / b_ref),
            'untested_drop': 100 * ((users - t_used) - (b_tf * mass - (t_used - t_stop))) / (users - t_used)}


def names(e, r, longrun):
    out = {f'x_{e}_tested_users_pc': f"{r['tested_users']:.0f}",
           f'x_{e}_impact_drop_pc': f"{r['impact_drop']:.0f}",
           f'x_{e}_untested_drop_pc': f"{r['untested_drop']:.0f}"}
    if longrun is not None:
        out[f'x_{e}_lr_vs_impact'] = 'larger' if float(longrun) > r['impact_drop'] else 'smaller'
    return out


def main():
    cur = json.load(open(OUT_JSON))
    out = {}
    W = os.path.join(RES, 'whostops_2c_C_pts_0p10_0p20')
    out.update(names('ws', impact(os.path.join(W, 'cfarm_null_imp_wsref', 'cf.log.gz'),
                                  os.path.join(W, 'cfarm_tf_imp_ws_p200', 'cf.log.gz')), cur.get('x_dcb_b_pc')))
    O = os.path.join(RES, 'whostops_omega1_pts_0p15_0p20')
    out.update(names('om1', impact(os.path.join(O, 'cfarm_null_imp_wo1ref', 'cf.log.gz'),
                                   os.path.join(O, 'cfarm_tf_imp_wo1_p150', 'cf.log.gz')), cur.get('x_om1_bdrop_held')))
    # the first experiment, once its rate is chosen and the point's log is in
    cp = os.path.join(RES, 'noext_pdet', 'columns_pdet.txt')
    if os.path.exists(cp):
        p = float(open(cp).read().split()[0])
        t = 'nx_p%03d' % round(1000 * p)
        hits = [d for d in glob.glob(os.path.join(RES, 'noext_pdet*', f'cfarm_tf_imp_{t}', 'cf.log.gz'))]
        if hits:
            d = os.path.dirname(os.path.dirname(hits[0]))
            r = impact(os.path.join(d, 'cfarm_null_imp_nxref', 'cf.log.gz'), hits[0])
            out.update(names('nx', r, cur.get('x_pe_b_pc')))
            out['x_nx_pdet_pc'] = f'{100 * p:g}'
            out['x_nx_stop_pc'] = f"{r['stop']:.0f}"
        else:
            # until the point's log is saved (at the end of run_noext_pdet.sh's scan), the share that stops from the
            # status line the job publishes for each point
            st = os.path.join(RES, 'noext_pdet', 'status.txt')
            M = [m for m in re.finditer(r'detection ([0-9.]+): ([0-9.]+) per cent of ALL tested', open(st, errors='replace').read())
                 if abs(float(m.group(1)) - p) < 1e-9]
            if M:
                out['x_nx_pdet_pc'] = f'{100 * p:g}'
                out['x_nx_stop_pc'] = f"{float(M[-1].group(2)):.0f}"
            print(f'  (the first experiment: no log for {t} yet; the share that stops from the status line)')
    cur.update(out)
    json.dump(cur, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')


if __name__ == '__main__':
    main()
