"""
THE AUTHOR'S CALIBRATION METHOD, which is the quantitative model's.

    parameter <- parameter - adjuster * (moment - target)     for EVERY parameter
    re-solve ONCE
    repeat

WHY THIS REPLACES THE BRACKETING SWEEP.  Author, 12 September: *"but if you used
my method it should run very very fast!"*, *"you just adjust the parameters based
on my method"*, *"you just need to set up the updates correctly"*.  They are
right on both counts and the old sweep was wrong on both.

    bisection : 18 solves to move ONE parameter, every other one frozen,
                22 brackets a sweep = 396 solves, about 6.4 minutes
    this      : 2 solves to move ALL NINE (the second is omega_c's
                counterfactual), about 2 seconds

AND THE NON-MONOTONICITY THAT WRECKED FOUR SWEEPS WAS AN ARTIFACT OF BISECTION.
r_use is non-monotone in kap, participation looked non-monotone in b -- but
bisection REQUIRES monotonicity and finds the wrong root or a bound without it,
while this rule needs only the SIGN of each response, which is fixed and known.
The surface was never the problem; the solver was.

THE ASSIGNMENT, in the author's own words, 12 September:

    *"gamma rises when spending on rent to income ratio is below 26.8%, beta
    rises when it is below target, unemployment with SUD should rise if too few
    homeless with SUD, kappa is set to 3, h1 need to rise if homelessness is
    below 1%, h2 is just set to some exogenous number to give a decent renters
    spending over 50% on rent, omega_c needs to match the child gap, and it
    should rise if the child gap is too small, theta is held at 0.16, b needs to
    match the user rate, and should decline if user rate is too low, onset should
    match share of SUD and should rise if the SUD rate is too low"*,

    *"pi_eu should be chosen to match an unemployment rate of 4.85% as in the
    quant model"* and *"you raise pi_eu if the unemployment rate is below the
    data"*, and *"you also need aleph to match the value of life ... and you
    raise it if the value of life is too low"*.

EVERY SIGN IS +1 EXCEPT b.  "b should DECLINE if the user rate is too LOW" is
the opposite of the rule's default, and it is the economics rather than a slip:
b is the Stone-Geary shifter, so a SMALLER b makes abstaining costlier and pulls
MORE households into use.  A mechanical reading would have got this one backwards.

THE STEP IS RELATIVE, not absolute.  The Fortran carries the scale in each
parameter's own adjuster because each has been tuned by hand over months.  Here
the gap is divided by the target first, so one adjuster is meaningful across
parameters that range from 1e-4 (h_hl) to 15 (aleph).  It is the same rule with
the scale factored out.
"""
import math
import numpy as np

from calibrate import stats
from stylized import P, with_

# (name, moment, target, sign, adjuster, lo, hi)
# (name, moment, target, sign, adjuster, lo, hi).  SEVEN CALIBRATED.
#
# beta AND u1 ARE SET, not calibrated, and both for reasons measured today.
#   beta = 1, author: *"exogenous, not calibration"*, *"beta=1.47 is not
#     believable"*.  Calibrated on net worth over income of 3 it went to 1.477,
#     and to 1.621 at zero interest.  networth becomes an OUTPUT.
#   u1 = 0.1625, its MEASURED value.  It was never a free parameter -- the
#     declaration reads "RESOURCE: the disorder costs you a job. Measured." --
#     and aiming it at the SUD share of the homeless was a sign error: the ratio
#     FALLS in u1, because a bigger job-loss penalty deters use so hard the
#     disorder disappears and the numerator goes to zero.  sud_of_homeless2
#     becomes an OUTPUT; its ceiling is 0.084 against a target of 0.217.
SPEC = [
    ('gam',     'hspend',           0.268,   +1, 0.40, 0.05,  0.60),
    ('aleph',   'vsl',             80.0,     +1, 0.30, 3.0,  60.0),
    ('h_hl',    'homeless',         0.0100,  +1, 0.40, 1e-7,  0.05),
    ('b',       'part',             0.08901, -1, 0.30, 0.005, 0.30),
    ('pi_base', 'sud',              0.0368,  +1, 0.40, 1e-3,  0.99),
    ('u0',      'unemployment',     0.0485,  +1, 0.40, 0.005, 0.30),
    ('omega',   'child_gap',        0.1834,  +1, 0.30, 0.0,   1.50),
]

MAX_REL_STEP = 0.05          # nothing moves more than 5 per cent a pass
DAMP = 0.5                   # halve the adjuster when the gap flips sign
GROW = 1.2                   # grow it back while the sign holds
ADJ_FLOOR = 1e-3
CHILD_GAP_FLOOR = 0.1        # of the participation target, as the Fortran uses


