#!/usr/bin/env python3
"""patch_latch.py SRC OUT -- THE CHILD PENALTY KEYED ON THE PARENT'S HOMELESSNESS, CARRIED WHERE THE SUD
HISTORY WAS (10 October). Replaces patch_hh.py, which added the latch as two more productivity blocks and
doubled the state.

The author: "Set deltad to 0 and replace it instead with a two class model with deltah=0.31 that is a
penalty for homelessness throughout childhood instead (the same way Sud enters adult earnings, ie parent
was homeless at some point during the childhood of the kid)", and then: "Since you track if they had a Sud,
why can't you just flip that off and instead track if they were homeless instead?", "you can still turn off
the ever had a Sud state since we shut that one off when we add deltah", "we don't need the model to have
four class in the run since the deltad class can be turned off".

WHY THE SLOT IS FREE. The folded unemployment index carries three SUD blocks -- never had it, had it and
clean now, has it -- and the only thing that separates the first two is the child's inherited penalty
(ever_sud_of has no other reader: onset, recovery, mortality and treatment all read the current disorder).
With delta_d at zero the recovered block is the never block under another name.

WHAT TAKES ITS PLACE. A latch L: the household has been homeless in some period at an age up to
child_at_home_last_index (26 to 50), the years its child is at home. It has to exist beside the disorder in
both directions, so the blocks become four, block 2*d + L:

    block 0: clean,    never homeless while the child was at home
    block 1: clean,    homeless at some point while the child was at home
    block 2: disorder, never homeless ...
    block 3: disorder, homeless at some point ...

each 3 employment states x number_of_smi_states, so the grid is 12 x number_of_smi_states (24) against 18.
threshold_addiction_index stays 2 x 3 x number_of_smi_states (12): every one of the sites that test
unemployment_index > threshold for "has the disorder" reads correctly, and every loop over the clean range
covers both clean blocks, as it covered the never and recovered blocks before.

THE LATCH FLIPS INSIDE THE TRANSITION. unemployment_process already takes the household's homelessness
this period (its fourth index, 2 for homeless) and its age, so the switch is built there: a household
homeless at an age up to 50 lands in L = 1 next period whatever its disorder does, and L is never reset.
No value-function or distribution site needs an edit. Newborns enter with L = 0.

WHAT THE CHILD INHERITS. transmit_of = max(L, homeless now), where ever_sud_of stood, at the parent's death
before 50 (weighted by the chance of dying) or at 50 (weight one) -- the timing child_continuation_value and
newborn_parent_share_acc already use. Two productivity classes, as before: class 1 carries 1 - delta_h
(penalty_child_homeless, set to 0.31 in the handover; penalty_child_addicted to 0), and the homelessness
birth shift of the two-class branch is off so delta_h is not counted twice.

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


# 1. FOUR SUD-BY-LATCH BLOCKS
rep("        integer, parameter :: unemployment_grid_size=&\n"
    "            include_addiction*9*number_of_smi_states+(1-include_addiction)*3\n",
    "        ! THE HOMELESSNESS LATCH IN THE RECOVERED BLOCK'S PLACE (10 October, code/deltah/patch_latch.py):\n"
    "        ! blocks 2*d + L, d the disorder now and L homeless at some point while the child was at home.\n"
    "        integer, parameter :: homeless_latch=1\n"
    "        integer, parameter :: unemployment_grid_size=&\n"
    "            include_addiction*(9+3*homeless_latch)*number_of_smi_states+(1-include_addiction)*3\n")

# 2. THE INDEX AND ITS FOURTH COORDINATE
rep("            idx_of=3*number_of_smi_states*(d_1+ever_1)+3*m_1+e_1\n",
    "            if (homeless_latch==1) then\n"
    "                idx_of=3*number_of_smi_states*(2*d_1+ever_1)+3*m_1+e_1\n"
    "            else\n"
    "                idx_of=3*number_of_smi_states*(d_1+ever_1)+3*m_1+e_1\n"
    "            end if\n")
rep("            ever_sud_of=min((i_1-1)/(3*number_of_smi_states),1)\n",
    "            ! with the latch on, the fourth coordinate is the latch, not the SUD history\n"
    "            if (homeless_latch==1) then\n"
    "                ever_sud_of=mod((i_1-1)/(3*number_of_smi_states),2)\n"
    "            else\n"
    "                ever_sud_of=min((i_1-1)/(3*number_of_smi_states),1)\n"
    "            end if\n")
rep("        integer function ever_sud_of(i_1)\n",
    "        ! what the child inherits: with the latch on, the latch or homelessness now (the period the parent\n"
    "        ! dies in, or 50); otherwise the SUD history\n"
    "        integer function transmit_of(u_1,homeless_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: u_1,homeless_1\n"
    "            if (homeless_latch==1) then\n"
    "                transmit_of=max(ever_sud_of(u_1),homeless_1-1)\n"
    "            else\n"
    "                transmit_of=ever_sud_of(u_1)\n"
    "            end if\n"
    "        end function\n\n"
    "        integer function ever_sud_of(i_1)\n")

# 3. THE BUILDER: L free of d, never reset, set by homelessness at an age up to 50; newborns at L = 0
rep("                        do ever_c_1=d_c_1,include_addiction\n",
    "                        do ever_c_1=(1-homeless_latch)*d_c_1,include_addiction\n")
rep("                            ever_f_1=max(ever_c_1,d_f_1)\n",
    "                            if (homeless_latch==1) then\n"
    "                                ever_f_1=ever_c_1\n"
    "                                if ((h_1==2) .AND. (a_1<=child_at_home_last_index)) ever_f_1=1\n"
    "                            else\n"
    "                                ever_f_1=max(ever_c_1,d_f_1)\n"
    "                            end if\n")
rep("                                                idx_of(e_f_1,m_f_1,d_f_1,d_f_1),h_1,d_f_1,p_1)=&\n",
    "                                                idx_of(e_f_1,m_f_1,d_f_1,(1-homeless_latch)*d_f_1),h_1,d_f_1,p_1)=&\n")

# 4. THE INDEX MAP'S CHECKS, for four blocks: half the states carry the disorder and half the latch, and
# the disorder no longer implies the fourth coordinate
rep("            if (count_sud_1/=(unemployment_grid_size/3)) bad_1=bad_1+1\n"
    "            if (count_ever_1/=(2*unemployment_grid_size/3)) bad_1=bad_1+1\n",
    "            if (homeless_latch==1) then\n"
    "            if (count_sud_1/=(unemployment_grid_size/2)) bad_1=bad_1+1\n"
    "            if (count_ever_1/=(unemployment_grid_size/2)) bad_1=bad_1+1\n"
    "            else\n"
    "            if (count_sud_1/=(unemployment_grid_size/3)) bad_1=bad_1+1\n"
    "            if (count_ever_1/=(2*unemployment_grid_size/3)) bad_1=bad_1+1\n"
    "            end if\n")
rep("                if (sud_of(i_1)>ever_sud_of(i_1)) bad_1=bad_1+1\n",
    "                if ((homeless_latch==0) .AND. (sud_of(i_1)>ever_sud_of(i_1))) bad_1=bad_1+1\n")

# 5. THE CHILD: class 1 carries delta_h, no birth shift
rep("        child_penalty_factor(1)=(1.d0-penalty_child_addicted)**include_child_penalty\n",
    "        child_penalty_factor(1)=(1.d0-penalty_child_addicted)**include_child_penalty\n"
    "        if (homeless_latch==1) child_penalty_factor(1)=(1.d0-penalty_child_homeless)**include_child_penalty\n")
rep("                else if (child_penalty_classes==2) then\n\n"
    "                    class_1=d_index\n"
    "                    penalty=(1-penalty_child_homeless)**((h_index-1)*include_child_penalty)\n",
    "                else if (child_penalty_classes==2) then\n\n"
    "                    class_1=d_index\n"
    "                    penalty=(1-penalty_child_homeless)**((h_index-1)*include_child_penalty)\n"
    "                    if (homeless_latch==1) penalty=1.d0\n")
rep("            transmitted_1=ever_sud_of(unemployment_index_1)\n",
    "            transmitted_1=transmit_of(unemployment_index_1,homeless_1)\n")
rep("newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),is_homeless_1)",
    "newborn_parent_share_acc(employment_index,transmit_of(unemployment_index,is_homeless_1),is_homeless_1)", n=2)

assert 'integer, parameter :: child_penalty_classes=2\n' in s, 'expected the two-class build'
open(dst, 'w').write(s)
print(f'wrote {dst}')
