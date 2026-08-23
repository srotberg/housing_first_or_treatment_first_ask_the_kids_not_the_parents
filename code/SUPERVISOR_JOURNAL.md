
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

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops, and its moment is not reported as a scalar

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops, and its moment is not reported as a scalar

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops, and its moment is 58.7 per cent off
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops, and its moment is 48.0 per cent off
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops, and its moment is 10.4 per cent off

## 2026-08-23 12:20 UTC: homelessness is a step function and h_1 cannot land on the target

The container rebuilt and the run was restored from the branch tip and relaunched
at loop 5. Two things in the banked logs are worth a person's attention.

**h_1's moment is not monotone in h_1, and the bracket keeps being thrown away.**
Measured across the run, homelessness against the parameter that sets the service
flow of the street:

    h_1 0.2943 -> 4.15e-04     h_1 0.2596 -> 6.73e-05
    h_1 0.2981 -> 2.32e-03     h_1 0.2630 -> 6.17e-06
    h_1 0.2962 -> 1.46e-02     h_1 0.2515 -> 3.14e-02
    h_1 0.2825 -> 1.58e-02     h_1 0.2363 -> 3.43e-02

A three per cent cut in the parameter, 0.2596 to 0.2515, moves the moment by a
factor of 470, and the 3.99e-03 target sits inside that jump. The direction
reverses twice. The log carries the model's own verdict three times over: two
`size_homelessness BRACKET DISCARDED` lines, one for the moment falling when the
parameter rose and one for it rising when the parameter fell, and a third for
beta, whose wealth to output ratio rose when the discount factor was lowered.

The declaration at line 1630 anticipated exactly this and says what it means:
the bracket is valid only if its endpoints were priced under the same value of
life, and *"if the violations keep coming, the message they carry is that this
parameter cannot be calibrated while the value of life is still moving under it,
and the answer to that is to sequence the loop rather than to bisect harder."*
The violations are coming. Sequencing the loop is a structural change to the
calibration and is left for the author.

This is also why four other moments cannot be identified. mu_H is HELD whenever
no homeless household carries the disorder, lambda_m moves only in the loops
where there is homeless mass to measure the SMI share on, and rho_m and rho_d
are measured on whatever handful of households the step function happens to have
left on the street.

**kappa_uem is buying nothing.** It has risen at every one of twenty four loops,
4.42 to 13.79, and the employment rate given SMI has wandered between 0.43 and
0.54 throughout against a target of 0.30: 0.486 at kappa 8.62 and 0.476 at
kappa 13.79. A parameter that has more than tripled while its moment has not
moved is either paired with the wrong moment or saturated, and neither is a
bound tweak, so it is recorded rather than damped.

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops, and its moment is not reported as a scalar

## 2026-08-23 12:50 UTC: omega's moment is not measuring omega

The omega gap has moved away for three checkpoints, 177 to 210 to 257 per cent,
and the sign is wrong: switching the child term off LOWERS drug use in five of
the last six loops, where the mechanism says it must raise it. It is not the
counterfactual's own convergence. The diagnostic put in for exactly this question
answers it every loop: 61 to 83 sweeps, reached between 2e-05 and 5.7e-04
against a stopping rule of 6e-4, capped zero every time.

**The term is too small to move the moment at all.** It is
`beta*(1-survival)*omega*[E[V_child(d,h)] - E[V_child(0,1)]]`. Omega has been
between 0.000 and 0.024 all run; `(1-survival)` is the chance the child is born,
order 1e-2 at working age; and the note at line 21805 measures the gradient in
`E[V_child]` at 60.291 against 60.276, or 0.015 utils. The product is order 1e-6
utils. A term worth a millionth of a util does not change drug participation by
twenty nine per cent.

**The log proves it directly.** In loop 3 the counterfactual returned
0.19214831778983701 users with the child penalty off, which is loop 1's BASELINE
to all seventeen digits. Switching the term off changed the distribution by
nothing at all. What differs between the two numbers the gap is built from is
therefore not the child term:

    loop 1   counterfactual 0.136837   baseline 0.192148   gap -0.288
    loop 3   counterfactual 0.192148   ( = loop 1's baseline, exactly)

**Where the difference comes from.** The counterfactual is solved first, from
whatever distribution the previous loop left, and then `initialize_feasible_
distribution` is skipped from loop 3 onwards, so the baseline's distribution
solve starts from the counterfactual's. The two numbers are a distribution
reached from the previous loop's baseline under one policy, and a distribution
reached from THAT under the current loop's parameters. The distribution does not
converge in max norm at any grid and stops on a 6e-4 rule under a 200 sweep cap,
so the difference between the two is the loop's other parameter updates plus
path dependence. It is attributed to omega in full.

So the omega bracket is calibrating on a number that does not respond to omega,
which is why its gap wanders with the sign of whatever else moved that loop. The
fix is a modelling decision -- measure the counterfactual and the baseline from
the SAME starting distribution, which means solving the baseline first and
re-seeding the counterfactual from it, or holding the moment until the two can
be priced from a common point -- so it is recorded rather than changed here.

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3697, one way across 24 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 13.79, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_housing` moved 0.2743 to 0.1265, one way across 24 loops, and its moment is not reported as a scalar
- `relative_share_leisure` moved 3.495 to 0.5733, one way across 24 loops, and its moment is not reported as a scalar

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.1276 to 0.3835, one way across 26 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 15.42, one way across 25 loops, and its moment is 21.7 per cent off
- `relative_share_housing` moved 0.2743 to 0.1017, one way across 25 loops, and its moment is 32.9 per cent off

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `size_homelessness` moved 0.263 to 0.1, one way across 9 loops, and its moment is not reported as a scalar
- `kappa_uem` moved 4.415 to 15.77, one way across 29 loops, and its moment is not reported as a scalar
- `relative_share_housing` moved 0.2743 to 0.09162, one way across 28 loops, and its moment is not reported as a scalar

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `relative_share_housing` moved 0.2743 to 0.08765, one way across 29 loops, and its moment is not reported as a scalar

## Parameters drifting one way

Recorded, not acted on: damping a drift or repairing a moment pairing is a modelling call, and escalating would kill a run whose other brackets are converging.

- `largest_house_size` moved 0.3835 to 0.1597, one way across 8 loops, and its moment is not reported as a scalar
