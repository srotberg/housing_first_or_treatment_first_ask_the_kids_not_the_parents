# THE DRUG PRICE IS MADE ENDOGENOUS, 24 September 16:20

The author: *"you need to allow the drug price to be endogenous based on that
elasticities"*.

`code/build_cf_clearing.sh` generates a build-directory copy with exactly four
one-line changes, each asserted by value, and leaves the tracked .f90 untouched:

    44793  clear_drug_market: `if (is_counterfactual==0)` -> `if (.false.)`
           so the clearing branch runs instead of the re-normalisation
    46236  drug_price_start: `if (is_counterfactual==1)` -> `if (.true.)`
           so a warm start is honoured instead of IGNORED on this path
    32257, 32381  the two holder-testing guards, as in build_tf_rationed.sh;
           inert when vcc = 0 and the multiplier is 1, so one binary serves every arm

Tested here: the diff is exactly those four lines, and -O3 builds with 7 warnings
and 0 errors.

`code/remote_cf_clearing.sh tf|omega1|internalise` writes the Housing First
omega_c = 0.06 shifter, 1.6045261392144357 (its last block, V = 0.50141078281734985;
1/V**(1/1.46) reproduces it to 4e-16), as drug_supply_shifterbaseline_benchmark.dat.
Every arm therefore prices drugs on the benchmark's own supply curve at
elasticity 1.46. The cap is 30 blocks. The stillness exit does not look at the
drug market, so the price counts as cleared only when distance_drug_market is
< 5e-3 at the exit block. The clearing branch prints drug quantity, the implied
supply price, the price and distance_drug_market on every call.

The fixed-price TF run with applicants tested was archived, superseded.
Treatment First goes first as the pilot for the clearing path; omega_c = 1 and
internalisation follow once its first blocks show the gap closing.

STILL NOT ADDRESSED: the tax rate is held fixed in every frozen counterfactual,
and omega_c = 0.06 was chosen with the price pegged.

