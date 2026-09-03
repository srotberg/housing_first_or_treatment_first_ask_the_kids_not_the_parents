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
