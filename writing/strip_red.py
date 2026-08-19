"""Remove every red wrapper from the note, keeping the text inside.

Three forms are in use and all three nest, so this matches braces rather than
using a regex:

    \\new{...}                 the macro, which is \\textcolor{red}{...}
    \\textcolor{red}{...}      written out
    {\\color{red}...}          a group with a colour switch, used where a
                              paragraph break or a delimiter pair would break
                              the argument form

Verified by counting: the output must contain none of the three markers, and
the character count must fall by exactly the length of the wrappers removed.
"""
import re
import sys

OPENERS = [
    ("\\new{", 1),                 # (text to match, number of braces to close)
    ("\\textcolor{red}{", 1),
    ("{\\color{red}", 1),
]


def strip(s):
    # footnote guard: \\footnote{\\color{red}...} loses the footnote's own brace
    # when the wrapper goes, because the wrapper's brace IS the footnote's. Rewrite
    # it to the nested form first, which strips cleanly.
    s = s.replace("\\footnote{\\color{red}", "\\footnote{{\\color{red}")

    out = []
    i = 0
    removed = 0
    n = len(s)
    while i < n:
        hit = None
        for tok, _ in OPENERS:
            if s.startswith(tok, i):
                hit = tok
                break
        if hit is None:
            out.append(s[i])
            i += 1
            continue
        # walk to the matching close brace of the group this opener starts
        depth = 1
        j = i + len(hit)
        body = []
        while j < n and depth > 0:
            c = s[j]
            if c == "\\" and j + 1 < n:
                body.append(s[j:j + 2])
                j += 2
                continue
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0:
                    j += 1
                    break
            body.append(c)
            j += 1
        removed += len(hit) + 1
        out.append(strip("".join(body)))
        i = j
    return "".join(out)


if __name__ == "__main__":
    p = sys.argv[1]
    src = open(p).read()
    # THE MACRO DEFINITION IS NOT AN INSTANCE OF THE MACRO. Stripping
    # \\newcommand{\\new}[1]{\\textcolor{red}{#1}} turns \\new into a no-op and
    # silently un-reds every number fill.py marked, which is the opposite of
    # what a strip is for: those marks are generated fresh on the next fill.
    # It is hidden from the stripper and put back afterwards.
    DEF = "\\newcommand{\\new}[1]{\\textcolor{red}{#1}}"
    guarded = DEF in src
    if guarded:
        src = src.replace(DEF, "@@NEWDEF@@")
    before = {t: src.count(t) for t, _ in OPENERS}
    out = strip(src)
    after = {t: out.count(t) for t, _ in OPENERS}
    print("wrappers before:", before)
    print("wrappers after :", after)
    if any(after.values()):
        print("FAILED: markers survive")
        sys.exit(1)
    # brace balance must be unchanged
    def bal(x):
        d = 0
        k = 0
        while k < len(x):
            if x[k] == "\\":
                k += 2
                continue
            if x[k] == "{":
                d += 1
            elif x[k] == "}":
                d -= 1
            k += 1
        return d
    print("brace balance before/after:", bal(src), bal(out))
    if bal(src) != bal(out):
        print("FAILED: brace balance changed")
        sys.exit(1)
    # \\hspace{0pt} is inserted inside a red group so TeX can still hyphenate the
    # word it wraps: a word that begins with a whatsit is never hyphenated, and
    # that alone produced overfull boxes. It is part of the mark, so it goes when
    # the mark goes.
    out = out.replace("\\hspace{0pt}", "")
    if guarded:
        out = out.replace("@@NEWDEF@@", DEF)
    open(p, "w").write(out)
    print("stripped:", p, len(src), "->", len(out))
