"""Cross-tabulate a solved distribution by SMI and by SUD.

The moment print inside the Fortran reports only the RATIO, and a ratio does
not say whether a target is reachable: the ceiling on SUD given SMI over SUD
given no SMI is one over the non-SMI SUD rate, so the levels are what tell you
how far b_smi has to travel.  This reads calibration_distribution1.dat and
prints the four masses the bracket uses, plus that ceiling.

The file is one F30.28 per line, 31 bytes each, written in Fortran's column
major order over

    vector_real(age, financial, unemployment, employment, housing, voucher)

so in C order the shape is the reverse of that.  Only the unemployment index
carries SMI and SUD:

    smi_of(i) = mod((i-1)/3, 2)        SUD is i > 12

Usage:  python3 smi_sud_xtab.py <path to calibration_distribution1.dat>
"""
import os
import sys
import numpy as np

N_AGE, N_FIN, N_UEM, N_HOUSE, N_VOUCHER = 61, 25, 18, 4, 3
BYTES_PER_LINE = 31


def main(path):
    size = os.path.getsize(path)
    if size % BYTES_PER_LINE:
        sys.exit("%s is %d bytes, not a whole number of %d byte lines"
                 % (path, size, BYTES_PER_LINE))
    n_lines = size // BYTES_PER_LINE
    per_employment = N_AGE * N_FIN * N_UEM * N_HOUSE * N_VOUCHER
    if n_lines % per_employment:
        sys.exit("%d lines is not a whole number of employment slices (%d)"
                 % (n_lines, per_employment))
    n_emp = n_lines // per_employment

    with open(path, "rb") as handle:
        raw = np.frombuffer(handle.read(), dtype="S%d" % BYTES_PER_LINE)
    mass = raw.astype(np.float64)
    mass = mass.reshape(N_VOUCHER, N_HOUSE, n_emp, N_UEM, N_FIN, N_AGE)
    by_uem = mass.sum(axis=(0, 1, 2, 4, 5))

    smi = np.array([((i - 1) // 3) % 2 for i in range(1, N_UEM + 1)])
    sud = np.array([i > 12 for i in range(1, N_UEM + 1)])

    mass_pop = by_uem.sum()
    mass_smi = by_uem[smi == 1].sum()
    sud_pop = by_uem[sud].sum()
    sud_smi = by_uem[sud & (smi == 1)].sum()
    mass_non = mass_pop - mass_smi
    sud_non = sud_pop - sud_smi

    print("employment grid size inferred  ", n_emp,
          "(13 is the one class model, 26 the two class)")
    print()
    print("mass, population               ", "%.10f" % mass_pop)
    print("mass, SMI                      ", "%.10f" % mass_smi,
          "  share %.4f" % (mass_smi / mass_pop))
    print("SUD mass, population           ", "%.10f" % sud_pop,
          "  rate  %.4f" % (sud_pop / mass_pop))
    print("SUD mass, SMI                  ", "%.10f" % sud_smi)
    print()
    print("SUD rate given SMI             ", "%.4f" % (sud_smi / mass_smi))
    print("SUD rate given no SMI          ", "%.4f" % (sud_non / mass_non))
    print("ratio r_smi                    ", "%.4f"
          % ((sud_smi / mass_smi) / (sud_non / mass_non)),
          "   target 7.30")
    print("CEILING on r_smi               ", "%.4f" % (mass_non / sud_non),
          "   (SMI at a SUD rate of one)")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
