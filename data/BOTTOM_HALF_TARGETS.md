# Bottom-half targets for the single-type restructuring

**READ THE TABLE, NOT THE HISTORY.** Three of these numbers were reported wrong
before being corrected; the corrections log at the bottom records what moved and
why, so an older number quoted elsewhere can be traced. The table is authoritative.

Population: households that cannot accumulate beyond 1.5 x average income. That
cap admits **52.0 per cent** of households in SCF 2022 (median net worth is
1.363 x mean income), so it delivers the bottom half without conditioning on it.
STATE IT AS THE CAP, not as a sample cut -- being in the bottom half of wealth is
partly caused by addiction and homelessness, so selecting on it is selecting on
an outcome the model explains. The cap has no such problem.

## The targets

| moment | was | becomes | how |
|---|---:|---:|---|
| `beta` wealth/GDP | 3.0-4.5 | **0.8216** | SCF: bottom half's net worth / their own income |
| `gamma` housing/expenditure | 0.268 | **0.2051** | SCF: their housing cost / their own income |
| `h_2` >50% of income on housing | 0.101 | **0.1307** | SCF -- BUT SEE WARNING BELOW |
| `sigma_y` bottom-half earnings share | 0.172 | **removed** | meaningless when the model IS the bottom half |
| -- replaced by sd(log earnings) | -- | **0.8791** | SCF `wageinc`, age<65, earnings>0 |
| `w_bot` bottom-half wealth share | 0.025 | **removed** | 1.0 by construction |
| `pi_eu` unemployment | 0.049 | **0.0683** | SCF ratio 1.3947 x the official 4.9% |
| `tau_l` average labour income tax | 0.224 | **0.0546** | model's own schedule, aggregate, see below |
| `h_1` homelessness | 0.00399 | **0.00798** | x2 -- ASSUMED, not measured |
| `cbar` food stamps / income | 0.0042 | **0.0209** | / 0.2006, their share of income |
| `b` drug users | 0.089 | **x1.31 or x1.59** | NSDUH -- depends on the drug concept |
| `lambda_d` disorder rate | 0.0368 | **x1.31 or x1.59** | NSDUH -- same |
| `theta`, `emp_homeless`, `lambda_m`, `mu_H`, `tau_u`, `pi_V` | -- | **unchanged** | all conditional on homeless/addicted/eligible |

Underlying quantities, SCF 2022, households ranked by `networth`, weighted by
`wgt`, cut at the weighted median:

    bottom half's share of all income      0.2006
    bottom half's share of all net worth   0.0220   (vs the old w_bot target of 0.025)
    their mean income / population mean    0.4012
    their income spread p90/p10            7.50     (population 12.11)

## THE SCALING RULE, and why it is not one rule

    headcount shares of the population        x 2
    anything normalised by income             / 0.2006
    conditional on homeless/addicted/eligible unchanged
    drug use                                  x1.31 or x1.59, NOT x2

Food stamps doubles only if the bottom half earned half the income. It earns a
fifth. And drug use scales by neither, because it is not concentrated the way
homelessness is.

## THE ONE PLACE THE RESTRUCTURING CAN MOVE A GAP

For homelessness the rescaling CANCELS -- the model's rate doubles and so does
the target, so the gap is unchanged at +652%. The restructuring buys speed and
parsimony, NOT a fix for the block that is failing.

Drug use is the exception. From NSDUH 2024, past-year use disorder:

    measure                       whole   bottom half   ratio   share of cases in bottom half
    all six substances, 12+       0.0793     0.1001      1.263        0.632
    all six substances, 26+       0.0689     0.0906      1.314        0.657
    HARD DRUGS only, 26+          0.0130     0.0207      1.593        0.797

Only 63-80 per cent of drug use disorder is in the bottom half, so the target
scales by ~1.3-1.6 while the MODEL's rate scales by however concentrated the
model makes it. If the model treats drug use as more of a poverty phenomenon
than the data does, restricting to the bottom half makes `b` and `lambda_d`
WORSE. **The model's own concentration has never been measured and should be,
before this is built.**

