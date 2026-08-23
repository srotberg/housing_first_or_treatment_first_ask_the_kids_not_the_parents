
## 2026-08-23, loop 21: the trace was reading the wrong column, and what it says now

The parameter trace was rebuilt from the thirty six banked run logs after the
reconstructed version failed its own check. Six of fourteen columns had been
reading `distance_X=` rather than `X=`, because the model prints the distance on
the line below and the pattern was not anchored; `lambda_m` had been reading a
setup line from `build_smi_onset` and so read the same number every loop. A
distance falling smoothly to zero reads as a runaway and a setup constant reads
as a frozen parameter, so nothing earlier attributed to those columns stands.

With the columns right, over twenty one loops:

**The users are the poor, and this is now measured rather than hoped.** Income
of drug users over average labour income is 0.587 and income of the disordered
0.628. Theta is 0.120, off its 0.25 ceiling; b is 0.103, off both bounds. The
guard that holds theta while the gradient is inverted has not had to fire since
b was freed.

**Homelessness has collapsed, and it takes four moments with it.** The model
puts 6.7e-05 of households on the street against a target of 3.99e-03. With
essentially no homeless population: mu_H is HELD every loop, because no homeless
household carries the disorder and the recovery gradient cannot be measured;
lambda_m moved in three loops out of twenty one, and its moment, the SMI share
of the homeless, reads 0.943 against 0.25, the worst gap in the table; rho_m is
83.6 per cent off on homeless income share and rho_d 67.1 per cent off on the
employed share of the homeless. Four of the six worst gaps are one failure.

**bar_tau^u is at its floor of zero and the model says why.** Take up is 0.0014
against 0.245, and the printed message is that treatment is declined even when
free, so the target is out of reach on the benefit side -- g, mu_H, pi_r and the
forced abstention -- not on the cost. This is no longer treated as a frozen
parameter, because escalating kills the run.

**kappa_uem is running away.** It has risen at every one of twenty one loops,
4.42 to 12.52, and its moment is still 44.7 per cent off. `diagnose_runaway` is
hard coded to size_homelessness and cannot see this; it is left as a reading for
now rather than fixed, because raising or damping it is a modelling call.

Converging: the leisure share is 3.3 per cent off, the tax rate 0.7, the
separation rate 4.2, the addiction hazard 6.4, the voucher probability 7.6.
