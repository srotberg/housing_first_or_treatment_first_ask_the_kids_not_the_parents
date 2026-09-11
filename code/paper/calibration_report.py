"""Every parameter the model calibrates internally, in ONE table.

HOW TO REPORT A CALIBRATION, AND HOW THIS GOT IT WRONG THREE TIMES.

The reader wants one list: every parameter that is being calibrated, the value it
currently holds, the moment it is aimed at, and how far off it is. Anything that
splits that list hides rows, and each of the three splits this file grew hid a
different set.

1. A row per PARAMETER rather than per MOMENT double counted the two moments that
   move two parameters each, so a fourteen moment table read as sixteen and the
   median counted those two twice.

2. Parameters whose moment is not a scalar the report can evaluate -- a vector, an
   expression, a target that is not a declaration -- were pushed into a footnote
   with their names only. Seven calibrated parameters moving every loop looked
   inert because of it.

3. The value column was read by the row's name, and a row is named for the
   parameter as the paper calls it while the model prints the Fortran variable.
   Where the two differ the column was blank, which reads as "not calibrated"
   rather than "looked in the wrong place". PARAM_NAME below is the fix and it
   has to be extended whenever a row is added.

So: ONE table, every internally calibrated parameter in it, a status column
saying why a row has no gap rather than removing the row. The only parameters
dropped entirely are those whose own include flag is zero, because those are
switched off in the model rather than merely unreportable, and they come back the
moment the flag does.

Read the parameter's value from a pattern ANCHORED to the start of its line. The
model prints distance_X= directly under X=, and this project has twice read the
distance and called it the parameter.
"""


import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FORTRAN = os.path.normpath(os.path.join(HERE, '..',
                                        'housing_first_or_treatment_first_SR_v1.f90'))

sys.path.insert(0, HERE)
import export_moments


def pairs():
    """parameter -> (model quantity, data target), read out of the Fortran."""
    src = open(FORTRAN, errors='replace').read()
    src = re.sub(r'&\s*\n\s*', '', src)            # join continuations
    # A DISTANCE WRITTEN THROUGH A NAMED GAP IS STILL A DISTANCE. Some blocks
    # compute the gap once, use it for the adjuster's sign test AND for the
    # update, and then write distance_X=abs(gap_X_1). Reading only the inline
    # form dropped three parameters that are calibrated every loop and never
    # appeared in the report at all: beta against wealth over output, b against
    # the participation rate, and the child's penalty against the ratio of
    # disorder rates across generations. Follow the gap back to where it is
    # assigned. A gap assigned in two places is ambiguous and is skipped; both
    # of those (gap_house_size_1, for h_2 and h_4) already match inline.
    gap_of = {}
    seen_twice = set()
    for m in re.finditer(r'^\s*(gap_\w+)\s*=\s*([^\n!]*?)\s*$', src, re.M):
        g, e = m.group(1), m.group(2).strip()
        if g in gap_of and gap_of[g] != e:
            seen_twice.add(g)
        gap_of[g] = e

    out = {}
    for m in re.finditer(r'distance_(\w+)\s*=\s*abs\(([^\n]*?)\)\s*$', src, re.M):
        name, expr = m.group(1), m.group(2).strip()
        if expr in gap_of and expr not in seen_twice:
            expr = gap_of[expr]
        hit = re.match(r'^(.+?)\s*-\s*(\w*_data(?:\(\d+\))?)$', expr)
        if hit:
            out.setdefault(name, (hit.group(1).strip(), hit.group(2).strip()))
    return out


def rules():
    """parameter -> stopping rule, read out of the declarations."""
    got = {}
    pat = re.compile(r'stopping_rule_(\w+)\s*=\s*([0-9eEdD\.\*\+\-\(\)]+)')
    for line in open(FORTRAN, errors='replace'):
        s = line.strip()
        if not s.startswith('real(8)'):
            continue
        for name, expr in pat.findall(s):
            try:
                got.setdefault(name, float(eval(expr.replace('d0', 'e0').replace('D0', 'e0'),
                                                {'__builtins__': {}}, {})))
            except Exception:
                pass
    return got


