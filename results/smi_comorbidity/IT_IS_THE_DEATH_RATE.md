# IT IS THE DEATH RATE. THE AUTHOR CALLED IT, AND MAKING SMI HOUSEHOLDS POOR
# DOES NOT FIX IT

The author, 23 September: *"i dont understand how the SUD risk doesnt convert
more of them....maybe it's the death rate?"* It is.

## THE ARITHMETIC

Onset is common -- flat at 0.0336 for any positive quantity, no SMI term -- so
the whole difference in the stationary disorder share among users is EXIT.
Backing exit out of the shares at `b_smi_multiple = 1e-12`:

    exit | SMI users      0.0336*(1-0.22809)/0.22809 = 0.1137
    exit | non-SMI users  0.0336*(1-0.44428)/0.44428 = 0.0420
    gap                                                0.0717

And exit is recovery PLUS DEATH. The model's own survival print at age 40:

    clean and housed            death hazard  0.0128
    SMI, homeless, with SUD     death hazard  0.1127
    gap                                       0.0999

**The mortality gap is the right size to account for essentially all of the
exit gap.** The earlier reading of this file's predecessor -- that SMI users
recover 2.7 times faster, which is backwards from the dual-diagnosis evidence
-- is WITHDRAWN. They are not recovering faster. They are dying.

## THE TEST THAT CLOSES THE POVERTY ROUTE

`uem_probe`: `kappa_uem = 23.5` against 1.0554, everything else identical,
`zeta_DI = 0` on the author's instruction, block 1.

                                        kappa_uem 1.0554   kappa_uem 23.5
    employment given SMI (target 0.30)           0.80731          0.14823
    fraction homeless    (target 0.004)          0.00829          0.01951
    participation, SMI                           0.99752          0.99705
    participation, non-SMI                       0.12759          0.13168
    r_smi                (target 7.30)           4.01404          3.92436

    participation ratio                           7.8182           7.5718
    conditional ratio                             0.5134           0.5183

**Employment given SMI was driven from 0.81 to 0.15 -- past its own 0.30 target
-- homelessness more than doubled, and the comorbidity ratio went DOWN.** The
conditional term moved one per cent. Making SMI households jobless and homeless
buys extra entry into the disorder and an extra death rate that removes them
again, and the two cancel.

So the poverty route is closed as a way to reach 7.30, and with it the last
mechanism that needed no parameter the author has already fixed at one.

## WHAT THE DATA ACTUALLY OFFERS, AND WHY 7.30 IS THE WRONG OBJECT

`data/SMI_SUD_TARGET.md` has four objects at 26+, and the ratio climbs with
severity:

                                     SMI   non-SMI   ratio   population
    used any illicit, past year   0.5640    0.2309    2.44      0.2476
    used excl. marijuana          0.2832    0.0755    3.75      0.0859
    any drug use disorder         0.3413    0.0757    4.51      0.0890
    moderate/severe DUD           0.2043    0.0280    7.30      0.0368

Against the model at `b_smi = 1e-12`:

  - **participation ratio 7.82 against a data USE ratio of 2.44.** The model is
    overshooting differential use by more than three times. `b_smi` has been
    pushed far past anything the data supports, not short of it;
  - **SUD ratio 4.01 against the any-disorder ratio of 4.51** -- within eleven
    per cent.

The model reproduces the ANY-DISORDER ratio and misses the MODERATE/SEVERE one,
and mortality is why. NSDUH measures LIVING RESPONDENTS. A household dying at
11.3 per cent a year is not in the survey. A model carrying honest excess
mortality for SMI with a disorder will systematically undershoot a survey-based
SEVERE prevalence ratio, because the survey cannot see the households the
mortality removed. That is a difference in the objects, not a failure of the
model.

## SO THE THREE THINGS THAT FOLLOW

1. **`b_smi` should be RAISED, not lowered.** At 1e-12 participation runs at
   7.82 against a data use ratio of 2.44 to 3.75. Whatever the disorder target
   becomes, the use margin is badly overshot and it is a moment the data speaks
   to directly.
2. **Score the disorder ratio against 4.51, the any-disorder cut**, unless the
   survival selection is modelled explicitly. The model already sits there.
3. **`mu_m` remains the only lever that reaches 7.30** on the present
   definition, it reopens the recovery decision rather than the risk one, and
   it is unwired at eleven of fifteen call sites. Surveyed, not applied.
