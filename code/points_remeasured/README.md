# Re-measurements, kept beside the archive rather than inside it

`points/` is the search's archive and a file in it is named for the md5 of its
vector, so a vector has exactly one slot. A point re-measured under different
conditions is a different measurement of the same vector and cannot share that
slot without destroying the first, which is why it goes here instead.

Each file's name says what was different. `points/` keeps what the search
actually ran on; `score_points.py` reads only `points/` and does not see these.

| file | what it is |
|---|---|
| `point_ad09bce9b1.cold_fixed_harness.txt` | the leader, re-measured 27 August with the handover fix, from a COLD start: no `calibration_state.dat` and no warm-start distribution, so the run is a function of its 24 parameters and the Fortran declarations alone. Loss 0.304 against the archived 0.266, and the archived file's rank 1 becomes rank 41. All 23 handover lines present in both, so this is not the handover bug. |
