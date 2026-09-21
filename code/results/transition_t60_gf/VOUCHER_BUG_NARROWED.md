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

---

# CORRECTIONS, 21 September, after reading the coordinator's newer source

Three things in this file need amending. It is left standing with the amendments
below rather than rewritten, because two of them are mistakes worth recording.

## 1. THE COORDINATOR WAS ALREADY PAST THIS, AND THIS FILE DID NOT KNOW IT

My push helper rebases onto the shared branch before every push, so the
coordinator's later commits have been arriving in this working tree all along --
and the source now carries four new per-period diagnostics (`TRANSITION VOUCHER
DIAG`, `VOUCHER CENSUS`, `AMORT DIAG`, `INCOME GATE`) plus comments that state the
diagnosis directly:

> At t=1 holders=0.2744 and at t=2 holders, receiving, eligibles_getting and
> drug_tests are all exactly zero, so the state is gone rather than unpaid.

So the conclusion above -- the payment is innocent, the voucher STATE is empty --
is confirmed independently and by a more direct instrument than mine. It was not a
new finding by the time it was written. What survives as this session's own
contribution is the INDEPENDENT REPRODUCTION on a separately re-solved chain, which
rules out the inputs, and the closed budget arithmetic below.

**None of those diagnostics appear in this session's T=5 log, and that is not a
finding either.** The binary was built at 19:09 and they were added afterwards. A
run's log can only contain the diagnostics its binary was compiled with, which is
worth remembering before reading a silent diagnostic as a silent code path.

## 2. THE `tests=` ARGUMENT IS WEAKER THAN I PRESENTED IT

I rested the "accounting is innocent" conclusion on `tests=` going to exactly zero
at a site with its own accumulator. The coordinator's own comment says that
variable is misleading:

> Note that "tests=" above prints a SCALAR, not a path: there is no (time_index)
> on govt_spending_on_drug_tests. Its going to zero after t=1 is this print's
> artefact and not a second symptom.

Tracing it: `govt_spending_on_drug_tests` is declared scalar at 505 and assigned at
20364 as `voucher_conditional_on_clean*cost_per_drug_test*model_drug_tests(time_period)`
-- so it is re-assigned per period from an array that IS a path, and the printed
value does correspond to the period printed. On that reading the argument holds.

**But it should not have been the load-bearing evidence, and I am withdrawing it as
such.** Resting a published claim on a variable whose owner has documented it as
misleading, when a direct instrument for the same question exists, is the wrong
order of operations regardless of whether the inference happens to survive. The
conclusion stands on `holders`, `receiving` and `eligibles_getting` all being
exactly zero, which is what actually settles it.

## 3. WHAT DOES SURVIVE AS EVIDENCE FROM THIS CHAIN: THE BUDGET ARITHMETIC CLOSES

`net_govt_revenues` IS printed at loop 0, against a constraint of 6.0219346:

    t   net_govt_revenues   residual    vouchers_2
    1   6.0646344           +0.0427     0.649367
    2   6.6693559           +0.6474     0.0
    3   6.6358740           +0.6139     0.0
    4   6.6073047           +0.5854     0.0

The coordinator's `t5_fixed.log` had 0.0534 then 0.693, 0.686, 0.680. Same shape,
independently, on a different benchmark and compiler.

And the jump in the surplus from t=1 to t=2 is **+0.6047** against a lost voucher
spend of **0.649367** -- within 7 per cent, the remainder being small movements in
social security, UI, food stamps and bequests. **The surplus is quantitatively the
unpaid programme**, which is the claim the hold rests on, now closed on this
session's own numbers.

---

# AND ONE NEW FINDING THAT BITES THE GRANDFATHERED ARM ONLY

**`TRANSITION VOUCHER CENSUS` CANNOT SEE THE GRANDFATHERED STATE, AND WILL REPORT
THE EXEMPT COHORT AS "excluded".**

    8337:  real(8), dimension(0:2) :: model_mass_by_voucher_state=0
    18486: model_mass_by_voucher_state(min(max(voucher_index,0),2))=&
    18487:     model_mass_by_voucher_state(min(max(voucher_index,0),2))+...

The array has THREE slots. With `grandfather_voucher_states=1`,
`voucher_gf = voucher_state_max = 3`, and `min(max(3,0),2) = 2`. So the
grandfathered mass is **clamped into slot 2 and counted as "excluded"** -- the
state for a household BARRED from vouchers, which is the exact opposite of exempt.

Three consequences:

- On the no-grandfathering arm the census is correct, because only three states
  exist. **It is wrong only on the grandfathered build**, which is this session's.
- The clamp means it does not crash, does not go out of bounds, and the printed
  `total` still adds up -- so nothing flags it. The 3.6183 of grandfathered mass
  simply appears under the wrong label.
- Anyone reading that census on the grandfathered arm to chase the missing voucher
  mass would conclude the exempt cohort had been EXCLUDED from vouchers, and would
  be chasing an artefact of the diagnostic.

This is the class the brief names: *adding a value to a state variable breaks every
if-chain enumerating the old values, and neither the compiler nor the bounds checker
sees it.* The `min(...,2)` is what hides it here, and the same clamp appears at
11074-11076 in the steady-state `DIAG voucher-state mass` print.

It is NOT a fix this session should make -- the model is frozen and the coordinator
is editing this routine now -- but the census should gain a fourth slot before it
is read on a grandfathered run, or it will mislead exactly the person trying to
find where the voucher mass went.
