"""
The quantitative model's T=60 transition, year by year, for the figure and the prose.

usage: python3 code/paper/transition_series.py
       -> results/transition/restart3_loop0/{series.csv, cohorts.csv, alive.csv, reference.json}

THE RUN IS PINNED, not picked.  export_results.py took "the newest log under code/trtf60
that reaches year 26", which silently moves to whichever restart is newest: on 30 September
that was restart 3c, a second iterate seeded from restart 3's output, and it would have moved
the reform cohort's CEV while the prose still said "the first iteration".  The basis is
restart 3's loop 0 (code/trtf60/restart3_killed_1323/run.log): the only complete 59-year
forward pass on the current binary (aed5b190, items 1-9) with every by-age line.  It has NOT
converged (drug market misclears by up to 0.02 and the budget by up to 0.016), so everything
read from it is preliminary.  code/trtf60 is not tracked, so the series are written to
results/ and the figure reads them from there.

Series per year t (the reform lands at the start of year 1):
  b, lambda_d, h_1, p_drug, pi_v      the TRANSITION MECH line
  child_hl     children in a shelter: homelessness of households aged 26-50 (the years a
               child is at home), mass-weighted.  HOMELESS_BY_AGE is the homeless mass times
               1e14 in loop 0 (CALIBRATION_STATE, 29 September 07:15); the scale that
               reproduces h_1 is used, and the script stops if neither does.
  par_use      parents using drugs: the share of households aged 26-50 consuming the drug
               (USE_BY_AGE, the same definition as the steady state's DIAG age lines)
  par_sud      children living with a parent who carries a SUD: households aged 26-50,
               from the SUD_BANDS masses (26-34, 35-44, 45-54 bands), as export_results does
  excluded     the share of the population excluded from the voucher (VOUCHER CENSUS)
Cohorts: the CEV of each cohort born in year b = 1..34 (childhood on the path, adult entry
at b + 25 <= 59), from code/transition_fix/cohort_cev.py on the same log.
Alive at the reform: TRANSITION ALLALIVE and BETTER OFF at t = 1.  These are utils and the
share better off, NOT a CEV: an all-age CEV needs a benchmark welfare curve by age that has
not been computed.
Reference values: the Housing First benchmark (results/counterfactuals_cf_fix2/null_share)
and the Treatment First long run (tf85), from their cf.log.gz, on the same definitions.

Parsing follows the 30 September audit of the transition logs.
"""
import csv
import gzip
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from transition_source import LOG, OUT   # the one pin
CURVE = os.path.join(ROOT, 'code', 'trtf60', 'welfare_curvebaseline_benchmark.dat')
RES = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
KV = re.compile(r'(\w+)=\s*([-+0-9.E]+)')


def first_pass(path):
    lines = open(path, errors='replace').read().splitlines()
    s = [i for i, l in enumerate(lines) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] + [len(lines)]
    return lines[s[0]:s[1]]


def tnum(l):
    return int(re.search(r't=\s*(\d+)', l).group(1))


def vec(l):
    f = l.split('t=')[1].split()
    return int(f[0]), [float(x) for x in f[1:]]


def parse(block):
    S = {k: {} for k in ('MECH', 'HB', 'MB', 'USE', 'SUDB', 'CENSUS', 'ALLALIVE', 'BETTER',
                         'DRUG', 'BUDGET')}
    for l in block:
        if ' TRANSITION MECH t=' in l:
            S['MECH'][tnum(l)] = {k: float(v) for k, v in KV.findall(l.split('t=', 1)[1].split(None, 1)[1])}
        elif ' TRANSITION DRUG t=' in l:
            S['DRUG'][tnum(l)] = {k: float(v) for k, v in KV.findall(l)}
        elif ' TRANSITION BUDGET loop=' in l:
            S['BUDGET'][tnum(l)] = {k: float(v) for k, v in KV.findall(l)}
        elif l.startswith(' TRANSITION HOMELESS_BY_AGE t='):
            t, v = vec(l); S['HB'][t] = v
        elif l.startswith(' TRANSITION MASS_BY_AGE t='):
            t, v = vec(l); S['MB'][t] = v
        elif l.startswith(' TRANSITION USE_BY_AGE t='):
            t, v = vec(l); S['USE'][t] = v
        elif ' TRANSITION SUD_BANDS t=' in l:
            s = [float(x) for x in l.split('sud=')[1].split('mass=')[0].split()]
            m = [float(x) for x in l.split('mass=')[1].split()]
            S['SUDB'][tnum(l)] = (s, m)
        elif ' TRANSITION VOUCHER CENSUS t=' in l:
            S['CENSUS'][tnum(l)] = {k: float(v) for k, v in KV.findall(l)}
        elif ' TRANSITION ALLALIVE t=' in l:
            d = {k: float(v) for k, v in KV.findall(l)}
            S['ALLALIVE'].setdefault(tnum(l), {})[int(d['band'])] = d
        elif ' TRANSITION BETTER OFF t=' in l:
            S['BETTER'][tnum(l)] = {k: float(v) for k, v in KV.findall(l)}
    return S


def hl_share_by_age(S, t):
    h = S['MECH'][t]['h_1']; HB, MB = S['HB'][t], S['MB'][t]
    for raw in ([x * 1e-14 for x in HB], [x * m for x, m in zip(HB, MB)]):
        if abs(sum(raw) / sum(MB) / h - 1) < 1e-6:
            return [r / m if m > 0 else 0.0 for r, m in zip(raw, MB)]
    raise SystemExit(f'HOMELESS_BY_AGE t={t} reproduces h_1 on neither scale')


