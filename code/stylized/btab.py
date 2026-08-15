"""The b values behind figure 1, so the recalibration is visible."""
import json, numpy as np
from stylized import P, with_
from calibrate import bracket, stats
from run import _scaled
base = with_(P(), **json.load(open('calibrated.json')))
sc = [0.0, 0.17, 0.33, 0.50, 0.67, 0.83, 1.0]
print(f"{'strength':>9s}{'b, mort':>10s}{'r_use':>9s}{'part':>8s}"
      f"{'b, res':>10s}{'r_use':>9s}{'part':>8s}")
for s in sc:
    row = []
    for which in ('mortality', 'resource'):
        p = _scaled(base, which, s); m = stats(p)
        row += [p.b, m['r_use'], m['part']]
    print(f"{100*s:8.0f}%{row[0]:10.5f}{row[1]:9.3f}{row[2]:8.4f}"
          f"{row[3]:10.5f}{row[4]:9.3f}{row[5]:8.4f}")
