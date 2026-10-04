#!/usr/bin/env python3
"""analyse.py -- the revoked-voucher experiment's guards and tables (code/revoked_2c/README.md).

  analyse.py guard3 <plain3 log> <track3 log> <hf3 log> <track3 bounds log>
  analyse.py main   <tf10 log> <hf10 log>

Reads only the REVK lines the tracking module prints and the transition's own TRANSITION lines.
"""
import re
import sys

P_NULL, V_NULL = 1.0001082, 0.067533863
AGG = ("TRANSITION MECH", "TRANSITION VOUCHER CENSUS", "TRANSITION BUDGET", "TRANSITION DRUG",
       "TRANSITION WELFARE loop", "TRANSITION MILBY", "TRANSITION RECOVERY", "TRANSITION ALLALIVE",
       "TRANSITION BETTER OFF", "TRANSITION CEV", "TRANSITION TREATMENT", "TRANSITION SUD_BANDS",
       "TRANSITION HOMELESS_BY_AGE", "TRANSITION MASS_BY_AGE", "TRANSITION VOUCHER DIAG")
LABEL = {1: "revoked in year 1", 2: "revoked in year 2", 3: "revoked in year 3", 4: "holding a voucher at the reform"}


def kv(line):
    return {k: float(v) for k, v in re.findall(r'(\w+)=\s*([-+0-9.EeDd]+)', line.replace('D', 'E'))
            if re.match(r'^[-+]?[0-9.]+([Ee][-+]?[0-9]+)?$', v.replace('D', 'E'))}


def load(path):
    L = open(path, errors='replace').read().splitlines()
    groups, pop, mech, tags, done = {}, {}, {}, {}, []
    for l in L:
        s = l.strip()
        if s.startswith('REVK GROUP'):
            d = kv(s); groups[(int(d['g']), int(d['t']))] = d
        elif s.startswith('REVK POP'):
            d = kv(s); pop[int(d['t'])] = d
        elif s.startswith('TRANSITION MECH'):
            d = kv(s); mech[int(d['t'])] = d
        elif s.startswith('REVK TAG'):
            m = re.search(r'c=\s*(\d+).*mass=\s*(\S+)', s)
            tags[int(m.group(1))] = float(m.group(2))
        elif s.startswith('REVK PERIOD DONE'):
            done.append(s)
    return dict(lines=L, groups=groups, pop=pop, mech=mech, tags=tags, done=done,
                stopped=any('REVK STOP after loop 0' in l for l in L),
                rterr=[l for l in L if 'Fortran runtime error' in l or 'At line' in l])


def agg_lines(run):
    return [l.strip() for l in run['lines'] if l.strip().startswith(AGG)]


def check_common(run, name, out):
    ok = True
    # mass accounting
    worst = max([abs(d['acct_close']) for d in run['groups'].values()] + [abs(d['acct']) for d in run['groups'].values()] + [0])
    good = worst < 1e-10
    out.append(f"  {name}: mass accounting, worst |alive + cumulative deaths - starting mass| / starting mass = {worst:.2e} (rule 1e-10) {'PASS' if good else 'FAIL'}")
    ok &= good
    # the shadow kernel is the model's kernel
    k = max([d['kernel_maxabs'] / max(d['max_cell'], 1e-300) for d in run['pop'].values()] + [0])
    good = k < 1e-12 and len(run['pop']) > 0
    out.append(f"  {name}: shadow kernel against the model's own step (ages 2+), worst max-cell gap / largest cell = {k:.2e} (rule 1e-12) {'PASS' if good else 'FAIL'}")
    ok &= good
    # fixed paths
    ps = sorted({d['p_drug'] for d in run['mech'].values()}); vs = sorted({d['pi_v'] for d in run['mech'].values()})
    good = len(ps) == 1 and len(vs) == 1 and abs(ps[0] - P_NULL) < 1e-12 and abs(vs[0] - V_NULL) < 1e-12
    out.append(f"  {name}: price printed in {len(run['mech'])} years: {ps}; pi_V: {vs} {'PASS' if good else 'FAIL'}")
    ok &= good
    good = run['stopped'] and not run['rterr']
    out.append(f"  {name}: one pass and stopped cleanly: {run['stopped']}, runtime errors: {len(run['rterr'])} {'PASS' if good else 'FAIL'}")
    ok &= good
    return ok


