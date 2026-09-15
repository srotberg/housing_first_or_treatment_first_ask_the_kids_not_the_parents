#!/usr/bin/env python3
"""Say where each value in a built seed CAME FROM: the log, or the base file.

WHY THIS EXISTS. On 15 September a kappa = 1.9 seed was built carrying
`kappa_phi_d_level 2.4`, for a run whose own handover line reads `8.0 -> 1.9`.
It was caught by eye on a four-line spot check, and nothing else would have
caught it.

The extractor takes the LAST value a log prints for each name and falls back to
the base file when the log never prints it. 49 of the 75 names in a seed are
never printed AT ALL -- every pinned or held parameter. For those the base is not
a fallback, it IS the answer, so building a seed on another run's base silently
imports that run's pinned parameters.

This turns the silent fallback into a visible one. It does not guess which base
is right; it says which names the log confirms and which are inherited on trust,
so the inherited list can be read against what the run actually pinned.
"""
import io, re, sys, signal

# Write the whole report even when the reader is `head`; a BrokenPipeError here
# would look like a failed check rather than a closed pipe.
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

NUM = r'[-+]?[0-9]*\.?[0-9]+(?:[eEdD][-+]?[0-9]+)?'

def main():
    if len(sys.argv) < 3:
        sys.exit("usage: seed_provenance.py <seed> <log> [handover-line-check]")
    seed, log = sys.argv[1], sys.argv[2]
    names = [l.split() for l in io.open(seed) if len(l.split()) == 2]
    txt = io.open(log, errors='replace').read()

    measured, inherited = [], []
    for name, val in names:
        if re.findall(r'(?m)^[ \t]*' + re.escape(name) + r'=[ \t]*(' + NUM + r')', txt):
            measured.append((name, val))
        else:
            inherited.append((name, val))

    print("%d names: %d confirmed by the log, %d INHERITED from the base"
          % (len(names), len(measured), len(inherited)))

    # A HANDOVER line is the run's own record of what it was started with, and it
    # is printed for names the loop never prints again -- so it can contradict an
    # inherited value. That contradiction is the bug this file was written for.
    bad = 0
    for name, val in inherited:
        m = re.findall(r'(?m)^[ \t]*HANDOVER ' + re.escape(name) + r':.*?->[ \t]*(' + NUM + r')', txt)
        if m:
            handed = float(m[-1].replace('D', 'E').replace('d', 'e'))
            if abs(handed - float(val)) > 1e-9 * max(1.0, abs(handed)):
                print("  MISMATCH %s: seed says %s, the run was handed %.10g" % (name, val, handed))
                bad += 1
    if bad:
        print("%d inherited value(s) CONTRADICT the run's own handover -- the base is wrong" % bad)
        return 1
    print("no inherited value contradicts a handover line")
    if inherited:
        print("inherited on trust from the base (log never prints these):")
        for name, _ in inherited:
            print("    " + name)
    return 0

if __name__ == '__main__':
    sys.exit(main())
