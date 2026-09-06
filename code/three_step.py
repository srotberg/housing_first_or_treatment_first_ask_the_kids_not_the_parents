#!/usr/bin/env python3
"""One iteration of the author's three-instrument fixed point.

    "H1 to homelessness rate, h2 to cost burdened renters and mass at bottom
    productivity to share of employed homeless."   -- 6 September

Reads the newest point that carries the author's configuration, computes a damped
log step for each of the three instruments against its own moment, and prints the
run_one_point.sh line for the next iterate. three_loop.sh runs it in a loop.

WHY A LOOP AND NOT ANOTHER BATCH. The author, 6 September: *"I think you need to
let my method run for a while and see if the model converges"*. Every round on
6 September moved one coordinate off a base chosen by hand that firing, so the
search never iterated -- it sampled. Twenty-eight points were spent that way and
the base moved five times. A fixed point needs the same map applied to its own
output, repeatedly, and that is all this does.

ONE INSTRUMENT, ONE MOMENT, NO CROSS TERMS. This is deliberately NOT the joint
Newton step that was tried at 18:40. That step solved exactly and then asked for
two instruments 10 and 43 times outside their clamps, because it trusted first
derivatives across a factor-of-ten move. A damped coordinate map cannot do that:
each instrument only ever chases its own moment, every step is bounded, and if the
three are genuinely coupled the loop stalls at a fixed point that SHOWS the
coupling rather than a step that hides it.

THE SIGNS ARE MEASURED, NOT ASSUMED, and two of the three are counter-intuitive
enough that guessing them wrong cost hours on 6 September:

  size_homelessness      -> h_1           +  smaller street, less homelessness
  smallest_rental...     -> h_2           +  cheaper rung, fewer cost burdened
  kkk_s_deviation_bottom -> emp_homeless  -  WIDER bottom pushes mass OFF the
                                             bottom node, so a HIGHER value LOWERS
                                             the employed share of the homeless

THE MASS INSTRUMENT TURNS AT ABOUT 2.2 and its floor here is set there rather than
at the Fortran clamp of 1.0. Measured: emp_homeless is 0.1000 at 3.35, 0.2434 at
2.20 and 0.0392 at 1.60. Below the turn the bottom node stops being a thin
always-homeless sliver and becomes a large low-productivity block whose own
unemployment dominates, so the moment reverses. A step that crosses 2.2 is not a
smaller step in the same direction; it is a different economy.
"""
import glob, hashlib, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _gate_tables():
    """OWN, BOUNDS and TARGETS, read out of next_batch.py by TEXT.

    Imported rather than parsed would be cleaner, but importing next_batch runs
    its module body, which builds the revision map and reads the whole archive --
    seconds per call inside a loop that runs every iteration. These three tables
    are plain literals, so they are read with a regex and nothing else executes.

    ONE SOURCE FOR WHO OWNS WHAT. next_batch's OWN map is the table the author has
    been editing all week; a second copy here would drift from it silently, which
    is exactly how emp_homeless ended up assigned to two different instruments in
    two different files this evening.
    """
    src = open(os.path.join(HERE, 'next_batch.py'), errors='replace').read()

    def block(name):
        m = re.search(r'^%s\s*=\s*\{(.*?)^\}' % name, src, re.S | re.M)
        return m.group(1) if m else ''

    own = dict(re.findall(r"^\s*'([a-z_0-9]+)':\s*'([a-z_0-9]+)'",
                          block('OWN'), re.M))
    bounds = {}
    for k, v in re.findall(r"^\s*'([a-z_0-9]+)':\s*\(([^)]*)\)",
                           block('BOUNDS'), re.M):
        try:
            lo, hi = [float(x) for x in v.split(',')[:2]]
            bounds[k] = (lo, hi)
        except ValueError:
            pass
    targets = {}
    for k, v in re.findall(r"^\s*'([a-z_0-9]+)':\s*([-\d.eE+]+)",
                           block('TARGET'), re.M):
        try:
            targets[k] = float(v)
        except ValueError:
            pass
    return own, bounds, targets


_OWN, _BOUNDS, _GATE_TARGETS = _gate_tables()


