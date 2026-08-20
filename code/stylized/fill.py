"""
Fill the note's inline numbers straight from the model.

Every number quoted in the prose of housing_first_children_later.tex is written as a
placeholder @@name@@ in housing_first_children_later.src.tex, and this file computes each one
and writes housing_first_children_later.tex. Nothing in the note can then drift away from the
code, which is the same discipline the tables already follow.

Run:  python3 fill.py
"""

import json
import os
import numpy as np
from stylized import P, with_, value1, H_RATIO
from calibrate import YG, W, stats, bracket, TARGET
from children import (child_grid, shifted, DEL_D, DEL_H, RATIO_TARGET,
                      ratio_h)
from frontier import TH_BREAK

HERE = os.path.dirname(os.path.abspath(__file__))
WRITE = os.path.normpath(os.path.join(HERE, '..', '..', 'writing'))
WW = W / W.sum()


def compare(a, b, name, more='higher', less='lower', same='the same as',
            tol=0.0):
    """Words for an inequality, so a sentence turns when its numbers do.

    Returns {name+'dir'} for the direction word and {name+'gap'} for the size of
    the gap, both as strings the prose can quote. Any sentence in the paper that
    asserts one quantity is above or below another should take its direction
    word from here, because the assertion is a result and results move.
    """
    d = a - b
    w = more if d > tol else (less if d < -tol else same)
    return {name + 'dir': w, name + 'gap': f'{abs(d):.4f}'}


