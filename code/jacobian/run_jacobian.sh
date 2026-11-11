#!/bin/bash
# run_jacobian.sh KEY... -- THE CALIBRATION'S JACOBIAN (11 November; the author: "ok, do the 21-solve version", for Referee
# 1's comment 2(f), which asks for the identification argument of Section 5.1 to be shown numerically).
#
# For each KEY, Housing First is solved once with that internally calibrated parameter raised by its STEP (one percent,
# 0.2 percent for the discount factor) and every other parameter at its calibrated value, and the run's MOMENT and
# UNTARGETED lines are saved. KEY 'base' solves it with nothing raised. jacobian.py then turns the saved runs into
# elasticities: the percent change in each targeted moment for a one percent rise in each parameter.
#
# THE SOLVE IS TABLE 3's BENCHMARK, the corrected Housing First (rulec_paths.NULL_DIR, results/decomp_2c_shares_Cu/
# arm_tf/null): the same build (cf_fix2_share_treatCu), the same benchmark files, the same handover settings and the same
# environment as extra_2c/remote_decomp_shares_Cu2.sh's 'null' arm, with ONE difference: the drug price is HELD at that
# run's final price, 0.99938969 (DRUG_MARKET_ADJUSTER=0), because the calibration normalises the price rather than
# clearing it. Like that arm, the solve holds what the counterfactual binary imports from the benchmark: the median income
# behind eligibility, the fair market rent, and the average labour income that scales benefits.
#
# KEY 'omega_c' raises the parent's weight on its child, but its own moment (the rise in drug use when the child's weight
# is set to zero) needs an omega_c = 0 twin of every run, so that row is not computed (the author chose the 21-solve
# version).
#
# Runs MAXPAR solves at once (default 2, two threads each: 4 cores, 15 GiB). Results: results/jacobian/<KEY>/ (cf.log.gz,
# PARAM_HANDOVER.txt, check.txt); each arm directory is deleted once its files are saved. With JAC_PUSH=1 each finished
# run is committed and pushed to the branch (for a worker session); unset, nothing is committed.
#
# START IT DETACHED FROM THE REPO ROOT:  setsid nohup bash code/jacobian/run_jacobian.sh base theta b > /tmp/jac.log 2>&1 &
set -u
C=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$C/.." && pwd)
BRANCH=claude/two-period-addiction-hazard-d7gb61
REF=$REPO/results/reference/hf_2c_omega_0.085
HANDOVER=$REPO/results/decomp_2c_shares_Cu/arm_tf/null/PARAM_HANDOVER.arm.txt
OUT=$REPO/results/jacobian; mkdir -p "$OUT"
MAXPAR=${MAXPAR:-2}
P_HELD=0.99938969
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'

# KEY  handover name  step (relative)  [the label the run echoes it under, when not the name; _ for a space]
TABLE="
theta    relative_share_of_addiction_1        0.01
b        addiction_scalar_1                   0.01
pi_d     addiction_onset_base                 0.01
kphid    kappa_phi_d_level                    0.01
aleph    value_of_life                        0.01
kued     multiple_find_if_addicted            0.01
h1       size_homelessness                    0.01
cmin     max_food_cost                        0.01
piV      probability_of_voucher_benchmark_used 0.01 voucher_probability
T0       newborn_endowment_scale              0.01
omega_m  smi_onset_level                      0.01
kuem     kappa_find_smi                       0.01
muH      mu_homeless                          0.01
tauu     utility_cost_of_treatment            0.01
omega_c  weight_on_child                      0.01
gamma    relative_share_of_housing            0.01
beta     discount_factor                      0.002
h2       smallest_rental_relative_to_lowest_income 0.01 smallest_rental
sigma    kkk_sigma_scale                      0.01
pieu     probability_becoming_unemployed      0.01
taul     labor_income_tax_rate                0.01
"
row() { echo "$TABLE" | awk -v k="$1" '$1==k {print $2, $3, ($4 ? $4 : "-")}'; }

export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$C/jacobian/welfare_curve.dat

note() { echo "jacobian: $* ($(date -u '+%d %b %H:%M UTC'))" | tee -a "$OUT/status_$(hostname).txt"; }

push() (
    [ "${JAC_PUSH:-0}" = 1 ] || exit 0
    cd "$REPO"; exec 8> "$C/jacobian/git.lock"; flock 8
    git add "results/jacobian" 2>/dev/null
    git commit -q -m "jacobian: $1$TRAILER" 2>/dev/null || true
    for i in 1 2 3 4 5 6; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && exit 0
        git rebase --abort 2>/dev/null; sleep $((2 ** i))
    done
    echo "push failed: $1"
)

