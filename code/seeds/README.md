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
