"""The moments calibration_report.py cannot map, printed with their gaps.

WHY THIS EXISTS. calibration_report.py builds its table from
`distance_X = abs(<model> - <name>_data)` in the Fortran, so a moment whose
distance is not written in that shape has no row -- and five of them are not,
including the two largest gaps in the run. They were being read off the log by
hand every firing, which is how a moment goes unreported for a night.

    b             MOMENT line          the participation rate, the long pole
    y_u           MOMENT line          income of drug users, no live instrument
    kappa_ued     MOMENT line          unemployment given a SUD
    sud_homeless  UNTARGETED line      SUD share of the homeless
    emp_homeless  UNTARGETED line      employed share of the homeless

READ THE LAST OCCURRENCE, NOT THE FIRST. A run prints one block per loop and
the live state is the newest one. And match on the WHOLE line: `MOMENT b ` with
the trailing space, because `MOMENT beta` starts with it.
"""

import re
import sys

# (label, what it is, regex over one log line -> model, target)
ROWS = [
    ('b',            'total drug users',
     re.compile(r'^\s*MOMENT b\s+total drug users\s+model=\s*(\S+)\s+target=\s*(\S+)')),
    ('y_u',          'income of drug users',
     re.compile(r'^\s*MOMENT y_u\s+income of drug users\s+model=\s*(\S+)\s+target=\s*(\S+)')),
    ('kappa_ued',    'unemployment given SUD',
     re.compile(r'^\s*MOMENT kappa_ued\s+unemployment given SUD\s+model=\s*(\S+)\s+target=\s*(\S+)')),
    ('sud_homeless', 'SUD share of the homeless',
     re.compile(r'^\s*UNTARGETED SUD share of the homeless\s+model=\s*(\S+)\s+observed=\s*(\S+)')),
    ('emp_homeless', 'employed share of the homeless',
     re.compile(r'^\s*UNTARGETED employed share of the homeless\s+model=\s*(\S+)\s+observed=\s*(\S+)')),
]


def num(s):
    return float(s.replace('D', 'E').replace('d', 'e'))


def read(path):
    got = {}
    with open(path, errors='replace') as fh:
        for line in fh:
            for label, _, pat in ROWS:
                m = pat.match(line)
                if m:
                    try:
                        got[label] = (num(m.group(1)), num(m.group(2)))
                    except ValueError:
                        pass
    return got


def main():
    if len(sys.argv) < 2:
        sys.exit('usage: unmapped_moments.py <worker log>')
    got = read(sys.argv[1])
    print('moment        what it is                      model        target      gap %')
    for label, what, _ in ROWS:
        if label not in got:
            print(f'{label:<13s} {what:<30s} {"not printed yet":>12s}')
            continue
        model, target = got[label]
        gap = 100.0 * (model - target) / target if target else float('nan')
        print(f'{label:<13s} {what:<30s} {model:12.5f} {target:12.5f} {gap:+9.2f}')


if __name__ == '__main__':
    main()
