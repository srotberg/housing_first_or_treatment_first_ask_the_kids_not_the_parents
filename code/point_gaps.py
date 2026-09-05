#!/usr/bin/env python3
"""The gap table for ONE point, plus the four things the author asks for every time.

    python3 code/point_gaps.py <tag>        # a specific point
    python3 code/point_gaps.py              # the newest point on the live model

WHY THIS EXISTS RATHER THAN gaps.py. gaps.py ranks the whole archive and prints
the BEST point in the economy, which is the right thing while a search is
converging and the wrong thing right after a parameter is moved by hand: the
best point is then several iterations stale and does not show what the change
did. This prints the point you name.

THE FOUR STANDING EXTRAS, on the author's instruction of 5 September: *"in every
gaps table i want to also see the homeless with SUD, the homelessness share by
age, the average income of users and of the homeless"*. Three of the four are
UNTARGETED or DIAG lines rather than MOMENT lines, so a table built from MOMENT
alone silently drops them -- which is exactly what happened before this file.
"""

import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import next_batch as nb, fixed_point as fp


def live_model():
    import hashlib
    src = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
    return hashlib.md5(open(src, 'rb').read()).hexdigest()[:10]


def newest_on(model):
    d = os.path.join(HERE, 'points')
    best, best_m = None, -1
    for f in os.listdir(d):
        if not (f.startswith('point_') and f.endswith('.txt')):
            continue
        p = os.path.join(d, f)
        try:
            if f'MODEL {model}' not in open(p, errors='replace').read(4000):
                continue
        except OSError:
            continue
        m = os.path.getmtime(p)
        if m > best_m:
            best, best_m = f[6:-4], m
    return best


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else newest_on(live_model())
    if not tag:
        print('no point on the live model'); return
    s = open(os.path.join(HERE, 'points', f'point_{tag}.txt'), errors='replace').read()
    vec = dict(kv.split('=', 1) for kv in re.search(r'^VECTOR (.*)$', s, re.M).group(1).split())
    mom = {m.group(1): (float(m.group(2)), float(m.group(3))) for m in
           re.finditer(r'^ MOMENT (\S+)\s+.*?model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', s, re.M)}

    PMAP = [v for k, v in vars(nb).items()
            if isinstance(v, dict) and v.get('size_homelessness') == 'h_1'][0]

    rows = []
    for p, mo in PMAP.items():
        if p not in vec or mo not in mom:
            continue
        md, tg = mom[mo]
        gap = (md / tg - 1.0) * 100 if tg else float('nan')
        st = 'FROZEN' if p in fp.FROZEN else ('capped' if p in fp.CAPPED else '')
        rows.append((abs(gap), p, vec[p], mo, md, tg, gap, st))
    rows.sort(reverse=True)

    model_tag = re.search(r'^MODEL (\S+)', s, re.M).group(1)
    print(f'point_{tag}   MODEL {model_tag}')
    print(f'{"parameter":<44}{"value":>14}  {"moment":<14}{"model":>11}{"target":>11}{"gap":>10}  status')
    print('-' * 118)
    for _, p, v, mo, md, tg, gap, st in rows:
        print(f'{p:<44}{v:>14}  {mo:<14}{md:>11.5f}{tg:>11.5f}{gap:>+9.1f}%  {st}')

    print(f'\n{"FROZEN / EXOGENOUS":<44}{"value":>14}')
    for p in sorted(fp.FROZEN):
        if p in vec:
            print(f'{p:<44}{vec[p]:>14}')

    scored = set(PMAP.values())
    print('\nSCORED, NO PARAMETER IN THE VECTOR')
    for mo, (md, tg) in sorted(mom.items()):
        if mo not in scored and tg:
            print(f'{"(no instrument)":<44}{"-":>14}  {mo:<14}{md:>11.5f}{tg:>11.5f}'
                  f'{(md/tg-1)*100:>+9.1f}%')

    # ---- the author's four standing extras ----
    def one(pat):
        m = re.search(pat, s, re.M)
        return (float(m.group(1)), float(m.group(2))) if m else None

    print('\n=== STANDING EXTRAS ===')
    for label, pat in (
        ('homeless with a SUD',
         r'UNTARGETED SUD share of the homeless\s+model=\s*([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)'),
        ('average income of drug users',
         r'MOMENT y_u\s+.*?model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)'),
        ('average income of the homeless',
         r'UNTARGETED income of the homeless\s+model=\s*([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)'),
    ):
        r = one(pat)
        print(f'  {label:<34}{r[0]:>11.5f}   data {r[1]:>8.5f}' if r
              else f'  {label:<34}      not in this point')

    print('\n  homelessness SHARE of the homeless, by age band')
    bands = re.findall(r'UNTARGETED share of the homeless, band\s+(\d+)\s+model=\s*'
                       r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', s)
    ages = {1: '26-34', 2: '35-44', 3: '45-54', 4: '55-64', 5: '65-85'}
    for i, md, ob in bands:
        print(f'    band {i} ({ages[int(i)]:<5}) {float(md):>10.5f}   data {float(ob):>7.3f}')

    print('\n  homelessness RATE within each age band')
    rates = re.findall(r'UNTARGETED homelessness rate, band\s+(\d+)\s+model=\s*'
                       r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', s)
    for i, md, ob in rates:
        print(f'    band {i} ({ages[int(i)]:<5}) {float(md):>10.6f}   data {float(ob):>8.5f}')


main()
