#!/usr/bin/env python3
"""Print the newest stylized calibration table, and the gap history, legibly.

The raw log table is fine to read one at a time and useless to compare across
iterations, which is what the author asked for: the point of a calibration table
is whether a gap is CLOSING, and that only shows up beside its own past.
"""
import re, sys, glob, os

HERE = os.path.dirname(os.path.abspath(__file__))
log = sys.argv[1] if len(sys.argv) > 1 else max(
    glob.glob(os.path.join(HERE, 'sr_run_*.log')), key=os.path.getmtime)
T = open(log, errors='replace').read().split('\n')

# HELD ROWS MUST APPEAR.  The first version required a numeric gap, so every
# held parameter -- the ones whose guard has fired and which are therefore the
# ones actually stuck -- vanished from the table without a word.  A reporter
# that drops rows is worse than no reporter.
ROW = re.compile(r'^\s{2}(\w+)\s+([\d.]+)\s+(\w+)\s+(HELD|[\d.]+)\s+([\d.]+)\s+(-?[\d.]+|--)')
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
for p, v, mom, mod, tgt, gap in rows:
    held = (mod == 'HELD') or gap == '--'
    mod = '     held' if held else '%9.4f' % float(mod)
    g = '    --' if held else '%+.1f%%' % float(gap)
    print('  %-9s %10.4f   %-18s %9s %9.4f %9s'
          % (p, float(v), mom, mod, float(tgt), g))
live = [float(g) for _, _, _, mo, _, g in rows
        if mo != 'HELD' and g != '--']
if live:
    live = sorted(abs(x) for x in live)
    print('  ' + '-' * 70)
    held = len(rows) - len(live)
    print('  %d live moments   worst %.1f%%   median %.1f%%   %d within 10%%'
          '   %d HELD'
          % (len(live), live[-1], live[len(live) // 2],
             sum(1 for x in live if x <= 10), held))

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
