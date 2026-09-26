"""Statistics of a counterfactual run's LAST complete pass, for the result tables.

usage: python3 finalstats.py <cf.log or cf.log.gz> [<cf.log of the no-policy run>]

A pass ends at its `distance_govt_budget=` line; within it the last printed
value of each quantity is taken. With a second log, each line also shows the
no-policy run's value and the change, and the welfare split is given the way
code/CALIBRATION_STATE.md (25 September) did it: childhood utility, and the
adult part as welfare_with_childhood minus childhood, both in utils against
the no-policy run.
"""
import gzip, sys

KEYS = [  # (label, line prefix, field index after the '=' split, scale)
    ("drug price", "price_of_addictive_good=", 0),
    ("pi_V (voucher probability)", "probability_of_voucher=", 0),
    ("drug use b", "CF MOMENTS distance=", "b"),
    ("SUD lambda_d", "CF MOMENTS distance=", "lambda_d"),
    ("homelessness h_1", "CF MOMENTS distance=", "h_1"),
    ("share of households holding a voucher", "model_fraction_recieving_housing_vouchers=", 0),
    ("eligibles getting a voucher", "model_eligibles_getting_voucher=", 0),
    ("treatment take-up", "model_treatment_take_up,", 0),
    ("SUD share of the homeless", "model_fraction_homeless_and_addicted=", 0),
    ("SMI share of the homeless", "SMI share of homeless=", 0),
    ("employed share of the homeless", "employed share of homeless=", 0),
    ("voucher spending", "BUDGET food_stamps=", "vouchers_2"),
    ("food stamps", "BUDGET food_stamps=", "food_stamps"),
    ("drug-test cost", "BUDGET drug_tests=", "drug_tests"),
    ("net government revenue", "net_govt_revenues=", 0),
    ("welfare (with childhood)", "average_welfare_with_childhood=", 0),
    ("childhood utility", "average_childhood_utility=", 0),
]


def value(line, prefix, field):
    rest = line.split(prefix, 1)[1]
    if isinstance(field, int):
        return float(rest.replace(",", " ").split()[field])
    toks = (prefix + rest).replace("=", "= ").split()
    for i, t in enumerate(toks):
        if t == field + "=":
            return float(toks[i + 1])
    raise KeyError(field)


def last_pass(path):
    op = gzip.open if path.endswith(".gz") else open
    lines = op(path, "rt", errors="replace").read().splitlines()
    ends = [i for i, l in enumerate(lines) if l.strip().startswith("distance_govt_budget=")]
    assert ends, "no complete pass in " + path
    start = ends[-2] + 1 if len(ends) > 1 else 0
    seg = lines[start:ends[-1] + 1]
    out = {}
    for label, prefix, field in KEYS:
        for l in seg:
            if prefix in l:
                try:
                    out[label] = value(l, prefix, field)
                except (KeyError, ValueError, IndexError):
                    pass
    return out, len(ends)


run, npass = last_pass(sys.argv[1])
base = last_pass(sys.argv[2])[0] if len(sys.argv) > 2 else None
print(f"last complete pass: {npass}")
for label, _, _ in KEYS:
    v = run.get(label)
    if v is None:
        print(f"  {label:40s} not printed")
        continue
    if base and label in base and base[label] != 0:
        b = base[label]
        print(f"  {label:40s} {v:14.8g}   no policy {b:14.8g}   change {100*(v/b-1):+7.2f}%")
    else:
        print(f"  {label:40s} {v:14.8g}")
if base:
    wc, bc = run["childhood utility"], base["childhood utility"]
    wa = run["welfare (with childhood)"] - wc
    ba = base["welfare (with childhood)"] - bc
    print(f"  welfare split against no policy (utils; 1% CEV is about 0.33): "
          f"childhood {wc-bc:+.4f}, adult part {wa-ba:+.4f}, total {wc-bc+wa-ba:+.4f}")
