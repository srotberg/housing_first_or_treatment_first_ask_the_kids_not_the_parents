#!/usr/bin/env python3
"""analyse_street.py -- the SMI x street split's guards and tables (README.md).

  analyse_street.py guard <plain3 1-thread> <street3 1-thread> <track3 1-thread>
  analyse_street.py main  <tf10 log> <hf10 log>

Reads the REVK GROUP lines (groups 1-4, unchanged from code/revoked_2c), the REVK SUBGROUP lines (cohort c = 1..3 cut at
revocation by SMI, smi0, and by whether the first housing choice after the revocation, Treatment First's, is the
street, street), the REVK SPLIT lines and the REVK PERSIST lines (the street parts' mass on the street in every year
since the revocation). Pooled numbers as code/paper/export_revoked.py computes them: deaths as a share of the mass at
revocation, survivors' shares weighted by survivors, each cohort read the same number of years after its revocation.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'revoked_2c'))
from analyse import kv, load, agg_lines, check_common  # noqa: E402

FIELDS = ('mass0', 'alive', 'cum_deaths_h', 'cum_deaths_e')
SHARES = ('sud', 'homeless', 'holding', 'excluded', 'smi_now')
COHORTS = (1, 2, 3)
AGE0 = 25                                            # model age 1 is age 26 (code/paper/export_revoked.py)
OLD = dict(dead_tf=6.92, dead_hf=6.12, gap=0.80)    # results/revoked_2c/RESULT.md
SUBS = ((1, 1), (1, 0), (0, 1), (0, 0))             # (smi0, street)
NAME = {(1, 1): 'SMI, on the street', (1, 0): 'SMI, housed', (0, 1): 'no SMI, on the street', (0, 0): 'no SMI, housed'}


def load_st(path):
    r = load(path)
    sub, split, pers = {}, {}, {}
    for l in r['lines']:
        s = l.strip()
        if s.startswith('REVK SUBGROUP'):
            d = kv(s); sub[(int(d['cohort']), int(d['smi0']), int(d['street']), int(d['t']))] = d
        elif s.startswith('REVK SPLIT'):
            d = kv(re.sub(r'file=\S+', '', s)); split[int(d['c'])] = d
        elif s.startswith('REVK PERSIST'):
            d = kv(s); pers[(int(d['cohort']), int(d['smi0']), int(d['t']))] = d
    r.update(sub=sub, split=split, pers=pers)
    return r


def view(r, sel):
    """{(c, t): line} for the cell set sel: None = the unsplit cohort, else a list of (smi0, street) parts, summed"""
    if sel is None:
        return {k: d for k, d in r['groups'].items() if k[0] in COHORTS}
    V = {}
    for (c, s, k, t), d in r['sub'].items():
        if (s, k) not in sel:
            continue
        v = V.setdefault((c, t), dict(mass0=0.0, alive=0.0, cum_deaths_h=0.0, cum_deaths_e=0.0,
                                      **{x + '_m': 0.0 for x in SHARES + ('mean_age',)}))
        for f in FIELDS:
            v[f] += d[f]
        for x in SHARES + ('mean_age',):
            v[x + '_m'] += d[x] * d['alive']
    for v in V.values():
        for x in SHARES + ('mean_age',):
            v[x] = v[x + '_m'] / v['alive'] if v['alive'] > 0 else float('nan')
    return V


def split_sum(r, out, name):
    """the four parts summed against their cohort"""
    w, n, exact, start_gap = 0.0, 0, 0, 0.0
    for (c, t), g in r['groups'].items():
        parts = [r['sub'].get((c, s, k, t)) for s, k in SUBS]
        if c not in COHORTS or not all(parts):
            continue
        for f in FIELDS + tuple(x + '*alive' for x in SHARES[:-1]):
            if f.endswith('*alive'):
                x = f[:-6]; u = g[x] * g['alive']; v = sum(p[x] * p['alive'] for p in parts)
            else:
                u, v = g[f], sum(p[f] for p in parts)
            n += 1; exact += (u == v)
            w = max(w, abs(u - v) / max(abs(u), 1e-300))
            if t == c and f in ('mass0', 'alive'):
                start_gap = max(start_gap, abs(u - v) / u)
    cells = [d['cell_maxabs_parts_minus_cohort'] for d in r['split'].values()]
    good = n > 0 and w < 1e-12 and cells and max(cells) == 0.0
    out.append(f"  {name}: the four parts summed against the unsplit cohort, {n} comparisons (levels; shares times survivors): "
               f"{exact} bit for bit, worst relative difference {w:.1e} (rule 1e-12); at the split, cell by cell, max |parts - "
               f"cohort| = {max(cells) if cells else 'none'} over {len(cells)} splits (rule 0, a partition of cells) "
               f"{'PASS' if good else 'FAIL'}")
    out.append(f"    (the parts move in separate passes through the same kernel and rejoin in the same cells, so a sum of four "
               f"separately rounded passes can differ from the joint pass in the last bit; at the start the totals "
               f"differ by {start_gap:.1e} relative, the order of summation over the same cells)")
    bad = [(c, s, k) for (c, s, k, t), d in r['sub'].items() if t == c and abs(d['smi_now'] - s) > 1e-12]
    out.append(f"  {name}: SMI share at revocation 1 in the SMI parts, 0 in the others (to 1e-12, the ratio of two sums): {'PASS' if not bad else 'FAIL ' + str(bad[:4])}")
    worst = max([abs(d['acct_close']) for d in r['sub'].values()] + [abs(d['acct']) for d in r['sub'].values()] + [0])
    out.append(f"  {name}: mass accounting in the parts, worst {worst:.1e} (rule 1e-10) {'PASS' if worst < 1e-10 else 'FAIL'}")
    for c, d in sorted(r['split'].items()):
        out.append(f"    split of cohort {c} (at t = {int(d['t'])}): no SMI housed {d['mass_s0_k0']:.6e}, no SMI street {d['mass_s0_k1']:.6e}, "
                   f"SMI housed {d['mass_s1_k0']:.6e}, SMI street {d['mass_s1_k1']:.6e}; cohort {d['cohort_mass']:.6e}; "
                   f"at the last age (no choice, counted housed) {d['endlife_mass']:.3e}")
    return good and not bad and worst < 1e-10


def street_check(r, out, name):
    """Treatment First: one year after the revocation every survivor of a street part is homeless and none of a housed
    part is; and the persistence mass equals the street part's survivors then"""
    bad, n = [], 0
    for (c, s, k, t), d in r['sub'].items():
        if t != c + 1 or d['alive'] <= 0:
            continue
        n += 1
        if abs(d['homeless'] - k) > 1e-12:
            bad.append((c, s, k, d['homeless']))
        if k == 1:
            p = r['pers'].get((c, s, t))
            if not p or abs(p['on_street_every_year'] - d['alive']) > 1e-12 * d['alive']:
                bad.append((c, s, 'persist', p and p['on_street_every_year'], d['alive']))
    good = n > 0 and not bad
    out.append(f"  {name}: the classification is the kernel's choice: one year after revocation the survivors' homeless share is "
               f"1 in every street part and 0 in every housed part, and the persistence mass equals the street part's "
               f"survivors ({n} parts) {'PASS' if good else 'FAIL ' + str(bad[:4])}")
    return good


