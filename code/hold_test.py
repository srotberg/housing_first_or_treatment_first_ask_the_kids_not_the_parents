"""IS THE HOLD BAND STICKY, OR A REVOLVING DOOR?

The author, 4 September: *"maybe the right way is to push them into the rule when
they pass 10%, and then only start updating them again when they leave 15%"*, and
*"so it's not so much in and out"*.

With ONE threshold a moment sitting near the line is held, released and held again
every iteration, and a parameter that is essentially converged keeps moving and
keeps injecting cross-effects into the ones that are not. It showed in the live
run: fp4 held 12 of 21 at iteration 1, then 9, 9, 8.

This walks one gap across the line and counts STATE CHANGES. Sticky means two --
in once, and out once when it genuinely leaves. The single-threshold case is run
alongside so the test states the fault it protects against, not only the fix.
"""
import sys

sys.path.insert(0, '/home/user/housing_first_or_treatment_first/code')
import fixed_point as FP

# per cent: settles near the line, wobbles across it, then genuinely leaves
WALK = [0.40, 0.09, 0.11, 0.09, 0.12, 0.08, 0.14, 0.09, 0.13, 0.22, 0.30]


def run(release):
    old, FP.RELEASE_BAND = FP.RELEASE_BAND, release
    try:
        held, flips, seen = False, 0, []
        for g in WALK:
            now = FP.hold(g, held)
            if now != held:
                flips += 1
            held = now
            seen.append('H' if held else '.')
        return flips, ''.join(seen)
    finally:
        FP.RELEASE_BAND = old


def main():
    print('\n  hold band: does a parameter go in and out?\n')
    print('  gaps:  ' + ' '.join(f'{g:.0%}'.rjust(4) for g in WALK))
    f1, s1 = run(FP.FREEZE_BAND)      # release == freeze: one threshold
    f2, s2 = run(0.15)
    print(f'  one threshold  (in {FP.FREEZE_BAND:.0%}, out {FP.FREEZE_BAND:.0%}):'
          f'  {" ".join(c.rjust(4) for c in s1)}   {f1} state changes')
    print(f'  hysteresis     (in {FP.FREEZE_BAND:.0%}, out 15%):'
          f'  {" ".join(c.rjust(4) for c in s2)}   {f2} state changes')
    ok = True
    if f1 < 4:
        print('  FAIL: one threshold did not thrash, so this test is not testing '
              'anything')
        ok = False
    if f2 != 2:
        print(f'  FAIL: sticky should be in once and out once, got {f2}')
        ok = False
    if s2[-1] != '.':
        print('  FAIL: a gap of 30 per cent must not stay held')
        ok = False
    print('  ' + ('PASS' if ok else 'FAIL'))
    print()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
