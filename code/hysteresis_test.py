"""DOES THE HOLD BAND THRASH WHEN A MOMENT SITS ON THE LINE?

The hold rule shrinks the simplex to the instruments whose own moment is outside
ten per cent, and stage_night rebuilds the simplex whenever that set shrinks, at
about three model solves a rebuild. With ONE threshold for both directions a
moment oscillating across the line -- 9.9, 10.1, 9.9 -- is held, released and held
again, and every re-entry buys another rebuild. Over a night that is the whole
night spent re-seeding.

This drives outside_band with a fake archive whose one moment walks across the
line, and counts how many times the live set SHRINKS. With hysteresis the answer
must be one: held once, and never released by a wobble smaller than the gap
between the thresholds.

The single-threshold case is run too, so the test states the fault it is
protecting against rather than only the fix.
"""
import json, os, sys, tempfile

HERE = '/home/user/housing_first_or_treatment_first/code'
sys.path.insert(0, HERE)
import nelder as NM

INST = [('pA', 'mA'), ('pB', 'mB')]
KEYS = ['mA', 'mB']
# mA walks across the ten per cent line; mB stays far outside so the simplex is
# never empty and the "or inst" fallback cannot mask the result.
WALK = [0.30, 0.09, 0.11, 0.09, 0.12, 0.08, 0.14, 0.09]


class FakeN:
    def __init__(self):
        self.gap = WALK[0]

    def archive(self):
        return {'t': ({}, {})}

    def best(self, A, keys):
        return 0.0, 't', {}, {'mA': (1.0 + self.gap, 1.0), 'mB': (2.0, 1.0)}


def run(release):
    N = FakeN()
    old_release, NM.NM_RELEASE = NM.NM_RELEASE, release
    d = tempfile.mkdtemp()
    old_state, NM.STATE = NM.STATE, os.path.join(d, 's.json')
    shrinks, live = 0, None
    try:
        for g in WALK:
            N.gap = g
            now = {p for p, _ in NM.outside_band(N, None, INST, KEYS)}
            if live is not None and now < live:
                shrinks += 1
            live = now
            # stage_night rebuilds the simplex on the live set; that rebuild is
            # what writes names back into the state file, so mirror it here.
            json.dump({'names': sorted(live)}, open(NM.STATE, 'w'))
    finally:
        NM.NM_RELEASE, NM.STATE = old_release, old_state
    return shrinks


def main():
    print('\n  hold-band hysteresis: a moment walking across the line\n')
    print('  gaps: ' + ', '.join(f'{g:.0%}' for g in WALK))
    flat = run(NM.NM_BAND)          # release == hold: the old behaviour
    hyst = run(0.15)
    print(f'  single threshold  (hold {NM.NM_BAND:.0%}, release {NM.NM_BAND:.0%}): '
          f'{flat} rebuilds')
    print(f'  hysteresis        (hold {NM.NM_BAND:.0%}, release 15%): '
          f'{hyst} rebuilds')
    ok = True
    if flat < 2:
        print('  FAIL: the single-threshold case did not thrash, so this test is '
              'not testing anything')
        ok = False
    if hyst != 1:
        print(f'  FAIL: hysteresis should hold once and stay held, got {hyst}')
        ok = False
    print('  ' + ('PASS' if ok else 'FAIL'))
    print()
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
