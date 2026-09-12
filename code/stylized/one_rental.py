"""
ONE RENTAL SIZE INSTEAD OF TWO: does the model still calibrate?

The author, 12 September: *"you dont need 2 sizes....just homeless and 1
rental"*.  The model docstring already answers a question that SOUNDS like this
one and is not it:

    Collapsing h_sm into h_lg takes homelessness far above its target and NO
    value of h_hl brings it back.

That measurement collapsed the small unit UP to the large one, 0.40, and it is
sound as far as it goes: at a rent of 0.40 the bottom of the income
distribution cannot afford to be housed at any level of street misery, so
homelessness is forced rather than chosen.  But "one rental" does not have to
mean "one rental at 0.40".  A single unit at 0.10, or 0.16, or 0.22 is equally
one rental, and the affordability floor moves with it.  That question has not
been measured.

TWO THINGS THIS SCRIPT DOES NOT DO, both of which are how the answer was got
wrong four times already in this model:

  * it does not freeze the other parameters.  Every "structurally unreachable"
    claim made about this model so far -- the housing share, the value of life,
    net worth, the SUD share of the homeless -- was measured with one parameter
    moving and the rest held, and the joint rule reached all four.  So this runs
    the FULL eleven-parameter rule at each candidate size and asks where it
    LANDS, not whether one dial can cover the distance.

  * it does not report a best-of across sizes as though it were an equilibrium.
    Each size gets its own converged table and they are printed side by side.

FIXED itself carries h_lg = 0.40 and h_sm = 0.10, so both are dropped from it
before the single size goes in.  h_sm and h_lg are ALWAYS passed together.  with_() ties h_sm to H_RATIO * h_lg
when h_lg arrives alone, which would silently reintroduce the second size in the
middle of an experiment whose whole point is that there is only one.
"""
import sys
import stylized as S
from stylized import with_, P
import sr_calibrate as C
from recalibrate import FIXED, START

SIZES = [0.10, 0.13, 0.16, 0.20, 0.25, 0.30, 0.40]
PASSES = int(sys.argv[1]) if len(sys.argv) > 1 else 400


def run(h1):
    """The full rule from the standard start, with a SINGLE rental unit h1."""
    par = with_(P(), **{k: v for k, v in FIXED.items() if k not in ('kap', 'h_lg', 'h_sm')},
                **{**START, "th": 0.25, "beta": 1.0, "kap": 1.0 - 0.91 ** 2,
                   "h_lg": h1, "h_sm": h1})
    state = {}
    for it in range(PASSES):
        m = C.moments(par, it)
        par = C.step_on_branch(par, m, state)
    return par, C.moments(par)


print(f"ONE RENTAL SIZE, full eleven-parameter rule, {PASSES} passes each\n")
head = f"{'h1':>6} {'homeless':>9} {'hshare':>8} {'part':>7} {'sud':>7} " \
       f"{'r_use':>7} {'dshare':>7} {'burden50':>9} {'h_hl':>10} {'gam':>7} {'worst%':>7}"
print(head); print('-' * len(head))
for h1 in SIZES:
    par, m = run(h1)
    worst = 0.0
    for name, mom, tgt, sgn, adj0, lo, hi in C.SPEC:
        v = m.get(mom)
        if v is not None:
            worst = max(worst, abs(100.0 * (v - tgt) / tgt))
    print(f"{h1:6.2f} {m['homeless']:9.4f} {m['hspend']:8.4f} {m['part']:7.4f} "
          f"{m['sud']:7.4f} {m['r_use']:7.4f} {m['dshare']:7.4f} "
          f"{m['burden50']:9.4f} {par.h_hl:10.2e} {par.gam:7.4f} {worst:7.1f}")
    sys.stdout.flush()
print("\nTARGETS  homeless 0.0100   hshare 0.2680   part 0.0890   sud 0.0368"
      "   r_use 0.7400   dshare 0.1410")
print("burden50 is REPORTED, not targeted (17.5 per cent in the data).")
