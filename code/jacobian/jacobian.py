"""jacobian.py -- THE CALIBRATION'S JACOBIAN FROM THE SAVED RUNS (11 November; Referee 1, comment 2(f)).

Reads results/jacobian/<KEY>/cf.log.gz, written by run_jacobian.sh: the corrected Housing First solved once with nothing
raised (KEY 'base') and once with each internally calibrated parameter raised by its step. For every parameter and
every targeted moment it computes the elasticity

    e = (m_raised / m_base - 1) / step,

the percent change in the moment for a one percent rise in the parameter, and writes

    results/jacobian/elasticities.csv   parameters in rows, moments in columns, in Table 3 and Table A1's order
    results/jacobian/summary.txt        each parameter's own-moment elasticity, its largest elasticity, and the rank and
                                        condition number of the square block (the twenty parameters with a moment)
    writing/figures/jacobian.{pdf,png}  the heat map

Each moment is read as the calibration tables read it (code/paper/calib_tables.py): the MOMENT and UNTARGETED lines of
the run's log, the aggregate drug spending share from its DIAG line, and the share of users with a SUD as lambda_d over b.
SIX PARAMETERS ARE READ FROM <KEY>_dat. The counterfactual binary's upload_vars re-reads beta, gamma, aleph, h_1, tau_l and
h_2 from the benchmark's saved files after the handover, so run_jacobian.sh's runs of those solved the benchmark again;
run_jacobian_dat.sh raises them in the file too, into results/jacobian/<KEY>_dat, and only those runs are used.

THE VOUCHER PROBABILITY'S RUN FAILS cf_arm_Cu.sh's voucher check by design: the check asks that the arm ran at the
benchmark's probability, and this run raises it. So for piV the check is redone here: every GUARD in the run must be that
one, and the probability the run printed last must be the raised one.

The parent's weight on its child has no moment here (its moment needs an omega_c = 0 twin of every run), so its row
shows how it moves the other moments only.

usage: python3 code/jacobian/jacobian.py [--no-figure | --partial]   (--partial draws the unsolved rows grey, into
       $JAC_PREVIEW_DIR/jacobian_partial.{pdf,png}, results/jacobian by default)
"""
import gzip
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
RES = os.path.join(ROOT, 'results', 'jacobian')
FIG = os.path.join(ROOT, 'writing', 'figures', 'jacobian')

# key, symbol, step, the moment it is calibrated to (label, how to read it), in Table 3 then Table A1 order
PARAMS = [
    ('theta',   r'$\theta$',            0.01,  ('Drug spending over income',        'diag_theta')),
    ('b',       r'$b$',                 0.01,  ('Drug use',                         'b total drug users')),
    ('pi_d',    r'$\pi_d$',             0.01,  ('Share of users with a SUD',        'share_sud')),
    ('kphid',   r'$\kappa_{\phi d}$',   0.01,  ('Income of users over average',     'y_u income of drug users')),
    ('aleph',   r'$\aleph$',            0.01,  ('Value of a statistical life',      'aleph value of life / income')),
    ('kued',    r'$\kappa^{ue}_{d}$',   0.01,  ('SUD share of the homeless',        'sud_homeless SUD share of the homeless')),
    ('h1',      r'$h_1$',               0.01,  ('Homelessness',                     'h_1 homelessness rate')),
    ('cmin',    r'$\underline{c}$',      0.01,  ('Food stamps over output',          'cbar food stamps / income')),
    ('piV',     r'$\pi_V$',             0.01,  ('Recipients over eligible',         'pi_V eligibles with a voucher')),
    ('T0',      r'$T_0$',               0.01,  ('Homeless aged 25 to 34',           'share of the homeless, band 1')),
    ('omega_m', r'$\omega_m$',          0.01,  ('SMI share of the population',      'p_m SMI population share')),
    ('kuem',    r'$\kappa^{ue}_{m}$',   0.01,  ('SMI share of the homeless',        'lambda_m SMI share of the homeless')),
    ('muH',     r'$\mu_H$',             0.01,  ('Abstinence, housed over homeless', 'mu_H recovery housed / homeless')),
    ('tauu',    r'$\bar\tau^{u}$',      0.01,  ('Treatment take-up',                'tau_u treatment take up')),
    ('omega_c', r'$\omega_c$',          0.01,  None),
    ('gamma',   r'$\gamma$',            0.01,  ('Housing over expenditure',         'gamma housing over expenditure')),
    ('beta',    r'$\beta$',             0.002, ('Wealth over output',               'beta wealth over output')),
    ('h2',      r'$h_2$',               0.01,  ('Renters paying over half',         'over half of income, all renters')),
    ('sigma',   r'$\sigma_\zeta$',      0.01,  ('Bottom half of earnings',          'sigma_y bottom half labour income share')),
    ('pieu',    r'$\bar\pi^{eu}$',      0.01,  ('Unemployment rate',                'pi_eu unemployment rate')),
    ('taul',    r'$\tau_\ell$',         0.01,  ('Average labour income tax',        'tau_l average labour income tax')),
]
MOMENTS = [p[3] for p in PARAMS if p[3] is not None]


