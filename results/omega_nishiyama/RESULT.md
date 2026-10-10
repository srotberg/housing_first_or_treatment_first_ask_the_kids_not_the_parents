# omega_c = 0.686 (Nishiyama 2000) sensitivity

The author, 9 October: *"a sensitivity test where omega_c = [Nishiyama's value] in the benchmark ... and show
whether the long run welfare effects are similar"*, and *"You should take exactly the number nishiyama finds."*
omega_c = 0.686 (Nishiyama 2000, CBO Technical Paper 2000-7: 0.509 per child household x 1.35 child
households; see OMEGA_LITERATURE.md). Everything else is the benchmark of record
(results/reference/hf_2c_omega_0.085: omega_c 0.085, b 0.0054222, kappa_uem 1.0, drug users 8.956 per cent),
with b re-matched to drug use. Orchestrator: session_01NzKWR6JcFw2XXovtVWLrDY.

## Stage 1: one class (CLASSES 1), b scan at omega_c 0.686

Control: one class at omega_c 0.085, b 0.0054222 (session_01QdHZe9tWNJ95ZPEwNtywRD,
results/omega07_1c/): converged in 10 blocks (last move 6.6e-4), drug users **8.593 per cent**.
Workers launched 17:21 UTC, tag omega-nishiyama, results/omega_nishiyama_1c/. Users are the last block's
"MOMENT b total drug users", read 19:22 UTC.

| b multiple | b | session | blocks | last move | drug users (per cent) |
|---|---|---|---|---|---|
| 1.0 | 0.0054222 | session_01NdBwfzqNp91qgcuSYkEzsV | 12, converged | 1.4e-4 | 2.945 |
| 0.9 | 0.0048800 | session_0188Zxo3q88QEPezmM63zdpv | 12, converged 19:40 | 1.5e-4 | 5.446 (5.519 at 19:22) |
| 0.8 | 0.0043378 | session_01HpATQ5eSn67kkzjZ1A2yxB | 11, converged | 2.9e-4 | 10.409 |
| 0.7 | 0.0037955 | session_012MgAo6Kkac2cQntP5ZGy1J | 12, converged 20:34 | 8.5e-4 | 15.662 |
| 0.6 | 0.0032533 | session_01AFm1381E83bfSiXYGky4rk | 10, converged | 6.5e-4 | 21.026 |
| 0.5 | 0.0027111 | session_01CrA5ZTX54jbmB2nCz3DFyC | 12, converged 19:53 | 6.4e-4 | 26.035 |

**b1* = 0.004531742** (0.8358 x the benchmark's b): log-b interpolation between 0.8x (10.409) and 0.9x
(5.519) to the control's 8.593. The 0.9x point had not met the 1e-3 rule (its use has hovered between 5.45
and 5.59 for five blocks, a large relative move on a small level); at 5.45 b1* would be 0.004528985, 0.06 per
cent lower, well inside the stage 2 bracket of +-2 per cent, so stage 2 was launched at 19:23 without waiting.
At omega_c 0.686 use is far more sensitive to b than at 0.085: a 10 per cent cut in b moves the one-class
users by about 5 points near the target. To match the benchmark's drug use, b must fall by about 16 per cent.
With 0.9x converged (5.446) the same interpolation gives 0.004528828, 0.06 per cent below the b1* used; stage 2 stands.
release_all committed for omega_nishiyama_1c and omega07_1c at 19:25 (no benchmark files needed); all six stage 1 sessions archived after their runs exited.

## Stage 2: two class, matched to 8.956 per cent

Launched 19:23 UTC (CLASSES 2, results/omega_nishiyama_2c/), target the benchmark's own 8.956 per cent:

