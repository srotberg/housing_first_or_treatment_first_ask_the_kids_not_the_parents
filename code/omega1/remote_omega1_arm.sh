#!/bin/bash
# remote_omega1_arm.sh <null|fixboth|fixp|fixpv|tf> [OMEGA1_B=<b>] [OMEGA1_PDET=<p>] -- ONE COLUMN OF THE omega_c = 1
# EXPERIMENT (6 November; stage 3 of code/OMEGA1_PLAN.md; the author: "we want to simulate the tf with the various piv and
# pv", "piv and pv held, piv held and pv not, pv held and piv not, and both not. like we did with the others"). A COPY of
# code/omega_nishiyama/remote_nish_nodes_Cu.sh (the omega_c = 0.686 sensitivity on rule C against its own re-solved
# Housing First), one column per call so that each runs in its own container. That script is left untouched. What differs:
#   * THE BENCHMARK is results/omega1_2c/bench_1.0_b<OMEGA1_B>_ku1.0 (code/remote_omega_point.sh 1.0 <b> 1.0 "" 2
#     omega1_2c, its files/ sent by send_bench_<tag>). OMEGA1_B, its b, comes from the environment or a trailing
#     OMEGA1_B=<b> argument (so the command still starts with "bash code/omega1/...") and is read nowhere else. GUARD,
#     before anything starts, if it is unset, if the benchmark's files are not in this checkout, or if its handover is not
#     weight_on_child 1.0, addiction_scalar_1 <b>, kappa_uem 1.0. BENCH_OMEGA 1.0. KAPPA_X is the log's first KAPPA_X
#     PROBE IMPLIED times 1.5076 and PASSES_BASE its INVARIANT PASS users, SUD and h_1, read at run time: the 0.686 script
#     typed both, and the same rule (results/omega_nishiyama/RESULT.md, remote_cf_nishiyama.sh) reproduces its values.
#   * THE COLUMN. null is the first half of the 0.686 script: Housing First re-solved on cf_fix2_share_treatCu (the
#     corrected build), its price clearing from the benchmark's own (no earlier Housing First exists for this economy),
#     pi_V at the benchmark's; its net revenue goes to results/omega1_Cu/cf/null/net_target.txt LAST, once every check
#     has passed (the 0.686 script wrote it before its 26-node check). The four Treatment First columns are the second
#     half, each on cf_fix2_treatC through treat/cf_arm_C.sh, holding or clearing the drug price and pi_V exactly as
#     Table 5's columns do (code/extra_2c/remote_decomp_shares_Cu2.sh, which produced results/decomp_2c_shares_Cu/arm_*):
#       fixboth  PV_START=V_NULL DRUG_PRICE_START=P_NULL DRUG_MARKET_ADJUSTER=0, EXTRA_SET test cost;adjust_taxes 0
#       fixp     NET_TARGET PV_START=V0 DRUG_PRICE_START=P_NULL DRUG_MARKET_ADJUSTER=0, EXTRA_SET test cost
#       fixpv    PV_START=V_NULL DRUG_PRICE_START=P0, EXTRA_SET test cost;adjust_taxes 0
#       tf       NET_TARGET PV_START=V0 DRUG_PRICE_START=P0, EXTRA_SET test cost (the 0.686 script's tf)
#     and Cu2's two fallbacks, renamed: OMEGA1_HOLD_PRICE=1 holds fixpv's price at OMEGA1_P0 (Cu2's SHARES_HOLD_PRICE:
#     the main column's price cycled and is held at the cycle's mean, 0.9444), OMEGA1_HOLD_PV=1 holds fixp's pi_V at
#     OMEGA1_V0 with no budget clearing (Cu2's SHARES_HOLD_PV: no pi_V balanced the main column, held at 0.0924), its net
#     revenue noted against the target (Cu2 noted it before final.txt was written, so its note was empty).
#   * DETECTION is OMEGA1_PDET (GUARD if unset in a Treatment First column; the 0.686 script typed 0.20); the $35 test
#     and the rest as the main column.
#   * NET_TARGET (fixp, tf) is the null's results/omega1_Cu/cf/null/net_target.txt, from this checkout or else origin's
#     tip (git show, nothing checked out), waited for up to OMEGA1_NULL_WAIT hours (default 12), polled every 5 minutes;
#     a null solved at another b counts as not there. With it come the null's final.txt (P_NULL) and cf.log.gz (each
#     column's final.txt compares with it, as the 0.686 script's did with its local null).
#   * P_NULL, the held drug price (fixboth, fixp), is that null's. V_NULL, the held pi_V (fixboth, fixpv), is the
#     benchmark log's own in full (Housing First holds it there: its VOUCHER CHECK), checked against the null's. fixboth
#     and fixpv do not wait: without a null in yet, fixboth holds the benchmark's own price (its log's
#     price_of_addictive_good, 1 by construction), said in its status as a stand-in to re-run; OMEGA1_WAIT_NULL=1 makes
#     them wait too. Table 5's held columns hold the corrected Housing First's price (decomp_2c_shares_Cu3, 0.99938969).
#   * WARM STARTS: the main column's converged values (P0, V0 below, from results/decomp_2c_shares_Cu*/arm_<column>), or
#     this column's own last published pass on a restart, as the 0.686 script; OMEGA1_P0 / OMEGA1_V0 replace the
#     first (7 November: they used to override both, so a restarted tagged run went back to its start).
#   * A HELD CHECK in the held columns: the last pass ran at the held price or pi_V (final.txt against the value set).
#   * RESULTS to results/omega1_Cu/nodes/<column>/ and, accepted, results/omega1_Cu/cf/<column>/ (final.txt, cf.log.gz,
#     passes.txt, checks.txt, PARAM_HANDOVER.arm.txt, value_at_26_by_node.txt; Treatment First also run.out.gz and
#     milby.txt), as the 0.686 script's nodes/{null,tf} and cf/{null,tf}. Its running status (nodes/passes.txt there) is
#     per column, nodes/<column>/status.txt; cf/passes.txt, whose first line names the benchmark for export_results.py,
#     is the null's.
#   * run directories cfarm_null_o1 and cfarm_tf_o1_<column> (the 0.686 script's cfarm_null_2c, cfarm_tf_2c), worker
#     files code/cf_point_omega1_<column>.*, so a container that ran another economy cannot hand this one a finished
#     run, and a GUARD if code/cfarm_bench holds another benchmark (cf_arm_C.sh would reuse it without looking).
#   * BUILDS: only the column's (null: cf_fix, cf_fix2, cf_fix2_share, cf_fix2_share_treatCu; Treatment First: cf_fix,
#     cf_fix2, cf_fix2_treatC, with Cu2's guard on the held-price stopping rule), each rebuilt when older than the model
#     source, as run_whostops_C_points.sh does for its binary.
#   * OMEGA1_DRY=1 runs in the foreground: the checks, the builds and the inputs (one look for the null, no waiting),
#     prints the column's settings, and stops before any solve, with no commit.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/omega1/remote_omega1_arm.sh <column> OMEGA1_B=0.00479 OMEGA1_PDET=0.20
# remote_nish_nodes_Cu.sh's header follows.
# remote_nish_nodes_Cu.sh -- THE omega_c = 0.686 SENSITIVITY ON RULE C, AGAINST THE CORRECTED HOUSING FIRST (14 October;
# the author: yes to re-running it on rule C). remote_nish_nodes_C.sh, whose run stopped at pass 1 on 12 October, with:
#   * Housing First RE-SOLVED here on cf_fix2_share_treatCu (patch_treatC2's internal_computations fix ungated, use
#     counted as rule C counts it, treatment publicly funded), not rule A's null reused: rule A's has the old arithmetic
#     and no treatment spending (code/RULE_C_PLAN.md '05:20'). Its net revenue is the Treatment First arm's target.
#   * detection 0.20 (remote_nish_nodes_C.sh still had 0.85), and the warm start at the corrected main column's
#     price and pi_V (results/decomp_2c_shares_Cu/arm_tf/tf/final.txt).
#   * results to results/omega_nishiyama_Cu/{nodes,cf}/{tf,null}.
# remote_nish_nodes_C.sh's header follows.
# remote_nish_nodes_C.sh -- THE omega_c = 0.686 SENSITIVITY ON RULE C (12 October; the author: "all the stuff already in
# the paper should be redone for rule C", "start the simulations from guesses that equal each corresponding simulation
# with rule a"). remote_nish_nodes.sh with the Treatment First arm on the rule-C build (cf_fix2_treatC,
# treat/build_treatC.sh, through treat/cf_arm_C.sh), warm-started at rule A's converged price and pi_V for this economy
# (results/omega_nishiyama/nodes/tf/final.txt: 0.8494885, 0.095466831), or at this arm's own last published pass on a
# restart. Housing First (the null arm) has no screen and is NOT re-run: rule A's accepted null
# (results/omega_nishiyama/nodes/null, and cf/null with its net revenue, the budget target) is copied beside the new arm
# so the exporters find both. Results to results/omega_nishiyama_C/nodes/{tf,null} (export_nish_parts.py) and, once
# accepted, the same files to results/omega_nishiyama_C/cf/{tf,null} (export_results.py's x_nish_cev). A COPY.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root, and run it again whenever the call stops (it
# attaches):  bash code/omega_nishiyama/remote_nish_nodes_C.sh
set -u
# the column, and OMEGA1_*=<value> settings given as arguments rather than in the environment
COL=
for a in "$@"; do
    case "$a" in
        OMEGA1_[A-Z0-9_]*=*) export "$a" ;;
        *) if [ -z "$COL" ]; then COL=$a; else COL=" $COL"; fi ;;
    esac
