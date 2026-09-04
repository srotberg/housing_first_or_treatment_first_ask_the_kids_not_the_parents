"""The night's staircase: seed a stage, search it, promote, repeat.

*"so start stage 2....once it converges move to stage 3"* and *"do it
automatically yourself and work on it all night"* -- the author, 4 September.

STAGES ARE SIZED BY DIMENSION, not by identification. nelder_test.py passes 8-dim
Rosenbrock at 4.6e-14 and FAILS 20-dim at 0.187 with three thousand evaluations,
so Nelder-Mead is competent at seven or twelve instruments and not at twenty.
Stage 1 is the seven already inside ten per cent, stage 2 adds the five the author
named, stage 3 the rest.

A STAGE ENDS TWO WAYS AND BOTH PROMOTE.
  converged -- every moment in scope inside ten per cent, the author's rule;
  stalled   -- STALL quiet evaluations, and then only after RESTARTS attempts
               from a NEW LOCATION, each further away than the last.

ESCAPING A LOCAL MINIMUM. Twenty evaluations with no new best is treated as a
local minimum rather than as slow progress, and the answer is to move the anchor
and rebuild the simplex somewhere else: 25 per cent of each instrument's value on
the first restart, 50 on the second, 75 on the third. A restart cannot lose
ground, because the incumbent is whatever the ARCHIVE's best is and the archive
keeps every point ever solved.
Which of the two happened is written to the trace, because "promoted" without
saying why would hide a stage that never worked.

Each stage reseeds from the CURRENT BEST on the live economy, so the work of the
earlier stages is carried forward rather than restarted.

    python3 code/stage_night.py
"""
import json, os, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

STALL    = 20     # quiet evaluations before the simplex is moved somewhere else
RESTARTS = 3      # restarts from a new location before the stage is given up on
BAND    = 0.10    # the author's rule: inside ten per cent
LOG     = os.path.join(HERE, 'stage_night.log')
BRANCH  = 'claude/two-period-addiction-hazard-d7gb61'
# The best vector on the economy immediately before the current one. Used only
# when a model change has emptied the archive. 2f138e4fa0 is stage 2's best at
# SSR 0.3195, eight of twelve moments inside ten per cent.
FALLBACK_ANCHOR = 'point_2f138e4fa0.txt'


def say(m):
    with open(LOG, 'a') as f:
        f.write(f'{time.strftime("%H:%M:%S")}  {m}\n')
    print(m, flush=True)


def sh(cmd, quiet=True):
    return subprocess.run(cmd, shell=True, cwd=ROOT,
                          stdout=subprocess.DEVNULL if quiet else None,
                          stderr=subprocess.DEVNULL if quiet else None)


def push(stage):
    sh('git add -A code/points code/.nm_state.json code/nm_trace.txt '
       'code/batch_nm.txt code/nm_stage.txt code/stage_night.log '
       'code/nm_run.log code/calibration_state.dat code/B_SWEEP_GRID.txt '
       'code/batch_stage*_seed.txt')
    sh(f'git commit -q -m "Stage {stage}, {time.strftime("%H:%M")} UTC\n\n'
       f'Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>\n'
       f'Claude-Session: https://claude.ai/code/session_01WpmVwzkbKX7RRP8t9yBCLv"')
    sh(f'git pull --rebase -q origin {BRANCH}')
    sh(f'git push -q origin {BRANCH}')


def fresh():
    for m in ('newton', 'next_batch', 'nelder', 'gaps', 'model_hash'):
        sys.modules.pop(m, None)
    import newton as N, next_batch as NB, nelder as NM
    NB._apply_process_mapping()
    return N, NB, NM


def scope(stage):
    N, NB, NM = fresh()
    inst, _ = NM.instruments_all(N, NB, stage)
    return N, NB, NM, inst, [p for p, _ in inst], [m for _, m in inst]


def runner_default(name):
    """run_one_point.sh's own default for a parameter, as a string."""
    txt = open(os.path.join(HERE, 'run_one_point.sh'), errors='replace').read()
    m = re.search(r'\[' + re.escape(name) + r'\]=\s*([0-9.eE+-]+)', txt)
    return m.group(1) if m else '0'


