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
import glob, hashlib, json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))


# MOMENTS THE FORTRAN PRINTS AS "UNTARGETED ... observed=" RATHER THAN
# "MOMENT ... target=". They are scored by the gate all the same, and a reader
# that only knows the MOMENT form is blind to them -- which is why sud_homeless
# reported "not in this point" while sitting at 0.035 against 0.217. The same
# patterns next_batch uses, so the two files read the archive identically.
_UNTARGETED_SINGLES = (
    (r'UNTARGETED SUD share of the homeless\s+model=\s*([0-9.eE+-]+)'
     r'\s+observed=\s*([0-9.eE+-]+)', 'sud_homeless'),
    (r'UNTARGETED renters above 50 pct of income\s+model=\s*([0-9.eE+-]+)'
     r'\s+observed=\s*([0-9.eE+-]+)', 'rent50'),
)


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
        for pat, nm in _UNTARGETED_SINGLES:
            mm = re.search(pat, src)
            if mm:
                t.setdefault(nm, float(mm.group(2)))
        if t:
            return t
    return {}


_PIT_OVERALL = None


def _pit_overall():
    """The point-in-time overall rate the HUD band rates are normalised on.

    Read from the Fortran rather than typed: it is the divisor the model itself
    uses at 6766 to turn val_hud_rate_1 into the observed PROFILE, so it is by
    construction the overall rate on the same basis as the five band rates.
    """
    global _PIT_OVERALL
    if _PIT_OVERALL is None:
        src = open(os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90'),
                   errors='replace').read()
        m = re.search(r'val_hud_rate_1\(k_1\)\s*/\s*([0-9.]+)d0', src)
        _PIT_OVERALL = float(m.group(1)) if m else 0.0
    return _PIT_OVERALL


def _annualise_age_rates(t):
    """Put the five HUD band rates on the model's ANNUAL basis.

    THE AUTHOR CHOSE THIS, 7 September, over holding the SSI floor or dropping
    the old band: *"Go with 2"* -- target the band RATE rather than the band
    SHARE.

    WHY THE SHARES COULD NOT WORK. The five shares sum to one, which the model's
    own invariant confirms, so they are not independent. Two instruments aimed at
    two components of a simplex fight by construction: newborn_endowment_scale
    drove h_share1 from 0.48 to 0.33 and every other band's share rose to absorb
    it, so ssi_floor_level read a 197 per cent gap on h_share5 that its own
    instrument had not caused. The instrument moved 13 per cent across eight
    iterations while the moment swung by a factor of 3.4. Rates carry no such
    constraint: each band's rate is its own homeless mass over its own
    population, and one band can move without touching another.

    THE RATES HAD TO BE RE-BASED FIRST. val_hud_rate_1 is HUD's POINT IN TIME
    count and the model's period is a YEAR, the same mismatch that moved h_1 from
    0.00399 to 0.01097 on 6 September. Comparing an annual model rate against a
    point-in-time observed one would have read every band as three to four times
    too homeless -- h_age1 showed +641 per cent in the gaps table for exactly
    this reason, and it was flagged as a basis artefact rather than a model
    failure.

    The re-basing preserves the PROFILE and fixes only the level: every band is
    scaled by the same factor, the annual overall over the point-in-time overall.
    That is the one number the two bases disagree on, and it is the same
    construction h_1 already uses. Nothing new is asserted about the age gradient
    -- the shape is HUD's, untouched.

    DONE HERE AND NOT IN THE FORTRAN, deliberately. val_hud_rate_1 is a
    multi-line array declaration, so it cannot be blanked by TARGET_CONSTANTS the
    way a scalar target can, and editing it would change the semantic hash and
    orphan all 47 points on this economy -- including the loop's own base, which
    would stop it dead. The model still prints the point-in-time figure as its
    observed column; only the method's target is re-based.
    """
    pit = _pit_overall()
    ann = t.get('h_1')
    if not pit or not ann:
        return
    factor = ann / pit
    for k in range(1, 6):
        key = 'h_age%d' % k
        if key in t:
            t[key] = t[key] * factor


