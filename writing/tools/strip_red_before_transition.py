"""
Strip this round's red from the sections that have been signed off, and leave
everything from Section 4 onward alone.

THE RULE. Red marks one round's edits, so it is cleared at the start of the
next round. That holds only up to the end of Section 3.6. From the transition
onward the red ACCUMULATES: the stylized model's results and the whole
quantitative half are being audited later, and the reader wants to see every
change made since the last time they read it, not only the most recent one.

Wiping that by running the general stripper over the whole file is a mistake
that cannot be undone from the file itself, so this script exists to make the
boundary mechanical rather than remembered. It refuses to run if it cannot
find the boundary.

Run:  python3 strip_red_before_transition.py [--dry-run]
"""

import io
import os
import re
import sys

P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   # writing/, one up from tools/
     'housing_first_or_treatment_first.src.tex')
# THE ANCHOR IS THE LABEL, not the section title, because the title is itself
# wrapped in red at the moment and a stripper that keyed on the title would
# stop finding it the first time it ran.
# THE BOUNDARY MOVED. It was the start of the transition, Section 3.7, while
# that section was still unread. The whole of Section 3 has now been audited,
# so red is cleared up to the quantitative model and accumulates from there.
ANCHOR = r'\section{The quantitative model}'
TOK = r'\textcolor{red}{'
# the two macro definitions carry red of their own and are not edits
KEEP = (r'\newcommand{\new}', r'\newcommand{\cw}', r'\def\cw')


def _strip(t):
    out, i = [], 0
    while True:
        j = t.find(TOK, i)
        if j < 0:
            out.append(t[i:])
            break
        line_start = t.rfind('\n', 0, j) + 1
        if any(t.startswith(k, line_start) for k in KEEP):
            out.append(t[i:j + len(TOK)])
            i = j + len(TOK)
            continue
        out.append(t[i:j])
        k, depth, body = j + len(TOK), 1, []
        while depth:
            ch = t[k]
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    k += 1
                    break
            body.append(ch)
            k += 1
        out.append(''.join(body))
        i = k
    return ''.join(out)


def main(dry=False):
    s = io.open(P, encoding='utf-8').read()
    if s.count(ANCHOR) != 1:
        sys.exit(f'refusing to run: found {s.count(ANCHOR)} copies of {ANCHOR}')
    cut = s.index(ANCHOR)
    head, tail = s[:cut], s[cut:]
    from marks import drop_marks          # struck deletions and notes go with the red
    head = drop_marks(head)
    before, kept = head.count(TOK), tail.count(TOK)
    new_head = _strip(head)
    print(f'   before Section 3.7: {before} red group(s) -> {new_head.count(TOK)}')
    print(f'   from Section 3.7 on: {kept} red group(s) left untouched')
    if dry:
        print('   dry run, nothing written')
        return
    io.open(P, 'w', encoding='utf-8').write(new_head + tail)
    print(f'   wrote {P}')


if __name__ == '__main__':
    main('--dry-run' in sys.argv)
