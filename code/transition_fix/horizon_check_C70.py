# horizon_check_C70.py <loop dir> <run dir> -- horizon_check_C.py for remote_tr70_Cu.sh (16 October): how far the last ten
# years of the loop's price and pi_V paths (years 60-69 at T = 70) sit from the terminal values. horizon_check_C.py read
# the terminal from the seed's header and failed on the T = 50 run's loop 3 ("AttributeError: 'NoneType' object has no
# attribute 'group'"): the relaunch had overwritten the seed with the last saved path, whose header has no terminal.
# Here the terminal comes from terminal_values.txt (written at seeding by extend_seeds_C70.py), else from the staged
# copy's or the seed's header, and the check says which it could not find rather than raising.
import os, re, sys
d, m = sys.argv[1], sys.argv[2]
term = {}
if os.path.exists(f'{m}/terminal_values.txt'):
    term = {k: float(v) for k, v in (l.split() for l in open(f'{m}/terminal_values.txt') if l.strip())}
out = []
for name in ('drug_price', 'pi_v'):
    v = [float(l) for l in open(f'{d}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    xT = term.get(name)
    for p in (f'{m}/{name}_path_seed.staged.txt', f'{m}/{name}_path_seed.txt'):
        if xT is None and os.path.exists(p):
            h = re.search(r'rule-C terminal ([0-9.]+)', open(p).read())
            if h:
                xT = float(h.group(1))
            elif p.endswith('staged.txt'):
                flat = [float(l) for l in open(p) if l.strip() and not l.strip().startswith('#')]
                if flat and max(flat) - min(flat) < 1e-15:
                    xT = flat[0]
    if xT is None:
        out.append(f'{name}: NO TERMINAL FOUND in {m}')
        continue
    dev = [abs(x / xT - 1) for x in v[-10:]]
    out.append(f'{name} years {len(v)-9}-{len(v)} within {100*max(dev):.2f}% of the terminal {xT:.6f} '
               f'(year 1 {v[0]:.6f}, year {len(v)-9} {v[-10]:.6f}, year {len(v)} {v[-1]:.6f})')
print('; '.join(out))
