"""
Fill the note's inline numbers straight from the model.

Every number quoted in the prose of housing_first_or_treatment_first_ask_the_kids.tex is written as a
placeholder @@name@@ in housing_first_or_treatment_first_ask_the_kids.src.tex, and this file computes each one
and writes housing_first_or_treatment_first_ask_the_kids.tex. Nothing in the note can then drift away from the
code, which is the same discipline the tables already follow.

Run:  python3 fill.py
"""

import json
import os
import numpy as np
from stylized import P, with_, value1
from calibrate import YG, W, stats, bracket, TARGET, _drug_targets
from children import (child_grid, shifted, DEL_D, DEL_H, RATIO_TARGET,
                      RATIO_H_TARGET, ratio_h, ratio_d)
from frontier import TH_BREAK, DSHARE_TOP, DSHARE_CEIL

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



# ---------------------------------------------------------------------------
_ONES = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six',
         7: 'seven', 8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven',
         12: 'twelve', 13: 'thirteen', 14: 'fourteen', 15: 'fifteen',
         16: 'sixteen', 17: 'seventeen', 18: 'eighteen', 19: 'nineteen'}
_TENS = {2: 'twenty', 3: 'thirty', 4: 'forty', 5: 'fifty', 6: 'sixty',
         7: 'seventy', 8: 'eighty', 9: 'ninety'}


def _word(n):
    """The paper spells these out, HYPHENATED as standard English writes them: fifty-four
    (review, 3 October; they were open before)."""
    if n in _ONES:
        return _ONES[n]
    t, u = divmod(n, 10)
    return _TENS[t] + ('-' + _ONES[u] if u else '')


def _param_counts():
    """Rows of the two parameter tables, split by the Set column.

    Table 5 is the parameters that carry this paper's story and Table 6 the
    standard ones; each row says Int. or Ext. in its third cell. Counting them
    here is what stops the prose and the tables disagreeing, which is the same
    rule the numbers themselves follow.
    """
    import re as _re
    tab = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '..', '..', 'writing', 'tables'))

    def one(name):
        n_int = n_ext = 0
        for line in open(os.path.join(tab, name)):
            s_ = line.strip()
            if (not s_.endswith(r'\\') or s_.startswith(r'\multicolumn')
                    or s_.startswith('Parameter &')):
                continue
            cells = s_[:-2].split('&')
            if len(cells) < 3:
                continue
            # A CELL MARKED RED IS STILL A CELL. sync_tables.py and the round
            # marking both wrap a changed cell in \textcolor{red}{...}, and
            # stripping punctuation from that leaves 'textcolorredInt.', which
            # starts with neither Int nor Ext. Every red row would then have
            # fallen out of the count silently, and the count is what the prose
            # quotes.
            c = _re.sub(r'\\textcolor\{red\}\{(.*?)\}', r'\1', cells[2])
            c = _re.sub(r'[^A-Za-z.]', '', c)
            if c.startswith('Int'):
                n_int += 1
            elif c.startswith('Ext'):
                n_ext += 1
        return n_int, n_ext

    mi, me = one('tab_eleven.tex')
    si, se = one('tab_standard.tex')
    out = {'n_all': _word(mi + me + si + se),
           'n_ext': _word(me + se), 'n_int': _word(mi + si),
           'n_main': _word(mi + me), 'n_main_int': _word(mi), 'n_main_ext': _word(me),
           'n_std': _word(si + se), 'n_std_int': _word(si), 'n_std_ext': _word(se)}
    # A CAPITALISED FORM FOR THE ONES THAT OPEN A SENTENCE. LaTeX has no
    # portable way to upcase the first letter of a macro's expansion, and
    # \MakeUppercase would shout the whole word.
    out.update({k + '_cap': v[0].upper() + v[1:] for k, v in list(out.items())})
    return out

