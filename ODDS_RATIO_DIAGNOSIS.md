# Why the child SUD odds ratio cannot be raised

Two point runs at the benchmark-of-record vector, with the three objects the
ratio is built from printed for the first time, plus a hand recomputation of the
ratio from those printed objects.

- **point `6876263050`** — benchmark of record, `penalty_child_addicted=0.24`.
  `delta_d child SUD ratio = 1.0944611599212291` against a target of 2.00.
  `delta_h child homelessness ratio = 3.4476565560901311` against 2.10.
- **point `4cbe708367`** — identical except `penalty_child_addicted=0.85`.
  `delta_d = 1.3124101188405817`, `delta_h = 3.4477586305133157`.

The prints were added immediately above the `stop` inside
`if (sweep_addiction_scalar==1)` (line ~41954), prefixed `RATIODIAG`. They are a
diagnostic and are **not** committed with this report; only this file is.

---

## 0. The headline, before anything else: the shelf is not a shelf

The sweep reads 1.3123 at penalty 0.65 and 1.3124 at 0.85, a move of 2.3e-05
across a penalty change of 0.20. That is not saturation. **Both points ran at
penalty 0.60**, because `penalty_child_addicted` is hard-clamped there:

```
housing_first_or_treatment_first_SR_v1.f90:38324   (PARAM_HANDOVER)
    penalty_child_addicted=max(min(handover_value,0.6d0),0.d0)
housing_first_or_treatment_first_SR_v1.f90:37531   (state file read)
    penalty_child_addicted=max(min(penalty_child_addicted,0.6d0),0.d0)
```

The handover line *prints* the value it was asked for and then assigns the
clamped one, so the log says `HANDOVER penalty_child_addicted: 0.24 -> 0.85`
while the model runs 0.60. This is confirmed independently of the print, from
the object itself: reconstructing `newborn_employment_probability` from the
model's own formula and asking which penalty reproduces the printed `d=1` rows
of point `4cbe708367` gives

```
penalty implied by printed nep(d=1): delta = 0.6000   max abs error 1.1e-16
```

exactly, to machine precision, across all 49 entries. The "flat interval" from
0.65 to 0.85 is the same economy solved twice; 2.3e-05 is the reproducibility of
the solve, not a derivative.

There are in fact **three inconsistent caps** on this one parameter:

| where | cap | line |
|---|---|---|
| the calibrator's own update | **0.4** | 40691–40693 |
| the handover and the state-file read | **0.6** | 38324, 37531 |
| the "PINNED AT A BOUND" warning | **0.9** | 40704 |

So the internal calibration can never move `penalty_child_addicted` past 0.40,
a hand-driven point can never move it past 0.60, and the diagnostic that is
supposed to announce a corner does not fire until 0.90 — which is why nothing in
the output ever said the parameter was pinned.

Removing the clamp does **not** rescue the moment. That is the rest of this
document.

---

## 1. a(k): the disorder rate by productivity node

`percent_addicted_by_employment(1,:)`, point `6876263050`:

| k | y(k) | node mass | a(k) | a(k)/ā | h(k) | h(k)/h̄ |
|---|---|---|---|---|---|---|
| 1 | 0.0511 | 0.002007 | 0.073275 | 2.2094 | 0.271776 | 29.2652 |
| 2 | 0.1170 | 0.033259 | 0.054167 | 1.6333 | 0.097477 | 10.4965 |
| 3 | 0.2681 | 0.194406 | 0.042054 | 1.2680 | 0.009651 | 1.0392 |
| 4 | 0.6144 | 0.399108 | 0.033377 | 1.0064 | 0.005590 | 0.6020 |
| 5 | 1.4078 | 0.290039 | 0.027679 | 0.8346 | 0.003604 | 0.3881 |
| 6 | 3.2258 | 0.074344 | 0.022551 | 0.6800 | 0.002583 | 0.2782 |
| 7 | 7.3913 | 0.006837 | 0.019089 | 0.5756 | 0.002043 | 0.2200 |

ā = `csud_d` = 0.0331646575 (the clean-weighted average, computed below);
h̄ = `chom_d` = 0.0092866466.

`a(k)` **is monotone decreasing** in the node index, and it is **shallow**:

```
a(1)/a(7) = 3.8386        h(1)/h(7) = 133.0366
```

Node by node in logs (the grid is uniform in logs at 0.8291 per node):

```
dlog a/dlog y :  -0.364  -0.305  -0.279  -0.226  -0.247  -0.201     OLS over 7 nodes: -0.2673
dlog h/dlog y :  -1.237  -2.789  -0.659  -0.529  -0.402  -0.283
```

