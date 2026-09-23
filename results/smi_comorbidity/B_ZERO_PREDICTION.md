# PREDICTION BEFORE THE RUN: WHAT `b_smi = 0` SHOULD GIVE, AND WHAT EACH
# OUTCOME WOULD MEAN

Written 23 September 02:48, BEFORE the two points were launched, because
ENGINE.md's corollary for controls is that the reference value is stated first.

The author's argument: at `b_smi_multiple = 0` the Stone-Geary shifter is zero,
flow utility is Cobb-Douglas in `(b+v)`, so an SMI household choosing `v = 0`
has flow utility of minus infinity. Abstaining is then infinitely costly and
every SMI household that CAN buy the drug will. If the ratio still misses 7.30,
the households that do not buy are households that cannot -- no income and no
assets -- and the modelling question becomes whether they should be given some.

## THE ARITHMETIC THAT MAKES IT A TEST

Onset is `min(base + (1-exp(-lambda*v)), 1)` with `lambda_addiction = 0`, so it
is a FLAT 0.0336 for any positive quantity and exactly zero at none. Recovery
carries no SMI term either, because `mu_m` is one and is not wired in any case.
So for a group whose members buy with share `u`, the stationary disorder rate is
`u * k` with the SAME `k = onset/(onset+exit)` for both groups, and

    r_smi = u_SMI / u_non

At `b_smi_multiple = 1e-5`, block 3, the model gives

    SUD | SMI      0.2311        SUD | non-SMI   0.0631      r_smi  3.66
    fraction addicted + experimenters (population)          0.18077
    SMI population share                                    0.047

Solving those together, `u_non = 0.1607`, `u_SMI = 0.588`, `k = 0.393`.

## SO THE PREDICTION IS

At `b_smi_multiple = 0`, if every SMI household that can buy does, `u_SMI -> 1`
and

    SUD | SMI  ->  k  =  0.393            r_smi  ->  0.393/0.0631  =  6.2

**AND 7.30 IS STILL MISSED, BECAUSE IT WOULD NEED `SUD | SMI` = 0.46 AGAINST A
CEILING OF 0.393.** That ceiling is the onset and exit hazards, not the budget:
a household that uses every year still leaves the disorder at the common
recovery rate, and 0.393 is where those two balance.

## WHAT EACH OUTCOME MEANS

  - **`r_smi` near 6.2.** The binding constraint is the onset/exit steady state
    `k`, not affordability. Getting to 7.30 then needs a higher onset or a lower
    exit for SMI households -- which is the two channels the author has just
    fixed at one -- or a lower non-SMI rate.
  - **`r_smi` well below 6, say still near 4.** A large share of SMI households
    cannot buy at any price, which is the author's hypothesis, and the next
    question is theirs: whether those households should be given some income.
  - **`r_smi` above 6.2.** The common-`k` assumption is wrong somewhere and the
    decomposition above has to be redone before anything is concluded.

Two points are run rather than one: `b_smi_multiple = 0` exactly, which is what
the author asked for, and `1e-12` beside it, because zero makes an abstainer's
flow utility literally infinite and Inf arithmetic can produce a NaN somewhere
downstream. At 1e-12 the penalty on abstaining is finite but 170 times a user's,
which is the same experiment without the singularity. If the two disagree, the
zero point is the one to distrust.

The 1e-6 floor on the handover is removed in a PRIVATE copy,
`code/b0_probe/b0.f90`; the shared source keeps it.