DAT_KEYS = ('beta', 'gamma', 'aleph', 'h1', 'taul', 'h2')


def run_dir(key):
    return os.path.join(RES, key + '_dat' if key in DAT_KEYS else key)


def valid(key, log):
    """True when the run's check passed; for piV, when its only failure is the voucher check and it ran at the raised value."""
    chk = os.path.join(run_dir(key), 'check.txt')
    if not os.path.exists(chk):
        return False
    c = open(chk).read()
    if c.startswith('OK') and not c.startswith('OK-SKIP'):
        return True
    if key == 'h2':
        # run_jacobian_dat.sh looked for the handover echo as 'smallest rental' (its table's '_ for a space'), but the
        # binary prints 'HANDOVER smallest_rental:', so the read-back came up empty and the check said FAIL. The two other
        # read-backs it prints (the benchmark file and the value the last pass printed) are the raised value; so is the
        # echo under its real label. Accept the run when all three equal the value the check was looking for.
        m = re.match(r"FAIL h2_dat: handover read back '', file '(\S+)', last pass printed '(\S+)', not (\S+)", c)
        h = re.findall(r'HANDOVER smallest_rental:\s*\S+\s*->\s*(\S+)', log)
        if not (m and h):
            return False
        want = float(m.group(3))
        return all(abs(float(v) / want - 1) < 1e-9 for v in (m.group(1), m.group(2), h[-1])) and 'DIST_DONE' in log
    if key != 'piV' or 'GUARD FAIL: arm ran at voucher probability' not in c:
        return False
    h = re.findall(r'HANDOVER voucher probability:\s*\S+\s*->\s*(\S+)', log)
    p = re.findall(r'^\s*probability_of_voucher=\s*(\S+)', log, re.M)
    return bool(h and p and abs(float(p[-1]) / float(h[-1]) - 1) < 1e-9 and 'DIST_DONE' in log)


def read_moments(key):
    path = os.path.join(run_dir(key), 'cf.log.gz')
    if not os.path.exists(path):
        return None
    log = gzip.open(path, 'rt', errors='replace').read()
    if not valid(key, log):
        return None
    return parse(log)


def read_log(path):
    return parse(gzip.open(path, 'rt', errors='replace').read())


def parse(log):
    M = {}
    for l in log.splitlines():
        m = re.match(r'\s*(MOMENT|UNTARGETED)\s+(.*?)\s+model=\s*(\S+)', l)
        if m:
            M[re.sub(r'\s+', ' ', m.group(2).strip())] = float(m.group(3))   # the last block's value wins
    d = re.findall(r'drug share, sum spend / sum income\s*=\s*(\S+)', log)
    if d:
        M['diag_theta'] = float(d[-1])
    if 'b total drug users' in M and 'lambda_d disorder rate' in M:
        M['share_sud'] = M['lambda_d disorder rate'] / M['b total drug users']
    return M


