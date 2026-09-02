#!/usr/bin/env python3
"""The full gap table, printed when the loss improves.

The author, 1 September: "I want you to show me the full gaps table each time
the loss function improves." So this is not a report anyone has to remember to
run -- ENGINE.md calls it every firing, it decides for itself whether the loss
moved, and it prints the whole table when it did and one line when it did not.

THE LOSS IS THE AUTHOR'S OWN, not a convenient summary. A MINIMAX over the
scored moments -- "once we get below 10% for everything we can stop" -- with
beta scoring zero anywhere inside its 3.0-4.5 band. The median is printed
beside it because the two moved in opposite directions more than once today
and reporting only one of them hides that, but the median is never the
criterion.

The high-water mark lives in .gaps_best so it survives a container.
"""
import glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
_MAP = {}
_OK = set()
SKIP = {'h_3'}
# rent50 is REPORTED, NOT SCORED. The cheapest rung is bracketed on h_2, the
# headcount above half of total SPENDING, on the author's instruction that gamma
# and the cost burden share a denominator. rent50 is the same headcount over
# INCOME and pointed the OPPOSITE way -- +163 per cent against h_2's -38 -- so
# scoring both left one parameter with two targets it could not satisfy at once.
UNSCORED = {'kappa_ued', 'kappa_uem', 'rent50', 'h_2'}
BAND = {'beta': (3.0, 4.5)}

# parameter -> the moment it is bracketed on. Kept here rather than imported so
# that a broken next_batch.py cannot stop the author seeing where things stand.
OWN = [
    ('discount_factor', 'beta'),
    ('discount_factor_impatient', 'w_bot'), ('probability_becoming_unemployed', 'pi_eu'),
    ('size_homelessness', 'h_1'), ('newborn_endowment_scale', 'h_share1'),
    ('relative_share_of_housing', 'gamma'), ('max_food_cost', 'cbar'),
    ('relative_share_of_addiction_1', 'theta'),     ('value_of_life', 'aleph'), ('mu_homeless', 'mu_H'),
    ('utility_cost_of_treatment', 'tau_u'), ('kappa_uem', 'lambda_m'),
    ('probability_of_voucher_benchmark_used', 'pi_V'),
    # increased_prob_if_homeless is EXOGENOUS at 0.2 on the author's
    # instruction -- twenty per cent each way -- so it owns nothing. The
    # cheapest rung owns emp_homeless instead; see next_batch.py for why.
    ('smallest_rental_relative_to_lowest_income', 'emp_homeless'),
    ('lambda_addiction', 'b'), ('addiction_scalar_1', 'lambda_d'),
    ('relative_share_of_leisure', 'omega_l'),
    ('labor_income_tax_rate', 'tau_l'),
    ('sd_permanent_productivity', 'sigma_y'),
    ('smi_onset_level', 'p_m'),
    # BOTH ADDED ON THE AUTHOR'S INSTRUCTION AND BOTH MISSED HERE. next_batch
    # gained them and gaps.py did not, which is the third time these two files
    # have drifted apart on the scored set in one evening -- rent50, then h_2,
    # now these. The cross-check at the top is what caught it each time.
    ('multiple_of_probabilities_of_employment_if_addicted', 'sud_homeless'),
    ('weight_on_child', 'omega_c'),
]


def _cross_check():
    """Warn if this file's scored set has drifted from next_batch.py's.

    It had. h_2 was in next_batch's OWN and missing from the list above, so the
    author's table showed twenty-one moments where the search was working
    twenty-two, and the omitted one was sitting at minus twenty-seven per cent.
    It did not bind, so nothing looked wrong. The same class of divergence over
    rent50 made the printed loss read 162.8 against a true 100.1 earlier the
    same day, which is why this is checked rather than remembered.

    Deliberately a warning and not an import: the whole reason OWN is duplicated
    here is that a broken next_batch.py must not stop the author seeing where
    things stand.
    """
    try:
        sys.path.insert(0, HERE)
        import next_batch as _nb
    except Exception:
        return
    # next_batch keeps b and lambda_d OUT of OWN because the drug block is
    # bracketed by the gate rather than by a single arm, so they must be added
    # back before comparing or the check cries wolf about two moments both files
    # score. omega_c used to be dropped from both sides here, on the ground that
    # measure_child_gap=0 meant nothing measured it. That stopped being true when
    # the author put omega_c in round 5 and the flag became settable, so the
    # exclusion was itself masking a divergence -- the check reported one and hid
    # the other. Both sides now compare the full set.
    mine = {m for _, m in OWN} - SKIP - UNSCORED
    theirs = (set(_nb.OWN.values()) | set(_nb.GATE)) - _nb.SKIP - _nb.UNSCORED
    if mine != theirs:
        for m in sorted(theirs - mine):
            print(f'WARNING: next_batch.py scores {m} and gaps.py does not.')
        for m in sorted(mine - theirs):
            print(f'WARNING: gaps.py scores {m} and next_batch.py does not.')
        print('The loss below is over gaps.py\'s set. Reconcile the two files.\n')
