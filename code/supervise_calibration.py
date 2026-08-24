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
import resource
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
# THE PARAMETER TRACE, APPEND ONLY AND ACROSS CONTAINERS. calibration_run.log is
# a copy of the CURRENT container's log and holds the two or three loops it
# lived for, so a stall spanning ten loops cannot be seen in it at all: the
# median gap sat at 52.6, 44.2, 47.8, 48.4, 46.5 across five loops and there was
# no way to ask which bracket had stopped moving. One row per loop, every
# watched parameter, surviving every rebuild.
PARAMS = os.path.join(HERE, 'CALIBRATION_PARAMS.tsv')
TABLE = os.path.join(HERE, 'CALIBRATION_TABLE.txt')
TABLE_HISTORY = os.path.join(HERE, 'CALIBRATION_TABLE_HISTORY.txt')
PROGRESS = os.path.join(HERE, 'CALIBRATION_PROGRESS.tsv')

# -O3 RATHER THAN -O2, MEASURED AND NOT ASSUMED: 1.15x on the sixteen expensive
# ages, 162.5 seconds against 141.8, with the cores otherwise idle so the two
# were comparable. -march=native was in that measurement and is deliberately NOT
# here: it lets the compiler contract multiplies and adds into FMAs, which
# changes results in the last bits, and a calibration that has to be reproducible
# on another machine should not depend on which instructions this one has.
# -g AND -fbacktrace COST NOTHING AND BUY THE ONLY THING A CRASH REPORT NEEDS.
# The model segfaulted three times in a row at the same point and the backtrace
# read "#0 0x1501b4023e59 in ???" for every frame, because the binary carried no
# debug information. -g does not disable any optimisation at -O3; it only keeps
# the line table, so the next crash names its own line instead of costing a
# morning of reading the file around it.
COMPILE = ['gfortran', SRC, '-mcmodel=medium', '-fopenmp', '-O3',
           '-funroll-loops', '-ffree-line-length-none', '-g', '-fbacktrace',
           '-o', BIN]

# ---------------------------------------------------------------------------
# WHAT A LOOP LOOKS LIKE IN THE LOG. The calibration prints loop_count= once a
# loop, so a loop is the text between two of those. A value is taken as the LAST
# occurrence inside the loop, because several are printed both before and after
# their update and it is the post-update value the next loop starts from.
LOOP_MARK = re.compile(r'^\s*loop_count=\s*(\d+)', re.M)

_NUM = r'([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)'

# Adding a parameter here is what makes it watched.
#
# EVERY PATTERN IS ANCHORED TO THE START OF ITS LINE, and that is not tidiness.
# The model prints "distance_relative_share_of_leisure=" right after
# "relative_share_of_leisure=", read_loops keeps the LAST match in a loop, and an
# unanchored name is a substring of its own distance line: six of the fourteen
# columns were reading the convergence distance rather than the parameter, which
# reads as a parameter falling smoothly to zero -- a runaway -- when what is
# actually happening is the bracket converging. lambda_m was worse still,
# matching a setup line from build_smi_onset and so reading the same number every
# loop, which reads as a frozen parameter. Anchor, then check with the audit at
# the foot of rebuild_params_trace.py, which fails loudly on an ambiguous name.
_A = r'(?m)^\s*'
WATCH = {
    'smallest_rental': _A + r'smallest_rental_relative_to_lowest_income=\s*' + _NUM,
    'size_homelessness': _A + r'size_homelessness=\s*' + _NUM,
    'largest_house_size': _A + r'largest_house_size=\s*' + _NUM,
    'grid_expander': _A + r'housing_status_grid_expander=\s*' + _NUM,
    'lambda_m': _A + r'lambda_m=\s*' + _NUM,
    'mu_homeless': _A + r'mu_homeless=\s*' + _NUM,
    'kappa_uem': _A + r'kappa_uem=\s*' + _NUM,
    'discount_factor': _A + r'discount_factor=\s*' + _NUM,
    'relative_share_housing': _A + r'relative_share_of_housing=\s*' + _NUM,
    'relative_share_leisure': _A + r'relative_share_of_leisure=\s*' + _NUM,
    'addiction_scalar': _A + r'addiction_scalar_1=\s*' + _NUM,
    # THE FACT THE PAPER EXISTS TO EXPLAIN, watched like a parameter because a
    # calibration that hits every target while the rich are the users has not
    # succeeded at anything. It is not a target and no bracket moves on it.
    #
    # AND THE TEST IS ONE, NOT ZERO. The users are not meant to be destitute:
    # Table 7 puts the average income of drug users at 0.74 of the average in
    # NSDUH 2024, against a benchmark model that produced 0.41 and was too poor
    # rather than not poor enough. A ratio drifting UP toward 0.74 is the model
    # getting closer to the data, not a gradient failing, and only a ratio above
    # one says the rich have become the users. Do not read a rise as a fault.
    'income_of_users': _A + r'model_avg_income_drug_users/model_average_labour_income,\s*' + _NUM,
    'income_of_disordered': _A + r'model_average_income_addicted/model_average_labour_income\.\s*' + _NUM,
    # Treatment take up is the moment furthest from its target, so this is the
    # parameter to watch when the run stalls.
    'utility_cost_treatment': _A + r'utility_cost_of_treatment=\s*' + _NUM,
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
    'homelessness': _A + r'model_fraction_homeless\(1\)=\s*' + _NUM,
}

