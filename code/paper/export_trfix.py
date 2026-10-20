"""export_trfix.py -- HOW MANY WITH A SUD LOSE WHEN THE PRICES ARE HELD (20 October, round r365; the author on "67 percent
of those who have one when the reform lands are worse off": "well, you need to report how many of them lose when the pv
and piv are constant!", "you may have to simulate this transition, because this is the correct comparison", "that
transition only needs one iteration").

The main transition (rule C, detection 0.20, T = 70) with the drug price and pi_V held at Housing First's values along
the whole path and at the end (results/transition_2c_t70_Cfix, code/transition_fix/remote_tr70_Cfix.sh): one backward
and one forward pass, since nothing clears. x_trfix_sud_worse_pc is the share of households with a SUD alive at the
reform who are worse off, from the forward pass's 'TRANSITION BETTER OFF TOL t= 1' line at the 1e-3 tolerance -- the
same line and field (worse_sud) transition_series.py reads for the main transition's x_trf_alive_sud_worse_pc. Until
the run has archived its loop the name prints a yellow dash. Run after export_alttrans.py."""
import gzip, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from trpaths import latest_loop  # noqa: E402
OUT = os.path.join(HERE, 'results_numbers.json')
RUN = os.path.join(ROOT, 'results', 'transition_2c_t70_Cfix')


def worse_sud(log):
    """worse_sud at t = 1 in the latest forward pass of a log, or None"""
    L = gzip.open(log, 'rt', errors='replace').read().splitlines()
    start = max([i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [0])
    for l in L[start:]:
        if re.match(r'\s*TRANSITION BETTER OFF TOL t=\s*1\s', l):
            return float(re.search(r'worse_sud=\s*(\S+)', l).group(1))
    return None


loop = latest_loop(RUN)
w = worse_sud(os.path.join(loop, 'run.log.gz')) if loop else None
d = json.load(open(OUT))
d['x_trfix_sud_worse_pc'] = f'{100 * w:.0f}' if w is not None else '\\mbox{\\tocheck{--}}'
json.dump(d, open(OUT, 'w'), indent=1, sort_keys=True)
print('export_trfix:', os.path.relpath(loop, ROOT) if loop else 'no archived loop yet', '->', d['x_trfix_sud_worse_pc'])