def live_distances(log):
    """parameter -> the distance the run last printed for it.

    The sweep zeroes a distance when its adjuster is zero, which is how a
    parameter that is deliberately not calibrated announces itself. Reading that
    beats evaluating every adjuster declaration against every flag in the file.
    """
    got = {}
    pat = re.compile(r'distance_(\w+?)(?:\(1\))?=\s*([-\d.]+(?:[eEdD][-+]?\d+)?)')
    for line in open(log, errors='replace'):
        for name, val in pat.findall(line):
            try:
                got[name] = float(val.replace('D', 'E').replace('d', 'e'))
            except ValueError:
                pass
    return got


# THE ROW'S NAME IS NOT ALWAYS THE VARIABLE'S NAME. A row is named for the
# parameter as the paper calls it; the model prints the Fortran variable, and for
# three of them the two differ, which is why their value column was empty while
# the parameter was moving every loop.
PARAM_NAME = {
    # b is declared and printed as addiction_scalar_1; the block that calibrates
    # it is named for the parameter without the suffix.
    'addiction_scalar': 'addiction_scalar_1',
    'voucher_probability': 'probability_of_voucher_benchmark_used',
    'employment_multiplier': 'multiple_of_probabilities_of_employment_if_addicted',
    'separation_rate': 'probability_becoming_unemployed',
    'smallest_house_size': 'smallest_rental_relative_to_lowest_income',
    'probability_of_becoming_addicted': 'lambda_addiction',
}


def param_values(path):
    """Each parameter's value AT THE SOLVE, and the value the update moved it to.

    THE VALUE COLUMN WAS ONE UPDATE AHEAD OF THE MODEL COLUMN, and the row it
    made was unreadable. A loop prints its moments and THEN its updated
    parameters, and this read the last print in the file, so the table paired a
    post-update parameter with the moment its pre-update value had produced.
    It showed size_homelessness = 0 beside homelessness of 9.2 per cent, which
    reads as a parameter that does nothing; what happened was that 9.2 per cent
    was produced at 0.3747 and the update then slammed it to zero in a single
    step. The author caught it by noticing the pair could not both be true.

    So split on the aggregation, which runs before the moments and long before
    the update block: the last print at or before it is the value that produced
    what is reported, and the last print overall is what the next loop starts
    from. A sweep log has no update block, so the two coincide.

    ANCHORED, because the model prints distance_X= directly under X= and an
    unanchored name is a substring of its own distance line. Reading the
    distance and calling it the parameter is a mistake this project has already
    made once, in the supervisor's watch list, and it reads as a parameter
    converging smoothly to zero.
    """
    try:
        txt = open(path, errors='ignore').read()
    except OSError:
        return {}
    series = {}
    for m in re.finditer(r'(?m)^\s*([a-z_][a-z_0-9]*)=\s*'
                         r'([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)\s*$', txt):
        name, v = m.group(1), m.group(2)
        if name.startswith(('distance_', 'previous_', 'stopping_rule_')):
            continue
        try:
            val = float(v.replace('D', 'E').replace('d', 'e'))
        except ValueError:
            continue
        series.setdefault(name, []).append((m.start(), val))
    return txt, series


def value_at(series, txt, name, label):
    """(value that produced the reported moment, value after the update).

    NEITHER A FIXED ANCHOR NOR THE MOMENT'S OWN LINE WORKS, and both were tried.
    The model computes its moments during the solve, runs the update block,
    and only THEN prints the moments, so in the log the new parameter appears
    ABOVE the moment its old value produced: size_homelessness printed 0.37466
    up to line 4928, 0 at 4931, and model_fraction_homeless = 0.0921 at 4997.
    Anchoring on the moment therefore picks the post-update value, which is the
    error this was written to remove.

    What is reliable is that the update block writes each parameter ONCE, at the
    end, so the last CHANGE in the log is the update and the value before it is
    the value the solve ran at. Collapse the series to consecutive distinct
    values: the last is what the next loop starts from, the one before it is
    what produced the moments being reported. A parameter that never moved has
    one value and the two coincide.
    """
    del txt, label
    got = series.get(name)
    if not got:
        return None, None
    seq = []
    for _, v in got:
        if not seq or seq[-1] != v:
            seq.append(v)
    return (seq[-2] if len(seq) >= 2 else seq[-1]), seq[-1]


