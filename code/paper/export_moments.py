"""
Expose every model moment the calibration prints to the prose as @@m_<name>@@.

WHY THIS EXISTS. export_consts.py covers the Fortran DECLARATIONS, which are the
parameters and the data targets. It cannot cover the other half of what Section 4
onward quotes, which is what the model PRODUCES: the homelessness rate it
generates, the SUD rate, the shares by age band, the untargeted moments the paper
says the model can be caught on. Those exist only as numbers the run prints.

So this reads the run's log and writes every scalar it printed under the name
m_<label>, taking the LAST occurrence of each label so that a converged run's
value wins over the loops it passed through on the way. Both a raw and a percent
form are written, m_x and m_x_pc, for the same reason export_consts.py writes
both.

The parse is deliberately dumb: the Fortran prints "label= value" and that is the
whole contract. A label that stops being printed disappears from the JSON, and a
sentence that reads it fails loudly at fill time rather than keeping a stale
number, which is the behaviour the pipeline wants.

Run:  python3 export_moments.py <run.log>
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'model_numbers.json')

# " label=   0.1234" or " label(1)=  0.1234", one value only. A line carrying a
# second number after the first is a vector and is skipped: naming its elements
# is a decision, not a parse.
LINE = re.compile(
    r'^\s*(?P<label>[A-Za-z][^=]{0,120}?)\s*=\s*'
    r'(?P<value>[-+]?\d+\.?\d*(?:[eEdD][-+]?\d+)?)\s*$'
)


def sanitise(label):
    """A Fortran print label as a placeholder name."""
    s = label.strip()
    s = s.replace('/', '_over_')
    s = re.sub(r'\((?:time_period|1|j)\)', '', s)
    s = re.sub(r'[^0-9A-Za-z_]+', '_', s)
    return s.strip('_')


def fmt(x):
    if x == int(x):
        return str(int(x))
    return f'{x:.6f}'.rstrip('0').rstrip('.')


def parse(path):
    """label -> value, last occurrence wins."""
    found = {}
    with open(path, errors='replace') as fh:
        for line in fh:
            m = LINE.match(line.rstrip('\n'))
            if not m:
                continue
            name = sanitise(m.group('label'))
            if not name or name[0].isdigit():
                continue
            raw = m.group('value').replace('D', 'E').replace('d', 'e')
            try:
                found[name] = float(raw)
            except ValueError:
                continue
    return found


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)
    found = parse(sys.argv[1])
    out = {}
    for name, value in found.items():
        if value != value or abs(value) == float('inf'):
            continue          # a NaN moment is not a number the prose may quote
        out[f'm_{name}'] = fmt(value)
        out[f'm_{name}_pc'] = fmt(value * 100)
    with open(OUT, 'w') as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
    print(f'{len(found)} moments -> {OUT}')


if __name__ == '__main__':
    main()
