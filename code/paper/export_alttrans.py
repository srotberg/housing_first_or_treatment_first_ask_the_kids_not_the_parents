"""export_alttrans.py -- THE ALTERNATIVE TRANSITIONS, Section 6.5 and Table tab:alttrans (19 October; the author: "make a
new subsection called something like: alternative transition specifications", "it should just explain what each
experiment does and how the first years of the transition look like on homelessness, childhood homelessness and
newborn welfare").

Seven T = 70 paths from the corrected Housing First, each read from its latest archived loop (trpaths.latest_loop):

  main     the main transition, rule C at detection 0.20 (results/transition_2c_t70_Cu, Section 6.4)
  ne100    no exemption for treatment (rule CA) at 1.00: results/transition_2c_t70_CAc, both prices clearing, else the
           held-price loop 0 of results/transition_2c_t70_CAb (the run 6.4's x_ne_tr_* read, export_noescape.py)
  ne20     the same at 0.20: results/transition_2c_t70_CA20e
  ann100   announced: Housing First for five years, rule CA from year 6 (code/transition_fix/patch_announce.py):
  ann20    results/transition_2c_t70_CAann100 and _CAann20
  gr100    grace years: rule CA from the reform, but in years 1-5 a household in treatment passes whatever it uses
  gr20     (code/transition_fix/patch_grace.py): results/transition_2c_t70_CAgrace100 and _CAgrace20

For each: the largest rise of homelessness and of the share of children in a shelter (homelessness of households aged
26-50) over years 1-15 against Housing First's steady state, the years either sits above it,
and the CEV of the cohort born at the reform (trpaths.reform_cohort_cev; the main row's is x_tr_cev_b1_2, the paper's
6.4 number). A run with no archived loop prints yellow dashes; a pass whose budget misses by more than 0.6 per cent of
net revenue after year 1, or whose drug market sits more than 5e-3 from clearing in more than three years, prints its
row in yellow (the author, 18 October: "it's enough if they are reasonable").

Writes writing/tables/tab_alttrans.tex and the x_at_* names into results_numbers.json; run after export_results.py."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from trpaths import levels, path, child_steady, latest_loop, pass_quality, reform_cohort_cev, mech_series  # noqa: E402
OUT = os.path.join(HERE, 'results_numbers.json')
TAB = os.path.join(ROOT, 'writing', 'tables', 'tab_alttrans.tex')
R = os.path.join(ROOT, 'results')
d = json.load(open(OUT))
PDET = d['x_tf_pdet_pc']
YEARS, ABOVE = 15, 0.05         # the window of "the first years", and what counts as above Housing First (percent; 6.4's
#                                 x_ne_tr_*_yrs count any year above; 0.05, not 0, from round r359: the announced path's
#                                 period 1 is +0.02 per cent, Housing First's own numerical noise, and read as above it)
Y = lambda s: '\\tocheck{' + s + '}'


def run(key, rdir, arms, fallback=None):
    """the row's numbers, or None while the run has no archived loop"""
    loop = latest_loop(os.path.join(R, rdir))
    if loop is None and fallback:
        rdir, arms = fallback
        loop = latest_loop(os.path.join(R, rdir))
    if loop is None:
        return None
    null, tf = os.path.join(R, rdir, *arms, 'arm_null'), os.path.join(R, rdir, *arms, 'arm_tf')
    p = path(os.path.join(loop, 'run.log.gz'))
    h0, c0 = levels(os.path.join(null, 'final.txt'))['homelessness h_1'], child_steady(null)
    dh = {t: 100 * (h / h0 - 1) for t, (h, c) in p.items()}
    dc = {t: 100 * (c / c0 - 1) for t, (h, c) in p.items()}
    first = [t for t in sorted(p) if t <= YEARS]
    assert len(first) == YEARS, f'{loop}: only {len(first)} of the first {YEARS} years'
    bud, drug = pass_quality(os.path.join(loop, 'run.log.gz'))
    out = dict(src=os.path.relpath(loop, ROOT), ok=bud <= 6e-3 and drug <= 3, bud=bud, drug=drug)
    for k, x in (('h', dh), ('c', dc)):
        t_pk = max(first, key=lambda t: x[t])
        up = [t for t in sorted(x) if x[t] > ABOVE]
        out[k + 'pk'], out[k + 'yr'] = x[t_pk], t_pk
        runs = []                       # consecutive periods as ranges: the announced path is below, then above
        for t in up:
            if runs and t == runs[-1][1] + 1:
                runs[-1][1] = t
            else:
                runs.append([t, t])
        out[k + 'span'] = ', '.join(f'{a}--{b}' if b > a else str(a) for a, b in runs) if runs else 'none'
    out['cev'] = float(d['x_tr_cev_b1_2']) if key == 'main' else reform_cohort_cev(loop, null, tf)
    # (round r360) what the text cites: drug use and treatment take-up in the first five periods, against Housing First
    nl = levels(os.path.join(null, 'final.txt'))
    b, tu = mech_series(os.path.join(loop, 'run.log.gz'), 'b'), mech_series(os.path.join(loop, 'run.log.gz'), 'take_up')
    out['b1'] = 100 * (b[1] / nl['drug use b'] - 1)
    out['tu15'] = 100 * sum(tu[t] for t in range(1, 6)) / 5
    out['tu0'] = 100 * nl['treatment take-up']
    out['dh'], out['dc'] = dh, dc
    return out


