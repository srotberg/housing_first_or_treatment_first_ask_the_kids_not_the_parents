"""THE RULE-C RUNS THE PAPER READS, IN ONE PLACE (14 October).

The exporters read these instead of the rule-A paths (code/RULE_C_PLAN.md, 'PAPER SWITCH'); the rule-A footnote's
numbers are frozen in ruleA_numbers.json (export_ruleA.py), so switching cannot move them. A run that has not landed yet
leaves its path missing, and the exporter that needs it prints \\tocheck{--} (yellow) instead of a number.

NULL_DIR is Housing First as the comparisons use it: re-solved beside the main arm on the rule-C build, so that use is
counted as rule C counts it (b 0.088953 against nulltf/null's 0.089584, the same welfare). If the 14 October diagnostic
(results/decomp_2c_shares_Cu: the internal_computations fix ungated) shows Housing First's values move, this is the one
line to change."""
import os
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
R = os.path.join(ROOT, 'results')
CF = os.path.join(R, 'counterfactuals_2c')
SC = os.path.join(R, 'decomp_2c_shares_C')
TF_ARM = 'tf_pdet20_C/tf'                                   # under CF: the main arm, detection 0.20
TF_DIR = os.path.join(CF, TF_ARM)
TF_HALF_DIR = os.path.join(CF, 'tf_pdet10_C', 'tf')         # the half rate, 0.10
# (19 October) the half rate re-solved against the corrected Housing First's net revenue (pdet/remote_pdet_Cu.sh 0.10,
# ACCEPTED 11:00): tf_pdet10_C cleared against the old target, 5.8275
if os.path.exists(os.path.join(CF, 'tf_pdet10_Cu', 'tf', 'cf.log.gz')):
    TF_HALF_DIR = os.path.join(CF, 'tf_pdet10_Cu', 'tf')
TF_NODES = os.path.join(SC, 'arm_tf', 'tf')                 # the main arm re-solved beside Housing First: by-node values
NULL_DIR = os.path.join(SC, 'arm_tf', 'null')               # Housing First: welfare files and by-node values
DC = {k: os.path.join(SC, f'arm_{k}') for k in ('fixboth', 'fixpv', 'fixp', 'tf')}   # each with tf/ and null/
PE = os.path.join(R, 'pe_noext_C')                          # no externalities: Arm A, and Arm B (both held)
FX = os.path.join(R, 'noext_fixp_C')                        # Arm D, pi_V clears
NC = os.path.join(R, 'noext_clear_C2')                      # Arm C, both clear (the nearer start; not noext_clear_C)
NE = os.path.join(R, 'noext_pclear_C')                      # Arm E, the price clears
# THE CORRECTED HOUSING FIRST (14 October, 05:20; code/RULE_C_PLAN.md '05:20 THE DIAGNOSTIC'). patch_treatC2's
# internal_computations fix was gated on the screen, so Housing First ran the old arithmetic and Treatment First the
# corrected one; ungated (results/decomp_2c_shares_Cu), the screen alone leaves no household with a SUD better off (24
# percent before). extra_2c/remote_decomp_shares_Cu2.sh tf re-solves Housing First on the ungated build and the main arm
# re-cleared against its net revenue (5.8372). Once all its files are in, the main column, Housing First and the welfare
# split read it; until then the old paths stand and the main column's better-off shares print yellow.
SCU = os.path.join(R, 'decomp_2c_shares_Cu')
CU_TF = os.path.join(SCU, 'arm_tf')
CORRECTED = all(os.path.exists(os.path.join(CU_TF, f)) for f in (
    'shares.txt', 'newborn_shares.json', 'tf/final.txt', 'tf/cf.log.gz', 'tf/value_at_26_by_node.txt',
    'null/final.txt', 'null/cf.log.gz', 'null/value_at_26_by_node.txt'))
if CORRECTED:
    TF_ARM = os.path.relpath(os.path.join(CU_TF, 'tf'), CF)
    TF_DIR = TF_NODES = os.path.join(CU_TF, 'tf')
    NULL_DIR = os.path.join(CU_TF, 'null')
    DC['tf'] = CU_TF
# the age split of the children's paragraph: finish_tf_Cu.sh's when it is in, else the gated run's (it supplies only
# the 26-50 homelessness change, to the whole percent)
AGE_SPLIT = os.path.join(CU_TF, 'age_split.txt')
if not os.path.exists(AGE_SPLIT):
    AGE_SPLIT = os.path.join(SC, 'arm_tf', 'age_split.txt')
# better-off shares against the corrected Housing First where a column has them; every other rule-C column's were
# computed against the gated one and print yellow (Table 5's better-off rows, and the sentences that quote them)
SHARES_FILE = {'fixboth': os.path.join(SCU, 'arm_fixboth', 'shares.txt')}
STALE_SHARES = {'dc_pv', 'dc_p', 'pe_b', 'fx_d', 'ne_e', 'nc_c'} | (set() if CORRECTED else {'tf85'})
# THE CORRECTED DECOMPOSITION AND NO-EXTERNALITY COLUMNS (landed 14 October, 15:59 to 20:57; round r324). Each column
# moves to its corrected run once that run's files are all in, and its better-off shares stop printing yellow. The
# column with the drug price held and pi_V clearing holds pi_V at 0.0924 (remote_decomp_shares_Cu2.sh, SHARES_HOLD_PV):
# the clearing value sits at a jump in drug use, and there net revenue is 0.2 per cent above Housing First's.
# (18 October) decomp_2c_shares_Cu3 first: the held columns re-solved with the price held at the CORRECTED Housing
# First's (0.99938969; Cu2 held it at the pre-correction 1.0001082), code/extra_2c/remote_decomp_shares_Cu3.sh
# (18 October, 14:00) NOT Cu3's fixp: held at pi_V 0.09354 it landed past the jump in drug use, net revenue 0.42 per
# cent below Housing First's, further from clearing than Cu's 0.22 above. Cu4 (remote_decomp_shares_Cu4.sh fixp,
# SHARES_HOLD_PV=1 SHARES_V0=0.0924) is the paper's pi_V with the corrected held price; Cu's column until it lands.
SCU3 = os.path.join(R, 'decomp_2c_shares_Cu3')
SCU4 = os.path.join(R, 'decomp_2c_shares_Cu4')
for _k, _arm in (('fixboth', 'dc_b'), ('fixpv', 'dc_pv'), ('fixp', 'dc_p')):
    for _d in ((SCU4 if _k == 'fixp' else SCU3), SCU):
        _d = os.path.join(_d, f'arm_{_k}')
        if all(os.path.exists(os.path.join(_d, f)) for f in ('final.txt', 'shares.txt', 'newborn_shares.json',
                                                             'tf/final.txt', 'tf/cf.log.gz', 'status.txt')):
            DC[_k] = _d
            SHARES_FILE.pop(_k, None)
            STALE_SHARES.discard(_arm)
            break
for _name, _arm, _new in (('PE', 'pe_b', 'pe_noext_Cu'), ('FX', 'fx_d', 'noext_fixp_Cu'), ('NC', 'nc_c', 'noext_clear_Cu'),
                          ('NE', 'ne_e', 'noext_pclear_Cu')):
    if os.path.exists(os.path.join(R, _new, 'analysis.json')):
        globals()[_name] = os.path.join(R, _new)
        STALE_SHARES.discard(_arm)
REVOKED = os.path.join(R, 'revoked_2c_C')
REVOKED_STREET = os.path.join(R, 'revoked_2c_street_C')


def have(*paths):
    """every path exists (a run that has not landed yet is missing)"""
    return all(os.path.exists(p) for p in paths)
