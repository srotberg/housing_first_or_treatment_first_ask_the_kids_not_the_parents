# ON THE FROZEN PATH THE DRUG PRICE IS PEGGED AT 1: THE 1.46 ELASTICITY IS INERT, 24 September 16:05

The author asked whether the drug supply elasticity of 1.46 is included,
surprised at omega_c = 1's -75%. It is SET (handover line 9, in every run
tonight) but it DOES NOTHING on the path every run tonight used.

clear_drug_market (44756): on `is_counterfactual == 0` -- the benchmark binary,
which the frozen scan path is -- it re-picks the supply shifter so the price
sits at the benchmark's own, at WHATEVER quantity is consumed:

    drug_supply_shifter = 1/(quantity**(drug_supply_curvature-1))
    price_of_addictive_good = price_of_addictive_good_benchmark

Only the `else` branch, `is_counterfactual == 1`, reads the benchmark's shifter
and clears along the upward-sloping supply curve. The source says so at 46755:
"With is_counterfactual = 0 clear_drug_market normalises the shifter, sets the
price to the benchmark's own and sets distance_drug_market to zero".

Confirmed in the Housing First reference's own log: "drug_supply_shifter
(normalised)" is printed on all 12 blocks, the shifter moving with quantity
(1.7935 at V = 0.4262 to 1.6045 at V = 0.5014), and price_of_addictive_good is 1.

So every counterfactual tonight -- omega_c = 1, internalisation, both TF runs,
and the omega_c scan that picked 0.06 for an 18 per cent drop -- treats drug
supply as PERFECTLY ELASTIC. With 1.46, falling demand lowers the price, which
pushes use back up. For scale, arm 3 on the clearing path had its price fall
15.8% (to 0.8422) with quantity -22.6%. The frozen-path drops are therefore
UPPER BOUNDS on the clearing-market drops. The note's introduction claims "a
drug market that clears, so drug prices respond to policy" (source line ~369).

The same freeze also zeroes labor_income_tax_rate_adjuster (46773), so the tax
rate is held at the benchmark in every frozen counterfactual. Whether anything
else balances the budget there has NOT been checked. The note also claims "a
government budget that balances, so the tax rate responds".

WHAT CLEARING WOULD NEED, not done and the author's call: a counterfactual
build that takes the clearing branch (a build-directory sed of the one `if` at
44792, leaving the tracked model untouched), plus the Housing First omega_c = 0.06
shifter, already in its log as 1.6045261392144357 (the last block). Arm 3
needed 22 blocks to clear, so frozen_stop_after_blocks would have to rise.
omega_c = 0.06 was itself chosen with the price pegged.

