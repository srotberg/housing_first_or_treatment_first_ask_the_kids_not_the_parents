#!/usr/bin/env python3
"""Iterate delta_d, delta_h and omega_c onto their targets, one run at a time.

THE UPDATE IS A DIAGONAL SECANT, which is the right approximation here and not
laziness: delta_d moves children of parents with a substance use disorder,
delta_h moves children of homeless parents, and those are different class
blocks. The cross terms run only through general equilibrium and through class
3, which carries 0.66 per cent of the population.

EVERY READING COMES FROM THE BLOCK AFTER `FROZEN CONVERGED`. omega prints
twice and the earlier print is taken off a state that is not an equilibrium;
reading the wrong one produced 0.0824 against a true 0.00755 in this session.
"""
import glob, math, os, re, subprocess, sys, time

D = '/home/user/housing_first_or_treatment_first/code'
VEC = open('/tmp/claude-0/vec.txt').read().split()
# The anchor's timestamp. Logs older than this were produced by a different
# build -- a different number of voucher states, or one child class -- and a
# secant across two builds is not a secant.
FIRST = 'variant_save_20260910T032800Z.log'

TARGETS = {'odds_d': 2.00, 'odds_h': 2.10, 'omega': 0.18343195266272194}
# parameter -> (moment, how the parameter enters in logs)
OWNS = {'penalty_child_addicted': ('odds_d', 'penalty'),
        'penalty_child_homeless': ('odds_h', 'penalty'),
        'weight_on_child':        ('omega',  'level')}
CLAMP = {'penalty_child_addicted': (0.02, 0.95),
         'penalty_child_homeless': (0.02, 0.60),
         'weight_on_child':        (0.001, 1.0)}
TOL = 0.05          # relative, on every one of the three
MAX_RUNS = 10


def parse(path):
    """(params, moments) from a finished, converged log; None if not usable."""
    txt = open(path, errors='replace').read()
    if 'FROZEN CONVERGED' not in txt:
        return None
    cut = txt.rindex('FROZEN CONVERGED')
    tail, head = txt[cut:], txt
    p = {}
    for name in OWNS:
        m = re.findall(r'HANDOVER ' + name + r':\s*\S+\s*->\s*(\S+)', head)
        if m:
            p[name] = float(m[-1].replace('D', 'E'))
    # THE FROZEN DISTANCE IS THE RESOLUTION OF EVERY MOMENT IN THIS RUN.
    # omega is the difference between two solves of a model that is itself only
    # pinned to that distance, so an omega whose numerator is below it is noise
    # and must not be fitted to. Measured at delta_d=0.36: the child term moved
    # b by 2.15e-5 against a frozen distance of 2.47e-4.
    fd = re.findall(r'FROZEN CONVERGED after\s+\d+\s+passes, distance=\s*(\S+)', tail)
    frozen = float(fd[-1].replace('D', 'E')) if fd else None
    base = re.findall(r'OMEGA_DIAG baseline users=\s*(\S+)', tail)

    mom = {}
    for key, pat in (('odds_d', r'delta_d child SUD odds ratio\s+model=\s*(\S+)'),
                     ('odds_h', r'delta_h child homeless odds ratio\s+model=\s*(\S+)'),
                     ('omega',  r'MOMENT omega.*?model=\s*(\S+)')):
        m = re.findall(pat, tail)
        if m:
            mom[key] = float(m[-1].replace('D', 'E'))
    if len(p) != 3 or len(mom) != 3:
        return None
    # Flag omega as unresolved when the counterfactual's own move in b is
    # smaller than five times the distance the equilibrium is pinned to.
    if frozen is not None and base:
        signal = abs(mom['omega']) * float(base[-1].replace('D', 'E'))
        mom['omega_resolved'] = signal > 5.0 * frozen
    else:
        mom['omega_resolved'] = False
    return p, mom


def points():
    out = []
    for f in sorted(glob.glob(os.path.join(D, 'variant_save_*.log'))):
        if os.path.basename(f) < FIRST:
            continue
        got = parse(f)
        if got:
            out.append(got + (os.path.basename(f),))
    return out


