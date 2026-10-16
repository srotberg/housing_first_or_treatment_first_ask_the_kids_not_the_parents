# report_tr70_Cu.py <run.log[.gz]> <null arm dir> <tf arm dir> -- remote_tr70_Cu.sh's per-loop report (16 October; the
# author asked for T = 70 because at T = 50 homelessness and the share of children in a shelter were still above their
# long-run values in year 49). From the latest complete forward pass of the log (the one ending at its last
# 'TRANSITION PATHS SAVED'): the worst budget residual (t > 1) and drug gap of that pass, and homelessness h_1 and the
# share of children in a shelter in years 1, 10, 30, 50 and 69 against the long run (the terminal Treatment First arm)
# and against the Housing First the path starts from. Children in a shelter as report_tr50_CA.py (and
# paper/transition_series.py's child_hl): the homelessness of households aged 26-50, mass-weighted, the steady states'
# from their last DIAG age lines.
import gzip, os, re, sys

log, null_dir, tf_dir = sys.argv[1:4]
YEARS = (1, 10, 30, 50, 69)
op = (lambda p: gzip.open(p, 'rt', errors='replace')) if log.endswith('.gz') else (lambda p: open(p, errors='replace'))
L = op(log).read().splitlines()
marks = [i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l]
saved = [i for i, l in enumerate(L) if 'TRANSITION PATHS SAVED after loop' in l]
assert marks and saved, 'no complete forward pass in the log'
end = saved[-1]
start = max(i for i in marks if i < end)
loop = int(re.search(r'after loop\s+(\d+)', L[end]).group(1))
P = L[start:end + 1]


def tnum(l):
    return int(re.search(r't=\s*(\d+)', l).group(1))


def vec(l):
    f = l.split('t=')[1].split()
    return int(f[0]), [float(x) for x in f[1:]]


MECH, HB, MB = {}, {}, {}
bud = drug = 0.0
for l in P:
    if ' TRANSITION MECH t=' in l:
        MECH[tnum(l)] = {k: float(v) for k, v in re.findall(r'(\w+)=\s*([-+0-9.Ee]+)', l.split('t=', 1)[1].split(None, 1)[1])}
    elif l.startswith(' TRANSITION HOMELESS_BY_AGE t='):
        t, v = vec(l); HB[t] = v
    elif l.startswith(' TRANSITION MASS_BY_AGE t='):
        t, v = vec(l); MB[t] = v
    m = re.search(r'TRANSITION BUDGET loop=\s*(\d+)\s+t=\s*(\d+).*residual=\s*(\S+)', l)
    if m and int(m.group(2)) > 1:
        bud = max(bud, abs(float(m.group(3))))
    m = re.search(r'TRANSITION DRUG t=\s*(\d+)\s+distance=\s*(\S+)', l)
    if m:
        drug = max(drug, abs(float(m.group(2))))


def child_hl(t):
    h = MECH[t]['h_1']; hb, mb = HB[t], MB[t]
    for raw, tol in (([x * 1e-14 for x in hb], 1e-6), ([x * m for x, m in zip(hb, mb)], 5e-4)):
        if abs(sum(raw) / sum(mb) / h - 1) < tol:
            hs = [r / m if m > 0 else 0.0 for r, m in zip(raw, mb)]
            w = mb[:25]
            return sum(hs[a] * w[a] for a in range(25)) / sum(w)
    raise SystemExit(f'HOMELESS_BY_AGE t={t} reproduces h_1 on neither scale')


def steady(d):
    rows, h1 = {}, None
    for l in gzip.open(os.path.join(d, 'cf.log.gz'), 'rt', errors='replace'):
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*sud=\s*(\S+)\s+mass=\s*(\S+)', l)
        if m:
            rows[int(m.group(1))] = (float(m.group(2)), float(m.group(4)))
    for l in open(os.path.join(d, 'final.txt')):
        m = re.match(r'\s+homelessness h_1\s+([-+0-9.Ee]+)', l)
        if m:
            h1 = float(m.group(1))
    A = [a for a in rows if 26 <= a <= 50]
    assert len(A) == 25 and h1, f'{d}: {len(A)} DIAG ages, h_1 {h1}'
    W = sum(rows[a][1] for a in A)
    return h1, sum(rows[a][0] * rows[a][1] for a in A) / W


pct = lambda x, y: 100 * (x / y - 1)
h0, c0 = steady(null_dir)
hT, cT = steady(tf_dir)
T = sorted(MECH)
print(f'  binary loop {loop}, periods {T[0]}-{T[-1]}: worst budget residual (t>1) {bud:.2e}, worst drug gap {drug:.2e}')
print(f'  long run (terminal Treatment First): h_1 {hT:.6f}, children in a shelter {cT:.6f}; '
      f'Housing First (start): h_1 {h0:.6f}, children in a shelter {c0:.6f}')
print(f"  {'year':>4s} {'h_1':>10s} {'vs long run':>12s} {'vs HF':>8s} {'children in a shelter':>22s} {'vs long run':>12s} {'vs HF':>8s}")
for t in YEARS:
    if t not in MECH or t not in HB or t not in MB:
        print(f'  {t:4d} not in this pass'); continue
    h, c = MECH[t]['h_1'], child_hl(t)
    print(f'  {t:4d} {h:10.6f} {pct(h, hT):+11.2f}% {pct(h, h0):+7.2f}% {c:22.6f} {pct(c, cT):+11.2f}% {pct(c, c0):+7.2f}%')
