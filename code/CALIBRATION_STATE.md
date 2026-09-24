# EVERY GENERAL-EQUILIBRIUM CHANNEL OF A COUNTERFACTUAL IS CHECKED AGAINST THE OLD ARMS BEFORE IT RUNS, 24 September 16:35

Last night's counterfactuals -- the omega_c scan points, omega_c = 1,
internalisation, and three Treatment First runs -- were all solved on the frozen
scan path, which is the BENCHMARK binary. On that binary clear_drug_market
normalises the price to 1 every block, so drug_supply_elasticity 1.46 did
nothing. The old arms (19 September) ran the counterfactual binary, where the
price clears; arm 3's fell to 0.842. The author had to point it out: *"im
surprised that i had to tell you how to run the elasticity of drug supply
because in the old experiments that is how we did it"*. The source said so in
plain words (the comment at 46755), and the check was never made.

THE RULE: before any counterfactual runs, compare it channel by channel with
how the old arms ran -- drug market, taxes and budget, rental market, voucher
rules -- and check each against the branch the binary actually takes. A switch
being SET in the handover proves nothing; drug_supply_elasticity was set to
1.46 in every run.

THE GUARD: remote_tf_rationed.sh, remote_tf_point.sh and
remote_internalise_point.sh now refuse to run unless ALLOW_PEGGED_PRICE=1.
Counterfactuals go through remote_cf_clearing.sh. remote_scan_point.sh is left
alone: a BENCHMARK should normalise its own price.

THE TAX IS NOT THE SAME KIND OF MISS. adjust_taxes is 0 and labour income taxes
were removed on the author's instruction of 12 September ("we also dont need
labor income taxes"). The source records the unfunded residual as "the
experiment, not a bug" (line 333). The note's introduction still says the tax
rate responds, so that sentence may be stale -- the author's to decide.

