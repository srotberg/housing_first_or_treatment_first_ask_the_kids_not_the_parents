# What being homeless costs in this model, and for whom

The author, 3 September: *"homelessness reduce employment, increases mortality,
lowers the chance to recover from sud and gives less housing services... So that
is a lot of disutility"*.

That is right, and it corrects a claim I had made twice — that the model has "no
disutility of homelessness". It has four channels and they are all really there.
The claim was wrong and this file replaces it.

But the four channels do not bite equally, and they do not bite for the households
that are actually homeless HERE. **80.3 per cent of the model's homeless sit in
age band 5, the oldest**, against 7.5 per cent in the data. Evaluated at that age:

| channel | parameter | binds for the model's homeless? |
|---|---|---|
| employment | `increased_prob_if_homeless=0.2` | **No.** The process is written `unemployment_process(1:cutoff_age_1,...)` with `cutoff_age_1 = life_span-retirement_span-1`, so it stops at retirement. The oldest band is retired. |
| mortality | `rr_homeless` (Baggett et al.), `homeless_death_risk_flat_in_age=0` | **Barely.** Read straight off `data/us_mortality_multipliers.csv`: 9.10 at ages 26–34, 7.38 at 42, 5.54 at 50, 3.91 at 58, 2.55 at 66, **1.19 at 74 and 1.10 at 82–85**. |
| SUD recovery | `mu_homeless=0.911` scaling `probability_of_stopping_addiction` | **For 18 per cent.** `UNTARGETED SUD share of the homeless = 0.1836`. It is nothing to the other 82. |
| housing services | `housing_size**((1-sigma)*gamma)` | **Yes**, for everyone. The only one that does. |

So the disutility of homelessness in this model is large for a twenty six year old
and close to nothing for an eighty year old, because three of its four channels are
calibrated to fade with age and the fourth is the flow of housing services.

**AND THAT IS NOT A COINCIDENCE, IT IS THE EQUILIBRIUM.** The model puts its
homeless in the oldest band *because* that is where homelessness is cheapest. The
age profile of the penalties and the age profile of homelessness are the same
fact seen twice. `h_share5` at +970 per cent is the visible end of it.

## A diagnostic I had been over-reading

`DIAG homeless by choice, share of the homeless = 0.9386` is computed at line
13956 as

    after_tax_income_2 + financial_grid(financial_index)
        > rent(t,0) * housing_size(second_lowest_housing_grid_point)

That is a BUDGET test: it says 94 per cent of the homeless are not liquidity
constrained. It does NOT say the street is costless, and I had been quoting it as
though it did. Both things are true at once — they can afford the rent, and at
their age the penalties for not paying it are close to zero — but the second is
the substantive claim and the diagnostic is not evidence for it. The evidence for
it is the table above.

## What this implies for the calibration

The binding tension measured on 3 September is that `max_food_cost` closes `cbar`,
`b` and `lambda_d` together and sends `emp_homeless` and `h_share1` to hundreds of
per cent. Reading it through this table: raising the consumption floor pushes
households toward the cheapest margin, and the cheapest margin is old-age
homelessness, which costs almost nothing.

So the lever is not necessarily a NEW disutility parameter. It is the AGE PROFILE
of the ones that exist — `homeless_death_risk_flat_in_age` is already a switch with
three settings, and setting 2 is a flat multiplier of 1.6 at every age from Meyer,
Wyse and Logani, which would raise the cost of homelessness at 80 by half again
where Baggett's profile puts it at 1.10. Whether that shifts the age profile enough
is a general equilibrium question, which is what the comment beside the switch
already says. It is the author's call, and it is one switch rather than a new
parameter.
