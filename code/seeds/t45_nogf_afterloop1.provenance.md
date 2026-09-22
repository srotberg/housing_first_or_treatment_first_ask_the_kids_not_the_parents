# The T=45 no-grandfathering paths after loop 1

Committed 22 September 19:4x so that the transition can be restarted in a
container that is not this one. Everything else it needs is already committed:
the benchmark it runs against is `benchmark_dat/`, and the parameter vector is
`PARAM_HANDOVER_trans_postfix.txt`, which is byte identical to the
`PARAM_HANDOVER.kept.txt` the reference benchmark was solved at.

    drug_price_path_seed_t45_nogf_afterloop1.txt   44 entries
    pi_v_path_seed_t45_nogf_afterloop1.txt         44 entries

## Where they come from

`code/t45_nogf/`, run 8, which completed loop 1 at 16:45 and wrote them itself
as `drug_price_path_seed_out.txt` and `pi_v_path_seed_out.txt`. They are the
model's own output, not a harvest: `save_transition_paths.py` cannot read run
9 or run 10, which carry no `TRANSITION MECH` lines because both were killed
inside a backward pass.

Run 10 was killed at 19:25:18 by numeric pid, 15m24s into loop 2's backward
pass, to give the mortality-fix benchmark the whole four-core machine. Nothing
was lost that these two files do not carry: loop 2 had not yet written a path.

## Why pi_v matters here and did not before

`seeds/README.md` says there is no good pi_v vector and that
`pi_v_path_seed_t30.txt` is 29 copies of one number, because pi_v is gated on
`loop_count > start_updating_at_loop_number` and no transition had run past
loop 1. **This one has.** pi_v runs from 0.086768903041692 at t=1 down to
0.076226136906131, so it carries a shape rather than a constant, and it is the
first such file in the repository.

## The checks before committing

    NaN                       none in either file
    pi_v on a bound           no; range [0.076226, 0.086769], floor is 1e-5
    price range               [0.819051, 0.887092]
    entries                   44 and 44, against a horizon of 44

These are the three the harvester itself refuses on. They are stated here
because these files were copied rather than harvested, so the harvester's own
refusals never ran.

## Reading them

The reader skips `#` lines -- see `READ_ME_BEFORE_ADDING_A_HEADER.md`, which
measured this three ways. Confirm on any run from the log line

    DRUG PRICE PATH seeded FROM FILE, entries read=  44  of  44

and do not reconstruct the reader.