def _gate_targets():
    """Every scored target, with the author's own three overridden.

    h_1 is the ANNUAL figure of 6 September, not whatever the gate carries;
    pi_eu is the 4.9 per cent they moved it to the same evening.
    """
    t = dict(_GATE_TARGETS)
    t.update(_file_targets())
    # beta at 3.0, on the author's instruction of 7 September: *"i think maybe we
    # need it to hit a ratio of 4"*, corrected in the next message to *"of 3"*.
    #
    # OVERRIDDEN HERE AND NOT ONLY IN THE FORTRAN, because _file_targets reads
    # the NEWEST POINT and every point in the archive was measured against 2.25.
    # Without this the first step after the retarget would drive the discount
    # factor at the old number and only the second would see the new one. This
    # is the TARGET_OVERRIDE treatment ENGINE.md prescribes for exactly this.
    # h_1 at 1 per cent, on the author's instruction of 7 September: *"i think
    # h1 can target 1%"*, *"instead of 0.5%"*, after *"i think we can argue for
    # anything around 0.5-1%"*. fraction_homeless_data was changed in the Fortran
    # at the same time, but this override was still carrying 0.005 and silently
    # winning -- the points said 0.01 and the stepper chased 0.005.
    t.update({'h_1': 0.01160, 'h_2': 0.08, 'pi_eu': 0.049, 'beta': 3.0})
    # emp_homeless IS UNTARGETED, 7 September: *"and forget about targeting the
    # emp_homeless"*, *"let it be untargeted"*. Its only instrument moved it at
    # -0.0003 over 54 controlled pairs and has been pinned in the same round, so
    # scoring it would hold the ten per cent rule open on a moment with nothing
    # able to reach it. Dropped HERE rather than in the Fortran on purpose: the
    # write statement is not a comment and not a TARGET_CONSTANT, so editing it
    # would change the model hash and orphan every point in this economy.
    # next_batch.py's SKIP carries the same decision for the gate.
    t.pop('emp_homeless', None)
    if t.get('b'):
        t['sud_users'] = t['lambda_d'] / t['b']
    _annualise_age_rates(t)
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
    # THE LOWER BOUND WAS ARTIFICIAL AND WOULD HAVE BOUND BEFORE MORNING. h_1 is
    # the worst behaved moment with a live instrument -- +63 per cent and still
    # climbing, because the recovering drug block adds to the street faster than
    # the rung takes away -- and size_homelessness was moving its full half per
    # cent down every iteration from 3.72e-05. That is about 263 iterations from
    # 1e-05, roughly ten and a half hours, which is inside the night the author
    # asked for.
    #
    # 1e-05 was this file's own invention. next_batch.py has carried (1e-06,
    # 0.60) since the street was decoupled, and the FORTRAN's real floor is
    # street_size_floor=10.d0**(-6) at line 3245, applied at line 28039 as
    # housing_size(lowest) = max(size_homelessness*(1+increase_homeless_size*5),
    # street_size_floor) with increase_homeless_size=0.
    #
    # SET TO 2e-06, NOT 1e-06. At exactly the floor the max() takes over and the
    # parameter stops moving the street at all -- inert, in the way
    # sd_permanent_productivity was inert, and silently. Twice the floor keeps it
    # strictly live and still gives about 584 iterations of room.
    'size_homelessness':                        ('h_1',          +0.30, 2e-6, 0.20, 0.55, 0.25),
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
    # UPPER BOUND 1.0, NOT 1.2: the Fortran clamps this at
    # max(min(handover_value,1.d0),0.d0) at 37375, so a step past one was
    # silently truncated and the point that came back was not the point asked
    # for, with nothing in the trace to say so. Found in the bounds audit of
    # 23:30, on the author's instruction to check every parameter's range.
    # bottom_productivity_level IS PINNED AND emp_homeless IS UNTARGETED, on the
    # author's instruction of 7 September: *"i suggest to unpin the bottom
    # productivity level"*, corrected immediately to *"i mean to pin"*, then
    # *"and forget about targeting the emp_homeless"*, *"let it be untargeted"*,
    # and on where to put it, *"just let it be at the value it would be naturally
    # if we didnt actually touch it"*.
    #
    # IT WAS NOT MOVING ITS OWN MOMENT. Measured over 57 controlled pairs in the
    # archive -- points differing in this coordinate and nothing else:
    #
    #     d log emp_homeless / d log bottom_productivity_level = -0.0003  (n=54)
    #     d log h_1          / d log bottom_productivity_level = -0.0004  (n=57)
    #     d log w_bot        / d log bottom_productivity_level = +0.0014  (n=57)
    #     d log sigma_y      / d log bottom_productivity_level = +0.0002  (n=57)
    #     d log burden50     / d log bottom_productivity_level = -0.3903  (n=20)
    #
    # Four of the five are zero to three decimal places. It had stepped its full
    # half per cent every iteration through the night, 0.0668 up to 0.09695,
    # chasing emp_homeless from -1.9 per cent out to -19.6, and never touched it.
    # run_one_point.sh line 311 says why: "y_grid_kappa, bottom_productivity_level
    # and sd_permanent_productivity are inert under KKK", and every point runs
    # KKK. This is the second instrument tonight found pointing at nothing; the
    # first was sd_permanent_productivity on sigma_y.
    #
    # ZERO, NOT 0.0668. The Fortran declares it 0.d0 at line 3430 and says at 3417
    # that "bottom_productivity_level=0 LEAVES THE GRID ALONE"; line 29356 guards
    # the whole bottom-node override with if (bottom_productivity_level>0.d0), so
    # at zero the block does not run and the grid is whatever KKK produced. That
    # is what "naturally, if we didn't touch it" means. run_one_point.sh's own
    # default is 0.0668, so the zero has to be written into the vector explicitly,
    # which the pin below does on every iteration.
    #
    # THE EFFECT OF THIS IS NOT PREDICTABLE FROM THE ARCHIVE. Every one of the 57
    # controlled pairs has the parameter ABOVE zero, so they measure the margin
    # and not the switch. burden50, the one moment with a real elasticity, is
    # inside the band now and may well leave it.
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
    # THE DRUG BLOCK MOVES AT A THIRD SPEED. Both instruments step on slopes
    # four to five times too shallow, and both oscillated with period two for
    # four straight iterations: b went 0.065, 0.113, 0.074, 0.122, 0.068 and
    # lambda_d 0.029, 0.049, 0.033, 0.031. Realised responses were -8.96, -9.06,
    # -14.35, -9.47 against an assumed -2.32, and -13.30, -8.67 against -2.78.
    #
    # THOSE REALISED NUMBERS ARE NOT CONTROLLED and are not used as slopes. Seven
    # coordinates moved between each pair, and these two instruments in
    # particular cross-contaminate: onset and scale both feed b AND lambda_d, so
    # the one-instrument-one-moment approximation is at its weakest here. What
    # they establish is the SIGN of the error -- the step is far too big -- and
    # damping is the honest response to that, where substituting -9 for -2.32
    # would be reading a derivative off a diagonal move.
    'addiction_scalar_1':                        ('b',            -4.65, 1e-12, 1.0, 0.15, 0.20),
    # THREE MORE SIGNS THE AUTHOR SUPPLIED OR THE SOURCE SETTLES, 6 September.
    # All three were assigned to their moment already and frozen only for want of
    # a measured slope -- the method will not guess a direction -- so a sign is
    # exactly what unfreezes them. The magnitudes are a bare 1.0 and the speeds
    # are slow; the first controlled pair replaces them.
    #
    # kappa_uem. The author: *"shouldnt it go up if employment is too high?"*.
    # Yes, and the source settles it -- kappa_uem MULTIPLIES SEPARATION, so
    # raising it takes SMI households out of work and lowers the employment rate.
    # Its own declaration names the target: "Calibrated: employment rate given
    # SMI, 30 percent, the midpoint of the high disability range." At 0.633
    # against 0.300 this is the worst live gap in the table and nothing was
    # moving it.
    #
    # utility_cost_of_treatment. A utility COST of treatment can only lower
    # take-up, so tau_u above target means the cost is too low.
    #
    # multiple_of_probabilities_of_employment_if_addicted. POSITIVE, and the
    # first version of this line had it negative, inferred from the parameter's
    # NAME. The name is misleading and the source is not:
    #
    #     probability_becoming_unemployed_if_addicted = min(pi_eu * M, 1)
    #     probability_becoming_employed_if_addicted   = min(pi_ue / M, 1)
    #
    # M multiplies the probability of becoming UNEMPLOYED and DIVIDES the
    # probability of becoming employed, so raising it makes the addicted worse
    # off, poorer, and more likely homeless -- the SUD share OF THE HOMELESS
    # RISES. sud_homeless at 0.073 against 0.217 wants M HIGHER, and the wrong
    # sign had already driven it onto its floor of 1.0 in one step.
    #
    # This is what the no-guessed-slopes rule is for. A sign taken from a name
    # rather than from the code was wrong within one iteration.
    # UPPER BOUND 70, RAISED FROM 20 at 23:15. The 20 was set to keep
    # probability_becoming_unemployed * kappa_uem below the cap of one, at a pbu
    # of 0.041 where saturation sat at 24.4. The author's move of the
    # unemployment target to 4.9 per cent took pbu to 0.0128 and pushed
    # saturation out to 78, so the cap was guarding a limit that had moved: the
    # instrument pinned at 20 with employment given SMI at 0.543 against 0.300,
    # which needs about 55. The Fortran's own clamp is 100.
    #
    # SATURATION IS STILL THE THING TO WATCH. Above pbu*kappa_uem = 1 the SMI
    # separation rate pins at one and the instrument goes inert -- the trace
    # shows it stepping while the moment does not move. At 70 that happens if pbu
    # rises past 0.0143, which is close to where it is, so this bound is a
    # measurement decision that expires if the unemployment target moves again.
    # THE UPPER BOUND WAS THE ONLY THING HOLDING tau_u OUT, and it held it out
    # for the whole of the 7 September night run. The parameter sat at 8.0
    # printing AT BOUND every iteration while treatment take up read +84 per
    # cent and drifted further out. The author, 7 September: *"please adjust all
    # the parameters that are pinned at their bounds and prevent the model from
    # moving properly"*.
    #
    # CHECKED FIRST THAT IT IS NOT A DEAD LEVER, because that is exactly the
    # mistake sigma_y had just cost -- a bound was opened on an inert parameter
    # earlier the same evening and changed nothing. Four independent economies in
    # the archive agree that this one is strong and monotone:
    #
    #   211b867a51   u 6.99 -> 8.00   tau_u 0.659 -> 0.455   53 values, monotone
    #   0014027387   u 2.83 -> 11.0   tau_u 0.604 -> 0.0004
    #   ae7259b5bb   u 0.57 -> 2.86   tau_u 0.969 -> 0.030
    #   375aed92cf   u 2.18 -> 2.65   tau_u 0.704 -> 0.254   60 values
    #
    # The first of those brackets the value we are at, so the LOCAL elasticity is
    # about -2.5, not the -84.30 fallback below, which is a distance and not a
    # log slope. tau_u needs -0.611 in logs, so u needs about +28 per cent, near
    # 10.2. Twenty leaves room without being reachable in a night at the half per
    # cent cap.
    #
    # NOTHING IN THE FORTRAN CLAMPS IT. Line 289 is a plain
    # "real(8) :: utility_cost_of_treatment=0" with no max or min, and line 22349
    # is its only use, "flow_utility_1=flow_utility_1-utility_cost_of_treatment".
    # So the handover cannot silently truncate a value above 8, which is the risk
    # ENGINE.md warns about whenever a bound is raised.
    # -3.174, MEASURED ON A CONTROLLED PAIR, and the pair is the cleanest one
    # this loop has produced: point_90e331ce52 and point_e9df87e1e7 differ in
    # this coordinate and in nothing else.
    #
    #     u 10.000 -> 11.000   tau_u 0.29872 -> 0.21940   d log / d log = -3.174
    #
    # AND THE TARGET IS BRACKETED BY IT, 0.21940 < 0.24500 < 0.29872, which is
    # worth more than the slope: u = 10.624 is an interpolation inside a
    # measured interval rather than an extrapolation off a tangent.
    #
    # WHY -0.975 WAS WRONG, and it is not the usual reason. It was fitted over
    # 49 points and it was still meaningless, because the Fortran clamped this
    # parameter at 10 and forty of those points were solved at exactly 10 while
    # their handovers ranged up to 14.74. The fit was reading scatter across
    # points that shared an identical value of the regressor. A slope measured
    # over many points is not therefore a measured slope.
    'utility_cost_of_treatment':                 ('tau_u',         -3.174, 0.0, 20.0, 0.25, 0.20),
    # tau_l. NEGATIVE, on the author's instruction of 6 September: *"tau_l should
    # be lowered when the model is low relative to the data"*. The source agrees
    # and explains why a value of 0.79 yields an average tax of 0.21 --
    # net_income = labor_income_tax_rate * y**curvature, so the parameter is a
    # RETENTION scale, not a rate. Higher means more income kept and a LOWER
    # average tax.
    'labor_income_tax_rate':                     ('tau_l',        -7.40, 0.3, 0.95, 0.35, 0.20),
    # sigma_y. NEGATIVE, on the author's instruction of 6 September: *"sigma_y
    # should decline if the share of income at the bottom is too low. raising it
    # will reduce the share even more"*. sd_permanent_productivity is the
    # DISPERSION of the permanent draw, and more dispersion puts more distance
    # between the halves, so the bottom half's share of labour income falls. The
    # table had this backwards.
    # THE UPPER BOUND WAS BINDING AND sigma_y HAD NO WORKING INSTRUMENT. It sat at
    # 1.3, the ceiling, printing AT BOUND every iteration while sigma_y read +12
    # per cent and the stepper needed to raise it further to bring the share
    # down. Opened to 2.0 on the author's instruction: *"open the bound for
    # sigma_y"*. Nothing in the Fortran clamps this parameter -- it is a plain
    # declaration with no max or min -- so the handover cannot silently truncate
    # a value above 1.3, which is the risk ENGINE.md warns about when a bound is
    # raised.
    'sd_permanent_productivity':                 ('sigma_y',      -1.00, 0.6, 2.0, 0.35, 0.20),
    # THE LAST FIVE SIGNS, each read off the code rather than the parameter's
    # name. Four of the seven signs written from names on 6 September were wrong,
    # so every one of these was checked at its point of use:
    #
    #   kappa_find_smi   line 8372, find_1 = find_1 / kappa_find_smi. Higher means
    #                    SMI households find work LESS easily, so more of them end
    #                    up homeless and lambda_m RISES. Positive.
    #   smi_onset_level  line 36115, smi_onset_by_age = level * shape_by_age.
    #                    Higher onset, larger SMI population share. Positive.
    #   discount_factor  patience; more saving, higher wealth to output. Positive.
    #   mu_homeless      probability_of_stopping_addiction_if_homeless =
    #                    mu_homeless * 0.025, and mu_H is the HOUSED-to-homeless
    #                    recovery ratio, so mu_H goes as 1/mu_homeless. Negative
    #                    and close to unit elastic; the declared 4.48/6.60 is
    #                    Milby's raw ratio, and 1/0.679 is 1.473, which is the
    #                    target. Composition keeps it from being exactly -1.
    #   voucher          the probability an eligible household draws a voucher, so
    #                    the share of eligibles holding one rises with it. Positive.
    'kappa_find_smi':                            ('lambda_m',     +1.00, 1.0, 60.0, 0.35, 0.20),
    # THETA'S INSTRUMENT NEEDS A SIGN. The author, 7 September, on seeing it
    # frozen: *"it should move down towards the target"*. It could not: the
    # eight-node economy has no controlled pair for it, so it printed NO
    # CONTROLLED PAIR YET on every iteration where theta was off, and HOLDING on
    # every iteration where theta was inside five per cent. Twenty-two points
    # with the value unchanged at 0.248728.
    #
    # POSITIVE, and unambiguously so: it is the utility weight on the addiction
    # good, so a larger weight means households spend a larger share on it. theta
    # above target therefore wants the weight LOWER, which is what the author
    # said. The magnitude +1.92 is the single controlled pair measured on the
    # PREVIOUS economy -- carried as a prior for the sign and the order of
    # magnitude, and replaced as soon as this economy produces a pair of its own.
    # THE SUD MORTALITY MULTIPLIER IS A TARGET AGAIN, on the author's instruction
    # of 7 September once the history was traced: *"ah! ok, in that case allow
    # that to continue to be a target"*, *"but move it only very very slowly"*.
    #
    # It owns the income of drug users. That assignment is the one made on
    # 31 August -- "kappa_phi_d_level calibrated on the income of drug users" --
    # and reversed on 1 September; the 5.64 every vector has carried since is
    # what that calibration produced before it was cancelled.
    #
    # NEGATIVE, and next_batch's own note gives the mechanism: a stronger
    # deterrent to using leaves only the most desperate, who are the poorest, so
    # raising the multiplier LOWERS the income of drug users. y_u at 0.326
    # against 0.740 therefore wants it lower, which is exactly the direction the
    # cancelled calibration was moving it.
    #
    # VERY SLOWLY, at half a per cent a step against the two per cent everything
    # else gets, and damping 0.10 against 0.25. The reason is in the same note:
    # lowering it pushes the drug-price participation elasticity back up, and
    # that elasticity is an untargeted VALIDATION moment. This instrument spends
    # a validation result to buy a calibration target, so it should move only as
    # far as it must.
    #
    # It restarts from 8.0, the author's own value, not from the 5.64 it drifted
    # to unobserved.
    # THE DISORDER'S JOB-FINDING PENALTY, split off its separation penalty in the
    # Fortran on 7 September at the author's instruction: *"for Sud we might just
    # want to have the same thing"*, then *"Let's do the split now"*.
    #
    # POSITIVE, and the sign is the code's, not a name's: finding enters as
    # probability_becoming_employed / multiple_find_if_addicted, so raising it
    # makes work harder to regain, spells longer, wealth thinner, and more
    # households with the disorder end up on the street -- sud_homeless RISES.
    # The same shape as kappa_find_smi, which divides finding under SMI and
    # carries lambda_m.
    #
    # Bound 100, the Fortran's own handover clamp, matching kappa_find_smi's.
    #
    # THE SLOPE IS 5.00 AND IT IS A FLOOR, not a measurement, and the difference
    # is the point. +86.40 was a DISTANCE written in the pass that also produced
    # mu_homeless -32.40, newborn_endowment_scale -17.10 and
    # utility_cost_of_treatment -84.30; the first two have since been measured at
    # -1.00 and -0.37, so the defect is established and this is the last of the
    # four still carrying it. What is NOT established is what the true elasticity
    # is here. The loop's own trace over the current economy runs 23.165 -> 22.813
    # against sud_homeless 0.26789 -> 0.23971, which reads as an elasticity near
    # seven, but the moment's iteration-to-iteration scatter is +-2 per cent
    # against an instrument that moved 1.5 per cent in total, so that number is
    # not one to hand a step to.
    #
    # 5.00 is chosen so the GAP-SCALED CAP BINDS AND THE SLOPE DOES NOT. At the
    # 12.9 per cent gap the cap is 0.0225 x 0.121 = 0.27 per cent per iteration
    # and the slope asks for 0.59, so the step is the cap's and stays the cap's
    # for any slope below about 11. That is the safety: the step is governed by a
    # rule that shrinks with the gap rather than by a number I have not measured.
    # It is eight times the 0.034 per cent the fallback was taking, which needed
    # 140 iterations for a gap the cap closes in single figures.
    'multiple_find_if_addicted':                 ('sud_homeless',  +5.00, 1.0, 100.0, 0.25, 0.20),
    'smi_onset_level':                           ('p_m',          +1.00, 1e-08, 0.5, 0.35, 0.20),
    # +9.0, MEASURED, not assumed. It was +1.00, and that single wrong number
    # is why beta moved too much: across the 81bf69176d archive the discount
    # factor runs 0.90986 to 0.93907 and wealth over output runs 2.05 to 2.73,
    # which is d log(W/Y) / d log(beta) = +9.0 end to end. A stepper dividing by
    # 1.00 asks for a move nine times too large, gets clipped to the cap, and
    # lands on the far side of the target -- 0.90986 <-> 0.92824 for 148
    # iterations while W/Y straddled 2.25 at 2.04 and 2.57.
    #
    # THE DRUG BLOCK RODE ON IT. b flipped 0.003 <-> 0.19 in perfect antiphase,
    # 26 of 26 solves, because patience sets saving, saving sets current
    # consumption, and drug quantity is a share of consumption. b was never
    # discontinuous in its own instrument; it was bimodal in this one.
    'discount_factor':                           ('beta',         +9.00, 0.9, 1.02, 0.35, 0.10),
    # THE SLOPE IS -1.00 AND IT IS MEASURED, not assumed. The author, 7 September,
    # on being shown that the instrument works but steps a thirty-second of what
    # it should: *"sure"*.
    #
    #     d log mu_H / d log mu_homeless = -1.000 over 50 CONTROLLED PAIRS,
    #     range -4.03 to -1.00
    #
    # Unit elastic is also what the model says it must be: the recovery
    # probability if homeless is mu_homeless*0.025 and mu_H is the HOUSED-to-
    # homeless ratio, so mu_H goes as 1/mu_homeless exactly, and composition is
    # the only reason the pairs scatter above it.
    #
    # WHAT -32.40 WAS. A DISTANCE, not a log elasticity, written in the same pass
    # as multiple_find_if_addicted +86.40, newborn_endowment_scale -17.10 and
    # utility_cost_of_treatment -84.30. The step is damping x loggap / slope, so a
    # slope thirty-two times too large makes the step thirty-two times too small:
    # mu_H at -12.9 per cent needed about 40 iterations and needs about 13 now,
    # because the gap-scaled cap binds instead of the slope. The other three are
    # named here because they have the same defect and only this one has been
    # measured yet.
    'mu_homeless':                               ('mu_H',          -1.00, 0.0, 1.0, 0.35, 0.20),
    'probability_of_voucher_benchmark_used':     ('pi_V',         +1.00, 1e-05, 1.0, 0.35, 0.20),
    # THE SLOPE IS -0.37 AND IT IS MEASURED. h_1's target was pinned to where h_1
    # actually sat, which is what finally made this measurable: every earlier
    # reading of h_age1 was contaminated by the aggregate moving underneath it,
    # the error that was made three times and is now a standing check. Over the
    # twelve iterations from 0.74755 to 0.70310 the aggregate h_1 sat within half
    # a per cent of its target the whole way, so band 1 is answering to the
    # endowment and to nothing else:
    #
    #     d log h_age1 / d log newborn_endowment_scale = -0.371
    #     (0.01002 -> 0.01025 against 0.74755 -> 0.70310, h_1 flat throughout)
    #
    # THE SIGN IS RIGHT, which is the thing worth saying, because the sign was
    # what was in doubt: a smaller endowment does put more of the young on the
    # street. It is the SIZE that was wrong, by a factor of forty-six, -17.10
    # being a distance and not a log elasticity.
    #
    # It matters here because FAST caps this instrument at one per cent per
    # iteration on the author's instruction -- *"on the endowment just raise it to
    # 1%"* -- and with the slope forty-six times too large the step came out at
    # 0.54 per cent, so the cap never bound and the author's one per cent was not
    # what the loop was taking. With the measured slope the cap binds and the
    # instrument moves at the rate that was asked for.
    # -1.056, AND THIS ONE IS A REAL CONTROLLED PAIR. point_564ad3087b and
    # point_8ea4ed51ee differ in this coordinate and in nothing else --
    # 0.523362 -> 0.601866 -- which is what "controlled" has to mean.
    #
    #     d log h_age1 / d log newborn_endowment_scale = -1.056
    #     (0.014064 -> 0.012134)
    #
    # IT REPLACES A -0.37 THAT THIS COMMENT CALLED MEASURED AND THAT WAS NOT.
    # That number came from twelve consecutive loop iterations with the
    # AGGREGATE h_1 held near its target, and holding one other moment still is
    # not the same as holding the other coordinates still: kappa_find_smi,
    # utility_cost_of_treatment and six more were moving throughout. It was the
    # same error as the three sign errors before it, in a milder form -- reading
    # a derivative off a diagonal move -- and it was wrong by a factor of three
    # rather than in sign, which is exactly why it survived.
    #
    # THE ARM ALSO KILLED THE STORY ABOUT b. d log b / d log endowment is only
    # +0.129, so the endowment's 28.6 per cent fall accounts for about -3.6 per
    # cent of b against the -13.4 observed. The endowment is not what is pushing
    # b away from its target and the search for what is continues elsewhere.
    'newborn_endowment_scale':                   ('h_age1',       -1.056, 0.0, 3.0, 0.35, 0.20),
}

