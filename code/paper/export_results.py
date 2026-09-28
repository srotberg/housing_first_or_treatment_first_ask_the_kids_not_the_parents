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
  code/trtf60/<latest run log with a forward pass to period 26>
                                                      the T = 60 transition

THE TRANSITION IS NOT CONVERGED. Its numbers are exported with the loop they
come from, and the prose must say they are preliminary; rerun this file when a
later loop lands and the sentence moves with it.
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


def pc(x, nd=0):
    return f'{abs(x):.{nd}f}'


out = {}

tf = final('tf85')
out['x_tf_b_pc'] = pc(tf['drug use b']['pc'])
out['x_tf_sud_pc'] = pc(tf['SUD lambda_d']['pc'])
out['x_tf_h_pc'] = pc(tf['homelessness h_1']['pc'])
out['x_tf_price_pc'] = pc(tf['drug price']['pc'])
out['x_tf_cev'] = f"{last_cev('tf85'):.2f}"
# the long-run gain splits about evenly between childhood and adulthood
out['x_tf_child_share_pc'] = pc(100 * tf['split']['child'] / tf['split']['total'])

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
out['x_om_hchild_pc'] = pc(100 * (child_homeless('omega1') / hc0 - 1))

# THE TRANSITION: the latest forward pass that reached period 26, anywhere under
# code/trtf60 (the live run.log or a run a container restart killed).
tr_dir = os.path.join(ROOT, 'code', 'trtf60')
cands = [p for p in glob.glob(os.path.join(tr_dir, '**', '*.log'), recursive=True)
         if 'TRANSITION WELFARE' in open(p, errors='replace').read(10 ** 9)]
best = None
for p in sorted(cands, key=os.path.getmtime, reverse=True):
    txt = open(p, errors='replace').read()
    if re.search(r'TRANSITION WELFARE loop=\s*\d+\s+t=\s*26 ', txt):
        best = p
        break
if best is None:
    sys.exit('no transition log reaches period 26')
cc = subprocess.run([sys.executable, os.path.join(ROOT, 'code', 'transition_fix', 'cohort_cev.py'),
                     best, os.path.join(tr_dir, 'welfare_curvebaseline_benchmark.dat')],
                    capture_output=True, text=True).stdout
m = re.search(r'THE COHORT BORN AT THE REFORM \(b = 1\): CEV ([+-]\S+)%', cc)
out['x_tr_cev_b1'] = f'{float(m.group(1)):.1f}'
m = re.search(r'forward pass (\d+) of', cc)
out['x_tr_pass'] = m.group(1)

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

# the first forward pass in that log, years 1-10: peak homelessness and new users at t = 1
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
# long-run new users under Treatment First, for the transition's comparison
e_tf = None
for l in gzip.open(os.path.join(RES, 'tf85', 'cf.log.gz'), 'rt', errors='replace'):
    if 'total_experimenters_1=' in l:
        e_tf = float(l.split('=')[1].split()[0])
out['x_tf_new_pc'] = pc(100 * (e_tf / e0 - 1))
out['x_tr_h_peak_pc'] = pc(100 * (max(H[k] for k in range(1, 11)) / h0 - 1))
out['x_tr_new_t1_pc'] = pc(100 * (E[1] / e0 - 1))

json.dump(out, open(OUT, 'w'), indent=1, sort_keys=True)
print(f'wrote {OUT} (transition from {os.path.relpath(best, ROOT)}, forward pass {out["x_tr_pass"]})')
for k, v in sorted(out.items()):
    print(f'  {k} = {v}')
