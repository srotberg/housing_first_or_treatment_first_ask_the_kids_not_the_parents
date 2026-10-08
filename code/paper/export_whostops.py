"""
Who stops using when Treatment First is introduced, household by household: the x_ws_* names of the Validation
section's comparison with the US military's random drug testing (the author, 8 October: "use the like for like with
the military experiment. Maybe add it to the validation?").

usage: python3 code/paper/export_whostops.py   -> x_ws_* merged into code/paper/results_numbers.json
       (export_results.py rewrites that file from scratch: run this after it, as export_revoked.py and
       export_pe_noext.py are)

Reads the 'DIAG who stops' line of results/whostops_2c/cfarm_tf_imp_ws850 (code/deter_2c/run_whostops.sh): the paper's
Treatment First applied to Housing First's benchmark distribution, the drug price and pi_V held at Housing First's, each
state compared with its own choice under Housing First (the reference run's per-state file). The line carries, for
holders and for the tested (holders, and eligible non-holders weighted by their offer rate), the mass that used under
Housing First, and of it the mass that stops, and the mass that did not use and starts, for all users and for users
without a SUD. The like-for-like measure is the tested without a SUD: Mehay and Pacula's 61 per cent is past-year use
among service members who stayed and were subject to the testing, and a household with a SUD cannot stop on impact in
the model, since a disorder ends only with recovery.
"""
import gzip
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
LOG = os.path.join(ROOT, 'results', 'whostops_2c', 'cfarm_tf_imp_ws850', 'cf.log.gz')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
KEYS = ('hf_file', 'h_used', 'h_stop', 'h_start', 'hn_used', 'hn_stop', 'hn_start',
        't_used', 't_stop', 't_start', 'tn_used', 'tn_stop', 'tn_start')


def main():
    with gzip.open(LOG, 'rt', errors='replace') as f:
        lines = [l for l in f if 'DIAG who stops' in l]
    assert lines, 'no DIAG who stops line'
    v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', lines[-1])]
    assert len(v) == len(KEYS), (len(v), lines[-1][:200])
    d = dict(zip(KEYS, v))
    assert d['hf_file'] == 1, 'the screen run did not read the Housing First file'
    # nobody starts: the screen only removes a reason to use
    for g in ('h', 'hn', 't', 'tn'):
        assert d[g + '_start'] < 1e-12 * max(d[g + '_used'], 1), (g, d[g + '_start'])
    out = {
        'x_ws_tested_nosud_pc': f"{100 * d['tn_stop'] / d['tn_used']:.0f}",
        'x_ws_tested_all_pc': f"{100 * d['t_stop'] / d['t_used']:.0f}",
        'x_ws_holders_nosud_pc': f"{100 * d['hn_stop'] / d['hn_used']:.0f}",
        'x_ws_holders_all_pc': f"{100 * d['h_stop'] / d['h_used']:.0f}",
        # the share of the tested who used under Housing First that has a SUD, and cannot stop on impact
        'x_ws_tested_sud_share_pc': f"{100 * (1 - d['tn_used'] / d['t_used']):.0f}",
    }
    r = json.load(open(OUT_JSON))
    r.update(out)
    json.dump(r, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, val in sorted(out.items()):
        print(f'  {k} = {val}')


if __name__ == '__main__':
    main()