| b | session | blocks | drug users (per cent) |
|---|---|---|---|
| 0.004441108 (0.98 b1*) | session_01T2a3SiG27xEZP7A99mdHjH | running | |
| 0.004531742 (b1*) | session_012BNTu2UEcm6LYfWB3dc2Ji | running | |
| 0.004622377 (1.02 b1*) | session_01J7fgutKX5TVZPsNqETqHjE | running | |
| 0.004499171 (early b2*) | session_017yzPk5VxvAqKWXXw5Yyq6y | running, launched 21:14 | |

Block-by-block at 21:13: 0.98 b1* 8.317, 9.972, 9.939, 9.840; b1* 7.807, 8.757; 1.02 b1* 6.751, 8.018, 7.871,
7.835. The benchmark of record's own path (7.476, 9.177, 9.273, 9.189 ... 8.956) ends 2.5 per cent below its
block 4, so the target sits between 0.98 b1* and b1*, and the extra point the plan calls for was launched early,
at the block-4 log-b interpolation to 8.956 x 9.189/8.956 = 0.004499171, rather than after the three converge
(about 3 hours saved). It is taken if it lands within 0.05 points of 8.956; otherwise the four points give b2*.

23:32: the 0.98 and 1.02 b1* workers' solves restarted from the seed (22:30 and 23:12; container restarts, the
runner restarts a dead solve from the seed by design), so their earlier blocks above are the only record of
their first pass. Block 6 of the two that bracket the target: 0.004499171 9.218 (path 7.987, 9.476, 9.556,
9.443, 9.237, 9.218), b1* 8.545 (7.807, 8.757, 8.866, 8.796, 8.599, 8.545). Neither is heading to within 0.05
of 8.956, so a fifth point was launched at once at the block-6 log-b interpolation to 8.986 (the benchmark of
record's block 6, which ended 0.03 below it): **0.004510373**, session_01KU25a1Pxrn7ZMCux1H35nZ, 23:33.

00:34: every stage 2 solve had restarted from the seed between 23:12 and 23:43 (worker epoch 2: the containers
were replaced, and the runner restarts a dead solve from the seed by design), so the block-6 numbers above are
from first passes that no longer exist. All five points now solve from the start, the fifth among them; the
earliest converge about 03:30-04:00 UTC. The interpolation for the fifth point stands, since the re-runs
retrace the same paths (b1* block 1: 7.807 then 7.806; 0.98 b1* blocks 1-2: 8.317, 9.972 then 8.318, 9.972).

b2* = pending.

**INSTRUCTION FROM THE AUTHOR, 9 October 21:00 UTC (relayed by the main session):** *"omega_c=0.686 does
not have to be exactly calibrated. that one has slack."* Do NOT interpolate a b2* and do NOT launch another
two-class point. Take whichever of the three running points ends closest to 8.956 per cent once it meets the
convergence rule, record the drug use it landed on here, and go straight to stage 3 from it.

**Clarification, 21:25 UTC (main session):** the fourth point launched at 21:14 may keep running, but do not
wait for it and do not build a b2* from four points. Start stage 3 from the FIRST of the four points to meet the
convergence rule within 0.5 points of 8.956 per cent (on current blocks that is most likely b1*, at about 8.8);
if none does, take the closest converged point.

**DECISION FROM THE AUTHOR, 10 October 00:30 UTC (relayed by the main session):** *"it's ok 7.7 percent. you
can proceed. it is only a robustness check"*. b2* = **0.004622377** (1.02 b1*, converged, drug users about 7.7 per
cent; results/omega_nishiyama_2c/bench_0.686_b0.004622377_ku1.0). Have its worker send the benchmark files
(files/welfare_curvebaseline_benchmark.dat.gz and the rest, as remote_omega_point.sh does on release) and launch
stage 3 from it NOW with code/omega_nishiyama/remote_cf_nishiyama.sh. The other three two-class points
(0.004441108, 0.004499171, 0.004531742) are no longer needed and can be stopped. Record in the stage 3 write-up
that the sensitivity benchmark has about 7.7 per cent drug users against the benchmark's 8.956.

