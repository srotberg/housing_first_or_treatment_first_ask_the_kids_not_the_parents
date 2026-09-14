## 14 September 04:45 UTC -- THREE MOMENTS HAD NO INSTRUMENT, AND THE DEATH
## PENALTY AT 2 FIXED y_u

**THE PATTERN OF THE NIGHT.** Three of the moments on the author's first-block
list were reporting a visible gap with nothing behind them, each for a different
reason, and none of it was detectable from the gap table:

    moment                    instrument                  why it could not move
    SUD share of homeless     multiple_find_if_addicted   adjuster held at 0
                              mult_of_probs_emp_if_add    live, but AT ITS FLOOR
                                                          and the moment is above
                                                          target, so the step asks
                                                          it to go lower
    drug spending share       relative_share_of_addiction hold_theta=1, a PARAMETER
    SMI share of homeless     zeta_DI                     adjuster 0, and the
                                                          author set zeta_DI=0
                              lambda_m                    retired bracket, 0
                              kappa_uem                   zeroed by the FIRST
                                                          BLOCK FREEZE

A gap table cannot show this: every one of them prints a model value, a target
and a per cent, and looks exactly like a parameter that is trying and failing.
**A moment is only being calibrated if something with room is moving it**, and
that has to be checked separately from the gap.

kappa_uem also did NOT need rewiring, contrary to what was said in chat at
04:30: its update already scores model_smi_share_of_homeless against
smi_share_of_homeless_data. Only the MOMENT print beside it is still labelled
"employment given SMI", which is what caused the misreading.

**THE DEATH PENALTY AT 2 FIXED y_u**, on the author's *"i think you need to
lower the death penalty to maybe 2"* and *"you should allow kappa_phid to be as
low as 1"*. Measured at aleph 110, theta 0.075, b 3e-5:

    y_u   income of drug users   0.6879   target 0.7400    -7%

against 0.4094 and -45 per cent at kappa_phi_d = 8. It was the worst-behaved
moment in the block and it is now the second best. kappa_phi_d_level_lo was a
PARAMETER fixed at 2 while the handover's own clamp floored at 1, so the two
disagreed and the tighter one won silently inside the update.

**C BAR IS REACHABLE AND THE EARLIER CLAIM THAT IT IS NOT WAS WRONG.**
Eligibility is y < cbar/taper with taper 0.3, so the question is only which
groups clear the bar:

    group                       income    cbar needed to admit them
    homeless                    0.017          0.005
    unemployed, bottom node     0.055          0.017
    employed, bottom node       0.111          0.033
    unemployed, average worker  0.334          0.100

At cbar = 0.0276 the cutoff is 0.092, 13.8 per cent of average labour income,
which admits the homeless and the bottom-node unemployed and nobody else -- one
to two per cent of households against SNAP's twelve. Carrying 0.42 per cent of
output on the 4.9 per cent unemployed needs an allotment of 0.100 each and their
eligibility only begins at 0.100, so **cbar is about 0.20**.

That is four times the 0.047 the max-allotment diagnostic implies -- but that
diagnostic is NOT a scored target, it is a line added to the moment print. The
only scored moment is food stamps over output against 0.0042, and 0.20 hits it.
What it buys is the right aggregate with the wrong distribution: an allotment
near 30 per cent of average labour income where SNAP's is 4, paid to a sixth as
many households. **The binding cause is the 50 per cent UI replacement**, which
leaves an unemployed worker at 0.334 and therefore ineligible at any plausible
cutoff. That is a fact for the paper, not a reason to refuse the number.

**PI_EU CANNOT BE SOLVED BEFORE THE OTHER TWO.** The author's block is *"pi_eu
should be chosen so that about 25% of the homeless have SUD and 25% have SMI and
the unemployment rate is 4.9%"* -- three moments, three instruments, and they do
not separate, because the homelessness shares depend on who loses work and the
unemployment rate depends on who is disabled by SUD and SMI. Total unemployment
is not a clean signal for separation_rate on its own: it read 39 per cent LOW at
kappa_phi_d 8 and 26 per cent HIGH two hours later, entirely from the drug block
moving underneath it.

