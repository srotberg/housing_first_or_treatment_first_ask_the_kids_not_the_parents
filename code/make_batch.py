#!/usr/bin/env python3
"""Build a run_one_point batch from a FULL vector plus named overrides.

WHY THIS EXISTS. On 6 September four batches in a row -- batch_h2_down,
batch_frontier, batch_iph_off -- silently dropped addiction_onset_base. Each was
built by parsing a previous batch or point file into a dict and merging a small
"anchor" dict on top; where the anchor came from a vector that had already lost
the key, the loss was inherited and compounded. run_one_point.sh defaults that
parameter to ZERO by design, so the onset hazard became identically zero, no
household ever acquired the disorder, lambda_d/kappa_ued/mu_H/tau_u all read
exactly 0.0000, using became costless and b ran to 0.92.

The defect was the generator, not the value. This module makes the failure
impossible: it starts from a full source vector, applies ONLY named overrides,
and REFUSES to emit a line that has fewer parameters than its source.
"""
import re, sys

def read_vector(path):
    """Full parameter dict from a point file's VECTOR line or a batch line."""
    t = open(path, errors='ignore').read()
    m = re.search(r'^VECTOR (.*)$', t, re.M)
    # split(' ', 2) keeps EVERYTHING after 'bash code/run_one_point.sh'.
    # It was split(' ', 3) for one revision, which silently dropped the FIRST
    # parameter -- the same class of bug this module exists to prevent, in the
    # module itself. The count assertions below are what caught it.
    src = m.group(1) if m else t.splitlines()[0].split(' ', 2)[-1]
    d = {}
    for tok in src.split():
        if '=' in tok and not tok.startswith('bash') and not tok.endswith('.sh'):
            k, v = tok.split('=', 1)
            if re.fullmatch(r'[a-z_0-9]+', k):
                d[k] = v
    if not d:
        raise SystemExit(f'no parameters parsed from {path}')
    return d

def build(base, overrides):
    """Apply overrides, refusing to lose a key or invent one."""
    unknown = set(overrides) - set(base)
    if unknown:
        raise SystemExit(f'override names not in the source vector: {sorted(unknown)}\n'
                         f'  (a typo here would silently take run_one_point.sh\'s default)')
    out = dict(base)
    out.update(overrides)
    missing = set(base) - set(out)
    if missing:
        raise SystemExit(f'INTERNAL: dropped {sorted(missing)}')
    assert len(out) == len(base), (len(out), len(base))
    return out

def line(vec):
    return 'bash code/run_one_point.sh ' + ' '.join(f'{k}={v}' for k, v in sorted(vec.items()))

def write(path, base, override_list):
    lines = []
    for ov in override_list:
        v = build(base, ov)
        lines.append(line(v))
    for l in lines:
        n = len([t for t in l.split() if '=' in t])
        assert n == len(base), f'line carries {n} parameters, source had {len(base)}'
    open(path, 'w').write('\n'.join(lines) + '\n')
    return len(lines), len(base)
