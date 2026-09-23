"""Print drug participation by SMI in the steady-state moment block.

The four masses r_smi is built from already carry it. xtab_exp_mass_smi is the
mass of SMI households with addiction_consumption > 0 and no disorder,
incremented at 19305 on every block, and xtab_sud_mass_smi is the SMI disorder
stock. Their sum over xtab_mass_smi is the model's TOTAL DRUG USERS by SMI --
the object whose target is 0.10502, which is 1.180 times the data's 0.0890 for
any drug use disorder, the author's eighteen per cent uplift. Its data ratio is
4.51.

None of it is printed here. The masses go to the log only on the transition
path, at 54973, so the share of each group that uses has had to be INFERRED
from stocks twice in this session and both inferences were wrong -- 0.59 from
r_smi = u_SMI/u_non, 0.34 from the never-disordered stock and the onset hazard,
against a measured 0.9975.

This adds three WRITE statements next to MOMENT r_smi. It changes no
equilibrium: nothing downstream reads them and no value is assigned.

Usage:  python3 code/patch_participation_print.py [--check]
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'housing_first_or_treatment_first_SR_v1.f90')

ANCHOR = '''            end if
            write(*,*) "MOMENT pi_V      eligibles with a voucher    model=",&'''

ADDITION = '''            end if

            ! PARTICIPATION, READ RATHER THAN BACKED OUT. u_any is the model's
            ! TOTAL DRUG USERS by SMI -- experimenters plus the disorder stock
            ! over the group's mass -- which is the object targeted at 0.10502,
            ! or 1.180 times the data's 0.0890 for any drug use disorder. Its
            ! data ratio is 4.51. u_exp is the experimenter half alone.
            !
            ! The masses are already accumulated at 19286 to 19308 every block
            ! and were printed only on the transition path at 54973, which is
            ! why this share was inferred from stocks twice and wrongly both
            ! times. Nothing downstream reads these lines.
            write(*,*) "MOMENT u_any     total drug users: SMI=",&
                (xtab_exp_mass_smi(1)+xtab_sud_mass_smi(1))/&
                max(xtab_mass_smi(1),10.d0**(-12)),&
                " non-SMI=",&
                ((xtab_exp_mass_pop(1)-xtab_exp_mass_smi(1))+&
                (xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1)))/&
                max(xtab_mass_pop(1)-xtab_mass_smi(1),10.d0**(-12))
            write(*,*) "MOMENT u_exp     experimenters only: SMI=",&
                xtab_exp_mass_smi(1)/max(xtab_mass_smi(1),10.d0**(-12)),&
                " non-SMI=",&
                (xtab_exp_mass_pop(1)-xtab_exp_mass_smi(1))/&
                max(xtab_mass_pop(1)-xtab_mass_smi(1),10.d0**(-12))
            write(*,*) "MOMENT u_raw     xtab exp_smi exp_pop sud_smi sud_pop mass_smi mass_pop=",&
                xtab_exp_mass_smi(1), xtab_exp_mass_pop(1), xtab_sud_mass_smi(1),&
                xtab_sud_mass_pop(1), xtab_mass_smi(1), xtab_mass_pop(1)

            write(*,*) "MOMENT pi_V      eligibles with a voucher    model=",&'''


def main(check_only):
    src = open(SRC).read()

    if 'MOMENT u_any' in src:
        sys.exit('REFUSING: the participation print is already present.')
    n = src.count(ANCHOR)
    if n != 1:
        sys.exit('REFUSING: the anchor appears %d times, expected exactly 1.' % n)

    print('anchor found exactly once, immediately after the MOMENT r_smi block.')
    if check_only:
        print('--check: nothing written.')
        return

    open(SRC, 'w').write(src.replace(ANCHOR, ADDITION))
    print('written: three write statements added, no value assigned.')


if __name__ == '__main__':
    main('--check' in sys.argv)
