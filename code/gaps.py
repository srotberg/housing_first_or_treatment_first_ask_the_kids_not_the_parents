#!/usr/bin/env python3
"""The full gap table, printed when the loss improves.

The author, 1 September: "I want you to show me the full gaps table each time
the loss function improves." So this is not a report anyone has to remember to
run -- ENGINE.md calls it every firing, it decides for itself whether the loss
moved, and it prints the whole table when it did and one line when it did not.

THE LOSS IS THE AUTHOR'S OWN, not a convenient summary. A MINIMAX over the
scored moments -- "once we get below 10% for everything we can stop" -- with
beta scoring zero anywhere inside its 3.0-4.5 band. The median is printed
beside it because the two moved in opposite directions more than once today
and reporting only one of them hides that, but the median is never the
criterion.

The high-water mark lives in .gaps_best so it survives a container.
"""
import glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_MAP = {}
_OK = set()
SKIP = {'h_3'}
# rent50 is REPORTED, NOT SCORED. The cheapest rung is bracketed on h_2, the
# headcount above half of total SPENDING, on the author's instruction that gamma
# and the cost burden share a denominator. rent50 is the same headcount over
# INCOME and pointed the OPPOSITE way -- +163 per cent against h_2's -38 -- so
# scoring both left one parameter with two targets it could not satisfy at once.
# h_2 LEFT THIS SET on 3 September, when the rung was pointed back at it. It had
# been unscored because the rung was standing in for emp_homeless's missing
# instrument; emp_homeless now has bottom_productivity_level and h_2 is a target
# again. next_batch.py scores it and this file must agree -- when they disagreed
# the loss was computed over two different sets and the wrong point was promoted.
# h_share1 IS SCORED from 3 September, on the author's instruction: *"we can now
# bring back the wealth for the newborns to make their share of the homeless
# correct. We should calibrate it"*. Its instrument, newborn_endowment_scale, was
# parked at 0 while w_bot was too high; the seven-node grid brought h_share1 from
# +121 per cent to +24, so the push needed is now small.
UNSCORED = {
            # h_share1 IS PARKED TOO, on the author's instruction of 3 September:
            # *"Before you do anything for newborns, I suggest to leave it out for
            # now from the calibration measure. At the end we can decide what to
            # do."*
            #
            # Its only instrument, newborn_endowment_scale, is at its floor and
            # one-sided, and the two things that would free it are both open
            # questions the author has not ruled on: the endowment is delivered
            # TWICE at age 1, and the 2022 SCF puts every productivity node's mean
            # non-housing net worth POSITIVE, so a negative value is a calibration
            # choice the data do not support as a level.
            #
            # While it was scored it BOUND the minimax at 56.4 per cent and nothing
            # else could move the loss: every other gap sat below it, so the
            # measured gains waiting to be recombined -- tau_l to -4.2 at
            # labor_income_tax_rate 0.835, pi_eu to -2.3 at
            # probability_becoming_unemployed 0.055 -- could not register at all.
            #
            # NOT CONCEDED, PARKED, exactly as h_share5 is. Restoring it is
            # deleting this one line.
            'h_share1',
            # h_share5 IS PARKED, on the author's instruction of 3 September:
            # *"Ignore the old homelessness for now. Just calibrate the rest of
            # the block first."*
            #
            # It is 765 per cent out and dominates a MINIMAX, so while it is
            # scored the loss cannot rank points on any other margin -- which is
            # exactly why the rest of the block has been hard to read. Parking it
            # lets the other seventeen moments be worked.
            #
            # NOT CONCEDED, PARKED. ssi_floor_level still owns it and goes idle
            # rather than being retired, and restoring the moment is deleting
            # this one line. The open question in SSI_FLOOR_ANALYSIS.md stands:
            # the street carries no disutility, so a household prefers it below
            # an income of 0.4579, and retiree income runs 0.400 to 0.510.
            #
            # ONE THING TO CARRY INTO THAT LATER WORK, because it cuts against
            # the natural guess. The author's reading is that the old are
            # homeless from too little income and that low labour supply is part
            # of it. In absolute terms that is right, but raising labour supply
            # makes the SHARE worse, and the reason is structural: pensions are
            # computed from employment_grid at the last working age -- the
            # household's productivity TYPE -- and not from hours, so more hours
            # lift the working age over the threshold and leave retirement income
            # exactly where it was. Measured: rsl 3.05 -> 1.40 took band 5 from
            # 0.9306 to 0.9562 while h_1 halved.
            'h_share5',
    # w_bot LEAVES THE LOSS, 3 September: *"We don't need the w_bot anymore...
    # We have just one beta now!"* There is no second discount factor to aim at
    # it. It reads 0.02097 at the base against 0.025 in the SCF, so it is right
    # without an instrument. Printed, not scored.
    'w_bot',
'kappa_ued', 'kappa_uem', 'rent50'}
BAND = {# w_bot IS A WIDE BAND, on the author's instruction of 3 September:
        # *"It's ok if the bottom is not exactly 2.5%. It can be 0.8-5% no
        # problem"*. Anything inside scores zero.
        #
        # Worth knowing which edge binds, because it is not the one the
        # concession was offered for: under ONE beta type the bottom half holds
        # too MUCH, not too little -- 0.03203 at discount_factor 0.965 and
        # 0.05032 at 0.99980. The upper edge of 0.05 is the live constraint.
        'w_bot': (0.008, 0.05)}
