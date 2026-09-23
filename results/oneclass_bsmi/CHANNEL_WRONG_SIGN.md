# THE b_smi CHANNEL MOVES THE RATIO THE WRONG WAY, AND IT LEAKS

23 September 01:30 UTC. Two clean blocks of the cold run, healthy economy at
both, no corner. This is the answer to the question the run was launched to
ask, and it is not the expected one.

## THE MEASUREMENT

    b_smi_multiple      1.00        0.95        change
    MOMENT r_smi        1.77924     1.72495     -3.05%
    MOMENT b            0.13006     0.15570     +19.7%
    MOMENT lambda_d     0.052442    0.061267    +16.8%
    drug quantity V     0.82018     1.03137     +25.7%
    SMI prevalence      0.046544    0.047600    +2.3%

The economy is healthy at BOTH points -- populated cells, plausible magnitudes,
nothing at a corner -- so unlike the diverged resume these two readings count.
The ratio is printed by the model and needs no derivation.

**THE BRIEF'S TEST WAS: the channel is working if r_smi RISES as
b_smi_multiple FALLS. b_smi_multiple fell and r_smi FELL.**

For scale: the cold restart reproduces a block to a relative 3e-5, so a 3.05
per cent move is about a thousand times the solver's own noise. This is not
noise.

## THE UPDATE RULE THEREFORE DIVERGES

The rule adds the gap, so a model below target LOWERS the parameter:

    b_smi_multiple = b_smi_multiple + adjuster*(r_smi - 7.30)

r_smi is below target, so b_smi_multiple falls; a falling b_smi_multiple has now
been MEASURED to lower r_smi; so the gap widens and the parameter falls again.
The printed distance already shows it:

    distance_b_smi_multiple   0.75627  ->  0.76371     the gap got WORSE

Left alone this walks b_smi_multiple to its 1e-6 floor over tens of loops while
r_smi moves away from 7.30 the whole way. It is a positive feedback, not a
bracket.

## AND IT IS DRAGGING THE REST OF THE CALIBRATION

One step of this channel moved the drug block hard, all AWAY from target:

    MOMENT b        gap +23.8%  ->  +48.3%
    MOMENT lambda_d gap +20.8%  ->  +41.1%

So the cost of leaving it live is not confined to its own row.

## THE LEAK, WHICH IS THE SECOND HALF OF THE ANSWER

The control the author asked for, derived as the source prints only the ratio
in a steady-state solve (SUD|non-SMI = lambda_d/(1+s(r-1)), s = the p_m moment):

                        b_smi=1.00   b_smi=0.95   change
    SUD | SMI            0.090042     0.102158    +13.46%
    SUD | non-SMI        0.050607     0.059224    +17.03%

**SUD|non-SMI MOVED MORE THAN SUD|SMI.** The parameter is supposed to move SMI
households and essentially nothing else. It moved the households it must not
touch harder than the ones it targets, which is why the ratio fell even though
SMI use rose.

The levels are DERIVED and rest on the population SUD rate being lambda_d and
the SMI share being p_m; the ratio and its direction are printed and do not.
If the author wants the levels measured rather than inferred, that is the
one-line print of the four xtab masses already put to them.

## THE WIRING IS NOT THE BUG

Checked before reporting, because "the channel is leaking" invites the guess
that the multiple is applied to everyone. It is not -- it is conditional on the
household's own SMI state, at 12668:

    if (smi_of(unemployment_index)==1) then
        b_shifter=addiction_scalar_1*b_smi_multiple
    else
        b_shifter=addiction_scalar_1
    end if

So the leak is GENERAL EQUILIBRIUM, not miswiring. Lowering the multiple raises
SMI drug demand, that raises the whole drug quantity by a quarter, and the
market-wide expansion raises non-SMI use by more than the direct effect raises
SMI use. The direct effect is real and is simply swamped.

## WHAT THE SOURCE ALREADY SAYS ABOUT THIS FAMILY OF CHANNEL

Sitting immediately above the wiring, about b-as-a-taste generally rather than
b_smi specifically, and worth the author's eye now:

    "the channel works by making the drug better on the street, which is a
     strange thing to assert and stranger to calibrate. IT IS NOT NEEDED.
     Housing already changes drug use through a HAZARD rather than a taste...
     That is a transition probability, it is what Milby et al. (2005) actually
     measure, abstinence rates by arm"

If a taste shifter cannot move the comorbidity ratio in the right direction
without moving everyone else more, the hazard-side instrument that comment
points at is the obvious alternative for the SMI comorbidity target too.

## WHAT IS NOT BEING DONE

No Fortran edited and the adjuster not touched: the author's instruction was to
start moving b_smi, and turning the channel off is theirs to decide. The run is
left going, which is also how a third point gets measured. But every further
loop lowers b_smi_multiple another 5 per cent, moves r_smi further from target,
and costs the drug block, so the recommendation is to HOLD the channel --
b_smi_multiple_adjuster to 0 -- until the direction is decided.
