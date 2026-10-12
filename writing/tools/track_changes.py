"""Show what a round deleted, struck through, beside what replaced it (the author, 3 October: "deleted
sentences should show as crossed so I know what you delete").

    python3 writing/tools/track_changes.py OLD CUR OUT

OLD is the source as the author last saw it, CUR the source after the round's edits (insertions in \\new{},
notes in \\why{}, update tags in \\upd{}). OUT gets CUR with every deleted run as \\del{...} right before what
replaced it, and any inserted run not already marked wrapped in \\new{}. Display maths, tables, figures,
section titles and the preamble are left alone, and listed, since \\sout cannot be typeset there.
"""
import difflib, re, sys

old_src, cur_src, out_path = open(sys.argv[1]).read(), open(sys.argv[2]).read(), sys.argv[3]
GROUPS = {'\\new{': 'new', '\\why{': 'why', '\\upd{': 'upd'}


def close(s, j):
    d = 1
    while d:
        c = s[j]
        if c == '\\':
            j += 2
            continue
        d += (c == '{') - (c == '}')
        j += 1
    return j


CMD = re.compile(r'\\[a-zA-Z@]+\*?|\\[\s\S]')
WORD = re.compile(r'[^\s$\\{}\[\]%.,;:]+|[.,;:]')


def scan(s):
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
            continue
        hit = next((g for g in GROUPS if s.startswith(g, i)), None)
        if hit:
            j = close(s, i + len(hit))
            toks.append((GROUPS[hit], s[i:j], i, j)); i = j; continue
        if c == '%':
            j = s.find('\n', i); j = n if j < 0 else j
            toks.append(('plain', s[i:j], i, j)); i = j; continue
        if c == '$':
            j = i + 1
            while j < n and not (s[j] == '$' and s[j - 1] != '\\'):
                j += 1
            j += 1
            t = s[i:j]
            toks.append(('new' if '\\new{' in t else 'plain', t, i, j)); i = j; continue
        if c == '\\':
            m = CMD.match(s, i)
            j = m.end()
            toks.append(('plain', s[i:j], i, j)); i = j; continue
        if c in '{}[]':
            toks.append(('plain', c, i, i + 1)); i += 1; continue
        m = WORD.match(s, i)
        j = m.end()
        toks.append(('plain', s[i:j], i, j)); i = j
    return toks


def zones(s):
    """character ranges where nothing is struck or wrapped"""
    z = [(0, s.index('\\begin{document}'))]
    for env in ('equation', 'equation*', 'align', 'align*', 'aligned', 'table', 'figure', 'tabular', 'gather'):
        for m in re.finditer(r'\\begin\{' + re.escape(env) + r'\}.*?\\end\{' + re.escape(env) + r'\}', s, re.S):
            z.append((m.start(), m.end()))
    for m in re.finditer(r'\\(?:sub)*section\*?\{', s):
        z.append((m.start(), close(s, m.end())))
    for m in re.finditer(r'\\caption\{', s):
        z.append((m.start(), close(s, m.end())))
    return z


def atoms(s):
    """a cross-reference or a label is struck whole or not at all: a run may contain one, never cut one"""
    return [(m.start(), close(s, m.end())) for m in re.finditer(r'\\(?:label|input|ref|eqref|includegraphics)\{', s)]


def inz(z, a, b, at=()):
    return any(a < z1 and b > z0 for z0, z1 in z) or any(a < z1 and b > z0 and not (a <= z0 and b >= z1) for z0, z1 in at)


def balanced(t):
    d = 0
    for c in re.sub(r'\\[{}]', '', t):
        d += (c == '{') - (c == '}')
        if d < 0:
            return False
    return d == 0


def strike(t):
    t = t.replace('\\ref{', '\\ref*{').replace('\\eqref{', '\\ref*{')
    t = re.sub(r'\\url\{([^}]*)\}', lambda m: '\\texttt{' + m.group(1).replace('_', '\\_') + '}', t)
    parts = []
    for para in re.split(r'\n\s*\n', t):
        for k, item in enumerate(re.split(r'\\item\s', para)):
            item = item.strip()
            lead = '\\item ' if k > 0 else ''
            if item.endswith('\\'):          # a control space (et al.\ ) has nothing to strike
                item = item[:-1].rstrip()
            if item:
                parts.append(lead + '\\del{' + item + '}')
            elif lead:
                parts.append(lead)
    return '\n\n'.join([' '.join(parts)]) if parts else ''


def wrap(t):
    out = []
    for k, item in enumerate(re.split(r'\\item\s', t)):
        item = item.strip()
        lead = '\\item ' if k > 0 else ''
        out.append(lead + ('\\new{' + item + '}' if item else ''))
    return ' '.join(x for x in out if x)


