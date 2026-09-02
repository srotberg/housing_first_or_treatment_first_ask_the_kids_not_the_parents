# Borrowing ON at the 0.75-impatient vector: the solve did not finish

Point tag `b083f765a0` (`code/batch_bn_on075.txt`), the borrowing-ON twin of the
borrowing-OFF control `de322e4659`.

## Outcome: NO MEASUREMENT

The solve ran **5 h 30 m wall-clock** and was then killed, `exit 137` (SIGKILL),
when the session container was restarted out from under it. It had not written
`code/points/point_b083f765a0.txt`, and no such file exists.

The runner only writes the point file after `hftf` exits normally
(`run_one_point.sh:612`), so a mid-solve kill leaves nothing behind. The log ends
mid-word inside the benchmark aggregate block (`govt_spending_on_home`), i.e. it
died while printing period-1 aggregates, not at a crash or an error.

**No scored moment was produced.** Every item the brief asked to be reported --
`w_bot`, the three bottom-percentile wealth shares, `beta`, and the remaining
scored moments -- is therefore unavailable. Nothing below should be read as a
partial answer to those questions; the only quantity resembling a moment that
reached the log is a pre-solve calibration diagnostic, `bottom half's share of
productivity = 0.16905 against target 0.172`, which is not a scored moment and
not the wealth tail.

The two DIAG lines were reached and are reported below, because they are printed
during setup rather than at the end.

## The DIAG lines

```
DIAG borrowing floor, model units                = -0.95587205886840820
DIAG patient type barred from the negative grid  =           1
```

The second reads `1`, as expected: the patient type is barred from the negative
grid. The handover line confirms the flag arrived set:
`HANDOVER restrict_borrowing_to_impatient: 1 -> 1.0`.

## Why it took 5.5 h instead of the expected ~20 min

Switching borrowing on opens a region of the state space in which the household
budget cannot be made to clear, and the solver reports every instance.

| log | budget-clear failures |
|---|---|
| `worker_b083f765a0` (borrowing ON) | **525,418** |
| `worker_fd6f4b5257` (OFF) | 0 |
| `worker_f74796c1ee` (OFF) | 0 |
| `worker_fb1958e8b3` (OFF) | 0 |

Zero in every borrowing-off log checked. The failures are not scattered: the
shortfall takes essentially two values, both of them structural.

```
 158474  budget does not clear by -0.89828943890932111
 128066  budget does not clear by -0.89828943890932100
 106468  budget does not clear by -0.89828943890932123
  82097  budget does not clear by -0.95587205886840820
  15340  budget does not clear by -0.95587205886840809
  15113  budget does not clear by -0.95587205886840831
```

The clusters at `-0.955872058868408...` are the borrowing floor itself, to every
printed digit. The clusters at `-0.898289438909321...` differ from the floor by
0.0575827, which is the floor times the borrowing rate 0.055 plus rounding --
i.e. the floor carried one period forward at interest. So the states that fail
are the ones sitting exactly on the borrowing constraint, and the shortfall is
the whole of the borrowed balance.

Each failure prints a diagnostic block (`housing_status_index = -1`,
`years_left_on_mortgage_index`, `amortization_used`, the two `min(financial_grid
...)` lines -- 444,324 of each). The log reached **230 MB across 4.73 M lines**,
against 200-330 KB for a normal point: about a thousandfold. The failures run to
the very end (last one at line 4,729,848 of 4,730,095), so this is not a
transient of the first sweep -- it never settles.

`housing_status_index = -1` in that block is worth an eye: -1 is not a housing
status, and it recurs 444,324 times.

## What this does and does not tell us about the tail question

The question the run was meant to answer -- whether borrowing ON breaks the
degeneracy of the borrowing-OFF control, where the whole bottom decile sits on
one grid point and the three bottom shares come out exact 1x/5x/10x multiples
(+1.213e-04 / +6.064e-04 / +1.213e-03, all positive against data
-2.250e-03 / -4.220e-03 / -4.460e-03) -- is **unanswered**.

What the log does establish is narrower, and it is a caution rather than an
answer: with borrowing on, half a million states on the negative grid cannot
clear their budget. Whatever wealth distribution this vector would eventually
report would be built on top of those states. That is worth resolving before the
point is re-measured, because a tail that does go negative would be reading off
exactly the region that is failing.

## Reproducing

The vector is unchanged from `code/batch_bn_on075.txt` and was not edited. The
binary was built fresh in-container from source md5
`9575c59af0ff8632a4169d80352f134d` (`gfortran` was absent and was installed
first, which is included in the 5 h 30 m).

Evidence kept in `code/logs_bn_on075/` (the raw 230 MB log is gitignored and did
not survive the container restart):

- `worker_b083f765a0.extract.txt` -- first 300 lines, every distinct DIAG line,
  the budget-failure tally, and the last 300 lines up to the kill
- `build_b083f765a0.txt` -- the build log