## 14 September 03:55 UTC -- BEST POINT ON THE CURRENT MODEL.
## aleph = 110, b = 0.00035. DRUG USE IS 2.6 PER CENT OFF.

    moment                       model      target     gap
    b      total drug users     0.08670    0.08900    -2.6%
    lambda_d disorder rate      0.03424    0.03680    -6.9%
    aleph  VSL / income        71.65      80.00     -10.4%
    y_u    income of drug users 0.4094     0.7400    -44.7%

Three of the four drug-block moments inside eleven per cent, from a margin that
read 0.61 per cent at 03:25 and 44.9 at 02:35.  Found by two loop-0 scan legs,
one parameter per point, which is the method the block skipped.

**VSL DEPENDS ON USE FAR MORE THAN ON aleph, and that is what made the point
findable.**  At aleph held at 110:

    users     VSL/income
    26.8%       63.6
    16.1%       64.4
     8.67%      71.65
     0.61%      94.3     (block1, aleph 111.3)

Flat between 27 and 16 per cent, then climbing steeply below 16.  So the earlier
readings -- 48 to 60 at aleph 80, flat in b -- were taken on the FLAT part of
this curve and the aleph = 137 they implied was an artefact of reading a flat
segment.  The target of 80 sits inside the climbing part, at single-digit use,
which is where the b target is too.  The two moments are far closer to
compatible than any point tonight suggested.

**WHAT CLOSES THE REMAINING TEN PER CENT.**  Ratio over aleph is 71.65/110 =
0.651 at the target use level.  Holding that, VSL = 80 wants aleph = 123, and at
aleph 123 use falls so b must come down with it -- roughly b = 2.5e-4 to 3e-4 on
the local elasticity.  That is leg 3.  It is an extrapolation and it is written
here as one; the scan measures it.

**y_u IS THE ODD ONE OUT AND IT IS NOT b's TO FIX.**  It falls monotonically in
b -- 0.606, 0.563, 0.497, 0.426 at aleph 80, and 0.409 here -- so it wants low b
while use wants high b.  kappa_phi_d owns it, and the author's rule is that y_u
below target means kappa_phi_d comes DOWN.  Block 1 loop 1 did exactly that
(8 -> 7.992, "LOWERED: y_u is below target").  At 0.1 per cent a loop a 45 per
cent gap is out of reach, so kappa_phi_d needs the same treatment aleph and b
just had: a measured bracket before the block, not a capped walk inside it.

## 14 September 03:40 UTC -- SCAN LEG 1, aleph HELD AT 80. THE DRUG BLOCK IS
## SOLVABLE, AND THERE IS NO SUCH THING AS "THE" ELASTICITY OF USE IN b

Four loop-0 points, aleph fixed at 80, b alone moving.  One parameter per point,
the wide test first, which is ENGINE.md rule 1 and was skipped before block 1.

         b     users    lambda_d    VSL/income    y_u    elasticity
    0.00020    33.1%     0.1308        59.5      0.606
    0.00035    23.8%     0.0959        48.3      0.563     -0.59
    0.00050    16.0%     0.0642        48.4      0.497     -1.12
    0.00080     7.81%    0.0316        56.7      0.426     -1.52
    TARGET      8.9%     0.0368        80.0      0.740

**b = 0.0008 PUTS USE WITHIN TWELVE PER CENT OF TARGET**, and the disorder rate
within fourteen.  On the local elasticity b = 0.00073 hits both.  This is the
first point on the current model where the drug block is close, and it is the
margin the calibration has been failing on for weeks.

**THE ELASTICITY IS NOT A NUMBER, IT IS A FUNCTION.**  It runs -0.59, -1.12,
-1.52 across a factor of four in b, and the -1.64 recorded at 02:35 was measured
at a different aleph entirely.  Two projections were made tonight off a single
segment -- b = 0.0019 off the flattest, b = 0.00045 off the -1.64 -- and both
were wrong by more than a factor of two.  THE STANDING RULE IS RIGHT AND IT
EARNED IT AGAIN: prefer a measured bracket to an elasticity.

**VSL IS NOW THE BINDING MOMENT AND b CANNOT MOVE IT.**  At aleph = 80 the ratio
reads 48 to 60 and is U-SHAPED in b, with a minimum near b = 0.0004, against a
target of 80.  So the earlier story -- that fewer users dying pulls the average
up, monotonically -- is WRONG, and the aleph = 104 figure extrapolated from it
at 03:33 should be ignored.  Both the numerator and the denominator of
VSL/income are equilibrium objects and they do not move together with use.

