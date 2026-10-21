"""Every source with more than two authors is cited as "et al."

THE RULE. One author is "Vaillant (1995)". Two are "Desmond and Gershenson
(2016)", both named. Three or more are "Mechanic et al. (2002)", first author
only. Nothing enforced this and it is the kind of thing that drifts in one
edit, because a three-author paper reads perfectly naturally written out.

WHAT IT LOOKS FOR. A citation that names three or more surnames before its
year, in either the prose or a table: "A, B and C (2002)", "A, B, C and D
(1997)", or the same with a serial comma. It cannot tell how many authors a
two-name citation really has -- that is a fact about the paper, not about the
string -- so "A and B (2010)" is passed and a two-author citation wrongly
shortened to "et al." is not caught. This catches the direction that shows.

Run:  python3 check_citations.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # writing/: these tools live in writing/tools/
SRC = os.path.join(HERE, 'housing_first_or_treatment_first.src.tex')
TABLES = os.path.join(HERE, 'tables')

# A surname: a capital, then letters, and the accent macros this bibliography
# uses -- {\AA}sb{\o}, J\"a\"askel\"ainen, \.{I}mrohoro\u{g}lu.
NAME = r"(?:\\[.'\"`^~ubvHtcdr]?\{?[A-Za-z]{0,2}\}?)*[A-Z][A-Za-z\\{}'.À-ɏ-]+"
CITE = re.compile(
    r'(' + NAME + r')((?:\s*,\s*' + NAME + r')+)\s*(?:,)?\s+and\s+(' + NAME + r')'
    r'\s*\((?:19|20)\d\d\)')


def files():
    yield SRC
    if os.path.isdir(TABLES):
        for fn in sorted(os.listdir(TABLES)):
            if fn.endswith('.tex'):
                yield os.path.join(TABLES, fn)


def main():
    bad = []
    for p in files():
        if not os.path.exists(p):
            continue
        for n, line in enumerate(open(p, encoding='utf-8'), 1):
            for m in CITE.finditer(line):
                n_names = 2 + len([x for x in m.group(2).split(',') if x.strip()])
                bad.append('  %s:%d  %s   (%d authors named)'
                           % (os.path.basename(p), n, m.group(0), n_names))
    if bad:
        print('citations naming more than two authors:\n')
        print('\n'.join(bad))
        print('\n%d citation(s). Cite the first author and "et al.".' % len(bad))
        return 1
    print('   every source with more than two authors is cited as et al.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
