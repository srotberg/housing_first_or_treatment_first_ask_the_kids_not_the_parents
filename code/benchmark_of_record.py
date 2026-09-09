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

    # THE LAST MOMENTS BLOCK, NOT THE FIRST.
    #
    # A save run now prints TWO. The first is the sweep's own, before the frozen
    # equilibrium converges; the second is after it. They are not close --- on
    # the 9 September run the first said b = 0.0775588 and the second
    # b = 0.0864386, eleven per cent apart --- and the .dat state written at the
    # end belongs to the SECOND. Taking the first put a record and a state from
    # two different economies into the same file, which is the exact failure the
    # save-at-the-sweep-stop design existed to prevent.
    #
    # Collect every block and keep the last.
    blocks, block, keep = [], [], False
    for line in text.splitlines():
        if "ALL TARGETED MOMENTS" in line:
            keep, block = True, []
        if keep:
            block.append(line)
        if "END OF MOMENTS" in line and keep:
            blocks.append(block)
            keep = False
    if not blocks:
        sys.exit("%s has no complete moments block" % os.path.basename(log))
    block = blocks[-1]
    if len(blocks) > 1:
        print("  %d moments blocks in the log; took the last "
              "(after the frozen equilibrium converged)" % len(blocks))

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
            # The LAST occurrence, for the same reason the block is the last:
            # these are printed before and after the frozen passes.
            hit = None
            for line in text.splitlines():
                if line.strip().startswith(key + "="):
                    hit = line.strip()
            if hit:
                f.write("AGG %s\n" % hit)
        f.write("\n".join(block) + "\n")

    print("wrote %s" % os.path.relpath(OUT, os.path.dirname(HERE)))
    print("  from %s" % os.path.basename(log))
    print("  %d moment lines, %d state files"
          % (sum(1 for l in block if "MOMENT" in l or "UNTARGETED" in l), len(dats)))
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ---------------------------------------------------------------------------
# THE COUNTERFACTUAL-ONLY PARAMETERS GO STALE IN THE VECTOR, SILENTLY.
#
# probability_of_detection, probability_of_false_positive and cost_per_drug_test
# do nothing in the benchmark -- voucher_conditional_on_clean is zero there, so
# nothing is tested. CLAUDE.md says as much: a parameter that only binds in a
# counterfactual is not a calibration parameter.
#
# But they ride in the VECTOR line anyway, and the VECTOR is regenerated from a
# run that echoes the vector it was handed. So a value set once perpetuates
# itself forever, and its handover BEATS both the Fortran declaration and
# run_one_point.sh's defaults. On 9 September the author set the rates to 0.95
# and 0.005; both places were changed; and every arm still ran at 0.9 and 0.05
# because the record's vector overrode them. The universal Treatment First arm
# reached 43 per cent of eligibles against Housing First's 85, and the welfare
# ordering that came out of it was the thing that exposed the bug.
#
# This does not fix the vector -- an arm must still pass the rates explicitly --
# it makes the disagreement impossible to miss.
def warn_stale_counterfactual_params(vector_line, fortran_path):
    import re as _re
    src = open(fortran_path, errors="replace").read()
    for name in ("probability_of_detection", "probability_of_false_positive",
                 "cost_per_drug_test"):
        m = _re.search(r"^\s*real\(8\)\s*::\s*" + name + r"\s*=\s*([0-9.eEdD+-]+)",
                       src, _re.M)
        v = _re.search(r"(?:^| )" + name + r"=([0-9.eEdD+-]+)", vector_line)
        if not m or not v:
            continue
        decl = float(m.group(1).lower().replace("d", "e").rstrip("e") or 0)
        vec = float(v.group(1).lower().replace("d", "e"))
        if abs(decl - vec) > 1e-12 * max(abs(decl), 1.0):
            print("  STALE IN VECTOR: %s is %g in the vector but %g in the "
                  "declaration. The vector WINS via the handover -- pass it "
                  "explicitly on any counterfactual that should use %g."
                  % (name, vec, decl, decl))
