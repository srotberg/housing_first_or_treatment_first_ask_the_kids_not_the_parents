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


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        raise SystemExit(2)

    printed = export_moments.parse(sys.argv[1])
    consts = json.load(open(os.path.join(HERE, 'fortran_numbers.json')))
    pair, rule = pairs(), rules()

    rows, missing = [], []
    for name, (model_expr, target_expr) in sorted(pair.items()):
        label = export_moments.sanitise(model_expr)
        target_name = 'f_' + re.sub(r'\(\d+\)', '', target_expr)
        if label not in printed or target_name not in consts:
            missing.append((name, model_expr, target_expr))
            continue
        model, target = printed[label], float(consts[target_name])
        gap = abs(model - target) / max(abs(target), 1e-12)
        clears = name in rule and abs(model - target) <= rule[name]
        rows.append((gap, name, model, target, clears))

    rows.sort(reverse=True)
    print(f'{"parameter":34s} {"model":>13s} {"target":>13s} {"off by":>9s}  ')
    print('-' * 76)
    for gap, name, model, target, clears in rows:
        mark = 'ON TARGET' if clears else ''
        print(f'{name:34s} {model:13.6g} {target:13.6g} {gap*100:8.1f}%  {mark}')
    print('-' * 76)
    print(f'{sum(1 for r in rows if r[4])} of {len(rows)} on target, '
          f'{sum(1 for r in rows if not r[4] and r[0] <= 0.03)} within three per cent')

    if missing:
        print('\nnot reported, because the run did not print the model side as a '
              'scalar or the target is not a declaration:')
        for name, model_expr, target_expr in missing:
            print(f'  {name:32s} {model_expr} vs {target_expr}')


if __name__ == '__main__':
    main()
