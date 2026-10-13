"""net_target_with_treatment.py -- Housing First's budget target once treatment is publicly funded (13 October).

The author: "I think it should be add to the benchmark too... And all the runs. You need to add it as a cost in the
budget". patch_treatC.py charges public_cost_of_treatment for every treated household with the disorder, in every arm.
The Treatment First arms clear pi_V to Housing First's net revenue (NET_TARGET); that revenue now carries Housing
First's own treatment spending, so the target falls by public_cost_of_treatment times Housing First's treated mass.

Treated mass of the accepted Housing First (no-policy) run: holders and housed households without a voucher from its
MILBY SPLIT line (results/counterfactuals_2c/milby_split/null), plus the homeless treated, which that line does not
carry, from the no-screen ABSTAIN line of the inert check (results/counterfactuals_2c/tf_ruleC2_test).
"""
import os, re
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OLD_TARGET = 5.8918410999831181            # the accepted no-policy run's net revenue, before treatment was charged
COST = 0.0423951                            # patch_treatC.py's public_cost_of_treatment

m = open(os.path.join(ROOT, 'results/counterfactuals_2c/milby_split/null/milby_split.txt')).read().split()
v_treat = float(m[m.index('smi') + 3])                       # voucher mass rec treat smi -> the third number
h_treat = float(m[m.index('housed_nov') + 7])                # housed_nov mass rec treat smi, then mass rec treat smi: +7 is treat
ab = [l for l in open(os.path.join(ROOT, 'results/counterfactuals_2c/tf_ruleC2_test/inert_C2/passes.txt'))
      if l.strip().startswith('ABSTAIN sud=')][-1]
hl_treat = float(re.search(r'homeless_treated=\s*(\S+)', ab).group(1))
treated = v_treat + h_treat + hl_treat
new = OLD_TARGET - COST * treated
print(f'treated mass {treated:.6f} (holders {v_treat:.6f}, housed without voucher {h_treat:.6f}, homeless {hl_treat:.6f})')
print(f'NET_TARGET {OLD_TARGET:.10f} - {COST} * {treated:.6f} = {new:.10f}')
