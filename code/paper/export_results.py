"""
Export the quantitative model's RESULTS as x_<name>, for the prose to quote.

usage: python3 code/paper/export_results.py

f_<name> is what the model is told (the declarations), m_<name> what the
calibration produced (export_moments.py). This is the third kind: what the
counterfactuals and the transition produced. Each number is read from the run
that made it, never typed, and fill.py merges the file on the same setdefault
terms as the other two.

Sources, each the one saved equilibrium of its arm (the exit pass, never a
best-of):

  results/counterfactuals_cf_fix2/tf85/final.txt      Treatment First, 85 per cent
                                                      detection, long run
  results/counterfactuals_cf_fix2/omega1/final.txt    Housing First with the
                                                      weight on the child at 1
  results/counterfactuals_cf_fix2/null_share/cf.log.gz  no policy, the baseline
                                                      for the transition's changes
  code/trtf60/restart3_killed_1323/run.log            the T = 60 transition, PINNED

THE TRANSITION IS NOT CONVERGED. Its numbers are exported with the loop they
come from, and the prose must say they are preliminary.  THE LOG IS PINNED, not
picked: this file used to take the newest log under code/trtf60 that reached
period 26, which on 30 September silently moved to restart 3c, a second iterate,
while the figure (transition_series.py) read restart 3.  Both now read restart 3's
loop 0, the one complete 59-year pass on the current binary; move TR_LOG and
transition_series.LOG together when a converged pass lands.

THE CEV IS NET OF THE NO-POLICY RUN'S.  Read off the benchmark's curve, the
no-policy run itself sits at +0.027 per cent (null_share), which is what the
counterfactual code produces with no policy at all.  Every other change in
Section 6 is against that run, and so is the childhood/adult split, so the CEV is
too: x_tf_cev = CEV(tf85) - CEV(null_share), and the transition's cohorts are
netted by the same amount (the no-reform control's own cohort CEV is not printed).

This file OVERWRITES results_numbers.json, and then runs export_elasticity.py,
export_longrun.py and transition_figure.py, which merge their names into it, so the
file is always whole.
"""
import glob
import gzip
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'counterfactuals_2c')
RES_OLD = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
OUT = os.path.join(HERE, 'results_numbers.json')
# STAGE D (2 October): THE LONG RUN READS THE omega_c = 0.085 ARMS, each the accepted run of its
# experiment, pi_V clearing the budget in every one (the author: "you need to adjust piv"); the
# Treatment First arm is the $35 test (the author: "run the cost of the test on the upper end of the
# estimates...$35"). THE TRANSITION STILL READS THE OLD ARMS ('old_*'): its path was solved from the
# old benchmark to the old Treatment First, so its changes are measured against those two until the
# T = 60 transition is re-run on the new ones (stage E).
# 6 October: THE TRANSITION NOW READS THE T = 60 RUN ON THE 2c BUILD (tr2c_t60, loop 1), solved between
# results/transition_2c/arm_null and arm_tf, which transition_source.py names; the 'old_*' keys below are those two
# arms now, kept under their old names so every reader of the transition block is unchanged.
sys.path.insert(0, HERE)
from transition_source import REF as TR_REF, REF_NULL as TR_NULL, REF_TF as TR_TF, CURVE as TR_CURVE
TF_ARM = os.environ.get('TF_ARM', 'tf85_c35/tf')
ARMDIR = {'null_share': (RES, 'nulltf/null'), 'null_remote': (RES, 'nulltf/null'),
          'tf85': (RES, TF_ARM), 'omega1': (RES, 'omega1_clear/omega1'),
          'internalise': (RES, 'optimal_clear/internalise'),
          'old_null_share': (TR_REF, TR_NULL), 'old_tf85': (TR_REF, TR_TF)}


def adir(arm):
    return os.path.join(*ARMDIR[arm])


def levels(arm):
    """the first number on each line of an arm's final.txt, by label"""
    out = {}
    for l in open(os.path.join(adir(arm), 'final.txt')):
        m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
        if m:
            out[m.group(1).strip()] = float(m.group(2))
    return out


def final(arm):
    """change in per cent, and levels, of each line of an arm's final.txt. The old arms printed the
    no-policy level and the change beside each line, and the welfare split; the new arms print the
    level only, so both are taken against the no-policy run here (the same run every change in
    Section 6 is measured against). The split: total = the difference in welfare with childhood,
    childhood = the difference in childhood utility, adult = the rest (the old split, from these
    same two lines: +0.2367 = 451.03402 - 450.79733)."""
    rows = {}
    for l in open(os.path.join(adir(arm), 'final.txt')):
        m = re.match(r'\s+(.+?)\s{2,}(\S+)\s+no policy\s+(\S+)\s+change\s+(\S+)%', l)
        if m:
            rows[m.group(1).strip()] = dict(level=float(m.group(2)), base=float(m.group(3)),
                                            pc=float(m.group(4)))
        m = re.search(r'childhood ([+-]\S+), adult part ([+-]\S+), total ([+-]\S+)', l)
        if m:
            rows['split'] = dict(child=float(m.group(1)), adult=float(m.group(2)),
                                 total=float(m.group(3)))
    if not rows:
        a, b = levels(arm), levels('old_null_share' if arm.startswith('old_') else 'null_share')
        for k, v in a.items():
            if k in b:
                rows[k] = dict(level=v, base=b[k], pc=100 * (v / b[k] - 1) if b[k] else 0.0)
        tot = a['welfare (with childhood)'] - b['welfare (with childhood)']
        kid = a['childhood utility'] - b['childhood utility']
        rows['split'] = dict(child=kid, adult=tot - kid, total=tot)
    return rows


def last_cev(arm):
    """CEV at the exit pass, from passes.txt (the last row); an arm kept without passes.txt (the transition's
    re-solved arms in results/transition_2c) gives the CEV its cf.log.gz printed off the benchmark curve"""
    if not os.path.exists(os.path.join(adir(arm), 'passes.txt')):
        return cev_log(arm)
    L = open(os.path.join(adir(arm), 'passes.txt')).read().splitlines()
    rows = [l.split() for l in L if l.strip() and l.split()[0].isdigit()]
    # the CEV column by its header: the new arms' passes.txt adds V(chg) and V/user(chg) after it
    # ('drug gap' and 'budget gap' are two words each in the header and one number each in a row)
    col = [l.split() for l in L if l.startswith('pass')][-1].index('CEV') - 2
    return float(rows[-1][col].rstrip('%'))


