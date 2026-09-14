## 14 September 02:30 UTC -- THE FIRST PARAMETER IS SOLVED, NOT SEARCHED, AND
## INELASTIC LABOUR IS WHY

**tau_ell = 0.871398.**  Measured, not walked, and it landed to 0.13 per cent.

The author, 14 September: *"you will need to also raise tau_ell to reduce the
taxes.  tau_ell is going to be a pretty stable number because labor supply is
inelastic for workers"*.  That is exactly right and it is stronger than a
bracket.  T(y) = y - lambda*y^kappa, so the average rate is

    1 - lambda * E[y^kappa]/E[y]

which is LINEAR in lambda, and under inelastic labour that expectation is a
constant because earnings do not respond.  One measured point pins it:

    lambda 0.767599  ->  average labour income tax 0.31644
    implied E[y^kappa]/E[y] = 0.890523
    to hit 0.224:  lambda = 0.776 / 0.890523 = 0.871398

MEASURED AT THAT VALUE: 0.223717 against a target of 0.224000, off by 0.13 per
cent.  The deduction, the transfers and the employment composition together
move it by a tenth of a per cent and nothing more.

WHAT IT WOULD HAVE COST OTHERWISE.  A +13.5 per cent move at the one per cent
per loop cap is FOURTEEN LOOPS, about half an hour of solving, to find a number
that falls out of one equation.

**THE GENERAL RULE THIS ESTABLISHES, AND IT IS NEW WITH INELASTIC LABOUR.**  Any
moment that is a deterministic function of the frozen earnings distribution is
now ALGEBRA rather than iteration.  The test is whether the moment feeds back
into behaviour.  For the tax it plainly does not.  Ask the question of every
instrument before spending loops on it.

**AND ONE THAT IS NOT SUCH A CASE, recorded because the mistake was made here
first.**  Voucher coverage is a STOCK, not a flow.  The retention rule is
probability ONE -- voucher_probabilities(1,1,1,:)=1, keep it while income is
below the threshold -- so a small entry rate accumulates.  A one-point linear
extrapolation gave pi_V = 0.283 to reach coverage of 0.266, which is eight
times its current value and wrong: it treated the stock as a flow.  The author
caught it: *"i think pi_v=0.283 is way too high because someone who gets it
keeps it until it's income rises above the median income"*.

The moment's own arithmetic checks out -- it IS normalised by model_eligibles at
17531, so it is a rate among eligibles and not a population share, and
coverage_relative_to_pop of 0.00832 against 0.0339 implies about 24.5 per cent
of the population is income-eligible, consistent with a threshold at half the
median.  So the low coverage is the stock failing to build, not a denominator
error, and pi_V must not be fitted to it until that is understood.

**THE SEED IS SAVED AS code/SEED_VECTOR_14SEP.txt**, 75 parameters, derived from
point_16398ec68f (7 September, MODEL 211b867a51, the OLD model) with three
changes: tau_ell to the solved 0.871398, theta pinned to the author's 0.16, and
size_homelessness dropped because h_1 is tied to h_2 now.  Its VALUES are a
starting point only; its MOMENTS were measured on a model with endogenous labour
and no childhood and do not carry across.

**WHAT b IS, AND WHY IT IS NOT SETTLED.**  Measured on the current model at the
seed, drug use is violently non-linear in b and the elasticity is -1.64:

    b        0.0020   0.0010   0.0005   0.0002   0.0001
    users    0.19%    0.43%    3.71%    16.60%   26.82%
    SUD      0.08%    0.15%    1.44%     6.45%   10.24%

Interpolating, b = 0.000293 gives 8.9 per cent users with SUD at 3.45 against
3.68.  BUT that is conditional on aleph = 118, which is 48 per cent above its
target of 80.  The author: *"you will have to lower aleph quite a bit and then b
will have to rise"*.  They are right and the mechanism is the model's own -- a
lower value of life makes the drug's mortality risk matter less, use rises, and
b must rise to pull it back.  So 0.000293 is a waypoint, not a seed value.

THE DISORDERED SHARE OF USERS IS ALREADY RIGHT, which is the good news in that
table: SUD/users sits at 0.38-0.39 across a fifteen-fold range of b, against
0.41 in the data.  The onset at 0.0428 is producing very nearly the right
conversion rate, so b and the onset are NOT fighting over participation the way
they appeared to.

