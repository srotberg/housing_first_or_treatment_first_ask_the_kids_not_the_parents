"""The screen alone, with the drug price and pi_V both held at Housing First's (results/decomp_2c_both, arm fixboth):
how much drug use and the SUD fall, for the introduction's comparison with the military's deterrence (the author,
8 October: "with piv and pv constant, they dropped by 64%", "this should be in the introduction"). Reads the arm's
final.txt (changes against the no-policy run). usage: python3 code/paper/export_decomp_use.py -> code/paper/decomp_use.json"""
import sys, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# RULE C (14 October): the column re-solved beside Housing First; rule A's was results/decomp_2c_both/arm_fixboth
sys.path.insert(0, os.path.join(ROOT, 'code', 'paper'))
import rulec_paths as RC   # (16 October) the corrected screen-only column
F = os.path.join(RC.DC['fixboth'], 'final.txt')
def chg(label):
    for l in open(F):
        if l.strip().startswith(label):
            return float(re.search(r'change\s+([-+0-9.]+)%', l).group(1))
    raise SystemExit(f'GUARD: {label} not in {F}')
out = {'x_dc_b_b_pc': f"{abs(chg('drug use b')):.0f}", 'x_dc_b_sud_pc': f"{abs(chg('SUD lambda_d')):.0f}"}
json.dump(out, open(os.path.join(ROOT, 'code', 'paper', 'decomp_use.json'), 'w'), indent=1, sort_keys=True)
print(out)
