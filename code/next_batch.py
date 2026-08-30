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

HERE = os.path.dirname(os.path.abspath(__file__))

GATE = {'b': 0.05, 'lambda_d': 0.05}     # the author's five per cent, on both
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
    through = []
    for tag, (v, m) in A.items():
        if all(g in m and gap(g, m[g]) <= GATE[g] for g in GATE):
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
        nv = dict(v); nv[param] = f'{x1:.7g}'
        lines.append((param, mom, x0, x1, e, 100 * (cur / tgt - 1),
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
    out = os.path.join(HERE, f'CORRECT_{n}.txt')
    with open(out, 'w') as fh:
        fh.write(body)
    print(f'{len(lines)} correction arms written to {os.path.basename(out)}, '
          f'from point_{tag}, one coordinate each:\n')
    print(f'{"parameter":52s} {"moment":10s} {"gap":>7s} {"elast":>7s} {"from":>10s} {"to":>10s}')
    for p, mo, x0, x1, e, g, _ in lines:
        print(f'{p:52s} {mo:10s} {g:+6.0f}% {e:+7.2f} {x0:10.5g} {x1:10.5g}')
    for s in skipped:
        print(f'  skipped: {s}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
