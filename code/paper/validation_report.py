#!/usr/bin/env python3
"""Read a point file and print the validation table: model, data, gap.

WHY THIS IS SEPARATE FROM calibration_report.py. That one reads a SUPERVISOR
LOG and reports the targeted moments, which is what the search needs. This
reads a POINT FILE and reports the untargeted ones, which is what the note's
validation section needs, and the two have never overlapped: the validation
table has carried a data value and a source per row and nothing from the model
beside them.

    python3 code/paper/validation_report.py code/points/point_XXXXXXXXXX.txt

A row the point file does not carry is printed as missing rather than dropped,
because a table that silently loses a row reads as a table the model passed.
"""
import re
import sys

# The order the note's table lists them in, so the two can be read side by side.
ORDER = [
    "homelessness rate, band",
    "homelessness profile, band",
    "share of the homeless, band",
    "earnings share, bottom tenth",
    "earnings share, top tenth",
    "net worth share, bottom half",
    "wealth share bottom",
    "income share bottom",
    "renters above 30 pct of income",
    "renters above 50 pct of income",
    "tenant contribution rate",
    "voucher holders, wages main",
    "income with a SUD",
    "income of drug users",
    "participation, with a SUD",
    "participation, without a SUD",
    "homeless at treatment admission",
    "SMI alongside SUD at admission",
    "working, homeless in treatment",
    "SUD share of the homeless",
    "drug deaths, share of deaths",
    "price elasticity, participation",
    "price elasticity, intensive",
    "delta_h child homelessness ratio",
    "delta_d child SUD ratio",
]

ROW = re.compile(
    r"UNTARGETED\s+(?P<name>.*?)\s+model=\s*(?P<model>[-\d.E+]+)\s+observed=\s*(?P<obs>[-\d.E+]+)"
)
# The banded rows carry their index between the label and "model=".
BAND = re.compile(
    r"UNTARGETED\s+(?P<name>.*?),\s+band\s+(?P<band>\d+)\s+model=\s*(?P<model>[-\d.E+]+)"
    r"\s+observed=\s*(?P<obs>[-\d.E+]+)"
)
SKIP = re.compile(r"(ELASTICITY|VALIDATION) (SKIPPED|HELD|NOT COMPUTED)(?P<why>.*)")


def rows_of(path):
    found, notes = [], []
    for line in open(path):
        m = BAND.search(line)
        if m:
            found.append(("%s %s" % (m.group("name"), m.group("band")),
                          float(m.group("model")), float(m.group("obs"))))
            continue
        m = ROW.search(line)
        if m:
            found.append((m.group("name").strip(),
                          float(m.group("model")), float(m.group("obs"))))
            continue
        m = SKIP.search(line)
        if m:
            notes.append(line.strip())
    return found, notes


def gap(model, obs):
    if obs == 0:
        return None
    return 100.0 * (model - obs) / abs(obs)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = sys.argv[1]
    found, notes = rows_of(path)
    if not found:
        sys.exit("no UNTARGETED rows in %s; was it measured before the "
                 "validation column existed?" % path)

    width = max(len(n) for n, _, _ in found)
    print("validation moments at %s" % path)
    print()
    print("%-*s %12s %12s %9s" % (width, "moment", "model", "data", "gap"))
    print("-" * (width + 36))

    def key(item):
        for i, k in enumerate(ORDER):
            if item[0].startswith(k):
                return (i, item[0])
        return (len(ORDER), item[0])

    for name, model, obs in sorted(found, key=key):
        g = gap(model, obs)
        print("%-*s %12.5f %12.5f %8s" % (
            width, name, model, obs,
            "--" if g is None else "%+.1f%%" % g))

    if notes:
        print()
        for n in notes:
            print("  " + n)


if __name__ == "__main__":
    main()
