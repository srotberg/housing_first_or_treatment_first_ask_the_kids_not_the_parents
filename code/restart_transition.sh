#!/bin/bash
# restart_transition.sh <run dir>
#
# Promotes the TWO instrument paths a running transition writes every loop to
# the two seed files the next run reads, so a restart resumes from the latest
# guesses instead of from the seed it started on.
#
# THE TRANSITION SOLVES FOR EXACTLY TWO OBJECTS. The author, 21 September:
# "rent and housing price and lump sum transfer are not equilibrium objects,
# they are constant", and "i can only think of 2: pi_v and p_v". The source
# agrees: peg_prices_in_counterfactual=1 sets housing_price to
# calibrated_stationary_housing_price and rent to rent_calibrated in every
# period and ZEROES their distances, so two of the four stopping rules are
# satisfied by construction and never bind; lump_sum_transfer is never assigned
# inside the loop at all. An earlier version of this script promoted all five,
# on a reading of an elseif branch the peg makes dead. Promoting a constant is
# noise; feeding it back through a reader is worse, because loop 0's BACKWARD
# pass would use it before the peg is re-imposed.
#
# Aggregate homelessness is not here for the same reason, and it is the
# author's point too: once pi_v and the drug price clear, h_1 is whatever the
# distribution makes it and feeds the welfare calculation. It is written every
# loop as a reference to score a restart against, never read back.
#
# WHY THIS IS A SCRIPT AND NOT AUTOMATIC. The writer deliberately does NOT
# overwrite the seed files it read. t30_loop1_pivcollapse is the reason: pi_v
# went through zero to its floor in every period in one step, h_1 went to NaN,
# and as a file that is 29 plausible decimals. A run that automatically
# inherited its own last loop would have inherited that. So promotion is a
# deliberate act, and this script is where the guards live.
#
# The Fortran readers guard too -- pi_v on a bound is refused, a house price or
# rent at or below zero is refused, a short file keeps the ramp for the periods
# it could not read -- but a guard that fires after four hours of staging is
# worth firing here instead.
set -e
N=${1:?usage: restart_transition.sh <run dir>}
[ -d "$N" ] || { echo "REFUSING: no run dir at $N"; exit 1; }
cd "$N"

PAIRS="drug_price_path_seed pi_v_path_seed"

# NOTHING IS PROMOTED UNTIL EVERYTHING HAS BEEN CHECKED. A half-promoted set --
# a new price path against an old pi_v path -- is a state no loop ever produced
# and is worse than either.
bad=0
for b in $PAIRS; do
  f="${b}_out.txt"
  if [ ! -f "$f" ]; then echo "  MISSING $f"; bad=1; continue; fi
  n=$(grep -cv '^[[:space:]]*\(#\|$\)' "$f" || true)
  if [ "$n" -eq 0 ]; then echo "  EMPTY $f"; bad=1; continue; fi
  if grep -qi 'nan\|infinity' "$f"; then echo "  NaN or Infinity in $f"; bad=1; continue; fi
  case "$b" in
    pi_v_path_seed)
      if awk '!/^[[:space:]]*(#|$)/ {if ($1+0 <= 0.000010000011 || $1+0 >= 0.999999) exit 1}' "$f"; then :; else
        echo "  $f has an entry on a bound -- this is the collapse the clip exists to stop"; bad=1; fi ;;
    drug_price_path_seed)
      if awk '!/^[[:space:]]*(#|$)/ {if ($1+0 <= 0) exit 1}' "$f"; then :; else
        echo "  $f has a non-positive entry"; bad=1; fi ;;
  esac
  echo "  ok $f  ($n entries, loop $(grep -m1 'after loop' "$f" | awk '{print $NF}'))"
done

[ "$bad" -eq 0 ] || { echo; echo "REFUSING to promote: fix or delete the files above."; exit 1; }

# THE HANDOVER MUST BE PUT BACK FIRST. The binary DELETES PARAM_HANDOVER.txt as
# it starts, which is why stage_transition.sh keeps a copy as .kept.txt. Without
# it a restart runs on the declared defaults: is_counterfactual's file_number
# becomes 'counter_arm', nothing it opens exists, and it dies at the first read
# with "Cannot open file 'total_rental_supplycounter_arm.dat'". Measured, 09:48.
if [ -f PARAM_HANDOVER.kept.txt ]; then
  cp PARAM_HANDOVER.kept.txt PARAM_HANDOVER.txt
  echo "restored PARAM_HANDOVER.txt from .kept.txt"
else
  echo "REFUSING: no PARAM_HANDOVER.kept.txt. A restart without the handover runs"
  echo "  on declared defaults and dies at the first counter_arm file. Re-stage."
  exit 1
fi

echo
for b in $PAIRS; do
  [ -f "${b}.txt" ] && cp "${b}.txt" "${b}.previous.txt"
  cp "${b}_out.txt" "${b}.txt"
  echo "promoted ${b}_out.txt -> ${b}.txt"
done
echo
echo "the previous seeds are kept as *_path_seed.previous.txt"
echo
# LAUNCH IT OUTSIDE THE SESSION, OR THE NEXT SESSION RESTART TAKES IT WITH IT.
#
# The 09:46 kill on 21 September was NOT a machine reboot -- kernel uptime was
# continuous across it. The platform recycled the SESSION, and the solve died
# because it sat four levels under environment-manager and shared its session
# id. A plain ./hftf, or nohup ./hftf &, or ./hftf & disown, all keep that
# session id: disown removes the job from the shell'"'"'s table, not the process
# from the session. Only setsid gives the process its own session and reparents
# it to init, which a session recycle cannot reach.
#
# Verified before relying on it: a setsid probe came up with ppid 1 and its own
# sid, against the in-session solve'"'"'s sid of its launching shell.
#
# The cost is that the harness no longer tracks it, so completion has to be
# polled for. The log and the per-loop *_out.txt files are the real record
# anyway, and surviving a restart is worth more than a notification.
echo "restart with:"
echo "    cd $N && setsid ./hftf > run.log 2> run.err < /dev/null &"
echo
echo "then check it detached:  ps -o pid=,ppid=,sid= -p \$(pgrep -x hftf)"
echo "  ppid must be 1 and sid must be its own pid."