### The ceiling

The ratio is a weighted average of `a(k)` over the child's node distribution,
divided by ā. No distribution can put more weight on `a(1)` than all of it, so

```
CEILING = max_k a(k) / csud_d = 0.073275 / 0.0331646575 = 2.2094
```

and this is attained only in the limit where **every** child of a disordered
parent is born on the bottom node. Measured directly by driving the penalty to
1 in the model's own formula: ratio → 2.209433.

Against that ceiling:

- the observed shelf of 1.3124 sits at **59 per cent** of the ceiling;
- the target of 2.00 sits at **91 per cent** of the ceiling.

So the target is *inside* the ceiling — but only just, and only at a penalty that
is economically absurd. Because `a` is very nearly a power law in `y`, the ratio
obeys `ratio ≈ (1-δ)^(-ε)` with ε = 0.267:

```
delta   model (exact, 7 nodes)   power-law approximation
0.240          1.09446                  1.07612
0.450          1.19724                  1.17330
0.600          1.31238                  1.27756
0.850          1.73646                  1.66055
0.923          2.00015                  1.98459
```

**The penalty required to reach 2.00 is δ = 0.9230** — a 92.3 per cent
permanent earnings cut on every child of a disordered parent. Equivalently, at
the penalties that are actually available:

| δ available | ε required for ratio 2.00 | ε measured |
|---|---|---|
| 0.24 (benchmark) | 2.526 | 0.267 |
| 0.40 (calibrator cap) | 1.357 | 0.267 |
| 0.60 (handover cap) | 0.757 | 0.267 |
| 0.90 (warning bound) | 0.301 | 0.267 |

Note in passing that the declaration comment at line 660 states *"The model's
implied elasticity of SUD risk to log productivity is 0.73, so a ratio of 2 needs
a 61 per cent earnings cut"*. The measured elasticity of the printed `a(k)` is
**0.267**, not 0.73, and the required cut is **92.3 per cent**, not 61. The
comment is out by a factor of 2.7 on the elasticity and that is the whole
difference between "reachable at a stretch" and "not reachable".

---

## 2. The contrast with homelessness, which overshoots at δ_h = 0.31

Same machinery, same child draw, same parent shares, a *smaller* penalty — and
`delta_h` = 3.4477 against a target of 2.10, a 64 per cent overshoot. The two
gradients in the table above are the reason, and they differ in two separate
ways.

**First, the slope.** `h(k)` falls by a factor of 133 from node 1 to node 7,
`a(k)` by a factor of 3.8. Most of `h`'s fall is one cliff: between node 2 and
node 3 the homelessness rate drops by a factor of 10.1 (dlog h/dlog y = −2.79),
because that is where the cheapest rental stops being unaffordable. `a(k)` has
no such cliff anywhere; it is a smooth −0.27 power law from top to bottom. The
homelessness ceiling is `max h / chom_d = 29.27`, thirteen times the SUD
ceiling of 2.21.

**Second, and larger: the parent's node distribution.** `delta_h` compares
children of *clean street* parents against children of *clean housed* parents,
and those two groups sit at very different nodes. Holding the node distribution
fixed and letting only the penalty act, the homelessness penalty of 0.31 buys

```
h-ratio from the penalty alone = 1.76884
```

against a model value of 3.4477. The residual factor is

```
3.4477 / 1.76884 = 1.9491
```

and it is pure composition: street parents are concentrated on nodes 1–2, where
`h` is 29× and 10× the average, so their children start the calculation already
poor. `delta_h` overshoots because ρ, not δ_h, is carrying it.

For SUD the same composition channel contributes essentially nothing (§3).
That asymmetry — the same two channels, one moment where both are strong and
one where neither is — is the heart of the puzzle, and it is not a bug: it is
that homelessness is a sharply income-determined state in this model and
substance use disorder is not.

---

## 3. The child's node distribution, disordered parent against clean parent

This is the object the prompt asked to be checked for "nearly identical", and
the answer is in two parts: the **parents'** distributions are nearly identical,
the **children's** are not.

### The parents (`newborn_parent_share`, normalised within cell)

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | mean log y |
|---|---|---|---|---|---|---|---|---|
| disordered housed (:,1,1) | 0.0113 | 0.0873 | 0.2354 | 0.3420 | 0.2378 | 0.0752 | 0.0110 | −0.5058 |
| clean housed (:,0,1) | 0.0056 | 0.0511 | 0.2018 | 0.3510 | 0.2762 | 0.0984 | 0.0159 | −0.3215 |

Masses: disordered-housed dying parents 0.0374, clean-housed 0.9536.

