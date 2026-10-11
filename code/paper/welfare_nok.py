#!/usr/bin/env python3
"""WELFARE WITHOUT THE HOMELESSNESS DISAMENITY, kappa_x * H (10 October; the author: "can you take the old results and
compute all the welfare numbers without kappa_x H?", "kappa_x is not even in the optimization itself, you tack it on at
the end").

kappa_x enters no policy function. The Fortran subtracts kappa_x * H, H the aggregate share homeless, from the welfare
statistic after the solve: in every year of a child's childhood (calculate_childhood_utility, weight beta^(a-1)) and in
the adult value at 26 (compute_value_function_comparison), and its KAPPA_X PROBE measures the adult part at the
benchmark as 'beta^K * D_adult', the lifetime-level sensitivity per unit of kappa_x * H. Both pieces are linear in
kappa_x * H, so the term in any arm's lifetime value is kappa_x * H * K exactly, K = sum_{a=0}^{24} beta^a + beta^K D_adult,
and removing it is addition:

    W_free = W + kappa_x * H * K,

and the CEV without the term reads W_free off the benchmark's curve shifted by the benchmark's own term. The same
interpolation reproduces the Fortran's logged CEVs with the term to the third decimal (10 October: 4.337 against 4.337),
which is the check that the curve on disk is the one the Fortran used. beta^K D_adult is the benchmark's; it varies
across arms only with survival, a second-order effect on a term that is itself at most 0.2 utils.

Also here: the parts of a newborn's lifetime value (childhood, adult) without the term, used by export_welfare.py.
"""
import gzip
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
REF = os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085')


def _handover(path):
    d = {}
    for l in open(path):
        p = l.split()
        if len(p) >= 2:
            try:
                d[p[0]] = float(p[1])
            except ValueError:
                pass
    return d


_H = _handover(os.path.join(REF, 'PARAM_HANDOVER.bench.txt'))
BETA = _H['discount_factor']
KX0 = _H['kappa_x']
OMEGA_C = _H['weight_on_child']
XI = 2 ** 0.5                                   # the equivalence scale while the child is at home (Section 4.2)
CHILD_YEARS = 25
S_CHILD = sum(BETA ** a for a in range(CHILD_YEARS))
H0 = BKD = None
for _l in gzip.open(os.path.join(REF, 'bench.log.gz'), 'rt', errors='replace'):
    _m = re.search(r'KAPPA_X PROBE: H=\s*(\S+)\s+so beta\^K\*D_adult=\s*(\S+)', _l)
    if _m:
        H0, BKD = float(_m.group(1)), float(_m.group(2))
assert H0 and BKD, 'the benchmark log carries no KAPPA_X PROBE'
K = S_CHILD + BKD
ADULT_SENS = BKD / BETA ** CHILD_YEARS          # the same sensitivity at the level of the adult value at 26


def load_curve():
    p = os.path.join(REF, 'files', 'welfare_curvebaseline_benchmark.dat.gz')
    rows = [l.split() for l in gzip.open(p, 'rt') if l.strip()]
    xs = [float(r[0]) for r in rows]
    ws = [float(r[1]) for r in rows]
    assert all(b > a for a, b in zip(ws, ws[1:])), 'curve not increasing'
    return xs, ws


XS, WS = load_curve()
SHIFT0 = KX0 * H0 * K                            # the term in the benchmark's own lifetime value
WS_FREE = [w + SHIFT0 for w in WS]


# THE ADULT CURVE (the Fortran's 'WELFARE CURVE point k x= w=' lines: the entrants' value at 26 under consumption
# scaled by 1+x), so that the lifetime curve can be rebuilt with any weight on childhood: lifetime(x) =
# childhood(x) + beta^K adult(x), hence childhood(x) = lifetime(x) - beta^K adult(x). (11 October, the author:
# the child's childhood counts at xi-1 in the criterion, as it does in the household's equivalence scale; only
# omega_c separates the parent from the planner.)
_AD = {}
for _l in gzip.open(os.path.join(REF, 'bench.log.gz'), 'rt', errors='replace'):
    _m = re.search(r'WELFARE CURVE point\s+(\d+)\s+x=\s*(\S+)\s+w=\s*(\S+)', _l)
    if _m:
        _AD[int(_m.group(1))] = (float(_m.group(2)), float(_m.group(3)))
ADULT_CURVE = [_AD[k + 1][1] for k in range(len(XS))]
assert all(abs(_AD[k + 1][0] - XS[k]) < 1e-9 for k in range(len(XS))), 'adult and lifetime curves on different x'
B25 = BETA ** CHILD_YEARS
CHILD_CURVE = [w - B25 * a for w, a in zip(WS, ADULT_CURVE)]      # with the term, as the Fortran wrote it


def curve_for_weight(wc):
    """the lifetime curve WITHOUT the kappa_x term with the child's childhood counted at weight wc"""
    return [wc * (c + KX0 * H0 * S_CHILD) + (B25 * a + KX0 * H0 * BKD) for c, a in zip(CHILD_CURVE, ADULT_CURVE)]


def cev_of(t, ws=None):
    """quadratic Lagrange in w over the bracketing pair and a neighbour, as calculate_welfare_gains and cev.py"""
    ws = WS if ws is None else ws
    assert ws[0] <= t <= ws[-1], ('target off the curve', t, ws[0], ws[-1])
    i = next(k for k in range(1, len(ws)) if ws[k] >= t)
    j = max(1, min(i, len(ws) - 2))
    l0, l1, l2 = ws[j - 1], ws[j], ws[j + 1]
    d0 = (t - l1) * (t - l2) / ((l0 - l1) * (l0 - l2))
    d1 = (t - l0) * (t - l2) / ((l1 - l0) * (l1 - l2))
    d2 = (t - l0) * (t - l1) / ((l2 - l0) * (l2 - l1))
    return d0 * XS[j - 1] + d1 * XS[j] + d2 * XS[j + 1]


