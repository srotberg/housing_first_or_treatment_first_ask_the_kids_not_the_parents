"""export_noescape.py -- THE STRICT RULE FOR THE DISCUSSION (17 October; the author: "I think then you can write the
conclusion", after the no-escape runs). Detection 1.00 and no exemption for treatment (rule CA, corrected Housing First):

  the long run       results/transition_2c_t70_CAb/arms: the T = 70 transition's own two arms, Housing First and the
                     terminal Treatment First arm with the drug price held at the best long-run pass (0.8017,
                     code/RULE_C_PLAN.md 23:58 and 03:45) and pi_V clearing; changes against that Housing First, and the
                     newborn CEV as export_results.py takes it (welfare_nok.cev_free of the arm less that of Housing First)
  the first years    results/revoked_2c_CA100/{tf,hf}10_run.log.gz: Block 7's ten-year paths, the screen alone with the
                     drug price and pi_V held at their Housing First levels, against Housing First's own path;
                     homelessness and the share of children in a shelter (households aged 26-50, as transition_series.py)
  the revoked        results/revoked_2c_street_CA100/tables.md: the share of the households the screen revokes that are
                     homeless in years 1-3 (against none of the same households with their voucher kept)

Writes the x_ne_* names into results_numbers.json; run after export_results.py, which rewrites that file whole."""
import gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
import welfare_nok  # noqa: E402
OUT = os.path.join(HERE, 'results_numbers.json')
ARMS = os.path.join(ROOT, 'results', 'transition_2c_t70_CAb', 'arms')
PATHS = os.path.join(ROOT, 'results', 'revoked_2c_CA100')
STREET = os.path.join(ROOT, 'results', 'revoked_2c_street_CA100', 'tables.md')


from trpaths import levels, path, child_steady, latest_loop  # noqa: E402  (moved there 19 October, export_alttrans.py reads them too)


n, t = levels(os.path.join(ARMS, 'arm_null', 'final.txt')), levels(os.path.join(ARMS, 'arm_tf', 'final.txt'))
pc = lambda k: 100 * (t[k] / n[k] - 1)
assert pc('homelessness h_1') < 0 and pc('drug use b') < 0
cev = welfare_nok.cev_free(os.path.join(ARMS, 'arm_tf')) - welfare_nok.cev_free(os.path.join(ARMS, 'arm_null'))
tf, hf = path(os.path.join(PATHS, 'tf10_run.log.gz')), path(os.path.join(PATHS, 'hf10_run.log.gz'))
T = sorted(k for k in tf if k in hf)
rise = {k: 100 * (tf[k][0] / hf[k][0] - 1) for k in T}
rise_c = {k: 100 * (tf[k][1] / hf[k][1] - 1) for k in T}
assert max(rise.values()) > 0 and max(rise_c.values()) > 0, 'the screen alone does not raise homelessness: rewrite lesson 2'
last = T[-1]
assert rise[last] > 0 and rise_c[last] > 0, 'no longer above Housing First by the last year: rewrite lesson 2'
S = open(STREET).read()
assert 'GUARD SUMMARY: PASS' in S
row = [l for l in S.split('## pooled, years 1-3')[1].splitlines() if l.startswith('| all (the four parts summed) |')][0]
c = [x.strip() for x in row.strip('|').split('|')]
hl_a = [float(x) for x in c[11].split('/')]
hl_b = [float(x) for x in c[12].split('/')]
assert max(hl_b) < 0.05, hl_b
out = {
    'x_ne_b_pc': f"{abs(pc('drug use b')):.0f}",
    'x_ne_sud_pc': f"{abs(pc('SUD lambda_d')):.0f}",
    'x_ne_h_pc': f"{abs(pc('homelessness h_1')):.0f}",
    # (round r333) the share of children in a shelter in the long run, against the same Housing First
    'x_ne_hchild_pc': f"{100 * abs(child_steady(os.path.join(ARMS, 'arm_tf')) / child_steady(os.path.join(ARMS, 'arm_null')) - 1):.0f}",
    'x_ne_piv_pc': f"{100 * t['pi_V (voucher probability)']:.2f}",
    'x_ne_cev': f'{cev:.2f}',
    'x_ne_so_h_pc': f'{max(rise.values()):.0f}',
    'x_ne_so_hchild_pc': f'{max(rise_c.values()):.0f}',
    'x_ne_so_last_yr': str(last),
    'x_ne_so_h_last_pc': f'{rise[last]:.0f}',
    'x_ne_so_hchild_last_pc': f'{rise_c[last]:.0f}',
    'x_ne_rv_hl': f'{sum(hl_a) / len(hl_a):.0f}',
}
# THE FULL TRANSITION AT 1.00 (round r334): the savings recycled every year, pi_V clearing, the price held at the best
# pass at the end; the latest archived loop of results/transition_2c_t70_CAb, else the partial loop-0 log its worker
# published (17 October, 17:40). Peak rises over the first years and the last year each is above Housing First.
TRD = os.path.join(ROOT, 'results', 'transition_2c_t70_CAb')
# (19 October, 23:40) the path with the drug price clearing too, remote_tr70_CAc.sh, once it has an archived loop: its
# loop 0 started from CAb's loop-0 paths, the same arms, and lets the price clear every year
_CAC = os.path.join(ROOT, 'results', 'transition_2c_t70_CAc')
if any(d.startswith('loop') and os.path.exists(os.path.join(_CAC, d, 'run.log.gz')) for d in os.listdir(_CAC)):
    TRD = _CAC
