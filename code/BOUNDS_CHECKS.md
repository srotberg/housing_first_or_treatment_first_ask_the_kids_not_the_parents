# Bounds and initialisation checks on the model source

A record of what each instrumented build was asked and what it answered. A
check that came back clean is worth as much as one that fired, and is written
down for the same reason: the next reader needs to know which classes of fault
have already been ruled out on which code path, so that the search does not
repeat itself.

## 2026-09-03 -- the uninitialised-memory gate, on KKK line 2

### Why this check and not the bounds check

A bounds check had already run clean over this source and could not have found
the fault it was implicitly being trusted to find. `get_probabilities_KKK_process`
declared a local array `width` and never assigned it; the six reads of it were
reads of uninitialised memory, every one of them in range. Bounds checking asks
whether an index is inside its array, so a fully in-range read of a garbage
value is exactly the fault it is blind to. The consequence downstream was a NaN
economy: transition rows summed to zero for the middle nodes and the
normalisation divided by that zero. It was invisible for as long as
`fixed_productivity` was 1, because that routine's outputs are discarded on
that path. Full account in `KKK_VS_SIGMA_Y.md`.

`-finit-real=snan` is the check that can find it. It fills every uninitialised
real with a signalling NaN, and `-ffpe-trap=invalid` turns the first *use* of
one into a trap with a backtrace, rather than letting it propagate silently
into a normalisation.

### The build

    gfortran -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow \
        -fcheck=bounds,pointer -g -fbacktrace -fimplicit-none \
        -ffree-line-length-none -mcmodel=medium -fopenmp \
        code/housing_first_or_treatment_first_SR_v1.f90 -o /tmp/snan_kkk

Compiled at exit 0. Three warnings, all of one kind and all outside the path
under test: `housing_stock(i)`, `total_housing_demand(i)` and
`lump_sum_transfer(i)` are read at `i=0` in the transition's output-writing
loops at lines 41428 and 41455, in arrays declared from 1. They are in the
transition's file writing, they are not reached by a benchmark solve, and this
run did not reach them. They are recorded here because they are real
out-of-bounds reads that the compiler can see statically, and they belong to
whoever owns the transition.

### The vector

Line 2 of `code/batch_kkk.txt`:

    bash code/run_one_point.sh ssi_floor_takeup=0.5 fixed_productivity=0 kkk_s_deviation_bottom=3.35

`run_one_point.sh` was not modified and not run for this step. Its
`declare -A P=(...)` defaults block was extracted verbatim and the three
overrides applied to it, reproducing `PARAM_HANDOVER.txt` (60 lines, one per
parameter other than `addiction_scalar_1`) and `B_SWEEP_GRID.txt` (0.0224532)
by hand, in a scratch directory with the repository's `data/` beside it, with
no `calibration_state.dat` present. Run under the same environment the script
uses: `OMP_NUM_THREADS=4 OMP_STACKSIZE=512M GFORTRAN_UNBUFFERED_ALL=1`,
`ulimit -s unlimited`.

### Verdict: CLEAN. It did not trap.

Nothing fired. No backtrace, no `Fortran runtime error`, no
`Program received signal`, no bounds violation reported at run time. The run
was killed by hand after it had passed every milestone asked of it:

| milestone | result |
|---|---|
| handover applied | 60 of 60, none ignored |
| KKK grid construction | reached and passed; sd of log y at age 1 = 0.409033 |
| `create_newborn_employment_probability` | reached and passed |
| `verify_newborn_process` | `rows not summing to one = 0`, `rows off p(1) = 0` |
| backward induction | 39 ages completed (ages 60 down to 22), against the 25 asked for |

The internal invariants that print in this stretch all passed. The newborn
process check reports zero rows failing to sum to one and zero rows off
`p(1)`, which is the direct descendant of the failure mode the `width` bug
produced -- rows summing to zero and a normalisation dividing by it. The
transition matrix printed for age 1 has rows summing to one across all seven
nodes. `unemployment_process` reports its generic builder at
`number_of_smi_states=2`; the index map reports its accessors consistent.

So the `width` fix holds under signalling-NaN initialisation on this vector,
and the uninitialised-read class of fault is now ruled out over the grid
construction, the newborn draw and the first thirty-nine ages of the
household's problem -- which is the stretch where the previous NaN economy was
born. It is NOT ruled out over the distribution sweep, the equilibrium loop or
the transition, none of which this run reached.

### What the grid looks like at this vector, from the gate run

Recorded because it is the thing line 2 was run to see, and the gate run
reaches it long before the solve finishes.

    grid age 1            : 0.231921  0.357556  0.551248  0.849865  1.310247  2.020023  3.114293
    grid last working age : 0.196294  0.319002  0.518418  0.842493  1.369154  2.225043  3.615967
    masses at age 1       : 0.002395  0.036597  0.201672  0.397729  0.282706  0.072161  0.006740
    mean productivity at age 1 = 1.000000

    KKK grid: bottom half's share of productivity = 0.329425   target = 0.172000
    smallest_house_size*rent(1)/net_income_lowest = 0.117720

The fanning out is there: the same node index is a wider deviation at the last
working age than at the first, at both ends. The bottom half's share comes back
at 32.9 per cent against a target of 17.2, and the poorest household holds
0.2319 of mean productivity -- both of which were predicted in advance of the
run and are the known weakness of this vector rather than a fault of it. The
cheapest rental costs 0.1177 of the lowest net income in the economy, so the
poorest household can afford it comfortably, and low homelessness is what
should be expected from the solve.