# moments that are printed and deliberately not scored, with the reason
NOTE = {'h_3': 'conceded, a fact about a grid the model chose',
        'h_2': 'OUT OF THE LOSS: the rung targets emp_homeless on the author\'s decision',
        'omega_c': 'round 5 only; measured when measure_child_gap=1 is handed in',
        'rent50': 'reported, not scored: same headcount over income, opposite sign',
        'y_u': 'mortality pinned at 8 by the author; goes to a robustness run'}


import model_hash as _mh   # semantic identity: comments do not change the model


def model_hash():
    return _mh.current()


def config():
    """The economy, not just the source: run_one_point.sh's own default."""
    m = re.search(r'\[number_of_beta_types\]=(\d+)',
                  open(os.path.join(HERE, 'run_one_point.sh')).read())
    return m.group(1) if m else None


def load(path):
    t = open(path, encoding='utf-8', errors='replace').read()
    mv = re.search(r'^VECTOR (.*)$', t, re.M)
    if not mv:
        return None, None
    v = dict(kv.split('=', 1) for kv in mv.group(1).split())
    m = {k: (float(a), float(b)) for k, a, b in re.findall(
        r'MOMENT (\S+)\s+(?:.*?)model=\s*([0-9.eE+-]+)\s+target=\s*([0-9.eE+-]+)', t)}
    if 'gamma' in m and abs(m['gamma'][1] - 0.268) > 1e-9:
        r = re.search(r'DIAG aggregate housing / aggregate expenditure\s+=\s*([0-9.eE+-]+)', t)
        if r:
            m['gamma'] = (float(r.group(1)), 0.268)
    for pat, key, tv in (
            (r'UNTARGETED share of the homeless, band\s+1\s+model=\s*([0-9.eE+-]+)', 'h_share1', 0.26),
            (r'UNTARGETED employed share of the homeless\s+model=\s*([0-9.eE+-]+)', 'emp_homeless', 0.46),
            (r'UNTARGETED renters above 50 pct of income\s+model=\s*([0-9.eE+-]+)', 'rent50', 0.175)):
        r = re.search(pat, t)
        if r:
            m[key] = (float(r.group(1)), tv)
    return v, m


def gap(k, pair):
    mo, tv = pair
    if k in BAND:
        lo, hi = BAND[k]
        return 0.0 if lo <= mo <= hi else min(abs(mo - lo) / lo, abs(mo - hi) / hi)
    return abs(mo - tv) / abs(tv) if tv else float('nan')


# Two worst gaps within EPS are a TIE and the comparison moves to the next
# moment. See the note at the improvement test for what a strict comparison did.
EPS = 0.01


def _better_vec(new_v, old_v):
    for a, b in zip(new_v, old_v):
        if abs(a - b) > EPS:
            return a < b
    return len(new_v) < len(old_v)


