"""
Watch the quantitative model calibrate, diagnose it, fix what it can, restart.

WHY THIS EXISTS. Every pathology this calibration has hit so far was found by a
person reading a log by hand, hours after it started, and each cost a run:

  - two moments computed on an empty set, read as a clean 1.0 and 0.0, driving
    two brackets away from values that were fine;
  - a distribution loop with no iteration cap, spinning on a residual that had
    stopped falling;
  - h_2's bracket bounded at a value that DESTROYS the moment it is calibrated
    on, so the gap it read there was constant, it froze at the bound, and h_1
    ran away against it for five loops while nothing said a word.

None of those needs a person. Each has a signature in the log that a machine can
read while the run is still young, and each has a remedy that is a bounded
numeric change to a bound or an adjuster. This does that, and escalates anything
outside its catalogue rather than guessing.

WHAT IT WILL AND WILL NOT TOUCH. It edits BOUNDS and ADJUSTERS: the numbers that
control how a bracket searches. It does not touch model logic, targets, or
functional forms, because a supervisor that rewrites the model until its own
convergence test passes is not calibrating anything. Anything it cannot fix from
the catalogue stops the run and says why, in the journal.

Run:  python3 supervise_calibration.py [--max-restarts N] [--poll SECONDS]
"""

import os
import re
import signal
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
BIN = os.path.join(HERE, 'hftf')
LOG = os.path.join(HERE, 'supervisor_run.log')
JOURNAL = os.path.join(HERE, 'SUPERVISOR_JOURNAL.md')
REPORT = os.path.join(HERE, 'paper', 'calibration_report.py')

COMPILE = ['gfortran', SRC, '-mcmodel=medium', '-fopenmp', '-O2',
           '-ffree-line-length-none', '-o', BIN]

# ---------------------------------------------------------------------------
# WHAT A LOOP LOOKS LIKE IN THE LOG. The calibration prints loop_count= once a
# loop, so a loop is the text between two of those. A value is taken as the LAST
# occurrence inside the loop, because several are printed both before and after
# their update and it is the post-update value the next loop starts from.
LOOP_MARK = re.compile(r'^\s*loop_count=\s*(\d+)', re.M)

_NUM = r'([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)'

# Adding a parameter here is what makes it watched.
WATCH = {
    'smallest_rental': r'smallest_rental_relative_to_lowest_income=\s*' + _NUM,
    'size_homelessness': r'size_homelessness=\s*' + _NUM,
    'largest_house_size': r'largest_house_size=\s*' + _NUM,
    'grid_expander': r'housing_status_grid_expander=\s*' + _NUM,
}

# Moments, so a parameter moving against a moment that does not respond can be
# told from a bracket that is merely slow.
MOMENTS = {
    'homelessness': r'model_fraction_homeless\(1\)=\s*' + _NUM,
}

# The only bounds the supervisor may move. Nothing outside this table is edited.
BOUNDS = {
    'smallest_rental': dict(
        decl='real(8), parameter :: smallest_rental_floor=',
        kind='floor',
        # A floor that pins is a floor in the wrong place. The evidence for
        # pinning is that the moment stops responding at or below it, so raise.
        widen=lambda v: v * 2.0,
        limit=0.20,
    ),
}

PIN_LOOPS = 3        # loops on a bound before it counts as pinned
RUNAWAY_LOOPS = 5    # loops of one-way movement against a flat moment
FLAT_LOOPS = 5       # loops of a moment not moving at all


def _f(x):
    """Fortran's D exponent is Python's E."""
    return float(x.replace('d', 'e').replace('D', 'E'))


def read_loops(path):
    """The log split into loops, each a dict of the values seen inside it."""
    try:
        txt = open(path, errors='ignore').read()
    except FileNotFoundError:
        return []
    cuts = [m.start() for m in LOOP_MARK.finditer(txt)]
    if not cuts:
        return []
    out = []
    for a, b in zip([0] + cuts, cuts + [len(txt)]):
        chunk = txt[a:b]
        rec = {}
        for name, pat in {**WATCH, **MOMENTS}.items():
            hits = re.findall(pat, chunk)
            if hits:
                try:
                    rec[name] = _f(hits[-1])
                except ValueError:
                    pass
        if rec:
            out.append(rec)
    return out


def series(loops, name):
    return [r[name] for r in loops if name in r]


def current_bound(target):
    spec = BOUNDS.get(target)
    if spec is None:
        return None
    m = re.search(re.escape(spec['decl']) + _NUM, open(SRC).read())
    return _f(m.group(1)) if m else None


# ---------------------------------------------------------------------------
# THE DIAGNOSES. Each returns None or a dict naming the problem, the evidence,
# and the remedy. They are deliberately conservative: a false positive costs a
# restart, so each needs several loops of agreement before it fires.

