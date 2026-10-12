# omega_c = 0 CONTROL — converged

Run: `sh code/remote_scan_point.sh 0`, 2026-09-23 21:09 → 2026-09-24 00:07 UTC (~2h58m).
Clean exit 0, `run.err` empty (0 bytes), no backtrace, no `Error termination`, no OOM.
Boot time 2026-09-23 21:02:31 unchanged at every poll — no container rebuild.

This completes the control note in `results/omega_c_scan/SCAN_READINGS.md`, which had the
frozen vector still walking down and reaching 0.0914 at block 8. That reading is confirmed
exactly (block 8 here is 0.091459); the loop then converged four blocks later.

## Integrity checks — all pass

| check | value |
|---|---|
| HANDOVER lines in run.log | **97** (not 3) |
| `addiction_onset_base` | `0.0` -> `3.4509299932932086E-002` |
| handover file lines | 97 |
| `weight_on_child` | 0 |
| `omega_c_is_pinned` / `freeze_all_but_omega_c` | 1 / 1 |
| `"budget does not clear"` occurrences | **0** |
| OMP_NUM_THREADS | 2 (166% CPU, 4.9 GB RSS — the healthy signature) |
| moment blocks | 12 |
| final BLOCK MOVE | **3.3922946656584171E-004** < rule 1.0E-003 → **converged on the rule** |

`code/paper/calibration_report.py` agrees independently: "12 moment blocks; this is loop 12,
and it is within one per cent of loop 11", `model_fraction_addicted 0.0386617`, and every
adjuster reported as "its adjuster is zero, nothing moves it" — the freeze held.

## The number

| moment | converged control | published benchmark | rel. dev. |
|---|---|---|---|
| b (total drug-user share) | **0.090597511** | 0.098916 | **-8.410%** |
| lambda_d (disorder rate)  | **0.038661716** | 0.043579  | **-11.284%** |

The control was asked to reproduce the benchmark to about 1e-4 relative. It does not: these
are ~840x and ~1130x that. The frozen machinery is not the reason — see the integrity table.

## Full trajectory

| block | BLOCK MOVE | b |
|---|---|---|
| 1 | 1.000 | 0.083203 *(restart transient — bequest_residual re-converging)* |
| 2 | 0.2059 | 0.095075 |
| 3 | 0.08474 | 0.095765 |
| **4** | **0.03875** | **0.095095**  <- same convergence state as the published benchmark (0.03607) |
| 5 | 0.01846 | 0.093816 |
| 6 | 0.01274 | 0.092620 |
| 7 | 0.01827 | 0.091633 |
| 8 | 0.005336 | 0.091459  <- the 0.0914 already on the board |
| 9 | 0.003706 | 0.091120 |
| 10 | 0.003746 | 0.090778 |
| 11 | 0.002979 | 0.090611 |
| **12** | **0.000339** | **0.090598**  <- converged |

b falls monotonically from block 3 onward while `beta` settles onto 3.0.

## Why the two disagree

`code/scan_seed/PROVENANCE.txt` banks the published pair together with the block it was read from:

    BLOCK MOVE 3.6066408339053044E-002 against a rule of 1.0000000000000000E-003
      -- b 9.8916056747807166E-002  lambda_d 4.3579290623499613E-002

3.6e-2 against a rule of 1e-3 is 36x above the run's own convergence rule, so the published
vector is a hand-stopped snapshot rather than a converged solve — as
`6d019e45` already recorded. This run passes through that same state at block 4
(move 0.03875, b 0.095095) and then keeps falling to 0.090598.

## Status: the author's decision stands

The author decided at 23:15 that the omega_c = 0 benchmark **stands as published**, making
b = 0.098916 the reference and omega_c = 0.06 the answer. Nothing here reopens that. The scan
is internally consistent: every point is measured the same way against the same reference,
and the reduction being read is a difference between two runs treated identically.

This file records what is true of the model for whenever the benchmark's own convergence is
revisited, and one consequence worth having written down before then:

| omega_c | b | vs published 0.098916 | vs converged control 0.090598 |
|---|---|---|---|
| 0.06  | 0.081242 | -17.87% | -10.33% |
| 0.065 | 0.080735 | -18.38% | -10.89% |
| 0.07  | 0.080472 | -18.65% | -11.18% |
| 0.08  | 0.077688 | -21.46% | -14.25% |

An 18 per cent reduction is b = 0.081111 on the published reference, which the grid straddles
at 0.06. On the converged control it is b = 0.074290, which is **below every point on the
current grid** — the 0.08 point only reaches 0.077688. So the choice of reference does not
merely shift the reductions by a constant; on the converged reference the 18 per cent target
lies beyond omega_c = 0.08 and the grid would have to be extended to bracket it. That is the
thing to re-check first if the benchmark is ever re-published from a converged block.
