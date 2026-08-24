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
import resource
import shutil
import signal
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
         'income_of_users', 'income_of_disordered', 'drug_share']
HANDOVER = os.path.join(HERE, 'PARAM_HANDOVER.txt')
# The parameters the point in flight was launched at, so bank() records the
# whole vector rather than only the half the model prints.
CURRENT_SET = [{}]


def _f(x):
    return float(x.replace('D', 'E').replace('d', 'e'))


def full_grid():
    """The grid. Each line is a b, then any number of name=value assignments.

    A POINT IS A PARAMETER VECTOR, not a scalar. The moments that decide whether
    the model has an equilibrium worth calibrating from are not owned by b
    alone: b sets the quantity used, lambda turns quantity into the disorder,
    aleph prices the death risk that deters both, h_1 prices the street, and the
    employment multiplier decides how much of the unemployment the disordered
    account for. Sweeping one at a time measures each in a world where the other
    four are wrong, which is how b came to be measured at a lambda of 0.225 that
    put the disorder rate at 0.000327 against a target of 0.0368.

    So a line reads

        0.047 lambda_addiction=4.5 value_of_life=11 size_homelessness=0.304

    The first field is b, which the model takes from B_SWEEP_GRID.txt. Every
    other field goes into PARAM_HANDOVER.txt, which the model reads after the
    state and deletes as it does, so nothing outlives the point it was set for.
    Any name the Fortran's handover select case knows may be used. A line with
    only a b runs everything else at the banked value, which is what the first
    three points did, so they stay comparable.

    A # starts a comment, because a grid is easier to read when the design is
    written beside it.
    """
    out = []
    for line in open(FULL):
        line = line.split('#')[0]
        parts = line.split()
        if not parts:
            continue
        extra = {}
        for tok in parts[1:]:
            if '=' not in tok:
                raise SystemExit(f'sweep: grid line {line.strip()!r} has a field '
                                 f'{tok!r} that is not name=value')
            k, v = tok.split('=', 1)
            extra[k] = _f(v)
        out.append((_f(parts[0]), extra))
    return out


def done_points():
    """The points already measured, as (b, {name: value}) read back from the bank.

    KEYED ON THE WHOLE VECTOR, not on b. Two points can share a b and differ in
    lambda or in aleph, and keyed on b alone every one after the first would be
    skipped as already done.
    """
    if not os.path.exists(OUT):
        return []
    with open(OUT) as f:
        rows = f.read().splitlines()[1:]
    out = []
    for r in rows:
        if not r.strip():
            continue
        f_ = r.split('\t')
        extra = {}
        if len(f_) > 7 and f_[7].strip():
            for tok in f_[7].split():
                if '=' in tok:
                    k, v = tok.split('=', 1)
                    try:
                        extra[k] = _f(v)
                    except ValueError:
                        pass
        out.append((_f(f_[1]), extra))
    return out


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
        # SIX OR SEVEN. The drug spending share was added as a seventh column
        # mid run, so rows written before it have six and must still parse: a
        # stricter test would have made every earlier row vanish, and the
        # driver counts rows to decide what is new to bank.
        if len(f) < 6:
            continue
        try:
            v = [_f(x) for x in f[:7]]
        except ValueError:
            continue
        out.append(dict(zip(NAMES, v)))
    return out



def merge_to_main(root):
    """Fast forward main onto the branch and push it, every time.

    THE STANDING RULE IS THAT MAIN CARRIES THE WORK, and the automation was
    only pushing the branch: a container rebuild restores from a PINNED commit,
    and every hand made commit in this session has gone to both, so leaving the
    machine made ones on the branch alone put the two out of step by hours of
    loops. Failure here is not fatal -- the branch push already succeeded and
    that is what a resume reads -- so it reports and returns rather than
    raising.
    """
    br = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                        cwd=root, capture_output=True, text=True).stdout.strip()
    if not br or br == 'main':
        return
    steps = [['git', 'checkout', '-q', 'main'],
             ['git', 'merge', '-q', br, '-m', f"Merge branch '{br}'"]]
    ok = all(subprocess.run(c, cwd=root, capture_output=True).returncode == 0
             for c in steps)
    if ok:
        for wait in (0, 2, 4, 8):
            if wait:
                time.sleep(wait)
            if subprocess.run(['git', 'push', '-q', 'origin', 'main'], cwd=root,
                              capture_output=True).returncode == 0:
                break
        else:
            print('main push failed; the branch is pushed and a resume reads that',
                  flush=True)
    subprocess.run(['git', 'checkout', '-q', br], cwd=root, capture_output=True)


