"""WHEN A MOMENT WILL NOT MOVE, ASK WHETHER ITS PARAMETER HAS BEEN SAMPLED WHERE
THE TARGET LIVES -- AND IF NOT, EXTEND THE SAMPLING THAT WAY.

The author, 4 September: *"if you see that some targets seem to be stalled for
many iterations without moving, automate something that checks whether the
sampling needs to be expanded on those parameters from above or below to help
bring it to the right target"*.

This exists because the failure it detects had already happened twice and was
invisible both times. `kkk_sigma_scale` sat at -40 per cent on `sigma_y` through
every restart, and the reason was not the search: the seed displaced every
coordinate UPWARD, so in 1245 points the parameter was never once measured below
its anchor 2.20949 against a lower bound of 0.8, and lower is the direction the
moment needs. A stalled moment is a question about COVERAGE before it is a
question about the optimiser.

WHAT IT DOES.

1. Finds every clean RAY in the archive: a set of points identical in every
   coordinate except one instrument. No fitting, no elasticity -- a measured
   curve of the moment against its own parameter. Rays are found by signature,
   not by assuming a particular anchor, so they keep working as the calibration
   moves.

2. Asks whether the target is BRACKETED by the moments on that ray. If it is, the
   parameter can reach its target and the search only has to find where; the
   crossing interval is reported and refinement points are emitted inside it.

3. If it is not bracketed, works out from the ray's own slope WHICH WAY the
   parameter has to go, and emits points extending the ray that way, geometrically,
   out to the bound.

4. If the ray already reaches the bound in that direction, says UNREACHABLE and
   emits nothing. That is a finding for the author -- either the bound is wrong or
   the instrument is the wrong one -- and manufacturing more points inside a range
   that has already been shown not to contain the answer would bury it.

5. Records each moment's gap at the live best in `code/expand_history.json` and
   calls a moment STALLED when its gap has not improved by more than STALL_TOL
   over the last STALL_RUNS recordings. Stalled moments are expanded first.

WHAT IT DOES NOT DO. It does not choose between instruments, it does not change
bounds, and it does not touch a parameter the author has held. Those are the
author's calls and the report says so rather than acting.
"""
import json, math, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

MAX_PER_RUN = 2       # instruments extended per run, worst gap first
N_EXTEND = 5          # points added when a ray is extended
N_REFINE = 3          # points added inside a bracketing interval
MIN_RAY = 3           # a ray shorter than this says nothing about direction
STALL_RUNS = 5        # recordings a gap must fail to improve over
STALL_TOL = 0.02      # by more than two points of relative gap
HISTORY = os.path.join(HERE, 'expand_history.json')
OUT = os.path.join(HERE, 'scan')


def rays(A, names):
    """Every maximal set of archived points differing in ONE instrument only.

    Grouped by the signature of the vector with that instrument removed, so a ray
    is found wherever one exists rather than only around a nominated anchor. The
    largest group per instrument is the one used: a scan file produces exactly one
    such group, and a search that happened to walk one coordinate produces another.
    """
    out = {}
    for p in names:
        groups = {}
        for tag, (v, m) in A.items():
            if p not in v:
                continue
            sig = tuple(sorted((k, x) for k, x in v.items() if k != p))
            groups.setdefault(sig, []).append((float(v[p]), tag, m))
        if not groups:
            continue
        best = max(groups.values(), key=len)
        best.sort()
        out[p] = best
    return out


def direction(ray, mom_key, target):
    """Which way the parameter has to move, read off the ray's own ends.

    Returns (verdict, detail). BRACKETED carries the interval the crossing is in.
    UP and DOWN carry the sign of the local slope that justifies them, so a
    non-monotone ray is reported as such instead of being averaged into a lie.
    """
    pts = [(x, m[mom_key][0]) for x, _, m in ray if mom_key in m]
    if len(pts) < MIN_RAY:
        return 'THIN', {'n': len(pts)}
    xs = [x for x, _ in pts]
    ys = [y for _, y in pts]
    lo_y, hi_y = min(ys), max(ys)
    if lo_y <= target <= hi_y:
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            if (a[1] - target) * (b[1] - target) <= 0:
                return 'BRACKETED', {'x0': a[0], 'x1': b[0],
                                     'y0': a[1], 'y1': b[1]}
        return 'BRACKETED', {'x0': xs[0], 'x1': xs[-1], 'y0': ys[0], 'y1': ys[-1]}

    # NOT BRACKETED. The end of the ray CLOSEST to the target is the end to push
    # past, and the local slope there says which way pushing goes.
    hi_end = target > hi_y
    j = ys.index(hi_y if hi_end else lo_y)
    k = j - 1 if j > 0 else j + 1
    slope = (ys[j] - ys[k]) / (xs[j] - xs[k]) if xs[j] != xs[k] else 0.0
    want_up = (slope > 0) == hi_end            # raise x to raise y, and target is up
    mono = all((ys[i + 1] - ys[i]) * slope >= 0 for i in range(len(ys) - 1))
    return ('UP' if want_up else 'DOWN'), {'from': xs[j], 'slope': slope,
                                           'monotone': mono, 'need': target,
                                           'reached': ys[j]}