# THE BOTTOM NODE'S MASS IS FIXED AT 0.2 PER CENT, on the author's instruction.
# The source's own calibration of the instrument reads 3.00 -> 0.621 per cent,
# 3.25 -> 0.318, 3.50 -> 0.155, and log-interpolating those puts 0.200 per cent
# at 3.4113. Written into every iterate so it cannot drift.
FIXED = {'kkk_s_deviation_bottom': 3.4113,
         # PINNED, on the author's instruction of 7 September: *"i suggest to
         # pin theta to 0.27 and let my method run"*, after *"find a relative
         # share of addiction that is close to 14% and then pin it and not move
         # it. Because it affects b alot"*.
         #
         # IT AFFECTS b SIX TIMES HARDER THAN theta. Measured on one-coordinate
         # solves: d log theta / d log this = +1.73, d log b / d log this =
         # +11.14, against the +1.92 the rule assumed. Used as a theta
         # instrument it swung participation fifty fold overnight and took the
         # drug block to exactly zero, four moments with it.
         #
         # 0.248 gave theta 0.13297 at b 0.4023. theta falls with b -- the
         # author: *"if b gives you a higher share of users, they are richer,
         # which is why theta is high"* -- so the pin sits ABOVE 0.248, and
         # theta is then hit by construction rather than chased.
         'relative_share_of_addiction_1': 0.27,
         # HELD AT ZERO on the author's instruction of 6 September: *"i think for
         # now let's keep lambda_addiction=0 and only adjust the base"*. It is
         # written into every iterate rather than merely left unstepped, so a
         # base inherited from elsewhere cannot reintroduce it.
         'lambda_addiction': 0.0,
         # PINNED, on the author's instruction of 7 September: they asked to
         # *"calibrate the model first with lambdad=0 and just pick the base.
         # We know arithmetically what the base should be"*, and confirmed the
         # pin when it turned out the base was still being searched.
         #
         # IT IS ARITHMETIC, NOT A SEARCH. With lambda_addiction at zero the
         # onset hazard is flat in quantity, so every user faces the same
         # probability and the disorder share among users depends on the base
         # ALONE. Measured flat across the whole sweep band -- lambda_d/b read
         # 0.3365, 0.3524, 0.3510, 0.3549, 0.3565 at five values of
         # addiction_scalar_1 -- which is what a flat hazard implies and what a
         # dose-response one would not.
         #
         # 0.0428 comes from two points with different bases, corrected for the
         # ratio being SUBLINEAR in the base at an elasticity of 0.58 rather
         # than the 1.0 a naive scaling assumes. Both then agree:
         #   base 0.035291, lambda_d/b 0.3695  ->  0.042840
         #   base 0.044755, lambda_d/b 0.4241  ->  0.042841
         'addiction_onset_base': 0.0428,
         # PINNED, on the author's instruction of 7 September: *"so you pin
         # theta, and the base ... and lambda_d is 0 ... and let the rest run
         # through my method"*.
         #
         # IT IS ARITHMETIC, NOT A SEARCH. With lambda_addiction at zero the
         # onset hazard is flat in quantity, so every user faces the same
         # probability and the disorder share among users depends on the base
         # ALONE. Measured flat across the sweep band -- lambda_d/b read 0.3365,
         # 0.3524, 0.3510, 0.3549, 0.3565 at five values of addiction_scalar_1 --
         # which is what a flat hazard implies and a dose-response one would not.
         #
         # CLOSE, NOT EXACT, AND THE AUTHOR SAID WHY: *"the base is not exact
         # because it depends on the age and the mortality rates, but it can be
         # chosen to be close"*. That is visible in the measurement. Scaling the
         # base does not scale the ratio one for one; the elasticity is 0.58,
         # because the stock share among users is the flat hazard integrated
         # over the time a household spends using, which survival and the age
         # structure govern. Corrected for that, two points with quite different
         # bases agree to six figures:
         #   base 0.035291, lambda_d/b 0.3695  ->  0.042840
         #   base 0.044755, lambda_d/b 0.4241  ->  0.042841
         # THE SSI FLOOR IS NOT AN INSTRUMENT, on the author's judgement of
         # 7 September: *"Maybe best to leave the ssi as if was when homelessness
         # of the old was just low and untargeted. It was below 7.5% and around
         # 1%. I think maybe the ssi floor is not a good instrument"*.
         #
         # The measurement agrees with them. Across eight iterations the floor
         # moved 13 per cent while its moment swung by a factor of 3.4 -- first
         # as h_share5, which was a simplex artefact, and then as h_age5, which
         # is independent and still widened 197 -> 258 -> 281 -> 336 per cent
         # while the instrument stepped toward it. A lever whose moment moves
         # twenty-five times further than the lever, in whichever direction the
         # rest of the model happens to push, is not identifying anything.
         #
         # 0.1774 IS THE PROGRAMME'S OWN NUMBER, on the author's instruction of
         # 7 September: *"Maybe just set it the way the US system is..."*. It is
         # the 2024 SSI federal benefit rate of $943 a month as a share of the
         # average wage index, and it is the Fortran's declared default and
         # run_one_point's default alike. It sits with the rest of the actual US
         # structure -- the PIA bend points 0.2208 and 1.3314, the 90/32/15
         # replacement rates, the taxable maximum.
         #
         # IT WAS PINNED AT 0.13 FOR ONE COMMIT AND THAT NUMBER HAS NO
         # PROVENANCE. It was simply where the vector sat when this loop picked
         # the parameter up, left over from an earlier search that moved it as a
         # free instrument to buy the old-age share -- the state file still
         # carries "ssi_floor_level = 0.06 puts band 5 at -1.7 per cent" from
         # that period. Once it stopped being an instrument there was nothing
         # holding it at 0.13 but inertia, and a parameter the paper has to quote
         # cannot rest on that.
         #
         # THE COST IS BAND 5, KNOWINGLY. At 0.1774 the floor is 36 per cent more
         # generous than 0.13, so fewer old households are priced onto the
         # street and band 5 moves further from the 7.5 per cent in the data --
         # the gap the author has just accepted as untargeted.
         'ssi_floor_level': 0.1774,
         # SMI DOES NOT COST YOU YOUR JOB, IT COSTS YOU THE NEXT ONE. The author,
         # 7 September: *"maybe we should conceded the unemployment rate of those
         # with smi. And just leave it at the same rate as everyone else. And just
         # set the job finding rate to match the share of the homeless with smi"*.
         #
         # kappa_uem multiplies the SEPARATION rate under SMI, and at 1.0 an SMI
         # household loses its job at exactly the rate everyone else does. The
         # whole SMI labour penalty then runs through kappa_find_smi, which
         # divides the job-FINDING rate and is already pointed at lambda_m.
         #
         # IT COULD NOT REACH ITS TARGET ANYWAY. It sat at 70, its ceiling, with
         # employment given SMI at 0.522 against 0.300 -- a 74 per cent gap at the
         # top of its range, having been raised from 20 earlier in the night when
         # the old ceiling was found to have expired. Conceding it gives up
         # nothing that was achievable and stops an instrument grinding at a bound.
         #
         # The channel the author named on 6 September is the one that survives:
         # long spells drain wealth, and wealth depletion is what puts an SMI
         # household on the street.
         'kappa_uem': 1.0,
         # NINE, HELD, on the author's instruction of 7 September: *"hold
         # kappa_phi_d_level=9"*. It was the driver of the two-cycle that had
         # five moments hostage: it alternated between exactly 7.688 and 7.765 --
         # a one per cent spread -- in perfect antiphase with a fiftyfold swing
         # in b, while addiction_scalar_1 walked smoothly through. Chasing y_u
         # with it closed a loop, because y_u is really set by whether the drug
         # block is alive that iteration.
         #
         # EIGHT, which is the value the author set on 1 September and the
         # midpoint of Hjorthoj's six to ten. It is on the DETERRING side of the
         # threshold at the current scalar, so b starts collapsed and
         # addiction_scalar_1 -- now the only instrument on the drug block -- has
         # to walk it back. That is one lever on one margin instead of two
         # feeding each other.
         #
         # y_u loses its instrument again and goes untargeted.
         'kappa_phi_d_level': 8.0,
         # THE DISORDER DOES NOT COST YOU YOUR JOB EITHER, the same concession
         # the author made for SMI and for the same reason. At 1.0 a household
         # with the disorder loses its job at exactly the rate everyone else
         # does, and the whole labour penalty runs through
         # multiple_find_if_addicted, which divides job finding and carries
         # sud_homeless. Before the split this one parameter did both margins, so
         # the disorder's unemployment rate and its spell duration were one knob.
         'multiple_of_probabilities_of_employment_if_addicted': 1.0,
         # See the note where this left RULES: inert under KKK, measured at
         # -0.0003 on its own moment over 54 controlled pairs, and returned to
         # the value at which the Fortran leaves the employment grid alone.
         'bottom_productivity_level': 0.0}

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

