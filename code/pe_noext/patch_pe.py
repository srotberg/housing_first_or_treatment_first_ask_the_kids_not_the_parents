#!/usr/bin/env python3
"""patch_pe.py <base cf.f90> <out cf.f90> <print|hold>

The partial-equilibrium, no-externality experiment (code/pe_noext/README.md).

print  (Arm A, on cf_fix2_share): PRINT-ONLY. At the top of every pass of the counterfactual
       loop, before the value function is solved, writes the prices that solve will use, at full
       precision:
           PE USED pass= <loop_count> housing_price= <p_h> drug_price= <p_d> pi_V= <p_v>
       Nothing the run computes changes. Arm B is held at the prices of Arm A's LAST solve, which
       are the ones printed by the last PE USED line (the price printed at the end of a pass is the
       next pass's, and the last pass has no next).

hold   (Arm B, on cf_fix2): the same print, plus a HOLD of the house price. The counterfactual
       loop pegs housing_price to the calibrated value (peg_prices_in_counterfactual = 1) and then,
       in the same pass, moves it 2 per cent of the way to the supply curve (adjust_house_prices =
       1 - partial_equilibrium, a parameter), so every solve after the first runs at
       0.98 * calibrated + 0.02 * S(demand): 2.4e-4 above calibrated in the accepted fixboth arm.
       That is a general-equilibrium channel the handover cannot switch off. If the run directory
       holds housing_price_hold.dat (one number), the price is set to it before every solve and the
       print shows it. Without the file the build behaves exactly as cf_fix2.
"""
import sys

src, dst, mode = sys.argv[1], sys.argv[2], sys.argv[3]
assert mode in ("print", "hold")
s = open(src).read()

anchor = ("            (loop_count<aftr_how_mny_lps_start_update)) .AND. &\n"
          "            (loop_count<max_counterfactual_loops))\n"
          "                                \n"
          "            call solve_value_function_and_policy_functions(transition_length)\n")
assert s.count(anchor) == 1, ("loop anchor", s.count(anchor))

hold = ""
if mode == "hold":
    hold = ("            inquire(file=\"housing_price_hold.dat\",exist=pe_hold_exists_1)\n"
            "            if (pe_hold_exists_1) then\n"
            "                open(unit=422,file=\"housing_price_hold.dat\",action='read')\n"
            "                    read(422,*) pe_hold_value_1\n"
            "                close(422)\n"
            "                housing_price(transition_length)=pe_hold_value_1\n"
            "                write(*,*) \"PE HOLD housing_price set to\", pe_hold_value_1\n"
            "            end if\n")
add = (hold +
       "            write(*,'(A,I5,A,ES24.16,A,ES24.16,A,ES24.16)') \" PE USED pass=\", loop_count,&\n"
       "                \" housing_price=\", housing_price(transition_length),&\n"
       "                \" drug_price=\", price_of_addictive_good,&\n"
       "                \" pi_V=\", probability_of_voucher_benchmark_used\n")
new = anchor.replace("            call solve_value_function_and_policy_functions(transition_length)\n",
                     add + "            call solve_value_function_and_policy_functions(transition_length)\n")
s = s.replace(anchor, new)

if mode == "hold":
    decl = ("        character*1 :: string_used\n")
    i = s.index("    subroutine long_run_counter_factual()\n")
    j = s.index(decl, i)
    assert j - i < 600, "declaration not where expected"
    s = s[:j] + decl + "        logical :: pe_hold_exists_1\n        real(8) :: pe_hold_value_1\n" + s[j + len(decl):]

open(dst, "w").write(s)
