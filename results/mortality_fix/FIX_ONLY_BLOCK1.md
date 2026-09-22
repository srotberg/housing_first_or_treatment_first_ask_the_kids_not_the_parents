# The fix-only test, block 1: the sign flips and lambda_d lands on target

22 September 20:56. The clean run the void diagnostic should have been:
`seeds/PARAM_HANDOVER_bm_n90repro.txt`, benchmark switches verified IN THE RUN'S
OWN LOG before anything was read off it, warm started from the archive
benchmark (md5 c35f79f5..., `sum= 50.861206888360229`), patched survival, no
parameter moved.

    HANDOVER voucher_conditional_on_clean                       0 -> 0
    HANDOVER include_voucher_exclusion                          0 -> 0
    HANDOVER increased_prob_of_voucher_if_homeless_and_addicted 1 -> 1
    HANDOVER adjust_taxes                                       0 -> 0

## The result, block 1, BLOCK MOVE 1.0000 against a rule of 1e-4

                        reference    block 1     target
    SUD | SMI            0.02043     0.08923       --
    SUD | non-SMI        0.03428     0.04127       --
    ratio                0.596       2.162         --
    lambda_d aggregate   0.033609    0.043591    0.043424
    b        users       ~0.1038     0.10891     0.10502

`lambda_d` was the drug block's worst miss at 23 per cent below target. It is
now 0.4 per cent off, with no parameter moved. `b` goes from about one per cent
low to 3.7 per cent high.

## THE MECHANISM IS NOT THE ONE THE AUTHOR PROPOSED, AND THE TEST SAYS SO

The author, 22 September: *"smi lowers the value of life through unemployment and
they use more"*. That is the channel the model was expected to reveal. It is not
what moved. SUD by employment state, before and after:

    employment    SUD|SMI before/after   SUD|non before/after   ratio b/a   mass SMI
    state 1        0.0186  ->  0.0851     0.0305 -> 0.0368      0.61 -> 2.31   2.00
    state 2        0.0288  ->  0.1075     0.1194 -> 0.1399      0.24 -> 0.77   0.44
    state 3        0.0216  ->  0.0954     0.0334 -> 0.0399      0.65 -> 2.39   0.02

**The rise is about four fold in EVERY employment state.** An unemployment
channel would concentrate it in the non-employed cell. It does not.

**Even among the employed, SMI now carry SUD at 2.31 times non-SMI**, and that
cell holds 2.00 of the 2.46 SMI mass. Those households have jobs, so it is not
an income story either.

**Among the unemployed the ratio is still 0.77, below one**, because non-SMI
unemployed carry SUD at 0.14: addiction is what cost THEM their jobs. The two
disjoint doors into homelessness survive exactly where they were always
strongest.

What moved is the mortality price directly. Drugs were charged as roughly 2.5
times more lethal for an SMI household than they are, in every state, so SMI
households were over-deterred everywhere; correcting it raises their use
everywhere. For R1 that is a better answer than the income story, because it
needs no new preference, no new parameter and no assumption about the direction
of causality.

## NON-SMI ALSO ROSE, 20 PER CENT, AND THAT WAS PREDICTED WRONGLY

Before the block landed I wrote that non-SMI SUD should be unchanged because the
patch cannot reach non-SMI survival. That was too strong and the run corrected
it. `iota_smi=2.0` means carrying a SUD DOUBLES the hazard of SMI onset, so a
non-SMI drug user faces an elevated chance of arriving in exactly the cell the
old code overcharged. Drug users were over-deterred whether or not they were SMI
yet. The channel is real and it is not small.

## THERE IS STILL NO TARGET, AND 2.162 IS NOT YET A MATCH

The author: *"How do you know the ratio is 2 in the data?"* The answer is that I
do not, and the number had hardened through repetition rather than measurement.
See `data/SMI_SUD_COMORBIDITY_EVIDENCE.md`: the published range is 1.5 to 7.5
and the spread is the definition of SMI, not measurement error. The 2.1 came
from Nesvag's 7.6 per cent drug use disorder in BIPOLAR disorder, Norwegian
registry, converted across definitions onto this model's 0.0368.

`data/NSDUH_2024_SMI_by_SUD_code.txt` computes the real thing --
`svyrdudany` x SMI at `age3>=7`, weighted -- and needs the full public use file,
which this container does not have and samhsa.gov is blocked from reaching.

## What stands regardless of the target

The fix corrects an arithmetic error nobody chose, it moves lambda_d from 23 per
cent below target to 0.4 per cent off, and it turns the comorbidity from the
wrong sign to the right one. What the target decides is only whether a CHANNEL
is needed on top.
