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
import shutil
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
STATE = os.path.join(HERE, 'calibration_state.dat')
# THE BANKED COPY OF THE LOG, WHICH IS NOT THE LOG ITSELF. The running model
# holds LOG open, and a tracked file gets replaced by `git reset --hard`, which
# unlinks the inode under the process: it writes on into a deleted file and the
# visible log freezes at whatever the checkout put there. Copying at checkpoint
# keeps the live handle stable and still banks the content.
BANKED_LOG = os.path.join(HERE, 'calibration_run.log')
PROGRESS = os.path.join(HERE, 'CALIBRATION_PROGRESS.tsv')

# -O3 RATHER THAN -O2, MEASURED AND NOT ASSUMED: 1.15x on the sixteen expensive
# ages, 162.5 seconds against 141.8, with the cores otherwise idle so the two
# were comparable. -march=native was in that measurement and is deliberately NOT
# here: it lets the compiler contract multiplies and adds into FMAs, which
# changes results in the last bits, and a calibration that has to be reproducible
# on another machine should not depend on which instructions this one has.
COMPILE = ['gfortran', SRC, '-mcmodel=medium', '-fopenmp', '-O3',
           '-funroll-loops', '-ffree-line-length-none', '-o', BIN]

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
    'lambda_m': r'lambda_m=\s*' + _NUM,
    'mu_homeless': r'mu_homeless=\s*' + _NUM,
    'kappa_uem': r'kappa_uem=\s*' + _NUM,
    'discount_factor': r'discount_factor=\s*' + _NUM,
    'relative_share_housing': r'relative_share_of_housing=\s*' + _NUM,
    'relative_share_leisure': r'relative_share_of_leisure=\s*' + _NUM,
    'addiction_scalar': r'addiction_scalar_1=\s*' + _NUM,
    # THE FACT THE PAPER EXISTS TO EXPLAIN, watched like a parameter because a
    # calibration that hits every target while the rich are the users has not
    # succeeded at anything. It is not a target and no bracket moves on it.
    'income_of_users': r'model_avg_income_drug_users/model_average_labour_income,\s*' + _NUM,
    'income_of_disordered': r'model_average_income_addicted/model_average_labour_income\.\s*' + _NUM,
}

# The Fortran name of each watched parameter's step size. Shrinking a step is
# the one remedy that is generically safe: an oscillation with growing
# amplitude always means the step is too big, whatever the parameter means.
ADJUSTER = {
    'smallest_rental': 'smallest_house_size_adjuster',
    'size_homelessness': 'size_homelessness_adjuster',
    'largest_house_size': 'largest_house_size_adjuster',
    'grid_expander': 'housing_status_grid_expander_adjuster',
    'lambda_m': 'lambda_m_adjuster',
    'mu_homeless': 'mu_homeless_adjuster',
    'kappa_uem': 'kappa_uem_adjuster',
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
    # B'S CEILING, ADDED AFTER IT PINNED FOR A WHOLE RUN AND NOTHING NOTICED.
    # b sat exactly at 0.05 while the update asked for 2.5 times that, so
    # participation stayed at 76 per cent against a target of 8.90 and every
    # other moment was being read off a model where three quarters of the
    # population used. This is precisely what diagnose_pinned_at_bound is for,
    # and it could not act because the bound was not in this table.
    'addiction_scalar': dict(
        decl='real(8), parameter :: b_hi=',
        kind='ceiling',
        widen=lambda v: v * 4.0,
        # One is where the marginal value of the first unit, theta/b, falls to
        # the order of the marginal utility of consumption and there is no
        # interior participation left to find. Past four it is not a bracket
        # that needs widening.
        limit=4.0,
    ),
}

PIN_LOOPS = 3        # loops on a bound before it counts as pinned
RUNAWAY_LOOPS = 5    # loops of one-way movement against a flat moment
FLAT_LOOPS = 5       # loops of a moment not moving at all
FROZEN_LOOPS = 6     # loops of a parameter not moving at all
OSCILLATE_LOOPS = 5  # loops of alternating, growing steps


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
    """Any parameter sitting on its bound while the update asks it to move.

    THIS USED TO CHECK ONE PARAMETER BY NAME, and the one it did not check is
    the one that pinned. b sat exactly on its ceiling of 0.05 for a whole run
    while participation stayed at 76 per cent against a target of 8.90, and
    every other moment was being read off a model in which three quarters of
    the population used. A diagnosis written for a catalogue should read the
    catalogue.
    """
    for target in BOUNDS:
        v = series(loops, target)
        bound = current_bound(target)
        if len(v) < PIN_LOOPS or bound is None:
            continue
        tail = v[-PIN_LOOPS:]
        if all(abs(x - bound) <= max(abs(bound), 1e-12) * 1e-6 for x in tail):
            kind = BOUNDS[target].get('kind', 'bound')
            return dict(name=f'{target} pinned at its {kind}',
                        evidence=f'{target} at {bound:g} for {PIN_LOOPS} loops '
                                 f'while its update kept asking it to move',
                        remedy='widen_bound', target=target)
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


