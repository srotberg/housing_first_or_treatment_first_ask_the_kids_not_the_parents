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
RES = os.path.join(ROOT, 'results', 'counterfactuals_cf_fix2')
OUT = os.path.join(HERE, 'results_numbers.json')


def final(arm):
    """change in per cent, and levels, of each line of an arm's final.txt"""
    rows = {}
    for l in open(os.path.join(RES, arm, 'final.txt')):
        m = re.match(r'\s+(.+?)\s{2,}(\S+)\s+no policy\s+(\S+)\s+change\s+(\S+)%', l)
        if m:
            rows[m.group(1).strip()] = dict(level=float(m.group(2)), base=float(m.group(3)),
                                            pc=float(m.group(4)))
        m = re.search(r'childhood ([+-]\S+), adult part ([+-]\S+), total ([+-]\S+)', l)
        if m:
            rows['split'] = dict(child=float(m.group(1)), adult=float(m.group(2)),
                                 total=float(m.group(3)))
    return rows


def last_cev(arm):
    """CEV at the exit pass, from passes.txt (the last row)"""
    rows = [l.split() for l in open(os.path.join(RES, arm, 'passes.txt'))
            if l.strip() and l.split()[0].isdigit()]
    return float(rows[-1][-1].rstrip('%'))


def cev_log(arm):
    """the arm's CEV off the benchmark's curve, per cent, from its cf.log.gz"""
    x = None
    for l in gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace'):
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
out['x_tf_cev'] = f"{last_cev('tf85') - CEV0:.2f}"
out['x_tf_cev_dir'] = 'better' if last_cev('tf85') > CEV0 else 'worse'
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
# THE DRUG TEST'S COST, as the model charges it.  The declaration's comment says the
# value is in units of average earnings; the budget charges it raw (f90 20654), in
# the units in which productivity averages one at entry.  So it is quoted against the
# benchmark's average labour income, as Section 5 quotes the SSI floor.
_avg_lab = None
for l in gzip.open(os.path.join(RES, 'tf85', 'cf.log.gz'), 'rt', errors='replace'):
    if 'average_labor_income_calibrated=' in l:
        _avg_lab = float(l.split('=')[1].split()[0])
        break
_ctest = float(json.load(open(os.path.join(HERE, 'fortran_numbers.json')))['f_cost_per_drug_test'])
out['x_ctest_earn_pc'] = f'{100 * _ctest / _avg_lab:.2g}'
# the declared value was meant as the assay cost as a share of average earnings, so the
# cost the model charges is below it when average labour income exceeds one
out['x_ctest_vs_assay'] = 'below' if _avg_lab > 1 else 'above'
# the share of net government revenue that the tests cost under Treatment First
_tests = [float(l.split()[-1]) for l in open(os.path.join(RES, 'tf85', 'final.txt'))
          if l.strip().startswith('drug-test cost')][0]
out['x_ctest_budget_pc'] = f"{100 * _tests / tf['net government revenue']['level']:.2g}"
_ho = {}
for l in open(os.path.join(RES, 'tf85', 'PARAM_HANDOVER.arm.txt')):
    f = l.split()
    if len(f) >= 2:
        _ho[f[0]] = f[1]
out['x_tf_pdet_pc'] = pc(100 * float(_ho['probability_of_detection']))
out['x_tf_pfp_pc'] = pc(100 * float(_ho['probability_of_false_positive']))
assert _ho.get('include_voucher_exclusion') == '1', 'tf85 ran without exclusion?'
# the release rate out of exclusion is a compile-time parameter (f90 657), 1/3
_psi = float(json.load(open(os.path.join(HERE, 'fortran_numbers.json')))['f_voucher_exclusion_release'])
out['x_psi_x'] = '1/3' if abs(_psi - 1 / 3) < 1e-5 else f'{_psi:.2f}'
out['x_ban_years'] = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five'}.get(round(1 / _psi), f'{1 / _psi:.0f}')

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
    for l in gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace'):
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
    for l in gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace'):
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

# WHO THE NEWBORNS' PARENTS ARE, the channel any child penalty keys on: the
# share of newborns whose parent is homeless, and whose parent has a SUD, in
# percentage points, from the last newborn_parent_share each run printed
# (clean housed, disordered housed, clean street, disordered street).
def parent_share(arm):
    last = None
    for l in gzip.open(os.path.join(RES, arm, 'cf.log.gz'), 'rt', errors='replace'):
        if 'newborn_parent_share (clean housed' in l:
            last = [float(x) for x in l.split('=')[1].split()]
    return last


