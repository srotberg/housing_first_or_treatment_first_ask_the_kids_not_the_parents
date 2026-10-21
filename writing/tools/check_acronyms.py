"""
Catch an acronym whose first use does not define it.

THE RULE. Every acronym is spelled out in full on its first use with the
acronym in brackets, and only the acronym is used after that. Before writing
one, check whether it has appeared already: if it has, use the acronym alone; if
it has not, write the full name and put the acronym in brackets.

The expansion has to account for every letter of the acronym. "consumption
equivalent (CEV)" left the V unexplained; it is a consumption equivalent
VARIATION. And the acronym needs its own brackets rather than being folded into
a citation: "(National Survey on Drug Use and Health, NSDUH 2024)" defines
nothing.

WHAT IT CHECKS. Every all caps token used more than once in the prose, ignoring
LaTeX comments, maths and the bibliography. It reports one whose first
appearance is not immediately preceded by a bracketed definition.

FALSE POSITIVES ARE EXPECTED for acronyms that are proper names needing no
expansion, and for tokens that are not acronyms at all. Add those to ALLOW with
a reason rather than silencing the check.

Run:  python3 check_acronyms.py
"""

import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   # writing/, one up from tools/
       'housing_first_or_treatment_first_ask_the_kids.src.tex')

# Not acronyms, or proper names that stand alone.
ALLOW = {
    'I', 'A', 'II', 'III', 'IV', 'US', 'UK',      # numerals and countries
    'DC',                                          # Washington, DC, a publisher's place in the references
    'JAMA', 'NBER',                                # journal and series names in citations
    'DI',                                          # appears only as a maths subscript
    'WONDER',                                      # defined jointly as "(CDC WONDER)"
    'DATA',                                        # part of the filename DATA_APPENDIX.md
    'UPDATE',                                      # the blue pending-update marker (\\upd), not prose
}


def prose(text):
    from marks import drop_marks          # struck deletions and notes are not prose
    text = drop_marks(text)
    """The paper's prose: no comments, no maths, no bibliography."""
    end = text.find(r'\begin{thebibliography}')
    if end > 0:
        text = text[:end]
    text = '\n'.join(l for l in text.split('\n') if not l.lstrip().startswith('%'))
    text = re.sub(r'\\[a-zA-Z@]+\*?(\[[^\]]*\])?', ' ', text)
    return re.sub(r'\$[^$]*\$', ' ', text)


def main():
    body = prose(open(SRC).read())
    counts = {}
    for a in re.findall(r'\b([A-Z]{2,8}(?:-[A-Z])?)\b', body):
        counts[a] = counts.get(a, 0) + 1
    bad = []
    for a, n in sorted(counts.items(), key=lambda x: -x[1]):
        if a in ALLOW or n < 2:
            continue
        i = body.find(a)
        window = ' '.join(body[max(0, i - 200):i + len(a) + 3].split())
        if not re.search(r'\(\s*' + re.escape(a) + r'\s*[),]', window):
            bad.append((a, n, window[-96:]))
    if not bad:
        print('   every acronym is defined on first use')
        return 0
    print(f'   {len(bad)} acronym(s) whose first use does not define them:')
    for a, n, w in bad:
        print(f'   {a:8s} x{n:<4d} ...{w}')
    print('\n   spell it out with the acronym in brackets, or add it to ALLOW '
          'with a reason')
    return 0


if __name__ == '__main__':
    sys.exit(main())
