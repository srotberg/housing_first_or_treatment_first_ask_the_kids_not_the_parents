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
# The order the note's table lists them in, so the two can be read side by side.
#
# TRIMMED 8 September on the author's instruction. What went, and why it is a
# DROP rather than a deletion: every one of these is still printed by the model
# and still lands in the point file, so nothing is lost and any of them can come
# back by adding a line here.
#
#   housing over income, renters      asked to be removed
#   voucher holders, wages main       asked to be removed
#   participation, with a SUD         "just average income of users and those
#   participation, without a SUD       with SUD" -- the two income rows stay
#   SMI alongside SUD at admission    asked to be removed
#   working, homeless in treatment    asked to be removed
#   SUD share of the homeless         asked to be removed
#   homelessness rate, band           "just keep shares"
#   homelessness profile, band        "just keep shares"
#
# The two earnings shares move INTO the income block rather than standing in a
# section of their own, on the author's instruction, because they are the same
# kind of object as the bottom shares: a slice of a distribution.
ORDER = [
    # NOT "share of the homeless, band": the BAND regex strips the word when
    # it builds the row name, so the old entry matched nothing and the age
    # bands sorted to the BOTTOM of the table instead of the top.
    "share of the homeless",
    "earnings share, bottom tenth",
    "earnings share, top tenth",
    "income share bottom",
    "net worth share, bottom half",
    "wealth share bottom",
    "assets of the homeless",
    "renters above 30 pct of income",
    "renters above 50 pct of income",
    "tenant contribution rate",
    "income of drug users",
    "income with a SUD",
    "homeless at treatment admission",
    "drug deaths, share of deaths",
    "mean age of drug users",
    "users aged",
    "price elasticity, participation",
    "price elasticity, intensive",
    "delta_h child homeless odds ratio",
    "delta_d child SUD odds ratio",
]

# Printed by the model and deliberately not shown. Kept by name so the drop is
# auditable and reversible rather than silent.
DROPPED = [
    "housing over income, renters",
    "voucher holders, wages main",
    "participation, with a SUD",
    "participation, without a SUD",
    "SMI alongside SUD at admission",
    "working, homeless in treatment",
    "SUD share of the homeless",
    "over half of income, all renters",
    "homelessness rate",
    "homelessness profile",
]

# y_u IS A MOMENT LINE, NOT AN UNTARGETED ONE, which is why "income of drug
# users" was silently absent from this table until 8 September. It is a
# calibration target, so it prints as "MOMENT y_u ... target=" rather than
# "UNTARGETED ... observed=", and a reader asking for the average income of a
# user would have found no row at all rather than a wrong one.
MOMENT_ROWS = {"y_u": "income of drug users"}
MOMENT = re.compile(
    r"MOMENT\s+(?P<key>\S+)\s+.*?model=\s*(?P<model>[-\d.E+]+)\s+target=\s*(?P<obs>[-\d.E+]+)"
)

ROW = re.compile(
    r"UNTARGETED\s+(?P<name>.*?)\s+model=\s*(?P<model>[-\d.E+]+)\s+observed=\s*(?P<obs>[-\d.E+]+)"
)
# The banded rows carry their index between the label and "model=".
BAND = re.compile(
    r"UNTARGETED\s+(?P<name>.*?),\s+band\s+(?P<band>\d+)\s+model=\s*(?P<model>[-\d.E+]+)"
    r"\s+observed=\s*(?P<obs>[-\d.E+]+)"
)
SKIP = re.compile(r"(ELASTICITY|VALIDATION) (SKIPPED|HELD|NOT COMPUTED)(?P<why>.*)")

# MODEL ONLY ROWS. The author, 8 September: *"i also want to add the average
# assets of the homeless (not sure if there is data on it, but i just want to
# see it)"*. There is no observed counterpart, so the row carries a dash in the
# data and gap columns rather than a zero, which would read as a target of zero
# and a gap against it.
#
# The quantity is already computed and already printed -- model_avg_homeless_assets
# reaches the point file as a DIAG line -- so nothing in the Fortran changes.
DIAG_ROWS = {"average assets of the homeless": "assets of the homeless"}
DIAG = re.compile(r"DIAG\s+(?P<name>.*?)\s+=\s*(?P<model>[-\d.E+]+)")


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
        m = MOMENT.search(line)
        if m and m.group("key") in MOMENT_ROWS:
            found.append((MOMENT_ROWS[m.group("key")],
                          float(m.group("model")), float(m.group("obs"))))
            continue
        m = DIAG.search(line)
        if m and m.group("name").strip() in DIAG_ROWS:
            found.append((DIAG_ROWS[m.group("name").strip()],
                          float(m.group("model")), None))
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

    # Drop what the author asked not to see. Filtered HERE rather than never
    # printed by the model, so the point file stays complete and a row comes
    # back by editing one list.
    hidden = [n for n, _, _ in found if any(n.startswith(d) for d in DROPPED)]
    found = [r for r in found if not any(r[0].startswith(d) for d in DROPPED)]

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
        if obs is None:
            print("%-*s %12.5f %12s %8s" % (width, name, model, "no data", "--"))
            continue
        g = gap(model, obs)
        print("%-*s %12.5f %12.5f %8s" % (
            width, name, model, obs,
            "--" if g is None else "%+.1f%%" % g))

    if hidden:
        print()
        print("  not shown, still measured and still in the point file: %s"
              % ", ".join(sorted(set(hidden))))

    if notes:
        print()
        for n in notes:
            print("  " + n)


if __name__ == "__main__":
    main()
