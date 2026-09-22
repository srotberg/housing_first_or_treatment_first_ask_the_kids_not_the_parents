#!/usr/bin/env python3
"""Configure the one-class, omega_c=0 calibration with SMI made exogenous.

    patch_oneclass_smi.py <master .f90> <output .f90>

FIVE EDITS, each anchored on its full declaration line so a drifted source
fails loudly rather than being patched in the wrong place.

  child_penalty_classes 2 -> 1   the one-class model. employment_grid_size is
                                 employment_base_size*child_penalty_classes, so
                                 the employment dimension goes 26 -> 13 and the
                                 distribution array halves. NOTE this makes the
                                 two-class warm start unloadable: the shape
                                 stamp will not match and the reader refuses it.
  weight_on_child  0.0137 -> 0   omega_c off for this pass.
  omega_c_is_pinned     0 -> 1   pins omega_c AND zeroes distance_weight_on_child,
                                 so the do-while term retires and a loop costs
                                 one solve rather than two.
  iota_smi            2.0 -> 1.0 removes SUD -> higher SMI onset. SMI becomes a
                                 pure exogenous age-Markov state, which is what
                                 makes an SMI-specific preference parameter
                                 well posed rather than a preference that
                                 responds to the agent's own choices.
  mu_m               0.82 -> 1.0 removes the SMI penalty on SUD recovery.

WHAT IS DELIBERATELY NOT CHANGED, and it would hang the run:

  calibrate_weight_on_child STAYS 1. Setting it to 0 takes none of the branches
  that assign distance_weight_on_child, so the distance keeps its initial 1,
  the do-while has no iteration cap, and the loop never converges. ENGINE.md
  records this bug class: a bracket with a zero adjuster and a live distance
  cannot converge. omega_c_is_pinned is the correct switch.

  penalty_child_addicted is already 0.24 and freeze_all_but_omega_c already 0.

COST OF THE ONE-CLASS MODEL, from the declaration comment at 6118: at one class
delta_d lands in the BIRTH SHIFT and erodes at persistence_employment_surviving
= 0.9, so the child penalty has largely decayed before the child is at risk.
That is why two classes were introduced on 16 September. delta_d is inert here,
which is consistent with omega_c = 0 and this pass not targeting the child.
"""
import sys

EDITS = [
    ("integer, parameter :: child_penalty_classes=2",
     "integer, parameter :: child_penalty_classes=1"),
    ("real(8) :: weight_on_child=0.0137",
     "real(8) :: weight_on_child=0.d0"),
    ("integer :: omega_c_is_pinned=0",
     "integer :: omega_c_is_pinned=1"),
    ("real(8), parameter :: iota_smi=2.0",
     "real(8), parameter :: iota_smi=1.0"),
    ("real(8), parameter :: mu_m=0.82",
     "real(8), parameter :: mu_m=1.0"),
]

src = open(sys.argv[1]).read()
for old, new in EDITS:
    n = src.count(old)
    if n != 1:
        sys.exit("REFUSED: %r appears %d times, expected exactly 1" % (old, n))
    src = src.replace(old, new)

# the guard: this must NOT have been touched
if "integer, parameter :: calibrate_weight_on_child=1" not in src:
    sys.exit("REFUSED: calibrate_weight_on_child is not 1; turning it off hangs the do-while")

open(sys.argv[2], "w").write(src)
print("applied %d edits; calibrate_weight_on_child confirmed still 1" % len(EDITS))
