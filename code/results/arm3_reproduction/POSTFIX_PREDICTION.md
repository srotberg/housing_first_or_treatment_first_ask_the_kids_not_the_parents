# WHAT THE RENTAL-STANDARD PIN SHOULD DO TO ARM 3. Stated before the run landed.

21 September, 01:15. Arm 3 is re-solving on the fixed source (cbc9639 + f05451d).
This is a genuine before/after in ONE container -- same benchmark, same handover,
same binary settings, one source change -- which is the controlled pair the
standing rule asks for and which the archive could not provide.

## THE PRE-FIX VALUES, MEASURED HERE

    govt_spending_on_housing_vouchers_2         0.68646288
    model_fraction_recieving_housing_vouchers   0.06222395
    b        0.045265    lambda_d  0.018415    h_1  0.006521
    price    0.834257    pi_v      0.075482
    lifetime welfare 792.50392                 CEV +3.4337%

## WHAT THE PIN CHANGES, AND THE DIRECTION

The fix replaces the counterfactual's drifting
`model_average_rent(t)*model_average_rental_unit_size(t)` with the benchmark's
calibrated product, everywhere, from the normalisation onward. In a STEADY STATE
the product barely drifts -- that is the coordinator's own point -- so arm 3 moves
only by the gap between its own standard and the benchmark's:

    benchmark standard    0.302089800944
    long-run TF standard  0.303010526294      +0.305%

**The pin therefore LOWERS arm 3's fair-market-rent cap by about 0.305 per cent**,
and a lower cap means a smaller voucher, so:

    govt_spending_on_housing_vouchers_2   should FALL by roughly 0.3 to 0.4%
                                          from 0.68646288 to about 0.6837
    the count receiving                   should barely move: the cap changes the
                                          AMOUNT, and eligibility is a separate
                                          test
    b, lambda_d, h_1, price, pi_v         should move far less than their
                                          reproduction misses of 0.05 to 1.13%
    CEV                                   should stay near +3.4337%, moving by
                                          hundredths of a point at most

The coordinator's own estimate is that arm 3's "voucher moves about 0.4 per cent
-- far too small to move the published +3.249 per cent CEV", which is the same
prediction from the same numbers.

## THE TEST, AND WHAT WOULD FALSIFY IT

If spending falls by roughly a third of a per cent and nothing else moves
materially, the pin is what it claims: a policy parameter held at its data value,
with no steady-state cost.

**What would falsify it:** spending moving by materially more than half a per cent,
or any of b, lambda_d, h_1 moving by more than about half a per cent. Either would
mean the pin is not a small correction in the steady state, and that the archive's
arm 3 -- and hence the published +3.249 per cent CEV, and the transition's terminal
condition -- rests on the drifting product rather than on the pinned one.

## WHY THIS PAIR IS WORTH RECORDING AT ALL

`model_average_rental_unit_size=` printed in the log does NOT test this. It reads
0.302091520665 in the pre-fix log and in the post-fix one, identically, because
that print happens at upload when the benchmark's value is read, before the solve.
An earlier reading of this session took it as evidence the pin was active. It is
not evidence either way. **The converged dump in `counter_TF.txt` is the only place
the question is answered.**
