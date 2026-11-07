"""THE THIRD EXPERIMENT: A WEIGHT OF ONE ON THE CHILD (Section sec:omega1, Table tab:omega1; 7 November).

The author, 6 November: the experiment shows "the contract market"; "in the table, you just want to show the welfare
effects, no need to show the impacts on drug use levels", "you dont need to show the fit or the levels of other things",
"the point is to understand the change in welfare".

The omega_c = 1 economy: the benchmark's handover with weight_on_child 1 and only b reset to drug use
(results/omega1_2c/bench_1.0_b0.00479_ku1.0; the author: "it doesnt have to be fully recalibrated"); Housing First
re-solved on the corrected build (results/omega1_Cu/cf/null); Treatment First at detection 0.15, the rate at which 60
percent of the tested users stop on impact (results/whostops_omega1_pts_0p15_0p20/scan.txt), in the main experiment's
four columns (results/omega1_Cu/cf/{fixboth,fixp,fixpv,tf}). Each column's welfare is split exactly as Table
tab:whogains splits the main experiment's (welfare_nok.parts), against the omega_c = 1 benchmark's own curve, with
Housing First's newborn masses normalised (as export_nish_parts.py does for the 0.686 run). At omega_c = 1 the
externality is zero, so the newborn's gain is childhood, better productivity at entry and its own adult life, all of
them counted by the parent.

A column that has not landed (no checks.txt with a final DIST CHECK PASS) prints 'running' in the table and gives no
names, so no sentence can quote it.

usage: python3 code/paper/export_omega1.py   -> x_om1_* names merged into code/paper/results_numbers.json, and
writing/tables/tab_omega1.tex (export_results.py rewrites the JSON whole, so run this after it)."""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import welfare_nok as w

OUT_JSON = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_omega1.tex')
BENCH = os.path.join(ROOT, 'results', 'omega1_2c', 'bench_1.0_b0.00479_ku1.0')
MOMENTS = os.path.join(ROOT, 'results', 'omega1_2c', 'omega_1.0_b0.00479_ku1.0.moments.txt')
CF = os.path.join(ROOT, 'results', 'omega1_Cu', 'cf')
SCAN = os.path.join(ROOT, 'results', 'whostops_omega1_pts_0p15_0p20', 'scan.txt')
PDET = 0.15
# the columns in Table tab:longrun's order: both held, pi_V clears (price held), the price clears (pi_V held), both clear
COLS = [('held', 'fixboth', 'Both held'), ('pvc', 'fixp', r'$\pi_V$ clears'), ('prc', 'fixpv', 'Price clears'),
        ('tf', 'tf', 'Both clear')]


def accepted(d):
    p = os.path.join(d, 'checks.txt')
    return (os.path.exists(p) and os.path.exists(os.path.join(d, 'value_at_26_by_node.txt'))
            and 'DIST CHECK PASS' in open(p).read())


def users():
    """drug users in the omega_c = 1 benchmark, the last block's MOMENT b"""
    v = [float(re.search(r'model=\s*(\S+)', l).group(1)) for l in open(MOMENTS) if re.match(r'\s*MOMENT b\s', l)]
    return 100 * v[-1]


def stop_share():
    for l in open(SCAN):
        f = l.split()
        if f and not l.startswith('#') and abs(float(f[0]) - PDET) < 1e-9:
            return float(f[2])
    raise SystemExit(f'no detection {PDET} line in {SCAN}')


def final_change(d, label):
    """the percent change a column's final.txt reports for one line (e.g. 'drug use b', 'drug price')"""
    for l in open(os.path.join(d, 'final.txt')):
        if l.strip().startswith(label + ' '):
            return float(re.search(r'change\s+([-+]?[\d.]+)%', l).group(1))
    raise SystemExit(f'no {label!r} line in {d}/final.txt')


def num(x):
    return f"{x:.2f}".replace('-', '$-$') if x < 0 else f"{x:.2f}"


