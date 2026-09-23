# b_smi against the SUD comorbidity ratio

The economy is the ONE CLASS configuration the author asked for on 22 September:
`child_penalty_classes = 1`, `weight_on_child = 0`, `omega_c` pinned, and SMI
exogenous -- `iota_smi = 1` and `mu_m = 1`, so SMI carries neither a higher SUD
onset risk nor a lower recovery rate. Every remaining SMI-to-SUD link is
endogenous, through employment and income, plus the Stone-Geary shifter
`b_smi = addiction_scalar_1 * b_smi_multiple` that this sweep moves.

Target: `sud_smi_ratio_data = 7.30`, the SUD rate given SMI over the SUD rate
given no SMI, computed from the repo's own NSDUH 2024 file in
`data/SMI_SUD_TARGET.md`.

## Measured

| `b_smi_multiple` | `b_smi`    | r_smi | source |
|------------------|------------|-------|--------|
| 1.00             | 0.00491918 | 1.779 | cold solve |
| 0.50             | 0.00245959 | 2.657 | cold solve |
| 0.20             | 0.00098384 | 3.259 | `sw_02`, block 1 |

`sw_02`'s ratio is confirmed twice over: the Fortran's own `MOMENT r_smi`
printed 3.2588654628626594 and `code/smi_sud_xtab.py`, decoding
`calibration_distribution1.dat` independently, printed 3.2589.

## Levels at `b_smi_multiple = 0.20`

| quantity | value |
|----------|-------|
| SMI share of the population | 0.0462 |
| SUD rate, population | 0.0613 |
| SUD rate given SMI | 0.1809 |
| SUD rate given no SMI | 0.0555 |
| ceiling on r_smi, at an SMI SUD rate of one | 18.0 |

## What the three points say

The elasticity is collapsing. Halving the multiple from 1.00 to 0.50 bought
49 per cent on the ratio; cutting it from 0.50 to 0.20 bought 23 per cent. In
logs the slope falls from -0.579 to -0.223 over those two intervals, and a
straight extrapolation of the SECOND slope puts the root near
`b_smi_multiple = 0.005`, roughly two hundred times below `b`. Because the
slope is still falling, that is a lower bound on the distance, not an estimate.

7.30 is not blocked by a ceiling -- the ceiling is 18.0 and it RISES as the
drug price clears -- but reaching it needs the SUD rate given SMI at about
0.40 against 0.25 in the data, because the model's non-SMI SUD rate, 0.0555,
sits above the data's 0.034. The ratio and the level cannot both be matched
while the non-SMI base rate is above the data's; the author chose the ratio.

## Live

`sw_001` runs the bracket ITSELF: `b_smi_multiple` starts at 0.01 with
`b_smi_multiple_adjuster = 0.01`, so the loop walks it toward 7.30 at the
5 per cent per block the step cap allows, inside one process, with the value
function warm between blocks.
