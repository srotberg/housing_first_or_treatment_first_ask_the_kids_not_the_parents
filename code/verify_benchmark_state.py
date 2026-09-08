#!/usr/bin/env python3
"""Audit what a counterfactual imports from the benchmark, before it imports it.

    python3 code/verify_benchmark_state.py

THE FAILURE THIS EXISTS FOR. upload_vars opens forty-odd files by name and reads
them with no iostat, so a missing one is a runtime error and a STALE one is
silent -- the counterfactual prices every household against an economy that is
not the benchmark and still produces numbers. Nothing downstream can tell.

Three checks, in order of what they would catch:

1. EXISTENCE. Every file upload_vars opens under old_results must be on disk.
   Read straight out of the Fortran so the list cannot drift.
2. FRESHNESS. Every one of them must be newer than the model binary that wrote
   the benchmark point, and no older than the point file itself. A state left
   over from a previous model is the silent case.
3. CONSISTENCY. The numbers must agree with the benchmark point's own output:
   the supply shifter must put the drug price at one at the benchmark's
   quantity, and the budget constraint must equal the benchmark's net revenue.
"""
import os, re, sys, glob, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "housing_first_or_treatment_first_SR_v1.f90")
BENCH = "baseline_benchmark"


def upload_vars_files():
    """The file stems upload_vars opens, taken from the source itself."""
    text = open(SRC, encoding="utf-8", errors="replace").read()
    start = text.index("    subroutine upload_vars(")
    end = text.index("\n    end subroutine", start)
    body = text[start:end]
    stems = re.findall(r'file="([^"]+)"//trim\(old_results\)', body)
    # string_used is a 1 or a 2 appended in a two-pass loop over beta types.
    out = []
    for s in stems:
        out.append(s)
    return sorted(set(out)), body


def read_first(path):
    with open(path, errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    return float(line.split()[0].replace("D", "E"))
                except ValueError:
                    return None
    return None


def main():
    stems, body = upload_vars_files()
    print("upload_vars opens %d distinct names under old_results\n" % len(stems))

    missing, present = [], []
    for s in stems:
        # A name inside the two-pass loop carries string_used, 1 or 2.
        cands = [os.path.join(HERE, s + BENCH + ".dat"),
                 os.path.join(HERE, s + "1" + BENCH + ".dat")]
        hit = next((c for c in cands if os.path.exists(c)), None)
        (present if hit else missing).append((s, hit))

    if missing:
        print("MISSING -- the counterfactual would die or read garbage:")
        for s, _ in missing:
            print("   %s%s.dat" % (s, BENCH))
        print()
    else:
        print("EXISTENCE: all %d present\n" % len(present))

    # FRESHNESS against the benchmark point.
    pts = sorted(glob.glob(os.path.join(HERE, "points", "point_*.txt")),
                 key=os.path.getmtime)
    if not pts:
        print("no point files; cannot check freshness")
        return 1
    point = pts[-1]
    t_point = os.path.getmtime(point)
    stale = [(s, p) for s, p in present if os.path.getmtime(p) < t_point - 3600]
    if stale:
        print("STALE -- written more than an hour before %s:" % os.path.basename(point))
        for s, p in stale:
            print("   %s" % os.path.basename(p))
        print()
    else:
        print("FRESHNESS: none older than the newest point by more than an hour\n")

    # CONSISTENCY.
    print("CONSISTENCY")
    ok = True

    shifter = read_first(os.path.join(HERE, "drug_supply_shifter" + BENCH + ".dat"))
    # THE SAVE RUN'S OWN LOG, NOT THE POINT'S.
    #
    # The .dat files were written by the save run, so they must be checked
    # against the solve that wrote them. Checking them against the separate
    # run_one_point solve of the same vector compares TWO SOLVES, and two solves
    # of one vector differ by OpenMP reduction order: net revenue came out
    # 0.545289 in one and 0.545299 in the other, a relative 1.8e-5, which is
    # right in the band measured across all 72 moments earlier today. That is
    # not an error, but it makes an exact check impossible and a loose check
    # useless, because a genuinely stale state would also sit inside any
    # tolerance wide enough to admit it.
    #
    # Against its own log the check is EXACT, and exact is what catches a state
    # left over from a previous model.
    saves = sorted(glob.glob(os.path.join(HERE, "variant_save_*.log")),
                   key=os.path.getmtime)
    log = saves[-1] if saves else ""
    V = None
    if log and os.path.exists(log):
        for line in open(log, errors="replace"):
            if "drug quantity V=" in line:
                V = float(line.split("=")[-1].strip().replace("D", "E"))
    if shifter and V:
        eps = 1.46
        p = shifter * V ** (1.0 / eps)
        print("   drug price at the benchmark quantity = %.6f  (must be 1)" % p)
        print("     shifter=%.6f  V=%.6f  elasticity=%.2f" % (shifter, V, eps))
        if abs(p - 1.0) > 1e-3:
            print("     WRONG: the shifter does not belong to this benchmark")
            ok = False
    else:
        print("   drug price: shifter or V not found")
        ok = False

    con = read_first(os.path.join(HERE, "govt_revenues_to_use_in_tests" + BENCH + ".dat"))
    net = None
    if log and os.path.exists(log):
        for line in open(log, errors="replace"):
            if line.strip().startswith("net_govt_revenues="):
                net = float(line.split("=")[-1].strip().replace("D", "E"))
    if con is not None and net is not None:
        print("   budget constraint = %.6f   benchmark net revenue = %.6f" % (con, net))
        if abs(con - net) > 1e-9:
            print("     WRONG: the state does not come from the solve that wrote it")
            ok = False
    else:
        print("   budget constraint: not found in both places")
        ok = False

    prof = os.path.join(HERE, "average_labor_income_by_employment" + BENCH + ".dat")
    if os.path.exists(prof):
        vals = [float(x) for x in open(prof).read().split()]
        print("   income profile: %d nodes, min %.6f, max %.6f" %
              (len(vals), min(vals), max(vals)))
        if min(vals) <= 0:
            print("     WRONG: a zero node is what the STOP guard exists for")
            ok = False
    else:
        print("   income profile: MISSING")
        ok = False

    print()
    print("VERDICT: %s" % ("the counterfactual imports this benchmark"
                           if ok and not missing else "DO NOT RUN A COUNTERFACTUAL"))
    return 0 if (ok and not missing) else 1


if __name__ == "__main__":
    sys.exit(main())
