# The `beta` frontier: three prices for the last moment out

Round 1 stands at **eight of nine** on `point_35e8286c4e`. `beta` alone is
out, at 2.452826 against a band floor of 3.0 — −18.24%. This batch prices
three ways of closing it.

| line | point | changed from the base | solve |
|---|---|---|---|
| base | `point_35e8286c4e` | — | 14 min |
| 1 | `point_a3456efb23` | `discount_factor_impatient` 0.75 → **0.78** | 16 min |
| 2 | `point_44e91bb1d7` | `discount_factor` 0.99980 → **0.99995** | 16 min |
| 3 | `point_551e56afd4` | `probability_becoming_unemployed` 0.0122 → **0.0250** | 19 min |

Every other coordinate is identical across the four.

## The three `MODEL` lines agree

All three runs report `MODEL b8dc1077ad`, which is also the hash on
`point_35e8286c4e`. **Confirmed: the four points are the same model binary**,
so every difference below is the parameter vector and nothing else. All three
also report `HANDOVER OK: 42 of 42 parameters applied`, and all three pass
every invariant (`INVARIANTS: all PASS`, 16 of 16).

## The nine round-1 moments

`beta` is a BAND, 3.0–4.5; its gap is measured to the nearer edge, and is 0
inside the band. Everything else is a point target and the gap is against it.
`IN` is within ten per cent.

| moment | target | base | line 1, impatient 0.78 | line 2, df 0.99995 | line 3, `pi_eu` prob 0.0250 |
|---|---|---|---|---|---|
| `aleph`   | 80.0         | 75.828008 −5.21% IN  | 76.621373 −4.22% IN  | 76.342912 −4.57% IN  | 68.515814 **−14.36% OUT** |
| `beta`    | BAND 3.0–4.5 | 2.452826 −18.24% OUT | 2.465168 −17.83% OUT | 2.469489 −17.68% OUT | 2.723942 **−9.20% OUT of band** |
| `omega_l` | 0.40         | 0.363505 −9.12% IN   | 0.363211 −9.20% IN   | 0.363564 −9.11% IN   | 0.365367 −8.66% IN   |
| `sigma_y` | 0.172        | 0.169050 −1.72% IN   | 0.169050 −1.72% IN   | 0.169050 −1.72% IN   | 0.169050 −1.72% IN   |
| `tau_l`   | 0.224        | 0.226321 +1.04% IN   | 0.226745 +1.23% IN   | 0.225684 +0.75% IN   | 0.229433 +2.43% IN   |
| `pi_eu`   | 0.139        | 0.134279 −3.40% IN   | 0.133240 −4.14% IN   | 0.134269 −3.40% IN   | 0.194791 **+40.14% OUT** |
| `pi_V`    | 0.266        | 0.255978 −3.77% IN   | 0.257160 −3.32% IN   | 0.255605 −3.91% IN   | 0.270691 +1.76% IN   |
| `cbar`    | 0.0042       | 0.003935 −6.31% IN   | 0.003879 −7.63% IN   | 0.003933 −6.36% IN   | 0.005795 **+37.98% OUT** |
| `w_bot`   | 0.0250       | 0.024270 −2.92% IN   | 0.026270 +5.08% IN   | 0.024771 −0.92% IN   | 0.029949 **+19.80% OUT** |
| **inside ten per cent** | | **8 of 9** | **8 of 9** | **8 of 9** | **5 of 9** |

Line 3's count needs a footnote. `beta` at −9.20% is inside ten per cent of
the floor, so it scores `IN` in that column — but ten per cent of the floor is
not the band, and 2.723942 is below 3.0. On the band criterion line 3 is **4
of 9 plus a `beta` that is still out**, and the count of 5 is generous to it.

## 1. Does any line put `beta` in the 3.0–4.5 band?

**No. None of the three does.** `beta` is below the 3.0 floor on all three
lines, as it was on the base and on every line of the previous batch:

- line 1, 2.465168, −17.83%;
- line 2, 2.469489, −17.68%;
- line 3, 2.723942, −9.20%.

Line 3 gets closest by a wide margin and is still short of the floor by
0.276058. Nothing measured here reaches the band.

