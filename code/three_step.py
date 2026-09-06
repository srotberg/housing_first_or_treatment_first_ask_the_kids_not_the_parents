#!/usr/bin/env python3
"""One iteration of the author's three-instrument fixed point.

    "H1 to homelessness rate, h2 to cost burdened renters and mass at bottom
    productivity to share of employed homeless."   -- 6 September

Reads the newest point that carries the author's configuration, computes a damped
log step for each of the three instruments against its own moment, and prints the
run_one_point.sh line for the next iterate. three_loop.sh runs it in a loop.

WHY A LOOP AND NOT ANOTHER BATCH. The author, 6 September: *"I think you need to
let my method run for a while and see if the model converges"*. Every round on
6 September moved one coordinate off a base chosen by hand that firing, so the
search never iterated -- it sampled. Twenty-eight points were spent that way and
the base moved five times. A fixed point needs the same map applied to its own
output, repeatedly, and that is all this does.

ONE INSTRUMENT, ONE MOMENT, NO CROSS TERMS. This is deliberately NOT the joint
Newton step that was tried at 18:40. That step solved exactly and then asked for
two instruments 10 and 43 times outside their clamps, because it trusted first
derivatives across a factor-of-ten move. A damped coordinate map cannot do that:
each instrument only ever chases its own moment, every step is bounded, and if the
three are genuinely coupled the loop stalls at a fixed point that SHOWS the
coupling rather than a step that hides it.

THE SIGNS ARE MEASURED, NOT ASSUMED, and two of the three are counter-intuitive
enough that guessing them wrong cost hours on 6 September:

  size_homelessness      -> h_1           +  smaller street, less homelessness
  smallest_rental...     -> h_2           +  cheaper rung, fewer cost burdened
  kkk_s_deviation_bottom -> emp_homeless  -  WIDER bottom pushes mass OFF the
                                             bottom node, so a HIGHER value LOWERS
                                             the employed share of the homeless

THE MASS INSTRUMENT TURNS AT ABOUT 2.2 and its floor here is set there rather than
at the Fortran clamp of 1.0. Measured: emp_homeless is 0.1000 at 3.35, 0.2434 at
2.20 and 0.0392 at 1.60. Below the turn the bottom node stops being a thin
always-homeless sliver and becomes a large low-productivity block whose own
unemployment dominates, so the moment reverses. A step that crosses 2.2 is not a
smaller step in the same direction; it is a different economy.
"""
import glob, hashlib, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

TARGETS = {'h_1': 0.00399, 'h_2': 0.101, 'emp_homeless': 0.46}

# instrument -> (its moment, fallback slope, lower bound, upper bound)
#
# The fallbacks are the median controlled slopes measured on 6 September and are
# used only until the loop has generated a controlled pair of its own. Each is
# recorded with the range it was measured over so a later reader can see how
# trustworthy it is: the rung's was +3.22 to +7.86 and is the shakiest.
RULES = {
    'size_homelessness':                        ('h_1',          +0.30, 1e-4, 0.20),
    'smallest_rental_relative_to_lowest_income': ('h_2',          +5.36, 5e-3, 0.40),
    'kkk_s_deviation_bottom':                   ('emp_homeless', -2.65, 2.20, 6.00),
}

# The author's configuration. A point is an iterate of THIS loop only if every one
# of these matches: delta zero, the street's 20 per cent penalty on, the second and
# third productivity nodes merged with the lowest left alone, and no endowment.
# The endowment is in this list because it was added without being asked for and
# then carried into four bases; pinning it here is what stops that recurring.
CONFIG = {
    'homeless_job_penalty_pp':    0.0,
    'increased_prob_if_homeless': 0.20,
    'merge_from_node':            2.0,
    'merge_bottom_nodes':         3.0,
    'newborn_endowment_scale':    0.0,
}

DAMP = 0.55          # a full step on a slope measured elsewhere overshoots
MAX_EFOLD = 0.60     # no single move larger than a factor of 1.8


def model_hash():
    p = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
    return hashlib.md5(open(p, 'rb').read()).hexdigest()[:10]


def parse(path):
    s = open(path, errors='replace').read()
    m = re.search(r'^MODEL (\S+)', s, re.M)
    v = re.search(r'^VECTOR (.*)$', s, re.M)
    if not m or not v:
        return None
    vec = {}
    for tok in v.group(1).split():
        if '=' in tok:
            k, val = tok.split('=', 1)
            if re.fullmatch(r'[a-z_0-9]+', k):
                try:
                    vec[k] = float(val)
                except ValueError:
                    pass
    mom = {}
    for name, val in re.findall(r'MOMENT\s+(\S+)\s+.*?model=\s*([-\dEe.+]+)', s):
        try:
            mom[name] = float(val)
        except ValueError:
            pass
    return m.group(1), vec, mom, os.path.getmtime(path)


