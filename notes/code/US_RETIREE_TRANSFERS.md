# What the model has of the US system for low-income retirees, and what it lacks

Written 3 September, for the author's question: *"see how the old homelessness
is at the end of it when you use the full ss system in the US (I think you said
there are some things that need to be added for low income retired, like old age
top up's for low income retirees?)"*

## WHAT IS ALREADY IN, and it is more than the earlier notes implied

**1. The PIA benefit formula, the actual statute.** Three bend points at 0.2208
and 1.3314 of the average wage index with marginal replacement rates 0.90, 0.32
and 0.15, and a taxable maximum at 2.6428. Live whenever
`use_pia_formula=1`, which every current point carries.

**2. SSI, the old-age top-up, at the real federal rate.** The benefit is
`max(PIA_i, ssi_floor_takeup * ssi_floor_level)` with `ssi_floor_level` = 0.1774
— the 2024 federal benefit rate of $943 a month over the average wage index. The
current base carries take-up 1.0, so it binds on nodes 1, 2 and 3, which is
**24.07 per cent of retirees**.

**3. SNAP, and retirees are eligible.** Asset-tested only —
`assets_1 < threshold_for_food_stamps_as_perc_of_average_net_wealth * avg_net_wealth`
— and the benefit is computed from `calculate_income(..., in_retirement)`, so a
retired household with low assets receives it on the same terms as anyone else.

## WHAT IS MISSING, in the order it is likely to matter

**1. Real SSI take-up is about half, and the model is at ONE.** So the model is
already MORE generous than the programme on this margin, not less. That is a
deliberate identification choice — with take-up pinned at 1, `ssi_floor_level`
IS the effective floor and the two are not two names for one dial — but it means
"add more for low-income retirees" cannot come from take-up.

**2. There is no SSI asset test.** Real SSI has a $2,000 limit and the model's
floor applies regardless of wealth. Again more generous, not less.

**3. State SSI supplements are absent.** Most states top the federal benefit up
and roughly half of recipients receive one; these run from a few dollars to
about 20 per cent of the federal rate. This is the one genuine omission on the
generosity side, and it is small: it would move `ssi_floor_level` from 0.1774 to
perhaps 0.19–0.21, well inside the (0.1774, 0.30) bound already set.

**4. Medicare and Medicaid are absent because there is no health.** For actual
elderly homelessness this is probably the largest missing piece in the real
world, and it is out of scope here.

**5. Housing vouchers do not target the elderly.** `probability_of_voucher`
carries no age dimension, where real Section 8 and Section 202 do.

## THE HONEST CONCLUSION, BEFORE THE MEASUREMENT

Three of the five gaps run the wrong way for the author's hypothesis: the model
is already more generous than the US system on take-up, on the asset test, and
by not taxing benefits. The one real omission, state supplements, is worth at
most a couple of percentage points of the average wage index.

**So the full US system, faithfully implemented, would not close band 5.** The
measured bracket says why: `h_share5` was 0.9355 at a floor of 0.1774 and needed
0.60 to reach 0.518, and a floor above 0.75082 pays every retiree the same
number because PIA is capped there. State supplements move the floor by about
0.02. That is not the mechanism.

Which returns to the finding of 16:52 that this file's companion documents: the
street carries **no disutility at all**, so a household prefers it below an
income of 0.4579, and retiree income runs 0.400 to 0.510. The old are homeless
in this model because the street is free and their income sits astride that
threshold — not because the transfer system is missing a programme.
