#!/bin/bash
# run_all_CA20.sh -- A COPY of run_all_CA100.sh at detection 0.20 (17 October; the author: "I want to launch
# both because I want to see if homelessness rises with 20% detection and no escape"): every CA100 name is CA20 and the
# detection default 0.20, so nothing here touches the detection-1.00 results. The original follows.
# run_all_CA20.sh -- COPY of run_all_C.sh (16 October) for the Costantini comparison under the CA rule at detection 0.20: Treatment
# First on cf_fix2_treatCA (treat/build_treatCA.sh, rule A's screen on rule C's build) at PDET 1.00, Housing First the
# CORRECTED one (cf_fix2_share_treatCu, internal_computations fix ungated; NET_TARGET 5.8371628), arms
# cfarm_null_2c_CA20 and cfarm_tf_2c_fixboth_CA20, work directories work_CA20, results to results/revoked_2c_CA20
# and results/revoked_2c_street_CA20. Otherwise the original, which follows.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/revoked_2c/run_all_CA20.sh
# run_all_C.sh -- THE REVOKED-VOUCHER VALIDATION ON RULE C, START TO END, IN ONE CONTAINER (13 October; detection 0.20,
# run_arms_C.sh's default, RULEC_PDET overrides). The pipeline is five scripts that used to be started by hand in order;
# this starts them in that order: gfortran; revoked_2c/build_C.sh and revoked_2c_street/build_C.sh in the background
# (pids in work_C/build.pid, which the paths scripts wait on) with revoked_2c/run_arms_C.sh beside them; once
# revoked_2c's build has succeeded, revoked_2c/run_paths_C.sh; once the street build has succeeded,
# revoked_2c_street/run_paths_C.sh (which itself waits for revoked_2c's PATHS_DONE). Each of those publishes its own
# status to results/revoked_2c_CA20 and results/revoked_2c_street_C; this script publishes only a failed build, to
# results/revoked_2c_CA20/all_status.txt. Detached; re-running it attaches. Finishes when the street pipeline does.
# START IT WITH THE BASH TOOL'S run_in_background=true from the repo root:  bash code/revoked_2c/run_all_C.sh
set -u
BRANCH=claude/two-period-addiction-hazard-d7gb61
R=$(cd "$(dirname "$0")" && pwd); C=$(cd "$R/.." && pwd); REPO=$(cd "$C/.." && pwd)
W=$R/work_CA20; WS=$C/revoked_2c_street/work_CA20; mkdir -p "$W" "$WS"
printf "*\n" > "$W/.gitignore"; printf "*\n" > "$WS/.gitignore"
TRAILER=$'\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>\nClaude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv'
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }
if [ "${ALLC_DETACHED:-0}" != 1 ]; then
    if alive "$W/all.pid"; then
        echo "run_all_CA20: attaching to the running pipeline, pid $(cat "$W/all.pid")"
    else
        ( ALLC_DETACHED=1 setsid nohup bash "$0" > "$W/all.detached.log" 2>&1 < /dev/null & echo $! > "$W/all.pid" )
        echo "run_all_CA20: started detached, pid $(cat "$W/all.pid")"
    fi
    while alive "$W/all.pid"; do sleep 60; done
    echo "run_all_CA20: finished"; tail -n 3 "$W/all.log" 2>/dev/null
    exit 0
fi
log() { echo "run_all_CA20: $* ($(date -u +%H:%M))" | tee -a "$W/all.log"; }
fail() {   # <message>: publish the failure and stop
    log "GUARD: $1"
    mkdir -p "$REPO/results/revoked_2c_CA20"; cp "$W/all.log" "$REPO/results/revoked_2c_CA20/all_status.txt"
    ( cd "$REPO" && git add results/revoked_2c_CA20/all_status.txt && git commit -q -m "revoked 2c rule CA det 0.20: $1$TRAILER" && \
      for i in 1 2 3 4; do git fetch -q origin "$BRANCH" && git rebase -q -X theirs FETCH_HEAD && git push -q origin HEAD:"$BRANCH" && break; sleep $((2 ** i)); done )
    exit 1
}
command -v gfortran >/dev/null 2>&1 || { log "installing gfortran"; apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq gfortran >/dev/null 2>&1; }
command -v gfortran >/dev/null || fail "no gfortran"
build() {   # <work dir> <build script>: in the background, pid where run_paths_CA20.sh looks for it
    [ -f "$1/BUILT" ] && return 0
    alive "$1/build.pid" && return 0
    ( bash "$2" > "$1/build.log" 2>&1 && touch "$1/BUILT" ) &
    echo $! > "$1/build.pid"
}
build "$W" "$R/build_CA20.sh"
build "$WS" "$C/revoked_2c_street/build_CA20.sh"
log "builds started; arms: $(bash "$R/run_arms_CA20.sh" > /dev/null 2>&1 & echo started)"
while alive "$W/build.pid"; do sleep 30; done
[ -f "$W/BUILT" ] || fail "revoked_2c/build_CA20.sh failed: $(tail -n 3 "$W/build.log" | tr '\n' ' ')"
log "revoked_2c built; paths: $(bash "$R/run_paths_CA20.sh" > /dev/null 2>&1 & echo started)"
while alive "$WS/build.pid"; do sleep 30; done
[ -f "$WS/BUILT" ] || fail "revoked_2c_street/build_CA20.sh failed: $(tail -n 3 "$WS/build.log" | tr '\n' ' ')"
log "revoked_2c_street built; street paths: $(bash "$C/revoked_2c_street/run_paths_CA20.sh" > /dev/null 2>&1 & echo started)"
sleep 120
while alive "$WS/paths.pid" || alive "$W/paths.pid" || alive "$W/arms.pid"; do sleep 60; done
log "done: revoked_2c $( [ -f "$W/PATHS_DONE" ] && echo PATHS_DONE || echo 'no PATHS_DONE' ), street $( [ -f "$WS/PATHS_DONE" ] && echo PATHS_DONE || echo 'no PATHS_DONE' )"
