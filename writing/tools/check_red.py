"""The \\new macro must render red whenever the paper still contains \\new calls.

WHY THIS EXISTS. strip_red.py rewrites the definition to a passthrough,

    \\newcommand{\\new}[1]{#1}

so that any \\new left behind after a strip is inert rather than an error. That
is right at the moment of stripping and wrong ever after: the passthrough was
committed once, and every \\new written in the rounds that followed went into
the paper as plain black text. Several rounds of marked edits were invisible to
the reader -- the introduction, the calibration entries, the new citations --
while table cells kept showing red, because those use \\textcolor directly. The
author reads this paper by looking at what is red, so an edit that is not red is
an edit they have no way of finding.

Nothing caught it because both states are valid LaTeX and the build was green.

THE RULE. If the file contains at least one \\new{ call, the definition must put
its argument in red. A file with no \\new calls at all may keep the passthrough,
which is the state strip_red.py leaves behind.

Run:  python3 check_red.py
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # writing/: these tools live in writing/tools/
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_ask_the_kids.src.tex')

DEFN = re.compile(r'^\s*\\newcommand\{\\new\}\[1\]\{(.*)\}\s*$', re.M)


def main():
    src = open(SRC, encoding='utf-8').read()
    # a \new CALL, not the definition and not a comment
    body = re.sub(r'(?<!\\)%.*$', '', src, flags=re.M)
    body = DEFN.sub('', body)
    calls = len(re.findall(r'\\new\{', body))

    m = DEFN.search(src)
    if not m:
        print('   no \\new definition found in the source')
        return 1
    defn = m.group(1)
    red = 'color{red}' in defn or 'textcolor{red}' in defn

    if calls and not red:
        print('the \\new macro is a passthrough while the paper still marks edits with it\n')
        print('   definition: \\newcommand{\\new}[1]{%s}' % defn)
        print('   %d \\new{...} call(s) in the paper, every one rendering as black text' % calls)
        print('\nRestore \\newcommand{\\new}[1]{{\\color{red}#1}}. strip_red.py writes the '
              'passthrough\nwhen it strips; it must not survive into a round that marks new edits.')
        return 1
    if red:
        print('   \\new renders red, and marks %d edit(s)' % calls)
    else:
        print('   \\new is a passthrough and the paper marks no edits with it')
    return 0


if __name__ == '__main__':
    sys.exit(main())