def cev_log(arm):
    """the arm's CEV off the benchmark's curve, per cent, from its cf.log.gz"""
    x = None
    for l in gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace'):
        if 'CEV from the saved benchmark curve' in l:
            x = 100 * float(l.split('x=')[1])
    return x


def pc(x, nd=0):
    return f'{abs(x):.{nd}f}'


out = {}

tf = final('tf85')
out['x_tf_b_pc'] = pc(tf['drug use b']['pc'])
out['x_tf_sud_pc'] = pc(tf['SUD lambda_d']['pc'])
out['x_tf_h_pc'] = pc(tf['homelessness h_1']['pc'])
out['x_tf_price_pc'] = pc(tf['drug price']['pc'])
CEV0 = cev_log('null_share')
out['_cev_null_share'] = CEV0
out['x_cev0'] = f'{CEV0:.2g}'
# the exact CEV off the curve (cf.log), as Table 7 prints it: passes.txt rounds it to two decimals
# before the no-policy run's is taken off, which put the prose 0.01 above the table (4.34 against 4.33)
out['x_tf_cev'] = f"{cev_log('tf85') - CEV0:.2f}"
out['x_tf_cev_dir'] = 'better' if cev_log('tf85') > CEV0 else 'worse'
# the long-run gain splits about evenly between childhood and adulthood
out['x_tf_child_share_pc'] = pc(100 * tf['split']['child'] / tf['split']['total'])
# THE EXPERIMENT AS RUN (Section 7): pi_V clears the budget, and the screen's
# parameters are the ARM's handover values, not the Fortran declarations (0.95 and
# 0.005 there; the arm ran at 0.85 and 0).
out['x_tf_piv0'] = f"{tf['pi_V (voucher probability)']['base']:.3f}"
out['x_tf_piv1'] = f"{tf['pi_V (voucher probability)']['level']:.3f}"
out['x_tf_piv_pc'] = pc(tf['pi_V (voucher probability)']['pc'])
# and in per cent to two decimals, so that the two levels and the change agree when
# rounded (0.068 to 0.081 reads as 19 per cent, not the 21 it is)
out['x_tf_piv0_pc'] = f"{100 * tf['pi_V (voucher probability)']['base']:.2f}"
out['x_tf_piv1_pc'] = f"{100 * tf['pi_V (voucher probability)']['level']:.2f}"
out['x_tf_h_dir'] = 'raises' if tf['homelessness h_1']['pc'] > 0 else 'lowers'
# THE LEVELS BEHIND THE CHANGES (the author, 2 October: "from X to Y"), in percent of households
out['x_b0'] = f"{100 * tf['drug use b']['base']:.2f}"
out['x_tf_b1'] = f"{100 * tf['drug use b']['level']:.2f}"
out['x_h0'] = f"{100 * tf['homelessness h_1']['base']:.2f}"
out['x_tf_h1'] = f"{100 * tf['homelessness h_1']['level']:.2f}"
# the homelessness sentence of Section 6.2 (the author: "However, it also raises homelessness by 6
# percent from X to Y"): the 'However' belongs only to a rise, so the sentence turns with the sign
_hrise = tf['homelessness h_1']['pc'] > 0
# and why (the author, 2 October: "explain why....because it revokes vouchers for some of the very
# households that need them since they have SUD, spend more on drugs, and may have lost their job")
out['x_tf_h_sentence'] = (
    f"However, it also raises homelessness by {out['x_tf_h_pc']} percent, from {out['x_h0']} to "
    f"{out['x_tf_h1']} percent of households, because it revokes vouchers from some of the very "
    f"households that need them most: those with a SUD, who spend more on the drug and may have lost "
    f"their job." if _hrise else
    # (the author, 2 October, round 4ad85a30: "but also, less SUD means less unemployment and less
    # homelessness")
    f"It also lowers homelessness by {out['x_tf_h_pc']} percent, from {out['x_h0']} to "
    f"{out['x_tf_h1']} percent of households: less SUD means less unemployment and so less homelessness, "
    f"and the vouchers it revokes from households with a SUD go, through a higher $\\pi_V$, to other poor "
    f"households.")
# WHO THE FALL IN HOMELESSNESS COMES FROM (round 4ad85a30, the author on the introduction: "explain why
# ... it is worth explaining that result a bit more"): the share homeless among households with a SUD
# and among the rest, from h_1, the SUD share of the homeless and the SUD share of households
_hs, _lam = tf['SUD share of the homeless'], tf['SUD lambda_d']
_hh = tf['homelessness h_1']
_rs0 = _hh['base'] * _hs['base'] / _lam['base']
_rs1 = _hh['level'] * _hs['level'] / _lam['level']
_rc0 = _hh['base'] * (1 - _hs['base']) / (1 - _lam['base'])
_rc1 = _hh['level'] * (1 - _hs['level']) / (1 - _lam['level'])
out['x_tf_h_sud0'], out['x_tf_h_sud1'] = f'{100 * _rs0:.2f}', f'{100 * _rs1:.2f}'
out['x_tf_h_cln0'], out['x_tf_h_cln1'] = f'{100 * _rc0:.2f}', f'{100 * _rc1:.2f}'
# THE BALANCE, IN FULL (round c88b1dda, the author: "you have to explain the balance. on the one hand it puts
# those with SUD at risk of homelessness, but on the other it reduces SUD which more than offsets it...give the
# full explanation"; of the split sentence: "not clear"). The change in homelessness splits exactly into the
# risk of those who still carry a SUD, the number who carry one, and the risk of everyone else:
#   dh = lam1 (rs1 - rs0) + (lam1 - lam0)(rs0 - rc0) + (1 - lam1)(rc1 - rc0)
_l0, _l1 = _lam['base'], _lam['level']
_up = 100 * _l1 * (_rs1 - _rs0) / _hh['base']
_few = 100 * (_l1 - _l0) * (_rs0 - _rc0) / _hh['base']
_oth = 100 * (1 - _l1) * (_rc1 - _rc0) / _hh['base']
assert abs(_up + _few + _oth - _hh['pc']) < 0.05, (_up, _few, _oth, _hh['pc'])
if not _hrise and _up > 0 > _few and _oth < 0 and _few + _oth < -_up:
    out['x_tf_h_sentence'] = (
        f"Treatment First also lowers homelessness by {out['x_tf_h_pc']} percent, from {out['x_h0']} to {out['x_tf_h1']} "
        'percent of households, as the balance of three effects. First, it revokes the vouchers of '
        'households with a SUD and puts them at a higher risk of homelessness. Of them, '
        f'${100 * _rs1:.2f}$ percent are homeless, against ${100 * _rs0:.2f}$ under Housing First. On its own this '
        f'raises homelessness by ${_up:.0f}$ percent. Second, less SUD means '
        'less unemployment and so less homelessness. There are '
        f"{'a third' if round(abs(_l1 / _l0 - 1), 1) == 0.3 else f'{100 * abs(_l1 / _l0 - 1):.0f} percent'} "
        f'fewer households with a SUD, which on its own lowers homelessness by ${abs(_few):.0f}$ percent. '
        'Third, the vouchers it revokes go, through the higher $\\pi_V$, to other clean and eligible households, '
        f'lowering homelessness by ${abs(_oth):.0f}$ percent. Together the last two more than offset the first.')
