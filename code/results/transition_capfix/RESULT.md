# THE CAP FIX TURNS THE t=1 TRANSITION LOSS INTO A GAIN

A controlled before/after: same horizon T=5, same seed, same handover, same
binary settings, ONE source change -- cbc96395 and f05451d5, which pin the
voucher's fair-market-rent standard to the benchmark in a counterfactual.

## BOTH CONTROLS, STATED BEFORE THE RUN, PASSED

    FMR STANDARD t=1   avg_rent 1.0000000  avg_unit_size 0.30208980094400001
    FMR STANDARD t=2   avg_rent 1.0000000  avg_unit_size 0.30208980094400001

Pinned to the benchmark's 0.302089800944 and identical across periods. The
standard no longer tracks who happens to be renting.

                          pre-fix        post-fix      benchmark
    vouchers t=1          0.63943        0.65572        0.69016
    vouchers t=2          0.000000       0.66355        0.69016

## THE RESULT

                          pre-fix        post-fix      vs benchmark 791.39464
    lifetime t=1          790.873        792.194        +0.799
    lifetime t=2          --             792.521        +1.127
    CEV t=1               -9.272%        +2.306%
    CEV t=2               --             +3.273%

The long-run TF steady state is 792.5130, CEV +3.249%. By t=2 the transition has
essentially reached it.

The budget clears at LOOP 0: residuals 0.0327 and 0.0241 against the 5e-2 rule,
where before it ran a 0.445 phantom surplus that pi_v would have spent loops
chasing.

## WHAT THE BUG WAS, AND WHOSE ARGUMENT FOUND IT

The voucher pays min(standard - 0.3*income, actual rent - 0.3*income), and the
standard was model_average_rent(t)*model_average_rental_unit_size(t) -- recomputed
every period from the economy the policy was changing.

The author, 21 September, ruled out both economic explanations before any
measurement did:

  "those with vouchers mostly don't have sud... it can't explain this huge
  reduction in outlays" -- and the measurement agreed: the mass RECEIVING a
  voucher was flat at 3.0443, 2.9506, 2.8856 while the amount each got halved.
  Conditionality ZEROES a user; it cannot scale everyone down.

  "there are no fixed moving costs" -- so housing adjusts smoothly and cannot
  give a discrete halving that then sits flat.

  "so that you don't end up with some compositional change that affects things"
  -- which is the mechanism. The reform displaces renters, the composition of
  those left shifts to smaller units, the standard falls, every voucher shrinks,
  more are displaced. A feedback loop with no behavioural content.

The household's 30 per cent contribution is subtracted AFTER the cap, so a 38
per cent fall in the standard produced a 56 per cent fall in the payment. That
leverage is why one statistic could halve the programme.

## WHAT THIS DOES NOT SETTLE

T=5 is short: the terminal steady state is four periods away, so t=1 inherits
much of the long-run gain. The horizon contaminates BOTH sides of this
comparison equally, so the SIGN FLIP is real -- but +2.306 per cent is not the
transition's true t=1 cost. T=30 is running for that.
