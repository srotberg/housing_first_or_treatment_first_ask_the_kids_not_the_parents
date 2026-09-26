#!/bin/sh
# remote_cf_arm.sh <arm>     arm = tf | omega1 | internalise
#
# A COUNTERFACTUAL THE WAY THE OLD ARMS RAN IT: the counterfactual binary
# (build_cf.sh: is_counterfactual=1, use_revenues_to_increase_voucher_probability=1)
# against a Housing First omega_c = 0.06 benchmark solved IN THE SAME DIRECTORY.
#
#   * the drug price CLEARS on the benchmark's supply curve, elasticity 1.46
#     (clear_drug_market's counterfactual branch reads the benchmark's shifter);
#   * tf clears the budget with pi_V (adjust_taxes 1 -> tax_system_type 3: the
#     voucher lottery moves, the tax does not); omega1 and internalise have NO
#     budget clearing (adjust_taxes 0) -- the author, 24 September;
#   * upload_vars imports the benchmark's median income, labour income profile,
#     net revenue constraint and the rest from its own saved files, so no
#     declaration has to be edited.
#
# STAGE 1 solves the benchmark (12 blocks, straight into save_welfare_curve) in
# cfarm_bench and writes BENCH_DONE. STAGE 2 copies cfarm_bench to cfarm_<arm>
# and runs the arm there, so several arms in one container share ONE benchmark:
#   sh remote_cf_arm.sh internalise && sh remote_cf_arm.sh omega1
# A relaunch skips stage 1 when BENCH_DONE and the benchmark files are on disk.
#
# THE VOUCHER PROBABILITY IS CARRIED BY HAND. The benchmark reads
# probability_of_voucher_benchmark_used from calibration_state.dat (0.0675...);
# the counterfactual binary never calls read_calibration_state and the handover
# did not carry the line, so the 24 September arms ran at the DECLARED 0.06 --
# 11 per cent fewer offers, a policy change hidden inside omega1 and internalise.
# Stage 2 now sets it in the arm's handover from the benchmark's own log and
# checks the arm printed the same number back.
set -e
cd "$(dirname "$0")/.."
ARM="$1"
case "$ARM" in tf|omega1|internalise|null) ;; *) echo "usage: $0 tf|omega1|internalise|null"; exit 1 ;; esac
# THE DISTRIBUTION IS SOLVED EACH PASS (26 September): BUILD is cf_tightdist or
# cf_tightdist_permban (scratchpad build_cf_tightdist.sh), rule 5e-6 in the loop.
BUILD="${BUILD:-cf_tightdist}"
case "$BUILD" in cf_tightdist|cf_tightdist_permban|cf_tightdist_b4|cf_tightdist_b4_permban|cf_tightdist_b4h|cf_tightdist_b4h_permban|cf_tightdist_b3h|cf_tightdist_b3h_permban|cf_tightdist_b3hs|cf_tightdist_b3hs_permban|cf_tdm|cf_tdm_permban|cf_tdm_revdiag|cf_fix|cf_fix_permban|cf_fix2|cf_fix2_permban|cf_fix2_damp|cf_fix2_damp_permban) ;; *) echo "GUARD: BUILD must be a cf_tightdist build"; exit 1 ;; esac
[ -x "$BUILD/hftf_cf_prod" ] || { echo "GUARD: $BUILD/hftf_cf_prod missing"; exit 1; }
DIR="cfarm_${ARM}${DIAG_TAG}"; BDIR=cfarm_bench; SEED=scan_seed
export OMP_NUM_THREADS=2
command -v gfortran >/dev/null || { echo "GUARD: no gfortran"; exit 1; }
[ -e data ] || ln -s ../data data
COMMON="-fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium"

# the benchmark binary is the TRACKED source, unmodified
# A binary older than the source is stale (a container reused from 19 September
# held a cf binary from then): rebuild it.
if [ ! -x bench/hftf_bench ] || [ ! bench/hftf_bench -nt housing_first_or_treatment_first_SR_v1.f90 ]; then
  mkdir -p bench
  gfortran -O3 -funroll-loops $COMMON housing_first_or_treatment_first_SR_v1.f90 -o bench/hftf_bench 2> bench/build_prod.err
  e=$(grep -c Error bench/build_prod.err || true); [ "$e" = 0 ] || { echo "GUARD: benchmark build errors"; exit 1; }
