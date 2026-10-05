# The revoked-voucher experiment split by SMI and by whether the revocation puts the household on the street

The author, 5 October: *"for the constantini comparison, you need to condition on SMI for both voucher holder and those
revoked, and then compare those who ended up on the street whose voucher was revoked"*. Costantini (2025) estimates
that Housing First lowers the three-year mortality of HOMELESS veterans WITH MENTAL ILLNESS by 4.6 pp. The model's
counterpart: the households with SMI whose voucher Treatment First revokes AND whom the revocation puts on the street,
against the same households had they kept the voucher.

Everything is `code/revoked_2c` (README.md there: the design, the fixed paths, the shadow kernel, the guards), with one
print-only addition, `patch_street.py`, applied to that experiment's tracking source. `code/revoked_2c_smi` (another
worker) splits by SMI alone; nothing here touches it.

* **The split.** Each revoked cohort (holders whose voucher is revoked in year c = 1, 2, 3; groups 1-3) is cut into
  four parts, groups `4 + 4(c-1) + 1 + 2 smi + street`, by
  * `smi`: `smi_of(u)` of the cell the revocation lands in (year c);
  * `street`: whether the revocation puts the cell on the street (below).

  Each part is followed by the same `revk_step` under the same kernel as its cohort: Treatment First's in the `tf` run;
  Housing First's, with the voucher put back exactly as for the cohort, in the `hf` run, which reads the parts the `tf`
  run wrote (`revk_tag_c<c>_split.bin`). Same households, same split, on both sides.
* **"Put on the street", and why this definition.** In the forward kernel a household's step chooses next year's housing
  (`policy_function_housing_status_index`) and then draws next year's voucher state, which is the last factor. So a
  holder revoked in the step that makes year c chose its year-c housing as a holder: none of the revoked is homeless in
  year c (the unsplit tables show 0.00). The first housing choice made after the revocation is the one in the step into
  year c+1, made by Treatment First's policy at the excluded state. A cell is on the street when that choice, after the
  renters' adjustment the kernel applies, is `lowest_housing_grid_point` (`is_homeless_2 == 2` in the kernel). The model
  keeps one period's policy slice, so the split is made at the START of `revk_period(c+1)`, before anything moves, on the
  cohort's untouched year-c cells; the parts start at year c like their cohort. Cells at the last age make no choice (end
  of life) and count as housed; their mass is printed. Under Housing First the same cells are followed with the voucher
  kept, so (b) is "had the voucher not been revoked", whatever housing they would then have chosen.
* **Still on the street.** For each street part a further shadow mass is moved by the same kernel and cut to the
  homeless cells after every step: the mass on the street in EVERY year since the revocation (`REVK PERSIST`).
* **Unchanged.** Groups 1-4 and every line the unsplit build printed are untouched; the new lines are `REVK SPLIT`,
  `REVK SUBGROUP` (the `REVK GROUP` fields plus `cohort`, `smi0`, `street`, `smi_now`) and `REVK PERSIST`. `build.sh`
  refuses to build if the patch changes a line outside the tracking module.

## Guards

* T = 3, one thread: plain against split tracking, every aggregate line bit for bit; unsplit against split tracking,
  every `REVK GROUP/POP/TAG/LEAK/INIT/MASK` line byte for byte; mass accounting; the four parts summed against the
  cohort (cell by cell at the split, exactly; afterwards to rounding, since four separately rounded passes rejoin in
  the same cells); the classification is the kernel's (one year on, every survivor of a street part is homeless and
  none of a housed part). At T = 3 the forward periods are 1 and 2, so only cohort 1 is split; the T = 10 runs repeat
  every split check for all three cohorts.

## Files

* `patch_street.py` -- the split, on `revoked_2c/patch_revoked.py`'s tracking output.
* `build.sh` -- plain and unsplit tracking at T = 3 (controls), split tracking at T = 3 and T = 10.
* `run_paths.sh` -- waits for `revoked_2c/run_arms.sh` (the two steady states), then the one-thread T = 3 guards, the
  T = 10 Treatment First path (with the unsplit tracking at T = 3 beside it), the T = 10 Housing First path from its
  tags, and `analyse_street.py`; publishes `results/revoked_2c_street/status.txt` about every 30 minutes.
* `analyse_street.py` -- the guards and the tables.
