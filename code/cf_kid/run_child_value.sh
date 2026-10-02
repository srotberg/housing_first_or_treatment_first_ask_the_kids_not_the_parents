#!/bin/bash
# run_child_value.sh <arm_dir> [<out_dir>]
#
# Values every newborn of a FINISHED counterfactual arm by the household it is
# born into, W(1,s) (README.md), from the arm's saved equilibrium -- the
# *counter_arm.dat value function, policies and distribution that
# save_vars_and_functions wrote at the end of the arm's run. No re-solve.
#
# THE ARM DIRECTORY IS ONLY READ. The binary runs in <out_dir>/cf_kid_work.<tag>,
# where every file of the arm under 5 MB is COPIED (the initialisers rewrite a few
# small files: calibration_state.dat, the grid printouts, and the handover is
# deleted after it is read) and every larger one is SYMLINKED (only ever read: the
# routines that write them -- save_vars_and_functions, write_outputs -- are never
# reached, because the hook stops the program first). The mtimes of the symlink
# targets are checked before and after.
#
# THE PRICES OF THE ARM'S LAST SOLVE. The saved policies were solved, and the
# saved distribution iterated, at the drug price and pi_V in force at the start
# of the arm's last loop -- not at the values the loop printed last, which were
# updated AFTER the solve. Both are read out of the arm's cf.log here and handed
# in through the handover (drug_price_start, probability_of_voucher_benchmark_used).
#
# Outputs (copied to <out_dir>, default the arm directory):
#   child_value_at_birth<tag>.dat       W(1,s), F35.13, the age-1 slice of value_function1<tag>.dat's order
#   child_value_at_birth_mass<tag>.dat  Phi_1(s)/M_1 at the same cells
#   child_value_at_birth_parts<tag>.dat W, Wc, Wnd, K, V1 at the same cells
#   child_value_summary<tag>.txt        dimensions, validation numbers, node table
#   cf_kid<tag>.log                     the run's log
# Env: TAG (default counter_arm), THREADS (default 4), KEEP_WORK=1, CF_KID_ALL_AGES=1,
#      BIN (default code/cf_kid/hftf_cf_kid), FORCE_BUILD=1 to accept an unlisted BUILD_USED,
#      LOG / HANDOVER (default cf.log / PARAM_HANDOVER.arm.txt: the run's log and the handover it read),
#      P_SOLVE / PV_SOLVE to give the last solve's drug price and pi_V instead of reading them from LOG.
# The HF omega_c = 0.06 BENCHMARK in an arm directory (a proxy, solved by the benchmark binary):
#   TAG=baseline_benchmark LOG=bench.log HANDOVER=PARAM_HANDOVER.bench.txt P_SOLVE=1 \
#   PV_SOLVE=<last probability_of_voucher= in bench.log> sh run_child_value.sh <arm_dir> <out>
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
CODE=$(cd "$HERE/.." && pwd)
[ -n "$1" ] || { echo "usage: $0 <arm_dir> [<out_dir>]"; exit 1; }
ARM=$(cd "$1" && pwd)
OUT=${2:-$ARM}; mkdir -p "$OUT"; OUT=$(cd "$OUT" && pwd)
TAG=${TAG:-counter_arm}
BIN=${BIN:-$HERE/hftf_cf_kid}
THREADS=${THREADS:-4}
LOG=${LOG:-cf.log}
HANDOVER=${HANDOVER:-PARAM_HANDOVER.arm.txt}
[ -x "$BIN" ] || { echo "GUARD: $BIN missing -- run sh $HERE/build.sh"; exit 1; }

# ---- guards on the arm -------------------------------------------------------
for f in $LOG $HANDOVER value_function1$TAG.dat distribution_stationary1$TAG.dat \
         policy_function_consumption1$TAG.dat frac_mov_optimal_11$TAG.dat \
         value_function1baseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
  [ -s "$ARM/$f" ] || { echo "GUARD: $ARM/$f missing"; exit 1; }
done
if [ "$TAG" = baseline_benchmark ]; then
  [ -f "$ARM/BENCH_DONE" ] || { echo "GUARD: no BENCH_DONE in $ARM"; exit 1; }
  B=cf_fix2; echo "the benchmark's files: a proxy (solved by the benchmark binary); the RECON check says whether it reloads"
