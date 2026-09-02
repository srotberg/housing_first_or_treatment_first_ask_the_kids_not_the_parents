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

**5a. SHOW THE FULL GAP TABLE EVERY FIRING, WITHOUT EXCEPTION.**

The author, 2 September: *"each time a loop finishes, i want to see the current
best point's gaps table. it should be an automatic reporting."* This supersedes
their earlier *"each time the loss function improves"* -- the table goes out every
firing whether or not anything moved.

    python3 code/gaps.py --force

`--force` prints the table regardless of the high-water mark. The first line still
says which of three things happened, and that line matters as much as the table:

    PROGRESS                  the sorted gap vector improved lexicographically
    loss unchanged            it did not
    FIRST POINT in this economy   the mark was reset -- by a model change, a beta
                              configuration change, or the scored set changing --
                              so there is NOTHING to compare against and this is
                              not an improvement

Relay the WHOLE table: every parameter, its value, its moment, model, target and
gap. Not the worst few rows, not the median -- the median hides exactly the moment
that is stuck. One equilibrium, never a best-of across points.

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

## AN EARLIER ROUND'S MOMENT IS NUDGED, NOT STEPPED

The author, 2 September: *"in each subsequent stage, i want all the previous
stage's parameters to be adjusted slowly if needed if their model's moments
drift."*

Every open round's instruments stay live, so a moment that a later round knocks
back out of ten per cent is recovered rather than abandoned. But it is recovered
SLOWLY: a full Newton step on an earlier round's instrument undoes the round being
worked. aleph is the case that shows why -- its full step moves b by -85 per cent
and lambda_d by -91, which is round 2 destroyed to repair round 1.

    same round as the one being worked   full step
    one round back                       quarter step
    two or more rounds back              one eighth

The batch line says so: `earlier round (1), nudged at 0.25 step`. This replaced a
hard-coded aleph special case; do not add another one, extend the rule.

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

## A bounds-checked run is part of any change that opens an array index

Added 2 September, after two out-of-bounds bugs in one night.

Unsecured borrowing opened twenty-five renter state loops down to a financial
index of 1. Every renter array is allocated
`is_owner*1+(1-is_owner)*negative_financial_grid_size:financial_grid_size`, so
index 1 did not exist for a renter and all twenty-five loops ran past the lower
bound of `value_function`, every `policy_function_*` and `warm_start_a_prime`.

**What it looked like.** Not a crash. The borrowing-OFF control solved cleanly,
passed every one of the seventeen invariants, and returned `w_bot` 0.0032695
against a known 0.029487 -- an order of magnitude BELOW the target rather than
above it -- homelessness 0.0114 against 0.0842, and drug use of exactly zero. It looked like an economy. Hours of fleet time went into arms
measured on it, and a controlled OFF/ON twin taken from it was reported to the
author as evidence that borrowing was inert -- when what it actually showed was
that the ON arm's extra states were writes into memory belonging to something
else. A SIGSEGV on a later revision is what finally named the cause.

**The rule.** Any change that widens the range of an array index -- a loop
bound, a floor, a grid size -- gets ONE run under

    gfortran ... -O1 -fcheck=bounds,pointer -g -fbacktrace

before anything is measured on it. It is several times slower than the -O3
build and it does not need to finish: the first violation is the finding. One
such run costs less than a single 15-minute solve and would have caught both of
these in minutes.

**And the reason it is a rule rather than a habit.** The invariants cannot see
this. They check that the histogram holds the whole distribution, that the
rental market clears, that the age bands hold all of the homeless -- all of
which a corrupted-but-consistent solve satisfies. Neither can `gaps.py`: an
out-of-bounds economy has a loss, and it is a number. The only cheap detector is
the compiler.

**The corollary for controls.** The OFF control is what caught this, and it
caught it only because it was a re-measurement of a vector whose answer was
already known. A control whose expected value is not known in advance cannot
falsify anything. When a change is meant to be a no-op somewhere, re-measure the
vector it should not move and state the reference value BEFORE the run.

## A worker that blocks on input is lost, so brief against it

A remote worker cannot be messaged from the engine session. If it ends a turn
asking a question, it waits forever and its whole batch is dead time -- the
`beta frontier` worker sat blocked for twelve minutes on "provide line 3 of git
checkout -B c command", having split a git command across Bash calls and stopped
to await the rest.

Two lines in every brief prevent it:

- give multi-part git as SEPARATE one-line Bash calls, spelled out, rather than
  as a block the worker may treat as something to continue;
- say explicitly: **every Bash call must be a complete command; never leave one
  half-typed expecting to continue it in a later call.**