def numbers(base, fig):
    """The prose's numbers. `fig` is figure_numbers.json, already loaded."""
    # KEYS BEGINNING WITH AN UNDERSCORE ARE NOT PLACEHOLDERS. run.py exports a
    # few diagnostics for verify.py to assert on, _part_misses among them, and
    # they are ints rather than formatted strings. They have no @@name@@ in the
    # prose, so they are dropped here rather than being marked up and offered to
    # the substituter.
    out = {k: v for k, v in fig.items() if not k.startswith('_') or k == '_raw'}
    raw = dict(out.pop('_raw'))
    wel = _welfare()
    raw.update(wel.pop('_raw'))
    out.update(wel)
    out.update(_children())
    pc = lambda z, n=2: f'{100*z:.{n}f}'

    out['beta'] = f'{base.beta:.3f}'
    out['R'] = f'{base.R:.3f}'
    # FOUR PLACES, LIKE THE TABLE. At three the sentence said 0.049 while
    # Table 1 beside it said 0.0485, which is one number printed two ways.
    out['u0'] = f'{base.u0:.4f}'
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
    # THE SAME COVERAGE AS A PERCENTAGE, AND WHAT THE REFORM ADDS. The prose
    # says the reform moves most of a generation from market rent to a fraction
    # of it, and "most" is a number: pi_V of them already held a voucher and the
    # rest do not, so the reform newly covers 1 - pi_V.
    out['pvbase_pc'] = f'{100 * base.pV:.1f}'
    # THE SHARE ACTUALLY HOLDING A VOUCHER, which is NOT pi_V. pi_V is
    # recipients over the INCOME ELIGIBLE population, and eligibility is capped
    # at kappa_V times median income, so the covered share is pi_V times the
    # eligible share. Reading pi_V as a population share made the prose say the
    # reform moved 73 per cent of a generation onto vouchers when it moves 17
    # points, and the eligible population is only 23 per cent to begin with.
    from stylized import _states as _st
    _elig = 0.0
    for _i, _y in enumerate(YG):
        for _p, _inc, _rm in _st(base, 0, 'HF', float(_y), used=0):
            if _inc <= base.yV:
                _elig += WW[_i] * _p
    out['elig_pc'] = f'{100 * _elig:.1f}'
    out['cov_base_pc'] = f'{100 * _elig * base.pV:.1f}'
    out['cov_univ_pc'] = f'{100 * _elig:.1f}'

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
    out['h3'] = f'{base.h3 / float((WW * YG).sum()):.2f}'
    # h2frac IS GONE. It printed H_RATIO, the fixed quarter h2 used to be set
    # at, and h2 is bracketed now on the share of the housed in the small
    # unit, so the ratio is an outcome of the calibration rather than a choice.
    # Its value is in Table 2 with the other calibrated parameters and the prose
    # no longer quotes it.
    # HOW MANY PARAMETERS TABLE 2 HOLDS, counted from the table rather than
    # typed into the sentence that introduces it. It went from seven to eight
    # when h_2 moved out of the external table, and the sentence said seven for
    # as long as it took to notice.
    # HOW MANY PARAMETERS EACH TABLE HOLDS, COUNTED FROM THE TABLES. The prose
    # typed seven of these numbers -- fifty four in total, twenty nine external,
    # twenty five internal, and the two tables' own splits -- and a table that
    # gains or loses a row leaves every one of them wrong with nothing to catch
    # it. They are read off the Set column of the two table files, which is the
    # only place that says whether a parameter is calibrated inside the model or
    # set outside it.
    # THE DRUG SPENDING TARGET AND ITS ARITHMETIC, from the csv the data script
    # writes, so the note quotes the same numbers the calibration is fitted to.
    _d = _drug_targets()
    out['spend24'] = f'{_d["spend_2024_bn"]:.1f}'
    out['n_users'] = f'{_d["n_users_m"]:.1f}'
    out['user_inc'] = f'{_d["user_family_income"]:,.0f}'
    out['user_inc_bn'] = f'{_d["user_income_bn"]:,.0f}'
    out['share_uncorrected'] = f'{100 * _d["share_uncorrected"]:.1f}'
    out['share_income_only'] = f'{100 * _d["share_income_only"]:.1f}'
    out['share_price_only'] = f'{100 * _d["share_price_only"]:.1f}'
    out['share_lo'] = f'{100 * _d["share_top_75000"]:.1f}'
    out['share_hi'] = f'{100 * _d["share_top_125000"]:.1f}'
    out.update(_param_counts())
    # THE SMALL UNIT'S TARGET, from the dict the bracket actually reads rather
    # than typed into the sentence beside it. It is the same American Community
    # Survey table the quantitative model's size distribution comes from,
    # collapsed to this model's two rentals.
    out['hsmall_t'] = f'{100 * TARGET["hsmall"]:.1f}'
    # HOW MANY PARAMETERS THE STYLIZED MODEL'S TABLE 2 HOLDS, counted from the
    # table rather than typed into the sentence that introduces it. It went from
    # seven to eight when h_2 moved out of the external table, and back to seven
    # when theta left the internal one, and the sentence said seven throughout.
    #
    # NAMED n_styl AND NOT n_int. It was n_int, which is also what
    # _param_counts() calls the QUANTITATIVE model's internally calibrated
    # count, and this assignment runs second: the stylized model's seven
    # silently overwrote the quantitative model's twenty five, in a sentence
    # about a different table in a different section of the paper.
    from tables import INTERNAL as _INTERNAL
    out['n_styl'] = _word(len(_INTERNAL)).capitalize()
    out['kV'] = f'{base.kV:.2f}'
    out['smrd'] = f'{base.smr_d:.0f}'
    out['th_break'] = f'{TH_BREAK:.3f}'
    # THE TWO EDGES OF THE DISCONTINUITY, from frontier.py where they were
    # measured, so the note cannot quote one number and the scan another.
    out['dshare_top'] = f'{100 * DSHARE_TOP:.0f}'
    out['dshare_ceil'] = f'{100 * DSHARE_CEIL:.1f}'

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
    out['homeless1'] = pc(stats(with_(base, h2=base.h3))['homeless'])

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
    # BOTH RATIOS ARE UNTARGETED NOW. The penalties are set from the
    # earnings literature, so what the model delivers on each ratio is a
    # validation number rather than a matched moment.
    out['ratio_h'] = f'{ratio_h(base):.2f}'
    out['ratio_d_model'] = f'{ratio_d(base):.2f}'
    out['ratio_h_model'] = f'{ratio_h(base):.2f}'
    out['del_d_pc'] = f'{100*DEL_D:.0f}'
    out['ratio_h_t'] = f'{RATIO_H_TARGET:.1f}'
    # THE SAME TWO NUMBERS SPELLED OUT, because the literature review writes its
    # magnitudes in words and the introduction writes them in figures. Both come
    # off DEL_D and DEL_H so neither can drift from the parameter it describes.
    out['del_d_pcw'] = _word(int(round(100 * DEL_D)))
    out['del_h_pcw'] = _word(int(round(100 * DEL_H)))
    # THE DIRECTION WORDS FOR THE TWO UNTARGETED RATIOS. Each sentence says
    # where the model lands relative to evidence it was never shown, and that
    # is a result: delta_d and delta_h are set from the earnings estimates, so
    # nothing holds either ratio on its side of the comparison. Take the word
    # from the numbers so the sentence turns if a recalibration moves them.
    out.update(compare(ratio_d(base), RATIO_TARGET, 'rd',
                       more='above', less='below', same='level with'))
    out.update(compare(ratio_h(base), RATIO_H_TARGET, 'rh',
                       more='above', less='below', same='level with'))
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



