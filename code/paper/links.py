"""
Which Fortran declaration carries each row of the two parameter tables.

WRITTEN OUT RATHER THAN INFERRED. Linking a table cell to a constant by
matching its value was tried and is unsafe: the replacement rate is 0.50 and so
is the employment rate of the homeless, the discount factor targets a wealth to
output ratio of 3.00 and so does the child's SUD ratio, and a matcher happily
paired all four the wrong way round. A wrong link here would put one
parameter's number under another's name in the paper and nothing downstream
would notice, so the mapping is stated and checked by eye once.

A row with no entry has no counterpart in the Fortran: it is a value taken
straight from a paper, and its number stays in the spec.
"""

# The moment a row is calibrated against, for internally calibrated rows, and
# the declared value for externally set ones.
LINKS = {
    # --- Table 5, the parameters that carry the story
    r'$\theta$':                 'drug_spending_share_data',
    r'$b$':                      'participation_rate_data',
    r'$\lambda$':                'sud_rate_data',
    r'$\aleph$':                 'vsl_data',
    r'$h_2$':                    'employed_share_of_homeless_data',
    r'$\kappa_{ued}$':           'unemployment_rate_sud_data',
    r'$h_1$':                    'fraction_homeless_data',
    r'$\underline c$':           'food_stamps_share_data',
    r'$\pi_V$':                  'voucher_coverage_data',
    r'$\lambda_m$':              'smi_share_of_homeless_data',
    r'$\kappa_{uem}$':           'employment_rate_given_smi_data',
    r'$\mu_H$':                  'milby_recovery_ratio_data',
    r'$\bar\tau^{u}$':           'treatment_take_up_data',
    r'$\omega$':                 'child_use_gap_data',
    r'$\delta_d$':               'child_sud_ratio_data',
    r'$\delta_h$':               'child_homeless_ratio_data',
    r'$\kappa_{\phi m}$':        'kappa_phi_m',
    r'$\sigma_{\ell}$':          'leisure_curvature',
    # --- Table 6, the standard parameters
    r'$\gamma$':                 'avg_rent_to_income_data',
    r'$\beta$':                  'wealth_to_output_data',
    r'$\omega_{\ell}$':          'avg_labor_supply_data',
    r'$\sigma_y$':               'bottom_half_earnings_share_data',
    r'$\bar\pi^{eu}$':           'unemployment_rate_data',
    r'$\tau_{\ell}$':            'average_labor_income_tax_data',
    r'$r$':                      'risk_free_rate_data',
    r'$\xi$':                    'curvature_of_labor_income_taxes',
    r'$\tau_k$':                 'investment_income_tax',
    r'$\psi$':                   'replacement_rate_ui',
    r'$\kappa_V$':               'threshold_income_vouchers',
    r'$\kappa_r$':               'rent_to_income_ratio_vouchers',
    r'$\varrho$':                'food_stamp_taper',
    r'$J_E$':                    'max_age_to_choose_addiction',
}

# Rows whose Data column is deliberately NOT the linked constant, because the
# source states the number in units the model does not work in. The link is
# kept so the value can still be checked, but the cell keeps its own text.
UNITS_DIFFER = {
    r'$\aleph$': 'the source gives a value of life in dollars, the model in incomes',
    r'$\sigma_{\ell}$': 'the source gives a Frisch elasticity, the model a curvature',
}
