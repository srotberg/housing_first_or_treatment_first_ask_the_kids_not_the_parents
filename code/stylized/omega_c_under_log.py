"""
DOES omega_c SURVIVE LOG UTILITY? Measured, not argued.

The question is whether the CONTEMPORANEOUS child term of CHILD_FLOW_UTILITY.md
is a channel of its own or a reparameterisation of parameters that are already
calibrated.  It decides whether the stylized model can be written at sigma = 1.

    X_P = (c/xi)^phi_c (h/xi)^phi_h (bbar+q)^phi_q
    X_K = (c/xi)^phi_c (h/xi)^phi_h  bbar^phi_q
    V   = u(X_P) + omega_c*(xi-1)*u(X_K)

UNDER LOG IT IS NOT A CHANNEL.  X_K differs from X_P only by the constant
bbar^phi_q, so with u = log the whole thing collapses to

    V = A*[phi_c log(c/xi) + phi_h log(h/xi)] + phi_q log(bbar+q) + aleph + const

with A = 1 + omega_c*(xi-1).  Dividing by A gives the omega_c = 0 model with
theta -> theta/A and aleph -> aleph/A.  BOTH ARE CALIBRATED PARAMETERS, so an
ablation of omega_c under log returns an empty row by construction and not by
economics.

MEASURED, optimal q at five incomes, omega_c = 0.09 against omega_c = 0 with
theta refit.  Housing held at h_lg, static allocation, no continuation:

    LOG (sigma = 1)              SIGMA = 2
    income   ratio               income   ratio
      0.20   1.0059                0.20   1.0138
      0.50   1.0057                0.50   1.0061
      1.00   1.0056                1.00   1.0000
      2.00   1.0056                2.00   0.9934
      5.00   1.0056                5.00   0.9838

Flat to four decimals over a 25-fold range of income under log: the SAME
reweighting at every income, which is exactly what cannot move an income
gradient.  At sigma = 2 the ratio swings three per cent and CROSSES ONE, and the
sign says omega_c cuts use harder at the top than at the bottom, so it steepens
the gradient.  That is the same direction as the quantitative model's measured
omega_c effect and the opposite of the FOC argument that was withdrawn.

WHAT THIS DOES NOT COVER.  The continuation half of omega_c -- the child's value
function carrying delta_d -- survives log perfectly well, because the child's
value function is not a constant multiple of the parent's flow.  Only the
contemporaneous half dies.  So log remains available for a model in which
omega_c acts through the child's value function alone.
"""

import numpy as np

# The approved flow utility, CHILD_FLOW_UTILITY.md:
#   X_P = (c/xi)^phi_c (h/xi)^phi_h (bbar+q)^phi_q
#   X_K = (c/xi)^phi_c (h/xi)^phi_h  bbar^phi_q
#   V   = u(X_P) + omega_c*(xi-1)*u(X_K),   u(x)=x^(1-s)/(1-s)
xi  = np.sqrt(2.0); kap = xi - 1.0
gam, th = 0.20516, 0.16
phc, phh, phq = (1-gam)*(1-th), gam*(1-th), th
bbar, h = 0.0024, 0.40

def vstar(x, om, s, thq=phq):
    """optimal drug quantity out of resources x, on a fine grid."""
    pc, ph = (1-gam)*(1-thq), gam*(1-thq)
    q = np.linspace(0.0, 0.95*x, 200001)
    c = np.maximum(x - q, 1e-12)
    lP = pc*np.log(c/xi) + ph*np.log(h/xi) + thq*np.log(bbar+q)
    lK = pc*np.log(c/xi) + ph*np.log(h/xi) + thq*np.log(bbar)
    if s == 1.0:
        V = lP + om*kap*lK
    else:
        V = (np.exp(lP)**(1-s) + om*kap*np.exp(lK)**(1-s))/(1-s)
    return q[int(np.argmax(V))]

A = 1.0 + 0.09*kap
print("A = 1 + omega_c*(xi-1) =", round(A, 6))
print()
print("LOG (sigma=1): is omega_c=0.09 the same economy as omega_c=0 at theta/A?")
print(f"{'income':>8}{'v, om=0.09':>13}{'v, om=0, th/A':>15}{'ratio':>9}")
for x in (0.2, 0.5, 1.0, 2.0, 5.0):
    a = vstar(x, 0.09, 1.0, phq)
    b = vstar(x, 0.00, 1.0, phq/A)
    print(f"{x:8.2f}{a:13.6f}{b:15.6f}{a/max(b,1e-12):9.4f}")
print()
print("SIGMA=2: same comparison, best single theta' refit at income 1.0")
x0 = 1.0; tgt = vstar(x0, 0.09, 2.0, phq)
lo, hi = 1e-4, phq
for _ in range(60):
    mid = 0.5*(lo+hi)
    if vstar(x0, 0.00, 2.0, mid) < tgt: lo = mid
    else: hi = mid
thp = 0.5*(lo+hi)
print(f"theta' that matches v at income 1.0: {thp:.6f}  (theta/A would be {phq/A:.6f})")
print(f"{'income':>8}{'v, om=0.09':>13}{'v, om=0, th prime':>19}{'ratio':>9}")
for x in (0.2, 0.5, 1.0, 2.0, 5.0):
    a = vstar(x, 0.09, 2.0, phq)
    b = vstar(x, 0.00, 2.0, thp)
    print(f"{x:8.2f}{a:13.6f}{b:19.6f}{a/max(b,1e-12):9.4f}")
