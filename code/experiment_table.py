#!/usr/bin/env python3
"""The per-experiment table the author asked for, benchmark and counterfactuals.

    python3 code/experiment_table.py

Eight rows, on the author's list of 8 September: homelessness rate,
participation rate, SUD rate, CEV of newborns, unemployment rate, change in
average tax paid at benchmark average income, treatment take-up among those
with a SUD, and average age of drug users.

SIX OF THE EIGHT COME OUT OF THE SAME MOMENTS BLOCK IN BOTH COLUMNS, which is
the point of having taught the counterfactual to call print_all_moments. Before
that a counterfactual printed only its own scattered write statements, the age
distribution was not among them, and any comparison had to be assembled by hand
out of two different formats.

THE TAX ROW IS COMPUTED, NOT READ. increase_in_labour_income_tax is NOT a tax
rate: the tax function is the Heathcote-Storesletten-Violante form

    T(y) = max( y - lambda * y**kappa , 0 ),   lambda = labor_income_tax_rate
                                                        + increase_in_labour_income_tax

so that coefficient is the LEVEL OF POST-TAX INCOME and raising it CUTS taxes.
Reporting it, or its change, would give the reader the opposite sign. The row is
T_cf(ybar) - T_bench(ybar) at the BENCHMARK's average labour income, which with
the standard deduction and personal exemption both at zero in this calibration
is just -(lambda_cf - lambda_bench) * ybar**kappa.

CEV IS THE NEWBORN'S. calculate_welfare_gains solves for the consumption scale
x that equates the counterfactual's average welfare of the youngest cohort to
the benchmark's, bracketing on [-1,1]; the loop that calls it runs j=1 only, so
welfare_of_gains_by_addiction(1) is the newborn number and there is no
by-disorder split to confuse it with.

A COUNTERFACTUAL HAS NO TARGET, so this table has no gap column. Levels, and
the difference from the benchmark.
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
KAPPA = 0.85                      # curvature_of_labor_income_taxes
BASE_LAMBDA = None                # read from the vector

MOMENT = re.compile(r"MOMENT\s+(?P<key>\S+)\s+.*?model=\s*(?P<v>[-\d.E+]+)")
UNTARG = re.compile(r"UNTARGETED\s+(?P<name>.*?)\s+model=\s*(?P<v>[-\d.E+]+)")
LOOSE = re.compile(r"^\s*(?P<key>[a-z_0-9]+)\s*[=,]\s*(?P<v>[-\d.E+]+)\s*$")

WANT_MOMENT = {"h_1": "homelessness rate",
               "b": "participation rate",
               "lambda_d": "SUD rate",
               "pi_eu": "unemployment rate",
               "tau_u": "treatment take-up, given a SUD"}
WANT_UNTARG = {"mean age of drug users": "average age of drug users"}
ROWS = ["homelessness rate", "participation rate", "SUD rate",
        "CEV of newborns", "unemployment rate",
        "change in average tax at benchmark income",
        "treatment take-up, given a SUD", "average age of drug users"]


def scrape(path):
    out, loose = {}, {}
    if not os.path.exists(path):
        return None
    for line in open(path, errors="replace"):
        m = MOMENT.search(line)
        if m and m.group("key") in WANT_MOMENT:
            out[WANT_MOMENT[m.group("key")]] = float(m.group("v"))
        m = UNTARG.search(line)
        if m and m.group("name").strip() in WANT_UNTARG:
            out[WANT_UNTARG[m.group("name").strip()]] = float(m.group("v"))
        m = LOOSE.match(line)
        if m:
            loose[m.group("key")] = float(m.group("v"))
        # AGG lines are aggregates benchmark_of_record.py lifts out of the save
        # log because they sit above the moments block: the tax row needs the
        # benchmark's average labour income and the record would not carry it.
        if line.startswith("AGG "):
            m = LOOSE.match(line[4:])
            if m:
                loose[m.group("key")] = float(m.group("v"))
    out["_loose"] = loose
    return out


def lambda_of(path):
    """labor_income_tax_rate from the VECTOR line, plus any increase in the log."""
    base, inc = None, 0.0
    for line in open(path, errors="replace"):
        if line.startswith("VECTOR "):
            m = re.search(r"labor_income_tax_rate=([-\d.eE+]+)", line)
            if m:
                base = float(m.group(1))
        if "increase_in_labour_income_tax=" in line:
            try:
                inc = float(line.split("=")[-1].strip().replace("D", "E"))
            except ValueError:
                pass
    return base, inc


def main():
    rec = os.path.join(HERE, "benchmark_of_record.txt")
    if not os.path.exists(rec):
        sys.exit("no benchmark_of_record.txt; run python3 code/benchmark_of_record.py")
    bench = scrape(rec)
    base_lambda, _ = lambda_of(rec)
    ybar = bench["_loose"].get("average_labor_income_calibrated") \
        or bench["_loose"].get("model_average_income")
    bench["CEV of newborns"] = 0.0
    bench["change in average tax at benchmark income"] = 0.0

    cols = [("benchmark", bench)]
    for name in ("tf_rationed", "universal_hf", "universal_tf"):
        d = scrape(os.path.join(HERE, "p1_%s.log" % name))
        # A LOG THAT EXISTS IS NOT A RUN THAT FINISHED. A counterfactual that
        # is still building or still iterating has a log with no moments block
        # in it, and a column of dashes and a NaN reads like a result.
        if d is None or "homelessness rate" not in d:
            continue
        cev = d["_loose"].get("welfare_of_gains_by_addiction")
        d["CEV of newborns"] = cev if cev is not None else float("nan")
        _, inc = lambda_of(os.path.join(HERE, "p1_%s.log" % name))
        if ybar and base_lambda is not None:
            d["change in average tax at benchmark income"] = -inc * ybar ** KAPPA
        cols.append((name, d))

    if len(cols) == 1:
        print("only the benchmark is in; no counterfactual has finished yet.")
    w = max(len(r) for r in ROWS) + 2
    print("PHASE 1, long-run equilibria. Levels; a counterfactual has no target.")
    if ybar:
        print("benchmark average labour income = %.5f, tax curvature = %.2f" % (ybar, KAPPA))
    print()
    print("%-*s" % (w, "") + "".join("%16s" % n for n, _ in cols))
    print("-" * (w + 16 * len(cols)))
    for r in ROWS:
        line = "%-*s" % (w, r)
        for _, d in cols:
            v = d.get(r)
            line += "%16s" % ("--" if v is None else "%.5f" % v)
        print(line)
    if len(cols) > 1:
        print()
        print("differences from the benchmark")
        print("-" * (w + 16 * len(cols)))
        for r in ROWS:
            line = "%-*s" % (w, r)
            for n, d in cols:
                if n == "benchmark":
                    line += "%16s" % ""
                    continue
                v, b = d.get(r), bench.get(r)
                line += "%16s" % ("--" if v is None or b is None else "%+.5f" % (v - b))
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
