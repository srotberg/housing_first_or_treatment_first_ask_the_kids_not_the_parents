#!/usr/bin/env python3
"""Read point files and print ONE comparison table across them.

    python3 code/arm_table.py LABEL=code/points/point_xxxx.txt LABEL=...

Written for batch_kkk.txt's four arms, where the whole question is what changes
between them, and reading four point files by eye invites picking the number
that suits the story.  Every field it prints is pulled by an exact string match
on a line the model wrote; a field it cannot find prints as "--" rather than as
a plausible-looking zero.
"""
import re
import sys

FIELDS = [
    # label,                        the exact text that identifies the line,   target
    ('sigma_y  bottom-half share',  'MOMENT sigma_y',                          0.172),
    ('h_1      homelessness',       'MOMENT h_1',                              0.00399),
    ('w_bot    bottom-half wealth', 'MOMENT w_bot',                            0.025),
    ('emp_homeless',                'UNTARGETED employed share of the homeless', 0.460),
    ('income of the homeless',      'UNTARGETED income of the homeless',       0.191),
]

BANDS = [0.003161, 0.003378, 0.002912, 0.002496, 0.000770]

NUM = re.compile(r'[-+]?\d*\.?\d+(?:[EeDd][-+]?\d+)?')


def numbers(line):
    return [float(x.replace('D', 'E').replace('d', 'e')) for x in NUM.findall(line)]


def read(path):
    out = {'bands': [None] * 5, 'inv_pass': 0, 'inv_fail': 0, 'fail_names': []}
    with open(path, errors='replace') as fh:
        text = fh.read()
    for line in text.splitlines():
        for label, key, _ in FIELDS:
            if key in line:
                got = numbers(line.split(key)[-1])
                if got:
                    out[label] = got[0]
        m = re.search(r'UNTARGETED homelessness rate, band\s+(\d)\s+model=\s*(\S+)', line)
        if m:
            out['bands'][int(m.group(1)) - 1] = float(m.group(2).replace('D', 'E'))
        if 'INVARIANT PASS' in line:
            out['inv_pass'] += 1
        if 'INVARIANT FAIL' in line:
            out['inv_fail'] += 1
            out['fail_names'].append(line.split('INVARIANT FAIL')[-1].split('=')[0].strip())
        if 'net_income_lowest' in line:
            got = numbers(line.split('net_income_lowest')[-1])
            if got:
                out['rent_over_income'] = got[0]
        if 'sd of log y at age 1' in line:
            got = numbers(line.split('=')[-1])
            if got:
                out['sd_log_y'] = got[0]
        if line.startswith('MODEL '):
            out['model'] = line.split()[1]
        if line.startswith('point '):
            out['point'] = line.split()[1]
    return out


def cell(v):
    if v is None:
        return '     --  '
    if v != v:                       # NaN
        return '    NaN  '
    return f'{v:9.5f}'


def main(args):
    arms = []
    for a in args:
        label, path = a.split('=', 1)
        arms.append((label, read(path)))

    width = max(len(l) for l, _ in arms) if arms else 8
    head = f'{"":30s} {"target":>9s} ' + ' '.join(f'{l:>{max(9, width)}s}' for l, _ in arms)
    print(head)
    print('-' * len(head))
    for label, _key, target in FIELDS:
        row = f'{label:30s} {target:9.5f} ' + ' '.join(
            cell(d.get(label)).rjust(max(9, width)) for _, d in arms)
        print(row)
    print()
    for i in range(5):
        row = f'{"homelessness, band " + str(i + 1):30s} {BANDS[i]:9.5f} ' + ' '.join(
            cell(d['bands'][i]).rjust(max(9, width)) for _, d in arms)
        print(row)
    print()
    for label, key in (('rent / lowest net income', 'rent_over_income'),
                       ('sd of log y at age 1', 'sd_log_y')):
        row = f'{label:30s} {"":9s} ' + ' '.join(
            cell(d.get(key)).rjust(max(9, width)) for _, d in arms)
        print(row)
    row = f'{"invariants passed":30s} {"":9s} ' + ' '.join(
        f'{str(d["inv_pass"]) + "/" + str(d["inv_pass"] + d["inv_fail"]):>{max(9, width)}s}'
        for _, d in arms)
    print(row)
    print()
    for label, d in arms:
        if d['fail_names']:
            print(f'{label}: FAILED invariants -- ' + '; '.join(d['fail_names']))
        print(f'{label}: point {d.get("point", "?")}  model {d.get("model", "?")}')


if __name__ == '__main__':
    main(sys.argv[1:])