# Parameters the model itself documents as able to sit on a bound, with the
# value they sit at. A parameter here is NOT frozen when it reads that value: it
# has arrived somewhere the model has a printed explanation for, and stopping a
# sixteen moment calibration over it would throw away the fifteen that are still
# moving.
#
# bar_tau^u is the only one so far. At a utility cost of zero treatment is free
# in utils and still costs the household its drug spending, because taking it
# forces abstention, so a take up of zero is not this bracket failing -- it says
# the BENEFIT side is too small, which is g, mu_H, pi_r and the abstention, and
# no value of bar_tau^u reaches the target. The model prints exactly that when
# it happens. It is reported, not treated as a fault.
DOCUMENTED_FLOOR = {'utility_cost_treatment': 0.0}

# A FLOOR THE MODEL COMPUTES RATHER THAN DECLARES, keyed by the sentence the
# model prints when it reaches it. lambda_m's floor comes from the SMI
# prevalence profile, so it is not a number that can be written above.
ANNOUNCED_FLOOR = {'lambda_m': 'lambda_m IS AT ITS FLOOR'}


def _log_text():
    try:
        with open(LOG, errors='ignore') as fh:
            return fh.read()[-2_000_000:]
    except OSError:
        return ''

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


def banked_loops():
    """Every loop of the whole run, from the trace that outlives the container.

    WHY EVERY DIAGNOSIS WAS BLIND. read_loops reads the CURRENT log, and the
    container rebuilds every half hour, so it never returned more than the two or
    three loops that container lived for. RUNAWAY_LOOPS is 5 and FROZEN_LOOPS is
    6: neither could ever be reached, and a parameter climbing one way for
    fourteen loops went unnoticed because no single log held fourteen loops.
    Reconstructed from the checkpoint commits afterwards, three pathologies were
    sitting there in plain sight.

    The trace is banked to git each loop, so it is the run's memory. The current
    log is appended to it because the trace lags by one checkpoint.

    ROWS ALTERNATE and that is expected. The model prints its moments and its
    new parameters on opposite sides of the loop_count line the log is split on,
    so a loop banked mid way lands as two rows, one carrying the income ratios
    and one the parameters. Read a column downwards and it is the right series
    either way: series() drops the rows a name is missing from.
    """
    rows = []
    if not os.path.exists(PARAMS):
        return rows
    with open(PARAMS) as f:
        head = f.readline().rstrip('\n').split('\t')
        for line in f:
            f_ = line.rstrip('\n').split('\t')
            rec = {}
            for k, v in zip(head, f_):
                if k in ('utc', 'loop') or not v:
                    continue
                try:
                    rec[k] = float(v)
                except ValueError:
                    pass
            if rec:
                rows.append(rec)
    return rows


# Drifts already written to the journal, so a three minute poll does not write
# the same paragraph twenty times an hour.
_NOTED = set()

# A parameter that has moved one way for this many loops, by this much in total,
# is drifting rather than converging.
DRIFT_LOOPS, DRIFT_SIZE = 8, 0.5


