"""export_bcghw.py -- the comparison with Beauregard, Couture, Green, Hicks and Warburton (2026), "Pathways into
Homelessness" (the author, 14 October: "Add it to the validation section and I'll decide what to keep. Make sure to
explain what the numbers mean and their implications"). Reads results/bcghw_flows/flows.txt (the Housing First benchmark
with code/bcghw/patch_flows.py's print-only count of entries into homelessness and of how long new spells last; its last
pass) and writes the x_bc_* names into results_numbers.json. The data side is in lit_numbers.json (bcghw_*).
Run after export_results.py, which rewrites results_numbers.json whole."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
F = os.path.join(ROOT, 'results', 'bcghw_flows', 'flows.txt')
OUT = os.path.join(HERE, 'results_numbers.json')
T = open(F).read()
last = T[T.rindex('\npass '):]
def entry(group):
    m = re.search(r'entry, ' + re.escape(group) + r'\s*: no SUD\s+([0-9.]+)%\s+SUD\s+([0-9.]+)%\s+ratio\s+([0-9.]+)', last)
    return float(m.group(1)), float(m.group(2)), float(m.group(3))
a_n, a_s, a_r = entry('all working ages')
_, _, e_r = entry('employed')
_, _, u_r = entry('not employed')
_, _, y_r = entry('first ten adult years')
m = re.search(r'persistence: still homeless a year after entry: all\s+([0-9.]+)%, no SUD\s+([0-9.]+)%, SUD\s+([0-9.]+)%', last)
p_all, p_n, p_s = (float(x) for x in m.groups())
out = {
    'x_bc_entry_nosud_pc': f'{a_n:.2f}', 'x_bc_entry_sud_pc': f'{a_s:.2f}',
    'x_bc_ratio': f'{a_r:.2f}', 'x_bc_ratio_emp': f'{e_r:.2f}', 'x_bc_ratio_unemp': f'{u_r:.2f}',
    'x_bc_ratio_young': f'{y_r:.2f}',
    'x_bc_persist_pc': f'{p_all:.0f}', 'x_bc_persist_nosud_pc': f'{p_n:.0f}', 'x_bc_persist_sud_pc': f'{p_s:.0f}',
}
d = json.load(open(OUT)); d.update(out); json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_bcghw:', out)
