# Getting the calibration to a day

The target is hours, at most one day. The measured starting point is weeks. This
is where the factors come from, and only the first group is about making the
model smaller. The rest is about not doing the same solve hundreds of times.

    weeks  --17x-->  30 h  --5x-->  6 h  --4x-->  1.5 h
           removals         PE sweeps      secant, not bisection

## Group 1: remove machinery the model no longer has. 17x

Set out in `WHAT_TO_REMOVE.md` and unchanged here. Housing entered with as a
state, 6.6x. The owner branch and its 61 negative asset points, about 2x. The
housing choice grid from 7 to 3, 1.33x from the specified 4. None of it costs the
model as written anything.

## Group 2: the UI state, and what it is actually worth

The suggestion was to remove the no UI state, with everyone getting UI for one
period and nothing after. Two versions of that, and they are very different.

**Setting the UI draw to certainty.** `probability_of_ui=0.3` becomes 1, so every
household entering unemployment gets insurance for its first year. This removes a
parameter and it removes a branch from the employment transition, but it does
**not** remove a state: a household in its first year of a spell and one in its
third still have different income, zero against the replacement rate, and
different continuation values, so they do not merge. Worth a parameter, not
compute.

**Making unemployment last exactly one period.** This does remove the state, and
the employment dimension goes from 3 to 2, which takes `unemployment_grid_size`
from 6 to 4 since it carries employment crossed with the disorder. Worth
**1.5x**, and it appears twice, in the state and in the expectation nest.

But it removes long term unemployment, and that is not a free simplification
here. The mechanism the paper rests on is that an unemployed household at the
bottom cannot cover the rent out of current income, so it loses its housing. A
household unemployed for one year on a fifty per cent replacement rate is in far
less trouble than one unemployed for three years on nothing, and it is the second
that becomes homeless. Removing the long spell removes the households the
programme is for.

**Recommended: take the parameter, not the state.** Set the UI draw to certainty,
which is defensible on its own terms, and keep three employment states. If more
is needed later, this is the first thing to revisit, but only with the
homelessness rate watched closely.

## Group 3: calibrate in partial equilibrium, close at the end. 5 to 10x

This is the largest factor after the removals and it costs nothing at all.

A stationary equilibrium currently means solving the household problem, iterating
the distribution, and repeating until the tax rate, the drug price and estates
settle: five to ten household solves per equilibrium. Every one of the hundreds
of calibration evaluations pays that.

It does not need to. The model note already does this for the three step like
moments, which are bisected "at the head of each sweep, in partial equilibrium,
before anything else moves". Extend it to the whole sweep: hold prices at their
previous values through all the parameter bisections, and close the equilibrium
**once per sweep** rather than once per evaluation. Since a sweep moves each
parameter a little, prices move a little, so the fixed point is reached from a
very good starting point anyway.

The only care needed is with parameters whose moment is itself a price, so
`tau_l` and `psi_1` stay in the outer loop where they belong.

## Group 4: stop bisecting. 3 to 4x

Bisection on a bracket of width one, to a tolerance of a thousandth, is about
fifteen solves per parameter. Twenty two parameters over five sweeps is roughly
sixteen hundred solves, and that is the whole budget.

Bisection is the right tool for exactly three of those parameters, the step like
ones where the moment is a cliff and a derivative is meaningless. For the other
nineteen the moment is smooth and monotone in its parameter, which is what the
declared sign of dM/dtheta already asserts. Those should use the secant method or
Brent, which reach the same tolerance in **four to five** evaluations rather than
fifteen.

Keep bisection for participation in `b`, homelessness in `h_HL` and wealth over
output in `beta`. Everything else moves to secant. That is 19 parameters going
from 15 evaluations to 5, so the sweep cost falls by about a factor of three.

## What is left, and what it costs

    removals            17x     free, the model as written is already smaller
    PE sweeps           5x      free, prices close once per sweep
    secant              3x      free, only where the moment is smooth
    UI parameter        1x      a parameter, not compute
                       ---
                       255x

Weeks becomes a couple of hours. If that is still not enough, the next items in
order are the income grid from nine to seven, 1.3x and cheap, and then the
employment state from three to two, 1.5x and not cheap.

## What not to spend

Do not touch the asset grid. The `a'` search is quadratic in it, so it looks like
the biggest prize on the list, and it is the one place where the notches that
make the objective not single peaked live: voucher eligibility as a step in
income, the food stamp floor. Those are where the welfare comparison happens and
the margins are tenths of a per cent.