def seed(stage, jitter=0.0):
    """Solve the anchor and one displacement per instrument of this stage.

    jitter moves the ANCHOR somewhere else before building the simplex, which is
    the author's instruction of 4 September: *"if you see that the algortihm gets
    stuck for 20 iterations, you should consider moving the initial simplex to a
    different location.... and redo.... because you might be in a local min"*.

    A restart cannot lose ground: the incumbent is whatever the ARCHIVE's best
    is, and the archive keeps every point ever solved, so a restart that lands
    somewhere worse is simply a stage that reports the old best again.
    """
    N, NB, NM, inst, names, keys = scope(stage)
    A = N.archive()
    if A:
        _, tag, _, _ = N.best(A, keys)
        base = dict(A[tag][0])
    else:
        # THE FALLBACK ANCHOR IS THE BEST VECTOR FROM THE ECONOMY JUST LEFT,
        # not a fixed name from hours ago. A model change empties the archive,
        # and this branch is the only thing that decides where the next economy
        # starts; pointing it at a stale point throws away every stage that has
        # run since. FALLBACK_ANCHOR is updated whenever the model changes.
        t = open(os.path.join(HERE, 'points', FALLBACK_ANCHOR),
                 errors='replace').read()
        base = dict(kv.split('=', 1) for kv in
                    re.search(r'^VECTOR (.*)$', t, re.M).group(1).split()
                    if '=' in kv)
        base['max_age_to_choose_homelessness'] = '59'
    if jitter:
        import random
        rng = random.Random()
        for p in names:
            lo, hi = NB.BOUNDS[p]; x = float(base[p])
            f = 1.0 + rng.uniform(-jitter, jitter)
            base[p] = f'{min(max(x * f if abs(x) > 1e-12 else x + jitter * (hi - lo), lo), hi):.8g}'
        say(f'  RESTART: anchor moved by up to {jitter:.0%} on each instrument')
    # AN ANCHOR CAN PREDATE AN INSTRUMENT. point_2f138e4fa0 was solved before
    # rr_homeless_old_level existed, so its VECTOR line has no such key and
    # float(base[p]) raised KeyError and killed the run. Any instrument missing
    # from the anchor takes run_one_point.sh's own default, which is the value
    # the model would have used anyway.
    for p_ in names:
        lo, hi = NB.BOUNDS[p_]
        if p_ not in base:
            base[p_] = runner_default(p_)
            say(f'  anchor predates {p_}; taking the runner default '
                f'{base[p_]}')
        # AN ANCHOR COORDINATE OUTSIDE ITS OWN BOUNDS IS ALWAYS A BUG, and it is
        # silent: to_u maps it to a negative u, the simplex clips it to zero, and
        # the search starts at the BOUND rather than where the anchor said. It
        # happened within minutes of rr_homeless_old_level existing --
        # run_one_point's default was still 0, meaning "off", while its bounds
        # start at 1.0, so twenty of twenty-one seed vertices carried 0 and the
        # search would have jumped them to 1.0, which is NO excess mortality for
        # the old: the opposite of what the parameter was added to do.
        if not (lo <= float(base[p_]) <= hi):
            was = base[p_]
            base[p_] = runner_default(p_)
            if not (lo <= float(base[p_]) <= hi):
                base[p_] = f'{min(max(float(was), lo), hi):.8g}'
            say(f'  anchor has {p_}={was}, outside {lo}..{hi}; '
                f'using {base[p_]}')
    lines = ['bash code/run_one_point.sh ' +
             ' '.join(f'{k}={base[k]}' for k in sorted(base))]
    for p in names:
        lo, hi = NB.BOUNDS[p]; x = float(base[p])
        d = 0.10 * abs(x) if abs(x) > 1e-12 else 0.10 * max(abs(hi), 1e-6)
        xn = min(max(x + d, lo), hi)
        if abs(xn - x) < 1e-12:
            xn = min(max(x - d, lo), hi)
        v = dict(base); v[p] = f'{xn:.8g}'
        lines.append('bash code/run_one_point.sh ' +
                     ' '.join(f'{k}={v[k]}' for k in sorted(v)))
    open(os.path.join(HERE, f'batch_stage{stage}_seed.txt'), 'w').write(
        '\n'.join(lines) + '\n')
    say(f'  seeding stage {stage}: {len(lines)} vertices')
    for i, l in enumerate(lines, 1):
        say(f'    vertex {i} of {len(lines)}')
        sh(l)
        push(stage)


