# The drug targets are 26+; the comments beside them document 18+

22 September, found while writing `NSDUH_2024_SMI_by_SUD_code.txt`. The targets
are RIGHT. The shares quoted as their source are from a different universe, and
one sentence in the source is false. This matters now because the SMI channel
needs a conditional rate, and a conditional rate computed against the documented
shares would carry a denominator the model does not target.

## What the file actually contains

`data/NSDUH_2024.dta` is a 17-variable extract of the 2024 public use file,
58,633 observations, ALL AGES -- it is not pre-restricted. `svyrdudany` takes
1, 2, 3 and 4, with 4 the none category; `age3` runs 1 to 11 on NSDUH's bands,
so 18+ is `age3>=4` and 26+ is `age3>=7`.

Weighted by `analwt2_c`, the two cuts the model uses:

    universe            n        use          SUD
                              (1,2,3)        (2,3)
    all ages         58633     0.0982       0.0443
    18+  age3>=4     47299     0.1014       0.0454
    26+  age3>=7     33163     0.0890       0.0368

## Which one the model is built on

**26+, and it is exact.** The targets in the Fortran are

    participation_rate_data = 0.10502   = 0.089  * 1.18
    sud_rate_data           = 0.043424  = 0.0368 * 1.18

and 0.0890 and 0.0368 are the 26+ cut to every digit printed. Their ratio is
0.0368/0.0890 = 0.4135, which is the author's *"SUD has to be about 41% of b"*,
and 0.043424/0.10502 = 0.4135 confirms it survives the scaling.

That is the right universe: model age one is data age 26, fixed by the author's
rule of 13 September and carried by `child_at_home_last_index`.

## What the comments say instead

Both comments name the universe correctly and then quote the 18+ share:

> NSDUH 2024, adults 26 and over, ANY drug use disorder including mild,
> svyrdudany in (1,2,3). Weighted share 0.1013.

> NSDUH 2024, adults 26 and over, MODERATE OR SEVERE drug use disorder,
> svyrdudany in (2,3) on the file in data/. Weighted share 0.0454.

0.1013 and 0.0454 are the 18+ cut. Scaling THOSE by 1.18 would give 0.11953 and
0.053572, which are not the targets in use. The arithmetic in the comments uses
0.089 and 0.0368; only the quoted shares are wrong.

**And one sentence is false.** The SUD comment says of the old value:

> It was 0.0368, which matched no cut of that variable.

0.0368 IS a cut of that variable -- it is `svyrdudany in (2,3)` at `age3>=7`,
which is the cut the same sentence's own comment says it uses. The 18+ figure
was computed, the 26+ figure did not match it, and the conclusion drawn was that
the 26+ figure matched nothing.

The 18+ ratio is 0.4477 rather than 0.4135, which is the tell: had the two been
the same universe the ratio would not have moved.

## Why this had to be found before the SMI extract and not after

The obvious way to compute the comorbidity is to reproduce the documented 0.1013
and 0.0454 first, as a check that the extract is right, and then condition on
SMI. That reproduces at 18+ -- so the check PASSES on the wrong universe, and
every conditional rate after it is built on a denominator the model does not
target, including 18 to 25 year olds in a model whose youngest household is 26.
Drug use is highest in exactly that band, so the error is not small and it is
not random.

`NSDUH_2024_SMI_by_SUD_code.txt` therefore restricts to `age3>=7` and prints the
two population rates first, with 0.0890 and 0.0368 stated as the values that
must appear before anything below them is used.

## What is NOT claimed here

No target moves. The calibration is unaffected. This is a documentation defect
plus one false sentence, and the fix is to correct the two comments and the
data appendix, which is the author's call on a frozen source.
