# Mapping unemployment onto the productivity grid

Commissioned by the author, 3 September: *"go to the data and figure out how to
map the higher unemployment to the lower productivity guys."*

## The source, and why it is aggregates rather than microdata

The repo holds SCF 2022 and NSDUH 2024. Neither carries unemployment by
education; that is CPS, which is not here. The mapping below uses **published
BLS annual averages for 2019, age 25 and over** -- pre-COVID, so no pandemic
distortion -- which are citable without microdata:

    education                  share of 25+   unemployment rate
    less than high school          9.6%             5.4%
    high school, no college       27.4%             3.7%
    some college / associate      26.4%             3.3%
    bachelor's or higher          36.6%             2.1%

These shares and rates should be checked against a source the author trusts
before anything is published on them. The METHOD below does not depend on the
exact numbers.

## The method

**1. Education orders productivity.** Median earnings rise monotonically across
the four groups, so ordering the grid by productivity orders it by education.
Each group occupies a contiguous block of the productivity distribution sized by
its population share: the bottom 9.6 per cent is "less than high school", the
next 27.4 is "high school", and so on.

**2. The model's parameter is a FLOW, and the data is a STOCK.** This is the step
that is easy to get wrong. `adjusted_probability` multiplies `sep_1`, the
SEPARATION rate (line 7458), while the BLS number is the share unemployed. In
steady state u/(1-u) = s/f, so with the finding rate f common across types the
separation rate must scale with the ODDS u/(1-u), not with u itself. Using u
directly understates the bottom by about four per cent, which is small here but
wrong in principle.

**3. Each node takes the share-weighted average of the odds over its own
quantile interval**, and the whole profile is normalised so the mass-weighted
mean is one. Normalising matters: it leaves the AGGREGATE separation rate
untouched, so `probability_becoming_unemployed` keeps its meaning and `pi_eu`'s
calibration is not disturbed by switching the profile on.

## The result

    node   mass     odds     adjusted_probability
      1   0.0020   0.0571          1.7367
      2   0.0162   0.0571          1.7367
      3   0.0483   0.0571          1.7367
      4   0.1004   0.0439          1.3361
      5   0.1739   0.0384          1.1690
      6   0.2699   0.0346          1.0525
      7   0.3894   0.0222          0.6758

Bottom-to-top ratio **2.57**.

## Two honest weaknesses

**IT MAY BE TOO WEAK.** 2.57 is the whole spread, and the bottom THREE nodes get
the same value because all three sit inside the bottom 9.6 per cent of the
distribution, which is one education group. The employed share of the homeless
has to fall from 0.94 to 0.46, and it is not obvious that a 2.6-fold tilt in the
separation rate does it. That is a measurement, not an argument, and it is one
solve.

**MOST OF THE REAL GAP IS IN THE FINDING RATE, WHICH THIS CANNOT REACH.**
Low-education workers are not only more likely to lose a job, they take much
longer to find one, and that shows up in f rather than s. The code has
`adjusted_probability` on the separation side only, so the profile can reproduce
the stock rate but not the DURATION difference -- and duration is what exhausts
a household's savings and puts it on the street. Varying f by productivity as
well would need a second profile and a second line in the transition, and it is
the version that would actually bite.

## What this replaces

The dead line in `adjusting_unemployment_probabilities_based_on_productivity`:

    adjusted_probability_1(i)=(2n-2i)/(2n-2*5)

At seven nodes that runs 3.00 down to 0.00 -- the top type would face ZERO
separation risk, which is not a fact about the world. The profile above is
bounded, normalised, and sourced.