def state():
    f = os.path.join(HERE, '.nm_state.json')
    return json.load(open(f)) if os.path.exists(f) else None


def converged(stage):
    """Every moment in this stage's scope inside the band, at the live best."""
    N, NB, NM, inst, names, keys = scope(stage)
    A = N.archive()
    if not A:
        return False, 0, len(keys)
    _, tag, _, mom = N.best(A, keys)
    r = N.residual(mom, keys)
    ins = sum(1 for x in r if abs(x) <= BAND)
    return ins == len(r), ins, len(r)


def main():
    # RESUME FROM WHERE THE LAST RUN GOT TO. main() used to start the staircase
    # from stage 1 every time, so the crash at 06:00 was answered by a restart
    # that redid stage 1 -- harmless, since its moments converge on sight, but it
    # threw away forty minutes of stage 2 and reseeded from scratch. nm_stage.txt
    # is written before each stage begins and is the resume point.
    try:
        start = int(open(os.path.join(HERE, 'nm_stage.txt')).read().strip())
    except Exception:
        start = 1
    say(f'starting at stage {start}')
    for stage in range(start, 4):
        open(os.path.join(HERE, 'nm_stage.txt'), 'w').write(f'{stage}\n')
        say(f'=== STAGE {stage} ===')
        seed(stage)
        sh('python3 code/nelder.py --init')
        best, quiet, restarts = None, 0, 0
        asks = 0
        while True:
            if sh('python3 code/nelder.py --ask').returncode != 0:
                # AN --ask REFUSAL IS NOT A CONVERGED STAGE. It used to break
                # this loop, which promoted the stage instantly: on the first
                # run all three stages went by in twenty-five seconds without a
                # single solve. A refusal means a stale pending trial or a
                # simplex that never seeded, so clear and re-init, and only give
                # up if it keeps refusing.
                asks += 1
                say(f'  stage {stage}: --ask refused ({asks}); re-initialising')
                sh('python3 code/nelder.py --init')
                if asks >= 5:
                    say(f'  stage {stage}: --ask refused five times; promoting')
                    break
                time.sleep(10)
                continue
            asks = 0
            sh('bash code/batch_nm.txt')
            sh('python3 code/nelder.py --tell')
            push(stage)
            st = state()
            if st:
                f = min(v['f'] for v in st['simplex'])
                if best is None or f < best - 1e-12:
                    best, quiet = f, 0
                    ok, ins, tot = converged(stage)
                    say(f'  stage {stage}: new best {f:.4f}, inside {ins}/{tot}')
                else:
                    quiet += 1
            ok, ins, tot = converged(stage)
            if ok:
                say(f'  stage {stage} CONVERGED: all {tot} moments inside '
                    f'{BAND:.0%}, best {best:.4f}')
                break
            if quiet >= STALL:
                if restarts < RESTARTS:
                    restarts += 1
                    say(f'  stage {stage} stuck for {STALL} evaluations at '
                        f'{ins}/{tot} inside {BAND:.0%}, best {best:.4f}; '
                        f'restart {restarts} of {RESTARTS} from a new location')
                    # ESCALATING, so successive restarts search further afield
                    # rather than retrying the same neighbourhood: 25, 50 then
                    # 75 per cent of each instrument's value. This is basin
                    # hopping in miniature, and it is the escape the author
                    # asked for -- "you need to have some algorithm to extract
                    # you from a local min when it seems like you hit one".
                    seed(stage, jitter=0.25 * restarts)
                    sh('python3 code/nelder.py --init')
                    quiet = 0
                    continue
                say(f'  stage {stage} STALLED after {RESTARTS} restarts: '
                    f'{ins}/{tot} inside {BAND:.0%}, best {best:.4f}. '
                    f'Promoting so the night is not held.')
                break
        push(stage)
    say('all three stages done')
    # Keep the last stage searching rather than leaving the machine idle.
    while True:
        if sh('python3 code/nelder.py --ask').returncode != 0:
            time.sleep(60); continue
        sh('bash code/batch_nm.txt')
        sh('python3 code/nelder.py --tell')
        push(3)


if __name__ == '__main__':
    sys.exit(main())
