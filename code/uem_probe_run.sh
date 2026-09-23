#!/bin/bash
# THE AUTHOR'S PROPOSAL, 23 September: "with 0.0625 they will still be homeless
# if we made unemployment with SMI more persistent". The model splits that into
# two knobs on purpose (2181): kappa_uem multiplies SEPARATION and sets the SMI
# unemployment RATE, kappa_find_smi divides JOB FINDING and sets the spell
# DURATION. Persistence is already live -- kappa_find_smi is 10.79, calibrated
# on the SMI share of the homeless. The RATE is not: kappa_uem sits at 1.0554,
# where one is no penalty, with its adjuster zero in the declaration, and the
# source's own note says it "runs in the tens" and quotes 23.5.
#
# So this is kappa_uem = 23.5 with the author's zeta_DI = 0.0625 in place. The
# binary is u_probe's, which prints participation by SMI as well as r_smi.
#
# REFERENCE, STATED BEFORE THE RUN, u_probe block 1 at kappa_uem = 1.0554 and
# zeta_DI = 0:
#     employment given SMI      0.80731   target 0.30000
#     fraction homeless         0.0084412
#     SMI share of the homeless 0.32104   target 0.25
#     r_smi                     4.01404   target 7.30
#     share buying  SMI 0.99752   non-SMI 0.12759
#     SUD | SMI 0.22753   SUD | non-SMI 0.05668
cd "$(dirname "$0")/uem_probe" || exit 1
if [ ! -f PARAM_HANDOVER.txt ]; then cp PARAM_HANDOVER.relaunch.txt PARAM_HANDOVER.txt || exit 1; fi
export OMP_NUM_THREADS=2
exec ./hftf
