# flows_digest.py <cf.log> -- the FLOWS lines of code/bcghw/patch_flows.py, pass by pass, as the two statistics compared
# with Beauregard, Couture, Green, Hicks and Warburton (2026):
#   entry: the yearly rate at which housed working-age households become homeless, with and without a SUD, and the
#          ratio (theirs: a long-standing SUD multiplies the monthly hazard of first entry by 4.56, 6.49 without the
#          childhood controls; Table 1);
#   persistence: of the households that enter homelessness, the share still homeless a year later (theirs: about 25
#          per cent, Figure E.9: "about 75% of first-time homeless entrants are no longer homeless 12 months later").
import re, sys
G = {1: 'all working ages', 2: 'employed', 3: 'not employed', 4: 'first ten adult years'}
num = r'([-+0-9.EeDd]+)'
passes, cur = [], {}
for l in open(sys.argv[1], errors='replace'):
    m = re.search(r'FLOWS ENTRY group=\s*(\d+)\s+housed_nosud=\s*' + num + r'\s+housed_sud=\s*' + num +
                  r'\s+enter_nosud=\s*' + num + r'\s+enter_sud=\s*' + num, l)
    if m:
        cur[int(m.group(1))] = [float(x.replace('D', 'E')) for x in m.groups()[1:]]
        continue
    m = re.search(r'FLOWS PERSIST new_nosud=\s*' + num + r'\s+new_sud=\s*' + num + r'\s+stay_nosud=\s*' + num +
                  r'\s+stay_sud=\s*' + num, l)
    if m:
        cur['p'] = [float(x.replace('D', 'E')) for x in m.groups()]
        passes.append(cur); cur = {}
if not passes:
    print('no FLOWS lines yet'); sys.exit(0)
for k, p in enumerate(passes, 1):
    print(f'pass {k}')
    for g in sorted(x for x in p if x != 'p'):
        hn, hs, en, es = p[g]
        rn, rs = (en / hn if hn else float('nan')), (es / hs if hs else float('nan'))
        print(f'  entry, {G[g]:22s}: no SUD {100*rn:7.3f}%  SUD {100*rs:7.3f}%  ratio {rs/rn if rn else float("nan"):6.2f}'
              f'   (housed mass {hn:.4g} / {hs:.4g})')
    nn, ns, sn, ss = p['p']
    tot = nn + ns
    print(f'  persistence: still homeless a year after entry: all {100*(sn+ss)/tot if tot else float("nan"):6.2f}%, '
          f'no SUD {100*sn/nn if nn else float("nan"):6.2f}%, SUD {100*ss/ns if ns else float("nan"):6.2f}%'
          f'   (entrants {nn:.4g} / {ns:.4g})')
