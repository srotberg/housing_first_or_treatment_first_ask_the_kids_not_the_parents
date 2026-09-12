"""If the corner's drug share is an economic quantity it will not care what the
grid's smallest positive point is.  If it IS the smallest positive point, it
will scale one-for-one with it."""
import sys
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P
from calibrate import stats
from recalibrate import FIXED

V = dict(gam=0.43696, aleph=10.70306, h_hl=0.00949, b=0.09103, pi_base=0.39839,
         u0=0.04850, u1=0.04860, delta_d=0.24, kap=0.16470, th=0.21520, beta=1.0)
base = with_(P(), **{k: v for k, v in FIXED.items()
                     if k not in ('kap','gam','omega')}, **V)

print(f"{'v_lo':>10} {'omega':>8} {'part':>9} {'dshare':>11} {'dshare/v_lo':>13}")
print('-'*56)
for vlo in (1e-4, 1e-5, 1e-6):
    for om in (0.01463, 0.005):
        m = stats(with_(base, omega=om, v_lo=vlo))
        print(f"{vlo:10.0e} {om:8.5f} {m['part']:9.4f} {m['dshare']:11.7f} "
              f"{m['dshare']/vlo:13.1f}")
print()
print("dshare tracking v_lo one-for-one => the 'users' are pinned on the grid's")
print("smallest positive point, so the corner's drug share is a property of the")
print("GRID.  dshare unchanged across v_lo => it is an economic quantity.")
