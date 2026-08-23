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
    out = {}
    for m in re.finditer(r'distance_(\w+)\s*=\s*abs\(([^\n]*?)\)\s*$', src, re.M):
        name, expr = m.group(1), m.group(2).strip()
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
    'voucher_probability': 'probability_of_voucher_benchmark_used',
    'employment_multiplier': 'multiple_of_probabilities_of_employment_if_addicted',
    'separation_rate': 'probability_becoming_unemployed',
    'smallest_house_size': 'smallest_rental_relative_to_lowest_income',
    'probability_of_becoming_addicted': 'lambda_addiction',
}


def param_values(path):
    """Each parameter's own value, as the model last printed it.

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
    out = {}
    for m in re.finditer(r'(?m)^\s*([a-z_][a-z_0-9]*)=\s*'
                         r'([-+]?[0-9]*\.?[0-9]+(?:[EDed][-+]?[0-9]+)?)\s*$', txt):
        name, v = m.group(1), m.group(2)
        if name.startswith(('distance_', 'previous_', 'stopping_rule_')):
            continue
        try:
            out[name] = float(v.replace('D', 'E').replace('d', 'e'))
        except ValueError:
            pass
    return out


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
    'model_housing_size_dist_1_1': 'model_housing_size_dist_1',
    'model_housing_size_dist_1_housing_status_grid_size_1':
        'model_housing_size_dist_3',
}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)

    printed = export_moments.parse(sys.argv[1])
    consts = json.load(open(os.path.join(HERE, 'fortran_numbers.json')))
    pair, rule = pairs(), rules()

    live = live_distances(sys.argv[1])
    frozen = zero_adjusters()
    values = param_values(sys.argv[1])

    rows, held, missing, seen = [], [], [], {}
    for name, (model_expr, target_expr) in sorted(pair.items()):
        label = export_moments.sanitise(model_expr)
        label = ALIAS.get(label, label)
        target_name = 'f_' + re.sub(r'\(\d+\)', '', target_expr)
        if label not in printed or target_name not in consts:
            flag = consts.get('f_include_' + name)
            if flag is None or float(flag) != 0:
                missing.append((name, model_expr, target_expr))
            continue
        model, target = printed[label], float(consts[target_name])
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
            continue

        # A PARAMETER WITH A ZERO ADJUSTER IS NOT BEING CALIBRATED, so it has no
        # place in a table of the ones that are. It was shown as "held" with its
        # gap, which invited the gap to be read as a miss: the discount factor on
        # the child sat at the top of the table at a hundred per cent off while
        # nothing was moving it. Homeownership being switched off is what zeroes
        # these, and they return the moment it is switched back on.
        status = ''
        if (name in frozen or (name in live and live[name] == 0.0)) and gap > 1e-6:
            continue

        clears = name in rule and abs(model - target) <= rule[name]
        if clears:
            status = 'ON TARGET'
        val = values.get(PARAM_NAME.get(name, name))

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
            g, nm, mo, ta, cl, vv, st = rows[i]
            rows[i] = (g, nm + '+' + name, mo, ta, cl or clears,
                       vv if vv is not None else val, st or status)
            continue
        seen[key] = len(rows)
        rows.append((gap, name, model, target, clears, val, status))

    rows.sort(reverse=True)
    # THE UNREPORTABLE ONES ARE ROWS TOO, at the foot with a status rather than
    # in a footnote, because they are calibrated and moving like the rest.
    for name, model_expr, target_expr in missing:
        rows.append((-1.0, name, None, None, False,
                     values.get(PARAM_NAME.get(name, name)), 'no scalar moment'))

    w = max(len(r[1]) for r in rows) + 2
    print(f'{"parameter":{w}s} {"value":>12s} {"model":>13s} {"target":>13s} '
          f'{"off by":>9s}  status')
    print('-' * (w + 62))
    for gap, name, model, target, clears, val, status in rows:
        v = '--' if val is None else f'{val:.6g}'
        mo = '--' if model is None else f'{model:.6g}'
        ta = '--' if target is None else f'{target:.6g}'
        off = '--' if model is None else f'{gap*100:.1f}%'
        print(f'{name:{w}s} {v:>12s} {mo:>13s} {ta:>13s} {off:>9s}  {status}')
    print('-' * (w + 62))
    live_rows = [r for r in rows if r[2] is not None]
    print(f'{sum(1 for r in live_rows if r[4])} of {len(live_rows)} on target, '
          f'{sum(1 for r in live_rows if not r[4] and r[0] <= 0.03)} within three per cent'
          f'; {len(rows)} parameters calibrated internally')


if __name__ == '__main__':
    main()
