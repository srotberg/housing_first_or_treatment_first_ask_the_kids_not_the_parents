#!/usr/bin/env python3
"""Add the SUD gradient by quantity used: the moment lambda_addiction is for.

Applied to a COPY, deliberately. A solve was running when this was written and
ENGINE.md's rule is that code/ is not touched while one is, so the change is
built and compiled here and moved across at a break.
"""
import re, sys

src = sys.argv[1]
L = open(src, errors='replace').read().split('\n')

def find(pat, start=0, end=None):
    end = len(L) if end is None else end
    for i in range(start, end):
        if re.search(pat, L[i]):
            return i
    raise SystemExit('anchor not found: ' + pat)

edits = []   # (line index to insert AFTER, text block)

# ---------------------------------------------------------------- declarations
i = find(r'real\(8\), parameter :: sud_rate_data=')
DECL = '''
        ! THE GRADIENT OF THE DISORDER IN THE QUANTITY USED. This is the moment
        ! lambda_addiction is for, and until it existed lambda_addiction was
        ! pinned at zero because nothing in the calibration could see it.
        !
        ! b fixes how many people use at all and addiction_onset_base fixes how
        ! many of them convert on average; what is left over is the SHAPE of the
        ! hazard in quantity, and that is the only thing asked of lambda here.
        ! The author, 7 September: "we just have to give those above the median a
        ! 3.22 higher chance of converting to SUD on average", and, on whether
        ! the two halves' own rates have to come out right, "we dont need it to
        ! hit those". So the ratio is the target and the levels are free -- they
        ! are already spoken for by b and by lambda_d.
        !
        ! NSDUH 2024, adults 26 and over, users split on past year use frequency:
        ! the lighter bands carry a disorder rate of 0.2230 and the heavier ones
        ! 0.7175, a ratio of 3.22 on n=1,679.
        real(8), parameter :: sud_gradient_data=3.22

        ! WHERE THE SPLIT FALLS, as a share of users BELOW it. Not one half: the
        ! survey records frequency in bands and the boundary between the light
        ! bands and the heavy ones sits at the 53.91st percentile of users by
        ! weight, because band two straddles the median and cannot be cut. A
        ! true median ratio is therefore not recoverable from the data at all,
        ! so the model is measured at the same place the 3.22 is measured.
        ! NOT a target constant: moving it changes what the moment MEANS, so an
        ! archived point measured at the old split is stale and the model hash
        ! must say so.
        real(8), parameter :: sud_grad_split=0.5391

        ! A HISTOGRAM, NOT A SECOND PASS. The split is a quantile of the users'
        ! own quantity distribution and is not known until every household has
        ! been visited. The distribution nest is the expensive one in this file
        ! and walking it twice to learn one number is not worth it, so mass is
        ! binned on a log grid as the nest runs and the quantile is read off the
        ! cumulative afterwards. 600 bins over eight decades is 3.1 per cent of
        ! quantity per bin, and the boundary bin is split proportionally, so the
        ! only error left is the within-bin variation of the disorder share.
        integer, parameter :: sud_grad_bins=600
        real(8), parameter :: sud_grad_qmin=1.d-8, sud_grad_qmax=1.d2
        real(8), dimension(sud_grad_bins) :: sud_grad_user_mass=0
        real(8), dimension(sud_grad_bins) :: sud_grad_sud_mass=0
        real(8), dimension(sud_grad_bins) :: sud_grad_clean_mass=0
        real(8), dimension(sud_grad_bins) :: sud_grad_clean_haz=0

        ! TWO RATIOS, AND THEY ARE NOT THE SAME OBJECT.
        !
        ! FLOW is the one the author named -- the chance of CONVERTING, so the
        ! mean onset hazard among clean users above the split over the same
        ! below it. It is a function of the clean users' quantity distribution
        ! and of the hazard alone, which makes lambda_addiction the only thing
        ! that moves it, and that is what makes it an instrument's moment.
        !
        ! STOCK is what NSDUH literally measures -- the disorder share among all
        ! users above the split over the same below. It carries the flow AND the
        ! reverse channel, that having the disorder raises consumption, AND the
        ! duration of the disorder once acquired. Reported beside the flow so
        ! the size of the difference is visible rather than assumed; with
        ! lambda_addiction at zero the hazard is flat and FLOW is exactly one,
        ! so whatever STOCK reads then is the reverse channel on its own.
        real(8) :: model_sud_gradient_flow=0
        real(8) :: model_sud_gradient_stock=0
'''
edits.append((i, DECL))