def diagnose_pinned_at_bound(loops):
    """A parameter sitting on a bound while its moment says nothing."""
    v = series(loops, 'smallest_rental')
    floor = current_bound('smallest_rental')
    if len(v) < PIN_LOOPS or floor is None:
        return None
    tail = v[-PIN_LOOPS:]
    if all(abs(x - floor) <= max(floor, 1e-12) * 1e-6 for x in tail):
        return dict(name='h_2 pinned at its floor',
                    evidence=f'smallest_rental at {floor:g} for {PIN_LOOPS} loops',
                    remedy='widen_bound', target='smallest_rental')
    return None


def diagnose_dead_moment(loops):
    """A moment that has not moved at all for several loops."""
    m = series(loops, 'homelessness')
    if len(m) < FLAT_LOOPS:
        return None
    tail = m[-FLAT_LOOPS:]
    if max(tail) - min(tail) <= 1e-12:
        return dict(name='the homelessness moment is frozen',
                    evidence=(f'homelessness identical for {FLAT_LOOPS} loops '
                              f'at {tail[-1]:.3g}'),
                    remedy='widen_bound', target='smallest_rental')
    return None


def diagnose_runaway(loops):
    """A parameter moving one way, accelerating, against a flat moment.

    This is h_1's signature in run 2: size_homelessness climbing 0.30 to 0.82
    with growing steps while homelessness sat at exactly zero. The moment being
    FLAT is what separates a runaway from a bracket that is merely slow.
    """
    p, m = series(loops, 'size_homelessness'), series(loops, 'homelessness')
    if min(len(p), len(m)) < RUNAWAY_LOOPS:
        return None
    p, m = p[-RUNAWAY_LOOPS:], m[-RUNAWAY_LOOPS:]
    steps = [p[i + 1] - p[i] for i in range(len(p) - 1)]
    one_way = all(s > 0 for s in steps) or all(s < 0 for s in steps)
    growing = all(abs(steps[i + 1]) >= abs(steps[i]) * 0.99
                  for i in range(len(steps) - 1))
    if not (one_way and growing and max(m) - min(m) <= 1e-12):
        return None
    ev = (f'size_homelessness {p[0]:.4g} to {p[-1]:.4g} with growing steps '
          f'while homelessness stayed at {m[-1]:.3g}')
    # WHOSE FAULT IS IT. The run 2 failure was h_1 running against a moment that
    # h_2 had killed by sitting on its floor, and raising that floor is the fix.
    # If h_2 is NOT at its floor the cause is something else and raising it would
    # be a guess dressed as a remedy, so escalate instead.
    r, floor = series(loops, 'smallest_rental'), current_bound('smallest_rental')
    at_floor = (r and floor is not None
                and abs(r[-1] - floor) <= max(floor, 1e-12) * 1e-6)
    if at_floor:
        return dict(name='h_1 running away because h_2 sits on its floor',
                    evidence=ev + f', with h_2 pinned at {floor:g}',
                    remedy='widen_bound', target='smallest_rental')
    return dict(name='h_1 running away against a moment that does not respond',
                evidence=ev + ', and h_2 is not at its floor, so the cause is elsewhere',
                remedy='escalate', target='size_homelessness')


def diagnose_distribution_stall(path):
    try:
        txt = open(path, errors='ignore').read()
    except FileNotFoundError:
        return None
    if 'DIST_STALL' in txt:
        return dict(name='the distribution loop hit its sweep cap',
                    evidence=f'{txt.count("DIST_STALL")} DIST_STALL line(s)',
                    remedy='escalate', target='distribution')
    return None


DIAGNOSES = [diagnose_pinned_at_bound, diagnose_dead_moment, diagnose_runaway]


# ---------------------------------------------------------------------------
# THE REMEDIES.

def _fortran(x):
    s = f'{x:.10g}'
    return s + 'd0'


def widen_bound(target):
    """Move a bound that is pinning, inside the limit the table allows."""
    spec = BOUNDS[target]
    old = current_bound(target)
    if old is None:
        return False, f'no bound found for {target}'
    new = spec['widen'](old)
    if new > spec['limit']:
        return False, (f'{target} would go past its limit {spec["limit"]:g}; '
                       f'that is a modelling question, not a search one')
    txt = open(SRC).read()
    m = re.search(re.escape(spec['decl']) + _NUM, txt)
    txt = txt[:m.start()] + spec['decl'] + _fortran(new) + txt[m.end():]
    open(SRC, 'w').write(txt)
    return True, f'{target} {spec["kind"]} raised from {old:g} to {new:g}'


REMEDIES = {'widen_bound': widen_bound}


# ---------------------------------------------------------------------------

