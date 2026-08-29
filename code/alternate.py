#!/usr/bin/env python3
"""Move the four parameters that drive everything; then nudge the rest to match.

WHY ALTERNATE INSTEAD OF SOLVING THE WHOLE VECTOR. The coupling in this model is
asymmetric. The drug block drives the rest hard -- every point measured on the
night of 29 August shows lambda_d dragging pi_eu with a correlation of 1.00, and
reaching for lambda_d emptied homelessness to -71 per cent and pushed treatment
take-up to +268 -- while the other sixteen parameters barely push back on it. A
solve over all twenty at once therefore keeps making the same bad bargain: it
trades away h_1 and tau_u, which are cheap in the loss at weight one and two, to
buy lambda_d and b at weight three, and the trade nets out WORSE. The line
search did exactly this and every one of its eight lengths scored below the
point it started from.

So the loss does not get a vote in phase A.

  PHASE A -- THE DRUG BLOCK ALONE. Four parameters, four moments, a square
  system: addiction_scalar_1, lambda_addiction, relative_share_of_addiction_1
  and utility_cost_of_treatment against b, lambda_d, theta and tau_u. The other
  sixteen moments are NOT in the fit, so nothing can argue the step down for
  costing homelessness. It will cost homelessness. Phase B is where that is
  paid back.

  PHASE B -- A SMALL REPAIR OF THE REST. The drug coordinates freeze at what
  phase A found, and the other sixteen move against ALL the moments, with a
  deliberately short trust region. These sixteen are the well-behaved half:
  smooth, near-linear, each with an instrument that mostly works, which is
  exactly the case a Jacobian handles in one step. They need a nudge, not a
  search.

WHY THIS SHOULD BE FASTER THAN EITHER HALF ALONE. The drug block is where the
model cliffs -- the b response is flat and then falls off, which is why
Nelder-Mead was put on it in the first place -- so it needs short steps and
several of them measured at once. The other sixteen are where a derivative can
be trusted. Alternating lets each half be attacked with the method that suits
it, instead of forcing one method to cover both and doing neither well.

THE HONEST LIMIT, STATED UP FRONT. If phase A can put lambda_d, b and theta on
target and phase B can then restore the rest, the loss falls a long way. If
every phase-A setting that fixes lambda_d leaves damage phase B cannot repair,
that is the b/lambda_d frontier asserting itself, and no amount of alternating
will move it -- the next step would be a modelling decision and belongs to the
author.
"""
import argparse
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import jacobian                                          # noqa: E402
import line_search as ls                                 # noqa: E402
import score_points                                      # noqa: E402

# THE BLOCK IS WHAT THE JACOBIAN SAYS IT IS, NOT WHAT ITS NAME SAYS.
# The first cut of this file guessed the block from the parameter names --
# addiction_scalar_1, lambda_addiction, relative_share_of_addiction_1 -- and the
# fitted elasticities say that guess was wrong in both directions.
#
# lambda_addiction is NOT among the strongest movers of any drug moment. The
# three that dominate b, lambda_d and tau_u are value_of_life, discount_factor
# and addiction_scalar_1, all three at the elasticity clamp, which is
# economically the sensible answer: whether a household uses turns on what it
# holds its life to be worth and how hard it discounts the damage, not on the
# hazard rate the state transition is written with.
#
# And h_1 belongs INSIDE, which is the author's correction of 29 August. Every
# drug-block move measured that night swung homelessness violently -- -71 per
# cent, +43, +105, -57 -- because value_of_life, relative_share_of_housing and
# smallest_rental_relative_to_lowest_income move BOTH the drug moments and
# homelessness. Leaving h_1 to the repair phase meant phase A broke it every
# iteration and phase B had to buy it back, which is the same bad bargain the
# alternation exists to avoid, merely split across two batches.
#
# So the block is CLOSED under the relation "moves, or is moved by": start from
# the moments that are wrong, take the parameters that move them hardest, then
# take the moments those parameters own, and stop when nothing new is added.
# What falls outside is genuinely uncoupled -- sigma_y, cbar, p_m, omega_l,
# kappa_ued, kappa_uem, mu_H, h_4, pi_eu, pi_V -- and those are exactly the
# moments already sitting within a few per cent at the leader.
#
# A CAVEAT ON READING THE FIT. Several entries sit at the +/-5.0 clamp, so the
# ORDER among them is not measured, only that all of them are strong. That is
# an argument for putting the whole group in one block rather than for ranking
# them against each other.
# pi_eu JOINS THE BLOCK TOO, on the author's second correction of 29 August, and
# note first that it is misnamed in every discussion before this one: pi_eu is
# the UNEMPLOYMENT RATE -- 8.45 per cent against a target of 4.85 -- not the
# employment-to-unemployment transition probability. Its own instrument,
# probability_becoming_unemployed, has an elasticity of only +0.70 on it. What
# actually moves it is discount_factor at -2.14, with value_of_life and
# addiction_scalar_1 behind that: impatience drives unemployment harder than the
# separation rate does. Three of its six strongest movers were already block
# members, so scoring it outside the block meant the block kept moving it with
# nothing accountable for the result.
DRUG_PARAMS = ['addiction_scalar_1', 'lambda_addiction',
               'relative_share_of_addiction_1', 'value_of_life',
               'discount_factor', 'size_homelessness',
               'smallest_rental_relative_to_lowest_income',
               'relative_share_of_housing', 'labor_income_tax_rate',
               'probability_becoming_unemployed']