def bank(rows):
    if not os.path.exists(OUT):
        with open(OUT, 'w') as f:
            f.write('utc\t' + '\t'.join(NAMES) + '\tset\n')
    with open(OUT, 'a') as f:
        for rec in rows:
            rec.setdefault('set', ' '.join(f'{k}={v:.10g}' for k, v
                                          in sorted(CURRENT_SET[0].items())))
            f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()) + '\t'
                    + '\t'.join('' if k not in rec else f'{rec[k]:.6g}'
                                for k in NAMES)
                    + '\t' + (rec.get('set') or '') + '\n')
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
            merge_to_main(ROOT)
            return
    print('sweep: push failed, the point is committed locally')


def write_remaining():
    """ONE POINT PER LAUNCH, and the rest of the grid stays on the shelf.

    The model runs a single pass and stops, because the tail of the calibration
    body it used to step b in is never reached and because that body updates
    parameters the sweep is meant to hold. So the grid file gets the first point
    still outstanding and nothing else; the driver relaunches for the next. Each
    process therefore starts from the same banked state and the same banked
    distribution, which is what makes the curve a function of the point alone.
    """
    def same(x, y):
        return abs(x - y) <= abs(x) * 1e-9 + 1e-15

    def same_point(a, c):
        if not same(a[0], c[0]) or set(a[1]) != set(c[1]):
            return False
        return all(same(a[1][k], c[1][k]) for k in a[1])

    have = done_points()
    left = [pt for pt in full_grid() if not any(same_point(pt, d) for d in have)]
    with open(GRID, 'w') as f:
        f.write(f'{left[0][0]:.10g}\n' if left else '')
    # THIS POINT'S PARAMETERS ONLY. The model deletes the handover as it reads
    # it, so nothing leaks into the next point; a point that names nothing gets
    # no handover and runs everything at the banked value.
    if os.path.exists(HANDOVER):
        os.remove(HANDOVER)
    if left and left[0][1]:
        with open(HANDOVER, 'w') as f:
            for k, v in sorted(left[0][1].items()):
                f.write(f'"{k}" {v:.10g}\n')
    CURRENT_SET[0] = left[0][1] if left else {}
    return left


def _child_setup():
    """Own session, and an unlimited stack. Same reasoning as the supervisor's.

    The model puts large automatic arrays on the stack, so inheriting the
    launching shell's limit means the sweep runs with 8 MB whenever it is not
    started by hand after a `ulimit -s unlimited`, and a sweep point that dies
    that way looks exactly like a b at which the model cannot solve.
    """
    os.setsid()
    try:
        resource.setrlimit(resource.RLIMIT_STACK,
                           (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ValueError, OSError):
        pass


def launch():
    env = dict(os.environ, OMP_NUM_THREADS='4', OMP_STACKSIZE='512M',
               GFORTRAN_UNBUFFERED_ALL='1')
    f = open(LOG, 'a')
    f.write('\n===== sweep launch =====\n')
    f.flush()
    return subprocess.Popen(['./hftf'], cwd=HERE, stdout=f,
                            stderr=subprocess.STDOUT, env=env,
                            preexec_fn=_child_setup)


def main():
    poll = 60
    while True:
        left = write_remaining()
        if not left:
            print('sweep: every point measured')
            return 0
        print(f'sweep: {len(done_points())} done, {len(left)} left, launching')
        before = len(measured(LOG))
        proc = launch()
        while True:
            time.sleep(poll)
            rows = measured(LOG)
            if len(rows) > before:
                bank(rows[before:])
                print(f'sweep: banked {rows[-1]["b"]:.4g} -> '
                      f'{rows[-1]["participation"]:.5f}')
                break
            if proc.poll() is not None:
                # The model stops itself once its one point is written, so an
                # exit with nothing new is a failure, not a finish.
                print('sweep: the model exited without writing a point')
                break
        if proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            time.sleep(2)


if __name__ == '__main__':
    sys.exit(main())
