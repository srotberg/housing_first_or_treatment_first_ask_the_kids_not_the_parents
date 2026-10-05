# Partial equilibrium without externalities, full model: Housing First weakly dominates Treatment First

The author, 4 October: *"run a pe experiment with no externalities also in the full model ... take the omega_c = 0
case and don't impose any of the penalties ... simulate with piv, pv fixed and the externalities turned off."*
Scripts and design: `code/pe_noext/README.md`. Arm A = Housing First (no policy) with the externalities off and the
drug price clearing; Arm B = Treatment First (tf85_c35's programme) with the same switches and every price held at
Arm A's. All comparisons are weighted by Arm A's stationary distribution.

## Headline

**No household is better off under Treatment First beyond numerical tolerance.**

| weights: Arm A distribution | better off | worse off | indifferent |
|---|---|---|---|
| all households, tolerance 1e-8 utils | 0.0000 (2e-12, see below) | 0.7487 | 0.2513 |
| all households, tolerance 1e-6 utils | 0.0000 | 0.5320 | 0.4680 |
| all households, tolerance 1e-3 utils | 0.0000 | 0.2518 | 0.7482 |
| all households, tolerance 1e-6 x abs(V_A) | 0.0000 | 0.2441 | 0.7559 |
| households with a SUD, tolerance 1e-3 | 0.0000 | 0.9590 | 0.0410 |
| households without a SUD, tolerance 1e-3 | 0.0000 | 0.2235 | 0.7765 |
| entrants (age 26), tolerance 1e-3 | 0.0000 | 0.9973 | 0.0027 |

The loss is concentrated where the policy acts: almost every household with a SUD loses, and so does almost every
entrant. Without a SUD, most households lose a tiny amount, the option value of a voucher they might one day hold
while using. The worse-off share falls from 0.75 at 1e-8 utils to 0.18 at 1e-2.

**Consumption equivalents** (the proportional change in Arm A's consumption, every period for the rest of life,
worth as much as the move to Treatment First; negative = Treatment First worse):

| group | share | CEV of the group |
|---|---|---|
| population (every state alive, ages 26-85) | 1.0000 | **-1.91%** |
| affected, abs(dV) > 1e-3 utils | 0.2518 | -4.55% |
| affected, abs(dV) > 1e-6 utils | 0.5320 | -2.65% |
| with a SUD | 0.0384 | -31.29% |
| without a SUD | 0.9616 | -0.19% |
| **newborn, adult value at 26** (on Arm A's newborns) | 0.0197 | **-1.50%** |
| newborn, childhood-inclusive -- **NOT externality-free** | | **+1.88%** |

"CEV of the group" solves the group's weighted SUM of values. The mean of the state-by-state CEVs is
smaller: -0.57% for the population, -1.33% for newborn adults. That mean leaves out the 0.26% of the population (6.8%
of those with a SUD) whose loss is worth more than half their consumption for life, beyond the walk's grid at x =
-0.5 (`analysis.txt`).

**The childhood-inclusive newborn number is not part of the result.** It adds the child's own utility from its
parent's consumption and housing (calculate_childhood_utility) to the adult value. That is exactly the parent-to-child
channel switched off here, and it reverses the sign. The childhood term rises 0.82 utils because Treatment First cuts
parents' drug use by 60 per cent. The adult part falls 0.19 utils (lifetime units, beta^K = 0.25). With
omega_c = 0, no household's own value contains that childhood term. It is reported because the brief asked for it.

## The four states with dV > 0 beyond 1e-8: a missed maximum, not a channel

4,486 occupied states have V_B > V_A, with a combined mass share of 1.6e-4. Of these, 4,482 gain less than 1e-8
utils (the solver's noise). The other four gain +5.27 utils each and have a combined mass share of 2.2e-12. They are all the same grid
point: age 27 (model age 3), financial index 5, housing index 0, voucher holder, productivity node 8 in each child class,
with two clean unemployment states. At that point:

* Arm A's solver picks *use, housing 0*, worth 1290.26. Arm B's picks *abstain, housing 1, consumption 0.21*, worth
  1295.53. B's choice is open to A, since an HF voucher has no condition attached, and the flow is the same at the
  same prices.
* A's continuation values at B's destination (age 4, financial index 8 and 9, housing 1, voucher 0 and 1, every clean
  unemployment state) are equal to B's to four decimals (V_A - V_B prints +0.0000 at every one of them). So, up to that rounding, B's choice is worth
  about 1295.53 under A too. A's maximisation missed it at this point.
* Both value functions are non-monotone in assets around there (B dips to 1292.0 at index 8 between 1299.1 and 1306.9;
  A dips at index 8 too). This is a non-global maximisation on a coarse asset grid. It is not a remaining
  externality or price channel. No channel survives the check below.

## What is switched off, held, and not held

**Externalities off, in both arms** (HANDOVER lines in `arm_A/cf.log.gz`, `arm_B/cf.log.gz`):

| channel | switch | log |
|---|---|---|
| the parent values its child (flow term and continuation) | weight_on_child 0 | `HANDOVER weight_on_child: 0 -> 0` (*) |
| the child's productivity penalty for a parent with a SUD at death | penalty_child_addicted 0 | `0.24 -> 0`; `DIAG child-class factors: 1 1` |
| the same for a homeless parent | penalty_child_homeless 0 | `0 -> 0` (asserted) |
| the penalty in **retirement income**: the benchmark's Social Security benefit by productivity node, which the counterfactual uploads, was computed from class-1 earnings at 0.76 | SS_NO_CLASS: in each arm's copy of the file, each class-1 node gets the class-0 benefit | `SS_NO_CLASS: class-1 benefits 0.282 ... 1.194 -> ...` |
| the homelessness disamenity (welfare statistics only) | kappa_x 0 | `0.934 -> 0` in the handover file; `kappa_x= 0` in the walk |

(*) The counterfactual binary never reads calibration_state.dat, so the declaration (0) is what the handover replaces.
The accepted no-policy arm's line read `0 -> 0.085`. Nothing in the counterfactual path writes weight_on_child
afterwards. calibrating_model is not called. print_all_moments' omega block only zeroes and restores it, and it was
skipped here (`OMEGA SKIPPED child counterfactual off by measure_child_gap`, once in each arm).

**Check that no inherited channel is left.** In both arms, V(class 0, node k) and V(class 1, node k) are equal at
every evaluable state (maximum difference exactly 0.0). Children of parents with a SUD face the same economy as other
children.

**Checked and left on:** `child_penalty_off` (it removes only the inherited-penalty part of the child term, which
omega_c = 0 already removes). `rho_intergenerational` 0.5: the newborn's productivity draw is persistent in the
parent's node, and with the penalties at zero that node carries no class factor. Policy reaches it only through which
parents die at which node. That shifts the newborns' mix (Arm A's newborn draw starts 0.0094, 0.0159, ...; Arm B's
starts 0.0101, 0.0169, ...) but not any household's value. Every comparison here is weighted by Arm A's distribution,
so the mix does not enter. The newborn's initial wealth and inheritance are the same for every node and class.

**Held between A and B:**

| | how | value |
|---|---|---|
| drug price | drug_market_adjuster 0 (B), start = A's last solve | 1.0305057924439740 in every pass of B |
| pi_V | adjust_taxes 0 | 0.067533863251354 in both |
| house price | patch in cf_fix2_pe: the build pegs it and then moves it 2% toward the supply curve each pass, so without the patch it is not held | 12.049246174348939 (A's last solve) in every pass of B |
| rent | fix_rent = 1, infinite rental supply elasticity (build) | calibrated |
| inheritance, lump-sum transfer | residual_bequests_to_government = 1, so adjust_inheritance never runs; transfer 0 | benchmark's |
| labour income tax | adjust_taxes 0; cf_fix keeps the uploaded value | 0 |
| SS benefits, median and average income | uploaded from the benchmark | benchmark's (class-1 SS equalised) |

**Not held:** the government budget (Treatment First's saving goes unspent: net revenue +0.19%, within 0.012 of
Arm A) and the newborns' productivity mix (above).

## Guards

* Arm A: VOUCHER CHECK PASS (0.067533863251354 against the benchmark's); DIST CHECK PASS, 9 passes, largest final
  4.69e-5 (rule 5e-5, at least 70 sweeps); drug market gap 4.8e-4 at the last update, and the last pass's moments
  moved 9.3e-6.
* Arm B: DIST CHECK PASS, 3 passes, largest final 4.61e-5. Every pass ran at Arm A's last-solve prices (`PE USED`).
  pi_V printed 0.067533863251354 throughout.
* The CEV walk (`code/pe_noext/patch_walk.py`, walk-only mode of Arm A's build on Arm A's saved policies). Tested on
  the saved benchmark against the benchmark binary's own welfare curve: adult value +2.6011 utils (curve +2.6012) at
  x = +0.05 and -2.7883 (-2.7880) at -0.05. On Arm A its childhood term at x = 0 (450.69716) matches Arm A's reported
  childhood utility. Its level at x = 0 differs from V_A by +0.64 utils on average, the known discretisation loss of
  the walk (the benchmark shows +0.42 at age 1). The CEVs use only W(x) - W(0), so the loss cancels. W is increasing
  in x at all of the mass.
* The owner block holds no mass in either arm (renters only), so it does not enter.

## What switching the externalities off does to the benchmark (Arm A against the accepted no-policy arm)

| | accepted no-policy (`transition_2c/arm_null`) | Arm A, no externalities | change |
|---|---|---|---|
| drug price | 1.0003 | 1.0306 | +3.03% |
| drug use b | 0.08959 | 0.09013 | +0.61% |
| SUD lambda_d | 0.03814 | 0.03836 | +0.57% |
| homelessness h_1 | 0.006185 | 0.006021 | -2.66% |
| voucher holders | 0.06287 | 0.05898 | -6.19% |
| voucher spending | 0.6886 | 0.6462 | -6.15% |
| net government revenue | 5.892 | 6.383 | +8.33% |

Without the child penalty, demand for drugs rises: b is 0.101 at the starting price in the first pass. The price clears 3%
higher, and that brings use back to within 0.6% of the benchmark. The parent's own lifetime utility no longer counts
its child's loss, and its children no longer inherit lower earnings. The higher net revenue and the fall in
homelessness and voucher use come from that second change: class-1 children now earn class-0 wages.

## Arm B against Arm A (Treatment First at Arm A's prices)

| | Arm A (HF) | Arm B (TF, prices held) | change |
|---|---|---|---|
| drug use b | 0.09013 | 0.03587 | -60.20% |
| SUD lambda_d | 0.03836 | 0.01510 | -60.65% |
| homelessness h_1 | 0.006021 | 0.006213 | +3.19% |
| voucher holders | 0.05898 | 0.05424 | -8.03% |
| eligibles getting a voucher | 0.2685 | 0.2485 | -7.46% |
| treatment take-up | 0.2497 | 0.2986 | +19.61% |
| SUD share of the homeless | 0.2055 | 0.1611 | -21.60% |
| programme cost: voucher spending | 0.6462 | 0.5975 | -7.54% |
| programme cost: drug tests | 0 | 0.00165 | |
| net government revenue | 6.3830 | 6.3950 | +0.19% |

Full tables: `arm_A_vs_accepted_null.txt`, `arm_B_vs_arm_A.txt`, `arm_*/final.txt`; the household comparison:
`analysis.txt`, `analysis.json`.

## Files

`arm_A/`, `arm_B/`: cf.log.gz, the handover each arm read, the arm script's output. `walk_A.log.gz`: the CEV walk
on Arm A. `walk_benchmark_test.log.gz`: the walk's test on the benchmark. Run directories (not in git):
`code/cfarm_null_pe_noext`, `code/cfarm_tf_pe_noext`, `code/pe_walk_A`.
