# THE COLD-START BENCHMARK REPRODUCES THE ARCHIVE TO 0.19 PER CENT

20 September. The cold-start path had never been exercised: a container with
none of the 4.71 GB of .dat inputs, no gfortran in the image, and a benchmark
that had to be rebuilt from the repository alone. It works, and this is what it
reproduced.

## THE RESULT, AT BLOCK 14, AGAINST THE ARCHIVE BENCHMARK

    quantity     cold start    archive       gap
    b            0.081893      0.081740     +0.19%
    lambda_d     0.033685      0.033625     +0.18%
    h_1          0.0064614     0.0064583    +0.05%
    V            0.495359      0.494427     +0.188%
    shifter      1.617928      1.620015     -0.129%

`shifter` is the test that matters and it is not a fifth reading of the same
thing -- it is the ONLY number a counterfactual takes from the benchmark's drug
market, read once and held fixed, which is what makes the price rather than the
quantity endogenous. The identity behind it was re-derived here rather than
assumed: 0.494427^(-0.684932) = 1.620016 against the committed
1.62001478993009917495.

CONTROL.md bounds what an error there costs: x per cent on the shifter moves arm
3's price by x/(1+0.685*|dlnV/dlnp|), a divisor of 2.2 to 7.3 across the measured
elasticity range. At -0.129 per cent that is under 0.06 per cent on the price --
an eighth of one loop of max_drug_price_move.

## IT WAS SCORED PER BLOCK, NOT ONLY AT THE END

The standing no-op control is 1e-4 RELATIVE, and it cannot be used here: this is
gfortran 13.3 against whatever the archive was built with, and a cold start
rather than a restore. Levels cannot be scored that way and scoring them that
way would reject a correct reconstruction.

CALIBRATION_RECIPE.md section 3 records n90's own per-block MOVES for blocks 2
to 7. Those are ratios, so the level does not have to match for the shape to,
and they carry which of the four series binds. Measured against them:

    blk   this run    n90        ratio   binding
     2    2.074e-01   2.059e-01   1.01   y
     3    8.388e-02   8.497e-02   0.99   y
     4    3.820e-02   3.885e-02   0.98   y
     5    1.814e-02   1.859e-02   0.98   y
     6    8.807e-03   9.079e-03   0.97   y
     7    7.693e-03   8.973e-03   0.86   lambda_d

Block 7 is the one worth having: section 3's whole point is that y decays
geometrically and then hands over to lambda_d, which drifts rather than decays,
and that the run therefore ends at its cap. Both halves reproduced -- y fell by
a factor of about 0.45 a block and lambda_d took over at block 7.

Block 1 is not scored. The recipe rules it an artefact twice and it read b 11
per cent low, which is the expected size of that artefact.

## WHY IT WAS STOPPED AT BLOCK 14 RATHER THAN RUN TO THE CAP

Not because it converged. The block move was 3.008e-04 against a rule of 1e-4,
and the late ratios -- 0.93, 0.95 -- put it 23 blocks from the rule with 11
left. It was going to stop at the cap, and an earlier note in this session that
it would likely trip before the cap was wrong: that was read off one 0.21 ratio
which the next two blocks did not sustain.

It was stopped because its OUTPUT was superseded while it ran. a1da5ab commits
the archive benchmark's own .dat set, on the author's instruction that "both
arms come off the same benchmark and code", so the transition no longer reads a
re-solve. Eleven more blocks was two and a half hours of the only four cores to
produce files nothing would read, while arm 3 -- which is required, and which
the voucher-accounting hold does NOT block -- was waiting.

So this is a VALIDATION, complete as one, and not an input to anything.

## WHAT THE COLD-START PATH ACTUALLY NEEDS, beyond COLD_START.md

- gfortran is absent from the container image; gcc is there. apt-get
  install gfortran-13 and symlink it.
- git clone --depth 1 writes a refspec mapping ONLY main, so every later
  `git fetch origin <branch>` populates FETCH_HEAD and never creates
  origin/<branch>. Nothing can then tell what is pushed. Repair with
  git config --replace-all remote.origin.fetch '+refs/heads/*:refs/remotes/origin/*'.
- run_one_point.sh cannot solve this benchmark: it does not know
  frozen_stop_tolerance, frozen_stop_after_blocks, omega_c_is_pinned or
  freeze_all_but_omega_c, so a run launched through it never leaves the
  calibration loop and never writes the baseline_benchmark files.
- ~13.7 minutes a block on 4 cores, not the ~9 the recipe quotes.
