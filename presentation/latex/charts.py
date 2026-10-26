"""charts.py: write the four results charts of the Beamer deck as TikZ pictures.

    python3 presentation/latex/charts.py

Writes charts/{exp1,outcomes,decomp,alttrans}.tex, each a tikzpicture that slides.tex inputs. The numbers are
the paper's (Tables 5, 6 and 7), the same ones presentation/charts.py draws for the HTML deck; change both when
the paper's change. Colours as there: blue and orange are the paper's figures'; the decomposition adds pink and
aqua (checked with the dataviz validator), and every bar carries its value as a label.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'charts')


def fmt(v, d=0, pct=False):
    s = f'{abs(v):.{d}f}'
    return ('$-$' if v < 0 else '') + s + ('\\%' if pct else '')


def hbar(x0, x1, y, h, col):
    """A horizontal bar from x0 to x1 (cm), centred on y, its corners slightly rounded."""
    a, b = min(x0, x1), max(x0, x1)
    if b - a < 1e-6:
        return ''
    return (f'\\fill[{col}, rounded corners=0.6pt] ({a:.3f},{y - h / 2:.3f}) rectangle ({b:.3f},{y + h / 2:.3f});\n')


def node(x, y, text, anchor='west', style=''):
    return f'\\node[anchor={anchor}, inner sep=1pt{", " + style if style else ""}] at ({x:.3f},{y:.3f}) {{{text}}};\n'


def pic(body):
    return '\\begin{tikzpicture}[font=\\footnotesize, text=ink]\n' + ''.join(body) + '\\end{tikzpicture}\n'


# ----------------------------------------------------------------------------- Experiment 1
def exp1():
    rows = ['Both held', '$\\pi_V$ clears', 'Drug price clears', 'Both clear']
    use = [-28, -28, -17, -17]
    cev = [-1.17, -1.09, -0.89, -0.74]
    lab, pw, gap, rh, bh = 2.7, 4.9, 1.0, 0.62, 0.36
    body = []
    for k, (title, vmin, vals, col) in enumerate([
            ('Drug use, change against Housing First', -32, use, 'hfblue'),
            ('Newborn\'s welfare, \\% of lifetime consumption', -1.4, cev, 'tforange')]):
        x0 = lab + k * (pw + gap)
        zero = x0 + pw
        body.append(node(x0, 0.45, f'\\textbf{{{title}}}', 'west', 'text=navy'))
        body.append(f'\\draw[ink, line width=0.6pt] ({zero:.3f},0.1) -- ({zero:.3f},{-4 * rh - 0.05:.3f});\n')
        body.append(node(zero, -4 * rh - 0.1, '0', 'north', 'text=muted'))
        for i, v in enumerate(vals):
            y = -(i + 0.5) * rh
            xe = zero + v / -vmin * pw
            body.append(hbar(zero, xe, y, bh, col))
            body.append(node(xe - 0.08, y, '\\textbf{' + (fmt(v, 0, True) if k == 0 else fmt(v, 2, True)) + '}', 'east'))
    for i, r in enumerate(rows):
        body.append(node(0, -(i + 0.5) * rh, r, 'west'))
    return pic(body)


# ----------------------------------------------------------------------------- main outcomes
def outcomes():
    groups = [('Adults', [('Drug use', 8.92, 7.07, -21), ('Carrying a SUD', 3.83, 3.08, -19),
                          ('Homelessness', 0.62, 0.55, -11)]),
              ('Children', [('In a shelter', 1.03, 0.92, -11), ('Living with a parent who uses', 16.35, 13.24, -19),
                            ('Living with a parent with a SUD', 5.82, 4.75, -18)])]
    lab, pw, rh, bh, gh = 4.6, 5.6, 0.46, 0.28, 0.42
    zero = lab + pw
    body = [node(zero + 0.3, 0.3, 'Housing First $\\to$ Treatment First, \\% of households', 'west', 'text=muted')]
    y = 0.0
    for g, items in groups:
        body.append(node(0, y - gh / 2, f'\\textbf{{{g}}}', 'west', 'text=navy'))
        y -= gh
        for name, a, b, ch in items:
            yc = y - rh / 2
            xe = zero + ch / 25 * pw
            body.append(hbar(zero, xe, yc, bh, 'hfblue'))
            body.append(node(xe - 0.08, yc, f'\\textbf{{{fmt(ch, 0, True)}}}', 'east'))
            body.append(node(0.25, yc, name, 'west'))
            body.append(node(zero + 0.3, yc, f'{a:.2f} $\\to$ {b:.2f}', 'west'))
            y -= rh
        y -= 0.08
    body.append(f'\\draw[ink, line width=0.6pt] ({zero:.3f},0.05) -- ({zero:.3f},{y:.3f});\n')
    return pic(body)


# ----------------------------------------------------------------------------- decomposition
def decomp():
    parts = [('Childhood its parent does not count', 'tforange'),
             ('Productivity at entry its parent does not count', 'dpink'),
             ('Its own adult life under the policy', 'hfblue'),
             ('What its parent does count', 'daqua')]
    cols = [('Both held', [2.20, 1.06, -0.75, 0.31], 2.82, 116, -1.19),
            ('$\\pi_V$ clears', [3.47, 1.00, 1.54, 0.44], 6.45, 69, 2.42),
            ('Both clear', [1.50, 0.46, 0.43, 0.19], 2.57, 76, 0.69)]
    left, pw, sc, bw = 0.6, 6.6, 0.42, 1.25            # cm per unit of CEV
    body = []
    for v in range(0, 8, 2):
        body.append(f'\\draw[rulec, line width=0.3pt] ({left:.3f},{v * sc:.3f}) -- ({left + pw:.3f},{v * sc:.3f});\n')
        body.append(node(left - 0.12, v * sc, f'{v}', 'east', 'text=muted'))
    body.append(f'\\draw[ink, line width=0.6pt] ({left:.3f},0) -- ({left + pw:.3f},0);\n')
    for c, (name, vals, total, ext, parent) in enumerate(cols):
        cx = left + pw * (c + 0.5) / 3
        x = cx - bw / 2
        up = 0.0
        side = []
        for k, v in enumerate(vals):
            if v >= 0:
                ya, yb = up * sc, (up + v) * sc
                up += v
            else:
                ya, yb = v * sc, 0.0
            body.append(f'\\fill[{parts[k][1]}] ({x:.3f},{ya + 0.012:.3f}) rectangle ({x + bw:.3f},{yb - 0.012:.3f});\n')
            if yb - ya >= 0.32:
                tc = 'white' if parts[k][1] == 'hfblue' else 'navy'
                body.append(node(cx, (ya + yb) / 2, f'\\textbf{{{fmt(v, 2)}}}', 'center', f'text={tc}'))
            else:
                side.append([(ya + yb) / 2, fmt(v, 2)])
        side.sort(key=lambda r: r[0])
        for j in range(1, len(side)):
            side[j][0] = max(side[j][0], side[j - 1][0] + 0.26)
        for yl, s in side:
            body.append(node(x + bw + 0.06, yl, f'\\scriptsize {s}', 'west'))
        body.append(node(cx, up * sc + 0.08, f'\\textbf{{\\small {total:.2f}}}', 'south', 'text=navy'))
        base = -1.0 * sc - 0.12
        body.append(node(cx, base, f'\\textbf{{{name}}}', 'north', 'text=navy'))
        body.append(node(cx, base - 0.36, f'\\scriptsize externality {ext}\\%', 'north'))
        body.append(node(cx, base - 0.66, f'\\scriptsize parent {fmt(parent, 2, True)}', 'north'))
    lx = left + pw + 0.7
    body.append(node(lx, 7 * sc - 0.1, '\\textbf{The newborn\'s gain, four parts}', 'west', 'text=navy'))
    for k, (name, col) in enumerate(parts):
        yy = 7 * sc - 0.6 - k * 0.42
        body.append(f'\\fill[{col}, rounded corners=0.6pt] ({lx:.3f},{yy - 0.12:.3f}) rectangle ({lx + 0.24:.3f},{yy + 0.12:.3f});\n')
        body.append(node(lx + 0.36, yy, name, 'west'))
    yy = 7 * sc - 0.6 - 4 * 0.42 - 0.15
    body.append(node(lx, yy, '\\textbf{Orange and pink: the externality}', 'west', 'text=navy'))
    body.append(node(lx, yy - 0.4, 'Bold: the newborn\'s total, \\% of lifetime consumption', 'west'))
    return pic(body)


# ----------------------------------------------------------------------------- alternative transitions
def alttrans():
    rows = [('Main transition', 20, 0.0, 1.45),
            ('No exemption', 100, 13.6, 6.57), ('', 20, 5.3, 3.02),
            ('Announced five periods ahead', 100, 7.9, 3.46), ('', 20, 3.3, 1.91),
            ('Treatment exempt, first five periods', 100, 5.5, 6.20), ('', 20, 1.6, 2.72)]
    lab, pw, gap, rh, bh = 4.6, 3.9, 0.9, 0.36, 0.24
    body = []

    def ypos(i):
        return -(i + 0.5) * rh - (0.1 if i > 0 else 0) - (0.1 if i > 2 else 0) - (0.1 if i > 4 else 0)

    for k, (title, vmax) in enumerate([('Largest rise in homelessness, \\%', 15.0), ('Newborn\'s gain, \\%', 7.5)]):
        x0 = lab + k * (pw + gap)
        body.append(node(x0, 0.35, f'\\textbf{{{title}}}', 'west', 'text=navy'))
        body.append(f'\\draw[ink, line width=0.6pt] ({x0:.3f},0.12) -- ({x0:.3f},{ypos(6) - rh / 2:.3f});\n')
        for i, (g, pdet, rise, gain) in enumerate(rows):
            v = rise if k == 0 else gain
            xe = x0 + v / vmax * (pw - 0.6)
            y = ypos(i)
            body.append(hbar(x0, xe, y, bh, 'tforange' if pdet == 100 else 'hfblue'))
            lbl = 'none' if (k == 0 and v == 0) else (f'{v:.1f}' if k == 0 else f'{v:.2f}')
            body.append(node(xe + 0.06, y, f'\\textbf{{{lbl}}}', 'west'))
    for i, (g, pdet, rise, gain) in enumerate(rows):
        if g:
            body.append(node(0, ypos(i), f'\\textbf{{{g}}}' if i == 0 else g, 'west'))
    ly = ypos(6) - 0.55
    body.append(f'\\fill[tforange, rounded corners=0.6pt] ({lab:.3f},{ly - 0.11:.3f}) rectangle ({lab + 0.22:.3f},{ly + 0.11:.3f});\n')
    body.append(node(lab + 0.32, ly, 'Screen catches every user', 'west'))
    body.append(f'\\fill[hfblue, rounded corners=0.6pt] ({lab + 4.2:.3f},{ly - 0.11:.3f}) rectangle ({lab + 4.42:.3f},{ly + 0.11:.3f});\n')
    body.append(node(lab + 4.52, ly, 'Screen catches one in five (as in the main transition)', 'west'))
    return pic(body)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    for name, f in [('exp1', exp1), ('outcomes', outcomes), ('decomp', decomp), ('alttrans', alttrans)]:
        open(os.path.join(OUT, name + '.tex'), 'w').write(f())
        print('wrote charts/' + name + '.tex')
