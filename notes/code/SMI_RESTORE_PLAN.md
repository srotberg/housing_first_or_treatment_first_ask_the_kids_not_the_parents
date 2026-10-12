# THE RUN ORDER, AS THE AUTHOR SET IT ON 23 SEPTEMBER

## THE MODEL IS SETTLED

    zeta_DI          0        UI for SMI stays at zero
    b_smi_multiple   1.0      b_smi = b, NO SMI-specific drug preference
    iota_smi         2.0      a SUD raises the hazard of SMI onset  (Nielsen 2017)
    mu_m             0.82     SMI lowers the SUD recovery hazard    (Bradizza 2006)
    child_penalty_classes  2
    penalty_child_addicted 0.24

`zeta_DI` and `b_smi_multiple` are ALREADY at those values as declared values in
the shared source, so they need no change. `iota_smi` and `mu_m` are both at 1.0
and have to be restored to the values git records before 875750f4 made SMI
exogenous.

**`mu_m` ALSO HAS TO BE WIRED OR IT IS DECORATION.** Eleven of fifteen call
sites drop its optional argument; the four that pass it are all in the
government revenue accounting, so the household's problem and the distribution
have never seen it. Measured: `mu_m` at 0.10 against 1.0 reproduces every cell
to four decimals. `code/patch_wire_mu_m.py` does the wiring and refuses unless
it finds exactly 4 wired and 11 unwired sites. Dry run is clean. NOT APPLIED --
the author stopped it twice and it waits on their word.

## WHY b_smi IS OFF, WHICH IS THE RESULT THAT SETTLED IT

At `b_smi = 1`, with no SMI-specific preference anywhere, the model produces a
drug USE ratio of 2.715 against the data's 2.44. It does not fall short of it;
it overshoots by eleven per cent. **The SMI drug-use gradient is entirely
endogenous** -- SMI lowers employment and income, and poorer households use more
-- so it is a prediction rather than a fitted moment, and the whole b_smi ladder
was driving a moment that was already on target past it, up to 7.82.

The use ratio goes in the UNTARGETED numbers, on the author's instruction.

## THE ORDER

1. **Two calibrations IN PARALLEL**, two classes, `delta_d = 0.24`:
   `omega_c = 0` and `omega_c = 0.055`.
2. **Read the gaps tables.** If they are decent, continue; if not, stop here.
3. **Compute `kappa_x`.**
4. **`omega_c = 1`.**
5. **Full internalisation of homelessness** -- `kappa_x` borne by the homeless.
6. **Treatment First.**
7. **The transition at T = 60.**

## WHAT THE WIRING INVALIDATES, STATED BEFORE IT IS DONE

Every solved point, the benchmark of record and the transition, because the
recovery hazard starts depending on SMI wherever `mu_m` is away from one. At
`mu_m = 1` exactly it is a no-op by construction, which is the control to run
first: wire it, leave `mu_m` at 1.0, and confirm `r_smi` comes back at 1.7792
with `b_smi = 1` before changing any value.
