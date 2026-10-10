#!/usr/bin/env python3
"""patch_hh.py SRC OUT -- THE CHILD PENALTY KEYED ON THE PARENT'S HOMELESSNESS, NOT ITS SUD (10 October).

The author: "Set deltad to 0 and replace it instead with a two class model with deltah=0.31 that is a
penalty for homelessness throughout childhood instead (the same way Sud enters adult earnings, ie parent
was homeless at some point during the childhood of the kid). Run the benchmark with all the parameters
fixed but with deltad=0 and deltah=0.31. And then simulate the tf long run in full ge with piv and pv
adjusting." Asked whether to key it on homelessness in the period the parent dies (no new state) or on
EVER being homeless while the child is at home (a new state), the author chose the latter.

WHAT THE NEW STATE IS. A latched bit, hh: the household has been homeless in some period at an age up to
child_at_home_last_index (26 to 50), the years its child is at home. It is the homelessness analogue of
ever_sud_of, which latches the disorder over the same years. It lives in the productivity index, which
already carries the child class the household was BORN into: with child_penalty_classes = 4 the packed
grid has four blocks, block c + 2*hh, c the household's own inherited class and hh its own latch.

    block 0: c = 0, hh = 0    factor 1
    block 1: c = 1, hh = 0    factor 1 - delta_h   (its parent was homeless while it was a child)
    block 2: c = 0, hh = 1    factor 1
    block 3: c = 1, hh = 1    factor 1 - delta_h

so the earnings a household draws depend on c alone and hh is pure memory. employment_process is block
diagonal (a household never changes block through the productivity process); the latch flips through
hl_next, which moves a household that is homeless THIS period, at an age up to 50, from block c to block
c + 2 for the next period, at every site that reads the next age's value or writes the next age's mass.

WHAT THE CHILD INHERITS. The class of the newborn is transmit_of = max(latch, homeless now), where the
existing code used ever_sud_of: at the parent's death before 50 (weighted by the chance of dying) or at 50
(weight one), the timing child_continuation_value and newborn_parent_share_acc already use. The parent
prices it through child_continuation_value exactly as it priced delta_d, at weight omega_c.

delta_d is not removed from the code: it is set to zero in the handover (penalty_child_addicted 0) and
delta_h to 0.31 (penalty_child_homeless 0.31), and with homeless_latch = 1 child_penalty_factor(1) reads
delta_h, so delta_d has no block to act in. The homelessness birth shift of the two-class branch is off
(penalty 1 in the four-class branch), so delta_h is not counted twice.

Refuses unless every anchor is found the expected number of times. Source untouched.
"""
import re
import sys

src, dst = sys.argv[1], sys.argv[2]
s = open(src).read()


def rep(old, new, n=1):
    global s
    c = s.count(old)
    assert c == n, (c, n, old[:120])
    s = s.replace(old, new)


# 1. FOUR BLOCKS AND THE SWITCH
rep("        integer, parameter :: child_penalty_classes=2\n",
    "        integer, parameter :: child_penalty_classes=4\n"
    "        ! THE HOMELESSNESS LATCH (10 October, code/deltah/patch_hh.py): blocks c + 2*hh, c the class the\n"
    "        ! household was born into, hh whether it has been homeless while its child was at home.\n"
    "        integer, parameter :: homeless_latch=1\n")

# 2. THE FACTORS: delta_h on the inherited class, the latch carries no factor
rep("        child_penalty_factor(0)=1.d0\n"
    "        child_penalty_factor(1)=(1.d0-penalty_child_addicted)**include_child_penalty\n"
    "        child_penalty_factor(2)=(1.d0-penalty_child_homeless)**include_child_penalty\n"
    "        child_penalty_factor(3)=child_penalty_factor(1)*child_penalty_factor(2)\n",
    "        if (homeless_latch==1) then\n"
    "            child_penalty_factor(0)=1.d0\n"
    "            child_penalty_factor(1)=(1.d0-penalty_child_homeless)**include_child_penalty\n"
    "            child_penalty_factor(2)=1.d0\n"
    "            child_penalty_factor(3)=child_penalty_factor(1)\n"
    "        else\n"
    "        child_penalty_factor(0)=1.d0\n"
    "        child_penalty_factor(1)=(1.d0-penalty_child_addicted)**include_child_penalty\n"
    "        child_penalty_factor(2)=(1.d0-penalty_child_homeless)**include_child_penalty\n"
    "        child_penalty_factor(3)=child_penalty_factor(1)*child_penalty_factor(2)\n"
    "        end if\n")

