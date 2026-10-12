"""
Why omega_c = 1 barely moves drug use: the deterrent, decomposed.

Reads DeltaV_child from the near-benchmark log's expected_child_value= print and
the survival schedule from the Fortran source. No solve.
"""
import re, os, numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'code', 'housing_first_or_treatment_first_SR_v1.f90')
LOG = os.path.join(ROOT, 'code', 'variant_cf_20260910T161710Z.log')
BETA, KAPPA_PHI_D, V_NEWBORN = 0.934317, 8.0, 2195.0034506952861

src = open(SRC).read()
phi = np.array([float(x) for x in re.findall(
    r'0\.\d+', re.search(r'actual_survival_probability=\(/(.*?)/\)', src, re.S).group(1))])
assert len(phi) == 60

txt = open(LOG, 'rb').read().decode('utf8', 'replace')
last = None
for bl in re.findall(r'^ expected_child_value=((?:.|\n)*?)\n(?=\s*[A-Za-z\-])', txt, re.M):
    v = [float(x) for x in re.findall(r'-?\d+\.\d+(?:[EeDd][+-]?\d+)?', bl)]
    if len(v) == 56 and any(abs(z) > 1e-12 for z in v):
        last = np.array(v).reshape(2, 2, 14)      # (h, d, k), k fastest
dv = last[0, 1]                                    # h=1, d=1: the differenced penalty
print(f'DeltaV_child by productivity node: {dv.min():.1f} .. {dv.max():.1f} utils')
print(f'newborn lifetime value            : {V_NEWBORN:.1f} utils')
print(f'ratio at the low nodes (the margin): {100*abs(dv.min())/V_NEWBORN:.2f}%')

add = 1.0 - np.minimum(1.0, KAPPA_PHI_D * (1.0 - phi))

def W(surv, a):
    """Discounted probability of dying from age index a, staying in this regime."""
    w, alive = 0.0, 1.0
    for t in range(a - 1, 60):
        w += BETA ** (t - (a - 1)) * alive * (1.0 - surv[t])
        alive *= surv[t]
    return w

print(f'\n{"age":>4}{"data":>6}{"1-phi clean":>13}{"1-phi SUD":>11}{"W clean":>10}{"W SUD":>8}')
for a in (1, 6, 11, 21, 31):
    print(f'{a:4d}{24+a:6d}{1-phi[a-1]:13.5f}{1-add[a-1]:11.5f}{W(phi,a):10.4f}{W(add,a):8.4f}')

det = abs(dv.min()) / V_NEWBORN * W(add, 6)
print(f'\nQUANTITATIVE deterrent at omega_c=1, age 30 : {100*det:.2f}% of a life')
print(f'STYLIZED   deterrent at omega  =1 (rationed): {100*0.332192/3.42834:.2f}% of a life')
print(f'RATIO                                       : {(0.332192/3.42834)/det:.1f}')
