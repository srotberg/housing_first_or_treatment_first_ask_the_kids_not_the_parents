#!/bin/bash
# remote_tr70_CAann.sh <detection 1.00|0.20> [announce|grace] -- THE NO-ESCAPE REFORM PHASED IN (19 October; the author:
# "assume those with SUD cannot stop using", "whether 100% or 20% can result in decrease in homelessness in short run",
# "Consider HF but with announcement about TF to happen in 5 years. And consider another case in which treatment alone is
# exempted even if there is drug use, but only in the first 5 years"). Two modes, each at 1.00 and 0.20:
#   announce (default): Housing First for years 1 to LAG (5), every household knowing from year 1 that the no-escape screen
#     starts in year LAG+1 (the backward pass solves year 5 against year 6's screened values). The test at t acts on the
#     voucher held at t+1, so the first revocations land in year 7, as the main path's land in year 2;
#   grace: the screen is on from year 1, but for years 1 to LAG a household in treatment passes it whatever it uses
#     (only a household with a SUD can choose treatment); rule CA, no escape, from year LAG+1.
# A COPY of remote_tr70_CA20e.sh for a FRESH container, with these changes:
#   * the transition binary is transition_fix/build_tr70_CAann.sh's in that mode: tr70_CA plus patch_announce.py
#     (code/tr70_CAann: the screen OFF in years 1 to LAG and ON after; the other Treatment First switches -- exclusion,
#     detection, false positives, the test's cost -- are inert while it is off) or patch_grace.py (code/tr70_CAgrace).
#     pi_V clears the budget and the drug price its market in every year;
#   * the long-run arm and the terminal arm are the main no-escape path's at the same detection rate: at 1.00
#     tf_pdet100_CAbest held at its price (remote_tr70_CAc.sh), at 0.20 tf_pdet20_CAu held at its price
#     (remote_tr70_CA20e.sh); the end state is the same steady state, only the path differs;
#   * the seeds (shift_seeds_ann.py): announce, the main path shifted by LAG years, Housing First's price and pi_V for
#     years 1-5; grace, the main path unshifted. The main path is the main run's latest saved paths (its latest archived loop on the branch when staging runs: CAc or CA20e;
#     at 1.00, failing that, the held-price loop 0 of CAb; else rule C's rescaled paths, as the main runs started);
#   * a GUARD on the forward pass's TRANSITION ANNOUNCE lines (screen 0 for t <= LAG, 1 after, terminal 1) or TRANSITION
#     GRACE lines (grace 1 for t <= LAG, 0 after, screen 1), and the md5 of the mode's patch on the branch checked as the
#     other patches are;
#   * no superseding (a fresh container), no newborn step (the arms are the main runs', whose newborn values are in);
#   * the report (report_tr70_CAann.py) runs over the first 25 years; MAX_LOOPS 6.
# Results to results/transition_2c_t70_CA<tag>, worker files code/tr70CA<tag>_worker*, tag ann100, ann20, grace100, grace20.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:
#     bash code/transition_fix/remote_tr70_CAann.sh 1.00 announce     (or 0.20, or grace)
# and run the same command again whenever the call is stopped: it ATTACHES to the running worker.
# remote_tr70_CA20e.sh's header follows.
# remote_tr70_CA20e.sh -- A COPY of remote_tr70_CA20c.sh (18 October, 13:30; the author: "yes, do both", to starting the
# 20% no-escape path now from the cleared long run instead of waiting for remote_tr70_CA20d.sh's free-price terminal
# re-solve, which after 16 passes still swung around the tolerances: drug 4e-3 to 5.5e-3 against 5e-3, budget 9e-4 to
# 3e-3 against 1e-3, at price 0.9051-0.9056 and pi_V 0.0861 against the accepted 0.90564 and 0.08592). The ONLY change:
# the long-run arm is results/counterfactuals_2c/tf_pdet20_CAu, accepted with both markets inside their rules, and the
# terminal arm holds the drug price at its accepted 0.90563748 (DRUG_MARKET_ADJUSTER=0) while pi_V clears the budget.
# The path still clears both prices in every year: the handover is reset to drug_market_adjuster 0.1 with a GUARD, as
# in remote_tr70_CA20c.sh. The end state's drug market is checked afterwards from the arm's implied supply price.
# remote_tr70_CA20d.sh keeps running in its own container. Results to results/transition_2c_t70_CA20e, worker files
# code/tr70CA20e_worker*. remote_tr70_CA20c.sh's header follows.
# remote_tr70_CA20e.sh -- A COPY of remote_tr70_CA20b.sh at detection 0.20 (17 October, 21:40; the author: "the transition
# result has to allow pv and piv to clear in each period", "the point is about the real transition with no escape, 20%
# detection, vs 100%"). THE DRUG PRICE CLEARS ALONG THE PATH. remote_tr70_CAb.sh and remote_tr70_CA20b.sh solve the
# terminal arm with the drug price held at the best pass (DRUG_MARKET_ADJUSTER=0), and stage_tr_fix.sh copies the arm's
# PARAM_HANDOVER into the transition, so their paths ran with drug_market_adjuster 0: every year's price stayed at its
# seed in every loop (the log: "HANDOVER drug_market_adjuster: 0.2 -> 0.0", TRANSITION DRUG distance 0 at every t).
# Here the terminal arm is still held at the best pass (the market there sits on a knife edge; the author approved the
# best pass on 16 October), but the handover the path reads is reset to drug_market_adjuster 0.1, the arms' default and
# what the rule-C transition runs with, so each year's drug price is updated toward clearing every loop, as pi_V is, and
# a GUARD kills the run if the binary does not read it. MAX_LOOPS 6: the price still moves at most 0.5 per cent a year a
# loop (max_drug_price_move, the author's rule of 8 September).
# IT SUPERSEDES remote_tr70_CA20b.sh IN THE SAME CONTAINER and reuses its builds and arms: at its start it stops that launcher
# and any held-price transition it started, marks that transition finished (MAIN_EXIT) so a re-attach of the old launcher
# cannot restart it, and marks the old newborn step done so a re-attach cannot start that either. Its terminal arm, if still solving, is adopted and waited on, not re-solved.
# Results to results/transition_2c_t70_CA20e, worker files code/tr70CA20e_worker*. remote_tr70_CA20b.sh's header follows.
# remote_tr70_CA20b.sh -- A COPY of remote_tr70_CAb.sh at detection 0.20 (17 October; the author: "I want to launch both
# because I want to see if homelessness rises with 20% detection and no escape"). The long-run arm is
# results/counterfactuals_2c/tf_pdet20_CAbest: tf_pdet20_CAu's pass 13 (price 0.9044, pi_V 0.08624; drug-market gap
# 3.87e-3 and budget gap 3.08e-4, both inside their tolerances), the run otherwise alternating around them. The terminal arm
# holds the price there and clears pi_V, accepted whatever it clears to (REL_TOL 1); and an arm started from the accepted
# values at launch is no longer killed for drifting (FROM_ACCEPTED set at that start, which remote_tr70_CAb.sh did not do,
# costing it two hours). Results to results/transition_2c_t70_CA20b, worker files code/tr70CA20b_worker*.
# remote_tr70_CAb.sh's header follows.
# remote_tr70_CAb.sh -- A COPY of remote_tr70_CAu.sh (16 October, 23:58; the author, on the detection-1.00 long runs
# see-sawing at a drug price near 0.80: "yes, take the best pass and start the transition"). The long-run arm is
# results/counterfactuals_2c/tf_pdet100_CAbest: tf_pdet100_CAuC's pass 7 (price 0.8017, pi_V 0.10240, drug-market gap
# 9.64e-3 against the tolerance of 5e-3, budget gap 5.86e-4), the pass with the smallest drug-market gap of all three
# runs. Near that price a block of households switches in and out of use between passes (drug use -57 against -63 per
# cent for a 0.1 per cent price move), so the market does not settle inside the tolerance. The terminal arm therefore
# HOLDS the drug price at 0.8017 (DRUG_MARKET_ADJUSTER=0, as the fixp column holds Housing First's) and clears pi_V, and
# is accepted against the best pass within 5 per cent (REL_TOL 5e-2). Results to results/transition_2c_t70_CAb, worker
# files code/tr70CAb_worker*. Otherwise remote_tr70_CAu.sh, whose header follows.
# remote_tr70_CAu.sh -- A COPY of remote_tr50_CAu.sh at T = 70 (16 October, 21:20; the author: "you can do T=70 in that
# too", and on homelessness rising along this transition: "We would need to run a transition to make that statement for
# the conclusion"). Differs in: the horizon (transition_fix/build_tr70_CA.sh, code/tr70_CA, staging checked at 69
# periods), the seeds (rescale_seeds_CA70.py: rule C's T = 50 loop-3 paths rescaled to the CA terminal and held there for
# years 50-69), the results (results/transition_2c_t70_CAu), the worker files (code/tr70CAu_worker*), MAX_LOOPS 4 by
# default, and the long-run arm, C1R_OVERRIDE, which the launch sets to the detection-1.00 run accepted (or nearest to it:
# tf_pdet100_CAuC, started at the price where the other two runs' supply prices cross). Everything else as in
# remote_tr50_CAu.sh, whose header follows.
# remote_tr50_CAu.sh -- THE T = 50 TRANSITION UNDER RULE CA AT DETECTION 1.00 (16 October; the author: "do one run in which
# pdet is say 100% and those with SUD cannot get a voucher at all. That may raise homelessness, and we should check also
# the transition for this case to show when there is a trade off"). A COPY of remote_tr50_Cu.sh with these changes:
#   * the transition binary is build_tr50_CA.sh's (tr70_src.f90 with treat/patch_treatCA.py in place of patch_treatC2.py:
#     the disorder fails the screen in treatment or not, any use fails, treatment publicly paid for, abstention off);
#   * Housing First (the start and the null arm) on cf_fix2_share_treatCu exactly as remote_tr50_Cu.sh;
#   * the terminal arm on cf_fix2_treatCA at detection 1.00 against NET_TARGET 5.8371628, through
#     transition_2c/cf_arm_tr2c_CAu.sh, re-solved from the ACCEPTED long-run arm (results/counterfactuals_2c/tf_pdet100_CAu,
#     pdet/remote_pdet_CAu.sh 1.00; accepted = its passes.txt says 'arm tf ACCEPTED') and required within REL_TOL 5e-3 of
#     it. The long-run run's own code/cfarm_tf_2c, if in this container, is moved aside first so the arm is re-solved;
#   * seeds: results/transition_2c_t50_Cu/loop3's price and pi_V paths rescaled onto the CA terminal
#     (rescale_seeds_CA.py, x0 the re-solved Housing First's), horizon check horizon_check_CA.py;
#   * MAX_LOOPS 2; after each archived loop report_tr50_CA.py writes the author's question (h_1 and children in a shelter
#     year by year for 15 years and at the peak, the CEV of the cohort born at the reform) into the status;
#   * newborn values on cf_kid_CA (cf_kid/build_CA.sh); everything to results/transition_2c_t50_CAu (arm files in arms/).
# remote_tr50_Cu.sh's header follows.
# remote_tr50_Cu.sh -- THE T = 50 TRANSITION FROM THE CORRECTED HOUSING FIRST (14 October; the author: yes to relaunching
# it from the corrected Housing First, code/RULE_C_PLAN.md '05:20'). remote_tr50_C.sh with four changes:
#   * Housing First (the starting steady state, and the values every cohort is compared with) is solved on
#     cf_fix2_share_treatCu: patch_treatC2's internal_computations fix ungated, and use counted as rule C counts it
#     (remote_tr50_C.sh solved it on cf_fix2_share, rule A's build). Through transition_2c/cf_arm_tr2c_Cu.sh, which
#     admits that build.
#   * the terminal arm is the corrected main column, results/decomp_2c_shares_Cu/arm_tf (done 11:37 UTC): the main arm
#     re-cleared against the corrected Housing First's net revenue, NET_TARGET 5.8371628. It counts as accepted once
#     its tf/final.txt is on the branch.
#   * REL_TOL 5e-3, the drug market's own stopping rule: remote_tr50_C.sh's 1e-3 sat inside the solver's tolerances,
#     so its re-solve, deterministic, reproduced the same 3.8e-3 and could never pass.
#   * results to results/transition_2c_t50_Cu (the loops) and results/transition_2c_Cu (the arm files).
# remote_tr50_C.sh's header follows.
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
#   * THE TERMINAL ARM never waits on a stale walk. By default (the author: "we first need the main long run
#     experiment") it starts only when the long-run arm (pdet/remote_pdet_C2.sh 0.20) is ACCEPTED, from the accepted
#     price and pi_V; the builds and the no-policy arm run meanwhile. With TF_EARLY=1 it starts at once from the
#     long-run arm's latest published pass (TF_P0 / TF_V0 when it has none), and at acceptance is kept only if its
#     latest price is within 0.5 per cent and its pi_V within 2 per cent of the accepted values, otherwise it is killed
#     and re-solved from them. Either way it must end within REL_TOL of the accepted final.txt, as before.
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
MODE=${2:-announce}
case "$MODE" in announce) MT=ann ;; grace) MT=grace ;; *) echo "usage: remote_tr70_CAann.sh 1.00|0.20 [announce|grace]"; exit 1 ;; esac
case "${1:-}" in
    1.00) TAG=${MT}100; C1R_DEF=results/counterfactuals_2c/tf_pdet100_CAbest; MAINRUN=transition_2c_t70_CAc; FALLBACK=$REPO/results/transition_2c_t70_CAb/loop0 ;;
    0.20) TAG=${MT}20; C1R_DEF=results/counterfactuals_2c/tf_pdet20_CAu; MAINRUN=transition_2c_t70_CA20e; FALLBACK= ;;
    *) echo "usage: remote_tr70_CAann.sh 1.00|0.20"; exit 1 ;;