## Two targets still outstanding

- `p_m`, the SMI population share, needs the same treatment as drug use: SMI's
  concentration in the bottom half, which has not been measured.
- `aleph`, value of life over income, is income-normalised, so its target moves
  with the denominator -- but a value of life does not shrink because the
  household is poor, so a naive /0.2006 is probably wrong. Needs thought rather
  than arithmetic.

## Warnings that belong in the paper, not just here

**THE SCF DOES NOT SAMPLE THE HOMELESS.** It surveys occupied housing units. So
every bottom-half statistic above is the bottom half of HOUSED households, and
the x2 for `h_1` rests on an assumption -- that essentially all homelessness is
in the bottom half -- that this survey cannot test. The homelessness target
itself comes from HUD point-in-time counts, a different frame. R1 already
complained about data provenance; this needs a sentence.

**`h_2` CHANGES SURVEY.** The standing 0.101 is CEX severe cost burden. The
0.1307 above is SCF, with housing cost as 12*rent for renters plus 12*mortpay
for owners -- no property tax, insurance or utilities, and a payment rather than
a user cost. The whole-population SCF version is 0.0783 against the CEX 0.101,
so THE TWO ARE NOT INTERCHANGEABLE. Either recompute the bottom-half burden in
CEX, or change source deliberately and say so.

**THE DRUG CUT IS BY INCOME, NOT WEALTH.** NSDUH has no wealth variable, so the
1.3-1.6 factors are bottom-half-by-income. The design is bottom-half-by-wealth.
They are different populations.

**THE NSDUH MEASURE IS ILLICIT DRUGS ONLY** -- marijuana, cocaine, heroin,
hallucinogens, inhalants, methamphetamine. No alcohol, no prescription opioid
misuse. Whatever produced the 0.089 and 0.0368 targets needs to be checked
against that, because marijuana alone is 0.0717 of the 0.0793.

## How tau_l = 0.0546 was obtained

The SCF has no after-tax income and no tax variable -- 357 columns, none of them
tax. So the rate comes from the MODEL's own schedule,
`T(y)=max(y-lambda*y^tau,0)` with lambda=0.7522432 and tau=0.85 and both the
exemption and standard deduction zero, applied to the SCF income distribution.

The normalisation is not free, and taking the ratio does NOT make it free: the
schedule is nonlinear, so the bottom/whole ratio moves from 0.71 to 0.16 as the
income scale moves from a quarter of mean income to four times it. The
principled choice is the scale under which the model's OWN whole-economy target
holds: **2.886 x mean income**, at which the whole-population aggregate rate is
0.2240 by construction and the bottom half's is **0.0546**.

`tau_l` is an AGGREGATE in the model -- line 14196, revenue over income -- so the
aggregate is the right object. Evaluating the schedule AT the bottom half's mean
income gives exactly **zero**, because the schedule's zero-tax threshold is
`y* = lambda^(1/(1-tau))` = 0.1499 and their mean is 0.1390, 7.2 per cent below
it. That is a real feature worth a sentence in the paper -- this population sits
at the income tax threshold -- but it is thin, 1.1 per cent of income, so do not
lean on the exact zero.

## Corrections log

- `tau_l`: reported **0.1142**, then the author's proportional 0.224x0.4012 =
  0.0899 was called too low. Both wrong. 0.1142 was an artefact of normalising by
  mean income; 0.0899 is too HIGH, not too low, because the schedule has a
  zero-tax region at the bottom. **The answer is 0.0546.**
- sd: reported **0.8112** from total household `income`, which includes capital
  income and transfers and keeps retirees who have no productivity draw.
  **The answer is 0.8791**, from `wageinc` restricted to earners under 65.
- drug scaling: reported **1.26** from all six substances at ages 12+. Marijuana
  is 90 per cent of that measure and the model starts at 26. **The answer is
  ~1.59 for hard drugs at working age**, or 1.31 if marijuana is meant to be in.
