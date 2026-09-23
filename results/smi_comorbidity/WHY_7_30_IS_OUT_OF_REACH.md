# THE AUTHOR WAS RIGHT: SOME SMI HOUSEHOLDS CANNOT BUY THE DRUG AT ANY PRICE

`b_smi_multiple = 1e-12`, frozen, cold, block 1. The shifter is 4.9e-15 and an
abstaining SMI household's Cobb-Douglas factor is `b^-phi_q` = 230 against 1.37
for one buying the usual quantity: **abstaining is 170 times worse than using**,
and the run is clean -- no `NaN`, no `Infinity`, homelessness 0.0084.

    SUD | SMI      0.2275      SUD | non-SMI   0.0567      r_smi   4.0140
    users + experimenters (population)                     0.16751
    SMI population share                                   0.045893

## THE PREDICTION FAILED, AND THE WAY IT FAILED IS THE ANSWER

`B_ZERO_PREDICTION.md` said `r_smi` near 6.2 if every SMI household that can buy
does, and set out beforehand what a result near 4 would mean: *a large share of
SMI households cannot buy at any price, which is the author's hypothesis*.

It came out at 4.01. Decomposing with `r_smi = u_SMI/u_non`, which holds because
onset is flat at 0.0336 for any positive quantity and recovery carries no SMI
term:

    u_non   0.14715        u_SMI   0.59066        k = onset/(onset+exit)  0.3852

`k` lands where it was predicted, 0.385 against 0.393. **`u_SMI` does not.** It
was 0.588 at `b_smi_multiple = 1e-5` and it is 0.591 at 1e-12 -- SEVEN DECADES
of `b`, and the share of SMI households buying anything does not move.

**Forty one per cent of SMI households buy nothing while abstaining costs them
170 times what using would.** A preference trade-off does not do that. A
constraint does, and the only constraint available is that they have nothing to
spend.

## WHAT THE CEILING WOULD BE IF THEY COULD BUY

If `u_SMI` reached one, `r_smi` would be `1/u_non` = **6.8** and `SUD | SMI`
would be `k` = 0.385. A ratio of 7.30 needs `SUD | SMI` at 0.46. So even with
every SMI household using, the onset and exit hazards still cap it below the
target -- but at 6.8 rather than 4.0, and the remaining gap is small enough that
the non-SMI rate, which runs at 0.0567 here against 0.034 in the data, closes
it.

## SO THE AUTHOR'S NEXT QUESTION IS THE RIGHT ONE, AND THE LEVER ALREADY EXISTS

*"the question to ask is if they should be given a bit of income"*. The model
has exactly that parameter and it is set to zero:

    real(8) :: zeta_DI=0.d0
    ! EXTERNALLY SET AND ZERO, ON THE AUTHOR'S WORD: "DI replacement is 0",
    ! 13 September.

A non-employed household with SMI draws NO disability insurance. The long note
at 2255 explains the choice -- roughly three in thirteen actually draw DI and
the other ten draw nothing, `zeta_DI` is a single expected payment, so any
positive value gives all thirteen a floor that ten do not have -- and it names
the cost of the zero in the terms this run has just measured:

    the ten who get nothing are the ones who fall to zero income and lose
    their housing, and a mean-field floor hides exactly that margin

## THE DIAGNOSTIC THAT IS RUNNING

`di_probe`: identical to `sw_1e5` except `zeta_DI = 0.25`, the value the paper
declares and reports against. Reference stated before the run, from `sw_1e5`
block 1 at `zeta_DI = 0`:

    r_smi 4.0094    SUD|SMI 0.2278    SUD|non-SMI 0.0568
    u_SMI 0.588     u_non 0.161

If `u_SMI` rises and `r_smi` with it, affordability is confirmed as the binding
constraint and the modelling question is the author's: a mean-field `zeta_DI`,
or the permanent binary DI state the source writes down at 2277 -- 3/13 awarded
at 0.25 for as long as they stay ill, nothing forever otherwise -- which is the
object `zeta_DI` averages over and costs one more dimension. If `r_smi` does not
move, affordability is not it either and the search reopens.

## THE `Infinity` IN THESE LOGS IS BENIGN, AND HERE IS THE FAULT SIGNATURE THAT IS NOT

Grepping a log for `Infinity` flags every healthy run in this configuration.
`model_average_rental_unit_size(1)/model_average_owner_occupied_unit_size(1)`
divides by zero because homeownership is switched off, so the line prints
`Infinity` as a matter of course: four times in `sw_1e5`, four in `sw_0001`,
once in `sw_02`, once in `b0_1e12`.

The signature that actually distinguishes the void `b_smi = 0` point from every
valid one is

    model_value_of_life(1)=                       NaN

which appears once in `b0_0` and in NONE of `sw_1e5`, `b0_1e12` or `di_probe`.
Watch that, and `VALUE OF LIFE FLOOR BINDS ... -Infinity`, not the word
`Infinity` on its own. `b0_1e12`'s 4.0140 is clean.