fi
if [ ! -x cf/hftf_cf_prod ] || [ ! cf/hftf_cf_prod -nt housing_first_or_treatment_first_SR_v1.f90 ]; then sh build_cf.sh "$(pwd)/cf"; fi

set_line() {
  if grep -q "^$1 " PARAM_HANDOVER.txt; then sed -i "s|^$1 .*|$1 $2|" PARAM_HANDOVER.txt; else echo "$1 $2" >> PARAM_HANDOVER.txt; fi
  grep -qx "$1 $2" PARAM_HANDOVER.txt || { echo "GUARD: $1 is not '$2' in the file the run reads"; exit 1; }
}
stage_handover() {
  cp ../$SEED/PARAM_HANDOVER_base.txt PARAM_HANDOVER.txt
  n=$(wc -l < PARAM_HANDOVER.txt); [ "$n" -gt 50 ] || { echo "GUARD: handover only $n lines"; exit 1; }
  set_line kappa_x 0.9329
}

# SOLVE THE BENCHMARK ONCE, SHARE IT BY GIT. With BENCH_FROM=<dir holding
# bench_files.tar.gz and bench.log.gz> (e.g. ../results/counterfactuals_cf_v2/bench)
# stage 1 is not run: the arm reads that benchmark's *baseline_benchmark.dat set,
# which is all the counterfactual binary opens (it never reads the calibration
# distributions -- read_calibration_distribution is called only from
# calibrating_model). Gzipped, the set is tens of MB.
if [ -n "$BENCH_FROM" ] && [ ! -f "$BDIR/BENCH_DONE" ]; then
  [ -s "$BENCH_FROM/bench_files.tar.gz" ] && [ -s "$BENCH_FROM/bench.log.gz" ] || { echo "GUARD: $BENCH_FROM lacks bench_files.tar.gz or bench.log.gz"; exit 1; }
  rm -rf "$BDIR" && mkdir -p "$BDIR"
  tar xzf "$BENCH_FROM/bench_files.tar.gz" -C "$BDIR"
  gunzip -c "$BENCH_FROM/bench.log.gz" > "$BDIR/bench.log"
  echo "$BENCH_FROM" > "$BDIR/BENCH_FROM"; date +%s > "$BDIR/BENCH_DONE"
  echo "STAGE 1 taken from $BENCH_FROM: $(ls "$BDIR" | grep -c baseline_benchmark) benchmark files"
fi
if [ -f "$BDIR/BENCH_DONE" ] && [ -f "$BDIR/welfare_curvebaseline_benchmark.dat" ] && [ -f "$BDIR/median_incomebaseline_benchmark.dat" ]; then
  echo "STAGE 1 already done in $BDIR -- skipping the benchmark"
else
  rm -rf "$BDIR" && mkdir -p "$BDIR"
  cp "$SEED/calibration_state.dat" "$SEED/calibration_distribution_shape.dat" "$BDIR/"
  gunzip -c "$SEED/calibration_distribution1.dat.gz" > "$BDIR/calibration_distribution1.dat"
  gunzip -c "$SEED/calibration_distribution2.dat.gz" > "$BDIR/calibration_distribution2.dat"
  [ "$(stat -c%s "$BDIR/calibration_distribution1.dat")" = "265496400" ] || { echo "GUARD: distribution 1 wrong size"; exit 1; }
  cd "$BDIR"
  cp ../bench/hftf_bench ./hftf_bench
  stage_handover
  set_line weight_on_child          0.06
  set_line frozen_stop_after_blocks 12
  cp PARAM_HANDOVER.txt PARAM_HANDOVER.bench.txt
  echo "STAGE 1: Housing First omega_c = 0.06 benchmark, 12 blocks ..."
  ./hftf_bench > bench.log 2> bench.err
  for f in welfare_curvebaseline_benchmark.dat median_incomebaseline_benchmark.dat drug_supply_shifterbaseline_benchmark.dat; do
    [ -s "$f" ] || { echo "GUARD: the benchmark did not write $f -- it never reached the save"; exit 1; }
  done
  date +%s > BENCH_DONE
  # keep every file the counterfactual binary reads (ENGINE.md, 24 September 19:05)
  tar czf bench_files.tar.gz *baseline_benchmark.dat
  echo "STAGE 1 done"
  cd ..
fi