def track(OLD, CUR, guard=True):
    A, B = scan(OLD), scan(CUR)
    ka = [t[1] for t in A]
    kb = [t[1] if t[0] in ('plain', 'upd') else '\x00%d' % k for k, t in enumerate(B)]
    za, zb = (zones(OLD), zones(CUR)) if guard else ([], [])
    aa, ab = atoms(OLD), atoms(CUR)
    sm = difflib.SequenceMatcher(None, ka, kb, autojunk=False)
    edits, skipped = [], []          # (position in cur, text to insert) and (position in cur, end, replacement)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op == 'equal':
            continue
        gone = ''
        if i2 > i1:
            a0, a1 = A[i1][2], A[i2 - 1][3]
            orun = OLD[a0:a1]
            if inz(za, a0, a1, aa):
                skipped.append(('deleted in a protected place', orun[:120]))
            elif not balanced(orun):
                skipped.append(('deleted run not brace-balanced', orun[:120]))
            else:
                gone = strike(orun)
        # inserted tokens that carry no mark of their own are wrapped
        plain = [k for k in range(j1, j2) if B[k][0] == 'plain']
        rep = None
        if plain:
            b0, b1 = B[plain[0]][2], B[plain[-1]][3]
            run = CUR[b0:b1]
            if inz(zb, b0, b1, ab):
                skipped.append(('inserted in a protected place', run[:120]))
            elif balanced(run) and all(B[k][0] == 'plain' for k in range(plain[0], plain[-1] + 1)):
                rep = (b0, b1, wrap(run))
            else:
                skipped.append(('inserted run mixed or unbalanced', run[:120]))
        pos = B[j1][2] if j1 < len(B) else len(CUR)
        if gone:
            edits.append((pos, gone + ' '))
        if rep:
            edits.append(rep)
    out = CUR
    # at one position the replacement goes first, then the deletion is put in front of it
    for e in sorted(edits, key=lambda e: (e[0], len(e)), reverse=True):
        if len(e) == 2:
            out = out[:e[0]] + e[1] + out[e[0]:]
        else:
            out = out[:e[0]] + e[2] + out[e[1]:]
    return out, edits, skipped


LIST = re.compile(r'(\\section\*\{References\}.*?\\begin\{list\}\{\}\{[^\n]*\n)(.*?)(\\end\{list\})', re.S)


def _items(block):
    return [x for x in re.split(r'(?m)^\\item\s', block) if x.strip()]


def _plain(x):
    while '\\new{' in x:
        k = x.index('\\new{'); e = close(x, k + 5)
        x = x[:k] + x[k + 5:e - 1] + x[e:]
    return x.strip()


def _key(x):
    return re.split(r'[(]', _plain(x))[0].strip()


def track_refs(old_block, cur_block):
    """entry by entry: a removed entry struck where it stood, a corrected one diffed within itself, a moved one
    left as it is (the list is alphabetical, so where an entry stands is not news)"""
    olds, curs = _items(old_block), _items(cur_block)
    used, out = set(), []
    okeys = {}
    for k, o in enumerate(olds):
        okeys.setdefault(_key(o), []).append(k)
    placed = []
    for c in curs:
        p = _plain(c)
        hit = next((k for k, o in enumerate(olds) if o.strip() == p and k not in used), None)
        if hit is None:
            cand = [k for k in okeys.get(_key(c), []) if k not in used]
            hit = cand[0] if cand else None
            if hit is not None:
                c = track(olds[hit].strip(), c.strip(), guard=False)[0]
        if hit is not None:
            used.add(hit)
        placed.append((hit, c.strip()))
    # removed entries go after the entry that preceded them in the old list
    pos = {h: n for n, (h, _) in enumerate(placed) if h is not None}
    extra = {}
    for k, o in enumerate(olds):
        if k in used:
            continue
        prev = max([q for q in range(k) if q in pos], default=None)
        extra.setdefault(pos[prev] if prev is not None else -1, []).append('\\item \\del{' + o.strip() + '}')
    for x in extra.get(-1, []):
        out.append(x)
    for n, (_, c) in enumerate(placed):
        out.append('\\item ' + c)
        out.extend(extra.get(n, []))
    return '\n'.join(out) + '\n'


mo, mc = LIST.search(old_src), LIST.search(cur_src)
ref_out = track_refs(mo.group(2), mc.group(2))
old_src = old_src[:mo.start(2)] + '@@REFLIST@@\n' + old_src[mo.end(2):]
cur_src = cur_src[:mc.start(2)] + '@@REFLIST@@\n' + cur_src[mc.end(2):]
out, edits, skipped = track(old_src, cur_src)
out = out.replace('@@REFLIST@@\n', ref_out)

# NO SPACE BEFORE PUNCTUATION THAT REPLACES A STRUCK RUN: '\\del{x} \\new{. Y}' printed 'x . Y'
def _tight(t):
    return re.sub(r'(\\del\{(?:[^{}]|\{[^{}]*\})*\}) (\\new\{[.,;:])', r'\1\2', t)
out = _tight(out)
open(out_path, 'w').write(out)
print(f'{sum(1 for e in edits if len(e) == 2)} deletions struck, {sum(1 for e in edits if len(e) == 3)} unmarked insertions wrapped')
for why, t in skipped:
    print('SKIPPED', why, '::', repr(t))
