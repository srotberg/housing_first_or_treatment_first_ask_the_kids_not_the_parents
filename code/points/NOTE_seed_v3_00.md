# seed v3, batch_s2_00.txt: all three points are on fdc6078859, where borrowing was inert

The three lines of `code/batch_s2_00.txt` were run and pushed as briefed. They are
real solves and all invariants pass. **They are not evidence about unsecured
borrowing**, and this note exists so nobody reads them as if they were.

The batch varies exactly one thing across its three lines:

| line | point | include_unsecured_borrowing | unsecured_borrowing_limit | MODEL |
|------|-------|------|------|------|
| 1 | `point_4659380b40` | 1 | 0.30 | 1b0babfbed |
| 2 | `point_f9c16d5308` | 0 | 0.30 | 1b0babfbed |
| 3 | `point_f4a40be627` | 1 | 0.60 | 1b0babfbed |

`1b0babfbed` maps to economy `fdc6078859`. Commit `307aa35` ("unsecured borrowing
was inert: the state opened, the CHOICE never did") landed at 03:46, after all
three had solved, and moved the current economy to `99752a3cab`. Under
`fdc6078859` the 25 borrowing loops were STATE loops; `a'` was chosen in
`renter_to_renter_problem`, whose search floor was pinned at the index of zero, so
no renter could ever select a negative position at any limit.

That is why the three agree to four decimals -- the comparison was between an
economy with borrowing and an economy with borrowing nobody could use:

    w_bot (net worth share, bottom half)   target 0.025000
      line 1  ON  @ 0.30    0.030004
      line 2  OFF @ 0.30    0.029486
      line 3  ON  @ 0.60    0.029610

    homelessness rate
      line 1  ON  @ 0.30    0.0843018
      line 2  OFF @ 0.30    0.0841764
      line 3  ON  @ 0.60    0.0843020

Line 1 at limit 0.30 and line 3 at limit 0.60 differ in the eighth decimal of the
homelessness rate. Doubling the debt limit did nothing because the limit was never
reachable.

## No redo is needed from this batch

`code/batch_borrow_live.txt` (commit `3365b3c`) already re-runs this comparison on
`99752a3cab`: OFF@0.30, ON@0.30, ON@1.00. Its first two arms are lines 2 and 1 of
this batch exactly. The only arm here that it does not reproduce is line 3's
intermediate limit of 0.60; the 0.30/1.00 bracket was a deliberate choice by the
coordinator and adding a fourth arm was not this worker's call.

## Bookkeeping: line 1 was quarantined by path, not by its MODEL line

`b5bace8` moved `point_4659380b40` to `points_superseded/` as
`point_4659380b40.9caeb7a139.txt`, but the file's own `MODEL` line reads
`1b0babfbed`, which was the current economy at that moment. This is the same
false positive that `14386d3` corrected for `point_6aadbe9c3d` ("quarantined by
path, but its MODEL line is the current economy"). It is moot now -- `307aa35`
made `1b0babfbed` stale on its own -- so the file has been left where the
quarantine put it, and the filename stamp should not be trusted as the economy it
was solved on.

No build failed. `code/housing_first_or_treatment_first_SR_v1.f90` was not edited.