# beta IS A POINT TARGET AGAIN, at the wealth-to-output ratio of 3 the Fortran
# already declares in wealth_to_output_data. The author: *"Target wealth to
# income ratio of 3 since it seems to work well"*. It was briefly a (2.5, 3.0)
# band earlier today on their earlier instruction; a point target with the
# standard ten per cent tolerance is 2.7 to 3.3, which is tighter and is what
# they have now asked for. No BAND entry means gap() scores it the ordinary way
# against the target on its own MOMENT line.
#   THE AUTHOR'S beta BAND, 3 September
# *"If you targeted a net worth to income ratio of 2.5-3 I think you'd have less
# homelessness because people would not sacrifice on housing in order to save a
# bit for the future they care less about"*.
#
# It was (3.0, 4.5), with 3.0 the LOWER edge following wealth_to_output_data.
# The author has put 3.0 at the TOP instead, so the band now sits at and below
# the data point rather than at and above it. That is a target change, made on
# their instruction and not by inference, and it moves what counts as DONE for
# discount_factor.
#
# WHAT IT DOES TO THE SEARCH, which is the reason it is not a cosmetic edit: on
# THIS economy discount_factor 0.99980 gives W/Y 5.35 and 0.95 gives 2.93, so the
# new band is reached around 0.95 to 0.96 -- far below the 0.985 to 0.995 bracket
# already in flight, which sits entirely above it. The measured table beside
# wealth_to_output_data in the Fortran (0.99980 -> 2.4528) is from the FROZEN
# grid and does not transfer: stochastic productivity more than doubled
# aggregate wealth at the same patience.

# parameter -> the moment it is bracketed on. Kept here rather than imported so
# that a broken next_batch.py cannot stop the author seeing where things stand.
OWN = [
    ('discount_factor', 'beta'),
    # discount_factor_impatient RETIRED 3 September: *"We can use just one beta.
    # Ignore the second beta."* With number_of_beta_types=1 there is no impatient
    # type for it to be the discount factor of, so the row reported a gap against
    # a parameter that cannot move it. w_bot is a band now, (0.008, 0.05), and
    # discount_factor sets it -- 0.03203 at 0.965, 0.05032 at 0.99980.
    ('probability_becoming_unemployed', 'pi_eu'),
    ('size_homelessness', 'h_1'),
    # RESTORED 3 September: *"For band 1 of the homeless you can just use the
    # endowment of the newborns to match the share of homeless who are young."*
    # It only pushes band 1 down, and band 1 is far below target at the current
    # street size, so it binds only once the street shrinks -- which the street
    # map says it will, band 1 running 0.193 at 0.045 to 0.755 at 0.030.
    ('newborn_endowment_scale', 'h_share1'),
    # OLD-AGE HOMELESSNESS IS SCORED FROM 3 SEPTEMBER and the SSI floor owns it.
    # The author: *"we need to make sure that the old are not homeless too much,
    # they should have very little of the share of the homeless"*. Band 5 holds
    # 0.7186 of the homeless against 0.075 in the HUD count, the worst number in
    # the model, and it was in UNSCORED because nothing could reach it. The
    # reason nothing could is in next_batch.py: the floor sits inside
    # `if (use_pia_formula==1)` and every vector carries use_pia_formula=0, so
    # the code never ran.
    # The LEVEL owns it from 3 September, not the take-up: only the product
    # takeup*ssi_floor_level enters the benefit, take-up is clamped to [0,1] so
    # the effective floor could never pass 0.1774, and that is below the PIA of
    # the node holding 39.8 per cent of the mass. See SSI_FLOOR_ANALYSIS.md.
    ('ssi_floor_level', 'h_share5'),
    # THE ENDOWMENT NO LONGER OWNS h_share1 and h_share1 keeps its row as
    # "(no instrument)". The author, 3 September: *"If you don't need an
    # endowment for the youngest to get the right share of homeless young,
    # that's ok too!"* -- and it is not needed: h_share1 is minus 7.3 per cent
    # at point_c048025c98 with the endowment at 0.0. The reasoning, including
    # why the endowment could only push the share the wrong way from here, is
    # beside the removed OWN entry in next_batch.py.

    ('relative_share_of_housing', 'gamma'), ('max_food_cost', 'cbar'),
    ('relative_share_of_addiction_1', 'theta'),     ('value_of_life', 'aleph'), ('mu_homeless', 'mu_H'),
    ('utility_cost_of_treatment', 'tau_u'), ('kappa_uem', 'lambda_m'),
    ('probability_of_voucher_benchmark_used', 'pi_V'),
    # increased_prob_if_homeless is EXOGENOUS at 0.2 on the author's
    # instruction -- twenty per cent each way -- so it owns nothing. The
    # cheapest rung owns emp_homeless instead; see next_batch.py for why.
    ('smallest_rental_relative_to_lowest_income', 'h_2'),
    # The bottom productivity node owns emp_homeless from 3 September; the rung
    # went back to the cost burden. Income of the homeless stays untargeted and
    # belongs to validation, on the author's instruction.
    ('bottom_productivity_level', 'emp_homeless'),
    ('lambda_addiction', 'b'), ('addiction_scalar_1', 'lambda_d'),
    ('relative_share_of_leisure', 'omega_l'),
    ('labor_income_tax_rate', 'tau_l'),
    # SIGMA_Y'S INSTRUMENT DEPENDS ON THE PROCESS, and exactly one is live.
    # sd_permanent_productivity builds the quantile grid and moves nothing under
    # fixed_productivity=0; kkk_sigma_scale scales both innovation sds of
    # KKK_process and moves nothing under fixed_productivity=1. The inert one is
    # dropped below rather than left mapped, because a row against an instrument
    # that cannot move its moment reads as a stuck parameter when it is simply
    # not this economy's parameter.
    ('sd_permanent_productivity', 'sigma_y'),
    ('kkk_sigma_scale', 'sigma_y'),
    ('smi_onset_level', 'p_m'),
    # BOTH ADDED ON THE AUTHOR'S INSTRUCTION AND BOTH MISSED HERE. next_batch
    # gained them and gaps.py did not, which is the third time these two files
    # have drifted apart on the scored set in one evening -- rent50, then h_2,
    # now these. The cross-check at the top is what caught it each time.
    ('multiple_of_probabilities_of_employment_if_addicted', 'sud_homeless'),
    ('weight_on_child', 'omega_c'),
]

