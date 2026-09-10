#!/usr/bin/env python3
"""Generate a VARIANT of the model source, without touching the master.

    python3 code/make_variant.py save   ->  code/variant_save.f90
    python3 code/make_variant.py cf     ->  code/variant_cf.f90

WHY A GENERATED COPY AND NOT A HANDOVER PARAMETER. The two switches these
variants need -- is_counterfactual and the sweep's early stop -- are compile
time. is_counterfactual in particular initialises seven other `parameter`
declarations (1650, 1797, 2114, 2116, 2245, 2953, 4365, 4376), so making it a
runtime variable cascades through all of them. A build time substitution costs
one file and leaves the master byte identical, which is what keeps the point
archive valid: the tag is the md5 of the vector and the MODEL stamp is the md5
of the master source, so a variant that edited the master would reset every
point in points/ for a run that is not a calibration point at all.

EVERY PATCH ASSERTS ITS MATCH COUNT. A sed that silently matches nothing is
exactly how a variant ends up being the unmodified model wearing a new name,
and the run would still produce numbers.
"""
import io, sys, os, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = os.path.join(HERE, "housing_first_or_treatment_first_SR_v1.f90")


def patch(text, old, new, label, expect=1):
    n = text.count(old)
    if n != expect:
        raise SystemExit(f"PATCH FAILED [{label}]: matched {n} times, expected {expect}")
    return text.replace(old, new)


# ---------------------------------------------------------------- save
# The point run stops inside `if (sweep_addiction_scalar==1)` immediately after
# the moments, so it never reaches save_vars_and_functions at the end of
# calibrating_model and writes no *baseline_benchmark.dat. The counterfactual
# needs those files: median_income to freeze the voucher threshold at,
# govt_revenues_to_use_in_tests as its budget constraint, and
# average_labor_income_by_employment to refill the zeroed profile that the STOP
# at ~29464 guards.
#
# THE STATE IS NOW SAVED AFTER THE FROZEN EQUILIBRIUM CONVERGES, WHICH IS A
# CHANGE, and the old reasoning is kept here because it was right about the
# thing it was worried about and wrong about the remedy.
#
# It used to save at the sweep's stop, on the ground that
# re_do_simulation_with_fixed_parameters does NOT freeze everything --
# sd_permanent_productivity kept moving pass by pass, and participation at a
# fixed b drifted 0.3326, 0.3244, 0.3327 across three passes -- so letting the
# loop keep going would write a state that is not the state the reported moments
# came from.
#
# The missing distinction is between the CALIBRATION map and the EQUILIBRIUM
# map. The worry was about the first: re-entering the calibration update block
# moves calibrated parameters, and then the saved state belongs to a different
# vector. The remedy was to stop iterating at all, which left the saved state at
# one iterate of a search --- distance_average_labor_income at 1.8281e-2 against
# a rule of 1e-4, a hundred and eighty-three times its tolerance.
#
# The Fortran now iterates the EQUILIBRIUM map only, at frozen parameters, until
# the moments stop moving, and saves after that. No calibrated parameter can
# move, because the calibration update block is never re-entered.
SAVE = [
    ("""                call print_all_moments()

                stop""",
     """                call print_all_moments()

                ! THE VARIANT'S WHOLE PURPOSE. See make_variant.py.
                write(*,*) "SAVE VARIANT: writing the benchmark state"
                call save_vars_and_functions(1)
                write(*,*) "SAVE VARIANT: benchmark state written"

                stop""",
     "save the benchmark state after the frozen equilibrium converges"),
]

# ------------------------------------------------------------------ cf
CF = [
    ("        integer, parameter :: is_counterfactual=0",
     "        integer, parameter :: is_counterfactual=1",
     "is_counterfactual to one"),

    # NOTHING ELSE. The handover, the names and the missing initialisers used
    # to be patched in here; they are in the MASTER now, because they are a
    # real defect in long_run_counter_factual rather than a property of this
    # build. They do nothing when is_counterfactual is zero -- the subroutine
    # is never called -- so the benchmark is untouched by them, and keeping
    # them in one place is what stops the two copies drifting.
]

# --------------------------------------------------------- one class
# STEP 3, THE FAST RECALIBRATION. The author's sequencing of 10 September:
# *"then if it's ready, we hold them fixed and recalibrate the other parameters
# using the faster method with no permanent impact on the child"*.
#
# WHY A VARIANT AND NOT AN EDIT TO THE MASTER. Step 4 goes back to four classes,
# and the MODEL stamp on every point in points/ is the md5 of the master source.
# Editing the master to run step 3 would reset the archive for a run that is not
# a calibration point at all, and would then have to be edited back.
#
# voucher_exclusion_states GOES BACK TO 1 FOR ANY ARM. It dimensions the arrays
# the arms read out of the benchmark, so a benchmark built at 0 cannot be
# compared with an arm built at 1. It is 0 here and only here, because the
# benchmark has no conditionality and so has nothing to exclude.
ONE_CLASS = [
    ("        integer, parameter :: child_penalty_classes=4",
     "        integer, parameter :: child_penalty_classes=1",
     "child_penalty_classes to one"),

    ("        integer, parameter :: voucher_exclusion_states=1",
     "        integer, parameter :: voucher_exclusion_states=0",
     "voucher_exclusion_states to zero"),
]

# ------------------------------------------------------------- point1
# The measurement half of step 3. sweep_addiction_scalar stays at 1, which is
# what reaches the frozen-equilibrium loop and print_all_moments, so this is the
# master's own point run at one class. The gap table is read from the block
# AFTER `FROZEN CONVERGED`: b read 0.0795 before the frozen loop and 0.0849
# after on the four-class benchmark, a 6.4 per cent difference.
POINT1 = list(ONE_CLASS)