def zero_adjusters():
    """The parameters whose adjuster is zero, from the declarations.

    The sweep guards each update on its adjuster, so a zero one means the
    parameter is deliberately frozen and its moment is not a miss. Three are
    frozen in this paper because homeownership is switched off. Not all of these
    print a distance, so reading the log alone misses them, and the declarations
    are where the fact actually lives.
    """
    src = open(FORTRAN, errors='replace').read()
    src = re.sub(r'&\s*\n\s*', '', src)
    syms = {}
    for m in re.finditer(r'^\s*(?:integer|real\(8\))\s*,\s*parameter\s*::\s*(\w+)\s*=\s*([^!\n]+)',
                         src, re.M):
        try:
            syms[m.group(1)] = eval(m.group(2).replace('d0', 'e0').replace('D0', 'e0'),
                                    {'__builtins__': {}}, dict(syms))
        except Exception:
            pass
    frozen = set()
    for m in re.finditer(r'^\s*real\(8\)\s*(?:,\s*parameter\s*)?::\s*(\w+)_adjuster\s*=\s*([^!\n]+)',
                         src, re.M):
        try:
            if eval(m.group(2).replace('d0', 'e0').replace('D0', 'e0'),
                    {'__builtins__': {}}, dict(syms)) == 0:
                frozen.add(m.group(1))
        except Exception:
            pass
    return frozen


# WHAT THE FORTRAN CALLS IT AGAINST WHAT IT PRINTS. The distance expressions name
# variables; the write statements use human labels, and the two do not always
# agree. Nine targeted moments went unreported for that reason alone, including
# most of the ones this paper is about. Each entry here is a variable name on the
# left and the sanitised print label on the right, checked against the log.
ALIAS = {
    'model_smi_share_of_homeless': 'SMI_share_of_homeless',
    'model_employment_rate_given_smi': 'employment_rate_given_SMI',
    'model_employed_share_of_homeless': 'employed_share_of_homeless',
    'model_homeless_income_share': 'homeless_income_share',
    'drug_share_weighted_1': 'drug_share_weighted_by_their_population_shares',
    'child_use_gap_1': 'model_child_use_gap',
    # THE FORTRAN ARRAY IS ZERO INDEXED AND THE PRINT IS NOT. Both
    # model_housing_size_dist and housing_size_dist_data are declared over
    # 0:housing_status_grid_size-1, so element (1,1) is the SECOND rung, while
    # export_moments names the printed vector _1, _2, _3 in print order. The map
    # therefore shifts by one, and it was not shifted here: h_3's row scored the
    # cheapest rung against the middle rung's target.
    'model_housing_size_dist_1_0': 'model_housing_size_dist_1',
    'model_housing_size_dist_1_1': 'model_housing_size_dist_2',
    'model_housing_size_dist_1_housing_status_grid_size_1':
        'model_housing_size_dist_3',
    # FOUR MOMENTS THE MODEL PRINTS UNDER A DIFFERENT NAME THAN THE UPDATE USES.
    # Each of these read "no scalar moment" and sat at the foot of the table
    # with no value, no target and no gap, which reads as a parameter that is
    # not being calibrated rather than one the report could not find. All four
    # move every loop.
    # NOT ALIASED TO govt_spending_on_food_stamps/model_output, THOUGH IT IS THE
    # ONLY FOOD STAMP RATIO THE RUN PRINTS. The update divides by average LABOUR
    # INCOME and the print divides by OUTPUT, so the aliased row scored a gap of
    # 99 per cent against a target the calibration was never comparing to. A
    # moment printed under one denominator is not the moment updated under
    # another; the Fortran now prints the ratio its own update uses.
    'model_recovery_housed_over_model_recovery_homeless': 'model_recovery_ratio',
    # gamma's moment is the RENTERS series. The Fortran printed it under the
    # label "model_avg_housing_spending_all", which a second print further down
    # the loop uses for the genuinely all households series, so the label alone
    # picked whichever came first. The print is renamed; this entry is what the
    # report reads.
    'model_avg_housing_spending_renters': 'model_avg_housing_spending_renters',
    'model_bottom_half_earnings_share': 'bottom_half_s_share_of_productivity',
    'model_vsl_ratio_1': 'model_value_of_life_over_model_average_labour_income',
    # THREE THAT ARRIVED WITH THE NAMED GAP FIX, and print under their own names.
    'wealth_to_output_model_1': 'wealth_to_output_model',
    'child_sud_ratio_model_1': 'child_SUD_ratio_model',
}

