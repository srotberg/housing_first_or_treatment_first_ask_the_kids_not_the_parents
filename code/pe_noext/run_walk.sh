#!/bin/bash
# run_walk.sh -- the consumption-equivalent walk on Arm A (patch_walk.py) and the analysis (analyse.py).
# Waits for Arm A (run_pe.sh), runs the walk in code/pe_walk_A beside Arm B, then, when both arms are
# done, writes results/pe_noext/analysis.txt and analysis.json. Detached; re-running attaches.
#   bash code/pe_noext/run_walk.sh
# The walk build is tested on the benchmark (code/pe_walk_test): against the benchmark binary's own
# welfare curve the adult value moves +2.6011 (curve +2.6012) at x = +0.05 and -2.7883 (-2.7880) at -0.05.
set -u
C=$(cd "$(dirname "$0")/.." && pwd)
W=$C/pe_noext/work; R=$C/../results/pe_noext
D=$C/pe_walk_A
XS="-0.5 -0.3 -0.2 -0.15 -0.1 -0.07 -0.05 -0.03 -0.02 -0.01 -0.005 -0.002 -0.0005 0.0 0.0005 0.002 0.005 0.01 0.02 0.05 0.1"
note() { echo "run_walk: $* ($(date -u '+%d %b %H:%M'))" | tee -a "$W/walk.status"; }
alive() { [ -f "$1" ] && kill -0 "$(cat "$1")" 2>/dev/null; }

if [ "${WALK_DETACHED:-0}" != 1 ]; then
    if alive "$W/walk.pid"; then echo "attached to pid $(cat "$W/walk.pid")"; else
        ( WALK_DETACHED=1 setsid nohup bash "$0" > "$W/walk.detached.log" 2>&1 < /dev/null & echo $! > "$W/walk.pid" )
        echo "started detached, pid $(cat "$W/walk.pid")"
    fi
    exit 0
fi

[ -x "$C/cf_walk/hftf_cf_prod" ] || { note "GUARD: cf_walk not built (patch_walk.py on cf_fix2_share_pe)"; exit 1; }
note "waiting for arm A"
until grep -q "arm A's last solve used" "$W/pe.status" 2>/dev/null; do
    grep -q "GUARD" "$W/pe.status" 2>/dev/null && { note "arm A failed; stopping"; exit 1; }
    sleep 60
done
P_A=$(grep "arm A's last solve used" "$W/pe.status" | tail -n 1 | sed 's/.*drug price \([^,]*\),.*/\1/')
python3 -c "float('$P_A')" || { note "GUARD: cannot read p_A"; exit 1; }

if ! grep -aq "PE WALK done" "$D/walk.log" 2>/dev/null; then
    note "walk on arm A's policies at drug price $P_A, x in {$XS}"
    rm -rf "$D" && cp -a "$C/cfarm_null_pe_noext" "$D" && cd "$D"
    rm -f walk_V*.bin
    cp PARAM_HANDOVER.arm.txt PARAM_HANDOVER.txt
    sed -i "s/^drug_price_start .*/drug_price_start $P_A/" PARAM_HANDOVER.txt
    grep -qx "drug_price_start $P_A" PARAM_HANDOVER.txt || { note "GUARD: drug_price_start not set"; exit 1; }
    set -- $XS; { echo $#; for x in "$@"; do echo "$x"; done; } > pe_walk.dat
    cp "$C/cf_walk/hftf_cf_prod" ./hftf_walk
    OMP_NUM_THREADS=2 ./hftf_walk > walk.log 2> walk.err
    grep -aq "PE WALK done" walk.log || { note "GUARD: the walk did not finish: $(tail -n 3 walk.err | tr '\n' ' ')"; exit 1; }
    note "walk done: $(grep -a 'PE WALK prices' walk.log | tr -s ' ')"
fi

note "waiting for arm B"
until [ -f "$W/ARMS_DONE" ]; do
    grep -q "GUARD" "$W/pe.status" 2>/dev/null && { note "an arm failed; stopping"; exit 1; }
    sleep 60
done
cd "$C"
python3 pe_noext/analyse.py cfarm_null_pe_noext cfarm_tf_pe_noext pe_walk_A --json "$R/analysis.json" > "$R/analysis.txt" 2>&1 \
    && note "analysis written" || note "GUARD: analysis failed: $(tail -n 3 "$R/analysis.txt" | tr '\n' ' ')"
touch "$W/WALK_DONE"
