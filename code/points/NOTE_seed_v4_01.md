# batch_s2_01: the model changed under this batch, and it changed the thing the batch measures

## What happened

The batch was launched pinned to semantic hash `fdc6078859`. Lines 1 and 2 ran
against it. Between line 2 and line 3, a pull brought in `307aa35`, "unsecured
borrowing was inert: the state opened, the CHOICE never did", which moves the
semantic hash to `99752a3cab`. Line 3 therefore ran against a different model
from lines 1 and 2.

Provenance is recorded in each point file's `MODEL` line, so nothing is
ambiguous:

| batch line | limit | rate | beta_imp | point | MODEL (build) | semantic |
|---|---|---|---|---|---|---|
| 1 | 1.00 | 0.055 | 0.55 | `point_30f09ca36e` | `1b0babfbed` | `fdc6078859` |
| 2 | 0.30 | 0.20  | 0.55 | `point_deef8f1e37` | `1b0babfbed` | `fdc6078859` |
| 3 | 0.30 | 0.055 | 0.50 | `point_65c5d119a5` | `e55e1cc855` | `99752a3cab` |

## Why this is not just a bookkeeping annoyance

The three lines of this batch differ from each other only in
`unsecured_borrowing_limit`, `unsecured_borrowing_rate`, and (line 3)
`discount_factor_impatient`. This batch IS a borrowing limit-and-rate ladder.

`307aa35` says in its own commit message:

> WHAT THIS INVALIDATES: every borrowing arm measured so far -- the OFF/ON twin
> above, and the limit and rate ladders. They were all measuring an economy in
> which the feature did nothing, which is why they agree with each other.

`renter_to_renter_problem` pinned its search floor `a_lo_1` at the index of
zero, so no renter could ever choose a negative position. Under
`fdc6078859` the borrowing limit and the borrowing rate multiply a choice no
household can make. **Lines 1 and 2 are readings of a no-borrowing economy at
their respective impatience levels, and the limit and rate coordinates on them
mean nothing.**

So lines 1 and 2 as first run do not answer the question the batch asks. They
are being re-run against `99752a3cab`; those re-runs land as separate point
hashes and do not overwrite the originals.

## An independent cross-check that came free

Line 2's point hash `deef8f1e37` collided with a point another worker had
already measured and pushed. Two independent solves of the identical vector on
the identical model agree to roughly three decimals:

```
                                   theirs        mine
tau_l    average labour income tax  0.23433151   0.23404792
omega_l  labour supply / hours      0.37847299   0.37848363
beta     wealth over output         2.67476621   2.67687514
h_2      above half of spending     0.10663241   0.10648282
h_3      share in largest unit      0.47970083   0.47966030
```

That is the solver's own noise floor on these moments: about 1e-4 on shares and
about 2e-3 on the wealth-output ratio. Any arm effect smaller than that is not
resolvable by a single solve. The duplicate commit was dropped in rebase; the
point on the branch is theirs.

## Not done here

`owner_renter_problem` carries the same unfixed floor at line 20552.
`include_homeownership` is 0 so nothing reaches it, but it bars borrowing for
owners and must be fixed before homeownership is switched on. Flagged in
`307aa35` too; repeated here because this batch is where it would first bite.
