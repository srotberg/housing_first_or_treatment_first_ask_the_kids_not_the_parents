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

# 6. PRINT-ONLY: childhood utility by age in every transition period. The steady state prints it;
#    the transition computed it and printed nothing. With it, the lifetime utility of the cohort
#    BORN at the reform can be assembled along its own life (childhood at age a in period a, adult
#    value on entering at 26), which is the number the author asked for.
once('            if (solve_transition_dynamics==0) then\n\n'
     '                write(*,*) "average_childhood_utility=", average_childhood_utility(time_period)\n',
     '            if (solve_transition_dynamics==1) then\n'
     '                write(*,*) "TRANSITION CHILDHOOD t=", time_period, " own=", average_childhood_utility(time_period), &\n'
     '                    " with_childhood=", average_welfare_with_childhood(time_period)\n'
     '                write(*,*) "TRANSITION CHILDHOOD_BY_AGE t=", time_period, childhood_utility_by_age(time_period,:)\n'
     '            end if\n'
     '            if (solve_transition_dynamics==0) then\n\n'
     '                write(*,*) "average_childhood_utility=", average_childhood_utility(time_period)\n',
     "childhood print")

# 7. THE BUDGET AT t IS SET BY pi_V(t-1), NOT BY pi_V(t) (TRANSITION_LESSONS, "What the second loop
#    showed", 28 September). pi_V(t) sets the lottery households face in t, a draw in t makes a
#    holder in t+1, and the budget at t is paid on the holders at t, so the old rule stepped each
#    pi_V on a residual it cannot move: a lagged controller that overshot and flipped signs. Now
#    the residual at t steps pi_V(t-1). residual(1) is set by the holders the reform inherits and
#    no pi_V reaches it, so it is reported and left out of the stopping rule. The last free
#    period has no computed residual(T) and takes t-1's value. Secant state is kept per
#    INSTRUMENT period, and a secant is used only when its slope has the sign the map has.
#    Same gain, same growth guard, trust region and clip. NO EQUILIBRIUM CONDITION CHANGES.
def span_once(start, end, new, what):
    global s
    if s.count(start) != 1 or s.count(end) != 1:
        sys.exit(f"REFUSING: anchors for {what} found {s.count(start)}, {s.count(end)} times")
    i = s.index(start)
    j = s.index(end, i) + len(end)
    s = s[:i] + new + s[j:]


once("        real(8) :: pi_v_step_1=0,pi_v_cap_1=0,pi_v_gap_1=0,pi_v_damped_1=0,pi_v_new_1=0\n",
     "        real(8) :: pi_v_step_1=0,pi_v_cap_1=0,pi_v_gap_1=0,pi_v_damped_1=0,pi_v_new_1=0\n"
     "        integer :: pi_v_s_1=0\n",
     "pi_V instrument period declaration")

once("                    distance_govt_budget=adjust_taxes*abs(net_govt_revenues(time_index)-net_govt_revenue_constraint)\n",
     "                    distance_govt_budget=adjust_taxes*abs(net_govt_revenues(time_index)-net_govt_revenue_constraint)\n"
     "                    ! residual(1) is set by the holders the reform inherits; no pi_V reaches it\n"
     "                    if (time_index==1) distance_govt_budget=0\n",
     "budget stopping rule without t = 1")

