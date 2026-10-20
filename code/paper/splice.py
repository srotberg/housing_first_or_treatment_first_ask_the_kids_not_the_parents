"""splice.py -- fill every @@name@@ of the source into the typeset file, marking in red what moved.

    python3 code/paper/splice.py BASE_DIR

writing/housing_first_children_later.src.tex -> writing/housing_first_children_later.tex, the whole file (the preamble
has @@n_main@@ and @@n_std@@ too). A name prints at the text precision (fill.text_precision). It is red, \\new{...},
when what it prints differs from what it printed in BASE_DIR, a copy of the round's number files as the author last
read them (the same basenames as FILES below), or when it is new since then. A transition name (x_tr_*, x_trf_*,
x_disc_tr*) that did not move is wrapped in \\updnum{}, which prints black unless \\showupdatestrue.

This replaces the round splices that lived in the session's scratchpad and were lost with it (16 October). A generated
SENTENCE that moved is red word by word (20 October, round r362, the author: "remove all red and put only updates in
red" -- a whole paragraph went red when a clause of it changed): its words are diffed against what it printed in
BASE_DIR and only the inserted or changed runs are wrapped in \\new{}. A number, or a value of a few words, is red as a
whole. Struck text is not produced (the author, 14 October: "remove all crossed lines"), and run
writing/tools/fix_soul.py on the output before LaTeX.

    python3 code/paper/splice.py BASE_DIR [REGION_BASE_DIR MARKER]

A REGION (18 October, the author: "remove old red from the intro and abstract"): with a second base and a marker, the
source before the first occurrence of MARKER (e.g. '\\section{Related literature}') is compared with REGION_BASE_DIR
instead, so a part the author has re-read since BASE_DIR loses the red it carried while the rest keeps accumulating.
"""
import difflib
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
SENTENCE = 6        # words at brace depth 0 from which a value is diffed word by word
MERGE = 2           # black words between two red runs that join them


def words(t):
    """split at spaces outside braces and outside $...$, so a \\tocheck{...} or a formula stays one word"""
    out, cur, depth, math, i = [], [], 0, False, 0
    while i < len(t):
        c = t[i]
        if c == '\\' and i + 1 < len(t):
            cur.append(t[i:i + 2]); i += 2; continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif c == '$':
            math = not math
        if c == ' ' and depth == 0 and not math:
            if cur:
                out.append(''.join(cur)); cur = []
        else:
            cur.append(c)
        i += 1
    if cur:
        out.append(''.join(cur))
    return out


def word_red(old, new):
    """new, with the runs of words not in old wrapped in \\new{}; a deletion leaves nothing red"""
    a, b = words(old), words(new)
    seg = []                            # [words, red]
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if j2 > j1:
            seg.append([b[j1:j2], op != 'equal'])
    # a word or two left black between two red runs reads as a stray: it joins them
    for k in range(1, len(seg) - 1):
        if not seg[k][1] and len(seg[k][0]) <= MERGE and seg[k - 1][1] and seg[k + 1][1]:
            seg[k][1] = True
    out = []
    for w, red in seg:
        if red and out and out[-1][1]:
            out[-1][0] += w
        else:
            out.append([list(w), red])
    return ' '.join('\\new{' + ' '.join(w) + '}' if red else ' '.join(w) for w, red in out)


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


def main(base_dir, region_base_dir=None, marker=None):
    src = open(os.path.join(ROOT, 'writing', 'housing_first_children_later.src.tex')).read()
    if region_base_dir:
        i = src.index(marker)
        head, red_h = fill_part(src[:i], region_base_dir)
        tail, red_t = fill_part(src[i:], base_dir)
        out, red = head + tail, sorted(set(red_h) | set(red_t))
        print(f'splice: before {marker!r} against {region_base_dir}: {len(red_h)} red: {", ".join(sorted(red_h))}')
    else:
        out, red = fill_part(src, base_dir)
    open(os.path.join(ROOT, 'writing', 'housing_first_children_later.tex'), 'w').write(out)
    used = set(re.findall(r'@@([a-zA-Z0-9_]+)@@', src))
    print(f'splice: {len(used)} names, {len(red)} red: {", ".join(sorted(red))}')


def fill_part(src, base_dir):
    """fill one stretch of the source against one base; returns the text and the names marked red"""
    names = load([os.path.join(ROOT, f) for f in FILES])
    base = load([os.path.join(base_dir, os.path.basename(f)) for f in FILES])
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
            if k in base and f'$@@{k}@@$' not in src and len(words(v)) >= SENTENCE and \
                    len(words(str(fill.text_precision(k, base[k])))) >= SENTENCE:
                src = src.replace(f'@@{k}@@', word_red(str(fill.text_precision(k, base[k])), v))
                continue
            src = src.replace(f'$@@{k}@@$', f'\\new{{${v}$}}').replace(f'@@{k}@@', f'\\new{{{v}}}')
        elif UPD.match(k):
            src = src.replace(f'$@@{k}@@$', f'\\updnum{{${v}$}}').replace(f'@@{k}@@', f'\\updnum{{{v}}}')
        else:
            src = src.replace(f'@@{k}@@', v)
    src = src.replace('\\new{}', '')
    return src, red


if __name__ == '__main__':
    main(*sys.argv[1:4])
