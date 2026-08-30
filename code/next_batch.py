#!/usr/bin/env python3
"""Wait until b and lambda_d are both within five per cent, then correct the rest.

THE AUTHOR, 30 AUGUST 02:35: "once you are 5% away from both lambda_d and b, then
automatically start spawning the algorithm to converge on the other parameters",
and earlier, "the rest i think are much easier and you can slowly converge on
them". This is that gate and that algorithm, so the engine fires it on its own
rather than waiting for someone to notice the gate has opened.

WHY A GATE AND NOT A JOINT SOLVE OVER EVERYTHING. b and lambda_d are the pair
the whole search has failed on -- lambda_d was the worst moment at 70 of 110
points -- and they are reached through two instruments whose elasticities are
enormous and curved: addiction_scalar_1 moves b with an elasticity between -12
and -26 depending where you stand. Every other moment on the list has an
instrument with an elasticity between 0.7 and 2, measured, with the target
already spanned. Those are different problems and mixing them is what produced
twenty two hours of flat loss. So the drug block is closed first, on the locus,
and only then does this open.

THE STEP IS DAMPED AND SINGLE-COORDINATE. Each line moves ONE parameter, which
keeps every point a clean arm of the Jacobian as well as a correction, so a batch
that overshoots still buys the derivative it was missing. The step is
Newton on that parameter's own measured elasticity, damped, and capped in
e-folds, because the author asked to converge slowly and because an undamped
step through an elasticity measured somewhere else is exactly how the aimed
steps missed by factors of three and five.

ELASTICITIES ARE MEASURED, NOT ASSUMED. They come from pairs of archive points
differing in ONE coordinate, nearest the winning point first. A parameter with no
such pair gets no line, and says so, rather than being moved on a guess.
"""
import glob
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# THE GATE OPENS AT FIVE PER CENT; THE BASE IS THEN CHOSEN AT TEN.
# "once you are 5% away from both lambda_d and b, then automatically start
# spawning the algorithm to converge on the other parameters" is a condition for
# STARTING the correction phase, and it has been met. Holding every subsequent
# base to five per cent as well is stricter than the author's actual rule and has
# started to block progress: the tau_u correction took the worst gap from 82 to
# 70 per cent and is the best point in the archive, but its lambda_d sits at +7
# and the five per cent test rejects it as a base, so the loop would keep
# correcting from a worse point indefinitely.
#
# So the phase opens at five and the base is then the best point by worst-gap
# among those inside TEN, which is the standard the author set for the paper. A
# base whose drug block has drifted past five still gets repaired -- a restore
# line is emitted alongside the arms -- so the drift is corrected in parallel
# rather than being allowed to accumulate.
GATE = {'b': 0.05, 'lambda_d': 0.05}     # opens the phase
BASE_TOL = {'b': 0.10, 'lambda_d': 0.10}  # admissible as a base thereafter
RESTORE_AT = 0.05                         # emit a repair line beyond this
ACCEPT = 0.10                             # the author's ten per cent rule
DAMP = 0.70                               # converge slowly, do not jump
MAX_EFOLD = 0.35                          # no single step larger than this

# Parameter -> the moment it owns. Taken from the Fortran's own adjusters, which
# is why relative_share_of_addiction_1 is paired with theta: the model updates it
# against drug_share_weighted_1 - drug_spending_share_data and clamps it between
# variables named theta_lo and theta_hi. It is NOT a free instrument for the
# disorder ratio, which is the error that flattened the loss.
OWN = {
    'utility_cost_of_treatment':                           'tau_u',
    'probability_becoming_unemployed':                     'pi_eu',
    'relative_share_of_addiction_1':                       'theta',
    'mu_homeless':                                         'mu_H',
    'lambda_m':                                            'lambda_m',
    # THE SECOND HALF OF THE SMI PAIR. The parameter lambda_m moves BOTH SMI
    # moments the same way -- raising it 0.067 to 0.12 took the share of the
    # homeless 0.154 to 0.105 AND the population share 0.045 to 0.028 -- so it
    # cannot fix one without breaking the other. smi_onset_level owns the
    # population share: a controlled pair moves p_m by -6 per cent for a -20 per
    # cent step while barely touching the share of the homeless, +1.25 per cent.
    # Two moments, two instruments; only one of them had ever been listed.
    'smi_onset_level':                                     'p_m',
    'value_of_life':                                       'aleph',
    'multiple_of_probabilities_of_employment_if_addicted': 'kappa_ued',
    'probability_of_voucher_benchmark_used':               'pi_V',
    'max_food_cost':                                       'cbar',
    'size_homelessness':                                   'h_1',
    'kappa_uem':                                           'kappa_uem',
}
BOUNDS = {
    'utility_cost_of_treatment':                           (0.0001, 10.0),
    'probability_becoming_unemployed':                     (1e-6, 0.500),
    'relative_share_of_addiction_1':                       (0.40, 0.58),
    'mu_homeless':                                         (0.05, 1.0),
    'lambda_m':                                            (0.046, 0.500),
    'smi_onset_level':                                     (1e-5, 0.5),
    'value_of_life':                                       (1.0, 500.0),
    'multiple_of_probabilities_of_employment_if_addicted': (1.0, 50.0),
    'probability_of_voucher_benchmark_used':               (0.0001, 0.999),
    'max_food_cost':                                       (0.0001, 1.0),
    'size_homelessness':                                   (0.01, 5.0),
    'kappa_uem':                                           (1.0, 100.0),
}
# beta is banded on the author's instruction; h_2 is conceded.
BAND = {'beta': (3.0, 4.5)}
SKIP = {'h_2'}



