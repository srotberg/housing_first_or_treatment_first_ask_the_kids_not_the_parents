# RATIONED TREATMENT FIRST AGAINST RATIONED HOUSING FIRST, omega_c = 0.06, 24 September 09:03

`results/counterfactuals/treatment_first_rationed/` (a7b30642, 74e3819b), against
`results/reference/hf_omega_c_006/`. One container throughout; the build diff
was asserted to be exactly the two guard removals, and all eight HANDOVER
switches were echoed in the log.

    b          0.081261 -> 0.015392    -81.06%
    lambda_d   0.034617 -> 0.006520    -81.16%
    h_1        0.006079 -> 0.005787     -4.80%
    tau_u      0.2506   -> 0.3034      +21.08%

    CEV = +0.052927, i.e. +5.29% of non-drug consumption

The CEV is TF's average_welfare_with_childhood (791.08974658630109) read off the
Housing First curve, which is anchored at x = 0 on the same object (789.3488).
The identity-check line labels that object "average_welfare_of_youngest_cohort",
but the value it prints is average_welfare_with_childhood; average_welfare_of_youngest_cohort
itself is 1352.88. The interpolation mirrors calculate_welfare_gains (23028), and
returns 0 at the Housing First anchor. kappa_x is 0.9329 in both runs.

## THREE THINGS THAT QUALIFY IT

1. **Stopped at block 10 on the model's own stillness rule**, not the family rule:
   `frozen_stop_tolerance 0.001` is in the base handover (line 93), and block 10's
   block_move was 8.8e-4. b moved 0.887% and then 0.039% over the last two blocks,
   so the family rule was one block from firing. Residual 1.433, a little below the
   1.45-1.48 band; the policy changes bequests, so that is not by itself a fault.

2. **The three-year exclusion never bound.** The excluded-state mass is exactly 0
   from block 2 on. Testing ran (mass tested 3.58 of 11.56 eligibles, spending
   1.11e-3), but nobody failed. The likely reading is an off-equilibrium threat:
   users cannot get a voucher at all (see 3), and no holder chooses to use. That
   has NOT been verified by measuring drug use among holders directly.

3. **The door is a ban, not a 70 per cent test.** With
   increased_prob_of_voucher_if_homeless_and_addicted = 0, a failing applicant's
   offer is (1-p_det)*prob*0 = 0. The author's 30 per cent false negative therefore
   applies to holders only. This was put to the author at 03:41 and is unanswered.
   It may be a large part of the -81%.

The log also prints, as every run on this seed does, STALE CONSTANT lines:
median_income_calibrated 0.3875 against a realised 0.8650, and
average_labor_income_calibrated 0.6679 against 1.6243. Both arms share them, so
the comparison is internally consistent. Whether the voucher eligibility threshold
is meant to key on the stale value is a separate question.