What survives is a bracket.  Ratio over aleph, at every point now on the current
model:

    aleph   users    ratio/aleph
     56.7   44.9%       0.720      cand1
     80     33.1%       0.744
     80     23.8%       0.603
     80     16.0%       0.605
     80      7.81%      0.709
    111.3    0.61%      0.847      block1 loop 1

Between 0.60 and 0.85, so a ratio of 80 wants aleph somewhere in 95 to 130.
Leg 2 holds aleph at 110 and scans b DOWNWARD -- 1e-4 to 5e-4 -- because
aleph 111.3 at b = 8.05e-4 gave 0.61 per cent use.  That closes the 2x2: the
users = 8.9 per cent locus is known at aleph 80, and leg 2 gives it at aleph
110 together with the VSL there.

**AND y_u FALLS IN b** -- 0.606, 0.563, 0.497, 0.426 against a target of 0.74 --
so it wants LOW b while use wants high b.  y_u is kappa_phi_d's moment, not b's,
but the conflict is real and kappa_phi_d will be pulling against b in the block.
Worth watching rather than acting on yet.

## 14 September 03:25 UTC -- BLOCK 1, LOOP 1. TEN INSTRUMENTS LIVE AND MOVING,
## AND DRUG USE COLLAPSED BECAUSE TWO CORRECTIONS WERE TAKEN AT ONCE

The first block ran with the ten instruments the author named -- aleph, b,
onset, kappa_ued, h_1, pi_eu, kappa_phi_d, omega_c, tau_u, pi_V.  All ten moved
on loop 1: h_1 1.19585e-3 -> 1.20183e-3, b 8.050e-4 -> 8.0098e-4,
utility_cost_of_treatment 8 -> 8.08, kappa_phi_d 8 -> 7.992, and
voucher_probability 0.0443 -> 0.04452.  75 of 75 handover parameters applied,
no clamps.  Loop time about four minutes at one beta type.

    ON OR NEAR TARGET     model      target     gap
    p_m                 0.04797    0.04797    +0.0%
    tau_l               0.22380    0.22400    -0.1%
    theta               0.14215    0.14098    +0.8%
    beta                3.03752    3.00000    +1.3%
    kappa_ued           0.16583    0.16250    +2.0%
    mu_H                1.43822    1.47321    -2.4%
    sigma_y             0.17677    0.17200    +2.8%
    lambda_m            0.23143    0.25000    -7.4%
    emp_homeless        0.51560    0.46000   +12.1%

    THE BLOCK'S OWN     model      target     gap
    aleph              94.31242   80.00000   +17.9%
    h_1                 0.00664    0.01000   -33.6%
    pi_eu               0.02972    0.04900   -39.4%
    sud_homeless        0.06177    0.21700   -71.5%
    y_u                 0.19035    0.74000   -74.3%
    pi_V                0.03976    0.26600   -85.1%   (cold start, see 03:20)
    b                   0.00611    0.08900   -93.1%
    lambda_d            0.00193    0.03680   -94.8%
    tau_u               0.51774    0.24500  +111.3%

**DRUG USE COLLAPSED, AND IT WAS AN ERROR OF METHOD, NOT OF THE MODEL.**  Both
of the corrections taken from cand1 were applied at the same time:

    aleph  56.7   -> 111.2    measured holding b at 0.0003
    b      0.0003 -> 0.000805 measured holding aleph at 56.7

Each was measured with the OTHER held fixed, and BOTH PUSH USE THE SAME WAY --
a higher value of life makes the drug's mortality matter more, and a higher b
prices use directly.  Applied together they compound: cand1 had 44.9 per cent of
the population using, this has 0.61, an overshoot of a factor of fifteen.  This
is the same mistake ENGINE.md rule 1 was written about, in the other direction:
a correction read off a one-parameter measurement is only valid one at a time.

**THE CAPS CANNOT UNDO IT, AND THAT IS THE REASON THE RUN WAS STOPPED.**  At the
author's caps -- 0.1 per cent a loop for aleph, 0.5 for b -- b needs a factor of
5.4 (338 loops) and aleph about 12 per cent once use is right (120 loops).  At
four minutes a loop that is twenty-two hours to return to a point a twenty
minute scan locates.  The run was killed at loop 1; no repo .dat was touched,
the run lived entirely in the scratchpad.

