#!/usr/bin/env python3
"""The Phase 1 comparison table: each counterfactual against the benchmark.

    python3 code/compare_experiments.py                     # reads experiment_index.txt
    python3 code/compare_experiments.py point_a.txt point_b.txt

WHY THIS EXISTS RATHER THAN THE MODEL'S OWN COMPARISON. is_counterfactual turns
on use_old_results and a file_number naming block that writes counter_VTE_TF and
friends, and using it would mean converting is_counterfactual and the parameters
derived from it -- use_old_results and solve_transition_dynamics both key off it
at 1622 and 1769 -- from compile-time constants into variables. Comparing point
files instead needs no such change and keeps every counterfactual inside the
md5-tagged archive the calibration already uses.

IT REPORTS LEVELS AND DIFFERENCES, NOT GAPS AGAINST TARGETS. A counterfactual has
no target: the benchmark is calibrated and the experiment is whatever the model
says happens. Printing a "gap" for a counterfactual would invite reading the
benchmark's targets as if they still applied.
"""
import importlib.util, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("ts", os.path.join(HERE, "three_step.py"))
ts = importlib.util.module_from_spec(spec); spec.loader.exec_module(ts)

# The rows the paper's experiment table needs. Housing and disorder first, then
# the fiscal cost, then the welfare-relevant levels.
ROWS = ['h_1', 'h_age1', 'b', 'lambda_d', 'sud_homeless', 'emp_homeless',
        'tau_u', 'lambda_m', 'theta', 'pi_V', 'y_u', 'beta', 'aleph']


def moments(path):
    got = ts.parse(path)
    if not got:
        return None, None
    d = [x for x in got if isinstance(x, dict)]
    try:
        vec = next(x for x in d if 'utility_cost_of_treatment' in x)
        mom = next(x for x in d if 'tau_u' in x)
    except StopIteration:
        return None, None
    return vec, mom


def switches(vec):
    return (vec.get('probability_of_voucher_benchmark_used'),
            vec.get('increased_prob_of_voucher_if_homeless_and_addicted'),
            vec.get('voucher_conditional_on_clean'))


def main():
    idx = os.path.join(HERE, 'experiment_index.txt')
    runs = []
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            p = a if os.path.exists(a) else os.path.join(HERE, 'points', a)
            runs.append((os.path.basename(p), p))
    elif os.path.exists(idx):
        for line in open(idx):
            f = line.split()
            if len(f) >= 2:
                runs.append((f[0], os.path.join(HERE, 'points', f[1] + '.txt')))
    if not runs:
        print("nothing to compare: no arguments and no code/experiment_index.txt")
        return 1

    loaded = []
    for name, path in runs:
        if not os.path.exists(path):
            print("missing: %s (%s)" % (name, path)); continue
        vec, mom = moments(path)
        if mom is None:
            print("unparseable: %s" % name); continue
        loaded.append((name, vec, mom))
    if not loaded:
        return 1

    base_name, base_vec, base_mom = loaded[0]
    print("baseline for differences: %s" % base_name)
    print()
    print("switches (voucher rate / preferential access / conditional on clean):")
    for name, vec, _ in loaded:
        pv, ip, vc = switches(vec)
        print("  %-18s %-10s %-6s %s" % (name,
              ('%.4g' % pv) if pv is not None else '?',
              ('%g' % ip) if ip is not None else '?',
              ('%g' % vc) if vc is not None else '?'))
    print()

    head = "%-14s" % "moment" + "".join("%14s" % n[:13] for n, _, _ in loaded)
    print(head); print("-" * len(head))
    for m in ROWS:
        if not any(m in mom for _, _, mom in loaded):
            continue
        line = "%-14s" % m
        for _, _, mom in loaded:
            line += "%14s" % (("%.5g" % mom[m]) if m in mom else "--")
        print(line)
        if len(loaded) > 1 and m in base_mom and base_mom[m]:
            d = "%-14s" % "   vs base %"
            for _, _, mom in loaded:
                d += "%14s" % (("%+.1f" % (100*(mom[m]-base_mom[m])/abs(base_mom[m])))
                               if m in mom else "--")
            print(d)
    return 0


if __name__ == '__main__':
    sys.exit(main())
