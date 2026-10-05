#!/usr/bin/env python3
"""analyse_smi.py -- the SMI split's guards and tables (README.md).

  analyse_smi.py guard <plain3 1-thread> <smi3 1-thread> <track3 1-thread>
  analyse_smi.py main  <tf10 log> <hf10 log>

Reads the REVK GROUP lines (groups 1-4, unchanged from code/revoked_2c), the REVK SGROUP lines (the same groups cut
by SMI at their start: parent p, smi0 0 or 1) and the REVK SMI lines. The pooled numbers are computed exactly as
code/paper/export_revoked.py computes the x_rv_* the paper quotes: deaths as a share of the mass at revocation,
survivors' shares weighted by survivors, each cohort read the same number of years after its own revocation.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'revoked_2c'))
from analyse import kv, load, agg_lines, check_common  # noqa: E402

FIELDS = ('mass0', 'alive', 'cum_deaths_h', 'cum_deaths_e')
SHARES = ('sud', 'homeless', 'holding', 'excluded', 'smi_now')
REVOKED = (1, 2, 3)
OLD = dict(dead_tf=6.92, dead_hf=6.12, gap=0.80)   # results/revoked_2c/RESULT.md


def load_smi(path):
    r = load(path)
    split, smi = {}, {}
    for l in r['lines']:
        s = l.strip()
        if s.startswith('REVK SGROUP'):
            d = kv(s); split[(int(d['parent']), int(d['smi0']), int(d['t']))] = d
        elif s.startswith('REVK SMI'):
            d = kv(s); smi[(int(d['g']), int(d['t']))] = d['smi_now']
    for (g, t), d in r['groups'].items():
        d['smi_now'] = smi.get((g, t), float('nan'))
    r['split'], r['smi'] = split, smi
    return r


def view(r, s):
    """the groups as {(p, t): line}: s None = the unsplit groups, 0 / 1 = the halves without / with SMI at the start"""
    if s is None:
        return r['groups']
    return {(p, t): d for (p, q, t), d in r['split'].items() if q == s}


def split_sum(r, out, name):
    """the two halves against their parent: levels, and shares times survivors"""
    w, n, exact, start_exact = 0.0, 0, 0, True
    for (p, t), g in r['groups'].items():
        a, b = r['split'].get((p, 0, t)), r['split'].get((p, 1, t))
        if not a or not b:
            continue
        for f in FIELDS + tuple(x + '*alive' for x in SHARES[:-1]):
            if f.endswith('*alive'):
                k = f[:-6]; u = g[k] * g['alive']; v = a[k] * a['alive'] + b[k] * b['alive']
            else:
                u, v = g[f], a[f] + b[f]
            n += 1; exact += (u == v)
            w = max(w, abs(u - v) / max(abs(u), 1e-300))
            if t == int(g['start']) and f in ('mass0', 'alive') and u != v:
                start_exact = False
    good = n > 0 and w < 1e-12
    out.append(f"  {name}: the SMI halves summed against the unsplit group, {n} comparisons (levels; shares times survivors): "
               f"{exact} bit for bit, worst relative difference {w:.1e} (rule 1e-12) {'PASS' if good else 'FAIL'}")
    out.append(f"    (not identity: the module totals a group by summing whole arrays, a half by summing its own cells, so even "
               f"at the start, where the cut is an exact partition of cells, the totals are added in a different order "
               f"(starting masses bit for bit: {start_exact}); after it the halves move in separate passes and rejoin in the "
               f"same cells as SMI is left and entered. The rule is rounding.)")
    # the cut is by SMI at the start
    st = {(p, q): d['smi_now'] for (p, q, t), d in r['split'].items() if t == int(d['start'])}
    bad = [k for k, v in st.items() if (k[1] == 0 and v != 0) or (k[1] == 1 and abs(v - 1) > 1e-12)]
    out.append(f"  {name}: SMI share at the start: exactly 0 in the halves without SMI ({[st[k] for k in sorted(st) if k[1] == 0]}), "
               f"1 to rounding in the halves with it (worst |share - 1| {max([abs(v - 1) for k, v in st.items() if k[1] == 1] + [0]):.1e}, "
               f"rule 1e-12; a share of slices over a sum of the whole) {'PASS' if not bad else 'FAIL ' + str(bad[:4])}")
    worst = max([abs(d['acct_close']) for d in r['split'].values()] + [abs(d['acct']) for d in r['split'].values()] + [0])
    out.append(f"  {name}: mass accounting in the halves, worst {worst:.1e} (rule 1e-10) {'PASS' if worst < 1e-10 else 'FAIL'}")
    return good and not bad and worst < 1e-10


def guard(a):
    p1, s1, t1 = (load_smi(x) for x in a)
    out, ok = ["T = 3 GUARDS, ONE THREAD: plain, unsplit tracking, split tracking (Treatment First path)"], True
    A, B = agg_lines(p1), agg_lines(s1)
    diff = [i for i, (x, y) in enumerate(zip(A, B)) if x != y]
    good = len(A) == len(B) and not diff and len(A) > 0
    out.append(f"  aggregate lines (MECH, CENSUS, BUDGET, DRUG, WELFARE, MILBY, ...): plain {len(A)}, split {len(B)}, "
               f"differing {len(diff)} {'PASS' if good else 'FAIL'}")
    ok &= good
    keep = lambda r: [l.strip() for l in r['lines'] if l.strip().startswith(('REVK GROUP', 'REVK POP', 'REVK TAG', 'REVK INIT', 'REVK MASK'))
                      or (l.strip().startswith('REVK LEAK') and ('population' in l or int(kv(l)['g']) <= 4))] + agg_lines(r)
    X, Y = keep(t1), keep(s1)
    diff = [i for i, (x, y) in enumerate(zip(X, Y)) if x != y]
    good = len(X) == len(Y) and not diff and len(X) > 0
    out.append(f"  unsplit tracking against split tracking: every REVK GROUP, POP, TAG, LEAK, INIT, MASK and aggregate line, "
               f"{len(X)} and {len(Y)} lines, differing {len(diff)}: groups 1-4 reproduced byte for byte {'PASS' if good else 'FAIL'}")
    for i in diff[:3]:
        out.append(f"    unsplit: {X[i][:160]}\n    split:   {Y[i][:160]}")
    ok &= good
    ok &= check_common(s1, "split tracking, one thread", out)
    ok &= split_sum(s1, out, "split tracking, one thread")
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}")
    print("\n".join(out))


def pooled(G, years, key, groups=REVOKED):
    if key == 'dead':
        return sum(G[(g, g + years)]['cum_deaths_h'] + G[(g, g + years)]['cum_deaths_e'] for g in groups) / \
            sum(G[(g, g)]['mass0'] for g in groups)
    w = [G[(g, g + years)]['alive'] for g in groups]
    return sum(G[(g, g + years)][key] * x for g, x in zip(groups, w)) / sum(w) if sum(w) > 0 else float('nan')


def summary(tf, hf, s, groups):
    T, H = view(tf, s), view(hf, s)
    m = sum(T[(g, g)]['mass0'] for g in groups)
    d = {y: (pooled(T, y, 'dead', groups), pooled(H, y, 'dead', groups)) for y in (1, 2, 3, 4, 6)}
    hl = [pooled(T, y, 'homeless', groups) for y in (1, 2, 3)]
    hb = [pooled(H, y, 'homeless', groups) for y in (1, 2, 3)]
    rise = sum(x - y for x, y in zip(hl, hb)) / 3
    return dict(mass=m, d=d, hl=hl, hb=hb, rise=rise, wald=(d[3][0] - d[3][1]) / rise if rise > 0 else float('nan'),
                sud0=pooled(T, 0, 'sud', groups), age0=pooled(T, 0, 'mean_age', groups) + 25,
                smi=[(pooled(T, y, 'smi_now', groups), pooled(H, y, 'smi_now', groups)) for y in (0, 1, 2, 3, 6)],
                sud3=(pooled(T, 3, 'sud', groups), pooled(H, 3, 'sud', groups)))


def main(a):
    tf, hf = load_smi(a[0]), load_smi(a[1])
    out = ["# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)"]
    ok = True
    for r, nm in ((tf, 'Treatment First path'), (hf, 'Housing First path')):
        ok &= check_common(r, nm, out, 1e-4, "; four threads: bounded by the model's race, exact on one thread at T = 3")
        ok &= split_sum(r, out, nm)
    for k in sorted(tf['split']):
        p, q, t = k
        if t == int(tf['split'][k]['start']):
            m1, m2 = tf['split'][k]['mass0'], hf['split'].get(k, {}).get('mass0', -1)
            good = abs(m1 - m2) <= 1e-12 * m1
            out.append(f"  group {p}, SMI at start {q}: starting mass {m1:.6e} (a), {m2:.6e} (b) {'PASS' if good else 'FAIL'}")
            ok &= good
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}\n")

    out.append("# THE REVOKED BY SMI AT REVOCATION\n")
    out.append("(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. "
               "Deaths include the end of life. Homeless and SMI shares are of the survivors. Per household made homeless: "
               "the three-year gap over the average rise (a)-(b) in the survivors' homeless share in years 1-3, as in "
               "code/paper/export_revoked.py.\n")
    rows = []
    for lab, groups in (("pooled, years 1-3", REVOKED), ("year-1 cohort", (1,)), ("year-2 cohort", (2,)), ("year-3 cohort", (3,))):
        S = {s: summary(tf, hf, s, groups) for s in (None, 1, 0)}
        out.append(f"## {lab}\n")
        out.append("| group | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | 3-yr deaths (b) % | gap pp "
                   "| homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | per household made homeless pp | 4-yr gap pp | 6-yr gap pp |")
        out.append("|" + "---|" * 12)
        for s, nm in ((1, 'with SMI'), (0, 'without SMI'), (None, 'all (unsplit)')):
            x = S[s]
            out.append(f"| {nm} | {100 * x['mass'] / S[None]['mass']:.2f} | {100 * x['sud0']:.2f} | {x['age0']:.1f} "
                       f"| {100 * x['d'][3][0]:.2f} | {100 * x['d'][3][1]:.2f} | {100 * (x['d'][3][0] - x['d'][3][1]):+.2f} "
                       f"| {' / '.join(f'{100 * v:.1f}' for v in x['hl'])} | {' / '.join(f'{100 * v:.1f}' for v in x['hb'])} "
                       f"| {100 * x['wald']:.1f} | {100 * (x['d'][4][0] - x['d'][4][1]):+.2f} | {100 * (x['d'][6][0] - x['d'][6][1]):+.2f} |")
        # the mass-weighted combination
        sh = S[1]['mass'] / S[None]['mass']
        comb = [sh * S[1]['d'][3][i] + (1 - sh) * S[0]['d'][3][i] for i in (0, 1)]
        out.append(f"\nmass-weighted combination of the halves: {100 * comb[0]:.4f} (a), {100 * comb[1]:.4f} (b), gap "
                   f"{100 * (comb[0] - comb[1]):+.4f} pp; unsplit {100 * S[None]['d'][3][0]:.4f}, {100 * S[None]['d'][3][1]:.4f}, "
                   f"{100 * (S[None]['d'][3][0] - S[None]['d'][3][1]):+.4f}")
        out.append("\nSMI among the survivors of the halves, years since revocation 0 / 1 / 2 / 3 / 6, (a) and (b): "
                   + "; ".join(f"{nm}: " + " / ".join(f"{100 * u:.1f}, {100 * v:.1f}" for u, v in S[s]['smi'])
                               for s, nm in ((1, 'with SMI'), (0, 'without SMI'))))
        out.append(f"\nSUD among the survivors three years on, (a) and (b): with SMI {100 * S[1]['sud3'][0]:.1f}, {100 * S[1]['sud3'][1]:.1f}; "
                   f"without {100 * S[0]['sud3'][0]:.1f}, {100 * S[0]['sud3'][1]:.1f}\n")
        rows.append((lab, S))
    # by year since revocation, pooled
    out.append("## pooled, by years since revocation\n")
    out.append("| years since | deaths with SMI (a) % | (b) % | gap pp | deaths without SMI (a) % | (b) % | gap pp | all (a) % | (b) % | gap pp |")
    out.append("|" + "---|" * 10)
    for y in (1, 2, 3, 4, 6):
        c = []
        for s in (1, 0, None):
            dt, dh = pooled(view(tf, s), y, 'dead'), pooled(view(hf, s), y, 'dead')
            c += [f"{100 * dt:.2f}", f"{100 * dh:.2f}", f"{100 * (dt - dh):+.2f}"]
        out.append(f"| {y} | " + " | ".join(c) + " |")
    out.append("")
    # the holders at the reform
    out.append("## every holder at the reform, by SMI at the reform (t = 0)\n")
    out.append("| group | share % | deaths at 3 yrs (a) % | (b) % | gap pp | homeless at 3 yrs (a) % | (b) % |")
    out.append("|" + "---|" * 7)
    for s, nm in ((1, 'with SMI'), (0, 'without SMI'), (None, 'all')):
        T, H = view(tf, s), view(hf, s)
        m0 = T[(4, 0)]['mass0']
        dt = (T[(4, 3)]['cum_deaths_h'] + T[(4, 3)]['cum_deaths_e']) / m0
        dh = (H[(4, 3)]['cum_deaths_h'] + H[(4, 3)]['cum_deaths_e']) / m0
        out.append(f"| {nm} | {100 * m0 / tf['groups'][(4, 0)]['mass0']:.2f} | {100 * dt:.2f} | {100 * dh:.2f} | {100 * (dt - dh):+.2f} "
                   f"| {100 * T[(4, 3)]['homeless']:.2f} | {100 * H[(4, 3)]['homeless']:.2f} |")
    out.append("")
    S = rows[0][1]
    for s, nm in ((1, 'WITH SMI'), (0, 'WITHOUT SMI'), (None, 'ALL')):
        x = S[s]
        out.append(f"HEADLINE {nm}: {100 * x['mass'] / S[None]['mass']:.1f} per cent of the revoked (pooled, years 1-3); three-year "
                   f"mortality {100 * x['d'][3][0]:.2f} against {100 * x['d'][3][1]:.2f} per cent, gap {100 * (x['d'][3][0] - x['d'][3][1]):+.2f} pp; "
                   f"homeless {', '.join(f'{100 * v:.1f}' for v in x['hl'])} per cent in years 1-3; per household made homeless "
                   f"{100 * x['wald']:.1f} pp")
    x = S[None]
    out.append(f"AGAINST code/revoked_2c (re-solved arms): {100 * x['d'][3][0]:.2f} / {100 * x['d'][3][1]:.2f} / "
               f"{100 * (x['d'][3][0] - x['d'][3][1]):+.2f} against {OLD['dead_tf']:.2f} / {OLD['dead_hf']:.2f} / {OLD['gap']:+.2f}")
    print("\n".join(out))


if __name__ == '__main__':
    {'guard': guard, 'main': main}[sys.argv[1]](sys.argv[2:])
