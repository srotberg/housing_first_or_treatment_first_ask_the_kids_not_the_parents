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


def run(gain, damped, iters=200, x0=0.523):
    """x_{k+1} = x_k - a*f*clip(gain*x_k): the scalar caricature of one parameter.

    The clip is the solver's own -- |rel| is capped at one, so the step can never
    exceed the adjuster and x cannot run away to infinity. THAT IS WHY THE
    INSTABILITY HERE IS A LIMIT CYCLE RATHER THAN A DIVERGENCE, and it is exactly
    what rr_homeless_old_level does on the live model: 2.68, 2.99, 2.68, 2.99,
    forever, never settling, three minutes of model solve per bounce.

    So the thing to measure is the amplitude the iteration is left cycling at,
    not whether it blew up.
    """
    # x0 IS DELIBERATELY NOT A MULTIPLE OF THE STEP. At x0 = 1.0 and a = 0.10 the
    # undamped iterate lands exactly on zero in floating point and sits there for
    # sixty iterations before rounding error walks it back out -- a fixed point of
    # the arithmetic, not of the map, and it made this test report "settled" for a
    # map that does not settle.
    scale, last, x = {}, {}, x0
    a, seen = 0.10, []
    for _ in range(iters):
        rel = gain * x
        f = FP.damp(scale, 'p', rel, last) if damped else 1.0
        last['p'] = rel
        x -= a * f * max(-1.0, min(1.0, rel))
        seen.append(x)
    tail = seen[-20:]
    return max(tail) - min(tail)


def test_scalar():
    # A gain steep enough that the clipped step always overshoots zero: with
    # gain 25 the residual saturates for any |x| > 0.04, so every step is the
    # full adjuster and every step crosses.
    g = 25.0
    u, d = run(g, False), run(g, True)
    print(f'  scalar, gain {g}:  undamped cycle {u:.4g}   damped cycle {d:.4g}')
    ok = True
    # The undamped cycle is the adjuster itself peak to peak: the iterate lands a
    # half-step either side of zero and steps the full adjuster across it forever.
    if u < 0.9 * 0.10:
        print(f'  FAIL: the undamped iteration settled ({u:.4g}), so there is no '
              'limit cycle to damp and the test is not testing anything')
        ok = False
    if d > u / 4.0:
        print(f'  FAIL: damping shrank the cycle by only {u / d:.3g}x')
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
