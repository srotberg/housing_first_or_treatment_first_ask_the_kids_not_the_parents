#!/usr/bin/env python3
"""WHERE THE CHILD'S ADULT GAIN COMES FROM.

The author, 13 September: *"so the child first loses because they have more
homelessness, but then gains through its higher earnings during adulthood"*.

That is testable, because the adult term is W(p, v1) -- a mixture p over the
four inherited penalty types, and a value function v1.  Only p carries the
parent.  So the gain splits exactly:

    INHERITANCE   W(p_TF, v1_HF) - W(p_HF, v1_HF)   fewer children inherit the
                                                    disorder penalty on income
    OWN WORLD     W(p_TF, v1_TF) - W(p_TF, v1_HF)   the same child, living
                                                    under the new policy itself

The first is the earnings channel the author names.  The second is everything
the policy does to a child once it is grown, its own vouchers included.
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transition as T
from stylized import with_
from tf_long_run import calibrated

NAMES = ['clean, housed', 'disorder', 'homeless', 'both']


def main():
    par, _ = calibrated()
    v1h, sudh, hlh, _ = T._policy_grids(par, 'HF', par.pV)
    v1t, sudt, hlt, _ = T._policy_grids(par, 'TF', par.pV)
    ph = T._rest_point(sudh, T._hl_by_shift(par, 'HF', par.pV), par)
    pt = T._rest_point(sudt, T._hl_by_shift(par, 'TF', par.pV), par)

    sh = T._shifts(par)
    print("THE MIXTURE A CHILD IS BORN INTO, and the income multiplier it carries")
    print(f"   {'type':>14}{'multiplier':>12}{'HF':>10}{'TF':>10}{'change':>10}")
    for k in range(4):
        print(f"   {NAMES[k]:>14}{sh[k]:12.5f}{ph[k]:10.5f}{pt[k]:10.5f}"
              f"{pt[k]-ph[k]:+10.5f}")
    ey_h = float((sh * ph).sum())
    ey_t = float((sh * pt).sum())
    print(f"   {'expected multiplier':>26}{ey_h:10.5f}{ey_t:10.5f}"
          f"{100*(ey_t/ey_h-1):+9.3f}%")

    a_hh = T._welfare(ph, v1h, par)
    a_th = T._welfare(pt, v1h, par)
    a_tt = T._welfare(pt, v1t, par)
    print("\nTHE ADULT GAIN, split")
    print(f"   {'HF benchmark    W(p_HF, v1_HF)':<36}{a_hh:11.5f}")
    print(f"   {'inheritance     W(p_TF, v1_HF)':<36}{a_th:11.5f}"
          f"{a_th-a_hh:+11.5f}{100*(a_th-a_hh)/(a_tt-a_hh):8.1f}%")
    print(f"   {'own world       W(p_TF, v1_TF)':<36}{a_tt:11.5f}"
          f"{a_tt-a_th:+11.5f}{100*(a_tt-a_th)/(a_tt-a_hh):8.1f}%")
    print(f"   {'total':<36}{'':11}{a_tt-a_hh:+11.5f}")


if __name__ == '__main__':
    main()
