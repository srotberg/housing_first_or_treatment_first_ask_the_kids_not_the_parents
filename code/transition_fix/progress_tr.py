# progress_tr.py <run.log> <Housing First arm dir> -- THE FORWARD PASS AS IT RUNS (20 October; the author, on container
# restarts costing a pass: "you can just start from the most recent paths, no?", then "yes" to publishing each period
# as it is computed). Reads the latest forward pass of a live run.log (from its last 'TRANSITION INIT PARENT SHARE
# RESTORED' marker) and prints, for every period it has reached, homelessness and the share of children in a shelter
# against Housing First's steady state, the drug market's distance and pi_V. A launcher publishes this every 20 minutes,
# so a restart no longer loses the periods already computed, and the first periods are visible hours before the pass
# ends. Children in a shelter: homelessness of households aged 26-50, as code/paper/trpaths.py and report_tr50_CA.py.
import gzip, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'paper'))
from trpaths import levels, child_steady  # noqa: E402

log, null = sys.argv[1], sys.argv[2]
op = (lambda p: gzip.open(p, 'rt', errors='replace')) if log.endswith('.gz') else (lambda p: open(p, errors='replace'))
L = op(log).read().splitlines()
start = max([i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [-1])
if start < 0:
    print('no forward pass yet'); sys.exit(0)
MECH, HB, MB, DRUG = {}, {}, {}, {}
for l in L[start:]:
    if ' TRANSITION MECH t=' in l:
        t = int(l.split('t=')[1].split()[0])
        MECH[t] = {k: float(v) for k, v in re.findall(r'(\w+)=\s*([-+0-9.Ee]+)', l.split('t=')[1])}
    elif l.startswith(' TRANSITION HOMELESS_BY_AGE t=') or l.startswith(' TRANSITION MASS_BY_AGE t='):
        f = l.split('t=')[1].split()
        (HB if 'HOMELESS' in l else MB)[int(f[0])] = [float(x) for x in f[1:]]
    else:
        m = re.search(r'TRANSITION DRUG t=\s*(\d+)\s+distance=\s*(\S+)', l)
        if m:
            DRUG[int(m.group(1))] = float(m.group(2))
h0, c0 = levels(os.path.join(null, 'final.txt'))['homelessness h_1'], child_steady(null)
print(f'# the forward pass in progress, {len(MECH)} periods so far; against Housing First h_1 {h0:.6f}, children in a shelter {c0:.6f}')
print(f"  {'period':>6s} {'h_1 vs HF':>10s} {'children vs HF':>15s} {'drug distance':>14s} {'pi_V':>8s}")
for t in sorted(MECH):
    h = MECH[t].get('h_1')
    c = None
    if t in HB and t in MB:
        hb, mb = HB[t], MB[t]
        for raw, tol in (([x * 1e-14 for x in hb], 1e-6), ([x * m for x, m in zip(hb, mb)], 5e-4)):
            if abs(sum(raw) / sum(mb) / h - 1) < tol:
                hs = [r / m if m > 0 else 0.0 for r, m in zip(raw, mb)]
                c = sum(hs[a] * mb[a] for a in range(25)) / sum(mb[:25])
                break
    cs = f'{100 * (c / c0 - 1):+14.2f}%' if c is not None else f"{'--':>15s}"
    ds = f'{DRUG[t]:14.4f}' if t in DRUG else f"{'--':>14s}"
    print(f"  {t:6d} {100 * (h / h0 - 1):+9.2f}% {cs} {ds} {100 * MECH[t].get('pi_v', float('nan')):7.2f}%")
