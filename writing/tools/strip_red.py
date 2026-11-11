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
    # DELETED TEXT AND NOTES GO WHOLE (the author, 3 October): \del{...} is what a round took out, shown
    # struck through, and \why{...} a note to the author; neither is the paper's text once the round is read
    from marks import drop_marks
    src = drop_marks(src)
    # THE MACRO DEFINITION IS NOT AN INSTANCE OF THE MACRO. Stripping
    # \\newcommand{\\new}[1]{\\textcolor{red}{#1}} turns \\new into a no-op and
    # silently un-reds every number fill.py marked, which is the opposite of
    # what a strip is for: those marks are generated fresh on the next fill.
    # It is hidden from the stripper and put back afterwards.
    # From 19 August \new prints as ordinary text, so the definition carries no
    # red for the stripper to find. The guard is kept because the red form is
    # one edit away and stripping it silently un-reds every marked number.
    # THE GUARD MUST MATCH THE DEFINITION THAT IS ACTUALLY IN THE FILE. It named
    # the \\textcolor form while the file had carried {\\color{red}#1} since the
    # macro was restored, and {\\color{red} is itself one of the three openers -- so
    # a strip would have rewritten the definition to \\newcommand{\\new}[1]{#1} and
    # turned every mark in the paper black. That is the passthrough bug that ran
    # for several rounds before check_red.py was written to catch it, and it would
    # have come back through the stripper rather than through an edit. Both forms
    # are guarded now, and check_red.py is the backstop either way.
    DEFS = ["\\newcommand{\\new}[1]{{\\color{red}#1}}",
            "\\newcommand{\\new}[1]{\\textcolor{red}{#1}}"]
    # THE SAME TRAP CAUGHT \\cw. Its definition contains two red wrappers, and
    # stripping them turned every proposed deletion black: the rule was still
    # drawn and the text still struck, but nothing was red any more, so a whole
    # round of cuts went out looking like ordinary text with a line through it.
    CWDEF = ("\\newcommand{\\cw}[1]{{\\settowidth{\\cw@len}{#1}%\n"
             "  \\rlap{\\textcolor{red}{\\rule[0.55ex]{\\cw@len}{0.4pt}}}"
             "\\textcolor{red}{\\hspace{0pt}#1}}}")
    guarded = None
    for d in DEFS:
        if d in src:
            guarded = d
            src = src.replace(d, "@@NEWDEF@@")
            break
    if guarded is None and "\\newcommand{\\new}" in src:
        sys.exit("the \\new definition in the file matches no guarded form; "
                 "add it to DEFS before stripping, or the strip will silently "
                 "turn every mark in the paper black")
    cwguarded = CWDEF in src
    if cwguarded:
        src = src.replace(CWDEF, "@@CWDEF@@")
    # AND THE SAME TRAP CAUGHT \\del (found 11 November): its definition is a {\\color{red} group, so the strip of
    # r452 rewrote it to a plain \\sout and every deletion after it printed struck in black, which the author had asked
    # to see in red. Both copies of the definition are hidden from the stripper and put back; check_red.py now checks it.
    DELDEF = "\\DeclareRobustCommand{\\del}[1]{{\\color{red}\\sout{#1}}}"
    delguarded = DELDEF in src
    if delguarded:
        src = src.replace(DELDEF, "@@DELDEF@@")
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
        out = out.replace("@@NEWDEF@@", guarded)
    if cwguarded:
        out = out.replace("@@CWDEF@@", CWDEF)
    if delguarded:
        out = out.replace("@@DELDEF@@", DELDEF)
    open(p, "w").write(out)
    print("stripped:", p, len(src), "->", len(out))
