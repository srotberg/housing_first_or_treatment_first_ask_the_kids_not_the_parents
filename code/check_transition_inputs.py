#!/usr/bin/env python3
"""check_transition_inputs.py [run_dir]

Every file the TRANSITION opens for reading must exist before it starts.

WHY THIS EXISTS. The binary DELETES PARAM_HANDOVER.txt as it starts, so a run
that dies on a missing input has already eaten its seed, and a naive restart
runs the Fortran's declared values -- b near 0.95, lambda_d at zero -- while
looking perfectly healthy. That failure has happened twice: once on the two
CSVs, once on the four 596 MB benchmark files. A transition loop is ~80-90
minutes, so finding it at minute one is worth a script.

THE LIST IS DERIVED FROM THE SOURCE, NEVER TYPED. It is parsed out of every
open(...action='read') whose name is built from benchmark_simulation,
long_run_simulation or old_results, with line continuations joined first --
upload_functions writes its opens across two lines and a single-line regex
silently misses every policy function it reads.
"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "housing_first_or_treatment_first_SR_v1.f90")
RUN  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "trans_bench_to_tf")

# set_files_names with is_counterfactual=1: old_results and benchmark_simulation
# are the initial steady state, long_run_simulation is the reform's own arm.
NAMES = {"benchmark_simulation": "baseline_benchmark",
         "old_results":          "baseline_benchmark",
         "long_run_simulation":  "counter_TF"}

raw = open(SRC, encoding="utf-8", errors="surrogateescape").read().split("\n")

# join Fortran continuations, dropping comment-only lines first
joined, buf = [], ""
for line in raw:
    st = line.strip()
    if st.startswith("!"):
        continue
    buf += st
    if buf.endswith("&"):
        buf = buf[:-1]
        continue
    joined.append(buf)
    buf = ""
if buf:
    joined.append(buf)

pat = re.compile(r'file\s*=\s*"([^"]*)"\s*(//\s*trim\(string_used\)\s*)?'
                 r'//\s*trim\((benchmark_simulation|long_run_simulation|old_results)\)')

need = set()
for l in joined:
    if "action='read'" not in l and 'action="read"' not in l:
        continue
    for m in pat.finditer(l):
        stem, per_i, which = m.group(1), bool(m.group(2)), m.group(3)
        tag = NAMES[which]
        if per_i:
            need.add(("%s1%s.dat" % (stem, tag), which))
            need.add(("%s2%s.dat" % (stem, tag), which))
        else:
            need.add(("%s%s.dat" % (stem, tag), which))

# the two CSVs, which the model opens as ../data/<f> relative to the run dir
csvs = ["us_mh_onset_shape.csv", "us_mortality_multipliers.csv"]

missing, present = [], 0
for fn, which in sorted(need):
    if os.path.exists(os.path.join(RUN, fn)):
        present += 1
    else:
        missing.append((fn, which))
for c in csvs:
    if not (os.path.exists(os.path.join(RUN, "..", "data", c))
            or os.path.exists(os.path.join(RUN, c))):
        missing.append((c, "../data or run dir"))
    else:
        present += 1

print("run dir : %s" % RUN)
print("required: %d files parsed out of the source" % (len(need) + len(csvs)))
print("present : %d" % present)
if missing:
    print("\nMISSING -- do NOT start the transition:")
    by = {}
    for fn, which in missing:
        by.setdefault(which, []).append(fn)
    for which in sorted(by):
        print("  from %s:" % which)
        for fn in sorted(by[which]):
            print("      %s" % fn)
    print("\n'counter_TF' files come from the Treatment First arm's own converged")
    print("run and are written only by save_vars_and_functions at the end of it.")
    sys.exit(1)

print("\nall inputs present -- the transition has everything it opens for reading")
sys.exit(0)
