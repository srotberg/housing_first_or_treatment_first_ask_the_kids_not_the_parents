# Rationed TF, 70 per cent detection, with the children's split -- NOT FIRM, 26 September 02:30

Same settings as ../tf_tight70 (detection 0.70, budget rule 2e-3, target 6.26479886,
TARGET CHECK PASS) on build code/cf_childdecomp_tight, which adds only diagnostic
prints. Warm start at tf_tight70's exit: price 0.87805, pi_V 0.068739. Exit at pass 7:
budget gap 0.00184, drug gap 0.0031.

THE PROOF THAT tf_tight70 IS NOT FIRM. Same model, same rules, same target:

| run | exit pass | pi_V | homelessness | CEV |
|---|---|---|---|---|
| tf_tight70 | 15 | 0.0688 | +10.3% | -0.30% |
| this run | 7 | 0.0758 | +8.2% | +0.70% |

Both satisfy every stopping rule. The first stopped at the bottom of the pi_V cycle, this
one near the top (CALIBRATION_STATE.md, 26 September 02:30). The children's split printed
here is taken at that phase and is not used.