# ---------------------------------------------------------------- setup: compiler, builds, the shared benchmark
command -v gfortran >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
cd "$C"
[ -s "$CEV_CURVE" ] || gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
[ -f cf_fix2/cf.f90 ] || { GEN_ONLY=1 bash cf_runs/build_cf_fix.sh && GEN_ONLY=1 bash cf_runs/build_cf_fix2.sh; } > "$C/jacobian/gen.log" 2>&1
[ -x cf_fix2_share_treatCu/hftf_cf_prod ] || bash treat/build_share_treatCu.sh > "$C/jacobian/build.log" 2>&1 \
    || { note "GUARD: cf_fix2_share_treatCu did not build ($(tail -2 "$C/jacobian/build.log" | tr '\n' ' '))"; exit 1; }
[ -x cf/hftf_cf_prod ] || sh build_cf.sh "$C/cf" > "$C/jacobian/build_cf.log" 2>&1
# stage 1 once, before any arm, so two arms never unpack the benchmark together
if [ ! -f cfarm_bench/BENCH_DONE ]; then
    env BUILD=cf_fix2_share_treatCu STAGE1_ONLY=1 sh treat/cf_arm_Cu.sh null > "$C/jacobian/stage1.out" 2>&1 \
        || { note "GUARD: stage 1 failed ($(tail -2 "$C/jacobian/stage1.out" | tr '\n' ' '))"; exit 1; }
fi
note "set up on $(hostname): $(nproc) cores, $(free -g | awk '/Mem/{print $2}') GiB, $(df -h "$C" | tail -1 | awk '{print $4}') free"

# ---------------------------------------------------------------- one solve
run_one() {
    K=$1; D=cfarm_null_jac_$K; R=$OUT/$K
    if [ -f "$R/check.txt" ] && grep -q "^OK" "$R/check.txt"; then note "$K already done"; return 0; fi
    mkdir -p "$R"
    if [ "$K" = base ]; then SETS=""; NAME=""; NEW=""
    else
        set -- $(row "$K"); NAME=${1:-}; STEP=${2:-}; ECHO=${3:--}
        if [ "$ECHO" = - ]; then ECHO=$NAME; else ECHO=${ECHO//_/ }; fi
        [ -n "$NAME" ] || { note "GUARD: unknown key $K"; return 1; }
        OLD=$(awk -v n="$NAME" '$1==n {print $2}' "$HANDOVER")
        python3 -c "float('$OLD')" 2>/dev/null || { note "GUARD: $NAME has no value in the handover ('$OLD')"; return 1; }
        NEW=$(python3 -c "print(repr(float('$OLD'.replace('D','E')) * (1 + $STEP)))")
        SETS="$NAME $NEW"
    fi
    note "$K: start${NAME:+ ($NAME $OLD -> $NEW)}"
    env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_jac_$K DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 \
        ${SETS:+"EXTRA_SET=$SETS"} sh treat/cf_arm_Cu.sh null > "$C/$D.out" 2>&1
    rc=$?
    L="$C/$D/cf.log"
    {
        if [ $rc = 0 ] && tail -5 "$C/$D.out" | grep -q "DIST CHECK PASS" && ! grep -q GUARD "$C/$D.out" && [ -s "$L" ]; then
            if [ -n "$NAME" ]; then
                got=$(grep -a "HANDOVER $ECHO:" "$L" | tail -1 | awk '{print $NF}')
                python3 -c "import sys; sys.exit(0 if abs(float('$got')/float('$NEW')-1) < 1e-9 else 1)" 2>/dev/null \
                    && echo "OK $K $NAME $OLD -> $NEW (read back $got)" \
                    || echo "FAIL $K: the run read $NAME as '$got', not $NEW"
            else
                echo "OK base"
            fi
        else
            echo "FAIL $K: rc $rc; $(tail -3 "$C/$D.out" | tr '\n' ' ')"
        fi
    } > "$R/check.txt"
    [ -s "$L" ] && gzip -c "$L" > "$R/cf.log.gz"
    cp "$C/$D/PARAM_HANDOVER.txt" "$R/" 2>/dev/null
    cp "$C/$D.out" "$R/run.out" 2>/dev/null
    note "$K: $(cat "$R/check.txt")"
    grep -q "^OK" "$R/check.txt" && rm -rf "$C/$D"
    push "$K $(head -c 60 "$R/check.txt")"
}

# ---------------------------------------------------------------- the queue, MAXPAR at a time
pids=()
for K in "$@"; do
    while [ "$(jobs -rp | wc -l)" -ge "$MAXPAR" ]; do sleep 30; done
    run_one "$K" &
    pids+=($!)
    sleep 60   # stagger the starts: each arm copies the benchmark directory
done
wait
note "all done: $*"
