"""
Catch compound modifiers that are missing a hyphen, and hyphens that should not
be there.

THE RULE. A hyphen joins words that act TOGETHER as a single modifier in front
of a noun: a long-run equilibrium, a consumption-equivalent variation, a
point-in-time count, the pre-reform rest point. The same words take no hyphen
when they are a noun phrase in their own right: in the long run, the steady
state, measured at a point in time.

So the test is positional, not lexical. "long run" is right in "in the long
run" and wrong in "the long run equilibrium", and no word list can decide which
without looking at what follows.

WHAT IT CHECKS. Two directions.

  MISSING: a known compound appearing immediately before a noun, unhyphenated.
  SPURIOUS: the same compound hyphenated where nothing follows it, so it is
  being used as a noun.

FALSE POSITIVES ARE EXPECTED. Established open compounds stay open even
attributively in economics writing: "moral hazard force", "general equilibrium
model". Those are in OPEN. And a compound followed by a verb is not a modifier:
"the value of life being risked" is a noun phrase, which is why the word after
has to be checked against VERBS.

Run:  python3 check_hyphens.py
"""

import os
import re
import sys

SRC = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),   # writing/, one up from tools/
       'housing_first_or_treatment_first.src.tex')

# Compounds that take a hyphen when they modify a following noun.
COMPOUNDS = [
    'long run', 'short run', 'point in time', 'consumption equivalent',
    'rent to income', 'case control', 'means tested', 'forward looking',
    'pre reform', 'post reform', 'two period', 'three period', 'life cycle',
    'first order', 'second order', 'reduced form', 'closed form',
    'low income', 'high poverty', 'out of pocket', 'income eligible',
    'value of life', 'take up', 'means test',
]

# Established open compounds: no hyphen even in front of a noun.
OPEN = {'moral hazard', 'general equilibrium', 'partial equilibrium',
        'substance use', 'housing assistance', 'social security'}

# A following verb means the phrase is a noun, not a modifier.
VERBS = {'draws', 'is', 'are', 'was', 'were', 'has', 'have', 'had', 'can', 'could',
         'will', 'would', 'may', 'might', 'must', 'does', 'do', 'did',
         'being', 'been', 'becomes', 'remains', 'stays', 'falls', 'rises',
         'matters', 'holds', 'follows', 'means', 'implies', 'and', 'or',
         'of', 'to', 'the', 'a', 'in', 'it', 'that', 'which', 'than', 'but',
         'so', 'for', 'with', 'at', 'by', 'if', 'when', 'where', 'as',
         # a preposition after the phrase makes it a noun too: "the long run under
         # Treatment First", "in transition and the long run through children's"
         'under', 'through', 'beside', 'against', 'from', 'on', 'into', 'over',
         'after', 'before', 'until', 'between'}


def prose(text):
    from marks import drop_marks          # struck deletions and notes are not prose
    text = drop_marks(text)
    # STRIP THE RED WRAPPERS FIRST. A phrase marked as an edit reads as
    # "\textcolor{red}{value-of-life} force" once the macro name is blanked,
    # which leaves a brace between the compound and the noun it modifies and
    # makes a correctly hyphenated phrase look like a noun.
    for op in ('\\textcolor{red}{', '\\new{'):
        while True:
            j = text.find(op)
            if j < 0:
                break
            k = j + len(op)
            d = 1
            while d and k < len(text):
                if text[k] == '{':
                    d += 1
                elif text[k] == '}':
                    d -= 1
                k += 1
            text = text[:j] + text[j + len(op):k - 1] + text[k:]
    end = text.find(r'\begin{thebibliography}')
    if end > 0:
        text = text[:end]
    text = '\n'.join(l for l in text.split('\n') if not l.lstrip().startswith('%'))
    text = re.sub(r'\\[a-zA-Z@]+\*?(\[[^\]]*\])?', ' ', text)
    return re.sub(r'\$[^$]*\$', ' ', text)


def main():
    body = prose(open(SRC).read())
    missing, spurious = [], []
    for p in COMPOUNDS:
        if p in OPEN:
            continue
        gap = p.replace(' ', r'\s+')
        for m in re.finditer(r'\b' + gap + r'\s+([a-z]+)', body):
            nxt = m.group(1)
            if nxt in VERBS:
                continue
            missing.append((p, nxt, ' '.join(
                body[max(0, m.start() - 58):m.end() + 12].split())))
        # ALWAYS HYPHENATED, including predicatively and as nouns. These are
        # established forms rather than positional compounds: "eligibility is
        # means-tested", "treatment take-up". NOT forward-looking: the author, 5 October,
        # wants "households are forward looking" open and only the attributive form hyphenated.
        # "the income-eligible" is a compound adjective used substantively and
        # keeps its hyphen, so it is not a spurious one.
        if p in ('means tested', 'take up', 'point in time',
                 'income eligible'):
            continue
        hy = p.replace(' ', '-')
        for m in re.finditer(r'\b' + re.escape(hy) + r'\b(?!\s*[a-z(])', body):
            spurious.append((hy, ' '.join(
                body[max(0, m.start() - 58):m.end() + 22].split())))
    if missing:
        print(f'   {len(missing)} compound modifier(s) missing a hyphen:')
        for p, n, c in missing:
            print(f'      "{p} {n}"   ...{c[-84:]}')
    if spurious:
        print(f'\n   {len(spurious)} hyphen(s) where the phrase is a noun:')
        for h, c in spurious:
            print(f'      "{h}"   ...{c[-84:]}')
    if not missing and not spurious:
        print('   hyphenation of compound modifiers is consistent')
    return 0


if __name__ == '__main__':
    sys.exit(main())