loops = sorted((d for d in os.listdir(TRD) if d.startswith('loop') and os.path.exists(os.path.join(TRD, d, 'run.log.gz'))),
               key=lambda d: int(d[4:]))
TRLOG = os.path.join(TRD, loops[-1], 'run.log.gz') if loops else os.path.join(TRD, 'partial_loop0_run.log.gz')
tr = path(TRLOG)
h0, c0 = levels(os.path.join(ARMS, 'arm_null', 'final.txt'))['homelessness h_1'], child_steady(os.path.join(ARMS, 'arm_null'))
TT = sorted(tr)
assert len(TT) >= 15, f'{TRLOG}: only {len(TT)} years'
up = [k for k in TT if tr[k][0] > h0]; upc = [k for k in TT if tr[k][1] > c0]
assert up and upc and max(up) < TT[-1] and max(upc) < TT[-1], 'the rise does not end within the years published'
out_tr = {
    'x_ne_tr_h_pc': f'{100 * (max(tr[k][0] for k in TT) / h0 - 1):.0f}',
    'x_ne_tr_hchild_pc': f'{100 * (max(tr[k][1] for k in TT) / c0 - 1):.0f}',
    'x_ne_tr_h_yrs': str(max(up)),
    'x_ne_tr_hchild_yrs': str(max(upc)),
}
# THE 0.20 RULE'S CHILDREN IN A SHELTER IN THE LONG RUN (round r334, the author: "what about childhood homelessness?"):
# from the terminal arm of its T = 70 transition (results/transition_2c_t70_CA20b/arms) once it lands; '--' until then
# (17 October, 22:30) NOT transition_2c_t70_CA20b: its terminal arm held the price at 0.9044 while pi_V re-cleared and
# ended with an implied supply price of 0.9118 (drug gap 7.4e-3 against 5e-3); remote_tr70_CA20d.sh re-solves it from
# the accepted free-price run with both markets clearing
# (18 October, 23:00) from the cleared long run itself, results/counterfactuals_2c/tf_pdet20_CAu (both markets inside
# their rules), against the corrected Housing First, as footnote 36's other numbers (export_ca.py): the held-price
# terminal arm of transition_2c_t70_CA20e gives -11.6 against this -11.2, its implied supply price 5.0e-3 off
A20T = os.path.join(ROOT, 'results', 'counterfactuals_2c', 'tf_pdet20_CAu', 'tf')
A20N = os.path.join(ROOT, 'results', 'decomp_2c_shares_Cu', 'arm_tf', 'null')
if os.path.exists(os.path.join(A20T, 'cf.log.gz')):
    out_tr['x_ne20_hchild_pc'] = f"{100 * abs(child_steady(A20T) / child_steady(A20N) - 1):.0f}"
else:
    out_tr['x_ne20_hchild_pc'] = '--'
# THE 0.20 RULE'S FIRST YEARS (round r353, the author on "lowers them even along the transition": "Need to fix this").
# Block 7's ten-year paths at 0.20 (results/revoked_2c_CA20, the screen alone with the drug price and pi_V held at their
# Housing First levels) raise homelessness too, by less than catching every user does along its transition; the 0.20
# no-escape transition (results/transition_2c_t70_CA20e) replaces them when it lands
tf20, hf20 = path(os.path.join(ROOT, 'results', 'revoked_2c_CA20', 'tf10_run.log.gz')), \
    path(os.path.join(ROOT, 'results', 'revoked_2c_CA20', 'hf10_run.log.gz'))
T20 = sorted(k for k in tf20 if k in hf20)
r20 = max(100 * (tf20[k][0] / hf20[k][0] - 1) for k in T20)
r20c = max(100 * (tf20[k][1] / hf20[k][1] - 1) for k in T20)
assert r20 > 0 and r20c > 0, 'the 0.20 screen alone no longer raises homelessness: rewrite 6.4 and the third lesson'
# (21 October) the 0.20 no-exemption transition itself has landed (results/transition_2c_t70_CA20e/loop0; the hedge
# _CAne20 if it has none): its peaks replace the screen-only paths above, and 6.5 drops "before its savings are
# recycled and the drug price falls"
L20 = latest_loop(os.path.join(ROOT, 'results', 'transition_2c_t70_CA20e')) or \
    latest_loop(os.path.join(ROOT, 'results', 'transition_2c_t70_CAne20'))
if L20:
    p20 = path(os.path.join(L20, 'run.log.gz'))
    r20 = 100 * (max(v[0] for v in p20.values()) / h0 - 1)
    r20c = 100 * (max(v[1] for v in p20.values()) / c0 - 1)
r100, r100c = float(out_tr['x_ne_tr_h_pc']), float(out_tr['x_ne_tr_hchild_pc'])
out_tr['x_ne20_so_h_pc'] = f'{r20:.0f}'
out_tr['x_ne20_so_hchild_pc'] = f'{r20c:.0f}'
out_tr['x_ne20_so_cmp'] = ('though by less' if r20 < r100 - 1 and r20c < r100c - 1 else
                           'by more' if r20 > r100 + 1 and r20c > r100c + 1 else 'by about as much')
out.update(out_tr)
d = json.load(open(OUT))
d.update(out)
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_noescape:', out)
