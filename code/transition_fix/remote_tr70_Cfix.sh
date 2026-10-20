#!/bin/bash
# remote_tr70_Cfix.sh -- THE MAIN TRANSITION WITH THE DRUG PRICE AND pi_V HELD AT HOUSING FIRST'S VALUES (20 October; the
# author, on "67 percent of those who have one when the reform lands are worse off": "you need to report how many of them
# lose when the pv and piv are constant", "you may have to simulate this transition, because this is the correct
# comparison i believe", and "that transition only needs one iteration"). With both prices held there is nothing for the
# loops to clear, so one backward pass and one forward pass are the whole transition. remote_tr70_Cu.sh (the main
# transition, rule C at detection 0.20, T = 70; a worker still runs it, so this is a NEW file) with these changes:
#   * THE TERMINAL ARM is Treatment First's long run with both held, Table 5's 'fixboth' column
#     (results/decomp_2c_shares_Cu3/arm_fixboth, code/extra_2c/remote_decomp_shares_Cu3.sh): cf_fix2_treatC at
#     detection 0.20, DRUG_MARKET_ADJUSTER=0 at the corrected Housing First's cleared price P_HELD=0.99938969 and
#     adjust_taxes 0 at its pi_V V_HELD=0.067533863, no budget target. Re-solved here, checked to hold both exactly and
#     compared with that column's final.txt. It starts with the no-policy arm, not after an acceptance.
#   * THE PATHS: staging (stage_tr_fix.sh) seeds the drug price and pi_V flat at the terminal arm's final values, i.e.
#     at P_HELD and V_HELD in every period (checked); rent and the house price are constant in the main run too, and the
#     lump sum is the binary's own ramp, as there. The path's handover is the terminal arm's: drug_market_adjuster 0 and
#     adjust_taxes 0, checked in the run's HANDOVER lines (the CA launchers reset the adjuster to 0.1; not here), and
#     the forward pass's first TRANSITION MECH line must show p_drug and pi_v at the held values, or the run is killed.
#     Loop 0's forward pass reads only the seeded paths (the price update lands in the path for the next loop), so with
#     MAX_LOOPS=1 the binary is stopped once loop 0 is archived.
#   * THE NUMBER WANTED is printed at the start of the forward pass: 'TRANSITION BETTER OFF TOL t=   1 ... worse_sud=',
#     the share of households with a SUD alive at the reform who are worse off (tolerance 1e-3), the definition of
#     transition_series.py's worse_off_sud and so of the paper's x_trf_alive_sud_worse_pc (67 per cent in the main
#     transition). It goes into the status and results/transition_2c_t70_Cfix/better_off_t1.txt as soon as it appears.
#   * SAFEGUARDS, as remote_tr70_CAgr2.sh: progress.txt every 20 minutes during the forward pass (progress_tr.py), and
#     the backward-pass checkpoint where the disk allows (build_tr70_C2ck.sh: patch_ckpt.py on the plain build's own
#     tr.f90, lines added only; ON if free disk >= the file's 6 GB + 4 + 4 for swap; CKPT=off forces it off). A relaunch
#     reseeds from the staged flat paths, keeps VF_CHECKPOINT.bin (deleted if the killed log ends in CHECKPOINT CORRUPT)
#     and should print 'TRANSITION CHECKPOINT loop= 0 restored= 1'.
#   * no shares, age split or newborn values (the long-run column has them, results/decomp_2c_shares_Cu3/arm_fixboth).
# Results to results/transition_2c_t70_Cfix (status.txt, progress.txt, better_off_t1.txt, arm_null, arm_tf, loop0).
#
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/transition_fix/remote_tr70_Cfix.sh
# and run the same command again whenever the call is stopped: it ATTACHES to the running worker.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)   # this script lives in code/transition_fix; C is code/
REPO=$(cd "$C/.." && pwd)
REF=$REPO/results/reference/hf_2c_omega_0.085
R=$REPO/results/transition_2c_t70_Cfix
R2=$R
PDET_C=${RULEC_PDET:-0.20}
FIXBOTH=$REPO/results/decomp_2c_shares_Cu3/arm_fixboth   # Table 5's held column, to compare the terminal arm with
mkdir -p "$R"
D=$C/tr70Cfix_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
NET_TARGET=${NET_TARGET_U:-5.8371628}   # the corrected Housing First's net revenue (staging writes it; adjust_taxes 0 leaves it unused)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082                               # the no-policy arm's start, as remote_tr70_Cu.sh
P_HELD=0.99938969; V_HELD=0.067533863          # the corrected Housing First's cleared price and pi_V (remote_decomp_shares_Cu3.sh)
POLL=${POLL:-1200}
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
MAIN=$C/tr2c_t70_Cfix
T70=$C/tr70_C2u
T70CK=$C/tr70_C2uck   # the same source with the backward-pass checkpoint (build_tr70_C2ck.sh)
CK_GB=6               # the checkpoint file, rounded up
MAX_LOOPS=1
note() { echo "remote_tr70_Cfix: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR70CFIX_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_tr70_Cfix: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( TR70CFIX_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr70_Cfix.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_tr70_Cfix: started detached, pid $(cat "$D.pid"); log /tmp/tr70_Cfix.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_tr70_Cfix: finished"; cat "$D.status" 2>/dev/null
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
    print(f"  binary loop {k}: periods to {d['t']}, worst budget residual (t>1) {d['bud']:.2e} (pi_V held: not cleared), "
          f"worst drug gap {d['drug']:.2e} (price held: not cleared)" + ('  [paths saved]' if k in saved else ''))
start = max([i for i, l in enumerate(L) if 'TRANSITION INIT PARENT SHARE RESTORED' in l] or [0])
cev = [(int(m.group(1)), float(m.group(2))) for m in (re.search(r'TRANSITION CEV t=\s*(\d+)\s+CEV=\s*(\S+)', l) for l in L[start:]) if m]
if cev:
    print('  CEV path of the latest forward pass (per cent, t: value):')
    for i in range(0, len(cev), 10):
        print('    ' + '  '.join(f'{t}: {100*c:+.3f}' for t, c in cev[i:i+10]))
for tag in ('TRANSITION BETTER OFF t=           1 ', 'TRANSITION BETTER OFF TOL t=   1 '):
    better = [l for l in L if tag in l]
    if better: print('  latest', better[-1].strip())
PYEOF
)
publish() (
    {
        echo "# the T = 70 MAIN transition (rule C, detection $PDET_C) with the drug price and pi_V HELD at Housing First's ($P_HELD, $V_HELD), one loop (code/transition_fix/remote_tr70_Cfix.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null
                             [ $a = tf ] && grep -a "MILBY SPLIT" "$L" | tail -1; }
        done
        [ -d "$MAIN" ] && { echo; echo "== tr2c_t70_Cfix (T = 70, rule C, both prices held)"; tr_digest "$MAIN"; }
        for f in $(ls "$D".report_loop* 2>/dev/null | sort -V); do echo; echo "== ${f##*.report_} (report_tr70_Cu.py)"; cat "$f"; done
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" 2>/dev/null
    git commit -q -m "transition T=70 rule C, prices held (Cfix): $1$TRAILER" || return 0
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
    ( cd "$C" && env BUILD="$b" OMP_NUM_THREADS=2 "$@" sh transition_2c/cf_arm_tr2c_Cu.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 ) &
    echo $! > "$D.arm_$a.pid"
}
arm_ok() {   # <name> <check>: the arm exited with its checks passed
    O="$C/cfarm_${1}_2c.out"
    [ -f "$O" ] && tail -5 "$O" | grep -q "DIST CHECK PASS" && grep -q "$2" "$O" && ! grep -q "GUARD" "$O"
}
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
wait_publishing() {   # <pid file> <label>: publish every 20 minutes while it runs
    while alive "$1"; do
        for _ in $(seq 1 120); do alive "$1" || break; sleep 10; done
        alive "$1" && publish "$2"
    done
}
branch_file() { ( cd "$REPO" && git fetch -q origin "$BRANCH" 2>/dev/null; git show "FETCH_HEAD:$1" 2>/dev/null ); }
lv() {   # <final.txt> <key>: the value column of a finalstats.py line
    python3 - "$1" "$2" <<'PYEOF'
import re, sys
for l in open(sys.argv[1]):
    m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
    if m and m.group(1).strip() == sys.argv[2]:
        print(m.group(2)); break
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

# THE BUILDS (as remote_tr70_Cu.sh)
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/tr70Cfix_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/tr70Cfix_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ]; then
    note "building cf_fix2_share_treatCu (Housing First with the internal_computations fix ungated)"
    bash treat/build_share_treatCu.sh > /tmp/tr70Cfix_build_shareCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/tr70Cfix_build_shareCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > /tmp/tr70Cfix_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 /tmp/tr70Cfix_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_treatC/hftf_cf_prod" ]; then
    note "building cf_fix2_treatC"
    bash treat/build_treatC.sh > /tmp/tr70Cfix_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/tr70Cfix_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC has no held-price stopping rule"; publish "failed"; exit 1; }