# EXACTLY ONE DISPERSION INSTRUMENT IS LIVE, and which one is a property of the
# economy rather than of this table. Read from run_one_point.sh's default,
# because that is what every new point inherits unless a line overrides it.
# The inert one is dropped rather than left in: a row against an instrument that
# cannot move its moment reads as a stuck parameter when it is simply not this
# economy's parameter, and next_batch.py makes the same swap from the same
# source, so the two files agree by construction rather than by memory.
def _live_productivity_process():
    try:
        txt = open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'run_one_point.sh'), errors='replace').read()
    except OSError:
        return 1
    m = re.search(r'\[fixed_productivity\]=\s*(\d+)', txt)
    return int(m.group(1)) if m else 1


def _live_switch(name, fallback='1'):
    """run_one_point.sh's own default for a configuration switch.

    Read from the script, not duplicated as a literal, for the reason the
    numbers rule gives: one number in two places is how they drift apart.
    """
    try:
        txt = open(os.path.join(HERE, 'run_one_point.sh'), errors='replace').read()
    except OSError:
        return fallback
    m = re.search(r'\[' + re.escape(name) + r'\]=\s*([0-9]+)', txt)
    return m.group(1) if m else fallback


# THE SWITCHES THAT DEFINE THE ECONOMY. Duplicated from next_batch.py rather
# than imported, for the same reason OWN is: a broken next_batch.py must not
# stop the author seeing where things stand. _cross_check below is what catches
# the two drifting apart.
#
# use_pia_formula joined on 3 September, on the author's *"Yes flip it to 1"*.
# It chooses between the US statute's benefit formula with a means-tested SSI
# floor and a flat replacement rate, so a point either side of it is a
# different economy. ssi_floor_takeup is NOT here: it is the calibrated dial
# inside the PIA branch, with a bracket and a target, and filtering on it would
# discard every arm measured on it.
CONFIG_SWITCHES = {
    'fixed_productivity': _live_switch('fixed_productivity'),
    'use_pia_formula': _live_switch('use_pia_formula'),
    # homeless_death_risk_flat_in_age IS A CONFIG SWITCH, added 4 September when
    # setting it to 2 was first tested.  It is a HANDOVER parameter, so it needs no
    # source edit and does not move the model hash -- which is exactly why it has to
    # be listed here.  Without it a point run at 2 would POOL with the 150 points run
    # at 0 and gaps.py would rank them against each other as one economy, when they
    # are two: setting 0 uses Baggett's measured age profile, 9.1 times the death
    # hazard at 26 falling to 1.1 at 82, and setting 2 uses a FLAT 1.6 multiplier at
    # every age from Meyer, Wyse and Logani.  Those are different models of what
    # homelessness does to an old person, not different parameter values.
    'homeless_death_risk_flat_in_age': _live_switch('homeless_death_risk_flat_in_age'),
}

_DEAD_SIGMA = ('kkk_sigma_scale' if _live_productivity_process() == 1
               else 'sd_permanent_productivity')
OWN = [(p_, m_) for p_, m_ in OWN if p_ != _DEAD_SIGMA]



