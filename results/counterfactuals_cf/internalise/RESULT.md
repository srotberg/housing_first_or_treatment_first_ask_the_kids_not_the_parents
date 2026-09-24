# Internalise counterfactual (omega_c = 0.06, kappa_x 0.9329, adjust_taxes 0)

Run with `code/remote_cf_arm.sh internalise` on commit 5ab5d5f. The next commit on
the branch, 3b509b7, only changes ENGINE.md. Both stages ran in
`code/cfarm_internalise/` in one container, with no relaunch. Stage 1 ran from
16:07 to about 20:08 UTC and stage 2 from about 20:08 to about 20:23 UTC.

## Stage 1: the Housing First omega_c = 0.06 benchmark (tracked source, 12 blocks)

The handover lines were checked: `weight_on_child -> 0.06`, `kappa_x -> 0.9329`
and `frozen_stop_after_blocks -> 12`.

| block | b | lambda_d | h_1 | BLOCK MOVE |
|---|---|---|---|---|
| 1 | 7.1895755309827059E-002 | 3.1459414195080346E-002 | 7.0782207746248119E-003 | 1.0 |
| 2 | 8.5114919580758272E-002 | 3.5931240666125491E-002 | 6.4900190282358378E-003 | 0.2061 |
| 3 | 8.5318988163538834E-002 | 3.6354841351990873E-002 | 6.3162036690321069E-003 | 8.53E-002 |
| 4 | 8.4482398083339835E-002 | 3.6108799062232015E-002 | 6.1536867921687301E-003 | 3.91E-002 |
| 5 | 8.3842607255431384E-002 | 3.5838341430792814E-002 | 6.1422144250049904E-003 | 1.86E-002 |
| 6 | 8.2252812727503344E-002 | 3.5457525142433756E-002 | 6.1185091020692804E-003 | 1.90E-002 |
| 7 | 8.1784053933381173E-002 | 3.4934300227028321E-002 | 6.1167141617694204E-003 | 1.48E-002 |
| 8 | 8.1374496845001393E-002 | 3.4797335439116131E-002 | 6.0882428340514310E-003 | 5.01E-003 |
| 9 | 8.1192665130311384E-002 | 3.4660179947660352E-002 | 6.0732001018812707E-003 | 3.94E-003 |
| 10 | 8.1254789923681070E-002 | 3.4628721069939736E-002 | 6.0642214828726428E-003 | 1.48E-003 |
| 11 | 8.1251543827946943E-002 | 3.4604962071646941E-002 | 6.0784193298358677E-003 | 2.34E-003 |
| 12 | 8.1245138655032023E-002 | 3.4601960986537866E-002 | 6.0788095759818986E-003 | 1.56E-004 |

Final values: **b = 0.081245138655032023, lambda_d = 0.034601960986537866,
h_1 = 0.0060788095759818986.**

Against the reference Housing First b = 0.081260630474628087, the relative
difference is **-1.91E-4**, inside the 1e-3 flag.

The benchmark log also prints
`KAPPA_X PROBE: IMPLIED kappa_x=  0.24717855425188087 against the coded  0.93289999999999995`.
It is recorded here without further comment.

## Stage 2: the internalise arm (counterfactual binary)

The handover lines were checked: `weight_on_child -> 0.06`, `kappa_x -> 0.9329`,
`internalise_homelessness_cost 0 -> 1`, `adjust_taxes -> 0` and
`drug_price_start 1.0 -> 1.0`. drug_price_start was APPLIED, not IGNORED.

The counterfactual loop ran 4 times. Each row is one pass of the loop. The price
shown is the one `clear_drug_market` printed after the pass; the price the
households faced in pass 1 was 1.0.

