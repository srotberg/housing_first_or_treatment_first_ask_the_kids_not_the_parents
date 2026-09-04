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

## NEVER EDIT code/ WHILE A SOLVE IS RUNNING -- THE COORDINATOR INCLUDED

Every worker prompt carries this rule and the coordinator broke it on 4 September.
`run_one_point.sh` was edited to change a default while a bisection was still
running in this container. Bash reads a script BY BYTE OFFSET, so the running
shell resumed at a stale position and the build line came apart:

    code/run_one_point.sh: line 653: -O3: command not found

The point died as `point_e33d8586a4.FAILED.txt` with a build failure that had
nothing to do with the Fortran, which compiled clean throughout. One solve lost,
and several minutes spent suspecting the source.

The same call also used `pkill -f "batch_holdbisect"`, which matched the
coordinator's OWN shell and killed the tool call. Kill by checking the process
list positionally, as the supervisor test below does, and never with a pattern
that the running command line itself contains.

Wait for `ps -eo args= | awk '/run_one_point/ && !/awk/'` to come back empty
before editing anything under `code/`.

## THE PARALLEL ROUND IS SUSPENDED WHILE THE SERIAL SEARCH IS ALIVE

On 4 September the author replaced the batch-and-fleet search with sequential
Nelder-Mead: *"we are better off trying nelder mead sequentially"*, *"since each
iteration is just 2.5 minutes, we are better off doing that"*, *"you can do all
the stages combined"*.

**If `nm_loop.sh` is running, do steps 0, 1 and 2 below and then STOP.** Do not
run `next_batch.py` and do not launch workers. The serial loop owns
`code/points/`: it asks for one trial, solves it, and reads the answer back out of
the archive, so a worker round landing twenty points from a different search
mid-reflection would be read as though the simplex had produced them. Report the
loop's line -- best vertex, worst vertex, evaluations -- and that is the firing.

    ps -eo args= | awk '{ n=split($2,q,"/");
        if (q[n]=="nm_loop.sh") found=1 } END { exit found ? 0 : 1 }'

`code/CALIBRATION_STATE.md` says which search is live and why. When the serial
loop is stopped for good, delete this section rather than leaving it to be read
as still in force.

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

**4a. COLLECT WHAT A BRANCH COMMITTED, NOT HOW IT DIFFERS.**

This is safe only while the coordinator's own tree carries no points for the round:

```
for f in $(git diff --name-only HEAD origin/$b -- code/points/)   # WRONG, see below
```

`git diff` lists files that differ IN EITHER DIRECTION. Once the coordinator has
committed points of its own -- which it does after every re-seed -- a file the
branch never solved shows up because the coordinator has the NEW version and the
worker inherited a STALE one at its branch point. Checking it out replaces the good
file with the stale one.

On 3 September this overwrote five new-economy points with old-economy copies from
branches that had never solved them, and the count of points on the current model
fell from 5 to 1 in one step. It was caught on the count and restored with
`git checkout HEAD -- code/points/`.

The failure is silent in the only way that matters: every file exists, every name is
right, and only the `MODEL` line inside says the contents are from a dead economy.
Nothing complains; the pooled set is simply wrong and the next Jacobian is built on
it. Ask each branch what IT COMMITTED:

```
git log --format='%h %s' --name-only origin/$b --not HEAD
```

then `git checkout origin/$b -- <those files only>`.

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

**A BOUNDS CHECK IS NOT ENOUGH, AND 3 SEPTEMBER PROVED IT.** The flags above
ran completely clean over `get_probabilities_KKK_process`, which reads a local
array `width` that the routine never assigns -- six times, in the transition and
in the unconditional distribution it hands back. Reading uninitialised memory is
not an out-of-bounds access, so `-fcheck=bounds,pointer` is blind to it by
construction. Fresh pages come back zeroed, the middle node's transition row
summed to exactly 0, the normalisation divided by it, and the economy came back
NaN with the employed share of the homeless at -1.97.

So the standing check is now BOTH of these, and the second one is the cheaper
of the two to run:

    gfortran ... -O1 -fcheck=bounds,pointer -g -fbacktrace
    gfortran ... -O1 -finit-real=snan -ffpe-trap=invalid,zero,overflow -g -fbacktrace

The second turns every uninitialised real into a signalling NaN and traps the
first arithmetic that touches one, with a backtrace naming the line. It would
have found this in the first second of the run instead of after a 140-second
solve and a full distribution iteration.

