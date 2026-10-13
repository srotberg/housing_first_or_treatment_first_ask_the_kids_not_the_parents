#!/bin/bash
# remote_tr50_C.sh -- THE RULE-C TRANSITION AT T = 50 (13 October; the author: "for the old rule A we know T had to be
# 70...50 was not enough", "but here we can probably use T=50": at detection 0.20 the price falls less and the
# disorder falls faster). A copy of remote_tr70_C.sh with these changes:
#
#   * T = 50: transition_fix/build_tr50_C.sh (build_tr70_C2.sh with transition_length 70 -> 50, checked). After every
#     loop the launcher reports how far the last ten years of the price and pi_V paths sit from the terminal values
#     ("horizon check" in the status), so a horizon that is too short shows as a path still moving at T.
#   * THE SEEDS ARE RESCALED TO RULE C. The transition moves each year's drug price at most 0.5 per cent a loop
#     (clear_drug_market's max_drug_price_move), so for the first loops the seed largely is the price path. Rule A's raw
#     path ends at 0.857 and the rule-C terminal at detection 0.20 sits near 0.93: remote_tr70_C.sh's raw rule-A seed
#     could not have closed that in two loops. Here rule A's converged T = 70 loop-2 path keeps its shape and is
#     rescaled, x_C(t) = x0 + (x_A(s) - x0) (x_C(T) - x0) / (x_A(T) - x0), x0 the no-policy value, x_C(T) the rule-C
#     terminal arm's, s = 1 + (t - 1) 68/48 so rule A's 69 years map onto 49 (as remote_transition_2c.sh rescaled the
#     old loop 0 for T = 60).
#   * THE TERMINAL ARM never waits on a stale walk. It starts at once from the long-run arm's latest published pass
#     (pdet/remote_pdet_C2.sh 0.20, restarted 18:35 from 0.93 / 0.082; TF_P0 / TF_V0 when it has none). When that arm is
#     ACCEPTED, a terminal arm still running is kept only if its latest price is within 0.5 per cent and its pi_V within
#     2 per cent of the accepted values, otherwise it is killed and re-solved from them. Either way it must end within
#     REL_TOL of the accepted final.txt, as before.
#   * LOOPS: binary loop k is archived as results/transition_2c_t50_C/loop<k>; the binary is stopped after MAX_LOOPS
#     (default 4) loops rather than two, since a 0.5 per cent step a loop is slow to correct a seed.
#   * THE NEWBORN VALUES (cf_kid) run after the transition instead of before it, so the path comes first.
#   The arm-dependent files the paper reads still go to results/transition_2c_C/.
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/transition_fix/remote_tr50_C.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running worker. In a container that
# ran remote_tr70_C.sh it reuses the builds and the accepted no-policy arm (code/cfarm_null_2c). Status every 20 minutes
# to results/transition_2c_t50_C/status.txt.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)   # this script lives in code/transition_fix; C is code/
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/transition_2c_t50_C
R2=$REPO/results/transition_2c_C
# 13 Oct: the paper's detection rate is 0.20 (61% of all tested users stop on impact, Mehay and Pacula); the accepted
# long-run arm at that rate is pdet/remote_pdet_C2.sh 0.20's. RULEC_PDET and C1R_OVERRIDE override both.
PDET_C=${RULEC_PDET:-0.20}
C1R=${C1R_OVERRIDE:-results/counterfactuals_2c/tf_pdet$(python3 -c "print('%02d' % round(100*$PDET_C))")_C}   # the accepted long-run rule-C arm
mkdir -p "$R" "$R2"
D=$C/tr50C_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
# 13 Oct: treatment is publicly funded in every arm (patch_treatC.py), so Housing First's net revenue, the target,
# carries its own treatment spending: treat/net_target_with_treatment.py gives 5.8918411 - 0.1332056 * 0.482685 ($9,426 a treated year)
NET_TARGET=5.8275447063                 # the accepted no-policy run's net revenue (tf85_c35's and tf_ruleC's target)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
REL_TOL=${REL_TOL:-1e-3}                      # re-solved arm against the accepted one (rule A's was 2.4e-4)
POLL=${POLL:-1200}                            # seconds between looks at the branch for the acceptance (and status)
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
MAIN=$C/tr2c_t50_C
T50=$C/tr50_C
SEEDS=$REPO/results/transition_2c_t70/loop2   # rule A's converged T = 70 paths, rescaled at staging
MAX_LOOPS=${MAX_LOOPS:-4}

