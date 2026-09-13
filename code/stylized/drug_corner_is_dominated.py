"""In the corner every 'user' sits on the grid's smallest positive point.  The
onset hazard is FLAT -- pi_base at any v > 0 -- so that choice buys a
vanishing amount of drug utility and pays the FULL addiction risk, which
abstention dominates.  Do those households actually want to use?

Raise the grid's floor.  If they are choosing a dominated infinitesimal, they
abstain once the infinitesimal is removed and participation collapses.  If they
genuinely want positive use, participation survives at the higher floor."""
import sys
sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code/stylized')
from stylized import with_, P
from calibrate import stats
from recalibrate import FIXED

V = dict(gam=0.43696, aleph=10.70306, h1=0.00949, b=0.09103, pi_base=0.39839,
         u0=0.04850, u1=0.04860, delta_d=0.24, kap=0.16470, th=0.21520, beta=1.0)
base = with_(P(), **{k: v for k, v in FIXED.items()
                     if k not in ('kap','gam','omega')}, **V)

print("CORNER vector, omega = 0.01463")
print(f"{'grid floor v_lo':>16} {'part':>9} {'dshare':>11}")
print('-'*40)
for vlo in (1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 3e-2):
    m = stats(with_(base, omega=0.01463, v_lo=vlo))
    print(f"{vlo:16.0e} {m['part']:9.4f} {m['dshare']:11.7f}")
print()
print("INTERIOR vector, omega = 0.005, as a control")
print(f"{'grid floor v_lo':>16} {'part':>9} {'dshare':>11}")
print('-'*40)
for vlo in (1e-6, 1e-4, 1e-2):
    m = stats(with_(base, omega=0.005, v_lo=vlo))
    print(f"{vlo:16.0e} {m['part']:9.4f} {m['dshare']:11.7f}")