esac
LAG=${ANNOUNCE_LAG:-5}   # announce: the screen is off for t <= LAG; grace: treatment passes it for t <= LAG
R=$REPO/results/transition_2c_t70_CA$TAG
R2=$REPO/results/transition_2c_t70_CA$TAG/arms
# 13 Oct: the paper's detection rate is 0.20 (61% of all tested users stop on impact, Mehay and Pacula); the accepted
# long-run arm at that rate is pdet/remote_pdet_C2.sh 0.20's. RULEC_PDET and C1R_OVERRIDE override both.
PDET_C=${RULEC_PDET:-$1}
C1R=${C1R_OVERRIDE:-$C1R_DEF}   # the long-run CA arm at this detection rate (the main path's)
mkdir -p "$R" "$R2"
D=$C/tr70CA${TAG}_worker
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
# 13 Oct: treatment is publicly funded in every arm (patch_treatC.py), so Housing First's net revenue, the target,
# carries its own treatment spending: treat/net_target_with_treatment.py gives 5.8918411 - 0.1332056 * 0.482685 ($9,426 a treated year)
NET_TARGET=${NET_TARGET_U:-5.8371628}   # the corrected Housing First's net revenue (results/decomp_2c_shares_Cu/arm_tf/null/final.txt)
CTEST=$(python3 -c "print('%.10f' % (35/(9e6/80)*1.589817990383))")
P_NULL=1.0001082; V_NULL=0.067533863          # results/counterfactuals_2c/nulltf/null/final.txt
REL_TOL=${REL_TOL:-1}                      # re-solved arm against the accepted one (rule A's was 2.4e-4)
POLL=${POLL:-1200}                            # seconds between looks at the branch for the acceptance (and status)
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_2c
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D.welfare_curve.dat
MAIN=$C/tr2c_t70_CA$TAG
T70=$C/tr70_CA$MT
SEEDS=$REPO/results/transition_2c_t50_Cu/loop3   # rule C's T = 50 paths, rescaled to rule CA at staging
MAX_LOOPS=${MAX_LOOPS:-6}

