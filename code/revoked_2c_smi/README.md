# The revoked-voucher experiment split by serious mental illness (SMI)

The author, 5 October: *"you need to condition on the SMI for the constantini comparison, no?"*, and on the draft:
*"are you measuring this in the model for the SMI and homeless?"*, *"you need to include SMI!"*. Costantini (2025)
estimates 4.6 pp for homeless veterans WITH MENTAL ILLNESS; the model has SMI (`smi_of(u)`, which shifts mortality,
employment and drug use), so the comparable model number is the gap among the revoked households with SMI.

Everything is `code/revoked_2c` (README.md there: the design, the fixed paths, the shadow kernel, the guards), with one
addition, print-only, in `patch_smi.py`, applied to that experiment's tracking source:

* **The split.** Each tracked group -- the holders revoked in year 1, 2, 3 (groups 1-3) and every holder at the reform
  (group 4) -- is cut by its SMI state AT ITS START (the year-t cells the revocation lands in; t = 0 for group 4) into
  two shadow groups, 5-12 (`4 + 2(p-1) + 1 + smi`). Each half is followed by the same `revk_step` under the same kernel
  as its parent (Treatment First's in the `tf` run; Housing First's, with the voucher put back first, in the `hf` run).
* **Unchanged.** Groups 1-4 and every line the old build printed are untouched; the new lines are `REVK SGROUP` (the
  halves, the `REVK GROUP` fields plus `parent`, `smi0` and `smi_now`) and `REVK SMI` (`smi_now` for groups 1-4).
  `build.sh` refuses to build if the split changes any line outside the tracking module.
* **SMI later on.** SMI is not absorbing (it is left at rate lambda_m and entered at the onset hazard), so each line
  carries `smi_now`, the share of the group's survivors in an SMI state now.

## Files

* `patch_smi.py` -- the split, on `revoked_2c/patch_revoked.py`'s tracking output.
* `build.sh` -- plain and unsplit tracking at T = 3 (controls), split tracking at T = 3 and T = 10.
* `run_paths.sh` -- waits for `revoked_2c/run_arms.sh` (the two steady states), then the one-thread T = 3 guards (plain
  and split together, then the unsplit tracking beside the T = 10 Treatment First path), the T = 10 Housing First path
  from the tags, and `analyse_smi.py`; publishes `results/revoked_2c_smi/status.txt` about every 30 minutes.
* `analyse_smi.py` -- the guards (aggregates against plain; groups 1-4 byte for byte against the unsplit build; the
  halves summing to their parent; mass accounting) and the tables, pooled as `paper/export_revoked.py` pools them.
