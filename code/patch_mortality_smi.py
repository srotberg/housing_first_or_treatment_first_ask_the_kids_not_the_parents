#!/usr/bin/env python3
"""Generate a source with the SMI mortality double-count fixed.

    patch_mortality_smi.py <master .f90> <output .f90>

WHAT IT FIXES. survival_probability is a precomputed table indexed by
(age, housing, SUD, SMI), built fully multiplicatively on the DEATH
probability:

    d(age, housed,   clean, no SMI) = d0
    d(age, homeless, clean, no SMI) = kappa_h * d0
    d(age, housed,   SUD,   no SMI) = kappa_d * d0
    d(age, homeless, SUD,   no SMI) = kappa_h * kappa_d * d0
    d(age,  ...,      ...,  SMI   ) = kappa_m * d(same cell, no SMI)

The last line makes the drug's MARGINAL contribution to death
kappa_m = 2.5 times larger for an SMI household:

    non-SMI   (kappa_d - 1)*d0
    SMI       kappa_m*(kappa_d - 1)*d0

Nobody chose that. It falls out of applying the SMI multiplier to a number
that already carries the drug's penalty -- and kappa_phi_m is ASSIGNED from
the standardised mortality ratio, which is a TOTAL already containing the
deaths caused by the substance use SMI populations have. So the model uses a
number that drug use helped produce in order to make drug use 2.5x more
dangerous for exactly that group.

THE FIX. kappa_phi_m scales the CLEAN death probability; the drug's increment
is added AT PAR. Six lines, in the table construction, so there is no runtime
cost -- the table is built once.

MEASURED EFFECT ON THE TABLE, 22 September: SMI + homeless + SUD survival at
age 40 goes 0.79504 -> 0.86884, a 36 per cent cut in the death probability.
Clipped cells go from 2 of 472 to 0 of 472 and the smallest survival
probability rises from 0.000 to 0.280 -- the old table had cells where
survival was exactly zero, a corner in which extra drug risk was free.

WHAT IT DOES NOT FIX. Afterwards kappa_phi_m=2.5 is still a TOTAL SMR applied
to NON-substance mortality, so it over-states the non-drug part. Strictly the
SMR wants decomposing into substance and non-substance components. That is
second order; the double count is first order.

THIS INVALIDATES THE CALIBRATION. Survival feeds the value of life, saving and
labour supply. A run with this patch is a DIAGNOSTIC at the existing
parameters, not a calibrated model.
"""
import sys

OLD = """            do i=1,life_span

                do j=1,2

                    do k=0,include_addiction

                        survival_probability(i,j,k,1)=&
                            survival_with_smi(survival_probability(i,j,k,0),1)

                    end do

                end do

            end do
"""

NEW = """            do i=1,life_span

                do j=1,2

                    ! SMI scales the CLEAN death probability and the drug's
                    ! increment is added AT PAR, so the drug costs an SMI
                    ! household the same extra risk it costs anyone else.
                    ! kappa_phi_m is assigned from the standardised mortality
                    ! ratio, a TOTAL that already contains substance-related
                    ! deaths; scaling the whole probability by it charged the
                    ! drug's own marginal risk 2.5 times over.
                    survival_probability(i,j,0,1)=&
                        survival_with_smi(survival_probability(i,j,0,0),1)

                    if (include_addiction==1) then

                        survival_probability(i,j,1,1)=1.d0-min(1.d0,&
                            kappa_phi_m*(1.d0-survival_probability(i,j,0,0))+&
                            ((1.d0-survival_probability(i,j,1,0))-&
                            (1.d0-survival_probability(i,j,0,0))))

                    end if

                end do

            end do
"""

def main():
    src_path, out_path = sys.argv[1], sys.argv[2]
    s = open(src_path).read()
    if s.count(OLD) != 1:
        sys.exit("REFUSING: anchor found %d times, expected 1. The survival "
                 "table construction has moved; look before patching." % s.count(OLD))
    open(out_path, "w").write(s.replace(OLD, NEW))
    print("wrote %s" % out_path)

if __name__ == "__main__":
    main()