DRUG_MOMENTS = ['b', 'lambda_d', 'theta', 'h_1', 'tau_u',
                'aleph', 'beta', 'gamma', 'h_2', 'tau_l', 'pi_eu']

# Phase A steps are SHORT and there are several, because this is the half where
# the response is flat and then cliffs and a derivative across that range is not
# a derivative. Phase B is one short step because that half is near-linear.
# MEASURED 29 AUGUST, 03:20. The first phase A batch used 0.10 to 0.55 and
# overshot catastrophically -- b at +258, +568 and +745 per cent, lambda_d at
# +1014 -- for losses of 1.77 to 2.23. Nine parameters pulling together on three
# drug moments is a far more potent direction than the four-parameter version
# these lengths were guessed for, and the drug block's response is the flat-then-
# cliff shape that made Nelder-Mead necessary here in the first place. Short
# steps, and one long enough to confirm the turn is real rather than assumed.
A_LADDER = (0.02, 0.05, 0.09, 0.16)
B_LADDER = (0.12, 0.25)

STATE = os.path.join(HERE, 'ALTERNATE_STATE.txt')
BATCH = os.path.join(HERE, 'ALTERNATE.txt')


def solve(centre, pts, params, moments_wanted=None, ridge=1e-3):
    """Gauss-Newton direction over a chosen subset of parameters and moments."""
    all_params = ls.varying(pts, centre)
    got = ls.fit(centre, pts, all_params)
    if got is None:
        return None, None
    moments, J, r, w, _ref, used = got
    cols = [all_params.index(k) for k in params if k in all_params]
    if len(cols) != len(params):
        return None, None
    if moments_wanted:
        rows = [i for i, m in enumerate(moments) if m in moments_wanted]
        if not rows:
            return None, None
    else:
        rows = list(range(len(moments)))
    Js, rs, ws = J[np.ix_(rows, cols)], r[rows], w[rows]
    W = np.diag(ws)
    d = np.linalg.solve(Js.T @ W @ Js + ridge * np.eye(len(cols)), Js.T @ W @ rs)
    n = float(np.max(np.abs(d)))
    return (d / n if n > 0 else d), {'moments': [moments[i] for i in rows],
                                     'used': used, 'resid': float(np.linalg.norm(rs))}


def emit(centre, params, d, ladder, tagfmt):
    out = []
    for t in ladder:
        v = dict(centre)
        for j, k in enumerate(params):
            v[k] = ls.clip(k, centre[k] * math.exp(t * d[j]))
        line = 'bash code/run_one_point.sh ' + ' '.join(f'{k}={v[k]:.7g}' for k in sorted(v))
        out.append((tagfmt % t, line))
    return out


def best_point():
    pts = [(v, m, n) for v, m, n in jacobian.points() if 'relative_share_of_housing' in v]
    scored = sorted(((score_points.loss(m)[0], v, n) for v, m, n in pts), key=lambda t: t[0])
    return scored[0] if scored else (None, None, None)


def phase_of():
    """(next phase, the previous batch's best point) from the state file."""
    if not os.path.exists(STATE):
        return 'A', None
    lines = [l.split() for l in open(STATE) if l.strip()]
    if not lines:
        return 'A', None
    # The next phase is the opposite of the last one EMITTED. The state file
    # also carries "<phase>done batchbest <point>" markers, which record a
    # finished batch's winner and must not be mistaken for an emit line -- that
    # is why the emitted phase is matched exactly rather than by first letter.
    emitted = [p[0] for p in lines if p and p[0] in ('A', 'B')]
    if not emitted:
        return 'A', None
    nxt = 'B' if emitted[-1] == 'A' else 'A'
    prev_best = None
    for parts in reversed(lines):
        if 'batchbest' in parts:
            prev_best = parts[parts.index('batchbest') + 1]
            break
    return nxt, prev_best


# WHICH POINT EACH PHASE STEPS FROM, AND WHY THEY DIFFER.
#
# PHASE B MUST CENTRE ON PHASE A'S RESULT, NOT ON THE BEST MEASURED POINT.
# This was wrong in the first version and the wrongness is total rather than
# partial: phase B freezes the drug parameters AT ITS CENTRE, so centring it on
# the old best freezes them at the values phase A had just moved away from, and
# the whole cycle reduces to a repair of a point that needed no repair. The
# 07:20 state file shows it plainly -- phase A and phase B both recorded
# "centre point_34d3191241" -- and every drug-block gain phase A had bought
# would have been discarded unmeasured.
#
# PHASE A CENTRES ON THE BEST MEASURED POINT. A phase A batch is EXPECTED to
# score worse than where it started, so following it blindly would walk the
# search downhill for as long as it ran. Starting each new cycle from the best
# point that actually exists is what bounds that: phase A may spend a cycle
# going nowhere, but it can never accumulate.
def centre_for(phase, prev_best, pts):
    if phase == 'B' and prev_best:
        for vec, mt, name in pts:
            if name == prev_best:
                return score_points.loss(mt)[0], vec, name
    return best_point()


