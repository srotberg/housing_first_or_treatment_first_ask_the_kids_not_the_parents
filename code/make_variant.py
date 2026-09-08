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
# THE STATE IS SAVED AT THE SWEEP'S STOP AND NOT AFTER A FULL CONVERGENCE LOOP,
# deliberately. The comment above that stop records that
# re_do_simulation_with_fixed_parameters does NOT freeze everything --
# sd_permanent_productivity was still moving pass by pass, and participation at
# a fixed b drifted 0.3326, 0.3244, 0.3327 across three passes. So a save run
# that let the loop keep going would write a state that is not the state the
# benchmark's reported moments came from. This writes exactly that state.
SAVE = [
    ("""                write(*,*) "B SWEEP POINT DONE at b=", addiction_scalar_1,&
                    " participation=", model_exprimenters(1)
                stop""",
     """                write(*,*) "B SWEEP POINT DONE at b=", addiction_scalar_1,&
                    " participation=", model_exprimenters(1)

                ! THE VARIANT'S WHOLE PURPOSE. See make_variant.py.
                write(*,*) "SAVE VARIANT: writing the benchmark state"
                call save_vars_and_functions(1)
                write(*,*) "SAVE VARIANT: benchmark state written"

                stop""",
     "save the benchmark state at the sweep's stop"),
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

VARIANTS = {"save": SAVE, "cf": CF}


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
