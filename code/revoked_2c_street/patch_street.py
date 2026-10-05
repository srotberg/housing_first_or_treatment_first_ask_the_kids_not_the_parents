#!/usr/bin/env python3
"""patch_street.py <revk_track.f90> <out_street.f90>

The SMI x street split of the revoked-voucher tracking (code/revoked_2c_street/README.md). Applied to the tracking
build that code/revoked_2c/patch_revoked.py writes; PRINT-ONLY like it: it changes no equation, no line of the model's
own output, and none of the REVK lines the unsplit build prints for groups 1-4.

  * revk_ng goes from 4 to 16. Groups 1-4 are untouched. Group 4 + 4*(c-1) + 1 + 2*s + k (c = 1..3, the year of
    revocation; s = smi_of(u) of the cell at revocation; k = 1 if the revocation puts the cell on the street) is the
    part of cohort c in that cell set.
  * STREET. The kernel makes next year's housing choice in the same step as the voucher draw, and the draw is the
    last factor: a holder revoked in the step that makes year t chose its year-t housing while still a holder (none of
    the revoked is homeless in year t). The first housing choice made AFTER the revocation is the one in the step that
    makes year t+1, taken by Treatment First's policy at the excluded state. A cell is "put on the street" when that
    choice, after the same renters' adjustment the kernel applies, is lowest_housing_grid_point (is_homeless_2 == 2 in
    the kernel). The model keeps one period's policy slice, so the split is made at the START of revk_period(t+1),
    before anything moves, on the cohort's untouched year-t cells; the subgroups start at t (years since 0) like
    their parent. Cells at the last age make no choice (end of life) and go to k = 0; their mass is printed.
  * The Treatment First run writes the four parts of each cohort to REVK_TAGDIR/revk_tag_c<c>_split.bin; the Housing
    First run reads them, puts each back in voucher state 1 exactly as revk_period does with the cohort, and follows
    them under its own kernel. Same households, same split, on both sides.
  * STILL ON THE STREET: for each street subgroup a further shadow mass, stepped by the same kernel and then cut to
    the homeless cells after every step: the mass on the street in every year since the revocation (REVK PERSIST).
  * New lines only: REVK SPLIT, REVK SUBGROUP, REVK PERSIST.
"""
import sys

src, out = sys.argv[1:3]
t = open(src).read()


def rep(text, old, new, count=1):
    n = text.count(old)
    assert n == count, (n, old[:120])
    return text.replace(old, new)


t = rep(t, "        integer, parameter :: revk_ng=4\n",
        "        integer, parameter :: revk_ng=16\n"
        "        ! SMI x STREET SPLIT (code/revoked_2c_street): 5..16 = cohort c (1..3) cut at revocation by SMI s and\n"
        "        ! by whether the first housing choice after it is the street (k), 4+4*(c-1)+1+2*s+k\n"
        "        type(jagged_matrix_real), dimension(1:2,1:6) :: revk_q\n"
        "        real(8), dimension(1:6) :: revk_q_mass0=0\n"
        "        integer, dimension(1:6) :: revk_q_active=0,revk_q_start=0\n")

# allocate the persistence masses with the others
t = rep(t, "            call revk_alloc(revk_tagbuf)\n            call revk_build_mask()\n",
        "            call revk_alloc(revk_tagbuf)\n"
        "            do rk_g=1,6\n                call revk_alloc(revk_q(:,rk_g))\n            end do\n"
        "            call revk_build_mask()\n")

