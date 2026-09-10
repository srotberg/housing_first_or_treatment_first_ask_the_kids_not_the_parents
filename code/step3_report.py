#!/usr/bin/env python3
"""The full gap table for a step-3 point1 run, read from the log.

WHY NOT gaps.py. That reads point files, and run_variant.sh deliberately writes
none: a variant has no target for the calibration machinery to score. The
scored/unscored/conceded sets are imported from gaps.py rather than retyped, so
this table and the author's own loss cannot disagree about what counts.

READ THE LAST BLOCK. `print_all_moments` runs twice on a point1 run, once before
the frozen-equilibrium loop and once after, and `omega` prints twice inside each.
The pre-frozen block is taken off a state that is not an equilibrium: quoting it
produced 0.0824 against a true 0.00755 in this project, a factor of eleven.
"""
import io, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CODE = "/home/user/housing_first_or_treatment_first/code"
sys.path.insert(0, CODE)
import gaps

ROW = re.compile(r'MOMENT\s+(\S+)\s+(\S+)\s+model=\s*([-+0-9.eEdD]+)\s+target=\s*([-+0-9.eEdD]+)')
ROW2 = re.compile(r'MOMENT\s+(\S+)\s+.*?model=\s*([-+0-9.eEdD]+)\s+target=\s*([-+0-9.eEdD]+)')


def f(x):
    return float(str(x).replace('D', 'E').replace('d', 'e'))


def main(path):
    txt = io.open(path, errors='replace').read()

    if 'FROZEN CONVERGED' in txt:
        frozen = 'CONVERGED'
    elif 'FROZEN STALLED' in txt:
        frozen = 'STALLED at the solver floor'
    elif 'FROZEN NOT AT TOLERANCE' in txt:
        frozen = 'NOT AT TOLERANCE'
    else:
        frozen = 'NO FROZEN BLOCK -- this is not a point1 run'
    cut = txt.rfind('FROZEN')
    if cut < 0:
        print('!! no frozen block at all; every number below is pre-frozen')
        cut = 0
    tail = txt[cut:]

    rows = {}
    for m in ROW2.finditer(tail):
        rows[m.group(1)] = (f(m.group(2)), f(m.group(3)))

    own = {mom: par for par, mom in gaps.OWN}

    # THREE ROWS gaps.OWN DOES NOT CARRY, read out of the Fortran's own update
    # block rather than guessed at. Two of them are moments the author has taken
    # out of the loss, so the report table never needed the instrument; the third
    # is an omission.
    #
    #   lambda_m   IS internally calibrated -- distance_lambda_m sits in the outer
    #              do while and the update at 42365 steps it on
    #              model_smi_share_of_homeless against smi_share_of_homeless_data,
    #              which is exactly this moment. gaps.OWN simply has no row for it.
    #              Same class of fault as the y_h and ssi_floor_level rows that
    #              file already records: the report named one parameter and the
    #              walk moved another. NOT fixed here, because gaps.py is the
    #              author's report and editing it mid-run is not step 3's job.
    #   kappa_ued  multiple_of_probabilities_of_employment_if_addicted, per
    #              suggest_next.py. Unscored, so it has no gaps.OWN row.
    #   h_3        largest_house_size in suggest_next.py, but the ladder ruling of
    #              5 September assigns h_3 = 2 x h_2, so it is a RATIO and has no
    #              instrument of its own. That is what "conceded, a fact about a
    #              grid the model chose" means.
    own.setdefault('lambda_m', 'lambda_m   [from the Fortran, not gaps.OWN]')
    own.setdefault('kappa_ued', 'multiple_of_probabilities_..._if_addicted')
    own.setdefault('h_3', '(none: h_3 = 2 x h_2 by the ladder ruling)')
    own.setdefault('w_bot', '(none: discount_factor_impatient retired)')
    own.setdefault('burden50', '(none: reported, not targeted)')
    own.setdefault('y_u', '(none: mortality pinned at 8 by the author)')
    unscored = set(gaps.UNSCORED) | set(gaps.SKIP)

    print(f'frozen equilibrium: {frozen}')
    for line in re.findall(r'^\s*FROZEN (?:PASS|CONVERGED|STALLED|NOT).*$', tail, re.M):
        print('   ' + line.strip()[:150])
    print()
    print(f'{"moment":<14}{"instrument":<46}{"model":>13}{"target":>13}{"gap":>9}  status')
    print('-' * 110)
    worst = []
    for mom in sorted(rows):
        model, target = rows[mom]
        par = own.get(mom, '(no instrument)')
        if abs(target) > 1e-14:
            g = (model - target) / abs(target) * 100.0
            gs = f'{g:+.1f}%'
        else:
            g = None
            gs = 'n/a'
        band = gaps.BAND.get(mom)
        if band and band[0] <= model <= band[1]:
            status = f'in band {band[0]:g}-{band[1]:g}'
            g = 0.0
        elif mom in gaps.SKIP:
            status = 'CONCEDED, not scored'
        elif mom in unscored:
            status = 'not scored'
        elif mom in gaps.NOTE:
            status = 'not scored: ' + gaps.NOTE[mom][:40]
        else:
            status = 'scored' + ('' if g is None or abs(g) <= 10 else '   OUT')
            if g is not None:
                worst.append((abs(g), mom, gs))
        print(f'{mom:<14}{par:<46}{model:>13.6g}{target:>13.6g}{gs:>9}  {status}')
    print('-' * 110)
    worst.sort(reverse=True)
    if worst:
        print('scored moments outside the author\'s ten per cent rule, worst first:')
        out = [w for w in worst if w[0] > 10]
        if not out:
            print('   NONE. Every scored moment is inside ten per cent.')
        for a, mom, gs in out:
            print(f'   {mom:<14}{gs}')
        print(f'\nminimax over the scored set: {worst[0][0]:.1f}% on {worst[0][1]}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1]))