# A TARGET THAT LIVES IN THE LOG RATHER THAN IN A DECLARATION. The rental
# ladder's data shares are a Fortran parameter ARRAY, so export_consts.py has no
# scalar for housing_size_dist_data(1); the run prints the vector and
# export_moments names its elements. Same zero indexed shift as above.
TARGET_IN_LOG = {
    'housing_size_dist_data(0)': 'housing_size_dist_data_1',
    'housing_size_dist_data(1)': 'housing_size_dist_data_2',
    'housing_size_dist_data(2)': 'housing_size_dist_data_3',
}



def settled_note(log):
    """Say how many loops the log holds and whether the last one moved."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from loop_trace import read as read_loops
        loops, _ = read_loops(log)
    except Exception:
        return
    n = len(loops)
    if n <= 1:
        print(f'ONE moment block in this log: nothing here says whether the run '
              f'settled, and a single loop is an iterate, not an equilibrium.\n')
        return
    moved = []
    for name in ('b', 'lambda_d', 'theta'):
        a, bb = loops[-2].get(name), loops[-1].get(name)
        if a and bb and a[0]:
            moved.append((name, (bb[0] - a[0]) / a[0] * 100))
    worst = max((abs(m) for _, m in moved), default=0.0)
    tail = '   '.join(f'{k} {v:+.1f}%' for k, v in moved)
    if worst > 1.0:
        print(f'{n} moment blocks; this is loop {n}, and it MOVED from loop {n-1}: '
              f'{tail}.')
        print('   The parameters are capped at 0.5 per cent a loop, so a moment '
              'moving further than\n   that is the map still settling. Do not '
              'quote this table as the benchmark.\n')
    else:
        print(f'{n} moment blocks; this is loop {n}, and it is within one per cent '
              f'of loop {n-1}: {tail}.\n')


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)

    # A SWEEP LOG CANNOT BE SCORED, AND SAYS SO RATHER THAN PRETENDING.
    #
    # A sweep point writes its row and STOPS, above most of the moment prints,
    # and it holds every parameter fixed. Read off one, sixteen of twenty five
    # rows come back "no scalar moment" and the nine that do score are scored
    # at whatever b that point ran at -- which, at the top of the grid, is a
    # model with nobody in it: employment given serious mental illness (SMI)
    # reads 0.9997 against 0.3, and four parameters read exactly a hundred per
    # cent off because their moment is zero. Those are artefacts of an empty
    # population, not gaps, and a table that prints them next to the word
    # "target" invites them to be acted on.
    log_text = open(sys.argv[1], errors='replace').read()
    if 'B SWEEP POINT DONE' in log_text:
        print('THIS IS A SWEEP LOG, NOT A CALIBRATION LOG. A sweep point stops')
        print('above most of the moment prints and holds every parameter fixed,')
        print('so the rows below are mostly empty and the ones that score are')
        print('scored on one b at frozen everything else. Read the curve in')
        print('B_SWEEP.tsv instead, and read this table again once the joint')
        print('loop is running.')
        print()

    printed = export_moments.parse(sys.argv[1])
    consts = json.load(open(os.path.join(HERE, 'fortran_numbers.json')))
    pair, rule = pairs(), rules()

    live = live_distances(sys.argv[1])
    frozen = zero_adjusters()
    log_txt, series = param_values(sys.argv[1])

    rows, held, missing, seen, excluded = [], [], [], {}, []
    for name, (model_expr, target_expr) in sorted(pair.items()):
        label = export_moments.sanitise(model_expr)
        label = ALIAS.get(label, label)
        target_name = 'f_' + re.sub(r'\(\d+\)', '', target_expr)
        in_log = TARGET_IN_LOG.get(target_expr)
        if label not in printed or (target_name not in consts and
                                    (in_log is None or in_log not in printed)):
            flag = consts.get('f_include_' + name)
            if flag is None or float(flag) != 0:
                missing.append((name, model_expr, target_expr))
            continue
        model = printed[label]
        target = (float(consts[target_name]) if target_name in consts
                  else printed[in_log])
        gap = abs(model - target) / max(abs(target), 1e-12)

        # A PARAMETER WHOSE ADJUSTER IS ZERO IS NOT BEING CALIBRATED, and its
        # moment is not a miss. The sweep says so itself by zeroing the distance
        # while the gap stays wide, which is the only signal that does not
        # require evaluating the adjuster's declaration against every flag in
        # the file. Three of them are held in this paper because homeownership
        # is switched off, and ranking them alongside live moments overstates
        # what is left to do.
        # A PARAMETER SWITCHED OFF IS NOT A MISS, AND NOT A ROW EITHER.
        # include_rho_d and include_rho_m are zero, and they enter the model as
        # rho**(sud*include_rho), so the multiplier is exactly one: the penalty
        # is absent and its update is gated on the same flag, so nothing moves
        # it. Its adjuster is still non-zero, though, which is why the frozen
        # test below never caught it and rho_m sat in the table at eighty eight
        # per cent off, inflating the median with a gap no parameter owns. A row
        # whose own include flag is off is dropped entirely rather than held: it
        # comes back the moment the flag does.
        # The constants come back as STRINGS, so compare as a number: '0' is
        # not 0 and the test read as always false, which is why rho_m survived
        # a first attempt at this.
        flag = consts.get('f_include_' + name)
        if flag is not None and float(flag) == 0:
            excluded.append((name, 'include_' + name + ' is 0, the channel is off'))
            continue

        # A PARAMETER WITH A ZERO ADJUSTER IS NOT BEING CALIBRATED, so it has no
        # place in a table of the ones that are. It was shown as "held" with its
        # gap, which invited the gap to be read as a miss: the discount factor on
        # the child sat at the top of the table at a hundred per cent off while
        # nothing was moving it. Homeownership being switched off is what zeroes
        # these, and they return the moment it is switched back on.
        status = ''
        if name in frozen and gap > 1e-6:
            excluded.append((name, 'its adjuster is zero, nothing moves it'))
            continue
        if name in live and live[name] == 0.0 and gap > 1e-6:
            excluded.append((name, 'the model zeroes its distance in this configuration'))
            continue

        clears = name in rule and abs(model - target) <= rule[name]
        if clears:
            status = 'ON TARGET'
        # A CORNER IS NOT A LARGE GAP, and the difference decides how the model
        # is allowed to move. Below a tenth of the target or above five times
        # it, the margin the parameter acts on is effectively absent, and the
        # model's move_factor gives that parameter room to escape instead of
        # the one per cent it uses to refine. Flagging it here is what lets the
        # table be read as "is there anything to work with yet".
        elif abs(target) > 1e-12 and (model < 0.1 * target or model > 5 * target):
            status = 'CORNER'
        val, nxt = value_at(series, log_txt, PARAM_NAME.get(name, name), label)

        # ONE ROW PER MOMENT, NOT PER PARAMETER. Two parameters can be moved by
        # the same moment -- h_2 and rho_d both by the employed share of the
        # homeless, and both addiction hazards by the share addicted -- and
        # printed once each they read as two independent misses. The median gap
        # then counts that moment twice, which is how a sixteen row table came
        # to describe fourteen moments. Joined with a plus so the name stays one
        # token: checkpoint() reads this table with a whitespace split.
        key = (label, target_name)
        if key in seen:
            i = seen[key]
            g, nm, mo, ta, cl, vv, st, lb, nx = rows[i]
            rows[i] = (g, nm + '+' + name, mo, ta, cl or clears,
                       vv if vv is not None else val, st or status, lb,
                       nx if nx is not None else nxt)
            continue
        seen[key] = len(rows)
        rows.append((gap, name, model, target, clears, val, status, label, nxt))

    rows.sort(reverse=True)
    # THE UNREPORTABLE ONES ARE ROWS TOO, at the foot with a status rather than
    # in a footnote, because they are calibrated and moving like the rest.
    for name, model_expr, target_expr in missing:
        rows.append((-1.0, name, None, None, False,
                     value_at(series, log_txt,
                              PARAM_NAME.get(name, name), None)[0],
                     'no scalar moment', None,
                     value_at(series, log_txt,
                              PARAM_NAME.get(name, name), None)[1]))

    # THE MOMENT IS NAMED, not just valued. A table of parameter, value, model
    # and target says which numbers disagree but not what the parameter is
    # being asked to match, and the name is the only thing that says whether
    # the pairing is the intended one -- which is how h_2 was found chasing the
    # employed share of the homeless while the ladder's curvature ran on the
    # smallest size share.
    # WHICH LOOP THIS TABLE IS, BEFORE THE TABLE ITSELF.
    #
    # This report reads the LAST value the log printed for each quantity, which
    # is right once a run has settled and wrong while it is still settling. On
    # 11 September the benchmark's log held three different economies -- b at
    # 9.27, 6.75 and 6.48 per cent -- because compute_expected_child_value reads
    # the current value function, so the child term is iterated once per loop
    # with no convergence test on it. Every benchmark figure reported up to that
    # morning had been read off loop 1 and none of them said so.
    #
    # A table that does not say which loop it is cannot be checked, so the count
    # and the last loop's movement go above it. The threshold is one per cent
    # because the parameters themselves are capped at half of one per cent a
    # loop: a moment moving further than its instruments possibly could is the
    # map still settling, not the search working.
    settled_note(sys.argv[1])
    w = max(len(r[1]) for r in rows) + 2
    mw = max([len(r[7]) for r in rows if r[7]] + [len('moment')]) + 2
    print(f'{"parameter":{w}s} {"value":>12s} {"-> after":>12s} {"moment":{mw}s} '
          f'{"model":>13s} {"target":>13s} {"off by":>9s}  status')
    print('-' * (w + mw + 76))
    for gap, name, model, target, clears, val, status, label, nxt in rows:
        v = '--' if val is None else f'{val:.6g}'
        if nxt is None:
            nv = '--'
        elif val is not None and abs(nxt - val) <= 1e-12 * max(abs(val), 1.0):
            nv = '='
        else:
            nv = f'{nxt:.6g}'
        mo = '--' if model is None else f'{model:.6g}'
        ta = '--' if target is None else f'{target:.6g}'
        off = '--' if model is None else f'{gap*100:.1f}%'
        lb = '--' if label is None else label
        print(f'{name:{w}s} {v:>12s} {nv:>12s} {lb:{mw}s} '
              f'{mo:>13s} {ta:>13s} {off:>9s}  {status}')
    print('-' * (w + mw + 76))
    live_rows = [r for r in rows if r[2] is not None]
    print(f'{sum(1 for r in live_rows if r[4])} of {len(live_rows)} on target, '
          f'{sum(1 for r in live_rows if not r[4] and r[0] <= 0.03)} within three per cent'
          f'; {len(rows)} parameters calibrated internally')

    # EVERY PARAMETER IS EITHER A ROW OR A NAMED EXCLUSION, never absent. The
    # row count moved between logs -- twenty three off a calibration log and
    # twenty five off a sweep -- because a parameter the model happened not to
    # print was silently dropped, and a table that quietly changes length cannot
    # be checked for completeness by reading it. Anything not shown above is
    # listed here with the reason it is not being calibrated.
    if excluded:
        print()
        print(f'{len(excluded)} parameter(s) NOT calibrated in this configuration, '
              f'and therefore not rows above:')
        for name, why in sorted(excluded):
            print(f'  {name:44s} {why}')
    print(f'\naccounted for: {len(rows)} calibrated + {len(excluded)} not calibrated '
          f'= {len(rows) + len(excluded)} parameters with a target in the Fortran')


if __name__ == '__main__':
    main()
