# shift_seeds_ann.py <run dir> <lag> <price x0> <pi_V x0> [<main loop dir>] -- the seeds of remote_tr70_CAann.sh (19 October;
# lag 0 for its grace mode, whose screen is on from year 1: the main path unshifted).
# The announced reform is the main no-escape reform started <lag> years later, so its seed is the main path shifted:
#   x(t) = x0 for t <= lag (Housing First's price and pi_V: the screen is off), x(t) = x_main(t - lag) after,
# the main path's last <lag> years dropped (they sit at the terminal). The main path is the main run's latest archived
# loop when one is given (results/transition_2c_t70_CAc or _CA20e, or the held-price loop 0 of _CAb), rescaled onto this
# run's terminal as rescale_seeds_CA70.py rescales rule C's, x0 + (x - x0) (xT - x0) / (x_main(69) - x0); else the seed
# rescale_seeds_CA70.py has just written in <run dir>. xT, this run's terminal, is read from that seed's header ('CA
# terminal'), which this file's header carries on for horizon_check_CA.py. Only the price and pi_V seeds are replaced.
import re, sys
n, lag, p0, v0 = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
main = sys.argv[5] if len(sys.argv) > 5 else None
for name, x0 in (('drug_price', p0), ('pi_v', v0)):
    path = f'{n}/{name}_path_seed.txt'
    head = open(path).readline()
    xT = float(re.search(r'CA terminal ([0-9.]+)', head).group(1))
    a = [float(l) for l in open(path) if l.strip() and not l.strip().startswith('#')]
    src = 'rescale_seeds_CA70.py\'s rule-C path'
    if main:
        b = [float(l) for l in open(f'{main}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
        assert len(b) == 69, (name, len(b))
        k = (xT - x0) / (b[-1] - x0) if abs(b[-1] - x0) > 1e-4 else 1.0
        assert 0.5 < k < 2, (name, k, 'the main run ends far from this terminal')
        a = [x0 + (x - x0) * k for x in b]
        src = f'{main}, factor {k:.4f}'
    m = len(a)
    assert m == 69 and abs(a[-1] - xT) < 1e-6 * max(1, abs(xT)), (name, m, a[-1], xT)
    vals = [x0] * lag + a[:m - lag]
    if name == 'pi_v':
        assert all(1e-5 < v < 1 for v in vals), 'pi_V seed on a bound'
    else:
        assert min(vals) > 0, 'drug price seed not positive'
    with open(path, 'w') as f:
        f.write(f' # {name} path: the announced reform, Housing First for t <= {lag}, then the main path ({src}) '
                f'shifted {lag} years: x0 {x0:.9f}, CA terminal {xT:.12f}\n # periods 1 to {m}\n')
        f.writelines(f'{x:25.15f}\n' for x in vals)
    pick = sorted({t for t in (1, lag, lag + 1, lag + 2, 10, 25, 49, m) if t >= 1})
    print(f'{name}: ' + ', '.join(f't={t} {vals[t-1]:.6f}' for t in pick))
