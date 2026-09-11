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
# Usage:  bash resume.sh        (from code/)
set -u
cd "$(dirname "$0")" || exit 1

if ps -eo args= | grep -q "[r]un_one_point.sh"; then
    echo "resume: a run is already alive, doing nothing"; exit 0
fi

L=$(ls -t worker_*.log 2>/dev/null | head -1)
[ -z "$L" ] && { echo "resume: no worker log to resume from"; exit 1; }

python3 - "$L" <<'PY'
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
v = dict(x.split("=", 1) for x in open("RESTART_VECTOR.txt").read().split())
moved = 0
for n in NAMES:
    x = last(n)
    if x is None or n not in v: continue
    if abs(float(x) - float(v[n])) > 1e-12:
        v[n] = x; moved += 1
open("RESTART_VECTOR.txt", "w").write(" ".join("%s=%s" % kv for kv in v.items()))
print("resume: carried %d parameters forward from %s" % (moved, sys.argv[1]))
PY

BASE=$(cat RESTART_VECTOR.txt)
nohup bash run_one_point.sh $BASE > "resume_$(date -u +%H%M%S).log" 2>&1 &
sleep 4
echo "resume: relaunched at $(date -u +%H:%M:%S)"