def landed():
    """(loss, name, line) for each line of the current batch that has a point."""
    import hashlib
    done, missing = [], []
    defaults = {}
    inp = False
    for line in open(os.path.join(HERE, 'run_one_point.sh')):
        if line.strip().startswith('declare -A P=('):
            inp = True
            continue
        if inp and line.strip() == ')':
            break
        if inp:
            import re as _re
            m = _re.match(r'\s*\[([A-Za-z0-9_]+)\]=(\S+)', line)
            if m:
                defaults[m.group(1)] = m.group(2)
    for i, line in enumerate(open(BATCH), 1):
        line = line.strip()
        if not line:
            continue
        vec = dict(defaults)
        for tok in line.split()[2:]:
            k, v = tok.split('=', 1)
            vec[k] = v
        tag = hashlib.md5(''.join(f'{k}={vec[k]}\n' for k in sorted(vec)).encode()).hexdigest()[:10]
        p = os.path.join(HERE, 'points', f'point_{tag}.txt')
        if os.path.exists(p) and 'END OF MOMENTS' in open(p, errors='replace').read():
            _h, mt = score_points.read(p)
            if mt:
                done.append((score_points.loss(mt)[0], f'point_{tag}.txt', i))
                continue
        if os.path.exists(os.path.join(HERE, 'points', f'point_{tag}.FAILED.txt')):
            continue
        missing.append(i)
    return done, missing


def advance():
    """Score this phase's batch; when it is complete, flip phase and emit."""
    if not os.path.exists(BATCH):
        print('no batch yet; run alternate.py to start phase A')
        return 1
    done, missing = landed()
    if missing:
        print(f'batch: {len(done)} of {len(done) + len(missing)} landed, still out {missing}')
        return 0
    if not done:
        print('batch: every point failed; not advancing')
        return 1
    done.sort()
    phase, _ = phase_of()
    prev_phase = 'B' if phase == 'A' else 'A'
    batch_best = done[0][1]
    print(f'phase {prev_phase} batch complete:')
    for L, name, i in sorted(done, key=lambda t: t[2]):
        print(f'   line {i}  loss {L:.4f}  {name}')
    print(f'best of batch {done[0][0]:.4f}')
    # A PHASE A BATCH IS NOT JUDGED ON THE LOSS. It is meant to move the drug
    # moments and it is expected to cost the others; phase B is what pays that
    # back. Only the pair of phases together is allowed to be called a failure,
    # which is why nothing here declares convergence on a single batch.
    with open(STATE, 'a') as fh:
        fh.write(f'{prev_phase}done batchbest {batch_best}\n')
    rc = main_emit()
    return rc


def main_emit():
    sys.argv = [sys.argv[0]]
    return main()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--emit', action='store_true')
    ap.add_argument('--advance', action='store_true')
    args = ap.parse_args()
    if args.advance:
        return advance()

    pts = [(v, m, n) for v, m, n in jacobian.points() if 'relative_share_of_housing' in v]
    phase, prev_best = phase_of()
    L0, centre, cname = centre_for(phase, prev_best, pts)
    if centre is None:
        print('no points', file=sys.stderr)
        return 2

    if phase == 'A':
        params, moments, ladder, tag = DRUG_PARAMS, DRUG_MOMENTS, A_LADDER, 'A%.2f'
    else:
        allp = ls.varying(pts, centre)
        params = [k for k in allp if k not in DRUG_PARAMS]
        moments, ladder, tag = None, B_LADDER, 'B%.2f'

    d, info = solve(centre, pts, params, moments)
    if d is None:
        print('could not solve this phase', file=sys.stderr)
        return 2

    print(f'phase {phase} from {cname} (loss {L0:.4f})', file=sys.stderr)
    print(f'  {len(params)} parameters against {len(info["moments"])} moments,'
          f' fit over {info["used"]} points, residual {info["resid"]:.3f}', file=sys.stderr)
    for j in sorted(range(len(params)), key=lambda j: -abs(d[j]))[:5]:
        print(f'    {params[j]:<48} {d[j]:+.3f}', file=sys.stderr)

    rows = emit(centre, params, d, ladder, tag)
    with open(BATCH, 'w') as fh:
        for _t, line in rows:
            fh.write(line + '\n')
    with open(STATE, 'a') as fh:
        fh.write(f'{phase} centre {cname} loss {L0:.5f} steps '
                 f'{",".join(t for t, _ in rows)}\n')
    if args.emit:
        for _t, line in rows:
            print(line)
    print(f'wrote {len(rows)} points to ALTERNATE.txt for phase {phase}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
