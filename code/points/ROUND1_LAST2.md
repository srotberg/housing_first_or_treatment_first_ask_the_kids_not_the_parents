# Round 1, the last two: `w_bot` and `beta`

Three points off `point_990da2a08d`, the best round-1 point on this economy
(seven of nine inside ten per cent, `pi_eu` carried). Only `w_bot` and `beta`
were out, and the batch tests whether patience moves them.

| line | point | `discount_factor` | `discount_factor_impatient` | solve |
|---|---|---|---|---|
| base | `point_990da2a08d` | 0.99950 | 0.62 | 10 min |
| 1 | `point_932e3cd75a` | 0.99950 | **0.75** | 15 min |
| 2 | `point_db14af8e82` | 0.99950 | **0.85** | 15 min |
| 3 | `point_35e8286c4e` | **0.99980** | **0.75** | 14 min |

Every other coordinate is identical across the four.

## The three `MODEL` lines agree

All three runs report `MODEL b8dc1077ad`, which is also the hash on
`point_990da2a08d`. **Confirmed: the four points are the same model binary**,
so the differences below are the parameter vector and nothing else. All three
also report `HANDOVER OK: 42 of 42 parameters applied`, and all three pass
every invariant.

## The nine round-1 moments

`beta` is a BAND, 3.0–4.5; its gap is measured to the nearer edge, and is 0
inside the band. Everything else is a point target and the gap is against it.
`IN` is within ten per cent.

| moment | target | base 0.62 | line 1, 0.75 | line 2, 0.85 | line 3, 0.75 + df 0.99980 |
|---|---|---|---|---|---|
| `aleph`   | 80.0        | 74.001083 −7.50% IN  | 75.522905 −5.60% IN  | 77.491335 −3.14% IN   | 75.828008 −5.21% IN  |
| `beta`    | BAND 3.0–4.5| 2.372005 −20.93% OUT | 2.413284 −19.56% OUT | 2.466814 −17.77% OUT  | 2.452826 −18.24% OUT |
| `omega_l` | 0.40        | 0.363737 −9.07% IN   | 0.363362 −9.16% IN   | 0.362250 −9.44% IN    | 0.363505 −9.12% IN   |
| `sigma_y` | 0.172       | 0.169050 −1.72% IN   | 0.169050 −1.72% IN   | 0.169050 −1.72% IN    | 0.169050 −1.72% IN   |
| `tau_l`   | 0.224       | 0.225810 +0.81% IN   | 0.226559 +1.14% IN   | 0.229975 +2.67% IN    | 0.226321 +1.04% IN   |
| `pi_eu`   | 0.139       | 0.136811 −1.57% IN   | 0.134282 −3.39% IN   | 0.128233 −7.75% IN    | 0.134279 −3.40% IN   |
| `pi_V`    | 0.266       | 0.253516 −4.69% IN   | 0.255749 −3.85% IN   | 0.255657 −3.89% IN    | 0.255978 −3.77% IN   |
| `cbar`    | 0.0042      | 0.004091 −2.58% IN   | 0.003942 −6.14% IN   | 0.003637 −13.41% OUT  | 0.003935 −6.31% IN   |
| `w_bot`   | 0.0250      | 0.017450 −30.20% OUT | 0.023930 −4.28% IN   | 0.032456 +29.82% OUT  | 0.024270 −2.92% IN   |
| **inside ten per cent** | | **7 of 9** | **8 of 9** | **6 of 9** | **8 of 9** |

## Line by line

**Line 1, `discount_factor_impatient` = 0.75 — eight of nine.**
One moment outside:

- `beta` 2.413284, **−19.56%, BELOW the 3.0 band floor**.

`w_bot` came in at 0.023930, −4.28% below its 0.0250 target and inside. This is
the moment the batch was built to move, and it moved: 0.017450 → 0.023930, a
step of +0.006480 for 0.62 → 0.75.

**Line 2, `discount_factor_impatient` = 0.85 — six of nine.**
Three moments outside:

- `beta` 2.466814, **−17.77%, BELOW the 3.0 band floor**;
- `cbar` 0.003637, **−13.41%, BELOW its 0.0042 target**;
- `w_bot` 0.032456, **+29.82%, ABOVE its 0.0250 target**.