The gap in mean log productivity is **0.184 logs = 0.22 of one node width**.
Set the penalty to zero and let this be the *only* channel:

```
ratio at delta = 0  :  1.01733
```

So parental income persistence, the ρ channel that was added to take "about
half" the work off δ_d, delivers **1.7 per cent** of a ratio that needs 100 per
cent. It is not half. It is a rounding error, and the reason is visible in the
table: a disordered parent in this model is barely poorer than a clean one.

### The children (marginal over parent nodes)

| δ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | ratio |
|---|---|---|---|---|---|---|---|---|
| clean parent (δ=0) | 0.0023 | 0.0345 | 0.1909 | 0.3888 | 0.2933 | 0.0817 | 0.0086 | 1.000 |
| disordered, δ=0.24 | 0.0084 | 0.0795 | 0.2874 | 0.3884 | 0.1968 | 0.0370 | 0.0026 | 1.094 |
| disordered, δ=0.45 | 0.0234 | 0.1476 | 0.3632 | 0.3349 | 0.1155 | 0.0147 | 0.0007 | 1.197 |
| disordered, δ=0.60 | 0.0561 | 0.2344 | 0.3953 | 0.2501 | 0.0589 | 0.0051 | 0.0002 | 1.312 |
| disordered, δ=0.85 | 0.3585 | 0.3912 | 0.2068 | 0.0406 | 0.0029 | 0.0001 | 0.0000 | 1.736 |
| disordered, δ=0.95 | 0.8438 | 0.1359 | 0.0193 | 0.0010 | 0.0000 | 0.0000 | 0.0000 | 2.112 |

**These are not nearly identical, and the penalty is moving the child's draw
exactly as designed.** At δ = 0.24 it shifts the child's log productivity by
−0.274, which is 0.33 of a node width; at δ = 0.60 by −0.916, or 1.10 node
widths. The mass does not pile up on the bottom node until δ is above 0.85. So
the third object is working; it is the first object it is multiplied against
that refuses to reward it.

---

## 4. Hand recomputation of csud_n, csud_d and the ratio

Contracting the three printed objects exactly as lines 6583–6588 do, in double
precision outside the model:

```
                       csud_n         csud_d        ratio         model's own
point 6876263050   0.0362974295   0.0331646575   1.0944611599   1.0944611599212291
point 4cbe708367   0.0435243939   0.0331637140   1.3124101188   1.3124101188405817
```

**They agree to every digit printed.** The moment measures exactly what the
formula says it measures; there is no accounting error in `delta_d` and nothing
is being mismeasured. Whatever is wrong is economics, not bookkeeping.

Two further consistency checks fall out of the same reconstruction:

- rebuilding `newborn_employment_probability` from the model's own AR(1)
  formula (ρ = 0.35, sd of log y at age 1 = 0.775948, edges at the log-grid
  midpoints with outer edges at ±12) reproduces the printed `d=0` rows at
  penalty 1 to 1.1e-16, and the `d=1` rows at δ = 0.24 and δ = 0.60 to 1.1e-16.
  The reconstruction is therefore trustworthy for extrapolating past the clamp;
- general-equilibrium feedback on the other two objects is negligible. Between
  the δ = 0.24 and δ = 0.60 solves, `a(k)` moves by at most 1.9e-04 in relative
  terms, the clean parent shares by 5.2e-06 and the disordered parent shares by
  1.1e-04. Holding `a` and the shares at their δ = 0.24 values and moving only
  the penalty predicts 1.31238 at δ = 0.60 against the model's own full GE
  1.31241 — an error of 3e-05, the same size as the "shelf".

---

## 5. Which of the three objects is responsible

**`a(k)`, the disorder rate by productivity node.** Not `newborn_parent_share`
and not `newborn_employment_probability`.

- `newborn_employment_probability` is doing its job: the penalty moves the
  child's draw smoothly and substantially, a third of a node at δ = 0.24 and
  over a node at δ = 0.60. It is not flat and it is not saturating below 0.85.
- `newborn_parent_share` is nearly inert (contributes 1.017), but it is not the
  *ceiling* — it is a missing 1.7 per cent, not a missing 0.9. It matters mainly
  as the explanation for why homelessness overshoots and SUD does not.
- `a(k)` sets both the gain and the ceiling. Its elasticity of 0.267 means the
  ratio can only ever be `(1-δ)^(-0.267)`, and its maximum-over-average of
  2.2094 is the absolute ceiling at any penalty whatsoever. To reach 2.00 the
  child must be moved essentially to the bottom node of the whole economy — a
  node carrying 0.2 per cent of the population.

## 6. Candidate fixes, and what each costs