FREE = ('lambda_addiction', 'addiction_scalar_1')
FREE_BOUNDS = {'lambda_addiction': (0.5, 20000.0), 'addiction_scalar_1': (1e-30, 1.0)}
# A step is compensated when its predicted drift in b exceeds this, and shrunk
# until the drift is no worse than MAX_DRIFT. Both come from the same finding:
# four of the nine instruments drag b and lambda_d with them -- value_of_life by
# -85 per cent, theta -74, pi_eu +44, kappa_ued +42 -- so moving them bare trades
# one wrong moment for two right ones.
COUPLED_AT = 0.10
MAX_DRIFT = 0.20


def drug_jacobian(A):
    """d ln(b, lambda_d) / d ln(lambda_addiction, addiction_scalar_1), refit local.

    Comparable points only: identical in every coordinate except the two free
    ones. locus.py uses the same filter because four points once read b from
    0.138 to 0.283 at identical lambda and addiction_scalar_1, differing only in
    probability_becoming_unemployed.
    """
    import numpy as np
    groups = {}
    for tag, (v, m) in A.items():
        if 'b' not in m or 'lambda_d' not in m:
            continue
        b, d = m['b'][0], m['lambda_d'][0]
        lam = float(v.get('lambda_addiction', 0))
        if b <= 0 or d <= 0 or not (15.0 <= lam <= 19.0):
            continue
        key = tuple(sorted((k, x) for k, x in v.items() if k not in FREE))
        groups.setdefault(key, []).append((lam, float(v['addiction_scalar_1']), b, d))
    if not groups:
        return None, 0
    best = max(groups.values(), key=len)
    if len(best) < 4:
        return None, len(best)
    X = np.column_stack([np.ones(len(best)), [math.log(p[0]) for p in best],
                         [math.log(p[1]) for p in best]])
    rows = []
    for i in (2, 3):
        c, *_ = np.linalg.lstsq(X, np.array([math.log(p[i]) for p in best]), rcond=None)
        rows.append(c[1:])
    return np.array(rows), len(best)


def coupling(A, param, base_v, base_m):
    """Per e-fold of this parameter, the log change it causes in b and lambda_d.

    Searched over ANY pair of archive points differing in this one coordinate,
    not only pairs anchored at the current base. The base moves every round --
    the gate re-opens on whichever point is best -- so a base-anchored search
    finds nothing the moment the base advances, which is exactly what happened
    the first time this was wired up: every arm came back uncoupled because the
    arms had been measured at the PREVIOUS base and the new one differed from
    them in five coordinates. Coupling is a property of the instrument, so the
    pair that measures it does not have to touch the base at all.

    The pair nearest the base in this coordinate wins, since these elasticities
    are strongly local.
    """
    best = None
    x_base = float(base_v[param]) if param in base_v else None
    items = list(A.items())
    for i in range(len(items)):
        ta, (va, ma) = items[i]
        for j in range(i + 1, len(items)):
            tb, (vb, mb) = items[j]
            if set(va) != set(vb):
                continue
            d = [k for k in va if va[k] != vb[k]]
            if d != [param]:
                continue
            if not all(k in mm for mm in (ma, mb) for k in ('b', 'lambda_d')):
                continue
            xa, xb = float(va[param]), float(vb[param])
            ya, yb = ma['b'][0], mb['b'][0]
            da, db = ma['lambda_d'][0], mb['lambda_d'][0]
            if min(xa, xb, ya, yb, da, db) <= 0 or abs(math.log(xb / xa)) < 1e-9:
                continue
            dx = math.log(xb / xa)
            cand = (math.log(yb / ya) / dx, math.log(db / da) / dx)
            dist = abs(math.log(xa / x_base)) if x_base else 0.0
            if best is None or dist < best[1]:
                best = (cand, dist)
    return best[0] if best else None