done
case "$COL" in null|fixboth|fixp|fixpv|tf) ;; *) echo "usage: remote_omega1_arm.sh <null|fixboth|fixp|fixpv|tf> [OMEGA1_B=<b>] [OMEGA1_PDET=<p>]"; exit 1 ;; esac
# OMEGA1_TAG (7 November): a re-run of a column under another name, so it cannot collide with a run of the same column
# still alive elsewhere (the omega_c = 1 tf column cycled at the default price step; its damped re-run is tf_damped)
NAME="$COL${OMEGA1_TAG:-}"
ARM=omega1_$NAME
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd)
REPO=$(cd "$C/.." && pwd)
# THE omega_c = 1 BENCHMARK: its b from OMEGA1_B, nowhere else
case "${OMEGA1_B:-}" in ''|*[!0-9.]*|*.*.*) echo "GUARD: OMEGA1_B (the omega_c = 1 benchmark's b, e.g. 0.00479) is unset or not a number: '${OMEGA1_B:-}'"; exit 1 ;; esac
BREL=results/omega1_2c/bench_1.0_b${OMEGA1_B}_ku1.0
REF=$REPO/$BREL
for f in bench.log.gz PARAM_HANDOVER.bench.txt files/welfare_curvebaseline_benchmark.dat.gz files/median_incomebaseline_benchmark.dat.gz files/drug_supply_shifterbaseline_benchmark.dat.gz; do
    [ -s "$REF/$f" ] || { echo "GUARD: $BREL/$f is not in this checkout (has the benchmark's worker sent its files, send_bench_1.0_b${OMEGA1_B}_ku1.0, and has this checkout pulled them?)"; exit 1; }
