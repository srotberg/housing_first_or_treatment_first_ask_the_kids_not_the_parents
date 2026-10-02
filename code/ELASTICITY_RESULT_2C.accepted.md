# The 2 October elasticity run is accepted despite its check (1)

Accepted 2 October, 00:30 UTC, in the main session; the worker's file (ELASTICITY_RESULT_2C.txt) is
left exactly as it wrote it, check (1) marked FAILED.

What failed: check (1) asked every one of the 27 last-block moments of the re-solved benchmark to be
within 1e-3 (relative) of results/reference/hf_2c_omega_0.085/bench.log.gz. One was not:
sud_homeless (the SUD share of the homeless), 0.20223 against 0.20198, 1.22e-3. The other 26 are
within 4.9e-4, drug users b within 1.24e-4 and lambda_d within 4.9e-4.

Why that does not touch the elasticities:
- the check exists to catch a patch that changes the benchmark; the worker showed the drift starts
  in the first distribution sweep of block 1, before any patched line runs, and that the unpatched
  build reproduces the benchmark binary's md5. It is OpenMP run-to-run variation, the kind
  ELASTICITY_RESULT_BENCH.txt saw in its blocks 7-11;
- the elasticities are log ratios against the run's OWN base state, restored before each step
  (check (3): one median_income, users at start equal to MOMENT b to every digit; the null
  re-solve at the base price moves users by -1.0e-6), so a 1e-4 shift in the base does not enter;
- sud_homeless is not an input to the drug price response.

The author asked for the elasticities to be updated everywhere (1 October, about 21:20: "when you
have the drug participation and intensive elasticities update them in the paper everywhere they
appear"); this note is the record of using a run whose own check came out 0.22e-3 over the line.
The six steps are read from code/elast_2c.log.gz; the 2 per cent step is dropped as before (the
author, 30 September).