HELPERS = r'''
        ! SMI x STREET: is the first housing choice the cell makes in the step on this period's policies the street?
        ! The kernel's own lines (revk_step): choose_to_own from the amortization policy, the housing policy, the
        ! renters' adjustment when renters' housing is not tracked, then is_homeless_2 == 2 iff lowest grid point.
        integer function revk_street_of(time_period,y,a,f,u,e,h,v)
            integer, intent(in) :: time_period,y,a,f,u,e,h,v
            integer :: rk_own,rk_tr,rk_fut
            revk_street_of=0
            if (a>=life_span) return
            if (policy_function_years_of_amortization_index(y)%vector_transition_integer(time_period,a,f,u,e,h,v)>1) then
                rk_own=1
            else
                rk_own=0
            end if
            rk_fut=policy_function_housing_status_index(y)%vector_transition_integer(time_period,a,f,u,e,h,v)
            rk_tr=1
            if (rk_own==0) then
                if (track_renters_housing==0) rk_tr=0
            end if
            if (rk_tr==0) then
                if (rk_fut>second_lowest_housing_grid_point) rk_fut=0
            end if
            if (rk_fut==lowest_housing_grid_point) revk_street_of=1
        end function

        real(8) function revk_smi_now(x)
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
            revk_smi_now=0
            if (rk_all>0) revk_smi_now=rk_m/rk_all
        end function

        ! cut x to its homeless cells
        subroutine revk_keep_street(x)
            type(jagged_matrix_real), dimension(1:2), intent(inout) :: x
            integer :: rk_k,rk_h
            do rk_k=1,2
                do rk_h=lbound(x(rk_k)%vector_real,5),ubound(x(rk_k)%vector_real,5)
                    if (rk_h/=lowest_housing_grid_point) x(rk_k)%vector_real(:,:,:,:,rk_h,:)=0
                end do
            end do
        end subroutine

        ! SMI x STREET: split cohort c at the start of period time_period = c+1 (before anything moves). In the
        ! Treatment First run the cells are classified on this period's policies and the parts written; in the Housing
        ! First run the parts are read and the voucher put back, as revk_period does with the cohort itself.
        subroutine revk_split(time_period,c)
            integer, intent(in) :: time_period,c
            integer :: rk_s,rk_k,rk_g,rk_b,rk_a,rk_f,rk_u,rk_e,rk_h,rk_v,rk_un,rk_ios
            real(8) :: rk_endlife,rk_maxabs,rk_x
            character(len=420) :: rk_name
            write(rk_name,'(A,A,I1,A)') trim(revk_tagdir), '/revk_tag_c', c, '_split.bin'
            do rk_g=4+4*(c-1)+1,4+4*c
                do rk_b=1,2
                    revk_s(rk_b,rk_g)%vector_real=0
                end do
            end do
            rk_endlife=0
            if (revk_mode==1) then
                do rk_b=1,2
                    do rk_v=lbound(revk_s(rk_b,c)%vector_real,6),ubound(revk_s(rk_b,c)%vector_real,6)
                    do rk_h=lbound(revk_s(rk_b,c)%vector_real,5),ubound(revk_s(rk_b,c)%vector_real,5)
                    do rk_e=lbound(revk_s(rk_b,c)%vector_real,4),ubound(revk_s(rk_b,c)%vector_real,4)
                    do rk_u=lbound(revk_s(rk_b,c)%vector_real,3),ubound(revk_s(rk_b,c)%vector_real,3)
                    do rk_f=lbound(revk_s(rk_b,c)%vector_real,2),ubound(revk_s(rk_b,c)%vector_real,2)
                    do rk_a=lbound(revk_s(rk_b,c)%vector_real,1),ubound(revk_s(rk_b,c)%vector_real,1)
                        rk_x=revk_s(rk_b,c)%vector_real(rk_a,rk_f,rk_u,rk_e,rk_h,rk_v)
                        if (rk_x==0) cycle
                        rk_s=min(smi_of(rk_u),1)
                        rk_k=revk_street_of(time_period,rk_b,rk_a,rk_f,rk_u,rk_e,rk_h,rk_v)
                        if (rk_a>=life_span) rk_endlife=rk_endlife+rk_x
                        rk_g=4+4*(c-1)+1+2*rk_s+rk_k
                        revk_s(rk_b,rk_g)%vector_real(rk_a,rk_f,rk_u,rk_e,rk_h,rk_v)=rk_x
                    end do
                    end do
                    end do
                    end do
                    end do
                    end do
                end do
                open(newunit=rk_un,file=trim(rk_name),access='stream',form='unformatted',status='replace',action='write')
                do rk_g=4+4*(c-1)+1,4+4*c
                    write(rk_un) revk_s(1,rk_g)%vector_real, revk_s(2,rk_g)%vector_real
                end do
                close(rk_un)
            else
                open(newunit=rk_un,file=trim(rk_name),access='stream',form='unformatted',status='old',action='read',iostat=rk_ios)
                if (rk_ios/=0) then
                    write(*,*) "REVK STOP: split file missing: ", trim(rk_name)
                    stop
                end if
                do rk_g=4+4*(c-1)+1,4+4*c
                    read(rk_un,iostat=rk_ios) revk_s(1,rk_g)%vector_real, revk_s(2,rk_g)%vector_real
                    if (rk_ios/=0) then
                        write(*,*) "REVK STOP: split file short: ", trim(rk_name)
                        stop
                    end if
                    ! KEPT THE VOUCHER, as for the cohort
                    if (voucher_excl>=2) then
                        revk_s(1,rk_g)%vector_real(:,:,:,:,:,1)=revk_s(1,rk_g)%vector_real(:,:,:,:,:,1)+&
                            revk_s(1,rk_g)%vector_real(:,:,:,:,:,voucher_excl)
                        revk_s(1,rk_g)%vector_real(:,:,:,:,:,voucher_excl)=0
                    end if
                end do
                close(rk_un)
            end if
            ! the parts against the cohort, cell by cell
            rk_maxabs=0
            do rk_b=1,2
                rk_maxabs=max(rk_maxabs,maxval(abs(revk_s(rk_b,c)%vector_real-revk_s(rk_b,4+4*(c-1)+1)%vector_real-&
                    revk_s(rk_b,4+4*(c-1)+2)%vector_real-revk_s(rk_b,4+4*(c-1)+3)%vector_real-&
                    revk_s(rk_b,4+4*(c-1)+4)%vector_real)))
            end do
            do rk_g=4+4*(c-1)+1,4+4*c
                revk_mass0(rk_g)=sum(revk_s(1,rk_g)%vector_real)+sum(revk_s(2,rk_g)%vector_real)
                revk_active(rk_g)=1
                revk_start(rk_g)=c
                revk_cum_h(rk_g)=0; revk_cum_e(rk_g)=0
                revk_step_h(rk_g)=0; revk_step_e(rk_g)=0; revk_acct(rk_g)=0
            end do
            write(*,'(A,I3,A,I2,A,A,7(A,ES23.15))') " REVK SPLIT t=", time_period, " c=", c, " file=", trim(rk_name), &
                " mass_s0_k0=", revk_mass0(4+4*(c-1)+1), " mass_s0_k1=", revk_mass0(4+4*(c-1)+2), &
                " mass_s1_k0=", revk_mass0(4+4*(c-1)+3), " mass_s1_k1=", revk_mass0(4+4*(c-1)+4), &
                " cohort_mass=", revk_mass0(c), " cell_maxabs_parts_minus_cohort=", rk_maxabs, " endlife_mass=", rk_endlife
            ! the persistence masses: the street parts
            do rk_s=0,1
                rk_g=2*(c-1)+1+rk_s
                do rk_b=1,2
                    revk_q(rk_b,rk_g)%vector_real=revk_s(rk_b,4+4*(c-1)+1+2*rk_s+1)%vector_real
                end do
                revk_q_mass0(rk_g)=revk_mass0(4+4*(c-1)+1+2*rk_s+1)
                revk_q_active(rk_g)=1
                revk_q_start(rk_g)=c
            end do
            do rk_g=4+4*(c-1)+1,4+4*c
                call revk_print_sub(c,rk_g)
            end do
            call revk_print_persist(c)
        end subroutine

        subroutine revk_print_sub(time_period,g)
            integer, intent(in) :: time_period,g
            real(8) :: alive,sud,hom,vhold,vexcl,meanage
            call revk_stats(revk_s(:,g),alive,sud,hom,vhold,vexcl,meanage)
            write(*,'(A,I3,A,I2,A,I2,A,I2,A,I2,A,I3,14(A,ES23.15))') " REVK SUBGROUP t=", time_period, " g=", g, &
                " cohort=", (g-5)/4+1, " smi0=", mod(g-5,4)/2, " street=", mod(g-5,2), " start=", revk_start(g), &
                " mass0=", revk_mass0(g), " alive=", alive, " cum_deaths_h=", revk_cum_h(g), &
                " cum_deaths_e=", revk_cum_e(g), " step_deaths_h=", revk_step_h(g), " step_deaths_e=", revk_step_e(g), &
                " sud=", sud, " homeless=", hom, " holding=", vhold, " excluded=", vexcl, " mean_age=", meanage, &
                " acct=", revk_acct(g), " acct_close=", (alive+revk_cum_h(g)+revk_cum_e(g)-revk_mass0(g))/max(revk_mass0(g),1.d-300), &
                " smi_now=", revk_smi_now(revk_s(:,g))
        end subroutine

        subroutine revk_print_persist(time_period)
            integer, intent(in) :: time_period
            integer :: rk_g
            do rk_g=1,6
                if (revk_q_active(rk_g)==1) write(*,'(A,I3,A,I2,A,I2,A,I3,2(A,ES23.15))') " REVK PERSIST t=", time_period, &
                    " cohort=", (rk_g-1)/2+1, " smi0=", mod(rk_g-1,2), " start=", revk_q_start(rk_g), &
                    " mass0=", revk_q_mass0(rk_g), " on_street_every_year=", &
                    sum(revk_q(1,rk_g)%vector_real)+sum(revk_q(2,rk_g)%vector_real)
            end do
        end subroutine
'''
t = rep(t, "        subroutine revk_tagfile(c,mode_rw)\n", HELPERS + "\n        subroutine revk_tagfile(c,mode_rw)\n")

