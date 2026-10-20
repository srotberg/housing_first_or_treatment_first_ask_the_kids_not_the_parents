"""fix_soul.py TEX -- after the splice: soul's \\hl (\\tocheck) and ulem's \\sout (\\del) cannot nest. Inside a struck
run, a \\tocheck{X} becomes X; inside a \\tocheck{...}, a moved number's \\del{old} is dropped, and a \\new{v} splits the
highlight around it, \\tocheck{A }\\new{\\tocheck{v}}\\tocheck{ B}, so it prints red on yellow (20 October, round r362: the
splice now marks a generated sentence word by word, and the yellow third lesson is one; soul cannot take a colour
change inside \\hl, and a whole run passed through it as one unit would not break across lines)."""
import sys
p = sys.argv[1]
s = open(p).read()


def close(t, j):
    d = 1
    while d:
        c = t[j]
        if c == '\\':
            j += 2
            continue
        d += (c == '{') - (c == '}')
        j += 1
    return j


def unwrap(t, cmd, drop=False):
    out, i = [], 0
    while True:
        k = t.find(cmd, i)
        if k < 0:
            out.append(t[i:])
            return ''.join(out)
        j = close(t, k + len(cmd))
        out.append(t[i:k])
        if not drop:
            out.append(t[k + len(cmd):j - 1])
        i = j


def within(t, cmd, f):
    out, i, n = [], 0, 0
    while True:
        k = t.find(cmd, i)
        if k < 0:
            out.append(t[i:])
            return ''.join(out), n
        j = close(t, k + len(cmd))
        out.append(t[i:k] + cmd + f(t[k + len(cmd):j - 1]) + '}')
        i, n = j, n + 1


A = s.index('\\begin{document}')
pre, body = s[:A], s[A:]
def inline_fn(t):
    """a footnote inside a struck run cannot be typeset by \\sout: it is printed inline, struck with the rest"""
    out, i = [], 0
    while True:
        k = t.find('\\footnote{', i)
        if k < 0:
            out.append(t[i:])
            return ''.join(out)
        j = close(t, k + 10)
        out.append(t[i:k] + ' [footnote: ' + t[k + 10:j - 1] + ']')
        i = j


body, n1 = within(body, '\\del{', lambda x: inline_fn(unwrap(x, '\\tocheck{')))
def unwrap_all(t, cmd):
    """unwrap until none is left: a moved number's \\new{v} can sit inside a \\new{...} sentence (round r333)"""
    while cmd in t:
        t = unwrap(t, cmd)
    return t
def split_red(t, hl='\\tocheck{'):
    """the body of a \\tocheck{...} (or an \\ai{...}): each top-level \\new{v} closes the highlight, prints v red and
    highlighted, and reopens it (a \\new or a \\tocheck nested in v is flattened, the highlight already covering it)"""
    out, i = [], 0
    while True:
        k = t.find('\\new{', i)
        if k < 0:
            out.append(t[i:])
            return ''.join(out)
        j = close(t, k + 5)
        v = unwrap_all(unwrap_all(t[k + 5:j - 1], '\\new{'), '\\tocheck{')
        out.append(t[i:k] + '}\\new{' + hl + v + '}}' + hl)
        i = j


body, n2 = within(body, '\\tocheck{', lambda x: split_red(unwrap(x, '\\del{', drop=True)))
body = body.replace('\\tocheck{}', '').replace('\\tocheck{ }', ' ')
# the blue AI-flagged sentences (20 October) are soul highlights too: the same treatment
# (soul cannot rebuild a control space, as in 'et al.\\ (2022)': inside the highlight it becomes a tie)
body, n3 = within(body, '\\ai{', lambda x: split_red(unwrap(x, '\\del{', drop=True), '\\ai{').replace('\\ ', '~'))
body = body.replace('\\ai{}', '').replace('\\ai{ }', ' ')
open(p, 'w').write(pre + body)
print(f'fix_soul: {n1} struck runs, {n2} highlighted runs and {n3} AI-flagged runs cleaned')