def band(a):
    """age index 0..24 (ages 26-50) to the SUD_BANDS band 26-34, 35-44, 45-54"""
    return 0 if a <= 8 else 1 if a <= 18 else 2


def parents(S, t):
    w = S['MB'][t][:25]; W = sum(w)
    hs = hl_share_by_age(S, t)
    child_hl = sum(hs[a] * w[a] for a in range(25)) / W
    par_use = sum(S['USE'][t][a] * w[a] for a in range(25)) / W
    s, m = S['SUDB'][t]
    rate = [s[k] / m[k] for k in range(5)]
    par_sud = sum(rate[band(a)] * w[a] for a in range(25)) / W
    return child_hl, par_use, par_sud


def steady(arm):
    """the same quantities at a steady state, from its cf.log.gz (last value printed)"""
    rows, bands, out = {}, {}, {}
    for l in gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace'):
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*sud=\s*(\S+)\s+mass=\s*(\S+)', l)
        if m:
            rows[int(m.group(1))] = tuple(float(m.group(i)) for i in (2, 3, 4))
        m = re.search(r'DIAG disorder rate, band\s+(\d)\s+=\s*(\S+)', l)
        if m:
            bands[int(m.group(1))] = float(m.group(2))
    P = [a for a in rows if 26 <= a <= 50]; W = sum(rows[a][2] for a in P)
    out['child_hl'] = sum(rows[a][0] * rows[a][2] for a in P) / W
    out['par_use'] = sum(rows[a][1] * rows[a][2] for a in P) / W
    k = lambda a: 1 if a <= 34 else 2 if a <= 44 else 3
    out['par_sud'] = sum(bands[k(a)] * rows[a][2] for a in P) / W
    return out


def final_tf85():
    """drug price, pi_V, b, SUD and h_1 under Treatment First and with no policy change,
    from tf85/final.txt (its 'no policy' column is the Housing First benchmark)"""
    keys = {'drug price': 'p_drug', 'pi_V (voucher probability)': 'pi_v', 'drug use b': 'b',
            'SUD lambda_d': 'lambda_d', 'homelessness h_1': 'h_1'}
    hf, tf = {}, {}
    for l in open(os.path.join(RES, 'tf85', 'final.txt')):
        for lab, k in keys.items():
            m = re.match(r'\s+' + re.escape(lab) + r'\s+(\S+)\s+no policy\s+(\S+)', l)
            if m:
                tf[k], hf[k] = float(m.group(1)), float(m.group(2))
    assert len(hf) == len(keys), f'final.txt gave {sorted(hf)}'
    return hf, tf


def main():
    if not os.path.exists(LOG):
        raise SystemExit(f'{LOG} is not on this machine; the series already written are in {OUT}')
    S = parse(first_pass(LOG))
    T = sorted(S['MECH'])
    assert T == list(range(1, 60)), f'the pass covers {T[0]}..{T[-1]}, not 1..59'
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, 'series.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['t', 'b', 'lambda_d', 'h_1', 'p_drug', 'pi_v', 'child_hl', 'par_use', 'par_sud',
                    'excluded', 'drug_gap', 'budget_residual'])
        for t in T:
            M = S['MECH'][t]
            ch, pu, ps = parents(S, t)
            C = S['CENSUS'].get(t, {})
            exc = C['excluded'] / C['total'] if C else float('nan')
            w.writerow([t, M['b'], M['lambda_d'], M['h_1'], M['p_drug'], M['pi_v'], ch, pu, ps, exc,
                        S['DRUG'].get(t, {}).get('distance', float('nan')),
                        S['BUDGET'].get(t, {}).get('residual', float('nan'))])
    # cohorts born after the reform, by the repository's own cohort CEV
    out = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'transition_fix', 'cohort_cev.py'),
                          LOG, CURVE], capture_output=True, text=True).stdout
    rows = re.findall(r'^\s+(\d+)\s+\S+\s+([-+]\d+\.\d+)%\s+\((\S+), (\S+)\)', out, re.M)
    assert rows, 'cohort_cev.py printed no cohorts'
    with open(os.path.join(OUT, 'cohorts.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['born', 'cev_pc', 'childhood', 'adult'])
        for b, c, ch, ad in rows:
            w.writerow([int(b), float(c), float(ch), float(ad)])
    # everyone alive at the reform, t = 1: utils and the share better off
    A, B = S['ALLALIVE'][1], S['BETTER'][1]
    with open(os.path.join(OUT, 'alive.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['band', 'ages', 'mass', 'dV_utils', 'better_off'])
        ages = {0: '26-85', 1: '26-35', 2: '36-45', 3: '46-55', 4: '56-65', 5: '66-75', 6: '76-85'}
        for k in sorted(A):
            d = A[k]
            w.writerow([k, ages.get(k, ''), d['mass'], d['V_reform'] - d['V_bench'], d['better_off']])
    hf, tf = final_tf85()
    ref = {'hf': {**steady('null_share'), **hf}, 'tf': {**steady('tf85'), **tf},
           'better_off_all': B['share_all_ages'], 'better_off_sud': B['share_addicted']}
    json.dump(ref, open(os.path.join(OUT, 'reference.json'), 'w'), indent=1)
    print(f'wrote {OUT}: {len(T)} years, {len(rows)} cohorts, {len(A)} age bands')


if __name__ == '__main__':
    main()