**And it applies to code you did not write.** The bug had been in the file for
as long as the routine had, and it was invisible for exactly one reason: with
`fixed_productivity=1` both of that routine's outputs are thrown away
downstream, the masses by the quantile construction and the transition by the
identity loop. Turning a switch off does not make the code behind it new, but it
does make it live for the first time, and it has to be checked as if it were.

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

## A worker that ends its turn mid-solve is lost, and the brief has to say how

3 September, and it cost twenty minutes of silence that the author noticed
before the engine did. Four arms were launched. Twenty minutes later not one
point file had been pushed, and the reason was not the model:

| worker | state | when |
|---|---|---|
| line 1 | RUNNING | briefed explicitly not to go idle |
| line 2 | **IDLE**, "solve running on 4 cores; awaiting moments block" | 6 min after launch |
| line 3 | **IDLE**, "container building Fortran; monitoring for output lines" | 1 min 43 s after launch |
| line 4 | **never launched at all** | coordinator's omission |

So one arm of four was alive. The two idle ones had working containers with
solves in them and nothing would ever wake them, because **a remote worker
cannot be messaged from the engine session**: there is no send_message tool for
sibling CCR sessions, only create, interrupt and archive. An idle worker is not
recoverable. It is a relaunch.

**The mechanism that actually works.** A command started with the Bash tool's
`run_in_background` parameter keeps running across turns and the harness
RE-INVOKES the worker when it exits. That wake-up is the only reliable one.
What loses it:

- running the solve in the foreground -- the tool times out at 10 minutes and a
  solve can take longer;
- detaching it by hand with `&` or `nohup` -- the harness is not tracking it, so
  nothing wakes anybody;
- ending the turn with "monitoring for output" and no tracked command at all,
  which is what both of these did.

**THIS SECTION CONTRADICTED THE ONE BELOW IT, AND THE ONE BELOW WINS.** The
rule of record, from 2 September, is FOREGROUND: a worker must not background
the solver at all. It was written after three workers ignored a foreground brief,
backgrounded their solve, and died. This section was added on 3 September
proposing the opposite -- background it through the Bash tool's parameter, so the
harness re-invokes the worker when it exits -- on the reasoning that the tool's
own tracking is a mechanism where "do not go idle" is only a hope.

**THE EVIDENCE IS NOW IN AND IT SETTLES IT: FOREGROUND WINS.** At 04:33 on
3 September the two briefs were running side by side on the same model, and the
result is not close:

| brief | workers | outcome |
|---|---|---|
| BACKGROUND, via the tool's `run_in_background` | 5 | **0 woke. 0 pushed.** All five idle 22 to 35 minutes with "solve running (task ...)" or "solve running in background" |
| FOREGROUND, do not end your turn | 3 | **all 3 solved and pushed**, in 2, 3 and 4 minutes |

The harness parameter did not re-invoke a single one of them. Whatever the
mechanism is meant to do, it did not do it here, and the cost was four KKK arms
and the SSI A/B -- five containers of compute that produced nothing.

So the rule below is the rule, without qualification: **brief FOREGROUND.** Do
not brief `run_in_background`, and do not treat any harness tracking as a
substitute for a brief that keeps the worker attached to its own solve.

What both sections agree on, and what the failures actually share: a worker must
never end its turn with the solve unattended, and it must PUSH THE POINT FILE
BEFORE WRITING ANY PROSE. A hand-detached `&` or `nohup` is fatal under either
rule.

**And count the launches.** Line 4 was simply never relaunched after its arm was
invalidated. Before ending the turn that launches a batch, list the sessions
created against the lines of the batch file and check the count matches.

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

### THE COORDINATOR MAY SOLVE, ON THE AUTHOR'S EXPLICIT AUTHORISATION OF 15:28

The author, 3 September: *"Yes, solve it in your container."* Granted after
twenty-four of twenty-eight workers were killed by API 529s and the fleet had
landed nothing for three firings, while this session's own API calls had
succeeded all day without a single failure.

**Measured on the first authorised solve: 5 minutes 0 seconds**, two beta
types, worker log 15:28:43 to 15:33:43. That is the honest cost of the rule
below and it is a twentieth of what the rule was written to protect.