def main():
    base = read_moments('base')
    if base is None:
        sys.exit('no finished base run in results/jacobian/base')
    missing = [lab for lab, k in MOMENTS if k not in base]
    if missing:
        sys.exit(f'the base run lacks these moments: {missing}')
    E, done = {}, []
    for key, sym, step, own in PARAMS:
        M = read_moments(key)
        if M is None:
            continue
        done.append(key)
        E[key] = [(M[k] / base[k] - 1) / step for lab, k in MOMENTS]
    # the table
    rows = ['parameter,' + ','.join(f'"{lab}"' for lab, k in MOMENTS)]
    for key, sym, step, own in PARAMS:
        if key in E:
            rows.append(key + ',' + ','.join(f'{v:.4f}' for v in E[key]))
    open(os.path.join(RES, 'elasticities.csv'), 'w').write('\n'.join(rows) + '\n')
    # the summary: own-moment elasticity, the largest one, and the square block's rank and conditioning
    out = [f'{len(done)} of {len(PARAMS)} parameters solved: {", ".join(done)}', '']
    labs = [lab for lab, k in MOMENTS]
    for key, sym, step, own in PARAMS:
        if key not in E:
            continue
        row = E[key]
        j = max(range(len(row)), key=lambda i: abs(row[i]))
        own_txt = 'no moment of its own' if own is None else f'own moment {row[labs.index(own[0])]:+.3f}'
        out.append(f'{key:8s} {own_txt:28s} largest {row[j]:+.3f} on {labs[j]}')
    sq = [k for k, s, st, own in PARAMS if own is not None and k in E]
    if len(sq) == len(MOMENTS):
        import numpy as np
        A = np.array([E[k] for k in sq])
        sv = np.linalg.svd(A, compute_uv=False)
        out += ['', f'square block ({len(sq)} parameters by {len(MOMENTS)} moments): rank {np.linalg.matrix_rank(A)}, '
                f'singular values {sv.max():.3g} to {sv.min():.3g}, condition number {sv.max() / sv.min():.3g}']
        own_largest = [k for k in sq if abs(E[k][sq.index(k)]) == max(abs(v) for v in E[k])]
        out.append(f'own moment is the largest in its row for {len(own_largest)} of {len(sq)}: {", ".join(own_largest)}')
        col_top = [k for j, k in enumerate(sq) if abs(A[j, j]) == np.abs(A[:, j]).max()]
        out.append(f'own parameter moves its moment the most (largest in its column) for {len(col_top)} of {len(sq)}: '
                   f'{", ".join(col_top)}')
        for j, k in enumerate(sq):
            if k not in col_top:
                i = int(np.abs(A[:, j]).argmax())
                out.append(f'    {labs[j]}: own {k} {A[j, j]:+.3f}, largest {sq[i]} {A[i, j]:+.3f}')
    # the noise floor: the void runs solved the benchmark again, so their distance from the base is numerical noise
    voids = [k for k in DAT_KEYS if os.path.exists(os.path.join(RES, k, 'VOID.txt'))
             and os.path.exists(os.path.join(RES, k, 'cf.log.gz'))]
    if voids:
        noise = []
        for k in voids:
            M = read_log(os.path.join(RES, k, 'cf.log.gz'))
            noise.append([abs(M[m] / base[m] - 1) for lab, m in MOMENTS])
        worst = [max(col) for col in zip(*noise)]
        j = max(range(len(worst)), key=lambda i: worst[i])
        out += ['', f'noise floor from {len(voids)} repeat solves of the benchmark ({", ".join(voids)}): largest relative '
                f'difference {worst[j]:.2e} ({labs[j]}), i.e. {worst[j] / 0.01:.3f} in elasticity units at a one percent step '
                f'and {worst[j] / 0.002:.3f} at the discount factor\'s 0.2 percent']
        if len(sq) == len(MOMENTS):
            # HOW MUCH THE NOISE CAN MOVE THE SMALLEST SINGULAR VALUE. Weyl's bound (the noise matrix's Frobenius norm,
            # every cell at its moment's worst repeat-solve difference) is far too loose here: it says 0.16 against a
            # smallest singular value of 0.004 with T0 and 0.06 without, and so calls both singular. Instead each row of
            # the noise matrix is drawn as one of the repeat solves' own error vectors, with a random sign, over that
            # row's step, which is what a perturbed run's error looks like; 2,000 draws give the 5 to 95 percent range of
            # the smallest singular value of A + noise. Done for the full block and without the parameter that loads
            # most on the weakest direction.
            import numpy as np
            step = {k: st for k, s, st, own in PARAMS}
            errs = np.array([[read_log(os.path.join(RES, k, 'cf.log.gz'))[m] / base[m] - 1 for lab, m in MOMENTS]
                             for k in voids])
            rng = np.random.default_rng(0)
            U, sv_all, _ = np.linalg.svd(A)
            weak = sq[int(np.abs(U[:, -1]).argmax())]
            for drop in ((), (weak,)):
                keys = [k for k in sq if k not in drop]
                cols = [jj for jj, k in enumerate(sq) if k not in drop]
                Ad = np.array([[E[k][jj] for jj in cols] for k in keys])
                Ud, sd, _ = np.linalg.svd(Ad)
                draws = [np.linalg.svd(Ad + np.array([errs[rng.integers(len(errs))][cols] * rng.choice([-1, 1]) / step[k]
                                                       for k in keys]), compute_uv=False)[-1] for t in range(2000)]
                u = Ud[:, -1]
                out.append(f'{"without " + drop[0] if drop else "all"} ({len(keys)} by {len(keys)}): smallest singular value '
                           f'{sd[-1]:.3g}, with the noise {np.percentile(draws, 5):.3g} to {np.percentile(draws, 95):.3g}; '
                           f'its direction ' + ', '.join(f'{keys[jj]} {u[jj]:+.2f}' for jj in np.argsort(-np.abs(u))[:4]))
    # h2 and T0 again at a larger step (run_jacobian_step.sh), to tell a flat own moment from a lumpy one
    for d in sorted(os.listdir(RES)):
        m = re.match(r'(\w+?)(?:_dat)?_s(\d+)$', d)
        if m and base is not None:
            k, big = m.group(1), int(m.group(2)) / 1000
            log_path = os.path.join(RES, d, 'cf.log.gz')
            chk = os.path.join(RES, d, 'check.txt')
            if os.path.exists(log_path) and os.path.exists(chk) and open(chk).read().startswith('OK'):
                M = read_log(log_path)
                own = [p[3] for p in PARAMS if p[0] == k][0]
                e_big = [(M[mm] / base[mm] - 1) / big for lab, mm in MOMENTS]
                jo = labs.index(own[0])
                out.append(f'{k} at a {100 * big:g} percent step: own moment {e_big[jo]:+.3f} (one percent: '
                           f'{E[k][jo]:+.3f}); ' + ', '.join(f'{labs[jj]} {e_big[jj]:+.2f}' for jj in
                                                            sorted(range(len(labs)), key=lambda i: -abs(e_big[i]))[:4]))
    open(os.path.join(RES, 'summary.txt'), 'w').write('\n'.join(out) + '\n')
    print('\n'.join(out))
    json.dump({'moments': labs, 'elasticities': E}, open(os.path.join(RES, 'elasticities.json'), 'w'), indent=1)
    if '--no-figure' not in sys.argv and len(done) == len(PARAMS):
        figure(E, labs)
    elif '--partial' in sys.argv:
        figure(E, labs, os.path.join(os.environ.get('JAC_PREVIEW_DIR', RES), 'jacobian_partial'))