done
for l in "weight_on_child 1.0" "addiction_scalar_1 $OMEGA1_B" "kappa_uem 1.0"; do
    grep -qxF "$l" "$REF/PARAM_HANDOVER.bench.txt" || { echo "GUARD: $BREL/PARAM_HANDOVER.bench.txt has no line '$l'"; exit 1; }
done
# from the benchmark's log: the first KAPPA_X PROBE IMPLIED, the INVARIANT PASS users, SUD and h_1, its pi_V and price
read -r KX_PROBE PB_B PB_L PB_H V_BENCH P_BENCH < <(zcat "$REF/bench.log.gz" | awk '
    /KAPPA_X PROBE: IMPLIED kappa_x=/ && kx == "" {kx = $5}
    /INVARIANT PASS +drug users/ {b = $NF} /INVARIANT PASS +disorder rate/ {l = $NF} /INVARIANT PASS +homelessness rate/ {h = $NF}
    /^ *probability_of_voucher=/ {v = $2} /^ *price_of_addictive_good=/ {p = $2}
    END {print (kx == "" ? "NA" : kx), (b == "" ? "NA" : b), (l == "" ? "NA" : l), (h == "" ? "NA" : h), (v == "" ? "NA" : v), (p == "" ? "NA" : p)}')
python3 -c "import sys; [float(x) for x in sys.argv[1:]]" "$KX_PROBE" "$PB_B" "$PB_L" "$PB_H" "$V_BENCH" "$P_BENCH" 2>/dev/null \
    || { echo "GUARD: $BREL/bench.log.gz lacks a KAPPA_X PROBE, INVARIANT PASS, probability_of_voucher or price line (kappa_x probe '$KX_PROBE', base '$PB_B,$PB_L,$PB_H', pi_V '$V_BENCH', price '$P_BENCH'): did the solve reach save_welfare_curve?"; exit 1; }
if [ -f "$C/cfarm_bench/BENCH_DONE" ] && [ "$(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null)" != "$REF" ]; then
    echo "GUARD: code/cfarm_bench holds another benchmark ($(cat "$C/cfarm_bench/BENCH_FROM" 2>/dev/null || echo 'one solved in place')), which the arm would reuse: move it aside and run again"; exit 1
fi
# DETECTION, for a Treatment First column
PDET=
if [ "$COL" != null ]; then
    PDET=${OMEGA1_PDET:-}
    python3 -c "import sys; p = float('$PDET'); sys.exit(0 if 0 < p <= 1 else 1)" 2>/dev/null \
        || { echo "GUARD: OMEGA1_PDET (the detection rate, e.g. 0.20) is unset or not in (0, 1]: '$PDET'"; exit 1; }
fi
[ "${OMEGA1_HOLD_PRICE:-0}" = 1 ] && { case "$COL" in fixpv|tf) true ;; *) false ;; esac && [ -n "${OMEGA1_P0:-}" ] || { echo "GUARD: OMEGA1_HOLD_PRICE=1 is for fixpv or tf and needs OMEGA1_P0, the price to hold"; exit 1; }; }
[ "${OMEGA1_HOLD_PRICE:-0}" = 1 ] && [ -n "${OMEGA1_ADJ:-}" ] && { echo "GUARD: OMEGA1_HOLD_PRICE=1 holds the price; OMEGA1_ADJ sets its step: give one"; exit 1; }
[ "${OMEGA1_HOLD_PV:-0}" = 1 ] && { [ "$COL" = fixp ] && [ -n "${OMEGA1_V0:-}" ] || { echo "GUARD: OMEGA1_HOLD_PV=1 is for fixp and needs OMEGA1_V0, the pi_V to hold"; exit 1; }; }
RC=$REPO/results/omega1_Cu
R=$RC/nodes
T=$R/$NAME                      # this column's running status, and its files at the end (the 0.686 script's nodes/{null,tf})
NF=$RC/cf/null                 # the re-solved Housing First's accepted files, net_target.txt among them
[ "${OMEGA1_DRY:-0}" = 1 ] || mkdir -p "$T"
D=$C/cf_point_$ARM
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
NET_TARGET_NULL=   # set from the corrected Housing First below
V_NULL=$V_BENCH    # Housing First's pi_V: the benchmark's, which it holds (its VOUCHER CHECK)
P_NULL=            # Housing First's drug price: the re-solved null's, below
export BENCH_FROM=$REF BENCH_B=$OMEGA1_B BENCH_OMEGA=1.0 BENCH_KU=1.0
export KAPPA_X=$(python3 -c "print(repr(float('$KX_PROBE') * 1.5076))")
export OMP_NUM_THREADS=4 SEED_FROM=bench
export PASSES_BASE="$PB_B,$PB_L,$PB_H"
export CEV_CURVE=$D.welfare_curve.dat
NULLRUN=cfarm_null_o1;      NULLLOG=$C/$NULLRUN/cf.log   # the corrected Housing First, solved here (column null)
TFRUN=cfarm_tf_o1_$NAME;     TFLOG=$C/$TFRUN/cf.log       # the Treatment First column, solved here
NULLCMP=                                                  # the null's cf.log(.gz) each final.txt compares with