Line 2 is the measurement the brief asked for and it settles the
`discount_factor` question. 0.99980 → 0.99995 bought **+0.016662** on `beta`
(2.452826 → 2.469489), against the +0.039542 that 0.99950 → 0.99980 bought.
The instrument is not merely slow, it is **decelerating**: half the step size
per unit of `discount_factor` over the second interval that it delivered over
the first. The remaining 0.530511 to the floor is not available on this
instrument, and no figure is projected for what value would deliver it.

## 2. Line 3: what `beta` gained and what `pi_eu` lost

This is the trade, stated as a price.

- **`beta` gained +0.271116**, 2.452826 → 2.723942. In gap terms the distance
  to the floor closes from −18.24% to −9.20%, a little over half of it. That
  is **sixteen times** what `discount_factor` bought on line 2 and twenty-two
  times what impatience bought on line 1.
- **`pi_eu` lost 0.060512**, 0.134279 → 0.194791. In gap terms it goes from
  −3.40%, comfortably inside, to **+40.14%, badly outside** — a swing of 43.5
  percentage points of gap, and the moment moves from below its target to well
  above it.

So the price of closing half the `beta` gap is the whole of `pi_eu`. The two
are the same instrument pulling in opposite directions, exactly as the archive
said: `probability_becoming_unemployed` was cut to 0.0122 to buy `pi_eu`, and
buying it back costs `pi_eu` at a rate of roughly 4.7 percentage points of
`pi_eu` gap per 0.01 of `beta`.

Note also that 0.0250 is only a little over half way from 0.0122 to the 0.0437
that the high-`beta` archive points carry, and `pi_eu` is already 40% out at
this point. There is no reading of this line on which the rest of the way is
cheap.

## 3. Did anything else break?

**On lines 1 and 2, no.** Both hold eight of nine and neither loses a moment
that was inside on the base. The two fragile ones both held:

- `w_bot` −2.92% → **+5.08%** on line 1 and **−0.92%** on line 2. Line 1
  crosses the target but only just; the +29.82% overshoot seen at impatient
  0.85 is not reached at 0.78, and 0.78 sits well inside the 0.75/0.85
  bracket. Line 2 is the best `w_bot` measured on this economy.
- `cbar` −6.31% → **−7.63%** on line 1 and **−6.36%** on line 2. Line 1 drifts
  further out, in the same direction as the −13.41% recorded at 0.85, but at
  0.78 it is still comfortably inside.

**On line 3, yes — three moments broke, and both fragile ones are among
them.** All three were inside on the base:

- `cbar` −6.31% → **+37.98%**, out, and it breaks upward. This is the opposite
  direction from the impatience ladder, where `cbar` fell; more unemployment
  risk means more food-stamp receipt.
- `w_bot` −2.92% → **+19.80%**, out. Also upward, and comparable in size to
  the +29.82% overshoot at impatient 0.85 — the same precautionary-saving
  channel that moves `beta` moves the bottom half's share with it.
- `aleph` −5.21% → **−14.36%**, out. This one was not on the watch list and it
  broke anyway.

So line 3 does not trade one moment for one moment. It trades **half** of
`beta` for `pi_eu`, `cbar`, `w_bot` and `aleph` — four moments lost to close
none, since `beta` is still out of the band at the end of it.

## What this batch settles

- **Nine of nine is not reachable on any instrument measured so far.** Lines 1
  and 2 tie the base at eight of nine without closing `beta`; line 3 closes
  half of `beta` and falls to five.
- **`discount_factor` is exhausted.** +0.039542 over the first interval,
  +0.016662 over the second. The brief asked how little is left; the answer is
  less than the previous step, and falling.
- **`discount_factor_impatient` at 0.78 is a safe interior point** — eight of
  nine, `w_bot` +5.08%, `cbar` −7.63%, both inside — but it buys `beta` only
  +0.012342 and so does not change the picture.
- **`probability_becoming_unemployed` is the instrument that owns `beta`**,
  confirmed at 0.0250, and it is priced. Whether the trade is worth taking is
  the author's call, not this batch's; what the batch establishes is that at
  the point where it has closed half the `beta` gap, four other moments are
  already outside ten per cent.

No instrument value is projected for putting `beta` in the band. Every
projection made on `discount_factor` on this branch has been wrong, and line 2
was run to measure the slope rather than to extrapolate from it.