def guard(a):
    p1, s1, t1 = (load_st(x) for x in a)
    out, ok = ["T = 3 GUARDS, ONE THREAD: plain, unsplit tracking, split tracking (Treatment First path)",
               "  (at T = 3 the forward periods are 1 and 2: cohort 1 is split at the start of period 2 and followed one step;"
               " cohorts 2 and 3 are split in the T = 10 runs, whose guards below repeat every split check)"], True
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
    ok &= street_check(s1, out, "split tracking, one thread")
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}")
    print("\n".join(out))


def pooled(G, years, key, cohorts=COHORTS):
    if key == 'dead':
        return sum(G[(c, c + years)]['cum_deaths_h'] + G[(c, c + years)]['cum_deaths_e'] for c in cohorts) / \
            sum(G[(c, c)]['mass0'] for c in cohorts)
    w = [G[(c, c + years)]['alive'] for c in cohorts]
    return sum(G[(c, c + years)].get(key, float('nan')) * x for c, x in zip(cohorts, w)) / sum(w) if sum(w) > 0 else float('nan')


def persist(r, sel, years, cohorts):
    """share of the starting mass, and of the survivors, on the street in every year since the revocation"""
    street = [s for s, k in sel if k == 1]
    if not street:
        return float('nan'), float('nan')
    on = sum(r['pers'][(c, s, c + years)]['on_street_every_year'] for c in cohorts for s in street)
    m0 = sum(r['pers'][(c, s, c)]['mass0'] for c in cohorts for s in street)
    V = view(r, [(s, 1) for s in street])
    alive = sum(V[(c, c + years)]['alive'] for c in cohorts)
    return on / m0, on / alive


