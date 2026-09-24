# THE AUTHOR'S TREATMENT FIRST, AND WHY TONIGHT'S RUN WAS NOT IT, 24 September 03:41

The author, asked which Treatment First is the paper's: *"TF should test everyone
who has a voucher! not just the homeless. And if you fail, you are not eligible
for an average of 3 years. And false negative occurs at a rate of 30%. Also, no
false positive."*

That is EXACTLY arm 3 of 19 September (`code/results/arm3/RESULTS.md`):

    voucher_conditional_on_clean 1     include_voucher_exclusion 1
    probability_of_detection 0.70      probability_of_false_positive 0.0
    increased_prob_of_voucher_if_homeless_and_addicted 0

Tonight's TF run departed from it in FOUR ways, three of them mine: it carried
the base handover's detection 0.95, false positive 0.005 and exclusion 0,
because I briefed it from the declarations at 487/488 -- the rule "never quote a
parameter from its declaration" broken in a new form. The spec lived in the arm-3
handover, not in the declaration or the scan seed. The fourth, the dead housed
branch, is the path.

Relaunched as universal TF in session_01SAVKzK7R5g1BkxS2G1KnmK: the arm-3 lines
by handover, the two guards (32257, 32381) removed by sed into a build directory,
frozen_stop_after_blocks 12, kappa_x 0.9329. The entry-only result stays,
labelled.

## THE DOOR IS A BAN, NOT A TEST

With increased_prob_of_voucher_if_homeless_and_addicted = 0, the offer to a
category-3 applicant is

    voucher_probabilities(0,1,1,3) = (1-probability_of_detection) * min(prob * 0, 1) = 0

so detection never enters at the door: an applicant who uses is refused with
certainty, and "uses" is drug_share > 0, any use at all. The 30 per cent false
negative bites only on HOLDERS. Arm 3 was built the same way. Put to the author,
not changed.

## PENDING, WHEN NO SOLVE IS RUNNING

The paper's p_det and p_fp are generated from the Fortran declarations, which
still read 0.95 and 0.005 (lines 487, 488). They must become 0.70 and 0 to match
the author's ruling. The guard removal at 32257 and 32381 should go into the
tracked source at the same time. Both are inert for every non-TF run.