# ------------------------------------------------------------- calib1
# The search half. sweep_addiction_scalar=0 is what opens the calibration's
# outer do while; at 1 the run is a fixed-parameter measurement and no parameter
# moves.
#
# THE TWO CHILD PENALTIES ARE HELD BY THEIR calibrate_ SWITCHES, not by their
# adjusters. An adjuster at zero is the documented trap: the damping branch
# resurrects it on the first sign flip. With the switch at zero the update block
# is skipped and the distance is set to 0, so the parameter cannot move AND the
# outer do while is not held open by a moment nobody is fitting.
#
# delta_d is held at 0.36, which hits the SUD odds ratio at 1.9857 against 2.00.
# delta_h is held at 0.14 PROVISIONALLY: its target of 2.10 is below the model's
# measured floor of 2.889, and 2.80 of that floor is rho_intergenerational
# transmitting homeless parents' poverty rather than the penalty. Neither is
# fittable here in any case -- delta_d pins near 1.11 with the classes off.
CALIB1 = list(ONE_CLASS) + [
    ("        integer, parameter :: sweep_addiction_scalar=1",
     "        integer, parameter :: sweep_addiction_scalar=0",
     "sweep_addiction_scalar to zero, which opens the calibration loop"),

    ("        integer, parameter :: calibrate_penalty_child_addicted=1",
     "        integer, parameter :: calibrate_penalty_child_addicted=0",
     "delta_d held"),

    ("        integer, parameter :: calibrate_penalty_child_homeless=1",
     "        integer, parameter :: calibrate_penalty_child_homeless=0",
     "delta_h held"),

    # THE ADJUSTER, AND WHY IT HAD TO BE RAISED BEFORE THE LOOP WAS STARTED.
    #
    # The update is
    #     weight_on_child -= adjuster * clamp(gap - target, -1, 1)
    # and the model's gap is about 0.02 against a target of 0.18343, so the
    # clamped term is about -0.163 every loop whatever omega_c does. At the
    # declared 2e-3 that is a step of 3.3e-4, and walking omega_c from 0.007 to
    # its ceiling of 1.0 would take about three thousand loops.
    #
    # THAT FAILURE MODE IS INDISTINGUISHABLE FROM A PARAMETER PARKED ON A BOUND.
    # The parameter barely moves, the distance barely moves, and the log reads
    # like a converging loop. Raising the adjuster 250-fold makes the step about
    # 0.082, so the ceiling -- or the fit -- is reached in roughly a dozen loops
    # and which of the two happened is visible.
    #
    # IT CANNOT RING. The sign of the step is the sign of the gap and the gap is
    # one-signed all the way: the measured elasticity of omega in omega_c is
    # about 0.32 in logs -- omega was 0.0075 at omega_c=0.007 and 0.0209 at 0.17
    # -- so omega_c would have to rise by three orders of magnitude to triple
    # omega, and the step shrinks in proportion to the gap as the gap closes.
    ("        real(8) :: weight_on_child_adjuster=2*10.d0**(-3)",
     "        real(8) :: weight_on_child_adjuster=5*10.d0**(-1)",
     "weight_on_child_adjuster raised 250-fold, from 2e-3 to 0.5"),

    # A CAP, BECAUSE THE OUTER do while HAS NONE. Its omega_c term is
    # distance_weight_on_child > 1e-2, and the gap is about 0.163. If omega_c
    # walks to its ceiling of 1.0 with omega still far below target -- which is
    # what the death-probability scaling of the child term predicts -- that term
    # never falls under its rule and the loop never terminates. A cap turns an
    # unbounded run into a bounded measurement with the evidence in the log.
    ("""            loop_count=loop_count+1
            
            write(*,*) "loop_count=", loop_count""",
     """            loop_count=loop_count+1
            
            write(*,*) "loop_count=", loop_count

            ! See make_variant.py: the outer do while has no loop cap and its
            ! omega_c term cannot be satisfied if omega_c pins at its ceiling.
            if (loop_count>=calib_loop_cap) then
                write(*,*) "CALIB CAP: stopping after", loop_count,&
                    " loops. distance_weight_on_child=", distance_weight_on_child,&
                    " weight_on_child=", weight_on_child
                stop
            end if""",
     "a loop cap on the calibration's outer do while"),

    # The cap's own declaration, beside the adjuster it is there to bound.
    ("        real(8) :: distance_weight_on_child=1",
     """        real(8) :: distance_weight_on_child=1
        ! STEP 3's LOOP CAP. See make_variant.py.
        integer, parameter :: calib_loop_cap=300""",
     "calib_loop_cap declared"),
]

VARIANTS = {"save": SAVE, "cf": CF, "calib1": CALIB1, "point1": POINT1}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in VARIANTS:
        raise SystemExit("usage: make_variant.py {save|cf}")
    name = sys.argv[1]
    src = io.open(MASTER, encoding="utf-8", errors="surrogateescape").read()
    master_md5 = hashlib.md5(src.encode("utf-8", "surrogateescape")).hexdigest()
    for old, new, label in VARIANTS[name]:
        src = patch(src, old, new, label)
        print(f"  patched: {label}")
    out = os.path.join(HERE, f"variant_{name}.f90")
    io.open(out, "w", encoding="utf-8", errors="surrogateescape").write(src)
    var_md5 = hashlib.md5(src.encode("utf-8", "surrogateescape")).hexdigest()
    print(f"master {master_md5}  ->  {os.path.basename(out)} {var_md5}")
    io.open(out + ".from", "w").write(master_md5 + "\n")


if __name__ == "__main__":
    main()
