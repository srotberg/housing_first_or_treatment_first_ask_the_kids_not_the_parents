# Bounds checks

One section per measured point. A section says which line of which batch was
run, and reports the moments asked for. A point whose invariants fail is
recorded here as a FAILURE and its numbers are not moments of anything.

## batch_kkk.txt line 4 -- KKK at rho_shock = 0.952 -- FAILED, NOT A MEASUREMENT

    bash code/run_one_point.sh ssi_floor_takeup=0.5 fixed_productivity=0 \
      kkk_s_deviation_bottom=3.35 sd_fixed_employment_newborn=0.59620 \
      sd_employment_surviving=0.32801 persistence_employment_surviving=0.952

Point `f661d96ff7`, model `8e0688e2d4`, run cold, 4 cores.

**The run exited 0 and produced no usable economy.** 14 of 16 invariants
FAIL. Most moments are NaN and the employed share of the homeless comes back
at **-1.97**, which is outside [0,1] and so is not a share. Nothing below is
a measurement of the model; the numbers are recorded only to show what the
failure looks like.

The two things that are NOT the cause, both checked:

* **The handover is clean.** `HANDOVER OK: 59 of 59 parameters applied`, and
  all six passed values are in the point file exactly as typed:
  `fixed_productivity=0`, `kkk_s_deviation_bottom=3.35`,
  `sd_fixed_employment_newborn=0.59620`, `sd_employment_surviving=0.32801`,
  `persistence_employment_surviving=0.952`, `ssi_floor_takeup=0.5`.
* **The productivity grid is finite and is the intended one.** The log reports
  `KKK productivity process live. sd of log y at age 1 = 0.76258`, against the
  0.763 that KKK_VS_SIGMA_Y.md predicts for the rho = 0.952 row. So line 4 is
  the arm it was meant to be. The seven nodes run 0.0564 to 7.1547, all finite.

### What was asked for

Bands first, as requested. Band = age band; `observed` is the data target.

| quantity | model | target/observed |
|---|---|---|
| homelessness rate, band 2 | 0.46048 | 0.003378 |
| homelessness rate, band 3 | 0.46435 | 0.002912 |
| homelessness rate, band 4 | **NaN** | 0.002496 |
| homelessness rate, band 1 | 0.49855 | 0.003161 |
| homelessness rate, band 5 | **NaN** | 0.000770 |
| homelessness overall (h_1) | **NaN** | 0.003990 |
| employed share of the homeless | **-1.96868** | 0.460 |
| income of the homeless | **NaN** | 0.191 |
| sigma_y, bottom half earnings share | 0.22588 | 0.172 |
| w_bot, net worth share bottom half | **NaN** | 0.025 |

DIAG line asked for, and it is finite:

    DIAG cheapest rental over lowest net income
      = smallest_house_size*rent(1)/net_income_lowest = 0.39134

### Why the finite-looking band numbers are still not results

Bands 1-3 print finite, but they are ~0.46 to 0.50 -- the model put **half the
population on the street at every age**, against a target near 0.003. The
invariant `the five age bands hold all of the homeless` is NaN, so the bands do
not even partition the homeless here. Read as a fan-out result this would say
the fan works 150 times too well; it says nothing of the kind.

### Where it breaks

Localised, not diagnosed -- no guess as to cause and no edit to the Fortran.

* The household solve completes (`time = 140.5` s) and the distribution
  iteration converges normally, down to `distribution distance = 1.58e-4`.
* The FIRST non-finite quantity is **`renter income` at age 26**, the earliest
  age in the model. At that same row `mass`, `homeless` and `sud` are all still
  finite (`mass = 2.000000`, the two beta types un-normalised).
* The first aggregate NaN is at the first distribution moment sweep:
  `DIST_MOM sweep= 0 mass= NaN wealth= NaN`. Only 2 such sweeps run and both
  carry NaN in mass.
* By the aggregation the whole age profile is NaN from 26 to 85.

So income goes non-finite before the distribution is ever summed, and the NaN
mass follows from it rather than the other way round.

### Bearing on the question the arm was asked to answer

**It does not answer it.** Line 4 was the strongest fan being measured and the
candidate mechanism for putting a middle-aged household with savings onto the
street -- bands 2-4 carry 0.00030 against 0.00879 observed, a factor of 29.
This run leaves that untested: bands 2 and 3 are unusable and band 4 is NaN.
The rho = 0.952 arm needs to be re-run once the NaN is understood, and until
then nothing should be concluded about whether the fan closes the middle-age
gap.
