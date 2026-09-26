#!/bin/bash
# stage_tr_fix.sh <run dir> <binary> <terminal arm dir> <no-policy arm dir> <net target>
#
# Stages a transition built by build_tr60_fix.sh (or a shorter-horizon copy), per
# TRANSITION_LESSONS.md section 16. Differs from the tracked stage_transition.sh in
# what the corrected arms need:
#
#   * TERMINAL STATE: the reform arm's own *counter_arm.* files. Arms on the corrected
#     build name themselves counter_arm (increased_prob_of_voucher_if_homeless_and_addicted
#     stays 1), and the transition, run under the same handover, names its terminal
#     state the same way. The arm's handover is the transition's configuration.
#   * INITIAL STATE: the arm directory's *baseline_benchmark.* files (a copy of the
#     benchmark), with the distribution replaced by the NO-POLICY arm's converged one:
#     the stationary point of the same machinery, at revenue = the budget target.
#   * PARENT SHARE AT t = 1: the no-policy arm's newborn_parent_share_counter.dat
#     (build cf_fix2_share), as newborn_parent_share_initial.dat.
#   * BUDGET TARGET: written into govt_revenues_to_use_in_testsbaseline_benchmark.dat.
#   * SEEDS: price and pi_V flat at the terminal arm's final values, periods 1..T-1.
#     The old T=45 paths are NOT used: their shape was the old seed's, walked by a
#     binding 0.5 per cent cap, on an older economy.
set -e
N=$1; BIN=$2; ARM=$3; NULL=$4; TARGET=$5
S=$(cd "$(dirname "$0")" && pwd); C=$(cd "$(dirname "$0")/.." && pwd)
[ -n "$TARGET" ] || { echo "usage: stage_tr_fix.sh <run dir> <binary> <terminal arm dir> <no-policy arm dir> <net target>"; exit 1; }
[ -x "$BIN" ] || { echo "REFUSING: no binary at $BIN"; exit 1; }
[ ! -e "$N" ] || { echo "REFUSING: $N exists; a run directory is not reusable"; exit 1; }
mkdir -p "$N"; cp "$BIN" "$N/hftf"

cp "$ARM"/*baseline_benchmark.dat "$ARM"/*baseline_benchmark.txt "$N/" 2>/dev/null || true
nb=$(ls "$N"/*baseline_benchmark.* | wc -l); [ "$nb" -ge 60 ] || { echo "REFUSING: $nb benchmark files"; exit 1; }
cp "$ARM"/*counter_arm.dat "$ARM"/*counter_arm.txt "$N/" 2>/dev/null || true
na=$(ls "$N"/*counter_arm.* | wc -l); [ "$na" -ge 10 ] || { echo "REFUSING: $na counter_arm files"; exit 1; }
echo "initial-state files $nb, terminal files $na (from $ARM)"

for i in 1 2; do
  f="$NULL/distribution_stationary${i}counter_arm.dat"
  [ -s "$f" ] || { echo "REFUSING: $f missing"; exit 1; }
  [ "$(stat -c%s "$f")" = "$(stat -c%s "$N/distribution_stationary${i}baseline_benchmark.dat")" ] || { echo "REFUSING: $f is not the benchmark's size"; exit 1; }
  cp "$f" "$N/distribution_stationary${i}baseline_benchmark.dat"
done
echo "t = 0 distribution from $NULL: $(md5sum "$N/distribution_stationary1baseline_benchmark.dat" | cut -c1-12)"

[ -s "$NULL/newborn_parent_share_counter.dat" ] || { echo "REFUSING: $NULL has no newborn_parent_share_counter.dat (run it on cf_fix2_share)"; exit 1; }
cp "$NULL/newborn_parent_share_counter.dat" "$N/newborn_parent_share_initial.dat"
python3 -c "import sys; v=[float(l) for l in open('$N/newborn_parent_share_initial.dat') if l.strip()]; assert len(v)==104 and abs(sum(v)-1)<1e-9, (len(v), sum(v)); print('parent share: 104 values, sum', sum(v))"

printf '%15.12f\n' "$TARGET" > "$N/govt_revenues_to_use_in_testsbaseline_benchmark.dat"
echo "budget target $(cat "$N/govt_revenues_to_use_in_testsbaseline_benchmark.dat")"

[ -s "$ARM/PARAM_HANDOVER.arm.txt" ] || { echo "REFUSING: $ARM/PARAM_HANDOVER.arm.txt missing"; exit 1; }
cp "$ARM/PARAM_HANDOVER.arm.txt" "$N/PARAM_HANDOVER.txt"; cp "$N/PARAM_HANDOVER.txt" "$N/PARAM_HANDOVER.kept.txt"

T=$(grep -m1 "parameter :: transition_length" "$(dirname "$BIN")/tr.f90" | grep -oE "solve_transition_dynamics\*[0-9]+" | cut -d'*' -f2)
P=$(grep -a "^ *price_of_addictive_good=" "$ARM/cf.log" | tail -1 | awk '{print $2}')
V=$(grep -a "^ *probability_of_voucher=" "$ARM/cf.log" | tail -1 | awk '{print $2}')
python3 - "$N" "$T" "$P" "$V" "$ARM" <<'PYEOF'
import sys
n, T, p, v, arm = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
assert 0.3 < p < 1.5 and 1e-5 < v < 1, (p, v)
for name, val in (("drug_price_path_seed.txt", p), ("pi_v_path_seed.txt", v)):
    with open(f"{n}/{name}", "w") as f:
        f.write(f"# flat at the terminal arm's final value, {arm}\n# periods 1 to {T-1}\n")
        f.writelines(f"{val:.15f}\n" for _ in range(T - 1))
print(f"seeds: T={T}, {T-1} periods, price {p:.12f}, pi_V {v:.12f}")
PYEOF

mkdir -p "$(dirname "$N")/data"
for f in us_mortality_multipliers.csv us_mh_onset_shape.csv; do
  [ -f "$(dirname "$N")/data/$f" ] || cp "$C/../data/$f" "$(dirname "$N")/data/$f"
done
sed 's/"long_run_simulation":  "counter_TF"/"long_run_simulation":  "counter_arm"/' "$C/check_transition_inputs.py" > "$S/check_transition_inputs_arm.py"
grep -q '"counter_arm"' "$S/check_transition_inputs_arm.py" || { echo "REFUSING: could not point the checker at counter_arm"; exit 1; }
sed -i "s|^HERE = .*|HERE = \"$C\"|" "$S/check_transition_inputs_arm.py"
python3 "$S/check_transition_inputs_arm.py" "$N"
echo "staged $N -- start with: cd $N && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1"
