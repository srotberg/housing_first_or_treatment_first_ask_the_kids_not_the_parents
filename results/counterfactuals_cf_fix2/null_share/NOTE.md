# No-policy steady state on cf_fix2_share: the transition's t = 0

Build cf_fix2_share = cf_fix2 plus one write of the final newborn_parent_share
(scratchpad build_cf_fix2_share.sh). Seeded from the earlier no-policy run's distribution.
Converged at pass 5: VOUCHER CHECK PASS (0.0675339), DIST CHECK PASS.

It reproduces the earlier no-policy run (../../counterfactuals_cf_local/null_fix), see final.txt:
net revenue 6.0371582 against 6.0370825, drug use -0.02 per cent, welfare +0.0003 utils.

Kept for the transition in code/seed_null_share: the final distribution (t = 0) and
newborn_parent_share_counter.dat (the parent share at t = 1; disordered housed 0.027986,
104 values summing to 1). The run directory was freed for disk.
