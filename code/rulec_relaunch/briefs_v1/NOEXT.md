# NOEXT: Rule C: the three no-externality Treatment First arms (engineering + run)

session session_01KfNXrhtt2bGBBJh7QNhh7N (ended 12 Oct 21:00 UTC), model claude-opus-5-5

```
You are an engineering-and-run worker for an economics paper (Fortran model, bash/Python tooling). Branch claude/two-period-addiction-hazard-d7gb61 (checked out). Read CLAUDE.md and code/RULE_C_PLAN.md first. Commit messages end with
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv
Push with `git fetch origin <branch> && git rebase FETCH_HEAD && git push origin HEAD:<branch>` (others push too; never force). NEVER edit writing/ and NEVER edit an existing script (other workers may be executing it): make new copies with a _C suffix. No pull requests.

CONTEXT. The paper's Treatment First screen changed to RULE C (code/treat/patch_treatC.py: a household with the disorder must be in treatment, nobody may use). Every Treatment First run the paper uses is being redone on rule C; Housing First / no-policy arms have no screen and are not re-run. Rule-C builds: code/treat/build_treatC.sh (cf_fix2 -> cf_fix2_treatC) and code/treat/cf_arm_C.sh (an arm script admitting rule-C builds, DRUG_MARKET_ADJUSTER from env). See code/extra_2c/remote_decomp_shares_C.sh and code/pdet/remote_pdet_C.sh for how rule-A launchers were turned into rule-C copies.

YOUR JOB: the three no-externality Treatment First arms the paper reads (code/paper/export_longrun.py and export_pe_noext.py):
 1. results/pe_noext, Arm B (code/pe_noext/run_pe.sh: TF with weight_on_child 0 and both child penalties 0, drug price, pi_V and the house price held at Arm A's; BUILD cf_fix2_pe from code/pe_noext/build_pe.sh + patch_pe.py, plus the walk on Arm A's distribution, code/pe_noext/run_walk.sh, and analyse.py -> analysis.json);
 2. results/noext_fixp, Arm D (code/noext_clear/run_noext_fixp.sh: drug price held at Arm A's, pi_V clearing against Arm A's net revenue);
 3. results/noext_clear, Arm C (code/noext_clear/run_noext_clear.sh: price and pi_V clearing).
Make rule-C copies (e.g. code/pe_noext/run_pe_C.sh, code/noext_clear/run_noext_fixp_C.sh, run_noext_clear_C.sh, a rule-C build of cf_fix2_pe = patch_treatC on top of patch_pe, and a copy of pe_noext/cf_arm_pe.sh admitting the rule-C builds) writing to results/pe_noext_C, results/noext_fixp_C, results/noext_clear_C, with the same structure and files as the rule-A results so the exporters can be pointed at them. Arm A (Housing First without externalities) is unchanged by the rule: reuse rule A's values where the scripts allow it, but re-solve it where the TF arm needs its files in the same container (walks, seeds). Warm-start every TF arm at its rule-A counterpart's converged price and pi_V (the author: "start the simulations from guesses that equal each corresponding simulation with rule a"; the values are in the rule-A results' final.txt / status). Verify each rule-C build compiles and that the patch landed (grep "RULE C (patch_treatC.py)").

Then RUN all three in this container to completion, as many at once as 4 cores and 15 GiB allow (each solve uses 2 threads), re-attaching whenever a background call stops (start each launcher with the Bash tool's run_in_background=true; running the same command again attaches). Each launcher must publish its status to its results folder every 20 minutes. Accept an arm only with DIST CHECK PASS, the budget cleared where pi_V clears (TARGET CHECK PASS), and no GUARD. When all three are accepted and pushed, reply with one paragraph: per arm, the newborn CEV, drug use, SUD, homelessness, pi_V, price, against rule A's values, and the paths of the new scripts. If something cannot be done, push what you have and reply with the problem and the options.
```