---

# The answer, as of now

Splitting what is measured from what is not, because the difference matters.

## The one measured number

One backward induction pass on four cores, with fixed productivity, the
collapsed experimentation regimes and the zero probability guards all in:
**51 minutes**, down from 88. Everything else below is arithmetic on top of it.

## What is shipped but not measured

The asset grid cut, ninety positive points to seventy. Renters loop 61 to 131
rather than 61 to 151, so 71 points rather than 91, and the a prime search is
quadratic: **1.65x**, predicted. That takes the pass to about **31 minutes**.

## The calibration on top of a pass

    one solve        = backward pass + distribution iteration      ~1.2 x pass
    one calibration  = parameter evaluations x one solve

Twenty two internal parameters, about fifteen bisection steps each, five sweeps:
**1,650 solves**. At 31 minutes a pass that is

    1,650 x 1.2 x 31 min  =  1,023 hours  =  43 days on four cores

Forty cores, if scaling holds at the measured 360 per cent on four:
**about four days**.

## With the rest of the list done

    housing entered with, as a state      6.6x
    the owner branch                      2x
    housing choice grid 7 to 3            1.33x
                                         -----
                                          17.5x  ->  pass of 1.8 minutes

    secant instead of bisection            3x    ->  550 solves

    550 x 1.2 x 1.8 min  =  20 hours on four cores
                         =  about 2 hours on forty

**So: twenty hours on this machine, two on a real one.** That is the target met,
and none of the three outstanding items costs the model as written anything.

## What could still be wrong with this

Three assumptions, none of them measured.

The distribution iteration at a fifth of a pass. Never timed.

Fifteen bisection steps per parameter and five sweeps. That is my reading of how
the first stage runs, not something read off the code.

Whether the price loop is nested inside the parameter loop or runs alongside it.
If it is nested, every number above is five to ten times worse and partial
equilibrium sweeps become the single most valuable change on the list rather
than a convenience. **This is the first thing to check**, and it is a ten minute
job for someone who knows the calibration driver.

## The lever not on this list

Twenty two internally calibrated parameters is the multiplier that dominates
everything. Halving it halves the calibration, and it is worth asking of each
one whether it needs to be fitted here or could be assigned, the way theta was
in the stylized model once the attempt to calibrate it failed honestly.

---

# Revised bottom line

Three corrections, two of them from the author and both right.

**The drug price needs no convergence in the calibration.** The normalisation is
that `psi_1` is chosen so `p_v = 1` at the benchmark quantity. That is a
definition, not a fixed point: solve at `p_v = 1`, read the quantity off the
solution, and set `psi_1 = 1/V^(psi_2-1)` at the end. Nothing iterates. Only the
counterfactuals, where the quantity moves and the price with it, need the loop.
That takes the outer loop from `tau_l`, `p_v` and estates to `tau_l` and estates,
worth roughly **2x** on every equilibrium in the calibration. This should have
been obvious and was not; it is the cheapest factor on the whole list.

**The housing state goes, and the reason it was ever there is ownership.**
Tracking the unit a household arrives in earns its keep only when selling carries
a transaction cost, so a homeowner's tenure decision depends on where it starts.
With ownership gone and renters facing no adjustment cost, it is dead weight, and
the dump confirms it: the value function spread across that index is exactly
zero. Worth **2.5x**, not the 6.6x in the model note, because six of the eight
slots are unpopulated owner states that already exit for free.

**The asset grid goes to fifty positive points**, not seventy. The renter loop
goes from 91 points to 51 and the `a'` search is quadratic, so **3.2x** against
the original ninety. This is the one number here that is a judgement rather than
a deduction, and it must be validated by solving the benchmark at fifty and at
ninety and comparing the targeted moments and both counterfactuals.

## What it comes to

    per pass, from the measured 51 minutes
      asset grid 90 to 50                  3.2x
      housing state removed                2x
      owner branch removed                 2x
      housing choice grid 7 to 3           2.3x
      income grid 9 to 7                   1.3x
                                          -----
                                            38x  ->  about 80 seconds a pass

    per calibration
      secant where the moment is smooth     3x   ->  550 evaluations
      no drug price loop                    2x
      equilibrium closed once per sweep    included above

    550 x 1.2 x 80 s  =  15 hours on four cores
                      =  about 1.5 hours on forty

**Eleven hours on this container.** That is the target met with room to spare,
and every factor except the asset grid is exact.
