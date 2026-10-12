"""patch_treat.py MODE IN OUT -- two print-and-rule variants of the counterfactual build cf_fix2 (12 October).

MODE split: print only. Each steady-state pass prints 'MILBY SPLIT', the housed households with a SUD split by
  voucher status: mass, recovery-hazard sum, mass in treatment, mass with SMI. The author, 12 October, on the model's
  Milby ratio: "you need to explain the driver of this gap" -- the recovery hazard of a housed household depends only on
  treatment and SMI, so these four numbers say which of the two makes voucher holders recover faster.
MODE treat: the print, and the screen's rule changed so that a household with the disorder that is in treatment
  passes (the author, 12 October: "I suppose we can test whether vouchers conditional on being in treatment help and
  add it as robustness"). Use still fails. One line: the SUD test is ANDed with meets_condition_1 == 0, the flag the
  same subroutine already sets for a household in treatment. Every anchor must be unique."""
import sys
mode, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
assert mode in ('split', 'treat')
s = open(src).read()


def rep(old, new):
    global s
    n = s.count(old)
    assert n == 1, (n, old[:70])
    s = s.replace(old, new)


# the four accumulators, declared beside the Milby ones
rep("            xtab_rec_voucher,xtab_mass_voucher,xtab_rec_housed_nov,xtab_mass_housed_nov,&\n",
    "            xtab_rec_voucher,xtab_mass_voucher,xtab_rec_housed_nov,xtab_mass_housed_nov,&\n"
    "            xtab_treat_voucher,xtab_treat_housed_nov,xtab_smi_voucher,xtab_smi_housed_nov,&\n")
rep("        if (accumulating_beta_types==0) xtab_mass_housed_nov(time_period)=0\n",
    "        if (accumulating_beta_types==0) xtab_mass_housed_nov(time_period)=0\n"
    "        if (accumulating_beta_types==0) xtab_treat_voucher(time_period)=0\n"
    "        if (accumulating_beta_types==0) xtab_treat_housed_nov(time_period)=0\n"
    "        if (accumulating_beta_types==0) xtab_smi_voucher(time_period)=0\n"
    "        if (accumulating_beta_types==0) xtab_smi_housed_nov(time_period)=0\n")
T = ("real(policy_function_treatment(years_left_on_mortgage_index)%vector_transition_integer(time_period,age_index,"
     "financial_index,unemployment_index,employment_index,housing_status_index,voucher_index),8)")
rep("                                                xtab_mass_voucher(time_period)=&\n"
    "                                                    xtab_mass_voucher(time_period)+distribution_mass_used\n",
    "                                                xtab_mass_voucher(time_period)=&\n"
    "                                                    xtab_mass_voucher(time_period)+distribution_mass_used\n"
    "                                                xtab_treat_voucher(time_period)=xtab_treat_voucher(time_period)+&\n"
    "                                                    distribution_mass_used*" + T + "\n"
    "                                                if (smi_of(unemployment_index)>=1) xtab_smi_voucher(time_period)=&\n"
    "                                                    xtab_smi_voucher(time_period)+distribution_mass_used\n")
rep("                                                xtab_mass_housed_nov(time_period)=&\n"
    "                                                    xtab_mass_housed_nov(time_period)+distribution_mass_used\n",
    "                                                xtab_mass_housed_nov(time_period)=&\n"
    "                                                    xtab_mass_housed_nov(time_period)+distribution_mass_used\n"
    "                                                xtab_treat_housed_nov(time_period)=xtab_treat_housed_nov(time_period)+&\n"
    "                                                    distribution_mass_used*" + T + "\n"
    "                                                if (smi_of(unemployment_index)>=1) xtab_smi_housed_nov(time_period)=&\n"
    "                                                    xtab_smi_housed_nov(time_period)+distribution_mass_used\n")
rep('            write(*,*) "net_govt_revenues=", net_govt_revenues(time_period)\n',
    '            write(*,*) "net_govt_revenues=", net_govt_revenues(time_period)\n'
    '            write(*,*) "MILBY SPLIT voucher mass rec treat smi", xtab_mass_voucher(time_period), &\n'
    '                xtab_rec_voucher(time_period), xtab_treat_voucher(time_period), xtab_smi_voucher(time_period), &\n'
    '                " housed_nov mass rec treat smi", xtab_mass_housed_nov(time_period), xtab_rec_housed_nov(time_period), &\n'
    '                xtab_treat_housed_nov(time_period), xtab_smi_housed_nov(time_period)\n')
if mode == 'treat':
    rep("            if (unemployment_index>threshold_addiction_index) fails_1=1\n            if (drug_share_1>0) fails_1=1\n",
        "            ! TREATMENT MEETS THE CONDITION IN THIS VARIANT (patch_treat.py): the disorder fails only without treatment\n"
        "            if ((unemployment_index>threshold_addiction_index) .AND. (meets_condition_1==0)) fails_1=1\n"
        "            if (drug_share_1>0) fails_1=1\n")
open(out, 'w').write(s)
print(f'{mode}: patched {src} -> {out}')
