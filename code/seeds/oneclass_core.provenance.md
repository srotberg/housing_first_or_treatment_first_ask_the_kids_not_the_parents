# The one-class core calibration's vector

`PARAM_HANDOVER_oneclass_core.txt`, the vector `code/oneclass_core/` runs on.
The run directory itself is gitignored with the other run directories; this is
the part that has to survive the container.

Built from `PARAM_HANDOVER_bm_n90repro.txt` -- the benchmark version of the
accepted calibration point, which agrees with the transition's handover on every
calibrated parameter and carries the benchmark policy switches -- with four
lines overridden for this pass:

    freeze_all_but_omega_c   0      everything except omega_c IS calibrated
    omega_c_is_pinned        1      pins omega_c AND zeroes its distance, so the
                                    do-while term retires and a loop costs one
                                    solve rather than two
    weight_on_child          0      omega_c = 0
    penalty_child_addicted   0.24   delta_d, Nilsson, pinned

`calibrate_weight_on_child` is NOT among them and must stay 1: with it at 0 no
branch ever assigns `distance_weight_on_child`, the distance keeps its initial
value of 1, and the do-while has no iteration cap. See the commit that set the
one-class configuration.

The source is the one-class configuration at `child_penalty_classes=1`,
`iota_smi=1.0`, `mu_m=1.0`. The binary was built -O3 from that source and copied
in, so the run is isolated from further edits to the master.

VERIFIED IN THE RUN'S OWN LOG before anything is read off it:

    voucher_conditional_on_clean  0        benchmark, not Treatment First
    weight_on_child               0
    omega_c_is_pinned             1
    freeze_all_but_omega_c        0
    survival: SMI homeless w/ SUD 0.88727469276301107   the mortality fix

It starts COLD. One class halves the employment dimension, 26 to 13, so the
two-class warm start's shape stamp does not match and the reader refuses it --
correctly, since a silent load would be a different distribution.

This vector does NOT contain the SMI channel. It refits the level after the
mortality fix, which has to happen whatever else is done, and the b_SMI channel
is a second stage.