def journal(entry):
    head = '' if os.path.exists(JOURNAL) else (
        '# Supervisor journal\n\n'
        'Written by `supervise_calibration.py`. One entry per intervention: what\n'
        'the log showed, what changed, and why. The source moves under this file,\n'
        'so it is the account of every automatic edit.\n')
    with open(JOURNAL, 'a') as f:
        if head:
            f.write(head)
        f.write('\n' + entry + '\n')


def commit(message):
    for cmd in (['git', 'add', '-A'],
                ['git', 'commit', '-q', '-m', message],
                ['git', 'push', '-q', 'origin', 'HEAD']):
        subprocess.run(cmd, cwd=ROOT, capture_output=True)


def compile_model():
    r = subprocess.run(COMPILE, cwd=HERE, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or '')[-2000:]


def launch():
    env = dict(os.environ, OMP_NUM_THREADS='4', OMP_STACKSIZE='512M',
               GFORTRAN_UNBUFFERED_ALL='1')
    f = open(LOG, 'a')
    f.write('\n===== supervisor launch =====\n')
    f.flush()
    return subprocess.Popen(['./hftf'], cwd=HERE, stdout=f,
                            stderr=subprocess.STDOUT, env=env,
                            preexec_fn=os.setsid)


def verdict():
    """The report's own reading, so the supervisor and the paper agree."""
    if not os.path.exists(REPORT):
        return False, 'no calibration_report.py'
    r = subprocess.run([sys.executable, REPORT, LOG], capture_output=True,
                       text=True, cwd=os.path.dirname(REPORT))
    m = re.search(r'(\d+) of (\d+) on target', r.stdout)
    if not m:
        return False, 'the report gave no verdict yet'
    hit, total = int(m.group(1)), int(m.group(2))
    return hit == total and total > 0, f'{hit} of {total} on target'


def main():
    max_restarts, poll = 12, 180
    for i, a in enumerate(sys.argv):
        if a == '--max-restarts':
            max_restarts = int(sys.argv[i + 1])
        if a == '--poll':
            poll = int(sys.argv[i + 1])

    ok, err = compile_model()
    if not ok:
        print('supervisor: COMPILE FAILED\n' + err)
        return 1
    proc, restarts = launch(), 0
    print(f'supervisor: launched pid {proc.pid}, polling every {poll}s')

    while True:
        time.sleep(poll)
        alive = proc.poll() is None
        loops = read_loops(LOG)
        done, said = verdict()

        if done:
            print(f'supervisor: CONVERGED, {said}')
            journal(f'## Converged\n\n{said}, after {restarts} intervention(s).')
            commit('Calibration converged under the supervisor')
            return 0

        finding = diagnose_distribution_stall(LOG)
        if finding is None:
            for d in DIAGNOSES:
                finding = d(loops)
                if finding:
                    break

        if finding is None:
            if not alive:
                print('supervisor: the model exited and nothing was diagnosed')
                journal('## The model exited and nothing in the catalogue matched\n\n'
                        'Stopping rather than restarting blind.')
                commit('Supervisor: model exited undiagnosed')
                return 2
            print(f'supervisor: {len(loops)} loop(s), {said}, nothing to fix')
            continue

        if finding['remedy'] == 'escalate' or restarts >= max_restarts:
            why = ('outside the catalogue' if finding['remedy'] == 'escalate'
                   else f'the restart budget of {max_restarts} is spent')
            print(f'supervisor: STOPPING, {finding["name"]} ({why})')
            journal(f'## Stopped: {finding["name"]}\n\n{finding["evidence"]}\n\n'
                    f'Not fixed automatically: {why}. This one needs a person.')
            if alive:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            commit(f'Supervisor stopped: {finding["name"]}')
            return 3

        if alive:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            time.sleep(2)

        applied, note = REMEDIES[finding['remedy']](finding['target'])
        if not applied:
            print(f'supervisor: STOPPING, the remedy refused: {note}')
            journal(f'## Stopped: {finding["name"]}\n\n{finding["evidence"]}\n\n'
                    f'The remedy refused to apply: {note}')
            commit('Supervisor stopped: remedy refused')
            return 4

        ok, err = compile_model()
        if not ok:
            print('supervisor: STOPPING, an automatic edit did not compile')
            journal(f'## Stopped: an automatic edit did not compile\n\n{err}')
            commit('Supervisor stopped: edit did not compile')
            return 5

        restarts += 1
        journal(f'## Intervention {restarts}: {finding["name"]}\n\n'
                f'**Seen.** {finding["evidence"]}\n\n**Done.** {note}\n\n'
                f'Recompiled and restarted.')
        commit(f'Supervisor intervention {restarts}: {note}')
        print(f'supervisor: {finding["name"]} -> {note}; restarting')
        proc = launch()


if __name__ == '__main__':
    sys.exit(main())
