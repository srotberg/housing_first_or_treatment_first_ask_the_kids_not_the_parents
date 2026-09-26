#!/usr/bin/env python3
"""patch_transition_fix.py <tracked source> <patched out>

The transition fixes of TRANSITION_LESSONS.md section 16, as a build copy. The
tracked source is not touched. Every edit replaces an anchor that must occur
exactly once, and the result is re-checked by value, so a moved line refuses
rather than builds a different binary.

  1. transition_tolerance_factor 2 -> 1: the path's stopping tests are the
     steady state's own rules, not twice them.
  2. stopping_rule_govt_budget 2.5e-2 -> 1e-3: every period's budget clears
     to the rule the corrected steady-state arms clear to.
  3. pi_V's first per-period step 0.05 -> 0.12 of the gap, the steady state's
     gain (about one over the measured slope of -9).
  4. newborn_parent_share at t = 1: the INITIAL steady state's share, read
     from newborn_parent_share_initial.dat at start-up (the run refuses to
     start without it) and restored beside init_keep_* at t = 1 of EVERY
     loop. Without it loop 0 draws the reform-date cohort from the clean
     housed default (1, 0, 0, 0) and every later loop from the end of the
     previous one.
"""
import re, sys

src, out = sys.argv[1], sys.argv[2]
s = open(src).read()


def once(old, new, what):
    global s
    n = s.count(old)
    if n != 1:
        sys.exit(f"REFUSING: anchor for {what} found {n} times")
    s = s.replace(old, new)


once("solve_transition_dynamics*2.d0+(1-solve_transition_dynamics)*1.d0",
     "solve_transition_dynamics*1.d0+(1-solve_transition_dynamics)*1.d0",
     "transition_tolerance_factor")

once("        real(8) :: stopping_rule_govt_budget=2.5*10.d0**(-2)",
     "        real(8) :: stopping_rule_govt_budget=1.0*10.d0**(-3)",
     "stopping_rule_govt_budget")

once("pi_v_damped_1=0.05*pi_v_gap_1",
     "pi_v_damped_1=0.12*pi_v_gap_1",
     "pi_V first step")

once("        logical :: init_keep_done=.false.\n",
     "        logical :: init_keep_done=.false.\n"
     "        real(8), dimension(employment_grid_size,0:1,1:2) :: init_parent_share_1=0\n"
     "        integer :: init_parent_share_ios_1=0\n",
     "parent share declaration")

once("                init_keep_done=.true.\n",
     "                init_keep_done=.true.\n"
     "                ! THE INITIAL STEADY STATE'S PARENT SHARE (TRANSITION_LESSONS 16).\n"
     "                open(unit=419,file=\"newborn_parent_share_initial.dat\",status='old',&\n"
     "                    action='read',iostat=init_parent_share_ios_1)\n"
     "                if (init_parent_share_ios_1/=0) then\n"
     "                    write(*,*) \"STOP: newborn_parent_share_initial.dat is missing\"\n"
     "                    stop\n"
     "                end if\n"
     "                read(419,'(F30.15)',iostat=init_parent_share_ios_1) init_parent_share_1\n"
     "                close(419)\n"
     "                if ((init_parent_share_ios_1/=0) .OR. &\n"
     "                    (abs(sum(init_parent_share_1)-1.d0)>10.d0**(-9))) then\n"
     "                    write(*,*) \"STOP: newborn_parent_share_initial.dat is short or does not sum to one\"\n"
     "                    stop\n"
     "                end if\n"
     "                write(*,*) \"TRANSITION INIT: initial parent share (clean housed, disordered housed,\"//&\n"
     "                    \" clean street, disordered street)=\", sum(init_parent_share_1(:,0,1)),&\n"
     "                    sum(init_parent_share_1(:,1,1)), sum(init_parent_share_1(:,0,2)),&\n"
     "                    sum(init_parent_share_1(:,1,2))\n",
     "parent share read")

once("                    write(*,*) \"TRANSITION INIT RESTORED loop=\", loop_count, \" mass=\",&\n",
     "                    newborn_parent_share=init_parent_share_1\n"
     "                    write(*,*) \"TRANSITION INIT PARENT SHARE RESTORED loop=\", loop_count, &\n"
     "                        \" disordered housed=\", sum(newborn_parent_share(:,1,1))\n"
     "                    write(*,*) \"TRANSITION INIT RESTORED loop=\", loop_count, \" mass=\",&\n",
     "parent share restore")

