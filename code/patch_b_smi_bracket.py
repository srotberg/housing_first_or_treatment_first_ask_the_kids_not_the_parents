#!/usr/bin/env python3
"""Calibrate b_smi_multiple on the SMI comorbidity ratio.

    patch_b_smi_bracket.py <master .f90> <output .f90>

THE SIGN IS REVERSED FROM THE USUAL CONVENTION, AND THAT IS THE WHOLE RISK.

Every other bracket here SUBTRACTS the gap, because its parameter and its
moment move together. This one does not. b enters flow utility as (b+q)^phi_q,
so the marginal value of the first unit is proportional to 1/b: a LARGER
b_smi_multiple makes the drug worth LESS to an SMI household, they use less,
and the ratio FALLS. Parameter and moment move in OPPOSITE directions.

    ratio ABOVE target -> want less SMI use -> RAISE b_smi_multiple
    ratio BELOW target -> want more SMI use -> LOWER b_smi_multiple

so the update ADDS the gap. CLAUDE.md records the same trap on
kappa_phi_d_level, whose bracket is DATA MINUS MODEL where every other is model
minus data, and warns that reading the operator alone gives the opposite
direction. Read this comment, not the plus sign.

HELD BY DEFAULT. b_smi_multiple_adjuster is 0, so nothing moves until it is
asked for in a vector. ENGINE.md's rule is obeyed: the else-branch zeroes
distance_b_smi_multiple, so a zero adjuster retires its own do-while term
rather than leaving a live distance the loop can never satisfy.

BOUNDS. Floored at 1e-6 because b at zero sends flow utility to minus infinity
for every SMI household at q=0 under u=-1/X. Capped at 10, well above 1, so the
search can correct an overshoot rather than sticking at the boundary -- a value
above one means SMI households find the drug LESS essential, which is the wrong
sign for the story but a legitimate place for a search to pass through.

THE DISTANCE IS RELATIVE. The ratio is order 7, not order 0.05 like the shares
the other brackets score, so an absolute distance against a 1e-3 rule would ask
for four significant figures on a moment measured off a distribution.
"""
import sys

DECL_ANCHOR = "        real(8) :: b_smi_multiple=1.d0\n"
DECL_NEW = DECL_ANCHOR + """
        ! ITS BRACKET. Held at zero, so the channel is measured but not moved
        ! until a vector asks for it. See patch_b_smi_bracket.py for the sign.
        real(8) :: b_smi_multiple_adjuster=0.d0
        real(8) :: distance_b_smi_multiple=1
        real(8) :: stopping_rule_b_smi_multiple=10.d0**(-2)
        real(8), parameter :: b_smi_multiple_max_rel_step=0.05d0
"""

TERM_ANCHOR = """        call one_convergence_term("kappa_find_smi",&
            distance_kappa_find_smi, stopping_rule_kappa_find_smi,&
            1, open_1)
"""
TERM_NEW = TERM_ANCHOR + """        call one_convergence_term("b_smi_multiple",&
            distance_b_smi_multiple, stopping_rule_b_smi_multiple,&
            1, open_1)
"""

WHILE_ANCHOR = "            (distance_kappa_find_smi>stopping_rule_kappa_find_smi) .OR. &\n"
WHILE_NEW = WHILE_ANCHOR + "            (distance_b_smi_multiple>stopping_rule_b_smi_multiple) .OR. &\n"

# The per-loop reset, disambiguated by its neighbours: distance_kappa_find_smi=1
# appears three times -- here, in the HELD branch, and in the NaN guard.
RESET_ANCHOR = """        distance_kappa_uem=1
        distance_kappa_find_smi=1
"""
RESET_NEW = RESET_ANCHOR + "        distance_b_smi_multiple=1\n"

# THE NaN GUARD, and it matters more here than for most. The ratio is a quotient
# of two quotients, so a corner that empties the SMI mass or the non-SMI SUD
# mass can produce a NaN that the do-while would read as convergence. The guard
# forces it to 1 and says so, exactly as every other distance does.
NAN_ANCHOR = """            if (distance_kappa_find_smi .NE. distance_kappa_find_smi) then
                write(*,*) "NaN DISTANCE: distance_kappa_find_smi, forced to 1 so the sweep cannot mistake it for convergence"
                distance_kappa_find_smi=1
            end if
"""
NAN_NEW = NAN_ANCHOR + """            if (distance_b_smi_multiple .NE. distance_b_smi_multiple) then
                write(*,*) "NaN DISTANCE: distance_b_smi_multiple, forced to 1 so the sweep cannot mistake it for convergence"
                distance_b_smi_multiple=1
            end if
"""

