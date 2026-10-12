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

## RETRACTED: there is no mass leak, and the state IS conserved

An earlier version of this file claimed the addiction state is not conserved across
`max_age_to_choose_addiction`, and called it a mechanical error, on the strength of
the addicted mass falling 98.8 per cent between age 80 and 81 while total mass fell
5 per cent. **That was wrong and it is retracted in full.**

The author, 3 September: *"At age 80 you just can't use drugs if you don't have sud
already. But if you have sud, you still have it if you didn't recover based on the
recovery probability."* That is the design, and it is what the code does.

The error was in what the diagnostic measures. `addiction_rate_by_age` is
accumulated from `is_addicted`, and `is_addicted` is set at line 13698 as

    is_addicted=0
    if (addiction_consumption_1>0) is_addicted=1

so it is **CONSUMES THIS PERIOD**, not HAS THE DISORDER. The disorder state is
`unemployment_index>threshold_addiction_index`, which is a different quantity. The
file says so itself in the comment at 13808-13815, which records that this exact
conflation had already caused one bug: *"requiring is_addicted==1 here -- which
means CONSUMES, not HAS THE DISORDER -- dropped the income and assets of every
carrier consuming nothing"*. The warning was there and I walked past it.

So the `sud=` column of the per-age table is a CONSUMPTION FLOW. Age 80 is the last
age at which consumption can be chosen, 43.7 per cent choose it, and at 81 the
choice is unavailable so the flow falls to 0.55 per cent. No mass moves, nothing
leaks, and the stock of the disorder passes the boundary untouched.

## What is still unexplained

The homelessness spike is real and it is not retracted: 0.190450 at age 80 against
0.000535 at 79 and 0.004786 at 81, in four independent points, and about three
quarters of all homelessness in the model when it appears.

What has changed is the QUESTION. It is no longer "why does a state vanish"; it is
**why do 43.7 per cent of eighty year olds choose to consume drugs at the last age
they are allowed to, and why does that put them on the street.** The second half is
easy -- drug spending crowds out rent -- and the first half is not yet answered.

A deadline alone should not produce it. Consuming at 79 does not preclude consuming
at 80, so waiting costs nothing and there is no option that expires. If anything
the cap should DETER consumption at 80, since a household acquiring the disorder
there carries it into ages where it can never feed it again.

Note also that the spike is parameter dependent: the joint step's first line has
none of it, with age 80 at 0.000324 and a smooth profile.

## Why it matters for the calibration, not just for correctness

When the spike appears it is about three quarters of all homelessness; when it does
not, homelessness nearly vanishes -- h_1 at -95.9 per cent and emp_homeless at -100.
So the model is currently either concentrated on one age or nearly empty of
homeless, and neither is a calibration the note can use.
