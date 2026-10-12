"""THE TWO MARKS THAT CARRY TEXT WHICH IS NOT THE PAPER'S (the author, 3 October: "deleted sentences should
show as crossed so I know what you delete" and "leave notes for me in case I need to understand why you made
a change").

    \\del{...}   text a round deleted, printed struck through in red so the author can see it went
    \\why{...}   a note to the author on why a change was made, printed in green and listed after the abstract

Both go, with their contents, when red is stripped, and neither is prose the checkers should read.
"""

DROP = ('\\del{', '\\why{')


def _close(s, j):
    """index just past the brace that closes the group whose body starts at j"""
    depth = 1
    while depth:
        c = s[j]
        if c == '\\':
            j += 2
            continue
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        j += 1
    return j


def drop_marks(s):
    """the text with every \\del{...} and \\why{...} removed, contents and all"""
    out, i = [], 0
    while True:
        hits = [(s.find(t, i), t) for t in DROP]
        hits = [(k, t) for k, t in hits if k >= 0]
        if not hits:
            out.append(s[i:])
            # a reference that was struck whole leaves its \\item behind with nothing in it
            import re
            return re.sub(r'(?m)^\\item[ \t]*\n', '', ''.join(out))
        k, t = min(hits)
        out.append(s[i:k])
        i = _close(s, k + len(t))
