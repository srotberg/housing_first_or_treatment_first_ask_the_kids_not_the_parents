"""trpaths.py -- reading a T = 70 transition's year-by-year homelessness, its steady states and its newborn welfare
(19 October). path(), child_steady() and levels() were export_noescape.py's; export_alttrans.py reads the same things
for six more paths, so they live here and both import them."""
import gzip, os, re, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import welfare_nok  # noqa: E402


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


def child_steady(d):
    """the share of children in a shelter in a steady state: homelessness of households aged 26-50, mass-weighted, from
    the arm's DIAG age lines (report_tr50_CA.py's steady())"""
    rows = {}
    for l in gzip.open(os.path.join(d, 'cf.log.gz'), 'rt', errors='replace'):
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*sud=\s*(\S+)\s+mass=\s*(\S+)', l)
        if m:
            rows[int(m.group(1))] = (float(m.group(2)), float(m.group(4)))
    A = [a for a in rows if 26 <= a <= 50]
    assert len(A) == 25, (d, len(A))
    return sum(rows[a][0] * rows[a][1] for a in A) / sum(rows[a][1] for a in A)


def latest_loop(run_dir):
    """the run's latest archived loop directory holding a run.log.gz, or None"""
    if not os.path.isdir(run_dir):
        return None
    loops = sorted((d for d in os.listdir(run_dir) if re.fullmatch(r'loop\d+', d)
                    and os.path.exists(os.path.join(run_dir, d, 'run.log.gz'))), key=lambda d: int(d[4:]))
    return os.path.join(run_dir, loops[-1]) if loops else None


def pass_quality(f, target=5.8371628):
    """the latest complete forward pass of a log: the worst budget residual after year 1 as a share of net revenue,
    and the number of years whose drug market sits further than 5e-3 from clearing (0 where the price is held)"""
    L = gzip.open(f, 'rt', errors='replace').read().splitlines()
    saved = [i for i, l in enumerate(L) if 'TRANSITION PATHS SAVED after loop' in l]
    end = saved[-1] if saved else len(L)
    start = max([i for i, l in enumerate(L[:end]) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [0])
    bud, drug = 0.0, 0
    for l in L[start:end]:
        m = re.search(r'TRANSITION BUDGET loop=\s*\d+\s+t=\s*(\d+).*residual=\s*(\S+)', l)
        if m and int(m.group(1)) > 1:
            bud = max(bud, abs(float(m.group(2))) / target)
        m = re.search(r'TRANSITION DRUG t=\s*\d+\s+distance=\s*(\S+)', l)
        if m and abs(float(m.group(1))) > 5e-3:
            drug += 1
    return bud, drug


def reform_cohort_cev(loop_dir, null_dir, tf_dir):
    """the CEV of the cohort born at the reform (code/transition_fix/cohort_cev.py on the loop's log, completed with the
    terminal arm), less Housing First's own CEV on the same curve (welfare_nok.cev_free), percent of lifetime
    consumption"""
    with tempfile.NamedTemporaryFile('w', suffix='.log', delete=False) as t:
        t.write(gzip.open(os.path.join(loop_dir, 'run.log.gz'), 'rt', errors='replace').read())
        tmp = t.name
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'transition_fix', 'cohort_cev.py'), tmp,
                        os.path.join(loop_dir, 'welfare_curvebaseline_benchmark.dat'),
                        '--terminal', os.path.join(tf_dir, 'cf.log.gz'),
                        '--refs', os.path.join(null_dir, 'cf.log.gz'), os.path.join(tf_dir, 'cf.log.gz')],
                       capture_output=True, text=True)
    os.unlink(tmp)
    m = re.search(r'THE COHORT BORN AT THE REFORM \(b = 1\): CEV\s+([+-]?\S+)%', r.stdout)
    assert m, f'{loop_dir}: cohort_cev.py printed no reform cohort: {(r.stderr or r.stdout)[-300:]}'
    return float(m.group(1)) - welfare_nok.cev_free(null_dir)


def mech_series(f, key='b'):
    """one quantity of the latest forward pass of a log, period by period: a TRANSITION MECH field (b, lambda_d, p_drug,
    pi_v, h_1), or 'take_up', the share of households with a SUD in treatment (TRANSITION TREATMENT)"""
    L = gzip.open(f, 'rt', errors='replace').read().splitlines()
    start = max([i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [0])
    tag = ' TRANSITION TREATMENT t=' if key == 'take_up' else ' TRANSITION MECH t='
    out = {}
    for l in L[start:]:
        if tag in l:
            m = re.search(key + r'=\s*(\S+)', l)
            if m:
                out[int(l.split('t=')[1].split()[0])] = float(m.group(1))
    return out
