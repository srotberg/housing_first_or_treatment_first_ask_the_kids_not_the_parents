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
# (20 October, round r364, the author: "if you have initial numbers for the full table, put them all in the table and
# paper, and remove the yellow (but keep the tab on your side so you know you have to update them later)") a number from
# a pass that is not yet reasonable prints plain; which ones are provisional is written to alttrans_provisional.json,
# not the paper. A run with no archived loop still prints a yellow dash: there is no number to show.
YELLOW_PROVISIONAL = False
TAB_PROV = os.path.join(HERE, 'alttrans_provisional.json')
WINDOW_100 = 25                 # the periods a 1.00 row is judged on (the reform cohort's childhood)
PREV = os.path.join(HERE, 'tab_alttrans_prev.json')   # the note as the author last read it (--freeze moves it)


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
    # (20 October, the author: "keep the 100% rows with a note") at 1.00 the long run has no clearing drug price (16
    # October: drug use jumps between -56 and -63 per cent near 0.80), so the path's last periods sit 8-10 per cent off
    # whatever the loops do; those rows are judged on the periods Table 7 and the reform cohort's childhood use
    bud, drug = pass_quality(os.path.join(loop, 'run.log.gz'), last=WINDOW_100 if key.endswith('100') else None)
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
    # (round r360, the author on the newborn's gains: "explain why more than the main experiment", "why is this less
    # than the 6.74 with no exemptions?") the share with a SUD and pi_V along the reform cohort's childhood
    out['lam'], out['pv'] = mech_series(os.path.join(loop, 'run.log.gz'), 'lambda_d'), mech_series(os.path.join(loop, 'run.log.gz'), 'pi_v')
    out['pv0'] = nl['pi_V (voucher probability)']
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
    # (20 October, the author: "restart the 20% run") the re-seeded run (remote_tr70_CAgr2.sh) once it lands, else the first
    'gr20': run('gr20', 'transition_2c_t70_CAgr2_20', ('arms',), fallback=('transition_2c_t70_CAgrace20', ('arms',))),
}