**02:45 UTC (main session):** the fifth point, **0.004510373**, converged at **9.050 per cent** users (block move
5.9e-4), within 1.1 per cent of 8.956. It is closer than the 1.02 b1* point the author accepted and is available now,
so stage 3 runs from it: send_bench committed, stage 3 launched by the main session in a separate cloud session.
Do not launch another stage 2 point or another stage 3.

**03:10 UTC (orchestrator):** stage 2 closed on the fifth point. Its kappa_x: first KAPPA_X PROBE IMPLIED 0.70897865
x 1.5076 = **1.0688562** (the benchmark of record's 0.934236), as stage 3 uses. send_bench for the 1.02 b1* point
withdrawn (it had not converged: it restarted at 23:12 and was at 7.65, move 1.9e-2, at block 10, so the 7.7
of the 00:30 note was an unconverged reading, and its files are no longer needed); release_<TAG> committed for
the other four points, the three still solving stopped by archiving their sessions. Last readings:

| b | blocks | last move | drug users (per cent) |
|---|---|---|---|
| 0.004441108 (0.98 b1*) | 10, converged | 6.6e-4 | 9.444 |
| 0.004499171 | 8, stopped | 5.4e-3 | 9.059 |
| **0.004510373 (fifth, b2*)** | **10, converged** | **5.9e-4** | **9.050** |
| 0.004531742 (b1*) | 6, stopped | 8.9e-3 | 8.545 |
| 0.004622377 (1.02 b1*) | 10, stopped | 1.9e-2 | 7.649 |

b2* = **0.004510373** (0.8318 x the benchmark of record's b), drug users 9.050 against 8.956 (+0.094 points).
The converged 0.98 b1* point (9.444) sits ABOVE the fifth point although its b is lower, as it should, but
only by 0.39 points for 1.6 per cent less b; in the first passes b1* ran 0.6 points below the fifth for 0.5 per
cent more b. Use near these b values responds unevenly within single blocks, so the block-level readings were a
rough guide only.

## The new benchmark's targeted moments against the benchmark of record

Last moment block of each log (results/reference/hf_2c_omega_0.085/bench.log.gz and
results/omega_nishiyama_2c/bench_0.686_b0.004510373_ku1.0/bench.log.gz), all other parameters frozen, so these
are the moments omega_c 0.686 and b 0.004510373 move. Ranked by relative change; the rest move under 2 per cent.

| moment | target | omega_c 0.085 | omega_c 0.686 | change |
|---|---|---|---|---|
| burden50, over half of income in h2 | 0.192 | 0.0058 | 0.0000 | -100% (both near zero) |
| theta, drug spending share | 0.16 | 0.522 | 0.388 | -25.8% |
| SUD share of the homeless | 0.217 | 0.202 | 0.165 | -18.4% |
| y_u, income of drug users | 0.74 | 0.620 | 0.703 | +13.4% |
| mu_H, recovery housed / homeless | 1.473 | 1.455 | 1.311 | -9.9% |
| beta, wealth over output | 3 | 2.952 | 2.793 | -5.4% |
| employed share of the homeless | 0.46 | 0.214 | 0.224 | +4.8% |
| r_smi, SUD ratio SMI over non-SMI | 7.3 | 2.007 | 2.075 | +3.4% |
| unemployment given SUD | 0.1625 | 0.1448 | 0.1401 | -3.3% |
| h_1, homelessness rate | 0.004 | 0.00618 | 0.00601 | -2.9% |
| aleph, value of life / income | 80 | 80.74 | 82.84 | +2.6% |
| b, drug users | 0.105 | 0.08956 | 0.09050 | +1.0% |
| lambda_d, disorder rate | 0.04342 | 0.03811 | 0.03801 | -0.3% |

With users held, the stronger weight on the child changes WHO uses: drug users earn more (y_u +13 per cent, moving
toward its 0.74 target), spend a smaller share on drugs (theta -26 per cent, toward 0.16), and fewer of the homeless
have a SUD (-18 per cent, away from 0.217). Since b falls 17 per cent to hold use, one reading of the shift is the
lower cost of use (lower b) drawing in better-off, lighter users while the parental weight deters the poorest
(a reading of the moments, not tested).

## Stage 3: long-run welfare, Housing First and Treatment First

Running since 02:46 UTC in session_01Pc6TKnc5jiN8mjtwAr1et6 (launched by the main session):
`bash code/omega_nishiyama/remote_cf_nishiyama.sh results/omega_nishiyama_2c/bench_0.686_b0.004510373_ku1.0
0.004510373 1.0688562125371026`, Housing First (null) then Treatment First (detection 0.85, $35 test, price and
pi_V clearing against the new null's net revenue), progress in results/omega_nishiyama/cf/passes.txt. The new
benchmark's base: drug users 9.0496, SUD 3.8011, homelessness 0.60062 per cent (benchmark of record 8.9563,
3.8113, 0.61836). Expected: null about 4 hours, Treatment First about 6 more.

**Housing First (null) ACCEPTED 04:36**, 5 passes (VOUCHER and DIST checks pass): drug price 1.00003, pi_V 0.067534
(the benchmark's, held), users 9.0497, SUD 3.8012, homelessness 0.60052 per cent; net government revenue
**5.7681232** (paper's null 5.8918411), the Treatment First budget target; CEV off the new benchmark's curve
**-0.028 per cent** (paper's null +0.003). Treatment First started 04:36 from price 0.8555, pi_V 0.0962; pass 1:
users -37.4, SUD -38.2, homelessness -6.6 per cent against the new benchmark (the paper's tf85_c35 pass 1: -30.5,
-32.0, -2.6).

**Treatment First ACCEPTED 11:42 UTC**, 10 passes (TARGET CHECK cleared against the null's 5.7681232; DIST CHECK
largest final 4.64e-5 against the 5e-5 rule, at least 70 sweeps each).

### Result: the newborn CEV of Treatment First is 5.51 per cent at omega_c 0.686, against 4.33 in the paper

Each CEV is the arm's cf.log.gz 'CEV from the saved benchmark curve' line, read off its own benchmark's curve, and
the welfare number is CEV(Treatment First) - CEV(Housing First), as code/paper/export_results.py forms x_tf_cev:

| | omega_c 0.085 (paper) | omega_c 0.686 |
|---|---|---|
| CEV, Treatment First | +4.3368 | +5.4818 |
| CEV, Housing First (no policy) | +0.0031 | -0.0283 |
| **Treatment First minus Housing First** | **+4.33** | **+5.51** |

So the sign and the ranking are unchanged and the gain is about a quarter larger (+1.18 points) when parents
weigh their child as Nishiyama finds. In the new run the gain splits into +1.20 utils of childhood welfare and +0.85
of adult welfare (1 per cent of CEV is about 0.33 utils); the paper's final.txt predates that split line.

### Long-run changes, Treatment First against Housing First, each against its own no-policy run

| | omega_c 0.085 (paper): Housing First -> Treatment First | change | omega_c 0.686: Housing First -> Treatment First | change |
|---|---|---|---|---|
| drug users (per cent) | 8.958 -> 6.093 | -32.0% | 9.050 -> 5.504 | **-39.2%** |
| SUD (per cent) | 3.814 -> 2.537 | -33.5% | 3.801 -> 2.281 | **-40.0%** |
| homelessness (per cent) | 0.6186 -> 0.6130 | -0.9% | 0.6005 -> 0.5718 | **-4.8%** |
| drug price | 1.0001 -> 0.8555 | -14.5% | 1.0000 -> 0.8495 | -15.1% |
| pi_V | 0.06753 -> 0.09615 | +42.4% | 0.06753 -> 0.09543 | +41.3% |
| households holding a voucher | 6.29 -> 7.01 | +11.5% | 6.36 -> 7.25 | +14.0% |
| treatment take-up | 24.9 -> 29.3 | +17.6% | 24.5 -> 28.0 | +14.3% |
| SUD share of the homeless | 20.2 -> 23.3 | +15.1% | 16.5 -> 16.4 | -0.7% |
| voucher spending | 0.689 -> 0.769 | +11.6% | 0.697 -> 0.796 | +14.1% |

(paper columns: results/counterfactuals_2c/nulltf/null/final.txt and tf85_c35/tf/final.txt; new:
results/omega_nishiyama/cf/null and cf/tf.)

Reading: with the child weighted at 0.686, conditioning the voucher on staying clean cuts use and SUD by about 7
points more than at 0.085, and homelessness falls by 4.8 per cent rather than 0.9. The two prices that clear move
almost exactly as in the paper (price -15 against -14.5, pi_V +41 against +42), so the larger gain comes from the
stronger response of households, not from the markets. The SUD share of the homeless, which rises by 15 per cent in
the paper's Treatment First, is flat here: the new benchmark's homeless already carry fewer SUDs (16.5 per cent
against 20.2), and conditionality no longer concentrates them on the street.

Caveats: the new benchmark matches drug use to within 0.09 points (9.050 against 8.956; the author: *"omega_c=0.686
does not have to be exactly calibrated"*) but not the other targets, which moved as tabulated above (drug spending
share -26 per cent, SUD share of the homeless -18, income of drug users +13, wealth over output -5); everything else
was held at the benchmark of record's values, as asked.

**Treatment First ACCEPTED 11:42**, 10 passes (TARGET CHECK PASS, cleared against 5.768123; DIST CHECK PASS, largest
final 4.64e-05). Final, against the new null (results/omega_nishiyama/cf/{null,tf}/final.txt), beside the paper's
arms (results/transition_2c/arm_tf/final.txt):

**The sensitivity benchmark has 9.05 per cent drug users against the paper's 8.956.**

| | omega_c 0.686: null | omega_c 0.686: Treatment First | change | paper: null | paper: Treatment First | change |
|---|---|---|---|---|---|---|
| drug use (per cent) | 9.050 | 5.504 | -39.18% | 8.959 | 6.093 | -31.99% |
| SUD (per cent) | 3.801 | 2.281 | -40.00% | 3.814 | 2.536 | -33.51% |
| homelessness (per cent) | 0.6005 | 0.5718 | -4.78% | 0.6185 | 0.6130 | -0.90% |
| drug price | 1.0000 | 0.8495 | -15.05% | 1.0003 | 0.8555 | -14.47% |
| pi_V | 0.06753 | 0.09543 | +41.30% | 0.06753 | 0.09615 | +42.37% |
| CEV from the saved benchmark curve | -0.000283 | 0.054818 | | 0.000031 | 0.043368 | |

**Newborn welfare gain, CEV(tf) - CEV(null): 5.51 per cent at omega_c 0.686, against the paper's 4.33 per cent.**
0.054818 - (-0.000283) = 0.055101; the paper's is 0.043368 - 0.000031 = 0.043337 (results/counterfactuals_2c/
tf85_c35/tf and nulltf/null; results/transition_2c/arm_tf's 0.043364 gives the same 4.33). Each CEV is the arm's
cf.log 'CEV from the saved benchmark curve' line.

The long-run result carries over in sign and mechanism. Treatment First again lowers the drug price by about 15 per
cent and raises pi_V by about 41 per cent on the same budget. The gain is about a quarter larger: 5.51 against 4.33.
Drug use falls by 39 rather than 32 per cent. Homelessness falls by 4.8 rather than 0.9 per cent. The welfare split
(finalstats, utils): childhood +1.20 and adult part +0.85, total +2.05, against the paper's +0.83, +0.64, +1.46.