def _file_targets():
    """Every target the FORTRAN states, read off the newest point file.

    next_batch.py has no moment-keyed table of target VALUES -- it carries who
    owns what and the bounds, but the numbers themselves live in the Fortran's
    *_data constants and reach the outside world only through a solve. Every
    MOMENT line in a point file prints `target=` beside `model=`, so that is the
    one place the target is guaranteed to be the number the point was actually
    scored against rather than a copy that can drift from it.

    The first attempt at this read a `TARGET` block out of next_batch.py, which
    does not exist; it returned an empty dict and only the four hand-set
    overrides below survived, so nineteen instruments sat unstepped with no
    error printed. Reading it from the artefact the solve itself wrote is what
    makes that failure impossible: a moment with no target simply is not there.
    """
    for f in sorted(glob.glob(os.path.join(HERE, 'points', 'point_*.txt')),
                    key=os.path.getmtime, reverse=True):
        if '.FAILED' in f:
            continue
        src = open(f, errors='replace').read()
        t = {}
        for name, val in re.findall(
                r'MOMENT\s+(\S+)\s+.*?target=\s*([-\dEe.+]+)', src):
            try:
                t[name] = float(val)
            except ValueError:
                pass
        # THE BAND SHARES AND RATES ARE PRINTED AS "UNTARGETED ... observed=",
        # not as MOMENT ... target=, so the generic reader above cannot see them
        # and the two instruments that answer to them sat frozen reporting
        # "not in this point". next_batch parses them with these same two
        # patterns; this keeps the two files reading the archive the same way.
        #
        # h_share<n> is the share OF THE HOMELESS in age band n -- the shares sum
        # to one across the five bands. It is NOT the homelessness rate within a
        # band; that is h_age<n>, and confusing the two would point an instrument
        # at a quantity an order of magnitude away.
        for n, _m, ob in re.findall(
                r'UNTARGETED share of the homeless, band\s+(\d+)\s+model=\s*'
                r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', src):
            t.setdefault('h_share' + n, float(ob))
        for n, _m, ob in re.findall(
                r'UNTARGETED homelessness rate, band\s+(\d+)\s+model=\s*'
                r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', src):
            t.setdefault('h_age' + n, float(ob))
        if t:
            return t
    return {}


def _gate_targets():
    """Every scored target, with the author's own three overridden.

    h_1 is the ANNUAL figure of 6 September, not whatever the gate carries;
    pi_eu is the 4.9 per cent they moved it to the same evening.
    """
    t = dict(_GATE_TARGETS)
    t.update(_file_targets())
    t.update({'h_1': 0.01097, 'h_2': 0.101, 'emp_homeless': 0.46, 'pi_eu': 0.049})
    return t



# THE AUTHOR'S METHOD, APPLIED TO EVERY PARAMETER. Their instruction of
# 6 September: *"the model should now use my method to calibrate all the
# parameters as we specified to adjust them"*.
#
# The method is a damped coordinate map iterated on its own output -- one
# instrument per moment, no cross terms, every step bounded, slopes only from
# pairs that differ in a single coordinate. It was built for their four and it
# converged on them in six iterations. This applies the same map to the whole
# assignment.
#
# THE ASSIGNMENT AND THE TARGETS COME FROM next_batch, not from a second copy
# here. Keeping two lists of what owns what is how they drift apart, and the
# gate's OWN map is the one the author has been editing all week. Only the four
# they named are overridden below.
TARGETS = _gate_targets()

# instrument -> (moment, fallback slope, lo, hi, damping, max e-fold per step)
#
# The fallback slopes are the median controlled measurements of 6 September, used
# only until the loop has made a controlled pair of its own. The rung's was the
# shakiest of the three, measured over a range of +3.22 to +7.86, which is part of
# why it is now the most heavily damped.
#
# THE SPEEDS ARE PER INSTRUMENT, on the author's diagnosis of 6 September: *"You
# might be updating h2 too fast ... And the mass too slowly"*. Both halves are
# right and the trace shows why.
#
# THE RUNG WAS OSCILLATING, NOT CONVERGING. Its realised slope on the burden
# moment across six iterations was -0.98, -2.38, -5.08, +0.45, +3.73, -3.40 --
# it changes SIGN. That is not noise: the burden share is non-monotone in the
# rung, measured independently this afternoon, because a cheaper rung pulls
# households off the street into the cheapest unit and they arrive poor, so they
# arrive burdened. Stepping 20 to 35 per cent at a time on an instrument like
# that guarantees overshoot, and iteration 6 to 7 moved the burden +123 per cent
# in one step. It now moves at most 8 per cent per iteration.
#
# It is also stepped on its slope for h_1 (+2.06) while its slope on the BURDEN
# is far steeper, so a step sized for one moment was always going to overshoot
# the other. The small cap is what reconciles the two.
#
# THE MASS WAS TOO SLOW AND RAN OUT OF ROOM. It took four iterations to walk
# 3.35 -> 2.20 and hit its floor while emp_homeless fell 0.382 -> 0.000. Damping
# 0.55 on a slope of -2.65 is a small move per round, and the moment it chases
# was being dragged down faster than that by the other two. It now moves at full
# damping.
RULES = {
    # THE FLOOR IS 1e-5 ON THE AUTHOR'S INSTRUCTION, 6 September: *"lower the h1
    # lower bound to 0.00001, and yes, that is the direction"*. It sat at 1e-4 and
    # the instrument was PINNED THERE with h_1 still 20.6 per cent high, so the
    # only lever pointed at homelessness had nowhere to go.
    #
    # IT IS NOT INERT AT 1e-5, which is the thing worth checking before moving a
    # floor. The street's size is max(size_homelessness*(1+increase_homeless_size*5),
    # street_size_floor) with increase_homeless_size=0 and street_size_floor=1e-6,
    # so anything above 1e-6 passes through unclamped. The gate's own BOUNDS entry
    # already allowed 1e-6; this table was the only thing holding it at 1e-4.
    # THE CAP IS 0.25 E-FOLDS, cut from 0.60 at 22:30 after iteration 2 overshot.
    # The slope it steps on, +0.29, was measured from four pairs at street values
    # of 1e-4 AND ABOVE. The floor came down to 1e-5 an hour later and the very
    # first step went to 5.5e-5, where the REALISED slope is +0.87 -- three times
    # steeper. The step took the cap, cut the street 45 per cent, and drove h_1
    # 0.01323 -> 0.00787 through a target of 0.01097, with emp_homeless following
    # it 0.459 -> 0.228.
    #
    # THE CAP IS THE HONEST CONTROL HERE, not a corrected slope. The response is
    # local -- that is why this fit is documented as local -- and the loop CANNOT
    # re-measure it: slope() takes only pairs differing in one coordinate and each
    # iteration moves seven or more, so slopes refresh from one-coordinate arms
    # and nowhere else. Bounding the step bounds what a stale slope can cost;
    # replacing +0.29 with a number nothing measured would not.
    'size_homelessness':                        ('h_1',          +0.30, 1e-5, 0.20, 0.55, 0.25),
    'smallest_rental_relative_to_lowest_income': ('h_2',          +5.36, 5e-3, 0.40, 0.30, 0.08),
    # THE SECOND NODE'S LEVEL, NOT THE BOTTOM NODE'S MASS. The author,
    # 6 September: *"instead of choosing the bottom mass, fix it to 0.2% and
    # adjust the second productivity level"*, and *"If emp homeless is too low,
    # you lower the second productivity a bit"*.
    #
    # This fixes the defect that made the previous assignment stall.
    # kkk_s_deviation_bottom moves the bottom node's LEVEL AND ITS MASS TOGETHER
    # -- a poorer tail is necessarily a thinner one -- so it could not make the
    # node poor enough to be priced out without also making it too small to
    # supply 46 per cent of the homeless. The second node's level is a separate
    # coordinate and moves only the level.
    #
    # Under merge_from_node=2 this parameter sets the MERGED second and third
    # nodes, leaving the lowest alone, which is exactly the group the author
    # means. Lowering it prices those households out of the cheapest rental even
    # when they are working, and a working household on the street is the only
    # thing that raises the employed share.
    #
    # The sign is measured, not assumed: -2.66 over six controlled pairs, range
    # -4.15 to -1.56, from the threshold sweep of 18:20. LOWER level, HIGHER
    # employed share, which is what the author said.
    'bottom_productivity_level':                 ('emp_homeless', -2.66, 0.02, 1.20, 0.60, 0.25),
    # THE NO-WAGE-INCOME SHARE, added 6 September when the author moved its
    # target from 0.1393 to 0.049: *"Let the method run with the new unemployment
    # rate target"*. Without an instrument pointed at it the target change does
    # nothing -- the three-instrument loop would carry the old pool and simply
    # report a bigger gap.
    #
    # WHY IT MATTERS MORE THAN ITS OWN MOMENT. h_1 decomposes almost exactly into
    # the size of this pool times the homelessness rate inside it: 0.1406 x
    # 0.2951 = 0.0415 against a measured 0.0582. It is the only lever measured
    # all day that works through the population at risk rather than the price of
    # the street, so it is the only one that does not drag emp_homeless down as
    # it lowers h_1.
    #
    # The slope is measured over 112 controlled pairs: median +0.42, range +0.03
    # to +0.71. WELL BELOW ONE, so the moment is far less than proportional to
    # the parameter and the step has to be large -- which is why its cap is the
    # loosest of the four.
    'probability_becoming_unemployed':           ('pi_eu',        +0.42, 0.002, 0.50, 0.70, 0.70),
    # THE TWO AGE MOMENTS, 6 September, with the author's own directions.
    #
    #   *"newborn endowment should rise when young homelessness is too high"*
    #   *"ssi should decline for the bottom 2 productivities when homelessness
    #    share of the old is too low"*
    #
    # Both are NEGATIVE slopes and both signs are the AUTHOR'S, not a
    # measurement -- which is why the magnitude is a bare 1.0 and the speeds are
    # the slowest in the table. A slope of -1 says only "this moves that moment
    # the other way, roughly one for one"; the first controlled pair replaces it.
    # Arms are queued to supply exactly that.
    #
    # h_share1 and h_share5 are shares OF THE HOMELESS by age band, targets 0.26
    # and 0.075, summing to one across the five bands. They are not the
    # homelessness RATE within a band -- that is h_age<n>, an order of magnitude
    # smaller, and pointing an instrument at the wrong one of the two would be
    # invisible in the trace.
    #
    # SSI ALREADY ACTS ONLY AT THE BOTTOM without a model change: the benefit is
    # max(PIA(node), takeup*level) and PIA rises with the node, so the floor
    # binds on a bottom set and lowering it can only reach those households. The
    # count of nodes it reaches is endogenous rather than pinned at two; pinning
    # it would be a semantic change and is the author's call.
    'newborn_endowment_scale':                   ('h_share1',     -1.00, 0.0, 3.0, 0.35, 0.20),
    'ssi_floor_level':                           ('h_share5',     -1.00, 0.0, 0.30, 0.35, 0.20),
}

# THE BOTTOM NODE'S MASS IS FIXED AT 0.2 PER CENT, on the author's instruction.
# The source's own calibration of the instrument reads 3.00 -> 0.621 per cent,
# 3.25 -> 0.318, 3.50 -> 0.155, and log-interpolating those puts 0.200 per cent
# at 3.4113. Written into every iterate so it cannot drift.
FIXED = {'kkk_s_deviation_bottom': 3.4113}

# A PARAMETER AT ZERO CANNOT BE REACHED BY A PROPORTIONAL STEP. The step is
# value*exp(...), so zero times anything is zero and the instrument is frozen
# however large its gap. next_batch hits this too and says so rather than
# stepping; here the two instruments the author asked for on 6 September both
# start at zero, so saying so would freeze the thing they just asked for.
#
# The seed is a STARTING MAGNITUDE, not a calibrated value: one step of the
# ordinary rule replaces it as soon as a controlled pair exists. 0.10 is a tenth
# of average labour income, which is the unit newborn_endowment_scale multiplies.
# Anything else at zero is reported, not seeded, because inventing a magnitude
# for an instrument nobody asked about is how a base configuration drifts.
SEED = {'newborn_endowment_scale': 0.10}

# The author's configuration. A point is an iterate of THIS loop only if every one
# of these matches: delta zero, the street's 20 per cent penalty on, the second and
# third productivity nodes merged with the lowest left alone, and no endowment.
# The endowment is in this list because it was added without being asked for and
# then carried into four bases; pinning it here is what stops that recurring.
CONFIG = {
    'homeless_job_penalty_pp':    0.0,
    'increased_prob_if_homeless': 0.20,
    'merge_from_node':            2.0,
    'merge_bottom_nodes':         3.0,
}
# THE ENDOWMENT IS AN INSTRUMENT AGAIN, on the author's instruction of 6
# September: *"i think we need to add an endowment for the newborns so that
# their share of homelessness aligns with the data"*. It was pinned at zero in
# CONFIG because it had been added to four bases without being asked for; the
# author has now asked for it, so the pin comes off and it enters RULES from OWN
# like any other instrument.
#
# IT IS NOT DELIVERED TWICE, which the archive claimed and which would have
# doubled whatever gets calibrated. Checked at 22:35: with
# uniform_newborn_endowment=1 the branch at 25311 sets relative_endowments to
# ZERO, so max_initial_endowment multiplies zero and hands out nothing through
# the asset grid. The endowment arrives once, as newborn_age_transfer(1) in the
# first budget constraint.

# EVERY OTHER INSTRUMENT THE GATE OWNS, on the author's instruction to apply the
# method to all the parameters. The four above keep the hand-set speeds and
# measured slopes that made them converge; the rest are added from OWN with
# conservative defaults, because a slope guessed for twenty instruments at once
# is twenty chances to get a sign wrong.
#
# NO FALLBACK SLOPE. Where the four carry a measured number, these carry None,
# and an instrument with no CONTROLLED PAIR in the archive is skipped and says
# so rather than stepping on an invented elasticity. That is the whole reason
# the gate is running a seventeen-arm correction round right now: it generates
# exactly those pairs. The two halves fit together -- the round measures, the
# loop iterates.
#
# The bounds are the gate's own, so a step can never ask for a value the Fortran
# would silently clamp. Damping 0.45 and a cap of 0.35 are deliberately slower
# than the four: those were tuned against measured behaviour, these have not been.
#
# FIXED IS NOT AN INSTRUMENT. kkk_s_deviation_bottom is in the gate's OWN map --
# it used to own emp_homeless -- and the first version of this loop added it here
# and then stepped it, so the iterate written one line earlier at the author's
# 3.4113 came back out at 1.202 and the bottom node stopped being 0.2 per cent of
# the population. A parameter the author has pinned is skipped here, and the pin
# below is what writes it.
for _p, _m in sorted(_OWN.items()):
    if _p in RULES or _p in FIXED or _p in CONFIG or _p not in _BOUNDS:
        continue
    _lo, _hi = _BOUNDS[_p]
    RULES[_p] = (_m, None, _lo, _hi, 0.45, 0.35)


def model_hash():
    """The SEMANTIC hash, not a raw md5 of the file.

    A raw md5 moves when a COMMENT moves. On 6 September the homelessness target
    was rewritten with a long comment and the unemployment target after it, and
    each edit orphaned every point in the loop's archive -- three_step reported
    "no solved point carries the configuration yet" with forty iterates on disk,
    because it was comparing against a hash that documentation had changed.

    model_hash.semantic() strips comments and blank lines and blanks the VALUE of
    the constants in TARGET_CONSTANTS, which is what makes a target change
    hash-neutral for every other tool here. The loop must agree with them or it
    silently disagrees about which economy a point belongs to.
    """
    p = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
    return _mh_module().semantic(open(p, errors='replace').read())


_MH = None


def _mh_module():
    """model_hash, loaded ONCE.

    It was being re-imported per stamp, and importing it rebuilds a map over
    four hundred git revisions. With forty points that is forty rebuilds and the
    step never returned. One module, one map, cached resolutions.
    """
    global _MH
    if _MH is None:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            '_mh', os.path.join(HERE, 'model_hash.py'))
        _MH = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(_MH)
    return _MH


_RESOLVE_CACHE = {}


def _resolve(stamp):
    """A point's raw md5 stamp, mapped to the semantic hash of its economy."""
    if stamp not in _RESOLVE_CACHE:
        _RESOLVE_CACHE[stamp] = _mh_module().resolve(stamp)
    return _RESOLVE_CACHE[stamp]


def parse(path):
    s = open(path, errors='replace').read()
    m = re.search(r'^MODEL (\S+)', s, re.M)
    v = re.search(r'^VECTOR (.*)$', s, re.M)
    if not m or not v:
        return None
    vec = {}
    for tok in v.group(1).split():
        if '=' in tok:
            k, val = tok.split('=', 1)
            if re.fullmatch(r'[a-z_0-9]+', k):
                try:
                    vec[k] = float(val)
                except ValueError:
                    pass
    mom = {}
    for name, val in re.findall(r'MOMENT\s+(\S+)\s+.*?model=\s*([-\dEe.+]+)', s):
        try:
            mom[name] = float(val)
        except ValueError:
            pass
    # THE BAND SHARES AND RATES, read here as well as in _file_targets. Adding
    # them to TARGETS without adding them here stopped the loop dead at 22:37:
    # iterates() drops any point missing a target, every point was missing
    # h_share1, so nothing qualified, three_step returned 2 and three_loop
    # halted. The two readers must move together -- a target with no moment is
    # not a gap, it is an empty archive.
    for n, val, _ob in re.findall(
            r'UNTARGETED share of the homeless, band\s+(\d+)\s+model=\s*'
            r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', s):
        try:
            mom['h_share' + n] = float(val)
        except ValueError:
            pass
    for n, val, _ob in re.findall(
            r'UNTARGETED homelessness rate, band\s+(\d+)\s+model=\s*'
            r'([0-9.eE+-]+)\s+observed=\s*([0-9.eE+-]+)', s):
        try:
            mom['h_age' + n] = float(val)
        except ValueError:
            pass
    return m.group(1), vec, mom, os.path.getmtime(path)


def on_config(vec):
    return all(k in vec and abs(vec[k] - want) <= 1e-9 * max(abs(want), 1.0)
               for k, want in CONFIG.items())


LEDGER = os.path.join(HERE, 'three_step_iterates.txt')


def remember(vec):
    """Record a vector this loop asked for, so its solved point is recognisable.

    THE METHOD ITERATES ON ITS OWN OUTPUT. That is what makes it the author's
    method rather than a search: x_{n+1} = f(x_n), one instrument per moment,
    starting from where the last iteration landed.

    Matching an iterate by "newest point that carries CONFIG" does not express
    that, and it broke the moment the gate started its correction round: those
    arms carry CONFIG too -- they are one-coordinate variations off a base that
    shares it -- so the newest of them became the base. The iteration restarted
    from kkk_s_deviation_bottom=6 and size_homelessness at its floor, discarding
    the fixed point six iterations had reached, and nothing said so.

    So the loop writes down what it asked for and reads back only those. A point
    solved from anyone else's vector is still available for SLOPES -- controlled
    pairs are exactly what the correction round exists to produce -- it just
    cannot be the base.
    """
    with open(LEDGER, 'a') as f:
        f.write(' '.join(f'{k}={v:.10g}' for k, v in sorted(vec.items())) + '\n')


def _ledger():
    if not os.path.exists(LEDGER):
        return []
    out = []
    for line in open(LEDGER, errors='replace'):
        d = {}
        for tok in line.split():
            if '=' in tok:
                k, v = tok.split('=', 1)
                try:
                    d[k] = float(v)
                except ValueError:
                    pass
        if d:
            out.append(d)
    return out


def is_iterate(vec, ledger):
    """True if this point was solved from a vector THIS loop asked for.

    Compared numerically and only over the keys the loop named: run_one_point
    fills the rest from its defaults and the point echoes those too, so an exact
    string match would never fire. The emitted values are already rounded to %g,
    so 1e-5 relative is far looser than any real difference between two iterates.
    """
    for want in ledger:
        if all(k in vec and abs(vec[k] - v) <= 1e-5 * max(abs(v), 1e-9)
               for k, v in want.items()):
            return True
    return False


def iterates():
    """Every solved point that is an iterate of this loop, newest last."""
    h = model_hash()
    out = []
    for f in glob.glob(os.path.join(HERE, 'points', 'point_*.txt')):
        if '.FAILED' in f:
            continue
        p = parse(f)
        if not p:
            continue
        md, vec, mom, mt = p
        # A POINT IS STAMPED WITH THE RAW md5, so it has to be RESOLVED to a
        # semantic hash before it can be compared with one. model_hash.resolve()
        # maps a stamp through the revision table for exactly this. Comparing the
        # two directly matches nothing at all, which is what "no solved point
        # carries the configuration yet" meant with forty iterates on disk.
        if _resolve(md) != h or not on_config(vec):
            continue
        if not all(k in mom for k in TARGETS):
            continue
        if not all(k in vec for k in RULES):
            continue
        out.append((mt, os.path.basename(f)[6:16], vec, mom))
    out.sort()
    return out


def bases(pts):
    """The iterates of this loop, in order. Empty before the first step."""
    led = _ledger()
    if not led:
        return []
    return [r for r in pts if is_iterate(r[2], led)]


def slope(pts, param, moment, fallback):
    """Median slope from pairs of iterates differing ONLY in param.

    Falls back to the 6 September measurement when the loop has not yet produced
    a controlled pair of its own. Regressing across points that differ in several
    coordinates is what produced three wrong directions on 6 September, so it is
    not done here at all.
    """
    rows = []
    for i, (_, _, v1, m1) in enumerate(pts):
        for (_, _, v2, m2) in pts[i + 1:]:
            if v1[param] <= 0 or v2[param] <= 0 or v1[param] == v2[param]:
                continue
            if m1.get(moment, 0) <= 0 or m2.get(moment, 0) <= 0:
                continue
            if any(abs(v1[k] - v2.get(k, v1[k])) > 1e-9 * max(abs(v1[k]), 1.0)
                   for k in v1 if k != param):
                continue
            rows.append(math.log(m2[moment] / m1[moment]) /
                        math.log(v2[param] / v1[param]))
    if not rows:
        return fallback, 'fallback'
    rows.sort()
    return rows[len(rows) // 2], f'{len(rows)} pair(s)'


def main():
    pts = iterates()
    if not pts:
        print('# no solved point carries the configuration yet; seed first',
              file=sys.stderr)
        return 2
    # THE BASE IS THIS LOOP'S OWN LAST ITERATE, never merely the newest point
    # that happens to share the configuration -- see remember(). Before the first
    # step there is no ledger, so the newest configured point seeds it; after
    # that, a point solved from someone else's vector can supply slopes but not
    # the base.
    own = bases(pts)
    if own:
        _, tag, vec, mom = own[-1]
        print(f'# from point_{tag}   (iterate {len(own)} of this loop)',
              file=sys.stderr)
    else:
        _, tag, vec, mom = pts[-1]
        print(f'# from point_{tag}   (SEED: no iterate of this loop yet)',
              file=sys.stderr)
    nxt = dict(vec)

    for k, v in FIXED.items():
        if abs(vec.get(k, v) - v) > 1e-9:
            print(f'#   {k:<44}{vec[k]:10.5g} -> {v:10.5g}   held at the '
                  f'author\'s 0.2 per cent bottom node', file=sys.stderr)
        nxt[k] = v

    # THE RUNG SERVES h_1 WHILE h_1 IS FAR OFF. The author, 6 September: *"If h1
    # gets closer then we just lower h2 a bit more and sacrifice a bit on the h2
    # target"*. h2 there is the RUNG, the parameter; the h2 they are willing to
    # give up is the cost-burden MOMENT. The two share a name and confusing them
    # has already cost a concession once, so it is spelled out here.
    #
    # The rung moves h_1 with a measured slope of +2.06, seven times the street's
    # +0.30, so it is the stronger of the two instruments on the homelessness
    # rate -- it simply was not pointed at it. While h_1 is more than half again
    # its target the rung chases h_1; inside that it reverts to the cost burden.
    #
    # RIGHT NOW THIS COSTS NOTHING, and that is worth recording so the "sacrifice"
    # is not booked before it happens: the burden moment is 0.1534 against 0.101,
    # ABOVE target, and lowering the rung lowers both. The sacrifice begins only
    # when the rung has pushed the burden below 0.101, and the trace will show
    # exactly when that is.
    rung = 'smallest_rental_relative_to_lowest_income'
    h1_gap = abs(mom['h_1'] - TARGETS['h_1']) / TARGETS['h_1']
    serve_h1 = h1_gap > 0.50

    # emp_homeless AT ZERO IS A CORNER, AND A LOG STEP CANNOT LEAVE ONE. The
    # author, 6 September: *"You need to lower the mass of the bottom
    # productivity if all the homeless are unemployed"*. They are right, and the
    # model prints the reason:
    #
    #     DIAG cheapest rental over lowest net income = 0.2458
    #
    # At the seed that ratio was 1.64 -- the cheapest rental cost more than the
    # WHOLE net income of the lowest node, so its households were homeless even
    # with a job, and they were the employed homeless. The rung has since fallen
    # 0.130 -> 0.0397 and the ratio with it, so no employed household is priced
    # out anywhere and every homeless household is unemployed by construction.
    #
    # THE MEASURED SLOPE HAS THE WRONG SIGN FOR THIS REGIME. It was measured at a
    # ratio of 1.64, where the bottom node WAS priced out and its MASS set how
    # many always-homeless households there were, so more mass meant a higher
    # employed share. Below the affordability line the mass does nothing at all
    # and only the node's LEVEL relative to the rung matters. A slope is a local
    # object and this one was carried across a regime change.
    #
    # THE ESCAPE IS NOW THE SECOND NODE'S LEVEL, not the bottom node's tail. The
    # first version of this rule thinned the tail with kkk_s_deviation_bottom,
    # which does work -- the ratio climbed 0.25 -> 0.39 -> 0.52 in three rounds --
    # but it buys the affordability by making the bottom node smaller at the same
    # time, so the households it prices out get fewer as they get poorer. The
    # author's fix removes that trade: hold the bottom node at 0.2 per cent and
    # lower the SECOND node instead, which has mass to spare.
    #
    # So at the corner bottom_productivity_level steps DOWN by a fixed factor,
    # and keeps stepping until employed households are priced out and the moment
    # comes off zero, at which point the ordinary log step takes over.
    at_corner = mom.get('emp_homeless', 0.0) <= 0.0
    if at_corner:
        k = 'bottom_productivity_level'
        _, _, klo, khi, _, _ = RULES[k]
        nxt[k] = max(klo, min(khi, vec[k] * 0.85))
        print(f'#   {k:<44}{vec[k]:10.5g} -> {nxt[k]:10.5g}   '
              f'emp_homeless is 0: lowering the second node until working '
              f'households are priced out of the cheapest rental',
              file=sys.stderr)

    for param, (moment, fb, lo, hi, damp, efold) in RULES.items():
        if param == 'bottom_productivity_level' and at_corner:
            continue
        if param == rung and serve_h1:
            moment, fb = 'h_1', +2.06
        # A MISSING MOMENT IS A SKIP, NOT A CRASH. With twenty-three instruments
        # the loop now reaches moments a given point may not print -- a solve that
        # stops early, a moment behind an include_ flag -- and one KeyError here
        # would lose the whole iteration including the instruments that did have
        # their moment. Same for an instrument absent from the vector.
        if moment not in TARGETS or moment not in mom or param not in vec:
            print(f'#   {param:<44}{"":>10}   {moment}: not in this point, '
                  f'not stepping', file=sys.stderr)
            continue
        tgt = TARGETS[moment]
        if tgt == 0:
            print(f'#   {param}: target for {moment} is zero, a log step '
                  f'cannot reach it', file=sys.stderr)
            continue
        cur = mom[moment]
        e, src = slope(pts, param, moment, fb)
        if e is None:
            print(f'#   {param:<44}{vec[param]:10.5g}   {moment} {cur:.5f} vs '
                  f'{tgt:.5f}, NO CONTROLLED PAIR YET -- not stepping',
                  file=sys.stderr)
            continue
        if cur <= 0 or abs(e) < 1e-6:
            print(f'#   {param}: {moment} is {cur:g}, cannot step on it',
                  file=sys.stderr)
            continue
        if vec[param] == 0.0:
            if param in SEED:
                nxt[param] = SEED[param]
                print(f'#   {param:<44}{0.0:10.5g} -> {SEED[param]:10.5g}   '
                      f'{moment} {cur:.5f} vs {tgt:.5f}, SEEDED off zero: a '
                      f'proportional step cannot leave it', file=sys.stderr)
            else:
                print(f'#   {param}: held at zero, a proportional step cannot '
                      f'leave it', file=sys.stderr)
            continue
        step = damp * math.log(tgt / cur) / e
        step = max(-efold, min(efold, step))
        new = max(lo, min(hi, vec[param] * math.exp(step)))
        at = '  AT BOUND' if new in (lo, hi) else ''
        print(f'#   {param:<44}{vec[param]:10.5g} -> {new:10.5g}   '
              f'{moment} {cur:.5f} vs {tgt:.5f}, slope {e:+.2f} ({src}){at}',
              file=sys.stderr)
        nxt[param] = new
    emit = {k: float(f'{v:g}') for k, v in nxt.items()}
    remember(emit)
    print('bash code/run_one_point.sh ' +
          ' '.join(f'{k}={v:g}' for k, v in sorted(emit.items())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
