# tf_ruleC2_test -- the abstention option under rule C (cf_fix2_treatC2): RESULT

**FINAL (12 Oct, 23:30 UTC). B and the compile table PASSED; patch_treatC2.py is READY to be copied over patch_treatC.py
(keeping the old one as patch_treatC_v1.py; not done here). Test C skipped per the coordinating session's addendum 2;
no other arm was launched.** Two things the switch-over must handle: `transition_fix/build_tr70_C.sh` refuses the
larger patch (section 7), and Treatment First changes for clean households too, not only through abstention (section 2).

| check | verdict |
|---|---|
| B, inert, 4 threads | NOT DECIDABLE AT 4 THREADS: the same cf_fix2_treatC binary run twice differs in the 4th decimal of welfare (a pre-existing data race, section 3); cf_fix2_treatC2 lands inside that spread |
| B, inert, 1 thread (bit for bit) | **PASSED**: the no-policy arm (no screen), pass 1 from the benchmark, cf_fix2_treatC against cf_fix2_treatC2 at OMP_NUM_THREADS=1: every line of the log identical apart from timing and the two new prints (welfare 789.12700176076169, b 0.086767962688725053, lambda_d 0.036939304740738692, h_1 0.0059992578920585564 in both) |
| compile / drop-in table | PASSED on every base except `transition_fix/build_tr70_C.sh`, whose own guard refuses the larger patch (use `build_tr70_C2.sh`; section 5) |

## 1. What was changed, and where

`code/treat/patch_treatC2.py IN OUT`. Same arguments as `patch_treatC.py`; it does everything that script does
(it calls `patch_treat.py split` itself and applies the rule-C screen and the two distribution call sites), so it is
**ready to be copied over `patch_treatC.py`** (the copy has been simulated, section 5). On top of rule C:

| # | routine | change | gate |
|---|---|---|---|
| 1 | Global_Vars | `integer :: abstain_now=0`, `!$omp threadprivate(abstain_now)` beside `treatment_choice_now`; switches `tc2_abstain_on/evkey_on/internal_on` (env `TC2_ABSTAIN`, `TC2_EVKEY`, `TC2_INTERNAL`, default 1, read once in `initialize_variables_and_grids`, printed as `TREATC2 switches`) | - |
| 2 | `renter_to_renter_problem` | `do abstain_choice_1=0,abstain_top_1` nested in `do treatment_choice_1`; `abstain_top_1=1` only if is_counterfactual, voucher_conditional_on_clean, the disorder, treatment_choice_1=1, include_treatment. `abstain_now` reset at the routine's top and after the loops | screen |
| 3 | `calculate_addiction_spending` | `abstain_now==1`: the treatment's money cost charged as before, then v=0 and c = all the rest; `optimize_frac_spent_on_addiciton` (and its child and risk refinements) skipped; the food-stamp check below it applies unchanged. The use index stays 1, recovery and mortality unchanged | abstain_now |
| 4 | `ensure_ev_table`, `fill_ev_table`, the two table reads in `renter_to_renter_problem`, the allocation | the table's opportunity dimension widened 0:1 -> 0:7, column `opp+2*voucher_category` when the screen is on, `opp` otherwise (section 2) | screen |
| 5 | `solve_value_function_and_policy_functions`, around `call internal_computations` | `treatment_choice_now` (and `abstain_now` for a treated household with the disorder and a stored v=0) set from the stored policy before the call, reset after | screen |
| 6 | `govt_revenues_calc` | drug use as v>0 (section 4) and the ABSTAIN accumulators | screen (the print is unconditional) |
| 7 | `govt_revenues_calc`, the transition's period loop | `ABSTAIN` and `TRANSITION ABSTAIN t=` prints (section 6) | - |

The only routine with a treatment choice is `renter_to_renter_problem` (owners have none), so the abstention option is
renters-only by construction. The candidate's v=0 is what `compute_voucher_index_1` sees (it is called after the secant
in the same branch), what is stored in `optimal_frac_spent_on_addiction_renter_renter` and then in
`policy_function_frac_spent_on_addiction`, so the distribution, the drug market, the distribution's screen sites, MILBY
SPLIT and the transition all read it.