def moments(par):
    """Every moment the spec needs, including the two that are not in aggregates."""
    m = dict(stats(par))
    # pi_eu's moment.  Employment is an i.i.d. draw, so the realised rate is u0
    # among the clean and u1 among those with the disorder.  Exact, no extra solve.
    m['unemployment'] = (1.0 - m['sud']) * par.u0 + m['sud'] * par.u1
    # omega_c's moment: use with the child term OFF against use with it on.  This
    # is the second solve, and it is what the Fortran spends a third of a loop on.
    # HELD when either population is too small for the ratio to mean anything --
    # the same guard, and the same reason: at a using mass near zero the ratio is
    # a statement about the denominator, not about internalisation.
    if par.omega > 0.0 and m['part'] > CHILD_GAP_FLOOR * 0.08901:
        off = stats(with_(par, omega=0.0))['part']
        m['child_gap'] = off / m['part'] - 1.0 if m['part'] > 0 else None
    else:
        m['child_gap'] = None
    return m


def step(par, m, state):
    """
    One pass of the author's rule over every parameter at once.

    WITH THE SIGN-FLIP RATCHET, which the first version left out and which is
    half the method.  Without it b swung 0.087 -> 0.168 -> 0.039 -> 0.101 and the
    child gap 0.894 -> 0.120 -> 1.125 across ten passes: the step overshoots, the
    gap changes sign, and the next step overshoots back.  The Fortran damps
    exactly this in damp_on_flip -- halve the adjuster when the gap flips, grow
    it back while the sign holds -- and every oscillating parameter here is one
    the Fortran already damps.
    """
    kw, moved = {}, []
    for name, mom, tgt, sgn, adj0, lo, hi in SPEC:
        v = m.get(mom)
        if v is None:                      # moment held this pass
            continue
        old = getattr(par, name)
        rel = (v - tgt) / tgt              # relative gap, so one adjuster fits all scales
        prev = state.get(name)
        adj = state.setdefault(name + '_adj', adj0)
        if prev is not None:
            adj = max(adj * DAMP, ADJ_FLOOR) if prev * rel < 0 else min(adj * GROW, adj0)
            state[name + '_adj'] = adj
        state[name] = rel
        new = old * (1.0 - sgn * adj * rel)
        room = MAX_REL_STEP * abs(old)
        new = max(min(new, old + room), old - room)
        new = max(min(new, hi), lo)
        kw[name] = new
        moved.append((name, old, new, 100 * rel))
    return with_(par, **kw), moved


def table(par, m, it):
    print(f'\n  ITERATION {it}')
    print(f'  {"param":9}{"value":>11}  {"moment":20}{"model":>10}{"target":>9}{"gap %":>8}')
    print('  ' + '-' * 70)
    gs = []
    for name, mom, tgt, *_ in SPEC:
        v = m.get(mom)
        if v is None:
            print(f'  {name:9}{getattr(par,name):11.5f}  {mom:20}{"HELD":>10}{tgt:9.4f}{"--":>8}')
            continue
        g = 100 * (v - tgt) / tgt
        gs.append(abs(g))
        print(f'  {name:9}{getattr(par,name):11.5f}  {mom:20}{v:10.4f}{tgt:9.4f}{g:8.1f}')
    print('  ' + '-' * 70)
    print(f'  worst {max(gs):.1f} %   median {sorted(gs)[len(gs)//2]:.1f} %   '
          f'{sum(1 for g in gs if g < 10)} of {len(gs)} inside ten')
    print(f'  OUTPUT  users income/mean {m["r_use"]:.4f}  drug share {m["dshare"]:.4f}'
          f'  networth {m["networth"]:.3f}  SUD of homeless {m["sud_of_homeless2"]:.4f}'
          f'  burden50 {m["burden50"]:.4f}')
    return max(gs)


if __name__ == '__main__':
    from recalibrate import FIXED, START
    # BETA IS EXOGENOUS AT 1, author 12 September: *"ok, i think we can just set
    # beta=1"*, *"exogenous, not calibration"*, *"beta=1.47 is not believable"*.
    # They are right: calibrating beta on a net worth to income ratio of 3 drove
    # it to 1.477 at the old positive interest rate and to 1.62 once interest was
    # set to zero -- a household that values a period thirty years away MORE than
    # the present.  networth leaves the target set with it and is reported.
    #
    # AND THE DIRECTION CONFIRMS WHAT WAS FLAGGED: removing a positive return
    # made saving less attractive, so beta rose rather than fell.
    par = with_(P(), **FIXED, **{k: v for k, v in START.items()}, beta=1.0)
    smr = 1 + math.log(1 - par.kap) / math.log(par.phi0)
    print(f"THE AUTHOR'S METHOD, sigma = 2, kappa SET at SMR {smr:.2f}")
    state = {}
    for it in range(240):
        m = moments(par)
        if it % 10 == 0 or it == 239:
            w = table(par, m, it)
            if w < 2.0:
                print('\n  every gap inside two per cent, stopping')
                break
        par, _ = step(par, m, state)
    print('\nFINAL')
    table(par, moments(par), 'final')
