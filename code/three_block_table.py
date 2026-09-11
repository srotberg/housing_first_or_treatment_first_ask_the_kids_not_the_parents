"""The three-block table: aleph, participation, the SUD onset, and h_1.

WHY THIS EXISTS SEPARATELY FROM gaps.py AND calibration_report.py. While only
three brackets are live the author wants those three and h_1, with the PARAMETER
beside the moment it moves, and the value each loop actually SOLVED at rather
than the post-update value the log prints. Getting that ordering wrong once made
a loop look like it sat at a value it never saw.

    python3 code/three_block_table.py [log]

with no argument it takes the newest worker log.
"""
import glob
import os
import re
import sys

TARGETS = {'aleph': 80.0, 'b': 0.089, 'lambda_d': 0.0368, 'h_1': 0.0116}


def moments(lines, name):
    """model values of one MOMENT, in loop order."""
    out = []
    pat = re.compile(r'^\s*MOMENT\s+' + re.escape(name) + r'\s')
    for l in lines:
        if pat.match(l):
            try:
                out.append(float(l.split()[-3].replace('D', 'E')))
            except (ValueError, IndexError):
                pass
    return out


def parameter(lines, name):
    """Distinct successive values of a parameter print, anchored on the whole line.

    Anchored because "distance_<name>=" contains "<name>=", and an unanchored
    match reads the distance as the value -- an error already made once here.
    """
    out = []
    pat = re.compile(r'\s*' + re.escape(name) + r'=\s*([0-9.eEdD+-]+)\s*$')
    for l in lines:
        m = pat.match(l)
        if m:
            v = float(m.group(1).replace('D', 'E').replace('d', 'e'))
            if not out or out[-1] != v:
                out.append(v)
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else max(
        glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker_*.log')),
        key=os.path.getmtime)
    lines = open(path, errors='replace').read().split('\n')

    al, b, ld, h1 = (moments(lines, n) for n in ('aleph', 'b', 'lambda_d', 'h_1'))
    if not b:
        sys.exit(f'{os.path.basename(path)}: no moment block yet')

    # THE PARAMETER PRINTS ARE POST-UPDATE, so loop k solved at print k-1 and
    # loop 1 solved at the handover.
    vol = parameter(lines, 'value_of_life')
    bb = parameter(lines, 'addiction_scalar_1')
    on = parameter(lines, 'onset_at_the_mean_quantity')
    hand = {}
    for l in lines:
        m = re.match(r'\s*HANDOVER (\w+):.*->\s*([0-9.eEdD+-]+)\s*$', l)
        if m:
            hand[m.group(1)] = float(m.group(2).replace('D', 'E').replace('d', 'e'))
    # PREPEND THE HANDOVER ONLY IF IT IS NOT ALREADY THE FIRST DISTINCT VALUE.
    # value_of_life prints ONCE a loop, after its update, so loop 1's value is
    # the handover and has to be put back. addiction_scalar_1 prints TWICE, once
    # before and once after, so the de-duplicated list already starts at the
    # handover and prepending it would shift every row by one -- which showed
    # loop 2 sitting at a value it never solved at.
    def prepend(seq, first):
        if first != first:                      # NaN: nothing to prepend
            return seq
        if seq and abs(seq[0] - first) <= 1e-12 * max(abs(first), 1.0):
            return seq
        return [first] + seq

    vol = prepend(vol, hand.get('value_of_life', float('nan')))
    bb = prepend(bb, hand.get('addiction_scalar_1', float('nan')))
    on = [float('nan')] + on

    def at(seq, i):
        return seq[i] if i < len(seq) else float('nan')

    def gap(x, t):
        return (x - t) / t * 100

    print(f'\n{os.path.basename(path)}: {len(b)} loop(s)\n')
    print(f'{"loop":>4} | {"value_of_life":>13} {"aleph":>7} {"gap":>8} | '
          f'{"addiction_scalar_1":>18} {"particip.":>9} {"gap":>8} | '
          f'{"onset":>8} {"lambda_d":>8} {"gap":>8} | {"h_1":>8} {"gap":>8}')
    print('-' * 128)
    for i in range(len(b)):
        print(f'{i+1:>4} | {at(vol,i):>13.3f} {at(al,i):>7.2f} {gap(at(al,i),80):>+7.1f}% | '
              f'{at(bb,i):>18.6g} {b[i]:>9.5f} {gap(b[i],0.089):>+7.1f}% | '
              f'{at(on,i):>8.5g} {at(ld,i):>8.5f} {gap(at(ld,i),0.0368):>+7.1f}% | '
              f'{at(h1,i):>8.5f} {gap(at(h1,i),0.0116):>+7.1f}%')
    print('-' * 128)
    print('targets:  aleph 80     participation 0.089     lambda_d 0.0368     h_1 0.0116')

    conv = [l for l in lines if 'CHILD V CONVERGED' in l or 'CHILD V DID NOT' in l]
    if conv:
        last = conv[-1].split()
        print(f'child V(1): {len(conv)} loop(s) reconciled, last {" ".join(last[2:])}')
    held = parameter(lines, 'size_homelessness')
    if held:
        print(f'size_homelessness HELD at {held[0]:.6g}: h_1 moves only as a side effect')


if __name__ == '__main__':
    main()
