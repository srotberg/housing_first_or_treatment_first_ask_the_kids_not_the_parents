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
# RULE C (13 October): the detection rate is calibrated to this response (the author: "pick pdet to match the 59%" -- the
# data's 61 -- "of all tested users"), so the paper reads the calibrated rate's run and, for the half-rate sensitivity,
# the run at half of it (code/deter_2c/run_whostops_C_points.sh 0.10 0.20). Rule A's run was whostops_2c/cfarm_tf_imp_ws850.
WS_DIR = os.path.join(ROOT, 'results', 'whostops_2c_C_pts_0p10_0p20')
LOG = os.path.join(WS_DIR, 'cfarm_tf_imp_ws_p200', 'cf.log.gz')
LOG_HALF = os.path.join(WS_DIR, 'cfarm_tf_imp_ws_p100', 'cf.log.gz')
# the quarter rate (6 November; the author: "even at half and a quarter of the detection rate"): its own run, against its
# own Housing First reference on the same build (code/deter_2c/run_whostops_C_points.sh 0.05)
LOG_QUARTER = os.path.join(ROOT, 'results', 'whostops_2c_C_pts_0p05', 'cfarm_tf_imp_ws_p050', 'cf.log.gz')
OUT_JSON = os.path.join(HERE, 'results_numbers.json')
KEYS = ('hf_file', 'h_used', 'h_stop', 'h_start', 'hn_used', 'hn_stop', 'hn_start',
        't_used', 't_stop', 't_start', 'tn_used', 'tn_stop', 'tn_start')


def read(log):
    with gzip.open(log, 'rt', errors='replace') as f:
        lines = [l for l in f if 'DIAG who stops' in l]
    assert lines, 'no DIAG who stops line'
    v = [float(x) for x in re.findall(r'=\s*([-+0-9.Ee]+)', lines[-1])]
    assert len(v) == len(KEYS), (len(v), lines[-1][:200])
    d = dict(zip(KEYS, v))
    assert d['hf_file'] == 1, 'the screen run did not read the Housing First file'
    # nobody starts: the screen only removes a reason to use
    for g in ('h', 'hn', 't', 'tn'):
        assert d[g + '_start'] < 1e-12 * max(d[g + '_used'], 1), (g, d[g + '_start'])
    return d


def main():
    d = read(LOG)
    h = read(LOG_HALF)
    out = {
        'x_ws_tested_nosud_pc': f"{100 * d['tn_stop'] / d['tn_used']:.0f}",
        'x_ws_tested_all_pc': f"{100 * d['t_stop'] / d['t_used']:.0f}",
        'x_ws_holders_nosud_pc': f"{100 * d['hn_stop'] / d['hn_used']:.0f}",
        'x_ws_holders_all_pc': f"{100 * d['h_stop'] / d['h_used']:.0f}",
        # the share of the tested who used under Housing First that has a SUD; under rule C it can stop on impact by
        # entering treatment and stopping, which keeps its voucher
        'x_ws_tested_sud_share_pc': f"{100 * (1 - d['tn_used'] / d['t_used']):.0f}",
        'x_ws_tested_sud_pc': f"{100 * (d['t_stop'] - d['tn_stop']) / (d['t_used'] - d['tn_used']):.0f}",
        # the half-rate sensitivity's response (footnote fn:halfrate)
        'x_ws_half_tested_all_pc': f"{100 * h['t_stop'] / h['t_used']:.0f}",
    }
    # direction word: users with a SUD stop more (or less) often than users without one
    _s, _n = (d['t_stop'] - d['tn_stop']) / (d['t_used'] - d['tn_used']), d['tn_stop'] / d['tn_used']
    out['x_ws_sud_dir'] = 'more' if _s > _n else 'less'
    # (round r262, the author: "when we include those with SUD, the model produces about 1/3 of the responses seen
    # in the other paper"): the share of all tested users who stop against the military's relative fall, as the
    # nearest simple fraction, so the word turns with either number
    _lit = json.load(open(os.path.join(os.path.dirname(OUT_JSON), 'lit_numbers.json')))
    _r = (100 * d['t_stop'] / d['t_used']) / float(_lit['mp_stay_rel_pc'])
    _fr = min(((1/5, 'a fifth'), (1/4, 'a quarter'), (1/3, 'a third'), (2/5, 'two fifths'), (1/2, 'half'),
               (3/5, 'three fifths'), (2/3, 'two thirds'), (3/4, 'three quarters'), (1, 'all')),
              key=lambda q: abs(q[0] - _r))
    out['x_ws_all_vs_mil'] = _fr[1]
    # THE HALF RATE against the military: as a fraction of the 61 per cent, and inside or outside Mehay and Pacula's own
    # policy estimates (mp_lo_rel_pc to mp_hi_rel_pc), so the words turn with the numbers
    _rh = (100 * h['t_stop'] / h['t_used']) / float(_lit['mp_stay_rel_pc'])
    out['x_ws_half_vs_mil'] = min(((1/5, 'a fifth'), (1/4, 'a quarter'), (1/3, 'a third'), (2/5, 'two fifths'),
                                   (1/2, 'half'), (3/5, 'three fifths'), (2/3, 'two thirds'), (3/4, 'three quarters'),
                                   (1, 'all')), key=lambda q: abs(q[0] - _rh))[1]
    _hp = round(100 * h['t_stop'] / h['t_used'])
    out['x_ws_half_where'] = ('inside' if float(_lit['mp_lo_rel_pc']) <= _hp <= float(_lit['mp_hi_rel_pc'])
                              else 'outside')
    # the half rate itself, from the run's own handover line (probability_of_detection), as a percentage
    with gzip.open(LOG_HALF, 'rt', errors='replace') as f:
        _pdh = [l for l in f if 'probability_of_detection' in l and 'HANDOVER' in l]
    assert _pdh, 'no probability_of_detection handover line in the half-rate run'
    out['x_tf_pdet_half_pc'] = f"{100 * float(_pdh[-1].split()[-1]):.0f}"
    # THE QUARTER RATE: the share of the tested users who stop on impact, and inside or outside Mehay and Pacula's range
    q = read(LOG_QUARTER)
    _qp = round(100 * q['t_stop'] / q['t_used'])
    out['x_ws_quarter_tested_all_pc'] = f"{_qp:.0f}"
    out['x_ws_quarter_where'] = ('inside' if float(_lit['mp_lo_rel_pc']) <= _qp <= float(_lit['mp_hi_rel_pc'])
                                 else 'outside')
    r = json.load(open(OUT_JSON))
    r.update(out)
    json.dump(r, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, val in sorted(out.items()):
        print(f'  {k} = {val}')


if __name__ == '__main__':
    main()
