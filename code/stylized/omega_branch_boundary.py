"""Does the child gap go to zero as omega_c goes to zero?  It must: the
counterfactual IS omega_c = 0, so at omega_c = 0 the two solves are the same
economy and the gap is identically zero.  At iteration 1300 the run reports
omega_c = 0.01463 with a gap of 0.38, which cannot both be true unless the two
solves are landing in different places."""
import sys
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P
from calibrate import stats
from recalibrate import FIXED

V = dict(gam=0.43696, aleph=10.70306, h1=0.00949, b=0.09103, pi_base=0.39839,
         u0=0.04850, u1=0.04860, delta_d=0.62141, kap=0.16470, th=0.21520,
         beta=1.0)
base = with_(P(), **{k: v for k, v in FIXED.items()
                     if k not in ('kap', 'gam', 'omega')}, **V)

print(f"{'omega':>9} {'part':>9} {'dshare':>9} | {'cf part':>9} {'cf dshare':>10} | "
      f"{'gap':>8} {'cf/base dshare':>15}")
print('-' * 82)
cf = stats(with_(base, omega=0.0))
for om in [0.20, 0.10, 0.05, 0.02463, 0.01463, 0.005, 0.001, 0.0001]:
    m = stats(with_(base, omega=om))
    gap = cf['part'] / m['part'] - 1.0 if m['part'] > 0 else float('nan')
    ratio = cf['dshare'] / max(m['dshare'], 1e-12)
    print(f"{om:9.5f} {m['part']:9.4f} {m['dshare']:9.4f} | "
          f"{cf['part']:9.4f} {cf['dshare']:10.4f} | {gap:8.4f} {ratio:15.4f}")
print("\nThe gap MUST tend to zero down the column.  The cf columns are constant "
      "by construction: the counterfactual does not depend on omega.")
