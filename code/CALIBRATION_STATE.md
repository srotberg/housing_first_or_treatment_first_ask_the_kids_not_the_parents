# 25 September 21:10: the 19 September null stopped after pass 1 -- its benchmark's big files are gone

code/null19 ran pass 1 and then died reading value_function1baseline_benchmark.dat:
code/arm1 kept only the small benchmark files and no copy of the large ones exists
on this machine. Pass 1 against its target 6.0213: net revenue 6.0868 (+0.0655),
revenue 14.322, ss 8.648, vouchers_2 0.696, income 63.33; b 0.082059, lambda 0.033087,
h 0.0063302. Today's null at the same stage: 6.0920 against 6.0389 (+0.0531), which
settled at +0.2259. So the 19 September model shows the same gap at pass 1, slightly
larger. Not proven to convergence; finishing it means re-solving the 19 September
benchmark (hours). Log in the scratchpad (cf_null19_pass1.log.gz).

# 25 September 21:00: the 85 per cent detection run is going

The author: "ok, run the 85% detection one"; "i think the 85% is more reasonable";
tests are by surprise, so nobody can abstain ahead of one. code/cfarm_tf_pdet85:
rationed TF, probability_of_detection 0.85, like-for-like target (log: 6.26479885996),
price start 0.87. To make room cfarm_tf_old_like (19 Sep design, corrected budget)
was stopped by pid at pass 1 (its pass-1 log in the scratchpad) and removed; rerun
later if the attribution is still wanted. Running now: null19, cfarm_tf_pdet85.

# 25 September 20:45: memory, and the detection-rate test queued

