# The optimal voucher clawback

The author, 10 September: *"instead of giving a voucher up to 30% of income you
can say that if you have sud it covers only up to 50%"*, and then *"I want to
test what the optimal voucher clawback is to maximize welfare"*.

## What was built

`kappa_c` in the stylized model: the tenant's share of the rent when the
household carries the disorder. It makes conditionality a ONE PARAMETER FAMILY
with both existing policies as endpoints rather than a switch:

    kappa_c = kappa_r = 0.30    no penalty, identical to Housing First
    kappa_c = 1.00              the whole voucher withdrawn, identical to
                                Treatment First, and the default
    in between                  a graduated clawback

Two call sites carried the old binary rule and both are generalised:
`_states`, where a household with the disorder used to draw no voucher at all,
and `_p1_rmul`, where a period 1 household that chose to use lost it outright.

BOTH ENDPOINTS REPRODUCE THE ORIGINAL EXACTLY. Against the pre-edit file,
max|V1 difference| is 0.0 for Housing First and 0.0 for Treatment First at
kappa_c = 1.00, and the verdict at that endpoint reproduces the paper's own
numbers, 2.8801 - 0.0513 = 2.8289.

## The result: eight percentage points does the whole job

    clawback   tenant share   sud %    private %   extern %   TOTAL %
      0 pp         0.30       5.663      0.0000     0.0000     0.0000   <- HF
      2 pp         0.32       3.783      0.0267     0.9563     0.9297
      4 pp         0.34       2.457      0.0399     1.6304     1.5905
      6 pp         0.36       0.981      0.0485     2.3813     2.3328
      8 pp         0.38       0.000      0.0513     2.8801     2.8289   <- optimum
     70 pp         1.00       0.000      0.0513     2.8801     2.8289   <- TF

TREATMENT FIRST SPENDS SEVENTY POINTS OF CLAWBACK TO ACHIEVE WHAT EIGHT
ACHIEVES. Raising the tenant's share from 30 to 38 per cent for a household with
the disorder eliminates the disorder outright, and withdrawing the entire
voucher does no better.

## Why the stylized model understates the case for a clawback

Above 0.38 the schedule is FLAT: the private loss is 0.0513 per cent at a
clawback of eight points and at seventy. The threat deters everyone, so it is
never executed, and severity beyond the deterrence threshold is free.

That is exactly where the stylized model is weakest. Drug use there is a period
by period choice, so everybody can comply costlessly. In the quantitative model
addiction is a PERSISTENT STATE with a costly exit through treatment at 12.69
utils, so the threat IS carried out, on a stock of households that cannot comply
cheaply. Severity above the deterrence point is not free there; it is paid every
period by the people the policy is meant to help.

PREDICTION, to be tested: a graduated clawback strictly DOMINATES full
withdrawal in the quantitative model, by a margin that does not exist in the
stylized one. The change there is the same ten lines sized earlier -- replace
`housing_voucher_1 = 0` in calculate_housing_voucher_2 with the voucher computed
at a higher tenant rate, since that routine already receives the addiction state.

## A correction to the record

An earlier note in this session said the stylized model values a penalised child
at 264.3 per cent against the quantitative model's 50, and explained the gap by
its two period consumption equivalent denominator and the voucher means test
notch. THAT IS WRONG AND IS WITHDRAWN. 264.3 was a historical figure inside a
code comment describing an earlier state of the model. The current value is

    per_case = 50.86 per cent      against an income only bound of 31.58

which is a sensible 1.6 fold behavioural amplification, and it AGREES with the
quantitative model's 50 per cent. The two models do not disagree about the child
at all. The whole disagreement is the private loss, 0.051 per cent against
several points, and the reason is the persistence of addiction.
