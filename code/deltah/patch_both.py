#!/usr/bin/env python3
"""patch_both.py SRC OUT -- BOTH CHILD PENALTIES: delta_d ON THE PARENT'S SUD HISTORY AND delta_h ON ITS HOMELESSNESS
WHILE THE CHILD WAS AT HOME (11 October). The author: "remove deltad is a big problem....we need to bring it back in.
can you actually solve the model with both deltad=0.24 and deltah=0.31?", "i think the deltad=0.24 is important",
"you have to first solve the benchmark with both deltad=0.24 and deltah=0.31 (and you can fix the parameters to what
the benchmark with deltad=0.24 and deltah=0 are). and then do TF full GE with piv and pv adjusting in the long run".

patch_latch.py carried the homelessness latch L in the slot of the SUD history, which was free only with delta_d at
zero. With both penalties the state carries both bits. The folded unemployment index becomes SIX blocks of
3 employment states x number_of_smi_states, ordered so that the 138 sites testing unemployment_index against
threshold_addiction_index for "has the disorder" still read correctly (the disorder blocks are the top two) and so
that the newborn draw over the first blocks lands at L = 0:

    block 0: clean, never had the disorder, L = 0        block 3: clean, recovered,        L = 1
    block 1: clean, recovered,              L = 0        block 4: has the disorder (ever), L = 0
    block 2: clean, never had the disorder, L = 1        block 5: has the disorder (ever), L = 1

    block = (1-d)*(ever + 2L) + d*(4 + L);  threshold_addiction_index = 4 blocks;  grid = 6 blocks (36 at two SMI states)

L flips inside unemployment_process: a household homeless this period at an age up to child_at_home_last_index
carries L = 1 from next period on, never reset; newborns enter at L = 0. The child's inherited class is FOUR-valued,
child_penalty_classes = 4 (the four-class branch the source already carries, factors 1, 1 - delta_d, 1 - delta_h and
their product): its first bit is the SUD history (ever_sud_of, as before) and its second is max(L, homeless now) at
the parent's death before 50 or at 50, carried in the housing slot of expected_child_value and newborn_parent_share
(transmit_hl), so the newborn branch's class_1 = d_index + 2*(h_index-1) reads it with no further change. The
productivity grid doubles with the classes (employment_grid_size = 13 x 4), the unemployment grid grows by half.

Refuses unless every anchor is found the expected number of times. Source untouched.
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old[:140])
    s = s.replace(old, new)


# 1. FOUR CHILD CLASSES, SIX UNEMPLOYMENT BLOCKS, THE THRESHOLD AT FOUR
rep("        integer, parameter :: child_penalty_classes=2\n",
    "        ! FOUR CLASSES (11 October, code/deltah/patch_both.py): the SUD history and the homelessness latch\n"
    "        integer, parameter :: child_penalty_classes=4\n")
rep("        integer, parameter :: unemployment_grid_size=&\n"
    "            include_addiction*9*number_of_smi_states+(1-include_addiction)*3\n",
    "        ! THE HOMELESSNESS LATCH BESIDE THE SUD HISTORY (11 October, code/deltah/patch_both.py): six blocks,\n"
    "        ! (never, recovered) x L in the clean half and the disorder x L on top; see the patch's header.\n"
    "        integer, parameter :: homeless_latch=1\n"
    "        integer, parameter :: unemployment_grid_size=&\n"
    "            include_addiction*18*number_of_smi_states+(1-include_addiction)*3\n")
rep("        integer, parameter :: threshold_addiction_index=2*3*number_of_smi_states\n",
    "        integer, parameter :: threshold_addiction_index=4*3*number_of_smi_states\n")

# 2. THE ACCESSORS
rep("            sud_of=(i_1-1)/(2*3*number_of_smi_states)\n",
    "            sud_of=(i_1-1)/(4*3*number_of_smi_states)\n")
rep("            ever_sud_of=min((i_1-1)/(3*number_of_smi_states),1)\n",
    "            ! blocks 4 and 5 carry the disorder (ever); below them the first bit of the block is the history\n"
    "            if ((i_1-1)/(3*number_of_smi_states)>=4) then\n"
    "                ever_sud_of=1\n"
    "            else\n"
    "                ever_sud_of=mod((i_1-1)/(3*number_of_smi_states),2)\n"
    "            end if\n")
rep("        integer function ever_sud_of(i_1)\n",
    "        ! HOMELESS AT SOME POINT WHILE THE CHILD WAS AT HOME: the latch L of the block\n"
    "        integer function latch_of(i_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: i_1\n"
    "            if ((i_1-1)/(3*number_of_smi_states)>=4) then\n"
    "                latch_of=(i_1-1)/(3*number_of_smi_states)-4\n"
    "            else\n"
    "                latch_of=((i_1-1)/(3*number_of_smi_states))/2\n"
    "            end if\n"
    "        end function\n\n"
    "        ! WHAT THE CHILD INHERITS IN THE HOUSING SLOT: 2 if the parent is homeless now or has been while the\n"
    "        ! child was at home, else 1 (the period the parent dies in, or 50, as the SUD history is read)\n"
    "        integer function transmit_hl(u_1,homeless_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: u_1,homeless_1\n"
    "            transmit_hl=1+max(latch_of(u_1),homeless_1-1)\n"
    "        end function\n\n"
    "        integer function ever_sud_of(i_1)\n")
rep("        integer function idx_of(e_1,m_1,d_1,ever_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: e_1,m_1,d_1,ever_1\n"
    "            idx_of=3*number_of_smi_states*(d_1+ever_1)+3*m_1+e_1\n",
    "        integer function idx_of(e_1,m_1,d_1,ever_1,l_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: e_1,m_1,d_1,ever_1,l_1\n"
    "            ! block = (1-d)(ever + 2L) + d(4 + L): the disorder on top, the latch beside the history\n"
    "            idx_of=3*number_of_smi_states*((1-d_1)*(ever_1+2*l_1)+d_1*(4+l_1))+3*m_1+e_1\n")

# 3. EVERY CALL OF idx_of: newborns and the draw at L = 0, the round trip with the latch, the builder with its own
rep("newborn_state_draw(idx_of(1,0,0,0))", "newborn_state_draw(idx_of(1,0,0,0,0))")
rep("newborn_state_draw(idx_of(1,1,0,0))", "newborn_state_draw(idx_of(1,1,0,0,0))")
rep("            if (idx_of(emp_of(i_1),smi_of(i_1),sud_of(i_1),ever_sud_of(i_1))/=i_1) bad_1=bad_1+1\n",
    "            if (idx_of(emp_of(i_1),smi_of(i_1),sud_of(i_1),ever_sud_of(i_1),latch_of(i_1))/=i_1) bad_1=bad_1+1\n")
rep("                        i_0=idx_of(emp_1,smi_1,0,0)\n                        i_1=idx_of(emp_1,smi_1,0,1)\n",
    "                        i_0=idx_of(emp_1,smi_1,0,0,0)\n                        i_1=idx_of(emp_1,smi_1,0,1,0)\n")

# 4. THE BUILDER: the latch loop around the future-disorder loop, the flip, the indices with L; newborns at L = 0
rep("        integer :: a_1,p_1,h_1,d_c_1,d_f_1,m_c_1,m_f_1,e_c_1,e_f_1,i_1,j_1,ever_c_1,ever_f_1\n",
    "        integer :: a_1,p_1,h_1,d_c_1,d_f_1,m_c_1,m_f_1,e_c_1,e_f_1,i_1,j_1,ever_c_1,ever_f_1,l_c_1,l_f_1\n")
rep("                        do ever_c_1=d_c_1,include_addiction\n\n"
    "                        do d_f_1=0,include_addiction\n",
    "                        do ever_c_1=d_c_1,include_addiction\n\n"
    "                        ! THE HOMELESSNESS LATCH (11 October, code/deltah/patch_both.py): a household homeless\n"
    "                        ! this period at an age up to child_at_home_last_index carries L = 1 from next period\n"
    "                        ! on, whatever its disorder does, and L is never reset.\n"
    "                        do l_c_1=0,homeless_latch\n\n"
    "                        l_f_1=l_c_1\n"
    "                        if ((homeless_latch==1) .AND. (h_1==2) .AND. (a_1<=child_at_home_last_index)) l_f_1=1\n\n"
    "                        do d_f_1=0,include_addiction\n")
rep("                                        i_1=idx_of(e_c_1,m_c_1,d_c_1,ever_c_1)\n",
    "                                        i_1=idx_of(e_c_1,m_c_1,d_c_1,ever_c_1,l_c_1)\n")
rep("                                            j_1=idx_of(e_f_1,m_f_1,d_f_1,ever_f_1)\n",
    "                                            j_1=idx_of(e_f_1,m_f_1,d_f_1,ever_f_1,l_f_1)\n")
rep("                                                idx_of(e_f_1,m_f_1,d_f_1,d_f_1),h_1,d_f_1,p_1)=&\n",
    "                                                idx_of(e_f_1,m_f_1,d_f_1,d_f_1,0),h_1,d_f_1,p_1)=&\n")
# the loop's closing: the builder is the only place these two 'end do' at the ever_c loop's indentation follow the
# future-SMI, current-SMI and future-disorder loops' closings in this order
closing = ("                                end do\n\n"      # m_f_1
           "                            end do\n\n"          # m_c_1
           "                        end do\n\n"              # d_f_1
           "                        end do\n\n"              # ever_c_1 (l_c_1's goes in front of it)
           "                    end do\n\n"                  # d_c_1
           "                end do\n\n"                      # h_1
           "            end do\n\n"                          # p_1
           "        end do\n\n"                              # a_1
           "    end subroutine\n")
rep(closing,
    "                                end do\n\n"
    "                            end do\n\n"
    "                        end do\n\n"
    "                        end do\n\n"
    "                        end do\n\n"
    "                    end do\n\n"
    "                end do\n\n"
    "            end do\n\n"
    "        end do\n\n"
    "    end subroutine\n")

# 5. WHAT THE CHILD INHERITS: the housing slot carries the latch or homelessness now, at every site that reads a
# parent's state into the child's draw (the parent's valuation, the banked shares, the per-death push)
rep("                    expected_child_value(employment_index_1,transmitted_1,homeless_1)\n",
    "                    expected_child_value(employment_index_1,transmitted_1,transmit_hl(unemployment_index_1,homeless_1))\n", n=2)
rep("newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),is_homeless_1)",
    "newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),transmit_hl(unemployment_index,is_homeless_1))", n=2)
rep("employment_index,is_addicted_1,is_homeless_2)*&\n",
    "employment_index,is_addicted_1,transmit_hl(unemployment_index,is_homeless_2))*&\n", n=2)

# 6. THE INDEX MAP'S CHECKS: the latch covers half the states; the counts of the disorder and the history are
# unchanged (two of six blocks, four of six); the message says what the grid is
rep("        integer :: i_1,bad_1,count_emp_1,count_ui_1,count_out_1,count_smi_1,count_sud_1,count_ever_1\n",
    "        integer :: i_1,bad_1,count_emp_1,count_ui_1,count_out_1,count_smi_1,count_sud_1,count_ever_1,count_latch_1\n")
rep("        count_ever_1=0\n", "        count_ever_1=0\n        count_latch_1=0\n")
rep("            if (ever_sud_of(i_1)==1) count_ever_1=count_ever_1+1\n",
    "            if (ever_sud_of(i_1)==1) count_ever_1=count_ever_1+1\n"
    "            if (latch_of(i_1)==1) count_latch_1=count_latch_1+1\n")
rep("            if (count_ever_1/=(2*unemployment_grid_size/3)) bad_1=bad_1+1\n",
    "            if (count_ever_1/=(2*unemployment_grid_size/3)) bad_1=bad_1+1\n"
    "            if (count_latch_1/=(unemployment_grid_size/2)) bad_1=bad_1+1\n")
rep('        write(*,*) "index map: three SUD blocks, threshold="',
    '        write(*,*) "index map: six blocks, the SUD history by the homelessness latch, threshold="')

assert 'homeless_latch=1' in s and s.count('transmit_hl(') == 7 and s.count('latch_of(') == 4, (s.count('transmit_hl('), s.count('latch_of('))
open(dst, 'w').write(s)
print(f'wrote {dst}')