# ------------------------------------------------------- helpers in `contains`
i = find(r'real\(8\) function addiction_onset_hazard_slope')
j = find(r'^\s*end function\s*$', i)
HELP = '''
        ! WHICH BIN A QUANTITY FALLS IN. Log spaced, so a bin is a fixed
        ! PROPORTION of quantity rather than a fixed amount of it: the users'
        ! quantities span orders of magnitude and a linear grid would put almost
        ! every one of them in the first bin.
        integer function sud_grad_bin_of(quantity_1)

            implicit none

            real(8), intent(in) :: quantity_1
            real(8) :: position_1

            if (quantity_1<=sud_grad_qmin) then

                sud_grad_bin_of=1

            elseif (quantity_1>=sud_grad_qmax) then

                sud_grad_bin_of=sud_grad_bins

            else

                position_1=log(quantity_1/sud_grad_qmin)/log(sud_grad_qmax/sud_grad_qmin)
                sud_grad_bin_of=min(max(int(position_1*sud_grad_bins)+1,1),sud_grad_bins)

            end if

        end function

        ! READ THE TWO RATIOS OFF THE HISTOGRAM.
        !
        ! The cut is walked up the cumulative user mass until sud_grad_split of
        ! it is below, and the bin the cut lands INSIDE is divided in the same
        ! proportion across all four histograms. Splitting the boundary bin
        ! matters more than it looks: quantities pile up where the policy
        ! function is flat, so a single bin can hold several per cent of users
        ! and assigning all of it to one side moves the ratio.
        !
        ! An undefined ratio is -1, which is this file's convention for a
        ! moment with no mass behind it, and not zero: zero is a value the
        ! ratio could legitimately take and would be read as a measurement.
        subroutine sud_gradient_from_histogram()

            implicit none

            integer :: bin_1
            real(8) :: total_1,cut_1,running_1,share_below_1
            real(8) :: light_users_1,heavy_users_1,light_sud_1,heavy_sud_1
            real(8) :: light_clean_1,heavy_clean_1,light_haz_1,heavy_haz_1
            real(8) :: light_rate_1,heavy_rate_1

            model_sud_gradient_flow=-1
            model_sud_gradient_stock=-1

            total_1=sum(sud_grad_user_mass)
            if (total_1<=10.d0**(-14)) return

            cut_1=sud_grad_split*total_1
            running_1=0
            light_users_1=0
            heavy_users_1=0
            light_sud_1=0
            heavy_sud_1=0
            light_clean_1=0
            heavy_clean_1=0
            light_haz_1=0
            heavy_haz_1=0

            do bin_1=1,sud_grad_bins

                if (sud_grad_user_mass(bin_1)<=0) cycle

                if (running_1+sud_grad_user_mass(bin_1)<=cut_1) then

                    share_below_1=1

                elseif (running_1>=cut_1) then

                    share_below_1=0

                else

                    share_below_1=(cut_1-running_1)/sud_grad_user_mass(bin_1)

                end if

                light_users_1=light_users_1+share_below_1*sud_grad_user_mass(bin_1)
                heavy_users_1=heavy_users_1+(1-share_below_1)*sud_grad_user_mass(bin_1)
                light_sud_1=light_sud_1+share_below_1*sud_grad_sud_mass(bin_1)
                heavy_sud_1=heavy_sud_1+(1-share_below_1)*sud_grad_sud_mass(bin_1)
                light_clean_1=light_clean_1+share_below_1*sud_grad_clean_mass(bin_1)
                heavy_clean_1=heavy_clean_1+(1-share_below_1)*sud_grad_clean_mass(bin_1)
                light_haz_1=light_haz_1+share_below_1*sud_grad_clean_haz(bin_1)
                heavy_haz_1=heavy_haz_1+(1-share_below_1)*sud_grad_clean_haz(bin_1)

                running_1=running_1+sud_grad_user_mass(bin_1)

            end do

            if ((light_users_1>10.d0**(-14)) .AND. (heavy_users_1>10.d0**(-14))) then

                light_rate_1=light_sud_1/light_users_1
                heavy_rate_1=heavy_sud_1/heavy_users_1
                if (light_rate_1>10.d0**(-14)) model_sud_gradient_stock=heavy_rate_1/light_rate_1

            end if

            if ((light_clean_1>10.d0**(-14)) .AND. (heavy_clean_1>10.d0**(-14))) then

                light_rate_1=light_haz_1/light_clean_1
                heavy_rate_1=heavy_haz_1/heavy_clean_1
                if (light_rate_1>10.d0**(-14)) model_sud_gradient_flow=heavy_rate_1/light_rate_1

            end if

        end subroutine
'''
edits.append((j, HELP))

