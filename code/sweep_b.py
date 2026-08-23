#!/usr/bin/env python3
"""Sweep b alone and record what participation it buys.

WHY A SWEEP RATHER THAN ANOTHER JOINT LOOP. Participation runs at 0.145 against
a target of 0.089, and at twice the right number of users nothing downstream of
it is identified: theta sits on its ceiling reaching for a drug spending share
that too many users put out of reach, and the income gradient, the spending
share and the treatment margin are all measured on the wrong population. b is
the parameter that sets participation, but the joint loop cannot pin it, because
every other parameter moves underneath it in the same iteration -- the run has b
at 0.0911 giving participation of 0.271 in one loop and 0.135 in another. So b
is moved alone, at fixed everything else, and the value that hits the target is
read off the curve.

The model does the stepping, with parameter updating switched off; this drives
it. It banks each point to git as it lands, because the container rebuilds about
every half hour and a sweep takes longer than that, and it rewrites the grid
file with the points that are LEFT before each launch, so a rebuild resumes
rather than restarts.
"""
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
LOG = os.path.join(HERE, 'sweep_b_run.log')
BANKED_LOG = os.path.join(HERE, 'b_sweep_run.log')
GRID = os.path.join(HERE, 'B_SWEEP_GRID.txt')
FULL = os.path.join(HERE, 'B_SWEEP_FULL.txt')
OUT = os.path.join(HERE, 'B_SWEEP.tsv')
RAW = os.path.join(HERE, 'B_SWEEP_RAW.tsv')

_NUM = r'([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)'
ANNOUNCE = re.compile(r'B SWEEP(?::\s+\d+\s+points, starting at b=|'
                      r' point\s+\d+\s+of\s+\d+\s+at b=)\s*' + _NUM)
DONE = re.compile(r'B SWEEP COMPLETE')
COLS = {
    'participation': r'(?m)^\s*model_exprimenters=\s*' + _NUM,
    'fraction_addicted': r'(?m)^\s*model_fraction_addicted=\s*' + _NUM,
    'drug_share': r'drug share, weighted by their population shares =\s*' + _NUM,
    'theta': r'(?m)^\s*relative_share_of_addiction_1=\s*' + _NUM,
    'income_of_users': (r'(?m)^\s*model_avg_income_drug_users/'
                        r'model_average_labour_income,\s*' + _NUM),
    'income_of_disordered': (r'(?m)^\s*model_average_income_addicted/'
                             r'model_average_labour_income\.\s*' + _NUM),
}
NAMES = ['b', 'participation', 'total_users', 'fraction_addicted',
         'income_of_users', 'income_of_disordered']


def _f(x):
    return float(x.replace('D', 'E').replace('d', 'e'))


def full_grid():
    with open(FULL) as f:
        return [_f(x) for x in f.read().split()]


def done_points():
    """The b values already measured, read back from the banked results."""
    if not os.path.exists(OUT):
        return []
    with open(OUT) as f:
        rows = f.read().splitlines()[1:]
    return [_f(r.split('\t')[1]) for r in rows if r.strip()]


def measured(path):
    """The rows the model wrote itself, not a reading of its log.

    THE LOG CANNOT SETTLE THE PAIRING. The model prints model_exprimenters from
    three separate places and prints its statistics on the opposite side of the
    loop counter from the b it moves to, so pairing a b with a participation
    means deciding which side of a boundary a print falls on. It writes the pair
    itself now, at the foot of the pass, where addiction_scalar_1 is still the b
    that pass ran at and the moments are the ones it finished with. `path` is
    ignored; it is kept so the caller reads the same way it did.
    """
    del path
    try:
        rows = open(RAW, errors='ignore').read().splitlines()
    except FileNotFoundError:
        return []
    out = []
    for line in rows:
        f = [x for x in line.split('\t') if x.strip()]
        if len(f) < 6:
            continue
        try:
            v = [_f(x) for x in f[:6]]
        except ValueError:
            continue
        out.append(dict(zip(NAMES, v)))
    return out


def bank(rows):
    if not os.path.exists(OUT):
        with open(OUT, 'w') as f:
            f.write('utc\t' + '\t'.join(NAMES) + '\n')
    with open(OUT, 'a') as f:
        for rec in rows:
            f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\t'
                    + '\t'.join('' if k not in rec else f'{rec[k]:.6g}'
                                for k in NAMES) + '\n')
    if os.path.exists(LOG):
        shutil.copyfile(LOG, BANKED_LOG)
    subprocess.run(['git', 'add', OUT, BANKED_LOG, FULL, RAW], cwd=ROOT)
    subprocess.run(['git', 'commit', '-q', '-m',
                    f'b sweep: {len(done_points())} of {len(full_grid())} points'],
                   cwd=ROOT)
    for wait in (0, 2, 4, 8):
        if wait:
            time.sleep(wait)
        r = subprocess.run(['git', 'push', '-u', 'origin', 'HEAD'], cwd=ROOT,
                           capture_output=True, text=True)
        if r.returncode == 0:
            return
    print('sweep: push failed, the point is committed locally')


def write_remaining():
    """The grid file gets what is LEFT, so a relaunch resumes."""
    have = done_points()
    left = [b for b in full_grid()
            if not any(abs(b - d) <= abs(b) * 1e-9 for d in have)]
    with open(GRID, 'w') as f:
        f.write('\n'.join(f'{b:.10g}' for b in left) + ('\n' if left else ''))
    return left


def launch():
    env = dict(os.environ, OMP_NUM_THREADS='4', OMP_STACKSIZE='512M',
               GFORTRAN_UNBUFFERED_ALL='1')
    f = open(LOG, 'a')
    f.write('\n===== sweep launch =====\n')
    f.flush()
    return subprocess.Popen(['./hftf'], cwd=HERE, stdout=f,
                            stderr=subprocess.STDOUT, env=env,
                            preexec_fn=os.setsid)


def main():
    poll = 60
    while True:
        left = write_remaining()
        if not left:
            print('sweep: every point measured')
            return 0
        print(f'sweep: {len(done_points())} done, {len(left)} left, launching')
        open(LOG, 'w').close()
        proc, banked = launch(), 0
        while True:
            time.sleep(poll)
            rows = measured(LOG)
            if len(rows) > banked:
                bank(rows[banked:])
                banked = len(rows)
                print(f'sweep: banked {rows[-1]["b"]:.4g} -> '
                      f'{rows[-1]["participation"]:.5f}')
            txt = open(LOG, errors='ignore').read()
            if DONE.search(txt):
                print('sweep: the model reports the grid exhausted')
                return 0
            if proc.poll() is not None:
                print('sweep: the model exited, relaunching on what is left')
                break


if __name__ == '__main__':
    sys.exit(main())
