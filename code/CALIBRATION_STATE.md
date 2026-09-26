# 26 September 10:35: THE FIX WORKS -- the no-policy run reproduces the benchmark

code/cfarm_null_fix (build cf_fix: tax warm starts neutralised, moments rule 1e-4): pass 3 net revenue
6.03766 against the benchmark's 6.03888, CEV +0.05 per cent (the old build: 6.1753, -0.26). The hidden
labour-tax rise was the whole gap. TF 85 relaunched on cf_fix (code/cfarm_tf_fix85): target 6.03766
(pass 3; checked against the no-policy run's final value when it ends), seeded from TF 85's converged
distribution, pi_V 0.0818, price 0.8666; its log confirms tax adjustment 0 and detection 0.85.
Freed: code/cfarm_bench_tdm (its file set, final calibration state and distribution are kept in the
scratchpad) and code/cfarm_bench_revdiag.

# 26 September 10:00: FOUND -- a hidden labour-tax rise in every counterfactual (ENGINE.md, same time)

The no-policy gap (revenue +0.148, welfare -0.26%) is the hard-coded tax warm start
increase_in_labour_income_tax = -2.599e-3 (lambda 0.8935 -> 0.8909), which no arm ever solves.
Every counterfactual so far carried it: omega_c = 1, internalisation, every TF run, the 19
September arms. TF measured against its own no-policy run is like-for-like in the tax (+1.39 net
for TF 85 on cf_tdm); levels and anything read against the benchmark directly are off.
Build code/cf_fix (+ _permban): cf_tdm with the three warm starts neutralised (the benchmark's
uploaded 0 stands) and the counterfactual moments rule 5e-4 -> 1e-4. Three builds each, 7
warnings / 0 errors; diff against cf_tdm exactly 4 lines. Running: code/cfarm_null_fix (no policy,
tax 0 confirmed in its log) -- it must reproduce the benchmark: revenue about 6.036-6.039, CEV
about 0. Then TF 85 against its revenue. The 12-block revenue diagnostic was stopped (not needed).
SOURCE FIX PROPOSED, NOT MADE: apply the tax warm start only when the tax is the instrument.

# 26 September 08:15: TF 85 CONVERGED (not firm); the benchmark's 12 blocks are an income fixed point

TF 85 on cf_tdm exited at pass 6 on every rule: pi_V 0.08184, b -29.8%, SUD -30.4%, h +5.6%,
CEV +1.13% (+1.39 net of the no-policy run); results/counterfactuals_cf_local/tf_tdm85. Not firm:
drug use was still rising about half a point a pass at exit (moments 4.3e-4 against 5e-4; the
parent-to-child penalty converges one generation per pass), and the no-policy gap is unexplained.
REVDIAG, benchmark side: warm-started from the re-solve's FINAL state, block 1 still gives net
revenue 10.34 (labour-income tax 12.98, investment 0.94, consumption and property 0). The
benchmark restarts its income normalisers every run: average labour income 1.148 -> 1.384 ->
... -> 1.617 at block 12, median income 0.580 -> 0.863, eligibles holding a voucher 0.072 ->
0.273. Only block 12 is its fixed point, so the diagnostic now runs all 12 blocks
(code/cfarm_bench_revdiag, about 2.5 h). The counterfactual side (code/cfarm_null_revdiag, no
policy seeded from its converged distribution) prints the same components.

# 26 September 07:55: THE BENCHMARK REPRODUCES ITSELF -- the no-policy gap is in the counterfactual binary

Re-solve (results/reference/hf_omega_c_006_tdm): 12 blocks at the counterfactual's numerics end at
net revenue 6.03603 against the old 6.03888, every saved value within 0.05 per cent. So the
no-policy counterfactual's +0.137 of net revenue (all of it in total revenue, spending barely
moves) and -0.26 per cent of welfare come from something the counterfactual binary does
differently. Checked and matching the benchmark: average labour income, net wealth, median
income, drug threshold, rental management costs, c_1 (its 592.94 prints are startup values; the
saved 171.39 is the value that clears the benchmark's housing market). Next: REVDIAG copies of
both binaries print the four revenue components (labour, consumption, investment income,
property) where they are summed; the benchmark side runs two blocks warm-started from the
re-solve's final state (code/cfarm_bench_revdiag), the counterfactual side a no-policy run seeded
from the no-policy distribution. TF 85 (code/cfarm_tf_tdm85, target 6.1753) is near convergence:
pass 5 pi_V 0.08185, b -30.3%, SUD -30.9%, h +5.4%, CEV +1.18% (+1.44% net of the no-policy
run) -- NOT firm until the counterfactual-side gap is explained.

# 26 September 03:50: BENCHMARK RE-SOLVE FIRST (the author: "run the benchmark re-solve first")

Why: a no-policy counterfactual should reproduce the benchmark (CEV about 0). The old converged
no-policy run gave +0.14 per cent and net revenue 6.2646 against the benchmark's saved 6.0389
(+0.226). Almost all of it is total revenue (14.278 against 14.040, +1.7 per cent); spending
barely differs; income +0.44 and consumption +0.14 per cent. The counterfactual's imported
averages match the saved benchmark (average labour income 1.6164, net wealth 3.3461). Leading
suspect: the benchmark itself, solved on the loose 6e-4 rule, with net revenue still falling in
its last four blocks (6.060, 6.049, 6.041, 6.039) and one sweep in the last. The +1.21 per
cent of a no-policy FIRST pass is separate: in pass 1 newborn_parent_share is (1,0,0,0), so no
child inherits a penalty (the first-sweep wave repeats when pass 2 restores the shares).
Build code/bench_tdm (scratchpad build_bench_tdm.sh): the benchmark binary with the calibration
loop's rule 6e-4 -> 5e-5 (47815) and at least 70 sweeps -- the counterfactual build's numerics.
Three builds, 7 warnings / 0 errors, 4 diff lines. Running code/cfarm_bench_tdm (scratchpad
bench_tdm.sh): same seed, same 97-line handover as cfarm_bench's stage 1, 12 frozen blocks,
into save_welfare_curve; it saves a full benchmark file set. TF 85 on cf_tdm was stopped after
pass 1 (log in the scratchpad) since a changed benchmark changes what every arm imports.
Still running: code/cfarm_null_tdm (no policy on cf_tdm, the other half of the comparison).

# 26 September 03:20: 5e-6 IS BELOW THE DISTRIBUTION'S FLOOR -- at least 70 sweeps a pass, then 5e-5

The no-policy run's first pass on cf_tightdist: the transient washes out after one lifetime
(per-sweep change 7.9e-4 at sweep 58, 7e-5 at 61; life_span 60), then the change bounces
between 1e-5 and 4e-4 with spikes in identical pairs and never settles below 5e-6 (156
sweeps, still 4.4e-5). So every pass would run to the 200-sweep cap: about an hour a TF
pass (TF sweeps take about 16 s, the no-policy run's about 7 s). The lag that made pi_V
cycle is removed by sweeping a whole lifetime every pass, not by the tolerance: build copy
code/cf_tdm (and _permban), scratchpad build_cf_tdm.sh = the 1e-3 halving build, seeded,
with the loop's rule 5e-5 and `do while ((distance > rule) .OR. (loop_count_dist < 70))`.
Seeding (the author: "You can also use the old equilibrium distribution"): use_old_distribution
1, read from distribution_stationary{1,2}seed.dat, which the arm script copies from a finished
run's counter_arm files or, with SEED_FROM=bench, from the benchmark's (sizes checked); the
benchmark's own files are not touched. The old runs' distributions were not kept. The arm
script's check now requires every pass at least 70 sweeps, final at or below 5e-5, and
below the cap. Three builds each, 7 warnings / 0 errors; each diff exactly the intended lines.
Running: code/cfarm_null_tightdist (no policy, 5e-6 rule, so 200 sweeps a pass -- the most
tightly solved run, and the source of the budget target) and code/cfarm_tf_tdm85 (seeded
from the benchmark, pi_V 0.0725, price 0.874, target 6.26479886, rule 1e-3; confirmed in
its log). Plan: TF 70 seeded from the no-policy run; the ban and elasticity 5 seeded from
TF 85; TF 85 repeated from the benchmark seed at a different pi_V as the uniqueness check.

# 26 September 03:10: TF RUNS MOVE TO THE 1e-3 HALVING BUILD (author's requests)

The author: "Why can't you clear the budget around 0.0002?", then "Maybe you need to update
piv more slowly closer to the end", then "You can do 0.001 too if it helps". Build copies
code/cf_tightdist_b3h and _b3h_permban (scratchpad build_cf_tightdist_b3h.sh): cf_tightdist
plus budget rule 1e-3 and pi_V's step HALVED whenever the budget gap changes sign (floor
0.05/8, prints "PV STEP: gap= gain="). Gain left at 0.05: the budget's slope in pi_V was
measured at about -8 (pass 1 of the two 70% runs) and about -21 including the distribution's
response, so a larger fixed gain could overshoot. Three builds each, 7 warnings / 0 errors;
diffs against cf_tightdist_b4 and between the pair are exactly the intended lines.
TF 85 on cf_tightdist was stopped in its first pass and relaunched as code/cfarm_tf_b3h85
(pi_V start 0.0725, price 0.874, target 6.26479886 pending the new no-policy run); its log
confirms detection 0.85, pi_V 0.0725, rule 1e-3. The no-policy run continues on cf_tightdist
(no budget clearing, so neither change touches it). Its first pass shows the distribution
converging in waves (a bump from 9.4e-6 to 1.2e-4 at sweep 68; acceleration is off,
accelerate_distribution = 0), most likely the parent-to-child link echoing a generation on.
Every relaunch starts from the best equilibrium guesses available (the author).

# 26 September 02:50: THE DISTRIBUTION SOLVED EACH PASS -- no-policy and TF 85 running

Build copies code/cf_tightdist and code/cf_tightdist_permban (scratchpad
build_cf_tightdist.sh): cf_childdecomp_tight (budget rule 2e-3 plus the diagnostic
children's and adults' split) with the counterfactual loop's distribution rule
6e-4 -> 5e-6 (source line 52877 only; the benchmark loop's 47815 untouched, asserted);
the permban copy also sets voucher_exclusion_release 0 and differs from the other by
that one line. Three builds each, 7 warnings / 0 errors. Arm script scratchpad
tightdist_cf_arm.sh (BUILD, PDET, PV_START, DRUG_PRICE_START, NET_TARGET, SUPPLY_ELAST,
DIAG_TAG); after the run it prints DIST CHECK PASS only if every pass ended at or below
5e-6 without hitting the 200-sweep cap.
Running: code/cfarm_null_tightdist (no policy, pi_V at the benchmark's, price start
1.00014) and code/cfarm_tf_tightdist85 (detection 0.85, target 6.26479886 -- to be
checked against the new no-policy net revenue -- price start 0.874, pi_V start 0.0725,
the middle of the old cycle). Next: TF 70, the permanent ban, elasticity 5 (85 per
cent), omega_c = 1.

# 26 September 02:30: THE TF WELFARE NUMBERS ARE NOT FIRM -- pi_V cycles because the distribution converges across passes

The "firm" 70 and 85 per cent runs (results/counterfactuals_cf_local/tf_tight70, tf_tight85)
stopped at the bottom of a cycle, not at a fixed point. PROOF: tf_childsplit70, same model,
rules and target, warm-started at tf_tight70's exit, stopped at pass 7 near the TOP of the
same cycle: pi_V 0.0758, h +8.2%, CEV +0.70%, against tf_tight70's 0.0688, +10.3%, -0.30%.
Both satisfy every stopping rule. The permanent ban (tf_permban85) stopped on the way down
at +0.15% (peak +1.03% at pass 7). The loose-rule pair of 22:45 (+0.15%, +0.73%) was the
same cycle, NOT the budget tolerance.

CAUSE: in the counterfactual loop stopping_rule_stationary_distribution is 6e-4 when
include_addiction is 1 (source ~52877), a per-sweep change, reached in 1 to 9 sweeps a pass.
The distribution is therefore a lagged state carried from pass to pass; the budget each
pass sees trails the pi_V that produced it, and pi_V overshoots with a period of about 12
passes. Measured in tf_tight70: passes 2 -> 3 moved pi_V 0.0681 -> 0.0685 while the budget
residual moved +0.057. Within one pass the budget answers pi_V with a slope of about -21,
so the static step (gain 0.05) contracts almost at once; the cycle is the distribution.
The source already says this for the benchmark loop (~47794: "the distribution converges
ACROSS blocks rather than within them") and gives its fixed-parameter pass 1e-8; the
counterfactual loop was never given the same.

What survives: in every pass TF cuts b 27-30% and SUD 28-30% and raises h (+7 to +17%).
The sign of welfare does not: 70% ranges -0.3 to +0.7 across the cycle.

PROPOSED FIX (awaiting the author; a kill of the two runs was refused by the permission
system at 01:25 and both have since exited on their own): a build copy with the
counterfactual loop's distribution rule 6e-4 -> 5e-6, a solver tolerance, not a model
change. Passes lengthen (value function ~4.2 min, a sweep ~19 s), passes should fall to a
handful. Order: the no-policy run first (the budget target and the +0.14% offset come
from it), then TF 70, TF 85, permanent ban, elasticity 5; omega_c = 1 on the same build
for comparability.

# 26 September 01:00: SUPPLY ELASTICITY 5 queued (the author: "run the supply elasticity 5 case")

Rationed TF, 85 per cent detection, tight budget rule (cf_tightbudget), target 6.26479886,
drug_supply_elasticity 5 with the supply level refitted (shifter 1.604666 -> 1.148080, price
1.000 at the benchmark quantity; see ENGINE.md). Script: scratchpad tight_elast_cf_arm.sh,
SUPPLY_ELAST=5 PDET=0.85 DIAG_TAG=_elast5_85, price start 0.94, PV_START 0.0702. Starts in
the first free slot (running: cfarm_tf_permban85, cfarm_tf_childdecomp_tight).

# 26 September 00:25: PERMANENT BAN queued (the author: "try the permanent ban")

Build copy code/cf_permban (scratchpad build_cf_permban.sh): voucher_exclusion_release
1/3 -> 0 (used only in the exclusion rows, no division) plus the tight budget rule
2e-3; three builds 7 warnings / 0 errors. Run at 85 per cent detection (the author:
"i think the 85% is more reasonable"), corrected target 6.26479886, warm start from
the tight 85 run, via scratchpad permban_cf_arm.sh with DIAG_TAG _permban85. Starts
when a tight run finishes and its directory is saved and freed.

# 25 September 22:55: FIRM TF NUMBERS -- 70 and 85 per cent detection with the budget closed tightly

The author: "finish both and give me firm numbers for 70% and 85%". Build copy
code/cf_tightbudget (scratchpad build_cf_tightbudget.sh): stopping_rule_govt_budget
2.5e-2 -> 2.0e-3, nothing else; three builds 7 warnings / 0 errors (a first attempt
ran them in parallel in one directory and collided on the module file).
Running (scratchpad tight_cf_arm.sh): code/cfarm_tf_tight70 (warm start price 0.8776,
pi_V 0.0753) and code/cfarm_tf_tight85 (0.8708, 0.0711); logs confirm the rule 2e-3,
the target 6.26479886, detection 0.70 / 0.85, applicant switch 1.
PAUSED (killed by pid, logs in the scratchpad *_paused.log.gz, directories removed):
cfarm_tf_old_saved (pass 5) and cfarm_tf_old_like (pass 0); restart after, ideally
on the tight build too so the comparison uses the same tolerance.

# 25 September 22:45: TWO CONVERGED TF RUNS DISAGREE ON WELFARE -- the budget tolerance is too loose

Same settings (rationed TF, 70% detection, target 6.26479886), different start:
run 1 (from the benchmark pi_V; results/counterfactuals_cf_local/tf): 10 passes, budget
gap at exit 0.021, pi_V 0.0705, voucher spending 0.643, h 0.00662, lifetime 789.4006,
CEV +0.15%. run 2 (warm start at pi_V 0.0715, price 0.881; the childdecomp run,
scratchpad cf_tf_childdecomp.log.gz): 8 passes, gap 0.008, pi_V 0.0753, spending
0.656, h 0.00655, lifetime 789.5976, CEV +0.73%. Both pass every stopping rule;
stopping_rule_govt_budget = 0.025 (declared, no handover case) is about 4% of voucher
spending, and welfare moves ~0.6pp of CEV inside it. NOT a best-of: neither is THE
number until a run closes the budget tightly (build copy with the declared value
changed, e.g. 2e-3). Welfare split, run 2 against the null: childhood +0.091 (users'
children 20.1% -> 14.6%, excluded 0.54%, homeless 0.97 -> 1.03%), adult +0.110 of
which the inherited penalty (penalised newborns 2.93% -> 2.10%) about +0.047.
Running: cfarm_tf_old_saved, cfarm_tf_old_like (19 Sep design, both targets).

# 25 September 22:05: QUEUE (the author: "yes, rerun both after the diagnostic")

1. running: cfarm_null_childdecomp (welfare split, no policy) and cfarm_tf_pdet85.
2. next, in the slot the null frees: TF on the cf_childdecomp build, corrected target
   6.2647988599575077, warm start (price 0.881, PV_START 0.0715).
3. after the diagnostic: the 19 September design (INC=0) on the fixed code, twice,
   via scratchpad design2_cf_arm.sh -- DIAG_TAG _old_like with NET_TARGET
   6.2647988599575077, and _old_saved without it -- price start 0.85.
At most two solves at once (ENGINE.md, memory).

# 25 September 21:55: the inherited channel works under TF; diagnostic extended to adults

The author: TF is "totally misaligned" with the stylized model, whose TF gain runs
through children inheriting better draws. The quantitative model's analogue is the
penalty class (child_penalty_classes 2, fed by newborn_parent_share), and it UPDATES
in the counterfactual: newborns with a disordered parent 2.93% (null) -> 2.18% (TF,
-26%) and 2.07% (omega_c 1, -29%); disordered or homeless 3.09% -> 2.34% (-24%) and
2.23% (-28%). Difference in the experiments: the stylized comparison is UNIVERSAL HF
against universal TF with zero homelessness under both; the quantitative one is
rationed TF with homelessness +9% and vouchers -5%. Diagnostic rebuilt with
ADULTDECOMP (age-one value by penalty class x SUD); cfarm_null_childdecomp restarted
on it (the first start had 2.7 minutes of run time).

# 25 September 21:30: the author bets on a code error behind TF's CEV of about 0

Checked and CLEARED: the child's flow uses goods consumption net of drugs
(consumption_choice = total*(1-frac_spent), asserted at six places). b_shifter is
addiction_scalar_1 (0.0055) for every child regardless of parental SUD (times
b_smi_multiple under SMI), and value_of_life (87.62) enters the child's flow as
(xi-1)*(u+aleph), so children do not die and the constant cancels. Homeless size
0.0216 against the smallest rental 0.0407 (53 per cent); housing share 0.447, sigma 2.
The author: drug spending is about 16 per cent of income for the 10 per cent who use,
so the diversion channel should be worth roughly +0.3 to +0.5 to children under TF,
against a measured -0.01. DIAGNOSTIC: scratchpad build_cf_childdecomp.sh prints
CHILDDECOMP mass/util/cons by household (1 homeless, 2 housed and using, 3 voucher,
4 excluded, 5 other), discounted and age-normalised so util sums to own childhood
before the kappa_x term. Running: cfarm_null_childdecomp (no policy); next, TF on the
same build with the corrected target once cfarm_tf_pdet85 frees memory.

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

