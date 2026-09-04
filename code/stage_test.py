"""DOES THE STAIRCASE ACTUALLY BEAT SOLVING ALL TWENTY-ONE AT ONCE?

The author, 4 September: *"but when we do the convergence in stages, that is
slightly different than converging on 21 parameters all at once"*. They are right,
and the point cuts both ways, which is why this exists.

stage_scope() is CUMULATIVE: stage 1 opens 12 instruments, stage 2 opens 16 and
stage 3 opens 21. So the staircase does not avoid the 21-dimensional problem that
nelder_test.py measures Nelder-Mead failing (Rosenbrock 21-dim, 4.42 after 3000
evaluations, against 2.4e-10 on a 21-dim quadratic bowl). It arrives at 21 with a
WARM START instead of a cold one, and the whole question is whether that is enough.

So: same objective, same machine, same total budget, one-shot against staged.
Nothing here touches the live run -- stage_now is monkeypatched rather than
nm_stage.txt written, because the solver reads that file.
"""
import json, os, sys, tempfile, types

HERE = '/home/user/housing_first_or_treatment_first/code'
sys.path.insert(0, HERE)
import nelder_test as T


def rosen(x):
    return T.rosen(x)


def drive(NM, arch, solve, iters):
    """--ask / --tell until the budget runs out or the machine refuses."""
    argv = sys.argv
    used = 0
    for _ in range(iters):
        sys.argv = ['nelder.py', '--ask']
        if NM.main() != 0:
            break
        line = open(NM.BATCH).read().strip()
        v = dict(kv.split('=', 1) for kv in line.split()[1:])
        solve(v)
        used += 1
        sys.argv = ['nelder.py', '--tell']
        NM.main()
    sys.argv = argv
    return used


def best_on(NM, N, NB, arch, keys):
    A = arch
    out = None
    for t, (v, m) in A.items():
        try:
            f = NM.ssr(N, m, keys)
        except Exception:
            continue
        if out is None or f < out[0]:
            out = (f, t)
    return out


def experiment(staged, budget, label):
    K = 21
    T.K = K
    T.NAMES = [f'p{i}' for i in range(K)]
    T.KEYS = [f'm{i}' for i in range(K)]
    N, NB, arch, solve = T.make_fakes(rosen)
    sys.modules['newton'] = N
    sys.modules['next_batch'] = NB
    sys.modules.pop('nelder', None)
    import nelder as NM
    d = tempfile.mkdtemp()
    NM.STATE = os.path.join(d, 's.json')
    NM.BATCH = os.path.join(d, 'b.txt')
    NM.TRACE = os.path.join(d, 't.txt')

    groups = ([T.KEYS[:12], T.KEYS[12:16], T.KEYS[16:]] if staged
              else [T.KEYS])
    NM.STAGE_MOMENTS = groups
    # THE LIVE nm_stage.txt IS NOT TOUCHED. The solver reads it.
    stage_box = [1]
    NM.stage_now = lambda: stage_box[0]

    # A starting simplex at x0 = 0, the same cold start nelder_test.py uses.
    for i in range(K + 1):
        solve({p: f'{(0.4 if j == i - 1 else 0.0):.10g}'
               for j, p in enumerate(T.NAMES)})

    per = budget // len(groups)
    argv = sys.argv
    for s in range(1, len(groups) + 1):
        stage_box[0] = s
        sys.argv = ['nelder.py', '--init']
        NM.main()
        drive(NM, arch, solve, per)
    sys.argv = argv
    f, t = best_on(NM, N, NB, arch, T.KEYS)
    print(f'  {label:<44} {budget:>5} evals   best {f:>12.6g}')
    return f


def main():
    print('\n  Rosenbrock, 21 instruments, identical total budget\n')
    for budget in (900, 3000):
        a = experiment(False, budget, 'ONE SHOT, all 21 open from the start')
        b = experiment(True, budget, 'STAGED 12 -> 16 -> 21, warm started')
        print(f'  {"":44} {"":5}          staged/one-shot = '
              f'{b / a if a else float("nan"):.3g}\n')
    return 0


if __name__ == '__main__':
    sys.exit(main())
