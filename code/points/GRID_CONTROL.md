# GRID CONTROL: does the 7-point negative grid leave the borrowing-OFF economy alone?

## Verdict

**NOT IDENTICAL.**

The borrowing-OFF economy is *not* bit-for-bit what it was. Every model
value moves except three, and the movement is **larger than the measured
run-to-run reproducibility band of 5.13e-05** in a dozen places, including
two targeted moments. **The 35-point archive is invalidated and resets.**

The worst single difference is **3.824e-03**, on the age-76 row of the
housing-margin age profile (`sud` field: 0.207640 -> 0.206846). The worst
targeted moment is **`w_bot` at 1.023e-04** -- twice the reproducibility
band, and `w_bot` is the moment this whole exercise is about.

## What was compared

| | old | new |
|---|---|---|
| point tag | `35e8286c4e` | `de322e4659` |
| `MODEL` stamp (md5 of the source) | `b8dc1077ad` | `64d52d8b6a` |
| semantic hash | `2f7c317e75` | `197407b07d` |
| parameters handed over | 42 of 42 | 43 of 43 |
| solve time | 14 min on 4 cores | 12 min on 4 cores |
| invariants | all PASS | all PASS |
| labour secant hit its cap | 0 | 0 |

Same vector otherwise, `include_unsecured_borrowing=0` in both. The 43rd
parameter is `financial_grid_expander_negative=2.0`, which the current
`run_one_point.sh` hands over explicitly and the old one left on its
declared default of the same value -- so it is not a change in the vector.

The structural change: `negative_financial_grid_size` 4 -> 8, hence
`financial_grid_size` 28 -> 32, with `positive_financial_grid_size`
unchanged at 24.

## Why this was expected to be inert, and what that argument misses

`initialize_financial_grid` sets

    financial_grid(1) = -include_unsecured_borrowing * unsecured_borrowing_limit
                        * average_labor_income_calibrated

so with borrowing OFF `financial_grid(1)` is exactly 0, and the accordion
interior

    financial_grid(i) = financial_grid(1) * ((n-i)/(n-1))**expander

is 0 times something for every `i`, so all eight negative rungs are exactly
zero -- as all four were before. `set_renter_floor` leaves
`renter_floor_by_age` at `negative_financial_grid_size` when borrowing is
off, so no household can reach any of them. `DIAG asset grid, reachable
points` is **25.000000 in both files**, confirming the reachable set is the
same size.

What the argument misses is that the *array* is four elements longer and
every positive rung has shifted index by four. Every sum, `minloc`, bracket
search and interpolation over `financial_grid` now runs over a different
index range with a different number of leading duplicate zeros. That is
enough to change floating-point association, and the general equilibrium
solve (rent, the labour secant, the distribution iteration) amplifies it.
This is a plausible mechanism, not a verified one -- I did not instrument
the solve to prove it, and the model source was not touched.

## Every targeted moment, old vs new

| MOMENT | what it is | old (35e8286c4e) | new (de322e4659) | rel. diff |
|---|---|---|---|---|
| `sigma_y` | bottom half earnings share | 0.169050021402 | 0.169050021402 | 0.000e+00 |
| `tau_l` | average labour income tax | 0.226320585498 | 0.226320618198 | 1.445e-07 |
| `omega_l` | labour supply / total hours | 0.363505000284 | 0.3635067501 | 4.814e-06 |
| `beta` | wealth over output | 2.45282633409 | 2.45289173275 | 2.666e-05 |
| `h_2` | above half of spending | 0.037082403227 | 0.0370841956244 | 4.833e-05 |
| `h_3` | share in the largest unit | 0.436444894824 | 0.436436623022 | 1.895e-05 |
| `gamma` | housing over expenditure | 0.122699708835 | 0.12270058356 | 7.129e-06 |
| `h_1` | homelessness rate | 0.0451469723591 | 0.0451479533322 | 2.173e-05 |
| `b` | total drug users | 0.408622447309 | 0.408623038323 | 1.446e-06 |
| `lambda_d` | disorder rate | 0.294785417386 | 0.294789418595 | 1.357e-05 |
| `theta` | drug spending share | 0.304600998293 | 0.304605027098 | 1.323e-05 |
| `aleph` | value of life / income | 75.8280078863 | 75.8287739481 | 1.010e-05 |
| `pi_eu` | unemployment rate | 0.134279134627 | 0.134281601361 | 1.837e-05 |
| `kappa_ued` | unemployment given SUD | 0.244468745824 | 0.244478139097 | 3.842e-05 |
| `kappa_uem` | employment given SMI | 0.147680965255 | 0.147674029291 | 4.697e-05 |
| `p_m` | SMI population share | 0.0501667619886 | 0.050169124747 | 4.710e-05 |
| `lambda_m` | SMI share of the homeless | 0.0262580453375 | 0.0262575313154 | 1.958e-05 |
| `pi_V` | eligibles with a voucher | 0.255977544628 | 0.255969334207 | 3.207e-05 |
| `cbar` | food stamps / income | 0.00393490612653 | 0.00393511859997 | 5.399e-05 **>band** |
| `tau_u` | treatment take up | 0 | 0 | 0.000e+00 |
| `mu_H` | recovery housed / homeless | 1.09178837854 | 1.09178681979 | 1.428e-06 |
| `w_bot` | net worth share, bottom half | 0.024269801123 | 0.0242673175631 | 1.023e-04 **>band** |
| `y_u` | income of drug users | 0.839032833276 | 0.839009412055 | 2.791e-05 |


