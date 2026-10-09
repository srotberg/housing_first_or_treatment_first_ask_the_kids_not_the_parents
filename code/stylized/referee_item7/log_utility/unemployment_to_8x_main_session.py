"""The unemployment channel alone at the log calibration, 0 to 8 times its calibrated strength, b refitted at every
point as gradient.scan does; saving off and on."""
import sys, json
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import numpy as np
import gradient as g
q = {**g.FIXED, 'sigma': 1.0, 'aleph': 3.691033434406929, 'b': 0.0030032655688011878,
     'theta': 0.16519793514966266, 'kappa': 11.954205318975035, 'cbar': 0.09953514675321687}
for save in (False, True):
    qq = {**q, 'save': save}
    ref = g.moments({**q, 'save': True})['part']
    c0 = g.channel(qq, 'unemployment', 0.0)
    ysg = g.Dist(c0['sig_y'], c0['y_min']).quantile(1.0 - ref)
    b = c0['theta'] * ysg / ((1.0 - c0['theta']) * c0['p_v'])
    row = []
    for x in np.arange(0.0, 8.01, 0.25):
        c = g.channel(qq, 'unemployment', float(x))
        if c['u1'] >= 1.0:
            break
        c['b'] = b = g.b_for_part(c, ref, b)
        m = g.moments(c)
        row.append((float(x), float(c['u1']), float(m['r_use'])))
    print('saving' if save else 'no saving', flush=True)
    print('  ' + '  '.join(f'x={x:.2f} (u1={u:.2f}): {r:.2f}' for x, u, r in row if abs(x * 4 - round(x * 4)) < 1e-9 and (x % 0.5 == 0)), flush=True)