note() { echo "remote_omega1_arm $COL: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${CF_POINT_DETACHED:-0}" != 1 ] && [ "${OMEGA1_DRY:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_omega1_arm $COL: attaching to the running solve, pid $(cat "$D.pid")"
        # a tagged re-run started before 7 November 05:45 UTC solved under DIAG_TAG _o1_$COL, so its folder is
        # cfarm_tf_o1_$COL while its status and its files at the end read $TFRUN: point the one at the other
        if [ "$NAME" != "$COL" ] && [ ! -e "$C/$TFRUN" ] && [ -d "$C/cfarm_tf_o1_$COL" ]; then
            ln -s "cfarm_tf_o1_$COL" "$C/$TFRUN" && echo "remote_omega1_arm $COL: linked $TFRUN to cfarm_tf_o1_$COL, the folder this solve writes"
        fi
    else
        ( CF_POINT_DETACHED=1 setsid nohup bash "$0" "$@" > "/tmp/cf_point_$ARM.detached.log" 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_omega1_arm $COL: started detached, pid $(cat "$D.pid"); log /tmp/cf_point_$ARM.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_omega1_arm $COL: finished"; cat "$D.status" 2>/dev/null
    grep -q "column $COL ACCEPTED" "$D.status" 2>/dev/null
    exit $?
fi

digest() ( cd "$C"; [ -f "$1" ] && python3 cf_runs/passes.py "$1" "$C/cf_runs/cev.py" 2>/dev/null )
publish() (
    [ "${OMEGA1_DRY:-0}" = 1 ] && return 0
    {
        echo "# omega_c 1.0 on RULE C, column $COL against $BREL (b $OMEGA1_B, kappa_uem 1.0, kappa_x $KAPPA_X; base $PASSES_BASE); detection ${PDET:-none, no screen}; Housing First re-solved on cf_fix2_share_treatCu; $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        [ -f "$NULLLOG" ] && { echo; echo "== null (the corrected Housing First, cf_fix2_share_treatCu)"; digest "$NULLLOG"; }
        [ -f "$TFLOG" ] && { echo; echo "== $COL"; digest "$TFLOG"; }
        true
    } > "$T/status.txt.tmp"; mv "$T/status.txt.tmp" "$T/status.txt"
    cd "$REPO"
    git add "$RC" 2>/dev/null
    git commit -q -m "omega_c 1.0 on rule C, column $COL: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && \
            git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null
        sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)
# fresh <build dir>: its binary exists and is newer than the model source
fresh() { [ -x "$C/$1/hftf_cf_prod" ] && [ "$C/$1/hftf_cf_prod" -nt "$C/housing_first_or_treatment_first_SR_v1.f90" ]; }
# null_have: the re-solved Housing First's accepted files, solved at THIS b, from this checkout or else origin's tip, to
# $D.null_*; with them NET_TARGET_NULL, P_NULL and NULLCMP
null_have() {
    local f src=checkout
    [ -s "$NF/net_target.txt" ] && grep -qxF "addiction_scalar_1 $OMEGA1_B" "$NF/PARAM_HANDOVER.arm.txt" 2>/dev/null || src=origin
    if [ $src = origin ]; then git -C "$REPO" fetch -q origin "$BRANCH" 2>/dev/null || return 1; fi
    for f in net_target.txt final.txt PARAM_HANDOVER.arm.txt cf.log.gz; do
        if [ $src = checkout ]; then cp "$NF/$f" "$D.null_$f" 2>/dev/null || return 1
        else git -C "$REPO" show "FETCH_HEAD:${NF#$REPO/}/$f" > "$D.null_$f" 2>/dev/null && [ -s "$D.null_$f" ] || return 1; fi
    done
    grep -qxF "addiction_scalar_1 $OMEGA1_B" "$D.null_PARAM_HANDOVER.arm.txt" && grep -qxF "weight_on_child 1.0" "$D.null_PARAM_HANDOVER.arm.txt" || return 1
    NET_TARGET_NULL=$(cat "$D.null_net_target.txt")
    P_NULL=$(awk '/^ *drug price /{print $3}' "$D.null_final.txt")
    local vn; vn=$(awk '/^ *pi_V \(voucher probability\) /{print $4}' "$D.null_final.txt")
    python3 -c "import sys; t, p, v, vb = map(float, sys.argv[1:]); sys.exit(0 if t > 0 and p > 0 and abs(v / vb - 1) < 1e-7 else 1)" "$NET_TARGET_NULL" "$P_NULL" "$vn" "$V_BENCH" 2>/dev/null \
        || { note "GUARD: the null's files do not read: net revenue '$NET_TARGET_NULL', price '$P_NULL', pi_V '$vn' against the benchmark's $V_BENCH"; return 2; }
    NULLCMP=$D.null_cf.log.gz
    note "Housing First (corrected, $src): net revenue $NET_TARGET_NULL, drug price $P_NULL, pi_V $vn"
}
# wait_null: null_have, polled every 5 minutes for OMEGA1_NULL_WAIT hours (default 12), publishing about hourly
wait_null() {
    local end n=0 r
    end=$(( $(date +%s) + ${OMEGA1_NULL_WAIT:-12} * 3600 ))
    while :; do
        null_have; r=$?
        [ $r = 0 ] && return 0
        [ $r = 2 ] && return 2
        [ "${OMEGA1_DRY:-0}" = 1 ] && return 1
        [ "$(date +%s)" -lt "$end" ] || return 1
        [ $((n % 12)) = 0 ] && { note "waiting for the re-solved Housing First at b $OMEGA1_B (${NF#$REPO/}/net_target.txt)"; publish "waiting for Housing First"; }
        n=$((n + 1)); sleep 300
    done
}
# held <final.txt label> <value>: the column's last pass ran at the held value
held() {
    python3 - "$T/final.txt" "$1" "$2" <<'PYEOF'
import re, sys
f, k, v = sys.argv[1], sys.argv[2], float(sys.argv[3])
for l in open(f):
    m = re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l)
    if m and m.group(1).strip() == k:
        x = float(m.group(2)); ok = abs(x / v - 1) < 1e-6
        print('HELD CHECK %s: %s %.9g, held at %.9g' % ('PASS' if ok else 'FAIL', k, x, v)); sys.exit(0 if ok else 1)
print('HELD CHECK FAIL: no %s in %s' % (k, f)); sys.exit(1)
PYEOF
}

[ -f "$D.status" ] && mv "$D.status" "$D.status.$(date -u +%H%M%S)"; : > "$D.status"
command -v gfortran >/dev/null 2>&1 || {
    note "gfortran missing, installing"
    apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1
}
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
note "benchmark $BREL: kappa_x $KAPPA_X (probe $KX_PROBE x 1.5076), base $PASSES_BASE, pi_V $V_BENCH, price $P_BENCH"
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"

cd "$C"
for b in cf_fix cf_fix2; do
    fresh "$b" && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "/tmp/omega1_build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 /tmp/omega1_build_$b.log | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ "$COL" = null ]; then
    fresh cf_fix2_share || { note "building cf_fix2_share"; bash transition_fix/build_cf_fix2_share.sh > /tmp/omega1_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed"; publish "failed"; exit 1; }; }
    fresh cf_fix2_share_treatCu || { note "building cf_fix2_share_treatCu (Housing First with the internal_computations fix ungated)"; bash treat/build_share_treatCu.sh > /tmp/omega1_build_shareCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/omega1_build_shareCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
    grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
else
    fresh cf_fix2_treatC || { note "building cf_fix2_treatC (rule C)"; bash treat/build_treatC.sh > /tmp/omega1_build_treatC.log 2>&1 || { note "GUARD: build cf_fix2_treatC failed: $(tail -3 /tmp/omega1_build_treatC.log | tr '\n' ' ')"; publish "failed"; exit 1; }; }
    grep -q "RULE C (patch_treatC.py)" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: cf_fix2_treatC is not rule C"; publish "failed"; exit 1; }
    grep -q "if (drug_market_adjuster==0.d0) distance_drug_market=0" "$C/cf_fix2_treatC/cf.f90" || { note "GUARD: no held-price stopping rule"; publish "failed"; exit 1; }
fi
publish "built, starting"

# HOUSING FIRST, CORRECTED, for this economy (omega_c 1): its values, its distribution and its net revenue, the target
if [ "$COL" = null ]; then
    if [ "${OMEGA1_DRY:-0}" = 1 ]; then
        note "DRY: arm null would run as: BUILD=cf_fix2_share_treatCu DIAG_TAG=_o1 DRUG_PRICE_START=$P_BENCH sh treat/cf_arm_Cu.sh null (BENCH_FROM=$BENCH_FROM BENCH_B=$BENCH_B BENCH_OMEGA=$BENCH_OMEGA BENCH_KU=$BENCH_KU KAPPA_X=$KAPPA_X SEED_FROM=$SEED_FROM)"
        note "DRY: its files would go to ${R#$REPO/}/null and ${NF#$REPO/}, net_target.txt last; nothing solved, nothing committed"
        exit 0
    fi
    if ! { [ -f "$C/$NULLRUN.out" ] && tail -5 "$C/$NULLRUN.out" | grep -q "DIST CHECK PASS" && grep -q "VOUCHER CHECK PASS" "$C/$NULLRUN.out"; }; then
        note "arm null on cf_fix2_share_treatCu (Housing First, the internal_computations fix ungated), DRUG_PRICE_START=$P_BENCH (the benchmark's)"
        env BUILD=cf_fix2_share_treatCu DIAG_TAG=_o1 DRUG_PRICE_START=$P_BENCH sh treat/cf_arm_Cu.sh null > "$C/$NULLRUN.out" 2>&1 &
        PN=$!
        while kill -0 "$PN" 2>/dev/null; do
            for _ in $(seq 1 120); do kill -0 "$PN" 2>/dev/null || break; sleep 10; done
            kill -0 "$PN" 2>/dev/null && publish "null running"
        done
        wait "$PN"
    fi
    tail -5 "$C/$NULLRUN.out" | grep -q "DIST CHECK PASS" && grep -q "VOUCHER CHECK PASS" "$C/$NULLRUN.out" && ! grep -q "GUARD" "$C/$NULLRUN.out" \
        || { note "GUARD: the corrected Housing First failed its checks: $(tail -3 "$C/$NULLRUN.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
    [ "$(grep -c . "$C/$NULLRUN/welfare_by_employment_youngestcounter_arm.txt" 2>/dev/null)" = 26 ] || { note "GUARD: the corrected null has no 26-node values"; publish "failed"; exit 1; }
    NET_TARGET_NULL=$(python3 cf_runs/finalstats.py "$NULLLOG" | awk '/net government revenue/{print $NF}')
    [ -n "$NET_TARGET_NULL" ] || { note "GUARD: no net revenue in the corrected null's final statistics"; publish "failed"; exit 1; }
    rm -f "$NF/net_target.txt"
    for d in nodes/null cf/null; do
        mkdir -p "$RC/$d"
        gzip -c "$NULLLOG" > "$RC/$d/cf.log.gz"
        python3 cf_runs/finalstats.py "$NULLLOG" > "$RC/$d/final.txt" 2>&1
        grep -a "CHECK PASS\|GUARD" "$C/$NULLRUN.out" > "$RC/$d/checks.txt"
        digest "$NULLLOG" > "$RC/$d/passes.txt"
        cp "$C/$NULLRUN/PARAM_HANDOVER.arm.txt" "$RC/$d/" 2>/dev/null
        cp "$C/$NULLRUN/welfare_by_employment_youngestcounter_arm.txt" "$RC/$d/value_at_26_by_node.txt" 2>/dev/null
    done
    [ "$(awk '/net government revenue/{print $NF}' "$NF/final.txt")" = "$NET_TARGET_NULL" ] || { note "GUARD: cf/null/final.txt does not carry the net revenue $NET_TARGET_NULL"; publish "failed"; exit 1; }
    echo "$NET_TARGET_NULL" > "$NF/net_target.txt"
    note "Housing First (corrected) done: net revenue $NET_TARGET_NULL, the budget target of the pi_V-clearing columns (fixp, tf); drug price $(awk '/^ *drug price /{print $3}' "$NF/final.txt"), the held price of fixboth and fixp"
    note "column null ACCEPTED: $(tr '\n' ' ' < "$NF/checks.txt")"
    # export_results.py reads the benchmark's omega_c off cf/passes.txt's first line
    publish "null done"; cp "$T/status.txt" "$RC/cf/passes.txt"
    publish "complete"
    exit 0
fi

# TREATMENT FIRST on rule C. The null's files: the pi_V-clearing columns wait for them, the others take them if in
case "$COL" in fixp|tf) WAIT=1 ;; *) WAIT=${OMEGA1_WAIT_NULL:-0} ;; esac
if [ "$WAIT" = 1 ]; then
    wait_null; r=$?
    [ $r = 2 ] && { publish "failed"; exit 1; }
    if [ $r = 1 ] && [ "${OMEGA1_DRY:-0}" = 1 ]; then
        note "DRY: no re-solved Housing First at b $OMEGA1_B in this checkout or on origin: the column would wait for ${NF#$REPO/}/net_target.txt up to ${OMEGA1_NULL_WAIT:-12} hours"
        NET_TARGET_NULL='<the-null-s-net-revenue>'
    elif [ $r = 1 ]; then
        note "GUARD: no re-solved Housing First at b $OMEGA1_B (${NF#$REPO/}/net_target.txt) after ${OMEGA1_NULL_WAIT:-12} hours"; publish "failed"; exit 1
    fi
else
    null_have; [ $? = 2 ] && { publish "failed"; exit 1; }
fi
PSRC="the re-solved Housing First's (${NF#$REPO/}/final.txt)"
if [ -z "$P_NULL" ]; then
    P_NULL=$P_BENCH
    PSRC="the BENCHMARK's own ($BREL/bench.log.gz), a stand-in: no re-solved Housing First at b $OMEGA1_B yet; re-run this column once ${NF#$REPO/}/final.txt is in"
fi
[ "$COL" = fixboth ] && note "drug price held at $P_NULL, $PSRC; pi_V held at $V_NULL, the benchmark's"
# the main column's converged values (Table 5), or this column's own last published pass
P0=; V0=
case "$COL" in
  tf)    P0=0.94626257; V0=0.078040993 ;;   # results/decomp_2c_shares_Cu/arm_tf/tf/final.txt (the 0.686 script's warm start)
  fixpv) P0=0.9444 ;;                       # results/decomp_2c_shares_Cu/arm_fixpv/tf/final.txt (held there at its cycle's mean)
  fixp)  V0=0.0924 ;;                       # results/decomp_2c_shares_Cu4/arm_fixp/tf/final.txt (held there where the budget came closest)
