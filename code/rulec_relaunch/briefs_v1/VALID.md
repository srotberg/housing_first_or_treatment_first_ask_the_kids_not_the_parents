# VALID: Rule C: validation runs, who-stops and revocations (engineering + run)

session session_015BJgiEXCE5sV9MseUiTq3i (ended 12 Oct 21:00 UTC), model claude-opus-5-5

```
You are an engineering-and-run worker for an economics paper (Fortran model, bash/Python tooling). Branch claude/two-period-addiction-hazard-d7gb61 (checked out). Read CLAUDE.md and code/RULE_C_PLAN.md first. Commit messages end with
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv
Push with `git fetch origin <branch> && git rebase FETCH_HEAD && git push origin HEAD:<branch>` (others push too; never force). NEVER edit writing/ and NEVER edit an existing script (other workers may be executing it): make new copies with a _C suffix. No pull requests.

CONTEXT. The paper's Treatment First screen changed to RULE C (code/treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use). Every Treatment First run the paper uses is being redone on rule C, the validation included. Rule-C build: code/treat/build_treatC.sh (cf_fix2 -> cf_fix2_treatC), arm script code/treat/cf_arm_C.sh. Examples of rule-A launchers turned into rule-C copies: code/extra_2c/remote_decomp_shares_C.sh, code/pdet/remote_pdet_C.sh.

YOUR JOB: the Treatment First runs behind the paper's VALIDATION numbers, on rule C:
 1. WHO STOPS (the Mehay and Pacula military-testing comparison, names x_ws_*, code/paper/export_whostops.py, which reads results/whostops_2c/cfarm_tf_imp_ws850): find the script and patch that produced it (a who-stops print build), make rule-C copies (apply patch_treatC.py together with the print patch; check both land), run, results to results/whostops_2c_C/ with the same files.
 2. REVOCATIONS (the Costantini comparison and the street/SMI numbers, x_rv_*, code/paper/export_revoked.py, reading results/revoked_2c and results/revoked_2c_street): same, results to results/revoked_2c_C and results/revoked_2c_street_C.
Warm-start each Treatment First arm at its rule-A counterpart's converged price and pi_V (the author: "start the simulations from guesses that equal each corresponding simulation with rule a"), or at the rule-C main arm's latest pass in results/counterfactuals_2c/tf_ruleC/passes.txt if that is closer to these runs' design. Verify every build compiles and every patch landed. Then RUN them in this container to completion, as many at once as 4 cores and 15 GiB allow, re-attaching whenever a background call stops (run_in_background=true; the same command again attaches); each launcher publishes its status to its results folder every 20 minutes. Accept a run only with DIST CHECK PASS, the budget cleared where pi_V clears, no GUARD, and the print present. When all are pushed, reply with one paragraph: each validation number on rule C against rule A's, and the paths of the new scripts. If something cannot be done, push what you have and reply with the problem and the options.
```