PV=$(grep -a "^ *probability_of_voucher=" "$BDIR/bench.log" | tail -1 | awk '{print $2}')
python3 -c "import sys; v=float('$PV'); sys.exit(0 if 1e-5<v<1 else 1)" || { echo "GUARD: no benchmark voucher probability in $BDIR/bench.log ('$PV')"; exit 1; }
echo "benchmark voucher probability $PV"

rm -rf "$DIR" && cp -a "$BDIR" "$DIR" && cd "$DIR"
rm -f cf.log cf.err
cp ../$BUILD/hftf_cf_prod ./hftf_cf
# A SEEDED BUILD STARTS FROM A FINISHED RUN'S DISTRIBUTION: SEED_FROM names that run's
# directory; its counter_arm files become this arm's distribution_stationary{1,2}seed.dat,
# checked against the benchmark's files for size (the same arrays, one time slot).
case "$BUILD" in *b3hs*|cf_tdm*|cf_fix*)
  [ -n "$SEED_FROM" ] || { echo "GUARD: a seeded build needs SEED_FROM"; exit 1; }
  for i in 1 2; do
    if [ "$SEED_FROM" = bench ]; then f="../cfarm_bench/distribution_stationary${i}baseline_benchmark.dat"; else f="../$SEED_FROM/distribution_stationary${i}counter_arm.dat"; fi
    [ -s "$f" ] || { echo "GUARD: $f missing"; exit 1; }
    [ "$(stat -c%s "$f")" = "$(stat -c%s distribution_stationary${i}baseline_benchmark.dat)" ] || { echo "GUARD: $f is not the benchmark's size"; exit 1; }
    cp "$f" "distribution_stationary${i}seed.dat"
  done
  echo "seeded from $SEED_FROM: $(md5sum distribution_stationary1seed.dat | cut -c1-12) $(md5sum distribution_stationary2seed.dat | cut -c1-12)" ;;
esac
echo "binary $BUILD/hftf_cf_prod"; echo "$BUILD" > BUILD_USED
stage_handover
set_line probability_of_voucher_benchmark_used "${PV_START:-$PV}"
case "$ARM" in
  tf)          set_line weight_on_child 0.06
               set_line voucher_conditional_on_clean 1
               set_line increased_prob_of_voucher_if_homeless_and_addicted ${INC:-1}
               set_line probability_of_detection ${PDET:-0.70}
               set_line probability_of_false_positive 0
               set_line include_voucher_exclusion 1
               set_line adjust_taxes 1
               set_line drug_price_start 0.6 ;;
  omega1)      set_line weight_on_child 1
               set_line adjust_taxes 0
               set_line drug_price_start 0.6 ;;
  internalise) set_line weight_on_child 0.06
               set_line internalise_homelessness_cost 1
               set_line adjust_taxes 0
               set_line drug_price_start 1.0 ;;
  null)        set_line weight_on_child 0.06
               set_line adjust_taxes 0
               set_line drug_price_start 1.0 ;;
esac
# THE OLD ARMS' DAMPING. drug_market_adjuster is declared 0.2; arm 3 CYCLED at
# 0.2 and only converged at 0.1 (code/results/arm3_convergence/CONVERGED.md,
# commit 97e5c146). launch_arm.sh set it for every arm; this script did not.
set_line drug_market_adjuster 0.1
# A MEASURED warm start beats a guess: max_drug_price_move caps the price at 0.5
# per cent a pass, so a start 20 per cent off costs about 40 passes of walking.
if [ -n "$DRUG_PRICE_START" ]; then set_line drug_price_start "$DRUG_PRICE_START"; fi
# THE BUDGET TARGET, LIKE FOR LIKE (author, 25 September). With no policy the
# counterfactual binary puts net revenue 0.226 above the benchmark's saved value
# (CALIBRATION_STATE.md, 25 September 18:20), so clearing against the saved value
# hands a policy a surplus it did not create. NET_TARGET overwrites this arm's
# COPY of the target file; cfarm_bench's is never touched. The guard after the
# run checks the value the binary actually cleared against.
# THE FILE IS govt_revenues_to_use_in_tests, NOT net_govt_revenues: with
# clear_only_vouchers_govt_budget a compile-time 0 the binary reads its
# constraint from the former, and the first attempt wrote the latter and
# cleared against the old value (both hold 6.038875634967).
if [ -n "$NET_TARGET" ]; then
  printf '%15.12f\n' "$NET_TARGET" > govt_revenues_to_use_in_testsbaseline_benchmark.dat
  echo "budget target $(cat govt_revenues_to_use_in_testsbaseline_benchmark.dat) (saved benchmark $(cat ../$BDIR/govt_revenues_to_use_in_testsbaseline_benchmark.dat))"
