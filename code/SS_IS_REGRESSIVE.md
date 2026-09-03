# Why the retired are homeless: social security is proportional, and against the
# net wage it is REGRESSIVE

The author, 3 September: *"So why are so many homeless homeless? Is their ss not
enough for the bottom productivity?"*

Yes. Quantified, at rung 0.114 where the cheapest rental costs 0.11400:

    node   mass      y        SS = .40y   net wage   rent/SS   rent/wage
      1   0.0020   0.03024     0.01210    0.03845     9.42x      2.96x
      2   0.0162   0.06504     0.02601    0.07371     4.38x      1.55x
      3   0.0483   0.11768     0.04707    0.12203     2.42x      0.93x
      4   0.1004   0.19816     0.07926    0.19003     1.44x      0.60x
      5   0.1739   0.33230     0.13292    0.29489     0.86x      0.39x
      6   0.2699   0.60192     0.24077    0.48862     0.47x      0.23x
      7   0.3894   1.93402     0.77361    1.31780     0.15x      0.09x

**Nodes one to four cannot pay rent out of social security at all** -- 16.7 per
cent of the population, against a homelessness target of 0.399 per cent. They
live on savings until those run out and then they are on the street. That is band
5 carrying 3.75 times the observed homelessness rate.

Note nodes three and four especially: rent is 0.93 and 0.60 of their NET WAGE, so
they rent comfortably while working, and 2.42 and 1.44 times their social
security, so they cannot once they retire. **The model manufactures old-age
homelessness at the moment of retirement.**

## The formula, and why it has the gradient backwards

    model_ss_benefits(i) = ss_replacement_rate * employment_grid(1,i)
    ss_replacement_rate  = 0.40

A flat proportional replacement of PRODUCTIVITY. But the tax function is
Heathcote-Storesletten-Violante, so net wage is lambda*y^tau with tau = 0.85, and

    SS / net wage = 0.40 y / (lambda y^0.85) = 0.5318 * y^0.15

which RISES with y:

    node 1   31.5%      node 5   45.1%
    node 2   35.3%      node 6   49.3%
    node 3   38.6%      node 7   58.7%
    node 4   41.7%

**The model's social security replaces less of a poor household's income than of
a rich one's.** US social security does the opposite: the AIME bend-point formula
replaces 90 per cent of the first tranche, 32 per cent of the next and 15 per
cent above, giving roughly 75 to 90 per cent for a low earner and about 28 per
cent at the taxable maximum.

The regressivity is not in the 0.40. It comes from replacing PRODUCTIVITY
proportionally while taxing income PROGRESSIVELY -- the concavity of lambda*y^tau
does the damage on its own.

## What this does and does not explain

It explains band 5 entirely, and band 5 is where the model's SMI homelessness
sits, which is why the SMI share of the homeless reads 51 per cent while the
working-age employed share reads 81.

It does NOT explain bands 2 to 4, which carry a homelessness rate of 0.00030
against 0.00879 observed. Fixing social security would REMOVE most of the model's
homelessness rather than redistribute it, and h_1 would then have to be found
again in the middle of the age distribution where it has never been.

## Not changed

`ss_replacement_rate` is a parameter, not a calibrated instrument, and the shape
of the benefit formula is a modelling choice. Both are the author's call. The
machinery for a means-tested reduction already exists and is switched off:
`reduce_ss_by_half = 0`, `scaling_of_ss = 1`, applied to nodes
1..`productivity_below_which_to_reduce_ss` -- which would make it MORE regressive,
not less.