ANCHOR = r'\section{The quantitative model}'


def _black_notes(src):
    """
    NO LONGER BLACKENS ANYTHING, and the reason is a standing instruction.

    This used to strip every \new{} ahead of \section{The quantitative model},
    on the rule that the author was auditing Sections 1 to 3 and wanted them
    clean. That rule is withdrawn: the author now asks for every change to be
    red, in Section 3 and its calibration explicitly, so that a round's edits can
    be read rather than taken on trust.

    It is kept as a no-op rather than deleted because the blackening was widened
    three times by hand and came back each time, so a future round that wants a
    clean front section should re-enable it HERE, in one place, rather than
    stripping marks somewhere else again.

    THE COST OF THE OLD RULE IS WORTH RECORDING. \new{} is what mark() wraps a
    moved number in AND what an edit is marked with by hand, so blackening one
    blackened both: a whole round of edits to Section 3.7 went out invisible,
    and so did this round's until the author said the changes were not showing.
    """
    return src


# DECIMALS, the author, 29 September: "no need to put 3 decimals in the text anywhere.
# please make a note of that", "same with tables unless it is important to put the 3rd
# decimal" (NUMBERS.md, "Decimals").  Applied when a name is filled, so every script
# keeps writing full precision and the prose never disagrees with a table that needs it.
#   |x| >= 0.1   two decimals               3.752 -> 3.75, 0.608 -> 0.61
#   |x| <  0.1   two significant figures    0.0248 -> 0.025, 0.0014 -> 0.0014
#                and no trailing zero past the second decimal: 0.040 -> 0.04
# A name whose third decimal IS the number is listed here and left alone.
KEEP_THIRD = {'s_beta_ann', 'g_beta_ann'}      # 0.995 a year; two decimals print 0.99, whose thirtieth power is 0.74, not the 0.86 of Table 1 (referee, 9 October)


def text_precision(k, v):
    import math, re as _re
    s = str(v)
    if k in KEEP_THIRD or not _re.fullmatch(r'-?\d+\.\d{3,}', s):
        return s
    x = float(s)
    if x == 0.0:
        return '0.00'
    if abs(x) >= 0.1:
        out = f'{x:.2f}'
    else:
        out = f'{x:.{1 - int(math.floor(math.log10(abs(x))))}f}'
        while _re.search(r'\.\d{3,}$', out) and out.endswith('0'):
            out = out[:-1]
    return '-0.00' if out in ('-0.00', '-0.0') else out


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


def _derived_from_fortran(out):
    """
    Numbers the prose DERIVES from two Fortran declarations rather than quoting
    one. The conversion rate from use to disorder is the SUD rate over the
    participation rate, and Section 5 uses it twice to weight the drug spending
    share. Typed, it was 0.717 and 0.283 beside two rates that the calibration
    moves, so the arithmetic in the sentence could stop being true of its own
    inputs.
    """
    F = _fortran_all()
    try:
        sud = float(F['f_sud_rate_data'])
        part = float(F['f_participation_rate_data'])
    except (KeyError, ValueError):
        return
    r = sud / part
    out.setdefault('convrate', f'{r:.3f}')
    out.setdefault('convrest', f'{1.0 - r:.3f}')