| block | b | lambda_d | h_1 | drug price | distance_drug_market |
|---|---|---|---|---|---|
| 1 | 7.7844464915820588E-002 | 3.2524233734685999E-002 | 6.1784928004499605E-003 | 0.99660482590266330 | 1.6975870233723045E-002 |
| 2 | 7.8495926423297058E-002 | 3.3472358068804900E-002 | 6.2509094230043223E-003 | 0.99162180188452931 | 1.3292594959238513E-002 |
| 3 | 7.9259787797173839E-002 | 3.3518125788238984E-002 | 6.2526755341800440E-003 | 0.99126664839174139 | 8.8436765512756033E-004 |
| 4 | 7.9291873132165069E-002 | 3.3534086993451367E-002 | 6.2530025538305133E-003 | 0.99110873326759885 | 2.7219561563252004E-004 |

`CF MOMENTS distance` by pass: 1.6286, 2.9838E-003, 8.1492E-004 and 2.8038E-004.
The drug-market distance shrank on every pass, and the price never hit a bound.

### Exit

The loop left its `do while` normally, with every distance inside its rule and
loop_count = 4, far below max_counterfactual_loops = 250. A normal save and CEV
followed, then `simulation_ended`, and all the invariants passed. The last pass,
the one that ended the loop, had these distances:

| distance | value | rule | inside |
|---|---|---|---|
| CF MOMENTS (max abs change in b, lambda_d, h_1, y) | 2.8038253679052438E-004 | 5E-004 (stopping_rule_frozen_moments) | yes |
| drug market | 2.7219561563252004E-004 | 5E-003 | yes |
| rental market | 0 | 1E-002 | yes |
| housing market | 0 | 2E-002 | yes |
| govt budget | 0 (adjust_taxes 0) | 2.5E-002 | yes |
| inheritance amount | 0 | 2E-003 | yes |

The last rule to be satisfied was the CF-moments rule: in pass 3 its distance,
8.1E-4, was still above 5E-4, although the drug market was already inside its
rule.

**The family rule did NOT hold.** It asks for two consecutive blocks with
|b(k)-b(k-1)|/b(k-1) < 0.5 per cent. The relative changes in b were:

| pass | relative change in b |
|---|---|
| 1 to 2 | +0.837% |
| 2 to 3 | +0.973% |
| 3 to 4 | +0.040% |

Only the last step is under 0.5 per cent, so the arm stopped on the CF-moments
rule after a single quiet pass. The CF-moments rule is an ABSOLUTE 5e-4 on b,
which is about 0.6 per cent of b. That is looser than the family rule.

## Final outcomes (model units)

| outcome | value |
|---|---|
| b (drug users) | 7.9291873132165069E-002 |
| lambda_d (disorder rate) | 3.3534086993451367E-002 |
| h_1 (homelessness rate) | 6.2530025538305133E-003 |
| tau_u (treatment take-up) | 0.25320584756662545 |
| pi_V (eligibles with a voucher) | 0.24837193695854318 |
| drug quantity V (at the last clear) | 0.49459054064634655 |
| drug price | 0.99110873326759885 |

For comparison, `model_drugs_consumed_by_users` is 0.49466934464028611 in the
final statistics.

## Change against the stage-1 benchmark

| outcome | change |
|---|---|
| b | -2.404% |
| lambda_d | -3.086% |
| h_1 | +2.866% |

## Welfare lines (cf.log, verbatim, final pass and after)

```
 average_welfare_of_youngest_cohort=   1352.2469203437363
 average_welfare_of_all_cohorts=   1031.5267770751695
 average_welfare_with_childhood=   788.99697049291763
 average_welfare_of_all_cohorts=   1031.5267770751695
 average_welfare_of_youngest_cohort=   1352.2469203437363
 welfare_by_addiction=   1030.9067275337493
 welfare_by_addiction_youngest=   1352.2469203437365
 welfare_by_addiction=   1049.3968549523599
 welfare_by_addiction_youngest=   0.0000000000000000
 CEV from the saved benchmark curve: target=   788.99697049291763       x=  -1.0264862008517617E-002
 welfare_of_gains_by_addiction=  -1.0264862008517617E-002
```

The CEV line is the binary's own output; nothing was computed from it here.