0.85 overshoots. `w_bot` crosses the target and lands almost exactly as far
past it as the base was short of it, and the overshoot costs `cbar` as well.

**Line 3, `discount_factor_impatient` = 0.75 with `discount_factor` = 0.99980
— eight of nine.** One moment outside:

- `beta` 2.452826, **−18.24%, BELOW the 3.0 band floor**.

## Does any line beat seven

**Yes. Lines 1 and 3 are both eight of nine, against seven for
`point_990da2a08d`.** `w_bot` is inside on both; `beta` is the only moment
still out anywhere in the batch.

Line 3 is marginally the better of the two on the two moments that separate
them — `w_bot` −2.92% against −4.28%, `beta` −18.24% against −19.56% — but the
two are close enough on every moment that neither dominates, and line 1 is the
cheaper vector in that it leaves `discount_factor` where the rest of the
calibration has it.

## Did raising patience break anything that was inside at 0.62

At 0.75, **no**. Both watched moments held: `aleph` −7.50% → −5.60% (it moved
TOWARD its target) and `cbar` −2.58% → −6.14% (it moved away, but stayed
inside). Line 3 is the same story: `aleph` −5.21%, `cbar` −6.31%, both in.
Nothing else that was inside at 0.62 left the band on either 0.75 line;
`omega_l` drifts a few hundredths of a per cent further out at −9.16% and
−9.12% but was already at −9.07% and is still in.

At 0.85, **yes — `cbar` broke**, from −2.58% at 0.62 to −13.41%, out. That is
the moment the brief flagged as one to watch, and 0.85 is where it goes. It is
the second casualty of that line rather than the first: `w_bot` had already
overshot to +29.82%.

So the cost of raising patience is not paid between 0.62 and 0.75. It is paid
between 0.75 and 0.85, and by then `w_bot` has passed its target anyway.

## `beta`, the probe

The brief asked for what `discount_factor` = 0.99980 does and for no
projection, and that is what follows.

Lines 1 and 3 are a matched pair: same vector, same
`discount_factor_impatient` = 0.75, `discount_factor` 0.99950 → 0.99980 the
only difference. `beta` went 2.413284 → 2.452826, **+0.039542, or +1.64%**.

The band floor is 3.0. From 2.452826 that is a further +22.3% to travel.

`beta` is out on all three lines of this batch, at −19.56%, −17.77% and
−18.24%, having been −20.93% at the base. Across the five retune lines it sat
between 2.351825 and 2.412630; this batch carries it to 2.466814 at the top.
Both instruments tried here move it in the right direction and both move it by
very little: +1.7% for 0.62 → 0.75 on impatience, +1.6% for 0.99950 → 0.99980
on `discount_factor`. No projection is offered from these two points.

One caveat on calling `beta` immobile. It is immobile *under patience*, which
is what has been tried on it. It is not immobile in the family:
`point_846f6a0a53` reaches 2.800366, −6.7% against the floor, and it gets there
on `probability_becoming_unemployed=0.0437` — at the cost of `pi_eu` 90% out.
The instrument that has actually moved `beta` is the one this economy fixed at
0.0122 to buy `pi_eu`.

## What this batch settles

- `w_bot` is not immobile. It was −30.2% and the instrument that owns it is
  `discount_factor_impatient`; 0.75 puts it inside, 0.85 puts it outside on the
  other side. The bracket is now 0.75 (−4.28%) and 0.85 (+29.82%).
- The old ladder was right to be distrusted. It predicted 0.0418 at 0.70;
  0.75 delivers 0.023930. The brief's instruction not to interpolate on it
  held up.
- `beta` is the one moment left, and neither instrument in this batch reaches
  it. Nine of nine needs something that is not patience.
- **Eight of nine is the best count measured on this economy**, against the
  seven of `point_990da2a08d` recorded in `ROUND1_RETUNE.md`. It is also the
  first time `w_bot` and `pi_eu` are inside together: `point_846f6a0a53` held
  `w_bot` at −7.0% but only with `pi_eu` +89.9%, and every line since had
  `pi_eu` for `w_bot`. Lines 1 and 3 hold both.
