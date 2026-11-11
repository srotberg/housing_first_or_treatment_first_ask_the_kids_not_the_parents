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

usage: python3 code/jacobian/jacobian.py [--no-figure]
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
    open(os.path.join(RES, 'summary.txt'), 'w').write('\n'.join(out) + '\n')
    print('\n'.join(out))
    json.dump({'moments': labs, 'elasticities': E}, open(os.path.join(RES, 'elasticities.json'), 'w'), indent=1)
    if '--no-figure' not in sys.argv and len(done) == len(PARAMS):
        figure(E, labs)


def figure(E, labs):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    keys = [p[0] for p in PARAMS]
    syms = [p[1] for p in PARAMS]
    A = np.array([E[k] for k in keys])
    lim = np.percentile(np.abs(A), 95)
    plt.rcParams.update({'font.family': 'serif', 'mathtext.fontset': 'cm'})
    fig, ax = plt.subplots(figsize=(10, 8.2))
    im = ax.imshow(np.clip(A, -lim, lim), cmap='RdBu_r', vmin=-lim, vmax=lim, aspect='auto')
    ax.set_xticks(range(len(labs)))
    ax.set_xticklabels(labs, rotation=60, ha='right', fontsize=8)
    ax.set_yticks(range(len(keys)))
    ax.set_yticklabels(syms, fontsize=9)
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if abs(A[i, j]) >= 0.05:
                ax.text(j, i, f'{A[i, j]:.1f}' if abs(A[i, j]) >= 1 else f'{A[i, j]:.2f}', ha='center', va='center',
                        fontsize=5.5, color='white' if abs(A[i, j]) > 0.6 * lim else 'black')
    for i, p in enumerate(PARAMS):   # outline each parameter's own moment
        if p[3] is not None:
            j = labs.index(p[3][0])
            ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False, edgecolor='black', linewidth=1.3))
    ax.set_xticks(np.arange(-.5, len(labs), 1), minor=True)
    ax.set_yticks(np.arange(-.5, len(keys), 1), minor=True)
    ax.grid(which='minor', color='white', linewidth=0.6)
    ax.tick_params(which='minor', length=0)
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label('Percent change in the moment for a one percent rise in the parameter', fontsize=8)
    fig.tight_layout()
    os.makedirs(os.path.dirname(FIG), exist_ok=True)
    fig.savefig(FIG + '.pdf')
    fig.savefig(FIG + '.png', dpi=200)
    print('wrote', FIG + '.pdf')


if __name__ == '__main__':
    main()