def summary(tf, hf, sel, cohorts):
    T, H = view(tf, sel), view(hf, sel)
    m = sum(T[(c, c)]['mass0'] for c in cohorts)
    d = {y: (pooled(T, y, 'dead', cohorts), pooled(H, y, 'dead', cohorts)) for y in (1, 2, 3, 4, 6)}
    return dict(mass=m, d=d,
                hl=[pooled(T, y, 'homeless', cohorts) for y in (1, 2, 3)],
                hb=[pooled(H, y, 'homeless', cohorts) for y in (1, 2, 3)],
                pers=[persist(tf, sel, y, cohorts) if sel else (float('nan'),) * 2 for y in (1, 2, 3)],
                persb=[persist(hf, sel, y, cohorts) if sel else (float('nan'),) * 2 for y in (1, 2, 3)],
                sud0=pooled(T, 0, 'sud', cohorts), age0=pooled(T, 0, 'mean_age', cohorts) + AGE0,
                smi=[(pooled(T, y, 'smi_now', cohorts), pooled(H, y, 'smi_now', cohorts)) for y in (0, 3)],
                sud3=(pooled(T, 3, 'sud', cohorts), pooled(H, 3, 'sud', cohorts)),
                hold3=(pooled(T, 3, 'holding', cohorts), pooled(H, 3, 'holding', cohorts)))


SELS = [('SMI, on the street', [(1, 1)]), ('SMI, housed', [(1, 0)]), ('no SMI, on the street', [(0, 1)]),
        ('no SMI, housed', [(0, 0)]), ('SMI, both', [(1, 1), (1, 0)]), ('on the street, both', [(1, 1), (0, 1)]),
        ('all (the four parts summed)', list(SUBS)), ('all (unsplit cohort lines)', None)]