def guard3(a):
    plain, track, hf, bnd = (load(p) for p in a)
    out, ok = ["T = 3 GUARDS"], True
    A, B = agg_lines(plain), agg_lines(track)
    diff = [i for i, (x, y) in enumerate(zip(A, B)) if x != y]
    good = len(A) == len(B) and not diff and len(A) > 0
    out.append(f"  aggregate lines (MECH, CENSUS, BUDGET, DRUG, WELFARE, ...): plain {len(A)}, tracking {len(B)}, differing {len(diff)} {'PASS' if good else 'FAIL'}")
    for i in diff[:5]:
        out.append(f"    plain:    {A[i][:160]}\n    tracking: {B[i][:160]}")
    ok &= good
    ok &= check_common(track, "tf T=3", out)
    ok &= check_common(hf, "hf T=3", out)
    tw = {c: m for c, m in track['tags'].items()}; th = hf['tags']
    good = bool(tw) and all(abs(th.get(c, -1) - m) <= 1e-15 * max(m, 1e-300) for c, m in tw.items())
    out.append(f"  tags written {tw}, read {th} {'PASS' if good else 'FAIL'}")
    ok &= good
    good = bnd['stopped'] and not bnd['rterr'] and len(bnd['done']) == len(track['done'])
    out.append(f"  bounds-checked tracking build: periods {len(bnd['done'])}, runtime errors {len(bnd['rterr'])} {'PASS' if good else 'FAIL'}")
    for l in bnd['rterr'][:3]:
        out.append("    " + l)
    ok &= good
    for t, d in sorted(hf['pop'].items()):
        out.append(f"  hf t={t}: population moved from t-1 by {d['moved_from_tminus1_sumabs']:.2e} (sum of |change| over cells, mass 1)")
    for r, nm in ((track, 'tf'), (hf, 'hf')):
        for l in r['done']:
            out.append(f"  {nm} {l}")
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}")
    print("\n".join(out))


def pct(x):
    return f"{100 * x:.2f}"


def table(tf, hf, g, T):
    rows = []
    for t in range(0, T + 1):
        a, b = tf['groups'].get((g, t)), hf['groups'].get((g, t))
        if not a or not b:
            continue
        m0 = a['mass0']
        da, db = a['cum_deaths_h'] + a['cum_deaths_e'], b['cum_deaths_h'] + b['cum_deaths_e']
        rows.append((t, t - int(a['start']), a, b, m0, da, db))
    return rows


