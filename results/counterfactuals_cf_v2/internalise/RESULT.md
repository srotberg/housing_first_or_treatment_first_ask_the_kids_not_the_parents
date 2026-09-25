# Counterfactual arm: internalise

Housing First omega_c = 0.06 benchmark (stage 1, `code/cfarm_bench`, 12 blocks), arm run by `code/remote_cf_arm.sh internalise`.

## Stage 1 benchmark

- b = 0.08125919405927133, lambda_d = 0.034615070734915473, h_1 = 0.00607822022110719, tau_u = 0.25056437697357403, pi_V (eligibles with a voucher) = 0.2724342741092692
- b against the reference 0.08126063047462809: relative difference -1.768e-05
- drug price 1.0000000000000000, drug quantity V 0.50139852937637885
- benchmark voucher probability 6.7533863251354007E-002

## Voucher probability

- benchmark 6.7533863251354007E-002
- arm, first printed: `probability_of_voucher=   6.7533863251354007E-002   6.7533863251354007E-002   6.7533863251354007E-002`
- arm, last printed: `probability_of_voucher=   6.7533863251354007E-002   6.7533863251354007E-002   6.7533863251354007E-002`
- `HANDOVER voucher probability:   5.9999998658895493E-002 ->   6.7533863251354007E-002`
- `VOUCHER CHECK PASS: arm ran at 6.7533863251354007E-002, benchmark 6.7533863251354007E-002`
- `HANDOVER drug_price_start:   1.0000000000000000      ->   1.0000000000000000` (the applied form; the IGNORED form does not appear)

## Block table

| block | b | lambda_d | h_1 | drug price | distance_drug_market | drug quantity V | CF MOMENTS distance | abs(b(k)-b(k-1))/b(k-1) |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.07788315420137981 | 0.0325568915037133 | 0.00584884589126931 | 0.99683522822469717 | 1.5823858640720556E-002 | 0.48985708192610145 | 1.6285786692910549 |  |
| 2 | 0.07905661766413936 | 0.03369143445294823 | 0.005915328727193229 | 0.99445525523753020 | 6.7920811021945360E-003 | 0.49412641817232783 | 0.002973981559044603 | 1.507% |
| 3 | 0.07987535801712659 | 0.033755369291971 | 0.005919866850436534 | 0.99541408247675978 | 4.5825225043192308E-003 | 0.50069429830892109 | 0.0008187403529872211 | 1.036% |
| 4 | 0.07983680030508672 | 0.033801151044543475 | 0.005921837135201657 | 0.99666838510155531 | 2.5971679740918185E-003 | 0.49994334759496645 | 0.0008620601048068277 | 0.048% |
| 5 | 0.07930453374114028 | 0.0338010552885183 | 0.005919407400446159 | 0.99547376343202909 | 5.9731082586246265E-003 | 0.49460168400589849 | 0.0005322665639464347 | 0.667% |
| 6 | 0.0798633231696489 | 0.03381957651126592 | 0.005924709173277306 | 0.99583117218842943 | 2.5499382069831267E-003 | 0.49995245406926747 | 0.0005587894285086215 | 0.705% |
| 7 | 0.0793543232061345 | 0.03381943315661786 | 0.00592430358717894 | 0.99493960199363929 | 4.4578509075235973E-003 | 0.49509598885827721 | 0.0005089999635144032 | 0.637% |
| 8 | 0.07989732168135415 | 0.03383805156861374 | 0.00592565010182608 | 0.99533809262151729 | 3.6026879358435071E-003 | 0.50033178243322574 | 0.0005429984752196443 | 0.684% |
| 9 | 0.07990519414441583 | 0.03385600564770853 | 0.005926492833966721 | 0.99732721607031694 | 3.0014025808834388E-003 | 0.50018343471630922 | 0.00029564541082494067 | 0.010% |

## Exit

The counterfactual `do while` loop (cf.f90) runs until CF MOMENTS distance <= stopping_rule_frozen_moments (5e-4) AND rental <= 1e-2, housing <= 2e-2, govt budget <= 2.5e-2, drug market <= 5e-3, inheritance within its rule, OR loop_count reaches max_counterfactual_loops.

Distances at exit (last printed):

- `CF MOMENTS distance=   2.9564541082494067E-004  b=   7.9905194144415825E-002  lambda_d=   3.3856005647708527E-002  h_1=   5.9264928339667214E-003`
- `distance_drug_market=   3.0014025808834388E-003`
- `distance_rental_market(transition_length)=   0.0000000000000000`
- `distance_housing_market=   0.0000000000000000`
- `distance_govt_budget=   0.0000000000000000`
- `distance_inheritance_amount=   0.0000000000000000`
- `loop_count=           9`

**Exit reason: the convergence rule fired, not the loop cap.** After block 9 every live distance was inside its rule: CF MOMENTS distance 2.96e-4 <= 5e-4, drug market 3.00e-3 <= 5e-3, and rental, housing, govt budget (no budget clearing in this arm) and inheritance all 0. loop_count was 9, against a cap of 250.

**The family rule did NOT hold over the last blocks.** It needs two consecutive blocks with |b(k)-b(k-1)|/b(k-1) < 0.5 per cent. Only the last block passes (0.010 per cent); block 8 moved b by 0.684 per cent. From block 5 to block 8, b swings by about 0.65 per cent each block (0.0793 / 0.0799 / 0.0794 / 0.0799), in step with the drug price oscillating between 0.9949 and 0.9967. The CF MOMENTS rule is an absolute distance (5e-4 on a b of 0.08, about 0.6 per cent), so it let the loop exit while b was still in that sawtooth. The final b sits at the top of the swing, so read the b change (-1.67 per cent) as uncertain by about +/-0.6 percentage points.

## Final values

- b = 0.07990519414441583 (-1.666% against stage 1)
- lambda_d = 0.03385600564770853 (-2.193%)
- h_1 = 0.005926492833966721 (-2.496%)
- tau_u = 0.24881930029705546 (stage 1 0.25056437697357403)
- pi_V, eligibles with a voucher = 0.2708578590137591 (stage 1 0.2724342741092692); voucher probability `probability_of_voucher=   6.7533863251354007E-002   6.7533863251354007E-002   6.7533863251354007E-002`
- drug quantity V = 0.50018343471630922
- drug price = 0.99732721607031694

## Welfare (verbatim, after the last block)

```
 average_welfare_of_youngest_cohort=   1352.9379735328023
 average_welfare_of_all_cohorts=   1031.8129686902628
 average_welfare_with_childhood=   789.40385536505323
 average_welfare_of_all_cohorts=   1031.8129686902628
 average_welfare_of_youngest_cohort=   1352.9379735328023
 welfare_by_addiction=   1031.1184546768879
 welfare_by_addiction_youngest=   1352.9379735328023
 welfare_by_addiction=   1051.6322158249418
 welfare_by_addiction_youngest=   0.0000000000000000
 CEV from the saved benchmark curve: target=   789.40385536505323       x=   1.6035689933691488E-003
 welfare_of_gains_by_addiction=   1.6035689933691488E-003
```

