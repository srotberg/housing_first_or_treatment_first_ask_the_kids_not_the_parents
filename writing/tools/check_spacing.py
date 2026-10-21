"""
Find words that have run together in the rendered paper, and the macro uses that
cause it.

WHY THIS EXISTS. Table 5's caption read "The twenty nineparameters that carry the
story of this paper" for a round, in red, at the top of a table the author was
reading closely, and nobody saw it. The cause is one of TeX's oldest traps:
a control word swallows the whitespace that follows it, so

    \\newcommand{\\nmain}{twenty nine}   ...   The \\nmain parameters

sets "twenty nineparameters". Nothing errors, nothing overfulls, and the source
reads correctly. The fix is \\nmain\\ or \\nmain{}, and the point of this file is
that the trap is found by a script rather than by an eye.

TWO CHECKS, because either alone misses cases.

THE SOURCE CHECK is exact. It reads every \\newcommand of no arguments out of the
preamble, keeps those whose body ends in a letter or a digit -- only those eat a
space visibly -- and flags every use followed by whitespace and a letter. It sees
the bug before it is typeset and it names the line.

THE RENDERED CHECK is a net for everything else: a missing space that comes from
a mistyped source rather than a macro, or from a placeholder filled without one.
It reads the PDF and flags any token that is not a word but splits cleanly into
two words that are, using a vocabulary built from the paper itself. That
vocabulary is why it works without a dictionary: a word that appears correctly
somewhere in the paper is evidence about what the paper's words are, and a
glued-together token is by construction two of them.

Both are reported with enough context to act on, and the rendered check is
deliberately conservative: it wants BOTH halves to be words seen elsewhere and it
skips anything with a digit, so a citation key or a file name does not trip it.

Run:  python3 check_spacing.py
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # writing/: these tools live in writing/tools/
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_ask_the_kids.src.tex')
BUILT = os.path.join(HERE, 'housing_first_or_treatment_first_ask_the_kids.tex')
PDF = os.path.join(HERE, 'housing_first_or_treatment_first_ask_the_kids.pdf')

# Words that legitimately run two words together, or that the paper uses as one
# token. Kept short on purpose: a long allow list hides the bug it is meant to
# find, so anything added here should be a real word, not a real mistake.
ALLOW = {
    'nonstopmode', 'newcommand', 'renewcommand', 'setlength', 'footnotesize',
    'scriptsize', 'textcolor', 'marginpar', 'raggedright', 'multicolumn',
    'inhouse', 'lifecycle', 'wellbeing', 'healthcare', 'anymore', 'whatsoever',
    'nonetheless', 'therefore', 'moreover', 'furthermore', 'whereas', 'someone',
    # CHECKED AND REAL. Each of these decomposes into two of the paper's own
    # words and each is an ordinary English word; they were read once and put
    # here so the check does not report them again. A new entry belongs here
    # only after the same reading.
    'database', 'downsize', 'overstate', 'reachable', 'reasonable', 'tradeoff',
    'undertake', 'withdrawing', 'withdraws', 'withdrawn', 'withdrawal',
    'dataset', 'datasets',
    'somebody', 'everybody', 'everyone', 'anybody', 'anyone', 'nobody',
    'something', 'anything', 'everything', 'nothing', 'himself', 'herself',
    'itself', 'themselves', 'oneself', 'without', 'within', 'throughout',
    'into', 'onto', 'upon', 'become', 'becomes', 'became', 'because',
    'however', 'whenever', 'wherever', 'whatever', 'whoever', 'another',
    'outside', 'inside', 'alongside', 'income', 'incomes', 'outcome',
    'outcomes', 'workless', 'homeless', 'homelessness', 'household',
    'households', 'overall', 'overnight', 'underlying', 'meanwhile',
    'nevertheless', 'notwithstanding', 'thereafter', 'thereby', 'herein',
    'nowhere', 'somewhere', 'everywhere', 'cannot',
}


def macro_check():
    """Zero-argument macros used with a following space and a letter.

    THE TABLES ARE SCANNED TOO, and they are the reason this is not a one file
    check: the caption of Table 5 is where the bug actually happened, and the
    macros are defined in the source but used in tables/*.tex. A checker that
    read only the file the definitions live in would have passed it.
    """
    src = open(SRC).read()
    defs = {}
    for m in re.finditer(r'\\newcommand\{\\([A-Za-z]+)\}\{([^{}]*)\}', src):
        body = m.group(2)
        if body and (body[-1].isalnum() or body[-1] == '@'):
            defs[m.group(1)] = body
    files = [SRC] + sorted(
        os.path.join(HERE, 'tables', f)
        for f in os.listdir(os.path.join(HERE, 'tables'))
        if f.endswith('.tex'))
    hits = []
    for path in files:
        lines = open(path, errors='ignore').read().split('\n')
        for name in defs:
            for i, line in enumerate(lines):
                for m in re.finditer(r'\\' + name + r'(?![A-Za-z])', line):
                    after = line[m.end():]
                    # \name{} and \name\ are the two correct forms, and a
                    # following non-letter needs no space at all
                    if after[:1].isspace() and after.lstrip()[:1].isalpha():
                        hits.append((os.path.relpath(path, HERE), i + 1, name,
                                     line.strip()[:100]))
    return hits


def rendered_check():
    """Tokens in the PDF that are two of the paper's own words run together."""
    try:
        import pymupdf
    except ImportError:
        return None, 'pymupdf is not installed, so the rendered check was skipped'
    if not os.path.exists(PDF):
        return None, 'no PDF built yet, so the rendered check was skipped'
    doc = pymupdf.open(PDF)
    # DELIBERATELY NOT DE-HYPHENATED. Joining "forward-\nlooking" makes
    # "forwardlooking", which is then reported as two words run together when it
    # is a hyphenated compound that happened to break over a line. And a word
    # that is genuinely missing its space is ONE token by construction, so it
    # cannot span a line break except through TeX's own hyphenation, which
    # leaves a hyphen behind. Nothing is lost by leaving them alone.
    #
    # URLS AND ADDRESSES ARE NOT PROSE, and they are full of run-together words
    # by design, so lines carrying one are dropped first.
    lines = [ln for ln in ' '.join(doc[p].get_text()
             for p in range(len(doc))).split('\n')
             if not re.search(r'https?:|www\.|@|\.org|\.com|\.gov|\.edu', ln)]
    text = '\n'.join(lines)
    toks = re.findall(r"[A-Za-z][A-Za-z'’]*", text)
    vocab = {}
    for t in toks:
        vocab[t.lower()] = vocab.get(t.lower(), 0) + 1
    # a word is "known" if it stands alone somewhere often enough to be real
    known = {w for w, c in vocab.items() if c >= 2 and len(w) >= 3}
    known |= {'a', 'an', 'the', 'of', 'to', 'in', 'is', 'it', 'as', 'at', 'on',
              'or', 'by', 'be', 'so', 'no', 'up', 'we', 'if'}
    # A REAL WORD RECURS AND A SLIP DOES NOT. A missing space is made once, in
    # one place, so a candidate that appears three times or more is far likelier
    # to be a word this paper simply uses than a mistake made three times.
    hits = []
    for t in sorted({t for t in toks if len(t) >= 8}):
        low = t.lower()
        if low in ALLOW or low in known or vocab[low] > 2:
            continue
        for i in range(3, len(low) - 2):
            a, b = low[:i], low[i:]
            if a in known and b in known and len(a) >= 3 and len(b) >= 3:
                hits.append((t, a, b))
                break
    return hits, ''


def main():
    bad = False
    hits = macro_check()
    if hits:
        bad = True
        print('   MACROS THAT EAT THE FOLLOWING SPACE:')
        for path, line, name, ctx in hits:
            print(f'     {path}:{line}  \\{name} '
                  f'-> write \\{name}\\ or \\{name}{{}}')
            print(f'       {ctx}')
    rend, note = rendered_check()
    if note:
        print(f'   {note}')
    if rend:
        bad = True
        print('   WORDS RUN TOGETHER IN THE RENDERED PAPER:')
        for tok, a, b in rend:
            print(f'     {tok}  = {a} + {b}')
    if not bad:
        print('   no words run together, and no macro eats a following space')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
