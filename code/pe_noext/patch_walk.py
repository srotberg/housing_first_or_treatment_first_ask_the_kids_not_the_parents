#!/usr/bin/env python3
"""patch_walk.py <base cf.f90> <out cf.f90>

THE PER-STATE CONSUMPTION EQUIVALENT FOR THE NO-EXTERNALITY EXPERIMENT (README.md). A walk-only mode of
the counterfactual binary, built on cf_fix2_share_pe (Arm A's build), that changes nothing a solve does:
if the run directory holds pe_walk.dat, long_run_counter_factual initialises exactly as an arm does
(handover, grids, upload_vars), then, instead of entering the loop,

  * loads ARM A's saved policies, value function and distribution (the *counter_arm.dat files its run
    wrote) into the *_benchmark arrays, with save_welfare_curve's own loading code, and its treatment
    policy into policy_function_treatment;
  * for each x listed in pe_walk.dat, runs compute_value_function_comparison(1,x) -- the policy-fixed
    walk the benchmark's welfare curve is built from: every state's value under Arm A's policies with
    non-drug consumption scaled by (1+x) -- and writes the whole array, renters and owners, as raw
    real(8) to walk_V<i>_<k>.bin, and the newborn averages (adult value at age 1 and the childhood
    term) as a PE WALK line;
  * at x = 0 calls report_walk_discrepancy (the walk against Arm A's own value function, by age);
  * stops.

One line of the walk is changed: the drug quantity in addiction_transition divides by
price_of_addictive_good, the price the run is at (the handover's drug_price_start, set to Arm A's),
instead of price_of_addictive_good_benchmark, a parameter equal to one. In the benchmark the two are
the same; in Arm A the solve divided by its own price, so the walk must too.
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def once(text, old):
    n = text.count(old)
    assert n == 1, (n, old[:80])


# 1. the drug quantity in the walk at the run's price
old = "total_consumption_1/price_of_addictive_good_benchmark,1,&\n"
once(s, old)
s = s.replace(old, "total_consumption_1/price_of_addictive_good,1,&\n")

# 2. save_welfare_curve's loading code, verbatim, as the body of the new routine
i0 = s.index("    subroutine save_welfare_curve(time_period)\n")
a = s.index("        vf_simulation='baseline_benchmark'\n", i0)
b = s.index("        already_uploaded_benchmark=1\n", a) + len("        already_uploaded_benchmark=1\n")
load = s[a:b].replace("        vf_simulation='baseline_benchmark'\n", "        vf_simulation='counter_arm'\n")
assert load.count("open(unit=10,") == 11, load.count("open(unit=10,")

routine = """    subroutine pe_walk_only()

        ! See code/pe_noext/patch_walk.py. Walk-only: evaluates Arm A's saved policies, solves nothing.
        use Global_Vars

        implicit none

        integer :: n_x_1,k_1,ios_1
        real(8), dimension(64) :: x_list_1
        real(8) :: w_1
        character*1 :: string_used
        character*2 :: k_string_1

        open(unit=431,file="pe_walk.dat",action='read')
            read(431,*) n_x_1
            do k_1=1,n_x_1
                read(431,*) x_list_1(k_1)
            end do
        close(431)

""" + load + """
        do i=1,2
            write(string_used,'(i1)') i
            open(unit=10,file="policy_function_treatment"//trim(string_used)//"counter_arm.dat",&
                action='read',iostat=ios_1)
                read(10,'(I1)') policy_function_treatment(i)%vector_transition_integer(:,:,:,:,:,:,:)
            close(10)
        end do

        write(*,*) "PE WALK prices: drug=", price_of_addictive_good, " housing=", housing_price(1),&
            " pi_V=", probability_of_voucher_benchmark_used, " kappa_x=", kappa_x,&
            " weight_on_child=", weight_on_child

        do k_1=1,n_x_1
            call compute_value_function_comparison(1,x_list_1(k_1))
            call compute_value_of_comparison(w_1,1)
            write(*,'(A,I3,A,F12.6,A,ES24.16,A,ES24.16)') " PE WALK k=", k_1, " x=", x_list_1(k_1),&
                " w_adult=", w_1, " childhood=", childhood_comparison
            if (abs(x_list_1(k_1))<10.d0**(-12)) call report_walk_discrepancy()
            write(k_string_1,'(I2.2)') k_1
            do i=1,2
                write(string_used,'(i1)') i
                open(unit=432,file="walk_V"//trim(string_used)//"_"//k_string_1//".bin",&
                    access='stream',form='unformatted',status='replace')
                    write(432) value_function_comparison(i)%vector_real
                close(432)
            end do
        end do

        write(*,*) "PE WALK done"

    end subroutine

"""
anchor = "    subroutine long_run_counter_factual()\n"
once(s, anchor)
s = s.replace(anchor, routine + anchor)

decl = "        character*1 :: string_used\n"
i = s.index(anchor)
j = s.index(decl, i)
assert j - i < 600
s = s[:j] + decl + "        logical :: pe_walk_1\n" + s[j + len(decl):]

loop = "        do while (((distance_counterfactual_moments>stopping_rule_frozen_moments) .OR. &\n"
k = s.index(loop, i)
s = s[:k] + ("        inquire(file=\"pe_walk.dat\",exist=pe_walk_1)\n"
             "        if (pe_walk_1) then\n"
             "            call pe_walk_only()\n"
             "            stop\n"
             "        end if\n\n") + s[k:]

open(dst, "w").write(s)