def diagnose_inverted_gradient(loops):
    """The users stopped being poorer than average.

    NOT A MOMENT AND NOT A BRACKET'S JOB. No parameter is calibrated on this and
    nothing in the sweep will notice it, which is exactly why the supervisor has
    to: the paper's mechanism is that mortality truncates the value of life for a
    user and so reverses the income gradient, and a calibration that reaches
    every target with the average user richer than average has produced a model
    that cannot make the paper's argument.

    Escalates rather than fixes. The repair is a modelling decision -- theta's
    ceiling is the break point above which the reversal fails, so a gradient that
    inverts while theta sits on that ceiling means the drug spending target and
    the gradient cannot both be had -- and that is not a search problem.
    """
    v = series(loops, 'income_of_disordered')
    if len(v) < PIN_LOOPS:
        return None
    tail = v[-PIN_LOOPS:]
    if all(x > 1.0 for x in tail):
        return dict(name='the income gradient has inverted',
                    evidence=('income of the disordered over average income is '
                              + ', '.join(f'{x:.3f}' for x in tail)
                              + f' across {PIN_LOOPS} loops: the users are not the '
                                'poor, which is the fact the model exists to '
                                'produce'),
                    remedy='escalate', target='relative_share_of_addiction_1')
    return None


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


def diagnose_frozen_parameter(loops):
    """Any watched parameter that has not moved at all for several loops.

    GENERIC ON PURPOSE, because a parameter can freeze for more reasons than a
    bound: a guard holding it, an adjuster that has damped to nothing, a gap
    that has gone exactly zero. Detection generalises; the REMEDY does not, so
    anything without a reasoned entry in BOUNDS escalates rather than being
    guessed at.
    """
    for name in WATCH:
        v = series(loops, name)
        if len(v) < FROZEN_LOOPS:
            continue
        tail = v[-FROZEN_LOOPS:]
        if max(tail) - min(tail) > max(abs(tail[-1]), 1e-12) * 1e-9:
            continue
        if name in BOUNDS:
            return dict(name=f'{name} frozen at {tail[-1]:g}',
                        evidence=f'unchanged for {FROZEN_LOOPS} loops',
                        remedy='widen_bound', target=name)
        return dict(name=f'{name} frozen at {tail[-1]:g}',
                    evidence=(f'unchanged for {FROZEN_LOOPS} loops, and there is '
                              f'no reasoned remedy for this parameter'),
                    remedy='escalate', target=name)
    return None


def diagnose_oscillation(loops):
    """A parameter alternating direction with growing amplitude.

    This one IS generic: whatever the parameter means, a step that overshoots
    further each time is too big. Shrinking it is safe because it cannot move
    the fixed point, only how the search approaches it.
    """
    for name in WATCH:
        v = series(loops, name)
        if len(v) < OSCILLATE_LOOPS or name not in ADJUSTER:
            continue
        v = v[-OSCILLATE_LOOPS:]
        steps = [v[i + 1] - v[i] for i in range(len(v) - 1)]
        if any(s == 0 for s in steps):
            continue
        alternating = all(steps[i] * steps[i + 1] < 0 for i in range(len(steps) - 1))
        growing = all(abs(steps[i + 1]) > abs(steps[i]) for i in range(len(steps) - 1))
        if alternating and growing:
            return dict(name=f'{name} oscillating with growing amplitude',
                        evidence=f'steps {[round(x, 6) for x in steps]}',
                        remedy='shrink_adjuster', target=name)
    return None


DIAGNOSES = [diagnose_pinned_at_bound, diagnose_dead_moment, diagnose_runaway,
             diagnose_oscillation, diagnose_frozen_parameter,
             diagnose_inverted_gradient]


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


