"""splice.py -- fill every @@name@@ of the source into the typeset file, marking in red what moved.

    python3 code/paper/splice.py BASE_DIR

writing/housing_first_children_later.src.tex -> writing/housing_first_children_later.tex, the whole file (the preamble
has @@n_main@@ and @@n_std@@ too). A name prints at the text precision (fill.text_precision). It is red, \\new{...},
when what it prints differs from what it printed in BASE_DIR, a copy of the round's number files as the author last
read them (the same basenames as FILES below), or when it is new since then. A transition name (x_tr_*, x_trf_*,
x_disc_tr*) that did not move is wrapped in \\updnum{}, which prints black unless \\showupdatestrue.

This replaces the round splices that lived in the session's scratchpad and were lost with it (16 October). It is the
simple form: a generated sentence that moved is red as a whole rather than word by word. Struck text is not produced
(the author, 14 October: "remove all crossed lines"), and run writing/tools/fix_soul.py on the output before LaTeX.
"""
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'code', 'stylized'))
import fill            # noqa: E402
import derived_names   # noqa: E402

FILES = ('code/paper/results_numbers.json', 'code/paper/params_numbers.json', 'code/paper/fortran_numbers.json',
         'code/paper/calib_numbers.json', 'code/stylized/gradient_numbers.json',
         'code/stylized/oldmodel_nosave_numbers.json', 'code/stylized/stage_numbers.json',
         'code/paper/nsfg_births.json', 'code/paper/smi_use_ratio.json', 'code/paper/nsduh_kids_home.json',
         'code/paper/nsduh_loneparent.json', 'code/paper/lit_numbers.json', 'code/paper/nsduh_kids_sud.json',
         'code/paper/decomp_use.json')
UPD = re.compile(r'^(x_trf?_|x_disc_tr)')


def load(paths):
    names = {}
    for f in paths:
        if os.path.exists(f):
            for k, v in json.load(open(f)).items():
                if not k.startswith('_'):
                    names.setdefault(k, v)
    names['del_d_pcw'] = fill._word(int(round(100 * fill.DEL_D)))
    names.update(fill._param_counts())
    names.update(derived_names.derived(names))
    return names


def main(base_dir):
    names = load([os.path.join(ROOT, f) for f in FILES])
    base = load([os.path.join(base_dir, os.path.basename(f)) for f in FILES])
    src = open(os.path.join(ROOT, 'writing', 'housing_first_children_later.src.tex')).read()
    used = set(re.findall(r'@@([a-zA-Z0-9_]+)@@', src))
    missing = sorted(k for k in used if k not in names)
    if missing:
        sys.exit(f'NO VALUE FOR: {missing}')
    red = []

    def moved(k):
        return k not in base or fill.text_precision(k, base[k]) != fill.text_precision(k, names[k])

    for k in sorted(used, key=len, reverse=True):
        v = str(fill.text_precision(k, names[k]))
        if not v.strip():
            src = src.replace(f'$@@{k}@@$', '').replace(f'@@{k}@@', '')
            continue
        if moved(k):
            red.append(k)
            src = src.replace(f'$@@{k}@@$', f'\\new{{${v}$}}').replace(f'@@{k}@@', f'\\new{{{v}}}')
        elif UPD.match(k):
            src = src.replace(f'$@@{k}@@$', f'\\updnum{{${v}$}}').replace(f'@@{k}@@', f'\\updnum{{{v}}}')
        else:
            src = src.replace(f'@@{k}@@', v)
    src = src.replace('\\new{}', '')
    open(os.path.join(ROOT, 'writing', 'housing_first_children_later.tex'), 'w').write(src)
    print(f'splice: {len(used)} names, {len(red)} red: {", ".join(sorted(red))}')


if __name__ == '__main__':
    main(sys.argv[1])
