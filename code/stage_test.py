"""FOUR WAYS TO SPEND THE SAME EVALUATIONS ON TWENTY-ONE PARAMETERS.

The author, 4 September: *"when we do the convergence in stages, that is slightly
different than converging on 21 parameters all at once"*, then *"first tighten
stage 1, then open only stage 2. after stage 2 is done, redo stage 1 holding stage
2 fixed... then go to stage 3, tighten it, and run back stage 1 and 2"*, and
*"so you do a ladder and tighten each time"*.

WHY THIS EXISTS. stage_scope() was CUMULATIVE, so stage 3 opened all twenty-one
instruments -- exactly the case nelder_test.py measures Nelder-Mead failing
(Rosenbrock 21-dim, 4.42 after 3000 evaluations, against 2.4e-10 on a 21-dim
quadratic bowl). The staircase did not avoid that problem, it only arrived at it
warm. Measured, same budget, same machine:

    ONE SHOT, all 21 open      3000 evals   4.42
    STAIRCASE 12 -> 16 -> 21   3000 evals   8.51     NEARLY TWICE AS BAD

So the warm start does not rescue twenty-one dimensions, and the staircase was
worse than doing nothing. The author's ladder is the alternative worth measuring,
and its point is that THE MAXIMUM DIMENSION EVER SEARCHED IS TWELVE.

Two forms of the ladder, and the difference matters more than the cycling:

  cycle_block  while a block is open the objective is only THAT BLOCK'S moments.
               This is what "open only stage 2" reads as literally, and it lets
               stage 2 wreck stage 1's moments for free because nothing is
               scoring them.
  cycle_full   the objective is ALWAYS all twenty-one moments; only the block of
               PARAMETERS allowed to move changes. Proper block coordinate
               descent: a block can no longer buy its own moments by ruining
               another's.

Nothing here touches the live run. stage_scope and stage_now are monkeypatched
rather than nm_stage.txt written, because the solver reads that file.
"""
import os, sys, tempfile

HERE = '/home/user/housing_first_or_treatment_first/code'
sys.path.insert(0, HERE)
import nelder_test as T

BLOCKS = (12, 4, 5)


def drive(NM, solve, iters):
    argv = sys.argv
    for _ in range(iters):
        sys.argv = ['nelder.py', '--ask']
        if NM.main() != 0:
            break
        line = open(NM.BATCH).read().strip()
        solve(dict(kv.split('=', 1) for kv in line.split()[1:]))
        sys.argv = ['nelder.py', '--tell']
        NM.main()
    sys.argv = argv


def experiment(mode, budget, label, cycles=3):
    K = sum(BLOCKS)
    T.K = K
    T.NAMES = [f'p{i}' for i in range(K)]
    T.KEYS = [f'm{i}' for i in range(K)]
    N, NB, arch, solve = T.make_fakes(T.rosen)
    sys.modules['newton'] = N
    sys.modules['next_batch'] = NB
    sys.modules.pop('nelder', None)
    import nelder as NM
    d = tempfile.mkdtemp()
    NM.STATE = os.path.join(d, 's.json')
    NM.BATCH = os.path.join(d, 'b.txt')
    NM.TRACE = os.path.join(d, 't.txt')

    cuts, a = [], 0
    for b in BLOCKS:
        cuts.append(T.KEYS[a:a + b]); a += b

    if mode == 'oneshot':
        phases = [set(T.KEYS)]
    elif mode == 'staircase':
        phases = [set().union(*cuts[:i + 1]) for i in range(len(cuts))]
    else:
        phases = [set(c) for c in cuts] * cycles

    box = [1]
    NM.stage_now = lambda: box[0]
    NM.stage_scope = lambda n: phases[n - 1]
    if mode == 'cycle_full':
        # THE OBJECTIVE STAYS WHOLE while only the open block may move.
        allk = list(T.KEYS)
        NM.ssr = lambda N_, mom, keys: sum(
            x * x for x in N_.residual(mom, allk))

    for i in range(K + 1):
        solve({p: f'{(0.4 if j == i - 1 else 0.0):.10g}'
               for j, p in enumerate(T.NAMES)})

    per = max(1, budget // len(phases))
    argv = sys.argv
    for s in range(1, len(phases) + 1):
        box[0] = s
        sys.argv = ['nelder.py', '--init']
        NM.main()
        drive(NM, solve, per)
    sys.argv = argv

    # SCORED ON ALL TWENTY-ONE, whatever was open when it was found. A method
    # that only ever scored a block cannot be graded on the block it liked.
    best = min(sum(x * x for x in N.residual(m, T.KEYS))
               for _, m in arch.values())
    print(f'  {label:<46} {budget:>5} evals   best {best:>12.6g}', flush=True)
    return best


def main():
    print('\n  Rosenbrock, 21 parameters, identical total budget,'
          ' everything scored on all 21\n')
    for budget in (900, 3000):
        base = experiment('oneshot', budget, 'ONE SHOT, all 21 open')
        experiment('staircase', budget, 'STAIRCASE 12 -> 16 -> 21 (cumulative)')
        for m, lab in (('cycle_block', 'LADDER, block-only objective'),
                       ('cycle_full', 'LADDER, full objective, 12/4/5 blocks')):
            v = experiment(m, budget, lab)
            print(f'  {"":46} {"":5}          vs one-shot = '
                  f'{v / base if base else float("nan"):.3g}')
        print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