def cells(r):
    if r is None:
        return [Y('--')] * 5
    pk = lambda k: f'{r[k + "pk"]:.1f} ({r[k + "yr"]})' if r[k + 'pk'] > ABOVE else 'none'
    c = [pk('h'), r['hspan'], pk('c'), r['cspan'], f'{r["cev"]:.2f}']
    return c if r['ok'] or not YELLOW_PROVISIONAL else [Y(x) for x in c]


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
\tabnote{Notes: Each row is a transition from the Housing First benchmark to Treatment First with the drug price and $\pi_V$ clearing every period, against Housing First's steady state. Main transition: Section~\ref{sec:ftrans}, where a household with a SUD keeps its voucher by entering treatment and not using. In the other rows it cannot stop using, and the disorder fails the screen even in treatment: from the reform (no exemption), from period six with Housing First until then (announced five periods ahead), or from period six with treatment alone passing it until then (sobriety while in treatment exempt for the first five periods). $p_{\mathrm{det}}$ is the detection rate, in percent. Largest rise: the largest percent increase over the first """ + {15: 'fifteen'}[YEARS] + r""" periods, with its period in brackets. Periods above: the periods in which it is above Housing First. Children in a shelter is the homelessness of households aged 26 to 50. Newborn's gain: the CEV of children born at the reform, percent of lifetime consumption. When every user is caught, no drug price clears the long-run drug market, because drug use jumps as the price moves through the level that would clear it; those transitions end at the long-run solution that comes closest.}
\endgroup
\end{table}
"""
# RED MARKS WHAT MOVED in the note (round r363): a sentence not in the frozen baseline is \\textcolor{red} (as the
# calibration tables, never \\new, which breaks a table cell); --freeze makes the current note the baseline
import re as _re
_m = _re.search(r'\\tabnote\{(.*)\}\n\\endgroup', tab, _re.S)
_sents = [x for x in _re.split(r'(?<=\.) (?=[A-Z$\\])', _m.group(1)) if x]
if '--freeze' in sys.argv:
    json.dump({'note_sentences': _sents}, open(PREV, 'w'), indent=1)
_prev = set(json.load(open(PREV))['note_sentences']) if os.path.exists(PREV) else set(_sents)
tab = tab[:_m.start(1)] + ' '.join(x if x in _prev else '\\textcolor{red}{' + x + '}' for x in _sents) + tab[_m.end(1):]
open(TAB, 'w').write(tab)
# THE TAB ON MY SIDE: every row's source and whether its pass is reasonable yet (a provisional row is updated as its
# runs' later loops archive)
_tab = {k: (None if r is None else {'src': r['src'], 'reasonable': bool(r['ok']), 'budget_pc': round(100 * r['bud'], 3),
                                    'drug_periods_off': r['drug']})
        for k, r in RUNS.items()}
# (round r365, the author on the third lesson: "remove this yellow and just leave in your notes that you have to double
# check this after all the simulations are done") the lesson prints black; this is the note
_tab['_to_check_when_all_runs_are_reasonable'] = [
    'the third lesson (conclusion): its first sentence and x_at_lesson -- re-read against the final alternative transitions',
    "6.5's paragraphs (x_at_ne_cev, x_at_ann_par, x_at_gr_par) and Table 7's rows: every number provisional while its row is"]
json.dump(_tab, open(TAB_PROV, 'w'), indent=1, sort_keys=True)

# THE PHASED-IN RULES IN THE TEXT (round r360, the author: "update the paper....the exemption for 5 years while in
# treatment seems pretty good"): one paragraph each, from the numbers; a rate whose run has not landed is said to be
# running, and a number from a pass that is not yet reasonable prints yellow
def num(r, x, fmt='.0f'):
    t = f'{x:{fmt}}'
    return t if r['ok'] or not YELLOW_PROVISIONAL else '\\mbox{\\tocheck{' + t + '}}'


def below_first(r, k='h'):
    """the periods from 1 before the path first rises above Housing First"""
    up = [t for t in sorted(r['d' + k]) if r['d' + k][t] > ABOVE]
    return (up[0] - 1) if up else None


MAIN = RUNS['main']
# (round r361, the author on "the screen that follows the exemption deters more": "how can it deter more when both
# cases have 20 percent detection rate?") the rule, not the rate: in the main transition a household with a SUD keeps
# its voucher by entering treatment and not using, here it cannot, so using drugs risks more (long run: drug use falls
# 30 per cent at 0.20 here, 21 in the main transition). Said in full the first time a 20 per cent path is compared with
# the main transition, then referred to.
# (round r362, the author on both: "makes no sense") said from the households' side: they cannot stop using, so the
# disorder puts the voucher at risk until recovery, where in the main transition treatment and sobriety keep it
def mech_full(when):
    return (f'Here a household with a SUD cannot stop using, so {when} the disorder puts its voucher at risk until it '
            'recovers, while in the main transition the household keeps the voucher by entering treatment and not using. '
            'Starting to use therefore risks more, and fewer households use drugs: ')


def mech_short(when):
    return (f'because {when} a household with a SUD, which cannot stop using, risks its voucher until it recovers, so '
            'fewer households use drugs: ')


SAID = {}


def pc(x):
    """a percent rise in the text: whole numbers, one decimal below one"""
    return '.1f' if abs(x) < 1 else '.0f'


def why_more(r, again=False):
    """(round r360) why children born at the reform gain more on a path than in the main transition, in the paper's own
    terms (Section 6.4's reform cohort): fewer of them grow up with a parent who has a SUD, and pi_V is higher. The
    share with a SUD by period ten (the main transition's is x_trf_sud10, the number 6.4 quotes); None if the path's
    cohort does not gain more or its share is not lower"""
    if r is None or r['cev'] <= MAIN['cev'] or not all(r['lam'][t] < MAIN['lam'][t] for t in range(2, 26)):
        return None
    assert f"{100 * MAIN['lam'][10]:.2f}" == d['x_trf_sud10'], (MAIN['lam'][10], d['x_trf_sud10'])
    w = (f'by period ten, ${num(r, 100 * r["lam"][10], ".2f")}$ percent of households have a SUD, against '
         f'${d["x_trf_sud10"]}$ percent' + ('' if again else ' in the main transition') + ', so fewer of these children grow up with a parent who has '
         'the disorder')
    if all(r['pv'][t] > MAIN['pv'][t] for t in range(1, 26)):
        w += ', and $\\pi_V$ is higher throughout their childhood'
    return w


WORDS = {1: 'period', 2: 'two periods', 3: 'three periods', 4: 'four periods', 5: 'five periods', 6: 'six periods',
         7: 'seven periods', 8: 'eight periods', 9: 'nine periods', 10: 'ten periods', 11: 'eleven periods',
         12: 'twelve periods'}
PENDING = '\\tocheck{{The run catching {} is still in progress.}} '


def ann_par():
    a, b, ne = RUNS['ann100'], RUNS['ann20'], RUNS['ne100']
    if a is None:
        return Y('The announced transitions are still running; Table~\\ref{tab:alttrans} adds them as they finish.')
    s = 'Announcing the screen five periods before it starts '
    s += ('lowers the rise but does not eliminate it. ' if ne is not None and 0 < a['hpk'] < ne['hpk'] else
          'changes the rise. ')
    if a['b1'] < -5 and max(a['dh'][t] for t in range(2, 6)) < 0:
        # (round r360, the author on "when every user will be caught": "but HF continue for 5 years, no?")
        s += ('While Housing First continues, households cut their drug use at once in anticipation of a screen that will '
              f'catch every user, by ${num(a, -a["b1"])}$ percent in the first period, and homelessness and the share of '
              'children in a shelter fall below their Housing First levels. ')
    s += (f'Once it starts revoking vouchers, they rise by up to ${num(a, max(a["hpk"], 0))}$ and '
          f'${num(a, max(a["cpk"], 0))}$ percent' + (f', against ${ne["hpk"]:.0f}$ and ${ne["cpk"]:.0f}$ percent without the '
                                                      'announcement' if ne is not None else '') + '. ')
    if b is None:
        s += PENDING.format('one in five users')
    elif b['hpk'] > ABOVE or b['cpk'] > ABOVE:
        s += (f'When it catches one in five users, they rise by up to ${num(b, max(b["hpk"], 0), pc(b["hpk"]))}$ and '
              f'${num(b, max(b["cpk"], 0), pc(b["cpk"]))}$ percent. ')
    else:
        s += 'When it catches one in five users, neither rises above its Housing First level. '
    s += (f'Children born at the reform gain ${num(a, a["cev"], ".2f")}$ percent of lifetime consumption when every user is '
          'caught' + (f' and ${num(b, b["cev"], ".2f")}$ percent when one in five users are' if b is not None else '') + '. ')
    # (round r360, the author on 4.94: "why is this less than the 6.74 with no exemptions?") the cohort's first five
    # periods: pi_V held at Housing First's (no voucher is revoked before the screen starts) and a smaller fall in use
    if ne is not None and a['cev'] < ne['cev']:
        flat = max(a['pv'][t] for t in range(1, 6)) <= a['pv0'] * 1.005 < a['pv'][6]
        less = a['b1'] > ne['b1']
        why = [w for w, c in (('$\\pi_V$ does not rise until the screen starts', flat),
                              (f'drug use falls by less in the first period than the ${num(ne, -ne["b1"])}$ percent when the '
                               'screen starts at once', less)) if c]
        if why:
            s += (('The first is' if b is not None else 'This is') + f' less than the ${num(ne, ne["cev"], ".2f")}$ percent without the '
                  'announcement, because ' + ' and '.join(why) + '. ')
    # (round r361, the author: "and why is the 2.57 higher than the main simulation?")
    w = why_more(b, again=True) if b is not None else None
    if w:
        s += (f'The second is also more than the ${MAIN["cev"]:.2f}$ percent in the main transition, although the screen '
              'catches one in five users in both. ' + mech_full('once the screen starts') + w + '.')
        SAID['mech'] = True
    return s.rstrip()


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
    # (round r362) both rates in the same words, the 1.00 path's as the 0.20 one's: it also falls below Housing First
    # while the exemption lasts, and its children in a shelter rise by 0.2 per cent, which a whole number printed as 0
    for r_, when in ((a, 'When the screen catches one in five users, '), (b, 'When every user is caught, ')):
        if r_ is None:
            s += PENDING.format('one in five users' if r_ is a else 'every user')
            continue
        k = below_first(r_)
        s += when
        if k is None:
            s += 'homelessness never rises above its Housing First level'
        else:
            s += (f'homelessness stays below its Housing First level for the first {WORDS.get(k, str(k) + " periods")} but '
                  f'rises above it by at most ${num(r_, r_["hpk"], ".1f")}$ percent after the exemption ends')
        s += (', and the share of children in a shelter never rises above its Housing First level. ' if r_['cpk'] <= ABOVE
              else f', and the share of children in a shelter by at most ${num(r_, r_["cpk"], ".1f")}$ percent. ')
    s += f'Children born at the reform gain ${num(r, r["cev"], ".2f")}$ percent of lifetime consumption' + \
         (' when one in five users are caught' if a is not None and b is not None else '')
    # (round r360, the author on 3.14: "why is it even higher than the main experiment without the exemptions?")
    w = why_more(a, again=True) if a is not None else None
    if w and 'mech' in SAID:
        s += (f', more than the ${MAIN["cev"]:.2f}$ percent in the main transition, ' + mech_short('once the exemption ends')
              + w + '.')
    elif w:
        s += (f', more than the ${MAIN["cev"]:.2f}$ percent in the main transition, although the screen catches one in five '
              'users in both. ' + mech_full('once the exemption ends') + w + '.')
    else:
        s += '.'
    if a is not None and b is not None:
        s += f' When every user is caught, they gain ${num(b, b["cev"], ".2f")}$ percent.'
    return s


def lesson():
    """the sentence the third lesson takes from the exemption at one in five users caught"""
    a = RUNS['gr20']
    if a is None:
        return ''
    if a['cpk'] <= ABOVE and a['hpk'] < 3:
        return ('A temporary exemption for those with a SUD keeps the latter from ever rising and the former\'s rise '
                'small: if a household in treatment keeps its '
                'voucher, sober or not, for the first five periods, and the screen catches one in five users, the share of '
                'children in a shelter never rises above its Housing First level and homelessness rises by at most '
                f'${a["hpk"]:.1f}$ percent, '   # plain: the paragraph is yellow
                + ('with newborns gaining even more than in the main transition.' if a['cev'] > MAIN['cev'] else
                   'while newborns still gain.' if a['cev'] > 0 else 'but newborns lose.'))
    return ''


# THE NEWBORN'S GAIN UNDER NO EXEMPTION (round r357, the author: "you don't talk about the newborn welfare numbers in
# that section"): the reform cohort at both detection rates against the main transition's; a number from a run that has
# not landed, or whose pass is not yet reasonable, prints yellow
def cev_txt(r):
    if r is None:
        return '\\mbox{\\tocheck{--}}'
    x = f'{abs(r["cev"]):.2f}'
    return x if r['ok'] or not YELLOW_PROVISIONAL else '\\mbox{\\tocheck{' + x + '}}'


a, b, m0 = RUNS['ne100'], RUNS['ne20'], float(d['x_tr_cev_b1_2'])
verb = lambda r: 'gain' if r is None or r['cev'] >= 0 else 'lose'
if verb(a) == verb(b) == 'gain':
    ne_cev = (f'Even so, children born at the reform gain ${cev_txt(a)}$ percent of lifetime consumption when every user is '
              f'caught and ${cev_txt(b)}$ percent when ${PDET}$ percent are, against ${m0:.2f}$ percent in the main transition.')
else:
    ne_cev = (f'Children born at the reform {verb(a)} ${cev_txt(a)}$ percent of lifetime consumption when every user is caught '
              f'and {verb(b)} ${cev_txt(b)}$ percent when ${PDET}$ percent are, against a gain of ${m0:.2f}$ percent in the main '
              f'transition.')
# (round r360, the author on the newborn's gain without the exemption: "explain why more than the main experiment")
_w = why_more(a, again=True) if a is not None and verb(a) == 'gain' else None
if _w:
    ne_cev += (' They gain more because the screen deters more: it catches every user, and a household with a SUD cannot '
               'stop using, so the disorder costs it its voucher until it recovers, while in the main transition the '
               'household keeps the voucher by entering treatment and not using. ' + _w[0].upper() + _w[1:] + '.')
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
