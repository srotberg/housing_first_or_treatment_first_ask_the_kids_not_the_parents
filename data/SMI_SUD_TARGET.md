# The SMI comorbidity target, computed: 7.30, not 2

22 September 21:05. The author: *"The full data is in the repo!!"* -- and it is,
`data/raw/NSDUH_2024_public_use_file_tab_delimited.zip`, 29.7 MB, 2,632
variables, 58,633 records. I had checked `data/` and not `data/raw/`, and had
been saying for an hour that the figure could not be computed here.

## The computation, and the check that it is the model's own cut

NSDUH 2024 public use file, adults 26 and over (`AGE3>=7`), weighted by
`ANALWT2_C`, SMI from `SMIPY` -- NSDUH's own past-year SMI indicator, blank for
the 12-17s. Drug involvement from `SVYRDUDANY`, the same variable both model
targets are built from.

THE UNIVERSE CHECK PASSES EXACTLY. `SMI_BY_SUD_UNIVERSE.md` requires the
population rates at 26+ to be 0.0890 and 0.0368 before anything below them is
used, because 18+ gives 0.1014 and 0.0454 and is the wrong universe:

    use  = 0.0890      SUD = 0.0368      weighted n = 227,344,798

Both to four decimals. `SVYRDUDANY`'s unweighted cells (1=3517, 2=1785, 3=1631,
4=51700) also reproduce the 17-variable extract exactly, so the extract came
from this file.

## The answer

                                      SMI    non-SMI   ratio
    use  (any DUD incl. mild)       0.34126   0.07570   4.51
    SUD  (moderate or severe)       0.20426   0.02797   7.30
    SUD among USERS                 0.59854   0.36940   1.62

    SMI prevalence 26+ = 0.0501     (model 0.0484)

## THE TARGET IS 7.30 AND THE GAP IS AT ENTRY

The "about 2" this session had been repeating is wrong by a factor of 3.6. It
came from secondary summaries of NSDUH on a BROAD SUD definition -- alcohol
included, adults 18+ -- where the base rate is roughly three times higher and
the ratio is compressed. `SMI_SUD_COMORBIDITY_EVIDENCE.md` said that figure was
not on the model's denominator and should not be used as one; it was used
anyway, in chat, until the author asked how it was known.

The decomposition is exact, because the two ratios multiply:

                  entry ratio  x  persistence ratio  =  SUD ratio
    data             4.51             1.62               7.30
    model, fix-only  0.78             2.78               2.16

**The model has SMI households STARTING to use less than everyone else, 0.78,
when the data says they start 4.5 times more.** It then compensates with too
much stickiness: 2.78 against 1.62. Entry needs to rise about 5.8 fold and
persistence to FALL about 1.7 fold.

## What this settles

**The mortality fix is not enough.** It moved the SUD ratio 0.596 -> about 2.1
against a target of 7.30 -- roughly a quarter of the way, and worth having,
since it corrects an arithmetic error and needs no new parameter. A channel is
still needed.

**The author's instrument was the right one.** `b`, `addiction_scalar_1`, is
bracketed on participation, which is exactly the margin that is missing. An
SMI-specific `b` answers to the use ratio 4.51 -- which is the pairing
`FIX_ONLY_BLOCK1.md` argued for on the model's own instrument assignment,
before the target was known.

**The "they get stuck" reading is wrong as a description of the data**, and it
was stated in chat as though it were a finding. In the data SMI users are 1.62
times more likely to carry a disorder; the model already produces 2.78. If
anything `mu_m=0.82` is too strong, not too weak, and the recovery-side routes
in `results/smi_comorbidity/WHAT_TO_ADD.md` are pushing on the margin that is
already overdone.

## Reproducing it

    cd /tmp && unzip -q <repo>/data/raw/NSDUH_2024_public_use_file_tab_delimited.zip
    # columns: 3 ANALWT2_C, 10 AGE3, 1723 SVYRDUDANY, 2191 SMIPY
    # restrict AGE3>=7, drop blank SMIPY, weight by column 3

The zip's header mangles the underscore in `ANALWT2_C` to `ANALWT2+AF8-C`, so
match the weight by position, not by name.

## CORRECTION 21:30: THE PERSISTENCE RATIO IS NEARLY RIGHT

The decomposition above compared the model's MILD-ONLY rate against the data's
ALL-USE rate, which is not like for like. The data's `use` counts everyone with
at least a mild disorder, so the model's equivalent is block 1 PLUS block 2.
Redone:

                    use ratio   persistence ratio   SUD ratio
        data           4.51           1.62             7.30
        model          1.39           1.47             2.04

    model: use  SMI 0.13470 non 0.09678 -> 1.392
           SUD  SMI 0.09889 non 0.04845 -> 2.041
           persistence 0.7342 / 0.5006  -> 1.467,  1.392 x 1.467 = 2.042