def vector(text):
    m = re.search(r'^\s*VECTOR (.*)$', text, re.M)
    return dict(t.split('=', 1) for t in m.group(1).split() if '=' in t) if m else None


def moments(text):
    out = {}
    for n, _, m, tg in re.findall(
            r'MOMENT (\S+)\s+(.*?)model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', text):
        out[n] = (float(m), float(tg))
    return out


def gap(name, pair):
    m, tg = pair
    if name in BAND:
        lo, hi = BAND[name]
        return 0.0 if lo <= m <= hi else min(abs(m / lo - 1), abs(m / hi - 1))
    if m <= 0 and tg > 0:
        return 1.0
    return abs(m / tg - 1)


def archive():
    out = {}
    for f in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        t = open(f).read()
        v, m = vector(t), moments(t)
        if v and 'b' in m and 'lambda_d' in m:
            out[os.path.basename(f)[6:-4]] = (v, m)
    return out


def elasticity(A, param, moment, near):
    """From archive pairs differing in ONE coordinate, the pair nearest `near`."""
    best = None
    for a, (va, ma) in A.items():
        for b, (vb, mb) in A.items():
            if a >= b or set(va) != set(vb):
                continue
            d = [k for k in va if va[k] != vb[k]]
            if d != [param] or moment not in ma or moment not in mb:
                continue
            xa, xb = float(va[param]), float(vb[param])
            ya, yb = ma[moment][0], mb[moment][0]
            if min(xa, xb, ya, yb) <= 0 or abs(math.log(xb / xa)) < 1e-9:
                continue
            e = math.log(yb / ya) / math.log(xb / xa)
            if abs(e) < 1e-6:
                continue
            dist = abs(math.log(xa / float(near[param]))) if float(near[param]) > 0 else 0.0
            if best is None or dist < best[1]:
                best = (e, dist)
    return best[0] if best else None


