"""patch_announce.py IN OUT LAG -- THE ANNOUNCED POLICY: the screen switched off for the first LAG years of the path
(19 October; the author: "Another test we can do is one where the policy is announced and households have no escape but
it is only implemented after 5 years. So it is known it is coming. But those with SUD cannot stay sober but they can go
to treatment", and "yes, launch it at 100% and 20%").

Run on the rule-CA transition source (treat/patch_treatCA.py's output). Three changes, each checked to land once:

  1. THE SCREEN BY YEAR. Both transition loops (the backward pass and the forward pass) already re-point the drug price
     and pi_V to year t before rebuilding the voucher lottery; here they also set voucher_conditional_on_clean to 0 for
     t <= LAG and to the handover's value (1, the terminal arm's) after. The test at t acts on the voucher a household
     holds at t+1, so the first revocations land in year LAG+2, as the main experiment's land in year 2: the reform is
     the main experiment's, started LAG years later, with every household knowing from year 1 that it is coming. The
     backward pass solves year LAG against year LAG+1's values, which are solved with the screen on, so the foresight
     is in the household problem, not added to it.
  2. THE LOTTERY IS REBUILT FROM ZERO. build_voucher_probabilities sets the screen's rows only when the screen is on and
     does not clear them when it is off (create_unemployment_process zeroes the array before its one call). With the
     flag constant along the path that never mattered; switching it from 1 at t = LAG+1 to 0 at t = LAG in the backward
     pass would leave the holder's revocation row (1 -> 0) at the detection rate beside a stay row of 1, and the rows
     would sum to more than one. Zeroing first is what create_unemployment_process does, so with the flag constant the
     lottery is the same as before.
  3. THE OWN-TREATMENT FIX UNGATED (treat/patch_treatCu.py's one change, on the transition source). The corrected Housing
     First the path starts from runs it; tr70_CA gates it on the screen, which was true in every year of the main
     paths. Here the screen is off for LAG years, and gated those years would run the old arithmetic. With the screen
     on the gate was true, so years after LAG are unchanged.

The forward pass prints TRANSITION ANNOUNCE t= <t> screen= <flag> lag= <LAG> at every year, which the launcher checks."""
import sys
src, out, lag = sys.argv[1], sys.argv[2], int(sys.argv[3])
assert 1 <= lag <= 20, lag
s = open(src).read()
assert 'RULE CA (patch_treatCA.py)' in s, 'not the rule-CA transition source'


def once(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


once("        integer :: voucher_conditional_on_clean=0\n",
     "        integer :: voucher_conditional_on_clean=0\n"
     f"        integer :: ann_flag_terminal=-1,ann_lag={lag}   ! patch_announce.py: the screen is off for t<=ann_lag\n")

pv = ("                probability_of_voucher_benchmark_used=probability_of_voucher_path(time_index)\n"
      "                probability_of_voucher_benchmark_used_1=probability_of_voucher_path(time_index)\n"
      "                call build_voucher_probabilities()\n")
assert s.count(pv) == 2, s.count(pv)
head, back, fwd = s.split(pv)
assert 'do time_index=max(transition_length-1,1),1,-1' in head[-3000:], 'first site is not the backward pass'
assert 'do time_index=1,max(transition_length-1,1)' in back[-6000:], 'second site is not the forward pass'


def site(printing):
    return (pv.replace("                call build_voucher_probabilities()\n", "")
            + "                ! THE ANNOUNCED POLICY (patch_announce.py): the screen is off for the first ann_lag years\n"
              "                if (ann_flag_terminal<0) ann_flag_terminal=voucher_conditional_on_clean\n"
              "                voucher_conditional_on_clean=ann_flag_terminal\n"
              "                if (time_index<=ann_lag) voucher_conditional_on_clean=0\n"
            + ("                write(*,*) \"TRANSITION ANNOUNCE t=\", time_index, \" screen=\", &\n"
               "                    voucher_conditional_on_clean, \" lag=\", ann_lag, \" terminal=\", ann_flag_terminal\n"
               if printing else "")
            + "                voucher_probabilities=0\n"
              "                call build_voucher_probabilities()\n")


s = head + site(False) + back + site(True) + fwd

once("                                            if ((tc2_internal_on==1) .AND. (voucher_conditional_on_clean==1)) then\n",
     "                                            ! INTERNAL UNGATED (patch_treatCu.py, by patch_announce.py): the own-treatment fix in every year\n"
     "                                            if (tc2_internal_on==1) then\n")
open(out, 'w').write(s)
print(f'announce: screen off for t <= {lag}, lottery rebuilt from zero at both sites, own-treatment fix ungated -> {out}')