fi
# A DIFFERENT DRUG SUPPLY ELASTICITY NEEDS A REFITTED SUPPLY LEVEL. The counterfactual
# reads drug_supply_shifter from the benchmark, fitted so price is 1 at the benchmark
# quantity UNDER 1.46; with another curvature that old level puts the price at the
# benchmark quantity far from 1 (1.398 at elasticity 5), a hidden supply shock. So the
# arm's COPY of the shifter is refitted for the new elasticity; cfarm_bench's is not.
if [ -n "$SUPPLY_ELAST" ]; then
  set_line drug_supply_elasticity "$SUPPLY_ELAST"
  python3 - "$SUPPLY_ELAST" <<'PYEOF'
import struct,sys
e_new=float(sys.argv[1]); e_old=struct.unpack('f',struct.pack('f',1.46))[0]
c_old=1+1/e_old; c_new=1+1/e_new
s_old=float(open('drug_supply_shifterbaseline_benchmark.dat').read())
Q=s_old**(-1/(c_old-1)); s_new=Q**(-(c_new-1))
assert abs(s_new*Q**(c_new-1)-1)<1e-12
open('drug_supply_shifterbaseline_benchmark.dat','w').write('%35.20f\n'%s_new)
print('supply refitted: benchmark quantity %.12f, shifter %.12f -> %.12f, price there %.12f (old shifter would give %.6f)'%(Q,s_old,s_new,s_new*Q**(c_new-1),s_old*Q**(c_new-1)))
PYEOF
fi
cp PARAM_HANDOVER.txt PARAM_HANDOVER.arm.txt
echo "STAGE 2: arm $ARM on the counterfactual binary ..."
./hftf_cf > cf.log 2> cf.err
echo "STAGE 2 exited"
grep -a "HANDOVER voucher probability" cf.log | head -1
PF=$(grep -a "^ *probability_of_voucher=" cf.log | head -1 | awk '{print $2}')
PA=$(grep -a "^ *probability_of_voucher=" cf.log | tail -1 | awk '{print $2}')
if [ "$ARM" = tf ]; then
  echo "tf: voucher probability first printed $PF, last $PA (benchmark $PV); it is the budget instrument and moves"
else
  python3 -c "import sys; a,b=float('$PA'),float('$PV'); sys.exit(0 if abs(a-b)<=1e-9*b else 1)" \
    && echo "VOUCHER CHECK PASS: arm ran at $PA, benchmark $PV" \
    || echo "GUARD FAIL: arm ran at voucher probability $PA, benchmark $PV -- the result is contaminated"
fi
if [ -n "$SUPPLY_ELAST" ]; then
  grep -a "HANDOVER drug_supply_elasticity\|drug_supply_curvature is now" cf.log | head -2
fi
if [ -n "$NET_TARGET" ]; then
  NC=$(grep -a "net_govt_revenue_constraint=" cf.log | head -1 | awk '{print $2}')
  python3 -c "import sys; sys.exit(0 if abs(float('$NC')-float('$NET_TARGET'))<1e-9 else 1)" \
    && echo "TARGET CHECK PASS: cleared against $NC" \
    || echo "GUARD FAIL: the run cleared against $NC, not $NET_TARGET"
fi
# THE DISTRIBUTION RULE THE BINARY ACTUALLY USED: every DIST_DONE must end at or below
# 5e-6, and none may have hit the 200-sweep cap.
python3 - <<'PYEOF'
import re
d = [(int(m.group(1)), float(m.group(2))) for m in re.finditer(r"DIST_DONE sweeps=\s*(\d+)\s+final_distance=\s*(\S+)", open("cf.log", errors="replace").read())]
tol, lo = (5e-5, 70) if any(k in open("BUILD_USED").read() for k in ("cf_tdm", "cf_fix")) else (5e-6, 1)
bad = [x for x in d if x[1] > tol or x[0] >= 200 or x[0] < lo]
print(("DIST CHECK PASS: %d passes, sweeps %s, largest final %.2e (rule %.0e, at least %d sweeps)" % (len(d), [x[0] for x in d], max(x[1] for x in d), tol, lo)) if d and not bad else "GUARD FAIL: distribution not solved to %.0e in %d to 199 sweeps: %s" % (tol, lo, bad))
PYEOF