out['x_tf_h_split'] = (
    'The fall hides a rise among the households the screen acts on: the share of households with a SUD who '
    f"are homeless {'rises' if _rs1 > _rs0 else 'falls'} from ${100 * _rs0:.2f}$ to ${100 * _rs1:.2f}$ "
    f"percent, while among the rest it {'falls' if _rc1 < _rc0 else 'rises'} from ${100 * _rc0:.2f}$ to "
    f"${100 * _rc1:.2f}$ percent."
    if not _hrise and _rs1 > _rs0 and _rc1 < _rc0 else '')
# the introduction's reason (the author: "it is because of the reduction in drug use that lowers the
# chance of homelessness, through moral hazard, and also from being able to house others whom the
# vouchers go to instead")
# (round c88b1dda, the author: "on the one hand, it revokes vouchers for those with SUD and puts them at higher
# risk for homelessness. On the other hand, in the long run....")
out['x_tf_h_why_intro'] = ('' if _hrise else
                           '. On the one hand, it revokes the vouchers of drug users and households with a SUD and puts them at a '
                           'higher risk of homelessness. On the other hand, in the long run, removing the moral '
                           'hazard cuts drug use, so fewer households acquire a SUD, remain unemployed because of it and lose '
                           'their housing, and the vouchers it revokes go to other poor households instead. '
                           'Together these two effects slightly more than offset the first')
# THE HOMELESS WHO COULD HAVE AFFORDED HOUSING, in the benchmark (the author, 2 October: "many just
# can't afford to not be homeless even if they wanted to"): the share homeless by choice
_bl = gzip.open(os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085', 'bench.log.gz'), 'rt',
                errors='replace').read()
_ch = float(re.findall(r'DIAG homeless by choice, share of the homeless\s*=\s*(\S+)', _bl)[-1])
out['x_hl_choice_pc'] = f'{100 * _ch:.2g}'
# pi_V's direction, and the clause the author added to a rise ("which makes staying clean of drugs
# even more desirable"): a voucher easier to get is a larger reward for passing the screen
_pvup = tf['pi_V (voucher probability)']['pc'] > 0
out['x_tf_piv_dir'] = 'rises' if _pvup else 'falls'
# (round f4276e76, the author: 'This' -> ', making')
out['x_tf_piv_so'] = ', making staying clean of drugs even more desirable' if _pvup else ''
# WHY WELFARE RISES (the author, 2 October: "you should explain why welfare rises. The cut in drug use
# reduces the budget and earnings externalities much more than it raises the childhood and aggregate
# homelessness externalities since the latter a small in an absolute sense relative to the former
# two"). That reason is for a reform that raises homelessness; when homelessness falls too, every
# one of the four moves the same way.
if cev_log('tf85') > CEV0:
    out['x_tf_cev_why'] = (
        'Welfare rises because the cut in drug use reduces the budget and earnings externalities by '
        'much more than it raises the externalities that run through homelessness, on the child and on '
        # (the author, 2 October: "as Table X has shown"): Table 7 sets the levels side by side, the
        # shares homeless and in a shelter moving by hundredths of a point against SUD's whole points
        'everyone else, which, as Table~\\ref{tab:longrun} has shown, are small in absolute terms next '
        'to the first two.' if _hrise else
        'Welfare rises because the cut in drug use reduces the budget and earnings externalities, and '
        'homelessness, and with it the externalities on the child and on everyone else, falls too.'
        if abs(tf['homelessness h_1']['pc']) >= 2 else
        # homelessness all but unchanged (the omega_c = 0.085 arms: -1 per cent, the shelter share flat)
        # (round 4ad85a30, the author: 'barely moves' -> "is unchanged in the long run"; almost, since
        # homelessness falls by 1 per cent while the shelter share is flat)
        # (3 October: the decomposition shows the cheaper drug LOWERS welfare -- at the benchmark price the
        # gain is larger -- so it is no longer listed beside the voucher programme as a source of the gain)
        'Welfare rises because the cut in drug use reduces the budget and earnings externalities and, '
        'through the government budget, pays for a larger voucher programme, while homelessness, and with it '
        'the externalities that run through it, is almost unchanged in the long run.')
else:
    out['x_tf_cev_why'] = ''


# THE TWO DECOMPOSITIONS (the author, 3 October: "the decomposition should be part of the long run results",
# then "if not, we can just mention this in the text, weaving it"). Each is Treatment First with one channel shut:
# fixpv holds pi_V at the no-policy value and leaves the revenue unspent, fixp holds the drug price at the
# no-policy value (code/extra_2c/remote_decomp_2c.sh). From each arm's cf.log.gz once it has finished (the exact
# CEV off the curve, as x_tf_cev), until then from the last pass in results/decomp_2c/status.txt, which rounds
# before the no-policy run's CEV is taken off (0.01 at most). DC_FINAL says which.
def _dc_last_pass(arm, sub='decomp_2c'):
    rows, cur = [], None
    for l in open(os.path.join(ROOT, 'results', sub, 'status.txt')):
        if l.startswith('== arm '):
            cur = l.split()[2]
        elif cur == arm and re.match(r'\s+\d+\s', l):
            rows.append(l.split())
    r = rows[-1]   # pass price pi_V b SUD h_1 drug-gap budget-gap welfare CEV V V/user
    pcv = lambda s: float(s.rstrip('%'))
    return {'b': pcv(r[3]), 'sud': pcv(r[4]), 'h': pcv(r[5]), 'cev': pcv(r[9]), 'piv': float(r[2]), 'pass': int(r[0])}


