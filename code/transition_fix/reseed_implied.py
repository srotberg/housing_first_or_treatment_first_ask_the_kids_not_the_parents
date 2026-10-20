# reseed_implied.py <run dir> <old loop dir> <lag> [<step>] -- BETTER SEEDS FOR THE ANNOUNCED RUNS (20 October; the
# author: "you can start the runs with better guesses"). The announced runs' first pass (remote_tr70_CAann.sh) seeded
# periods 1 to <lag> at Housing First's drug price, and households cut their use as soon as the screen was announced:
# at 1.00 the supply price their demand implies is 0.78-0.82 against the seeded 0.994. The transition moves each
# period's price at most 0.5 per cent a loop, so it could not close that gap in the loops it has.
# Here the old run's latest pass gives the new seeds: pi_V is its updated path (the binary's own rule); the drug price
# is its updated path too, except in periods 1 to <lag>, where it moves <step> (default 0.6) of the way to the implied
# supply price ('implied supply price=' before each 'TRANSITION DRUG t=' line of the pass). Not all the way: as the price
# falls, demand rises and so does the price that clears the market (with the supply elasticity 1.46 and a demand
# elasticity between 0.5 and 1 the clearing price is 0.84-0.87 at 1.00, about 0.6-0.7 of the way). Not after period
# <lag>: there the main path's seeds already sat near clearing, and in the last periods the gap is the held terminal
# arm's own (at 1.00 its implied supply price is 0.72 against the held 0.8017), which the path must end on.
# The header keeps 'CA terminal <x>' from the staged seed, which horizon_check_CA.py reads.
import gzip, re, sys
n, old, lag = sys.argv[1], sys.argv[2], int(sys.argv[3])
step = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
assert 0 < step <= 1 and 1 <= lag <= 20


def seed(path):
    return [float(l) for l in open(path) if l.strip() and not l.strip().startswith('#')]


L = gzip.open(f'{old}/run.log.gz', 'rt', errors='replace').read().splitlines()
start = max(i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l)
imp, cur = {}, None
for l in L[start:]:
    m = re.search(r'implied supply price=\s*(\S+)', l)
    if m:
        cur = float(m.group(1)); continue
    m = re.search(r'TRANSITION DRUG t=\s*(\d+)\s+distance=', l)
    if m and cur is not None:
        imp[int(m.group(1))] = cur; cur = None
assert all(t in imp for t in range(1, lag + 1)), ('no implied price for the first periods', sorted(imp)[:8])
for name in ('drug_price', 'pi_v'):
    head = open(f'{n}/{name}_path_seed.txt').readline()
    xT = re.search(r'CA terminal ([0-9.]+)', head).group(1)
    v = seed(f'{old}/{name}_path_seed_out.txt')
    assert len(v) == 69, (name, len(v))
    if name == 'drug_price':
        before = v[:lag]
        v = [x + step * (imp[t + 1] - x) if t < lag else x for t, x in enumerate(v)]
        print(f'drug price, periods 1-{lag}: ' + ', '.join(f'{b:.4f} -> {a:.4f} (implied {imp[t + 1]:.4f})'
                                                            for t, (b, a) in enumerate(zip(before, v[:lag]))))
    assert min(v) > 0 and (name != 'pi_v' or max(v) < 1)
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: re-seeded from {old} (its updated path; the drug price in periods 1-{lag} moved {step} '
                f'of the way to the implied supply price), CA terminal {xT}\n # periods 1 to 69\n')
        f.writelines(f'{x:25.15f}\n' for x in v)
    print(f'{name}: t=1 {v[0]:.6f}, t={lag} {v[lag - 1]:.6f}, t={lag + 1} {v[lag]:.6f}, t=69 {v[-1]:.6f}')
