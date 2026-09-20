# Arm 3's terminal condition, compressed

The ten `*counter_TF.dat` files a transition reads as `long_run_simulation` --
its TERMINAL steady state, the boundary condition that ends the backward pass --
plus `counter_TF.txt`, the arm's own moment dump. 331 MB becomes 43 MB; the
largest member is 41.9 MB, well under GitHub's per-file limit.

## Why this is committed

Same argument `seeds/benchmark_dat/README.md` makes for the initial condition,
one link further down the chain. The author, 20 September: *"make both arms come
off the same benchmark and code"*. The benchmark was shared by a1da5ab. Arm 3
was not, and it is just as much a shared input: it is the terminal condition of
BOTH transitions. Two separately solved arm 3s put the difference between two
solves straight into the difference between the arms, which is the quantity the
paper wants.

The size of that risk, measured here rather than assumed: this arm 3 and the
archive's differ by 0.05 per cent on b, 0.21 on lambda_d and 0.50 on h_1. The
T=5 arm difference was 1.6e-4 relative. So an unshared terminal condition is
noise one to two orders of magnitude LARGER than the signal.

## What this arm 3 is

Solved 20 September in the cold-start container, warm started from
`seeds/benchmark_dat` (the archive benchmark) at price 0.833490 and pi_v
0.076347, under `seeds/PARAM_HANDOVER_arm3_converged.txt` --
`drug_market_adjuster` 0.1, which is the setting the only arm 3 run that ever
passed its own acceptance test used, and which the Fortran does NOT default to.

    quantity    this run     CONVERGED.md   gap
    b           0.045262     0.045287      -0.05%
    lambda_d    0.018421     0.018460      -0.21%
    h_1         0.006509     0.006542      -0.50%
    pi_v        0.076070     0.076347      -0.36%
    price       0.832814     0.833490      -0.08%
    CEV        +3.2933%     +3.249%       +0.044pp

    three live rules   CF moments 4.05e-04 (5e-4)   ok
                       budget     1.74e-02 (2.5e-2) ok
                       drug gap   3.25e-03 (5e-3)   ok
    acceptance test    |db| 1.624e-04 -> 8.848e-05 -> 6.325e-06, monotone
                       b inside the measured cycle band [0.04492, 0.04732]

## IT IS A SECOND SEED, WHICH IS WHAT CONVERGED.md ASKED FOR AND DID NOT HAVE

That file's closing rule: *"An arm that has been solved once has not been shown
to be solved. A converged flag on a single run is not evidence; the same arm
from a different seed, or the trajectory of the last several loops, is."*

It seeded at the CYCLE MEAN, price 0.8375 and pi_v 0.074687. This run seeded at
the CONVERGED point, 0.833490 and 0.076347. Different seeds, same equilibrium to
half a per cent on every quantity. So b = 0.045287 is the fixed point, and the
two earlier runs at 0.047121 and 0.045209 were the peak and the trough of the
undamped cycle rather than two candidate answers.

**And the drug-gap caveat is resolved.** CONVERGED.md finished at -4.9903e-03
against a rule of 5.0e-03 -- 99.8 per cent of tolerance, not decaying -- and
concluded "b of 0.045287 is therefore likely a slight UNDERSTATEMENT". From this
seed the gap closed to +3.25e-03, two thirds of tolerance, with the sign flipped,
and b came in at 0.045262. The understatement was not material.

## The fixes this run does and does not carry

Solved on the source at 5bd9da5, so it does NOT carry a65b9dd (the median_income
initialiser) or c463dd2 (the unguarded division). Both are MEASURED inert for a
steady-state arm rather than argued so:

- arm 3 builds at `transition_length=1`, so `median_income` is a one-element
  array and `median_income(1)` is assigned before use; the bug needed interior
  periods `t>=2` that nothing assigns.
- the decisive check is that households receive vouchers at all. In a
  counterfactual the cutoff term is `0*median_income(1)`, and `income < NaN` is
  false for everyone, so a NaN there empties the programme. This run reports
  `model_fraction_recieving_housing_vouchers = 6.2426e-02`.
- 3ed3b89's `transition_tolerance_factor` is
  `solve_transition_dynamics*2+(1-solve_transition_dynamics)*1`, which is 1 here.

If a later fix touches the steady-state path semantically, this set must be
re-solved and replaced, and that is the one thing to check before reusing it.

## It also confirms that Treatment First does not save money

    quantity                              benchmark    this arm 3
    govt_spending_on_housing_vouchers_2   0.690164     0.688815
    model_fraction_recieving_vouchers     6.3018%      6.2426%

Within 0.2 per cent on spending. pi_v rises and coverage falls slightly;
conditionality re-sorts who holds a voucher rather than shrinking the programme.
That premise carried the whole voucher-accounting diagnosis and had rested on a
log no other container could read. It now rests on a re-solve.

## Unpacking

    cd <transition run directory>
    for f in <this dir>/*.dat.gz; do gzip -dc "$f" > "$(basename "${f%.gz}")"; done