def figure(E, labs, out=FIG):
    """The heat map. Colour is on a symmetric log scale, linear within +-0.1 (about eight times the repeat-solve noise),
    because the discount factor's row runs to about 200 while most cells are below 5: a linear scale either saturates
    that row or washes the rest out. Each cell prints its value when it is at least 0.05 in absolute value; the
    parameter's own moment is outlined. A parameter not yet solved is a grey row (a preview, with --partial)."""
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import SymLogNorm
    import numpy as np
    keys = [p[0] for p in PARAMS]
    syms = [p[1] for p in PARAMS]
    A = np.array([E[k] if k in E else [np.nan] * len(labs) for k in keys])
    vmax = 1.05 * np.nanmax(np.abs(A))
    norm = SymLogNorm(linthresh=0.1, linscale=0.6, vmin=-vmax, vmax=vmax, base=10)
    plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm'})
    cmap = matplotlib.colormaps['RdBu_r'].copy()
    cmap.set_bad('#d9d9d9')
    fig, ax = plt.subplots(figsize=(7.0, 7.3))   # printed at the letter's text width, 6.4 inches
    im = ax.imshow(np.ma.masked_invalid(A), cmap=cmap, norm=norm, aspect='auto')
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels(labs, rotation=60, ha='right', rotation_mode='anchor', fontsize=6.8)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(syms, fontsize=8.5)
    ax.set_xlabel('Targeted moment (in the order of the parameter it is matched to)', fontsize=7.5)
    ax.set_ylabel('Parameter raised', fontsize=7.5)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            v = A[i, j]
            if np.isfinite(v) and abs(v) >= 0.05:
                txt = f'{v:.0f}' if abs(v) >= 10 else (f'{v:.1f}' if abs(v) >= 1 else f'{v:.2f}')
                ax.text(j, i, txt.replace('-', '\N{MINUS SIGN}'), ha='center', va='center', fontsize=4.9,
                        color='white' if abs(norm(v) - 0.5) > 0.33 else '#1a1a1a')
    for i, p in enumerate(PARAMS):   # outline each parameter's own moment
        if p[3] is not None:
            j = labs.index(p[3][0])
            ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, edgecolor='black', linewidth=1.1))
    ax.set_xticks(np.arange(-.5, len(labs), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(keys), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=0.6)
    ax.tick_params(which='minor', length=0)
    ticks = [t for t in (-100, -10, -1, -0.1, 0, 0.1, 1, 10, 100) if abs(t) <= vmax]
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.015, ticks=ticks)
    cb.ax.set_yticklabels([f'{t:g}'.replace('-', '\N{MINUS SIGN}') for t in ticks], fontsize=6.5)
    cb.set_label('Percent change in the moment for a one percent rise in the parameter (log scale beyond 0.1)', fontsize=6.5)
    fig.tight_layout()
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out + '.pdf')
    fig.savefig(out + '.png', dpi=200)
    print('wrote', out + '.pdf')


if __name__ == '__main__':
    main()
