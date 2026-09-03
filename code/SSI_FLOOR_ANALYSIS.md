# Why the SSI floor cannot fix old-age homelessness

Closed-form, 3 September, prompted by the author: *"Maybe the ssi floor has to
apply to more than just 1 productivity? Maybe the bottom productivity is not
enough?"*

The floor is `max(PIA_i, takeup * 0.1774)` and applies at EVERY node. It lifts
a node only where the statutory benefit falls below it. Computed on the grid the
model actually ran (`point_27c117638d`, last working age, and its ergodic
masses), with the statute's own bend points 0.2208 and 1.3314 and rates
0.90/0.32/0.15:

    node   y(last)      mass       PIA    floor    binds?   flat 0.40y
      1    0.02152   0.00239   0.01936   0.1774     YES        0.00861
      2    0.06291   0.03660   0.05662   0.1774     YES        0.02516
      3    0.18393   0.20167   0.16554   0.1774     YES        0.07357
      4    0.53778   0.39773   0.30015   0.1774      no        0.21511
      5    1.57236   0.28271   0.59026   0.1774      no        0.62894
      6    4.59730   0.07216   0.75082   0.1774      no        1.83892
      7   13.44169   0.00674   0.75082   0.1774      no        5.37668

**THE FLOOR IS NOT CONFINED TO ONE NODE.** It binds on nodes 1, 2 and 3, which
is **24.07 per cent of the population** at full take-up. So the coverage
hypothesis is wrong in its narrow form: a quarter of retirees are already being
lifted, and taking the dial from 0.5 to 1.0 changed h_share5 by 0.005 --
0.93063 to 0.93548, the wrong way. Whoever is going homeless in retirement is
not in the bottom three nodes.

## WHAT THE FLIP ACTUALLY DID, AND IT IS THE OPPOSITE OF WHAT I REPORTED

Comparing the statute against the flat `ss_replacement_rate=0.40` it replaced:

    node 1   PIA 0.01936  flat 0.00861   PIA HIGHER  +125.0%
    node 2   PIA 0.05662  flat 0.02516   PIA HIGHER  +125.0%
    node 3   PIA 0.16554  flat 0.07357   PIA HIGHER  +125.0%
    node 4   PIA 0.30015  flat 0.21511   PIA HIGHER   +39.5%
    node 5   PIA 0.59026  flat 0.62894   PIA LOWER     -6.2%
    node 6   PIA 0.75082  flat 1.83892   PIA LOWER    -59.2%
    node 7   PIA 0.75082  flat 5.37668   PIA LOWER    -86.0%

The statute made poor retirees MUCH richer -- the bottom three nodes gained 125
per cent -- and rich retirees dramatically poorer, because the formula is
progressive and its third bracket is capped at `ss_taxable_max`. Nodes 6 and 7
lost 59 and 86 per cent of their retirement income.

**So I had the mechanism backwards.** I wrote that "the PIA formula is evidently
LESS generous to low-productivity retirees than the flat rate it replaced, and a
half take-up floor does not recover the difference." That is false at the bottom
and true only at the top. The bottom was made better off and old-age
homelessness still rose, which is the finding.

## WHERE THAT POINTS

The retirees going homeless are the ones the CAP hit, not the ones the floor
lifts. That is consistent with every other measurement on this economy:
homelessness here is a taste margin -- 0.9997 of the homeless are there by
choice and 0.9974 could afford a rental on income -- so the households that move
are the ones whose income fell relative to what they were used to, which under
the statute is the TOP of the distribution.

Two things follow.

**The flip should be reverted.** At `use_pia_formula=0` the same economy gives
h_share5 = 0.7186 and h_1 = 0.00383, which is inside ten per cent; at
`use_pia_formula=1` it gives 0.9306 to 0.9355 and h_1 at plus 229 to 253 per
cent. The flip was approved to give h_share5 an instrument and it has no
instrument either way, so it is paying for nothing.

**`ss_replacement_rate` IS THE PARAMETER THAT ACTS ON THE WHOLE DISTRIBUTION,
and it is not currently settable.** Line 3834 declares it
`real(8), parameter :: ss_replacement_rate=0.40`, so it cannot be handed in and
cannot be calibrated without a Fortran change. If old-age homelessness is to
have a real instrument, that is the candidate: it scales benefits at every node
rather than only where a floor binds. Making it a variable is a small change and
it is the author's call, not mine.

## THE FLOOR CANNOT BE THE INSTRUMENT, because a high floor IS a flat pension

The author, 3 September, on being shown that h_share5 needs a floor near 1.0:
*"I don't understand... You need the floor to be 1?? That means everyone has
the same ss"*. Correct, and it invalidates the recommendation in the section
above. The arithmetic was in the PIA table the whole time and was not read.

PIA is capped at **0.75082** on this grid, because nodes 6 and 7 both hit
`ss_taxable_max`. The benefit is `max(PIA_i, floor)`, so:

    floor     nodes on the floor   mass flat   benefit spread   what SS is
    0.1774    1,2,3                   0.2407          4.2324   earnings-related
    0.30      1,2,3                   0.2407          2.5027   earnings-related
    0.60      1,2,3,4,5               0.9211          1.2514   nearly flat
    0.75082   1,2,3,4,5               0.9211          1.0000   COMPLETELY FLAT
    0.90      all seven               1.0000          1.0000   COMPLETELY FLAT
    1.00      all seven               1.0000          1.0000   COMPLETELY FLAT