def _dc(arm, sub='decomp_2c'):
    log = os.path.join(ROOT, 'results', sub, f'arm_{arm}', 'cf.log.gz')
    d = _dc_last_pass(arm, sub)
    if os.path.exists(log):
        for l in gzip.open(log, 'rt', errors='replace'):
            if 'CEV from the saved benchmark curve' in l:
                d['cev'] = 100 * float(l.split('x=')[1]) - CEV0
        d['final'] = True
    return d


DC_PV, DC_P = _dc('fixpv'), _dc('fixp')
out['_dc_final'] = bool(DC_PV.get('final') and DC_P.get('final'))
out['_dc_passes'] = f"fixpv {DC_PV['pass']}, fixp {DC_P['pass']}"
_tfc = cev_log('tf85') - CEV0
out['x_dc_pv_cev'] = f"{DC_PV['cev']:.2f}"
out['x_dc_p_cev'] = f"{DC_P['cev']:.2f}"
out['x_dc_p_b_pc'] = f"{abs(DC_P['b']):.0f}"
# (round r114, the author on the price-held gain: "even holding pi_v constant?" -- no: pi_V still clears the budget,
# and rises further than under Treatment First, so the sentence says so and gives its level)
out['x_dc_p_piv_pc'] = f"{100 * DC_P['piv']:.2f}"
out['x_dc_pv_h_pc'] = f"{abs(DC_PV['h']):.0f}"
out['x_dc_pv_h_dir'] = 'rise' if DC_PV['h'] > 0 else 'fall'
# how much of the gain the unspent revenue takes with it, in words that turn with the numbers
_keep = DC_PV['cev'] / _tfc if _tfc else 1
out['x_dc_pv_share_word'] = ('nearly all of' if _keep < 0.1 else 'most of' if _keep < 0.5 else 'part of'
                             if _keep < 1 else 'none of')
# the cheaper drug: against the gain when it is not cheaper
# (round r115, the author: 'the gain' -> 'overall gain')
out['x_dc_p_dir'] = 'works against the overall gain' if DC_P['cev'] > _tfc else 'adds to the overall gain'
out['x_dc_p_cmp'] = 'larger' if DC_P['cev'] > _tfc else 'smaller'
# THE SCREEN ALONE (the author, 3 October: "can you also do constant price and constant piv?"): Treatment First with
# both pi_V and the drug price held (code/extra_2c/remote_decomp_2c_both.sh, results/decomp_2c_both). Read in the order
# screen -> its price response (fixpv) -> recycling (tf): what the cheaper drug takes back of the screen's gain, and
# how much of that loss recycling the revenue restores, in words that turn with the numbers
DC_B = _dc('fixboth', 'decomp_2c_both')
out['x_dc_b_cev'] = f"{DC_B['cev']:.2f}"
_lost = (DC_B['cev'] - DC_PV['cev']) / DC_B['cev'] if DC_B['cev'] else 0
_back = (_tfc - DC_PV['cev']) / (DC_B['cev'] - DC_PV['cev']) if DC_B['cev'] != DC_PV['cev'] else 0
_share = lambda x: 'nearly all of' if x >= 0.9 else 'most of' if x >= 0.5 else 'part of'
out['x_dc_b_takeback'] = _share(_lost)
out['x_dc_b_restore'] = _share(_back)
out['x_dc_b_source'] = ('the screen on its own delivers more than the whole reform' if DC_B['cev'] > _tfc else
                        'the screen on its own delivers most of the gain')
# THE DRUG TEST'S COST, as the model charges it.  The declaration's comment says the
# value is in units of average earnings; the budget charges it raw (f90 20654), in
# the units in which productivity averages one at entry.  So it is quoted against the
# benchmark's average labour income, as Section 5 quotes the SSI floor.
# AVERAGE LABOUR INCOME OF THE omega_c = 0.085 BENCHMARK (2 October), the model's own, saved with it.
# It was read from the arm's log, which for the old arms was the old benchmark's.
_avg_lab = float(gzip.open(os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085', 'files',
                                        'average_labor_incomebaseline_benchmark.dat.gz'), 'rt').read().split()[0])
_fn = json.load(open(os.path.join(HERE, 'fortran_numbers.json')))
_ctest = float(_fn['f_cost_per_drug_test'])
out['x_ctest_earn_pc'] = f'{100 * _ctest / _avg_lab:.2g}'
# IN DOLLARS, at the paper's dollar scale: average labour income is the value of a statistical
# life over its multiple, \$9m / vsl_data (Block 1), so the test is _ctest / _avg_lab of that
# (the author, 2 October: "give it in dollars too")
out['x_ctest_usd'] = f'{_ctest / _avg_lab * 9e6 / float(_fn["f_vsl_data"]):.0f}'
# the declared value was meant as the assay cost as a share of average earnings, so the
# cost the model charges is below it when average labour income exceeds one
out['x_ctest_vs_assay'] = 'below' if _avg_lab > 1 else 'above'
# the share of net government revenue that the tests cost under Treatment First
_tests = [float(l.split()[-1]) for l in open(os.path.join(adir('tf85'), 'final.txt'))
          if l.strip().startswith('drug-test cost')][0]
out['x_ctest_budget_pc'] = f"{100 * _tests / tf['net government revenue']['level']:.2g}"
_ho = {}
for l in open(os.path.join(adir('tf85'), 'PARAM_HANDOVER.arm.txt')):
    f = l.split()
    if len(f) >= 2:
        _ho[f[0]] = f[1]
out['x_tf_pdet_pc'] = pc(100 * float(_ho['probability_of_detection']))
# THE DETECTION RATE AGAINST THE EVIDENCE the paragraph quotes (the author, 2 October: "85% is
# conservative ... it would mean less of an effect of TF"): office screens detected 92.5 per cent of
# opioid use against LC-MS/MS (Manchikanti et al. 2011), laboratory screens 96 to 100 (Walsh et al.
# 2025). The words turn if the rate is ever set at or above the lower of the two.
_pd = 100 * float(_ho['probability_of_detection'])
out['x_tf_pdet_where'] = 'below' if _pd < 92.5 else 'at or above'
out['x_tf_pdet_so'] = (', to be conservative, since a lower rate weakens Treatment First'
                       if _pd < 92.5 else '')