esac
LAST=$(awk -v s="== $COL" '$0 == s {t=1; next} /^==/ {t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}' "$T/status.txt" 2>/dev/null)
if [ -n "$LAST" ] && [ "$COL" != fixboth ]; then
    case "$COL" in tf) P0=${LAST% *}; V0=${LAST#* } ;; fixpv) P0=${LAST% *} ;; fixp) V0=${LAST#* } ;; esac
    note "resuming from this column's last published pass: price ${LAST% *}, pi_V ${LAST#* }"
elif [ "$COL" != fixboth ]; then note "warm start at the main column's values: price ${P0:-held}, pi_V ${V0:-held}"; fi
# OMEGA1_P0 / OMEGA1_V0 replace the main column's values only: a restart resumes from this column's own last pass
[ -z "$LAST" ] && [ -n "${OMEGA1_P0:-}" ] && [ -n "$P0" ] && { P0=$OMEGA1_P0; note "OMEGA1_P0: price from $P0"; }
[ -z "$LAST" ] && [ -n "${OMEGA1_V0:-}" ] && [ -n "$V0" ] && { V0=$OMEGA1_V0; note "OMEGA1_V0: pi_V from $V0"; }
# the column's settings; HP / HV are the price / pi_V it holds (empty: that one clears), for the HELD CHECK
HP=; HV=
case "$COL" in
  tf)      SET=(PDET=$PDET NET_TARGET=$NET_TARGET_NULL PV_START=$V0 DRUG_PRICE_START=$P0 "EXTRA_SET=cost_per_drug_test $CTEST")
           # OMEGA1_ADJ (7 November): a smaller price step where the default 0.1 cycles (treat/cf_arm_C.sh: the old arm 3
           # cycled at 0.2 and converged at 0.1)
           [ -n "${OMEGA1_ADJ:-}" ] && SET+=(DRUG_MARKET_ADJUSTER=$OMEGA1_ADJ)
           # OMEGA1_HOLD_PRICE=1 (7 November): where the drug market flips between two states at one price and no
           # step clears it, hold the price at OMEGA1_P0 (the flips' mean) and clear pi_V and the budget, as the main
           # experiment's fixpv was held at its cycle's mean
           [ "${OMEGA1_HOLD_PRICE:-0}" = 1 ] && { SET+=(DRUG_MARKET_ADJUSTER=0); HP=$P0; } ;;
  fixboth) SET=(PDET=$PDET PV_START=$V_NULL DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0")
           HP=$P_NULL; HV=$V_NULL ;;
  fixpv)   SET=(PDET=$PDET PV_START=$V_NULL DRUG_PRICE_START=$P0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0")
           HV=$V_NULL
           [ "${OMEGA1_HOLD_PRICE:-0}" = 1 ] && { SET+=(DRUG_MARKET_ADJUSTER=0); HP=$P0; } ;;
  fixp)    SET=(PDET=$PDET NET_TARGET=$NET_TARGET_NULL PV_START=$V0 DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST")
           HP=$P_NULL
           [ "${OMEGA1_HOLD_PV:-0}" = 1 ] && { SET=(PDET=$PDET PV_START=$V0 DRUG_PRICE_START=$P_NULL DRUG_MARKET_ADJUSTER=0 "EXTRA_SET=cost_per_drug_test $CTEST;adjust_taxes 0"); HV=$V0; } ;;
esac
CLEARS_BUDGET=0; case " ${SET[*]} " in *" NET_TARGET="*) CLEARS_BUDGET=1 ;; esac
if [ "${OMEGA1_DRY:-0}" = 1 ]; then
    note "DRY: column $COL would run as: BUILD=cf_fix2_treatC DIAG_TAG=_o1_$NAME ${SET[*]} sh treat/cf_arm_C.sh tf (BENCH_FROM=$BENCH_FROM BENCH_B=$BENCH_B BENCH_OMEGA=$BENCH_OMEGA BENCH_KU=$BENCH_KU KAPPA_X=$KAPPA_X SEED_FROM=$SEED_FROM); clears the budget $CLEARS_BUDGET, holds the price at ${HP:-(clears)}, pi_V at ${HV:-(clears)}; compared with ${NULLCMP:-no null yet}"
    note "DRY: its files would go to ${T#$REPO/} and, accepted, ${RC#$REPO/}/cf/$NAME; nothing solved, nothing committed"
    exit 0