**The model's persistence ratio is 1.47 against a data value of 1.62.** It is
very nearly right. The claim above that the model over-does persistence at 2.78,
and the inference that `mu_m=0.82` is too strong, are both WITHDRAWN -- they came
from the mismatched comparison.

**The whole of the comorbidity gap is the USE ratio, 1.39 against 4.51.** That
makes the instrument unambiguous rather than merely indicated:
`addiction_scalar_1` is bracketed on participation and participation is the only
margin that is wrong. The recovery-side routes in `WHAT_TO_ADD.md` would push on
a ratio that is already close.

## AND ON "IT WOULD IMPLY A USE RATE OF ABOUT 70 PER CENT"

The author, 21:28. That is the SUD ratio applied to use: 7.30 x 0.0890 = 0.650.
The two margins have different ratios and the SUD one already contains the
progression difference. The implied use rate is 4.51 x 0.0757 = 0.341.

34 per cent of SMI adults carrying at least a mild drug use disorder is high but
internally consistent: NSDUH's own `SMISUD5ANY` puts 44.5 per cent of SMI adults
on ANY substance use disorder including alcohol, leaving about 10 points for
alcohol-only, which is the ordinary pattern.

## THE SEVERITY GRADIENT, 21:32 -- why 7.30 is not an artefact, and is conservative

The author, twice: *"It seems way too high"*, *"I still think the 7.3 seems
ridiculous"*. The obvious way it could be junk is that NSDUH's SMI is PREDICTED
from K6 distress and WHODAS impairment rather than diagnosed, and heavy drug
users score high on both -- so drug use could be manufacturing the SMI
classification. That would show up as a jump at the SMI boundary.

It does not. `MICATPY` gives the four-rung ladder, adults 26+, weighted:

    mental illness   share     use      SUD    SUD vs none
    none             78.0%   0.0525   0.0160      1.00
    mild             10.9%   0.1494   0.0613      3.83
    moderate          6.1%   0.2404   0.1217      7.61
    serious           5.0%   0.3413   0.2043     12.77

Each step up in severity roughly DOUBLES the SUD rate, monotonically, on both
margins. That is a dose-response, not a boundary artefact.

**AND 7.30 IS THE CONSERVATIVE SUMMARY.** It compares SMI against everyone else,
and everyone else contains 38 million adults with mild or moderate mental
illness running at 3.8 and 7.6 times the clean baseline. Against adults with NO
mental illness the ratio is 12.77.

7.30 is nonetheless the right target for THIS model, because the model carries
one binary SMI state at about 5 per cent and its non-SMI group pools none, mild
and moderate exactly as that ratio does.

The surprising number is not 7.30. It is that 1.6 per cent of adults with no
mental illness carry a moderate or severe drug use disorder against 20.4 per
cent of those with serious mental illness.

## EVERY CHECK ON 7.30, AND WHERE THE REAL PROBLEM IS

The author pushed back three times -- *"way too high"*, *"ridiculous"*,
*"implausible"*. Everything checkable about the number has now been checked and
none of it moves:

    universe            reproduces 0.0890 and 0.0368, the target's own source
    missing SMI at 26+  none, 0 records
    cell counts         418 SMI with mod/severe, 1146 non-SMI -- not thin
    severity gradient   0.0160 / 0.0613 / 0.1217 / 0.2043 across none, mild,
                        moderate, serious: monotone, not a boundary jump
    NSDUH's own var     SMISUD5ANY puts 44.5% of SMI on ANY SUD, consistent
    external            TEDS-A 2022, in data/FINDINGS.md: 43.1% of treatment
                        admissions carry a co-occurring psychiatric problem,
                        against an implied 27.8% population share -- right
                        order, right direction for a severity-selected sample

**THE CODING IS NOW VERIFIED FROM THE DATA, NOT FROM A COMMENT.** Everything
rested on the Fortran's claim that `svyrdudany in (2,3)` is moderate-or-severe.
Cross-tabulated against the per-drug severity variable `IRPYSEV5MRJ`:

    svyrdudany=1  ->  2575 at marijuana severity 1, none higher
    svyrdudany=2  ->  1488 at severity 2
    svyrdudany=3  ->  1133 at severity 3
    svyrdudany=4  ->  no drug disorder at all

`SVYRDUDANY` is the MAXIMUM severity across drugs, ordered 1 mild, 2 moderate,
3 severe, 4 none. The Fortran's reading is right.

## SO THE DISCOMFORT IS NOT ABOUT THE DATA. IT IS ABOUT WHICH SMI

