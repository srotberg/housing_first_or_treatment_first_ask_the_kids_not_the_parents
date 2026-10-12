THE THREE ARMS, as specified by the author on 19 September.

All three start from the pinned benchmark: delta_d = 0.24, omega_c = 0.055,
every other parameter frozen at n72's vector, and kappa_x pinned from n87's
probe. All three clear the government budget with pi_v and clear the drug
price at supply elasticity 1.46.

COMMON BUILD. is_counterfactual and use_revenues_to_increase_voucher_probability
are compile-time parameters, so the arms need one counterfactual binary that is
not the benchmark's:
    is_counterfactual                            0 -> 1
    use_revenues_to_increase_voucher_probability 0 -> 1     (picks tax_system_type=3)
    increase_vouchers_for_homeless_only          0          (already; instrument is pi_v,
                                                             not increased_prob_if_homeless)
    partial_equilibrium                          0          (already)

COMMON HANDOVER.
    adjust_taxes            1     without it distance_govt_budget is identically
                                  zero and the budget never clears
    penalty_child_addicted  0.24
    kappa_x                 <from n87's probe>

ARM 1 -- THE OPTIMAL DRUG USE RATE
    weight_on_child                 1.0
    internalise_homelessness_cost   0
    voucher_conditional_on_clean    0
Each household faces the whole cost of its own drug use to its child. What
survives is the optimal drug use rate.

ARM 2 -- ARM 1 PLUS THE HOMELESSNESS EXTERNALITY INTERNALISED
    weight_on_child                 1.0
    internalise_homelessness_cost   1
    voucher_conditional_on_clean    0
Adds the flat kappa_x charge on the household's own housing choice. Unlike
kappa_x*H this MOVES POLICY FUNCTIONS -- it is the Pigouvian charge.

ARM 3 -- TREATMENT FIRST
    weight_on_child                 0.055   (the benchmark's own)
    internalise_homelessness_cost   0       kappa_x is an externality on
                                            everyone, NOT internalised privately
    voucher_conditional_on_clean    1
    include_voucher_exclusion       1
    probability_of_detection        0.70    author, 19 Sept: false negative
                                            "about 30%", revised from 0.95
    probability_of_false_positive   0.0     author: "labs have a 5% CI....so you
                                            cannot get a false positive",
                                            revised from 0.005
    increased_prob_of_voucher_if_homeless_and_addicted  0   the second TF switch
    voucher_exclusion_release       1/3     already: expected exclusion 3 years

WHAT ARM 3'S SANCTION DOES, from the code's own comment. A homeless household's
voucher pays zero -- the payment is capped by actual rent spending and a
homeless household spends none -- so removing THIS period's voucher costs the
targeted household nothing. The thing of value is the OPTION to draw on it once
housed, and only a bar on future offers destroys that. Hence the excluded
state rather than a one-period removal.

AT probability_of_false_positive = 0 the wrongly-sanctioned group disappears
entirely and every exclusion is a true positive. The code's comment calls false
positives half of the empirical case for Housing First, so the write-up has to
say this was set to zero deliberately.
