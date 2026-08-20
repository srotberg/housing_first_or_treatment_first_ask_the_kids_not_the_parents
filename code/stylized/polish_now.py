"""
Polish the checkpoint and write calibrated.json.

Used when a sweep loop has converged in everything but the structural
homelessness residual and the remaining sweeps would only reproduce it. It runs
exactly the pass calibrate.py's __main__ runs after its sweeps.
"""
import json
from calibrate import polish, report, PAIRS, P, with_

kw = json.load(open('calibrated.json'))
seed = with_(P(), **{k: v for k, v in kw.items()
                     if k in {n for n, _, _, _ in PAIRS}})
print(f'polishing the checkpoint; theta is set at {seed.th:.4f}', flush=True)
par = polish(seed)
report(par)
json.dump({n: getattr(par, n) for n, _, _, _ in PAIRS}
          | {'th': par.th, 'gam': par.gam},
          open('calibrated.json', 'w'), indent=1)
print('\nwrote calibrated.json')