And check for it. `get_session` on a worker shows `status_category: need_input`
with the question in `needs_action`. A blocked worker looks IDLE, which is the
same status as one that has finished, so idleness alone does not mean done.
Relaunch rather than wait: the batch file is in the repo and a fresh worker picks
it up from scratch.


## The container is part of the measurement

Added 2 September, after a control run separated two things that had been
conflated all night.

`TARGET_CHANGE_CHECK.md` was commissioned to ask whether changing
`wealth_to_output_data` from 3.0 to 2.5 -- a calibration TARGET, not a model
primitive -- had changed the economy. It had not. But the same run found that
the archive could not be reproduced at all:

    archive vs the same source rebuilt in another container   w_bot  1.78e-02
    3.0 vs 2.5, both in one container                         w_bot  6.86e-04
    one identical binary, run twice in one container          w_bot  1.21e-03

The constant's own effect is SMALLER than the spread between two runs of one
binary. What differs is the execution environment.

**This qualifies the REPRODUCIBLE finding in `DETERMINISM.md`.** That measured
5.13e-05 worst over 23 targeted moments -- three sequential cold runs IN ONE
CONTAINER. It is a statement about one container, not about the model, and it was
reported as though it were the latter. Another container's own floor is 1.21e-03,
twenty-four times larger, and across containers the spread reaches 1.8e-02.

**Why it matters here specifically.** Every worker runs in its own container, so
every point in the archive was measured somewhere different. On `w_bot`, whose
target is 0.0250 with a ten per cent budget of 0.0025, a cross-container spread
of 1.8 per cent eats about a fifth of that budget before any parameter moves.

**The rule.** A controlled pair must be measured in ONE worker. The existing
brief already does this by accident of a different rule -- all three lines of a
batch run in one container -- so arms WITHIN a batch are sound. What is not sound
is the thing done constantly all night: comparing a new batch against a base read
out of the archive and measured by an earlier worker. **A batch that needs a base
must re-measure the base as one of its own lines.** It costs one solve and it is
the difference between a bracket and a coincidence.

Readings taken across batches are not worthless -- 1.8e-02 is small against gaps
of 100 or 700 per cent -- but they cannot settle anything at the ten per cent
margin, which is exactly where the calibration now is.


### The author's decision on tolerances, 2 September

**Leave the outer tolerances where they are and tighten at the END of the
calibration.** In their words: "it's fine for now. We can tighten at the very end
of the calibration. Right now we want convergence."

So the rental and housing markets stay at 2e-2, the government budget at 1e-2,
and the ~1.8e-02 cross-container spread on `w_bot` stands as a known cost rather
than a bug to fix now. Do not propose tightening again while the search is
running; it is a settled decision with a scheduled revisit.

What still applies meanwhile is the same-worker rule above: a controlled pair is
measured in one container, so the spread cancels within a batch and the search
does not need the tolerances tightened to make progress. The place it will matter
is the FINAL reported benchmark, which is exactly when the author has said to
deal with it.


## Push after every line, and never change the model under a running batch

Added 2 September, after losing four solved points to both mistakes at once.

**Push after every line.** The no-rebase-mid-batch rule exists so a source change
cannot split one batch across two economies. Holding the PUSH to the end was my
own addition and has no such justification: a worker held four solved points for
forty-five minutes, invisible, blocked behind a fourth solve, and they were lost.
The brief must say: commit and push after EACH line, and simply never pull. If a
push is rejected because the branch moved, leave that commit local, carry on, and
push again after the next line -- rebasing mid-batch would rebuild the binary
from a different source, which is the thing the rule exists to prevent.

**Model changes wait for a quiet fleet.** A batch is a measurement of ONE
economy. Three author-instructed changes landed while that batch ran -- the
seven-point grid, the unemployment target, and beta's target going back to 3.0 --
so its points were stale before they arrived. The author is entitled to change
anything at any time; the engine's job is to QUEUE the change, say it is queued
and what it is waiting on, and apply it when nothing is mid-solve. Applying a
change immediately while eight worker-hours are in flight is not responsiveness,
it is discarding the work without saying so.

The exception is a BUG. A model that is wrong should stop the fleet at once,
because everything it is measuring is worthless anyway. Three times tonight that
was the right call -- the build failure, the out-of-bounds arrays, the ambient
age_index. A target or a grid is not that.


## A worker must push to its OWN branch, not the shared one

Added 2 September, after deadlocking a worker with two rules that cannot both
hold.

The rules were "push after every line" and "never rebase mid-batch". Together
they are impossible on a shared branch: a plain push is rejected the moment the
branch moves, and without a rebase the worker can never make it succeed. A worker
solved its first point at 14:15 and reported "local commits ready; retrying push
after line 2 solve" -- and every retry failed too, because the ENGINE was pushing
batch files and notes to the same branch every few minutes. The engine was the
blocker, and the worker was doing exactly as told.