**(a) More productivity nodes — this does not work, and the discreteness
diagnosis in the source is wrong.** Rebuilding the same calculation on a grid of
n nodes spanning the same −3.445 to +2.966 standard deviations, with `a(y)` the
fitted power law and the parent distributions fitted to the measured 0.184-log
gap:

| n nodes | ratio @ δ=0.24 | ratio @ δ=0.60 | ceiling |
|---|---|---|---|
| 7 | 1.09471 | 1.29796 | 1.9953 |
| 13 | 1.09467 | 1.29757 | 1.9987 |
| 21 | 1.09465 | 1.29747 | 1.9995 |
| 41 | 1.09465 | 1.29744 | 1.9998 |
| 101 | 1.09465 | 1.29742 | 1.9999 |
| 401 | 1.09465 | 1.29742 | 1.9999 |

Going from 7 nodes to 401 moves the ratio by **6e-05** at δ = 0.24 and 5e-04 at
δ = 0.60. It could hardly be otherwise: `create_newborn_employment_probability`
already *integrates* the normal over each node's own log interval rather than
splitting between two neighbours, so the child's distribution already responds
smoothly and continuously to the penalty — there is no step function left to
smooth out. (The bottom-node merge is also **off** in this vector:
`bottom_productivity_level=0`, so the `merge_bottom_nodes=2` block at line 29782
never executes and the bottom two nodes are not merged.) Cost: a large
recalibration — `y_grid_kappa`, `sd_permanent_productivity`, `kkk_sigma_scale`
and everything downstream of the earnings distribution — and roughly n²/49
times the solve time, for a fourth-decimal change in the moment. **Not worth
doing for this reason.** It may be worth doing for others, but it will not move
`delta_d`.

**(b) Move the child's node index directly instead of shifting the
distribution.** Replacing the log shift with "the child of a disordered parent
is born j nodes below where they would otherwise be", evaluated on the same
`a(k)`:

| j | ratio | implied income cut |
|---|---|---|
| 0 | 1.017 | 0 % |
| 1 | 1.279 | 56.4 % |
| 2 | 1.629 | 80.9 % |
| 3 | 1.975 | 91.7 % |
| 4 | 2.161 | 96.4 % |

Reaching 2.00 needs **three whole nodes**, which on this grid *is* a 92 per cent
income cut — the identical number δ = 0.9230 gave. The reparameterisation
changes the units the penalty is quoted in and changes nothing else, because
the constraint is `a(k)`, not the way the child is moved onto it. It also loses
the smooth response the integrated form was built for, and would put the whole
disordered cohort on one node with no dispersion. Cost: a day's work; benefit:
none. **Do not do this.**

**(c) Raise the caps to a common bound.** Cheap and correct as hygiene
regardless of what else is decided: the calibrator cannot reach 0.4, the
handover cannot reach 0.6, and the pin warning does not fire until 0.9, so a
search that has been at its corner for the whole calibration has been reporting
that it is not. Fixing this makes the corner *visible*; it does not make the
moment reachable, since even δ = 0.60 only buys 1.312.

**(d) Re-target the moment. This is the honest answer.** The moment is not
reachable through an income channel at any defensible penalty, and I would say
so plainly in the note rather than continue to search for it:

- reaching 2.00 needs a 92.3 per cent permanent earnings cut on the children of
  disordered parents. The earnings literature the declaration comment itself
  cites supports odds ratios of 1.33 to 1.89 on low socioeconomic status, which
  in this model's units is a penalty of 0.10 to 0.25 — i.e. approximately the
  0.24 already in place;
- at that defensible penalty the income channel delivers **1.09**, so income
  explains about **10 per cent** of a 2.00 ratio and genes, environment and
  behaviour carry the other 90;
- the ceiling of 2.21 means that even a 100 per cent earnings cut leaves less
  than 10 per cent of headroom above the target, so there is no version of this
  channel in which income is the main story;
- and the intergenerational income persistence that was added to carry "about
  half" of the effect in fact carries **1.7 per cent**, because a disordered
  parent in this model is only 0.18 logs poorer than a clean one.

The consistent statement is therefore: **δ_d is not internally calibrated to a
child SUD ratio of 2.00. It is set externally at 0.24 from the socioeconomic-
status earnings literature, and the model's implied child SUD ratio of 1.09 is
reported as an untargeted moment that the income channel undershoots by design.**
That is a one-line change to the calibration table and a paragraph in the note,
and it is the only option on this list that is both true and cheap.

Explicitly out of scope, per standing instruction: no direct parent-to-child SUD
channel of any kind — no inherited liability, no raised onset for children of
disordered parents, no birth in the disordered state. Nothing above proposes one.
