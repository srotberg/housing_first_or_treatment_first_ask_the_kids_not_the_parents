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
from trpaths import levels, path, child_steady, latest_loop, pass_quality, reform_cohort_cev  # noqa: E402
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
    return out


RUNS = {
    'main': run('main', 'transition_2c_t70_Cu', ()),
    'ne100': run('ne100', 'transition_2c_t70_CAc', ('arms',), fallback=('transition_2c_t70_CAb', ('arms',))),
    # (19 October, 16:10) the hedge in a fresh container, code/transition_fix/remote_tr70_CAne.sh 0.20, while CA20e has no loop
    'ne20': run('ne20', 'transition_2c_t70_CA20e', ('arms',), fallback=('transition_2c_t70_CAne20', ('arms',))),
    'ann100': run('ann100', 'transition_2c_t70_CAann100', ('arms',)),
    'ann20': run('ann20', 'transition_2c_t70_CAann20', ('arms',)),
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

# THE TWO SENTENCES ON THE PHASED-IN RULES, from the numbers; yellow until both detection rates of a rule are in
LABEL = {'ann': 'Announcing the screen five periods before it starts',
         'gr': 'Exempting sobriety while in treatment for the first five periods'}


def clause(r):
    if r['hpk'] > ABOVE or r['cpk'] > ABOVE:
        return (f'raises homelessness by up to ${max(r["hpk"], 0):.0f}$ percent and the share of children in a shelter by '
                f'up to ${max(r["cpk"], 0):.0f}$ percent')
    return 'keeps homelessness and the share of children in a shelter from rising above their Housing First levels'


def sentence(m):
    a, b = RUNS[m + '100'], RUNS[m + '20']
    if a is None or b is None:
        return None
    ca, cb = clause(a), clause(b)
    s = (f'{LABEL[m]} {ca} at both detection rates' if ca == cb and ca.startswith('keeps') else
         f'{LABEL[m]} {ca} when the screen catches every user and {cb} when it catches ${PDET}$ percent')
    v = lambda x: (f'gain ${x:.2f}$' if x >= 0 else f'lose ${-x:.2f}$')
    if a['cev'] >= 0 and b['cev'] >= 0:
        s += f', and children born at the reform gain ${a["cev"]:.2f}$ and ${b["cev"]:.2f}$ percent of lifetime consumption, respectively.'
    else:
        s += f'; children born at the reform {v(a["cev"])} and {v(b["cev"])} percent of lifetime consumption, respectively.'
    return s if a['ok'] and b['ok'] else Y(s)


S = {m: sentence(m) for m in ('ann', 'gr')}
if S['ann'] is None and S['gr'] is None:
    res = Y('The announced transitions and those exempting sobriety while in treatment for the first five periods are still running; Table~\\ref{tab:alttrans} adds them as they finish.')
else:
    res = ' '.join(S[m] if S[m] is not None else Y(f'{LABEL[m]}: the transition is still running.') for m in ('ann', 'gr'))
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
out = {'x_at_results': res, 'x_at_years_word': {15: 'fifteen'}[YEARS], 'x_at_ne_cev': ne_cev,
       'x_at_pdet_words': 'one in ' + {2: 'two', 4: 'four', 5: 'five', 10: 'ten', 20: 'twenty'}[round(_inv)]}
d.update(out)
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_alttrans:', {k: (None if r is None else (r['src'], f'h {r["hpk"]:+.1f}/{r["hyr"]} c {r["cpk"]:+.1f}/{r["cyr"]} '
                                                    f'cev {r["cev"]:.2f} bud {100 * r["bud"]:.2f}% drug {r["drug"]}y'))
                          for k, r in RUNS.items()})