p0, p1 = parent_share('null_share'), parent_share('tf85')
out['x_tf_par_hl_pp'] = f"{100 * ((p1[2] + p1[3]) - (p0[2] + p0[3])):.2f}"
out['x_tf_par_sud_pp'] = f"{abs(100 * ((p1[1] + p1[3]) - (p0[1] + p0[3]))):.2f}"

# THE TRANSITION: restart 3's loop 0, pinned (see the docstring)
best = os.path.join(ROOT, 'code', 'trtf60', 'restart3_killed_1323', 'run.log')
tr_dir = os.path.join(ROOT, 'code', 'trtf60')
if not re.search(r'TRANSITION WELFARE loop=\s*\d+\s+t=\s*26 ', open(best, errors='replace').read()):
    sys.exit(f'{best} does not reach period 26')
cc = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'transition_fix', 'cohort_cev.py'),
                     best, os.path.join(tr_dir, 'welfare_curvebaseline_benchmark.dat')],
                    capture_output=True, text=True).stdout
m = re.search(r'THE COHORT BORN AT THE REFORM \(b = 1\): CEV ([+-]\S+)%', cc)
out['x_tr_cev_b1'] = f'{float(m.group(1)) - CEV0:.1f}'
out['x_tr_cev_b1_2'] = f'{float(m.group(1)) - CEV0:.2f}'
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
for l in gzip.open(os.path.join(RES, 'null_share', 'cf.log.gz'), 'rt', errors='replace'):
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
for l in gzip.open(os.path.join(RES, 'tf85', 'cf.log.gz'), 'rt', errors='replace'):
    if 'total_experimenters_1=' in l:
        e_tf = float(l.split('=')[1].split()[0])
out['x_tf_new_pc'] = pc(100 * (e_tf / e0 - 1))
out['x_tr_h_peak_pc'] = pc(100 * (max(H[k] for k in range(1, 11)) / h0 - 1))
out['x_tr_new_t1_pc'] = pc(100 * (E[1] / e0 - 1))
# the largest fall in drug users without a SUD over the same first decade, for 'falls by up to'
out['x_tr_new_peak_pc'] = pc(100 * (min(E[k] for k in range(1, 11)) / e0 - 1))
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
out['x_tr_b_peak_pc'] = pc(100 * (min(B[k] for k in range(1, 11)) / tf['drug use b']['base'] - 1))

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
    for raw in (raw_floor, raw_share):
        if abs(sum(raw) / sum(MB[t]) / H[t] - 1) < 1e-6:
            share[t] = [r / m if m > 0 else 0.0 for r, m in zip(raw, MB[t])]
            break
    else:
        sys.exit(f'HOMELESS_BY_AGE at t={t} reproduces h_1 on neither scale')
if not all(t in share for t in range(1, 26)):
    sys.exit('the forward pass does not cover the first cohort\'s childhood')
w = [MB[t][t - 1] for t in range(1, 26)]
hc_b1 = sum(share[t][t - 1] * w[t - 1] for t in range(1, 26)) / sum(w)
out['x_tr_hchild_b1'] = f'{100 * hc_b1:.2f}'
out['x_tr_hchild_b1_pc'] = pc(100 * (hc_b1 / hc0 - 1))
# and in percentage points, the author 29 September: a relative change beside two levels
# read as inconsistent with them
out['x_tr_hchild_b1_pp'] = f'{abs(100 * (hc_b1 - hc0)):.2f}'
# 'rises by less than in the long run' (the author, 29 September): the comparison word comes
# from the two rises, the cohort born at the reform against children born in the long run
out['x_tr_hchild_vs_lr'] = 'less than' if hc_b1 < child_homeless('tf85') else 'more than'
# the direction word the prose takes, from the numbers, not typed
out['x_tr_hchild_b1_dir'] = 'rises' if hc_b1 > hc0 else 'falls'
# and ALL children at home in each of the first ten years, the cross section on the same
# base: its largest rise, for 'rises by up to'
hc_cross = {t: sum(share[t][a] * MB[t][a] for a in range(25)) / sum(MB[t][:25]) for t in share}
out['x_tr_hchild_peak_pc'] = pc(100 * (max(hc_cross[t] for t in range(1, 11)) / hc0 - 1))
out['x_tr_hchild_peak'] = f'{100 * max(hc_cross[t] for t in range(1, 11)):.2f}'
out['x_tr_hchild_peak_dir'] = 'rises' if max(hc_cross[t] for t in range(1, 11)) > hc0 else 'falls'

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