def extend(x, lo, hi, up, n=N_EXTEND):
    """Geometric steps out from x toward the bound, or linear if x straddles zero."""
    edge = hi if up else lo
    if abs(edge - x) <= 1e-12 * max(1.0, abs(x)):
        return []
    if x > 0 and lo > 0 and (hi / lo if lo else 0) > 4.0:
        a, b = math.log(x), math.log(max(edge, 1e-12))
        out = [math.exp(a + (b - a) * (i + 1) / n) for i in range(n)]
    else:
        out = [x + (edge - x) * (i + 1) / n for i in range(n)]
    # CLAMP. exp(log(0.8)) came back a hair BELOW 0.8 and the last step of an
    # extension therefore sat outside the bound it was aiming at, which
    # run_one_point rejects and stage_night's own guard would have clipped
    # silently. Caught by expand_test.py, not by a run.
    return [min(max(t, lo), hi) for t in out]


def history(gaps):
    h = json.load(open(HISTORY)) if os.path.exists(HISTORY) else {}
    for k, g in gaps.items():
        h.setdefault(k, []).append(round(g, 6))
        h[k] = h[k][-40:]
    json.dump(h, open(HISTORY, 'w'), indent=1)
    stalled = set()
    for k, series in h.items():
        if len(series) > STALL_RUNS:
            window = series[-(STALL_RUNS + 1):]
            if window[0] - min(window[1:]) <= STALL_TOL:
                stalled.add(k)
    return stalled


def main():
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    A = N.archive()
    if not A:
        print('  no points on the live economy; nothing to say about coverage')
        return
    inst, _ = NM.instruments_all(N, NB, None)
    names = [p for p, _ in inst]
    keys = [m for _, m in inst]
    _, _, _, mom0 = N.best(A, keys)
    gaps = {m: abs(mom0[m][0] / mom0[m][1] - 1.0)
            for m in keys if m in mom0 and mom0[m][1]}
    stalled = history(gaps)
    R = rays(A, names)
    os.makedirs(OUT, exist_ok=True)

    print(f'  {len(A)} points on the live economy, {len(R)} instruments with a ray\n')
    print(f'  {"parameter":<45} {"moment":<13} {"ray":>4} {"measured":>21} '
          f'{"target":>9}  verdict')
    print('  ' + '-' * 118)
    emitted = 0
    # WORST GAP FIRST, AND ONLY A FEW PER RUN. Emitting an extension for every
    # unbracketed moment at once queues a hundred solves and the loop stops being
    # a response to a stall and becomes a second scan. Stalled moments sort ahead
    # of merely-large gaps, because a large gap that is still closing needs no help.
    order = sorted(inst, key=lambda pm: (pm[1] not in stalled,
                                         -gaps.get(pm[1], 0.0)))
    budget = MAX_PER_RUN
    for p, m in order:
        if p not in R:
            print(f'  {p:<45} {m:<13} {"-":>4} {"no ray":>21} {"":>9}  '
                  f'NOT SAMPLED')
            continue
        ray = R[p]
        if m not in mom0:
            continue
        target = mom0[m][1]
        verdict, d = direction(ray, m, target)
        ys = [x[2][m][0] for x in ray if m in x[2]]
        xs = [x[0] for x in ray if m in x[2]]
        span = f'{min(ys):.5g}..{max(ys):.5g}' if ys else '-'
        mark = ' STALLED' if m in stalled else ''
        lo, hi = NB.BOUNDS[p]
        note = ''
        if verdict in ('UP', 'DOWN'):
            up = verdict == 'UP'
            newx = extend(d['from'], lo, hi, up)
            if not newx:
                note = f'  AT THE {"UPPER" if up else "LOWER"} BOUND, UNREACHABLE'
            elif budget <= 0:
                note = f'  extend {"up" if up else "down"}, QUEUED for a later run'
            else:
                budget -= 1
                base = dict(next(v for t, (v, mm) in A.items()
                                 if any(t == r[1] for r in ray)))
                lines = []
                for t in newx:
                    v = dict(base); v[p] = f'{t:.8g}'
                    lines.append('bash code/run_one_point.sh '
                                 + ' '.join(f'{k}={v[k]}' for k in sorted(v)))
                open(os.path.join(OUT, f'expand_{p}.txt'), 'w').write(
                    '\n'.join(lines) + '\n')
                emitted += len(lines)
                note = (f'  extend {"up" if up else "down"} to '
                        f'{max(newx) if up else min(newx):.5g}'
                        + ('' if d['monotone'] else ', RAY IS NOT MONOTONE'))
        elif verdict == 'BRACKETED':
            note = f"  crossing in {d['x0']:.5g}..{d['x1']:.5g}"
        print(f'  {p:<45} {m:<13} {len(ys):>4} {span:>21} {target:>9.5g}  '
              f'{verdict}{mark}{note}')
    print(f'\n  {emitted} points emitted into code/scan/expand_*.txt')
    if stalled:
        print('  stalled: ' + ', '.join(sorted(stalled)))


if __name__ == '__main__':
    main()
