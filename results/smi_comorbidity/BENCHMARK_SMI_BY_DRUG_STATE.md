# SMI by drug state in the benchmark, read off the stationary distribution

22 September. The author asked for "the prevalence of drug use (but no sud) for
those with SMI relative to the entire population and ... the rate of SUD for
those with SMI as well", then asked why it could not be seen in the benchmark.
It could. This is read from `distribution_stationary{1,2}baseline_benchmark.dat`
in five seconds, with no model change and without touching the running solve.

## How the file decodes, and why the decode is trusted

`vector_real(age, financial, unemployment, employment, housing, voucher)`,
Fortran column major, one value per line in F30.28 so 31 bytes a line.

    file 1 (renters) 61 x 25 x 18 x 26 x 4 x 3 = 8,564,400  = 265,496,400 / 31
    file 2 (owners)  61 x 27 x 18 x 26 x 1 x 1 =   770,796  =  23,894,676 / 31

Both factor exactly, which pins the bounds: financial runs 3..27 for renters,
not 1..27, because `renter_array_floor=3`.

Age and financial vary fastest, so the unemployment index of a flat position is
`(pos / (n_age * n_fin)) mod 18`, and both SMI and SUD live in that one index:
`i-1 = employment + 3*(SMI + 2*addiction_block)`, which reproduces `smi_of`
and puts the SUD block at i=13..18 against `threshold_addiction_index=12`.

FOUR MARGINALS CONFIRM IT, each against a number the model printed itself:

    SMI prevalence   0.048291     model 0.048291
    total mass      50.861207     model 50.861206888360229
    SUD mass         1.709418     model 1.7094186790049224
    SUD rate         0.033610     model lambda_d 0.033609752

## The result

                            SMI      non-SMI    ratio
    homeless rate         0.03330    0.00503     6.61
    SUD rate              0.02043    0.03428     0.60
    SUD | homeless        0.04028    0.23313     0.17
    SUD | housed          0.01974    0.03327     0.59

SMI households carry SUD at 60 per cent of the population rate. LESS, not more,
which is the opposite of the data and the opposite of what the author predicted
from their low income and high unemployment.

## Why, and it is not what I first said

My first explanation was mortality -- kappa_phi_m=2.5 emptying the comorbid cell
by killing it. That is wrong. The third row is the mechanism: among the
HOMELESS, SMI households have SUD at 4.0 per cent against 23.3 for non-SMI
homeless, nearly six times less.

THE MODEL HAS TWO INDEPENDENT DOORS INTO HOMELESSNESS AND NO DOOR BETWEEN THEM.
An SMI household reaches the street through low employment; a non-SMI household
reaches it through addiction. They are substitute causes, so conditioning on
homelessness makes SMI and SUD negatively related, and because homelessness is
where SUD concentrates the unconditional rate inherits the sign. Nothing carries
SMI into addiction, so the SMI homeless arrive clean and stay clean.

    SMI=1 SUD=1 homeless=1   mass 0.003294 of 50.861

The comorbid homeless, who are what this policy debate is about, are six
thousandths of one per cent of the model's population.

## What it means for R1

R1 wrote that mental health is "largely absent from the model" and that mental
health "contributing to drug use and addiction as well as homelessness would
weaken TF dramatically". The model does not merely omit the link: it produces
one with the WRONG SIGN. That is his criticism located exactly, and it says what
a fix must do -- adding self-medication to preferences is not enough, because
the binding problem is that the SMI-homeless and the SUD-homeless are disjoint
populations. A channel has to put SMI households at risk of addiction GIVEN the
circumstances they land in.

## The one caveat

The housing split is INDICATIVE, not confirmed. My homeless mass is 0.32547
against the model's printed 0.39003, and SMI share of homeless 0.25128 against
0.23612. That is probably a denominator difference -- the model's line carries
`mass_all= 37.914862` beside it while the distribution sums to 50.861207, so it
is printed over a subpopulation -- but it is not proven, and no printed figure
shares my denominator. The SMI x SUD result does not depend on housing and
rests on the four exact marginals above.
