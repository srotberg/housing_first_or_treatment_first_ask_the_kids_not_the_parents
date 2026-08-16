import json, time, numpy as np
from stylized import P, with_
from calibrate import stats, YG, W
from run import _scaled
t=time.time()
base = with_(P(), **json.load(open('calibrated.json')))
m = stats(base)
print('THREE PERIOD BASELINE at calibrated.json')
for k in ('part','sud','prog','dshare','r_use','homeless','sud_of_homeless','housing_share','vsl'):
    print(f'   {k:18s} {m[k]:.5f}')
print('   lam', base.lam, 'b', base.b, 'aleph', base.aleph, 'h_hl', base.h_hl, 'th', base.th, 'gam', base.gam)
uinc = float(((W/W.sum())*m['use']*YG).sum()/max(m['part'],1e-12))
vbar = float(((W/W.sum())*m['use']*m['v']).sum()/max(m['part'],1e-12))
print(f'   mean user income {uinc:.4f}   mean v {vbar:.6f}   lam*v {base.lam*vbar:.4f}')
print(f'   r_off  {stats(_scaled(base,"mortality",0.0))["r_use"]:.3f}')
print(f'   r_mort {stats(_scaled(base,"mortality",1.0))["r_use"]:.3f}')
print(f'   r_unem {stats(_scaled(base,"unemployment",1.0))["r_use"]:.3f}')
print('elapsed', time.time()-t)
