"""export_ruleA.py -- the rule-A footnote's numbers, as x_ruleA_<name>, into ruleA_numbers.json.

The author, 12 October: "redo the whole paper with rule C ... and we can then put a footnote saying that using rule A
still gives similar qualitative results". Rule A, the paper's Treatment First until then, revokes the voucher of a
household that uses OR has the disorder, whether or not it is in treatment; rule C (the paper's from 12 October) lets a
household with the disorder keep it if it is in treatment and does not use.

The rule-A numbers are read from the rule-A main arm exactly as export_results.py reads the main arm, by running it with
TF_ARM pointing at the rule-A run, its output sent to a temporary file and its tables left alone, then keeping the main
arm's names under the x_ruleA_ prefix. So the footnote quotes the same computation the paper quoted before the switch,
and it does not move when export_results.py is pointed at the rule-C arms.
"""
import json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RULE_A_ARM = 'tf85_c35/tf'          # results/counterfactuals_2c/tf85_c35/tf: rule A, detection 0.85, the $35 test
KEEP = ['x_tf_cev', 'x_tf_b_pc', 'x_tf_sud_pc', 'x_tf_h_pc', 'x_tf_h_dir', 'x_tf_piv_pc', 'x_tf_price_pc',
        'x_tf_hchild_pc', 'x_tf_hchild_dir', 'x_tf_hchild_pp', 'x_tf_sudchild_pp', 'x_tf_sudchild_dir',
        'x_tf_childpart_cev', 'x_tf_adultpart_cev']

tmp = tempfile.NamedTemporaryFile(suffix='.json', delete=False).name
env = dict(os.environ, TF_ARM=RULE_A_ARM, EXPORT_OUT=tmp, EXPORT_TABLES='0')
subprocess.run([sys.executable, os.path.join(HERE, 'export_results.py')], env=env, check=True,
               stdout=subprocess.DEVNULL)
raw = json.load(open(tmp))
os.unlink(tmp)
out = {'x_ruleA_' + k[len('x_tf_'):]: raw[k] for k in KEEP if k in raw}
missing = [k for k in KEEP if k not in raw]
if missing:
    sys.exit(f'export_ruleA: export_results.py no longer writes {missing}')
json.dump(out, open(os.path.join(HERE, 'ruleA_numbers.json'), 'w'), indent=1, sort_keys=True)
print(f'wrote ruleA_numbers.json ({len(out)} names from {RULE_A_ARM})')