cfarm_tf_old_saved was killed by the kernel (out of memory: three 4.9 GB solves on
16 GB); removed, not rerun (the TF pair already measures the target's effect).
QUEUED: the author asks whether 15 per cent false negatives would deter more.
Rationed TF with probability_of_detection 0.85, like-for-like target, price 0.87,
via scratchpad design2_cf_arm.sh (PDET), DIAG_TAG _pdet85, as soon as null19 frees
its memory. Running: cfarm_tf_old_like, null19.

# 25 September 20:40: NULL ARM ON THE 19 SEPTEMBER MODEL (did arm 3 have the surplus too?)

The author: "start it now". code/null19: the 19 September counterfactual binary
(code/arm1/hftf, built 19-Sep 13:14, the arms' shared binary) against the 19 September
benchmark files in code/arm1 (saved target 6.021272176537, the value arm 3 cleared
against). Handover rebuilt from arm 3's 101 echoed HANDOVER lines with the policy off:
test 0, exclusion 0, adjust_taxes 0, applicant switch back to 1, price start 1.0,
omega_c 0.055, pi_V 0.068274, adjuster 0.1 (102 lines, all echoed back). If its net
revenue settles well above 6.0213, arm 3's 3.25% carried the same surplus.
The author also asked that pi_V balance the budget: it does (tax_system_type 3 in the
TF logs; the labour tax rate stays at the benchmark's 0.8935).

# 25 September 20:30: the author doubts the TF CEV (about 0, against 3.25% in arm 3)

Welfare split (childhood + beta^25*adult), against the null arm, 1% CEV ~ 0.33 utils:
TF fixed, like-for-like target: childhood -0.01, adult +0.02 (CEV 0.15%, null 0.14%);
TF fixed, SAVED target: childhood +0.89, adult +0.63 (CEV 4.76%); 19 Sep settings on
today's model, unfixed, saved target: childhood +0.78, adult +0.09 (CEV 2.75%).
The CEV code passes the null and the curve is shifted to w(0) = benchmark welfare
(bench log: shift -0.0917 utils). With sigma = 2 the voucher money (to the poorest)
carries most of the welfare. IN FLIGHT, to attribute the old 3%:
- code/cfarm_tf_old_like: INC 0 (the 19 Sep design), fixed code, target 6.26479886
- code/cfarm_tf_old_saved: INC 0, fixed code, saved target 6.03887563
(scratchpad design_cf_arm.sh = remote_cf_arm.sh with DIAG_TAG and INC; price 0.85).
code/cfarm_tf removed for disk; its log, handover and target are in results/.

# 25 September 19:50: RATIONED TF CONVERGED against the like-for-like budget

results/counterfactuals_cf_local/tf/RESULT.md (the saved-target run kept beside it as
RESULT_saved_target.md). TARGET CHECK PASS at 6.26479885996; exit after pass 10.
Against the benchmark (against the null arm): b -27.7% (-27.4%), lambda_d -28.2%
(-27.9%), h_1 +8.9% (+9.5%), SMI -0.3%, SMI share of homeless -6.0%, drug quantity
-17.5%, price 0.88117 (-11.9%), pi_V 0.07154 (+5.9%), eligibles getting a voucher
-5.3% (-4.7%), voucher spending -6.0% (-4.5%). CEV +0.151% against the null's
+0.140%: about zero. Budget gap 0.021 at exit, pi_V still easing down.

# 25 September 18:40: rationed TF RERUN against the like-for-like budget target

The author: "Go ahead with the rerun... You need to rerun the rationed tf with the
correct budget and budget clearing". code/cfarm_tf, remote_cf_arm.sh tf with
NET_TARGET 6.2647988599575077 (the null arm's converged net revenue) and price start
0.86; binary cf/ from a102cfaa. The log confirms net_govt_revenue_constraint
6.2647988599580; cfarm_bench's file still reads 6.038875634967.
- The target file is govt_revenues_to_use_in_tests, not net_govt_revenues:
  clear_only_vouchers_govt_budget is a compile-time 0. The first launch wrote the
  wrong file, cleared against 6.0389 and was stopped by pid at startup.
- Report TF's CEV next to the null arm's own CEV against the saved curve: +0.14%.

# 25 September 18:20: the null arm converged (exit after pass 4, VOUCHER CHECK PASS)

b 0.080903 (-0.4%), lambda_d 0.034513 (-0.3%), h_1 0.0060470 (-0.5%), price 1.00014,
total income 63.236 (+0.44%), revenue 14.2783 (labour 13.5104, investment 0.7679),
ss 8.4384. NET REVENUE 6.2647988599575077 against the saved target 6.038875634967:
+0.2259. That is the proposed arm-local TF budget target. Log in the scratchpad
(cf_null_revsplit.log.gz). Waiting on the author.

# 25 September 18:10: TF's voucher expansion is a BUDGET-TARGET ARTEFACT

The author doubted pi_V +54 per cent ("But not that much"). A NULL ARM settles it:
the counterfactual binary with NO policy change (code/cfarm_null_revsplit: omega_c
0.06, test 0, exclusion 0, adjust_taxes 0, price clearing from 1.0), built with one
extra print, the revenue split (scratchpad build_cf_revsplit.sh; source untouched).
Pass 3 against the saved benchmark:
  b 0.080884 (-0.5%), lambda_d 0.034528 (-0.2%), h_1 0.0060467 (-0.5%)  -- moments reproduce
  total income 63.246 vs 62.956 (+0.46%); revenue 14.2817 vs 14.0405
  (labour 13.514, investment 0.768, consumption 0, property 0); ss 8.4385 vs 8.4078
  NET REVENUE 6.2685 vs the target 6.0389 read from net_govt_revenuesbaseline_benchmark.dat
So the budget rule sees +0.23 of "surplus" with no policy at all -- a third of
voucher spending -- and TF's pi_V clearing hands it to vouchers. Against the null,
TF's net revenue BEFORE vouchers is about 0.065 LOWER (warm-started TF, pass 4:
net 6.0588 with vouchers 0.8182, i.e. 6.877 before vouchers, vs the null's 6.942):
more retirees (ss +0.06), smaller bequest residual (-0.04), revenue +0.036. Budget-
neutral TF would cut voucher spending about 9 per cent, not raise it 20.
Unaffected: omega1 and internalise (adjust_taxes 0). Their moments are measured
against the saved benchmark, which the null reproduces within 0.5 per cent.
Root cause of the +0.46 per cent income gap: NOT FOUND. The warm-started TF
diagnostic was stopped by pid after pass 4 (its log in the scratchpad).
Proposed: rerun TF with the target set, arm-locally, to the null's converged net
revenue (the arm directory's copy of net_govt_revenuesbaseline_benchmark.dat, not
cfarm_bench's). Waiting on the author.

# 25 September 17:15: RATIONED TF CONVERGED on the fixed model

results/counterfactuals_cf_local/tf (RESULT.md, cf.log.gz, the 100-line arm
handover). Exit after pass 9 by the run's own rule. Against the benchmark: b -32.8%,
lambda_d -32.8%, h_1 -6.4%, SMI prevalence -0.4%, SMI share of homeless -12.7%,
drug quantity -20.0%, price 0.86208 (-13.8%), pi_V 0.10381 (+53.7%), eligibles
getting a voucher +20.3%, CEV +4.76%. Caveat: budget gap 1.06e-02 at exit, pi_V
still drifting down. The 24 September TF result is marked superseded.

# 25 September 16:45: the voucher fixes are a NO-OP for the benchmark, within run-to-run noise

cfarm_det_bench ran cfarm_bench's OWN binary (built 01:42) from the same seed
and handover. Block 1:
  b        7.1887043830630423E-002  (reference 7.1894758675946219E-002, -0.011%)
  lambda_d 3.1450566266557796E-002  (reference 3.1458335936491132E-002, -0.025%)
  h_1      7.0776658289252760E-003  (reference 7.0781358129644208E-003, -0.007%)
So a run is NOT bitwise reproducible at 2 OpenMP threads: the same binary moves
b by 1e-4 relative between runs. The fixed build's gap (-0.005%) is inside that,
so a102cfaa is a no-op for the benchmark and cfarm_bench's baseline files stand.
STANDING CONSEQUENCE for no-op checks: compare against a SECOND run of the old
binary, not against its saved log, or the noise reads as a change.
Both check directories stopped by pid; their files are not used.
TF pass 4 at 0.8723: b 0.05600 (-31.1%), lambda 0.02449 (-29.2%), h 0.006024 (-0.9%).

# 25 September 16:35: grandfathering is not needed

The author, on the latent voucher_gf leak: "It is ok with the grandfathering. We
don't need to run it". Leave grandfather_voucher_states at 0 and the gf leak
unfixed; revisit only if the author asks for a grandfathered run.

# 25 September 16:30: no-op check NOT bitwise; determinism test running

cfarm_noop_bench block 1 (fixed build a102cfaa, same seed, same 97-line handover
with exclusion 0, test 0, inc 1) against cfarm_bench block 1 (binary built 01:42,
no source commit in between but this one):
  b        7.1890971726074712E-002  vs 7.1894758675946219E-002  (-0.005%)
  lambda_d 3.1454560537358053E-002  vs 3.1458335936491132E-002  (-0.012%)
  h_1      7.0780456256119388E-003  vs 7.0781358129644208E-003  (-0.001%)
  y        1.1459324862351796       vs 1.145927...
Every changed line is gated on vcc 1 or exclusion 1, so the gap is either run
to run noise (2 OpenMP threads) or -O3 code generation. Test: code/cfarm_det_bench
runs cfarm_bench's OWN binary from the same start; if it reproduces the reference
exactly, runs are deterministic and the gap is the build. noop run stopped by pid
after block 1.
TF (code/cfarm_tf) pass 1 at 0.860: b 0.06551 (-19.4%), lambda 0.02696 (-22.1%),
h 0.006806 (+12.0%); price moved to 0.8643.

# 25 September 16:05: the voucher fixes are in the source (a102cfaa); rationed TF relaunched

The author, 25 September: "Go ahead with the fix, keep the exclusion running".
Three fixes, each gated on the test or the exclusion switch:
- (a) calculate_future_voucher_index_and_opportunity: an excluded household no
  branch catches (above the income gate, or buying) now gets the range
  [0, voucher_excl], so the stay row is summed and the exclusion keeps running.
- (b) same routine, holder branch: with the test on and exclusion off the range
  starts at 0, where the test sends a caught holder.
- (c) calculate_housing_voucher_2: the branch that zeroed every user's and SUD
  holder's voucher under the test is gone; the test acts only through the
  transition, so a holder the test misses is paid.
Three builds 7 warnings / 0 errors each; benchmark -O3 7 / 0. Binaries in cf/
and bench/ are from a102cfaa.

IN FLIGHT (both harness background tasks, 2 threads each):
- code/cfarm_tf: remote_cf_arm.sh tf, DRUG_PRICE_START 0.86 (the leak-fixed,
  payment-unfixed diagnostic was clearing near 0.854 at pass 13: b 0.05315,
  lambda 0.02302, h 0.005870, pi_V 0.0968). Handover checked in the log:
  vcc 1, inc 1, p_det 0.70, p_fp 0, exclusion 1, adjust_taxes 1, omega_c 0.06,
  pi_V 0.067534, adjuster 0.1.
- code/cfarm_noop_bench: NO-OP CHECK. The fixed benchmark binary from scan_seed
  with cfarm_bench's own 97-line handover must reproduce cfarm_bench block 1:
  b 7.1894758675946219E-002, lambda_d 3.1458335936491132E-002,
  h_1 7.0781358129644208E-003. Kill it (by pid) once block 1's BLOCK MOVE line
  prints; its baseline files stay in that directory and are not used.

LATENT, NOT FIXED: with grandfather_voucher_states = 1 (a compile-time 0 today)
voucher_gf has the same leak -- rows (gf,gf)=1 only, but the range is [0,0]
above the gate or buying and [0,2] for has_house = 1. Must be settled before
any grandfathered transition runs; the author said on 20 September a
grandfathered household leaves the state when its income rises past the gate.
Also latent: the holder range's inc==0 case is gated on is_counterfactual while
its row is not, so a BENCHMARK with inc 0 would leak (every benchmark has inc 1).

# 25 September 14:35: the 19 September TF settings on the current model, FINISHED (record only, leak in)

code/cfarm_tf_diagold19 (inc 0, exclusion on, p_det 0.70, unfixed build, so the
excluded-state leak bites every excluded HOLDER) exited 0 after 10 passes.
Against the benchmark (b 0.08126, lambda 0.03461, h 0.006079, price 1.0, pi_V 0.06753):
b 0.04558 (-43.9%), lambda 0.01861 (-46.2%), h 0.006239 (+2.6%), price 0.8239
(-17.6%), pi_V 0.07143 (+5.8%), CEV 2.75%. Drug market cleared: demand 0.3769
against supply 0.5013*0.8239^1.46 = 0.3779; budget distance 0.0175.
Close to the old run's recollected size (price -13, drug use -35, h +5), so the
recalibration is not what moved TF. NOT A RESULT: the leak inflates it by an
unknown amount. Log kept outside the repo (scratchpad cf_tf_diagold19_final.log.gz).

# 25 September 14:20: CONFIRMED -- the excluded-state leak is what made TF -99 per cent

The new design (inc 1, exclusion on, p_det 0.70, unfixed payment) on the
range-fixed build (code/cfarm_tf_rangefix, price start 0.80), against the
benchmark b 0.08126, h 0.006079, V 0.5013 at price 1.0:

| pass | price | b | vs bench | h_1 | vs bench | V (demand) | pi_V next |
|---|---|---|---|---|---|---|---|
| 1 | 0.800 | 0.08200 | +0.9% | 0.007088 | +16.6% | 0.6870 | 0.0748 |
| 2 | 0.804 | 0.07495 | -7.8% | 0.006850 | +12.7% | 0.6237 | 0.0885 |

The same design on the unfixed build: pass 1 b 0.00057 (-99 per cent) at 0.86.
So the leak, not the model, drove the collapse. The fixed run is nowhere near a
cleared market: supply at 0.808 is 0.5013*0.808^1.46 = 0.367 against demand
0.624, so the price walks up at the 0.5 per cent cap and b will fall as it does.
Its equilibrium is not known yet; it is a diagnostic (payment rule still unfixed).

The leak is OLD: the exclusion state and its range date from 9-10 September,
so the 19 and 24 September TF runs had it too, but with inc 0 only holders could
be excluded. The old design on the current model (code/cfarm_tf_diagold19, same
unfixed binary) sits at b 0.0433 (-47 per cent), price 0.831, h +3 per cent, so its
size is also inflated by the leak to an unknown degree.

Proposed (author's call, and only once no solve is running): fix in the source
(a) the excluded-state range, (b) the holder range with exclusion off,
(c) the payment rule so a holder who passes is paid; three builds; rerun TF.
Open design choice for (a): an excluded household above the income gate either
keeps its exclusion clock running (range [0,2], what the diagnostic does) or is
released on leaving eligibility (row 1 to state 0).

# 25 September 13:55: SUSPECTED CAUSE -- a probability leak for the excluded state

calculate_future_voucher_index_and_opportunity (32273-32400) gives an EXCLUDED
household with has_opportunity = 0 (income above 0.5 * median, or buying) the
next-state range [0,0]. But voucher_probabilities writes the exclusion rows for
BOTH opportunity slices: (excl,0) = 1/3 and (excl,excl) = 2/3 (36757-36759, and
the comment there says so deliberately). The 2/3 fall outside the range, so in
the VALUE FUNCTION such a household keeps a third of its continuation value.
Exclusion is then close to catastrophic for anyone whose income might rise.
The simulation loses no mass: every run's sum of the distribution is about 51,
the same as omega1, which has no exclusion. So only decisions are distorted.
- It fits the asymmetry. With inc 0 only holders (about 7 per cent) can be
  excluded; with inc 1 every failing lottery winner can be.
- The exclusion-off diagnostic (b 0.00001) hit a SECOND leak: a holder's range
  is [1,2], so with exclusion OFF a failing holder's 0.7 to state 0 is dropped.
  That leak cannot bite with exclusion on.
- omega1, internalise and the HF benchmark have exclusion off, so they are unaffected.
- Test: code/build_cf_rangefix.sh (ignored build copy) adds, before the routine's
  end, "if has_opportunity==0 and exclusion on and voucher_index==voucher_excl:
  range [0, voucher_excl]". The new design (inc 1, unfixed payment) runs on it in
  code/cfarm_tf_rangefix at price 0.80. Compare with the unfixed new design's
  pass 1 (-99 per cent) and the old design (-40 per cent).

# 25 September 13:40: the TF size traced to the applicant switch, not the model

Pass-1 first answers, all against the same local benchmark (b 0.0813):
- 19 September design (inc 0) on the CURRENT model, unfixed, p 0.83: b 0.0487
  (-40%), lambda_d -43%, h_1 +4%. This reproduces the old arm 3 (-44.6%, h +1.3%)
  and the author's memory, so the recalibration since 21 September is NOT it.
  (Handover diff against PARAM_HANDOVER_arm3_converged.txt: the homeless-state
  parameters are identical; only modest recalibrations moved.)
- New design (inc 1), unfixed, p 0.86: b 0.00057 (-99%).
- New design (inc 1), payment fixed, p 0.85: b 0.00146 (-98%). So the payment
  rule is not what separates the two designs.
- Probe B (inc 1, p_det 0, unfixed, p 1): b 0.0298 (-63%). Payment zeroing alone.
- Code: inc changes only the row for a FAILING NON-HOLDER. With inc 0 it is never
  offered, tested or excluded. With inc 1 it wins with probability pi, then
  30% get the voucher and 70% are excluded. On paper that is MORE generous except
  for the exclusion, so the size is not explained yet.
- The comment at 32366 records an earlier bug in which a voucher carried no
  continuation value: drug use fell 0.0849 to 0.0253. In this model drug use
  leans heavily on the voucher as a safety net.
- Running: code/cfarm_tf_diagnoexcl (inc 1, exclusion OFF, unfixed, p 0.86)
  isolates the applicant exclusion. code/cfarm_tf_diagold19 continues to converge.

# 25 September 13:12: two TF diagnostics running locally (the author: "do both")

- The payment zeroing is NOT new. git blame puts line 18194 at 304e9ed4
  (30 August), so the 19 September arm 3 had it too. It cannot explain why TF is
  larger now than then.
- Probe B (unfixed, p_det 0, price 1, pass 1): b 0.0298, -63 per cent. The
  payment zeroing ALONE removes two thirds of drug use in the current model.
- (1) code/cfarm_tf_payfix: the payment fixed (build copy), the author's TF
  settings (inc 1), price start 0.85.
- (2) code/cfarm_tf_diagold19: the 19 September design (inc 0, p_det 0.70, p_fp 0,
  exclusion, vcc 1) on the CURRENT model with the unfixed binary, price start
  0.83. If still huge, the model changes since 19 September are the cause; if
  near -35 to -45 per cent, the test-and-exclude applicant design (inc 1) is.

# 25 September 13:05: TF PAYMENT BUG, diagnostic run on a build copy

The author's rule: test only holders and those about to get a voucher; a fail
revokes it (holder) or withholds it (new winner), then about 3 years of exclusion;
false negatives 30 per cent; SUD fails the test even without use this period
("those who have sud can't change anything and the test reveals if they have sud").
The transitions (voucher_probabilities, compute_voucher_index_1) match this.
THE PAYMENT DOES NOT: calculate_housing_voucher_2 (18191-18194) zeroes a holder's
voucher every period the holder uses drugs or has SUD, even when the test missed
them. That contradicts equation 32's own comment ("a household that is not
caught gets the whole voucher") and the author's 30 per cent false negatives.
- code/build_cf_payfix.sh (ignored) builds the cf binary with line 18194's
  condition set to ==-1 (asserted by content) into code/cf_payfix. The tracked
  source is NOT edited, because solves were running.
- TF on that binary: code/cfarm_tf_payfix, drug_price_start 0.85 (the earlier
  TF price was about -13 to -17 per cent).
- The unfixed TF (price about 0.38, b -85 per cent) was stopped. Its logs are in
  the scratchpad only.
- Probe B (unfixed, p_det 0, price 1) in code/cfarm_tf_diagB isolates the zeroing
  channel.
If the fix brings TF back near the 19 September size, fix the source (with all
three builds) once no solve is running, with the author's OK.

# 25 September 13:00: the author accepts omega1 and internalisation; tf payment rule queried

The author: *"Omegac=1 and internalizarion seem correct to me. Similar to before"*
(results/counterfactuals_cf_local/{omega1,internalise}).

On tf the author doubts b -85 per cent. The fall is policy-driven: at p = 0.86 it
was -99 per cent, and the price then fell to about 0.38 to clear the market.
Found and put to the author, awaiting a decision:
calculate_housing_voucher_2 (18191) zeroes a holder's PAYMENT every period the
holder uses drugs or has SUD, deterministically. p_det = 0.70 governs only
revocation and exclusion, so the 30 per cent false negatives never reach the
payment. Options offered: (a) decompose who stops using, (b) pay a using holder
with probability 1 - p_det, (c) keep the rule and write it up with the caveat.
Local tf runs continue meanwhile (cfarm_tf from 0.35, cfarm_tf_probe from 0.42,
both near 0.375). v3 archived: its tf is redundant with the local runs.

# 25 September 10:35: tf settled demand is price-inelastic; main run restarted at 0.35

Settled (post-transient) demand, with the budget cleared (pi_V about 0.10):
0.0600 at p = 0.4448 and 0.0626 at 0.4359 (0.47-start run); 0.0733 at 0.4196 and
0.0743 at 0.4175 (0.42-start run); b about 0.008 to 0.009. The implied elasticity
is 2 to 4, so against supply 0.5014*p^1.46 it clears at p = 0.354 to 0.372. First
passes overstate demand, so the price climbs a few per cent before it settles. The
main run now starts at 0.35 (code/cfarm_tf); the 0.42-start run (code/cfarm_tf_probe,
now at 0.415) walks down from above as the check.

# 25 September 07:55: tf clearing price bracketed by probes, local runs at 0.47 and 0.52

These are pass-1 demands from the local benchmark at adjuster 0.1, with the voucher
probability carried:
- p = 0.86: V = 0.0018, b = 0.00057, lambda_d = 0.00019 (supply about 0.40);
  passes 2 to 4 kept b under 0.0006.
- p = 0.40: V = 0.917, b = 0.0487 (supply 0.13).
The log-linear demand has elasticity 8.1 and clears near p = 0.49. First-pass demand
overstated the settled demand in omega1, so the main run starts at 0.47
(code/cfarm_tf) and a probe at 0.52 (code/cfarm_tf_probe, via the ignored copy
code/probe_cf_arm.sh). A run started at 0.6 (v3) or 0.86 walks 20 to 60 passes at
the 0.5 per cent cap, which is why v3 has taken over 6 hours.

# 25 September 06:55: internalise and omega1 DONE (adjuster 0.1, one local benchmark); tf pending

- results/counterfactuals_cf_local/internalise: lambda_d -2.14%, h_1 -2.47% (firm);
  b -1.64% final, -1.94% averaged over the last five passes (range -2.4 to -1.6);
  price 0.9966.
- results/counterfactuals_cf_local/omega1: b -35.0%, lambda_d -33.0%, h_1 -12.3%,
  price 0.870. b steps each time the price rises 1.5 to 2 per cent; the price
  stopped with the gap inside its rule.
- tf: v3 (session_012k9WecRrXzogSi5ZtEuDRN) has been running since about 01:25.
  When it pushes results/counterfactuals_cf_v3/tf, ARCHIVE v3 (its queued omega1
  duplicates the local one).

# 25 September 04:50: omega1 restarted at drug_price_start 0.81

The omega1 arm started at 0.6. Pass 1 printed demand V = 1.91 (b = 0.157)
against supply 0.5014*0.6^1.46 = 0.238, so the price rose at the 0.5 per cent
cap, which is about 60 passes (10 hours) to anywhere near 0.8. The fixed-price
omega1 run had b = 0.0202 at p = 1, so demand there is about 0.12. The log-linear
demand through the two points has elasticity 5.4. Against supply elasticity 1.46
it clears at p^6.88 = 0.12/0.5014, so p = 0.81. Killed (pid 3063) and relaunched
with DRUG_PRICE_START=0.81 (task b14c0bziq). The same arithmetic puts TF near
0.79 (fixed-price b = 0.0154), about 54 passes from its 0.6 start.

# IN FLIGHT, 25 September 04:25: both remaining local arms from ONE local benchmark

- Local benchmark (code/cfarm_bench) done 04:15: b = 0.081255009769345327,
  -6.9e-5 against the reference; voucher probability 0.067533863251354.
  bench_files.tar.gz is 131 MB, over GitHub's 100 MB limit, which is why v2
  never pushed it. Deleted; the set lives in code/cfarm_bench only.
- Local internalise at adjuster 0.1 (task b3hj81odq), stage 2 since 04:15.
- Local omega1 at adjuster 0.1 (task b08fa7bn8), from the same benchmark, since
  04:24. Deleted code/trans_bench_to_tf (4.5 GB, the 21 September arm 3
  transition on the superseded model, results in results/transition/) to make
  disk room: one arm directory is 2.5 GB.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): tf at 0.1 since about 01:25. Archive
  it once tf is pushed; its omega1 duplicates the local one.

# IN FLIGHT, 25 September 01:35

- internalise v2 (results/counterfactuals_cf_v2/internalise/): the voucher
  check PASSED and stage-1 b is -1.8e-5 against the reference. At adjuster 0.2
  b sawtooths +/-0.65 per cent with the price (0.9949 to 0.9967), so its b
  change of -1.67 per cent is +/-0.6 pp. lambda_d -2.19 per cent and h_1 -2.50
  per cent are steady. bench_files.tar.gz was NOT pushed. v2 archived.
- THIS container: `remote_cf_arm.sh internalise` at adjuster 0.1. The 01:32
  launch used nohup and DIED when the turn ended (the container is suspended
  between firings); relaunched 01:43 as a harness background task (Bash
  run_in_background), which survives. Stage 1 started 01:43 in code/cfarm_bench (out: code/cfarm_internalise.out). The
  container restarted once (01:21), so check `uptime -s` each firing and
  relaunch the same line if it is newer than the launch. Push
  cfarm_bench/bench_files.tar.gz when stage 1 finishes.
- v3 (session_012k9WecRrXzogSi5ZtEuDRN): stage 1 passed; tf at 0.1 running
  since about 01:25, omega1 after it.

# PLAN, 24 September 22:25: ONE benchmark (v2's), every remaining arm run from it

The author: *"Wouldn't it be more efficient to run it once in this session and
use it for the other sessions??"* Yes. v2's benchmark finishes first. Its worker
pushes results/counterfactuals_cf_v2/bench/{bench_files.tar.gz,bench.log.gz}.
When those land, run tf and omega1 from them in THIS container:
`cd code && BENCH_FROM=../results/counterfactuals_cf_v2/bench sh remote_cf_arm.sh <arm>`
(4 cores, 16 GB; two arms at OMP 2 each; check the first arm's RSS before
starting the second). Then archive v3 (session_012k9WecRrXzogSi5ZtEuDRN), whose
own benchmark is a hedge only in case v2's tarball is over 40 MB and not pushed.

# IN FLIGHT, 24 September 22:10: v3 for tf and omega1; v2 is kept for internalise only

- session_012k9WecRrXzogSi5ZtEuDRN (v3) runs the benchmark, then tf, then omega1,
  at drug_market_adjuster 0.1, to results/counterfactuals_cf_v3/<arm>/.
- session_011HE2FoD9oEfGDmCFwFg9gx (v2) runs at the declared adjuster 0.2.
  Its internalise arm is fine, because the price barely moves there (0.991).
  ARCHIVE v2 AS SOON AS results/counterfactuals_cf_v2/internalise/ IS PUSHED,
  before its omega1 and tf run at 0.2.
- The first tf run (session_01LxhTRbB5QNDAeLqvVag69e) runs at 0.2 and started
  its price at 0.6. When it pushes, read its price path. It gives the tf
  clearing price and shows whether the run cycled; do not report its numbers
  unless the movement decayed into the stop.

# IN FLIGHT, 24 September 20:40: counterfactuals v2, one benchmark and three arms

- session_011HE2FoD9oEfGDmCFwFg9gx runs remote_cf_arm.sh: the HF omega_c = 0.06
  benchmark once (cfarm_bench), then internalise, omega1 and tf, each carrying
  the benchmark's voucher probability 0.067533863251354. Results go to
  results/counterfactuals_cf_v2/<arm>/. Expected: internalise about 01:00 UTC,
  the other two a few hours after.
- The first internalise arm (results/counterfactuals_cf/internalise/) ran at the
  declared 0.06 and is superseded. The first omega1 arm had the same fault and
  was archived before it finished.
- The first tf arm (session_01LxhTRbB5QNDAeLqvVag69e) is still running. pi_V is
  its budget instrument, so the start value washes out at convergence. Check its
  stage-1 b: its benchmark stage ended after about 50 minutes, where the others
  took 2.5 to 4 hours.

# THE REDO RUNS THE WAY THE OLD ARMS DID, 24 September 16:55

The author: *"the budget clearing in rationed TF is done with pi_v and in the
omega_c=1 case and internlization case for homelessness there is no budget
clear"*, and chose the old counterfactual build over patching the frozen one.

The market-clearing pilot on the frozen build was archived: that setup zeroes
voucher_probability_adjuster, so pi_V could not clear the budget.

`code/remote_cf_arm.sh tf|omega1|internalise`, one container per arm:

    STAGE 1  Housing First omega_c = 0.06 benchmark on the TRACKED source,
             12 blocks into save_welfare_curve, in the arm's own directory.
             Its full saved files were lost with the reference container, and
             the counterfactual binary reads them.
    STAGE 2  the arm on build_cf.sh's binary (is_counterfactual=1,
             use_revenues_to_increase_voucher_probability=1), in the same
             directory.

Checked in the source before writing it:
- the drug price clears in clear_drug_market's counterfactual branch against the
  benchmark's own shifter, drug_supply_shifterbaseline_benchmark.dat;
- adjust_taxes 1 plus use_revenues=1 sets tax_system_type 3 (53091), so pi_V
  moves with gain 0.05 and the tax does not. adjust_taxes 0 gives no budget
  clearing. That is tf, and omega1/internalise, respectively;
- upload_vars imports the median income, the labour income profile, the net
  revenue constraint and the rest from the benchmark's saved files. So the
  STALE CONSTANT declarations are overwritten before use, and no Fortran edit
  is needed; I told the author otherwise and corrected it;
- inc = 1 (applicants tested) takes the file-name branch 'counter_arm', and
  old_results is still 'baseline_benchmark', so every arm reads the right files.

A relaunch skips stage 1 when BENCH_DONE and the benchmark files are on disk.