**AND THE THIRD ONE WAS KILLED, exit 137, taking the session's worker process
with it.** 16:26, the patience=0.990 rung. The container came back, the
checkout survived, and the solve left nothing but a partial
`calibration_state.dat` that `run_one_point.sh` would have removed at line 595
had it reached the end. So the score on authorised coordinator solves is **2
landed, 1 killed**, and the reason the original rule gives -- this is the
container that gets restarted -- is not hypothetical. It happened within the
hour.

That does not withdraw the authorisation, which is the author's. It sets the
price: a coordinator solve is a five-minute bet that loses about a third of the
time and takes the trigger loop down with it when it does. Spend it on a
measurement that unblocks the search and cannot wait, never on a rung a worker
could carry, and after any kill run step 0 of the firing sequence again and
check `git status` for a partial `.dat` left behind.

USE IT WHEN THE FLEET IS DEGRADED AND FOR THE MEASUREMENT THAT UNBLOCKS THE
SEARCH, not as the default. The reasons in the rule below have not stopped
being true -- this container holds the trigger loop and the conversation, and a
restart still loses whatever is running -- so a coordinator solve is a
deliberate five-minute bet placed on the one line that matters most, taken in
the FOREGROUND, never backgrounded. The original rule's failure was a
backgrounded solve, which is the part that must never come back.

Follow the same discipline demanded of a worker: `cat -n` the batch, read the
line off the screen, issue it VERBATIM in a separate call, no command
substitution.

**AND IT DIRTIES THE SHARED WORKING TREE, which a worker's own container
absorbs.** The first authorised solve left three tracked files modified:
`calibration_state.dat`, `B_SWEEP_GRID.txt` and `newborn_parent_share.dat`.
Checked before committing them, because two of the three are read back as warm
starts: `run_one_point.sh` line 575 deletes `calibration_state.dat` and its
distribution files at the head of EVERY run, and line 578 rewrites
`B_SWEEP_GRID.txt` from the vector, so neither can seed a later point. That is
what "cold" means in the standing rule and it is why the byproducts are safe to
commit rather than needing to be reverted.

Do not take that on trust after a change to `run_one_point.sh`. A coordinator
solve writes into the same directory the next gate run reads, so if that
deletion ever stops happening, a point measured here would seed the one after
it and the two would not be independent.

### NEVER RUN A SOLVE IN THE COORDINATOR'S OWN CONTAINER -- superseded above

Added 2 September 22:09. The coordinator started one arm of the h_1 bracket
locally with `run_in_background`, to save a worker slot. The container was
restarted twenty minutes later, the solve died with it, and it left NOTHING --
no point file, no partial, no log worth keeping. Twenty minutes of a
twenty-five minute solve, gone, and the only reason it was noticed at once is
that the harness prints a stopped-task notice.

The coordinator's container is the one that gets restarted, because it is the
one holding a long conversation. A worker's container is doing one thing and is
left alone. **Every solve goes to a worker, including the one it seems wasteful
to spend a slot on.** There are eight slots and a solve costs one; the coordinator
should be holding none of them.

The same restart is also why the coordinator must re-run step 0 of the firing
sequence after any restart notice: the checkout survives, but nothing running
does, and `CALIBRATION_ACTIVE` can be left behind by a supervisor that died
mid-write.

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


## A WORKER BRANCH NAME MUST NOT COLLIDE WITH AN OLD ONE

3 September, 04:37. A worker was briefed to `git checkout -b wip/drugfit2`, and
`origin/wip/drugfit2` already existed from an earlier session. Sweeping the live
branches for new points then turned up `point cb276aa100`, "solved in 11 min",
which read as the slow-solve anomaly recurring on a fresh run. It was nothing of
the kind: `MODEL be2ff73819`, `HANDOVER OK: 44 of 44 parameters` -- an old point
on an old model with a 44-name vector, sitting on a branch that happened to share
the name.

Two rules out of it, and the second is the general one:

- Name a worker branch after the BATCH AND THE ROUND, not after the block --
  `wip/drugfit-0431-a`, not `wip/drugfit2`. Check `git branch -r` before
  briefing if the name is at all plausible as an old one.
- **NEVER read a point without checking its `MODEL` stamp and its HANDOVER
  count.** A point from another model is not a measurement of this one, and it
  will not announce itself: it has the same file name shape, the same moment
  labels and a plausible solve time. `next_batch.py` filters on the model hash
  for exactly this reason; a hand sweep of branches does not.

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