else
  grep -aq "simulation_ended" "$ARM/$LOG" || { echo "GUARD: $ARM/$LOG has no simulation_ended -- the arm has not finished"; exit 1; }
  B=$(cat "$ARM/BUILD_USED" 2>/dev/null || echo unknown)
fi
case "$B" in
  cf_fix2|cf_fix2_share|cf_fix2_damp) ;;
  *) if [ "$FORCE_BUILD" = 1 ]; then echo "WARNING: BUILD_USED=$B accepted by FORCE_BUILD"; else
       echo "GUARD: the arm was solved by '$B'; this binary is cf_fix2's model (cf_fix2, cf_fix2_share and"
       echo "       cf_fix2_damp share its law of motion). A *permban build has a different voucher rule."
       echo "       FORCE_BUILD=1 only after checking the two builds' law of motion agree."; exit 1; fi ;;
esac
if grep -aq "TAX STEP:" "$ARM/$LOG"; then
  echo "GUARD: this arm moved the labour income tax; the tax of its last solve is not handed over here"; exit 1
fi

# ---- the drug price and pi_V of the LAST SOLVE, from the arm's log -----------
if [ -n "$P_SOLVE" ] && [ -n "$PV_SOLVE" ]; then
  NLOOP=given; echo "prices given: drug price $P_SOLVE, pi_V $PV_SOLVE"
else
read P_SOLVE PV_SOLVE NLOOP <<EOF
$(python3 - "$ARM/$LOG" "$ARM/$HANDOVER" <<'PYEOF'
import sys, re
log = open(sys.argv[1], errors="replace").read().splitlines()
hand = {}
for l in open(sys.argv[2]):
    p = l.split()
    if len(p) >= 2: hand[p[0]] = p[1]
# drug price: every clear_drug_market update prints "implied supply price=" then the NEW price
upd = [float(log[i+1].split("=")[1]) for i, l in enumerate(log[:-1])
       if l.strip().startswith("implied supply price=") and log[i+1].strip().startswith("price_of_addictive_good=")]
loops = [i for i, l in enumerate(log) if l.strip().startswith("loop_count=")]
start = float(hand["drug_price_start"]) if "drug_price_start" in hand else None
if len(upd) != len(loops):
    sys.stderr.write("WARNING: %d price updates for %d loops\n" % (len(upd), len(loops)))
if len(upd) >= 2: p = upd[-2]
elif start is not None: p = start
else: sys.exit("GUARD: no drug price to hand over")
# pi_V: the pre-step print of the LAST loop (after its loop_count line), else the
# last post-step value, else the handover's
last = loops[-1] if loops else 0
pre = [l for l in log[last:] if l.strip().startswith("probability_of_voucher_benchmark_used_1=")]
post = [l for l in log[:last] if l.strip().startswith("probability_of_voucher_benchmark_used=")]
if pre: pv = float(pre[-1].split("=")[1])
elif post: pv = float(post[-1].split("=")[1])
else: pv = float(hand["probability_of_voucher_benchmark_used"])
print("%.17g %.17g %d" % (p, pv, len(loops)))
PYEOF
)
EOF
fi
[ -n "$PV_SOLVE" ] || { echo "GUARD: could not read the last solve's prices"; exit 1; }
echo "arm $ARM: $NLOOP loops; last solve at drug price $P_SOLVE, pi_V $PV_SOLVE"

# ---- the work directory ------------------------------------------------------
WORK="$OUT/cf_kid_work.$TAG"
rm -rf "$WORK"; mkdir -p "$WORK"
find "$ARM" -maxdepth 1 -type f -size -5M -exec cp -p {} "$WORK/" \;
find "$ARM" -maxdepth 1 -type f ! -size -5M | while read -r f; do ln -s "$f" "$WORK/$(basename "$f")"; done
for csv in us_mh_onset_shape.csv us_mortality_multipliers.csv; do
  for d in "$CODE/data" "$CODE/../data"; do [ -s "$d/$csv" ] && { ln -sf "$(cd "$d" && pwd)/$csv" "$WORK/$csv"; break; }; done
  [ -e "$WORK/$csv" ] || { echo "GUARD: $csv not found"; exit 1; }
