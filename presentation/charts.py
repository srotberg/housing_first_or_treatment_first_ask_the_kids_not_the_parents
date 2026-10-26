"""charts.py: write the four results slides as inline-SVG charts, with their explanations.

    python3 presentation/charts.py

Rewrites project/slides/{exp1-table,main-outcomes,decomp,alt-table}.html. The numbers are the
paper's (Tables 5, 6 and 7 as of round r414), typed here once; change them here when the paper's do.
Colours: blue #2C6FAD and orange #D9822B are the paper's figures'; the decomposition adds
pink #e87ba4 and aqua #1baf7a (order checked with the dataviz validator: all checks pass, contrast
below 3:1 for three of them, so every bar carries its value as a label).
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SLIDES = os.path.join(HERE, 'project', 'slides')
INK, INK2, MUTED, GRID = '#14213D', '#3A4556', '#8A93A0', '#E4E0D5'
BLUE, ORANGE, PINK, AQUA = '#2C6FAD', '#D9822B', '#e87ba4', '#1baf7a'
FONT = "'IBM Plex Sans', Arial, sans-serif"


def head(sid, eyebrow, title, gap=24):
    return (f'<section id="{sid}" data-transition="fade" style="background:#FBFAF6;color:{INK2};font-family:{FONT};'
            f'padding:96px 128px 150px;display:flex;flex-direction:column;gap:{gap}px">\n'
            f'<p style="font-size:24px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:{BLUE}">{eyebrow}</p>\n'
            f'<h2 style="font-family:\'Source Serif 4\', Georgia, serif;font-size:56px;font-weight:600;line-height:1.1;color:{INK}">{title}</h2>\n')


def tail(n, footer, notes):
    return (f'<p style="position:absolute;left:128px;bottom:56px;width:1400px;font-size:24px;color:{MUTED}">{footer}</p>\n'
            f'<p style="position:absolute;right:128px;bottom:56px;width:120px;font-size:24px;color:{MUTED};text-align:right">{n}</p>\n'
            f'<aside>{notes}</aside>\n</section>\n')


def explain(read, takeaway):
    read, takeaway = read[0].upper() + read[1:], takeaway[0].upper() + takeaway[1:]
    return (f'<div style="display:flex;flex-direction:column;gap:10px">\n'
            f'<p style="font-size:24px;line-height:1.4;color:{INK2}"><b style="color:{INK}">How to read it.</b> {read}</p>\n'
            f'<p style="font-size:26px;line-height:1.4;color:{INK}"><b>What it shows.</b> {takeaway}</p>\n</div>\n')


def t(x, y, s, size=24, fill=INK2, anchor='start', weight=400):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-family="{FONT}">{s}</text>')


def bar(x0, x1, y, h, fill, tip):
    """A horizontal bar from x0 to x1, its data end rounded (4px) and its baseline end square."""
    a, b = min(x0, x1), max(x0, x1)
    w = max(b - a, 0.0)
    if w == 0:
        return ''
    r = min(4.0, w / 2, h / 2)
    if x1 >= x0:   # grows rightwards: round the right end
        d = (f'M{a:.1f},{y:.1f} H{b - r:.1f} Q{b:.1f},{y:.1f} {b:.1f},{y + r:.1f} V{y + h - r:.1f} '
             f'Q{b:.1f},{y + h:.1f} {b - r:.1f},{y + h:.1f} H{a:.1f} Z')
    else:          # grows leftwards: round the left end
        d = (f'M{b:.1f},{y:.1f} H{a + r:.1f} Q{a:.1f},{y:.1f} {a:.1f},{y + r:.1f} V{y + h - r:.1f} '
             f'Q{a:.1f},{y + h:.1f} {a + r:.1f},{y + h:.1f} H{b:.1f} Z')
    return f'<path d="{d}" fill="{fill}"><title>{tip}</title></path>'


def svg(w, h, body):
    return (f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" style="display:block;overflow:visible">'
            + ''.join(body) + '</svg>\n')


def fmt(v, d=0, pct=False):
    s = f'{abs(v):.{d}f}'
    return ('−' if v < 0 else '') + s + ('%' if pct else '')


# ---------------------------------------------------------------------------- slide 28
def exp1():
    rows = ['Both held', 'π<tspan baseline-shift="sub" font-size="18">V</tspan> clears',
            'Drug price clears', 'Both clear']
    tips = ['Both held', 'pi_V clears', 'Drug price clears', 'Both clear']
    use = [(6.48, -28), (6.48, -28), (7.47, -17), (7.46, -17)]          # level, change vs 8.97 (Table 5)
    cev = [-1.17, -1.09, -0.89, -0.74]
    W, H, lab, gap, rh, bh, top = 1664, 400, 300, 120, 80, 44, 64
    pw = (W - lab - gap) / 2
    body = []
    for k, (title, vmin) in enumerate([('Drug use, change against Housing First', -32),
                                       ('Newborn’s welfare, % of lifetime consumption', -1.4)]):
        x0 = lab + k * (pw + gap)
        zero = x0 + pw
        body.append(t(x0, 28, title, 26, INK, weight=600))
        body.append(f'<line x1="{zero}" y1="{top - 12}" x2="{zero}" y2="{top + 4 * rh}" stroke="{INK2}" stroke-width="2"/>')
        body.append(t(zero, top + 4 * rh + 32, '0', 24, MUTED, 'middle'))
        for i in range(4):
            y = top + i * rh + (rh - bh) / 2
            v = use[i][1] if k == 0 else cev[i]
            xe = zero + (v / -vmin) * pw
            tip = f'{tips[i]}: ' + (f'drug use {use[i][0]:.2f}% ({v}%)' if k == 0 else f'CEV {v:.2f}%')
            body.append(bar(zero, xe, y, bh, BLUE if k == 0 else ORANGE, tip))
            lbl = fmt(v, 0, True) if k == 0 else fmt(v, 2, True)
            body.append(t(xe - 12, y + bh / 2 + 9, lbl, 26, INK, 'end', 600))
    for i, r in enumerate(rows):
        body.append(t(0, top + i * rh + rh / 2 + 9, r, 26, INK))
    chart = svg(W, H, body)
    html = (head('exp1-table', 'Experiment 1 · no externalities',
                 'Drug use falls by up to 28%, yet a newborn loses in every case')
            + chart
            + explain('each row is one way of introducing Treatment First with the children left out: the drug price '
                      'and the voucher probability π<sub>V</sub> are held at their Housing First levels or allowed to clear. '
                      'Bars to the left of zero are falls in drug use (blue) and losses for a newborn (orange).',
                      'the screen deters a lot of use, but it takes an option from households that weigh the risks '
                      'correctly, and the budget gives little back: when π<sub>V</sub> clears, 58% of households gain, '
                      'by 0.05% on average, and 96% of those with a SUD lose. Moral hazard alone does not justify the screen.')
            + tail(28, 'Table 5, first half; change in drug use against Housing First without externalities (8.97%)',
                   'With the price clearing, the newborn loses less, 0.74 percent, but that is the general-equilibrium '
                   'effect of a cheaper drug, not a correction of moral hazard. Households with a SUD better off: 0, 0, 13 '
                   'and 13 percent.'))
    return html


# ---------------------------------------------------------------------------- slide 31
def outcomes():
    groups = [('Adults', [('Drug use', 8.92, 7.07, -21), ('Carrying a SUD', 3.83, 3.08, -19),
                          ('Homelessness', 0.62, 0.55, -11)]),
              ('Children', [('In a shelter', 1.03, 0.92, -11), ('Living with a parent who uses', 16.35, 13.24, -19),
                            ('Living with a parent with a SUD', 5.82, 4.75, -18)])]
    W, lab, pw, rh, bh, gh = 1664, 470, 640, 50, 32, 44
    zero = lab + pw
    body, y = [], 10
    body.append(t(zero + 40, 26, 'Housing First → Treatment First, % of households', 24, MUTED))
    y = 44
    for g, items in groups:
        body.append(t(0, y + 34, g, 26, INK, weight=600))
        y += gh
        for name, a, b, ch in items:
            yy = y + (rh - bh) / 2
            xe = zero + ch / 25 * pw
            body.append(bar(zero, xe, yy, bh, BLUE, f'{name}: {a:.2f}% to {b:.2f}% ({ch}%)'))
            body.append(t(xe - 12, yy + bh / 2 + 9, fmt(ch, 0, True), 25, INK, 'end', 600))
            body.append(t(28, yy + bh / 2 + 9, name, 25, INK2))
            body.append(t(zero + 40, yy + bh / 2 + 9, f'{a:.2f} → {b:.2f}', 25, INK2))
            y += rh
        y += 10
    body.append(f'<line x1="{zero}" y1="44" x2="{zero}" y2="{y}" stroke="{INK2}" stroke-width="2"/>')
    chart = svg(W, y + 6, body)
    html = (head('main-outcomes', 'Main experiment · long run',
                 'Every outcome falls, childhood homelessness included')
            + chart
            + explain('each bar is the long-run change when Treatment First replaces Housing First, with the drug price '
                      'and π<sub>V</sub> both clearing; on the right, the two levels.',
                      'children in a shelter fall by as much as homelessness, although critics expect a sobriety '
                      'condition to raise it. π<sub>V</sub> rises by 16%, to 7.80%; the drug price falls by 5%; treatment among '
                      'those with a SUD rises from 24.6 to 29.0%.')
            + tail(31, 'Table 5, last column; children are those living with households aged 26 to 50',
                   'Tax revenue rises mainly because more children start adult life with higher productivity. A household '
                   'with a SUD keeps its voucher by entering treatment and stopping; when it cannot respond at all, the '
                   'results still hold.'))
    return html


# ---------------------------------------------------------------------------- slide 33
def decomp():
    parts = [('Childhood its parent does not count', ORANGE),
             ('Productivity at entry its parent does not count', PINK),
             ('Its own adult life under the policy', BLUE),
             ('What its parent does count', AQUA)]
    cols = [('Both held', [2.20, 1.06, -0.75, 0.31], 2.82, 116, -1.19),
            ('π<tspan baseline-shift="sub" font-size="18">V</tspan> clears', [3.47, 1.00, 1.54, 0.44], 6.45, 69, 2.42),
            ('Both clear', [1.50, 0.46, 0.43, 0.19], 2.57, 76, 0.69)]
    tipname = ['Both held', 'pi_V clears', 'Both clear']
    W, H = 1664, 360
    left, plot_w, top, ymax, ymin = 70, 760, 34, 7.0, -1.0
    base_h = 330
    sc = base_h / (ymax - ymin)
    y0 = top + ymax * sc                                    # pixel row of zero
    body = []
    for v in range(0, 8, 2):
        yy = y0 - v * sc
        body.append(f'<line x1="{left}" y1="{yy:.1f}" x2="{left + plot_w}" y2="{yy:.1f}" stroke="{GRID}" stroke-width="1"/>')
        body.append(t(left - 14, yy + 8, f'{v}', 24, MUTED, 'end'))
    body.append(f'<line x1="{left}" y1="{y0:.1f}" x2="{left + plot_w}" y2="{y0:.1f}" stroke="{INK2}" stroke-width="2"/>')
    bw = 150
    for c, (name, vals, total, ext, parent) in enumerate(cols):
        cx = left + plot_w * (c + 0.5) / 3
        x = cx - bw / 2
        up = 0.0
        side = []
        for k, v in enumerate(vals):
            if v >= 0:
                ya, yb = y0 - (up + v) * sc, y0 - up * sc
                up += v
            else:
                ya, yb = y0, y0 - v * sc
            h = yb - ya
            body.append(f'<rect x="{x:.1f}" y="{ya + 1:.1f}" width="{bw}" height="{max(h - 2, 0):.1f}" fill="{parts[k][1]}">'
                        f'<title>{tipname[c]}: {parts[k][0]} {v:.2f}</title></rect>')
            if h >= 34:
                col = '#FFFFFF' if parts[k][1] == BLUE else INK
                body.append(t(cx, (ya + yb) / 2 + 9, fmt(v, 2), 24, col, 'middle', 600))
            elif v != 0:
                side.append([(ya + yb) / 2 + 8, fmt(v, 2)])
        side.sort(key=lambda r: -r[0])          # bottom first, then push each label up clear of the one below
        for j in range(1, len(side)):
            side[j][0] = min(side[j][0], side[j - 1][0] - 24)
        for yl, s_ in side:
            body.append(t(x + bw + 10, yl, s_, 22, INK2))
        ytot = y0 - up * sc
        body.append(t(cx, ytot - 14, f'{total:.2f}', 30, INK, 'middle', 700))
        body.append(t(cx, y0 - ymin * sc + 40, name, 26, INK, 'middle', 600))
        body.append(t(cx, y0 - ymin * sc + 74, f'externality {ext}%', 24, INK2, 'middle'))
        body.append(t(cx, y0 - ymin * sc + 104, f'parent {fmt(parent, 2, True)}', 24, INK2, 'middle'))
    lx = left + plot_w + 70
    body.append(t(lx, 40, 'The newborn’s gain, four parts', 26, INK, weight=600))
    for k, (name, col) in enumerate(parts):
        yy = 80 + k * 54
        body.append(f'<rect x="{lx}" y="{yy}" width="28" height="28" rx="4" fill="{col}"/>')
        body.append(t(lx + 44, yy + 22, name, 24, INK2))
    body.append(t(lx, 80 + 4 * 54 + 30, 'Orange and pink: the externality', 24, INK, weight=600))
    body.append(t(lx, 80 + 4 * 54 + 64, 'Bold: the newborn’s total, % of lifetime consumption', 24, INK2))
    chart = svg(W, H + 110, body)
    html = (head('decomp', 'Where the gain comes from',
                 'Three quarters of the newborn’s gain is an externality')
            + chart
            + explain('each bar is a newborn’s gain, split into four parts that sum to it; below it, the externality’s '
                      'share of the gain and the parent’s own gain.',
                      'the childhood part is the largest, because it accrues every year at home while the earnings '
                      'penalty reaches the child once. With prices held the parent loses; once the budget clears, both '
                      'the child and the parent gain.')
            + tail(33, 'Table 6, Section 6.3', 'ΔW = (1−ω_c)ΔC + (1−ω_c)ΔE + β^{J_K}ΔP + ω_c(ΔC+ΔE). With prices '
                   'held, the newborn’s own adult life is a loss, so the externality is more than all of the gain.'))
    return html


# ---------------------------------------------------------------------------- slide 39
def alttrans():
    rows = [('Main transition', None, 20, 0.0, 1.45),
            ('No exemption', 'every', 100, 13.6, 6.57), ('', 'one in five', 20, 5.3, 3.02),
            ('Announced five periods ahead', 'every', 100, 7.9, 3.46), ('', 'one in five', 20, 3.3, 1.91),
            ('Treatment exempt, first five periods', 'every', 100, 5.5, 6.20), ('', 'one in five', 20, 1.6, 2.72)]
    W, lab, gap, rh, bh, top = 1664, 520, 110, 44, 30, 56
    pw = (W - lab - gap) / 2
    body = []
    for k, (title, vmax) in enumerate([('Largest rise in homelessness, %', 15.0), ('Newborn’s gain, %', 7.5)]):
        x0 = lab + k * (pw + gap)
        body.append(t(x0, 28, title, 26, INK, weight=600))
        body.append(f'<line x1="{x0}" y1="{top - 10}" x2="{x0}" y2="{top + len(rows) * rh + 6}" stroke="{INK2}" stroke-width="2"/>')
        for i, (g, who, pdet, rise, gain) in enumerate(rows):
            y = top + i * rh + (rh - bh) / 2 + (10 if i > 0 else 0) + (10 if i > 2 else 0) + (10 if i > 4 else 0)
            v = rise if k == 0 else gain
            col = ORANGE if pdet == 100 else BLUE
            xe = x0 + v / vmax * (pw - 90)
            body.append(bar(x0, xe, y, bh, col, f'{g or rows[i - 1][0]}, detection {pdet}%: '
                                                + (f'largest rise {v}%' if k == 0 else f'newborn gain {v:.2f}%')))
            lbl = 'none' if (k == 0 and v == 0) else (f'{v:.1f}' if k == 0 else f'{v:.2f}')
            body.append(t(xe + 12, y + bh / 2 + 9, lbl, 26, INK, weight=600))
    for i, (g, who, pdet, rise, gain) in enumerate(rows):
        y = top + i * rh + rh / 2 + 9 + (10 if i > 0 else 0) + (10 if i > 2 else 0) + (10 if i > 4 else 0)
        if g:
            body.append(t(0, y, g, 26, INK, weight=600 if i == 0 else 400))
    ly = top + len(rows) * rh + 46
    body.append(f'<rect x="{lab}" y="{ly}" width="28" height="28" rx="4" fill="{ORANGE}"/>')
    body.append(t(lab + 42, ly + 22, 'Screen catches every user', 24, INK2))
    body.append(f'<rect x="{lab + 420}" y="{ly}" width="28" height="28" rx="4" fill="{BLUE}"/>')
    body.append(t(lab + 462, ly + 22, 'Screen catches one in five (as in the main transition)', 24, INK2))
    chart = svg(W, ly + 34, body)
    html = (head('alt-table', 'Alternative transitions · those with a SUD cannot stop',
                 'A temporary exemption nearly removes the early rise in homelessness', 20)
            + chart
            + explain('here a household with a SUD cannot stop using, so treatment alone does not keep its voucher. Left: '
                      'the largest rise in homelessness above Housing First along the path. Right: the gain of children '
                      'born at the reform.',
                      'putting every holder with a SUD out at once raises homelessness by up to 14%. A five-period '
                      'exemption in treatment holds it to 1.6% at one in five, with no rise in children in a shelter, and '
                      'newborns gain more than in the main transition.')
            + tail(39, 'Table 7, Section 6.5; the drug price and π<sub>V</sub> clear every period',
                   'Catching every user with no exemption keeps homelessness above Housing First for fifteen years. '
                   'Announcing the screen cuts drug use by 15 percent before it starts, but the rise comes when it does.'))
    return html


if __name__ == '__main__':
    for name, f in [('exp1-table', exp1), ('main-outcomes', outcomes), ('decomp', decomp), ('alt-table', alttrans)]:
        open(os.path.join(SLIDES, name + '.html'), 'w').write(f())
        print('wrote', name)