def on_config(vec):
    return all(k in vec and abs(vec[k] - want) <= 1e-9 * max(abs(want), 1.0)
               for k, want in CONFIG.items())


def iterates():
    """Every solved point that is an iterate of this loop, newest last."""
    h = model_hash()
    out = []
    for f in glob.glob(os.path.join(HERE, 'points', 'point_*.txt')):
        if '.FAILED' in f:
            continue
        p = parse(f)
        if not p:
            continue
        md, vec, mom, mt = p
        if md != h or not on_config(vec):
            continue
        if not all(k in mom for k in TARGETS):
            continue
        if not all(k in vec for k in RULES):
            continue
        out.append((mt, os.path.basename(f)[6:16], vec, mom))
    out.sort()
    return out


def slope(pts, param, moment, fallback):
    """Median slope from pairs of iterates differing ONLY in param.

    Falls back to the 6 September measurement when the loop has not yet produced
    a controlled pair of its own. Regressing across points that differ in several
    coordinates is what produced three wrong directions on 6 September, so it is
    not done here at all.
    """
    rows = []
    for i, (_, _, v1, m1) in enumerate(pts):
        for (_, _, v2, m2) in pts[i + 1:]:
            if v1[param] <= 0 or v2[param] <= 0 or v1[param] == v2[param]:
                continue
            if m1.get(moment, 0) <= 0 or m2.get(moment, 0) <= 0:
                continue
            if any(abs(v1[k] - v2.get(k, v1[k])) > 1e-9 * max(abs(v1[k]), 1.0)
                   for k in v1 if k != param):
                continue
            rows.append(math.log(m2[moment] / m1[moment]) /
                        math.log(v2[param] / v1[param]))
    if not rows:
        return fallback, 'fallback'
    rows.sort()
    return rows[len(rows) // 2], f'{len(rows)} pair(s)'


def main():
    pts = iterates()
    if not pts:
        print('# no solved point carries the configuration yet; seed first',
              file=sys.stderr)
        return 2
    _, tag, vec, mom = pts[-1]
    print(f'# from point_{tag}', file=sys.stderr)
    nxt = dict(vec)

    # THE RUNG SERVES h_1 WHILE h_1 IS FAR OFF. The author, 6 September: *"If h1
    # gets closer then we just lower h2 a bit more and sacrifice a bit on the h2
    # target"*. h2 there is the RUNG, the parameter; the h2 they are willing to
    # give up is the cost-burden MOMENT. The two share a name and confusing them
    # has already cost a concession once, so it is spelled out here.
    #
    # The rung moves h_1 with a measured slope of +2.06, seven times the street's
    # +0.30, so it is the stronger of the two instruments on the homelessness
    # rate -- it simply was not pointed at it. While h_1 is more than half again
    # its target the rung chases h_1; inside that it reverts to the cost burden.
    #
    # RIGHT NOW THIS COSTS NOTHING, and that is worth recording so the "sacrifice"
    # is not booked before it happens: the burden moment is 0.1534 against 0.101,
    # ABOVE target, and lowering the rung lowers both. The sacrifice begins only
    # when the rung has pushed the burden below 0.101, and the trace will show
    # exactly when that is.
    rung = 'smallest_rental_relative_to_lowest_income'
    h1_gap = abs(mom['h_1'] - TARGETS['h_1']) / TARGETS['h_1']
    serve_h1 = h1_gap > 0.50

    for param, (moment, fb, lo, hi) in RULES.items():
        if param == rung and serve_h1:
            moment, fb = 'h_1', +2.06
        cur, tgt = mom[moment], TARGETS[moment]
        e, src = slope(pts, param, moment, fb)
        if cur <= 0 or abs(e) < 1e-6:
            print(f'#   {param}: {moment} is {cur:g}, cannot step on it',
                  file=sys.stderr)
            continue
        step = DAMP * math.log(tgt / cur) / e
        step = max(-MAX_EFOLD, min(MAX_EFOLD, step))
        new = max(lo, min(hi, vec[param] * math.exp(step)))
        at = '  AT BOUND' if new in (lo, hi) else ''
        print(f'#   {param:<44}{vec[param]:10.5g} -> {new:10.5g}   '
              f'{moment} {cur:.5f} vs {tgt:.5f}, slope {e:+.2f} ({src}){at}',
              file=sys.stderr)
        nxt[param] = new
    print('bash code/run_one_point.sh ' +
          ' '.join(f'{k}={v:g}' for k, v in sorted(nxt.items())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
