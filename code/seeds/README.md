# The frozen parameter vector

`n72_frozen_seed.dat` is the calibration every omega_c and delta_d trial is run
against: 96 parameters, the point the author accepted, with b at 0.10376 against
a target of 0.10502 and fifteen rows inside six per cent.

It is committed because a parallel session cannot reach the coordinator's
scratchpad, and a worker needs it to build `PARAM_HANDOVER.txt`. The
DISTRIBUTION that goes with it is 265 MB and is not committed, so a worker
starts cold and pays a few extra blocks while the class-1 stock fills from zero.

## Building a handover from it

Copy it to `PARAM_HANDOVER.txt` beside the binary, then override the four
switches that define a trial:

    penalty_child_addicted   0.24    delta_d, Nilsson, pinned
    weight_on_child          <trial> omega_c, the thing being searched
    omega_c_is_pinned        1       counterfactual OFF, one solve a block
    freeze_all_but_omega_c   1       all 47 other adjusters zeroed

Nothing else is changed. The binary reads the file, applies it AFTER
calibration_state.dat, and deletes it.

## The benchmark it is scored against

    D0 = 0.10148     total drug users at omega_c = 0, delta_d = 0.24, converged
    gap = D0 / b - 1    target 0.18343, accept band [0.17790, 0.18890]

# The transition's path seeds

A transition run iterates two quantities PER PERIOD, and only these two can be
seeded, because only these two are instruments:

    price_of_addictive_good_path   clears the drug market   drug_price_path_seed*.txt
    probability_of_voucher_path    clears the govt budget   pi_v_path_seed*.txt

Seeding matters because the fallback is a linear ramp, and the ramp cost about
ten loops on the T=30 arm: the secant roots took the mean drug-market gap from
0.2027 to 0.01351. A loop at T=60 is between five and eight hours, so a path
thrown away is a day.

`save_transition_paths.py <run.log>` harvests them. It reproduces the
hand-built `drug_price_path_seed_t30.txt` exactly, to 0.000e+00 relative,
which is the check that it reads the log the way a person did.

## Homelessness is not an instrument

`h1_path_reference*.txt` is written for the same loop but NOTHING READS IT.
h_1 is an outcome of the distribution, so there is no slot in the model to put
it in; the file is a target to score a restart against. The object that would
genuinely warm-start homelessness is the distribution path, which is 73 MB per
period and is not a vector.

## Two ways a saved path lies, both of which have happened

**The deepest loop is usually the incomplete one.** A run is killed part way
through its newest loop, so the newest loop can be a four-period fragment of a
thirty-period horizon. Taking it silently hands a restart four periods of seed
and twenty-six of ramp, which is worse than the complete older loop it stepped
over. The default is the deepest loop that covers the whole horizon, and
`--fill` splices the deeper values in per period and records in the file which
loop each period came from.

**A collapsed loop is indistinguishable from a converged one once it is a
column of numbers.** `t30_loop1_pivcollapse.log` is the example: at loop 1 the
budget residual was -6.02, more than ten times anything the steady state has
produced, and pi_v went through zero to its 1e-5 floor in one step, in every
period, with h_1 at NaN. As a file that is 29 plausible-looking decimals. The
harvester refuses to write a path with a NaN in it or a pi_v sitting on either
bound, and `--force` is the only way past.

## There is no good pi_v vector yet, and that is not a bug in the harvester

pi_v is gated on `loop_count > start_updating_at_loop_number`, which is 0, so it
is pinned at the benchmark's 0.076347 for the whole of loop 0. No transition has
yet run past loop 1. `pi_v_path_seed_t30.txt` is therefore 29 copies of one
number and carries no information; it is committed so that the first run which
does get deep has something to diff against.