# AN INSTRUMENT WHOSE MOMENT IS INSIDE THE BAND DOES NOT MOVE, on the author's
# instruction of 6 September: *"are you fixing the parameters that are within 10%
# of the target? you should only adjust the ones that are outside the band"*.
#
# Ten per cent is their stopping rule -- *"once we get below 10% for everything we
# can stop"* -- so an instrument already inside it has nothing left to buy, and
# every step it takes is pure disturbance to the moments it cross-affects. gamma
# was still being stepped at -2.0 per cent and cbar at +0.7, and each of those
# steps moved h_1 and emp_homeless underneath the instruments that were actually
# trying to hit them.
#
# It also damps the loop mechanically: fewer coordinates move per iteration, so
# the one-instrument-one-moment approximation -- which ignores every cross term --
# is asked to hold over a smaller step.
BAND_TOL = 0.10

# The author's configuration. A point is an iterate of THIS loop only if every one
# of these matches: delta zero, the street's 20 per cent penalty on, the second and
# third productivity nodes merged with the lowest left alone, and no endowment.
# The endowment is in this list because it was added without being asked for and
# then carried into four bases; pinning it here is what stops that recurring.
CONFIG = {
    'homeless_job_penalty_pp':    0.0,
    'increased_prob_if_homeless': 0.20,
    'merge_from_node':            2.0,
    # TWO FROM 7 September, not three. The arm at merge_bottom_nodes=2 took the
    # burden moment from +28 per cent to -2.6 for a 4 per cent cost in
    # homelessness: node 3's 19.4 per cent were being made poor enough to be
    # rent-burdened and not poor enough to be homeless, so the merge was paying
    # h_2 and buying nothing. Unmerged, bottom_productivity_level moved h_1 by 37
    # per cent and emp_homeless by 50 while h_2 stayed at 0.0983 -> 0.0985, which
    # is the decoupling the merged grid never gave.
    'merge_bottom_nodes':         2.0,
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
# ONE INSTRUMENT PER MOMENT. lambda_addiction and
# multiple_of_probabilities_of_employment_if_addicted BOTH own sud_homeless in
# the gate's map, and two instruments chasing one moment with no cross terms
# between them do not share the work -- they each take a full step for the whole
# gap and overshoot together.
#
# The employment multiplier keeps it. lambda_addiction is the dose-response slope
# in 1-exp(-lambda*quantity) and the source identifies it from the NSDUH SUD rate
# BY USE FREQUENCY -- 0.134, 0.428, 0.577, 0.717, 0.819 across the five
# categories -- so it is read from data, not fitted to a moment. It would also
# double-target drug prevalence, which addiction_onset_base already owns through
# lambda_d. The multiplier instead works through selection INTO homelessness
# among the addicted, which is what a share OF THE HOMELESS measures.
#
# SEPARATELY, AND FOR THE AUTHOR: the vector carries lambda_addiction=0 against a
# declared 0.027364, so 1-exp(-0*q) is zero and the dose-response channel the
# NSDUH gradient identifies is switched off entirely. That is a modelling
# question, not a calibration one, and it is not changed here.
HELD = {'lambda_addiction'}

# A FALLBACK OF None MEANS THE INSTRUMENT NEVER MOVES, and nobody chose that.
#
# The author, 7 September: *"i want cbar and aleph to be moving"*, *"who told
# you to freeze them? same with omega_l, and gamma?"*, *"who said they should be
# frozen?"*. Nobody did. It was an accident of this loop.
#
# An instrument added here got fallback None. slope() returns None when there is
# no controlled pair AND no fallback, and the stepper then skips the parameter
# and prints "NO CONTROLLED PAIR YET", which reads as a temporary state. It is
# permanent: the loop steps about fifteen coordinates every iteration, so a pair
# differing in exactly ONE of them is never produced. Measured over 136 points
# on this economy, max_food_cost, value_of_life, relative_share_of_housing and
# relative_share_of_leisure each had exactly one distinct value. Not one step in
# a whole day, while cbar sat at -69 per cent and aleph at -15.
#
# THE SLOPES BELOW ARE FROM THEORY, NOT MEASURED, and are marked so in the
# trace. Three of them are near certainties of arithmetic rather than guesses:
# aleph is the value of life over income and value_of_life scales its numerator,
# cbar is food stamps over income and max_food_cost caps the numerator, so both
# are +1 by construction. A higher taste for leisure means less labour supplied,
# so omega_l takes -1. gamma's 0.167 is the one real measurement available: it
# is the slope ENGINE.md records over 226 archived points, where Cobb-Douglas
# would give 1.0 and the discrete ladder saturates it.
#
# A WRONG MAGNITUDE CANNOT DO MUCH DAMAGE HERE, which is why this is safe to do
# without a sweep first: the half per cent cap bounds every step, and the
# sign-flip ratchet halves the gain the first time one of these overshoots. A
# wrong sign costs one iteration and then self-corrects.
_THEORY = {
    'value_of_life':             +1.00,   # aleph = VSL / income, direct
    'max_food_cost':             +1.00,   # cbar = food stamps / income, direct
    'relative_share_of_leisure': -1.00,   # more leisure weight, less labour
    'relative_share_of_housing': +0.167,  # ENGINE.md, measured over 226 points
}

for _p, _m in sorted(_OWN.items()):
    if _p in RULES or _p in FIXED or _p in CONFIG or _p in HELD or _p not in _BOUNDS:
        continue
    _lo, _hi = _BOUNDS[_p]
    RULES[_p] = (_m, _THEORY.get(_p), _lo, _hi, 0.45, 0.35)

# EVERYTHING MOVES SLOWLY, on the author's instruction of 7 September: *"Are you
# adjusting parameters slowly? They should move slowly"*.
#
# They were not. probability_becoming_unemployed could move 101 per cent in one
# iteration, six instruments 42 per cent, and most of the rest 22. A step that
# large breaks the one assumption this whole method rests on -- that the response
# is LOCAL, so a slope measured near the current point still describes the step
# being taken. Every failure tonight was that assumption breaking: the street's
# slope measured a decade away, the drug block's realised response four to six
# times its assumed one, the addiction multiplier onto its floor in a single
# step.
#
# So the cap is a tenth of an e-fold, about ten and a half per cent, and damping
# is a quarter. Applied as a ceiling rather than a rewrite, so anything already
# slower keeps its own number -- the rung stays at 0.08 and the discount factor
# at 0.10, both set against measured misbehaviour.
#
# THE COST IS ITERATIONS, NOT ACCURACY. A 68 per cent gap closed at ten per cent
# a step is about five iterations rather than two, which at four minutes a solve
# is twenty minutes. That is cheap against one runaway, which is what the drug
# block just cost.
# FOUR PER CENT, on the author's instruction of 7 September: *"I suggest smaller
# steps.... Let's say that a parameter should not move more than 3-5% between
# iterations"*. 0.04 e-folds is 4.08 per cent, the middle of the range they gave.
# It was 0.10 for one commit and that was still too loose for a method whose only
# assumption is locality.
# TWO PER CENT, on the author's instruction of 7 September: *"Maybe you need to
# reduce the steps of each parameter to 2% at most"*. It was four, and ten before
# that, and 101 before that.
# HALF A PER CENT, on the author's instruction of 7 September: *"you need to
# check that all parameters we update do not move more than 2% between
# iterations at most. i think even 0.5% is better"*, then *"maybe the most they
# should move is 0.5%"*. 0.005 e-folds is 0.501 per cent.
#
# IT IS A CEILING OVER EVERY RULE, applied by the min() below the table, so this
# one number binds all twenty-two instruments and a per-instrument cap can only
# be tighter than it, never looser.
#
# WHAT A CAP CANNOT DO, which is why it is not the whole fix: it bounds how far
# a mis-signed or mis-scaled step travels, not whether it repeats. An instrument
# whose gain is wrong by a factor of nine asks for a nine-times-too-large move
# every iteration and is clipped to the cap every iteration, which is a cycle at
# the cap rather than a convergence. discount_factor did exactly that for 148
# iterations at 2 per cent.
SLOW_DAMPING, SLOW_CAP = 0.25, 0.005

# THE SIGN-FLIP RATCHET, on the author's instruction of 7 September: *"sure add
# the halving"*.
#
# WHAT IT FIXES, which a step cap does not. A cap bounds how far a wrong-gain
# step travels; it cannot stop that step repeating in the opposite direction
# for ever. On 7 September eight instruments sat at the two per cent cap in
# antiphase for 150 iterations -- discount_factor alternating 0.90986 <-> 0.92824
# while beta straddled its target at 2.036 and 2.521, and b riding underneath it
# 0.003 <-> 0.19 -- because each one's assumed slope was one to two orders of
# magnitude too small and the cap merely set the amplitude of the cycle.
#
# THE MODEL ALREADY KNEW THIS. The Fortran's own stepper for discount_factor
# carries the same rule at discount_factor_damping=0.5 and its comment says why:
# *"Wealth over output is very sensitive to beta close to one, so a fixed step
# overshoots and then oscillates"*. That stepper is inert when a point is run --
# the handover pins every parameter, so calibrating_model never steps -- which
# is how the method outside it came to be the only updater and to be missing the
# ratchet. This restores it rather than inventing it, and the constants are the
# Fortran's own: halve on a flip, grow by 1.2 otherwise.
#
# A GAIN, NOT A CAP. The ratchet multiplies the damping, so an instrument that
# is converging keeps its full speed and only one that has just jumped over its
# target is slowed -- and only that one, because the state is per instrument.
# The floor is 1/500 of the ceiling, matching the Fortran's adjuster_floor
# against adjuster_start, so a ratcheted instrument slows without ever freezing.
# The step cap reaches its full value only at a gap of about 25 per cent;
# below that the ceiling is this fraction of the gap. See the step block.
GAP_SCALE = 0.0225

# A PER-INSTRUMENT STEP CEILING, on the author's instruction of 8 September:
# *"Maybe make the steps on tau_u larger. Maybe 3% per iteration"*.
#
# An entry here replaces BOTH limits for that instrument: the flat efold from
# RULES and the gap-scaled ceiling above. Both had to go to deliver three per
# cent. At tau_u's log gap of 0.3698 the gap-scaling alone allows
# 0.0225*0.3698 = 0.0083, so raising the flat cap by itself would have bought
# 0.83 per cent and no more, and the author would have been told three and given
# less than one.
#
# THE SLOPE HAD TO BE CORRECTED IN THE SAME BREATH or the ceiling is irrelevant.
# The step is damping*loggap/slope, and at the old -84.30 that is 0.25*0.3698/84.30
# = 0.0011, so the instrument was moving 0.11 per cent an iteration and would
# never have reached ANY ceiling. -84.30 is a DISTANCE, not a log elasticity;
# the measured value over 49 points on this economy is -0.975, which also makes
# economic sense as very nearly unit elastic. With both changed the raw step is
# 0.25*0.3698/0.975 = 0.0948 and the new ceiling binds at 0.03.
#
# WHAT IT BUYS: tau_u was 442 points and 15.5 hours from band and would have read
# about +35 per cent in the morning. At three per cent a step with a unit slope
# it closes 0.3698 in logs in about a dozen iterations.
#
# THIS IS FASTER THAN THE AUTHOR'S OWN HALF-PER-CENT RULE, deliberately and at
# their instruction. Do not add entries here without them.
# SLOWED FROM 3 PER CENT TO 1 ON THE AUTHOR'S INSTRUCTION OF 8 September 03:12:
# *"maybe slow down the 3% parameters to 1%?"*. Both still land before morning --
# utility_cost_of_treatment reaches its bound of 20 in about fifty iterations
# rather than seventeen, kappa_find_smi reaches the 40 lambda_m needs in about
# the same -- so the only thing three per cent was buying was arrival an hour
# earlier, against a real cost: two instruments moving fast together is what
# made b jump before, and neither of these slopes is measured.
FAST = {'utility_cost_of_treatment': 0.01,
        # kappa_find_smi ADDED 8 September 02:59: *"Maybe add 3% rate to the
        # endowment and lamdba m?"*. Safe because its SLOPE IS ALREADY RIGHT --
        # measured +0.890 over 49 points against the +1.00 fallback, so unlike
        # tau_u no slope correction is needed and only the ceiling was binding.
        # Raw step is 0.25*0.262/1.00 = 0.0655 against a 0.005 cap, so the
        # instrument was moving at a thirteenth of what it asked for. At three
        # per cent lambda_m's 0.262 log gap closes in about nine iterations.
        'kappa_find_smi': 0.01,
        # newborn_endowment_scale AT ONE PER CENT, not three, on the author's
        # instruction of 8 September 03:02: *"on the endowment just raise it to
        # 1%"*, after being shown that its sign is not established. Twice the
        # half per cent it had, a third of what the other two got. If the sign is
        # wrong h_age1 moves away at twice the old rate rather than six times,
        # which is recoverable inside an hour.
        'newborn_endowment_scale': 0.01}

# newborn_endowment_scale IS DELIBERATELY NOT HERE, though the author asked for
# it in the same breath. ITS SIGN IS NOT ESTABLISHED. The claim that it was
# backwards was made and RETRACTED at 02:08, and a retraction is not a
# confirmation: the own-effect on h_age1, after removing the aggregate, measured
# +0.296 over the full window and about -0.74 over the last four readings. At the
# half per cent step a wrong sign is slow and recoverable; at three per cent it
# drives h_age1 away six times faster, from an already -32.7 per cent.
#
# AND THE MEASUREMENT IS ABOUT TO BECOME POSSIBLE. h_age1's target is annualised
# off h_1's, and h_1's target moved FOUR times between 23:00 and 02:35, so every
# gap history for h_age1 tonight is contaminated by retargeting. h_1's target is
# now PINNED at 0.01160, so from 02:35 onward h_age1's target is fixed and the
# endowment's own effect can be read cleanly for the first time. Measure over the
# next hour, THEN add it here if the sign holds.

RATCHET_HALVE, RATCHET_GROW = 0.5, 1.2
RATCHET_FLOOR, RATCHET_CEIL = 0.002, 1.0
_GAIN_FILE = os.path.join(HERE, 'three_step_gain.json')


def _load_gain():
    try:
        with open(_GAIN_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_gain(g):
    try:
        with open(_GAIN_FILE, 'w') as fh:
            json.dump(g, fh, indent=1, sort_keys=True)
    except Exception:
        pass


# THE HOLD IS HYSTERETIC: an instrument stops at five per cent and does not start
# again until ten. The author, 7 September: *"maybe stop updating when the moment
# is within 5% and only start updating when it goes outside of 10%?"*.
#
# ONE THRESHOLD CHATTERS. With a single ten per cent rule an instrument that
# lands at 9.9 holds, drifts to 10.1 on somebody else's step, moves, lands at
# 9.8, holds again -- and every one of those moves disturbs the moments it cross
# affects, which is how a settled moment gets knocked out of band by an
# instrument that was itself almost on target. Two thresholds give it somewhere
# to rest: it must be properly wrong, not marginally wrong, before it moves.
#
# THE STATE HAS TO PERSIST, because the rule is about where a moment HAS BEEN,
# not only where it is. A moment sitting at seven per cent is held if it got
# there by converging from twelve, and stepped if it is on its way out from
# three. That history lives in three_step_active.json, next to the ledger.
# NO BANDS FROM 7 September, on the author's instruction: *"let all parameters
# move together without any bands"*. Every instrument steps every iteration,
# however small its gap.
#
# The hold was theirs too, earlier the same night, and it did what it was asked:
# it stopped instruments chattering on a single threshold. What it also did was
# freeze coordinates while the rest of the system moved underneath them, so a
# moment that was on target at one iteration was off at the next and its
# instrument had sat out the change. Moving everything together is a joint step
# in all coordinates rather than a sequence of frozen ones.
#
# Set to zero rather than deleted so the machinery and its state file survive and
# the hold can be restored by putting the two numbers back.
HOLD_ENTER, HOLD_EXIT = 0.0, 0.0
_ACTIVE_FILE = os.path.join(HERE, 'three_step_active.json')


def _load_active():
    try:
        with open(_ACTIVE_FILE) as fh:
            return json.load(fh)
    except Exception:
        return {}


def _save_active(a):
    try:
        tmp = _ACTIVE_FILE + '.tmp'
        with open(tmp, 'w') as fh:
            json.dump(a, fh, indent=0, sort_keys=True)
        os.replace(tmp, _ACTIVE_FILE)
    except Exception:
        pass
# WHICH PRODUCTIVITY PROCESS IS LIVE, AND THEREFORE WHICH INSTRUMENT sigma_y HAS.
#
# THIS LOOP SPENT AN ENTIRE RUN STEPPING A PARAMETER THAT DOES NOTHING. The
# author asked on 7 September whether sigma_y was moving towards its target at
# all. It was not. Over forty iterations sd_permanent_productivity rose 1.4158
# to 1.5881 -- its full half per cent every single iteration -- and the
# DIAG bottom half PRODUCTIVITY share went 0.214993 to 0.214997, flat to five
# decimal places, while the drug block swung sixty percentage points around it.
# The sigma_y gap widened from +13.52 to +14.23 per cent.
#
# run_one_point.sh sets [fixed_productivity]=0, so every point runs the author's
# KKK process, and it says outright at its line 311 that "y_grid_kappa,
# bottom_productivity_level and sd_permanent_productivity are inert under KKK".
# The dispersion under KKK is kkk_sigma_scale, which multiplies BOTH innovation
# sds at line 29006 of the Fortran.
#
# next_batch.py has had this right since 3 September, in
# _apply_process_mapping, and its comment names the exact failure that then
# happened here: "leaving the inert one mapped is worse than a conflict: the
# search would step a number that changes no moment and read the noise as a
# slope." This loop never got that mapping, and this loop is what runs.
#
# READ, NOT HARDCODED, for the same reason next_batch.py reads it: the process
# is a line in run_one_point.sh that every new point inherits, so it is the
# economy the search is actually stepping around, and pinning either instrument
# here would put this file back out of step the next time it is flipped.
#
# THE SIGN CARRIES OVER UNCHANGED. The moment is the bottom half's share, more
# dispersion puts more distance between the halves, so the share FALLS as the
# scale rises -- negative, exactly as it was written for the quantile grid. The
# bounds are next_batch.py's own, (1.50, 4.00).
def _live_productivity_process():
    try:
        txt = open(os.path.join(HERE, 'run_one_point.sh'), errors='replace').read()
    except OSError:
        return 1
    m = re.search(r'\[fixed_productivity\]=\s*(\d+)', txt)
    return int(m.group(1)) if m else 1


if _live_productivity_process() == 0:
    RULES.pop('sd_permanent_productivity', None)
    RULES['kkk_sigma_scale'] = ('sigma_y', -1.00, 1.50, 4.00, 0.35, 0.20)
else:
    RULES.pop('kkk_sigma_scale', None)

for _p, (_m, _fb, _lo, _hi, _d, _e) in list(RULES.items()):
    RULES[_p] = (_m, _fb, _lo, _hi, min(_d, SLOW_DAMPING), min(_e, SLOW_CAP))


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


_RESOLVE_FILE = os.path.join(HERE, 'resolve_cache.json')
_RESOLVE_LOADED = False


def _resolve(stamp):
    """A point's raw md5 stamp, mapped to the semantic hash of its economy.

    CACHED ON DISK, because resolving is expensive and the answer never changes.
    model_hash.resolve() walks the git revision table, which costs about 0.59
    seconds a stamp; the archive carries 82 distinct stamps, so a cold step spent
    47.7 seconds here -- against 0.1 seconds for the pair search it all feeds.
    Over the two to three hundred iterations the author expects that is four
    hours of re-deriving a fixed mapping.

    A raw md5 identifies a file's exact contents, so its semantic hash cannot
    change UNDER A FIXED HASH RULE. It lives in code/ so it survives a container
    reclaim through the pusher, which matters because a cold start would
    otherwise pay the 47.7 seconds again.

    THE RULE IS NOT FIXED, AND THIS DOCSTRING USED TO SAY THE CACHE "never needs
    invalidating". That sentence took the loop down on 7 September. Adding a name
    to model_hash.TARGET_CONSTANTS -- done that evening so h_2's target could move
    from 10.1 to 8 per cent -- changes what semantic() computes for EVERY revision
    at once, so every stored value became wrong rather than stale. model_hash
    already guards its own map with HASH_VERSION and rebuilds on a bump; this
    second cache had no version key, went on serving the pre-rule answers after
    the bump, and three_step kept exiting 2 with "no solved point carries the
    configuration yet" until the file was deleted by hand.

    So the version is stored alongside the entries and a mismatch drops the lot.
    The author, on being shown the two caches disagree: *"ok"*.
    """
    global _RESOLVE_LOADED
    if not _RESOLVE_LOADED:
        _RESOLVE_LOADED = True
        try:
            with open(_RESOLVE_FILE) as fh:
                _disk = json.load(fh)
            if _disk.pop('__hash_version__', None) == _mh_module().HASH_VERSION:
                _RESOLVE_CACHE.update(_disk)
        except Exception:
            pass
    if stamp not in _RESOLVE_CACHE:
        _RESOLVE_CACHE[stamp] = _mh_module().resolve(stamp)
        try:
            tmp = _RESOLVE_FILE + '.tmp'
            with open(tmp, 'w') as fh:
                json.dump(dict(_RESOLVE_CACHE,
                               __hash_version__=_mh_module().HASH_VERSION),
                          fh, indent=0, sort_keys=True)
            os.replace(tmp, _RESOLVE_FILE)
        except Exception:
            pass
    return _RESOLVE_CACHE[stamp]


def _add_sud_users(mom):
    """The SUD rate AMONG USERS, lambda_d / b, added as a derived moment.

    THE AUTHOR, 6 September: *"addiction_onset_base must be selection. you have
    to consider addiction_onset_base with b at the same time"*. They are right,
    and it resolves a sign that looked backwards for a whole afternoon.

    addiction_onset_base was pointed at lambda_d, a share of the WHOLE
    POPULATION, and measured at -2.78 over three controlled pairs: raising it
    from 0.02 to 0.08 took lambda_d from 0.0687 to 0.0015. That is real, but it
    is not what the parameter does. With lambda_addiction pinned at zero the
    onset hazard is min(base + (1-exp(0*q)), 1) = base flat for any user and zero
    for an abstainer, so there is no intensive margin: raising the base makes
    using so risky that b collapses from 0.2558 to 0.0024, and lambda_d falls
    with it because only users can carry the disorder.

    Conditioned on being a user the sign is the author's, and monotone:

        base 0.020   b 0.2558   lambda_d 0.0687   ratio 0.269
        base 0.040   b 0.0576   lambda_d 0.0256   ratio 0.444
        base 0.080   b 0.0024   lambda_d 0.0015   ratio 0.602

    slope +0.72, +0.44 and +0.58 across the three pairs. So the base owns the
    CONDITIONAL rate and addiction_scalar_1 owns the extensive margin, which
    separates two instruments that were otherwise chasing one margin between
    them.

    The target is the ratio of the two existing targets, 0.03680/0.08900 =
    0.4135, so nothing new is asserted about the data -- it is the same pair of
    numbers read as a rate rather than a share. The source records the NSDUH
    figure for SUD among users at 0.4509 beside it.
    """
    b, d = mom.get('b'), mom.get('lambda_d')
    if b and d and b > 0:
        mom['sud_users'] = d / b


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
    for pat, nm in _UNTARGETED_SINGLES:
        mm = re.search(pat, s)
        if mm:
            try:
                mom.setdefault(nm, float(mm.group(1)))
            except ValueError:
                pass
    _add_sud_users(mom)
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


_HEAD = {}


def _head_is_this_model(path, want):
    """True if this file's MODEL stamp resolves to the current economy.

    Reads the head of the file only, and remembers the answer against the file's
    mtime so a second call in the same process costs nothing. Point files never
    change once written, so the mtime guard is belt and braces.
    """
    try:
        st = os.stat(path)
    except OSError:
        return False
    key = (path, st.st_mtime, st.st_size)
    hit = _HEAD.get(key)
    if hit is None:
        try:
            with open(path, errors='replace') as fh:
                head = fh.read(512)
        except OSError:
            return False
        m = re.search(r'^MODEL (\S+)', head, re.M)
        hit = _HEAD[key] = (_resolve(m.group(1)) if m else None)
    return hit == want


def iterates():
    """Every solved point that is an iterate of this loop, newest last."""
    h = model_hash()
    out = []
    for f in glob.glob(os.path.join(HERE, 'points', 'point_*.txt')):
        if '.FAILED' in f:
            continue
        # THE MODEL LINE IS CHECKED BEFORE THE FILE IS READ. The archive holds
        # 2318 points and 77 of them are on this economy, so parsing every one
        # cost 49.8 seconds a step while the pair search it feeds cost 0.1. Over
        # the two to three hundred iterations the author expects, that is four
        # hours spent reading points from dead economies.
        #
        # MODEL is the third line of a point file, so a few hundred bytes decide
        # it. A file whose stamp does not resolve to this economy is never opened
        # past its head. Nothing else changes: the ones that do match are parsed
        # exactly as before.
        if not _head_is_this_model(f, h):
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
    active = _load_active()
    gain = _load_gain()
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

    # THE REASON IS PER PARAMETER. This message was written when
    # kkk_s_deviation_bottom was the only pinned parameter and said so
    # literally, so when lambda_addiction and ssi_floor_level joined FIXED the
    # trace reported both of them as "the author's 0.2 per cent bottom node". A
    # trace that names the wrong reason is worse than one that gives none: it is
    # read later as evidence.
    WHY = {
        'kkk_s_deviation_bottom': "the author's 0.2 per cent bottom node",
        'lambda_addiction':       "held at zero, the base carries the drug block",
        'kappa_uem':              "SMI separation conceded; kappa_find_smi carries it",
        'kappa_phi_d_level':      "held at 8; it was driving the drug two-cycle",
        'multiple_of_probabilities_of_employment_if_addicted':
                                  "SUD separation conceded; multiple_find_if_addicted carries it",
        'ssi_floor_level':        "the SSI floor is not an instrument; band 5 untargeted",
    }
    for k, v in FIXED.items():
        if abs(vec.get(k, v) - v) > 1e-9:
            print(f'#   {k:<44}{vec[k]:10.5g} -> {v:10.5g}   pinned: '
                  f'{WHY.get(k, "the author fixed it")}', file=sys.stderr)
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
        gap = abs(cur - tgt) / abs(tgt)
        # THE STATE IS ALWAYS WRITTEN BACK, including when it does not change.
        # The first version only assigned inside the two transition branches, so
        # an instrument that stayed active fell through with nothing stored and
        # the next line raised KeyError -- which stops three_step, and stopping
        # three_step stops the loop.
        was = active.get(moment, True)
        now = was
        if was and gap <= HOLD_ENTER:
            now = False
        elif not was and gap > HOLD_EXIT:
            now = True
        active[moment] = now
        if not now:
            why = ('reached' if was else 'still inside')
            print(f'#   {param:<44}{vec[param]:10.5g}   {moment} {cur:.5f} vs '
                  f'{tgt:.5f}, {100*(cur-tgt)/tgt:+.1f}%, HOLDING ({why} the five '
                  f'per cent hold; resumes past ten)', file=sys.stderr)
            continue
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
        # THE RATCHET. The sign is of the gap, not of the step, so it does not
        # matter whether the instrument raises or lowers its moment: an
        # instrument that was above target and is now below has jumped over it,
        # whatever direction it moved to get there.
        sign = 1.0 if cur > tgt else -1.0
        g, prev = gain.get(param, [RATCHET_CEIL, 0.0])
        if prev != 0.0 and sign * prev < 0:
            g = max(RATCHET_FLOOR, g * RATCHET_HALVE)
            marks = f'  RATCHET x{g:.3f}'
        else:
            g = min(RATCHET_CEIL, g * RATCHET_GROW)
            marks = '' if g >= RATCHET_CEIL else f'  gain {g:.3f}'
        gain[param] = [g, sign]
        # THE CAP SCALES WITH THE GAP, on the author's instruction of 7 September:
        # *"even 0.5% should be on large gaps"*, *"it should be less for smaller
        # gaps"*, after *"in general parameters should move very very slowly"*.
        #
        # WHY THE FLAT CAP WAS NOT ENOUGH. The step is already proportional to
        # the log gap, so a small gap SHOULD give a small step -- and for every
        # instrument with a large measured slope it did: beta at -0.7 per cent
        # took 0.01, tau_l at +0.3 took 0.01, sud_homeless at -8.2 took 0.02,
        # mu_H at -24.1 took 0.21. But an instrument whose slope is near or below
        # one divides by almost nothing, so even a tiny gap asks for a step far
        # past the cap and is clipped to the whole 0.5. Measured on the live
        # trace: gamma at a 2.6 PER CENT gap was taking the full cap, because a
        # slope of 0.17 says closing it needs a 15 per cent parameter move.
        #
        # So the ceiling is now a fraction of the gap, with the flat cap still
        # the absolute limit on top. The full 0.5 per cent is reached only past a
        # 25 per cent gap; 12 per cent is allowed 0.26, 2.6 per cent is allowed
        # 0.06. A wrong slope can no longer turn a small gap into a maximum step.
        if param in FAST:
            room = FAST[param]
        else:
            room = min(efold, GAP_SCALE * abs(math.log(tgt / cur)))
        step = damp * g * math.log(tgt / cur) / e
        step = max(-room, min(room, step))
        new = max(lo, min(hi, vec[param] * math.exp(step)))
        at = '  AT BOUND' if new in (lo, hi) else ''
        print(f'#   {param:<44}{vec[param]:10.5g} -> {new:10.5g}   '
              f'{moment} {cur:.5f} vs {tgt:.5f}, slope {e:+.2f} ({src}){at}{marks}',
              file=sys.stderr)
        nxt[param] = new
    _save_active(active)
    _save_gain(gain)
    emit = {k: float(f'{v:g}') for k, v in nxt.items()}
    remember(emit)
    print('bash code/run_one_point.sh ' +
          ' '.join(f'{k}={v:g}' for k, v in sorted(emit.items())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
