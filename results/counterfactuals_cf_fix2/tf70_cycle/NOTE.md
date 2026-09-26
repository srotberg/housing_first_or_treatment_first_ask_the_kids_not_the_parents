# TF 70 per cent on cf_fix2: STOPPED, a two-pass cycle -- not a result

Passes 4 to 8 alternate between two states and never meet the moments rule (change 3.6-3.8e-4
against 1e-4 at every pass from 5 on), although the budget came inside its rule at pass 7
(-0.00043) and the drug market cleared:

| pass | pi_V | drug use b | SUD | disordered-housed parent share | budget gap | CEV |
|---|---|---|---|---|---|---|
| 5 | 0.08045 | 0.05817 (-28.4%) | 0.02455 | 0.01917 | -0.0027 | +1.50% |
| 6 | 0.08029 | 0.05781 (-28.9%) | 0.02440 | 0.01905 | -0.0027 | +1.50% |
| 7 | 0.08012 | 0.05817 (-28.4%) | 0.02455 | 0.01917 | -0.00043 | +1.45% |
| 8 | 0.08010 | 0.05781 (-28.8%) | 0.02440 | 0.01905 | -0.0013 | +1.48% |

pi_V and the drug price move smoothly; the parent share does not. The newborn draw of pass k+1
uses the parents who died in pass k, and at 70 per cent detection that map overshoots: more
parents with the disorder give more low-productivity children, who under Treatment First depend
more on vouchers and are deterred more, so fewer use, which lowers the next share. TF 85 does not
cycle (its share converges smoothly to 0.01865).

Rerun on cf_fix2_damp (scratchpad build_cf_fix2_damp.sh): the share in use becomes half the new
share and half the old, which leaves the fixed point unchanged. Seeded from TF 85's converged
distribution at pi_V 0.0801 and price 0.8736: code/cfarm_tf_damp70. The two states above bracket
its answer.