def _fortran_all():
    """
    fortran_numbers.json, every Fortran declaration as f_<name>.

    params_numbers.json carries only the 36 constants that are rows of Tables 5
    and 6. The quantitative model's prose quotes many more than its tables
    state, so this exposes all of them and lets a sentence read the declaration
    rather than repeat it.
    """
    p = os.path.normpath(os.path.join(HERE, '..', 'paper',
                                      'fortran_numbers.json'))
    if not os.path.exists(p):
        print('   fortran_numbers.json missing: run '
              'code/paper/export_consts.py first')
        return {}
    return json.load(open(p))


def _model_all():
    """
    model_numbers.json, every scalar the calibration printed as m_<name>.

    The other half of what Section 4 onward quotes. f_<name> is what the model
    is TOLD, from the declarations; m_<name> is what it PRODUCES, from the run's
    own output. A moment the run stops printing disappears from the file and any
    sentence reading it fails at fill time, which is the point: a stale model
    number in the prose is exactly what this pipeline exists to prevent, and it
    is the kind that no table would catch.
    """
    p = os.path.normpath(os.path.join(HERE, '..', 'paper',
                                      'model_numbers.json'))
    if not os.path.exists(p):
        print('   model_numbers.json missing: run '
              'code/paper/export_moments.py <run.log> after a calibration')
        return {}
    return json.load(open(p))


def _results_all():
    """
    results_numbers.json, the counterfactuals' and the transition's results as
    x_<name>, written by code/paper/export_results.py from each arm's saved
    equilibrium and the transition's latest forward pass.
    """
    p = os.path.normpath(os.path.join(HERE, '..', 'paper',
                                      'results_numbers.json'))
    if not os.path.exists(p):
        print('   results_numbers.json missing: run '
              'code/paper/export_results.py first')
        return {}
    return json.load(open(p))


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
    # AND EVERY OTHER DECLARATION, as f_<name>. Same setdefault discipline: a
    # linked table row keeps its q_<name>, and anything the stylized model
    # computes itself wins over a constant of the same name.
    for k, v in _fortran_all().items():
        out.setdefault(k, v)
    # AND WHAT THE MODEL PRODUCED, as m_<name>, on the same terms.
    for k, v in _model_all().items():
        out.setdefault(k, v)
    # AND WHAT THE COUNTERFACTUALS AND THE TRANSITION PRODUCED, as x_<name>.
    for k, v in _results_all().items():
        out.setdefault(k, v)
    # AND THE STAGED STYLIZED MODEL, as s<stage>_<name> and s_<name>
    # (stage_results.py, stage_transition.py), and SECTION 5'S TABLES, as
    # c_<name> (code/paper/calib_tables.py). Leading underscores are raw data.
    # AND THE STRIPPED STYLIZED MODEL OF SECTION 3, as g_<name> (gradient.py, 8 October).
    for fn in (os.path.join(HERE, 'gradient_numbers.json'), os.path.join(HERE, 'oldmodel_nosave_numbers.json'),
               os.path.join(HERE, 'stage_numbers.json'),
               os.path.normpath(os.path.join(HERE, '..', 'paper', 'calib_numbers.json')),
               # the rule-A footnote's numbers, x_ruleA_<name> (code/paper/export_ruleA.py, 12 October)
               os.path.normpath(os.path.join(HERE, '..', 'paper', 'ruleA_numbers.json'))):
        if not os.path.exists(fn):
            print(f'   {os.path.basename(fn)} missing')
            continue
        for k, v in json.load(open(fn)).items():
            if not k.startswith('_'):
                out.setdefault(k, v)
    _derived_from_fortran(out)


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
    src = open(os.path.join(WRITE, 'housing_first_or_treatment_first_ask_the_kids.src.tex')).read()
    missing = set()
    for k in sorted(n, key=len, reverse=True):
        src = src.replace(f'@@{k}@@', n[k])
    import re
    for m in re.findall(r'@@[a-zA-Z_0-9]+@@', src):
        missing.add(m)
    src = _black_notes(src)
    open(os.path.join(WRITE, 'housing_first_or_treatment_first_ask_the_kids.tex'), 'w').write(src)
    for k in sorted(n):
        print(f'   {k:12s} {n[k]}')
    print(f'\n   {len(moved)} number(s) moved and are marked red:')
    for m in moved:
        print(f'      {m}')
    if missing:
        print('\n   UNFILLED PLACEHOLDERS:', ' '.join(sorted(missing)))
    else:
        print('\n   wrote housing_first_or_treatment_first_ask_the_kids.tex, every placeholder filled')