RUNS = {
    'main': run('main', 'transition_2c_t70_Cu', ()),
    'ne100': run('ne100', 'transition_2c_t70_CAc', ('arms',), fallback=('transition_2c_t70_CAb', ('arms',))),
    # (19 October, 16:10) the hedge in a fresh container, code/transition_fix/remote_tr70_CAne.sh 0.20, while CA20e has no loop
    'ne20': run('ne20', 'transition_2c_t70_CA20e', ('arms',), fallback=('transition_2c_t70_CAne20', ('arms',))),
    # (20 October) the re-seeded announced runs (remote_tr70_CAann2.sh) once they land, else the first ones
    'ann100': run('ann100', 'transition_2c_t70_CAann2_100', ('arms',), fallback=('transition_2c_t70_CAann100', ('arms',))),
    'ann20': run('ann20', 'transition_2c_t70_CAann2_20', ('arms',), fallback=('transition_2c_t70_CAann20', ('arms',))),
    'gr100': run('gr100', 'transition_2c_t70_CAgrace100', ('arms',)),
    'gr20': run('gr20', 'transition_2c_t70_CAgrace20', ('arms',)),
}


def cells(r):
    if r is None:
        return [Y('--')] * 5
    pk = lambda k: f'{r[k + "pk"]:.1f} ({r[k + "yr"]})' if r[k + 'pk'] > ABOVE else 'none'
    c = [pk('h'), r['hspan'], pk('c'), r['cspan'], f'{r["cev"]:.2f}']
    return c if r['ok'] else [Y(x) for x in c]


ROWS = [('Main transition', PDET, 'main'),
        ('No exemption', '100', 'ne100'), ('', PDET, 'ne20'),
        ('Announced five periods ahead', '100', 'ann100'), ('', PDET, 'ann20'),
        ('Sobriety while in treatment', '100', 'gr100'), ('exempt for the first five periods', PDET, 'gr20')]
body = []
for i, (lab, det, k) in enumerate(ROWS):
    if i in (1, 3, 5):
        body.append('\\addlinespace')
    body.append(' & '.join([lab, det] + cells(RUNS[k])) + ' \\\\')
tab = r"""\begin{table}[!htb]\centering
\caption{The first years of the alternative transitions}\label{tab:alttrans}
\begingroup\small
\sbox{\ntbox}{\begin{tabular}{@{}lcccccc@{}}
\toprule
 & & \multicolumn{2}{c}{Homelessness} & \multicolumn{2}{c}{Children in a shelter} & Newborn's \\
\cmidrule(lr){3-4}\cmidrule(lr){5-6}
 & $p_{\mathrm{det}}$ & Largest rise & Periods above & Largest rise & Periods above & gain \\
\midrule
""" + '\n'.join(body) + r"""
\bottomrule
\end{tabular}}
\usebox{\ntbox}
\tabnote{Notes: Each row is a transition from the Housing First benchmark to Treatment First with the drug price and $\pi_V$ clearing every period, against Housing First's steady state. Main transition: Section~\ref{sec:ftrans}, where a household with a SUD keeps its voucher by entering treatment and not using. In the other rows it cannot stop using, and the disorder fails the screen even in treatment: from the reform (no exemption), from period six with Housing First until then (announced five periods ahead), or from period six with treatment alone passing it until then (sobriety while in treatment exempt for the first five periods). $p_{\mathrm{det}}$ is the detection rate, in percent. Largest rise: the largest percent increase over the first """ + {15: 'fifteen'}[YEARS] + r""" periods, with its period in brackets. Periods above: the periods in which it is above Housing First. Children in a shelter is the homelessness of households aged 26 to 50. Newborn's gain: the CEV of children born at the reform, percent of lifetime consumption.}
\endgroup
\end{table}
"""
open(TAB, 'w').write(tab)

