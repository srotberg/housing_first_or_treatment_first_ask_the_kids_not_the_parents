#!/usr/bin/env python3
"""Build the handover that resumes a calibration WITHOUT losing its progress.

THERE ARE TWO WAYS TO RESUME WRONG AND BOTH WERE DONE ON 23 SEPTEMBER.

1. NO HANDOVER AT ALL. The reader CONSUMES PARAM_HANDOVER.txt at startup, so a
   finished run directory has none and `./hftf` alone looks like a resume.
   calibration_state.dat banks 108 names; a handover supplies about 100 and
   MOST OF THOSE ARE NOT BANKED, so they revert to their Fortran declarations.
   addiction_onset_base is declared 0.d0, and with lambda_addiction pinned the
   onset hazard is min(base + (1-exp(-0*q)),1), so a zero base means NOBODY
   EVER DEVELOPS A DISORDER. Measured: b = 0.952, lambda_d = 0.000.

2. THE FULL STAGING HANDOVER. The handover is applied AFTER the state and
   OVERRIDES it, so copying the original file resets every CALIBRATED
   parameter back to where the run started. Measured: addiction_scalar_1 went
   from its reached 5.5336E-3 back to the declared 4.9192E-3, discarding ten
   blocks, in a block whose moments looked entirely healthy.

THE CORRECT HANDOVER IS NEITHER, and this script builds it:

    for each name in the reference handover
        if the name is NOT banked        -> emit it, at its REACHED value if
                                            the log has one, else staging
        elif the log HAS a reached value -> emit it, repairing the state
        else                             -> OMIT it, so the state keeps it

Usage:
    python3 code/build_resume_handover.py <run_dir> -o out.txt \
        --omega-c 0 --loop joint

--omega-c and --loop are REQUIRED, not optional. The reference handover is
oc00's, which is a FROZEN run at omega_c = 0, so both switches come through
wrong for anything else and a silent inheritance is exactly the failure this
script exists to prevent.

It reads every log in <run_dir> (run.log and any run.log.* archives), newest
last, so the most recent reached value wins.
"""

import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')
REFERENCE = os.path.join(HERE, 'oc00', 'PARAM_HANDOVER.relaunch.txt')

# The state writer's block. Bounds are checked against the open() and the
# rename() rather than hard-coded blindly.
def banked_names():
    src = open(SRC, errors='ignore').read().splitlines()
    lo = hi = None
    for i, ln in enumerate(src):
        if 'file="calibration_state.tmp"' in ln:
            lo = i
        if lo is not None and 'calibration_state.tmp' in ln and 'rename' in ln:
            hi = i
            break
    if lo is None or hi is None:
        sys.exit('REFUSING: could not locate the state writer block; '
                 'the file has moved and the bounds must be re-found.')
    pat = re.compile(r"write\(71,'[^']*'\)\s*([A-Za-z_0-9]+)")
    names = set()
    for ln in src[lo:hi]:
        m = pat.search(ln)
        if m:
            names.add(m.group(1))
    if len(names) < 50:
        sys.exit('REFUSING: only %d banked names found, expected ~108. '
                 'The parse is wrong.' % len(names))
    return names


def reached_values(logs):
    """The last value the loop printed for each parameter it moves."""
    pat = re.compile(r'^ ([a-z_0-9]+)=\s+([-+0-9.EDed]+)')
    got = {}
    for path in logs:
        try:
            for ln in open(path, errors='ignore'):
                m = pat.match(ln)
                if m:
                    got[m.group(1)] = m.group(2)
        except IOError:
            pass
    return got


def main(argv):
    for flag in ('-o', '--omega-c', '--loop'):
        if flag not in argv:
            sys.exit(__doc__)
    out = argv[argv.index('-o') + 1]
    omega = argv[argv.index('--omega-c') + 1]
    loop = argv[argv.index('--loop') + 1]
    if loop not in ('joint', 'frozen'):
        sys.exit('REFUSING: --loop must be joint or frozen, not %r.' % loop)
    freeze = '0' if loop == 'joint' else '1'
    rundir = argv[1]

    logs = []
    for f in sorted(os.listdir(rundir)):
        if f == 'run.log' or f.startswith('run.log.'):
            logs.append(os.path.join(rundir, f))
    # run.log last so the newest values win
    logs.sort(key=lambda p: (os.path.basename(p) == 'run.log',
                             os.path.getmtime(p)))
    if not logs:
        sys.exit('REFUSING: no logs in %s, so no reached values to read.' % rundir)

    banked = banked_names()
    reached = reached_values(logs)

    lines, repaired, omitted, unbanked_n = [], [], [], 0
    for ln in open(REFERENCE):
        p = ln.split()
        if len(p) < 2:
            continue
        name, staging = p[0], p[1]
        if name not in banked:
            unbanked_n += 1
            lines.append('%s %s' % (name, reached.get(name, staging)))
        elif name in reached:
            lines.append('%s %s' % (name, reached[name]))
            repaired.append(name)
        else:
            omitted.append(name)

    # THE SWITCHES ARE SET HERE, NOT INHERITED. Whatever the reference said,
    # and whatever the log's reached values were, these three are what the
    # caller asked for.
    lines = [l for l in lines
             if l.split()[0] not in ('weight_on_child', 'omega_c_is_pinned',
                                     'freeze_all_but_omega_c')]
    lines.append('weight_on_child %s' % omega)
    lines.append('omega_c_is_pinned 1')
    lines.append('freeze_all_but_omega_c %s' % freeze)

    # A zero onset base is the collapse, so refuse rather than write it.
    ob = [l for l in lines if l.startswith('addiction_onset_base ')]
    if not ob:
        sys.exit('REFUSING: no addiction_onset_base line; a resume without it '
                 'runs the declared 0.d0 and NOBODY DEVELOPS A DISORDER.')
    if float(ob[0].split()[1].replace('D', 'E').replace('d', 'e')) <= 0:
        sys.exit('REFUSING: addiction_onset_base is zero or negative.')

    open(out, 'w').write('\n'.join(lines) + '\n')
    print('logs read, oldest first: %s' % ', '.join(os.path.basename(p) for p in logs))
    print('banked names in the state writer: %d' % len(banked))
    print('written: %d lines  (%d unbanked, %d banked repaired from the log)'
          % (len(lines), unbanked_n, len(repaired)))
    print('omitted so the state keeps them: %s' % (', '.join(omitted) or 'none'))
    print()
    print('switches SET (not inherited): omega_c=%s, loop=%s' % (omega, loop))
    for k in ('addiction_onset_base', 'addiction_scalar_1', 'weight_on_child',
              'freeze_all_but_omega_c', 'omega_c_is_pinned'):
        v = [l for l in lines if l.startswith(k + ' ')]
        print('  %-24s %s' % (k, v[0].split(None, 1)[1] if v else '(omitted -- state keeps it)'))


if __name__ == '__main__':
    main(sys.argv)
