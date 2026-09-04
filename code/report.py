"""The author's standing report, 4 September.

*"Things I want you to report as we move along are the gaps table, the homelessness
of the young and old (and where the homelessness for the old spikes). The average
income of users and average income of homeless."*

Run with no argument to report the best point, or with a tag to report one point:

    python3 code/report.py
    python3 code/report.py 50edd1ae5b

It prints gaps.py's own table first -- that file stays the only sanctioned gap
report, and this one calls it rather than reimplementing it -- then the three things
the author asked for on top. ONE POINT, never a best-of across points.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def best_tag():
    import newton as N, next_batch as NB
    NB._apply_process_mapping()
    A = N.archive()
    keys = [m for _, m in N.instruments()]
    w, tag, _, _ = N.best(A, keys)
    return tag


def band_rows(txt, what):
    out = {}
    for m in re.finditer(rf'UNTARGETED {what}, band\s+(\d+)\s+model=\s*([\d.eE+-]+)\s+observed=\s*([\d.eE+-]+)', txt):
        out[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    return out


def one(txt, pat):
    m = re.search(pat, txt)
    return tuple(float(g) for g in m.groups()) if m else None


def main():
    tag = sys.argv[1] if len(sys.argv) > 1 else best_tag()
    path = os.path.join(HERE, 'points', f'point_{tag}.txt')
    txt = open(path, errors='ignore').read()

    print(subprocess.run([sys.executable, os.path.join(HERE, 'gaps.py'), '--force'],
                         capture_output=True, text=True).stdout)

    print(f'=== the age profile of homelessness, point_{tag} ===\n')
    sh = band_rows(txt, 'share of the homeless')
    rt = band_rows(txt, 'homelessness rate')
    lbl = {1: 'youngest', 5: 'oldest'}
    print(f"  {'band':>5}{'share model':>13}{'observed':>10}{'rate model':>13}{'observed':>11}")
    for b in sorted(sh):
        s, so = sh[b]
        r, ro = rt.get(b, (float('nan'),) * 2)
        print(f'  {b:>5}{s:13.4f}{so:10.4f}{r:13.5f}{ro:11.5f}   {lbl.get(b, "")}')

    ages = [(int(m.group(1)), float(m.group(2)), float(m.group(3)))
            for m in re.finditer(r'DIAG age\s+(\d+)\s+homeless=\s*([\d.eE+-]+).*?mass=\s*([\d.eE+-]+)', txt)]
    tot = sum(h * ms for _, h, ms in ages)
    print('\n  WHERE THE OLD SPIKE SITS -- top five ages by share of all homelessness:')
    for a, h, ms in sorted(ages, key=lambda r: -r[1] * r[2])[:5]:
        print(f'    age {a:>3}  rate {h:9.5f}   {100*h*ms/tot:5.1f}% of all homelessness')
    ret = [r for r in ages if r[0] >= 66]
    print(f'\n    retired (66+) are {100*sum(h*ms for _, h, ms in ret)/tot:.1f}% of the homeless '
          f'and {100*sum(ms for *_, ms in ret)/sum(ms for *_, ms in ages):.1f}% of the population')

    print('\n=== incomes, relative to the average ===\n')
    for lab, pat, note in [
        ('income of drug users', r'MOMENT y_u\s+income of drug users\s+model=\s*([\d.eE+-]+)\s+target=\s*([\d.eE+-]+)',
         'Table 7 puts it at 0.74 in the data against 0.41 in the old benchmark, so a RISE toward 0.74 is the model improving'),
        ('income of the homeless', r'UNTARGETED income of the homeless\s+model=\s*([\d.eE+-]+)\s+observed=\s*([\d.eE+-]+)',
         'Meyer et al. 2024'),
    ]:
        v = one(txt, pat)
        if v:
            print(f'  {lab:24s} model {v[0]:7.4f}   data {v[1]:7.4f}   gap {100*(v[0]/v[1]-1):+7.1f}%')
            print(f'    {note}')


if __name__ == '__main__':
    main()