`DATA_APPENDIX.md` already records that the model is incoherent here, and this
is where an implausible-feeling implication actually comes from:

    s_m(j)       matched to NSDUH's SMI, 5.6 per cent; the model delivers 4.86
    kappa_uem    deliberately NOT NSDUH's SMI -- set to 30 per cent employment
                 from the clinical high-disability literature, BECAUSE on
                 NSDUH's own definition 58.0 per cent of those with SMI are
                 employed against 57.5 per cent of those without

The model takes its SMI POPULATION from NSDUH and its SMI SEVERITY from the
schizophrenia literature. Pick one and the rest follows:

    SMI = NSDUH's SMI          ratio 7.30, concentration 27.8%, and kappa_uem
    (what the prevalence       needs rethinking
     target already commits
     the model to)

    SMI = high-disability      ratio nearer 10 (Hunt's schizophrenia figure) but
    (about 1 per cent)         at 1 per cent prevalence the concentration falls
                               to roughly 9 per cent, and the PREVALENCE target
                               has to change

The second is the coherent version of the objection. It is a legitimate choice.
It is not the one the model is currently calibrated to, and taking it means
moving `s_m(j)`, not the comorbidity target.

## `b` IS LABELLED "TOTAL DRUG USERS" AND MEASURED AS A DISORDER

Found 21:47 answering the author's *"Or are you saying that about 1 in 4
uses..."*. It is not about SMI at all and it is worth settling on its own.

Adults 26+, weighted, four different objects:

                                    SMI    non-SMI   ratio   population
    USED any illicit, past year   0.5640   0.2309    2.44      0.2476
    USED excl. marijuana          0.2832   0.0755    3.75      0.0859
    any DRUG use disorder         0.3413   0.0757    4.51      0.0890   <- b
    moderate/severe DUD           0.2043   0.0280    7.30      0.0368   <- lambda_d

`b` is called "total drug users" in the Fortran and sourced from `svyrdudany in
(1,2,3)`, which is ANY DRUG USE DISORDER, not use. **Past-year use of an illicit
drug other than marijuana is 0.0859 against `b`'s 0.0890** -- the same number to
within four per cent, so the LEVEL is defensible under either reading and
nothing in the existing calibration is wrong because of this.

But they are not the same object and the SMI ratio differs:

    if b means non-marijuana USE          SMI target ratio 3.75
    if b means any drug USE DISORDER      SMI target ratio 4.51

It also bears on `theta`, drug spending over income across users, whose
denominator is whoever `b` counts.

DSM-5 matters here and explains why these rates feel high against older figures.
The variable names carry the edition -- `IRPYUD5MRJ`, `IRPYSEV5COC` -- and NSDUH
switched in 2020. DSM-5 counts "mild" at two criteria where DSM-IV required an
abuse or dependence syndrome, and population SUD on this file is 16.4 per cent
for adults 26+ against roughly 7 per cent on the older criteria. The familiar
"1 in 4 adults with SMI has a co-occurring SUD" is a DSM-IV era statistic; the
DSM-5 figure for the same quantity is 44.5 per cent.

## A CALCULATION THAT ALMOST WORKS, AND WHY IT DOES NOT

The author, 21:52: *"if we have a ratio of 2 and drug use is what the 1 in 5
means, then 8.9*2=17.9 which is almost exactly the rate in the data for smi"*.

    proposed   8.9%  x 2.00 = 17.8%      data SMI moderate/severe 20.4%
    correct    3.68% x 5.55 = 20.4%

Two errors that nearly cancel. 8.9 per cent is the base for ANY drug use
disorder while 20.4 per cent is the MODERATE/SEVERE rate, so the base is 2.4
times too high; and the ratio that multiplies a POPULATION rate is 5.55, not the
7.30 quoted against non-SMI and not the model's 2.0, so the ratio is 2.8 times
too low. 2.4 x 0.36 = 0.87, and 17.8/20.4 = 0.87.

## THE LIKE-FOR-LIKE COMPARISON, WHICH IS BETTER NEWS THAN THE RATIOS

Rescaling the model to its target aggregate, which is what a refit does:

    lambda_d margin        SMI     non-SMI   aggregate
    model as it stands    0.0983    0.0480    0.0505
    model rescaled        0.0717    0.0350    0.0368
    data                  0.2043    0.0280    0.0368
                        SMI 0.35x  non 1.25x

Once the level is refitted the NON-SMI side is roughly right, at 1.25 times the
data, and essentially the whole remaining gap is the SMI group, which has to
roughly triple. One parameter, one margin, one group.

---

# EXCLUDING MARIJUANA RAISES THE RATIO, IT DOES NOT LOWER IT. COMPUTED 23 Sep

The author asked what the SMI SUD ratio is excluding marijuana, expecting it to
come in below 7.30. It comes in ABOVE.

`SVYRDUDANY` is the maximum severity across the drug components, and the
components are separately available, so the object can be rebuilt without
marijuana. Rebuilt WITH marijuana first, as the validation:

    object, adults 26+, weighted        SMI   non-SMI   ratio   population
    any DUD  (SVYRDUDANY, published) 0.3413    0.0757    4.51      0.0890
    mod/sev  (SVYRDUDANY, published) 0.2043    0.0280    7.30      0.0368
    any DUD  rebuilt                 0.3413    0.0757    4.51      0.0890
    mod/sev  rebuilt                 0.2043    0.0280    7.30      0.0368
    any DUD  EXCLUDING marijuana     0.1749    0.0299    5.86      0.0371
    mod/sev  EXCLUDING marijuana     0.1034    0.0114    9.06      0.0160

The rebuild reproduces the published figures to four decimals in every cell,
which is what licenses the exclusion. Components used: IRPYSEV5MRJ, COC, HER,
HAL, INH, MTH and SVYRPSYANY, taking the largest value in {1,2,3} and treating
4 as none; weights ANALWT2_C, universe AGE3 >= 7.

**Marijuana use disorder is common in the NON-SMI population and dilutes the
denominator.** Drop it and the non-SMI rate falls from 0.0757 to 0.0299 while
the SMI rate falls from 0.3413 to only 0.1749, so the ratio rises.

## THE LEVEL CHECK THAT FIXES WHICH OBJECT `lambda_d` IS

`lambda_d`'s target is 0.043424 and the data's moderate/severe rate INCLUDING
marijuana is 0.0368:

    0.043424 / 0.0368 = 1.180

which is exactly the eighteen per cent uplift the author specified on
22 September. So the model's SUD state is the MODERATE/SEVERE cut with
marijuana IN, and the data ratio that matches it is **7.30**. An earlier
suggestion in this session to score it against 4.51 was wrong: 4.51 belongs to
the 0.0890 population rate, which is a different model object.

The author's decision, 23 September: **keep marijuana in.**

---

# THE AUTHOR'S CHOICE, 23 September: 2.44 FOR USE AND 2.98 FOR THE DISORDER

All eight cuts, computed from the repo's own NSDUH 2024 file, adults 26 and
over, weighted by ANALWT2_C, universe AGE3 >= 7:

    object                              SMI   non-SMI   ratio   population
    used any illicit, past year      0.5640    0.2309    2.44      0.2476  <-
    any SUD, INCLUDING alcohol       0.4454    0.1493    2.98      0.1641  <-
    used excl. marijuana             0.2832    0.0755    3.75      0.0859
    any DUD, drugs only              0.3413    0.0757    4.51      0.0890
    mod/severe SUD, incl. alcohol    0.2833    0.0576    4.92      0.0689
    any DUD, excl. marijuana         0.1749    0.0299    5.86      0.0371
    mod/severe DUD                   0.2043    0.0280    7.30      0.0368
    mod/severe DUD, excl. marijuana  0.1034    0.0114    9.06      0.0160

The two marked rows are what the paper reports against. The reading is that the
model's single addictive good stands for substance use broadly rather than for
one illicit drug, which is what licenses the alcohol-inclusive disorder ratio.

**MODEL AGAINST THEM.** `r_smi` is 2.0610 at `omega_c = 0.055`, two classes,
`iota_smi = 2.0` and `mu_m = 0.82` wired -- **31 per cent short of 2.98**. The
use ratio is being measured and scores against 2.44.

## WHAT A REFEREE WILL CHECK, RECORDED SO IT IS NOT A SURPRISE

The LEVELS do not line up with those two rows, and they do line up with two
others:

    model object            target      data row                level   ratio
    total drug users       0.10502      used any illicit       0.2476   0.42x
    SUD (lambda_d)         0.043424     any SUD incl. alcohol  0.1641   0.26x

    total drug users       0.10502      any DUD                0.0890   1.180x
    SUD (lambda_d)         0.043424     moderate/severe DUD    0.0368   1.180x

The second pair reproduces the eighteen per cent uplift the author specified on
22 September, on BOTH objects independently, which is the arithmetic that says
the calibration's levels were set against the drugs-only cuts with marijuana
in. Scoring the ratio against 2.44 and 2.98 while the levels were set against
0.0890 and 0.0368 is a deliberate choice, not an oversight, and the ratio
comparison is sound on its own terms.

Against the level-consistent pair the model would be 72 per cent short rather
than 31.
