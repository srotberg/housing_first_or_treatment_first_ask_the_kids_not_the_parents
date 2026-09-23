# GIVING NON-EMPLOYED SMI HOUSEHOLDS DI INCOME DOES NOT MOVE THE COMORBIDITY
# RATIO -- AND THE REASON POINTS SOMEWHERE MUCH MORE INTERESTING

`di_probe`: identical to `sw_1e5` in every respect except `zeta_DI = 0.25`
instead of 0. Clean run -- no `NaN`, no backtrace, homelessness 0.0063. Both
read at block 1.

                              zeta_DI = 0      zeta_DI = 0.25
    SUD | SMI                      0.2278            0.2278
    SUD | non-SMI                  0.0568            0.0581
    r_smi                          4.0094            3.9230
    users + experimenters          0.18077           0.17055
    SMI population share           0.047             0.04603

**`SUD | SMI` does not move at all.** The ratio falls by two per cent, and it
falls because the DENOMINATOR rises -- a general equilibrium effect on non-SMI
households, not an effect on the treated group. Backing out the shares as
before gives `u_SMI` = 0.590 against 0.591 without the income. Nothing.

## WHY THE LEVER MISSES, AND IT IS NOT THAT THE HYPOTHESIS IS WRONG

DI is paid to NON-EMPLOYED households with SMI. In this model,

    MOMENT kappa_uem  employment given SMI   model= 0.80826   target= 0.30000

**Eighty one per cent of SMI households are employed, against thirty in the
data.** So `zeta_DI` reaches at most a fifth of them, and the households that
do not buy the drug are overwhelmingly ones with wage income already. Raising a
transfer that four in five of them cannot claim was never going to move the
share who buy.

`kappa_uem`'s adjuster is zero. It is HELD, and its moment is out by a factor
of 2.7 -- the largest miss in the SMI block by a wide margin, and larger than
anything `b_smi` was ever going to close.

## SO THE LEAD IS EMPLOYMENT, NOT PREFERENCES AND NOT TRANSFERS

The only route from SMI to a SUD left in this model is the endogenous one:
SMI lowers employment and income, and poorer households use more. That route is
being fed an SMI employment rate of 0.81 when the data says 0.30. A household
that is employed four times more often than its counterpart in the data is a
household with four times too little of the disadvantage the channel runs on.

This is also the referee's point, in the model's own numbers. The concern was
that households with SMI do not respond enough; the model currently has them
barely worse off in the labour market at all.

## THE CAVEAT ON THE DECOMPOSITION, STATED RATHER THAN BURIED

`u_SMI` and `u_non` are backed out of `r_smi = u_SMI/u_non`, which assumes both
groups share `k = onset/(onset+exit)`. Onset is common -- it is flat at 0.0336
for any positive quantity and carries no SMI term. Exit is NOT obviously
common: recovery is harder on the street, and SMI households are over
represented among the homeless, so `k_SMI` may exceed `k_non` and `u_SMI` would
then be SMALLER than 0.59. That would make MORE of the ratio come from the
hazards and LESS from who buys, and it does not change either measured fact --
`SUD | SMI` is flat across seven decades of `b` and flat again when DI income
is switched on.

Pinning it needs the exit hazard by SMI, which is not printed. That is a
one-line diagnostic, not a solve.
