#!/bin/bash
# run_jacobian_omega.sh KEY... -- run_jacobian_step.sh with two additions (11 November), for omega_c, whose one-percent
# row moves no moment by more than 0.03 (drug use by -0.003) while the calibration's own comparison (results/reference/
# hf_2c_omega_0.085/RESULT.md) has drug use 17.65 per cent higher at omega_c = 0. JAC_STEP=-1 solves the Jacobian's
# benchmark at weight_on_child = 0 with everything else as in every other solve, so the arc from 0 to 0.085 can be set
# beside the one-percent slope; the check compares in absolute terms, because a relative check divides by the zero.
# JAC_EXTRA adds handover lines to EXTRA_SET (e.g. 'measure_child_gap 1', ';' between lines) and JAC_TAG names the
# result directory for them. run_jacobian_step.sh is not edited because a running job reads it.
set -u
JAC_STEP=${JAC_STEP:?set JAC_STEP, e.g. -1}; SUF=_s$(python3 -c "print(round($JAC_STEP*1000))")${JAC_TAG:-}; XSET=${JAC_EXTRA:-}
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
# KEY  the file upload_vars re-reads  its format
DATS="
beta   discount_factor            15.12
gamma  relative_share_of_housing  15.12
aleph  value_of_life              15.10
h1     size_homelessness          15.12
taul   labor_income_tax_rate      15.12
h2     smallest_house_size        15.12
"
dat() { echo "$DATS" | awk -v k="$1" '$1==k {print $2, $3}'; }
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
    K=$1
    set -- $(dat "$K"); DNAME=${1:-}; FMT=${2:-}
    if [ -n "$DNAME" ]; then T=${K}_dat$SUF; else T=$K$SUF; fi   # a parameter with no file to raise has no _dat
    D=cfarm_null_jacdat_$T; R=$OUT/$T
    if [ -f "$R/check.txt" ] && grep -q "^OK" "$R/check.txt"; then note "$T already done"; return 0; fi
    mkdir -p "$R"
    set -- $(row "$K"); NAME=${1:-}; STEP=${2:-}; ECHO=${3:--}
    if [ "$ECHO" = - ]; then ECHO=$NAME; else ECHO=${ECHO//_/ }; fi
    [ "$K" = h2 ] && ECHO=smallest_rental
    STEP=$JAC_STEP
    [ -n "$NAME" ] || { note "GUARD: unknown key $K"; return 1; }
    OLD=$(awk -v n="$NAME" '$1==n {print $2}' "$HANDOVER")
    python3 -c "float('$OLD')" 2>/dev/null || { note "GUARD: $NAME has no value in the handover ('$OLD')"; return 1; }
    NEW=$(python3 -c "print(repr(float('$OLD'.replace('D','E')) * (1 + $STEP)))")
    if [ -n "$DNAME" ]; then
        FOLD=$(cat "$C/cfarm_bench/${DNAME}baseline_benchmark.dat" | tr -d ' ')
        python3 -c "import sys; sys.exit(0 if abs(float('$FOLD')/float('$OLD')-1)<1e-9 else 1)" \
            || { note "GUARD: the benchmark file holds $DNAME=$FOLD, not the handover's $OLD"; return 1; }
        note "$T: start ($NAME $OLD -> $NEW; file $DNAME $FOLD -> $NEW)"
        env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_jacdat_$T DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 \
            "EXTRA_SET=$NAME $NEW" "DAT_SET=$DNAME $NEW $FMT" sh treat/cf_arm_Cj.sh null > "$C/$D.out" 2>&1
    else
        note "$T: start ($NAME $OLD -> $NEW)"
        env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_jacdat_$T DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 \
            "EXTRA_SET=$NAME $NEW${XSET:+;$XSET}" sh treat/cf_arm_Cj.sh null > "$C/$D.out" 2>&1
    fi
    rc=$?
    L="$C/$D/cf.log"
    {
        if [ $rc = 0 ] && tail -5 "$C/$D.out" | grep -q "DIST CHECK PASS" && ! grep -q GUARD "$C/$D.out" && [ -s "$L" ]; then
            got=$(grep -a "HANDOVER $ECHO:" "$L" | tail -1 | awk '{print $NF}')
            if [ -n "$DNAME" ]; then
                fil=$(grep -a "^DAT_SET $DNAME:" "$C/$D.out" | tail -1 | sed 's/.*-> \[ *\([^] ]*\) *\].*/\1/')
                prt=$(grep -a "^ *$DNAME= " "$L" | tail -1 | awk '{print $NF}')
            else
                fil=$NEW; prt=''
            fi
            python3 -c "
import sys
new = float('$NEW'); close = lambda x: abs(x-new) <= 1e-9*max(abs(new), 1e-6)
ok = close(float('$got')) and close(float('$fil'))
prt = '$prt'
ok = ok and (prt == '' or close(float(prt)))
sys.exit(0 if ok else 1)" 2>/dev/null \
                && echo "OK $T $NAME $OLD -> $NEW (handover read back $got${DNAME:+; file $fil; last pass printed ${prt:-nothing}})" \
                || echo "FAIL $T: handover read back '$got', file '$fil', last pass printed '$prt', not $NEW"
        else
            echo "FAIL $T: rc $rc; $(tail -3 "$C/$D.out" | tr '\n' ' ')"
        fi
    } > "$R/check.txt"
    [ -s "$L" ] && gzip -c "$L" > "$R/cf.log.gz"
    cp "$C/$D/PARAM_HANDOVER.txt" "$R/" 2>/dev/null
    cp "$C/$D.out" "$R/run.out" 2>/dev/null
    note "$T: $(cat "$R/check.txt")"
    grep -q "^OK" "$R/check.txt" && rm -rf "$C/$D"
    push "$T $(head -c 60 "$R/check.txt")"
}

# ---------------------------------------------------------------- the queue, MAXPAR at a time
narms() { pgrep -fc 'cf_arm_C[uj]\.sh null$' || true; }
for K in "$@"; do
    while [ "$(jobs -rp | wc -l)" -ge "$MAXPAR" ] || [ "$(narms)" -ge "$MAXPAR" ]; do sleep 30; done
    run_one "$K" &
    sleep 90   # stagger the starts: each arm copies the benchmark directory, and the count above must see this one
done
wait
note "all done (step $JAC_STEP): $*"