def main(a):
    tf, hf = load(a[0]), load(a[1])
    T = max(tf['pop']) if tf['pop'] else 0
    out = ["# GUARDS (T = 10)"]
    ok = check_common(tf, "Treatment First path", out)
    ok &= check_common(hf, "Housing First path", out)
    good = all(abs(hf['tags'].get(c, -1) - m) <= 1e-15 * max(m, 1e-300) for c, m in tf['tags'].items()) and len(tf['tags']) == 3
    out.append(f"  tags: written {tf['tags']}, read {hf['tags']} {'PASS' if good else 'FAIL'}")
    ok &= good
    for g in (1, 2, 3, 4):
        x = [(t, tf['groups'][(g, t)]['mass0'], hf['groups'].get((g, t), {}).get('mass0')) for t in range(T + 1) if (g, t) in tf['groups']]
        if x:
            t, m1, m2 = x[0]
            out.append(f"  group {g} ({LABEL[g]}): starting mass {m1:.6e} under Treatment First, {m2:.6e} in the counterfactual"
                       + (" PASS" if m2 is not None and abs(m1 - m2) <= 1e-12 * m1 else " FAIL"))
            ok &= m2 is not None and abs(m1 - m2) <= 1e-12 * m1
    out.append("  Housing First stationarity (the no-policy steady state pushed through its own kernel, newborns added):")
    for t, d in sorted(hf['pop'].items()):
        out.append(f"    t={t}: sum over cells of |dist(t) - dist(t-1)| = {d['moved_from_tminus1_sumabs']:.2e}; SUD {d['sud']:.8f}, "
                   f"homeless {d['homeless']:.8f}, deaths {d['deaths_h'] + d['deaths_e']:.8f}, alive {d['alive']:.10f}")
    out.append(f"GUARD SUMMARY: {'PASS' if ok else 'FAIL'}")

    out.append("\n# TABLES\n")
    out.append("(a) = Treatment First as it happened to them; (b) = the same households, voucher kept, under Housing First's rules.")
    out.append("Deaths include the end of life (age 85, the model's last age); 'hazard' is the survival draw alone.\n")
    head = ("| year | years since | alive (a) | alive (b) | cum. deaths (a) | cum. deaths (b) | % of start (a) | % of start (b) "
            "| hazard % (a) | hazard % (b) | SUD % (a) | SUD % (b) | homeless % (a) | homeless % (b) | holding % (a) | holding % (b) |")
    sep = "|" + "---|" * 16
    pooled = {}
    for g in (1, 2, 3, 4):
        rows = table(tf, hf, g, T)
        if not rows:
            continue
        out.append(f"## {LABEL[g]} (starting mass {rows[0][4]:.6e} of a population of 1)\n")
        out += [head, sep]
        for t, k, x, y, m0, da, db in rows:
            out.append(f"| {t} | {k} | {x['alive']:.6e} | {y['alive']:.6e} | {da:.6e} | {db:.6e} | {pct(da / m0)} | {pct(db / m0)} "
                       f"| {pct(x['cum_deaths_h'] / m0)} | {pct(y['cum_deaths_h'] / m0)} | {pct(x['sud'])} | {pct(y['sud'])} "
                       f"| {pct(x['homeless'])} | {pct(y['homeless'])} | {pct(x['holding'])} | {pct(y['holding'])} |")
            if g <= 3:
                p = pooled.setdefault(k, [0, 0, 0, 0, 0, 0])
                p[0] += m0; p[1] += da; p[2] += db; p[3] += x['cum_deaths_h']; p[4] += y['cum_deaths_h']; p[5] += 1
        out.append("")
    out.append("## the three revoked cohorts pooled, by years since revocation (each cohort from its own revocation year)\n")
    out.append("| years since | cohorts | starting mass | cum. deaths % (a) | cum. deaths % (b) | gap (a)-(b) pp | hazard % (a) | hazard % (b) | hazard gap pp |")
    out.append("|" + "---|" * 9)
    for k in sorted(pooled):
        m0, da, db, ha, hb, n = pooled[k]
        if n < 3:
            continue
        out.append(f"| {k} | {n} | {m0:.6e} | {pct(da / m0)} | {pct(db / m0)} | {100 * (da - db) / m0:+.2f} | {pct(ha / m0)} | {pct(hb / m0)} | {100 * (ha - hb) / m0:+.2f} |")
        if k == 3:
            head3 = (100 * (da - db) / m0, 100 * da / m0, 100 * db / m0, 100 * (ha - hb) / m0)
    out.append("")
    out.append("## the whole population, Treatment First path against Housing First\n")
    out.append("| year | deaths TF | deaths HF | SUD % TF | SUD % HF | homeless % TF | homeless % HF | holding % TF | holding % HF | excluded % TF |")
    out.append("|" + "---|" * 10)
    for t in sorted(tf['pop']):
        x, y = tf['pop'][t], hf['pop'].get(t)
        if not y:
            continue
        out.append(f"| {t} | {x['deaths_h'] + x['deaths_e']:.6e} | {y['deaths_h'] + y['deaths_e']:.6e} | {pct(x['sud'])} | {pct(y['sud'])} "
                   f"| {pct(x['homeless'])} | {pct(y['homeless'])} | {pct(x['holding'])} | {pct(y['holding'])} | {pct(x['excluded'])} |")
    out.append("")
    if 'head3' in locals():
        out.append(f"HEADLINE: three-year cumulative mortality of the households revoked in years 1-3: {head3[1]:.2f} per cent "
                   f"under Treatment First against {head3[2]:.2f} per cent had they kept the voucher; gap {head3[0]:+.2f} pp "
                   f"(survival draw alone {head3[3]:+.2f} pp)")
    print("\n".join(out))


if __name__ == '__main__':
    {'guard3': guard3, 'main': main}[sys.argv[1]](sys.argv[2:])
