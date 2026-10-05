#!/usr/bin/env python3
"""patch_smi.py <revk_track.f90> <out_smi.f90>

The SMI split of the revoked-voucher tracking (code/revoked_2c_smi/README.md). Applied to the tracking build that
code/revoked_2c/patch_revoked.py writes; PRINT-ONLY like it, and it changes no equation and no existing line of output.

  * revk_ng goes from 4 to 12. Groups 1-4 are untouched (the same masses, the same REVK GROUP lines, byte for byte).
    Groups 5-12 are the split: group 4+2*(p-1)+1+s is the part of group p (p = 1..4) whose SMI state AT THE START
    (the year of revocation for p = 1-3, the reform's t = 0 for p = 4) is s = smi_of(u) (0 without SMI, 1 with).
    Each is cut from its parent when the parent starts (after the voucher is put back in the Housing First run) and
    then followed by the same revk_step, under the same kernel, exactly as the parent is.
  * New lines only: REVK SGROUP (the split groups, the REVK GROUP fields plus parent, smi0 and smi_now) and REVK SMI
    (smi_now for groups 1-4). smi_now is the share of the group's survivors in an SMI state now: SMI is not absorbing
    (it is left at rate lambda_m, and onset can bring the non-SMI into it).
"""
import sys

src, out = sys.argv[1:3]
t = open(src).read()


def rep(text, old, new, count=1):
    n = text.count(old)
    assert n == count, (n, old[:120])
    return text.replace(old, new)


t = rep(t, "        integer, parameter :: revk_ng=4\n",
        "        integer, parameter :: revk_ng=12\n"
        "        ! SMI SPLIT (code/revoked_2c_smi): 5..12 = group p (1..4) cut by SMI at its start, 4+2*(p-1)+1+smi\n")

HELPERS = r'''
        ! SMI SPLIT: the cells of x whose SMI state is s, copied into y (y zero elsewhere)
        subroutine revk_cut_smi(x,y,s)
            type(jagged_matrix_real), dimension(1:2), intent(in) :: x
            type(jagged_matrix_real), dimension(1:2), intent(inout) :: y
            integer, intent(in) :: s
            integer :: rk_k,rk_u
            do rk_k=1,2
                y(rk_k)%vector_real=0
                do rk_u=lbound(x(rk_k)%vector_real,3),ubound(x(rk_k)%vector_real,3)
                    if (smi_of(rk_u)==s) y(rk_k)%vector_real(:,:,rk_u,:,:,:)=x(rk_k)%vector_real(:,:,rk_u,:,:,:)
                end do
            end do
        end subroutine

        ! SMI SPLIT: start the two halves of parent group p from the parent's starting mass
        subroutine revk_start_split(p)
            integer, intent(in) :: p
            integer :: rk_s,rk_g
            do rk_s=0,1
                rk_g=4+2*(p-1)+1+rk_s
                call revk_cut_smi(revk_s(:,p),revk_s(:,rk_g),rk_s)
                revk_mass0(rk_g)=sum(revk_s(1,rk_g)%vector_real)+sum(revk_s(2,rk_g)%vector_real)
                revk_active(rk_g)=1
                revk_start(rk_g)=revk_start(p)
                revk_cum_h(rk_g)=0; revk_cum_e(rk_g)=0
                revk_step_h(rk_g)=0; revk_step_e(rk_g)=0; revk_acct(rk_g)=0
            end do
        end subroutine

        real(8) function revk_smi_share(x)
            type(jagged_matrix_real), dimension(1:2), intent(in) :: x
            integer :: rk_k,rk_u
            real(8) :: rk_all,rk_m
            rk_all=0; rk_m=0
            do rk_k=1,2
                rk_all=rk_all+sum(x(rk_k)%vector_real)
                do rk_u=lbound(x(rk_k)%vector_real,3),ubound(x(rk_k)%vector_real,3)
                    if (smi_of(rk_u)>=1) rk_m=rk_m+sum(x(rk_k)%vector_real(:,:,rk_u,:,:,:))
                end do
            end do
            revk_smi_share=0
            if (rk_all>0) revk_smi_share=rk_m/rk_all
        end function

        subroutine revk_print_split(time_period,g)
            integer, intent(in) :: time_period,g
            real(8) :: alive,sud,hom,vhold,vexcl,meanage
            call revk_stats(revk_s(:,g),alive,sud,hom,vhold,vexcl,meanage)
            write(*,'(A,I3,A,I2,A,I2,A,I2,A,I3,14(A,ES23.15))') " REVK SGROUP t=", time_period, " g=", g, &
                " parent=", (g-5)/2+1, " smi0=", mod(g-5,2), " start=", revk_start(g), &
                " mass0=", revk_mass0(g), " alive=", alive, " cum_deaths_h=", revk_cum_h(g), &
                " cum_deaths_e=", revk_cum_e(g), " step_deaths_h=", revk_step_h(g), " step_deaths_e=", revk_step_e(g), &
                " sud=", sud, " homeless=", hom, " holding=", vhold, " excluded=", vexcl, " mean_age=", meanage, &
                " acct=", revk_acct(g), " acct_close=", (alive+revk_cum_h(g)+revk_cum_e(g)-revk_mass0(g))/max(revk_mass0(g),1.d-300), &
                " smi_now=", revk_smi_share(revk_s(:,g))
        end subroutine

        ! SMI SPLIT: the print block that follows the REVK GROUP lines
        subroutine revk_print_smi(time_period)
            integer, intent(in) :: time_period
            integer :: rk_g
            do rk_g=1,4
                if (revk_active(rk_g)==1) write(*,'(A,I3,A,I2,A,ES23.15)') " REVK SMI t=", time_period, " g=", rk_g, &
                    " smi_now=", revk_smi_share(revk_s(:,rk_g))
            end do
            do rk_g=5,revk_ng
                if (revk_active(rk_g)==1) call revk_print_split(time_period,rk_g)
            end do
        end subroutine
'''
t = rep(t, "        subroutine revk_tagfile(c,mode_rw)\n", HELPERS + "\n        subroutine revk_tagfile(c,mode_rw)\n")

# group 4 starts at t = 0: cut it there and print its halves after its own line
t = rep(t, "                revk_start(4)=0\n                call revk_print_group(0,4)\n",
        "                revk_start(4)=0\n                call revk_print_group(0,4)\n"
        "                call revk_start_split(4)\n                call revk_print_smi(0)\n")

# a revoked cohort: cut it once its start (in hf, voucher already kept) is set
t = rep(t, "                revk_step_h(rk_g)=0; revk_step_e(rk_g)=0; revk_acct(rk_g)=0\n            end if\n\n"
           "            do rk_g=1,revk_ng\n                if (revk_active(rk_g)==1) call revk_print_group(time_period,rk_g)\n            end do\n",
        "                revk_step_h(rk_g)=0; revk_step_e(rk_g)=0; revk_acct(rk_g)=0\n"
        "                call revk_start_split(rk_g)\n            end if\n\n"
        "            do rk_g=1,4\n                if (revk_active(rk_g)==1) call revk_print_group(time_period,rk_g)\n            end do\n"
        "            call revk_print_smi(time_period)\n")
open(out, 'w').write(t)
print("written", out)
