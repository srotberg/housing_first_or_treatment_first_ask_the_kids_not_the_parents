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