out['x_tf_pfp_pc'] = pc(100 * float(_ho['probability_of_false_positive']))
assert _ho.get('include_voucher_exclusion') == '1', 'tf85 ran without exclusion?'
# the release rate out of exclusion is a compile-time parameter (f90 657), 1/3
_psi = float(json.load(open(os.path.join(HERE, 'fortran_numbers.json')))['f_voucher_exclusion_release'])
out['x_psi_x'] = '1/3' if abs(_psi - 1 / 3) < 1e-5 else f'{_psi:.2f}'
out['x_ban_years'] = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}.get(round(1 / _psi), f'{1 / _psi:.0f}')
# THE EXCLUSION AGAINST THE VOUCHER PROGRAMME'S OWN RULE (the author, 2 October: "Is this also in
# line with current programme rules? if so cite some reason"): 24 CFR 982.553 bars for three years a
# household evicted from federally assisted housing for drug-related criminal activity
out['x_ban_rule_lead'] = ('the same period for which' if round(1 / _psi) == 3 else
                          'against the three years for which')

om = final('omega1')
out['x_om_b_pc'] = pc(om['drug use b']['pc'])
out['x_om_sud_pc'] = pc(om['SUD lambda_d']['pc'])
out['x_om_h_pc'] = pc(om['homelessness h_1']['pc'])

# CHILDHOOD HOMELESSNESS: a child lives with its parent from the parent's age 26
# to 50 (child_at_home_last_index = 25 model years), so the share of children on
# the street is the mass-weighted homelessness of households aged 26-50, from the
# last DIAG age profile each run printed.
def child_homeless(arm):
    rows = {}
    for l in gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace'):
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=\s*(\S+).*mass=\s*(\S+)', l)
        if m:
            rows[int(m.group(1))] = (float(m.group(2)), float(m.group(3)))
    ages = [a for a in rows if 26 <= a <= 50]
    return sum(rows[a][0] * rows[a][1] for a in ages) / sum(rows[a][1] for a in ages)


hc0 = child_homeless('null_share')
out['x_tf_hchild_pc'] = pc(100 * (child_homeless('tf85') / hc0 - 1))
out['x_hchild0'] = f'{100 * hc0:.2f}'
out['x_tf_hchild1'] = f"{100 * child_homeless('tf85'):.2f}"
out['x_tf_hchild_pp'] = f"{abs(float(out['x_tf_hchild1']) - float(out['x_hchild0'])):.2f}"
out['x_tf_hchild_dir'] = 'rises' if child_homeless('tf85') > hc0 else 'falls'
# the SUD rate, all adults, levels and the fall in points, for the comparison
# with childhood homelessness in the same units
out['x_sud0'] = f"{tf['SUD lambda_d']['base'] * 100:.2f}"
out['x_tf_sud1'] = f"{tf['SUD lambda_d']['level'] * 100:.2f}"
out['x_tf_sud_pp'] = f"{abs(tf['SUD lambda_d']['level'] - tf['SUD lambda_d']['base']) * 100:.2f}"
out['x_om_hchild_pc'] = pc(100 * (child_homeless('omega1') / hc0 - 1))

# CHILDREN LIVING WITH A PARENT WHO HAS A SUD, the comparison to the children on
# the street above, over the same ages 26-50 and the same mass weights. The age
# profile's sud= column is drug CONSUMPTION (is_addicted = consumes), so the
# disorder is read from DIAG disorder rate, band k, where band 1 is ages 26-34,
# 2 is 35-44 and 3 is 45-54; each age takes its band's rate, so ages 45-50 carry
# band 3's rate. The same banding reproduces the exact childhood homelessness
# above to within 0.02 points (1.001 against 1.015, 1.061 against 1.078).
def child_sud(arm):
    ages, band = {}, {}
    for l in gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace'):
        m = re.search(r'DIAG age\s+(\d+)\s+homeless=.*mass=\s*(\S+)', l)
        if m:
            ages[int(m.group(1))] = float(m.group(2))
        m = re.search(r'DIAG disorder rate, band\s+(\d)\s+=\s*(\S+)', l)
        if m:
            band[int(m.group(1))] = float(m.group(2))
    k = lambda a: 1 if a <= 34 else 2 if a <= 44 else 3
    aa = [a for a in ages if 26 <= a <= 50]
    return sum(band[k(a)] * ages[a] for a in aa) / sum(ages[a] for a in aa)


sc0, sc1 = child_sud('null_share'), child_sud('tf85')
out['x_sudchild0'] = f'{100 * sc0:.2f}'
out['x_tf_sudchild1'] = f'{100 * sc1:.2f}'
# from the two levels as printed, so that the three numbers agree (5.28 - 3.69 = 1.59)
out['x_tf_sudchild_pp'] = f"{abs(float(out['x_tf_sudchild1']) - float(out['x_sudchild0'])):.2f}"
out['x_tf_sudchild_dir'] = 'falls' if sc1 < sc0 else 'rises'
# the shelter sentence opens with 'In contrast' (the author, 2 October) only when the share of
# children in a shelter moves the other way from the share living with a parent who carries a SUD
out['x_tf_hchild_lead'] = ('In contrast, the' if (child_homeless('tf85') > hc0) != (sc1 > sc0) else 'The')
# STAGE D: THE SENTENCES THAT TURN WITH THE CHILDREN'S SHELTER SHARE. On the omega_c = 0.085 arms
# Treatment First lowers homelessness and leaves the share of children in a shelter where it was
# (1.03 to 1.03 at the $22 test), so 'rises by 0.00 percentage points' and 'runs in both directions'
# would be false; each sentence is generated in three versions, rise, no change at two decimals,
# and fall, the rise being the text the paper had.
_hc1 = child_homeless('tf85')
_hpp = float(out['x_tf_hchild_pp'])
_hflat = _hpp < 0.005
_hcup = _hc1 > hc0 and not _hflat
a0, a1 = out['x_hchild0'], out['x_tf_hchild1']
if _hflat:
    # (round r134, the author's own text: "is essentially at 1.03 percent", read as 'essentially unchanged at')
    out['x_tf_hchild_sentence'] = (f"In the long run, the share of children in a shelter is essentially unchanged at "
                                   f"${a0}$ percent.")
    out['x_tf_hchild_even'] = f", while childhood homelessness stays at ${a0}$ percent of children"
    # (round 4ad85a30, the author: ", since aggregate homelessness slightly declines")
    # (round c88b1dda, the author: 'since' -> 'as')
    out['x_tf_hchild_since'] = (', as aggregate homelessness slightly declines'
                                if tf['homelessness h_1']['pc'] < 0 else '')
    out['x_tf_hchild_only'] = 'does not rise in the long run'