## TAKE THE POINT FILE BY NAME. DO NOT MERGE A WORKER'S BRANCH.

Added 2 September 22:50. Four worker branches were merged into the coordinator's
branch to collect their points. Every one of them also carried
`code/calibration_state.dat` and one carried `code/B_SWEEP_GRID.txt` -- both
per-run scratch that every worker rewrites -- and both conflicted. Resolving one
of those conflicts with `git add -A code/` staged the conflicted file WITH ITS
MARKERS and committed them into `B_SWEEP_GRID.txt`, which the Fortran opens and
reads in B-sweep mode.

Collect a worker's result like this instead:

```
git fetch -q origin wip/<branch>
git checkout FETCH_HEAD -- code/points/<the point file>
git add code/points/<the point file>
```

Name the path. The point file is the entire deliverable; nothing else on a
worker's branch is wanted, and `git diff --diff-filter=A --name-only HEAD
FETCH_HEAD -- code/points/` lists exactly the files the worker ADDED, which is
not the same as the plain diff -- the plain diff also lists points that exist on
the coordinator's side and not the worker's, and those come back empty when read.

Brief the worker to commit only the named point file for the same reason.

**Never resolve a conflict with `git add -A`.** Stage the paths you have actually
looked at.

## THE COORDINATOR MUST NOT RETYPE A LINE EITHER

Added 2 September 23:33. The read-it-off-screen rule was written for workers and
the coordinator broke it itself. A pi_eu sign test was built off a point with
`value_of_life=34`, and the brief was typed out by hand with `value_of_life=42.0`
in it -- and then, worse, carried the sentence "use the line above EXACTLY as
written. Note value_of_life=42.0 in it", which would have made a worker preserve
the error on purpose. The arm would have differed from its base in TWO
coordinates and answered nothing.

Caught before the solve started; the session was archived and relaunched.

**A worker brief must not contain a hand-typed command line.** Commit the batch
file, then tell the worker to `cat -n` it and read its assigned line off the
screen -- the same rule the workers already follow, for the same reason. The
coordinator has no privileged accuracy.

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

**ON THE SEVEN NODE GRID, 3 September: 2 to 4 minutes, median 3.** Twenty-two
points, every one of them at `number_of_beta_types=2` and every one passing
16 of 16 invariants, so they are comparable runs and not short-circuited ones.
Cutting the productivity grid from seventeen nodes to seven is what bought it.
The `-O3` build that precedes the solve is 76 seconds, measured, and is NOT in
the "solved in N min" figure -- the script starts its clock after the build.

**Judge a run against 3 minutes, not against the numbers below.** On the night
of 3 September a control on this grid was still solving at 13 minutes, which
against the old figures looks ordinary and against the right one is more than
four times over. Reading it against the stale benchmark would have hidden it.

The older figures, kept because they are the benchmark for the seventeen node
grid and for a borrowing-ON economy:

Borrowing OFF, 4 cores: 13, 15, 16, 17 minutes across four points on
841e04b785. Borrowing ON adds seven negative grid points to BOTH the state loops
and the choice loops for every renter, so expect appreciably longer -- the 0.75
and 0.90 arms were still solving at 26 minutes.

DO NOT RESPAWN AN ARM BEFORE ITS PLAUSIBLE WINDOW HAS PASSED. Respawning at
minute 26 of a job that may legitimately take 40 burns a container and produces a
duplicate point with the same md5. Judge it against these numbers, not against
impatience.
## The patient type is barred from the negative grid (restrict_borrowing_to_impatient)

The author asked for it as a SPEED measure: the patient type discounts at
0.9998 against a gross borrowing rate of 1.055, so beta*R>1 for them and the
negative grid is a region their Euler equation points away from. The grid is
24 positive points plus 8 negative, so barring seven of them removes about a
fifth of the states AND a fifth of the choices from the patient pass -- roughly
(25/32)^2 of the value function cost on half the population.

It works because the two types are solved in SEPARATE SEQUENTIAL PASSES.
`renter_floor_by_age` is a module array read by every state loop, every choice
loop and every distribution loop, so `set_renter_floor` reading
`current_beta_type` at the top of a pass shrinks that pass alone. It is now
called FROM the pass loop; before this it ran once at the end of the last
type's accumulation, which was enough only while the floor did not depend on
the type.

TWO THINGS THAT WOULD HAVE BEEN WRONG:

- **The warm distribution carries mass the patient pass no longer visits.**
  From loop three onward `initialize_feasible_distribution` is skipped and the
  patient pass starts from the IMPATIENT pass's converged distribution.
  `distribution_guess` is the operative array -- the iteration zeroes
  `distribution_implied` every sweep and rebuilds it from the guess -- and
  `sum(distribution_guess)` feeds both the convergence distance and the Aitken
  step. Both it and `distribution_stationary` are now cleared over the negative
  region at the top of the patient pass. Safe because it is only the starting
  guess: the iteration runs to 6e-4 from whatever it is handed.

- **The borrowing-floor DIAG read a per-pass array.** It printed
  `financial_grid(renter_floor_by_age(1))`, which is the zero point during the
  patient pass, so the log would have said the borrowing floor was zero in an
  economy where borrowing was on. It reads `renter_array_floor` now, and a
  second line states whether the patient type is barred.

**IT IS A RESTRICTION ON THE CHOICE SET, NOT AN IDENTITY.** A patient household
young enough to face a rising income profile can want to borrow even when
beta*R>1. Whether it is free has to be MEASURED -- `restrict_borrowing_to_
impatient=0` against `=1`, same vector, SAME CONTAINER, which is what
`batch_patient_floor.txt` is. If the moments move by more than the within-
container floor of 1.21e-03 it is a model change and belongs with the author,
not a speed setting.

## A LONG BORROWING-ON SOLVE IS NOT A HANG, and here is why that was checked

The borrowing-ON arms ran past 50 minutes against a predicted 25-40, so the
obvious worry was an unbounded loop. It is not one:

- the stationary distribution loop is capped at `max_distribution_sweeps=200`
  and stops rather than spins, carrying on with the best distribution reached;
- `loop_count` advances once per value function solve, and every secant and
  bisection loop in the file carries a `loop_1<max_loop_count` guard.

So a slow ON solve is slow, not stuck. THE DIAGNOSTIC THAT SETTLES WHERE THE
TIME GOES is already printed: line 36134 reports `capped =` 1 or 0 for whether
the distribution hit its 200-sweep ceiling. Read that off the first ON point
that lands before theorising about the cause.

TWO ESTIMATES OF ON COST HAVE NOW BEEN WRONG, both mine, both too low. The
first assumed the choice loop widens with the grid; it does not, because the
warm start searches a +/-3 window that is independent of grid width. The second
therefore scaled only the state loop, at x1.28. Both ignored that a warm guess
is LEAST reliable exactly when the choice set has just been widened, and every
window miss falls back to a full unit-stride sweep of all 32 points -- and that
opening a borrowing margin may simply need more outer equilibrium iterations to
meet the rental and housing tolerances, which no grid ratio predicts.

DO NOT PUBLISH A THIRD ESTIMATE. Take the measured wall-clock off the first ON
point and put it here.

## NEVER `pkill -f` FROM THE COORDINATOR

Same trap as `pgrep -f`, which this file already warns about, and it bit anyway
on 2 September: `pkill -f "hftf"` matched the shell running the command, killed
that shell mid-script (exit 144), and killed the solver it was aimed at, which
came back as `hftf exit status 143` -- SIGTERM -- and a point file with
`NO MOMENTS BLOCK`. A stub was briefly read as a completed solve.

Two rules out of it:

- kill by PID, never by pattern, and read the PID out of the launch;
- **a point file is only a measurement if it has a MOMENTS block.** `solved in
  N min` is run_one_point's wall clock and is printed whether the binary
  finished or was shot. Check for the moments before quoting anything.

## MEASURED, 18:05: BORROWING ON COSTS THE SAME AS OFF. The grid was never it.

Per-age wall time, read off the logs rather than estimated:

    borrowing OFF   2.16, 2.76, 3.31 s/age
    borrowing ON    2.75 s/age        (fixed model, zero budget failures)

IDENTICAL. And the outer work matches too -- 3 value function passes either way,
98 distribution sweeps ON against 112 and 133 OFF. Widening a renter's grid from
25 points to 32 costs essentially nothing, because the choice loop searches a
+/-3 warm-start window that does not widen and the state loop is not where the
time is.

SO THE AUTHOR WAS RIGHT AND BOTH OF MY ESTIMATES WERE WRONG. They said a
borrowing-ON solve should be about 14-16 minutes rather than 25-40. It is: the
same 13-17 as OFF. The x1.64 and x1.28 grid ratios were both inventions.

The 44 to 55 minute runs were the broken budget check writing a gigabyte of
diagnostics, exactly as the section below says -- that claim was withdrawn too
early, at 36 minutes, on the strength of workers that had most likely cloned the
pre-fix source. It stands.

## THE SLOW BORROWING-ON SOLVES WERE THE BUG, NOT THE GRID

Worth stating plainly because two firings were spent estimating grid ratios that
were never the cause.

Borrowing-ON solves ran 44, 54 and 55+ minutes against 13-17 off, and the whole
of that gap is explained by the broken budget check. It printed TEN LINES PER
FAILING STATE, and with `include_homeownership=0` every household is a renter,
so it failed at every borrowing state: 87 MB of log in five minutes, which at 55
minutes is on the order of a gigabyte of text written by a solver that should
have been doing arithmetic.

So the honest account of the day's runtime is not that borrowing widens the grid
by a factor the arithmetic got wrong twice. It is that a diagnostic was firing a
quarter of a million times and nobody read the log until 16:45.

THE PREDICTION THIS MAKES, and it is worth checking against the first fixed ON
arm: with the check passing and the printing stopped, an ON solve should fall
back toward the grid estimate of roughly 15-20 minutes rather than 45+. If it
does not, there is a second cause and the grid arithmetic is still not it.

THE GENERAL RULE: when a run is unexpectedly slow, read its log before modelling
its cost. A log that is growing at megabytes per minute is telling you what is
wrong, and no amount of reasoning about loop bounds substitutes for looking.

## A 529 KILLS A WORKER BEFORE IT DOES ANYTHING, AND IT COMES IN CLUSTERS

Measured on 3 September. Eight workers were launched in three groups and five
were lost to `API Error: 529 Overloaded`, every one of them about four minutes
in, with `current_branches: null` and nothing attempted:

    13:29 launched 3  ->  all 3 dead at 13:33, 41k tokens used, no branch
    13:42 launched 3  ->  1 alive and solving; 2 dead at 13:46, 0 tokens
    13:43 launched 2  ->  both dead at 13:47, 41k tokens used, no branch

The pattern is what matters. **The failures arrive in tight clusters** -- three
inside one minute, then two, then two -- so a group launched in the same instant
tends to die together, and a survivor from the same group proves the brief was
fine. This is not the background-brief failure and not a permission prompt: the
session reaches IDLE with `status_bucket: FAILED` and a `post_turn_summary`
naming the 529.

**Three things follow, and they are cheap.**

1. **BRIEF AGAINST IT EXPLICITLY.** A worker treats a 529 as terminal unless
   told otherwise, because it looks like an error rather than a wait. Every
   brief now says: a 529 is transient, wait and retry the SAME call, keep
   retrying, and do not end the turn until the solve has run or the retry has
   been tried at least five times.

2. **CONSOLIDATE RATHER THAN RESPAWN ONE-FOR-ONE.** Re-launching four dead
   lines as four fresh sessions exposes four more containers to the same
   cluster, and each pays a container start and a repository clone before it can
   fail. Two workers at two lines each halves the exposure; ENGINE.md already
   allows three lines per worker. Serial solve time is 3-5 minutes a line, which
   is cheaper than a second wave of losses.

3. **PUSH AFTER EACH LINE, NOT AFTER THE LAST.** A multi-line worker that
   batches its pushes loses every line if it dies on the final one. The brief
   must say push after each solve.

### THE BRIEF CANNOT FIX A 529, BECAUSE THE 529 ENDS THE TURN

Updated 14:05. The first version of this section told the brief to instruct a
retry. That was tried on four workers at 13:51-13:59 and **all four died
anyway**, at the same 3.5 to 4 minute mark, with no branch created.

The reason is mechanical and it is worth stating plainly: **the 529 terminates
the worker session's own turn.** The worker is not choosing to give up when it
sees an error -- it never gets another model call in which to act on the
instruction. Telling it to be persistent is telling it something it cannot hear.

Running total for 3 September: **nine of twelve workers lost**, every one of
them before its solve began.

**SO THE MITIGATION IS TO SHORTEN THE RUN-UP, NOT TO TOUGHEN THE BRIEF.** The
danger window is the interval between launch and the first `run_one_point.sh`
call, because that is when the worker is making model calls. Once the solver is
running in the foreground the worker makes NO API calls for three to five
minutes and the window has passed. Every turn spent before the solve is
exposure.

That has one concrete consequence for the brief, and it reverses standing
advice in this file: **a one-task worker should NOT be told to read ENGINE.md
first.** This file is 47 KB and the dead workers show 41k tokens of context
used -- almost all of it this document -- consumed in the minutes they then
died in. Inline the three or four constraints the line actually needs (verbatim
line, no command substitution, foreground, no edits under `code/` mid-solve,
the branch name) and tell the worker to start the first solve on its first tool
call region. Reserve "read ENGINE.md" for a worker doing something structural.

**AND PUSH AFTER EVERY LINE, WHICH MATTERS MORE ON A CONSOLIDATED WORKER.** A
worker carrying three lines that batches its pushes loses all three to a 529 on
the last one.

**BUT A PUSH IS ITSELF A TURN, AND THAT CUTS AGAINST CONSOLIDATION.** Measured
at 14:16: the minimal-brief worker got much further than any of the others --
it created its branch, spent 62k tokens and ran for twelve minutes, so it
almost certainly completed one or two solves -- and then died with NOTHING on
origin. Twelve minutes bought zero points. Its two siblings died at the usual
3.5 minutes with zero tokens, before starting.

The lesson is that turn COUNT is the exposure, not elapsed time, and a
consolidated worker needs a turn between every solve and every push. So at a
high 529 rate the right shape is the opposite of consolidation:

**ONE LINE PER WORKER, THREE TOOL CALLS TOTAL.** Checkout-and-`cat -n` in one
call, the solve in the second, `add && commit && push` chained in the third.
That is the minimum number of model turns in which a measurement can be taken
and landed. Consolidation is for when the fleet is healthy; when it is not, run
one line per container and accept the extra containers.

Running total for 3 September: **seventeen of twenty-one workers lost.**

**AND ONLY THE FIRST-LAUNCHED WORKER OF A GROUP HAS EVER SURVIVED.** The launch
record for the day:

    launch group  times (s)               outcome
    13:29 x3      13:28:59 / :05 / :12    all died
    13:42 x3      13:42:44 / :53 / :00    FIRST survived, other two died
    13:43 x2      13:43:57 / 13:44:09     both died
    13:51 x2      13:51:44 / 13:52:06     both died
    13:58 x2      13:58:58 / 13:59:17     both died
    14:04 x2      14:04:37 / :46          both died
    14:20 x3      14:20:33 / :38 / :42    all died
    14:26 x3      14:26:37 / :43 / :47    FIRST survived, other two died

**0 of 13 non-first workers survived; 2 of 8 first-launched did.** It looked
worth acting on, and one worker was launched ALONE at 14:35 to test it.

**IT DIED TOO, at 14:41, 529, no solve.** So the hypothesis is FALSIFIED and
this paragraph is kept only so that nobody spends another firing on it. Being
launched first is neither necessary nor sufficient; the 529s are close to
indiscriminate and the apparent pattern was eight groups' worth of noise. The
honest reading of the whole record is a flat per-worker survival rate of about
one in five, roughly independent across workers.

**WHICH MEANS LAUNCH THE FLEET, NOT ONE.** Under independence at p roughly 0.2,
three workers land about 0.5 measurements and one lands 0.2. Deliberately
launching one was the wrong inference and it cost a firing. The author's
standing instruction -- run the whole fleet, do not be timid with it -- is also
the arithmetically correct policy at any per-worker rate, because the failures
do not compete with each other.

What DOES still hold from this section is everything about the shape of the
brief: three tool calls, no ENGINE.md read, push chained onto the commit. That
is about the exposure of a single worker and is unaffected.

Do not read this as a reason to be timid when the fleet is healthy. The author's
instruction is to run the whole fleet, and eight parallel workers is the right
shape the moment 529s stop arriving. This is a rule for a degraded API, and the
test of whether it still applies is the session record, not memory.

**AND CHECK THE SESSION RECORD, NOT ONLY THE BRANCH LIST.** `git ls-remote`
cannot distinguish "still solving" from "died eight minutes ago", and at this
cadence that is the difference between waiting and losing a firing. `mine: true`
on the session list gives `status_bucket`, `current_branches` and the
`post_turn_summary` that names the cause. A branch that is absent while its
session reads FAILED is a line to relaunch now, not a line in flight.
