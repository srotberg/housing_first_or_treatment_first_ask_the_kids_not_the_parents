#!/usr/bin/env python3
"""Validate a PARAM_HANDOVER file against the Fortran's own case keys.

A handover name the parser does not recognise is SILENTLY IGNORED: the run keeps
the compiled default and nothing in the log says so above the noise floor.  That
cost several runs on 14 September, when `smallest_rental` was seeded instead of
`smallest_rental_relative_to_lowest_income` and every run built on it was a
different economy from the one intended.

The check itself has already been got wrong once, in the obvious way: a character
class of [a-z0-9_] silently drops every key with a capital in it -- zeta_DI is the
one in this file -- so a real key reads as unknown and, far worse, an unknown key
that happens to contain a capital reads as fine.  The class below is [A-Za-z0-9_]
and the count of parser keys is printed so a sudden drop is visible.

Usage:  python3 code/check_handover.py <handover file> [fortran source]
Exit 1 if any seeded name is not a parser key.
"""
import re
import sys

FORTRAN = "code/housing_first_or_treatment_first_SR_v1.f90"


def parser_keys(path):
    src = open(path, errors="ignore").read()
    return set(re.findall(r'case \("([A-Za-z0-9_]+)"\)', src))


def seeded_names(path):
    names = []
    for line in open(path, errors="ignore"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.append(line.split()[0])
    return names


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    handover = sys.argv[1]
    fortran = sys.argv[2] if len(sys.argv) > 2 else FORTRAN

    keys = parser_keys(fortran)
    names = seeded_names(handover)
    unknown = [n for n in names if n not in keys]

    print(f"{len(names)} names seeded, {len(keys)} case keys in {fortran}")
    dupes = {n for n in names if names.count(n) > 1}
    if dupes:
        print("REPEATED, the last one wins: " + ", ".join(sorted(dupes)))
    if unknown:
        print("\nSILENTLY IGNORED by the parser, the run keeps the default:")
        for n in unknown:
            close = [k for k in keys if k.startswith(n) or n.startswith(k)]
            print(f"  {n}" + (f"   did you mean: {', '.join(sorted(close))}" if close else ""))
        return 1
    print("every seeded name is a parser key")
    return 0


if __name__ == "__main__":
    sys.exit(main())
