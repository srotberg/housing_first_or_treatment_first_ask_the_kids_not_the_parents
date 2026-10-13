#!/bin/bash
# run_flows.sh -- the Housing First benchmark re-solved on cf_flows (cf_fix2_share plus code/bcghw/patch_flows.py, which
# is print-only), for two untargeted checks against Beauregard, Couture, Green, Hicks and Warburton (2026), "Pathways
# into Homelessness" (13 October; the author: "yes, try to incorporate what could be used in that paper"):
#   * entry into homelessness with and without a SUD (theirs: hazard ratio 4.56 for a long-standing SUD, Table 1);
#   * the share of new entrants still homeless a year later (theirs: about 25 per cent, Figure E.9).
# The no-policy arm as the transitions run it (cf_fix2_share, the benchmark's own price and pi_V), so its passes
# converge on the benchmark the validation table describes. Results: results/bcghw_flows/{status.txt,flows.txt,cf.log.gz}.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/bcghw/run_flows.sh
# Re-running attaches to the running worker. Status every 20 minutes.
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
C=$(cd "$(dirname "$0")/.." && pwd); REPO=$(cd "$C/.." && pwd)
R=$REPO/results/bcghw_flows; D=$C/bcghw/work; mkdir -p "$R" "$D"
REF=$REPO/results/reference/hf_2c_omega_0.085
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
export BENCH_FROM=$REF BENCH_B=0.0054222 BENCH_OMEGA=0.085 BENCH_KU=1.0 KAPPA_X=0.9342362271804227
export SEED_FROM=bench DIAG_TAG=_flows
export PASSES_BASE="0.089562893104297908,0.038113117586549894,0.0061835672543113307"
export CEV_CURVE=$D/welfare_curve.dat
P_NULL=1.0001082
ARMDIR=$C/cfarm_null_flows
note() { echo "run_flows: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$D/status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${FLOWS_DETACHED:-0}" != 1 ]; then
    if alive "$D/run.pid"; then echo "run_flows: attaching to pid $(cat "$D/run.pid")"; else
        ( FLOWS_DETACHED=1 setsid nohup bash "$0" > "$D/detached.log" 2>&1 < /dev/null & echo $! > "$D/run.pid" )
        echo "run_flows: started detached, pid $(cat "$D/run.pid")"
    fi
    while alive "$D/run.pid"; do sleep 60; done
    echo "run_flows: finished"; cat "$D/status" 2>/dev/null
    exit 0
fi

publish() (
    {
        echo "# Housing First benchmark with the FLOWS print, against Beauregard et al. (2026) (code/bcghw/run_flows.sh); $(date -u '+%d %b %H:%M UTC')"
        cat "$D/status" 2>/dev/null
        if [ -f "$ARMDIR/cf.log" ]; then
            echo; echo "== passes"; ( cd "$C" && python3 cf_runs/passes.py "$ARMDIR/cf.log" cf_runs/cev.py 2>/dev/null )
            echo; echo "== flows"; python3 "$C/bcghw/flows_digest.py" "$ARMDIR/cf.log"
        fi
        true
    } > "$R/status.txt.tmp"; mv "$R/status.txt.tmp" "$R/status.txt"
    cd "$REPO"; git add "$R" 2>/dev/null
    git commit -q -m "bcghw flows: $1$TRAILER" || return 0
    for i in 1 2 3 4; do
        git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && return 0
        git rebase --abort 2>/dev/null; sleep $((2 ** i))
    done
    note "push failed after 4 tries"
)

: > "$D/status"
command -v gfortran >/dev/null 2>&1 || { note "gfortran missing, installing"; apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || { note "GUARD: no gfortran"; publish "failed"; exit 1; }
python3 -c "import numpy" 2>/dev/null || pip install -q numpy >/dev/null 2>&1
gunzip -c "$REF/files/welfare_curvebaseline_benchmark.dat.gz" > "$CEV_CURVE"
note "free disk $(df -h "$C" | tail -1 | awk '{print $4}'), memory $(free -g | awk '/Mem/{print $2}') GiB, cores $(nproc)"
cd "$C"
for b in cf_fix cf_fix2; do
    [ -x "$C/$b/hftf_cf_prod" ] && continue
    note "building $b"
    bash "cf_runs/build_$b.sh" > "$D/build_$b.log" 2>&1 || { note "GUARD: build $b failed: $(tail -3 "$D/build_$b.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
done
if [ ! -x "$C/cf_fix2_share/hftf_cf_prod" ]; then
    note "building cf_fix2_share"
    bash transition_fix/build_cf_fix2_share.sh > "$D/build_share.log" 2>&1 || { note "GUARD: build cf_fix2_share failed: $(tail -3 "$D/build_share.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
if [ ! -x "$C/cf_flows/hftf_cf_prod" ]; then
    note "building cf_flows (patch_flows.py on cf_fix2_share)"
    mkdir -p "$C/cf_flows"
    python3 bcghw/patch_flows.py cf_fix2_share/cf.f90 cf_flows/cf.f90 > "$D/build_flows.log" 2>&1 || { note "GUARD: patch failed: $(tail -3 "$D/build_flows.log" | tr '\n' ' ')"; publish "failed"; exit 1; }
    ( cd "$C/cf_flows" && gfortran -O3 -funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium cf.f90 -o hftf_cf_prod 2> build_prod.err )
    [ -x "$C/cf_flows/hftf_cf_prod" ] || { note "GUARD: cf_flows did not compile: $(grep -m2 Error "$C/cf_flows/build_prod.err" | tr '\n' ' ')"; publish "failed"; exit 1; }
fi
publish "built"
if ! { [ -f "$C/cfarm_null_flows.out" ] && tail -5 "$C/cfarm_null_flows.out" | grep -q "DIST CHECK PASS"; }; then
    note "arm null on cf_flows (the benchmark's price $P_NULL and pi_V), 4 threads"
    ( env BUILD=cf_flows OMP_NUM_THREADS=4 DRUG_PRICE_START=$P_NULL sh bcghw/cf_arm_flows.sh null > "$C/cfarm_null_flows.out" 2>&1 ) &
    echo $! > "$D/arm.pid"
    while alive "$D/arm.pid"; do
        for _ in $(seq 1 120); do alive "$D/arm.pid" || break; sleep 10; done
        publish "running, $(grep -ac 'CF MOMENTS' "$ARMDIR/cf.log" 2>/dev/null) passes"
    done
fi
tail -5 "$C/cfarm_null_flows.out" | grep -q "DIST CHECK PASS" && grep -q "VOUCHER CHECK PASS" "$C/cfarm_null_flows.out" && ! grep -q GUARD "$C/cfarm_null_flows.out" \
    || { note "GUARD: the arm failed its checks: $(grep -a GUARD "$C/cfarm_null_flows.out" | head -2 | tr '\n' ' ')$(tail -2 "$C/cfarm_null_flows.out" | tr '\n' ' ')"; publish "failed"; exit 1; }
python3 bcghw/flows_digest.py "$ARMDIR/cf.log" > "$R/flows.txt"
gzip -c "$ARMDIR/cf.log" > "$R/cf.log.gz"
note "done: $(grep -c '^pass' "$R/flows.txt") passes; the last is the converged benchmark"
publish "done"