# ------------------------------------------------------------------- zeroing
i = find(r'if \(accumulating_beta_types==0\) model_alive_by_age\(:\)=0')
ZERO = '''        if (accumulating_beta_types==0) sud_grad_user_mass(:)=0
        if (accumulating_beta_types==0) sud_grad_sud_mass(:)=0
        if (accumulating_beta_types==0) sud_grad_clean_mass(:)=0
        if (accumulating_beta_types==0) sud_grad_clean_haz(:)=0'''
edits.append((i, ZERO))

# --------------------------------------------------------------- accumulation
i = find(r'model_mass_total_users\(time_period\)=&')
assert 'model_mass_total_users(time_period)+distribution_mass_used' in L[i+1], L[i+1]
ACC = '''
                                        ! THE QUANTITY, NOT THE SPENDING, and the
                                        ! same expression the three lines above
                                        ! use, so a change to one is a change to
                                        ! both or the histogram stops describing
                                        ! the average it sits beside.
                                        sud_grad_quantity_1=frac_spent_on_addiction_used*&
                                            total_consumption_used/price_of_addictive_good
                                        sud_grad_bin_1=sud_grad_bin_of(sud_grad_quantity_1)

                                        sud_grad_user_mass(sud_grad_bin_1)=&
                                            sud_grad_user_mass(sud_grad_bin_1)+distribution_mass_used

                                        if (unemployment_index>threshold_addiction_index) then

                                            sud_grad_sud_mass(sud_grad_bin_1)=&
                                                sud_grad_sud_mass(sud_grad_bin_1)+distribution_mass_used

                                        else

                                            ! CLEAN USERS ONLY carry the hazard.
                                            ! Onset is what a household without
                                            ! the disorder faces; asking it of
                                            ! one that already has it would count
                                            ! a transition that cannot happen.
                                            sud_grad_clean_mass(sud_grad_bin_1)=&
                                                sud_grad_clean_mass(sud_grad_bin_1)+distribution_mass_used

                                            sud_grad_clean_haz(sud_grad_bin_1)=&
                                                sud_grad_clean_haz(sud_grad_bin_1)+distribution_mass_used*&
                                                addiction_onset_hazard(sud_grad_quantity_1)

                                        end if
'''
edits.append((i + 1, ACC))

# ------------------------------------------------- locals for the accumulation
i = find(r'choose_addiction_1,age_group_1\s*$')
edits.append((i, '        integer :: sud_grad_bin_1\n        real(8) :: sud_grad_quantity_1'))

# ------------------------------------------------------------ post-processing
i = find(r'model_drugs_used_by_users_on_average\(time_period\)/max\(model_mass_total_users')
j = find(r'^\s*end if\s*$', i)
POST = '''
        if (current_beta_type==number_of_beta_types) call sud_gradient_from_histogram()
'''
edits.append((j, POST))

# ------------------------------------------------------------- the MOMENT line
i = find(r'"MOMENT lambda_d  disorder rate')
MOM = '''            write(*,*) "MOMENT sud_grad  disorder gradient, flow   model=",&
                model_sud_gradient_flow, " target=", sud_gradient_data
            write(*,*) "UNTARGETED disorder gradient, stock          model=",&
                model_sud_gradient_stock, " observed=", sud_gradient_data'''
edits.append((i + 1, MOM))

for at, block in sorted(edits, key=lambda e: -e[0]):
    L[at + 1:at + 1] = block.split('\n')

open(src, 'w').write('\n'.join(L))
print('patched', src)
