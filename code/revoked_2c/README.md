# What happens to the households whose voucher Treatment First revokes (short run, fixed prices)

The author, 4 October: *"Can we test a short run experiment with fixed prices and fixed pi_V, where you do Treatment
First and check what happens to the SUD of those whose voucher was revoked in the first 3 years?"*, and the MORTALITY of
those households *"relative to what would happen to them if they had stayed housed"*. For the associate editor's
comment on Costantini (2025) (HF_or_TF_RED_reviews/AE_R1.txt; placeholders `\tbd{HF LATE}`, `\tbd{TF LATE}` in
HF_or_TF_RED_reviews/responses_round1/response_AE.tex). Results: `results/revoked_2c/`.

## Design

* **Path.** Start: the Housing First (no-policy) steady state, `cfarm_null_2c`. Treatment First is switched on at the
  start of year 1 (sobriety-conditioned vouchers, detection 85 per cent, the $35 test, three-year exclusion, no false
  positives). End: Treatment First with the drug price and pi_V both held at the no-policy values and the budget not
  cleared, exactly the `fixboth` arm of `extra_2c/remote_decomp_2c_both.sh` (`cfarm_tf_2c_fixboth`). Price
  P_NULL = 1.0001082 and pi_V V_NULL = 0.067533863 in every year (seeds), `adjust_taxes 0`, `drug_market_adjuster 0`.
  T = 10, ONE forward pass (loop 0; the build stops after it, so nothing is updated).
* **Counterfactual path.** The same machinery with the no-policy steady state at both ends (the flat control's
  configuration, with the same fixed paths): every year runs Housing First's own policy functions.
* **Tracking (print-only).** `patch_revoked.py` adds a module, `revk_track`, whose `revk_step` is the forward kernel of
  `converge_to_stationary_equilibrium` written out a second time, term for term and in the same multiplication order,
  applied to a SHADOW mass, with no newborn row. Every period it also pushes the whole population at t-1 through it and
  compares the result with the model's own distribution at t, ages 2 and up: that is the check that the shadow kernel
  IS the model's kernel.
  * **Revoked in year t** (t = 1, 2, 3): the terms of the kernel that move a holder (voucher state 1) into the
    exclusion state, in the step that makes year t. With no false positives every such move is a failed test of a
    holder. (A household in the queue that wins the lottery and fails the test also goes to the exclusion state; it
    never held a voucher and is not tagged.)
  * **(a) actual**: that mass, followed under Treatment First's kernel from year t+1.
  * **(b) counterfactual**: the same mass with voucher state 1 instead of the exclusion state -- the voucher draw is the
    last factor of the kernel, so this is the same households with the same year-t choices and the voucher kept --
    followed under Housing First's kernel from year t+1 (the tags are written by the Treatment First run and read by the
    Housing First run).
  * **Holders at the reform**, revoked or not: voucher state 1 in the t = 0 distribution, followed under each kernel
    from year 1.
  * The model's reduction (the per-thread arrays summed into `distribution_implied`) copies only the cells inside
    each age's own state range, so mass the kernel sends outside it -- below the renter floor of the last age, where
    the floor is 3 rather than 1 -- leaves the model. The first T = 3 run showed it (shadow against model 1.9e-6 in
    one cell); the shadow now drops the same cells (`revk_build_mask`, the reduction loop's ranges verbatim) and books
    the mass as an exit at the end of life, printed as `REVK LEAK`.
  * Deaths: in each step, mass times one minus the survival probability the kernel applies (homelessness, the disorder
    and SMI enter it through the mortality multipliers), plus the mass at the last age, which the kernel does not
    carry (end of life).
* **No equation changes.** The two build copies differ from stage E's corrected transition source
  (`transition_fix/patch_transition_fix.py`, 176 lines) by the stop after loop 0 (`plain`) and by that plus the module
  and three calls (`track`).

## Files

* `run_arms.sh` -- stage 1: re-solves the two steady states (the containers that held them are gone) with the tracked
  scripts, unchanged.
* `build.sh` -- the patched sources and four binaries: plain and tracking at T = 3 (the identity guard), tracking at
  T = 10, and a bounds-checked tracking build at T = 3.
* `run_paths.sh` -- stage 2: the T = 3 guard runs, then the two T = 10 paths, then `analyse.py`; publishes
  `results/revoked_2c/status.txt` about hourly.
* `analyse.py` -- the guards and the tables; `compare_arms.py` -- the re-solved arms against the accepted ones.