note() { echo "remote_tr70_CAann $PDET_C $MODE: $* ($(date -u +%H:%M))" | tee -a "$D.status"; }

if [ "${TR70ANN_DETACHED:-0}" != 1 ]; then
    if [ -f "$D.pid" ] && kill -0 "$(cat "$D.pid")" 2>/dev/null; then
        echo "remote_tr70_CAann $1 $MODE: attaching to the running worker, pid $(cat "$D.pid")"
    else
        ( TR70ANN_DETACHED=1 setsid nohup bash "$0" "$@" > /tmp/tr70_CA$TAG.detached.log 2>&1 < /dev/null &
          echo $! > "$D.pid" )
        echo "remote_tr70_CAann $1 $MODE: started detached, pid $(cat "$D.pid"); log /tmp/tr70_CA$TAG.detached.log"
    fi
    while kill -0 "$(cat "$D.pid")" 2>/dev/null; do sleep 60; done
    echo "remote_tr70_CAann $1 $MODE: finished"; cat "$D.status" 2>/dev/null
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
        echo "# the T = 70 transition on RULE CA at detection $PDET_C, $MODE ($([ $MODE = announce ] && echo "the screen off in years 1-$LAG and on from year $((LAG + 1))" || echo "treatment passes the screen in years 1-$LAG, no escape from year $((LAG + 1))")), both prices clearing along the path (code/transition_fix/remote_tr70_CAann.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D.status" 2>/dev/null
        for a in null tf; do
            L="$C/cfarm_${a}_2c/cf.log"
            [ -f "$L" ] && { echo; echo "== arm $a"; python3 "$C/cf_runs/passes.py" "$L" "$C/cf_runs/cev.py" 2>/dev/null
                             [ $a = tf ] && grep -a "MILBY SPLIT" "$L" | tail -1; }
        done
        [ -d "$MAIN" ] && { echo; echo "== tr2c_t70_CA$TAG (T = 70, rule CA, detection $PDET_C, $MODE, lag $LAG)"; tr_digest "$MAIN"; }
        [ -f "$D.ann_checked" ] && { echo; cat "$D.ann_checked"; }
        for f in "$D".report_loop*; do [ -f "$f" ] && { echo; echo "== THE AUTHOR'S QUESTION, ${f##*.report_}: does homelessness or the share of children in a shelter rise, and the reform cohort's CEV"; cat "$f"; }; done
        [ -f "$D.horizon" ] && { echo; echo "== horizon check (the last ten years against the terminal values)"; cat "$D.horizon"; }
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"
    git add "$R" "$R2" 2>/dev/null
    git commit -q -m "transition T=70 rule CA $MODE (lag $LAG, detection $PDET_C): $1$TRAILER" || return 0
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
    ( cd "$C" && env BUILD="$b" OMP_NUM_THREADS=2 "$@" sh transition_2c/cf_arm_tr2c_CAu.sh "$a" > "$C/cfarm_${a}_2c.out" 2>&1 ) &
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
accepted() { branch_file "$C1R/passes.txt" | grep -q "arm tf ACCEPTED" && branch_file "$C1R/tf/final.txt" | grep -q "drug price"; }   # CAu: the long-run arm met its tolerances
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
if [ ! -x "$C/cf_fix2_share_treatCu/hftf_cf_prod" ]; then
    note "building cf_fix2_share_treatCu (Housing First with the internal_computations fix ungated)"
    bash treat/build_share_treatCu.sh > /tmp/tr50Cu_build_shareCu.log 2>&1 || { note "GUARD: build cf_fix2_share_treatCu failed: $(tail -3 /tmp/tr50Cu_build_shareCu.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "INTERNAL UNGATED (patch_treatCu.py)" "$C/cf_fix2_share_treatCu/cf.f90" || { note "GUARD: cf_fix2_share_treatCu is not ungated"; publish "failed"; exit 1; }
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > /tmp/tr50C_build_share.log 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 /tmp/tr50C_build_share.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_fix2_treatCA/hftf_cf_prod" ]; then
    note "building cf_fix2_treatCA"
    bash treat/build_treatCA.sh > /tmp/tr50CA_build_treatCA.log 2>&1 || { note "GUARD: build cf_fix2_treatCA failed: $(tail -3 /tmp/tr50CA_build_treatCA.log | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
grep -q "RULE CA (patch_treatCA.py)" "$C/cf_fix2_treatCA/cf.f90" || { note "GUARD: cf_fix2_treatCA is not rule CA"; publish "failed"; exit 1; }
grep -q "tc2_abstain_on=0" "$C/cf_fix2_treatCA/cf.f90" || { note "GUARD: cf_fix2_treatCA has the abstention option on"; publish "failed"; exit 1; }
if [ ! -x "$T70/hftf_tr_prod" ]; then
    note "building tr70_CA$MT (build_tr70_CAann.sh, lag $LAG, $MODE)"
    bash transition_fix/build_tr70_CAann.sh "$T70" "$LAG" "$MODE" > /tmp/tr50CA_build_tr.log 2>&1 || { note "GUARD: build tr70_CAann failed: $(tail -3 /tmp/tr50CA_build_tr.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "$(tail -1 /tmp/tr50CA_build_tr.log)"
fi
grep -q "parameter :: transition_length=(1-solve_transition_dynamics)\*1+solve_transition_dynamics\*70 *$" "$T70/tr.f90" \
    || { note "GUARD: $T70 is not at T = 70"; publish "failed"; exit 1; }
grep -q "RULE CA (patch_treatCA.py)" "$T70/tr.f90" && ! grep -q "RULE C (patch_treatC.py)" "$T70/tr.f90" \
    || { note "GUARD: the transition source in $T70 is not rule CA"; publish "failed"; exit 1; }
if [ $MODE = announce ]; then
    grep -q "integer :: ann_flag_terminal=-1,ann_lag=$LAG " "$T70/tr.f90" && [ "$(grep -c 'if (time_index<=ann_lag) voucher_conditional_on_clean=0' "$T70/tr.f90")" = 2 ] \
        || { note "GUARD: the transition source in $T70 is not announced at lag $LAG"; publish "failed"; exit 1; }
else
    grep -q "integer :: grace_now=0,grace_lag=$LAG " "$T70/tr.f90" && [ "$(grep -c 'if (time_index<=grace_lag) grace_now=1' "$T70/tr.f90")" = 2 ] \
        && grep -q "if ((grace_now==1) .AND. (meets_condition_1==1)) fails_1=0" "$T70/tr.f90" \
        || { note "GUARD: the transition source in $T70 has no grace years at lag $LAG"; publish "failed"; exit 1; }
fi
# the long-run CA run (pdet/remote_pdet_CAu.sh) leaves its arm in code/cfarm_tf_2c; moved aside, so the terminal arm is
# re-solved here and compared with it rather than taken as done
# the superseded launcher already moved the long-run run's arm aside: cfarm_tf_2c is its terminal arm, kept
if [ ! -f "$D.phase1_moved" ]; then
    alive "$C/cf_point_tf_pdet100_CAu.pid" && { note "GUARD: the long-run CA solve is still running in this container"; publish "failed"; exit 1; }
    for f in cfarm_tf_2c cfarm_tf_2c.out; do [ -e "$C/$f" ] && mv "$C/$f" "$C/$f.phase1"; done
    touch "$D.phase1_moved"; note "the long-run run's cfarm_tf_2c (if any) moved to cfarm_tf_2c.phase1"
fi
publish "built"

# THE TWO ARMS. The no-policy arm as rule A's; the terminal arm from the long-run rule-C arm's latest published pass
if ! arm_ok null "VOUCHER CHECK PASS" && ! alive "$D.arm_null.pid"; then
    arm null cf_fix2_share_treatCu DRUG_PRICE_START=$P_NULL
    while [ ! -f "$C/cfarm_bench/BENCH_DONE" ] && alive "$D.arm_null.pid"; do sleep 10; done
fi
start_tf() {   # <price> <pi_V> <why>
    note "terminal arm from $3: price $1, pi_V $2"
    arm tf cf_fix2_treatCA PDET=$PDET_C NET_TARGET="$NET_TARGET" PV_START="$2" DRUG_PRICE_START="$1" DRUG_MARKET_ADJUSTER=0 EXTRA_SET="cost_per_drug_test $CTEST"
}
if ! arm_ok tf "TARGET CHECK PASS" && ! alive "$D.arm_tf.pid"; then
    if accepted; then
        PV=$(branch_file "$C1R/tf/final.txt" | awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}')
        start_tf ${PV% *} ${PV#* } "the ACCEPTED long-run rule-C arm ($C1R/tf/final.txt)"
        FROM_ACCEPTED=1
    elif [ "${TF_EARLY:-0}" = 1 ]; then
        LAST=$(branch_file "$C1R/passes.txt" | awk '/^== tf/{t=1;next} /^==/{t=0} t && $1 ~ /^[0-9]+$/ {p=$2; v=$3} END{if (p) print p, v}')
        [ -n "$LAST" ] || LAST="${TF_P0:-0.93} ${TF_V0:-0.082}"
        start_tf ${LAST% *} ${LAST#* } "the long-run rule-C arm's latest published pass (not yet accepted)"
    else
        # 13 Oct (the author: "we first need the main long run experiment"): by default nothing that depends on the
        # Treatment First equilibrium starts before $C1R is accepted; the builds and the no-policy arm go ahead
        note "terminal arm waits for $C1R to be accepted (TF_EARLY=1 would start it early from the latest pass)"
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
    [ "$(branch_file code/transition_fix/patch_$MODE.py | md5sum | cut -c1-32)" = "$(cat "$T70/patch_$MODE.md5")" ] \
        || { note "GUARD: patch_$MODE.py on the branch is not the one the build used; rebuild (rm -rf code/tr70_CA$MT) and relaunch"; publish "failed"; exit 1; }
    for p in patch_treatCA patch_treatC; do
        [ "$(branch_file code/treat/$p.py | md5sum | cut -c1-32)" = "$(cat "$T70/$p.md5")" ] \
            || { note "GUARD: $p.py on the branch is not the one the builds used; rebuild (rm -rf code/cf_fix2_treatCA code/tr70_CA code/cfarm_tf_2c*) and relaunch"; publish "failed"; exit 1; }
    done
    branch_file "$C1R/tf/final.txt" > "$R/accepted_tf_ruleC_final.txt"
    if [ ! -f "$D.arm_tf.pid" ] && ! arm_ok tf "TARGET CHECK PASS"; then
        PV=$(awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}' "$R/accepted_tf_ruleC_final.txt")
        start_tf ${PV% *} ${PV#* } "the ACCEPTED long-run rule-C arm"
        FROM_ACCEPTED=1
    fi
    if alive "$D.arm_tf.pid" && [ "${FROM_ACCEPTED:-0}" != 1 ]; then
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
note "arms: null against the corrected Housing First (decomp_2c_shares_Cu/arm_tf/null) $(python3 - "$R2/arm_null/final.txt" "$REPO/results/decomp_2c_shares_Cu/arm_tf/null/final.txt" <<'PYEOF'
import re, sys
def lv(p):
    return {m.group(1).strip(): float(m.group(2)) for m in (re.match(r'\s+(.+?)\s{2,}([-+0-9.Ee]+)(\s|$)', l) for l in open(p)) if m}
x, y = lv(sys.argv[1]), lv(sys.argv[2])
print('worst relative difference %.1e' % max(abs(x[k] / y[k] - 1) for k in ('drug price', 'drug use b', 'SUD lambda_d', 'homelessness h_1') if y.get(k)))
PYEOF
); tf against the accepted long-run CA arm $(cat "$D.tf_confirmed")"
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
    bash transition_fix/stage_tr_fix.sh "$MAIN" "$T70/hftf_tr_prod" "$C/cfarm_tf_2c" "$C/cfarm_null_2c" "$NET_TARGET" > /tmp/tr50C_stage_main.log 2>&1 || { note "GUARD: staging T = 70 failed: $(tail -3 /tmp/tr50C_stage_main.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    grep -q "seeds: T=70, 69 periods" /tmp/tr50C_stage_main.log || { note "GUARD: staging did not read T = 70: $(grep seeds /tmp/tr50C_stage_main.log)"; publish "failed"; exit 1; }
    X0=$(awk '/^ *drug price /{p=$NF} /pi_V \(voucher probability\)/{v=$NF} END{print p, v}' "$R2/arm_null/final.txt")
    python3 "$C/transition_fix/rescale_seeds_CA70.py" "$MAIN" "$SEEDS" ${X0% *} ${X0#* } > /tmp/tr50CA_seeds.log 2>&1 \
        || { note "GUARD: seeding failed: $(tail -2 /tmp/tr50CA_seeds.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    note "T = 70 staged: $(tail -2 /tmp/tr50C_stage_main.log | tr '\n' ' '); seeds rescaled from rule C's T = 50 loop3 (x0 $X0): $(tr '\n' ' ' < /tmp/tr50CA_seeds.log)"
    # THE ANNOUNCED SEEDS (see the header): the main run's latest archived loop on the branch, else the fallback, shifted
    rm -rf "$D.mainseed"; mkdir -p "$D.mainseed"; SRC=
    ( cd "$REPO" && git fetch -q origin "$BRANCH" 2>/dev/null )
    N=$(cd "$REPO" && git ls-tree --name-only FETCH_HEAD "results/$MAINRUN/" 2>/dev/null | grep -o 'loop[0-9]*$' | sed 's/loop//' | sort -n | tail -1)
    if [ -n "$N" ]; then
        for f in drug_price pi_v; do
            ( cd "$REPO" && git show "FETCH_HEAD:results/$MAINRUN/loop$N/${f}_path_seed_out.txt" ) > "$D.mainseed/${f}_path_seed_out.txt" 2>/dev/null
        done
        [ -s "$D.mainseed/drug_price_path_seed_out.txt" ] && [ -s "$D.mainseed/pi_v_path_seed_out.txt" ] && SRC="results/$MAINRUN/loop$N (from the branch)"
    fi
    if [ -z "$SRC" ] && [ -n "$FALLBACK" ] && [ -s "$FALLBACK/drug_price_path_seed_out.txt" ] && [ -s "$FALLBACK/pi_v_path_seed_out.txt" ]; then
        cp "$FALLBACK"/drug_price_path_seed_out.txt "$FALLBACK"/pi_v_path_seed_out.txt "$D.mainseed/"; SRC="${FALLBACK#$REPO/}"
    fi
    SHIFT=$LAG; [ $MODE = grace ] && SHIFT=0
    python3 "$C/transition_fix/shift_seeds_ann.py" "$MAIN" "$SHIFT" ${X0% *} ${X0#* } ${SRC:+"$D.mainseed"} > /tmp/tr70ann_seeds.log 2>&1 \
        || { note "GUARD: the announced seeds failed: $(tail -2 /tmp/tr70ann_seeds.log | tr '\n' ' ')"; publish "failed"; exit 1; }
    for f in drug_price pi_v; do cp "$MAIN/${f}_path_seed.txt" "$MAIN/${f}_path_seed.staged.txt"; done
    note "$MODE seeds: Housing First for years 1-$SHIFT, then the main path from ${SRC:-the rescaled rule-C paths} shifted $SHIFT years: $(tr '\n' ' ' < /tmp/tr70ann_seeds.log)"
fi
if [ -f "$MAIN/MAIN_EXIT" ]; then
    note "T = 70 already finished: $(cat "$MAIN/MAIN_EXIT")"
elif alive "$D.main.pid"; then
    note "T = 70 running, attaching to pid $(cat "$D.main.pid")"
else
    if [ -f "$MAIN/run.log" ]; then
        for f in drug_price pi_v; do
            [ -s "$MAIN/${f}_path_seed_out.txt" ] && cp "$MAIN/${f}_path_seed_out.txt" "$MAIN/${f}_path_seed.txt"
        done
        mv "$MAIN/run.log" "$MAIN/run.log.killed.$(date -u +%Y%m%d%H%M)"
        note "T = 70 RELAUNCH after a killed run (seeds: $(ls "$MAIN"/*_path_seed_out.txt >/dev/null 2>&1 && echo 'its last saved paths' || echo 'the staged seeds, loop 0 again'))"
    fi
    # THE HANDOVER IS CONSUMED (the binary deletes PARAM_HANDOVER.txt after reading it): restore it from staging's copy
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || cp "$MAIN/PARAM_HANDOVER.kept.txt" "$MAIN/PARAM_HANDOVER.txt" 2>/dev/null
    [ -s "$MAIN/PARAM_HANDOVER.txt" ] || { note "GUARD: no PARAM_HANDOVER.txt or .kept.txt in $MAIN"; publish "failed"; exit 1; }
    # THE FIX (see the header): the terminal arm held the drug price; the path clears it
    for h in PARAM_HANDOVER.txt PARAM_HANDOVER.kept.txt; do
        [ -f "$MAIN/$h" ] || continue
        sed -i "s|^drug_market_adjuster .*|drug_market_adjuster 0.1|" "$MAIN/$h"
        grep -qx "drug_market_adjuster 0.1" "$MAIN/$h" || echo "drug_market_adjuster 0.1" >> "$MAIN/$h"
        grep -qx "drug_market_adjuster 0.1" "$MAIN/$h" || { note "GUARD: could not set drug_market_adjuster 0.1 in $MAIN/$h"; publish "failed"; exit 1; }
    done
    if [ -z "$(swapon --show 2>/dev/null)" ] && [ "$(df -BG --output=avail "$C" | tail -1 | tr -dc 0-9)" -ge 10 ]; then
        fallocate -l 4G /var/tmp/tr70CA.swap 2>/dev/null && chmod 600 /var/tmp/tr70CA.swap && mkswap /var/tmp/tr70CA.swap >/dev/null 2>&1 \
            && swapon /var/tmp/tr70CA.swap 2>/dev/null && note "4 GiB swap on" || note "no swap (could not enable)"
    fi
    ( cd "$MAIN" && date +%s > START_EPOCH && OMP_NUM_THREADS=4 ./hftf > run.log 2>&1; echo "exit $?" > MAIN_EXIT ) &
    echo $! > "$D.main.pid"
    note "T = 70 transition started, pid $(cat "$D.main.pid")"
    for _ in $(seq 1 60); do grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    grep -q -a "HANDOVER" "$MAIN/run.log" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the run printed no HANDOVER line in five minutes; killed"; publish "failed"; exit 1; }
    note "handover applied: $(grep -a -c '^ HANDOVER' "$MAIN/run.log") parameters"
    for _ in $(seq 1 24); do grep -q -a "HANDOVER drug_market_adjuster" "$MAIN/run.log" 2>/dev/null && break; sleep 5; done
    ADJ=$(grep -a "HANDOVER drug_market_adjuster" "$MAIN/run.log" 2>/dev/null | tail -1 | awk '{print $NF}')
    python3 -c "import sys; sys.exit(0 if float('${ADJ:-0}') > 0 else 1)" 2>/dev/null || {
        pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
        note "GUARD: the path read drug_market_adjuster '${ADJ:-none}', so its drug price would be held: killed"; publish "failed"; exit 1; }
    note "the path's drug price clears: HANDOVER drug_market_adjuster -> $ADJ"
fi
publish "T = 70 running"

# the forward pass's TRANSITION ANNOUNCE (or GRACE) lines: 'wait' until year LAG+1 is printed, then 'ok' or 'bad'
ann_check() {
    python3 - "$MAIN/run.log" "$LAG" "$MODE" <<'PYEOF'
import re, sys
lag, mode = int(sys.argv[2]), sys.argv[3]
if mode == 'announce':
    pat = r'TRANSITION ANNOUNCE t=\s*(\d+)\s+screen=\s*(-?\d+)\s+lag=\s*(\d+)\s+terminal=\s*(-?\d+)'
    want = lambda t: (0 if t <= lag else 1, lag, 1)
    say = f'screen 0 in years 1-{lag}, 1 from year {lag + 1}, terminal 1'
else:
    pat = r'TRANSITION GRACE t=\s*(\d+)\s+grace=\s*(-?\d+)\s+lag=\s*(\d+)\s+screen=\s*(-?\d+)'
    want = lambda t: (1 if t <= lag else 0, lag, 1)
    say = f'treatment passes in years 1-{lag}, not from year {lag + 1}, the screen on throughout'
rows = [tuple(map(int, m.groups())) for m in (re.search(pat, l) for l in open(sys.argv[1], errors='replace')) if m]
if not any(r[0] == lag + 1 for r in rows):
    print('wait'); sys.exit(0)
bad = [r for r in rows if r[1:] != want(r[0])]
print(f'bad {bad[:3]}' if bad else f'ok, {len(rows)} lines: {say}')
PYEOF
}
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
    # THE SCHEDULE GUARD: once the forward pass has printed year LAG+1, the year-by-year rule must be the one asked for
    if [ ! -f "$D.ann_checked" ]; then
        A=$(ann_check)
        case "$A" in
            ok*) echo "$MODE checked on the forward pass: $A" > "$D.ann_checked"; note "$MODE checked: $A" ;;
            bad*) pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
                  note "GUARD: the $MODE schedule is not the one asked for (lag $LAG): $A; killed"; publish "failed"; exit 1 ;;
        esac
    fi
    last=$(grep -a -o 'TRANSITION PATHS SAVED after loop *[0-9]*' "$MAIN/run.log" 2>/dev/null | tail -1 | grep -o '[0-9]*$')
    if [ -n "$last" ] && [ "$last" -gt "$archived" ]; then
        L=$((last + OFF))
        mkdir -p "$R/loop$L"
        gzip -c "$MAIN/run.log" > "$R/loop$L/run.log.gz"
        cp "$MAIN"/*_path_seed_out.txt "$R/loop$L/" 2>/dev/null
        cp "$MAIN"/welfare_curvebaseline_benchmark.dat "$R/loop$L/" 2>/dev/null
        archived=$last
        echo "loop$L: $(python3 "$C/transition_fix/horizon_check_CA.py" "$R/loop$L" "$MAIN" 2>&1 | tail -1)" >> "$D.horizon"
        DETECTION=$PDET_C RUN_LABEL="$MODE, lag $LAG" python3 "$C/transition_fix/report_tr70_CAann.py" "$R/loop$L/run.log.gz" "$R2/arm_null" "$R2/arm_tf" "$R/loop$L/welfare_curvebaseline_benchmark.dat" > "$D.report_loop$L" 2>&1
        cp "$D.report_loop$L" "$R/loop$L/report.txt"
        note "binary loop $last complete, archived to results/transition_2c_t70_CA$TAG/loop$L; $(tail -1 "$D.horizon"); $(grep -m1 'PEAK homelessness' "$D.report_loop$L"); $(grep -m1 'CEV OF THE COHORT' "$D.report_loop$L")"
        if [ "$((L + 1))" -ge "$MAX_LOOPS" ]; then
            note "loop$L archived ($MAX_LOOPS loops): stopping the binary"
            pkill -P "$(cat "$D.main.pid")" 2>/dev/null; kill "$(cat "$D.main.pid")" 2>/dev/null
            sleep 5
            echo "stopped after $MAX_LOOPS loops" > "$MAIN/MAIN_EXIT"
            break
        fi
    fi
    publish "T = 70 running"
done
gzip -c "$MAIN/run.log" > "$R/run_final.log.gz"
note "T = 70 transition ended: $(cat "$MAIN/MAIN_EXIT" 2>/dev/null)"
publish "T = 70 rule CA ended"

# NO NEWBORN STEP: the arms are the main path's, whose newborn values are in results/transition_2c_t70_CAc and _CA20e