# 5. PRINT-ONLY: welfare of everyone ALIVE AT THE REFORM (TRANSITION_LESSONS 6.1). The support
#    routine already compares, on the pre-reform distribution, each state's value on the path at
#    t with its benchmark value; it only tallied the share of winners. This totals both values,
#    overall and by ten-year age band, and prints them. Nothing the model computes changes.
once("        integer :: benchmark_welfare_files_loaded=0\n",
     "        integer :: benchmark_welfare_files_loaded=0\n"
     "        real(8), dimension(0:6) :: allalive_v_1=0,allalive_vb_1=0,allalive_m_1=0,allalive_win_1=0\n"
     "        integer :: allalive_band_1=0\n",
     "all-alive declarations")
once("        average_welfare_of_winners(time_period)=0\n        average_welfare_of_winners_benchmark(time_period)=0\n",
     "        average_welfare_of_winners(time_period)=0\n        average_welfare_of_winners_benchmark(time_period)=0\n"
     "        allalive_v_1=0\n        allalive_vb_1=0\n        allalive_m_1=0\n        allalive_win_1=0\n",
     "all-alive zeroing")
once("                                    value_function_benchamrk_used=value_function_benchmark(years_left_on_mortgage_index)%&\n"
     "                                        vector_real(age_index,financial_index,unemployment_index,employment_index,&\n"
     "                                        housing_status_index,voucher_index)\n",
     "                                    value_function_benchamrk_used=value_function_benchmark(years_left_on_mortgage_index)%&\n"
     "                                        vector_real(age_index,financial_index,unemployment_index,employment_index,&\n"
     "                                        housing_status_index,voucher_index)\n"
     "                                    if (distribution_mass_used>0.d0) then\n"
     "                                    allalive_band_1=min((age_index-1)/10+1,6)\n"
     "                                    allalive_m_1(0)=allalive_m_1(0)+distribution_mass_used\n"
     "                                    allalive_m_1(allalive_band_1)=allalive_m_1(allalive_band_1)+distribution_mass_used\n"
     "                                    allalive_v_1(0)=allalive_v_1(0)+distribution_mass_used*value_function_used\n"
     "                                    allalive_v_1(allalive_band_1)=allalive_v_1(allalive_band_1)+distribution_mass_used*value_function_used\n"
     "                                    allalive_vb_1(0)=allalive_vb_1(0)+distribution_mass_used*value_function_benchamrk_used\n"
     "                                    allalive_vb_1(allalive_band_1)=allalive_vb_1(allalive_band_1)+&\n"
     "                                        distribution_mass_used*value_function_benchamrk_used\n"
     "                                    if (value_function_used>value_function_benchamrk_used) then\n"
     "                                        allalive_win_1(0)=allalive_win_1(0)+distribution_mass_used\n"
     "                                        allalive_win_1(allalive_band_1)=allalive_win_1(allalive_band_1)+distribution_mass_used\n"
     "                                    end if\n"
     "                                    end if\n",
     "all-alive accumulation")
once("        frac_in_support_addicted_youngest(time_period)=&\n"
     "            frac_in_support_addicted_youngest(time_period)/max(total_addicted_youngest_1,10.d0**(-14))\n",
     "        frac_in_support_addicted_youngest(time_period)=&\n"
     "            frac_in_support_addicted_youngest(time_period)/max(total_addicted_youngest_1,10.d0**(-14))\n"
     "        do allalive_band_1=0,6\n"
     "            write(*,*) \"TRANSITION ALLALIVE t=\", time_period, \" band=\", allalive_band_1, &\n"
     "                \" mass=\", allalive_m_1(allalive_band_1), &\n"
     "                \" V_reform=\", allalive_v_1(allalive_band_1)/max(allalive_m_1(allalive_band_1),10.d0**(-14)), &\n"
     "                \" V_bench=\", allalive_vb_1(allalive_band_1)/max(allalive_m_1(allalive_band_1),10.d0**(-14)), &\n"
     "                \" better_off=\", allalive_win_1(allalive_band_1)/max(allalive_m_1(allalive_band_1),10.d0**(-14))\n"
     "        end do\n",
     "all-alive print")

# Re-checked by value in the result.
for must in ["solve_transition_dynamics*1.d0+(1-solve_transition_dynamics)*1.d0",
             "real(8) :: stopping_rule_govt_budget=1.0*10.d0**(-3)",
             "pi_v_damped_1=0.12*pi_v_gap_1",
             "newborn_parent_share=init_parent_share_1",
             "file=\"newborn_parent_share_initial.dat\"",
             "TRANSITION ALLALIVE t="]:
    if s.count(must) != 1:
        sys.exit(f"REFUSING: {must!r} is not in the result exactly once")
if "unit=419" in open(src).read():
    sys.exit("REFUSING: unit 419 is already used in the tracked source")

open(out, "w").write(s)
print(f"patched: {out}")
