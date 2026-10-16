"""The omega_c = 0.686 sensitivity's gain split as Table tab:whogains splits the paper's (12 October, the author on the
footnote's childhood/adult split: "break it down by externalities and non-externalities").

welfare_nok.parts needs each arm's value at 26 by entry node, which the sensitivity's first arms did not write, so the two
arms were re-solved for it (code/omega_nishiyama/remote_nish_nodes.sh -> results/omega_nishiyama/nodes/{null,tf}); they
reproduce the sensitivity (CEV 5.37 against the first arms' 5.36). The entry nodes are weighted by the paper's newborn
run's masses (results/transition_2c/newborn/shares.txt), the only ones printed, NORMALISED: they sum to 1 - 4e-5, which
alone put the by-node average 0.05 utils off the null arm's logged value at 26. Normalised, they reproduce it to 0.04
utils, while scaling the penalised-parent class by 0.8 or 1.2, or tilting the masses by 2 percent a node, misses it by
0.4 to 2.3 utils: the sensitivity's newborns are distributed over the nodes as the benchmark's are.

usage: python3 code/paper/export_nish_parts.py   -> x_nish_ext* names merged into code/paper/results_numbers.json
(export_results.py rewrites that file whole, so run this after it.)"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import welfare_nok as w

OUT_JSON = os.path.join(HERE, 'results_numbers.json')
N = os.path.join(ROOT, 'results', 'omega_nishiyama_Cu', 'cf')   # rule C, the corrected Housing First (16 October): cf/ carries the by-node values for both arms
BENCH = os.path.join(ROOT, 'results', 'omega_nishiyama_2c', 'bench_0.686_b0.004510373_ku1.0')

if __name__ == '__main__':
    B = w.Bench(BENCH)
    m = w.masses()
    s = sum(m.values())
    m = {k: v / s for k, v in m.items()}
    r = w.parts(os.path.join(N, 'tf'), os.path.join(N, 'tf'), os.path.join(N, 'null'), os.path.join(N, 'null'),
                bench=B, m=m)
    p = r['pts']
    d = json.load(open(OUT_JSON))
    # the re-solved arms must be the sensitivity the footnote reports
    assert abs(p['tot'] - float(d['x_nish_cev'])) < 0.02, (p['tot'], d['x_nish_cev'])
    out = {
        'x_nish_ext_cev': f"{p['ext']:.2f}",
        'x_nish_rest_cev': f"{p['tot'] - p['ext']:.2f}",
        'x_nish_cnt_cev': f"{p['cnt']:.2f}",
        'x_nish_own_cev': f"{p['own']:.2f}",
        'x_nish_extsh': f"{p['ext_share']:.0f}",
    }
    # the footnote says a smaller share is an externality at this weight because the parent counts more of the child's
    # loss: both must hold against the benchmark's column
    assert p['ext_share'] < float(d['x_wd_extsh_tf']) and p['cnt'] > float(d['x_wd_cnt_tf']), (p, d['x_wd_extsh_tf'])
    d.update(out)
    json.dump(d, open(OUT_JSON, 'w'), indent=1, sort_keys=True)
    for k, v in sorted(out.items()):
        print(f'  {k} = {v}')