def main(a):
    tf, hf = load_st(a[0]), load_st(a[1])
    out = ["# GUARDS (T = 10, four threads; the tracked numbers are serial and exact, see code/revoked_2c)"]
    ok = True
    for r, nm in ((tf, 'Treatment First path'), (hf, 'Housing First path')):
        ok &= check_common(r, nm, out, 1e-4, "; four threads: bounded by the model's race, exact on one thread at T = 3")
        ok &= split_sum(r, out, nm)
    ok &= street_check(tf, out, 'Treatment First path')
    for (c, s, k, t), d in sorted(tf['sub'].items()):
        if t == c:
            m2 = hf['sub'].get((c, s, k, t), {}).get('mass0', -1)
            good = abs(d['mass0'] - m2) <= 1e-12 * max(d['mass0'], 1e-300)
            out.append(f"  cohort {c}, {NAME[(s, k)]}: starting mass {d['mass0']:.6e} (a), {m2:.6e} (b) {'PASS' if good else 'FAIL'}")
            ok &= good
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}\n")

    out.append("# THE REVOKED BY SMI AT REVOCATION AND BY WHETHER THE REVOCATION PUTS THEM ON THE STREET\n")
    out.append("(a) Treatment First as it happened to them; (b) the same households, voucher kept, under Housing First's rules. "
               "'On the street': Treatment First's first housing choice after the revocation (the step into the year after it) "
               "is the lowest housing grid point. Deaths include the end of life. Homeless, SUD and SMI shares are of the "
               "survivors. 'Still on the street': on the street in every year since the revocation, as a share of the "
               "survivors.\n")
    heads = {}
    for lab, cohorts in (("pooled, years 1-3", COHORTS), ("year-1 cohort", (1,)), ("year-2 cohort", (2,)), ("year-3 cohort", (3,))):
        S = {nm: summary(tf, hf, sel, cohorts) for nm, sel in SELS}
        tot = S['all (unsplit cohort lines)']['mass']
        out.append(f"## {lab} (revoked mass {tot:.6e})\n")
        out.append("| group | mass | share of the revoked % | SUD at revocation % | mean age | 3-yr deaths (a) % | (b) % | gap pp | gap % "
                   "| 4-yr gap pp | 6-yr gap pp | homeless (a) yrs 1/2/3 % | homeless (b) yrs 1/2/3 % | still on the street (a) yrs 1/2/3 % |")
        out.append("|" + "---|" * 14)
        for nm, sel in SELS:
            x = S[nm]
            d3 = x['d'][3]
            out.append(f"| {nm} | {x['mass']:.4e} | {100 * x['mass'] / tot:.2f} | {100 * x['sud0']:.1f} | {x['age0']:.1f} "
                       f"| {100 * d3[0]:.2f} | {100 * d3[1]:.2f} | {100 * (d3[0] - d3[1]):+.2f} | {100 * (d3[0] / d3[1] - 1):+.0f} "
                       f"| {100 * (x['d'][4][0] - x['d'][4][1]):+.2f} | {100 * (x['d'][6][0] - x['d'][6][1]):+.2f} "
                       f"| {' / '.join(f'{100 * v:.1f}' for v in x['hl'])} | {' / '.join(f'{100 * v:.1f}' for v in x['hb'])} "
                       f"| {' / '.join(f'{100 * v[1]:.1f}' for v in x['pers'])} |")
        out.append("")
        out.append("| group | deaths (a) yrs 1/2/3/4/6 % | deaths (b) yrs 1/2/3/4/6 % | SMI now (a), (b) at 0 and 3 yrs % "
                   "| SUD at 3 yrs (a), (b) % | holding at 3 yrs (a), (b) % | still on the street (a), share of the starting mass, yrs 1/2/3 % |")
        out.append("|" + "---|" * 7)
        for nm, sel in SELS[:6]:
            x = S[nm]
            da = ' / '.join('%.2f' % (100 * x['d'][y][0]) for y in (1, 2, 3, 4, 6))
            db = ' / '.join('%.2f' % (100 * x['d'][y][1]) for y in (1, 2, 3, 4, 6))
            sm = ' / '.join('%.1f, %.1f' % (100 * u, 100 * v) for u, v in x['smi'])
            pe = ' / '.join('%.1f' % (100 * v[0]) for v in x['pers'])
            out.append(f"| {nm} | {da} | {db} | {sm} | {100 * x['sud3'][0]:.1f}, {100 * x['sud3'][1]:.1f} "
                       f"| {100 * x['hold3'][0]:.1f}, {100 * x['hold3'][1]:.1f} | {pe} |")
        out.append("")
        heads[lab] = S
    S = heads["pooled, years 1-3"]
    for nm in ('SMI, on the street', 'SMI, housed', 'no SMI, on the street', 'no SMI, housed', 'all (unsplit cohort lines)'):
        x = S[nm]; d3 = x['d'][3]
        out.append(f"HEADLINE {nm}: {100 * x['mass'] / S['all (unsplit cohort lines)']['mass']:.1f} per cent of the revoked; "
                   f"three-year mortality {100 * d3[0]:.2f} (a) against {100 * d3[1]:.2f} (b), gap {100 * (d3[0] - d3[1]):+.2f} pp "
                   f"({100 * (d3[0] / d3[1] - 1):+.0f} per cent); homeless (a) {', '.join(f'{100 * v:.1f}' for v in x['hl'])} in years 1-3")
    x = S['all (unsplit cohort lines)']
    out.append(f"AGAINST code/revoked_2c (re-solved arms): {100 * x['d'][3][0]:.2f} / {100 * x['d'][3][1]:.2f} / "
               f"{100 * (x['d'][3][0] - x['d'][3][1]):+.2f} against {OLD['dead_tf']:.2f} / {OLD['dead_hf']:.2f} / {OLD['gap']:+.2f}")
    print("\n".join(out))


if __name__ == '__main__':
    {'guard': guard, 'main': main}[sys.argv[1]](sys.argv[2:])