else:
    out['x_tf_hchild_sentence'] = (f"{out['x_tf_hchild_lead']} share of children in a shelter "
                                   f"{out['x_tf_hchild_dir']} from ${a0}$ to ${a1}$ percent, by "
                                   f"${out['x_tf_hchild_pp']}$ percentage points.")
    out['x_tf_hchild_even'] = (f", even as childhood homelessness rises by ${out['x_tf_hchild_pc']}$ percent, "
                               f"from ${a0}$ to ${a1}$ percent of children" if _hcup else
                               f", and childhood homelessness falls by ${out['x_tf_hchild_pc']}$ percent, "
                               f"from ${a0}$ to ${a1}$ percent of children")
    out['x_tf_hchild_since'] = ''
    out['x_tf_hchild_only'] = (f"rises by only ${out['x_tf_hchild_pp']}$ percentage points" if _hcup else
                               f"falls by ${out['x_tf_hchild_pp']}$ percentage points")
out['x_tf_kids_dir'] = 'runs in both directions' if _hcup else 'runs one way'
# the introduction's penalty sentence (round c88b1dda, the author: "because child homelessness in the long run
# stays the same")
# the level, folded into the author's sentence (round 20b4ddb5: the introduction's gain paragraph rewritten)
out['x_tf_pen_level'] = (f", at ${out['x_hchild0']}$ percent of children, with aggregate homelessness slightly declining"
                         if _hflat and tf['homelessness h_1']['pc'] < 0 else '')
out['x_tf_pen_because'] = (', because childhood homelessness stays the same in the long run' if _hflat else
                           f": the share of children in shelters {out['x_tf_hchild_only']}, while the share of "
                           f"children living with a parent who has a SUD {out['x_tf_sudchild_dir']} by "
                           f"${out['x_tf_sudchild_pp']}$ points")
# the introduction's homelessness clause
out['x_tf_h_clause'] = (f", but raises homelessness by ${out['x_tf_h_pc']}$ percent" if _hrise else
                        f", and lowers homelessness by ${out['x_tf_h_pc']}$ percent")
# THE kappa_x ITEM OF SECTION 5 (the author, 2 October: "make sure the prose everywhere is consistent"):
# a higher disamenity loads whichever policy houses more people, and in the long run that is Treatment
# First once it lowers homelessness, so the 'favours Housing First' argument for the high-end value
# holds only for a rise
out['x_kx_sentence'] = (
    'As it rises the aggregate homelessness externality increases, which loads whichever policy houses '
    'more people, which in this model is Housing First. I therefore take a value from the high end of the '
    'estimates, so that if Treatment First still ranks above Housing First, it does so under an assumption '
    'that favours Housing First.' if _hrise else
    'As it rises the aggregate homelessness externality increases, which loads whichever policy houses '
    # the rest removed (round 4ad85a30, the author: "remove", twice)
    'more people.')
# THE DISCUSSION'S PENALTY SENTENCE ('what the model does not have'): a penalty for growing up in a shelter
# works against Treatment First only if the share of children in a shelter rises
_sud_pp = out['x_tf_sudchild_pp']
out['x_disc_penalty'] = (
    f"A penalty of that kind would work against Treatment First, but on few children: the share of children "
    f"in a shelter rises by ${out['x_tf_hchild_pp']}$ percentage points while the share living with a parent "
    f"who carries a SUD {out['x_tf_sudchild_dir']} by ${_sud_pp}$." if _hcup else
    f"A penalty of that kind would not work against Treatment First in the long run, where the share of "
    f"children in a shelter does not rise while the share living with a parent who carries a SUD "
    f"{out['x_tf_sudchild_dir']} by ${_sud_pp}$ percentage points." if _hflat else
    f"A penalty of that kind would work in favour of Treatment First in the long run, where the share of "
    f"children in a shelter falls by ${out['x_tf_hchild_pp']}$ percentage points and the share living with a "
    f"parent who carries a SUD {out['x_tf_sudchild_dir']} by ${_sud_pp}$.")
# TABLE 6'S TRANSMISSION BLOCK, against the results (round c88b1dda, the consistency check of Sections 3-5): the
# tilt of the two odds ratios read against what Treatment First does to the share of children in a shelter; the
# old sentence said the over-transmission of homelessness loads the model toward Housing First, which holds only
# when Treatment First raises that share
_cal = json.load(open(os.path.join(HERE, 'calib_numbers.json')))
_sud_low = _cal.get('u_odds_sud_pos', '').startswith('at the low end') or _cal.get('u_odds_sud_pos') == 'below'
out['x_odds_hl_margin'] = '' if _hflat else ', the margin Housing First acts on'
out['x_odds_tilt_sentence'] = (
    'Since Treatment First leaves the share of children in a shelter roughly constant, the excess transmission of '
    'homelessness favours neither policy, while transmission of the SUD '
    + ('at the low end of' if _cal.get('u_odds_sud_pos', '').startswith('at the low end') else 'below')
    + ' the evidence understates what Treatment First does for children, so if it still raises welfare in the '
    'experiments below, that result is conservative.' if _hflat and _sud_low else
    f"The model loads the externality on children towards {_cal['u_odds_tilt']} more than "
    f"{_cal['u_odds_tilt_other']}, so {_cal['u_odds_tilt_so']}.")
out['_tf_hchild_flat'] = _hflat
out['_tf_hchild_up'] = _hcup

# WHO THE NEWBORNS' PARENTS ARE, the channel any child penalty keys on: the
# share of newborns whose parent is homeless, and whose parent has a SUD, in
# percentage points, from the last newborn_parent_share each run printed
# (clean housed, disordered housed, clean street, disordered street).
def parent_share(arm):
    last = None
    for l in gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace'):
        if 'newborn_parent_share (clean housed' in l:
            last = [float(x) for x in l.split('=')[1].split()]
    return last


p0, p1 = parent_share('null_share'), parent_share('tf85')
out['x_tf_par_hl_pp'] = f"{100 * ((p1[2] + p1[3]) - (p0[2] + p0[3])):.2f}"
out['x_tf_par_sud_pp'] = f"{abs(100 * ((p1[1] + p1[3]) - (p0[1] + p0[3]))):.2f}"

