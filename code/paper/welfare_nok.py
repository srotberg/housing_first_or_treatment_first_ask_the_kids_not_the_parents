#!/usr/bin/env python3
"""THE PAPER'S WELFARE CRITERION, READ FROM THE SAVED ARMS: without the homelessness disamenity kappa_x * H, and
with the child's childhood counted at xi - 1.

1. kappa_x (10 October; the author: "can you take the old results and compute all the welfare numbers without
   kappa_x H?", "kappa_x is not even in the optimization itself, you tack it on at the end"). kappa_x enters no policy
   function. The Fortran subtracts kappa_x * H, H the aggregate share homeless, from the welfare statistic after the
   solve: in every year of a child's childhood (calculate_childhood_utility, weight beta^(a-1)) and in the adult value
   at 26 (compute_value_function_comparison), and its KAPPA_X PROBE measures the adult part at the benchmark as
   'beta^K * D_adult', the lifetime-level sensitivity per unit of kappa_x * H. Both pieces are linear in kappa_x * H,
   so the term in an arm's lifetime value is kappa_x * H * K exactly, K = sum_{a<25} beta^a + beta^K D_adult, and
   removing it is addition. Reading the arms WITH the term off the curve on disk reproduces the Fortran's logged CEVs
   to the third decimal (4.337 against 4.337), which is the check that the curve is the one the Fortran used.

2. The weight on childhood (11 October; the author: "the child's count [should be] (xi(j)-1) ... just omega_c is
   different ... otherwise you are attributing an externality unrelated to weight on the child at all"). The
   household's flow is U(X_P) + omega_c (xi(j) - 1) U(X_c): the child enters at its equivalence weight xi - 1, and
   omega_c is the share of that the parent internalises (Section 4.10: "only 1 - omega_c remains external"). The
   criterion therefore counts the child's childhood flow at xi - 1 as well, so that only omega_c separates the parent
   from the planner; the Fortran's own welfare statistic counts it at one, so every lifetime value here is rebuilt as
   (xi - 1) C + A from the logged childhood C and adult part A, and the benchmark's curve is rebuilt the same way from
   its adult curve (the Fortran's 'WELFARE CURVE point' lines) and its lifetime curve file: childhood(x) =
   lifetime(x) - beta^K adult(x).

The Bench class holds a benchmark's handover, curves and kappa_x probe, so the omega_c = 0.686 sensitivity reads its
arms off its own benchmark the same way.
"""
import gzip
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
XI = 2 ** 0.5                                   # the equivalence scale while the child is at home (Section 4.2)
CHILD_WEIGHT = XI - 1                           # the child's weight in the criterion (11 October)
CHILD_YEARS = 25


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


def lagrange(t, xs, ws):
    """quadratic Lagrange in w over the bracketing pair and a neighbour, as calculate_welfare_gains and cev.py"""
    assert ws[0] <= t <= ws[-1], ('target off the curve', t, ws[0], ws[-1])
    i = next(k for k in range(1, len(ws)) if ws[k] >= t)
    j = max(1, min(i, len(ws) - 2))
    l0, l1, l2 = ws[j - 1], ws[j], ws[j + 1]
    d0 = (t - l1) * (t - l2) / ((l0 - l1) * (l0 - l2))
    d1 = (t - l0) * (t - l2) / ((l1 - l0) * (l1 - l2))
    d2 = (t - l0) * (t - l1) / ((l2 - l0) * (l2 - l1))
    return d0 * xs[j - 1] + d1 * xs[j] + d2 * xs[j + 1]


