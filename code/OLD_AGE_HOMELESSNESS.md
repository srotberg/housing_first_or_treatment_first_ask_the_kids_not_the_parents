# Who is homeless when old in this model

The author, 3 September: *"the main issue is that too many old are homeless and I
don't understand why.... Are they so poor they can't even afford the smallest
rental? If they can, why do they prefer to live on the street? Who are these guys
that are homeless when old"*.

## The answer to "who": ONE AGE

The per-age diagnostic at the best point, `point_19fa680bc0`:

    age 77  homeless= 0.000770
    age 78  homeless= 0.000616
    age 79  homeless= 0.000535
    age 80  homeless= 0.190450     <-- 356 times its neighbour
    age 81  homeless= 0.004786
    age 82  homeless= 0.003417

Weighted by the mass alive at each age:

- age 80 alone is **74.2 per cent of ALL homelessness in the model**;
- it is **93.7 per cent of band 5's**, which is the +1015 per cent h_share5 gap;
- delete it and the homelessness rate falls from 0.00283 to **0.00073** against a
  target of 0.00399, so the model would be far BELOW target rather than above.

It is not a property of this point. The same spike sits at 0.19-0.21 in
`50c4b984e9`, `a43cf8dd3d` and `00de801fdd`, with neighbours at 0.0005-0.012.

**So there is no population of old people choosing the street. There is one age.**
The question "why do the old prefer homelessness" may not have an economic answer,
and the age profile of the penalties in `HOMELESSNESS_DISUTILITY.md` is not what is
driving h_share5 -- that file's arithmetic stands, but this dwarfs it.

## The answer to "are they too poor": almost none of them

    DIAG homeless who could afford it on INCOME ALONE = 0.9601
    DIAG average assets of the homeless               = 0.0291
    UNTARGETED income of the homeless    model = 0.396   observed = 0.191

96 per cent could pay the cheapest rent out of income alone. There IS a genuinely
priced-out group -- `DIAG cheapest rental over lowest net income = 16.55`, so for
the very poorest the smallest unit costs sixteen years of net income -- but it is
the other 4 per cent.

## What age 80 coincides with, and what is NOT yet established

    integer, parameter :: max_age_to_choose_addiction=55
    integer, parameter :: max_age_to_choose_homelessness=59

Age is printed as `25 + diag_age_1`, so index 55 is **exactly age 80**. The disorder
rate spikes at the same age and only there:

    age 79  sud= 0.000671
    age 80  sud= 0.436898      <-- 651 times its neighbour
    age 81  sud= 0.005521

That coincidence is strong, and homelessness spiking with the disorder is what the
drug block would predict, since drug spending crowds out rent.

**THE MECHANISM IS NOT ESTABLISHED AND ONE GUESS HAS ALREADY BEEN WRONG.** The
first reading was that the cap ERASES the addiction state above age 80, giving a
household one free period of use at exactly 80. It does not. The loop is

    do future_addiction_index=addiction_index, &
        (1-allow_to_choose_addiction)*addiction_index+allow_to_choose_addiction*(...)

so with `allow_to_choose_addiction=0` the bound collapses to `addiction_index` and
the state is FROZEN, not erased -- a user stays a user, a non-user stays a
non-user. That is the intended behaviour and it does not explain the spike.

Nor does mortality explain the fall from 0.437 to 0.0055: at an SUD multiplier of 8
an old user's annual death chance is roughly a third at 80, so persistence plus
recovery would still leave far more than 0.55 per cent using at 81.

So what is established is the FACT and the COINCIDENCE, not the cause.

## The obstacle to testing it

`max_age_to_choose_addiction` is an `integer, parameter` -- a compile-time
constant, not a HANDOVER variable -- so it cannot be varied from a batch line.
Testing whether the spike moves with the cap requires editing the source, which
changes the model hash and unpools all 99 points in this economy. That is a real
cost and it is the author's call, not the loop's.

## THE MASS ACCOUNTING: the disorder state is not conserved across the cap

The author, 3 September: *"We need to understand what is special about age 55....
why they become homeless. Is it some strange mechanical error?"*

It is. Here is the arithmetic, from `point_19fa680bc0`, across index 55 to 56:

    age 79:  sud rate 0.000671   mass 0.588689   addicted mass 0.000395
    age 80:  sud rate 0.436898   mass 0.561685   addicted mass 0.245399
    age 81:  sud rate 0.005521   mass 0.533166   addicted mass 0.002944

The addicted mass falls by **98.8 per cent** in one period, 0.2454 to 0.0029.

**They did not die.** If that mass had died, TOTAL mass would have to fall by at
least 0.2425. It fell by 0.0285 -- eight and a half times less. The households
survive into age 81.

**They did not recover.** `probability_of_stopping_addiction = 0.025`, so at most
0.0061 of that mass could recover in a year, forty times too little.

So the households live, and the disorder they had at 80 is gone at 81. **The
addiction state is not conserved across the boundary at
`max_age_to_choose_addiction`.** That is a mechanical error, not an economic
mechanism, and it is what makes starting to use at exactly index 55 attractive:
the household gets the flow benefit and the state is wiped before the cost is paid.

That also explains what the earlier reading of the choice loop could not. The loop

    do future_addiction_index=addiction_index, &
        (1-allow_to_choose_addiction)*addiction_index+allow_to_choose_addiction*(...)

freezes the state correctly when read on its own. So the fault is not in the loop
bound; it is that the mass chosen into state 1 at index 55 does not ARRIVE in state
1 at index 56.

**WHERE TO LOOK, stated as a hypothesis and not as a finding.**
`allow_to_choose_addiction` is recomputed at five separate sites -- 18986, 19609,
20170, 20577, 21003 -- each from the local `age_index`. If the site that
accumulates the DISTRIBUTION evaluates the flag at the age it is writing INTO
rather than the age it is reading FROM, mass chosen to enter state 1 is written to
state 0. That is the same family as the newborn endowment double-count found
earlier today: a policy path and an accounting path that disagree.

This has NOT been confirmed by reading that code. What is confirmed is that mass is
conserved, households survive, and the state disappears.

## Why it matters for the calibration, not just for correctness

The joint step's first line has no spike at all -- age 80 sits at 0.000324 and the
profile is smooth -- so the spike is parameter dependent and appears only where the
drug block makes onset at the deadline attractive. But when it appears it is about
three quarters of all homelessness, and when it does not, homelessness nearly
vanishes: h_1 -95.9 per cent and emp_homeless -100.

So the model is currently either concentrated in a mechanical artefact or has
almost no homeless at all, and neither is a calibration the note can use.