# THE PHASED-IN RULES IN THE TEXT (round r360, the author: "update the paper....the exemption for 5 years while in
# treatment seems pretty good"): one paragraph each, from the numbers; a rate whose run has not landed is said to be
# running, and a number from a pass that is not yet reasonable prints yellow
def num(r, x, fmt='.0f'):
    t = f'{x:{fmt}}'
    return t if r['ok'] else '\\mbox{\\tocheck{' + t + '}}'


def below_first(r, k='h'):
    """the periods from 1 before the path first rises above Housing First"""
    up = [t for t in sorted(r['d' + k]) if r['d' + k][t] > ABOVE]
    return (up[0] - 1) if up else None


WORDS = {1: 'period', 2: 'two periods', 3: 'three periods', 4: 'four periods', 5: 'five periods', 6: 'six periods',
         7: 'seven periods', 8: 'eight periods', 9: 'nine periods', 10: 'ten periods', 11: 'eleven periods',
         12: 'twelve periods'}
PENDING = '\\tocheck{{The run catching {} is still in progress.}} '


def ann_par():
    a, b, ne = RUNS['ann100'], RUNS['ann20'], RUNS['ne100']
    if a is None:
        return Y('The announced transitions are still running; Table~\\ref{tab:alttrans} adds them as they finish.')
    s = 'Announcing the screen five periods before it starts '
    s += ('lowers the rise without removing it. ' if ne is not None and 0 < a['hpk'] < ne['hpk'] else
          'changes the rise. ')
    if a['b1'] < -5 and max(a['dh'][t] for t in range(2, 6)) < 0:
        s += (f'While the screen is only announced, households cut their drug use at once, by ${num(a, -a["b1"])}$ percent in '
              'the first period when every user will be caught, and homelessness and the share of children in a shelter '
              'fall below their Housing First levels. ')
    s += (f'Once it starts revoking vouchers, they rise by up to ${num(a, max(a["hpk"], 0))}$ and '
          f'${num(a, max(a["cpk"], 0))}$ percent' + (f', against ${ne["hpk"]:.0f}$ and ${ne["cpk"]:.0f}$ percent without the '
                                                      'announcement' if ne is not None else '') + '. ')
    if b is None:
        s += PENDING.format('one in five users')
    elif b['hpk'] > ABOVE or b['cpk'] > ABOVE:
        s += (f'When it catches one in five users, they rise by up to ${num(b, max(b["hpk"], 0))}$ and '
              f'${num(b, max(b["cpk"], 0))}$ percent. ')
    else:
        s += 'When it catches one in five users, neither rises above its Housing First level. '
    s += (f'Children born at the reform gain ${num(a, a["cev"], ".2f")}$ percent of lifetime consumption' +
          (f' and ${num(b, b["cev"], ".2f")}$ percent, respectively.' if b is not None else '.'))
    return s


