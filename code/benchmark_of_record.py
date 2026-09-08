#!/usr/bin/env python3
"""Derive THE benchmark -- one solve, one set of numbers -- from the save run.

    python3 code/benchmark_of_record.py          # newest save log
    python3 code/benchmark_of_record.py <log>

WHY THIS EXISTS. The benchmark used to be two things at once: a POINT written by
run_one_point.sh, and a STATE of fifty-five .dat files written by
run_variant.sh save. Two runs, two solves of the same vector -- and two solves of
one vector are not identical, because the OpenMP reductions do not run in the
same order. Measured on 8 September: net revenue came out 0.545299 in one and
0.545289 in the other, a relative 1.8e-5, right in the band that all 72 moments
showed.

That is small, and that is exactly what makes it dangerous. It is too small to
notice and too large to check against, so no consistency test between the point
and the state can be exact, and any tolerance loose enough to admit it is also
loose enough to admit a state left over from a PREVIOUS MODEL -- which is the
failure that produces confident, wrong counterfactuals.

So the benchmark is one solve. The save run prints the complete moments block
before it writes the state, so the numbers the paper quotes and the numbers the
counterfactual imports come from the same pass over the same distribution. This
extracts the former from the log that produced the latter.
"""
import os, sys, glob, re, hashlib, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "benchmark_of_record.txt")


def main():
    if len(sys.argv) > 1:
        log = sys.argv[1]
    else:
        logs = sorted(glob.glob(os.path.join(HERE, "variant_save_*.log")),
                      key=os.path.getmtime)
        if not logs:
            sys.exit("no variant_save_*.log; run: bash code/run_variant.sh save <vector>")
        log = logs[-1]

    text = open(log, errors="replace").read()

    if "SAVE VARIANT: benchmark state written" not in text:
        sys.exit("%s did not reach the state write; it is not a benchmark"
                 % os.path.basename(log))
    if "END OF MOMENTS" not in text:
        sys.exit("%s has no moments block" % os.path.basename(log))

    head = []
    for line in text.splitlines():
        if line.startswith(("VARIANT ", "SOURCE_MD5 ", "VECTOR ")):
            head.append(line)
        if line.startswith("VECTOR "):
            break

    block, keep = [], False
    for line in text.splitlines():
        if "ALL TARGETED MOMENTS" in line:
            keep = True
        if keep:
            block.append(line)
        if "END OF MOMENTS" in line and keep:
            break

    # WHICH STATE THIS RECORD BELONGS TO. The .dat files are what a
    # counterfactual imports; naming the newest of them and its time is what
    # lets verify_benchmark_state.py refuse a record and a state that did not
    # come from the same run.
    dats = glob.glob(os.path.join(HERE, "*baseline_benchmark.dat"))
    newest = max(dats, key=os.path.getmtime) if dats else None

    with open(OUT, "w") as f:
        f.write("BENCHMARK OF RECORD -- one solve, both the numbers and the state\n")
        f.write("SAVE_LOG %s\n" % os.path.basename(log))
        f.write("SAVE_LOG_MTIME %d\n" % int(os.path.getmtime(log)))
        f.write("STATE_FILES %d\n" % len(dats))
        if newest:
            f.write("STATE_NEWEST %s %d\n"
                    % (os.path.basename(newest), int(os.path.getmtime(newest))))
        for h in head:
            f.write(h + "\n")
        # AGGREGATES THE MOMENTS BLOCK DOES NOT CARRY. The tax row of the
        # experiment table is T(ybar) evaluated at the BENCHMARK's average
        # labour income, and that number is printed by the run but sits above
        # the moments block, so the record would not have it.
        for key in ("average_labor_income_calibrated", "median_income_calibrated",
                    "average_net_wealth_calibrated", "price_of_addictive_good"):
            for line in text.splitlines():
                if line.strip().startswith(key + "="):
                    f.write("AGG %s\n" % line.strip())
                    break
        f.write("\n".join(block) + "\n")

    print("wrote %s" % os.path.relpath(OUT, os.path.dirname(HERE)))
    print("  from %s" % os.path.basename(log))
    print("  %d moment lines, %d state files"
          % (sum(1 for l in block if "MOMENT" in l or "UNTARGETED" in l), len(dats)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
