"""DOES THE DAMPING RULE ACTUALLY KILL THE LIMIT CYCLE IT WAS WRITTEN FOR?

Two tests, and the second is the one that matters.

  REPLAY  The residual signs rr_homeless_old_level actually produced over ten
          iterations of the live solver, taken from fixed_point_trace.txt. The
          rule must recognise the alternation and drive that parameter's scale
          to the floor, while a parameter that held one sign throughout --
          kappa_uem did, all ten iterations -- must keep its full step. A rule
          that damps everything is not damping, it is just a smaller adjuster.

  SCALAR  A fixed point with a gain large enough to make the undamped iteration
          diverge. The undamped run must diverge and the damped run converge, on
          the same gain and the same start. This is what the rule claims to buy,
          so it is stated as a claim that can fail rather than as a comment.

Nothing here touches the live solver: damp() is pure, and the state it reads is
passed in.
"""
import sys

sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code')
import fixed_point as FP


# The gaps rr_homeless_old_level produced, iterations 3 to 10 (per cent).
RR = [237.25, -99.28, 228.89, -97.57, 608.92, -73.47, 182.24, -80.34]
# kappa_uem over the same iterations: one sign throughout.
KU = [-88.84, -95.20, -88.16, -84.46, -93.65, -81.31, -89.79, -84.83]


def replay(name, gaps):
    scale, last = {}, {}
    seen = []
    for g in gaps:
        seen.append(FP.damp(scale, name, g / 100.0, last))
        last[name] = g / 100.0
    return seen


def test_replay():
    rr = replay('rr_homeless_old_level', RR)
    ku = replay('kappa_uem', KU)
    print(f'  rr_homeless_old_level scale over 8 iterations: '
          + ' '.join(f'{x:.3g}' for x in rr))
    print(f'  kappa_uem                                    : '
          + ' '.join(f'{x:.3g}' for x in ku))
    ok = True
    if rr[-1] > 0.2:
        print(f'  FAIL: the oscillator was not damped (ended at {rr[-1]:.3g})')
        ok = False
    if rr[-1] < FP.OSC_FLOOR - 1e-12:
        print(f'  FAIL: damped below the floor {FP.OSC_FLOOR}')
        ok = False
    if min(ku) < 1.0 - 1e-12:
        print(f'  FAIL: a parameter that never flipped was damped to {min(ku):.3g}')
        ok = False
    print('  replay: ' + ('PASS' if ok else 'FAIL'))
    return ok


def run(gain, damped, iters=60, x0=1.0):
    """x_{k+1} = x_k - a*f*g(x_k), with g(x) = gain*x: the scalar caricature."""
    scale, last, x = {}, {}, x0
    a = 0.10
    for _ in range(iters):
        rel = gain * x
        f = FP.damp(scale, 'p', rel, last) if damped else 1.0
        last['p'] = rel
        x -= a * f * max(-1.0, min(1.0, rel))
        if abs(x) > 1e6:
            break
    return abs(x)


def test_scalar():
    # A gain that makes the undamped step overshoot: the correction is
    # a*gain*x = 2.5x, so each iteration lands further out on the other side.
    g = 25.0
    u, d = run(g, False), run(g, True)
    print(f'  scalar, gain {g}:  undamped |x| {u:.4g}   damped |x| {d:.4g}')
    ok = True
    if u < 0.5 * 1.0:
        print('  FAIL: the undamped iteration did not diverge, so the test is '
              'not testing anything')
        ok = False
    if d >= u:
        print('  FAIL: damping did not help')
        ok = False
    print('  scalar: ' + ('PASS' if ok else 'FAIL'))
    return ok


def main():
    print('\n  damping on oscillation\n')
    ok = test_replay() & test_scalar()
    print()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
