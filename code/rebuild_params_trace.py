#!/usr/bin/env python3
"""Rebuild the parameter trace from the banked run logs, not from guesswork.

WHY THIS EXISTS, AND WHY THE FIRST ATTEMPT WAS THROWN AWAY. The trace answers
which parameter has stopped moving, and it is worthless if a column is on the
wrong parameter. The first attempt read `calibration_state.dat` out of the
checkpoint commits and matched its 157 values against the names in the
`write(71,...)` block by regex, which captured 98 names for 99 statements and
could not have lined up. It did not: four columns came back carrying the same
number in every row. Anything read off that file was an artefact of the
mismatch, so it was deleted rather than patched.

The banked run log is the honest source. It is the model's own printed output,
each value next to the name the model printed it under, and every checkpoint
commit holds a copy. This walks those commits, parses each log with the SAME
read_loops the supervisor uses live, and dedupes: containers restart, so
successive commits hold overlapping prefixes of one log.
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from supervise_calibration import (BANKED_LOG, MOMENTS, PARAMS,  # noqa: E402
                                   WATCH, read_loops)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REL = os.path.relpath(BANKED_LOG, ROOT)


def git(*a):
    return subprocess.run(['git'] + list(a), cwd=ROOT, capture_output=True,
                          text=True).stdout


def main():
    revs = git('log', '--reverse', '--format=%H %cI', '--', REL).split('\n')
    revs = [r.split() for r in revs if r.strip()]
    seen, rows = set(), []
    tmp = os.path.join(HERE, '.params_trace_tmp.log')
    for sha, when in revs:
        txt = git('show', f'{sha}:{REL}')
        if not txt:
            continue
        with open(tmp, 'w') as f:
            f.write(txt)
        for rec in read_loops(tmp):
            key = tuple(sorted(rec.items()))
            if key in seen:
                continue
            seen.add(key)
            rows.append((when, rec))
    if os.path.exists(tmp):
        os.remove(tmp)

    # A PARTIAL LOOP IS NOT A LOOP. Each banked log is committed the moment the
    # loop counter ticks, so its last chunk is cut short and holds only the
    # moments printed so far. The next commit holds that same chunk complete.
    # Without this the trace read 41 loops where 21 had run, every other row a
    # torso of the row below it.
    full = []
    for i, (when, rec) in enumerate(rows):
        items = set(rec.items())
        if any(items < set(o.items()) for _, o in rows[i + 1:]):
            continue
        full.append((when, rec))
    rows = full

    names = sorted(WATCH)
    with open(PARAMS, 'w') as f:
        f.write('utc\tloop\t' + '\t'.join(names) + '\n')
        for i, (when, rec) in enumerate(rows, 1):
            f.write(when + f'\t{i}\t' + '\t'.join(
                '' if k not in rec else f'{rec[k]:.6g}' for k in names) + '\n')
    print(f'{len(revs)} banked logs, {len(rows)} distinct loops -> {PARAMS}')

    audit(''.join(git('show', f'{sha}:{REL}') for sha, _ in revs), rows, names)


def audit(txt, rows, names):
    """Refuse to hand back a trace whose columns might be on the wrong thing.

    TWO WAYS A COLUMN GOES WRONG, both of which have happened here. It can carry
    a different quantity than its name says, which is what an unanchored pattern
    does when the model prints distance_X= just below X=; and two columns can
    silently be the same quantity, which is what the abandoned first attempt at
    this trace produced when it matched 98 names against 157 values. Neither is
    visible in the numbers themselves -- both give a plausible looking series --
    so they are checked rather than eyeballed.
    """
    bad = False
    for name, pat in {**WATCH, **MOMENTS}.items():
        labels = set()
        for m in re.finditer(pat, txt):
            line = txt[txt.rfind('\n', 0, m.start()) + 1:m.end()]
            labels.add(line.strip().split('=')[0].split(',')[0].strip()[:60])
        if len(labels) > 1:
            bad = True
            print(f'  AMBIGUOUS: {name} matches {sorted(labels)}')
        elif not labels:
            print(f'  UNMATCHED: {name} never appears in any banked log')
    cols = {k: [r.get(k) for _, r in rows] for k in names}
    for a in names:
        for b in names:
            if a < b and cols[a] == cols[b] and any(v is not None
                                                    for v in cols[a]):
                bad = True
                print(f'  SUSPECT: {a} and {b} are identical in every loop')
    if bad:
        print('  the trace is NOT trustworthy as written; fix the patterns')


if __name__ == '__main__':
    sys.exit(main())