# WATCH shortens a few Fortran names; the report prints them in full.
REPORT_NAME = {
    'relative_share_housing': 'relative_share_of_housing',
    'relative_share_leisure': 'relative_share_of_leisure',
    'smallest_rental': 'smallest_house_size',
    'utility_cost_treatment': 'utility_cost_of_treatment',
    'grid_expander': 'housing_status_grid_expander',
    'addiction_scalar': 'relative_share_of_addiction_1',
}


def report_rows(text):
    """(parameter, gap in per cent) for each row of the report's table.

    COUNTING COLUMNS BROKE ONCE AND BROKE SILENTLY. Both readers of this table
    were written as `^(\\S+)\\s+\\S+\\s+\\S+\\s+([\\d.]+)%`, three fields and then the
    gap. A `value` column was added to the report and a `moment` column after
    it, and neither regex was touched: they matched NOTHING from that day on,
    so report_gaps returned an empty dict and note_drift wrote no journal row
    at all. Nothing failed, the supervisor simply stopped seeing gaps, which is
    the machinery that catches an adjuster moving too fast or too slow.

    So find the gap by what it IS -- the field ending in a per cent sign -- and
    the parameter by its position at the head of the line. A row with no per
    cent is a parameter with no scalar moment and has no gap to report.
    """
    out = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 2 or not parts[0][:1].isalpha():
            continue
        pct = [x for x in parts[1:] if x.endswith('%')]
        if not pct:
            continue
        try:
            out.append((parts[0], float(pct[-1].rstrip('%'))))
        except ValueError:
            continue
    return out


def report_gaps():
    """Each parameter's current gap in per cent, from the report itself."""
    if not os.path.exists(REPORT):
        return {}
    r = subprocess.run([sys.executable, REPORT, LOG], capture_output=True,
                       text=True, cwd=os.path.dirname(REPORT))
    out = {}
    # Rows are keyed on the moment, so one row can name two parameters.
    for name, gap in report_rows(r.stdout):
        for nm in name.split('+'):
            out[nm] = gap
    return out


