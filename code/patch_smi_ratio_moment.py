#!/usr/bin/env python3
"""Add the SMI comorbidity ratio as a measured moment with its data target.

    patch_smi_ratio_moment.py <master .f90> <output .f90>

THE MEASUREMENT IS ALREADY IN THE MODEL. govt_revenues_calc accumulates
xtab_mass_smi, xtab_mass_pop, xtab_sud_mass_smi and xtab_sud_mass_pop, and that
routine runs on the benchmark path as well as the transition. They were only
ever PRINTED from the transition driver, so this adds the benchmark print and
the target beside it.

THE TARGET IS 7.30 AND IS NOT SCALED BY 1.18. NSDUH 2024, adults 26 and over,
weighted, SUD = svyrdudany in (2,3), SMI = SMIPY: 0.20426 against 0.02797. The
universe check passes exactly, reproducing 0.0890 and 0.0368, the two numbers
the level targets are built from. See data/SMI_SUD_TARGET.md.

It is a RATIO, and the file's own rule is that ratio targets are not scaled:
"THE RATIO TARGETS ARE NOT SCALED and should not be: tau_u and the SUD share of
the homeless are both shares OF users, so they are approximately invariant when
the level moves." A ratio of two rates is invariant to a common 18 per cent
scaling in exactly the same way.
"""
import sys

TARGET_ANCHOR = "        real(8), parameter :: sud_share_of_homeless=0.217\n"
TARGET_NEW = TARGET_ANCHOR + """
        ! THE SMI COMORBIDITY RATIO, SUD given SMI over SUD given no SMI.
        !
        ! NSDUH 2024, adults 26 and over, weighted by ANALWT2_C, SUD from
        ! svyrdudany in (2,3) and SMI from SMIPY: 0.20426 against 0.02797.
        ! The same file and the same variable the level targets come from, and
        ! the universe check reproduces 0.0890 and 0.0368 exactly.
        !
        ! NOT SCALED BY 1.18, because it is a ratio of two rates and a common
        ! scaling cancels, exactly as for sud_share_of_homeless above.
        !
        ! IT IS THE RATIO AGAINST NON-SMI, NOT AGAINST THE POPULATION. Against
        ! the population it is 5.55, and multiplying a population rate by 7.30
        ! double counts. Against adults with NO mental illness at all it is
        ! 12.77, so 7.30 is the conservative summary: the non-SMI comparison
        ! group contains 38 million adults with mild or moderate mental illness
        ! running at 3.8 and 7.6 times the clean baseline.
        real(8), parameter :: sud_smi_ratio_data=7.30
"""

MOMENT_ANCHOR = """            write(*,*) "MOMENT lambda_m  SMI share of the homeless   model=",&
                model_smi_share_of_homeless(1), " target=", smi_share_of_homeless_data
"""
MOMENT_NEW = MOMENT_ANCHOR + """            ! THE COMORBIDITY RATIO. Built from the four masses govt_revenues_calc
            ! already accumulates, which is why no new accumulation is needed.
            ! Guarded on both denominators: at a corner with no SMI mass or no
            ! non-SMI SUD the ratio is meaningless rather than large, so it
            ! prints as zero and the gaps table shows it against its target
            ! rather than reporting a spurious number.
            if ((xtab_mass_smi(1)>10.d0**(-12)) .AND. &
                ((xtab_mass_pop(1)-xtab_mass_smi(1))>10.d0**(-12)) .AND. &
                ((xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1))>10.d0**(-12))) then

                write(*,*) "MOMENT r_smi     SUD ratio SMI over non-SMI  model=",&
                    (xtab_sud_mass_smi(1)/xtab_mass_smi(1))/&
                    ((xtab_sud_mass_pop(1)-xtab_sud_mass_smi(1))/&
                    (xtab_mass_pop(1)-xtab_mass_smi(1))),&
                    " target=", sud_smi_ratio_data

            else

                write(*,*) "MOMENT r_smi     SUD ratio SMI over non-SMI  model=",&
                    0.d0, " target=", sud_smi_ratio_data

            end if
"""

src = open(sys.argv[1]).read()
for anchor, new in ((TARGET_ANCHOR, TARGET_NEW), (MOMENT_ANCHOR, MOMENT_NEW)):
    n = src.count(anchor)
    if n != 1:
        sys.exit("REFUSED: anchor appears %d times, expected 1:\n%r" % (n, anchor[:70]))
    src = src.replace(anchor, new)
open(sys.argv[2], "w").write(src)
print("added sud_smi_ratio_data=7.30 and the MOMENT r_smi print")