**THE TWO POINTS DO BRACKET THE TARGET ON BOTH MOMENTS**, which is worth
keeping:

    point          aleph        b       users    VSL/income
    cand1           56.7   0.000300     0.4494     40.80
    block1 L1      111.3   0.000805     0.0061     94.31
    TARGET                              0.0890     80.00

They lie on a line, so they identify one degree of freedom and not the 2x2.
Balanced log interpolation along it puts both moments about twenty per cent off
at aleph 80, b 4.6e-4, which is the neighbourhood the scan is searching.

**AND THE COUPLING RUNS THE OTHER WAY TOO, WHICH HELPS.**  VSL ratio over aleph
is 0.72 at 45 per cent use and 0.85 at 0.6 per cent, because users dying pull
the average down.  So aleph does not have to travel the full 18 per cent: once b
puts use back at 8.9 per cent the ratio falls on its own.

**THE SCAN RUNNING NOW** holds aleph at 80 and moves b alone over
2e-4, 3.5e-4, 5e-4, 8e-4, reading each at loop 0.  One parameter per point, the
wide test first.

## 14 September 03:20 UTC -- THE 4.2 PER CENT WAS LOOP 2, NOT THE ANSWER.
## PI_V IS TWENTY PER CENT LOW, NOT EIGHTY-FOUR

The row `pi_V 0.0420 0.2660 -84%` in the entry below is WRONG and is corrected
here.  4.20 per cent is what `cand1` read on its SECOND loop, before the
distribution had built a voucher stock from a cold start.  The run's own
trajectory, one reading per scored loop:

    loop   pi_V        eligibles getting a voucher
      2    0.036132          4.20%
      5    0.036493         18.28%
      8    0.036858         22.77%
     11    0.037227         23.20%      target 26.60%

pi_V moved 3 per cent across those loops and coverage moved by a factor of
5.5, so the movement is the DISTRIBUTION CONVERGING, not the instrument.  The
last two steps are +4.49 and +0.43 points, a ratio of 0.096, so the limit is
about 23.25 and loop 11 is converged.

`calibration_report.py` reads the LAST loop and had it right the whole time --
`voucher_probability 0.231977 vs 0.266, off by 12.8%`.  The -84 per cent was a
hand-read of the first loop in the log.  THE LESSON IS THE PROCEDURE: a moment
quoted off anything but the last loop is a cold-start artefact, and the tool
that knows this already exists.

**WHAT PI_V SHOULD BE, from the chain the code actually implements.**  Entrants
to eligibility hold nothing, because crossing the line revokes; non-holders
acquire at hazard pi and leave eligibility at hazard 1/L.  So

    N(pi + 1/L) = (1/L)E   ->   holder share  s = pi*L/(pi*L + 1)

At pi = 0.0369 the model gives s = 0.2320, so pi*L = 0.3021 and the mean
eligibility spell is L = 8.19 PERIODS.  For s = 0.266, pi*L = 0.3624 and

    pi_V = 0.0443

a rise of about twenty per cent.  The author's judgement that 0.283 was "way
too high" was right, and the 0.283 came from treating the stock as a flow.

Left LIVE in the first block at its existing 1 per cent cap rather than pinned
at 0.0443, so the number that gets pinned is measured rather than computed.

## 14 September 03:05 UTC -- THE VOUCHER TRANSITION HAS THREE UNWRITTEN ROWS,
## AND A CLASS OF DIVISIONS THAT SIGFPE ON AN EMPTY POPULATION

Chasing the coverage number turned up two real defects, neither of which was
causing it.

**THREE ROWS OF `voucher_probabilities` ARE NEVER ASSIGNED** on the benchmark
path: `(1,0,1,:)`, a holder losing the voucher while still eligible;
`(1,1,0,:)`, a holder keeping it with income above the threshold; and
`(0,1,0,:)`, a non-holder acquiring one above the threshold.  All three are
complements of rows set to one, so zero is correct -- and zero is what they
read, but only because the array is module scope and the loader clears static
storage.  That is an accident of storage class, not a statement of the model,
and the block already zeroes the exclusion rows by hand for exactly this
reason.  The whole array is now zeroed before any row is written.

