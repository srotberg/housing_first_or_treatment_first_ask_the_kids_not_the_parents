# THE VOUCHER BUG REPRODUCED INDEPENDENTLY, AND THE ACCOUNTING IS INNOCENT

21 September, from this session's own T=5 grandfathered probe. The coordinator
owns the fix; this is evidence handed over, not a fix attempted.

## IT REPRODUCES ON A CHAIN THAT SHARES NOTHING WITH THE COORDINATOR'S

    coordinator   govt_spending_on_housing_vouchers_2  0.63943 at t=1, then exact 0.0
    this session                                       0.64937 at t=1, then exact 0.0

Different container, different compiler (GNU Fortran 13.3.0), a benchmark and an
arm 3 both re-solved from scratch, a different price path seed. **So the bug is in
the code and not in anyone's inputs.** That was worth establishing before anyone
spends time on the inputs.

## THE DISTINGUISHING TEST IS ANSWERED, AND IT IS NOT THE ACCOUNTING

`HOLD.md` proposed separating two causes by asking whether the holder COUNTS are
also zero. The counts are not printed along the path, so that exact test could not
be run -- but the same budget line answers it better:

    t=1   vouchers_2= 0.64936655728891546   tests= 1.8098151377179050E-004
    t=2   vouchers_2= 0.0000000000000000    tests= 0.0000000000000000
    t=3   vouchers_2= 0.0000000000000000    tests= 0.0000000000000000

**`tests` is accumulated at a DIFFERENT site with its own accumulator**, and it is
gated on the household holding a voucher. If `calculate_housing_voucher_2` were
returning zero for holders who exist, the drug tests would still be counted.

Both being EXACTLY zero means there is no mass in the voucher-holder states at
t >= 2 at all. **The payment calculation is innocent. It is the forward transition
of the voucher state.**

And t=1 being non-zero is consistent rather than puzzling: at t=1 the holders are
there because the INITIAL CONDITION put them there -- the benchmark's own stock,
plus the grandfathered slab mapped into voucher_gf -- not because any transition
delivered them. The transition matrix only decides where they go NEXT period. So
the first period a transition has to produce holders is t=2, and that is the first
period with none.

## ONE OF MY OWN LEADS IS WITHDRAWN

`HOLD.md`'s second lead said the transition assigns
`probability_of_voucher_benchmark_used` while the matrix reads
`probability_of_voucher_benchmark_used_1`, a write-one-read-another shape.

**That is wrong and it should not cost anyone time.** The transition assigns BOTH
names, at 53634/53635 and again at 53692/53693, and the matrix at 36322 reads the
`_1` one. The pair is consistent. Withdrawn.

It also would not have produced an EXACT zero in any case: a stale pi_v is still a
positive pi_v, so awards would continue at the wrong rate rather than stopping.
Anything that explains this has to explain exact zeros.

## WHERE THE EVIDENCE POINTS

`voucher_probabilities(current, future, income_below_threshold, category)`, built
around 36294-36345. Two features of it matter:

- **the third index gates everything.** `voucher_probabilities(0,0,0,:)=1` -- a
  household above the income threshold never gets one -- and the retention entry
  `voucher_probabilities(1,1,1,:)=1` also requires the third index to be 1. So a
  household misclassified as above-threshold both fails to receive AND fails to
  retain, which is a route to exact zero rather than to a wrong positive number.
- **the grandfathered state is meant to be absorbing.**
  `voucher_probabilities_benchmark(voucher_gf,voucher_gf,:,:)=1` at 36340. The
  exempt cohort should therefore persist and keep being paid whatever happens to
  the ordinary award rule -- and it does not. **That is the sharpest single fact
  here:** whatever empties the holder states is emptying the ABSORBING state too,
  which no ordinary award-rule defect should be able to do.

So the two things worth looking at first are what sets the third index along the
path, and `calculate_future_voucher_index_and_opportunity`, which is where the
household's voucher transition is actually applied and which already needed a
grandfathered branch added to it on 20 September.

## WHAT IT DOES NOT AFFECT

The chain verification in `CHAIN_VERIFIED.md` stands. The bug is in the forward
simulation, and every reference this session matched is either a steady-state
object or a count over the benchmark's own distribution:

    benchmark b, lambda_d, h_1, V, shifter        all within 0.09%
    arm 3 b, lambda_d, h_1, price, pi_v, welfare  all within 1.2%
    grandfathered mass 3.61833 of 50.861572       -0.010%, none left in state 1
    h_1 at t=1  0.0087462 against 0.008747        -0.009%
    t=1 lifetime welfare 790.97323 against 790.9978  -0.0031%

The last two come from the transition and still match, which is not a
contradiction: the T=5 reference they are matched against was measured on a run
carrying this same bug. They test that this chain reproduces that one, which is
what they were for. They do NOT say the economics is right, and they were never
going to.
