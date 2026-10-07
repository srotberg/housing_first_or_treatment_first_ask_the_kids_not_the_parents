"""
ENDOGENOUS CHILDREN IN THE STYLIZED MODEL -- A TEST, NOT YET A STAGE.

The author, 7 October: "We drop the deltad thing.... And keep the model fully endogenous and the
child choice is endogenous", "if you have a child, you get some constant utility benefit each
period even after the child left", and "We can start with the stylized model... to see how the
results change".

WHAT IS CHOSEN.  At the start of adulthood, before its period 1 employment and voucher draws, a
household of productivity y chooses whether to have a child.

  * A PARENT shares its consumption and housing with the child in period 1 (xi), weighs the
    child's flow at omega, and gets the warm glow psi in every period it is alive, period 1 and
    period 2, after the child has left too (P.glow, added in _flow like aleph).
  * A NON-PARENT has xi = 1, no child term and no warm glow.
  * delta_d is zero for both: the child's productivity does not depend on the parent's disorder.

THE TASTE SHOCK.  Each household draws an idiosyncratic logit taste for children at the decision
and carries nothing of it afterwards, so the share choosing a child at income y is
1 / (1 + exp(-(V_c(y) - V_n(y)) / s)) and no state is added.  psi sets the level of fertility,
s its dispersion across incomes.

THE POPULATION.  Each generation's productivity is drawn afresh from the base distribution, as the
stylized rest point already does once delta_d is zero, so who has children does not change the
next generation's distribution and the population is replaced by construction.

What this file reports is a comparison at given parameters, exogenous against endogenous
children; the calibration of psi and s to their targets is in calibrate_fertility below.

usage: python3 fertility.py            (the test at the stage 2 parameters)
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stages                                    # noqa: E402  (installs the zero child damage)
import calibrate as C                            # noqa: E402
from stylized import with_, value1, aggregates   # noqa: E402

WW = C.W / C.W.sum()

# NSFG 2017-2019, ages 40-49 (data/nsfg_births_by_drug_use.py, the scratchpad nsfg_overall.py):
# 79.7 percent have had a child; past-year users 71.0 against 81.5 for non-users.
PARENT_SHARE = 0.797
USER_PARENT_RATIO = 0.710 / 0.815
# NSDUH 2024 (data/make_altruism_moment.py): non-parents use 18.34 percent more than parents
# reweighted to the non-parents' characteristics.
CHILD_GAP = 1.0 / 0.845 - 1.0


def groups(par, psi):
    """The parent's and the non-parent's parameters, delta_d zero for both."""
    pc = stages._solve_or_zero(with_(par, delta_d=0.0, glow=psi), par.policy)
    pn = stages._solve_or_zero(with_(par, delta_d=0.0, xi=1.0, omega=0.0, glow=0.0), par.policy)
    return pc, pn


def values(par, psi, policy=None):
    pc, pn = groups(par, psi)
    Vc = np.array([value1(pc, y, policy) for y in C.YG])
    Vn = np.array([value1(pn, y, policy) for y in C.YG])
    return pc, pn, Vc, Vn


def share(Vc, Vn, s):
    z = np.clip((Vc - Vn) / s, -700.0, 700.0)
    return 1.0 / (1.0 + np.exp(-z))


def mixed(par, psi, s, policy=None):
    """Moments of the economy where each household chooses whether to have a child."""
    policy = policy or par.policy
    pc, pn, Vc, Vn = values(par, psi, policy)
    P = share(Vc, Vn, s)
    A = aggregates(pc, C.YG, WW * P, policy, C.EDGES, C.CDF, raw=True)
    B = aggregates(pn, C.YG, WW * (1.0 - P), policy, C.EDGES, C.CDF, raw=True)
    t = {k: A[k] + B[k] for k in A if k not in ('use',)}
    Mc, Mn = float((WW * P).sum()), float((WW * (1.0 - P)).sum())
    ybar = float((WW * C.YG).sum())
    fn = WW * (1.0 - P) / max(Mn, 1e-12)
    use_np = float((fn * B['use']).sum())
    use_p_rw = float((fn * A['use']).sum())
    users_p, users_n = A['part'], B['part']
    par_user = users_p / max(users_p + users_n, 1e-12)
    par_nonuser = (Mc - users_p) / max((Mc - users_p) + (Mn - users_n), 1e-12)
    return dict(
        part=t['part'], sud=t['sud'], homeless=t['hl'] / max(t['mass'], 1e-12),
        sud_of_homeless2=t['hl_sud'] / max(t['hl2'], 1e-12),
        dshare=t['spend'] / max(t['uinc'], 1e-12),
        r_use=(A['yuse'] + B['yuse']) / max(t['part'], 1e-12) / ybar,
        hspend=t['hcost'] / max(t['hexp'], 1e-12),
        parent_share=Mc,
        part_parents=users_p / max(Mc, 1e-12), part_nonparents=users_n / max(Mn, 1e-12),
        user_parent_ratio=par_user / max(par_nonuser, 1e-12),
        child_gap=use_np / max(use_p_rw, 1e-12) - 1.0,
        P=P, Vc=Vc, Vn=Vn)


def mixed_stats(par):
    """calibrate.stats() for the economy with children chosen (par.fert = 1): every moment the
    stage calibration reads, plus the three fertility ones, parents and non-parents added
    before any ratio is formed."""
    from stylized import vsl, priced_out_share
    policy = par.policy
    base = with_(par, fert=0)
    pc, pn, Vc, Vn = values(base, par.psi, policy)
    P = share(Vc, Vn, par.fert_s)
    A = aggregates(pc, C.YG, WW * P, policy, C.EDGES, C.CDF, raw=True)
    B = aggregates(pn, C.YG, WW * (1.0 - P), policy, C.EDGES, C.CDF, raw=True)
    t = {k: A[k] + B[k] for k in A if k != 'use'}
    Mc, Mn = float((WW * P).sum()), float((WW * (1.0 - P)).sum())
    ybar = float((WW * C.YG).sum())
    fn = WW * (1.0 - P) / max(Mn, 1e-12)
    use_np, use_p_rw = float((fn * B['use']).sum()), float((fn * A['use']).sum())
    users_p, users_n = A['part'], B['part']
    par_user = users_p / max(users_p + users_n, 1e-12)
    par_nonuser = (Mc - users_p) / max((Mc - users_p) + (Mn - users_n), 1e-12)
    p1 = float(np.interp(0.0, np.log(C.YG), P))          # the share with a child at y = 1
    use = WW * 0 + (P * A['use'] + (1.0 - P) * B['use'])
    m = dict(part=float(t['part']), sud=float(t['sud']),
             dshare=float(t['spend'] / max(t['uinc'], 1e-12)),
             prog=float(t['sud'] / max(t['part'], 1e-12)),
             r_use=float((A['yuse'] + B['yuse']) / max(t['part'], 1e-12) / ybar),
             homeless=float(t['hl'] / max(t['mass'], 1e-12)),
             sud_of_homeless=float(t['hl_sud'] / max(t['hl'], 1e-12)),
             sud_of_homeless2=float(t['hl_sud'] / max(t['hl2'], 1e-12)),
             hl2=float(t['hl2']), hl_sud=float(t['hl_sud']),
             housing_share=float(t['hcost'] / max(t['hinc'], 1e-12)),
             hsmall=float(t['smallmass'] / max(t['housedmass'], 1e-12)),
             burden50=float(t['burden'] / max(t['mass1'], 1e-12)),
             networth=float(t['wealth'] * par.years / max(t['winc'], 1e-12)),
             hspend=float(t['hcost'] / max(t['hexp'], 1e-12)),
             fshare=float(t['fsp'] / max(t['lab'], 1e-12)),
             cost=float(t['cost']), use=use, v=None,
             parent_share=Mc, part_parents=users_p / max(Mc, 1e-12),
             part_nonparents=users_n / max(Mn, 1e-12),
             user_parent_ratio=par_user / max(par_nonuser, 1e-12),
             child_gap=use_np / max(use_p_rw, 1e-12) - 1.0)
    m['vsl'] = p1 * vsl(pc) + (1.0 - p1) * vsl(pn)
    m['bot50'] = C._bottom_half_share(C.SIG)
    m['priced_out'] = priced_out_share(pc, C.YG, C.W)
    m['P'] = P
    return m


def psi_for_share(par, s, target=PARENT_SHARE, policy=None, lo=-50.0, hi=50.0, iters=40):
    """The warm glow that makes `target` of households have a child, at taste dispersion s.
    The values of having and not having a child are solved once at psi = 0 and the glow is
    then added in closed form only for the BISECTION; the final moments are re-solved at it,
    since the glow also moves the drug choice through the value of staying alive."""
    pc0, pn0, Vc0, Vn0 = values(par, 0.0, policy)
    # how much one unit of glow adds to V_c: one period-1 unit plus the expected period-2 one
    _, _, Vc1, _ = values(par, 1.0, policy)
    dV = Vc1 - Vc0
    f = lambda g: float((WW * share(Vc0 + g * dV, Vn0, s)).sum()) - target
    a, b = lo, hi
    for _ in range(iters):
        m = 0.5 * (a + b)
        if f(m) > 0:
            b = m
        else:
            a = m
    return 0.5 * (a + b)


if __name__ == '__main__':
    import stage_results as SR
    os.environ.setdefault('STYLIZED_WORKERS', '2')
    par, _ = SR.load(2)
    print(f'stage 2 parameters: omega {par.omega:.5f}, xi {par.xi:.4f}, b {par.b:.5f}, aleph {par.aleph:.3f}')
    for pol in ('HF', 'TF'):
        q = with_(par, policy=pol)
        ex = C.stats(stages._solve_or_zero(with_(q, delta_d=0.0), pol))
        print(f'\n{pol}, EXOGENOUS children (everyone a parent), delta_d 0: participation {100*ex["part"]:.2f}, '
              f'SUD {100*ex["sud"]:.3f}, homeless {100*ex["homeless"]:.3f}, users/average income {ex["r_use"]:.2f}')
        for s in (0.05, 0.5, 5.0):
            psi = psi_for_share(q, s, policy=pol) if pol == 'HF' else PSI[s]
            if pol == 'HF':
                PSI = globals().setdefault('PSI', {}); PSI[s] = psi
            m = mixed(q, psi, s, pol)
            print(f'  ENDOGENOUS, s {s:5.2f}, psi {psi:8.4f}: parents {100*m["parent_share"]:.1f}%, '
                  f'participation {100*m["part"]:.2f} (parents {100*m["part_parents"]:.2f}, non-parents '
                  f'{100*m["part_nonparents"]:.2f}), user/non-user parenthood {m["user_parent_ratio"]:.3f} '
                  f'[data {USER_PARENT_RATIO:.3f}], child gap {100*m["child_gap"]:+.1f}% [data +18.3], '
                  f'SUD {100*m["sud"]:.3f}, homeless {100*m["homeless"]:.3f}')