note() { echo "remote_tr50_C: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR50CC_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_tr50_C: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( TR50CC_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr50_C.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_tr50_C: started detached, pid $(cat "$D.pid"); log /tmp/tr50_C.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_tr50_C: finished"; cat "$D.status" 2>/dev/null
    exit 0
fi

# the transition's progress: per loop, the periods done, the worst drug-market and budget gaps; the CEV path of the
# latest forward pass (TRANSITION CEV t=, the newborn-with-childhood CEV per period)
tr_digest() (
    L=$1/run.log; [ -f "$L" ] || exit 0
    python3 - "$L" <<'PYEOF'
import re, sys
L = open(sys.argv[1], errors='replace').read().splitlines()
loops = {}
for l in L:
    m = re.search(r'TRANSITION BUDGET loop=\s*(\d+)\s+t=\s*(\d+).*residual=\s*(\S+)', l)
    if m:
        d = loops.setdefault(int(m.group(1)), {'t': 0, 'bud': 0.0, 'drug': 0.0})
        t = int(m.group(2)); d['t'] = max(d['t'], t)
        if t > 1: d['bud'] = max(d['bud'], abs(float(m.group(3))))
    m = re.search(r'TRANSITION DRUG t=\s*(\d+)\s+distance=\s*(\S+)', l)
    if m and loops:
        d = loops[max(loops)]; d['drug'] = max(d['drug'], abs(float(m.group(2))))
saved = [int(x) for x in re.findall(r'TRANSITION PATHS SAVED after loop\s+(\d+)', '\n'.join(L))]
for k in sorted(loops):
    d = loops[k]
    print(f"  binary loop {k}: periods to {d['t']}, worst budget residual (t>1) {d['bud']:.2e}, "
          f"worst drug gap {d['drug']:.2e}" + ('  [paths saved]' if k in saved else ''))
start = max([i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [0])
cev = [(int(m.group(1)), float(m.group(2))) for m in (re.search(r'TRANSITION CEV t=\s*(\d+)\s+CEV=\s*(\S+)', l) for l in L[start:]) if m]
if cev:
    print('  CEV path of the latest forward pass (per cent, t: value):')
    for i in range(0, len(cev), 10):
        print('    ' + '  '.join(f'{t}: {100*c:+.3f}' for t, c in cev[i:i+10]))
better = [l for l in L if 'TRANSITION BETTER OFF t=           1 ' in l]
if better: print('  latest', better[-1].strip())
PYEOF
)
publish() (
    {
        echo "# the T = 50 transition on RULE C (code/transition_fix/remote_tr50_C.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null
                             [ $a = tf ] && grep -a "MILBY SPLIT" "$L" | tail -1; }
        done
        [ -d "$MAIN" ] && { echo; echo "== tr2c_t50_C (T = 50, rule C)"; tr_digest "$MAIN"; }
        [ -f "$D.horizon" ] && { echo; echo "== horizon check (the last ten years against the terminal values)"; cat "$D.horizon"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" "$R2" 2>/dev/null
    git commit -q -m "transition T=50 rule C: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

# arm <name> <build> [VAR=value ...]: one steady state in code/cfarm_<name>_2c, in the background
arm() {
    a=$1; b=$2; shift 2
    note "arm $a on $b: $*"
    ( cd "$C" && env BUILD="$b" OMP_NUM_THREADS=2 "$@" sh transition_2c/cf_arm_tr2c_C.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 ) &
    echo $! > "$D.arm_$a.pid"
}
arm_ok() {   # <name> <check>: the arm exited with its checks passed
    O="$C/cfarm_${1}_2c.out"
    [ -f "$O" ] && tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "$2" "$O" && ! grep -q "GUARD" "$O"
}
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
killtree() { local p; for p in $(pgrep -P "$1"); do killtree "$p"; done; kill "$1" 2>/dev/null; }
wait_publishing() {   # <pid file> <label>: publish every 20 minutes while it runs
    while alive "$1"; do
        for _ in $(seq 1 120); do alive "$1" || break; sleep 10; done
        alive "$1" && publish "$2"
    done
}
# the long-run rule-C arm on the branch: <file> printed from the fetched head
branch_file() { ( cd "$REPO" && git fetch -q origin "$BRANCH" 2>/dev/null; git show "FETCH_HEAD:$1" 2>/dev/null ); }
accepted() { branch_file "$C1R/passes.txt" | grep -q "arm tf ACCEPTED"; }
# the arm in $C/cfarm_tf_2c against the accepted final.txt: prints the worst relative difference
compare_tf() {
    branch_file "$C1R/tf/final.txt" > "$D.accepted_final.txt"
    python3 "$C/cf_runs/finalstats.py" "$C/cfarm_tf_2c/cf.log" "$C/cfarm_null_2c/cf.log" > "$D.mine_final.txt" 2>&1
    python3 - "$D.mine_final.txt" "$D.accepted_final.txt" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = lv(sys.argv[1]), lv(sys.argv[2])
keys = ('drug price', 'pi_V (voucher probability)', 'drug use b', 'SUD lambda_d', 'homelessness h_1')
assert all(y.get(k) for k in keys), 'accepted final.txt incomplete'
print('%.3e' % max(abs(x[k] / y[k] - 1) for k in keys))
PYEOF
}

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"

# THE BUILDS
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/tr50C_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/tr50C_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > /tmp/tr50C_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 /tmp/tr50C_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_treatC/hftf_cf_prod" ]; then
    note "building cf_fix2_treatC"
    bash treat/build_treatC.sh > /tmp/tr50C_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/tr50C_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
if [ ! -x "$T50/hftf_tr_prod" ]; then
    note "building tr50_C (build_tr50_C.sh)"
    bash transition_fix/build_tr50_C.sh "$T50" > /tmp/tr50C_build_tr.log 2>&1 || { note "GUARD: build tr50_C failed: $(tail -3 /tmp/tr50C_build_tr.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "$(tail -1 /tmp/tr50C_build_tr.log)"
fi
publish "built"

# THE TWO ARMS. The no-policy arm as rule A's; the terminal arm from the long-run rule-C arm's latest published pass
if ! arm_ok null "VOUCHER CHECK PASS" && ! alive "$D.arm_null.pid"; then
    arm null cf_fix2_share DRUG_PRICE_START=$P_NULL
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_null.pid"; do sleep 10; done
fi
start_tf() {   # <price> <pi_V> <why>
    note "terminal arm from $3: price $1, pi_V $2"
    arm tf cf_fix2_treatC PDET=$PDET_C NET_TARGET="$NET_TARGET" PV_START="$2" DRUG_PRICE_START="$1" EXTRA_SET="cost_per_drug_test $CTEST"
}
if ! arm_ok tf "TARGET CHECK PASS" && ! alive "$D.arm_tf.pid"; then
    if accepted; then
        PV=$(branch_file "$C1R/tf/final.txt" | awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}')
        start_tf ${PV% *} ${PV#* } "the ACCEPTED long-run rule-C arm ($C1R/tf/final.txt)"
    else
        LAST=$(branch_file "$C1R/passes.txt" | awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}')
        [ -n "$LAST" ] || LAST="${TF_P0:-0.93} ${TF_V0:-0.082}"
        start_tf ${LAST% *} ${LAST#* } "the long-run rule-C arm's latest published pass (not yet accepted)"
    fi
fi
wait_publishing "$D.arm_null.pid" "arms running"
arm_ok null "VOUCHER CHECK PASS" || { note "GUARD: the no-policy re-solve failed its checks: $(tail -3 "$C/cfarm_null_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
[ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share"; publish "failed"; exit 1; }

# WAIT FOR THE LONG-RUN ARM'S ACCEPTANCE, publishing while the terminal arm runs
if [ ! -f "$D.tf_confirmed" ]; then
    n=0
    until accepted; do
        [ $((n % 4)) = 0 ] && note "waiting for $C1R to be accepted"
        n=$((n + 1))
        for _ in $(seq 1 $((POLL / 10))); do sleep 10; done
        publish "waiting for the long-run rule-C arm"
    done
    note "long-run rule-C arm ACCEPTED: $(branch_file "$C1R/passes.txt" | grep -m1 'arm tf ACCEPTED')"
    [ "$(branch_file code/treat/patch_treatC2.py | md5sum | cut -c1-32)" = "$(cat "$T50/patch_treatC2.md5")" ] \
        || { note "GUARD: patch_treatC2.py on the branch is not the one the builds used; rebuild (rm -rf code/cf_fix2_treatC code/tr50_C code/cfarm_tf_2c*) and relaunch"; publish "failed"; exit 1; }
    branch_file "$C1R/tf/final.txt" > "$R/accepted_tf_ruleC_final.txt"
    if alive "$D.arm_tf.pid"; then
        PV=$(awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}' "$R/accepted_tf_ruleC_final.txt")
        PE=$(grep -a "^ *price_of_addictive_good=" "$C/cfarm_tf_2c/cf.log" 2>/dev/null | tail -1 | awk '{print $2}')
        VE=$(grep -a "^ *probability_of_voucher=" "$C/cfarm_tf_2c/cf.log" 2>/dev/null | tail -1 | awk '{print $2}')
        if python3 -c "import sys; p,v=map(float,'$PV'.split()); sys.exit(0 if abs(float('$PE')/p-1)<0.005 and abs(float('$VE')/v-1)<0.02 else 1)" 2>/dev/null; then
            note "terminal arm (started early) at price $PE, pi_V $VE, close to the accepted $PV: letting it finish"
        else
            note "terminal arm (started early) at price ${PE:-none}, pi_V ${VE:-none}, not close to the accepted $PV: killed, to re-solve from the accepted values"
            killtree "$(cat "$D.arm_tf.pid")"; sleep 5
        fi
    fi
    wait_publishing "$D.arm_tf.pid" "terminal Treatment First arm running"
    W=nan; arm_ok tf "TARGET CHECK PASS" && W=$(compare_tf)
    if python3 -c "import sys; sys.exit(0 if float('$W') < $REL_TOL else 1)" 2>/dev/null; then
        note "terminal arm (started early) within $REL_TOL of the accepted arm: worst relative difference $W"
    else
        note "terminal arm (started early) NOT within $REL_TOL of the accepted arm ($W, or not accepted): re-solving from the accepted price and pi_V"
        PV=$(awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}' "$R/accepted_tf_ruleC_final.txt")
        [ -f "$C/cfarm_tf_2c.out" ] && mv "$C/cfarm_tf_2c.out" "$C/cfarm_tf_2c.out.early"
        start_tf ${PV% *} ${PV#* } "the ACCEPTED long-run rule-C arm"
        wait_publishing "$D.arm_tf.pid" "terminal Treatment First arm re-solving from the accepted values"
        arm_ok tf "TARGET CHECK PASS" || { note "GUARD: the terminal re-solve failed its checks: $(tail -3 "$C/cfarm_tf_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
        W=$(compare_tf)
        python3 -c "import sys; sys.exit(0 if float('$W') < $REL_TOL else 1)" \
            || { note "GUARD: the terminal re-solve from the accepted values is $W from it, above $REL_TOL"; publish "failed"; exit 1; }
        note "terminal arm re-solved from the accepted values: worst relative difference $W"
    fi
    grep -a "MILBY SPLIT" "$C/cfarm_tf_2c/cf.log" | tail -1 | grep -q . || { note "GUARD: the terminal arm printed no MILBY SPLIT (not rule C?)"; publish "failed"; exit 1; }
    echo "$W" > "$D.tf_confirmed"
fi
for a in null tf; do
    mkdir -p "$R/arm_$a" "$R2/arm_$a"
    python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $( [ $a = tf ] && echo "$C/cfarm_null_2c/cf.log" ) > "$R2/arm_$a/final.txt" 2>&1
    cp "$R2/arm_$a/final.txt" "$R/arm_$a/final.txt"
    gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R2/arm_$a/cf.log.gz"
    cp "$C/cfarm_${a}_2c/welfare_by_employment_youngestcounter_arm.txt" "$R2/arm_$a/value_at_26_by_node.txt" 2>/dev/null
done
grep -a "MILBY SPLIT" "$C/cfarm_tf_2c/cf.log" | tail -1 > "$R2/arm_tf/milby_split.txt"
note "arms: null against nulltf/null $(python3 - "$R2/arm_null/final.txt" "$REPO/results/counterfactuals_2c/nulltf/null/final.txt" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = lv(sys.argv[1]), lv(sys.argv[2])
print('worst relative difference %.1e' % max(abs(x[k] / y[k] - 1) for k in ('drug price', 'drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k)))
PYEOF
); tf against tf_ruleC $(cat "$D.tf_confirmed")"
publish "arms done"

# WHAT THE PAPER READS FROM results/transition_2c/, ON THE RULE-C ARMS (remote_transition_2c.sh's stage E)
if [ ! -f "$R2/shares.txt" ]; then
    ( cd "$C" && python3 transition_2c/shares.py cfarm_tf_2c cfarm_null_2c counter_arm > "$R2/shares.txt" 2>&1
      python3 transition_2c/shares.py cfarm_tf_2c cfarm_tf_2c baseline_benchmark > "$R2/shares_vs_benchmark_strict.txt" 2>&1 )
    note "shares written: $(grep 'all households' "$R2/shares.txt" | head -1)"
fi
if [ ! -f "$R2/age_split.txt" ]; then
    ( cd "$C" && python3 transition_2c/age_split.py null=cfarm_null_2c:counter_arm tf=cfarm_tf_2c:counter_arm \
        > "$R2/age_split.txt" 2>&1 ) || note "age_split FAILED: $(tail -2 "$R2/age_split.txt" | tr '\n' ' ')"
    note "age split: $(grep -c 'housing policy (exact)' "$R2/age_split.txt") of 2 arms exact"
fi
publish "arms done, shares written (newborn values after the transition)"

# THE T = 50 PATH: staged from the arms, then the seeds replaced by rule A's T = 70 loop-2 paths, rescaled to rule C
if [ ! -d "$MAIN" ]; then
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$T50/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr50C_stage_main.log 2>&1 || { note "GUARD: staging T = 50 failed: $(tail -3 /tmp/tr50C_stage_main.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=50, 49 periods" /tmp/tr50C_stage_main.log || { note "GUARD: staging did not read T = 50: $(grep seeds /tmp/tr50C_stage_main.log)"; publish "failed"; exit 1; }
    python3 "$C/transition_fix/rescale_seeds_C.py" "$MAIN" "$SEEDS" "$P_NULL" "$V_NULL" > /tmp/tr50C_seeds.log 2>&1 \
        || { note "GUARD: seeding failed: $(tail -2 /tmp/tr50C_seeds.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "T = 50 staged: $(tail -2 /tmp/tr50C_stage_main.log | tr '\n' ' '); seeds rescaled from rule A: $(tr '\n' ' ' < /tmp/tr50C_seeds.log)"
fi
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "T = 50 already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "T = 50 running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do
            [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"
        done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "T = 50 RELAUNCH after a killed run (seeds: $(ls "$MAIN"/*_path_seed_out.txt >/dev/null 2>&1 && echo 'its last saved paths' || echo 'the staged seeds, loop 0 again'))"
    fi
    # THE HANDOVER IS CONSUMED (the binary deletes PARAM_HANDOVER.txt after reading it): restore it from staging's copy
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || { note "GUARD: no PARAM_HANDOVER.txt or .kept.txt in $MAIN"; publish "failed"; exit 1; }
    if [ -z "$(swapon --show 2>/dev/null)" ] && [ "$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)" -ge 10 ]; then
        fallocate -l 4G /var/tmp/tr50C.swap 2>/dev/null && chmod 600 /var/tmp/tr50C.swap && mkswap /var/tmp/tr50C.swap >/dev/null 2>&1 \
            && swapon /var/tmp/tr50C.swap 2>/dev/null && note "4 GiB swap on" || note "no swap (could not enable)"
    fi
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = 50 transition started, pid $(cat "$D.main.pid")"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a -c '^ HANDOVER' "$MAIN/run.log") parameters"
fi
publish "T = 50 running"

# ARCHIVE: binary loop k is archived as loop<k>. After a relaunch the binary's loop numbering restarts at 0 from the
# saved paths, so the offset is carried in $D.loop_offset.
OFF=$(cat "$D.loop_offset" 2>/dev/null || echo 0)
if ls "$MAIN"/run.log.killed.* >/dev/null 2>&1 && [ ! -f "$D.offset_for_$(ls "$MAIN"/run.log.killed.* | wc -l)" ]; then
    LASTA=$(ls -d "$R"/loop[0-9]* 2>/dev/null | grep -o '[0-9]*$' | sort -n | tail -1)
    OFF=$(( ${LASTA:--1} + 1 )); echo $OFF > "$D.loop_offset"; touch "$D.offset_for_$(ls "$MAIN"/run.log.killed.* | wc -l)"
    note "relaunch: the binary's loop 0 is archived as loop$OFF"
fi
archived=-1
while alive "$D.main.pid"; do
    for _ in $(seq 1 120); do alive "$D.main.pid" || break; sleep 10; done
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        L=$((last + OFF))
        mkdir -p "$R/loop$L"
        gzip -c "$MAIN/run.log" > "$R/loop$L/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$R/loop$L/" 2>/dev/null
        cp "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop$L/" 2>/dev/null
        archived=$last
        echo "loop$L: $(python3 "$C/transition_fix/horizon_check_C.py" "$R/loop$L" "$MAIN" 2>&1 | tail -1)" >> "$D.horizon"
        note "binary loop $last complete, archived to results/transition_2c_t50_C/loop$L; $(tail -1 "$D.horizon")"
        if [ "$((L + 1))" -ge "$MAX_LOOPS" ]; then
            note "loop$L archived ($MAX_LOOPS loops): stopping the binary"
            pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
            sleep 5
            echo "stopped after $MAX_LOOPS loops" > "$MAIN/MAIN_EXIT"
            break
        fi
    fi
    publish "T = 50 running"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "T = 50 transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = 50 rule C ended"

# THE NEWBORN VALUES, after the path (remote_tr70_C.sh ran them before it)
cd "$C"
if [ ! -f "$C/newborn_2c_C/DONE" ]; then
    mkdir -p "$C/newborn_2c_C" "$R2/newborn"
    # the no-policy arm on cf_kid as rule A's (cf_fix2's model, no screen); the rule-C arm on cf_kid_C (cf_kid/build_C.sh:
    # cf_fix2_treatC's model, with the household's own treatment choice at cf_kid's screen call, as the law of motion)
    if sh "$C/cf_kid/build.sh" > /tmp/tr50C_build_kid.log 2>&1 && bash "$C/cf_kid/build_C.sh" "$C/cf_kid_C" >> /tmp/tr50C_build_kid.log 2>&1; then
        for a in null tf; do
            if [ $a = tf ]; then KID="BIN=$C/cf_kid_C/hftf_cf_kid FORCE_BUILD=1"; else KID="BIN=$C/cf_kid/hftf_cf_kid"; fi
            env $KID THREADS=4 sh "$C/cf_kid/run_child_value.sh" "$C/cfarm_${a}_2c" "$C/newborn_2c_C/$a" > "$R2/newborn/run_$a.out" 2>&1 \
                || note "cf_kid on $a FAILED: $(tail -2 "$R2/newborn/run_$a.out" | tr '\n' ' ')"
            cp "$C/newborn_2c_C/$a"/child_value_summary*.txt "$R2/newborn/summary_$a.txt" 2>/dev/null
        done
        python3 "$C/cf_kid/share_newborns.py" --tf "$C/newborn_2c_C/tf" --hf "$C/newborn_2c_C/null" \
            --json "$R2/newborn/shares.json" > "$R2/newborn/shares.txt" 2>&1 || note "share_newborns FAILED"
        ( cd "$C" && python3 cf_kid/value_shares.py --tf cfarm_tf_2c --null cfarm_null_2c > "$R2/value_shares.txt" 2>&1 ) \
            || note "value_shares FAILED"
        touch "$C/newborn_2c_C/DONE"
        note "newborn values written: $(grep -i -m1 'better' "$R2/newborn/shares.txt")"
    else
        note "cf_kid build FAILED: $(tail -3 /tmp/tr50C_build_kid.log | tr '\n' ' ')"
    fi
fi
publish "newborn values done"
