"""patch_useinc.py IN OUT -- print-only diagnostic: households and drug users (the y_u guard, character for character)
by interest-inclusive income (income_2, the y_u numerator's concept) in 400 fine bins of width 0.025 from -1, so the
use rate by income relative to the mean can be drawn against NSDUH. Nothing the run computes reads these arrays."""
import sys
src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()
decl_anchor = ("            total_addited_1,income_2,frac_getting_vouchers,homeowner_spending,total_addicted_and_homeless_1,bequest_1,&\n"
               "            addiction_consumption_1\n")
assert s.count(decl_anchor) == 1, s.count(decl_anchor)
s = s.replace(decl_anchor, decl_anchor +
    "        ! DIAG USEINC scratch (druginc diagnostic build only; print-only)\n"
    "        real(8), dimension(400), save :: dui_mass,dui_user,dui_inc,dui_uinc\n"
    "        integer :: dui_b\n")
reset_anchor = "        if (accumulating_beta_types==0) model_avg_income_drug_users(time_period)=0\n"
assert s.count(reset_anchor) == 1
s = s.replace(reset_anchor, reset_anchor +
    "        if (accumulating_beta_types==0) then\n"
    "            dui_mass=0; dui_user=0; dui_inc=0; dui_uinc=0\n"
    "        end if\n")
guard = ("                                    if (((addiction_consumption_1>0) .AND. (unemployment_index<=threshold_addiction_index)) .OR. &\n"
         "                                        ((unemployment_index>threshold_addiction_index) .AND. (tc2_ab_1==0))) then\n\n"
         "                                        diag_users_by_voucher_state(")
assert s.count(guard) == 1, s.count(guard)
hook = ("                                    ! DIAG USEINC: every household, then the users under the y_u guard\n"
        "                                    dui_b=min(max(int((income_2+1.d0)/0.025d0)+1,1),400)\n"
        "                                    dui_mass(dui_b)=dui_mass(dui_b)+distribution_mass_used\n"
        "                                    dui_inc(dui_b)=dui_inc(dui_b)+income_2*distribution_mass_used\n"
        "                                    if (((addiction_consumption_1>0) .AND. (unemployment_index<=threshold_addiction_index)) .OR. &\n"
        "                                        ((unemployment_index>threshold_addiction_index) .AND. (tc2_ab_1==0))) then\n"
        "                                        dui_user(dui_b)=dui_user(dui_b)+distribution_mass_used\n"
        "                                        dui_uinc(dui_b)=dui_uinc(dui_b)+income_2*distribution_mass_used\n"
        "                                    end if\n")
s = s.replace(guard, hook + guard)
norm_anchor = ("        if (current_beta_type==number_of_beta_types) then\n"
               "            model_avg_income_drug_users(time_period)=&\n"
               "                model_avg_income_drug_users(time_period)/max(model_mass_total_users(time_period),10.d0**(-14))\n"
               "        end if\n")
assert s.count(norm_anchor) == 1
s = s.replace(norm_anchor, norm_anchor +
    "        if ((current_beta_type==number_of_beta_types) .AND. (time_period==1)) then\n"
    "            write(*,*) 'DIAG USEINC BEGIN total_mass=', sum(dui_mass), ' total_users=', sum(dui_user)\n"
    "            do dui_b=1,400\n"
    "                if (dui_mass(dui_b)>0.d0) write(*,'(A,I4,4ES16.8)') ' DIAG USEINC ', dui_b, dui_mass(dui_b), dui_user(dui_b), &\n"
    "                    dui_inc(dui_b), dui_uinc(dui_b)\n"
    "            end do\n"
    "            write(*,*) 'DIAG USEINC END'\n"
    "        end if\n")
open(dst, 'w').write(s)
print('patched')
