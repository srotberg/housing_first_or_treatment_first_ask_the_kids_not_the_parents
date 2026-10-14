#!/bin/bash
# export_all_C.sh -- THE ROUND'S EXPORTERS IN ORDER, ON THE RULE-C RUNS (14 October). export_results.py rewrites
# results_numbers.json whole (and runs export_longrun.py), so the others follow it. A name whose rule-C run has not
# landed prints yellow (\tocheck{--}), never a rule-A number: the long run's pending columns (export_longrun.py), the
# decomposition's (export_results.py), and here the revocations until results/revoked_2c_C has both paths, the street
# split until results/revoked_2c_street_C/tables.md, and the Milby impact row until the rule-C transition's t=1.
set -e
cd "$(dirname "$0")"
python3 export_results.py > /tmp/export_results_C.log 2>&1 || { tail -20 /tmp/export_results_C.log; exit 1; }
grep -a "PENDING" /tmp/export_results_C.log || true
python3 export_revoked.py | tail -2
python3 export_pe_noext.py | tail -1
python3 export_whostops.py | tail -1
python3 export_welfare.py | tail -2
python3 export_decomp_use.py | tail -1
python3 export_nish_parts.py | tail -1
python3 - <<'PYEOF'
import json, os, sys
sys.path.insert(0, '.')
import export_revoked as R
p = 'results_numbers.json'
d = json.load(open(p))
pend = []
if R.PENDING_C:
    pend.append('x_rv_')
elif R.PENDING_STREET:
    pend.append('x_rv_street_')
# the Milby impact row: the rule-C transition's first year (RULE_C_PLAN, the Milby row) has not run
pend += ['x_milby_model_impact', 'x_milby_model_lr']
# the omega_c = 0.686 sensitivity is rule A's (no rule-C run): its numbers beside the rule-C benchmark would compare
# two rules, so they wait, yellow, for the author's call (re-run it on rule C, or say it is rule A's)
pend += ['x_nish_']
# names the paper uses that a pending run never wrote (the price-held welfare column, the transition's first year)
import re
src = open('../../writing/housing_first_children_later.src.tex').read()
others = set()
for f in ('params_numbers.json', 'fortran_numbers.json', 'calib_numbers.json', 'lit_numbers.json', 'decomp_use.json',
          'ruleA_numbers.json'):
    if os.path.exists(f):
        others |= set(json.load(open(f)))
for k in sorted(set(re.findall(r'@@([a-zA-Z0-9_]+)@@', src))):
    if k not in d and k not in others and (re.match(r'x_wd_\w+_p$', k) or k.startswith('x_milby_t1_')):
        d[k] = '\\mbox{\\tocheck{--}}'
        print('  yellow, not written by a pending run:', k)
n = 0
for k in list(d):
    if any(k.startswith(x) for x in pend):
        d[k] = '\\mbox{\\tocheck{--}}'; n += 1
json.dump(d, open(p, 'w'), indent=1, sort_keys=True)
print(f'export_all_C: {n} names yellow ({", ".join(pend)})')
PYEOF