def numbers(base, fig):
    """The prose's numbers. `fig` is figure_numbers.json, already loaded."""
    out = dict(fig)
    raw = dict(out.pop('_raw'))
    wel = _welfare()
    raw.update(wel.pop('_raw'))
    out.update(wel)
    out.update(_children())
    pc = lambda z, n=2: f'{100*z:.{n}f}'

    out['beta'] = f'{base.beta:.3f}'
    out['R'] = f'{base.R:.3f}'
    out['u0'] = f'{base.u0:.3f}'
    out['u1'] = f'{base.u1:.4f}'
    out['phi0'] = f'{base.phi0:.2f}'
    out['pV'] = f'{base.pV:.2f}'
    out['phi1'] = f'{base.phi0 * (1.0 - base.kap):.2f}'
    out['kap'] = f'{base.kap:.2f}'
    out['dth0'] = f'{100*(1.0 - base.phi0):.0f}'
    out['dth1'] = f'{100*(1.0 - base.phi0*(1.0 - base.kap)):.0f}'
    out['beta_ann'] = f'{base.beta_ann:.3f}'
    out['vsl_t'] = f'{TARGET["vsl"]:.0f}'
    out['dshare_t'] = f'{100*TARGET["dshare"]:.0f}'
    out['pvbase'] = f'{base.pV:.3f}'

    # THE GRID, quoted in the footnote where the income distribution is
    # introduced. The pooled share is read off the weights rather than typed,
    # so it cannot drift from the grid the model is actually solved on.
    out['gridn'] = f'{len(YG)}'
    out['poolpct'] = f'{100.0 * W[0] / W.sum():.1f}'

    # THE HOUSING AND VOUCHER SETTINGS. Every one of these is also a row of
    # Table 1, and the prose used to type them again beside it. They are set
    # rather than calibrated, so they move rarely, which is exactly why typing
    # them is dangerous: the copy in the prose survives a change to the class
    # for as long as nobody reads that sentence against the table.
    # AS A MULTIPLE OF AVERAGE INCOME, which is the convention Table 1 prints it
    # in. Average income is one by construction, so the two agree today; they
    # would stop agreeing silently if the grid ever moved off that normalisation.
    out['h3'] = f'{base.h_lg / float((WW * YG).sum()):.2f}'
    out['h2frac'] = f'{H_RATIO:g}'
    out['kV'] = f'{base.kV:.2f}'
    out['smrd'] = f'{base.smr_d:.0f}'
    out['th_break'] = f'{TH_BREAK:.2f}'

    mb = stats(base)
    out['dshare_m'] = f'{100*mb["dshare"]:.2f}'
    # the conversion from use to disorder is IMPLIED here rather than
    # targeted, so it is quoted from the model and never typed into the text
    out['prog_m'] = f'{100*mb["prog"]:.1f}'
    out['sudhl'] = f'{100*mb["sud_of_homeless"]:.0f}'
    out['r_base'] = f'{mb["r_use"]:.2f}'
    out['hshare_m'] = f'{100*mb["housing_share"]:.0f}'
    out['hspend_m'] = f'{100*mb["hspend"]:.1f}'
    # what gamma would have to be with a CONTINUOUS housing choice: the
    # Cobb-Douglas share of non drug spending times (1-theta)
    out['gam_naive'] = f'{0.268 * (1.0 - base.th):.3f}'
    out['th'] = f'{base.th:.2f}'
    out['gam'] = f'{base.gam:.3f}'
    out['lam'] = f'{base.lam:.0f}'

    # one rental size only: the model that fails to calibrate
    out['homeless1'] = pc(stats(with_(base, h_sm=base.h_lg))['homeless'])

    # THE TWO CHANNELS AND THE POLICY EXPERIMENT ARE NOT COMPUTED HERE. Every
    # one of those numbers appears on Figure 1 or Figure 2, so run.py computes
    # it once while it draws the figure and writes it to figure_numbers.json,
    # and _figures() below reads it in. Recomputing them here is what let the
    # note quote an income ratio of 3.33 at half strength beside a figure that
    # showed 4.70.
    # THE SENTENCE THAT COMPARES THEM HAS TO TURN WITH THEM. The two outlays
    # are within a fraction of a percent of each other and which is the larger
    # is not robust to a recalibration, so the prose around them is generated
    # from the same comparison rather than typed. A sweep that flipped the sign
    # and left the paragraph saying "more expensive" would be a contradiction no
    # reader could resolve and no test would catch.

    # welfare at universal cover
    # THE WELFARE NUMBERS ARE TABLE 3'S OWN CELLS, written by welfare.py when it
    # built the table and merged into `out` at the top of this function. They are
    # not recomputed here. That includes whether anyone is better off under
    # Treatment First, which is a RESULT and not an assumption: the conditional
    # policy covers a strict subset of what the unconditional one covers, so
    # nobody should gain, and verify.py checks the same property independently.

    # the externality on children
    v1b, useb = child_grid(base, 'HF', base.pV)
    ratio = shifted(useb, DEL_D) / max(shifted(useb, 0.0), 1e-12)
    out['ratio'] = f'{ratio:.1f}'
    out['del_d'] = f'{DEL_D:.2f}'
    out['ratio_t'] = f'{RATIO_TARGET:.0f}'
    out['del_h'] = f'{DEL_H:.2f}'
    out['del_h_pc'] = f'{100*DEL_H:.0f}'
    # UNTARGETED: what delta_h, set from Chetty et al., implies for how much
    # likelier the child of a homeless parent is to be homeless itself
    out['ratio_h'] = f'{ratio_h(base):.2f}'
    # PANEL B OF TABLE 4 IS NOT RECOMPUTED HERE either. children.py writes every
    # cell of it while it builds the table, including the smallest gain over loss
    # anywhere in Panel A, and _children() merges them in at the top of this
    # function. The private cost row is Table 3's population consumption
    # equivalent, and verify.py checks that the two agree.

    v1 = np.array([value1(base, y, 'HF') for y in YG])
    out['minv1'] = f'{v1.min():.2f}'
    return out


# WHAT CHANGED SINCE THE LAST VERSION THE READER SAW, marked rather than
# described. numbers_prev.json holds this same dictionary computed at the
# previous calibration, so a number is red if and only if it actually moved.
# Refresh it with `python3 fill.py --freeze` once a version has been sent out,
# so the next round's red marks what moved since THAT version and not since
# some older one. (The comment here used to point at scratchpad/baseline.py,
# which does not exist.)
PREV = os.path.join(HERE, 'numbers_prev.json')


