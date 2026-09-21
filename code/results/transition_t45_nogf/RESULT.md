# T=45, NO GRANDFATHERING, LOOP 0. THE SHAPE IS RIGHT AND THE NUMBERS ARE NOT YET.

21 September, 02:49 to 07:58. 5,192 age sweeps, 5h09m, one loop, on the fully
corrected source (a65b9dd + c463dd2 + cbc9639 + f05451d) with the post-fix
terminal anchor (pi_v 0.076876159888350143, drug price 0.83283631757376753).

## THE PATH

              t=1        t=44      long-run TF
    h_1     +18.74%     -0.62%       +1.3%
    b       -45.96%    -48.71%      -44.6%
    lambda_d  0.00%    -52.34%      -45.2%
    CEV      +2.318%   +2.983%      +3.249%

**Welfare is a gain in every one of the 44 periods.** It ranges +2.3 to +3.8 per
cent and settles near +3.0. There is no trough anywhere on the path. The -9.272
per cent at t=1 that the 20 September run reported, and that the whole
grandfathering rationale was built on, does not exist on a working cap.

Homelessness rises 18.7 per cent on impact, is back to the benchmark by about
t=23 and ends slightly below it. Participation falls 46 per cent immediately and
is at its terminal value from period one. The SUD stock decays smoothly, crosses
its long-run value around t=17, and overshoots.

## THE HORIZON QUESTION IS SETTLED, AND 45 HAS ROOM TO SPARE

Everything is at or past its terminal value by the early twenties. The last
twenty periods carry the overshoot returning to the boundary and little else.
**Post-fix, T=30 would have sufficed**; the "T=30 IS TOO SHORT" finding was the
collapsing fair-market-rent cap from end to end, as predicted in
`../transition_t30_nogf/HORIZON_PREDICTION.md` before this run's forward pass.

## WHAT MUST NOT BE QUOTED YET

    drug market      max 0.1818 over 44 periods, rule 0.01  -> outside (18.2x)
    budget residual  max 0.0738 over 44 periods, rule 0.05  -> outside (1.5x)

Neither equilibrium object has cleared, so every number above is an iterate.

**p_drug** sits at about 0.15 excess demand in EVERY period -- flat, not
decaying along the path, which is the signature of a level error in the seed
rather than something the path works off. The seed was measured on the pre-fix
economy, where participation fell 27 per cent; here it falls 46. The seed is
worse for this economy than it was for the one it came from, through no fault of
its own.

**pi_v is a flat line at 0.0768762 across the whole path.** Its update only
switches on at loop 1, so panel 3 of the figure shows the terminal value held
constant, not a solved path. The budget residual drifts out to 1.5x its rule in
the late periods precisely because no instrument has moved there yet.

## ONE THING TO WATCH

The CEV path is not smooth at t=2 and t=3: +3.302 then +2.728. That is loop-0
iterate noise and should settle as the price path converges. **If it survives
loop 1 it is worth a look** rather than an explanation.

## FILES

    transition_loop0.png            the five panels
    t45_loop0.log.gz                the run log
    drug_price_path_seed_loop0.txt  p_drug, 44 entries, as saved by the run
    pi_v_path_seed_loop0.txt        pi_v, 44 entries (flat at the terminal)
    h1_path_reference_loop0.txt     h_1, a reference, never read back

The run directory also holds house_price, rent and lump_sum _out files. Those
three are CONSTANTS under peg_prices_in_counterfactual=1 and are not archived
here; see `../transition_t30_nogf/TWO_OBJECTS_NOT_FIVE.md`.