class Bench:
    """a benchmark's handover, kappa_x probe and welfare curves (ref: a directory with PARAM_HANDOVER.bench.txt,
    bench.log.gz and files/welfare_curvebaseline_benchmark.dat.gz, or the curve file's path as curve)"""

    def __init__(self, ref, curve=None):
        self.ref = ref
        # the curve file: files/welfare_curvebaseline_benchmark.dat.gz under ref unless given (results/deltah keeps it at
        # the top level)
        curve = curve or os.path.join(ref, 'files', 'welfare_curvebaseline_benchmark.dat.gz')
        h = _handover(os.path.join(ref, 'PARAM_HANDOVER.bench.txt'))
        self.beta, self.kx, self.omega = h['discount_factor'], h['kappa_x'], h['weight_on_child']
        self.b25 = self.beta ** CHILD_YEARS
        self.s_child = sum(self.beta ** a for a in range(CHILD_YEARS))
        self.H0 = self.bkd = None
        ad = {}
        for l in gzip.open(os.path.join(ref, 'bench.log.gz'), 'rt', errors='replace'):
            m = re.search(r'KAPPA_X PROBE: H=\s*(\S+)\s+so beta\^K\*D_adult=\s*(\S+)', l)
            if m:
                self.H0, self.bkd = float(m.group(1)), float(m.group(2))
            m = re.search(r'WELFARE CURVE point\s+(\d+)\s+x=\s*(\S+)\s+w=\s*(\S+)', l)
            if m:
                ad[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
        assert self.H0 and self.bkd, f'{ref}: the benchmark log carries no KAPPA_X PROBE'
        self.K = self.s_child + self.bkd
        self.adult_sens = self.bkd / self.b25            # the same sensitivity at the level of the value at 26
        rows = [l.split() for l in gzip.open(curve, 'rt') if l.strip()]
        self.xs = [float(r[0]) for r in rows]
        self.ws = [float(r[1]) for r in rows]                       # the lifetime curve, childhood at one, with the term
        assert all(b > a for a, b in zip(self.ws, self.ws[1:])), 'curve not increasing'
        assert len(ad) == len(self.xs) and all(abs(ad[k + 1][0] - self.xs[k]) < 1e-9 for k in range(len(self.xs))), \
            f'{ref}: adult and lifetime curves on different x'
        # WHICH PARTS CARRY THE TERM (checked against the re-solved no-policy arm, 11 October): the lifetime curve
        # file carries it in both parts (the arm's W matches the file at x = 0 to 1e-3), while the log's adult curve
        # is WITHOUT it (the arm's V26 sits kappa_x * H * D_adult below it). So the childhood part with the term is
        # lifetime(x) - beta^K (adult(x) - kappa_x H0 D_adult), and the kappa_x-free curve adds the childhood term.
        self.adult = [ad[k + 1][1] for k in range(len(self.xs))]    # the value at 26 under 1+x, WITHOUT the term
        self.adult_term = self.kx * self.H0 * self.adult_sens
        self.child = [w - self.b25 * (a - self.adult_term) for w, a in zip(self.ws, self.adult)]   # with the term
        self.shift0 = self.kx * self.H0 * self.K                   # the term in the benchmark's own lifetime value

    def lifetime_curve(self, weight=CHILD_WEIGHT, with_term=False):
        cs = 0 if with_term else self.kx * self.H0 * self.s_child
        return [weight * (c + cs) + self.b25 * a_ for c, a_ in zip(self.child, self.adult_curve(with_term))]

    def adult_curve(self, with_term=False):
        return [a - (self.adult_term if with_term else 0) for a in self.adult]

    def cev_of(self, t, ws):
        return lagrange(t, self.xs, ws)


REF = Bench(os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085'))
# the names earlier readers use, all the benchmark of record's
BETA, KX0, OMEGA_C = REF.beta, REF.kx, REF.omega
S_CHILD, H0, BKD, K, ADULT_SENS, B25 = REF.s_child, REF.H0, REF.bkd, REF.K, REF.adult_sens, REF.b25
XS, WS, SHIFT0 = REF.xs, REF.ws, REF.shift0
WS_FREE = [w + SHIFT0 for w in WS]                  # childhood at one, without the term (the r291 convention)
ADULT_CURVE, CHILD_CURVE = REF.adult, REF.child


def curve_for_weight(wc):
    return REF.lifetime_curve(wc, with_term=False)


def cev_of(t, ws=None):
    return lagrange(t, XS, WS if ws is None else ws)


def arm_values(d):
    """W (the Fortran's lifetime value: childhood at one, with the term), its childhood part C, the adult value at 26,
    kappa_x and H of the arm in directory d, from its cf.log.gz and final.txt; None where either file is missing"""
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


def term(v, bench=REF):
    return v['kx'] * v['H'] * bench.K


def components(v, bench=REF, with_term=False):
    """the child's childhood (at one) and the discounted adult part of the arm's lifetime value"""
    C, A = v['C'], v['W'] - v['C']
    if not with_term:
        C += v['kx'] * v['H'] * bench.s_child
        A += v['kx'] * v['H'] * bench.bkd
    return C, A


def components_free(v, bench=REF):
    return components(v, bench, with_term=False)


def lifetime(v, weight=CHILD_WEIGHT, bench=REF, with_term=False):
    C, A = components(v, bench, with_term)
    return weight * C + A


def cev_at(d, weight=CHILD_WEIGHT, bench=REF, with_term=False):
    """the arm's CEV against its benchmark, per cent, with the child's childhood at this weight"""
    v = arm_values(d)
    assert v, f'no welfare to read in {d}'
    return 100 * bench.cev_of(lifetime(v, weight, bench, with_term), bench.lifetime_curve(weight, with_term))


def cev_free(d, bench=REF):
    """THE PAPER'S: childhood at xi - 1, without the term"""
    return cev_at(d, CHILD_WEIGHT, bench, with_term=False)


def cev_with(d, bench=REF):
    """the Fortran's own: childhood at one, with the term; must agree with its logged CEV"""
    return cev_at(d, 1.0, bench, with_term=True)


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


def parts(arm_w, arm_n, base_w, base_n, bench=REF, weight=CHILD_WEIGHT):
    """WHERE THE NEWBORN'S GAIN COMES FROM. Treatment First (welfare files in arm_w, by-node values in arm_n)
    against Housing First (base_w, base_n), without the kappa_x term, the child's childhood at `weight`:
      C   the child's childhood at one (the Fortran's), Cw = weight * C
      A   the child's adult life, beta^J_K times the entrants' average value at 26, each policy's own entrants
      P   the parent's own lifetime value: the value at 26 by entry node under each policy, weighted by the Housing
          First newborns, so the same households are valued under both (it carries omega_c times the child terms)
      Aown = beta^J_K P: the newborn's own gain from living under the policy as an adult (hold who enters, change
          the policy); E = A - Aown: entering adult life on a better node (hold the policy, change who enters). The
          split is exact because the entrants' value at 26 is the same function in A and in P.
    Utils: nb = Cw + A (the criterion), eq = P + nb, extc = (1 - omega_c) Cw, cnt = omega_c Cw.
    Points of lifetime consumption ('pts'): the four pieces extc, E, own, cnt read off the benchmark's lifetime curve
    one after another, in that order, so that they sum to the CEV 'tot'; and 'P' on the adult curve, the parent's
    own gain as a percent of its own lifetime consumption."""
    m = masses()
    vb, va = arm_values(base_w), arm_values(arm_w)
    assert vb and va, (base_w, arm_w)
    Cb, Ab = components(vb, bench)
    Ca, Aa = components(va, bench)
    nb0, na = v26(base_n), v26(arm_n)
    assert abs(sum(m[n] * nb0[n] for n in m) - vb['V26']) < 0.05, 'by-node values do not average to the logged V26'
    P = sum(m[n] * (na[n] - nb0[n]) for n in m) + (va['kx'] * va['H'] - vb['kx'] * vb['H']) * bench.adult_sens
    om = bench.omega
    r = dict(C=Ca - Cb, A=Aa - Ab, P=P, Aown=bench.b25 * P, E=Aa - Ab - bench.b25 * P, b25=bench.b25, weight=weight,
             worse=100 * sum(m[n] for n in m if na[n] < nb0[n]))
    r['Cw'] = weight * r['C']
    r['nb'] = r['Cw'] + r['A']
    r['eq'] = r['P'] + r['nb']
    r['extc'] = (1 - om) * r['Cw']
    r['cnt'] = om * r['Cw']
    # points of lifetime consumption, one piece after another on the lifetime curve
    curve = bench.lifetime_curve(weight, with_term=False)
    W0 = weight * Cb + Ab
    pts, w = {}, W0
    for name, u in (('extc', r['extc']), ('E', r['E']), ('own', r['Aown']), ('cnt', r['cnt'])):
        c0 = bench.cev_of(w, curve)
        w += u
        pts[name] = 100 * (bench.cev_of(w, curve) - c0)
    pts['tot'] = 100 * (bench.cev_of(W0 + r['nb'], curve) - bench.cev_of(W0, curve))
    assert abs(sum(pts[k] for k in ('extc', 'E', 'own', 'cnt')) - pts['tot']) < 1e-9
    ac = bench.adult_curve(with_term=False)
    V0 = vb['V26'] + vb['kx'] * vb['H'] * bench.adult_sens
    pts['P'] = 100 * (bench.cev_of(V0 + P, ac) - bench.cev_of(V0, ac))
    pts['ext'] = pts['extc'] + pts['E']
    pts['ext_share'] = 100 * pts['ext'] / pts['tot']
    pts['child_share'] = 100 * (pts['extc'] + pts['cnt']) / pts['tot']
    r['pts'] = pts
    return r


if __name__ == '__main__':
    print(f'benchmark of record: beta {BETA:.5f}  kappa_x {KX0:.4f}  omega_c {OMEGA_C}  H0 {H0:.6f}  S_child {S_CHILD:.3f}  '
          f'beta^K D_adult {BKD:.3f}  K {K:.3f}  term {SHIFT0:.4f} utils; child weight {CHILD_WEIGHT:.4f}')
    print('lifetime curve at x=0: file %.4f, rebuilt at weight one with the term %.4f; file+shift %.4f, rebuilt without %.4f'
          % (WS[10], REF.lifetime_curve(1.0, True)[10], WS_FREE[10], curve_for_weight(1.0)[10]))