# THE TRANSITION: restart 3's loop 0, pinned (see the docstring). ITS BASELINES ARE THE OLD ARMS
# (see ARMDIR): the no-policy run and Treatment First it was solved between
CEV0_TR = cev_log('old_null_share')
tf_tr = final('old_tf85')
hc0_tr = child_homeless('old_null_share')
out['x_tr_lr_cev'] = f"{last_cev('old_tf85') - CEV0_TR:.2f}"
out['_cev_null_share_tr'] = CEV0_TR
# the long run the transition prose compares its path with: the old Treatment First's homelessness change
out['x_tr_lr_h_pc'] = pc(tf_tr['homelessness h_1']['pc'])
out['x_tr_hchild0'] = f'{100 * hc0_tr:.2f}'
sys.path.insert(0, HERE)
from transition_source import LOG as best   # the one pin
tr_dir = os.path.join(ROOT, 'code', 'trtf60')
if not re.search(r'TRANSITION WELFARE loop=\s*\d+\s+t=\s*26 ', open(best, errors='replace').read()):
    sys.exit(f'{best} does not reach period 26')
cc = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'transition_fix', 'cohort_cev.py'),
                     best, TR_CURVE, '--refs', os.path.join(adir('old_null_share'), 'cf.log.gz'),
                     os.path.join(adir('old_tf85'), 'cf.log.gz')],
                    capture_output=True, text=True).stdout
m = re.search(r'THE COHORT BORN AT THE REFORM \(b = 1\): CEV ([+-]\S+)%', cc)
out['x_tr_cev_b1'] = f'{float(m.group(1)) - CEV0_TR:.1f}'
out['x_tr_cev_b1_2'] = f'{float(m.group(1)) - CEV0_TR:.2f}'
# (round f9ac1593, the author on ', against 1.39 percent in the long run.': "incorrect....need to use updated
# figures", 'consumption,' -> 'consumption, even more than...'): against the long run of the SAME computation,
# which is the only one the path converges to; the paper's long run (4.33) is the new arms', whose transition
# (stage E) has not finished a pass
_b1x, _lrx = float(m.group(1)) - CEV0_TR, float(out['x_tr_lr_cev'])
out['x_tr_cev_b1_vs_lr'] = ('even more than those born in the long run' if _b1x > _lrx else
                            'less than those born in the long run')
# THE DISCUSSION'S TRANSITION (round f4276e76, the author on 'The transition is harder': "I don't think it's harder.
# I think it has even higher welfare....but from a policy point of view it can look decieving because homelessness
# would rise for a while"): the cohort born at the reform against the long run of the same computation
_b1, _lr = float(m.group(1)) - CEV0_TR, float(out['x_tr_lr_cev'])
# (round 0e3b2441, the author: 'The transition is not hard' -> remove, 'years' -> "(because households with SUD who
# have not had enough time to recover keep it demand elevated) insert it nicely", 'use.' -> ", thus raising their
# childhood consumption even more in the transition")
out['x_disc_tr_kids'] = (
    'Children born at the reform gain even more than those born in the long run. The drug price stays high for '
    'years, because households with a SUD who have not yet had time to recover keep demand for it elevated. The '
    "high price keeps more of these children's parents from starting to use, thus raising their childhood "
    'consumption even more in the transition.'
    if _b1 > _lr > 0 else
    'Children born at the reform gain less than those born in the long run, because they grow up while the share of '
    'parents carrying a SUD is still close to its Housing First level, but they still gain.' if _lr > _b1 > 0 else '')
m = re.search(r'forward pass (\d+) of', cc)
out['x_tr_pass'] = m.group(1)
# THE REFORM COHORT'S GAIN IS A CHILDHOOD GAIN (the author, 29 September: the transition's
# larger drop in use "diverts more resources in transition to the children"): its
# childhood gain over the long run's, in utils, from cohort_cev.py's split
g_b1 = float(re.search(r'gain on no policy\s+([+-]\S+)', cc).group(1))
g_lr = float(re.search(r'long-run gain\s+([+-]\S+)', cc).group(1))
out['x_tr_kid_ratio'] = f'{g_b1 / g_lr:.1f}'

# no-policy baselines for the transition's changes, and the benchmark's two
# UNTARGETED intergenerational odds ratios (a child of a parent with a SUD
# acquiring one; a child of a homeless parent becoming homeless), the last
# printed values in the no-policy run on the corrected build
h0 = e0 = None
for l in gzip.open(os.path.join(adir('old_null_share'), 'cf.log.gz'), 'rt', errors='replace'):
    if 'model_fraction_homeless=' in l:
        h0 = float(l.split('=')[1].split()[0])
    elif 'total_experimenters_1=' in l:
        e0 = float(l.split('=')[1].split()[0])
    elif 'UNTARGETED delta_d child SUD odds ratio' in l:
        out['x_odds_sud'] = f"{float(l.split('model=')[1].split()[0]):.2f}"
    elif 'UNTARGETED delta_h child homeless odds ratio' in l:
        out['x_odds_hl'] = f"{float(l.split('model=')[1].split()[0]):.2f}"

# the first forward pass in that log, years 1-10: peak homelessness, and drug users WITHOUT A SUD
# (exp_pop; total_experimenters_1 in the steady state, the same count on the same base: the
# no-reform control's t = 1 value equals the no-policy steady state's, 2.3726) at t = 1
H, E = {}, {}
t = None
for l in open(best, errors='replace'):
    if 'TRANSITION INIT PARENT SHARE RESTORED' in l and H:
        break
    if 'TRANSITION MECH t=' in l:
        t = int(l.split('t=')[1].split()[0])
        H[t] = float(re.search(r'h_1=\s*(\S+)', l).group(1))
    elif 'TRANSITION SMIDRUG t=' in l:
        E[t] = float(re.search(r'exp_pop=\s*(\S+)', l).group(1))
# long-run drug users without a SUD under Treatment First, for the transition's comparison
e_tf = None
for l in gzip.open(os.path.join(adir('old_tf85'), 'cf.log.gz'), 'rt', errors='replace'):
    if 'total_experimenters_1=' in l:
        e_tf = float(l.split('=')[1].split()[0])
out['x_tf_new_pc'] = pc(100 * (e_tf / e0 - 1))
out['x_tr_h_peak_pc'] = pc(100 * (max(H[k] for k in range(1, 11)) / h0 - 1))
out['x_tr_new_t1_pc'] = pc(100 * (E[1] / e0 - 1))
# the largest fall in drug users without a SUD over the same first decade, for 'falls by up to'
out['x_tr_new_peak_pc'] = pc(100 * (min(E[k] for k in range(1, 11)) / e0 - 1))
# THE TRANSITION AGAINST THE PAPER'S LONG RUN (round c88b1dda, the author, of 'against 29 and 6 percent in the
# long run': "need to correct this. also need to explain why here it raises homelessness"). The path is still
# the old arms' (stage E is re-solving it); its long-run comparison is the omega_c = 0.085 Treatment First of
# Section 6.2, so the introduction and the Discussion agree with 6.2
def _exp(arm):
    v = None
    for l in gzip.open(os.path.join(adir(arm), 'cf.log.gz'), 'rt', errors='replace'):
        if 'total_experimenters_1=' in l:
            v = float(l.split('=')[1].split()[0])
    return v
