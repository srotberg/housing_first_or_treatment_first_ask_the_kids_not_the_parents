# Permanent voucher ban, 85 per cent detection -- NOT FIRM, 26 September 02:30

Rationed TF at detection 0.85 with voucher_exclusion_release 1/3 -> 0 (a caught holder
or winner is excluded for good), budget rule 2e-3, like-for-like target 6.26479886
(TARGET CHECK PASS), build code/cf_permban (scratchpad build_cf_permban.sh). Warm start
price 0.87495, pi_V 0.07016. Exit at pass 20: budget gap 0.00199, drug gap 0.0015.

NOT A RESULT. The loop solves the household distribution only to a per-sweep change of
6e-4 (1 to 9 sweeps a pass), so the distribution converges across passes and pi_V
chases a lagging budget in a cycle (CALIBRATION_STATE.md, 26 September 02:30). This run
stopped on the way down: pi_V still falling (0.0775, 0.0774), homelessness still rising
about 0.1 point a pass, welfare still falling about 0.08 utils a pass. Its CEV, +0.15
per cent at exit, peaked at +1.03 at pass 7. passes.txt holds every pass.