# the split, at the start of period c+1, before any group moves
t = rep(t, "            ! 1. every group already started moves one year on this period's kernel\n",
        "            ! SMI x STREET: cohort time_period-1 is split here, before anything moves\n"
        "            if ((time_period>=2) .AND. (time_period<=4)) then\n"
        "                if (revk_active(time_period-1)==1) call revk_split(time_period,time_period-1)\n"
        "            end if\n\n"
        "            ! 1. every group already started moves one year on this period's kernel\n")

# the persistence masses move after the groups, by the same kernel, then are cut to the street
t = rep(t, "            ! 2. the whole population at t-1 through the same kernel: deaths, the kernel check, and (Treatment First,\n",
        "            ! SMI x STREET: the mass on the street every year since the revocation\n"
        "            do rk_g=1,6\n"
        "                if ((revk_q_active(rk_g)==1) .AND. (revk_q_start(rk_g)<time_period)) then\n"
        "                    call revk_step(time_period,revk_q(:,rk_g),revk_new,rk_maxabs,rk_sumabs,0.d0,revk_tagbuf,0)\n"
        "                    do rk_k=1,2\n"
        "                        revk_q(rk_k,rk_g)%vector_real=revk_new(rk_k)%vector_real\n"
        "                    end do\n"
        "                    call revk_keep_street(revk_q(:,rk_g))\n"
        "                end if\n"
        "            end do\n\n"
        "            ! 2. the whole population at t-1 through the same kernel: deaths, the kernel check, and (Treatment First,\n")

# print: groups 1-4 exactly as before, then the new lines
t = rep(t, "            do rk_g=1,revk_ng\n                if (revk_active(rk_g)==1) call revk_print_group(time_period,rk_g)\n            end do\n",
        "            do rk_g=1,4\n                if (revk_active(rk_g)==1) call revk_print_group(time_period,rk_g)\n            end do\n"
        "            do rk_g=5,revk_ng\n                if (revk_active(rk_g)==1) call revk_print_sub(time_period,rk_g)\n            end do\n"
        "            call revk_print_persist(time_period)\n")
open(out, 'w').write(t)
print("written", out)