def x_of(name, value):
    """The scale a secant is taken on. A penalty acts through (1 - penalty)."""
    return (1.0 - value) if OWNS[name][1] == 'penalty' else value


def invert(name, x):
    return (1.0 - x) if OWNS[name][1] == 'penalty' else x


def propose(pts):
    """Next triple, by a diagonal secant on the two most recent points."""
    (p2, m2, _), = [pts[-1]]
    if len(pts) < 2:
        return None
    p1, m1, _ = pts[-2]
    nxt = dict(p2)
    for name, (key, _kind) in OWNS.items():
        if key == 'omega' and not (m1.get('omega_resolved') and m2.get('omega_resolved')):
            # Both readings must be above the noise floor or the secant is a
            # line through two pieces of solver noise.
            continue
        t = TARGETS[key]
        x1, x2 = x_of(name, p1[name]), x_of(name, p2[name])
        y1, y2 = m1[key], m2[key]
        if min(x1, x2, y1, y2) <= 0:
            continue
        if abs(math.log(x2) - math.log(x1)) < 1e-9 or abs(math.log(y2) - math.log(y1)) < 1e-9:
            # This parameter did not move between the two, or its moment did
            # not respond. Fall back to the level elasticity through this point.
            e = math.log(y2) / math.log(x2) if abs(math.log(x2)) > 1e-9 else None
            if not e:
                continue
        else:
            e = (math.log(y2) - math.log(y1)) / (math.log(x2) - math.log(x1))
        if abs(e) < 1e-6:
            continue
        step = (math.log(t) - math.log(y2)) / e
        # DAMPED. A secant on a response that is flat and then steep can land
        # anywhere, and every wild step costs thirty-five minutes.
        step = max(-0.7, min(0.7, step))
        lo, hi = CLAMP[name]
        nxt[name] = max(lo, min(hi, invert(name, math.exp(math.log(x2) + step))))
    return nxt


def gaps(m):
    return {k: abs(m[k] - TARGETS[k]) / TARGETS[k] for k in TARGETS}


def main():
    launched = 0
    while launched < MAX_RUNS:
        pts = points()
        if not pts:
            print('no converged point yet; waiting'); time.sleep(120); continue
        p, m, f = pts[-1]
        g = gaps(m)
        print(f'[{time.strftime("%H:%M:%S")}] {len(pts)} points; newest {f}')
        print(f'   d={p["penalty_child_addicted"]:.4f} h={p["penalty_child_homeless"]:.4f} '
              f'w={p["weight_on_child"]:.4f}  ->  odds_d={m["odds_d"]:.4f} '
              f'odds_h={m["odds_h"]:.4f} omega={m["omega"]:.6f}')
        print(f'   gaps: ' + ', '.join(f'{k} {100*v:.1f}%' for k, v in g.items()))
        if not m.get('omega_resolved'):
            print('   omega is BELOW the solver floor at this weight and is not '
                  'being fitted to; the two odds ratios still are')
        if max(g.values()) <= TOL:
            print('ON TARGET. Stopping; the one-class recalibration is next.')
            return 0
        nxt = propose(pts)
        if nxt is None:
            print('only one point; waiting for the queued probe'); time.sleep(180); continue
        if all(abs(nxt[k] - p[k]) < 1e-6 for k in nxt):
            print('the proposal did not move; stopping rather than re-running it')
            return 0
        args = ['bash', 'run_variant.sh', 'save'] + VEC + ['measure_child_gap=1'] + \
               [f'{k}={v:.6g}' for k, v in nxt.items()]
        print('   next: ' + ' '.join(f'{k}={v:.6g}' for k, v in nxt.items()), flush=True)
        with open(os.path.join(D, f'fit_iter_{launched}.log'), 'w') as fh:
            subprocess.run(args, cwd=D, stdout=fh, stderr=subprocess.STDOUT)
        launched += 1
    print('hit the run cap; stopping rather than grinding')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
