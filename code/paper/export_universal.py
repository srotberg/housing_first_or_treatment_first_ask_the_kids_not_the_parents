#!/usr/bin/env python3
"""export_universal.py -- the universal-voucher check (footnote in Section 6.2) from results/universal_C_tax/.

THE EXPERIMENT (11 November; the author: "you can do the universal one and put in a footnote", "we just want the full GE
cases", "2 cases", and "Labour tax clears"). Housing First and Treatment First with every income-eligible household
holding a voucher (pi_V = 1), the drug price clearing, and the labour income tax keeping net revenue at Housing First's
no-policy value, 5.8371628 (code/universal/remote_universal_tax.sh).

WHAT IS READ, AND WHY THE LAST ROUND (12 November; the author: "we can stop the simulations and report what they have
since it is nearly converged"). Housing First converged (DIST CHECK PASS and TARGET CHECK PASS, 33 passes). Treatment
First cycled for hours at its stopping rules, the budget gap between 0.0005 and 0.004 against a rule of 0.001 and the
drug-market gap between 0.0013 and 0.006 against 0.005, because a tax step moves the drug market by about as much as the
rule allows; it was stopped after 39 passes. Its last round is used, and the spread over its last six rounds is
written to the summary: the newborn's gain moves by less than 0.1 of a percentage point across them.

THE CEV. Each arm's average_welfare_with_childhood is read against the benchmark's saved welfare curve with the
three-point Lagrange form calculate_welfare_gains uses. Treatment First's welfare lies just above the curve's top point
(x = 0.5), where calculate_welfare_gains stops rather than extrapolate; the same three-point form on the curve's last
three points extends it by about a fifth of one grid step, and a straight line through the last two points gives the
same gain to within 0.03 of a percentage point (both are written to the summary). The gain reported is the difference of
the two CEVs, as in Table 5.

    python3 code/paper/export_universal.py      writes results/universal_C_tax/summary.txt and
                                                  code/paper/universal_numbers.json
"""
import gzip, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'universal_C_tax')
CURVE = os.path.join(ROOT, 'results', 'reference', 'hf_2c_omega_0.085', 'files', 'welfare_curvebaseline_benchmark.dat.gz')
OUT = os.path.join(HERE, 'universal_numbers.json')

curve = [tuple(map(float, l.split())) for l in gzip.open(CURVE, 'rt') if l.strip()]


def lagrange(w, pts):
    (x0, w0), (x1, w1), (x2, w2) = pts
    return (x0 * (w - w1) * (w - w2) / ((w0 - w1) * (w0 - w2)) + x1 * (w - w0) * (w - w2) / ((w1 - w0) * (w1 - w2))
            + x2 * (w - w0) * (w - w1) / ((w2 - w0) * (w2 - w1)))


def cev(w):
    """calculate_welfare_gains' form: the first point at or above w, with its neighbours; past the top, the last three"""
    j = next((i for i in range(1, len(curve)) if curve[i][1] >= w), len(curve) - 1)
    j = min(max(j, 1), len(curve) - 2)
    return lagrange(w, curve[j - 1:j + 2])


def cev_linear_top(w):
    (x1, w1), (x2, w2) = curve[-2:]
    return x1 + (w - w1) * (x2 - x1) / (w2 - w1)


def arm(a):
    L = gzip.open(os.path.join(RES, a, 'cf.log.gz'), 'rt', errors='replace').read()
    ws = [float(v) for v in re.findall(r'average_welfare_with_childhood=\s*(\S+)', L)]
    mom = re.findall(r'CF MOMENTS distance=\s*\S+\s+b=\s*(\S+)\s+lambda_d=\s*(\S+)\s+h_1=\s*(\S+)', L)
    last = lambda pat: float(re.findall(pat, L)[-1])
    return dict(w=ws[-1], w6=ws[-6:], use=float(mom[-1][0]), sud=float(mom[-1][1]), hl=float(mom[-1][2]),
                price=last(r'price_of_addictive_good=\s*(\S+)'), tax=last(r'increase_in_labour_income_tax=\s*(\S+)'),
                pv=last(r'probability_of_voucher=\s*(\S+)'), passes=len(re.findall(r'expected_child_value=', L)),
                converged=bool(re.search(r'DIST CHECK PASS', open(os.path.join(RES, a, 'run.out')).read())))