HANDOVER_ANCHOR = '                case ("b_smi_multiple")\n'
HANDOVER_NEW = '''                case ("b_smi_multiple_adjuster")
                    write(*,*) "HANDOVER b_smi_multiple_adjuster:",&
                        b_smi_multiple_adjuster, "->", handover_value
                    b_smi_multiple_adjuster=max(min(handover_value,10.d0),0.d0)

''' + HANDOVER_ANCHOR

# THE UPDATE ITSELF, placed after the kappa_find_smi bracket it is modelled on.
# Its else-branch is what makes a zero adjuster safe: it zeroes the distance, so
# the do-while term retires instead of never being satisfied.
UPDATE_ANCHOR = """                    else

                        distance_kappa_find_smi=0

                    end if
"""
UPDATE_NEW = UPDATE_ANCHOR + """
                    ! ------- b_smi_multiple, on the SMI comorbidity ratio -------
                    !
                    ! THE SIGN IS REVERSED FROM EVERY OTHER BRACKET HERE, and the
                    ! plus is not a typo. b enters flow utility as (b+q)^phi_q, so
                    ! the marginal value of the first unit goes like 1/b: a LARGER
                    ! multiple makes the drug worth LESS to an SMI household, they
                    ! use less, and the ratio FALLS. Parameter and moment move in
                    ! OPPOSITE directions, so a model ABOVE target wants the
                    ! parameter RAISED and the update ADDS the gap. CLAUDE.md
                    ! records the same trap on kappa_phi_d_level and warns that
                    ! reading the operator alone gives the opposite direction.
                    if ((b_smi_multiple_adjuster>0) .AND. (number_of_smi_states>1)) then

                        ! Three denominators, and a corner in any one of them
                        ! makes the ratio a fabricated number rather than a large
                        ! one. Same guard kappa_find_smi carries on its homeless
                        ! mass above.
                        if ((xtab_mass_smi(1)<=10.d0**(-12)) .OR. &
                            ((xtab_mass_pop(1)-xtab_mass_smi(1))<=10.d0**(-12)) .OR. &
                            ((xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1))<=10.d0**(-12))) then

                            write(*,*) "b_smi_multiple HELD: the comorbidity ratio is not"
                            write(*,*) "   measurable this loop -- an empty SMI, non-SMI or non-SMI SUD cell"

                            distance_b_smi_multiple=1

                        else

                            sud_smi_ratio_1=(xtab_sud_mass_smi(1)/xtab_mass_smi(1))/&
                                ((xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1))/&
                                (xtab_mass_pop(1)-xtab_mass_smi(1)))

                            cap_old_1=b_smi_multiple
                            b_smi_multiple=min(max(b_smi_multiple+b_smi_multiple_adjuster*&
                                (sud_smi_ratio_1-sud_smi_ratio_data),&
                                10.d0**(-6)),10.d0)
                            b_smi_multiple=cap_step_rel(b_smi_multiple,cap_old_1,&
                                b_smi_multiple_max_rel_step)

                            ! RELATIVE, because the ratio is order 7 and not order
                            ! 0.05 like the shares the other brackets score. An
                            ! absolute distance against a 1e-2 rule would be asking
                            ! for three significant figures on a moment read off a
                            ! distribution.
                            distance_b_smi_multiple=&
                                abs(sud_smi_ratio_1-sud_smi_ratio_data)/sud_smi_ratio_data

                        end if

                        write(*,*) "b_smi_multiple=", b_smi_multiple,&
                            " distance_b_smi_multiple=", distance_b_smi_multiple,&
                            " SUD ratio SMI over non-SMI=", sud_smi_ratio_1,&
                            " target=", sud_smi_ratio_data

                    else

                        distance_b_smi_multiple=0

                    end if
"""

# the local the update needs
LOCAL_ANCHOR = "        real(8) :: mean_drug_quantity_1,onset_at_mean_1,onset_step_1,treatment_step_1,&\n"
LOCAL_NEW = "        real(8) :: sud_smi_ratio_1=0\n" + LOCAL_ANCHOR

src = open(sys.argv[1]).read()
for anchor, new in ((DECL_ANCHOR, DECL_NEW), (TERM_ANCHOR, TERM_NEW),
                    (WHILE_ANCHOR, WHILE_NEW), (RESET_ANCHOR, RESET_NEW), (NAN_ANCHOR, NAN_NEW), (UPDATE_ANCHOR, UPDATE_NEW), (LOCAL_ANCHOR, LOCAL_NEW),
                    (HANDOVER_ANCHOR, HANDOVER_NEW)):
    n = src.count(anchor)
    if n != 1:
        sys.exit("REFUSED: anchor appears %d times, expected 1:\n%r" % (n, anchor[:80]))
    src = src.replace(anchor, new, 1)
open(sys.argv[2], "w").write(src)
print("added the declarations, the convergence term, the do-while entry,")
print("the per-loop reset and the adjuster's handover case")
