# omega_c = 0.686 (Nishiyama 2000) sensitivity

The author, 9 October: *"a sensitivity test where omega_c = [Nishiyama's value] in the benchmark ... and show
whether the long run welfare effects are similar"*, and *"You should take exactly the number nishiyama finds."*
omega_c = 0.686 (Nishiyama 2000, CBO Technical Paper 2000-7: 0.509 per child household x 1.35 child
households; see OMEGA_LITERATURE.md). Everything else is the benchmark of record
(results/reference/hf_2c_omega_0.085: omega_c 0.085, b 0.0054222, kappa_uem 1.0, drug users 8.956 per cent),
with b re-matched to drug use. Orchestrator: session_01NzKWR6JcFw2XXovtVWLrDY.

## Stage 1: one class (CLASSES 1), b scan at omega_c 0.686

Control: one class at omega_c 0.085, b 0.0054222 (session_01QdHZe9tWNJ95ZPEwNtywRD,
results/omega07_1c/): converged in 10 blocks (last move 6.6e-4), drug users **8.593 per cent**.
Workers launched 17:21 UTC, tag omega-nishiyama, results/omega_nishiyama_1c/. Users are the last block's
"MOMENT b total drug users", read 19:22 UTC.

| b multiple | b | session | blocks | last move | drug users (per cent) |
|---|---|---|---|---|---|
| 1.0 | 0.0054222 | session_01NdBwfzqNp91qgcuSYkEzsV | 12, converged | 1.4e-4 | 2.945 |
| 0.9 | 0.0048800 | session_0188Zxo3q88QEPezmM63zdpv | 9, solving | 1.3e-2 | 5.519 (blocks 5-9: 5.50, 5.59, 5.55, 5.46, 5.52) |
| 0.8 | 0.0043378 | session_01HpATQ5eSn67kkzjZ1A2yxB | 11, converged | 2.9e-4 | 10.409 |
| 0.7 | 0.0037955 | session_012MgAo6Kkac2cQntP5ZGy1J | 6, solving | 9.3e-3 | 16.03 |
| 0.6 | 0.0032533 | session_01AFm1381E83bfSiXYGky4rk | 10, converged | 6.5e-4 | 21.026 |
| 0.5 | 0.0027111 | session_01CrA5ZTX54jbmB2nCz3DFyC | 8, solving | 2.9e-3 | 26.63 |

**b1* = 0.004531742** (0.8358 x the benchmark's b): log-b interpolation between 0.8x (10.409) and 0.9x
(5.519) to the control's 8.593. The 0.9x point had not met the 1e-3 rule (its use has hovered between 5.45
and 5.59 for five blocks, a large relative move on a small level); at 5.45 b1* would be 0.004528985, 0.06 per
cent lower, well inside the stage 2 bracket of +-2 per cent, so stage 2 was launched at 19:23 without waiting.
At omega_c 0.686 use is far more sensitive to b than at 0.085: a 10 per cent cut in b moves the one-class
users by about 5 points near the target. To match the benchmark's drug use, b must fall by about 16 per cent.
release_all committed for omega_nishiyama_1c and omega07_1c at 19:25 (no benchmark files needed).

## Stage 2: two class, matched to 8.956 per cent

Launched 19:23 UTC (CLASSES 2, results/omega_nishiyama_2c/), target the benchmark's own 8.956 per cent:

| b | session | blocks | drug users (per cent) |
|---|---|---|---|
| 0.004441108 (0.98 b1*) | session_01T2a3SiG27xEZP7A99mdHjH | running | |
| 0.004531742 (b1*) | session_012BNTu2UEcm6LYfWB3dc2Ji | running | |
| 0.004622377 (1.02 b1*) | session_01J7fgutKX5TVZPsNqETqHjE | running | |

b2* = pending.

## Stage 3: long-run welfare, Housing First and Treatment First

Pending.