Rebasing is not the fix. run_one_point.sh rebuilds from the working tree on every
line, so a rebase between lines can build the next point from a different source
and split one batch across two economies -- which is the whole reason the
no-rebase rule exists.

**The fix is a branch per worker.** Brief every worker to push with

    git push origin HEAD:refs/heads/wip/<worker-name>

which never conflicts because nothing else writes there, needs no fetch, no pull
and no rebase, and leaves the checkout untouched. The engine then collects the
points with a fetch and a checkout of the paths it wants, at a moment of its own
choosing.

Until that is in every brief, the interim rule is simpler and also correct: **the
engine does not push to the shared branch while a batch is in flight.** Hold
notes and batch files locally and push them when the fleet is quiet. Committing
process notes about not disturbing running work, in a way that disturbs running
work, is the specific failure to avoid.

## A TARGET IS NOT A MODEL, and it used to reset the archive like one

The single largest cause of "no scoreable point in the current economy" on
2 September was not a bug and not a slow solve. Fifteen points solved between
12:53 and 15:00 and not one was scoreable, because FOUR source changes landed in
that window and every one of them re-stamped the model. Two of the four were
TARGET edits the author asked for -- the wealth-to-GDP ratio to 2.5 at 12:53 and
back to 3.0 at 13:59, ninety minutes apart.

A target changes nothing about the economy. It is not in any household's
problem, any price, or any equilibrium condition; it enters a `write` statement
and a gap in the outer calibration stepper, and a point pins every parameter so
the stepper has nothing left to move. The three points measured between 13:18
and 13:59 differed from the source that followed them by EXACTLY ONE non-comment
line in 40,000, `wealth_to_output_data=2.5d0` against `=3.0d0`, and were thrown
away for it.

`model_hash.semantic()` now blanks the VALUE of the constants in
`TARGET_CONSTANTS` while keeping their declaration, so renaming or deleting a
target still moves the hash and only the number is ignored. Those three points
came back the moment it did.

**THE BAR FOR ADDING A NAME TO THAT LIST IS EVIDENCE, NOT THE SUFFIX.** Thirty-six
constants end in `_data` and most of them are NOT safe: `personal_exemption_data`
and `standard_deduction_data` build the tax function, `avg_labor_supply_data` is
inside a labour supply expression, `fraction_of_average_house_price_data` is in
the household problem. Read every non-comment use of a name before adding it. If
any use is an equilibrium object rather than a write or a stepper gap, it stays
out.

The scorer already re-applies the CURRENT target rather than the one baked into
the point file, for `beta`, through `BAND` -- which is why a point measured at
2.5 scores against 3.0-4.5 correctly. Anything else needing that treatment goes
in `TARGET_OVERRIDE`.

**AND THE OTHER HALF OF THE LESSON IS SCHEDULING.** Two of the four changes were
real -- the grid went from 4 negative points to 8 with a new limit -- and those
correctly killed seven points. Solving THROUGH a run of model edits is what
wasted the two hours. Settle the source first, then launch; a solve started
before an edit that is already coming is a solve thrown away.

## A WORKER MUST NOT BACKGROUND THE SOLVER

On 2 September three workers were briefed to run their point in the FOREGROUND
and all three backgrounded it anyway, reported "4h run in flight", and ended
their turn. Twenty-five minutes later none had woken, none had pushed a point,
and one -- bn-on075 -- had produced no branch at all, so its entire solve existed
only inside a container nobody could reach. Cross-session messaging cannot reach
a cloud worker from the coordinator (`ListAgents` shows no peers and this build
has no remote send_message), so a worker that goes idle mid-solve CANNOT BE
NUDGED. The brief is the only control there is.

Say all of this in every worker prompt, not just "foreground":

- Run the solve in the FOREGROUND and do not end your turn while it runs. Do not
  use `&`, do not use run_in_background, do not register it as a background task.
- PUSH THE POINT FILE BEFORE WRITING ANYTHING UP. The measurement is the
  deliverable; the findings file is commentary. A worker that writes prose first
  and dies has produced nothing.
- If you must wait, wait with a blocking command, and push whatever exists first.

## HOW LONG A SOLVE ACTUALLY TAKES, measured

Borrowing OFF, 4 cores: 13, 15, 16, 17 minutes across four points on
841e04b785. Borrowing ON adds seven negative grid points to BOTH the state loops
and the choice loops for every renter, so expect appreciably longer -- the 0.75
and 0.90 arms were still solving at 26 minutes.

DO NOT RESPAWN AN ARM BEFORE ITS PLAUSIBLE WINDOW HAS PASSED. Respawning at
minute 26 of a job that may legitimately take 40 burns a container and produces a
duplicate point with the same md5. Judge it against these numbers, not against
impatience.