n, t = arm('null'), arm('tf')
assert abs(cev(n['w']) - 0.46360376017561150) < 1e-9, 'the CEV form does not reproduce Housing First\'s own CEV line'
gain = 100 * (cev(t['w']) - cev(n['w']))
gain6 = [100 * (cev(w) - cev(n['w'])) for w in t['w6']]
gain_lin = 100 * (cev_linear_top(t['w']) - cev(n['w']))
pc = lambda k: 100 * (1 - t[k] / n[k])

lines = ['Universal vouchers in full equilibrium: pi_V = 1 in both arms, the drug price and the labour income tax clearing,',
         'net revenue at Housing First\'s no-policy 5.8371628 (code/universal/remote_universal_tax.sh; see export_universal.py).',
         f'  Housing First: {n["passes"]} passes, converged {n["converged"]}.  Treatment First: {t["passes"]} passes, '
         f'converged {t["converged"]} (stopped while cycling at its stopping rules; its last round is used).']
for k, lab in (('use', 'drug use'), ('sud', 'SUD prevalence'), ('hl', 'homelessness'), ('price', 'drug price'),
               ('tax', 'labour tax shift'), ('pv', 'pi_V')):
    lines.append(f'  {lab:17s} Housing First {n[k]:.6f}  Treatment First {t[k]:.6f}')
lines += [f'  CEV against the benchmark curve: Housing First {100*cev(n["w"]):.3f}, Treatment First {100*cev(t["w"]):.3f} '
          f'(Treatment First above the curve top, x = 0.5: extended by the three-point form)',
          f'  Newborn gain, Treatment First against Housing First: {gain:+.3f} percent of lifetime consumption',
          f'    last six rounds: {min(gain6):+.3f} to {max(gain6):+.3f}; a straight line through the curve top: {gain_lin:+.3f}',
          f'  Drug use {-pc("use"):+.1f} percent, SUD prevalence {-pc("sud"):+.1f} percent under Treatment First']
open(os.path.join(RES, 'summary.txt'), 'w').write('\n'.join(lines) + '\n')

# the direction words come from the numbers (CLAUDE.md: a sentence asserting a direction takes it from the numbers)
nums = {'x_univ_cev': f'{abs(gain):.1f}', 'x_univ_dir': 'raises' if gain > 0 else 'lowers',
        'x_univ_use_pc': f'{abs(pc("use")):.0f}', 'x_univ_use_dir': 'cuts' if pc('use') > 0 else 'raises',
        'x_univ_sud_pc': f'{abs(pc("sud")):.0f}', 'x_univ_sud_dir': 'cuts' if pc('sud') > 0 else 'raises'}
assert nums['x_univ_use_dir'] == nums['x_univ_sud_dir'], 'the footnote gives drug use and SUD one verb: rewrite it if they part'
# UNIVERSAL VOUCHERS LOWER DRUG USE UNDER HOUSING FIRST TOO (12 November, the author: "you can explain that the increase in
# the value of life reduces drug use under HF as well"): Housing First's universal drug use against its rationed value,
# x_b0 in results_numbers.json, the number Table 5 prints, read from there so the two cannot disagree.
b0 = float(json.load(open(os.path.join(HERE, 'results_numbers.json')))['x_b0'])
nums.update(x_univ_b_hf=f'{100 * n["use"]:.2f}', x_univ_hf_dir='lower' if 100 * n['use'] < b0 else 'raise')
# UNIVERSAL HOUSING FIRST AGAINST RATIONED HOUSING FIRST (12 November, the author: "You should say that universal HF is
# better than rationed HF. You can even state the gain."): Housing First's own CEV against the benchmark curve, i.e. against
# Housing First with rationed vouchers, the benchmark. It is inside the curve (x = 0.46 of a curve that ends at 0.5).
hf_gain = 100 * cev(n['w'])
nums.update(x_univ_hf_cev=f'{abs(hf_gain):.0f}', x_univ_hf_cev_dir='raise' if hf_gain > 0 else 'lower')
json.dump(nums, open(OUT, 'w'), indent=1, sort_keys=True)
print('\n'.join(lines)); print(nums)
