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

## The author's test, at RATIONED generosity

The author, 10 September: *"In the stylized model I want you to do it for
rationed tf. ... It would be interesting to first estimate the excess drug use
with it (comparing omega_c = 0 and = 1). And then see if the optimal policy
indeed reduces drug use by the same amount"*.

Both halves were run at the calibrated coverage rate, pi_V = 0.266, with `b`
HELD at its calibrated value in every cell. Holding it is deliberate and unlike
`internalise.py`'s `row`, which refits `b` at every omega: refitting would put
participation back on target and so destroy the very quantity being measured.

### Half one: the excess

    pi_V = 0.266,  Housing First      use        disorder
      omega = 0  (pure externality)   8.9010%     3.7139%
      omega = 1  (fully internalised) 0.0000%     0.0000%
      EXCESS                          8.9010 pp   3.7139 pp

Every point of drug use at rationed generosity is excess: a parent who valued
the child at par would not use at all. DELTA, the child's loss in lifetime
utility, is 0.332192 utils there against 0.287770 at universal cover, and the
per-case consumption equivalent is 54.33 per cent against 50.86.

### Half two: the answer is NO

    clawback   kappa_c     use     disorder   private   extern    TOTAL
       0 pp      0.30    8.9010%    3.7139%   0.0000%   0.0000%   0.0000%  <- HF
       2 pp      0.32    7.5588%    3.1099%   0.0100%   0.3281%   0.3182%
       4 pp      0.34    6.4193%    2.4105%   0.0169%   0.7081%   0.6912%
       6 pp      0.36    5.7309%    1.7462%   0.0199%   1.0690%   1.0491%
       8 pp      0.38    5.1891%    1.2217%   0.0218%   1.3539%   1.3321%
      10 pp      0.40    4.6760%    0.7267%   0.0232%   1.6229%   1.5997%
      15 pp      0.45    4.6223%    0.6667%   0.0252%   1.6554%   1.6303%
      20 pp      0.50    4.5666%    0.6499%   0.0271%   1.6646%   1.6375%
      30 pp      0.60    4.4488%    0.5756%   0.0308%   1.7049%   1.6741%
      40 pp      0.70    4.3202%    0.5174%   0.0337%   1.7366%   1.7028%
      55 pp      0.85    3.8558%    0.4440%   0.0372%   1.7764%   1.7392%
      70 pp      1.00    3.5727%    0.3793%   0.0408%   1.8116%   1.7708%  <- TF

THE OPTIMAL CLAWBACK AT RATIONED GENEROSITY IS FULL WITHDRAWAL, AND IT STILL
DOES NOT REACH THE SOCIAL OPTIMUM. Use falls from 8.9010 to 3.5727 per cent, so
the instrument closes 5.33 of the 8.90 points of excess, three fifths of it. The
schedule is still RISING at its own endpoint: there is no interior optimum to
find, because the constraint is not the severity of the penalty.

### Why, and why it reverses the design lesson

Only 26.6 per cent of eligible households hold a voucher. For the other 73.4 per
cent the clawback threatens nothing they have, so no severity reaches them. The
instrument's grip is bounded above by COVERAGE, not by how hard it bites, and
the bound is close to binding: 3.7139 - 0.3793 is most of what the threat can
take, and the residual 3.5727 per cent of use is in households the policy cannot
touch.

That runs OPPOSITE to the universal case in the same model:

    generosity      optimal clawback        does it reach the social optimum?
    pi_V = 1.000    8 pp, and 62 further    YES, exactly: use 0, and the extra
                    points buy nothing      62 points are pure unexercised risk
    pi_V = 0.266    70 pp, the maximum      NO: 3.5727% of use survives it

SO THE OPTIMAL DEGREE OF CONDITIONALITY DEPENDS ON GENEROSITY, AND IN THE
DIRECTION THAT MAKES THE TWO POLICIES ARGUE PAST EACH OTHER. Where the
programme is universal, Treatment First is far more severe than it needs to be
and the surplus severity is a pure risk with no deterrence value. Where the
programme is rationed, Treatment First is not severe enough and cannot be made
so, and the binding margin is GENEROSITY: enrolling more households is what
gives the threat something to hold.

One observation recorded rather than explained: at rationed coverage Housing
First produces MORE use than at universal (8.9010 against 7.1076) but LESS
disorder (3.7139 against 5.6633). The mechanism has not been traced and no
claim is made about it here.

### Reproduction

`code/stylized/clawback_sweep.py`, which uses the paper's own accounting from
`children.verdict`: `priv` and `per_case` are both mass-weighted means of node
by node consumption equivalents, so their ratio is like for like, and
`gain = dsud * per_case`. It reproduces the universal endpoint exactly,
2.8801 - 0.0513 = 2.8289 at 8 pp.

An earlier pass through this used `internalise.py`'s scalar
`cev(mean) * PV_INCOME` instead and reported 3.06 per cent at the rationed
optimum. THAT PAIRING IS WITHDRAWN: it mixes the two conventions, and it does
not reproduce the universal endpoint. The rationed optimum is 1.7708 per cent.