def main():
    _cross_check()
    global _MAP, _OK
    _MAP = _mh.build_map()
    h, cfg = model_hash(), config()
    # BEHAVIOUR-PRESERVING PREDECESSORS, READ FROM next_batch.py AND KEYED ON THE
    # CURRENT HASH -- never a literal.
    #
    # This was a literal set unioned unconditionally with the current hash, and
    # on 1 September the model changed and it kept admitting the old points and
    # printing them under the NEW hash: "MODEL 0e0abddab7, 33 points in this
    # economy", when not one of the 281 points in the archive had run that
    # source. next_batch.py, keying its lookup on the current hash, correctly
    # said "no archive" in the same minute. The two disagreed about whether an
    # entire archive existed.
    #
    # That is an equivalence ASSERTED rather than measured, which is the one
    # thing ENGINE.md says this mechanism must never be used for, and it asserted
    # it silently at the moment the model had just changed underneath it.
    #
    # The fallback is {h} alone, not a remembered list: when next_batch cannot be
    # imported the honest answer is "only points on this exact source count",
    # which under-counts rather than over-claims.
    try:
        sys.path.insert(0, HERE)
        import next_batch as _nb
        _OK = {h} | set(_nb.EQUIVALENT_MODELS.get(h, set()))
    except Exception:
        _OK = {h}
    best = None
    n = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        t = open(f, encoding='utf-8', errors='replace').read()
        mm = re.search(r'^MODEL (\S+)', t, re.M)
        if not mm or _mh.resolve(mm.group(1), _MAP) not in _OK:
            continue
        v, m = load(f)
        if v is None or (cfg and v.get('number_of_beta_types', cfg) != cfg):
            continue
        n += 1
        g = {k: gap(k, m[k]) for k in m
             if k not in SKIP and k not in UNSCORED and m[k][1]}
        if not g:
            continue
        worst = max(g.values())
        # THE SAME TIE TOLERANCE HAS TO APPLY HERE, and this is the line that
        # matters: `worst < best[0]` is how the best point is CHOSEN, and it is
        # what promoted a point whose drug block had collapsed to -96.3 per cent
        # over one at +8.7, on a tenth of a point of emp_homeless. Fixing only
        # the improvement test left the wrong point selected and merely stopped
        # announcing it.
        vv = sorted(g.values(), reverse=True)
        if best is None or _better_vec(vv, best[5]):
            best = (worst, os.path.basename(f)[6:-4], v, m, g, vv)
    if best is None:
        print('no scoreable point in the current economy'); return 1
    worst, tag, v, m, g, _bv = best
    med = sorted(g.values())[len(g) // 2]

    mark = os.path.join(HERE, '.gaps_best')
    prev = json.load(open(mark)) if os.path.exists(mark) else {}
    # THE HIGH-WATER MARK IS KEYED ON THE SCORED SET, NOT JUST THE MODEL.
    #
    # Removing p_m on the author's instruction took the scored set from 21
    # moments to 20, and the stored gap vector still had 21 entries. Python
    # compares lists elementwise and then by LENGTH, so the shorter vector won
    # and gaps.py announced "PROGRESS" for a round in which nothing had moved --
    # the loss was 100.1 per cent before and after. A comparison across two
    # different sets of moments is not a comparison at all.
    #
    # The set's signature goes in the key, so changing what is scored starts a
    # fresh mark instead of silently beating the old one.
    key = f'{h}|{cfg}|{",".join(sorted(g))}'

    # PROGRESS IS LEXICOGRAPHIC, NOT JUST THE MINIMAX.
    #
    # The author asked to see the table whenever the loss improves, and then, an
    # hour later, "I want to see progress" -- because they had not seen one. The
    # reason is that a plain minimax cannot show progress while its binding
    # moment is stuck: emp_homeless sat at +100.1 per cent all evening, so the
    # worst gap never fell, so the table never printed, while fourteen other
    # moments were free to move in either direction unseen.
    #
    # The criterion is still theirs -- the number reported as the LOSS is the
    # minimax, and the stopping rule is still every scored moment inside ten per
    # cent. This only changes when the table is SHOWN: the gap vector sorted
    # worst-first is compared lexicographically, so a round that leaves the worst
    # moment where it is and improves the second worst counts as progress and
    # prints. That is the standard refinement of a minimax and it cannot call
    # something progress that the minimax would call a regression.
    # THE MINIMAX NEEDS A TIE TOLERANCE OR IT WILL TRADE EVERYTHING FOR NOTHING.
    #
    # Strict lexicographic on the sorted gap vector compares element 0 first and
    # stops the moment it differs. On 2 September that promoted point_2cb1dfff73
    # over point_a6ff37446f because its worst gap was 100.0 per cent against
    # 100.1 -- a tenth of a point on emp_homeless, which no instrument can reach
    # anyway -- while b went from +8.7 per cent to -96.3, h_1 from -63 to -97.7,
    # h_share1 from -27 to -95.8, the median from 26.7 to 59.5 and the count
    # inside ten per cent from six to three. The drug block was destroyed and the
    # tool called it PROGRESS.
    #
    # That is correct lexicographic behaviour and useless as a search criterion,
    # because the binding moment is one nothing can move: any point may buy the
    # top slot with a rounding-sized gain and pay for it anywhere it likes.
    #
    # So two worst gaps within EPS of each other are a TIE and the comparison
    # moves to the next element. The author's stopping rule is untouched -- it is
    # still every scored moment inside ten per cent -- and so is the reported
    # LOSS. This changes only which point is called best while the search runs.
    _better = _better_vec
    vec = sorted(g.values(), reverse=True)
    old = prev.get(key, {}).get('vec')
    improved = old is None or _better(vec, [float(x) for x in old])
    if improved:
        prev[key] = {'worst': worst, 'tag': tag, 'vec': vec}
        json.dump(prev, open(mark, 'w'), indent=1)

    head = (f'point_{tag}  MODEL {h}  beta types {cfg}  {n} points in this economy\n'
            f'LOSS (minimax over scored) {100*worst:.1f}%   median {100*med:.1f}%   '
            f'inside ten per cent {sum(1 for x in g.values() if x <= .10)} of {len(g)}')
    # --force PRINTS THE TABLE REGARDLESS. The gate above exists so that the
    # hourly firing does not spam an unchanged table at the author, and that is
    # the right default. But the author asks for the table directly -- "can you
    # show me the gaps table" -- more often than the loss improves, and working
    # around the gate by hand each time is how a hand-computed table that
    # disagreed with the loss got shown once already.
    if not improved and '--force' not in sys.argv:
        print(f'no lexicographic progress; best still point_{prev[key]["tag"]} '
              f'at {100*prev[key]["worst"]:.1f}%. Table not reprinted.')
        print(head)
        return 0

    # A FIRST POINT IS NOT PROGRESS. The mark is keyed on the model, the beta
    # configuration and the scored set, so any of those changing starts a fresh
    # mark and the first point after it beats nothing. That printed "PROGRESS"
    # when p_m left the scored set, again when the second beta type came back,
    # and would print it after every model change -- three times in one evening,
    # each time announcing an improvement that had not happened.
    first = old is None
    print('FIRST POINT in this economy -- nothing to compare against yet.\n' if first
          else 'PROGRESS -- full table below.\n' if improved
          else 'loss unchanged; table printed on request.\n')
    print(head + '\n')
    rows = []
    for p, mo in OWN:
        val = v.get(p, '-')
        if mo in m:
            a, tv = m[mo]
            # A BANDED MOMENT IS NOT MISSING ITS TARGET BY THE DISTANCE TO ONE
            # EDGE. beta scores zero anywhere in 3.0-4.5, so printing it against
            # 3.0 said "+106.9%" for a value the loss was charging 50.9 for, and
            # the two numbers disagreeing in the same row is exactly the kind of
            # thing that gets read as the loss being broken.
            if mo in BAND:
                lo, hi = BAND[mo]
                tgt = f'{lo:g}-{hi:g}'
                gp = 'in band' if lo <= a <= hi else f'{100*gap(mo, m[mo]):+.1f}% out'
            else:
                tgt, gp = f'{tv:.5f}', f'{(a/tv-1)*100:+.1f}%'
            rows.append((g.get(mo, -1.0), p, val, mo, f'{a:.5f}', tgt, gp,
                         NOTE.get(mo, '')))
        else:
            rows.append((-2.0, p, val, mo, 'not measured', '-', '-', NOTE.get(mo, '')))
    # EVERY MEASURED MOMENT GETS A ROW, not only the owned ones and the conceded
    # ones. h_2 fell out of the table entirely the moment the cheapest rung was
    # reassigned to emp_homeless: it was no longer in OWN, and it is not in SKIP
    # because the author reversed its concession, so it matched neither loop and
    # printed nowhere -- while still being SCORED and still sitting at minus
    # twenty-seven per cent. A moment that counts against the loss and appears in
    # no row is the worst thing this table can do.
    shown = {mo for _, mo in OWN}
    for k in sorted(set(m) - shown):
        a, tv = m[k]
        note = NOTE.get(k, '')
        if k not in SKIP and k not in UNSCORED and not note:
            note = 'SCORED but no parameter brackets on it'
        rows.append((-2.0, '(no instrument)', '-', k, f'{a:.5f}', f'{tv:.5f}',
                     f'{(a/tv-1)*100:+.1f}%', note))
    rows.sort(reverse=True)
    print(f'{"parameter":42}{"value":>12}  {"moment":12}{"model":>12}{"target":>12}{"gap":>9}')
    for s, p, val, mo, a, tv, gp, note in rows:
        star = ' *' if 0 <= s <= .10 else '  '
        print(f'{p:42}{str(val):>12}  {mo:12}{a:>12}{tv:>12}{gp:>9}{star}'
              + (f'  {note}' if note else ''))
    print('\n* inside ten per cent. kappa_ued and kappa_uem are outputs on the '
          "author's instruction, not targets.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
