# THE GRANDFATHERED TRANSITION AT T=60. What must be true, stated BEFORE the run.

The standing rule: a change meant to be a no-op somewhere has its reference
value stated before the run, and a control whose expected value is not known in
advance cannot falsify anything. This whole chain was rebuilt in a container that
had none of it -- a different compiler, a re-solved benchmark, a re-solved arm 3
-- so there is more to control here than the grandfathering itself.

## THE CHAIN, AND WHERE EACH LINK CAN BE CHECKED

    1. benchmark      cold, from resume_seed.dat + 7 names     see COLD_START.md
    2. arm 3          warm from 1, at p=0.833490, pi_v=0.076347
    3. T=5 GF probe   a CONTROL against five known numbers
    4. T=60 GF run    the measurement

Step 3 exists because steps 1 and 2 are re-solves of runs made in another
container on another compiler, and the T=5 grandfathered test has already been
run, so its numbers are a reference this chain can be scored against for about
forty minutes of wall clock instead of seven and a half hours.

## STEP 2'S ACCEPTANCE TEST, from results/arm3_convergence/CONVERGED.md

    b        0.045287      lambda_d  0.018460      h_1    0.006542
    pi_v     0.076347      price     0.833490      CEV    +3.249%

Not near these, and the chain stops here rather than carrying a different arm 3
into a seven-hour run. "Near" is not equality: the model is not
bit-reproducible, the standing score for a no-op is 1e-4 RELATIVE, and this is a
different compiler as well as a different container, where the measured
cross-container spread on w_bot is 1.8e-2.

## STEP 3'S ACCEPTANCE TEST, from the T=5 grandfathered test

    grandfathered mass          3.6187 of 50.8612 total, about 7.1 per cent
    left in state 1             0.0                       exactly
    t=1 lifetime welfare        790.9978   (arm 3 790.8726, benchmark 791.3946)
    h_1 at t=1                  0.008747   (arm 3's transition 0.007713)
    h_1 at t=2                  0.012876   (arm 3's transition 0.010648)

The first two are the startup print and are a HARD check -- they are counts, not
equilibrium objects, so a compiler cannot move them. The last three are
equilibrium objects at an unconverged loop and are only worth reading as
"the same economy to two or three digits".

## WHAT THE T=5 PROBE IS ALSO FOR, and it is the reason to spend the time

It supplies the only MEASURED (price faced, price implied) pair the grandfathered
arm has, and the seed below needs it. Grandfathering leaves about 7.1 per cent of
the population exempt from conditionality, so participation along the path is
materially higher -- b rose 21.7 per cent against arm 3's transition at T=5 --
and a higher quantity implies a higher clearing price. On the supply side
p = shifter*V^(1/1.46), so the whole price path under grandfathering should sit
ABOVE the path the T=30 arm-3 secant measured.

**That shift is NOT estimated here.** Chaining the measured participation
elasticity (-1.8) onto the supply exponent gives about +6 per cent, and the
standing rule is to prefer a measured bracket to an elasticity and never to
extrapolate a slope past the pair that produced it. The T=5 probe's own
`drug quantity V=` and `distance_drug_market` at t=1 to t=4 measure it instead,
and the seed is shifted on that, or not at all.

What the probe CANNOT settle: whether the sign of the t=1 gap under this seed is
the grandfathering or the horizon. At T=5 the terminal condition sits on top of
t=1, which is the same defect T=60 exists to remove.

## THE T=60 PRICE PATH SEED, AND WHAT IN IT IS MEASURED

`seeds/drug_price_path_seed_t60.txt`, 59 entries for t=1..59; t=60 is the
boundary condition and the code pins it to arm 3's cleared 0.833490.

    t = 1..20    the T=30 run's measured secant roots, VERBATIM
    t = 21..59   0.83349 + 0.03940 * 0.894614^(t-20)

The first twenty are measurements: two real (price, implied) pairs per period,
every root strictly inside its own bracket, and the run they seeded came in at
`distance_drug_market` 0.031346 at t=1 against 0.21730 for the ramp, mean 0.01351
over 29 periods. They are used only out to t=20 because past that the T=30 run's
own boundary was pulling them: it forced p(29)=0.83349 on a period where h_1 was
still +63.9 per cent against a long run of +1.3, which is the whole reason T=30
was rejected.

**The decay rate is pinned on lambda_d and is not a shape I chose.** The T=30
run's disorder stock went 0.033610 at t=1 to 0.020800 at t=29 against a terminal
0.018460 -- 84.6 per cent of the journey, 15.4 per cent of the gap left. The
price is monotone in that stock, so the price gap above the terminal at t=29
should be about 0.154 of the t=1 gap. Solving the decay from t=20 through that
point gives rho = 0.894614, and the resulting path leaves a gap of 0.000512 at
t=59, which is inside the 5e-3 stopping rule on its own.

    t=1  0.92739   t=20 0.87289   t=29 0.84795   t=40 0.83774   t=59 0.83400

Against the T=30 seed this is HIGHER from t=21 on -- 0.84795 against 0.83349 at
t=29, 1.7 per cent -- which is the point: at T=60 those periods are no longer
pinned to the boundary and the economy is not near the terminal steady state
when they arrive.

**THIS IS A CONSTRUCTION, NOT A MEASUREMENT, PAST t=20**, and it must not be
quoted as one. It is a seed; the run's own per-period (faced, implied) pairs are
what locate the roots, by secant, on the reseed. The price moves 0.5 per cent a
loop and no faster -- `max_drug_price_move` is load bearing and is not to be
loosened -- so the seed is most of the answer and a reseed is how it is earned.

## WHAT MUST APPEAR IN THE T=60 LOG BEFORE ANYTHING IS BELIEVED

    TRANSITION GF: grandfathered= <mass>   with  left in state 1= 0.0
    grandfathered mass about 7.1 per cent of total population
    DRUG PRICE PATH seeded FROM FILE, entries read= 59 of 59
    HANDOVER IGNORED                       count 0
    peak RSS                               about 13.1 GB of 15
    the budget residual PRINTED AT LOOP 0  (lesson 15: a diagnostic must not
                                            share a gate with its instrument)

A short seed file is a silent half-failure: the code keeps the linear ramp for
the periods it could not read and says so in one line. `entries read= 59 of 59`
is the only thing that rules it out.