def arm_values(d):
    """W (the lifetime value, with the term), its childhood part C, the adult value at 26, kappa_x and H of the arm
    in directory d, from its cf.log.gz and final.txt; None where either file is missing"""
    log, fin = os.path.join(d, 'cf.log.gz'), os.path.join(d, 'final.txt')
    if not (os.path.exists(log) and os.path.exists(fin)):
        return None
    v = {'kx': KX0}
    for l in gzip.open(log, 'rt', errors='replace'):
        for key, name in (('average_welfare_with_childhood=', 'W'), ('average_childhood_utility=', 'C'),
                          ('average_welfare_of_youngest_cohort=', 'V26')):
            if key in l:
                v[name] = float(l.split('=')[1].split()[0])
        m = re.search(r'HANDOVER kappa_x:.*->\s*(\S+)', l)
        if m:
            v['kx'] = float(m.group(1))
        if 'CEV from the saved benchmark curve' in l:
            v['cev_logged'] = 100 * float(l.split('x=')[1])
    for l in open(fin):
        if l.strip().startswith('homelessness h_1'):
            v['H'] = float(l.split()[2])
    return v if 'W' in v and 'H' in v else None


def term(v):
    return v['kx'] * v['H'] * K


def cev_free(d):
    """the arm's CEV against the benchmark, per cent, without the term"""
    v = arm_values(d)
    assert v, f'no welfare to read in {d}'
    return 100 * cev_of(v['W'] + term(v), WS_FREE)


def cev_with(d):
    """the same with the term, which must agree with the Fortran's logged CEV"""
    v = arm_values(d)
    assert v, f'no welfare to read in {d}'
    return 100 * cev_of(v['W'], WS)


def components_free(v):
    """the child's childhood and the discounted adult part of the lifetime value, without the term"""
    C = v['C'] + v['kx'] * v['H'] * S_CHILD
    A = v['W'] - v['C'] + v['kx'] * v['H'] * BKD
    return C, A



def masses():
    """the Housing First newborns' masses over the 26 entry nodes (13 productivity nodes x a clean or penalised
    parent), from stage E2's newborn run"""
    m = {}
    for l in open(os.path.join(ROOT, 'results', 'transition_2c', 'newborn', 'shares.txt')):
        g = re.match(r'parent node\s+(\d+) class (\d) \(y=\S+\)\s+(\S+)\s', l)
        if g and (int(g.group(1)), int(g.group(2))) not in m:
            m[(int(g.group(1)), int(g.group(2)))] = float(g.group(3))
    assert len(m) == 26 and abs(sum(m.values()) - 1) < 1e-3, (len(m), sum(m.values()))
    return m


def v26(d):
    """the value at 26 by entry node of the re-solved arm in d (value_at_26_by_node.txt: 26 lines, nodes 1-13 with
    a clean parent, 14-26 penalised); it carries the arm's kappa_x * H term at the level of the value at 26"""
    v = [float(x) for x in open(os.path.join(d, 'value_at_26_by_node.txt')) if x.strip()]
    assert len(v) == 26, d
    return {(k + 1, 0): v[k] for k in range(13)} | {(k + 1, 1): v[13 + k] for k in range(13)}


def parts(arm_w, arm_n, base_w, base_n):
    """Treatment First (welfare files in arm_w, by-node values in arm_n) against Housing First (base_w, base_n),
    in utils of the newborn's lifetime value, without the kappa_x * H term:
      C  the child's childhood, the first term of the newborn's welfare, each policy's own
      A  the child's adult life, beta^J_K times the entrants' average value at 26, each policy's own entrants
      P  the parent's own lifetime value: the value at 26 by entry node under each policy, weighted by the Housing
         First newborns, so the same households are valued under both
      E  A - beta^J_K P: since the entrants' value at 26 is the same function in A and in P, this is exactly the
         composition term sum_s (m_TF(s) - m_HF(s)) V_TF(s), the gain from entering adult life on a better node
      worse  the share of the Housing First newborns on a node whose value at 26 falls"""
    m = masses()
    vb, va = arm_values(base_w), arm_values(arm_w)
    assert vb and va, (base_w, arm_w)
    Cb, Ab = components_free(vb)
    Ca, Aa = components_free(va)
    nb, na = v26(base_n), v26(arm_n)
    assert abs(sum(m[n] * nb[n] for n in m) - vb['V26']) < 0.05, 'by-node values do not average to the logged V26'
    P = sum(m[n] * (na[n] - nb[n]) for n in m) + (va['kx'] * va['H'] - vb['kx'] * vb['H']) * ADULT_SENS
    b25 = BETA ** CHILD_YEARS
    r = dict(C=Ca - Cb, A=Aa - Ab, P=P, Aown=b25 * P, E=Aa - Ab - b25 * P, b25=b25,
             worse=100 * sum(m[n] for n in m if na[n] < nb[n]))
    r['nb'] = r['C'] + r['A']
    r['eq'] = r['P'] + r['nb']
    return r


if __name__ == '__main__':
    print(f'beta {BETA:.5f}  kappa_x {KX0:.4f}  H0 {H0:.6f}  S_child {S_CHILD:.3f}  beta^K D_adult {BKD:.3f}  K {K:.3f}  '
          f'term in the benchmark {SHIFT0:.4f} utils')
