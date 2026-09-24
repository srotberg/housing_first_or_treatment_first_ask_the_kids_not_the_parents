# TREATMENT FIRST IS RERUN WITH APPLICANTS TESTED, 24 September 15:00

The author, on the rationed TF result: *"the rationed TF should be redone with an
average three-year exclusion. ... it should be tested before being rejected. the
false negative should apply to applicants too."*

The exclusion WAS on in the last run (`include_voucher_exclusion 1`, echoed in
the log). It never bound because applicants who use were refused outright, so
nobody was ever caught. With
increased_prob_of_voucher_if_homeless_and_addicted = 0, a failing applicant's
offer is (1-p_det)*min(prob*0,1) = 0, and detection never enters.

At 1, the vcc = 1 block of voucher_probabilities gives exactly the author's rule,
with no Fortran change:

    applicant, fails:  offered 0.30*prob, excluded 0.70*prob, stays out 1-prob
    applicant, clean:  offered prob (no false positives), never excluded
    holder, fails:     keeps 0.30, excluded 0.70 (never straight to 0)
    holder, clean:     keeps 1

A failing applicant is offered at the base rate before the test, which is the
same rate Housing First gives it (the benchmark also carries this multiplier at
1). So the only thing that separates this arm from Housing First is the test and
the exclusion. Of the two guards removed for holder testing, 32257 still binds
through vcc = 1. 32381 goes dead at inc = 1, and it is not needed: with the
exclusion on, a caught holder goes to voucher_excl, which the holder's default
range already spans.

`code/remote_tf_rationed.sh <omega> tested` stages it; `ban`, the default,
reproduces the previous run. Stated before the run: the excluded mass must be
POSITIVE after block 1, or the test is not reaching applicants.