def _cross_check():
    """Warn if this file's scored set has drifted from next_batch.py's.

    It had. h_2 was in next_batch's OWN and missing from the list above, so the
    author's table showed twenty-one moments where the search was working
    twenty-two, and the omitted one was sitting at minus twenty-seven per cent.
    It did not bind, so nothing looked wrong. The same class of divergence over
    rent50 made the printed loss read 162.8 against a true 100.1 earlier the
    same day, which is why this is checked rather than remembered.

    Deliberately a warning and not an import: the whole reason OWN is duplicated
    here is that a broken next_batch.py must not stop the author seeing where
    things stand.
    """
    try:
        sys.path.insert(0, HERE)
        import next_batch as _nb
    except Exception:
        return
    # next_batch keeps b and lambda_d OUT of OWN because the drug block is
    # bracketed by the gate rather than by a single arm, so they must be added
    # back before comparing or the check cries wolf about two moments both files
    # score. omega_c used to be dropped from both sides here, on the ground that
    # measure_child_gap=0 meant nothing measured it. That stopped being true when
    # the author put omega_c in round 5 and the flag became settable, so the
    # exclusion was itself masking a divergence -- the check reported one and hid
    # the other. Both sides now compare the full set.
    # THE CHECK WAS COMPARING AGAINST THE WRONG SET, and it cried wolf for it.
    #
    # It reconstructed next_batch's scored set as OWN.values() | GATE. That is
    # not how next_batch scores. Its loss is
    #
    #     {k: gap(k, p) for k, p in m.items() if k not in SKIP and k not in UNSCORED}
    #
    # -- every moment the point PARSES, minus the two exclusion sets. OWN says
    # which parameter gets an ARM aimed at a moment, which is a different
    # question: a moment can be scored with nothing bracketing on it, and this
    # file's own note on the cost burden headcount says so in as many words.
    #
    # So the reconstruction understated next_batch's set by exactly the
    # scored-but-unowned moments, and the warning fired on a legitimate state.
    # It said "gaps.py scores h_share1 and next_batch.py does not" all
    # afternoon on 3 September; h_share1 was in next_batch's loss the whole
    # time. Acting on that warning cost a wrong mapping and a wrong statement
    # to the author.
    #
    # The honest comparison is the two exclusion sets themselves, plus this
    # file's OWN-derived set against what next_batch would score on the same
    # point. Only the first is available without a point in hand, and it is the
    # part that actually diverges when the files drift.
    # AND THE COMPARISON IS RESTRICTED TO THE MOMENTS THIS FILE KNOWS ABOUT.
    # next_batch parses the four other age shares and all five band rates and
    # excludes them in UNSCORED; this file never parses them, so it has nothing
    # to exclude. Comparing the exclusion sets raw made that benign difference
    # look like nine divergences. The question worth asking is narrower: for a
    # moment BOTH files handle, do they agree on whether it is in the loss?
    known = {m for _, m in OWN} | SKIP | UNSCORED | set(NOTE)
    mine = known - SKIP - UNSCORED
    theirs = known - _nb.SKIP - _nb.UNSCORED
    if mine != theirs:
        for m in sorted(theirs - mine):
            print(f'WARNING: next_batch.py scores {m} and gaps.py does not.')
        for m in sorted(mine - theirs):
            print(f'WARNING: gaps.py scores {m} and next_batch.py does not.')
        print('The loss below is over gaps.py\'s set. Reconcile the two files.\n')
# moments that are printed and deliberately not scored, with the reason
NOTE = {'h_3': 'conceded, a fact about a grid the model chose',
        # THE ENDOWMENT'S MAPPING IS CONDITIONAL AND LIVES IN next_batch.py, so
        # this row explains the empty instrument column rather than guessing at
        # it. The author's rule, 3 September: *"If you see that you need to
        # bring up the youngest endowment since their share is too high, then
        # you can turn on that instrument. Keep it off if the share of young is
        # below the data"*. The endowment only pushes the share DOWN -- measured
        # 0.956 to 0.785 across the transfer sweep -- and sits at its 0.0 floor,
        # so above target it is the instrument and below target it is a
        # parameter that can only make things worse.
        #
        # The condition is NOT duplicated here on purpose: it depends on the
        # chosen base's own h_share1, next_batch.py applies it after selecting
        # that base, and a second copy would be a second thing to drift.
        'h_share1': 'endowment turns ON only when the young share is ABOVE '
                    'the data; it is one-sided and at its floor',
        'omega_c': 'round 5 only; measured when measure_child_gap=1 is handed in',
        'rent50': 'reported, not scored: same headcount over income, opposite sign',
        'y_u': 'mortality pinned at 8 by the author; goes to a robustness run'}


import model_hash as _mh   # semantic identity: comments do not change the model


def model_hash():
    return _mh.current()


def config():
    """The economy, not just the source: run_one_point.sh's own default."""
    m = re.search(r'\[number_of_beta_types\]=(\d+)',
                  open(os.path.join(HERE, 'run_one_point.sh')).read())
    return m.group(1) if m else None