def mark(new, prev):
    """Wrap every value that moved in \new{}, and leave the rest black."""
    out, moved = {}, []
    for k, v in new.items():
        # a key MISSING from prev is a number the reader has not seen either, so
        # it is red for the same reason a changed one is
        if prev is not None and (k not in prev or prev[k] != v):
            out[k] = r'\new{' + v + '}'
            moved.append(f'{k}: {prev.get(k, "new")} -> {v}')
        else:
            out[k] = v
    return out, moved


def _params(out):
    """The quantitative model's table numbers, from the Fortran declarations.

    sync_tables.py reads them out of the Fortran, pushes them into Tables 5 and
    6 and writes them here, so the prose quotes the same number the table does
    and neither is typed. setdefault, not assignment: a name this file already
    computes from the stylized model wins, since that one is the model's own
    output rather than a target read off a declaration."""
    p = os.path.normpath(os.path.join(HERE, '..', 'paper', 'params_numbers.json'))
    if not os.path.exists(p):
        print('   params_numbers.json missing: run code/paper/sync_tables.py first')
        return
    for k, v in json.load(open(p)).items():
        out.setdefault(k, v)


def _figures(base):
    """
    figure_numbers.json, written by run.py while it drew the figures.

    It is an ERROR for this file to be missing or stale rather than something to
    work around: every number in it appears on a figure, and a note whose text
    and figure disagree is worse than one that fails to build. run.py runs
    before this file in build.sh.
    """
    p = os.path.join(HERE, 'figure_numbers.json')
    if not os.path.exists(p):
        raise SystemExit('   figure_numbers.json missing: run run.py first')
    return json.load(open(p))


def _children():
    """children_numbers.json, written by children.py while it built Table 4."""
    p = os.path.join(HERE, 'children_numbers.json')
    if not os.path.exists(p):
        raise SystemExit('   children_numbers.json missing: run children.py first')
    return json.load(open(p))


def _welfare():
    """
    welfare_numbers.json, written by welfare.py while it built Table 3.

    Same contract as _figures: a number that a table states is computed by
    whatever writes that table, once.
    """
    p = os.path.join(HERE, 'welfare_numbers.json')
    if not os.path.exists(p):
        raise SystemExit('   welfare_numbers.json missing: run welfare.py first')
    return json.load(open(p))


def _transition(out):
    """The transition numbers, from the file transition.py writes.

    They are read rather than recomputed because the transition solves the
    model under two policies for several cohorts, which is far more work than
    filling in a number, and transition.py runs before this file."""
    p = os.path.join(HERE, 'transition_numbers.json')
    if not os.path.exists(p):
        print('   transition_numbers.json missing: run transition.py first')
        return
    for k, v in json.load(open(p)).items():
        out.setdefault(k, v)


if __name__ == '__main__':
    import sys
    base = with_(P(), **json.load(open(os.path.join(HERE, 'calibrated.json'))))
    n = numbers(base, _figures(base))
    _params(n)
    _transition(n)
    if '--freeze' in sys.argv:
        json.dump(n, open(PREV, 'w'), indent=1)
        print(f'   froze {len(n)} numbers into numbers_prev.json; '
              'the next run marks what moves from here')
        raise SystemExit
    prev = json.load(open(PREV)) if os.path.exists(PREV) else None
    if prev is None:
        print('   numbers_prev.json missing: nothing will be marked red')
    n, moved = mark(n, prev)
    src = open(os.path.join(WRITE, 'housing_first_children_later.src.tex')).read()
    missing = set()
    for k in sorted(n, key=len, reverse=True):
        src = src.replace(f'@@{k}@@', n[k])
    import re
    for m in re.findall(r'@@[a-zA-Z_0-9]+@@', src):
        missing.add(m)
    open(os.path.join(WRITE, 'housing_first_children_later.tex'), 'w').write(src)
    for k in sorted(n):
        print(f'   {k:12s} {n[k]}')
    print(f'\n   {len(moved)} number(s) moved and are marked red:')
    for m in moved:
        print(f'      {m}')
    if missing:
        print('\n   UNFILLED PLACEHOLDERS:', ' '.join(sorted(missing)))
    else:
        print('\n   wrote housing_first_children_later.tex, every placeholder filled')