Two targeted moments are exactly unchanged: `sigma_y`, and `tau_u` which is
identically zero because treatment is off. Outside the targeted block the
only exactly-unchanged `UNTARGETED` lines are the two earnings shares and
the three "homeless/SMI/working at treatment admission" lines, which are
also identically zero. `sigma_y` and the earnings shares are functions of
the exogenous productivity process alone, which touches no asset grid.
Everything that passes through the household's savings problem moves.

**Targeted moments above the 5.13e-05 reproducibility band: 2 of 23**
(`w_bot` 1.023e-04, `cbar` 5.399e-05).
21 of 23 differ by more than 1e-9.

## DIAG and UNTARGETED

The twelve largest UNTARGETED differences:

| UNTARGETED | old | new | rel. diff |
|---|---|---|---|
| users aged 45-54, share | 0.221998101152 | 0.22195578691 | 1.906e-04 **>band** |
| homelessness rate, band           3 | 0.00934896004825 | 0.00934984648674 | 9.481e-05 **>band** |
| SUD share of the homeless | 0.169388180852 | 0.169403097063 | 8.805e-05 **>band** |
| users aged 35-44, share | 0.250557687963 | 0.250578588944 | 8.341e-05 **>band** |
| users aged 65 plus, share | 0.125951976645 | 0.125961850099 | 7.838e-05 **>band** |
| users aged 55-64, share | 0.165356084715 | 0.165368222784 | 7.340e-05 **>band** |
| homelessness profile, band           3 | 0.207078339028 | 0.207093473716 | 7.308e-05 **>band** |
| homelessness rate, band           5 | 0.055944455249 | 0.0559481728845 | 6.645e-05 **>band** |
| homelessness profile, band           2 | 0.653908132473 | 0.653866265694 | 6.403e-05 **>band** |
| share of the homeless, band           5 | 0.263192643601 | 0.263209244845 | 6.307e-05 **>band** |
| homelessness profile, band           4 | 0.100404494648 | 0.100399357818 | 5.116e-05 |
| homelessness profile, band           5 | 1.2391629455 | 1.2392183644 | 4.472e-05 |

### Counts, at the 1e-9 relative threshold asked for

| | lines compared | differing > 1e-9 | differing > 5.13e-05 |
|---|---|---|---|
| `UNTARGETED` | 46 | 41 | 10 |
| `DIAG` | 144 | 112 | 34 |
| **combined** | **190** | **153** | **44** |

Counting individual numeric fields rather than lines (many `DIAG` lines
carry five or six numbers), 234 `DIAG` fields differ by more than 1e-9.

**Largest `DIAG`/`UNTARGETED` difference: 3.824e-03**, on

    DIAG age  76  homeless=  0.065790  own=  0.00000  renter wealth=    0.82392
                  renter income=   14.11012  sud=  0.206846  mass=    0.850975

in the `sud` field, old 0.207640 against new 0.206846. The next four
largest are also age-profile rows (age 67 at 1.669e-03, age 78 at
1.090e-03, age 53 at 1.037e-03, age 73 at 4.953e-04); the largest that is
not an age-profile row is `DIAG users band 3 use rate` at 2.908e-04.

## Which regime the differences fall in

