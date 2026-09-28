# The corrected transition (TRANSITION_LESSONS.md section 16)

- `patch_transition_fix.py`: the section-16 fixes as a build copy -- every per-period rule at the
  steady state's own value (budget 1e-3), pi_V's first step 0.12, the initial steady state's
  newborn_parent_share read at start-up and restored at t = 1 of every loop -- plus a print-only
  `TRANSITION ALLALIVE` line per period: the average value of everyone alive at the reform on the
  path and in the benchmark, the share better off, overall and by ten-year age band.
- Items 7 and 8 of `patch_transition_fix.py` (28 September): the budget residual at t now steps
  pi_V(t-1), the instrument that sets it (a draw in t-1 makes a holder paid at t); residual(1) is
  reported and left out of the stopping rule, since no pi_V reaches it; the last free period takes
  t-1's value; the secant is used only when its slope has the map's sign. Print-only: `TRANSITION
  HOMELESS_BY_AGE`, `MASS_BY_AGE`, `SUD_BANDS` and `DRUG` lines each period, so childhood
  homelessness along the path can be read off. The `PI_V` line's `t=` is now the instrument period.
- `build_tr60_fix.sh`, `build_tr10_fix.sh` (+ `build_transition_t10_copy.sh`): T = 60 and the
  T = 10 flat control, through the tracked build_transition_t45/t60 scripts.
- `build_cf_fix2_share.sh`: the no-policy steady state that saves its newborn_parent_share, the
  transition's t = 0.
- `stage_tr_fix.sh`: stages a run directory (terminal = the reform arm's counter_arm files, t = 0
  = the no-policy distribution and parent share, flat seeds at the arm's values, budget target).
- `patch_allage_curve.py`: print-only, for the BENCHMARK binary. Averages the welfare curve over
  every age as well as over newborns (`ALLAGE CURVE` lines), so the all-alive gain can be read as
  a CEV.

Results: `results/transition_fix/`. The flat control (flat10) passed on 26 September.
