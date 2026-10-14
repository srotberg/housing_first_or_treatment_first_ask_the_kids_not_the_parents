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
TF_NODES = os.path.join(SC, 'arm_tf', 'tf')                 # the main arm re-solved beside Housing First: by-node values
NULL_DIR = os.path.join(SC, 'arm_tf', 'null')               # Housing First: welfare files and by-node values
DC = {k: os.path.join(SC, f'arm_{k}') for k in ('fixboth', 'fixpv', 'fixp', 'tf')}   # each with tf/ and null/
PE = os.path.join(R, 'pe_noext_C')                          # no externalities: Arm A, and Arm B (both held)
FX = os.path.join(R, 'noext_fixp_C')                        # Arm D, pi_V clears
NC = os.path.join(R, 'noext_clear_C2')                      # Arm C, both clear (the nearer start; not noext_clear_C)
NE = os.path.join(R, 'noext_pclear_C')                      # Arm E, the price clears
REVOKED = os.path.join(R, 'revoked_2c_C')
REVOKED_STREET = os.path.join(R, 'revoked_2c_street_C')


def have(*paths):
    """every path exists (a run that has not landed yet is missing)"""
    return all(os.path.exists(p) for p in paths)
