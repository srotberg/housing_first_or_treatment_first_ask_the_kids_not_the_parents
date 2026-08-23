"""
Where every calibrated moment stands, model against target, from the run itself.

WHY THIS EXISTS. The sweep prints one distance per parameter and stops there, so
reading how a calibration is doing means holding forty stopping rules and forty
data targets in your head at once. Worse, a distance is an absolute number
against a target on its own scale, so 0.0368 and 59.4 say nothing about which is
the bigger miss until you know both scales.

WHAT IT DOES. Each parameter's distance in the Fortran is written as
abs(<model quantity> - <data target>), so the pairing is already in the source
and does not have to be maintained by hand here. This joins those three things:
the pair, parsed out of the Fortran; the model side, taken from the run's own
output by export_moments.py's parser; and the target, from the declarations by
way of fortran_numbers.json. It reports the gap in RELATIVE terms so the misses
can be ranked against each other, and says whether each clears its own rule.

The three convergence checks that compare a quantity to its own previous value
rather than to data (average labour income, median income, average net wealth)
are reported separately, since a small number there means "stopped moving" and
not "matches anything".

Run:  python3 calibration_report.py <run.log>
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

        if (name in frozen or (name in live and live[name] == 0.0)) and gap > 1e-6:
            held.append((name, model, target))
            continue

        clears = name in rule and abs(model - target) <= rule[name]
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
            g, nm, mo, ta, cl, vv = rows[i]
            rows[i] = (g, nm + '+' + name, mo, ta, cl or clears, vv if vv is not None else val)
            continue
        seen[key] = len(rows)
        rows.append((gap, name, model, target, clears, val))

    rows.sort(reverse=True)
    print(f'{"parameter":50s} {"value":>12s} {"model":>13s} {"target":>13s} {"off by":>9s}  ')
    print('-' * 105)
    for gap, name, model, target, clears, val in rows:
        mark = 'ON TARGET' if clears else ''
        v = '--' if val is None else f'{val:.6g}'
        print(f'{name:50s} {v:>12s} {model:13.6g} {target:13.6g} {gap*100:8.1f}%  {mark}')
    print('-' * 105)
    print(f'{sum(1 for r in rows if r[4])} of {len(rows)} on target, '
          f'{sum(1 for r in rows if not r[4] and r[0] <= 0.03)} within three per cent')

    if held:
        print('\nheld, not calibrated: the sweep zeroes these distances, so the gap '
              'is not a miss')
        for name, model, target in held:
            v = values.get(PARAM_NAME.get(name, name))
            vs = '--' if v is None else f'{v:.6g}'
            print(f'  {name:32s} value {vs:>12s}   model {model:12.6g}   '
                  f'its target {target:12.6g}')

    if missing:
        # THE PARAMETER IS STILL WORTH SHOWING even when its moment is a vector,
        # an expression the report cannot evaluate, or a target that is not a
        # declaration. These are calibrated parameters moving every loop, and
        # printing only their names made them look inert.
        print('\nmoment not reportable as a scalar, but the parameter is live:')
        for name, model_expr, target_expr in missing:
            v = values.get(PARAM_NAME.get(name, name))
            vs = '--' if v is None else f'{v:.6g}'
            print(f'  {name:32s} value {vs:>12s}   {model_expr} vs {target_expr}')


if __name__ == '__main__':
    main()