At any floor at or above 0.75082 every retiree receives an identical benefit.
At 0.60 the whole schedule already spans a factor of 1.25 and 92 per cent of
the mass is on the floor. **h_share5 crosses its target between 0.60 and 1.00**,
which is exactly the region where social security stops being a function of
lifetime earnings.

So the bracket that looked like a success is a bracket across a modelling
boundary, not a calibration. The search bound is now (0.1774, 0.30): 0.30 is
the last value at which the floor binds on exactly the bottom three nodes, 24
per cent of the mass, which is what real SSI does -- node 4's own PIA is
0.30015 and node 4 carries 39.8 per cent.

## WHAT WOULD ACTUALLY WORK: scale benefits, do not truncate them

The moment needs a parameter that raises retirement income PROPORTIONALLY, so
the schedule keeps its shape. Two candidates, both requiring a one-line source
change and both the author's call:

- **`ss_replacement_rate`**, currently `real(8), parameter :: 0.40` at line
  3834 and so unreachable. It multiplies the last working age grid point
  directly, which preserves earnings-relatedness exactly. It is only live when
  `use_pia_formula=0` -- and PIA=1 has independently been measured to make
  h_share5 WORSE and to cost h_1, so reverting the flip and calibrating this is
  the cleaner of the two.
- **A scalar on the PIA**, or the three `ss_pia_rate_*` moved together. They
  are already variables rather than parameters, but there is no single dial for
  them, and moving three numbers against one moment is not identified.

## THE AUTHOR IS RIGHT THAT SOMETHING IS WRONG, AND HERE IS HOW WRONG

*"That tells you that something is very strange... Why do you need such a high
floor?? It is very odd"*. It is, and the static algebra says the floor should
not be needed at all.

First, a correction to the number in the section above: the cheapest rental's
cost was computed with `curvature_of_labor_income_taxes` assumed to be 1.0. It
is **0.85** (line 3350). Redone:

    net_income_lowest = 0.7522432 * 0.004^0.85 = 0.006888
    cheapest rental   = 16.5499 * 0.006888    = 0.11400

which is exactly `smallest_house_size`, so `rent(1,0)` is 1.0 by normalisation
and the cheapest unit costs **17.9 per cent of average labour income**.

### The flow trade-off says a retiree on real SSI should rent

Cobb-Douglas over consumption and housing, weight 0.100, `mu_homeless` 0.911,
street housing 7.6 per cent of the rental's and free:

    income     c if rents     U rent    U street    prefers
    0.16554       0.05154    -2.8860    -3.0045       rent    node 3 PIA
    0.17740       0.06340    -2.6996    -2.9423       rent    real SSI floor
    0.30015       0.18615    -1.7302    -2.4690       rent    node 4 PIA
    0.59026       0.47626    -0.8848    -1.8603       rent    node 5 PIA
    0.75082       0.63682    -0.6233    -1.6438       rent    the PIA cap

The indifference income is **0.1568**, which is 1.38 times the rent and a
quarter of average labour income. Every PIA in the schedule is above it, and so
is the real SSI floor of 0.1774 -- by 13 per cent.

### And it is not the housing weight

Checked, because a low Cobb-Douglas weight on housing would make the street
cheap in utility terms:

    housing weight        flip income   x the rent   who is above it
    0.100  (the model)         0.1568         1.38   nodes 3+, real SSI
    0.229  (model gamma)       0.1330         1.17   nodes 3+, real SSI
    0.268  (target gamma)      0.1284         1.13   nodes 3+, real SSI

Raising the weight to its target moves the threshold the right way but changes
nothing qualitative. To push the threshold up to where the observed behaviour
would make sense, `mu_homeless` would have to go to about 20 against 0.911.

### SO THE QUESTION IS NARROWED, NOT ANSWERED

On flow utility, no retiree at the real SSI floor should ever choose the street,
and 4.8 per cent of band 5 do. The margin is not large -- 0.243 in utility at
0.1774 -- so something the static comparison does not see is flipping it. What
this algebra cannot reach, and what has to be looked at next:

- the DYNAMIC problem: assets, the continuation value, and
  `homeless_excess_death_risk` interacting with `value_of_life` at the very end
  of life. Band 5's homelessness RISES with age -- 0.0588 at 83, 0.0860 at 84 --
  which is the shape of an absorbing state or of a terminal-horizon effect, not
  of a flow choice repeated each period;
- `max_food_cost` of 0.0130 and the food stamp rules, which change consumption
  on both sides and are not in the comparison above;
- whether becoming housed again is restricted once homeless, which would make
  the old homeless a STOCK inherited from working life rather than a retirement
  decision.

**Do not calibrate `ssi_floor_level` against `h_share5` until this is
resolved.** The instrument works -- the band 5 rate fell thirteenfold -- but if
it is compensating for a defect rather than pricing a margin, then fitting the
moment with it buries the defect at an implausible pension.