if [ ! -x "$T70/hftf_tr_prod" ]; then
    note "building tr70_C2u (build_tr70_C2.sh)"
    bash transition_fix/build_tr70_C2.sh "$T70" > /tmp/tr70Cfix_build_tr.log 2>&1 || { note "GUARD: build tr70_C2u failed: $(tail -3 /tmp/tr70Cfix_build_tr.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "$(tail -1 /tmp/tr70Cfix_build_tr.log)"
fi
# THE CHECKPOINTED BUILD (see the header): optional; a failure or a mismatch drops it, the run goes on with the plain one
if [ "${CKPT:-auto}" != off ] && [ ! -x "$T70CK/hftf_tr_prod" ]; then
    note "building tr70_C2uck (build_tr70_C2ck.sh, with the backward-pass checkpoint)"
    if bash transition_fix/build_tr70_C2ck.sh "$T70" "$T70CK" > /tmp/tr70Cfix_build_ck.log 2>&1; then
        note "$(tail -1 /tmp/tr70Cfix_build_ck.log)"
    else
        note "the checkpointed build failed, the run goes on without it: $(tail -3 /tmp/tr70Cfix_build_ck.log | tr '\n' ' ')"; rm -rf "$T70CK"
    fi
fi
if [ -x "$T70CK/hftf_tr_prod" ]; then
    { cmp -s "$T70/patch_treatC2.md5" "$T70CK/patch_treatC2.md5" && [ "$(diff "$T70/tr.f90" "$T70CK/tr.f90" | grep -c '^<')" = 0 ] \
        && grep -q "TRANSITION CHECKPOINT SAVED loop=" "$T70CK/tr.f90"; } \
        || { note "the checkpointed source is not the plain one with the checkpoint added: dropped"; rm -rf "$T70CK"; }
fi
publish "built"

# THE TWO ARMS: Housing First as the main run's; Treatment First with both prices held (Table 5's fixboth column)
if ! arm_ok null "VOUCHER CHECK PASS" && ! alive "$D.arm_null.pid"; then
    arm null cf_fix2_share_treatCu DRUG_PRICE_START=$P_NULL
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_null.pid"; do sleep 10; done
fi
if ! arm_ok tf "DIST CHECK PASS" && ! alive "$D.arm_tf.pid"; then
    arm tf cf_fix2_treatC PDET=$PDET_C PV_START=$V_HELD DRUG_PRICE_START=$P_HELD DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0"
fi
wait_publishing "$D.arm_null.pid" "arms running"
arm_ok null "VOUCHER CHECK PASS" || { note "GUARD: the no-policy re-solve failed its checks: $(tail -3 "$C/cfarm_null_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
[ -s "$C/cfarm_null_2c/newborn_parent_share_counter.dat" ] || { note "GUARD: no newborn_parent_share_counter.dat from cf_fix2_share"; publish "failed"; exit 1; }
wait_publishing "$D.arm_tf.pid" "terminal arm (both prices held) running"
arm_ok tf "DIST CHECK PASS" || { note "GUARD: the held terminal arm failed its checks: $(tail -3 "$C/cfarm_tf_2c.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
grep -a "MILBY SPLIT" "$C/cfarm_tf_2c/cf.log" | tail -1 | grep -q . || { note "GUARD: the terminal arm printed no MILBY SPLIT (not rule C?)"; publish "failed"; exit 1; }
for a in null tf; do
    mkdir -p "$R/arm_$a"
    python3 "$C/cf_runs/finalstats.py" "$C/cfarm_${a}_2c/cf.log" $( [ $a = tf ] && echo "$C/cfarm_null_2c/cf.log" ) > "$R/arm_$a/final.txt" 2>&1
    gzip -c "$C/cfarm_${a}_2c/cf.log" > "$R/arm_$a/cf.log.gz"
done
# HELD, EXACTLY: the terminal arm's drug price and pi_V are P_HELD and V_HELD
PT=$(lv "$R/arm_tf/final.txt" "drug price"); VT=$(lv "$R/arm_tf/final.txt" "pi_V (voucher probability)")
python3 -c "import sys; sys.exit(0 if abs(float('$PT')/$P_HELD-1)<1e-6 and abs(float('$VT')/$V_HELD-1)<1e-6 else 1)" 2>/dev/null \
    || { note "GUARD: the terminal arm did not hold the prices: drug price ${PT:-none} (want $P_HELD), pi_V ${VT:-none} (want $V_HELD)"; publish "failed"; exit 1; }
CMP=$(python3 - "$R/arm_tf/final.txt" "$FIXBOTH/final.txt" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
try:
    x, y = lv(sys.argv[1]), lv(sys.argv[2])
    ks = [k for k in ('drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k)]
    print('worst relative difference %.1e over %s' % (max(abs(x[k] / y[k] - 1) for k in ks), ', '.join(ks)))
except Exception as e:
    print('not compared (%s)' % e)
PYEOF
)
note "arms done: Treatment First held at drug price $PT, pi_V $VT; against Table 5's held column ($FIXBOTH): $CMP"
publish "arms done"

# THE PATH: staged from the arms, seeds flat at the held values (checked), handover the held arm's (checked)
if [ ! -d "$MAIN" ]; then
    NEED=$((CK_GB + 4)); [ -z "$(swapon --show 2>/dev/null)" ] && NEED=$((NEED + 4))
    FREE=$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)
    if [ "${CKPT:-auto}" != off ] && [ -x "$T70CK/hftf_tr_prod" ] && [ "${FREE:-0}" -ge "$NEED" ]; then
        BIN=$T70CK; touch "$D.ckpt_on"; note "checkpoint ON: $FREE GB free against $NEED needed (the file is about $CK_GB GB)"
    else
        BIN=$T70; rm -f "$D.ckpt_on"; note "checkpoint OFF: ${FREE:-?} GB free against $NEED needed, or no checkpointed build (CKPT=${CKPT:-auto})"
    fi
    grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$T70/tr.f90" \
        || { note "GUARD: $T70 is not at T = 70"; publish "failed"; exit 1; }
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$BIN/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr70Cfix_stage.log 2>&1 || { note "GUARD: staging T = 70 failed: $(tail -3 /tmp/tr70Cfix_stage.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=70, 69 periods" /tmp/tr70Cfix_stage.log || { note "GUARD: staging did not read T = 70: $(grep seeds /tmp/tr70Cfix_stage.log)"; publish "failed"; exit 1; }
    python3 - "$MAIN" "$P_HELD" "$V_HELD" <<'PYEOF' || { note "GUARD: the staged seeds are not flat at the held values"; publish "failed"; exit 1; }
import sys
n, p, v = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
for name, x in (('drug_price', p), ('pi_v', v)):
    s = [float(l) for l in open(f'{n}/{name}_path_seed.txt') if l.strip() and not l.strip().startswith('#')]
    assert len(s) == 69 and max(abs(a / x - 1) for a in s) < 1e-6, (name, len(s), min(s), max(s))
PYEOF
    for h in "$MAIN/PARAM_HANDOVER.kept.txt"; do
        grep -qx "drug_market_adjuster 0" "$h" && grep -qx "adjust_taxes 0" "$h" \
            || { note "GUARD: the staged handover does not hold the prices ($(grep -E '^(drug_market_adjuster|adjust_taxes) ' "$h" | tr '\n' ' '))"; publish "failed"; exit 1; }
    done
    for f in drug_price pi_v; do cp "$MAIN/${f}_path_seed.txt" "$MAIN/${f}_path_seed.staged.txt"; done
    note "T = 70 staged: $(tail -2 /tmp/tr70Cfix_stage.log | tr '\n' ' '); seeds flat at drug price $P_HELD and pi_V $V_HELD, handover drug_market_adjuster 0, adjust_taxes 0"
fi
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "T = 70 already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "T = 70 running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        rm -f "$MAIN/VF_CHECKPOINT.tmp"
        if grep -a -q "CHECKPOINT CORRUPT" "$MAIN/run.log"; then
            rm -f "$MAIN/VF_CHECKPOINT.bin"; note "the killed log ends in CHECKPOINT CORRUPT: VF_CHECKPOINT.bin deleted, the loop starts again from its backward pass"
        fi
        [ -f "$MAIN/VF_CHECKPOINT.bin" ] && note "relaunch with a backward-pass checkpoint in $MAIN ($(du -h "$MAIN/VF_CHECKPOINT.bin" | cut -f1)): the binary should print TRANSITION CHECKPOINT loop= 0 restored= 1"
        # the held paths, not the killed pass's updated ones
        for f in drug_price pi_v; do cp "$MAIN/${f}_path_seed.staged.txt" "$MAIN/${f}_path_seed.txt"; done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "T = 70 RELAUNCH after a killed run (seeds: the staged flat paths, loop 0 again)"
    fi
    # THE HANDOVER IS CONSUMED (the binary deletes PARAM_HANDOVER.txt after reading it): restore it from staging's copy
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || { note "GUARD: no PARAM_HANDOVER.txt or .kept.txt in $MAIN"; publish "failed"; exit 1; }
    if [ -z "$(swapon --show 2>/dev/null)" ] && [ "$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)" -ge 10 ]; then
        fallocate -l 4G /var/tmp/tr70Cfix.swap 2>/dev/null && chmod 600 /var/tmp/tr70Cfix.swap && mkswap /var/tmp/tr70Cfix.swap >/dev/null 2>&1 \
            && swapon /var/tmp/tr70Cfix.swap 2>/dev/null && note "4 GiB swap on" || note "no swap (could not enable)"
    fi
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = 70 transition started, pid $(cat "$D.main.pid")"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a -c '^ HANDOVER' "$MAIN/run.log") parameters"
    sleep 30
    ADJ=$(grep -a "HANDOVER drug_market_adjuster" "$MAIN/run.log" 2>/dev/null | tail -1 | awk '{print $NF}')
    TAX=$(grep -a "HANDOVER adjust_taxes" "$MAIN/run.log" 2>/dev/null | tail -1 | awk '{print $NF}')
    python3 -c "import sys; sys.exit(0 if float('${ADJ:-1}') == 0 and float('${TAX:-1}') == 0 else 1)" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the path read drug_market_adjuster '${ADJ:-none}' and adjust_taxes '${TAX:-none}', not both 0: killed"; publish "failed"; exit 1; }
    note "the path holds both prices: HANDOVER drug_market_adjuster -> $ADJ, adjust_taxes -> $TAX"
fi
publish "T = 70 running"

archived=-1
while alive "$D.main.pid"; do
    for _ in $(seq 1 120); do alive "$D.main.pid" || break; sleep 10; done
    # THE CHECKPOINT'S LINES (restored=, SAVED, CLEARED, NOT SAVED) into the status as they appear
    CKN=$(grep -a -c "TRANSITION CHECKPOINT" "$MAIN/run.log" 2>/dev/null); CKN=${CKN:-0}
    if [ "$CKN" -gt "${CKSEEN:-0}" ]; then
        grep -a "TRANSITION CHECKPOINT" "$MAIN/run.log" | tail -n $((CKN - ${CKSEEN:-0})) | tr -s ' ' | while read -r l; do note "$l"; done
        CKSEEN=$CKN
    fi
    # THE HELD PATH, ON THE FORWARD PASS: period 1's p_drug and pi_v must be the held values
    if [ ! -f "$D.held_checked" ] && grep -a -q " TRANSITION MECH t=           1 " "$MAIN/run.log" 2>/dev/null; then
        H=$(grep -a " TRANSITION MECH t=           1 " "$MAIN/run.log" | tail -1 | python3 -c "
import re, sys
l = sys.stdin.read(); p = float(re.search(r'p_drug=\s*(\S+)', l).group(1)); v = float(re.search(r'pi_v=\s*(\S+)', l).group(1))
print(('ok' if abs(p / $P_HELD - 1) < 1e-6 and abs(v / $V_HELD - 1) < 1e-6 else 'bad'), p, v)")
        case "$H" in
            ok*) touch "$D.held_checked"; note "held on the forward pass: period 1 at drug price and pi_V ${H#ok }" ;;
            *) pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
               note "GUARD: the forward pass's period 1 is not at the held prices: ${H:-unreadable}; killed"; publish "failed"; exit 1 ;;
        esac
    fi
    # THE NUMBER WANTED (see the header), as soon as the forward pass prints it
    if [ ! -s "$R/better_off_t1.txt" ] && grep -a -q "TRANSITION BETTER OFF TOL t=   1 " "$MAIN/run.log" 2>/dev/null; then
        grep -a -m1 "TRANSITION BETTER OFF t=           1 " "$MAIN/run.log" | tr -s ' ' > "$R/better_off_t1.txt"
        grep -a -m1 "TRANSITION BETTER OFF TOL t=   1 " "$MAIN/run.log" | tr -s ' ' >> "$R/better_off_t1.txt"
        note "alive at the reform, prices held: $(tail -1 "$R/better_off_t1.txt")"
        publish "the share better off at the reform is in"
    fi
    # THE FORWARD PASS AS IT RUNS
    python3 "$C/transition_fix/progress_tr.py" "$MAIN/run.log" "$R/arm_null" > "$R/progress.txt.tmp" 2>&1 && mv "$R/progress.txt.tmp" "$R/progress.txt"
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        L=$last
        mkdir -p "$R/loop$L"
        gzip -c "$MAIN/run.log" > "$R/loop$L/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$R/loop$L/" 2>/dev/null
        cp "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop$L/" 2>/dev/null
        archived=$last
        python3 "$C/transition_fix/report_tr70_Cu.py" "$R/loop$L/run.log.gz" "$R/arm_null" "$R/arm_tf" > "$D.report_loop$L" 2>&1
        cp "$D.report_loop$L" "$R/loop$L/report.txt"
        note "binary loop $last complete, archived to results/transition_2c_t70_Cfix/loop$L"
        if [ "$((L + 1))" -ge "$MAX_LOOPS" ]; then
            note "loop$L archived (one loop: both prices held, nothing to clear): stopping the binary"
            pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
            sleep 5
            echo "stopped after $MAX_LOOPS loop" > "$MAIN/MAIN_EXIT"
            break
        fi
    fi
    publish "T = 70 running"
done
if grep -a -q "CHECKPOINT CORRUPT" "$MAIN/run.log" 2>/dev/null && [ ! -f "$D.corrupt_retried" ]; then
    touch "$D.corrupt_retried"; rm -f "$MAIN/VF_CHECKPOINT.bin" "$MAIN/MAIN_EXIT"
    note "the binary stopped on CHECKPOINT CORRUPT: the file deleted, relaunching once from the staged paths"; publish "relaunching after CHECKPOINT CORRUPT"
    cd "$C" && exec env TR70CFIX_DETACHED=1 bash "$C/transition_fix/remote_tr70_Cfix.sh"
fi
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "T = 70 transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = 70 rule C, prices held, ended"