# 3. THE NEWBORN'S BLOCK: the transmitted bit (the d slot now carries it), no birth shift
rep("                if (child_penalty_classes>=4) then\n\n"
    "                    class_1=d_index+2*(h_index-1)\n",
    "                if ((child_penalty_classes>=4) .AND. (homeless_latch==1)) then\n\n"
    "                    class_1=d_index\n"
    "                    penalty=1.d0\n\n"
    "                else if (child_penalty_classes>=4) then\n\n"
    "                    class_1=d_index+2*(h_index-1)\n")

# 4. THE HELPERS, beside ever_sud_of
rep("        integer function ever_sud_of(i_1)\n",
    "        integer function latch_of(e_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: e_1\n"
    "            latch_of=0\n"
    "            if (homeless_latch==1) latch_of=min((e_1-1)/(2*employment_base_size),1)\n"
    "        end function\n\n"
    "        ! the productivity index next period: a household homeless this period, at an age the child is at\n"
    "        ! home, moves from block c to block c + 2 (hh 0 -> 1); everything else is unchanged\n"
    "        integer function hl_next(e_1,homeless_1,age_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: e_1,homeless_1,age_1\n"
    "            hl_next=e_1\n"
    "            if ((homeless_latch==1) .AND. (homeless_1==2) .AND. (age_1<=child_at_home_last_index)) then\n"
    "                if (latch_of(e_1)==0) hl_next=e_1+2*employment_base_size\n"
    "            end if\n"
    "        end function\n\n"
    "        ! what the child inherits: the latch or homelessness now (the period the parent dies in, or 50)\n"
    "        integer function transmit_of(u_1,e_1,homeless_1)\n"
    "            implicit none\n"
    "            integer, intent(in) :: u_1,e_1,homeless_1\n"
    "            if (homeless_latch==1) then\n"
    "                transmit_of=max(latch_of(e_1),homeless_1-1)\n"
    "            else\n"
    "                transmit_of=ever_sud_of(u_1)\n"
    "            end if\n"
    "        end function\n\n"
    "        integer function ever_sud_of(i_1)\n")

# 5. THE PARENT'S PRICE OF IT, and 6. WHO THE NEWBORN'S PARENT WAS
rep("            transmitted_1=ever_sud_of(unemployment_index_1)\n",
    "            transmitted_1=transmit_of(unemployment_index_1,employment_index_1,homeless_1)\n")
rep("newborn_parent_share_acc(employment_index,ever_sud_of(unemployment_index),is_homeless_1)",
    "newborn_parent_share_acc(employment_index,transmit_of(unemployment_index,employment_index,is_homeless_1),is_homeless_1)", n=2)

# 7. THE LATCH FLIPS: every statement that reads the next age's value or writes the next age's mass,
# in a branch where the household can be homeless (the owner branches pass a literal 1 and are skipped)
lines = s.split('\n')
stmts, cur = [], []
for i, l in enumerate(lines):
    code = '' if l.strip().startswith('!') else l.split('!')[0]
    cur.append(i)
    if not code.rstrip().endswith('&'):
        stmts.append(cur)
        cur = []
flipped = []
for st in stmts:
    txt = '\n'.join(lines[i] for i in st)
    if 'age_index+1' not in txt:
        continue
    hv = re.findall(r'survival_probability(?:_for_dist_iteration)?\s*&?\s*\(\s*age_index\s*,\s*(\w+)', txt)
    if not hv:
        continue
    hv = set(hv)
    assert len(hv) == 1, hv
    hv = hv.pop()
    if hv == '1':
        continue
    assert hv in ('is_homeless_1', 'is_homeless_2', 'evx_homeless'), hv
    new, k = re.subn(r'((?:future_unemployment_index|fui_1),(?:\s*&\s*\n\s*)?)(future_employment_index|fei_1)\b',
                     lambda m: f'{m.group(1)}hl_next({m.group(2)},{hv},age_index)', txt)
    if k:
        nl = new.split('\n')
        assert len(nl) == len(st)
        for j, i in enumerate(st):
            lines[i] = nl[j]
        flipped.append((st[0] + 1, hv, k))
s = '\n'.join(lines)
print('latch flips:', flipped)
total = sum(k for _, _, k in flipped)
EXPECT = int(sys.argv[3]) if len(sys.argv) > 3 else 11
assert total == EXPECT, f'expected {EXPECT} flipped index reads/writes, got {total}'
open(dst, 'w').write(s)
print(f'wrote {dst}: {total} flips')