def load(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    mv = re.search(r'^VECTOR (.*)$', t, re.M)
    if not mv:
        return None, None
    v = dict(kv.split('=', 1) for kv in mv.group(1).split())
    # THE LABEL IS CAPTURED, not skipped, because sigma_y names two different
    # statistics in this archive. Until 3 September it was "bottom half earnings
    # share", built from employment_grid and its ergodic masses; from then it is
    # "bottom half labour income share", walked at the median of the model's own
    # earnings histogram with hours and the age profile in it. Same target, very
    # different number. next_batch.py drops the old one by label in STALE_LABEL
    # and this does the same, so a stale point does not report a gap against a
    # moment it never measured.
    m = {}
    for k, lab, a, b in re.findall(
            r'MOMENT (\S+)\s+(.*?)model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', t):
        if k == 'sigma_y' and 'bottom half earnings share' in lab:
            continue
        m[k] = (float(a), float(b))
    # pi_eu IS SCORED AGAINST 0.139, whatever the point's own MOMENT line says.
    # The Fortran declares 0.139 from 3 September -- the SCF share of households
    # aged 26 to 64 with no wage income, which is what model_fraction_unemployed
    # actually measures -- but every archived point printed 0.049, the U-3 rate.
    # next_batch.py forces the same number through TARGET_OVERRIDE; without the
    # matching line here the two tools would score the identical model value
    # against different targets and their tables would disagree.
    if 'pi_eu' in m:
        m['pi_eu'] = (m['pi_eu'][0], 0.139)
    if 'gamma' in m and abs(m['gamma'][1] - 0.268) > 1e-9:
        r = re.search(r'DIAG aggregate housing / aggregate expenditure\s+=\s*([0-9.eE+-]+)', t)
        if r:
            m['gamma'] = (float(r.group(1)), 0.268)
    # THESE ARE FALLBACKS, NOT OVERRIDES. emp_homeless is a MOMENT line from 3
    # September and the generic parser above already has it; a point measured
    # before today carries the UNTARGETED wording instead and is picked up here.
    # The guard matters in the one direction: without it a point that somehow
    # carried both wordings would have the old line win, which is the wrong way
    # round.
    #
    # sigma_y is NOT in this list on purpose. Its object changed today, so an
    # old point's number is not the new moment under a different name -- it is a
    # different statistic, and next_batch.py drops it by label. There is nothing
    # to fall back to.
    for pat, key, tv in (
            (r'UNTARGETED share of the homeless, band\s+1\s+model=\s*([0-9.eE+-]+)', 'h_share1', 0.26),
            (r'UNTARGETED share of the homeless, band\s+5\s+model=\s*([0-9.eE+-]+)', 'h_share5', 0.075),
            (r'UNTARGETED employed share of the homeless\s+model=\s*([0-9.eE+-]+)', 'emp_homeless', 0.46),
            (r'UNTARGETED renters above 50 pct of income\s+model=\s*([0-9.eE+-]+)', 'rent50', 0.175),
            # THE SUD SHARE OF THE HOMELESS, the untargeted half of the same
            # Gutwinski meta regression lambda_m is calibrated to. The model has
            # printed it on every point ever solved and nothing here read it, so
            # the instrument that owns it --
            # multiple_of_probabilities_of_employment_if_addicted -- looked like a
            # parameter with no moment and was dropped from the search as dead.
            # It is not dead: it sits at 0.117 against 0.217, a gap of 46 per
            # cent, on all 153 points in the archive. Adding the pattern scores
            # them all retroactively and costs no model time.
            (r'UNTARGETED SUD share of the homeless\s+model=\s*([0-9.eE+-]+)',
             'sud_homeless', 0.217)):
        if key in m:
            continue
        r = re.search(pat, t)
        if r:
            m[key] = (float(r.group(1)), tv)
    return v, m


def gap(k, pair):
    mo, tv = pair
    if k in BAND:
        lo, hi = BAND[k]
        return 0.0 if lo <= mo <= hi else min(abs(mo - lo) / lo, abs(mo - hi) / hi)
    return abs(mo - tv) / abs(tv) if tv else float('nan')


# Two worst gaps within EPS are a TIE and the comparison moves to the next
# moment. See the note at the improvement test for what a strict comparison did.
EPS = 0.01


def _better_vec(new_v, old_v):
    for a, b in zip(new_v, old_v):
        if abs(a - b) > EPS:
            return a < b
    return len(new_v) < len(old_v)


def main():
    _cross_check()
    global _MAP, _OK
    _MAP = _mh.build_map()
    h, cfg = model_hash(), config()
    # BEHAVIOUR-PRESERVING PREDECESSORS, READ FROM next_batch.py AND KEYED ON THE
    # CURRENT HASH -- never a literal.
    #
    # This was a literal set unioned unconditionally with the current hash, and
    # on 1 September the model changed and it kept admitting the old points and
    # printing them under the NEW hash: "MODEL 0e0abddab7, 33 points in this
    # economy", when not one of the 281 points in the archive had run that
    # source. next_batch.py, keying its lookup on the current hash, correctly
    # said "no archive" in the same minute. The two disagreed about whether an
    # entire archive existed.
    #
    # That is an equivalence ASSERTED rather than measured, which is the one
    # thing ENGINE.md says this mechanism must never be used for, and it asserted
    # it silently at the moment the model had just changed underneath it.
    #
    # The fallback is {h} alone, not a remembered list: when next_batch cannot be
    # imported the honest answer is "only points on this exact source count",
    # which under-counts rather than over-claims.
    try:
        sys.path.insert(0, HERE)
        import next_batch as _nb
        _OK = {h} | set(_nb.EQUIVALENT_MODELS.get(h, set()))
    except Exception:
        _OK = {h}
    best = None
    n = 0
    # ONLY point_<tag>.txt. The glob used to be '*.txt' with a FAILED exclusion,
    # which swept up anything else a worker left in points/: a determinism test
    # renaming its replicates RUN1_point_... had them scored as separate points
    # of the same vector, and the tag in the header came out truncated because it
    # is cut from a fixed offset. Replicates of one vector are not independent
    # points and must not be counted as several.
    n_wrong_proc = 0
    # THE OPEN STAGE'S MOMENTS, computed once so every point is ranked on the
    # same set. Imported from next_batch rather than copied so the two files
    # cannot drift; STAGES[0] is the open round until it closes.
    try:
        import next_batch as _nb0
        _SCOPE = set(_nb0.STAGES[0]) if _nb0.STAGES else set()
    except Exception:
        _SCOPE = set()
    for f in sorted(glob.glob(os.path.join(HERE, 'points', 'point_*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        if not re.fullmatch(r'point_[0-9a-f]{10}\.txt', os.path.basename(f)):
            continue
        t = open(f, encoding='utf-8', errors='replace').read()
        mm = re.search(r'^MODEL (\S+)', t, re.M)
        # resolve_for_point, not resolve: a change gated on a flag is inert for
        # the points that ran with the flag off, and only the point's own
        # vector can say which those are.
        if not mm or _mh.resolve_for_point(mm.group(1), t, _MAP) not in _OK:
            continue
        v, m = load(f)
        if v is None or (cfg and v.get('number_of_beta_types', cfg) != cfg):
            continue
        # THE PRODUCTIVITY PROCESS IS PART OF THE ECONOMY, and this file was
        # missing the filter that next_batch.py's archive() has had since the
        # flip to stochastic productivity this morning.
        #
        # WHAT IT COST, caught on 3 September at 14:00. With h_share5 newly
        # scored, gaps.py selected point_e8f6f3b777 as the best point and
        # printed a full table for it. That point carries fixed_productivity=1:
        # it is a FROZEN GRID point, an economy the author abandoned, pooled
        # with the stochastic ones because the MODEL hash is inert across the
        # switch and nothing here looked at the flag. The header even said "69
        # points in this economy" while counting two different economies.
        #
        # The inert registration is right and this filter is its other half:
        # the SOURCE is unchanged across the switch, so the archive pools on the
        # hash, and the VECTOR is what says which process a point actually ran.
        # next_batch.py has the same test with the same reasoning beside it.
        if any(str(int(float(v.get(k, '1')))) != w
               for k, w in CONFIG_SWITCHES.items()):
            n_wrong_proc += 1
            continue
        n += 1
        g = {k: gap(k, m[k]) for k in m
             if k not in SKIP and k not in UNSCORED and m[k][1]}
        if not g:
            continue
        # RANK ON WHAT THE SEARCH MAY ACTUALLY MOVE, which next_batch does and
        # this file did not.
        #
        # WHAT IT COST, measured 3 September 19:00 on two candidate points:
        #
        #   2b699025a0  worst 99.5% (tau_u)     then 69, 45, 40, 39   5 inside ten
        #   d9f6fab6e8  worst 82.7% (lambda_d)  then 82, 80, 75, 73   7 inside ten
        #
        # This file picked d9f6fab6e8 because 82.7 < 99.5 lexicographically. But
        # tau_u is HELD -- its stage is not open and utility_cost_of_treatment
        # may not step -- so on every moment the round can touch, 2b699025a0 is
        # much better: 69 against 82.7 on the open worst, with a far shorter
        # tail. The report was naming as best a point the search would be wrong
        # to step from, and disagreeing with the OPEN STAGE line it printed
        # three lines later in its own header.
        if _SCOPE:
            _g = {k: x for k, x in g.items() if k in _SCOPE}
            if _g:
                g = _g
        worst = max(g.values())
        # THE SAME TIE TOLERANCE HAS TO APPLY HERE, and this is the line that
        # matters: `worst < best[0]` is how the best point is CHOSEN, and it is
        # what promoted a point whose drug block had collapsed to -96.3 per cent
        # over one at +8.7, on a tenth of a point of emp_homeless. Fixing only
        # the improvement test left the wrong point selected and merely stopped
        # announcing it.
        # THE OBJECTIVE IS THE SUM OF SQUARED RESIDUALS, on the author's
        # instruction of 4 September: *"i want you to use a better measure than
        # minmax. use sum of squared residuals"*.
        #
        # WHY IT WAS CHANGED, in the evidence that prompted it.  Under a minimax
        # one bad moment sets the score and everything behind it is invisible.
        # sigma_y was closed to +0.9 per cent and pi_eu to -1.9 in solved points
        # on 4 September, after sitting at -39.5 and -43.8 all day, and neither
        # ever appeared in the table: the points carrying them scored 96 per cent
        # on a collapsed drug block, so the reported best stayed the old one and
        # the author reasonably asked why sigma_y was stuck.  It was not stuck.
        #
        # The sum of squares counts every moment, so a point that closes eleven
        # and loses one ranks above a point that is mediocre everywhere.  It is
        # also what the Newton step already minimises, so the report and the
        # search now agree on what better means.
        #
        # `worst`, the old minimax, is still computed and still printed beside the
        # loss, because the author's STOPPING RULE is unchanged -- everything
        # inside ten per cent -- and that is a statement about the worst gap.
        vv = sorted(g.values(), reverse=True)
        sq = sum(x * x for x in g.values())
        if best is None or sq < best[6]:
            best = (worst, os.path.basename(f)[6:-4], v, m, g, vv, sq)
    if n_wrong_proc:
        live = ', '.join(f'{k}={w}' for k, w in sorted(CONFIG_SWITCHES.items()))
        print(f'  {n_wrong_proc} points skipped for running a different '
              f'configuration than run_one_point.sh defaults to ({live})')
    if best is None:
        print('no scoreable point in the current economy'); return 1
    worst, tag, v, m, g, _bv, _sq = best
    med = sorted(g.values())[len(g) // 2]

    mark = os.path.join(HERE, '.gaps_best')
    prev = json.load(open(mark)) if os.path.exists(mark) else {}
    # THE HIGH-WATER MARK IS KEYED ON THE SCORED SET, NOT JUST THE MODEL.
    #
    # Removing p_m on the author's instruction took the scored set from 21
    # moments to 20, and the stored gap vector still had 21 entries. Python
    # compares lists elementwise and then by LENGTH, so the shorter vector won
    # and gaps.py announced "PROGRESS" for a round in which nothing had moved --
    # the loss was 100.1 per cent before and after. A comparison across two
    # different sets of moments is not a comparison at all.
    #
    # The set's signature goes in the key, so changing what is scored starts a
    # fresh mark instead of silently beating the old one.
    key = f'{h}|{cfg}|{",".join(sorted(g))}'

    # PROGRESS IS LEXICOGRAPHIC, NOT JUST THE MINIMAX.
    #
    # The author asked to see the table whenever the loss improves, and then, an
    # hour later, "I want to see progress" -- because they had not seen one. The
    # reason is that a plain minimax cannot show progress while its binding
    # moment is stuck: emp_homeless sat at +100.1 per cent all evening, so the
    # worst gap never fell, so the table never printed, while fourteen other
    # moments were free to move in either direction unseen.
    #
    # The criterion is still theirs -- the number reported as the LOSS is the
    # minimax, and the stopping rule is still every scored moment inside ten per
    # cent. This only changes when the table is SHOWN: the gap vector sorted
    # worst-first is compared lexicographically, so a round that leaves the worst
    # moment where it is and improves the second worst counts as progress and
    # prints. That is the standard refinement of a minimax and it cannot call
    # something progress that the minimax would call a regression.
    # THE MINIMAX NEEDS A TIE TOLERANCE OR IT WILL TRADE EVERYTHING FOR NOTHING.
    #
    # Strict lexicographic on the sorted gap vector compares element 0 first and
    # stops the moment it differs. On 2 September that promoted point_2cb1dfff73
    # over point_a6ff37446f because its worst gap was 100.0 per cent against
    # 100.1 -- a tenth of a point on emp_homeless, which no instrument can reach
    # anyway -- while b went from +8.7 per cent to -96.3, h_1 from -63 to -97.7,
    # h_share1 from -27 to -95.8, the median from 26.7 to 59.5 and the count
    # inside ten per cent from six to three. The drug block was destroyed and the
    # tool called it PROGRESS.
    #
    # That is correct lexicographic behaviour and useless as a search criterion,
    # because the binding moment is one nothing can move: any point may buy the
    # top slot with a rounding-sized gain and pay for it anywhere it likes.
    #
    # So two worst gaps within EPS of each other are a TIE and the comparison
    # moves to the next element. The author's stopping rule is untouched -- it is
    # still every scored moment inside ten per cent -- and so is the reported
    # LOSS. This changes only which point is called best while the search runs.
    # PROGRESS IS NOW THE SUM OF SQUARES TOO, not the lexicographic worst vector.
    # Leaving the improvement test on the old measure while the SELECTION used the
    # new one would report "loss unchanged" on a firing that had just found a
    # strictly better point, which is the same class of error as the one that hid
    # sigma_y: the file would know and not say.
    vec = sorted(g.values(), reverse=True)
    old_sq = prev.get(key, {}).get('sq')
    improved = old_sq is None or _sq < float(old_sq) - 1e-12
    if improved:
        prev[key] = {'worst': worst, 'sq': _sq, 'tag': tag, 'vec': vec}
        json.dump(prev, open(mark, 'w'), indent=1)

    head = (f'point_{tag}  MODEL {h}  beta types {cfg}  {n} points in this economy\n'
            f'LOSS (sum of squared residuals) {_sq:.4f}   worst {100*worst:.1f}%   '
            f'median {100*med:.1f}%   '
            f'inside ten per cent {sum(1 for x in g.values() if x <= .10)} of {len(g)}')

    # THE HEADLINE LOSS IS NOT A PROGRESS NUMBER WHILE THE GATE IS STAGED, and
    # printing it alone misled the author for a full day. It is a minimax over
    # EVERY scored moment, but next_batch holds every instrument whose moment is
    # in a stage that has not opened, so the moments that dominate the minimax
    # are frozen by construction. On 2 September the headline sat at 652.2 per
    # cent, pinned by h_1 in stage 2, while the open stage's own worst gap was
    # 119.4 -- and the fleet was correctly working the latter. Reported as one
    # number it looked like a day of no progress on a search that was not
    # allowed to touch what the number measured.
    #
    # So print the open stage too. The stage list is next_batch's, imported
    # rather than copied, so the two cannot drift apart.
    try:
        import next_batch as _nb
        _open = None
        for _st in _nb.STAGES:
            _in = {k: x for k, x in g.items() if k in _st}
            # ten per cent is the author's own bar -- "once we get below 10% for
            # everything we can stop" -- and next_batch's BASE_TOL is a per-moment
            # dict rather than a scalar, so the objective's threshold is used here.
            if _in and max(_in.values()) > 0.10:
                _open = (_st, _in)
                break
        if _open:
            _st, _in = _open
            _w = max(_in.values()); _wm = max(_in, key=_in.get)
            head += (f'\nOPEN STAGE {_nb.STAGES.index(_st)}: minimax {100*_w:.1f}% '
                     f'(worst: {_wm})   inside ten per cent '
                     f'{sum(1 for x in _in.values() if x <= .10)} of {len(_in)}'
                     f'   -- the moments the search may actually move')
    except Exception:
        pass
    # --force PRINTS THE TABLE REGARDLESS. The gate above exists so that the
    # hourly firing does not spam an unchanged table at the author, and that is
    # the right default. But the author asks for the table directly -- "can you
    # show me the gaps table" -- more often than the loss improves, and working
    # around the gate by hand each time is how a hand-computed table that
    # disagreed with the loss got shown once already.
    if not improved and '--force' not in sys.argv:
        print(f'no progress in the sum of squares; best still '
              f'point_{prev[key]["tag"]} at {float(prev[key].get("sq", 0)):.4f}. '
              f'Table not reprinted.')
        print(head)
        return 0

    # A FIRST POINT IS NOT PROGRESS. The mark is keyed on the model, the beta
    # configuration and the scored set, so any of those changing starts a fresh
    # mark and the first point after it beats nothing. That printed "PROGRESS"
    # when p_m left the scored set, again when the second beta type came back,
    # and would print it after every model change -- three times in one evening,
    # each time announcing an improvement that had not happened.
    first = old_sq is None
    print('FIRST POINT in this economy -- nothing to compare against yet.\n' if first
          else 'PROGRESS -- full table below.\n' if improved
          else 'loss unchanged; table printed on request.\n')
    print(head + '\n')
    rows = []
    for p, mo in OWN:
        val = v.get(p, '-')
        if mo in m:
            a, tv = m[mo]
            # A BANDED MOMENT IS NOT MISSING ITS TARGET BY THE DISTANCE TO ONE
            # EDGE. beta scores zero anywhere in 3.0-4.5, so printing it against
            # 3.0 said "+106.9%" for a value the loss was charging 50.9 for, and
            # the two numbers disagreeing in the same row is exactly the kind of
            # thing that gets read as the loss being broken.
            if mo in BAND:
                lo, hi = BAND[mo]
                tgt = f'{lo:g}-{hi:g}'
                gp = 'in band' if lo <= a <= hi else f'{100*gap(mo, m[mo]):+.1f}% out'
            else:
                tgt, gp = f'{tv:.5f}', f'{(a/tv-1)*100:+.1f}%'
            rows.append((g.get(mo, -1.0), p, val, mo, f'{a:.5f}', tgt, gp,
                         NOTE.get(mo, '')))
        else:
            rows.append((-2.0, p, val, mo, 'not measured', '-', '-', NOTE.get(mo, '')))
    # EVERY MEASURED MOMENT GETS A ROW, not only the owned ones and the conceded
    # ones. h_2 fell out of the table entirely the moment the cheapest rung was
    # reassigned to emp_homeless: it was no longer in OWN, and it is not in SKIP
    # because the author reversed its concession, so it matched neither loop and
    # printed nowhere -- while still being SCORED and still sitting at minus
    # twenty-seven per cent. A moment that counts against the loss and appears in
    # no row is the worst thing this table can do.
    shown = {mo for _, mo in OWN}
    for k in sorted(set(m) - shown):
        a, tv = m[k]
        note = NOTE.get(k, '')
        if k not in SKIP and k not in UNSCORED and not note:
            note = 'SCORED but no parameter brackets on it'
        rows.append((-2.0, '(no instrument)', '-', k, f'{a:.5f}', f'{tv:.5f}',
                     f'{(a/tv-1)*100:+.1f}%', note))
    rows.sort(reverse=True)
    print(f'{"parameter":42}{"value":>12}  {"moment":12}{"model":>12}{"target":>12}{"gap":>9}')
    for s, p, val, mo, a, tv, gp, note in rows:
        star = ' *' if 0 <= s <= .10 else '  '
        print(f'{p:42}{str(val):>12}  {mo:12}{a:>12}{tv:>12}{gp:>9}{star}'
              + (f'  {note}' if note else ''))
    print('\n* inside ten per cent. kappa_ued and kappa_uem are outputs on the '
          "author's instruction, not targets.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
