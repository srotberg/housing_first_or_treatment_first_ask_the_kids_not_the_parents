# ARM 3 REPRODUCED, AND THE CEV PREDICTION HELD TO 0.003 PERCENTAGE POINTS

20 September, 23:49. `simulation_ended`, all invariants PASS, exit 0, no errors.
Re-solved cold in a fresh container on GNU Fortran 13.3.0, warm started from this
session's own benchmark at the converged price 0.833490 and pi_v 0.076347, with
`drug_market_adjuster = 0.1`.

Note the log line is `simulation_ended`, with an UNDERSCORE. Grepping for
"simulation ended" returns zero on a converged arm and reads as a crash.

## THE RESULT AGAINST results/arm3_convergence/CONVERGED.md

                        this run      archive       miss
    b                   0.045265      0.045287      -0.05%
    lambda_d            0.018415      0.018460      -0.25%
    h_1                 0.006521      0.006542      -0.32%
    price               0.834257      0.833490      +0.09%
    pi_v                0.075482      0.076347      -1.13%
    lifetime welfare  792.50392     792.5130        -0.001%
    CEV                 +3.4337%      +3.249%       +0.185pp   <- EXPECTED, see below

Nine blocks, 49 minutes, against the archive's eight loops and 36.

## IT PASSED ITS OWN ACCEPTANCE TEST, WHICH IS NOT THE SAME AS HITTING THE NUMBER

CONVERGED.md's test, set before that run: the movement must DECAY MONOTONICALLY
into the stop, and b must land inside the measured cycle band [0.04492, 0.04732].
Both hold here, and the decay is longer than the archive's:

    |db|   6->7  1.554e-04
           7->8  7.629e-05
           8->9  5.825e-06        monotone, and preceded by 7.153e-04

All three live rules inside at the stop, none of them by a whisker:

    CF moments   4.0080e-04   (rule 5e-4)
    drug market  3.6539e-03   (rule 5e-3)
    budget       1.8184e-02   (rule 2.5e-2)

The budget traced the same hump the archive recorded -- 2.7e-3, 2.9e-2, 4.3e-2,
4.6e-2, then 2.0e-2, 4.1e-4 -- peaking at 0.0457 against its 0.0573. That is the
cold value function, not a pi_v instability, exactly as CONVERGED.md concluded.

## THE CEV IS 0.185pp HIGHER THAN THE ARCHIVE'S AND THAT WAS PREDICTED IN ADVANCE

`results/transition_t60_gf/CEV_OFFSET.md` was committed BEFORE this run finished,
predicting +0.209pp off one measured quantity: this session's benchmark welfare
curve sits 0.0711 utils below n90's, and `calculate_welfare_gains` obtains every
CEV by inverting that curve, whose local slope at arm 3's welfare is 34.0 utils
per unit x.

The full reconciliation, now that the arm's own welfare is known:

    curve 0.0711 utils lower          +0.0711/34.0  =  +0.209pp
    arm welfare 0.0091 utils lower    -0.0091/34.0  =  -0.027pp
    ----------------------------------------------------------
    predicted                                          +0.182pp
    OBSERVED                                           +0.185pp

**Three thousandths of a percentage point.** The prediction was made from the
curve shift alone and the residual is the arm's own welfare difference, which was
not known when the prediction was written.

WHAT THIS SETTLES. The +0.185pp is a measuring-stick effect and not economics.
Arm 3's own lifetime welfare reproduces the archive to 1e-5 relative -- 792.50392
against 792.5130 -- so the ARM is the same object; what moved is the benchmark
curve it is differenced against, because n90 ran at kappa_x = 0.002 and this
benchmark ran at 0.8139. This chain is internally consistent where the archive
was not, and its CEV is therefore the better number, not a worse one. It is also
NOT comparable with +3.249% and must never be quoted beside it without this note.

## AND IT CONFIRMS THE VOUCHER FINDING IN ONE CONTAINER

The coordinator's hold rests on Treatment First not saving money. That was
established across two runs in two containers. Here it is as a controlled pair --
one container, one binary, one benchmark, which is what the standing rule asks
for:

                                                benchmark      arm 3      change
    govt_spending_on_housing_vouchers_2         0.69009699   0.68646288   -0.53%
    model_fraction_recieving_housing_vouchers   0.06301067   0.06222395   -1.25%
    probability_of_voucher (pi_v)               0.06753386   0.07548246   +11.8%

**Conditionality re-sorts who holds a voucher; it does not shrink the programme.**
pi_v rises 11.8 per cent while the fraction receiving falls 1.25, and total
spending falls half a per cent. So a transition that reports a surplus of about
0.69 from t=2 is losing the whole programme, and that now stands on this session's
own runs as well as the coordinator's.

Also worth recording: `govt_spending_on_housing_vouchers` WITHOUT the `_2` is
identically zero in both the benchmark and arm 3, and both names appear in
`net_govt_revenues`.

## FILES, AND ONE COUNT TO CHECK BEFORE THE TRANSITION

211 files named `counter_TF`, against 213 named `baseline_benchmark`. The four
large ones are present at byte sizes identical to the benchmark's:

    value_function1counter_TF.dat            308318400
    value_function2counter_TF.dat             27748656
    distribution_stationary1counter_TF.dat   265496400
    distribution_stationary2counter_TF.dat    23894676

The two-file gap is not assumed harmless: `check_transition_inputs.py` parses the
required list out of the Fortran and is the thing that settles it, and it is run
against the staged transition directory before any transition starts.
