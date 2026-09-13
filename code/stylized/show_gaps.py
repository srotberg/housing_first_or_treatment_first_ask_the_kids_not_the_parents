#!/usr/bin/env python3
"""Print the newest stylized calibration table, and the gap history, legibly.

The raw log table is fine to read one at a time and useless to compare across
iterations, which is what the author asked for: the point of a calibration table
is whether a gap is CLOSING, and that only shows up beside its own past.
"""
import re, sys, glob, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
log = sys.argv[1] if len(sys.argv) > 1 else max(
    glob.glob(os.path.join(HERE, 'sr_run_*.log')), key=os.path.getmtime)
T = open(log, errors='replace').read().split('\n')

# HELD ROWS MUST APPEAR.  The first version required a numeric gap, so every
# held parameter -- the ones whose guard has fired and which are therefore the
# ones actually stuck -- vanished from the table without a word.  A reporter
# that drops rows is worse than no reporter.
ROW = re.compile(r'^\s{2}(\w+)\s+([\d.]+)\s+(\w+)\s+(HELD|[\d.]+)\s+([\d.]+)\s+(-?[\d.]+|--)\s*(smr\s+[\d.]+)?')
blocks, cur, it = [], None, None
for l in T:
    m = re.match(r'\s*ITERATION\s+(\d+)', l)
    if m:
        if cur: blocks.append((it, cur))
        it, cur = int(m.group(1)), []
        continue
    m = ROW.match(l)
    if m and cur is not None:
        cur.append(m.groups())
if cur: blocks.append((it, cur))
if not blocks:
    print('no table in %s yet' % os.path.basename(log)); sys.exit()

it, rows = blocks[-1]
print('%s   ITERATION %d' % (os.path.basename(log), it))
print()
print('  %-9s %10s   %-18s %9s %9s %9s' %
      ('parameter', 'value', 'moment', 'model', 'target', 'gap'))
print('  ' + '-' * 70)
for p, v, mom, mod, tgt, gap, smr in rows:
    held = (mod == 'HELD') or gap == '--'
    mod = '     held' if held else '%9.4f' % float(mod)
    g = '    --' if held else '%+.1f%%' % float(gap)
    # WHAT delta_d MEANS IN INCOME, printed beside it.  It is a LOG shift, so
    # the number in the value column says nothing about the size of the penalty
    # until it is exponentiated: 0.86 reads small and is a 58 per cent permanent
    # cut to the child's productivity.  The author asked for it on the table
    # rather than only on the log's PENALTY line.
    note = ''
    if p == 'delta_d':
        note = '   = %.1f%% income cut' % (100.0 * (1.0 - math.exp(-float(v))))
    elif smr:
        # THE IMPLIED SMR, which is what kappa actually means.  kappa is a
        # proportional fall in thirty-year survival; the standardised mortality
        # ratio it implies is how the literature states the same thing, and the
        # solver prints it beside r_use.
        note = '   implied %s' % smr.replace('smr', 'SMR')
    # SMALL PARAMETERS NEED MORE DIGITS.  omega is of order 1e-3 and steps at
    # 0.05 per cent of itself, so at four decimals it looks frozen when it is
    # moving -- which is exactly what it looked like.
    fmt = '%10.6f' if abs(float(v)) < 0.01 else '%10.4f'
    print(('  %-9s ' + fmt + '   %-18s %9s %9.4f %9s%s')
          % (p, float(v), mom, mod, float(tgt), g, note))
live = [float(g) for _, _, _, mo, _, g, _s in rows
        if mo != 'HELD' and g != '--']
if live:
    live = sorted(abs(x) for x in live)
    print('  ' + '-' * 70)
    held = len(rows) - len(live)
    print('  %d live moments   worst %.1f%%   median %.1f%%   %d within 10%%'
          '   %d HELD'
          % (len(live), live[-1], live[len(live) // 2],
             sum(1 for x in live if x <= 10), held))

# THE PARAMETERS MOVE TOO, AND THE GAPS ALONE DO NOT SHOW IT.  A moment that
# will not close because its instrument is pinned looks exactly like one that is
# converging slowly, until you put the parameter beside it.
# THE HOMELESSNESS ODDS RATIO IS REPORTED, NEVER TARGETED, so it has no row in
# the spec and never appeared on this table.  The author asked for it: it is the
# other half of what the child inherits, and delta_d drives BOTH -- a child
# pushed down by the penalty is likelier to be unhoused as well as to use.  The
# model's own ODDS line carries it, and ENGINE.md's rule is that anywhere from
# 1.8 to 2.4 is fine and only below 1.8 is a delta_h reconsidered.
tail = [l for l in T if l.strip().startswith('ODDS')]
if tail:
    m = re.search(r'child homeless\s+([\d.]+).*?child SUD\s+([\d.]+)', tail[-1])
    if m:
        print('\n  ODDS RATIOS   child homeless %s  (reported only, 1.8-2.4 is fine)'
              '   child SUD %s  (target 2.0)' % (m.group(1), m.group(2)))

print('\n  PARAMETER HISTORY')
pnames = [r[0] for r in max((b[1] for b in blocks), key=len)]
print('    it  ' + ''.join('%9s' % n[:8] for n in pnames))
for bit, brows in blocks:
    d = {r[0]: float(r[1]) for r in brows}
    print('  %4d  ' % bit + ''.join(
        ('%9.4f' % d[n]) if n in d else '%9s' % '-' for n in pnames))

print('\n  GAP HISTORY, per cent   (h = held)')
# the widest block, so a moment that was held out of the LAST table still
# gets a column and its history stays visible
names = max((b[1] for b in blocks), key=len)
names = [r[2] for r in names]
short = {'unemployment': 'unempl', 'sud_of_homeless2': 'sudhl2',
         'child_gap': 'chgap', 'child_sud_or': 'chsud', 'homeless': 'homeles'}
hdr = [short.get(n, n)[:7] for n in names]
print('    it  ' + ''.join('%8s' % h for h in hdr))
for bit, brows in blocks:
    d = {r[2]: ('h' if (r[3] == 'HELD' or r[5] == '--')
            else '%+.0f' % float(r[5])) for r in brows}
    print('  %4d  ' % bit + ''.join('%8s' % d.get(n, '-') for n in names))
