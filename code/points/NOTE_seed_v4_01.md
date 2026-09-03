# batch_s2_01: the model moved three times under this batch

## The chain

The batch was launched pinned to semantic hash `fdc6078859`. The source moved
three times while the three lines ran, and every move touched the borrowing
path this batch exists to measure. Nothing here is a parameter finding yet; it
is a provenance record and one reproduced engine failure.

| when | semantic | commit | what it did to this batch |
|---|---|---|---|
| lines 1, 2 ran | `fdc6078859` | — | borrowing inert; limit and rate meant nothing |
| line 3 ran | `99752a3cab` | `307aa35` | borrowing live, but mass diverges to 2.06e33 |
| now | `17529c7177` | `358057d`, `0f581bb` | out-of-bounds root-caused and fixed |

First-pass points, with the build hash each one records on its `MODEL` line:

| line | limit | rate | beta_imp | point | MODEL | verdict |
|---|---|---|---|---|---|---|
| 1 | 1.00 | 0.055 | 0.55 | `point_30f09ca36e` | `1b0babfbed` | invalid: feature inert |
| 2 | 0.30 | 0.20  | 0.55 | `point_deef8f1e37` | `1b0babfbed` | invalid: feature inert |
| 3 | 0.30 | 0.055 | 0.50 | `point_65c5d119a5` | `e55e1cc855` | invalid: mass diverged |

All three are being re-run against `17529c7177`. The re-runs land as new point
hashes and do not overwrite these.

## Why lines 1 and 2 measured nothing

`307aa35` found that `renter_to_renter_problem` pinned its search floor `a_lo_1`
at the index of zero, so no renter could ever choose a negative position. Under
`fdc6078859` the borrowing limit and rate multiply a choice no household can
make, which is why arms at different limits agree with each other. The commit
says so itself: it invalidates "every borrowing arm measured so far -- the
OFF/ON twin above, and the limit and rate ladders". This batch is a limit and
rate ladder.

## The divergence on line 3, reproduced

With borrowing live but before `0f581bb`, line 3 failed two invariants and the
population mass blew up. Another worker measured the identical vector
independently and got the same numbers:

```
                                              theirs            mine
pooled mass                              2.0588727e+33    2.0587580e+33
income histogram holds the distribution     1.4949252        1.4949061
wealth histogram holds the distribution     1.4949252        1.4949061
```

Deterministic to four significant figures, so this is not solver noise. Two
further tells in the same output: the per-age `mass=` column overflowed its
format field entirely, and the patient/impatient mass ratio read 507. The
signature is garbage read back from memory, and `0f581bb` names the cause --
the renter arrays had no negative indices to write into, so opening the choice
wrote past their bounds.

Note that `wealth histogram holds the whole of net worth` still PASSED at
1.0000 while the two distribution invariants failed at 1.4949. The invariant
that reads net worth was looking at a different, still-consistent object; only
the ones that walk the histogram saw the corruption. An engine failure this
large was visible in exactly two of sixteen invariant lines.

## An independent cross-check that came free

Line 2's point hash collided with a point another worker had already pushed.
Two independent solves of the identical vector on the identical model:

```
                                   theirs        mine
tau_l    average labour income tax  0.23433151   0.23404792
omega_l  labour supply / hours      0.37847299   0.37848363
beta     wealth over output         2.67476621   2.67687514
h_2      above half of spending     0.10663241   0.10648282
h_3      share in largest unit      0.47970083   0.47966030
```

That is the solver's noise floor on these moments: about 1e-4 on shares, about
2e-3 on the wealth-output ratio. **An arm effect smaller than that is not
resolvable by a single solve**, which is worth knowing before reading any
borrowing ladder: the first-pass OFF/ON twin in `307aa35` moved w_bot by
1.2e-4, inside this floor.

## Still open

`owner_renter_problem` carries the same floor bug at line 20552.
`include_homeownership` is 0 so nothing reaches it now, but it bars borrowing
for owners and must be fixed before homeownership is switched on. Flagged in
`307aa35`; repeated here because this batch is where it would first bite.