def main():
    A = archive()
    if not A:
        print('no archive'); return 1

    # The gate: any point with BOTH b and lambda_d inside five per cent, best by
    # worst-gap over everything else.
    opened = any(all(g in m and gap(g, m[g]) <= GATE[g] for g in GATE)
                 for _, m in A.values())
    tol = BASE_TOL if opened else GATE
    through = []
    for tag, (v, m) in A.items():
        if all(g in m and gap(g, m[g]) <= tol[g] for g in tol):
            rest = {k: gap(k, p) for k, p in m.items() if k not in SKIP}
            through.append((max(rest.values()), tag, v, m))
    if not through:
        best = min(((max(gap('b', m['b']), gap('lambda_d', m['lambda_d'])), tag)
                    for tag, (v, m) in A.items()))
        print(f'GATE CLOSED. Best on max(|b gap|,|lambda_d gap|) is {best[1]} at '
              f'{100*best[0]:.1f} per cent; the gate is {100*GATE["b"]:.0f}.')
        print('Keep working the locus. No correction batch emitted.')
        return 2

    through.sort()
    worst, tag, v, m = through[0]
    print(f'GATE OPEN at point_{tag}: b {100*(m["b"][0]/m["b"][1]-1):+.1f}%, '
          f'lambda_d {100*(m["lambda_d"][0]/m["lambda_d"][1]-1):+.1f}%. '
          f'Worst remaining {100*worst:.0f} per cent.\n')

    DJ, ndj = drug_jacobian(A)
    if DJ is not None:
        print(f'drug block refit on {ndj} comparable points, '
              f'condition {np.linalg.cond(DJ):.0f}\n')
    lines, skipped = [], []
    for param, mom in sorted(OWN.items(), key=lambda kv: -gap(kv[1], m[kv[1]]) if kv[1] in m else 0):
        if mom not in m or gap(mom, m[mom]) <= ACCEPT:
            continue
        e = elasticity(A, param, mom, v)
        if e is None:
            skipped.append(f'{param} (owns {mom}): no controlled pair in the archive')
            continue
        cur, tgt = m[mom]
        step = DAMP * math.log(tgt / cur) / e
        step = max(-MAX_EFOLD, min(MAX_EFOLD, step))
        x0 = float(v[param])
        lo, hi = BOUNDS[param]
        x1 = max(lo, min(hi, x0 * math.exp(step)))
        if abs(math.log(x1 / x0)) < 1e-4:
            skipped.append(f'{param} (owns {mom}): at a bound, cannot move')
            continue
        # COMPENSATE A COUPLED STEP INSTEAD OF EMITTING IT BARE. If this
        # instrument drags b, shrink the step until the predicted drift is
        # tolerable and fold in the lambda_addiction and addiction_scalar_1 that
        # cancel what is left. Bare, these arms trade one wrong moment for the
        # two that are finished.
        note = ''
        cpl = coupling(A, param, v, m)
        if cpl and DJ is not None and abs(cpl[0] * step) > COUPLED_AT:
            shrink = min(1.0, abs(math.log(1 + MAX_DRIFT) / (cpl[0] * step)))
            step *= shrink
            x1 = max(lo, min(hi, x0 * math.exp(step)))
            fix = np.linalg.solve(DJ, np.array([-cpl[0] * step, -cpl[1] * step]))
            note = f'  compensated, {shrink:.2f} of step, b drift {100*(math.exp(cpl[0]*step)-1):+.0f}%'
        else:
            fix = None
        nv = dict(v); nv[param] = f'{x1:.7g}'
        if fix is not None:
            for q, z in zip(FREE, fix):
                y0 = float(v[q]); qlo, qhi = FREE_BOUNDS[q]
                nv[q] = f'{max(qlo, min(qhi, y0 * math.exp(z))):.7g}'
        lines.append((param, mom, x0, x1, e, 100 * (cur / tgt - 1), note,
                      'bash code/run_one_point.sh ' +
                      ' '.join(f'{k}={nv[k]}' for k in sorted(nv))))

    # NEVER OVERWRITE A BATCH THAT IS STILL BEING CONSUMED. Workers read their
    # line out of this file and `git pull --rebase` between lines, so rewriting
    # it under them silently swaps the vectors on every line they have not
    # reached yet -- two bases mixed inside one batch, with nothing in the point
    # files to say so. This gate re-opens every firing and would have done
    # exactly that at 04:20, when it rewrote all nine arms from a new base while
    # six of the previous nine were still running. Each round gets its own file.
    n = 1
    while os.path.exists(os.path.join(HERE, f'CORRECT_{n}.txt')):
        n += 1
    # AND DO NOT WRITE A ROUND THAT IS IDENTICAL TO THE LAST ONE. The gate
    # re-runs every half hour; while a round is still solving, nothing it reads
    # has changed, so it would otherwise deposit a byte-identical batch file
    # every firing and the numbering would stop meaning "round".
    body = '\n'.join(l[-1] for l in lines) + ('\n' if lines else '')
    prev = os.path.join(HERE, f'CORRECT_{n-1}.txt') if n > 1 else os.path.join(HERE, 'CORRECT.txt')
    if os.path.exists(prev) and open(prev).read() == body:
        print(f'identical to {os.path.basename(prev)}; nothing new to run.')
        return 3
    # A base whose drug block has drifted gets a repair line of its own, so the
    # arms and the restore run in the same round instead of alternating.
    drift = max(gap('b', m['b']), gap('lambda_d', m['lambda_d']))
    if drift > RESTORE_AT and DJ is not None:
        fix = np.linalg.solve(DJ, np.array([math.log(m['b'][1] / m['b'][0]),
                                            math.log(m['lambda_d'][1] / m['lambda_d'][0])]))
        rv = dict(v)
        for q, z in zip(FREE, fix):
            y0 = float(v[q]); qlo, qhi = FREE_BOUNDS[q]
            rv[q] = f'{max(qlo, min(qhi, y0 * math.exp(z))):.7g}'
        lines.append(('RESTORE drug block', 'b, lambda_d', 0.0, 0.0, 0.0,
                      100 * drift, '  repairs the base itself',
                      'bash code/run_one_point.sh ' +
                      ' '.join(f'{k}={rv[k]}' for k in sorted(rv))))
    out = os.path.join(HERE, f'CORRECT_{n}.txt')
    with open(out, 'w') as fh:
        fh.write(body)
    print(f'{len(lines)} correction arms written to {os.path.basename(out)}, '
          f'from point_{tag}, one coordinate each:\n')
    print(f'{"parameter":52s} {"moment":10s} {"gap":>7s} {"elast":>7s} {"from":>10s} {"to":>10s}')
    for p, mo, x0, x1, e, g, note, _ in lines:
        print(f'{p:52s} {mo:10s} {g:+6.0f}% {e:+7.2f} {x0:10.5g} {x1:10.5g}{note}')
    for s in skipped:
        print(f'  skipped: {s}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