fi

note "column $COL on cf_fix2_treatC (rule C): ${SET[*]}"
env BUILD=cf_fix2_treatC DIAG_TAG=_o1_$NAME "${SET[@]}" sh treat/cf_arm_C.sh tf > "$C/$TFRUN.out" 2>&1 &
P=$!
while kill -0 "$P" 2>/dev/null; do
    for _ in $(seq 1 120); do kill -0 "$P" 2>/dev/null || break; sleep 10; done
    kill -0 "$P" 2>/dev/null && publish "$COL running, $(grep -ac '^ *distance_govt_budget=' "$TFLOG" 2>/dev/null) passes"
done
wait "$P"; rc=$?
# the null may have landed while this column ran: compare with it if so
[ -z "$NULLCMP" ] && { null_have; [ $? = 2 ] && { publish "failed"; exit 1; }; }
O="$C/$TFRUN.out"
mkdir -p "$T"
gzip -c "$O" > "$T/run.out.gz"
[ -f "$TFLOG" ] && gzip -c "$TFLOG" > "$T/cf.log.gz"
[ -f "$C/$TFRUN/PARAM_HANDOVER.arm.txt" ] && cp "$C/$TFRUN/PARAM_HANDOVER.arm.txt" "$T/"
grep -a "CHECK PASS\|GUARD" "$O" > "$T/checks.txt"
[ -f "$TFLOG" ] && python3 cf_runs/finalstats.py "$TFLOG" $NULLCMP > "$T/final.txt" 2>&1
digest "$TFLOG" > "$T/passes.txt"
grep -a "MILBY SPLIT" "$TFLOG" | tail -3 > "$T/milby.txt"
ok=0
tail -5 "$O" | grep -q "DIST CHECK PASS" || ok=1
[ "$CLEARS_BUDGET" = 1 ] && { grep -q "TARGET CHECK PASS" "$O" || ok=1; }
grep -q "GUARD" "$O" && ok=1
grep -q "RULE C" "$C/cf_fix2_treatC/cf.f90" || ok=1
[ -n "$HP" ] && { held "drug price" "$HP" >> "$T/checks.txt" || ok=1; }
[ -n "$HV" ] && { held "pi_V (voucher probability)" "$HV" >> "$T/checks.txt" || ok=1; }
[ "$COL" = fixboth ] && [ -n "$P_NULL" ] && [ "$P_NULL" != "$HP" ] && note "NOTE: the price was held at $HP, the benchmark's stand-in; the re-solved Housing First's is $P_NULL: re-run this column for the paper's"
[ "${OMEGA1_HOLD_PV:-0}" = 1 ] && note "pi_V held at $V0: net revenue $(awk '/net government revenue/{print $4}' "$T/final.txt") against the corrected Housing First's ${NET_TARGET_NULL:-(not in)}"
cp "$C/$TFRUN/welfare_by_employment_youngestcounter_arm.txt" "$T/value_at_26_by_node.txt" 2>/dev/null
[ "$(grep -c . "$T/value_at_26_by_node.txt" 2>/dev/null)" = 26 ] || { note "GUARD: no 26-node value file for $COL"; ok=1; }
[ "$rc" = 0 ] || ok=1
if [ "$ok" = 0 ]; then
    note "column $COL ACCEPTED (exit $rc): $(tr '\n' ' ' < "$T/checks.txt")"
    mkdir -p "$RC/cf/$NAME"
    for f in run.out.gz cf.log.gz PARAM_HANDOVER.arm.txt checks.txt final.txt passes.txt milby.txt value_at_26_by_node.txt; do
        [ -f "$T/$f" ] && cp "$T/$f" "$RC/cf/$NAME/"
    done
    publish "$COL finished"
else note "column $COL NOT accepted (exit $rc): $(tail -3 "$O" | tr '\n' ' ')"; fi
publish "complete"
