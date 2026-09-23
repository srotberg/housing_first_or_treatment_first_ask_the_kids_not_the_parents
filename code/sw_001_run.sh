#!/bin/bash
# One sweep point with the b_smi bracket LIVE: b_smi_multiple starts at 0.01 and
# the loop walks it toward the SUD comorbidity ratio target of 7.30, 5 per cent
# per block, inside one process so the value function stays warm.
cd "$(dirname "$0")/sw_001" || exit 1
export OMP_NUM_THREADS=2
exec ./hftf
