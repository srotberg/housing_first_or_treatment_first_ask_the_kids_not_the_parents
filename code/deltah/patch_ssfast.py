#!/usr/bin/env python3
"""patch_ssfast.py SRC OUT -- set_SS_benefits WITHOUT ITS ZERO TERMS (12 October, the both-penalties run on rule C).

WHY. set_SS_benefits runs at the top of every calibration loop. Its lifetime-income nest is, for each starting cell
(employment x unemployment, E*U of them) and each of the 40 working ages, a sum over every past cell and, inside it, an
update of every next cell: (E*U)^3 x 40 terms, with two row sums recomputed in the innermost loop. At the paper's state
E*U = 26*18 = 468; at the four-class state (patch_both.py) it is 52*36 = 1872, 64 times the work, and the benchmark sat
in this routine for hours before its first age (gdb on the 12 October launch: set_ss_benefits_ under calibrating_model,
35 minutes in; the 11 October attempts reached their first AGE_TIME only about two and a half hours in).

WHAT. Inside the age loop probability_came_from_past_employment_index_1 is never written (it is replaced by _2 only
after the age loop closes), so it stays the unit vector it was set to: one entry 1, every other 0. Every term of both
sums is multiplied by an entry of it, so a zero entry adds exactly +0 to a finite sum. Skipping those terms is exact,
bit for bit, for finite processes, and leaves (E*U)^2 x 40 terms. Nothing else in the routine changes. (The nest only
feeds model_average_lifetime_income_conditional_on_last_period_shock, which nothing else reads while use_pia_formula
is 1.)

Refuses unless the anchors are found exactly once inside set_SS_benefits."""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
assert s.count('    subroutine set_SS_benefits(time_period)') == 1
i = s.index('    subroutine set_SS_benefits(time_period)')
j = s.index('end subroutine', i)
body = s[i:j]
old = "                        do past_employment_index_2=1,unemployment_grid_size\n"
assert body.count(old) == 1, body.count(old)
# the unit vector is replaced only after the age loop: exactly one assignment to it from _2, and none inside the nest
assert body.count("probability_came_from_past_employment_index_1=&\n                    probability_came_from_past_employment_index_2") == 1
new = old + ("                            ! patch_ssfast.py: a zero weight adds exactly +0 to both sums below\n"
             "                            if (probability_came_from_past_employment_index_1&\n"
             "                                (past_employment_index_2,past_employment_index_1)==0.d0) cycle\n")
s = s[:i] + body.replace(old, new) + s[j:]
open(dst, 'w').write(s)
print(f'patch_ssfast: {src} -> {dst}')
