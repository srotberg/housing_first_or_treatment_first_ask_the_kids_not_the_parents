# reseed_path.py <run dir> <old loop dir> <first> <last> [<step>] [<taper>] -- BETTER SEEDS ALONG THE WHOLE PATH (20 October;
# the author: "restart the 20% run"). reseed_implied.py's rule over any stretch of periods, not only the announcement's
# first ones. The 0.20 exemption run's loop 0 (results/transition_2c_t70_CAgrace20) left the drug market 0.4 to 3.9 per
# cent off in periods 1-30 and 0.5 to 2.2 per cent after, the price above the implied supply price almost everywhere; the
# transition moves each period's price at most 0.5 per cent a loop, about a day a loop, so its own loops need a week.
# Here the old run's latest pass gives the new seeds: pi_V is its updated path (the binary's own rule); the drug price,
# the price the pass FACED, moves <step> (default 0.6) of the way to the implied supply price printed before each
# 'TRANSITION DRUG t=' line, in periods <first> to <last>. Not all the way, for reseed_implied.py's reason: as the price
# moves, demand moves with it and so does the price that clears the market (0.6-0.7 of the way). The step tapers linearly
# to zero over the last <taper> periods before 69 (default 9), so the path still ends on the terminal arm, whose own gap
# (0.5 per cent at 0.20) the path must end on. The header keeps 'CA terminal <x>' from the staged seed, which
# horizon_check_CA.py reads. A NEW FILE: reseed_implied.py, which the re-seeded announced runs ran, is untouched.
import gzip, re, sys
n, old, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
step = float(sys.argv[5]) if len(sys.argv) > 5 else 0.6
taper = int(sys.argv[6]) if len(sys.argv) > 6 else 9
assert 0 < step <= 1 and 1 <= first <= last <= 69 and 0 <= taper < 69


def seed(path):
    return [float(l) for l in open(path) if l.strip() and not l.strip().startswith('#')]


def weight(t):
    """the share of the step period t takes: the whole step, falling linearly to zero at period 69"""
    if t < first or t > last:
        return 0.0
    return step if taper == 0 or t <= 69 - taper else step * (69 - t) / taper


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
assert all(t in imp for t in range(first, last + 1)), ('no implied price for some periods', first, last, sorted(imp)[:8])
for name in ('drug_price', 'pi_v'):
    head = open(f'{n}/{name}_path_seed.txt').readline()
    xT = re.search(r'CA terminal ([0-9.]+)', head).group(1)
    v = seed(f'{old}/{name}_path_seed_out.txt')
    assert len(v) == 69, (name, len(v))
    if name == 'drug_price':
        before = v[:]
        v = [x + weight(t + 1) * (imp[t + 1] - x) if first <= t + 1 <= last else x for t, x in enumerate(v)]
        show = [t for t in (1, 2, 3, 4, 5, 6, 10, 15, 20, 30, 45, 60, 65, 69) if first <= t <= last]
        print(f'drug price, periods {first}-{last}, step {step}, taper {taper}: ' +
              ', '.join(f't{t} {before[t - 1]:.4f} -> {v[t - 1]:.4f} (implied {imp[t]:.4f})' for t in show))
        moved = [abs(a / b - 1) for a, b in zip(v, before)]
        print(f'drug price: largest move {100 * max(moved):.2f} per cent (period {moved.index(max(moved)) + 1})')
    assert min(v) > 0 and (name != 'pi_v' or max(v) < 1)
    with open(f'{n}/{name}_path_seed.txt', 'w') as f:
        f.write(f' # {name} path: re-seeded from {old} (its updated path; the drug price in periods {first}-{last} moved '
                f'{step} of the way to the implied supply price, tapering to zero over the last {taper} periods), '
                f'CA terminal {xT}\n # periods 1 to 69\n')
        f.writelines(f'{x:25.15f}\n' for x in v)
    print(f'{name}: t=1 {v[0]:.6f}, t=5 {v[4]:.6f}, t=6 {v[5]:.6f}, t=69 {v[-1]:.6f}')