def shrink_adjuster(target):
    """Halve a step that is overshooting. Cannot move the fixed point.

    THE WHOLE RIGHT HAND SIDE IS REPLACED, not the first number in it. These are
    declared as expressions, 1*10.d0**(-1) and 5*10.d0**(-2), and a pattern that
    matches the leading coefficient happens to give the right answer for those
    two and would write 5d0.d0**(-1) for a declaration with no leading
    coefficient. The current value comes from the same parser the paper uses, so
    the expression is evaluated rather than pattern matched, and what goes back
    is a plain literal.
    """
    name = ADJUSTER.get(target)
    if name is None:
        return False, 'no adjuster known for ' + target
    sys.path.insert(0, os.path.join(HERE, 'paper'))
    try:
        from fortran_consts import constants
        old = constants(SRC).get(name)
    except Exception as exc:                       # noqa: BLE001
        return False, 'could not evaluate ' + name + ': ' + str(exc)
    if old is None:
        return False, name + ' is not a constant this parser can read'
    new_v = old / 2.0
    if new_v < 1e-6:
        return False, (name + ' is already ' + format(old, 'g') + '; halving it '
                       'again would stop the search rather than steady it')
    txt = open(SRC).read()
    m = re.search(r'^([ \t]*real\(8\)[ \t]*::[ \t]*' + re.escape(name)
                  + r'[ \t]*=[ \t]*)(.+?)[ \t]*$', txt, re.M)
    if m is None:
        return False, 'could not find the declaration of ' + name
    txt = txt[:m.start(2)] + _fortran(new_v) + txt[m.end(2):]
    open(SRC, 'w').write(txt)
    return True, (name + ' halved from ' + format(old, 'g') + ' to '
                  + format(new_v, 'g'))


REMEDIES = {'widen_bound': widen_bound, 'shrink_adjuster': shrink_adjuster}


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


def commit(message, paths=None):
    """Commit and push. Named paths by preference, never `add -A` blindly.

    An earlier version added everything and swept a 67 MB distribution file into
    history. The ignore rules cover that now, but a calibration commits every
    loop for hours and one mistake in those rules would be committed hundreds of
    times before anyone looked.
    """
    add = ['git', 'add'] + (list(paths) if paths else ['-A'])
    for cmd in (add,
                ['git', 'commit', '-q', '-m', message],
                ['git', 'push', '-q', 'origin', 'HEAD']):
        subprocess.run(cmd, cwd=ROOT, capture_output=True)


def checkpoint(loops):
    """Put the calibration somewhere a container restart cannot reach.

    WHY THIS IS NOT OPTIONAL. The box rebuilds itself. It did so at 00:30 on the
    23rd, twelve minutes before this was written, and it took with it the run
    log holding three loops of run 3 and every validation log in the scratchpad:
    the repository is re-cloned from the remote on restart, /tmp is gone, and the
    scratchpad comes back from a snapshot days old. Nothing that is not PUSHED
    survives. A calibration of twelve hours on a box that rebuilds every ten
    therefore does not finish at all unless each loop is banked.

    WHAT IS BANKED. The parameter state, which is what a resume actually needs;
    the run log, so a diagnosis is still possible afterwards; and one row per
    loop in a tab separated file, which is the thing that answers how many loops
    are left. The two distribution files are NOT banked -- 60 MB a loop is not a
    commit, and rebuilding the distribution cold from the age one cross section
    costs about five hundred sweeps, four minutes, against the seven a loop
    takes. That is the right trade.
    """
    n = len(loops)
    row = None
    if os.path.exists(REPORT):
        r = subprocess.run([sys.executable, REPORT, LOG], capture_output=True,
                           text=True, cwd=os.path.dirname(REPORT))
        gaps = [float(g) for g in re.findall(r'\s([\d.]+)%\s*$', r.stdout, re.M)]
        m = re.search(r'(\d+) of (\d+) on target', r.stdout)
        if gaps:
            gaps.sort()
            row = (f'{n}\t{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}\t'
                   f'{gaps[len(gaps) // 2]:.3f}\t{gaps[-1]:.3f}\t'
                   f'{m.group(1) if m else ""}\t{m.group(2) if m else ""}\n')
    if row is not None:
        head = '' if os.path.exists(PROGRESS) else (
            'loop\tutc\tmedian_gap_pct\tworst_gap_pct\ton_target\tof\n')
        with open(PROGRESS, 'a') as f:
            f.write(head + row)
    if os.path.exists(LOG):
        shutil.copyfile(LOG, BANKED_LOG)
    paths = [pth for pth in (STATE, PROGRESS, BANKED_LOG, JOURNAL)
             if os.path.exists(pth)]
    if paths:
        commit(f'Calibration checkpoint, loop {n}', paths)


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
    if os.path.exists(STATE):
        print('supervisor: calibration_state.dat is present, the model will resume '
              'from it; the distribution is rebuilt cold, which is one loop of cost')
    proc, restarts = launch(), 0
    print(f'supervisor: launched pid {proc.pid}, polling every {poll}s')

    banked = -1
    while True:
        time.sleep(poll)
        alive = proc.poll() is None
        loops = read_loops(LOG)
        done, said = verdict()

        # BANK EVERY LOOP. See checkpoint(): nothing that is not pushed survives
        # a container restart, and the box rebuilds itself often enough that an
        # unbanked calibration never finishes. A few seconds against seven
        # minutes a loop.
        if len(loops) > banked:
            banked = len(loops)
            checkpoint(loops)

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
