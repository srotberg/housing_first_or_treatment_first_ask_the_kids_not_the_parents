# SMI is on the street. SUD is not. The asymmetry is employment.

The author, 3 September: *"I still don't understand why those with Sud and smi
are not in the homeless population.... That should make the unemployment there
be much higher."*

Half the premise is wrong and the other half is the whole problem.

## SMI is over-represented, by a lot

           population share   homeless share   over-representation
    MODEL       4.39%             50.78%            11.6x
    DATA        4.80%             25.00%             5.2x

**Serious mental illness is already TWICE as concentrated on the street as the
data asks.** `lambda_m` is +103 per cent. Nothing needs to push SMI toward
homelessness; if anything it needs restraining.

## SUD is absent, and for two separate reasons

           population share   homeless share   over-representation
    MODEL       0.93%              1.19%             1.28x
    DATA        3.68%             21.70%             5.90x

The SUD share of the homeless is EIGHTEEN times too low, and that decomposes:

1. **There are four times too few households with the disorder.** `lambda_d` is
   0.0093 against 0.0368, a gap of -75 per cent. This is the drug block, still
   open.
2. **The ones that exist are barely more likely to be homeless than anyone
   else** -- 1.28 times, against 5.90 in the data.

Fixing only the first gets a fifth of the way: at the target population share
with the over-representation unchanged, the SUD share of the homeless would be
4.7 per cent against 21.7. **Both have to move.**

## The asymmetry is employment, and it is measured

    employment given SMI      model 0.168  ->  83 per cent NOT employed
    unemployment given SUD    model 0.224  ->  78 per cent ARE employed

SMI households have no earnings, so they cannot pay rent and they end up on the
street. SUD households have jobs, so they can. That is the entire difference, and
it is why raising unemployment among the low-productivity -- the author's
proposal -- would help the poor generally but would NOT put people with the
disorder on the street: they are not there because of unemployment.

## AND THE DATA SAYS THE SAME THING ABOUT EMPLOYMENT

The target for unemployment given SUD is 0.1625, so the data says **84 per cent
of people with the disorder are employed** -- even more than the model's 78. And
the same data says they are 5.9 times over-represented among the homeless.

**So in the world, addiction causes homelessness while people are still working.
It is not an unemployment channel. It is a SPENDING channel.**

The model has that channel: `theta`, the share of income spent on drugs, sits at
0.174 against a 0.162 target -- on target and evidently not enough to price
anybody out. An addict earning a low wage, paying 17 per cent of it for drugs and
19 per cent of mean income for the cheapest rental, still rents.

## What this implies for the calibration

The unemployment-by-productivity profile is worth switching on for its own sake
-- it is true in the data and it makes poverty and joblessness coincide. But it
will not close `emp_homeless` through the SUD channel, because SUD homelessness
in the data is not a jobless phenomenon.

What would: making the disorder EXPENSIVE enough, or its earnings penalty
(`rho_d`, currently 1.0, i.e. no penalty at all) large enough, that a working
addict cannot afford rent. `rho_d` is the obvious candidate and it has never been
moved off one.

---

# THE AGE PROFILE IS THE REAL DEFECT, and it explains everything above

The author, 3 September: *"If some many with smi are homeless, why are the
homeless not unemployed? Are you maybe not counting smi as unemployed even when
they are??"*

The specific suspicion is wrong -- `emp_of = mod(i-1,3)+1` gives 1 employed,
2 unemployed without UI, 3 unemployed with UI, and the accumulator gates on
`emp_of > 1`, so the SMI unemployed ARE counted. But the instinct that the
numbers do not add up was right, and chasing it found something worse.

## The two shares are on different populations

    model_employed_share_of_homeless  =  1 - unemployed / mass_homeless_WORKING_AGE
    model_smi_share_of_homeless       =      smi_homeless / mass_homeless_RAW

One excludes retirees, the other does not. So "51 per cent of the homeless have
SMI" and "81 per cent of the homeless are employed" were never about the same
people, and quoting them side by side -- which this file did -- invited exactly
the contradiction the author spotted. A comment at the guard says retirees were
about thirty per cent of the model's homeless when it was written.

## And here is why that matters so much

    band     model rate    data rate   model/data
      1        0.00486      0.00316       1.54x
      2        0.00018      0.00338       0.05x
      3        0.00005      0.00291       0.02x
      4        0.00007      0.00250       0.03x
      5        0.00289      0.00077       3.75x

**Bands 2, 3 and 4 are the middle of working life, and the model puts twenty to
fifty times fewer people on the street there than the data does.** Summed, those
three bands carry a homelessness rate of 0.00030 against 0.00879 observed --
a factor of twenty-nine.

The model's homelessness is BIMODAL: the young, who start life with zero wealth,
and the RETIRED, who have low income. Everyone in between has savings and rents.

## This is the single explanation for the whole night

- **why the homeless are employed**: the working-age homeless are almost all
  band 1, the young, who have jobs but no assets yet;
- **why SMI looks over-represented**: it is concentrated in band 5, the retired,
  who are counted in the SMI share and excluded from the employment share;
- **why SUD is absent**: people with the disorder are middle-aged, and the middle
  of the age distribution is where the model has no homelessness at all;
- **why bottom_productivity_level did nothing**: it makes a household poor for
  life, and a household poor for life in this model accumulates savings anyway;
- **why unemployment does not put anyone on the street**: a spell hits a
  middle-aged household with a decade of assets.

The instrument question -- what owns `emp_homeless` -- is downstream of this. No
instrument that acts on WHO is poor will fix a profile that is wrong in AGE. What
is missing is a reason for a middle-aged household with savings to end up on the
street, and the candidates are the ones that destroy savings rather than reduce
income: the earnings penalty of the disorder `rho_d`, still at 1.0 meaning no
penalty, and drug spending `theta`, on target at 0.174 and evidently not enough.
