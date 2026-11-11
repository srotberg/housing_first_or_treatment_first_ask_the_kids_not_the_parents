#!/bin/bash
# run_jacobian_rung.sh KEY... -- run_jacobian_step.sh with THE UPPER RUNGS HELD (11 November; the author: "you need to
# change only h2 and not any other rung with it!"). The rental ladder is h_3 = rung_ratio_h3 x h_2 and h_4 = rung_ratio_h4
# x h_2 (cf.f90, the block after 'ONLY THE MIDDLE RUNG IS ASSIGNED'), at 4 and 8 in the benchmark, so raising h_2 alone, as
# run_jacobian_step.sh did, raised h_3 and h_4 with it. Here h_2 is raised by JAC_STEP and both ratios are divided by
# 1 + JAC_STEP in the same handover, so h_3 and h_4 stay at their benchmark levels; h_1 is a level of its own
# (tie_h1_to_h2 = 0). The check also reads the ratios back and asks that the last 'housing_size=' line carry the
# benchmark's h_3 and h_4. Results go to results/jacobian/<KEY>_dat_s<JAC_STEP*1000>_rungs/. run_jacobian_step.sh is not
# edited because running jobs read it.
set -u
JAC_STEP=${JAC_STEP:?set JAC_STEP, e.g. 0.05}; SUF=_s$(python3 -c "print(round($JAC_STEP*1000))")_rungs
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
        R3O=$(awk '$1=="rung_ratio_h3" {print $2}' "$HANDOVER"); R4O=$(awk '$1=="rung_ratio_h4" {print $2}' "$HANDOVER")
        R3=$(python3 -c "print(repr(float('$R3O'.replace('D','E')) / (1 + $STEP)))")
        R4=$(python3 -c "print(repr(float('$R4O'.replace('D','E')) / (1 + $STEP)))")
        H3=$(python3 -c "print(repr(float('$R3O'.replace('D','E')) * float('$OLD'.replace('D','E'))))")
        H4=$(python3 -c "print(repr(float('$R4O'.replace('D','E')) * float('$OLD'.replace('D','E'))))")
        note "$T: rungs held, rung_ratio_h3 $R3O -> $R3, rung_ratio_h4 $R4O -> $R4 (h_3 $H3, h_4 $H4)"
        env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_jacdat_$T DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 \
            "EXTRA_SET=$NAME $NEW;rung_ratio_h3 $R3;rung_ratio_h4 $R4" "DAT_SET=$DNAME $NEW $FMT" sh treat/cf_arm_Cj.sh null > "$C/$D.out" 2>&1
    else
        note "$T: start ($NAME $OLD -> $NEW)"
        env BUILD=cf_fix2_share_treatCu OMP_NUM_THREADS=2 DIAG_TAG=_jacdat_$T DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 \
            "EXTRA_SET=$NAME $NEW" sh treat/cf_arm_Cj.sh null > "$C/$D.out" 2>&1
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
new = float('$NEW'); ok = abs(float('$got')/new-1) < 1e-9 and abs(float('$fil')/new-1) < 1e-9
prt = '$prt'
ok = ok and (prt == '' or abs(float(prt)/new-1) < 1e-9)
import re, os
L = open('$L', errors='replace').read()
r3 = re.findall(r'HANDOVER rung_ratio_h3:\\s*\\S+\\s*->\\s*(\\S+)', L); r4 = re.findall(r'HANDOVER rung_ratio_h4:\\s*\\S+\\s*->\\s*(\\S+)', L)
hs = re.findall(r'^\\s*housing_size=\\s*(.*)$', L, re.M)
ok = ok and bool(r3 and r4 and hs) and abs(float(r3[-1])/float('$R3')-1) < 1e-9 and abs(float(r4[-1])/float('$R4')-1) < 1e-9
v = [float(x) for x in hs[-1].split()] if hs else []
ok = ok and len(v) >= 4 and abs(v[2]/float('$H3')-1) < 1e-6 and abs(v[3]/float('$H4')-1) < 1e-6
sys.exit(0 if ok else 1)" 2>/dev/null \
                && echo "OK $T $NAME $OLD -> $NEW (handover read back $got${DNAME:+; file $fil; last pass printed ${prt:-nothing}}; rungs held at $H3, $H4)" \
                || echo "FAIL $T: handover read back '$got', file '$fil', last pass printed '$prt', not $NEW, or the rungs moved"
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
