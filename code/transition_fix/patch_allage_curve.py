#!/usr/bin/env python3
"""patch_allage_curve.py <tracked source> <patched out>

PRINT-ONLY. The benchmark's welfare curve (save_welfare_curve) evaluates every
state's value under the benchmark's own policies with consumption scaled by
(1+x), at 21 points x in [-0.5, 0.5], and then averages that value over AGE 1
only (compute_value_of_comparison). That is the curve the newborn CEV is read
off. The welfare of everyone ALIVE at a reform (TRANSITION_LESSONS 6.1) needs
the same curve averaged over EVERY age on the benchmark distribution.

This adds compute_value_of_comparison_allages: the existing routine's own loops
and its own screening of cells the walk could not evaluate, with the age loop
widened to 1..life_span and the average kept overall and by ten-year age band.
save_welfare_curve calls it at every curve point, right after the newborn
average, and it prints

    ALLAGE CURVE x= <x> band= <0..6> w= <average value> mass= <mass> dropped= <mass>

Nothing the model computes changes. The all-alive CEV of a transition at t is
then the x at which w(x) - w(0) equals the transition's V_reform - V_bench for
the same band (TRANSITION ALLALIVE lines), read by interpolation.
"""
import sys

src, out = sys.argv[1], sys.argv[2]
s = open(src).read()

start = s.index("    subroutine compute_value_of_comparison(welfare_adjusted_1,type_1)\n")
end = s.index("    end subroutine\n", start) + len("    end subroutine\n")
r = s[start:end]


def sub(text, old, new, what):
    n = text.count(old)
    if n != 1:
        sys.exit(f"REFUSING: {what}: anchor found {n} times")
    return text.replace(old, new)


r = sub(r, "    subroutine compute_value_of_comparison(welfare_adjusted_1,type_1)\n",
        "    subroutine compute_value_of_comparison_allages(x_print_1)\n", "name")
r = sub(r, "        integer, intent(in) :: type_1\n",
        "        real(8), intent(in) :: x_print_1\n"
        "        real(8), dimension(0:6) :: w_band_1,m_band_1\n"
        "        integer :: band_1\n", "type_1 declaration")
r = sub(r, "        real(8), intent(inout) :: welfare_adjusted_1\n",
        "        real(8) :: welfare_adjusted_1\n", "welfare declaration")
r = sub(r, '        write(*,*) "type_1 loop=", type_1\n', "", "type_1 print")
r = sub(r, "        mass_1=0.d0\n",
        "        mass_1=0.d0\n        w_band_1=0.d0\n        m_band_1=0.d0\n", "zeroing")
r = sub(r, "        do age_index=1,1\n", "        do age_index=1,life_span\n", "age loop")

sel_start = r.index("                                        select case (type_1)\n")
sel_end = r.index("                                        end select\n", sel_start) + \
    len("                                        end select\n")
r = r[:sel_start] + (
    "                                        band_1=min((age_index-1)/10+1,6)\n"
    "                                        w_band_1(0)=w_band_1(0)+value_function_1*distribution_1\n"
    "                                        m_band_1(0)=m_band_1(0)+distribution_1\n"
    "                                        w_band_1(band_1)=w_band_1(band_1)+value_function_1*distribution_1\n"
    "                                        m_band_1(band_1)=m_band_1(band_1)+distribution_1\n"
) + r[sel_end:]

tail_start = r.index("        if (mass_1 > 0.d0) then\n")
r = r[:tail_start] + (
    "        do band_1=0,6\n"
    '            write(*,*) "ALLAGE CURVE x=", x_print_1, " band=", band_1, &\n'
    '                " w=", w_band_1(band_1)/max(m_band_1(band_1),10.d0**(-14)), &\n'
    '                " mass=", m_band_1(band_1), " dropped=", dropped_mass_1\n'
    "        end do\n"
    "    end subroutine\n"
)
for leftover in ("type_1", "select case"):
    if leftover in r:
        sys.exit(f"REFUSING: '{leftover}' survived in the new routine")

# the new routine goes in front of the one it was made from
s = s[:start] + r + s[start:]

call = ("            call compute_value_function_comparison(time_period,x_1)\n"
        "            call compute_value_of_comparison(w_1,1)\n")
if s.count(call) != 1:
    sys.exit(f"REFUSING: curve call anchor found {s.count(call)} times")
s = s.replace(call, call + "            call compute_value_of_comparison_allages(x_1)\n")

open(out, "w").write(s)
print(f"patched: {out}")
