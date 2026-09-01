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
SKIP = {'h_3', 'w_bot'}
UNSCORED = {'kappa_ued', 'kappa_uem'}
BAND = {'beta': (3.0, 4.5)}

# parameter -> the moment it is bracketed on. Kept here rather than imported so
# that a broken next_batch.py cannot stop the author seeing where things stand.
OWN = [
    ('discount_factor', 'beta'), ('probability_becoming_unemployed', 'pi_eu'),
    ('smallest_rental_relative_to_lowest_income', 'rent50'),
    ('size_homelessness', 'h_1'), ('newborn_endowment_scale', 'h_share1'),
    ('relative_share_of_housing', 'gamma'), ('max_food_cost', 'cbar'),
    ('relative_share_of_addiction_1', 'theta'), ('kappa_phi_d_level', 'y_u'),
    ('value_of_life', 'aleph'), ('mu_homeless', 'mu_H'),
    ('utility_cost_of_treatment', 'tau_u'), ('kappa_uem', 'lambda_m'),
    ('smi_onset_level', 'p_m'),
    ('probability_of_voucher_benchmark_used', 'pi_V'),
    ('increased_prob_if_homeless', 'emp_homeless'),
    ('lambda_addiction', 'b'), ('addiction_scalar_1', 'lambda_d'),
    ('relative_share_of_leisure', 'omega_l'),
    ('labor_income_tax_rate', 'tau_l'),
    ('sd_permanent_productivity', 'sigma_y'),
    ('smallest_rental_relative_to_lowest_income', 'h_2'),
    ('weight_on_child', 'omega_c'),
]
# moments that are printed and deliberately not scored, with the reason
NOTE = {'h_3': 'conceded, a fact about a grid the model chose',
        'w_bot': 'conceded with the second beta; nothing moves it at one type',
        'omega_c': 'measure_child_gap=0, so nothing measures it'}


def model_hash():
    return hashlib.md5(
        open(os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90'),
             'rb').read()).hexdigest()[:10]


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


def main():
    h, cfg = model_hash(), config()
    best = None
    n = 0
    for f in sorted(glob.glob(os.path.join(HERE, 'points', '*.txt'))):
        if f.endswith('.FAILED.txt'):
            continue
        t = open(f, encoding='utf-8', errors='replace').read()
        if f'MODEL {h}' not in t:
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
        if best is None or worst < best[0]:
            best = (worst, os.path.basename(f)[6:-4], v, m, g)
    if best is None:
        print('no scoreable point in the current economy'); return 1
    worst, tag, v, m, g = best
    med = sorted(g.values())[len(g) // 2]

    mark = os.path.join(HERE, '.gaps_best')
    prev = json.load(open(mark)) if os.path.exists(mark) else {}
    key = f'{h}|{cfg}'
    improved = key not in prev or worst < prev[key]['worst'] - 1e-9
    if improved:
        prev[key] = {'worst': worst, 'tag': tag}
        json.dump(prev, open(mark, 'w'), indent=1)

    head = (f'point_{tag}  MODEL {h}  beta types {cfg}  {n} points in this economy\n'
            f'LOSS (minimax over scored) {100*worst:.1f}%   median {100*med:.1f}%   '
            f'inside ten per cent {sum(1 for x in g.values() if x <= .10)} of {len(g)}')
    if not improved:
        print(f'loss unchanged at {100*prev[key]["worst"]:.1f}% '
              f'(best still point_{prev[key]["tag"]}); table not reprinted.')
        print(head)
        return 0

    print('LOSS IMPROVED -- full table below.\n')
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
    for k in sorted(SKIP):
        if k in m:
            a, tv = m[k]
            rows.append((-2.0, '(no instrument)', '-', k, f'{a:.5f}', f'{tv:.5f}',
                         f'{(a/tv-1)*100:+.1f}%', NOTE.get(k, '')))
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