Builds: `code/treat/build_treatC2.sh` -> `code/cf_fix2_treatC2`; `code/transition_fix/build_tr70_C2.sh` -> `code/tr70_C2`
(the transition's household problem is the same `renter_to_renter_problem`, in its own copy of the source, so the same
patch applies). Launchers: `code/treat/cf_arm_C2.sh` (cf_arm_C.sh with cf_fix2_treatC2 admitted and
`OMP_NUM_THREADS` taken from the caller), `code/treat/remote_treatC2.sh STEP`. Both compile with 0 errors (-O3
-funroll-loops -fimplicit-none -fopenmp -ffree-line-length-none -mcmodel=medium).

## 2. The design in the brief was incomplete: the EV table ignored the voucher category (AUDIT_E Finding 1)

`fill_ev_table`'s sum reads `voucher_probabilities(voucher_index,fv,opp,evx_vidx)`, but the cache was keyed on (use
state, dwelling, opportunity) and invalidated only when the household's own state moved. `code/audit/AUDIT_E_household.md`
found this ("DORMANT IN THE BENCHMARK, LIVE IN THE COUNTERFACTUAL") and it was still open. Under the screen the category
differs across the candidates at one node, so every candidate after the first at a (dwelling, opportunity) pair read the
first candidate's continuation:

- **without the fix the abstention option does nothing**: the loop order is untreated (category 3), treated-and-using
  (3), treated-and-abstaining (1 or 2), so the abstainer reads a category-3 table, never sees the voucher it keeps, and
  only ever loses drug utility;
- **in every Treatment First arm so far** (rule A and rule C, the paper's and the running ones), a clean household's
  use candidate (category 3) read the table filled by its no-use candidate (1 or 2): **users did not foresee losing the
  voucher in their continuation**; the loss reached them only through the distribution. The un-hoisted nest would have
  been right; the hoisted table is what runs (`hoist_expectation=1`).

So the fix is part of treatC2 and changes Treatment First for clean households too. `TC2_EVKEY=0` turns it off for a
decomposition. With the screen off the column is `opp` exactly as before.

## 3. A pre-existing data race makes 4-thread runs irreproducible

In `solve_value_function_and_policy_functions`' `!$omp parallel do default(none)`, `run_internal_grid` (and
`labor_supply_2`) are in `shared(...)` but are written per node by every thread (`run_internal_grid=1/0` at the node,
read on the next line to decide whether `internal_computations` runs). Another thread can overwrite it between the
write and the read, so a node can skip, or run, the internal-grid pass by timing alone. Present in every build
(benchmark included); not changed here, because making them private changes every build's arithmetic.

Measured: the no-policy arm, pass 1, from the benchmark, the **same** cf_fix2_treatC binary twice:

| run | welfare | drug gap | MILBY voucher mass |
|---|---|---|---|
| cf_fix2_treatC, beside 9 compiles (`inert_C_run1_loaded/`) | 789.1269 | 1.89e-03 | 0.180592 |
| cf_fix2_treatC, alone (`inert_C/`) | 789.1271 | 1.70e-03 | 0.180644 |
| cf_fix2_treatC2, alone (`inert_C2/`) | 789.1273 | 1.81e-03 | 0.180623 |

The logs agree line for line up to the value-function solve and first differ at `DIST_MOM sweep= 0`, i.e. in the
policies. The noise is about 2e-4 in welfare (0.01 pp of CEV) at pass 1. It is small next to every effect in the
paper, but it means "bit for bit" can only be checked at one thread, and that any two arms the paper differences (e.g.
a decomposition column of a few hundredths of a point) carry it. **Recommend** a separate, announced change making
`run_internal_grid` and `labor_supply_2` private.

### The inert check (B), at one thread

`inert1_C/` and `inert1_C2/`: the no-policy arm (voucher_conditional_on_clean=0) from results/reference/hf_2c_omega_0.085,
one pass each, `OMP_NUM_THREADS=1` (no race), 1593 s each. Diffing the two logs with the timing lines (`AGE_TIME`,
`time=`) and the two new prints (`TREATC2 switches`, `ABSTAIN`) removed: no difference; cf_fix2_treatC2's log is a
prefix of cf_fix2_treatC's (the latter has 11 more lines, the start of pass 2, because its pass-cap kill landed later).
The lines `average_welfare_with_childhood=`, `CF MOMENTS`, `distance_drug_market=`, `drug quantity V=`,
`net_govt_revenues=` and `MILBY SPLIT` hash to the same md5. No guard text in either log.

