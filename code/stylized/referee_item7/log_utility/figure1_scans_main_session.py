"""Figure 1's four scans at the log-utility calibration (sigma = 1, all five parameters refitted), as gradient.scan
does them: one channel from 0 to 200 per cent with the other off, b refitted to hold participation, saving on/off."""
import sys, json, time
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
import numpy as np
import gradient as g
D = '/tmp/claude-0/-home-user-housing-first-or-treatment-first/43825369-02f4-5759-bc82-a1a582111d14/scratchpad/logcal/'
q = {**g.FIXED, 'sigma': 1.0, 'aleph': 3.691033434406929, 'b': 0.0030032655688011878,
     'theta': 0.16519793514966266, 'kappa': 11.954205318975035, 'cbar': 0.09953514675321687}   # the cloud's converged log calibration
m = g.moments(q); print('log calibration check', {k: round(m[k], 4) for k in ('part', 'r_use', 'dshare', 'vsl', 'fshare')}, flush=True)
bench = {**g.FIXED, **{k: v for k, v in json.load(open('/home/user/housing_first_or_treatment_first/code/stylized/gradient.json')).items()}}
out = {}
for name, qq in (('log', q), ('sigma2', bench)):
    for which in ('mortality', 'unemployment'):
        for save in (True, False):
            t = time.time()
            try:
                sc, r = g.scan({**qq, 'save': save}, which, n=21)
                i1 = int(np.argmin(abs(sc - 1.0)))
                out[f'{name}_{which}_{save}'] = dict(x=sc.tolist(), r=r.tolist())
                print(f'{name:6s} {which:12s} saving={str(save):5s} r(0)={r[0]:.2f} r(0.5)={r[i1//2]:.2f} r(1)={r[i1]:.2f} r(1.5)={r[(i1+len(r)-1)//2]:.2f} r(2)={r[-1]:.2f}  {time.time()-t:.0f}s', flush=True)
            except Exception as e:
                print(f'{name} {which} saving={save} FAILED {e!r}', flush=True)
            json.dump(out, open(D + 'scans_log.json', 'w'))
print('DONE', flush=True)