span_once("                    pi_v_gap_1=net_govt_revenues(time_index)-net_govt_revenue_constraint\n",
          "                        \" secant=\", have_pi_v_secant_path(time_index)\n",
"""                    ! THE RESIDUAL AT t STEPS pi_V(t-1) (patch_transition_fix.py, item 7).
                    pi_v_gap_1=net_govt_revenues(time_index)-net_govt_revenue_constraint
                    pi_v_s_1=time_index-1

                    if (pi_v_s_1<1) then

                        write(*,*) "TRANSITION PI_V loop=", loop_count, " t=", time_index, &
                            " residual set by the inherited holders=", pi_v_gap_1, &
                            " (reported, not in the stopping rule)"

                    else

                        pi_v_damped_1=0.12*pi_v_gap_1

                        pi_v_step_1=pi_v_damped_1

                        if ((have_pi_v_secant_path(pi_v_s_1)==1) .AND. &
                            (abs(pi_v_gap_1-previous_budget_residual_path(pi_v_s_1))>10.d0**(-10)) .AND. &
                            (abs(probability_of_voucher_path(pi_v_s_1)-&
                                 previous_probability_of_voucher_path(pi_v_s_1))>10.d0**(-10)) .AND. &
                            ((pi_v_gap_1-previous_budget_residual_path(pi_v_s_1))*&
                             (probability_of_voucher_path(pi_v_s_1)-&
                              previous_probability_of_voucher_path(pi_v_s_1))<0.d0)) then

                            if (abs(pi_v_gap_1)>abs(previous_budget_residual_path(pi_v_s_1))) then

                                pi_v_step_1=pi_v_damped_1

                            else

                                pi_v_step_1=-pi_v_gap_1*&
                                    (probability_of_voucher_path(pi_v_s_1)-&
                                     previous_probability_of_voucher_path(pi_v_s_1))/&
                                    (pi_v_gap_1-previous_budget_residual_path(pi_v_s_1))

                                pi_v_step_1=max(min(pi_v_step_1,4*abs(pi_v_damped_1)),-4*abs(pi_v_damped_1))

                            end if

                        end if

                        pi_v_cap_1=0.25*probability_of_voucher_path(pi_v_s_1)
                        pi_v_step_1=max(min(pi_v_step_1,pi_v_cap_1),-pi_v_cap_1)

                        previous_probability_of_voucher_path(pi_v_s_1)=&
                            probability_of_voucher_path(pi_v_s_1)
                        previous_budget_residual_path(pi_v_s_1)=pi_v_gap_1
                        have_pi_v_secant_path(pi_v_s_1)=1

                        pi_v_new_1=max(min(probability_of_voucher_path(pi_v_s_1)+pi_v_step_1,1.d0),10.d0**(-5))

                        probability_of_voucher_path(pi_v_s_1)=pi_v_new_1

                        write(*,*) "TRANSITION PI_V loop=", loop_count, " t=", pi_v_s_1, &
                            " pi_v=", probability_of_voucher_path(pi_v_s_1), &
                            " budget_residual=", pi_v_gap_1, &
                            " step=", pi_v_step_1, " damped=", pi_v_damped_1, &
                            " secant=", have_pi_v_secant_path(pi_v_s_1), &
                            " from_residual_at_t=", time_index

                        if (time_index==max(transition_length-1,1)) then

                            probability_of_voucher_path(time_index)=probability_of_voucher_path(pi_v_s_1)

                            write(*,*) "TRANSITION PI_V loop=", loop_count, " t=", time_index, &
                                " pi_v=", probability_of_voucher_path(time_index), &
                                " (last free period: no residual(T) to pair with, takes t-1's value)"

                        end if

                    end if
""", "pi_V pairing")

# 8. PRINT-ONLY: each period's homelessness by age and its mass by age (children live with parents
#    aged 26-50, so childhood homelessness along the path can be read off), the disorder rate's band
#    sums, and the drug market's distance after clearing. Nothing the model computes changes.
once("                    \" p_drug=\", price_of_addictive_good_path(time_index), &\n"
     "                    \" pi_v=\", probability_of_voucher_path(time_index)\n",
     "                    \" p_drug=\", price_of_addictive_good_path(time_index), &\n"
     "                    \" pi_v=\", probability_of_voucher_path(time_index)\n"
     "                write(*,*) \"TRANSITION HOMELESS_BY_AGE t=\", time_index, homelessness_by_age(time_index,:)\n"
     "                write(*,*) \"TRANSITION MASS_BY_AGE t=\", time_index, mass_by_age(time_index,:)\n"
     "                write(*,*) \"TRANSITION SUD_BANDS t=\", time_index, \" sud=\", val_sud_band(time_index,:), &\n"
     "                    \" mass=\", val_mass_band(time_index,:)\n",
     "homelessness by age print")
once("                price_of_addictive_good_path(time_index)=price_of_addictive_good\n",
     "                price_of_addictive_good_path(time_index)=price_of_addictive_good\n"
     "                write(*,*) \"TRANSITION DRUG t=\", time_index, \" distance=\", distance_drug_market, &\n"
     "                    \" price=\", price_of_addictive_good\n",
     "drug market print")

# Re-checked by value in the result.
for must in ["solve_transition_dynamics*1.d0+(1-solve_transition_dynamics)*1.d0",
             "real(8) :: stopping_rule_govt_budget=1.0*10.d0**(-3)",
             "pi_v_damped_1=0.12*pi_v_gap_1",
             "newborn_parent_share=init_parent_share_1",
             "file=\"newborn_parent_share_initial.dat\"",
             "TRANSITION ALLALIVE t=",
             "TRANSITION CHILDHOOD_BY_AGE t=",
             "pi_v_s_1=time_index-1",
             "if (time_index==1) distance_govt_budget=0",
             "TRANSITION HOMELESS_BY_AGE t=",
             "TRANSITION DRUG t="]:
    if s.count(must) != 1:
        sys.exit(f"REFUSING: {must!r} is not in the result exactly once")
if "unit=419" in open(src).read():
    sys.exit("REFUSING: unit 419 is already used in the tracked source")

open(out, "w").write(s)
print(f"patched: {out}")
