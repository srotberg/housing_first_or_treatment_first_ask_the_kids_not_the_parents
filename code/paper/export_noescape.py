"""export_noescape.py -- THE STRICT RULE FOR THE DISCUSSION (17 October; the author: "I think then you can write the
conclusion", after the no-escape runs). Detection 1.00 and no exemption for treatment (rule CA, corrected Housing First):

  the long run       results/transition_2c_t70_CAb/arms: the T = 70 transition's own two arms, Housing First and the
                     terminal Treatment First arm with the drug price held at the best long-run pass (0.8017,
                     code/RULE_C_PLAN.md 23:58 and 03:45) and pi_V clearing; changes against that Housing First, and the
                     newborn CEV as export_results.py takes it (welfare_nok.cev_free of the arm less that of Housing First)
  the first years    results/revoked_2c_CA100/{tf,hf}10_run.log.gz: Block 7's ten-year paths, the screen alone with the
                     drug price and pi_V held at their Housing First levels, against Housing First's own path;
                     homelessness and the share of children in a shelter (households aged 26-50, as transition_series.py)
  the revoked        results/revoked_2c_street_CA100/tables.md: the share of the households the screen revokes that are
                     homeless in years 1-3 (against none of the same households with their voucher kept)

Writes the x_ne_* names into results_numbers.json; run after export_results.py, which rewrites that file whole."""
import gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import welfare_nok  # noqa: E402
OUT = os.path.join(HERE, 'results_numbers.json')
ARMS = os.path.join(ROOT, 'results', 'transition_2c_t70_CAb', 'arms')
PATHS = os.path.join(ROOT, 'results', 'revoked_2c_CA100')
STREET = os.path.join(ROOT, 'results', 'revoked_2c_street_CA100', 'tables.md')


def levels(p):
    return {m.group(1).strip(): float(m.group(2)) for m in
            (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}


def path(f):
    """year by year: aggregate homelessness and that of households aged 26-50 (report_tr50_CA.py's child_hl)"""
    MECH, HB, MB = {}, {}, {}
    for l in gzip.open(f, 'rt', errors='replace'):
        if ' TRANSITION MECH t=' in l:
            MECH[int(l.split('t=')[1].split()[0])] = float(re.search(r'h_1=\s*(\S+)', l).group(1))
        elif l.startswith(' TRANSITION HOMELESS_BY_AGE t=') or l.startswith(' TRANSITION MASS_BY_AGE t='):
            f2 = l.split('t=')[1].split()
            (HB if 'HOMELESS' in l else MB)[int(f2[0])] = [float(x) for x in f2[1:]]
    out = {}
    for t, h in MECH.items():
        hb, mb = HB[t], MB[t]
        for raw, tol in (([x * 1e-14 for x in hb], 1e-6), ([x * m for x, m in zip(hb, mb)], 5e-4)):
            if abs(sum(raw) / sum(mb) / h - 1) < tol:
                hs = [r / m if m > 0 else 0.0 for r, m in zip(raw, mb)]
                out[t] = (h, sum(hs[a] * mb[a] for a in range(25)) / sum(mb[:25]))
                break
        else:
            sys.exit(f'{f}: HOMELESS_BY_AGE t={t} reproduces h_1 on neither scale')
    return out


n, t = levels(os.path.join(ARMS, 'arm_null', 'final.txt')), levels(os.path.join(ARMS, 'arm_tf', 'final.txt'))
pc = lambda k: 100 * (t[k] / n[k] - 1)
assert pc('homelessness h_1') < 0 and pc('drug use b') < 0
cev = welfare_nok.cev_free(os.path.join(ARMS, 'arm_tf')) - welfare_nok.cev_free(os.path.join(ARMS, 'arm_null'))
tf, hf = path(os.path.join(PATHS, 'tf10_run.log.gz')), path(os.path.join(PATHS, 'hf10_run.log.gz'))
T = sorted(k for k in tf if k in hf)
rise = {k: 100 * (tf[k][0] / hf[k][0] - 1) for k in T}
rise_c = {k: 100 * (tf[k][1] / hf[k][1] - 1) for k in T}
assert max(rise.values()) > 0 and max(rise_c.values()) > 0, 'the screen alone does not raise homelessness: rewrite lesson 2'
last = T[-1]
assert rise[last] > 0 and rise_c[last] > 0, 'no longer above Housing First by the last year: rewrite lesson 2'
S = open(STREET).read()
assert 'GUARD SUMMARY: PASS' in S
row = [l for l in S.split('## pooled, years 1-3')[1].splitlines() if l.startswith('| all (the four parts summed) |')][0]
c = [x.strip() for x in row.strip('|').split('|')]
hl_a = [float(x) for x in c[11].split('/')]
hl_b = [float(x) for x in c[12].split('/')]
assert max(hl_b) < 0.05, hl_b
out = {
    'x_ne_b_pc': f"{abs(pc('drug use b')):.0f}",
    'x_ne_sud_pc': f"{abs(pc('SUD lambda_d')):.0f}",
    'x_ne_h_pc': f"{abs(pc('homelessness h_1')):.0f}",
    'x_ne_piv_pc': f"{100 * t['pi_V (voucher probability)']:.2f}",
    'x_ne_cev': f'{cev:.2f}',
    'x_ne_so_h_pc': f'{max(rise.values()):.0f}',
    'x_ne_so_hchild_pc': f'{max(rise_c.values()):.0f}',
    'x_ne_so_last_yr': str(last),
    'x_ne_so_h_last_pc': f'{rise[last]:.0f}',
    'x_ne_so_hchild_last_pc': f'{rise_c[last]:.0f}',
    'x_ne_rv_hl': f'{sum(hl_a) / len(hl_a):.0f}',
}
d = json.load(open(OUT))
d.update(out)
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_noescape:', out)
