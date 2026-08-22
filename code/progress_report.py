"""
One screen of where the calibration is, for a report on a timer.

WHY A SCRIPT AND NOT A LOOK AT THE LOG. A progress report that is assembled by
hand each time is a report whose definition drifts, and this one is read every
ten minutes: it has to say the same things in the same order so that two reports
can be held against each other. It also has to be cheap, because it runs while
the model has all four cores.

WHAT IT SAYS, in order: whether anything is running at all, how far the run has
got, what the supervisor has done, and how far every moment is from its target
in RELATIVE terms, which is the only form in which misses on different scales
can be ranked. The relative gap is the report's own arithmetic, not the
Fortran's distances, because a distance is an absolute number against a target
on its own scale.

Run:  python3 progress_report.py
"""

import os
import re
import json
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, 'supervisor_run.log')
JOURNAL = os.path.join(HERE, 'SUPERVISOR_JOURNAL.md')
REPORT = os.path.join(HERE, 'paper', 'calibration_report.py')
HISTORY = os.path.join(HERE, 'progress_history.json')

sys.path.insert(0, HERE)


def running(name):
    r = subprocess.run(['ps', '-eo', 'comm'], capture_output=True, text=True)
    return name in r.stdout.split()


def head():
    model = 'up' if running('hftf') else 'DOWN'
    sup = 'up' if 'supervise_calibration' in subprocess.run(
        ['ps', '-eo', 'args'], capture_output=True, text=True).stdout else 'DOWN'
    return f'model {model}, supervisor {sup}, {advancing()}'


def advancing():
    """Whether the log is still growing, and how long since it last did.

    A ten minute cadence is shorter than a calibration loop, which costs fifteen
    to twenty minutes, so a report that repeats the previous one is normal. This
    is what tells that apart from a hang: a repeat with a log that grew seconds
    ago is a loop in progress, a repeat with a log untouched for an hour is not.
    """
    try:
        age = time.time() - os.path.getmtime(LOG)
    except OSError:
        return 'no log yet'
    if age < 90:
        return f'log grew {age:.0f}s ago'
    return f'LOG UNTOUCHED FOR {age / 60:.0f} MINUTES'


def loops():
    try:
        txt = open(LOG, errors='ignore').read()
    except FileNotFoundError:
        return 0, 0, 0
    n = len(re.findall(r'^\s*loop_count=', txt, re.M))
    stalls = txt.count('DIST_STALL')
    holds = txt.count('HELD:')
    return n, stalls, holds


def interventions():
    if not os.path.exists(JOURNAL):
        return 0, ''
    txt = open(JOURNAL).read()
    entries = re.findall(r'^## (.+)$', txt, re.M)
    acted = [e for e in entries if e.startswith('Intervention') or e.startswith('Stopped')]
    return len(acted), (acted[-1] if acted else '')


def moments():
    """The report's table, trimmed to what fits a progress note."""
    if not os.path.exists(REPORT):
        return 'no calibration_report.py', []
    r = subprocess.run([sys.executable, REPORT, LOG], capture_output=True,
                       text=True, cwd=os.path.dirname(REPORT))
    verdict = 'no verdict yet'
    m = re.search(r'(\d+) of (\d+) on target(?:, (\d+) within three per cent)?',
                  r.stdout)
    if m:
        verdict = m.group(0)
    rows = []
    for line in r.stdout.splitlines():
        g = re.match(r'^(\S+)\s+(\S+)\s+(\S+)\s+([\d.]+)%\s*$', line.strip())
        if g:
            rows.append((g.group(1), g.group(2), g.group(3), float(g.group(4))))
    return verdict, rows


def track(n_loops, med, worst):
    """Keep one point per loop, so the RATE can be measured rather than guessed.

    WHY THIS EXISTS. Asked how long the calibration would take, the only honest
    answer was that there was no basis for one: the per loop cost was measured
    but the rate at which gaps close was not, and run 2 never converged so it
    could not supply one either. A history of the median gap by loop is what
    turns that into arithmetic.
    """
    hist = []
    if os.path.exists(HISTORY):
        try:
            hist = json.load(open(HISTORY))
        except Exception:                              # noqa: BLE001
            hist = []
    if not hist or hist[-1]['loops'] != n_loops:
        hist.append(dict(loops=n_loops, median=med, worst=worst, t=time.time()))
        json.dump(hist[-400:], open(HISTORY, 'w'))
    return hist


def rate(hist):
    """What the history says about how fast it is closing, and what is left.

    Deliberately crude and deliberately hedged. Gaps do not close at a constant
    rate and this cannot see the coupling between brackets, so it reports the
    trend over the last stretch and an extrapolation, and says plainly when the
    trend is flat or going the wrong way rather than dividing by a negative
    number and printing a confident nonsense.
    """
    pts = [h for h in hist if h.get('median') is not None]
    if len(pts) < 4:
        return 'not enough loops yet to measure a rate'
    a, b = pts[0], pts[-1]
    dl = b['loops'] - a['loops']
    if dl <= 0:
        return 'no completed loops between the two ends of the history'
    per_loop = (b['median'] - a['median']) / dl
    hours = (b['t'] - a['t']) / 3600.0
    loop_h = hours / dl if dl else 0
    if per_loop >= -1e-9:
        return (f'median gap {a["median"]:.0f}% to {b["median"]:.0f}% over {dl} '
                f'loops: NOT closing, so no estimate can be made from it')
    need = b['median'] / -per_loop
    return (f'median gap {a["median"]:.0f}% to {b["median"]:.0f}% over {dl} loops, '
            f'{-per_loop:.1f} points a loop; at that rate about {need:.0f} more '
            f'loops, {need * loop_h:.0f} hours, and coupling makes that a floor '
            f'rather than a forecast')


def main():
    n, stalls, holds = loops()
    acted, last = interventions()
    verdict, rows = moments()

    print(f'CALIBRATION PROGRESS  |  {head()}')
    print(f'  loops {n}   distribution stalls {stalls}   guarded holds {holds}')
    print(f'  supervisor interventions {acted}' + (f'   last: {last}' if last else ''))
    print(f'  {verdict}')
    if rows:
        worst = sorted(rows, key=lambda r_: -r_[3])
        print('  furthest from target:')
        for name, mod, tgt, off in worst[:5]:
            print(f'    {name:<34s} {mod:>12s} vs {tgt:>10s}   {off:6.1f}%')
        print('  closest:')
        for name, mod, tgt, off in worst[-3:]:
            print(f'    {name:<34s} {mod:>12s} vs {tgt:>10s}   {off:6.1f}%')
        med = sorted(r_[3] for r_ in rows)[len(rows) // 2]
        print(f'  median gap {med:.1f}%   worst {worst[0][3]:.1f}%')
        print('  ' + rate(track(n, med, worst[0][3])))


if __name__ == '__main__':
    main()
