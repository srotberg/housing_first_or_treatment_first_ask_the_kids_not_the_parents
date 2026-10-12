# RULE C: THE PLAN TO FINISH THE PAPER (12 October)

The author: "I think we should redo the whole paper with rule C", "all the stuff we are waiting on should be done on rule
C. and all the stuff already in the paper should be redone for rule C including any validation we rely on", "go ahead,
write out the plan, and execute to finish the paper fully finally", "use parallel sessions where you can".

Rule C: a household with the disorder must be in treatment, and no household may use (EO 14321 Sec. 5(b); the
ONDCP/HHS/HUD 2026 toolkit, p. 9). code/treat/patch_treatC.py. Housing First, the no-policy arms and the benchmarks have
no screen and are NOT re-run. The stylized model (Section 3) has no treatment choice and is NOT re-run.

## Workstreams (parallel)

| id | what | where | depends on | status |
|---|---|---|---|---|
| C1 | main Treatment First arm, detection 0.85, $35 test, price and pi_V clearing | cloud session_01RuzfgApLN9fv3B7J6B8kpS, code/treat/remote_treatC.sh -> results/counterfactuals_2c/tf_ruleC | - | building 17:01; INERT CHECK at pass 1 |
| INV | inventory of every Treatment First-dependent number in the paper (validation included) and the run behind it | local agent -> scratchpad ruleC_inventory.md, then into this file | - | running |
| BOTH | both penalties (delta_d 0.24, delta_h 0.31), long run, rule C, single precision + checkpoints; the disk (29 GB) cannot hold the four-class benchmark's text files plus an arm's, so the engineering is part of the job | cloud engineering session | - | launching |
| ARMS | every other rule-C arm the inventory lists (decomposition columns, no-externality columns, detection 0.70 and 0.50, omega_c 0.686, delta_d = 0 with its benchmark re-solved, the Milby split, who-stops and revocation prints), one cloud session each | cloud sessions | C1 passes the inert check; warm start from C1's latest pass | after INV |
| TR | the T = 70 transition on rule C (two loops) and the cohort-print loop | cloud session | C1 accepted | after C1 |
| PAPER | exporters re-pointed to the rule-C arms, every number regenerated, Section 4's rule and its footnote, the rule-A footnote, introduction and abstract; red, struck deletions, notes | this session | arms land | as they land |
| CODE | the code/ scripts reorganised (REFEREE_PLAN item 5) | this session | no run executing them | last |

## Gates
- C1 inert check (pass 1): welfare differs from rule A's 789.9399 at the same start, and the MILBY SPLIT line shows
  voucher holders with a SUD in treatment. Fail -> stop, diagnose, tell the author before anything else launches.
- Every arm: DIST CHECK PASS, budget cleared (TARGET CHECK PASS) where pi_V clears, no GUARD.
- The paper is rebuilt only from accepted arms; the checkers pass; the author gets the PDF with every change red.