def note_drift(loops):
    """Write one journal paragraph per parameter that is drifting, and no more.

    WHY THIS IS NOT A DIAGNOSIS. diagnose_runaway escalates, and escalating kills
    the run; it is also hard coded to size_homelessness and so could not see
    kappa_uem more than double over twenty loops while the employment rate given
    SMI sat between 0.43 and 0.54 against a target of 0.30. A parameter buying
    nothing with a sixty per cent move is worth a person's attention, but it is
    not worth throwing away the ten brackets that ARE converging, and whether to
    damp it or repair its pairing is a modelling call rather than a bound tweak.
    So this only records. The supervisor keeps running.
    """
    gaps = report_gaps()
    out = []
    for name in WATCH:
        v = series(loops, name)
        if len(v) < DRIFT_LOOPS or name in _NOTED:
            continue
        # Consecutive repeats collapsed: a checkpoint that lands inside a loop
        # records the loop again, and a zero step is neither up nor down.
        v = [x for i, x in enumerate(v) if i == 0 or x != v[i - 1]]
        if len(v) < DRIFT_LOOPS:
            continue
        # THE WHOLE ONE WAY RUN, not a fixed window. A drift that compounds
        # slowly clears no threshold inside eight loops and is obvious across
        # twenty five: kappa_uem gained 21 per cent over its last eight and 212
        # per cent over the run. So walk back while the sign holds and measure
        # the move over what that finds.
        i = len(v) - 1
        sign = 1 if v[-1] > v[-2] else -1
        while i > 0 and (v[i] - v[i - 1]) * sign > 0:
            i -= 1
        run, base = v[i:], max(abs(v[i]), 1e-12)
        if len(run) >= DRIFT_LOOPS and abs(run[-1] - run[0]) / base >= DRIFT_SIZE:
            _NOTED.add(name)
            g = gaps.get(REPORT_NAME.get(name, name))
            # THE MOVE ALONE SAYS NOTHING. A bracket walking one way for twenty
            # loops is what convergence looks like: the leisure share went 3.50
            # to 0.57 doing exactly that and its moment is now within ten per
            # cent. What separates a drift from a bracket doing its job is
            # whether the moment came with it, so the gap is printed beside the
            # move and a paragraph without one says so rather than implying a
            # fault.
            where = ('its moment is not reported as a scalar' if g is None
                     else f'its moment is {g:.1f} per cent off')
            out.append(f'- `{name}` moved {run[0]:.4g} to {run[-1]:.4g}, one way '
                       f'across {len(run)} loops, and {where}')
    if out:
        journal('## Parameters drifting one way\n\n'
                'Recorded, not acted on: damping a drift or repairing a moment '
                'pairing is a modelling call, and escalating would kill a run '
                'whose other brackets are converging.\n\n' + '\n'.join(out))
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
                    # RECORD, DO NOT STOP, WHILE THE AUTHOR IS WORKING ON THE
                    # COMPOSITION MOMENTS FIRST. This alarm is correct and it
                    # fired correctly: the users are richer than average, which
                    # the model exists to rule out. It was reported, and the
                    # decision taken was to hit the SUD rate, the participation
                    # rate and the employed share of the homeless before touching
                    # the reversal, and to leave the SUD death multiplier alone
                    # while doing it. Stopping the run every three loops makes
                    # that impossible. The alarm still writes its evidence to the
                    # journal every time it fires, so nothing is hidden; put
                    # 'escalate' back when the gradient is the thing being worked
                    # on.
                    remedy='journal', target='relative_share_of_addiction_1')
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
        # HELD BY DESIGN IS NOT FROZEN. Checked before anything else, because a
        # parameter with a zero adjuster has no bracket to be stuck in.
        if name in _HELD or REPORT_NAME.get(name, name) in _HELD:
            continue

        floor = DOCUMENTED_FLOOR.get(name)
        if floor is not None and abs(tail[-1] - floor) <= 1e-12:
            continue

        # A FLOOR THE MODEL COMPUTES AND ANNOUNCES IS A DOCUMENTED FLOOR TOO.
        # DOCUMENTED_FLOOR above holds constants, and lambda_m's floor is not a
        # constant: it is implied by the SMI prevalence profile, below which the
        # onset identity has no non negative solution, so it moves with the
        # profile and cannot be written here. The model says so in as many words
        # when it gets there --
        #
        #   lambda_m IS AT ITS FLOOR ... the profile cannot deliver this moment:
        #   the prevalence path, the onset identity and this target are not
        #   mutually consistent.
        #
        # -- and a parameter resting on a bound the model has already explained
        # is not a frozen bracket. Killing the run over it destroys the work in
        # flight and tells no one anything the log did not already say.
        if ANNOUNCED_FLOOR.get(name) and ANNOUNCED_FLOOR[name] in _log_text():
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



def merge_to_main(root):
    """Fast forward main onto this branch WITHOUT touching the working tree.

    CHECKING MAIN OUT AND BACK CHURNS FILES UNDER A RUNNING DRIVER, and it cost
    a measured point. B_SWEEP.tsv was reverted mid sweep to a version without
    the row just banked, done_points stopped seeing b = 0.05 as done, and the
    driver spent another eighteen minutes measuring it a second time. Two
    processes doing checkouts in one worktree is the whole problem.

    `git push origin HEAD:main` moves the remote ref and never switches the
    tree. It fast forwards when main is an ancestor of HEAD, which it is
    whenever the branch has already been pushed, and refuses rather than
    forcing when it is not. Failure is reported and not raised: the branch push
    has already succeeded and that is what a resume reads.
    """
    for wait in (0, 2, 4, 8):
        if wait:
            time.sleep(wait)
        r = subprocess.run(['git', 'push', '-q', 'origin', 'HEAD:main'],
                           cwd=root, capture_output=True, text=True)
        if r.returncode == 0:
            return
    print('main push failed; the branch is pushed and a resume reads that',
          flush=True)