| | price | pi_V | b | SUD | h_1 | drug gap | welfare |
|---|---|---|---|---|---|---|---|
| cf_fix2_treatC | 0.9999 | 0.06753 | 0.086767962688725053 | 0.036939304740738692 | 0.0059992578920585564 | 1.49e-03 | 789.12700176076169 |
| cf_fix2_treatC2 | 0.9999 | 0.06753 | 0.086767962688725053 | 0.036939304740738692 | 0.0059992578920585564 | 1.49e-03 | 789.12700176076169 |

## 4. Drug use counted by the disorder rather than by v>0: every site

The rule "user = (v>0 and clean) or the disorder" counts an abstainer as a user. Sites in `govt_revenues_calc` and what
was done (all changes gated on the screen and on `TC2_ABSTAIN`, so bit for bit unchanged without the screen):

| site | statistic | feeds | done |
|---|---|---|---|
| `model_total_drug_users = model_addicted + model_exprimenters` | b | `CF MOMENTS b=` (passes.txt b, V/user), finalstats `drug use b`, every exporter's b, `TRANSITION MECH b=` | **changed**: minus the treated v=0 mass |
| user rule (6 sites in the steady-state source, 3 in tr70's): `diag_users_eligible`, `diag_users_tested`, the voucher-state/age/income user diagnostics, `model_mass_total_users` (denominator of mean quantity per user, use by age, user income and assets), the experimentation block, `dg_use_here` (DIAG who stops) | | `DIAG use by voucher state`, `DIAG who stops` (export_whostops.py), `DIAG mean drug quantity, users` (export_longrun.py), MOMENT y_u, user ages | **changed**: the disorder half requires "not an abstainer" (`tc2_ab_1`, set per node: the disorder, treated, spending 0) |
| `model_age_by_addiction` (disorder or v>0) | | per-pass print | **changed** likewise |
| `model_addicted`, `model_fraction_addicted`, `model_mass_addicts`, MILBY, treatment take-up, SMI cross-tab, `model_addicts_getting_voucher`, `model_addicts_consuming_no_drugs` | disorder rates | lambda_d, MILBY SPLIT | unchanged, correctly: they are about the disorder |
| `model_drugs_consumed_by_users` (the drug market's quantity), `drug quantity V=` | quantity | price clearing | unchanged: sums spending, an abstainer adds 0 |
| `addiction_rate_by_age` ("sud=" column of DIAG age, export_longrun `par_use`), experimenter shares | already v>0 | | unchanged |

**A caveat on like-for-like comparisons.** Even with no screen, some households with the disorder spend v=0 at a budget
corner (the Stone-Geary split hits the corner): in the no-policy arm's ABSTAIN line, treated v=0 is 0.031 and untreated
v=0 0.054 (unnormalised masses; the population is about 50.8), i.e. 87% of the treated homeless and 36% of treated
holders. Gated as briefed, treatC2's b in a Treatment First arm excludes the treated v=0 (choice and corner alike) while
the benchmark's and no-policy arms' b include them. For a like-for-like change in b the comparison arm's b should be
reduced by its own `treated_v0` (printed in every arm on treatC2, screen or not), or the v>0 rule made unconditional
(which moves the benchmark's b, a calibration target). The author's call; nothing was done about it.

## 5. Guards

"error wrong addiction option" and the "wrong renter renter"/"wrong stay"/... guards key on the use index, which stays 1
for an abstainer; the c = C(1-v) consistency checks ("wrong", "wrong_1", "wrong_objective", "wrong_secant") hold at v=0;
the marginal utility of the drug at v=0 is finite (b>0); no division or log of an abstainer's spending is unguarded;
the disorder transition ignores v for a household that has the disorder. `guards.txt` in each step folder lists any
guard text in the logs (none in the inert runs).

## 6. The ABSTAIN print (format)

Once per `govt_revenues_calc` call (twice per pass; the second is the pass's), one line, list-directed, `key= value`
pairs; masses unnormalised (divide by the distribution's mass, about 50.8, for shares), only households with the disorder:

    ABSTAIN sud= <all with the disorder> treated= <in treatment> treated_v0= <in treatment, v=0>
      untreated_v0= <not in treatment, v=0>
      holder_treated= <voucher holders, housed, in treatment> holder_v0share= <share of those with v=0>
      housednov_treated= <housed, no voucher, in treatment> housednov_v0share= <...>
      homeless_treated= <homeless, in treatment> homeless_v0share= <...>

Housed is `housing_status_index_used>=second_lowest_housing_grid_point` and holder is `voucher_index==1`, as MILBY SPLIT
draws them (holder_treated equals MILBY SPLIT's voucher `treat`). Parse: `dict(zip(t[1::2], map(float, t[2::2])))` on
`line.split()` after the first token. The transition prints the same as `TRANSITION ABSTAIN t= <t> sud= ...` per
period, beside `TRANSITION MILBY t=`.

## 7. Compile and drop-in table

Simulated switch-over in a scratch copy of `code/` with `patch_treatC2.py` copied over `patch_treatC.py` (the old one
kept as `patch_treatC_v1.py`), each script's own build run unchanged (the remote_* scripts build through
`treat/build_treatC.sh` or `pe_noext/build_pe_C.sh`; their `RULE C (patch_treatC.py)` greps still find the marker).
"users" is the number of gated user-rule sites.

| script | base the patch is applied to | patch applied | compiles | ABSTAIN print | TRANSITION ABSTAIN | MILBY SPLIT / TRANSITION MILBY |
|---|---|---|---|---|---|---|
| treat/build_treatC.sh (also used by extra_2c/remote_decomp_shares_C.sh, omega_nishiyama/remote_nish_nodes_C.sh, pdet/remote_pdet_C2.sh) | cf_fix2/cf.f90 | yes (users 7) | yes | yes | yes | yes / yes |
| cf_kid/build_C.sh | cf_fix2_treatC/cf.f90 (+ cf_kid additions) | yes | yes | yes | yes | yes / yes |
| deltad/build_cf_fix2_1c_C.sh | cf_fix2 one class | yes | yes | yes | yes | yes / yes |
| deltah/build_both_sp.sh | cf_fix2 + patch_both, then single precision | yes | yes (bench and cf, 0 errors) | yes | yes | yes / yes |
| pe_noext/build_pe_C.sh (also noext_clear/noext_C_lib.sh) | cf_fix2_pe/cf.f90 | yes | yes | yes | yes | yes / yes |
| revoked_2c/build_C.sh | patch_transition_fix(source), then patch_revoked_C | yes | yes (track10, track3, track3b, plain3) | yes | yes | yes / yes |
| revoked_2c_street/build_C.sh | as revoked_2c + patch_street | yes | yes (street3, street10, track3, plain3) | yes | yes | yes / yes |
| deter_2c/run_whostops_C.sh (treat/build_treatC_impact_C.sh) | cf_fix2 + the fixed distribution | yes | yes | yes | yes | yes / yes |
| transition_fix/build_tr70_C.sh | transition_fix/tr70_src.f90 | yes (users 4; abstain loop in its household problem: yes) | **REFUSES before compiling**: its guard `patch_treatC.py removed $d lines ..., expected 1` sees 21 | - | - | - |
| transition_fix/build_tr70_C2.sh (new) | tr70_src.f90 | yes | yes | yes | yes | yes / yes |

So after the copy, `build_tr70_C.sh` needs its line-count guard relaxed (or the transition built with
`build_tr70_C2.sh`, which carries treatC2-specific guards instead). Every other script picks up the fix unchanged.

## 8. Other things that look wrong (not changed)

- `internal_computations`' no-secant path (retired or not working) recomputes consumption as (1-v)·(resources - a')
  with no treatment money cost, so the internal grid prices a treated non-worker's points without the charge. Present
  in every build; the abstainer's v=0 is unaffected (it is applied as a share), but treated non-workers' internal-grid
  values are too high by the cost.
- The two drug-test counting sites in `govt_revenues_calc` call `compute_voucher_index_1` with `treatment_choice_now=0`;
  harmless while `increased_prob_of_voucher_if_homeless_1` and `..._and_addicted` are both 1 (all categories then have
  the same offer rate), wrong otherwise.
