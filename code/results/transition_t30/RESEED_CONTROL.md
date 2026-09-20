# The reseeded T=30 run: what must move, and what must not

Written BEFORE the run, on the engine's corollary for controls: a change meant
to be a no-op somewhere has its reference value stated in advance.

## Reference: the old run, loop 0, from the linear ramp

    t=1   p_faced 0.98929   p_implied 0.77695   distance_drug_market 0.21730
    t=1   with_childhood 788.15108   CEV -8.663%   homeless 1.0342% (+19.2% on bench)
    every period          distance_drug_market 0.192 - 0.217, never below
    t=29  p_faced 0.83008   p_implied 0.79938   homeless 1.4038% (+61.7%)

## MUST MOVE

`distance_drug_market` at t=1. The seed sets p_faced(1)=0.77695, the supply
curve's own reading at the old allocation. If the map is the near-contraction
the old path implies, the new gap is a small fraction of 0.21730. **If it is
still of order 0.2, the seed is not the explanation and I am wrong about the
mechanism** -- that is the test, and it is answerable from the first forward
period, about 85 minutes in, not at the end of the loop.

## MUST NOT MOVE

- `price_of_addictive_good_path(30)` stays 0.83349. It is the transition's
  terminal boundary condition, not the previous run's to set, and the seed
  file's last entry is pinned to it rather than carried over from loop 0.
- `pi_v` is 0.076347 in every period of loop 0. Its update is gated behind
  `loop_count>0`, so loop 0 must report the flat handover value exactly as
  before. A different number means the reconciled handover is wrong.
- The 79 input files, the terminal value functions and the initial
  distribution are untouched. Only the price path's starting guess changed,
  plus two prints and the secant's bookkeeping.

## Also newly visible

`TRANSITION MECH` prints h_1, b, lambda_d, p_drug and pi_v every period on the
calibration's own bases, so the welfare path can be attributed without
reconstructing h from mass_homeless over mass_all -- a different base that
cannot be compared with the h_1 the calibration targets.
