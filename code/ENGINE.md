# The calibration engine

**This file is the engine's instructions. The trigger prompts are stubs that
point here.** They used to carry the whole thing, in three copies, and that cost
real mistakes: on 1 September both prompts asserted a concession the author had
reversed, and the parameter warnings in them were wrong by a factor for a day.
One source of truth, versioned, edited by commit.

## The objective

The author's rule, 30 August: *"once we get below 10% for everything we can
stop"*. A MINIMAX over every scored moment, with `beta` scored zero inside its
3.0–4.5 band. `next_batch.py` tests it and returns 4 when it is met.

**What is conceded is whatever `SKIP` says.** Read it out of `next_batch.py`;
each entry carries the author's own words. **Do not add to it without them** —
conceding a moment is a scope change.

## Two names mean two things

Confusing them has already cost a concession.

| name | the MOMENT | the PARAMETER the author means |
|---|---|---|
| h_2 | "above half of spending", CEX severe cost burden, target 0.101 | the cheapest rental rung, `smallest_rental_relative_to_lowest_income` |
| h_3 | share in the largest unit | the middle rung, assigned at 2× the cheapest |

On 1 September a statement about the parameter h_2 was applied to the moment, and
a moment sitting at −18 per cent was conceded until the author caught it. When
they say "h_2", work out which one they mean before acting.

## Each firing, in order

**0. Verify the checkout.**
```
git fetch origin claude/two-period-addiction-hazard-d7gb61
test "$(git rev-parse HEAD)" = "$(git rev-parse FETCH_HEAD)" || \
  git checkout -B claude/two-period-addiction-hazard-d7gb61 FETCH_HEAD
```

**1. No supervisor beside measurements, ever.** One is found at nearly every
firing, resurrected from stale container snapshots, and one once committed over
the coordinator's working tree. `code/CALIBRATION_ACTIVE` must be absent. Test
POSITIONALLY — `pgrep -f` matches the checking shell:
```
ps -eo args= | awk '{ n=split($1,p,"/"); m=split($2,q,"/");
    if (p[n] ~ /^python/ && q[m]=="supervise_calibration.py") found=1 }
  END { exit found ? 0 : 1 }'
```
If up: `kill -9`, remove the marker, verify the tree with `git status`, say so.

**2. Check the archive has points on the current model.**
```
cd code && H=$(md5sum housing_first_or_treatment_first_SR_v1.f90 | cut -c1-10)
grep -l "MODEL $H" points/*.txt | wc -l
```
Zero means the gate has nothing to interpolate from and any batch it writes is a
guess dressed as a step. SEED instead, with one anchor at the best known vector.

**3. Run the gate.** `python3 code/next_batch.py`, branch on the exit code:

- **4 — DONE.** Every scored target inside ten per cent. STOP. PushNotification
  the author, report the full gap table, update `CALIBRATION_STATE.md`.
- **0 — a batch was written**, filename in the output. Commit it, launch it, and
  use THAT filename in every worker prompt.
- **3 — identical to the last batch**, so a round is still solving. Check for
  stalled workers and respawn only the specific missing lines.
- **2 — the drug block is open** and could not be repaired automatically. If the
  message says no local Jacobian can be fitted, it has already emitted
  `batch_drugfit.txt` and returned 0 instead. Otherwise `restore.py <tag>`, or
  `repair3.py <tag>` when `pi_eu` also needs holding.

**4. Check which lines landed, not how many.** A count hides a worker stalled on
a permission prompt. Compare batch lines against `VECTOR` lines in
`code/points/` and respawn only what is missing. Nothing landing in two firings
means the fleet has drained.

**5. Workers — use the whole fleet.** Up to 8 alive, up to 3 lines each, so a
round of 24 lines fits. At one beta type a solve is about six minutes, so a full
round lands in roughly twenty minutes. Do not run a narrow round to be careful;
the batch is one arm per out-of-target parameter and its width is the point.

```
source_url:      https://github.com/srotberg/housing_first_or_treatment_first
source_revision: claude/two-period-addiction-hazard-d7gb61
```

Every worker prompt must say:
- `cat -n` the batch file, read the assigned line off the screen, issue a
  SEPARATE Bash call with that line VERBATIM. **Never command substitution** —
  `$(sed -n "1p" ...)` prompts for permission and strands the container.
- Do not stop after preparing; actually run it.
- **Name the branch and make it verify.** `git rev-parse --abbrev-ref HEAD`
  before starting and after every push, and never create or check out another
  branch. One worker put itself on `batch-beta-run` and its work was unreachable.
- Every value in the line is deliberate and none is to be corrected, however odd.
  A `MOMENT theta` of −1.0 is an empty-population sentinel, not a value.
- Never edit anything in `code/` while a solve runs — bash reads a script by byte
  offset and an edit under it resumes mid-word.

**5a. SHOW THE AUTHOR THE FULL GAP TABLE WHENEVER THE LOSS IMPROVES.** Their
instruction of 1 September: *"I want you to show me the full gaps table each time
the loss function improves."* Run `python3 code/gaps.py` EVERY firing. It decides
for itself: it prints the whole table when the minimax has fallen and one line
when it has not, and it keeps the high-water mark in `.gaps_best` so the decision
survives a container. When it prints the table, relay the whole thing to the
author -- not the worst few rows, not the median. They have asked for the full
table more than once and the median hides exactly the moment that is stuck.

The loss is theirs: a MINIMAX over the scored moments, with `beta` scoring zero
anywhere inside its 3.0–4.5 band. The median is printed beside it because the two
moved in opposite directions more than once on 1 September, but the median is
never the criterion.

**6. Update `code/CALIBRATION_STATE.md`** whenever a point changes the picture,
and commit it with the batch. That file is the handover; this one is the method.

**7. Report one line:** worst gap of the best point over the scored set, which
moment binds, workers alive. PushNotification (proactive, under 200 chars, one
line, no markdown) ONLY for: the stopping rule met; the fleet stuck two firings
running; something needing the author's decision.

## Rules that do not move

- Every point runs through `code/run_one_point.sh`, cold, with the HANDOVER
  assertion.
- `code/points_pregrid/` is history from the savings-grid bug. Never score it,
  never seed from it.
- Re-measuring an existing vector on a changed model reproduces its md5 tag and
  would overwrite a real measurement. Move `code/points` aside first, write to a
  distinctly named file, restore, verify the archive came back intact.
- A scope change — opening an assigned parameter, changing a target, conceding a
  moment — is the author's call. Fixing an outright bug is not, but say what it
  invalidates and MEASURE before believing it.
- Report moments within ten per cent AT ONE POINT. Each moment at its own best
  point is not a result.
- **Prefer a measured bracket to an elasticity**, and never extrapolate a slope
  past the pair that produced it.
- **Test a large step before calling an instrument dead.** Two were wrongly
  declared dead on 1 September off steps too small to leave a flat region; one of
  them read −0.03 at a 5 per cent step and +1.55 at a 40 per cent one.
- **An anchor moves ONE parameter**, or a pair shown orthogonal by measurement.
  Two multi-parameter anchors failed on 1 September with every individual step
  inside the 0.35 e-fold cap. Capping each step is not sufficient; they do not
  compose.
- **Read an arm beside its cross-effects on every other moment**, not just its
  own. That table is what revealed that `discount_factor_impatient`,
  `value_of_life` and `kappa_phi_d_level` all pass through the drug block, which
  is why the hand-built anchors kept exploding.