def gr_par():
    a, b = RUNS['gr20'], RUNS['gr100']
    if a is None and b is None:
        return Y('The transitions with sobriety exempt while in treatment are still running; Table~\\ref{tab:alttrans} '
                 'adds them as they finish.')
    r = a if a is not None else b
    s = ('Exempting sobriety while in treatment for the first five periods lets a household with a SUD keep its voucher '
         'in those periods by entering treatment, even if it uses drugs, and more of them do: '
         f'${num(r, r["tu15"])}$ percent of those with a SUD are in treatment, against ${r["tu0"]:.0f}$ percent under '
         'Housing First. ')
    if a is not None:
        k = below_first(a)
        s += 'When the screen catches one in five users, '
        if k is None:
            s += 'homelessness never rises above its Housing First level'
        else:
            s += (f'homelessness stays below its Housing First level for the first {WORDS.get(k, str(k) + " periods")} and '
                  f'rises above it by at most ${num(a, a["hpk"], ".1f")}$ percent after the exemption ends')
        s += (', and the share of children in a shelter never rises above its Housing First level. ' if a['cpk'] <= ABOVE else
              f', and the share of children in a shelter by at most ${num(a, a["cpk"], ".1f")}$ percent. ')
    if b is None:
        s += PENDING.format('every user')
    else:
        s += (f'When every user is caught, homelessness rises by up to ${num(b, max(b["hpk"], 0))}$ percent and the share '
              f'of children in a shelter by up to ${num(b, max(b["cpk"], 0))}$ percent. ')
    cevs = [(r_, w) for r_, w in ((a, 'one in five'), (b, 'every')) if r_ is not None]
    s += 'Children born at the reform gain ' + ' and '.join(f'${num(r_, r_["cev"], ".2f")}$' for r_, _ in cevs) + \
         ' percent of lifetime consumption' + (', respectively.' if len(cevs) == 2 else '.')
    return s


def lesson():
    """the sentence the third lesson takes from the exemption at one in five users caught"""
    a = RUNS['gr20']
    if a is None:
        return ''
    if a['cpk'] <= ABOVE and a['hpk'] < 3:
        return ('A temporary exemption keeps that rise small: if a household in treatment keeps its voucher, sober or not, '
                'for the first five periods, and the screen catches one in five users, the share of children in a shelter '
                f'never rises above its Housing First level and homelessness rises by at most ${a["hpk"]:.1f}$ '   # plain: the paragraph is yellow
                'percent, while newborns still gain.')
    return ''


# THE NEWBORN'S GAIN UNDER NO EXEMPTION (round r357, the author: "you don't talk about the newborn welfare numbers in
# that section"): the reform cohort at both detection rates against the main transition's; a number from a run that has
# not landed, or whose pass is not yet reasonable, prints yellow
def cev_txt(r):
    if r is None:
        return '\\mbox{\\tocheck{--}}'
    x = f'{abs(r["cev"]):.2f}'
    return x if r['ok'] else '\\mbox{\\tocheck{' + x + '}}'


a, b, m0 = RUNS['ne100'], RUNS['ne20'], float(d['x_tr_cev_b1_2'])
verb = lambda r: 'gain' if r is None or r['cev'] >= 0 else 'lose'
if verb(a) == verb(b) == 'gain':
    ne_cev = (f'Even so, children born at the reform gain ${cev_txt(a)}$ percent of lifetime consumption when every user is '
              f'caught and ${cev_txt(b)}$ percent when ${PDET}$ percent are, against ${m0:.2f}$ percent in the main transition.')
else:
    ne_cev = (f'Children born at the reform {verb(a)} ${cev_txt(a)}$ percent of lifetime consumption when every user is caught '
              f'and {verb(b)} ${cev_txt(b)}$ percent when ${PDET}$ percent are, against a gain of ${m0:.2f}$ percent in the main '
              f'transition.')
# (round r357, the author on 'Catching 20 percent of users': "only one in five users")
_inv = 100 / float(PDET)
assert abs(_inv - round(_inv)) < 1e-9, PDET
out = {'x_at_results': '', 'x_at_ann_par': ann_par(), 'x_at_gr_par': gr_par(), 'x_at_lesson': lesson(), 'x_at_years_word': {15: 'fifteen'}[YEARS], 'x_at_ne_cev': ne_cev,
       'x_at_pdet_words': 'one in ' + {2: 'two', 4: 'four', 5: 'five', 10: 'ten', 20: 'twenty'}[round(_inv)]}
d.update(out)
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_alttrans:', {k: (None if r is None else (r['src'], f'h {r["hpk"]:+.1f}/{r["hyr"]} c {r["cpk"]:+.1f}/{r["cyr"]} '
                                                    f'cev {r["cev"]:.2f} bud {100 * r["bud"]:.2f}% drug {r["drug"]}y'))
                          for k, r in RUNS.items()})
