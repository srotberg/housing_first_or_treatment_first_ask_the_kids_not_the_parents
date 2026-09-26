# The flat control: a transition with no reform stays flat. PASSED, 26 September 20:05

The control `code/stylized/TRANSITION_LESSONS.md` section 16 asked for before any transition
number is believed. T = 10, no grandfathering, built by scratchpad build_tr10_fix.sh (the
section-16 fixes: every per-period stopping test at the steady state's own rule, the budget at
1e-3, pi_V's first step 0.12, and the initial steady state's parent share restored at t = 1 of
every loop). Both end points are the no-policy steady state on the corrected build
(../../counterfactuals_cf_fix2/null_share): its value functions and prices at T, its distribution
at t = 0, its parent share at t = 1, its own net revenue 6.0371582079 as the budget target, and
the budget test switched on (adjust_taxes 1).

Start-up, from the log: the initial parent share read (disordered housed 0.027986) and
restored at t = 1 of loop 0; price and pi_V seeds read 9 of 9; constraint 6.0371582079130.

It stopped after loop 0 with every per-period rule met: largest budget residual 1.07e-4 (rule
1e-3), drug market at most 1.6e-4 (rule 5e-3), housing and rental 0.

Against the steady state (`table.txt`):

      t   h_1 chg     b chg    SUD chg   drug price    pi_V       welfare    vs SS (utils)  budget residual
      1   +0.0000%   +0.0001%   +0.0001%   1.0000321  0.06753386  789.35833  +0.00007   -1.14e-06
      2   +0.0003%   +0.0171%   -0.0043%   1.0000321  0.06753386  789.35812  -0.00014   -1.28e-05
      3   +0.0406%   +0.0016%   -0.0023%   1.0000321  0.06753386  789.35720  -0.00106   -2.30e-05
      4   -0.0112%   -0.0011%   -0.0016%   1.0000321  0.06753386  789.35830  +0.00004   -5.05e-05
      5   +0.0054%   -0.0010%   -0.0041%   1.0000321  0.06753386  789.35797  -0.00029   -7.80e-05
      6   +0.0003%   +0.0106%   -0.0036%   1.0000321  0.06753386  789.35783  -0.00043   -8.02e-05
      7   -0.0045%   +0.0110%   -0.0033%   1.0000321  0.06753386  789.35778  -0.00048   -8.81e-05
      8   -0.0036%   +0.0113%   -0.0020%   1.0000321  0.06753386  789.35778  -0.00048   -1.07e-04
      9   +0.0029%   +0.0002%   -0.0008%   1.0000321  0.06753386  789.35780  -0.00046   -1.04e-04

Welfare stays within 0.0011 utils of the steady state (about 0.003 per cent of CEV; 1 per cent is
about 0.338 utils) in every period, and at t = 1, the number a transition reports, within 0.00007.
The drift that remains is the size a steady state solved to 5e-5 per sweep produces when it is
advanced one sweep per period, and it is about 500 times smaller than Treatment First's long-run
effect (+1.42 per cent).

Not tested here: whether pi_V and the price move correctly when they must, which only a reform
path exercises. The loop exited before either was updated.
