#!/usr/bin/env python3
"""Build a vector file from the LAST value the calibration log prints for each
parameter it moved.

WHY NOT calibration_state.dat. run_variant.sh deletes it at the head of every
run -- that is what "cold" means in the standing rule -- and read_calibration_state
runs BEFORE apply_param_handover in any case, so a handover names the value that
wins. The measurement run therefore needs the numbers IN ITS VECTOR, not in a
state file, and a vector file is also the thing that can be committed and read
back later. The log is the record; this turns it into one.

WHY THE LAST OCCURRENCE. Every update block prints its parameter twice, before
and after the step, and once per loop. The last print in the file is the value
the last completed loop left behind, which is the state the measurement has to
reproduce.

IT ONLY EVER WRITES NAMES THE BASE VECTOR ALREADY CARRIES. A name the log prints
that run_one_point.sh does not accept would be rejected by run_variant.sh
anyway, and silently dropping it here would hide which parameters moved.
"""
import io, os, re, sys

BASE = sys.argv[1] if len(sys.argv) > 1 else 'code/step3_vector.txt'
LOG = sys.argv[2]
OUT = sys.argv[3] if len(sys.argv) > 3 else 'code/step3_fitted_vector.txt'

base = dict(t.split('=', 1) for t in io.open(BASE).read().split())
txt = io.open(LOG, errors='replace').read()

NUM = r'([-+]?[0-9]*\.?[0-9]+(?:[eEdD][-+]?[0-9]+)?)'
moved, missing = {}, []
for name in sorted(base):
    hits = re.findall(r'^\s*' + re.escape(name) + r'=\s*' + NUM, txt, re.M)
    if not hits:
        missing.append(name)
        continue
    v = hits[-1].replace('D', 'E').replace('d', 'e')
    if abs(float(v) - float(base[name])) > 1e-12:
        moved[name] = v
    base[name] = v

io.open(OUT, 'w').write(' '.join(f'{k}={base[k]}' for k in sorted(base)) + '\n')
print(f'{len(base)} parameters -> {OUT}')
print(f'{len(moved)} moved from the starting vector:')
for k, v in sorted(moved.items()):
    print(f'   {k:52s} {v}')
print(f'\n{len(missing)} never printed by the log (left at the starting value); '
      f'most are switches the calibration does not touch')
