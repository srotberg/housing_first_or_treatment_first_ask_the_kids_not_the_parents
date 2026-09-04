"""The author's standing report.

*"when i ask for the gaps table, show me the ones you are actually calibrating!
then add the homelessness stats for the young and old and average income of users.
now the table above it very hard to read....it's not well positioned"* -- 4 September.

So: ONLY the moments in the objective, columns that line up, then the age profile,
then the incomes.  gaps.py stays the full audit of every measured moment; this is the
working view.

ONE EQUILIBRIUM, never a best-of across points, and the point is chosen by the same
sum of squares gaps.py and newton.py now rank on.
"""
import os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    A = N.archive()
    # THE SAME SET THE SEARCH MINIMISES, which since 4 September is every stage
    # unioned rather than stage 0.  Reading N.instruments() here printed the
    # fifteen stage-0 moments while nelder.py was optimising twenty, so the
    # table left out tau_u, lambda_m, mu_H, p_m and sud_homeless -- among them
    # the two largest gaps in the problem.
    # THE STAGE'S OWN SCOPE, NOT THE WHOLE OBJECTIVE.
    #
    # This read instruments_all with no stage, so it ranked points on all twenty
    # moments and printed whichever won THAT -- a different point from the one
    # the stage in progress is working on. The author noticed on 4 September:
    # "I also find it strange that pieu and sigma_y for example were the same
    # values they were a while back... It looks like they are not moving at all
    # in the calibration."
    #
    # They were moving. kkk_sigma_scale had gone 2.20949 to 2.0733 and
    # probability_becoming_unemployed 0.0122 to 0.012727 in the stage-2 best;
    # this table was simply showing a different equilibrium. A report that ranks
    # on a scope the search is not using is worse than no report, because it
    # reads as evidence the search is idle.
    #
    # STAGE=n on the command line, or the live stage from nm_stage.txt.
    stage = None
    for a in sys.argv[1:]:
        if a.startswith('stage='):
            stage = int(a.split('=')[1])
    if stage is None:
        try:
            stage = int(open(os.path.join(HERE, 'nm_stage.txt')).read().strip())
        except Exception:
            stage = None
    inst, dead = NM.instruments_all(N, NB, stage)
    print(f'  scope: stage {stage}' if stage else '  scope: every stage')
    if dead:
        print('  not measured on this economy, so not scored: '
              + ', '.join(m for _, m in dead))
    keys = [m for _, m in inst]
    args = [a for a in sys.argv[1:] if not a.startswith('stage=')]
    if args:
        tag = args[0]
        v, mom = A[tag]
    else:
        _, tag, v, mom = N.best(A, keys)
    r = N.residual(mom, keys)
    ssr = sum(x * x for x in r)
    inside = sum(1 for x in r if abs(x) <= 0.10)

    print(f'\npoint_{tag}    SSR {ssr:.4f}    worst {100*max(abs(x) for x in r):.1f}%    '
          f'inside ten {inside} of {len(r)}    ({len(A)} points in this economy)\n')

    W = 51
    print(f'{"parameter":{W}}{"value":>12}  {"moment":<13}{"model":>10}{"target":>10}{"gap":>9}')
    print('-' * (W + 12 + 2 + 13 + 10 + 10 + 9))
    rows = sorted(zip(inst, r), key=lambda t: -abs(t[1]))
    for (p, m), g in rows:
        mo, tv = mom[m]
        flag = ' *' if abs(g) <= 0.10 else ''
        print(f'{p:{W}}{float(v[p]):12.6g}  {m:<13}{mo:10.5f}{tv:10.5f}{100*g:8.1f}%{flag}')
    print(f'\n  * inside ten per cent.  {inside} of {len(r)}.')

    txt = open(os.path.join(HERE, 'points', f'point_{tag}.txt'), errors='ignore').read()

    def band(what, b):
        m = re.search(rf'UNTARGETED {what}, band\s+{b}\s+model=\s*([\d.eE+-]+)\s+'
                      rf'observed=\s*([\d.eE+-]+)', txt)
        return (float(m.group(1)), float(m.group(2))) if m else (float('nan'),) * 2

    print('\nHOMELESSNESS BY AGE\n')
    print(f'  {"":16}{"model":>10}{"data":>10}')
    for lbl, b in (('young, band 1', 1), ('old, band 5', 5)):
        s, so = band('share of the homeless', b)
        rt, ro = band('homelessness rate', b)
        print(f'  {lbl:16}{s:10.4f}{so:10.4f}   share of the homeless')
        print(f'  {"":16}{rt:10.5f}{ro:10.5f}   homelessness rate')

    ages = [(int(a), float(h), float(ms)) for a, h, ms in
            re.findall(r'DIAG age\s+(\d+)\s+homeless=\s*([\d.eE+-]+).*?mass=\s*([\d.eE+-]+)', txt)]
    tot = sum(h * ms for _, h, ms in ages)
    a, h, ms = max(ages, key=lambda t: t[1] * t[2])
    ret = [t for t in ages if t[0] >= 66]
    print(f'\n  spike        age {a}, rate {h:.5f}, {100*h*ms/tot:.1f}% of all homelessness')
    print(f'  retired 66+  {100*sum(h*ms for _, h, ms in ret)/tot:.1f}% of the homeless, '
          f'{100*sum(ms for *_, ms in ret)/sum(ms for *_, ms in ages):.1f}% of the population')

    print('\nINCOME, relative to the average\n')
    for lbl, pat in (('drug users', r'MOMENT y_u\s+income of drug users\s+model=\s*([\d.eE+-]+)\s+target=\s*([\d.eE+-]+)'),
                     ('homeless', r'UNTARGETED income of the homeless\s+model=\s*([\d.eE+-]+)\s+observed=\s*([\d.eE+-]+)')):
        mm = re.search(pat, txt)
        if mm:
            mo, dv = float(mm.group(1)), float(mm.group(2))
            print(f'  {lbl:12}{mo:10.4f}{dv:10.4f}{100*(mo/dv-1):8.1f}%')
    print('\n  drug users: 0.74 in Table 7 against 0.41 in the old benchmark, so a rise')
    print('  toward 0.74 was the model improving; only a ratio above one is a problem.\n')


if __name__ == '__main__':
    main()
