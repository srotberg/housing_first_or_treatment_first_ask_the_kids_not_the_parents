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

## THE HOUSING LADDER, in the author's own words

Stated by them on 2 September and settled: *"the smallest unit is the street, h1.
that targets the homelessness rate. h2 targets the share of homeless with a job.
h3 is 50% higher than h2 and h4 is 100% larger than h2."*

| rung | index | what it is | size | targets |
|---|---|---|---|---|
| h_1 | -1 | the street | h_2 x `size_homelessness` | the homelessness rate |
| h_2 | 0 | cheapest rental | `smallest_rental_relative_to_lowest_income` | the employed share of the homeless |
| h_3 | 1 | middle rental | 1.5 x h_2 | nothing; it is a ratio |
| h_4 | 2 | largest rental | 2 x h_2 | nothing; it is a ratio |

FOUR LABELS, THREE RENTAL RUNGS. h_1 is the street, so the ladder reads as four
rentals if the labels are counted, and the author asked on 2 September why there
were six and how to keep people out of the fourth. There is no fourth rental unit:
`housing_size` is dimensioned -1:2 and every point prints exactly three
`DIAG unit` lines. The moment called `h_3` is "share in the LARGEST unit", which
is index 2, the third rental -- a label and a measurement that do not match.

THE STREET IS A RATIO OF THE RUNG, not a level: `size_homelessness` multiplies
h_2. So moving h_2 drags the street with it unless something holds it, which is
why the stepper works in (rung, absolute street) coordinates and rescales the
ratio underneath. Do not undo that.

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

**5-. SPLIT FILES MUST BE UNIQUE PER ROUND, LIKE THE BATCHES THEMSELVES.**
next_batch.py already refuses to reuse a CORRECT_n name, for a reason written out
below it: a worker reads its line, `git pull --rebase` between lines, and picks up
whatever the file now says. On 2 September the coordinator then split every round
into the SAME names -- `batch_st_00.txt`, `_01`, `_02` -- and reused them four
rounds running. Three workers reported it themselves: *"batch file replaced
upstream"*, *"file rewriting concurrently -- draining current queue"*, *"batch file
overwritten, pt 3 new"*. The points are still valid measurements, because each
records the vector it actually ran, but they are not the arm they were launched
for and nothing outside the worker's chat says so.

Name the split after the batch it came from -- `batch_c50_00.txt` from
CORRECT_50 -- and never reuse a number.

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

**REPORT ONE EQUILIBRIUM. NEVER A BEST-OF ACROSS POINTS.** The author's
instruction, 1 September: *"I want to see the best calibration points when you
report. Not the best points you reached across simulations."*

`gaps.py` is the only sanctioned report, because it prints ONE point — the best
equilibrium — and every moment that point produces. Do not build a table whose
rows come from different points, in any form: not "best gap ever seen for each
moment", not a per-moment minimum over the archive, not a mixture.

This was done once and it misled immediately. A reachability table said
`emp_homeless` had been as good as 69.1 per cent, which read as progress; the
point it came from, `b2969f8ebb`, had `lambda_d` at +1601 per cent, `b` at +775
and `h_1` at +441. It was a wrecked equilibrium whose employed share improved as a
side effect, and the minimax rejects it correctly. Quoting it invited the author
to believe a rung had been climbed that nobody could stand on.

A per-moment scan is a legitimate DIAGNOSTIC — it answers whether an instrument
can move its moment at all — and it may be used to decide what to run next. It is
not a report and it does not go to the author as one. If it must be mentioned,
say what point each number came from and what else was true there.

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

## PIN b AND lambda_d FIRST, THEN ADJUST THE REST

The author's ordering, 1 September: *"You might need to first pin down lambda d
and b and then adjust the rest."* That is what the gate is for, and it is the
right instinct for a reason worth stating: six of the nine instruments drag the
drug block, four of them violently, so any step taken before b and lambda_d are
pinned is measured against a moving base and has to be measured again.

The rule the loop follows:

- **Gate open** — both inside five per cent — emit composed steps, each
  compensated so it does not knock the block back out. That is the only mode that
  can produce a better equilibrium.
- **Gate shut but within four times the threshold** — the round is the drug block
  ALONE. No arms. The gate is a round or two away and every worker spent
  elsewhere is a worker not closing it.
- **Gate shut and far** — arms beside the repair, because the measurements are
  needed, the gate may stay shut for hours, and nothing else is using the fleet.

The middle case exists because the first version of this got it wrong in the
other direction: with the gate at 8.6 per cent the loop still emitted twenty-six
arms beside the repair and spread eighteen workers across everything.

**And do not expect the reported loss to move while the gate is shut.** Every
point in that mode is a one-parameter arm, and a one-parameter move cannot
improve a minimax binding on a moment it does not touch. Eighty-five points
landed on 1 September with the loss fixed at 100.1 per cent, which looked like
failure and was the measuring phase working normally. Say so when reporting
rather than letting a flat number read as a stall.

## THE MODEL IS FROZEN. Do not change the Fortran.

On 1 September the source changed TWELVE times and the archive reset eleven of
those, because eleven were semantic. That, and not the solver, is why the loss
did not converge: no search ever held more than a few points on one model. A
six-minute solve and eight workers is forty points an hour, and it bought almost
nothing because the target kept moving.

So from here the Fortran does not change. Not for a retarget, not for a better
denominator, not for a parameter that ought to be settable. If something in the
model looks wrong, WRITE IT DOWN in CALIBRATION_STATE.md and put it to the author
at the end of a run rather than fixing it mid-search. A model that holds still
for two hours is worth more than any single fix on that list.

The one exception is an outright bug that makes points meaningless, and even then
say what it invalidates before touching it.

**The author can thaw it, and did once, on 1 September.** They asked for the
street's labour cost to be "20% extra on the job loss and 20% less on the job
find rate", which the divided form could not give -- one parameter cannot be 1.2
one way and 0.8 the other under `*(1+x)` and `/(1+x)`. The finding side became
`*(1-x)`. That is a scope change, it is theirs to make, and it was made.

What the freeze still demands, and what was done that round:

- **Say what it invalidates, in the commit, before it is believed.** The hash
  moves, so every scored point stops counting.
- **Measure whether it really invalidates them rather than assuming.** Re-run one
  vector under the new form and compare moment by moment. If nothing moves by
  more than about one per cent of target, the pair belongs in
  `EQUIVALENT_MODELS` with the measured table written beside it, and the archive
  survives. `EQUIVALENT_MODELS` is for exactly this and must never be filled in
  from an argument about why the change ought to be small.
- **Run that comparison in a scratch copy**, never in `code/points`. The vector
  reproduces its own md5 tag and would overwrite the very measurement it is
  being compared against.

The freeze is back on the moment the change lands.

Comments are safe: `model_hash.py` strips them, so documenting the code no longer
resets the archive. That was one of the twelve.

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