**UNGUARDED DIVISIONS BY CONDITIONAL-POPULATION MASSES.**  The
`-finit-real=snan -ffpe-trap=invalid,zero,overflow` build trapped three times in
a row, each on a different unguarded division by a population that can be
empty: `total_addited_1` at 17661, `total_addited_1` again at 17775, and
`model_average_drug_spending_experimenters` at 36771.  Finding them one SIGFPE
at a time is the wrong method, so the class was swept instead: a denominator
that is a CONDITIONAL POPULATION gets a guard, a denominator that is an
economy-wide aggregate (GDP, total net wealth, sum_of_distribution,
total_govt_revenues) does not.  Sixty-odd sites.

**FORTY-ONE OF THEM WERE INVISIBLE TO A LINE-BY-LINE SEARCH**, because the
division is written with the `/` ending one line and the divisor opening the
next under a continuation `&`.  That is the house style for these
normalisations, so a grep for `/name` finds a minority of them.  Any future
sweep of this file has to join continuations first.

## 14 September 02:35 UTC -- THE FIRST LIVE ECONOMY. SIX MOMENTS ON TARGET,
## AND THE TWO THAT HAVE BEEN FIGHTING US ARE AMONG THEM

`cand1`: the 7 September vector with tau_ell solved at 0.871398, theta pinned at
0.16, aleph at 56.7, b at 0.0003, h_1 tied to h_2, child gap measured.  73 of 73
parameters applied.  THE FIRST POINT TONIGHT WITH A LIVE DRUG ECONOMY, so the
first whose moments mean anything.

    ON TARGET            model      data      gap
    tau_l               0.22264   0.22400    -0.6%
    pi_eu               0.05002   0.04900    +2.1%
    sigma_y             0.17645   0.17200    +2.6%
    beta                3.10267   3.00000    +3.4%
    p_m                 0.05308   0.05130    +3.5%
    y_u                 0.67261   0.74000    -9.1%

**UNEMPLOYMENT IS ON TARGET.** 5.00 per cent against 4.9, where it read 0.094
per cent at source defaults -- a factor of fifty-three -- and where every
emp_homeless reading tonight was worthless because of it.

**AND THE TAX SOLVE HELD.** -0.6 per cent with every other parameter moved,
which is the real test of the claim that inelastic labour makes it algebra.

    STILL WRONG         model      data      gap
    b (users)           0.4494    0.0890   +405%
    lambda_d            0.1737    0.0368   +372%
    aleph              40.80     80.00      -49%
    sud_homeless        0.5831    0.2170   +169%
    emp_homeless        0.3004    0.4600    -35%
    h_1                 0.01225   0.00700   +75%
    pi_V                0.0420    0.2660    -84%
    cbar                0.00046   0.00420   -89%
    tau_u               0.0506    0.2450    -79%
    theta               0.1029    0.1410    -27%

**THE AUTHOR PREDICTED THE CENTRAL RESULT AND THE MODEL DELIVERED IT.** Their
words: *"you will have to lower aleph quite a bit and then b will have to
rise"*.  Halving the value of life took drug use to 45 PER CENT of the
population.  A lower value of life makes the drug's mortality matter less, use
rises, and b has to rise to pull it back.  That is the model's own central
mechanism showing up in its own calibration.

**ALEPH IS NOT PROPORTIONAL AND THE TWO POINTS PROVE IT:**

    parameter 117.28  ->  VSL ratio 165.43   at  0% users
    parameter  56.70  ->  VSL ratio  40.80   at 45% users

The map moves with use, because drug users dying pulls the average down.  So
aleph and b are coupled in BOTH directions and neither can be solved alone.
56.7 overshot; scaling from the second point gives 111 as the next ITERATE.

**THETA IS ANSWERABLE AT LAST.** With use real, the drug spending share reads
0.1029 against 0.14098 -- 27 per cent low at theta = 0.16, and no longer the -1
empty-population sentinel.  Whether 0.16 can close it depends on how the share
moves when b cuts use from 45 per cent to 9.  That is the author's question from
02:00 and it now has a number attached.

**CORRECTIONS TAKEN, both from measured elasticities rather than guesses:**
b 0.0003 -> 0.000805 (elasticity of users in b is -1.64, so a 5.05x cut in use
needs 2.68x on b -- and 0.0008 is what the author guessed by eye two hours
earlier), aleph 56.7 -> 111.2.  Running as `cand2`.