if __name__ == '__main__':
    B = w.Bench(BENCH)
    assert abs(B.omega - 1) < 1e-12, B.omega
    m = w.masses()
    s = sum(m.values())
    m = {k: v / s for k, v in m.items()}
    out = {'x_om1_pdet_pc': f"{100 * PDET:.0f}", 'x_om1_stop_pc': f"{stop_share():.0f}",
           'x_om1_users_pc': f"{users():.2f}"}
    rows = {}
    for tag, col, _ in COLS:
        d = os.path.join(CF, col)
        # the both-clear column cycled at the default price step and was re-run damped (7 November); if that flips
        # too, the price is held at the flips' mean with pi_V clearing (tf_held): the latest accepted re-run wins
        if col == 'tf':
            for alt in ('tf_both', 'tf_held', 'tf_damped'):
                if accepted(os.path.join(CF, alt)):
                    d = os.path.join(CF, alt)
                    break
        if not accepted(d):
            continue
        r = w.parts(d, d, os.path.join(CF, 'null'), os.path.join(CF, 'null'), bench=B, m=m)
        p = r['pts']
        assert abs(p['ext']) < 1e-9, (col, p['ext'])          # no externality at a weight of one
        gain = max(0.0, 100 - r['worse'])
        rows[tag] = dict(tot=p['tot'], child=p['cntC'], entry=p['cntE'], own=p['own'], P=p['P'], gain=gain)
        out.update({
            f'x_om1_tot_{tag}': f"{p['tot']:.2f}", f'x_om1_totabs_{tag}': f"{abs(p['tot']):.2f}",
            f'x_om1_child_{tag}': f"{p['cntC']:.2f}", f'x_om1_entry_{tag}': f"{p['cntE']:.2f}",
            f'x_om1_early_{tag}': f"{p['cntC'] + p['cntE']:.2f}",
            f'x_om1_own_{tag}': f"{p['own']:.2f}", f'x_om1_ownabs_{tag}': f"{abs(p['own']):.2f}",
            f'x_om1_P_{tag}': f"{p['P']:.2f}", f'x_om1_Pabs_{tag}': f"{abs(p['P']):.2f}",
            f'x_om1_gain_pc_{tag}': f"{gain:.0f}",
            f'x_om1_tot_dir_{tag}': 'gains' if p['tot'] > 0 else 'loses',
            f'x_om1_P_dir_{tag}': 'gain' if p['P'] > 0 else 'lose',
            # drug use and the drug price, for the sentences that explain a column (not in the table: the author)
            f'x_om1_bdrop_{tag}': f"{(-final_change(d, 'drug use b') or 0.0) + 0.0:.2f}",
            f'x_om1_pdrop_{tag}': f"{(-final_change(d, 'drug price') or 0.0) + 0.0:.2f}",
            f'x_om1_pvrise_{tag}': f"{(final_change(d, 'pi_V (voucher probability)') or 0.0) + 0.0:.2f}",
            f'x_om1_parents_{tag}': ("every parent loses" if gain < 0.5 else "every parent gains" if gain > 99.5
                                     else f"{gain:.0f} percent of parents gain"),
        })
    # the first column against the main experiment's (Section 6.4: "the gain is @@x_om1_held_vs_main@@ compared to")
    if 'held' in rows:
        main = float(json.load(open(OUT_JSON))['x_dc_b_cev'])
        out['x_om1_held_vs_main'] = 'smaller' if rows['held']['tot'] < main else 'larger'
    # the price-clears column against partial equilibrium (Section 6.4, the author: "they gain less than the PE, right?
    # maybe explain it like that"): the newborn's gain, its childhood and entry parts, and the parents' loss
    if 'held' in rows and 'prc' in rows:
        h, c = rows['held'], rows['prc']
        out['x_om1_tot_prc_vs_held'] = 'less' if c['tot'] < h['tot'] else 'more'
        out['x_om1_early_prc_vs_held'] = 'less' if c['child'] + c['entry'] < h['child'] + h['entry'] else 'more'
        out['x_om1_loss_prc_vs_held'] = 'less' if abs(c['P']) < abs(h['P']) else 'more'
    # the table: welfare only (the author)
    hdr = ' & '.join(lab for _, _, lab in COLS)
    cell = lambda tag, k: num(rows[tag][k]) if tag in rows else 'running'
    pct = lambda tag: f"{rows[tag]['gain']:.0f}" if tag in rows else 'running'
    line = lambda lab, k: f"{lab} & " + ' & '.join(cell(t, k) for t, _, _ in COLS) + r' \\'
    tab = '\n'.join([
        r'\begin{tabular}{@{}lcccc@{}}', r'\toprule', f' & {hdr} \\\\', r'\midrule',
        line(r"The newborn's gain, $\Delta W$", 'tot'),
        line(r'\quad Childhood, $\Delta C$', 'child'),
        line(r'\quad Better productivity at entry, $\Delta E$', 'entry'),
        line(r"\quad Its own adult life, $\beta^{J_K}\Delta P$", 'own'),
        r'\midrule',
        line(r"The parent's own gain, $\Delta P$", 'P'),
        r"Parents who gain, percent & " + ' & '.join(pct(t) for t, _, _ in COLS) + r' \\',
        r'\bottomrule', r'\end{tabular}', ''])
    open(TAB, 'w').write(tab)
    d = json.load(open(OUT_JSON))
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    print(f"export_omega1: {len(out)} names, columns in: {', '.join(rows) or 'none'}; {TAB}")
