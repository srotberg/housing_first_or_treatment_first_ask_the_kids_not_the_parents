#!/usr/bin/env python3
"""Generate code/cf_kid/cf.f90 = code/cf_fix2/cf.f90 + the cf_kid additions.

Two changes, both asserted to land exactly once:
  1. a hook in long_run_counter_factual, after every initialiser and before the
     loop: the cf_kid binary computes the newborn's value from the arm's SAVED
     equilibrium instead of solving (child_value_from_saved_equilibrium ends with
     STOP, so nothing after the hook runs and nothing is saved over the arm);
  2. cf_kid_additions.f90 appended after the last subroutine.
The model itself is untouched: the diff against cf_fix2 is the hook plus the
appended block, and build.sh checks that.
"""
import sys, os

here = os.path.dirname(os.path.abspath(__file__))
src = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "cf_fix2", "cf.f90")
dst = sys.argv[2] if len(sys.argv) > 2 else os.path.join(here, "cf.f90")
add = open(os.path.join(here, "cf_kid_additions.f90")).read()

s = open(src).read()

anchor = "        distance_counterfactual_moments=1\n"
assert s.count(anchor) == 1, ("hook anchor not unique", s.count(anchor))
hook = ("        ! >>> CF_KID HOOK (code/cf_kid): value every newborn from the arm's saved equilibrium\n"
        "        ! instead of solving. Everything above has set the economy up exactly as the arm's\n"
        "        ! own run did; the routine reads the saved functions and stops. <<<\n"
        "        call child_value_from_saved_equilibrium(transition_length)\n")
s = s.replace(anchor, hook + anchor)

assert "child_value_from_saved_equilibrium(time_period)" not in open(src).read()
if not s.endswith("\n"):
    s += "\n"
s += add

open(dst, "w").write(s)
print("generated", dst)