def commit(message, paths=None):
    """Commit and push. Named paths by preference, never `add -A` blindly.

    An earlier version added everything and swept a 67 MB distribution file into
    history. The ignore rules cover that now, but a calibration commits every
    loop for hours and one mistake in those rules would be committed hundreds of
    times before anyone looked.
    """
    add = ['git', 'add'] + (list(paths) if paths else ['-A'])
    for cmd in (add, ['git', 'commit', '-q', '-m', message]):
        subprocess.run(cmd, cwd=ROOT, capture_output=True)

    # THE PUSH IS THE PART THAT MATTERS AND IT WAS FAILING SILENTLY. A commit
    # that is not pushed is not a checkpoint: the container rebuilds itself back
    # to a PINNED commit, so anything only in the local history goes with it.
    # The remote intermittently returns HTTP 403 through the proxy, and with
    # capture_output and no return code check a failed push looked exactly like
    # a successful one. The loop 33 checkpoint sat unpushed that way and would
    # have cost three loops of b's climb had a rebuild landed first.
    for attempt in range(4):
        r = subprocess.run(['git', 'push', '-q', 'origin', 'HEAD'],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode == 0:
            merge_to_main(ROOT)
            return
        time.sleep(2 ** attempt)
    print(f'supervisor: PUSH FAILED after four attempts, the checkpoint is local '
          f'only and a rebuild will lose it: {r.stderr.strip()[:200]}', flush=True)


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
        # BY NAME, NOT JUST BY NUMBER, so the median compares like with like.
        # omega's moment is only computed on some loops, so the row's moment
        # count alternates 16, 17, and its gap is large enough to move the
        # median on its own: the series read 60.3, 31.4, 40.8, 64.4, 30.6, which
        # is that alternation and not the calibration. It is excluded from the
        # median and reported in its own column.
        # THE WHOLE TABLE, EVERY LOOP, ON DISK AND IN GIT. The author has asked
        # for the full list each round -- every internally calibrated parameter
        # with its value, its moment, the model, the target and the gap -- and
        # asking for it by hand each time is how a round goes by without it.
        # The report accounts for every parameter with a target in the Fortran,
        # as a row or as a named exclusion, so a short table is a visible fact
        # rather than a silent omission.
        with open(TABLE, 'w') as f:
            f.write(f'loop {n}, {time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}\n\n')
            f.write(r.stdout)
        with open(TABLE_HISTORY, 'a') as f:
            f.write(f'\n===== loop {n}, '
                    f'{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())} =====\n')
            f.write(r.stdout)

        named = report_rows(r.stdout)
        omega = next((v for k, v in named if k == 'weight_on_child'), None)
        gaps = [v for k, v in named if k != 'weight_on_child']
        m = re.search(r'(\d+) of (\d+) on target', r.stdout)
        if gaps:
            gaps.sort()
            row = (f'{n}\t{time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}\t'
                   f'{gaps[len(gaps) // 2]:.3f}\t{gaps[-1]:.3f}\t'
                   f'{m.group(1) if m else ""}\t{m.group(2) if m else ""}\t'
                   f'{"" if omega is None else f"{omega:.1f}"}\n')
    if row is not None:
        # A CUMULATIVE INDEX, BECAUSE THE LOOP COUNTER RESETS. Every container
        # rebuild relaunches the run and the Fortran starts counting loops from
        # one again, so the file read 1,2,3,4,5,2 and the series it exists to
        # provide -- how fast the gaps close -- could not be read off it at all.
        # seq counts rows; cold marks the first row after a relaunch, whose
        # distribution was rebuilt from scratch and which is therefore not
        # comparable with the rows around it.
        exists = os.path.exists(PROGRESS)
        seq = 1
        if exists:
            with open(PROGRESS) as f:
                seq = max(1, sum(1 for _ in f))
        head = '' if exists else (
            'seq\tloop\tcold\tutc\tmedian_gap_pct\tworst_gap_pct\ton_target\tof'
            '\tomega_gap_pct\n')
        cold = 1 if n <= 1 else 0
        fields = row.rstrip('\n').split('\t')
        with open(PROGRESS, 'a') as f:
            f.write(head + '\t'.join([str(seq), fields[0], str(cold)]
                                     + fields[1:]) + '\n')
    if os.path.exists(LOG):
        shutil.copyfile(LOG, BANKED_LOG)
    # ONE ROW PER LOOP OF EVERY WATCHED PARAMETER, so a stall can be attributed.
    if loops:
        names = sorted(WATCH)
        last = loops[-1]
        if not os.path.exists(PARAMS):
            with open(PARAMS, 'w') as f:
                f.write('utc\tloop\t' + '\t'.join(names) + '\n')
        row = '\t'.join('' if k not in last else f'{last[k]:.6g}' for k in names)
        # A CHECKPOINT IS NOT A LOOP. Checkpoints run every three minutes and a
        # loop takes about seven, so appending unconditionally wrote the same
        # loop two or three times over. Repeats are not harmless: a drift is
        # detected on consecutive one way steps, and a repeated row inserts a
        # step of exactly zero, which is neither up nor down and breaks the run.
        prev = ''
        if os.path.exists(PARAMS):
            with open(PARAMS) as f:
                tail = f.readlines()
            if len(tail) > 1:
                prev = tail[-1].rstrip('\n').split('\t', 2)[-1]
        if row != prev:
            with open(PARAMS, 'a') as f:
                f.write(time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
                        + f'\t{n}\t' + row + '\n')

    paths = [pth for pth in (STATE, PROGRESS, PARAMS, BANKED_LOG, JOURNAL,
                             TABLE, TABLE_HISTORY)
             if os.path.exists(pth)]
    if paths:
        commit(f'Calibration checkpoint, loop {n}', paths)


def compile_model():
    r = subprocess.run(COMPILE, cwd=HERE, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or '')[-2000:]


def kill_strays():
    """Kill any hftf left over from a supervisor that is no longer here.

    A SECOND RUN IS NOT A SPARE, IT IS A CORRUPTION. Killing the supervisor does
    not kill the model: the child is reparented to init and keeps going, and it
    keeps writing calibration_state.dat and the distribution files that the
    replacement run reads and writes too. Two runs on a four core box also halve
    each other's speed. This happened on the 23rd -- an orphan ran for fifteen
    minutes beside its replacement -- and it happens by construction every time
    the container rebuilds, so the launch path clears them rather than the
    operator remembering to.

    Matched on the parent being init, so this can never reach a live sibling.
    """
    out = subprocess.run(['ps', '-eo', 'pid,ppid,args'], capture_output=True,
                         text=True).stdout
    for line in out.splitlines()[1:]:
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid, ppid, args = parts
        if args.strip().endswith('hftf') and ppid == '1':
            print(f'supervisor: killing orphaned model, pid {pid}')
            try:
                os.kill(int(pid), signal.SIGKILL)
            except (OSError, ValueError):
                pass


def _child_setup():
    """Own session, and an unlimited stack.

    THE STACK LIMIT USED TO BE INHERITED from whatever shell happened to start
    the supervisor, which meant the model ran with an unlimited stack when it
    was launched by hand after a `ulimit -s unlimited` and with 8 MB when
    anything else started it. The model puts large automatic arrays on the
    stack, so the second case is a segfault with no message that looks exactly
    like a modelling bug. Set it here, where it does not depend on the caller.
    """
    os.setsid()
    try:
        resource.setrlimit(resource.RLIMIT_STACK,
                           (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
    except (ValueError, OSError):
        pass


def launch():
    kill_strays()
    env = dict(os.environ, OMP_NUM_THREADS='4', OMP_STACKSIZE='512M',
               GFORTRAN_UNBUFFERED_ALL='1')
    f = open(LOG, 'a')
    f.write('\n===== supervisor launch =====\n')
    f.flush()
    return subprocess.Popen(['./hftf'], cwd=HERE, stdout=f,
                            stderr=subprocess.STDOUT, env=env,
                            preexec_fn=_child_setup)


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

    # A VERDICT READ OFF A NEARLY EMPTY LOG IS NOT A VERDICT. total is however
    # many parameters the report could SCORE, which depends on what the log
    # happens to contain; the number that are calibrated at all comes from the
    # Fortran and does not. On a log a few minutes old only one parameter had
    # printed its moment, it happened to be on target, and "1 of 1 on target"
    # declared the calibration converged and stopped a run that was nowhere
    # near it. Convergence needs most of the parameters to have reported.
    n = re.search(r'(\d+) parameters calibrated internally', r.stdout)
    known = int(n.group(1)) if n else 0
    if known and total < 0.8 * known:
        return False, (f'{hit} of {total} on target, but only {total} of {known} '
                       f'calibrated parameters have reported a moment yet')
    return hit == total and total > 0, f'{hit} of {total} on target'


def held_by_design():
    """Parameters whose adjuster is zero in the Fortran, so nothing moves them.

    A PARAMETER NOBODY IS MOVING IS NOT A FROZEN BRACKET. Every update in the
    sweep is guarded on its own adjuster, so a zero adjuster is the file saying
    "this one is set externally". h_3, the housing grid expander, is held that
    way on purpose, and diagnose_frozen_parameter read its constancy as a stall
    and killed a run over it. The declarations are where the fact lives; the
    parameter prints no distance to read it from.
    """
    try:
        src = open(SRC, errors='replace').read()
    except OSError:
        return set()
    src = re.sub(r'&\s*\n\s*', '', src)
    syms = {}
    for m in re.finditer(r'^\s*(?:integer|real\(8\))\s*,\s*parameter\s*::\s*(\w+)\s*=\s*([^!\n]+)',
                         src, re.M):
        try:
            syms[m.group(1)] = eval(m.group(2).replace('d0', 'e0').replace('D0', 'e0'),
                                    {'__builtins__': {}}, dict(syms))
        except Exception:
            pass
    out = set()
    for m in re.finditer(r'^\s*real\(8\)\s*(?:,\s*parameter\s*)?::\s*(\w+)_adjuster\s*=\s*([^!\n]+)',
                         src, re.M):
        try:
            if eval(m.group(2).replace('d0', 'e0').replace('D0', 'e0'),
                    {'__builtins__': {}}, dict(syms)) == 0:
                out.add(m.group(1))
        except Exception:
            pass
    return out


_noted = set()

# Computed once: the declarations do not change while the supervisor runs.
_HELD = held_by_design()


def already_running():
    """True if another supervisor is alive, so this one refuses to start.

    TWO SUPERVISORS IS TWO MODELS. Each relaunches its own on death and each
    writes calibration_state.dat, so they overwrite each other's checkpoints and
    halve each other's cores. It happened: a supervisor from an earlier launch
    survived a kill and sat for sixteen minutes with no model, about to start a
    second one beside the live run.

    Matched POSITIONALLY. `ps | grep supervise_calibration` matches the shell
    whose own command line contains the string, which is the trap this project
    has fallen into four times: argv[0] is a python and argv[1] is this script.
    """
    me = os.getpid()
    out = subprocess.run(['ps', '-eo', 'pid,args'], capture_output=True,
                         text=True).stdout
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 3:
            continue
        pid, argv0, argv1 = parts[0], parts[1], parts[2]
        if (int(pid) != me and 'python' in os.path.basename(argv0)
                and os.path.basename(argv1) == os.path.basename(__file__)):
            return int(pid)
    return None


def main():
    other = already_running()
    if other:
        print(f'supervisor: another supervisor is already running as pid {other}; '
              'refusing to start a second')
        return 0

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
        # THE WHOLE RUN, not this container's slice of it. See banked_loops.
        loops = banked_loops() + read_loops(LOG)
        done, said = verdict()

        # BANK EVERY LOOP. See checkpoint(): nothing that is not pushed survives
        # a container restart, and the box rebuilds itself often enough that an
        # unbanked calibration never finishes. A few seconds against seven
        # minutes a loop.
        here = read_loops(LOG)
        note_drift(loops)
        if len(loops) > banked:
            banked = len(loops)
            # checkpoint appends THIS container's latest loop, so it is handed
            # the current log's loops rather than the merged history.
            checkpoint(here or loops)

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

        # A FINDING THAT IS RECORDED RATHER THAN ACTED ON. Its evidence belongs
        # in the journal, but stopping the run on it would make the work chosen
        # next impossible. Journal it once per distinct piece of evidence, so a
        # poll every three minutes does not fill the file with the same
        # paragraph, and carry on.
        if finding['remedy'] == 'journal':
            print(f'supervisor: NOTED, {finding["name"]} (recorded, not acted on)')
            if finding['evidence'] not in _noted:
                _noted.add(finding['evidence'])
                journal(f'## Noted, not acted on: {finding["name"]}\n\n'
                        f'{finding["evidence"]}\n\n'
                        'Recorded rather than escalated: the decision taken was to '
                        'work on the composition moments first.')
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
