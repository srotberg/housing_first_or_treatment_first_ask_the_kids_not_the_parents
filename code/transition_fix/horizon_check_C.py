# horizon_check_C.py <loop dir> <run dir> -- remote_tr50_C.sh's horizon check (13 October): how far the last ten years of
# the loop's price and pi_V paths sit from the rule-C terminal values (read from the staged seed's header). A path still
# moving at T means T = 50 is too short.
import sys, re
d, m = sys.argv[1], sys.argv[2]
out = []
for name in ('drug_price', 'pi_v'):
    v = [float(l) for l in open(f'{d}/{name}_path_seed_out.txt') if l.strip() and not l.strip().startswith('#')]
    head = open(f'{m}/{name}_path_seed.txt').readline()
    xT = float(re.search(r'rule-C terminal ([0-9.]+)', head).group(1))
    dev = [abs(x / xT - 1) for x in v[-10:]]
    out.append(f'{name} years {len(v)-9}-{len(v)} within {100*max(dev):.2f}% of the terminal {xT:.6f} '
               f'(year 1 {v[0]:.6f}, year {len(v)-9} {v[-10]:.6f}, year {len(v)} {v[-1]:.6f})')
print('; '.join(out))
