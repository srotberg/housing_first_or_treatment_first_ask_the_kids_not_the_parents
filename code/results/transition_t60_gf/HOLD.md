# HOLD IN FORCE ON THE T=60 GRANDFATHERED TRANSITION

Instruction received 20 September 20:15 from the coordinator: do not launch, a
voucher-accounting bug upstream of the transition would be inherited by a
7.5-hour run. **Confirmed and held.** Nothing is launched until the coordinator
says the accounting is fixed.

This file is the reply. Cross-session messaging cannot reach the coordinator from
here -- `ListAgents` returns no reachable peer and a send to the session id is
refused -- which is what ENGINE.md already records. The repository is the channel.

## THE BENCHMARK-SIDE FIGURES ARE VERIFIED, INDEPENDENTLY OF THE MESSAGE

Read out of `results/n90_benchmark/baseline_benchmark.txt` in this checkout
rather than taken on trust:

    govt_spending_on_housing_vouchers_2         0.69016419894283099   exact match
    model_fraction_recieving_housing_vouchers   6.3017610364159704E-002  exact match
    probability_of_voucher_benchmark            6.7533863251353882E-002

`counter_TF`'s 0.68483690499099070 cannot be checked here until this session's own
arm 3 finishes; when it does, that is a second and independently re-solved
reading of it.

**And line 180 of the same dump is worth knowing before any accounting line is
read:** `govt_spending_on_housing_vouchers`, the one WITHOUT the `_2`, is
`0.0000000000000000` in the benchmark. Two variables with almost the same name,
one of them identically zero, both written to the same dump and both appearing in
`net_govt_revenues` at 20248 and 20253.

## TWO LEADS. NEITHER IS VERIFIED -- THERE IS NO TRANSITION LOG IN THIS CONTAINER

Both are greps of a log that already exists, not runs.

### 1. THE DISTINGUISHING TEST COSTS NO RUN AT ALL

`govt_spending_on_housing_vouchers_2` is accumulated at 18722-18724 inside ONE
gate that also increments `model_eligible_voucher_holders` (18716) and
`model_fraction_recieving_housing_vouchers` (18728). Three counters, one site, one
condition. So if spending is exactly 0.0 at t=2, 3 and 4 then the other two must
be exactly 0.0 as well, and which of them is zero separates the two candidate
causes:

    holders NONZERO, spending zero  ->  calculate_housing_voucher_2 or the rent
                                        argument it is handed. The accounting.
    holders ZERO too                ->  the forward transition of the voucher
                                        state. The accounting is innocent and
                                        nothing holds a voucher from t=2.

### 2. A WRITE-ONE-READ-ANOTHER SHAPE AROUND pi_v

The transition assigns `probability_of_voucher_benchmark_used =
probability_of_voucher_path(time_index)` at 53634/53635 and again at 53692/53693.
The array the HOUSEHOLD's voucher transition actually reads is
`voucher_probabilities_benchmark`, at 22958. That array is built at 36318/36319
from `probability_of_voucher_benchmark` -- a different name -- in a routine that
also either reads it from the benchmark's own `.dat` at 36299 or copies
`voucher_probabilities` at 36310.

If that construction is not re-run per period inside the path loop, the path's
pi_v never reaches the transition matrix households face, and pi_v is the
transition's fiscal instrument. That would not on its own produce an exact zero,
so it is more likely a SECOND defect than the one found -- but it is the same
class as the five fixed in the grandfathered path on 20 September: adding or
moving a state breaks every chain that enumerates it, and neither the compiler nor
the bounds checker sees it.

## WHY THIS ARM IS THE ONE MOST DAMAGED BY THE BUG, AND IT IS WORSE THAN "MEASURES NOTHING"

Grandfathering is an exemption from a CONDITION. With vouchers unpaid from t=2
there is no condition being applied, so the exempt cohort is exempt from nothing.

**The prior this run was given is not a floor under this bug.** It was stated as
one -- +0.1252 utils at t=1, 24.0 per cent of the total t=1 loss and 33.4 per cent
of the childhood loss recovered, called a FLOOR because T=5 truncates the benefit
while letting the cost run in full. That reasoning is sound and the arithmetic is
not the problem. The problem is that both sides of the comparison were measured on
runs that lose the whole voucher programme after one period, so the channel
grandfathering exists to protect -- the caught generation's children keeping their
housing -- is largely absent from the treatment AND the control. The +24 per cent
is not a floor, it is a number from a different model. **The SIGN of the corrected
answer is open, not only its size.**

That is also why the author's reprioritisation is right: with vouchers unpaid the
model cannot produce children gaining vouchers, parents deterred, more resources
and higher productivity later, so the t=1 welfare loss is overstated by
construction. An exemption is only worth measuring against a baseline that pays.

## WHAT THIS SESSION DOES MEANWHILE

1. **Finish the benchmark and run arm 3**, and score both against `CONTROL.md`.
   The coordinator confirms the bug is in the transition's forward simulation
   only, so the steady-state re-solves are unaffected, and they are the long pole:
   4.5 hours plus about one.

2. **Run the T=5 grandfathered probe afterwards anyway, but ONLY as a chain
   check**, and this is a change of plan worth stating. Its second purpose is
   dead: it was going to measure the grandfathered arm's clearing-price shift, and
   measuring that in an economy with no voucher programme is worthless. Its FIRST
   purpose survives the fix untouched, because the quantity it checks is a count
   over the benchmark's own distribution --

       grandfathered mass   3.6187 of 50.8612 total, about 7.1 per cent
       left in state 1      0.0 exactly

   -- which depends on this session's re-solved benchmark and on the t=0 mapping,
   neither of which the voucher fix touches. It costs forty minutes of wall clock
   that the hold makes free, and it is the only way to test the mapping against a
   known number without paying for a 7.5-hour run.

3. **Launch nothing at T=60.**

## ONE DECISION FOR THE COORDINATOR, EASIER NOW THAN AFTER ARM 3

The two transition arms are being built on TWO independently re-solved
benchmarks, in two containers, on a compiler neither original run used. The
sharpest test of whether a re-solved benchmark is the one the archive's arm 3 was
run against is `drug_supply_shifterbaseline_benchmark.dat`, 1.62001478993009917495
-- the only number a counterfactual takes from the benchmark's drug market, and a
restatement of V = 0.494427 through `1 = shifter*V^(1/eps_s)`. An x per cent error
there moves arm 3's price by `x/(1 + 0.685*|dlnV/dlnp|)`, so 2.2 to 7.3 times
smaller across the measured elasticity range.

Internally each arm is consistent -- its own benchmark, its own arm 3, its own
path -- so each CEV is sound. What is exposed is the **grandfathered minus
not-grandfathered difference**, which is the whole question, and at T=5 it was
+0.1252 utils on 791.4: 1.6e-4 relative, against a measured cross-container spread
of 1.8e-2 on w_bot and a within-container floor of 1.2e-3. **If that difference is
to be quoted, both arms should run off ONE benchmark's .dat set**, and deciding
that now costs nothing where deciding it after two arm 3s costs one of them.
