# The T=45 no-grandfathering transition, session 2, from loop 2 onward

Launched 22 September 19:44 in a fresh container, to carry on from the run that
completed loop 1 at 16:45 and was killed inside loop 2's backward pass at 19:25.
Everything it needs was committed; no benchmark was re-solved here.

## What was staged, and what verified it

    run directory   code/t45_nogf_s2/           (gitignored by code/t[0-9]*_*/)
    build directory code/tr45_s2/               (gitignored by code/tr[0-9]*/)
    binary          hftf_t45s2  = hftf_tr_prod  (-O3 -funroll-loops)

| input | source | the check that passed |
|---|---|---|
| initial condition and `old_results` | `seeds/benchmark_dat/*.gz`, 90 files | `drug_supply_shifterbaseline_benchmark.dat` = 1.62001478993009917495, exact; `median_income` = 0.863112277979, exact |
| terminal condition | `seeds/arm3_counter_TF/*.gz`, 11 files | `check_transition_inputs.py`: 79 required, 79 present |
| parameter vector | `seeds/PARAM_HANDOVER_trans_postfix.txt` | 102 `HANDOVER` lines echoed against 102 lines handed, and the two that prove it is not the declared vector: `relative_share_of_housing` 0.27799999713897705 -> 0.53560465351849429, `kappa_find_smi` 1.0 -> 10.791362553896779 |
| drug price path | `seeds/drug_price_path_seed_t45_nogf_afterloop1.txt` | `DRUG PRICE PATH seeded FROM FILE, entries read= 44 of 44`, and t=1 printed as 0.88605374568268902 against the file's own first entry 0.886053745682689 |
| pi_v path | `seeds/pi_v_path_seed_t45_nogf_afterloop1.txt` | `PI_V PATH seeded FROM FILE, entries read= 44 of 44`; `PI_V GATE: seeded run, pi_v updates from loop 0 (start_updating_at_loop_number=-1)` |

Both seeds were re-checked here against the three refusals the harvester makes,
because these files were copied rather than harvested: no NaN or Inf in either,
44 entries each, price in [0.819050561381922, 0.887091917482469] and pi_v in
[0.076226136906131, 0.086768903041692] with the floor at 1e-5. All three clear,
and all three reproduce `t45_nogf_afterloop1.provenance.md` to the digit.

## The model is the committed one

    md5(code/housing_first_or_treatment_first_SR_v1.f90) = 06a3a7458595d23ec9bda5a1b2d33e6a

`git status` was clean at build time, so `patch_mortality_smi.py` is NOT applied:
that patch is a separate diagnostic under the author's consideration and has no
part in this run. `build_transition_t45.sh` set four compile-time parameters and
refused unless exactly four lines changed, then asserted the two that define the
arm BY VALUE in the generated file -- `grandfather_voucher_states=0` and
`window_distributions=1`. All three builds are clean, all three `.err` files are
zero bytes:

    -O1 -fcheck=bounds,pointer -g -fbacktrace
    -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace
    -O3 -funroll-loops                                        <- the one running

## gfortran WAS NOT IN THIS CONTAINER AND HAD TO BE INSTALLED

Recorded because it is a fact about the measurement rather than a detail of the
setup. A fresh container carries `gcc` and not `gfortran`, so the first build
died on `gfortran: command not found` -- which looked exactly like the reaped
launch this project has paid for four times, and was not. Installed from the
distribution's own archive:

    GNU Fortran (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0

This is the compiler this arm is solved on. The benchmark `.dat` it reads was
produced elsewhere, which is the point of committing that set -- both arms share
ONE benchmark rather than each re-solving its own, and the cross-container spread
of 1.8e-2 on w_bot that `benchmark_dat/README.md` measured is exactly what that
avoids. Nothing here re-solves the benchmark, so that spread does not enter; the
compiler governs only the value functions and policies solved forward from it.
A later session comparing arms should check its own `gfortran --version` against
this line rather than assume it matched.

## The launch

    pid 1253, pgid 1253, sid 1253 -- its own session
    ppid 1251, a bash whose own parent is 1

which is the recipe ENGINE.md recorded on 22 September 19:05 as the one that
survived a container restart: launched from a BACKGROUND task, under `setsid`,
with that task allowed to EXIT rather than held alive as an anchor. At 37s it
held 5.2 GB RSS on 4 threads at 310 per cent of 400, against the build script's
predicted 6.5 GB peak.

## What convergence means here

Two equilibrium objects, `price_of_addictive_good_path(t)` and
`probability_of_voucher_path(t)`. The exit test is on the `largest_*` maxima with
`transition_tolerance_factor=2`, so drug 1e-2 and budget 5e-2; housing and rental
distances are zeroed by `peg_prices_in_counterfactual=1`; `max_counterfactual_loops=250`.
Loop 1 ended with the budget residual at 0.032962, having come down
0.069356 -> 0.046182 -> 0.032962, so the budget rule is already satisfied and the
drug market is the live condition.
