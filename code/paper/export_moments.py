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

# " label=   0.1234" or " label(1)=  0.1234".
#
# TWO PAIRS ON A LINE IS NOT A VECTOR, and the difference matters. The Fortran
# prints some moments two to a line --
#
#     SMI share of homeless=  0.0256  employment rate given SMI=  0.8692
#
# -- and a pattern anchored to the end of the line sees neither of them. Nine
# targeted moments were invisible to the calibration report that way, which is
# most of the ones this paper is about: the SMI share of the homeless, the
# employment rate given SMI, the employed share of the homeless.
#
# A VECTOR still has to be skipped, because naming its elements is a decision
# rather than a parse. The two are told apart by counting NAMES, not numbers:
# one name followed by several numbers is a vector; several names each followed
# by one number is several moments.
PAIR = re.compile(
    r'(?P<label>[A-Za-z][^=]{0,120}?)\s*=\s*'
    r'(?P<value>[-+]?\d+\.?\d*(?:[eEdD][-+]?\d+)?)'
    r'(?P<trailing>(?:\s+[-+]?\d+\.?\d*(?:[eEdD][-+]?\d+)?)*)'
)


# NAMED VECTOR PRINTS. The parser skips a vector because naming its elements is a
# decision; these are the decisions, made explicitly. Each entry maps the label
# the Fortran prints to the names its elements carry, in order. Without this the
# rental ladder's three moments -- which are h_2's, varsigma's and h_4's -- are
# invisible to the calibration report.
VECTORS = {
    'model_housing_size_dist': ('model_housing_size_dist_1',
                                'model_housing_size_dist_2',
                                'model_housing_size_dist_3'),
    'housing_size_dist_data': ('housing_size_dist_data_1',
                               'housing_size_dist_data_2',
                               'housing_size_dist_data_3'),
}
VEC = re.compile(r'^\s*(?P<label>[A-Za-z][A-Za-z0-9_ ()]{0,60})=\s*(?P<values>.*)$')


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
            bare = line.rstrip('\n')
            v = VEC.match(bare)
            if v and sanitise(v.group('label')) in VECTORS:
                names = VECTORS[sanitise(v.group('label'))]
                vals = re.findall(r"[-+]?\d+\.?\d*(?:[eEdD][-+]?\d+)?", v.group("values").replace("D","E").replace("d","e"))
                for nm, raw in zip(names, vals):
                    try:
                        found[nm] = float(raw)
                    except ValueError:
                        pass
                continue
            for m in PAIR.finditer(bare):
                # a number following the value, with no name of its own, makes
                # this a vector print rather than a moment
                if m.group('trailing').strip():
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
