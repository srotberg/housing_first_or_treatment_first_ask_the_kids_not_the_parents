# Partial equilibrium, no externalities, in the full model (pe_noext)

The author, 4 October: *"I think we should run a pe experiment with no externalities also in the full
model. You just take the omega_c = 0 case and don't impose any of the penalties. ... And then, simulate
with piv, pv fixed and the externalities turned off. That could be the very first experiment we refer
to."* The point: Section 3's result -- without externalities and at fixed prices, Housing First weakly
dominates Treatment First household by household -- checked in the quantitative model. No
recalibration and no paper edits. Results: `results/pe_noext/`.

## The arms

Every parameter not listed stays at the accepted omega_c = 0.085 benchmark
(`results/reference/hf_2c_omega_0.085`), which both arms read through `BENCH_FROM`.

* **Arm A, `null_pe_noext`**: Housing First, run as the accepted no-policy arm
  (`revoked_2c/run_arms.sh`, 'null'): cf_fix2_share, drug price clearing at adjuster 0.1 from
  P_NULL = 1.0001082, pi_V at the benchmark's 0.067533863, adjust_taxes 0. -> `code/cfarm_null_pe_noext`.
* **Arm B, `tf_pe_noext`**: Treatment First as tf85_c35 (detection 0.85, the $35 test, the three-year
  exclusion, no false positives), with the drug price, pi_V and the house price held at the values
  Arm A's LAST solve used, adjust_taxes 0 (the budget is not cleared; what Treatment First saves goes
  unspent). Seeded from Arm A's distribution. -> `code/cfarm_tf_pe_noext`.

## The externality switches (both arms)

| channel | switch |
|---|---|
| the parent values its child (flow term and continuation) | `weight_on_child 0` (handover) |
| the child's inherited productivity penalty for a parent with a SUD at death (child class 1) | `penalty_child_addicted 0` (was 0.24) |
| the same for a homeless parent | `penalty_child_homeless 0` (already 0, asserted) |
| the inherited penalty in RETIREMENT income: the benchmark's `model_ss_benefits` by node, which the counterfactual uploads, was computed from class-1 earnings at 0.76 | `SS_NO_CLASS=1`: the arm's copy of the file gives each class-1 node the benefit of the same class-0 node |
| the homelessness disamenity (welfare statistics only, no policy function reads it) | `kappa_x 0` |

Checked and left alone: `child_penalty_off` (zeroes the inherited-penalty part of the child term,
which omega_c = 0 already removes); `rho_intergenerational` 0.5 (the child's productivity draw
is persistent in the parent's productivity node; with the penalties at zero the parent's node carries
no class factor, so nothing the parent chooses or the policy does enters it except through which
nodes parents die at, a composition effect that cannot move any household's value and is held out of
the newborn comparison by weighting with Arm A's newborns); the newborn's initial wealth and
inheritance are the same for every node and class.

## Held and not held between the arms

Held by the build: rent (`fix_rent = 1`, infinite rental supply elasticity), inheritance
(`residual_bequests_to_government = 1`, so `adjust_inheritance` never runs), the lump-sum transfer
(0), the labour income tax (0), Social Security benefits, median and average income (uploaded from
the benchmark). Held by the handover: the drug price (`drug_market_adjuster 0`), pi_V (`adjust_taxes
0`). Held by the cf_fix2_pe patch: the house price (see `patch_pe.py`: the build pegs it and then
moves it 2 per cent toward the supply curve every pass, so it is not held without the patch). Not held:
the newborns' productivity mix, which follows the parents' productivity at death (rho), and the
government budget.

## Files

* `patch_pe.py`, `build_pe.sh` -- the two builds: cf_fix2_share_pe (print-only `PE USED` line,
  Arm A) and cf_fix2_pe (that plus the house-price hold, Arm B).
* `cf_arm_pe.sh` -- copy of `transition_2c/cf_arm_tr2c.sh`: the two builds in the whitelist, no
  benchmark build, `SS_NO_CLASS` and `HOUSING_PRICE_HOLD`.
* `run_pe.sh` -- both arms in order, detached; publishes `results/pe_noext/status.txt`.
