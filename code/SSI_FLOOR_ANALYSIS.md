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
