"""coupling.py -- DID A RUN MOVE ANYTHING BESIDES THE PARAMETER IT RAISED? (11 November; the author: "You should check if
any other parameter also scaled others when you tested it", after h_2 turned out to carry h_3 and h_4 with it.)

For every run in results/jacobian, every value the log prints before the solve starts (the HANDOVER echoes, and every
'name= value' line of the setup, up to the first expected_child_value= line), and the last 'housing_size=' line (the
shelter and the three rental sizes the solve used), is compared with the base run. A value that differs by more than one
part in a billion is listed, so a run should list its own parameter and nothing else that is an input.

usage: python3 code/jacobian/coupling.py [RUN...]
"""
import gzip, os, re, sys
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'results', 'jacobian')
NUM = r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[EeDd][-+]?\d+)?|NaN'
NUMRE = re.compile(NUM)


def setup(path):
    out = {}
    with gzip.open(path, 'rt', errors='replace') as f:
        for line in f:
            if 'expected_child_value=' in line:
                break
            m = re.match(r'\s*HANDOVER\s+(.+?):\s*(\S+)\s*->\s*(\S+)', line)
            if m:
                out['HANDOVER ' + m.group(1)] = m.group(3)
                continue
            if line.count('=') == 1:
                k, v = line.split('=')
                k, vals = k.strip(), v.split()
                if k and len(k) < 90 and vals and all(NUMRE.fullmatch(x) for x in vals):
                    out[k] = vals
    hs = []
    with gzip.open(path, 'rt', errors='replace') as f:
        for line in f:
            if line.lstrip().startswith('housing_size='):
                hs.append(line.split('=', 1)[1])
    if hs:
        out['FINAL housing_size (h1 h2 h3 h4)'] = hs[-1].split()
    return out


def differs(a, b):
    a = a if isinstance(a, list) else [a]
    b = b if isinstance(b, list) else [b]
    if len(a) != len(b):
        return True
    for x, y in zip(a, b):
        try:
            x, y = float(x.replace('D', 'E')), float(y.replace('D', 'E'))
        except ValueError:
            if x != y:
                return True
            continue
        if x != x or y != y:
            if (x != x) != (y != y):
                return True
            continue
        if abs(x - y) > 1e-9 * max(abs(x), abs(y), 1e-12):
            return True
    return False


base = setup(os.path.join(RES, 'base', 'cf.log.gz'))
runs = sys.argv[1:] or sorted(d for d in os.listdir(RES) if d != 'base' and os.path.exists(os.path.join(RES, d, 'cf.log.gz')))
for d in runs:
    s = setup(os.path.join(RES, d, 'cf.log.gz'))
    diff = [k for k in sorted(set(base) | set(s)) if k not in base or k not in s or differs(base[k], s[k])]
    print(f'== {d}: {len(diff)} differ')
    for k in diff:
        fmt = lambda v: ' '.join(v) if isinstance(v, list) else str(v)
        print(f'   {k}: {fmt(base.get(k, "-"))[:70]}  ->  {fmt(s.get(k, "-"))[:70]}')
