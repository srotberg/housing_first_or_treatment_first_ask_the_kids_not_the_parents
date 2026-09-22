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