The stated run-to-run reproducibility is **5.13e-05 worst**. Sorting the
differences against it:

- **Inside the noise regime.** 21 of 23 targeted moments, 36 of 46
  `UNTARGETED` lines and 110 of 144 `DIAG` lines. On their own these would
  be indistinguishable from re-running the same binary.
- **Outside it.** 2 targeted moments, 10 `UNTARGETED` lines and 34 `DIAG`
  lines, up to 74x the band. `w_bot` at 1.023e-04 is 2.0x the band; the
  worst `DIAG` at 3.824e-03 is 74.5x it.

So this is not a re-run of the same economy with a different random seed --
the model has no simulation noise to begin with, it is a deterministic
solve, and a deterministic solve that reproduces to 5.13e-05 has moved by
3.8e-03. **The differences are real, not measurement.**

They are, however, *small*: no moment changes in its third significant
figure, `w_bot` moves from 0.024270 to 0.024267 against a target of 0.0250,
and every invariant still passes. Nothing here suggests the new grid is
wrong. It says the OFF economy is a slightly different numerical object
than it was, so points measured under the old grid cannot be quoted
alongside points measured under the new one.

## Consequence

The archive resets. The 35 points carrying semantic hash `2f7c317e75` are
not comparable to points carrying `197407b07d`, at any borrowing setting,
including OFF. `point_35e8286c4e.txt` has been superseded by
`point_de322e4659.on_64d52d8b6a.txt` as the round-1 OFF reference.

## Provenance of the comparison

Measured on branch head `b03b86b`, which is what
`git fetch origin claude/two-period-addiction-hazard-d7gb61` resolved to
when this batch started.

- baseline file: `code/points/point_35e8286c4e.txt` at blob
  `73f443d44d58e6ea1d4dd49a548961c5cb4937ad` (the version present at
  `b03b86b`);
- new file: `code/points/point_de322e4659.txt`, solved from source md5
  `64d52d8b6a`, semantic `197407b07d`.

While this batch was running the branch head on the remote advanced to
`3527de0`, and two of those commits matter for reading this report:

- `68c3578 measure: point_35e8286c4e re-solved on the 2.5-target source`
  replaces the baseline file with a different blob
  (`d849957348868dbb35158dccb4c4de09b858ef4b`). **This report compares
  against the pre-`68c3578` blob**, which is the file that was on disk when
  the control was launched. Anyone re-running the comparison against the
  current file will get different numbers, and should say which blob they
  used.
- `de9d7a3 unemployment target 13.9 -> 4.9 per cent` moves the `pi_eu`
  target. Both points compared here were solved on the **13.9 per cent**
  source, and both report `target=0.13899999856948853`. The comparison is
  internally consistent -- old and new were solved against the same target
  -- but the `pi_eu` row should not be read against the 4.9 target.

Neither of those commits is in the history this batch was measured on. They
were not merged in mid-batch, deliberately: rebasing between lines would
have changed the source under the remaining runs.

## A second, independent measurement of the same vector exists

Rebasing this work onto the branch head produced an add/add conflict on
`code/points/point_de322e4659.txt`: another session had measured the same
control vector and, because the point tag hashes the VECTOR and not the
model, landed on the same filename.

The two are not duplicates. They are the same vector solved on different
sources:

| | this measurement | the other session's |
|---|---|---|
| file | `point_de322e4659.on_64d52d8b6a.txt` | `point_de322e4659.txt` |
| `MODEL` | `64d52d8b6a` | `1b081ebc4d` |
| solve time | 12 min | 13 min |
| `beta` target in force | 2.5 | 3.0 |
| `beta` model value | 2.4528917327498072 | 2.4532192344769714 |
| `w_bot` model value | 0.024267317563111793 | 0.024742905191260153 |

Neither was clobbered. This one keeps the `.on_<model hash>` suffix the
repository already uses in `points_superseded/`, and everything above in
this file refers to it.

**The tag collision is worth noticing on its own account.** Two different
sources produced one filename, and a plain `git checkout --theirs` or a
re-run would have silently replaced one measurement with the other. The
`MODEL` stamp inside the file is the only thing that distinguishes them.

The two disagree on `w_bot` by 1.9 per cent relative
(0.024267 against 0.024743), which is 380 times the 5.13e-05 run-to-run
reproducibility band, so they are measuring genuinely different economies
and must not be quoted alongside one another.
