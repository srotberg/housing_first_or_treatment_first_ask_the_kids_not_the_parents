"""patch_grace.py IN OUT LAG -- THE GRACE YEARS: treatment keeps the voucher, sober or not, for the first LAG years of the
path (19 October; the author: "maybe also a transition in which going to treatment and not being sober is allowed in the
first 5 periods of the reform. you can try both 100% and 20% with those with SUD not being able to stop using, but they
can go to treatment, and in the first 5 years this is acceptable").

Run on the rule-CA transition source (treat/patch_treatCA.py's output: the disorder fails the screen in treatment or
not, any use fails, abstention off, so a household with a SUD cannot stop using). The screen is on from year 1, as in
the main no-escape path. For t <= LAG one exemption is added: a household in treatment passes (meets_condition_1, which
only a household with the disorder can meet, since only it can choose treatment), whatever it uses. From t = LAG+1 the
screen is rule CA's with no exemption. Every household knows the schedule from year 1: the backward pass solves year LAG
against year LAG+1's values.

  1. grace_now, a module integer (0 by default, so the terminal solve and everything outside the two transition loops
     run rule CA), set in both loops beside the drug price and pi_V: 1 for t <= LAG, else 0. The forward pass prints
     TRANSITION GRACE t= <t> grace= <0|1> lag= <LAG>, which the launcher checks.
  2. compute_voucher_index_1, in the screen's rule-CA branch: if grace_now is 1 and the household is in treatment,
     fails_1 = 0. The voucher category then routes it as a passing household everywhere the category is read (the
     lottery, the EV key, the distribution), as rule C routes a treated one.
The lottery rows do not depend on grace_now (only the category does), so build_voucher_probabilities is unchanged."""
import sys
src, out, lag = sys.argv[1], sys.argv[2], int(sys.argv[3])
assert 1 <= lag <= 20, lag
s = open(src).read()


def once(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


once("        integer :: voucher_conditional_on_clean=0\n",
     "        integer :: voucher_conditional_on_clean=0\n"
     f"        integer :: grace_now=0,grace_lag={lag}   ! patch_grace.py: treatment passes the screen for t<=grace_lag\n")

ca = ("            if (unemployment_index>threshold_addiction_index) fails_1=1\n"
      "            if (drug_share_1>0) fails_1=1\n")
assert s.count("            ! RULE CA (patch_treatCA.py)") == 1, 'not the rule-CA transition source'
once(ca, ca + "            ! THE GRACE YEARS (patch_grace.py): in treatment the household passes, sober or not\n"
              "            if ((grace_now==1) .AND. (meets_condition_1==1)) fails_1=0\n")

pv = ("                probability_of_voucher_benchmark_used=probability_of_voucher_path(time_index)\n"
      "                probability_of_voucher_benchmark_used_1=probability_of_voucher_path(time_index)\n"
      "                call build_voucher_probabilities()\n")
assert s.count(pv) == 2, s.count(pv)
head, back, fwd = s.split(pv)
assert 'do time_index=max(transition_length-1,1),1,-1' in head[-3000:], 'first site is not the backward pass'
assert 'do time_index=1,max(transition_length-1,1)' in back[-6000:], 'second site is not the forward pass'


def site(printing):
    return ("                ! THE GRACE YEARS (patch_grace.py): treatment passes the screen for the first grace_lag years\n"
            "                grace_now=0\n"
            "                if (time_index<=grace_lag) grace_now=1\n"
            + ("                write(*,*) \"TRANSITION GRACE t=\", time_index, \" grace=\", grace_now, \" lag=\", grace_lag, &\n"
               "                    \" screen=\", voucher_conditional_on_clean\n" if printing else "")
            + pv)


s = head + site(False) + back + site(True) + fwd
open(out, 'w').write(s)
print(f'grace: treatment passes the screen for t <= {lag}, set at both transition sites -> {out}')