_e_lr = 100 * (_exp('tf85') / _exp('null_share') - 1)
_h_lr = tf['homelessness h_1']['pc']
out['x_tr_lr_compare'] = (
    f", whereas in the long run the number without a SUD falls by ${abs(_e_lr):.0f}$ percent and homelessness "
    f"{'falls' if _h_lr < 0 else 'rises'} by ${abs(_h_lr):.0f}$ percent" if _h_lr < 0 else
    f", against ${abs(_e_lr):.0f}$ and ${abs(_h_lr):.0f}$ percent in the long run, respectively")
out['x_tr_h_rise_why'] = (
    'Homelessness rises at first because the households that already carry a SUD when the reform lands lose '
    'their vouchers at once, whereas the fall in the number with a SUD, which is what lowers homelessness in the '
    'long run, takes years, since recovery is slow.'
    if max(H[k] for k in range(1, 11)) > h0 and _h_lr < 0 else '')
out['x_tr_h_lr_disc'] = (f", whereas in the long run it lowers homelessness by ${abs(_h_lr):.0f}$ percent" if _h_lr < 0
                         else f", against ${abs(_h_lr):.0f}$ percent in the long run")
# whether that first-decade fall in users without a SUD is larger than the long run's, as a word
out['x_tr_new_vs_lr'] = 'larger' if min(E[k] for k in range(1, 11)) < e_tf else 'smaller'
# drug use (participation b) in the same first decade, its largest fall on no
# policy, against the long run's x_tf_b_pc
B = {}
for l in open(best, errors='replace'):
    if 'TRANSITION INIT PARENT SHARE RESTORED' in l and B:
        break
    if 'TRANSITION MECH t=' in l:
        B[int(l.split('t=')[1].split()[0])] = float(re.search(r' b=\s*(\S+)', l).group(1))
out['x_tr_b_peak_pc'] = pc(100 * (min(B[k] for k in range(1, 11)) / tf_tr['drug use b']['base'] - 1))

# CHILDHOOD HOMELESSNESS OF THE COHORT BORN AT THE REFORM, on x_hchild0's base (ages
# 26-50, mass-weighted), followed down the diagonal: a child born in year 1 is at
# home while its parent is 26 to 50, which is age index t in year t, t = 1..25.
#
# THE BY-AGE PRINT IS NOT A SHARE IN LOOP 0. The division by mass_by_age runs before
# the routine that fills the mass, so loop 0 divides by the 1e-14 floor and prints the
# raw homeless mass times 1e14; a later loop divides by the previous loop's mass
# (CALIBRATION_STATE, 29 September 07:15). So the scale is not assumed: each period is
# read both ways and must reproduce that period's h_1 on its MECH line, or nothing is
# written.
HB, MB = {}, {}
for l in open(best, errors='replace'):
    if 'TRANSITION INIT PARENT SHARE RESTORED' in l and HB:
        break
    for tag, D in (('HOMELESS_BY_AGE', HB), ('MASS_BY_AGE', MB)):
        if l.startswith(' TRANSITION ' + tag + ' t='):
            f = l.split('t=')[1].split()
            D[int(f[0])] = [float(x) for x in f[1:]]
share = {}
for t in HB:
    raw_floor = [x * 1e-14 for x in HB[t]]
    raw_share = [x * m for x, m in zip(HB[t], MB[t])]
    # loop 0 prints masses x 1e14 (exact to 1e-13); later loops print shares, exact only to about 1e-4 relative
    for raw, tol in ((raw_floor, 1e-6), (raw_share, 5e-4)):
        if abs(sum(raw) / sum(MB[t]) / H[t] - 1) < tol:
            share[t] = [r / m if m > 0 else 0.0 for r, m in zip(raw, MB[t])]
            break
    else:
        sys.exit(f'HOMELESS_BY_AGE at t={t} reproduces h_1 on neither scale')
if not all(t in share for t in range(1, 26)):
    sys.exit('the forward pass does not cover the first cohort\'s childhood')
w = [MB[t][t - 1] for t in range(1, 26)]
hc_b1 = sum(share[t][t - 1] * w[t - 1] for t in range(1, 26)) / sum(w)
out['x_tr_hchild_b1'] = f'{100 * hc_b1:.2f}'
out['x_tr_hchild_b1_pc'] = pc(100 * (hc_b1 / hc0_tr - 1))
# and in percentage points, the author 29 September: a relative change beside two levels
# read as inconsistent with them
out['x_tr_hchild_b1_pp'] = f'{abs(100 * (hc_b1 - hc0_tr)):.2f}'
# 'rises by less than in the long run' (the author, 29 September): the comparison word comes
# from the two rises, the cohort born at the reform against children born in the long run
out['x_tr_hchild_vs_lr'] = 'less than' if hc_b1 < child_homeless('old_tf85') else 'more than'
# the direction word the prose takes, from the numbers, not typed
out['x_tr_hchild_b1_dir'] = 'rises' if hc_b1 > hc0_tr else 'falls'
# and ALL children at home in each of the first ten years, the cross section on the same
# base: its largest rise, for 'rises by up to'
hc_cross = {t: sum(share[t][a] * MB[t][a] for a in range(25)) / sum(MB[t][:25]) for t in share}
out['x_tr_hchild_peak_pc'] = pc(100 * (max(hc_cross[t] for t in range(1, 11)) / hc0_tr - 1))
out['x_tr_hchild_peak'] = f'{100 * max(hc_cross[t] for t in range(1, 11)):.2f}'
out['x_tr_hchild_peak_dir'] = 'rises' if max(hc_cross[t] for t in range(1, 11)) > hc0_tr else 'falls'

json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(f'wrote {OUT} (transition from {os.path.relpath(best, ROOT)}, forward pass {out["x_tr_pass"]})')
for k, v in sorted(out.items()):
    print(f'  {k} = {v}')
# the names the other two exporters own, merged back so the file is whole
for f in ('export_elasticity.py', 'export_longrun.py', 'transition_figure.py'):
    r = subprocess.run([sys.executable, os.path.join(HERE, f)], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f'{f} failed:\n{r.stdout}\n{r.stderr}')
    print(f'  + {f}: {r.stdout.strip().splitlines()[0]}')
