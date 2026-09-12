#!/usr/bin/env bash
# RESUME THE CALIBRATION AFTER THE CONTAINER KILLS IT.
#
# On 11 September the container was recreated roughly every eight minutes --
# dmesg showing a fresh boot each time, memory and disk both fine -- and every
# recreation killed the solve mid-write. run_one_point.sh deletes
# calibration_state.dat on launch, so a plain relaunch discards every loop since
# the run began and restarts at the original vector.
#
# This scrapes the live parameter values out of the newest worker log and
# relaunches from THEM, which is what the handover is for. A kill then costs the
# loops since the last resume, not the whole run.
#
# Usage:  bash resume.sh [BASE_VECTOR]      (from code/)
#         BASE_VECTOR defaults to THREE_BLOCK_VECTOR.txt and MUST be the vector
#         the dead run was launched on -- it supplies every parameter the scrape
#         below does not carry, which is every STRUCTURAL one.
set -u
cd "$(dirname "$0")" || exit 1

if ps -eo args= | grep -q "[r]un_one_point.sh"; then
    echo "resume: a run is already alive, doing nothing"; exit 0
fi

L=$(ls -t worker_*.log 2>/dev/null | head -1)
[ -z "$L" ] && { echo "resume: no worker log to resume from"; exit 1; }

python3 - "$L" "${1:-THREE_BLOCK_VECTOR.txt}" <<'PY'
import re, sys
T = open(sys.argv[1], errors="replace").read().split("\n")
def last(name):
    r = None
    for l in T:
        m = re.match(r"\s*%s=\s*([0-9.E+-]+)\s*$" % re.escape(name), l)
        if m: r = m.group(1).replace("E", "e")
    return r
# Anchored on the WHOLE line: "distance_<name>=" contains "<name>=" and an
# unanchored match silently reads the distance as the value. That error was made
# once and produced a table claiming theta had fallen 79 per cent.
NAMES = ["addiction_scalar_1","relative_share_of_addiction_1","weight_on_child",
 "value_of_life","utility_cost_of_treatment","mu_homeless","size_homelessness",
 "smallest_rental_relative_to_lowest_income","relative_share_of_housing",
 "relative_share_of_leisure","discount_factor","labor_income_tax_rate",
 "max_food_cost","probability_of_voucher_benchmark_used",
 "probability_becoming_unemployed","kkk_sigma_scale","smi_onset_level",
 "newborn_endowment_scale","addiction_onset_base"]
# THE BASE VECTOR IS AN ARGUMENT AND IT MUST BE THE ONE THE RUN WAS LAUNCHED ON.
# This read RESTART_VECTOR.txt unconditionally, and on 12 September that file was
# STALE: it carried kappa_phi_d_level=8 from a much older run while the live run
# was at 3.0, and weight_on_child=0.1009 while omega_c was pinned at 0.09.  The
# NAMES list below holds only CALIBRATED parameters, so neither was overwritten,
# and the resume silently relaunched a DIFFERENT MODEL from the one that had
# just spent two and a half hours and twenty-six loops.  It was caught by
# reading the vector back before trusting the relaunch, which is now what the
# echo at the end of this script is for.
BASE = sys.argv[2] if len(sys.argv) > 2 else "THREE_BLOCK_VECTOR.txt"
v = dict(x.split("=", 1) for x in open(BASE).read().split())
moved = 0
for n in NAMES:
    x = last(n)
    if x is None or n not in v: continue
    if abs(float(x) - float(v[n])) > 1e-12:
        v[n] = x; moved += 1
open("RESUME_VECTOR.txt", "w").write(" ".join("%s=%s" % kv for kv in v.items()))
print("resume: base %s, carried %d parameters forward from %s"
      % (BASE, moved, sys.argv[1]))
# STRUCTURAL PARAMETERS ARE PRINTED, NOT ASSUMED.  These are the ones the NAMES
# list does NOT carry, so they come from the base and decide WHICH MODEL runs.
# If they are not what the run is meant to be at, the base is wrong.
for k in ("kappa_phi_d_level", "weight_on_child", "relative_share_of_addiction_1",
          "bottom_productivity_level", "lambda_addiction", "addiction_onset_base"):
    if k in v:
        print("resume:   %-42s %s" % (k, v[k]))
PY

BASE=$(cat RESUME_VECTOR.txt)
nohup bash run_one_point.sh $BASE > "resume_$(date -u +%H%M%S).log" 2>&1 &
sleep 4
echo "resume: relaunched at $(date -u +%H:%M:%S)"