done
rm -f "$WORK/cf.log" "$WORK/bench.log"
cp "$ARM/$HANDOVER" "$WORK/PARAM_HANDOVER.txt"
set_line() {
  if grep -q "^$1 " "$WORK/PARAM_HANDOVER.txt"; then sed -i "s|^$1 .*|$1 $2|" "$WORK/PARAM_HANDOVER.txt"; else echo "$1 $2" >> "$WORK/PARAM_HANDOVER.txt"; fi
  grep -qx "$1 $2" "$WORK/PARAM_HANDOVER.txt" || { echo "GUARD: $1 not set"; exit 1; }
}
set_line drug_price_start "$P_SOLVE"
set_line probability_of_voucher_benchmark_used "$PV_SOLVE"
cp "$WORK/PARAM_HANDOVER.txt" "$WORK/PARAM_HANDOVER.cf_kid.txt"
cp "$BIN" "$WORK/hftf_cf_kid"
STAMP_BEFORE=$(find "$WORK" -maxdepth 1 -type l -exec stat -L -c '%n %Y %s' {} \; | sort | md5sum)

# ---- run ---------------------------------------------------------------------
echo "running in $WORK with $THREADS threads ..."
T0=$(date +%s)
( cd "$WORK" && OMP_NUM_THREADS=$THREADS CF_KID_READ_TAG=$TAG CF_KID_OUT_TAG=$TAG ./hftf_cf_kid > cf_kid.log 2> cf_kid.err ) || { echo "GUARD: the binary failed; see $WORK/cf_kid.log, cf_kid.err"; exit 1; }
T1=$(date +%s)
STAMP_AFTER=$(find "$WORK" -maxdepth 1 -type l -exec stat -L -c '%n %Y %s' {} \; | sort | md5sum)
[ "$STAMP_BEFORE" = "$STAMP_AFTER" ] && echo "ARM FILES UNTOUCHED: symlinked inputs have the same mtimes and sizes" \
  || { echo "GUARD FAIL: a symlinked arm file changed during the run"; exit 1; }
grep -aq "CF_KID DONE" "$WORK/cf_kid.log" || { echo "GUARD: no CF_KID DONE in the log"; exit 1; }
echo "wall time $((T1-T0)) s"

# ---- checks: the reload reproduces the arm's own numbers ---------------------
python3 - "$ARM/$LOG" "$WORK/cf_kid.log" "$P_SOLVE" "$PV_SOLVE" <<'PYEOF'
import sys, re
arm = open(sys.argv[1], errors="replace").read().splitlines()
kid = open(sys.argv[2], errors="replace").read().splitlines()
def last(lines, key):
    v = [l.split("=")[-1] for l in lines if l.strip().startswith(key)]
    return float(v[-1].split()[0]) if v else None
ok = True
hp = [l for l in kid if "HANDOVER drug_price_start" in l]
hv = [l for l in kid if "HANDOVER voucher probability" in l]
print("handed over:", hp[-1].strip() if hp else "NONE", "|", hv[-1].strip() if hv else "NONE")
for key, rkey in (("model_fraction_homeless=", "CF_KID RECON model_fraction_homeless="),
                  ("average_childhood_utility=", "CF_KID RECON average_childhood_utility="),
                  ("average_welfare_with_childhood=", "CF_KID RECON average_welfare_with_childhood=")):
    a = last(arm, key); r = last(kid, rkey)
    rel = abs(a - r) / max(abs(a), 1e-300) if (a is not None and r is not None) else float("nan")
    good = rel < 1e-9
    ok &= good
    print("RECON %-32s arm %.15g  reload %.15g  rel diff %.2e  %s" % (key, a, r, rel, "PASS" if good else "FAIL"))
print("RECON CHECK " + ("PASS" if ok else "FAIL: the reloaded state is not the arm's equilibrium"))
for l in kid:
    if "CF_KID" in l and ("VALIDATION" in l or " =" in l or "SANITY" in l or "TIMING" in l):
        print(l.rstrip())
PYEOF

for f in child_value_at_birth$TAG.dat child_value_at_birth_mass$TAG.dat child_value_at_birth_parts$TAG.dat child_value_summary$TAG.txt child_value_by_age$TAG.dat; do
  [ -f "$WORK/$f" ] && cp "$WORK/$f" "$OUT/"
done
cp "$WORK/cf_kid.log" "$OUT/cf_kid$TAG.log"
cp "$WORK/PARAM_HANDOVER.cf_kid.txt" "$OUT/PARAM_HANDOVER.cf_kid$TAG.txt"
echo "wrote $OUT/child_value_at_birth$TAG.dat (and _mass, _parts, summary, log)"
[ "$KEEP_WORK" = 1 ] || rm -rf "$WORK"
