#!/usr/bin/env python3
"""Who is better off under Treatment First, household by household, from the two
steady states' own value functions (no new computation in Fortran).

    python3 value_shares.py --tf <TF arm dir> --null <no-policy arm dir> [--tag counter_arm]
                            [--tf-tag T] [--null-tag T] [--rtol 1e-6] [--atol 1e-3 1e-2] [--json out]

For every state s = (age, assets, employment/SMI/SUD index, productivity, housing,
voucher) with mass in the NO-POLICY stationary distribution, compares V_TF(s) with
V_null(s) (value_function1<tag>.dat, the household's own value, which already contains
the parent's altruistic term for a child at home). A household is

    better  if  V_TF - V_null >  tol,   worse  if  < -tol,   unchanged  otherwise,

with tol = rtol*|V_null| (default rtol 1e-6, the coordinator's rule) and, for scale,
fixed absolute tolerances in utils. Shares are weighted by the no-policy distribution.

Groups: households WITH a SUD now (unemployment_index > threshold_addiction_index) at
ages 26-50 (model ages 1-25, the child-at-home window) and at all ages; all households
at ages 26-50 and at all ages; and age-26 households (model age 1, the parents of
newborns, all clean by construction).
"""
import argparse, json, os, sys
import numpy as np

# cf_fix2's renter arrays: (t=1, age 1..life_span+1, fin, u, e, h, v), Fortran order
DIMS = dict(nf=25, nu=18, ne=26, nh=4, nv=3, n_smi=2, J_K=25, life_span=60)


def read(path):
    if not os.path.exists(path):
        sys.exit("GUARD: %s missing" % path)
    x = np.fromfile(path, sep=" ")
    return x


def shape(x, d):
    slab = d["nf"] * d["nu"] * d["ne"] * d["nh"] * d["nv"]
    if x.size % slab:
        sys.exit("GUARD: %d values is not a whole number of %d-cell age slices" % (x.size, slab))
    na = x.size // slab
    if na != d["life_span"] + 1:
        sys.exit("GUARD: %d ages in the file, expected %d" % (na, d["life_span"] + 1))
    # reverse the Fortran order: v, h, e, u, fin, age (fastest last in C)
    return x.reshape((d["nv"], d["nh"], d["ne"], d["nu"], d["nf"], na))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tf", required=True)
    ap.add_argument("--null", required=True)
    ap.add_argument("--tag", default="counter_arm")
    ap.add_argument("--tf-tag", default=None)
    ap.add_argument("--null-tag", default=None)
    ap.add_argument("--rtol", type=float, default=1e-6)
    ap.add_argument("--atol", type=float, nargs="*", default=[1e-3, 1e-2])
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    d = DIMS
    tt, nt = a.tf_tag or a.tag, a.null_tag or a.tag

    vt = shape(read(os.path.join(a.tf, "value_function1%s.dat" % tt)), d)
    vn = shape(read(os.path.join(a.null, "value_function1%s.dat" % nt)), d)
    m = shape(read(os.path.join(a.null, "distribution_stationary1%s.dat" % nt)), d)

    age = np.arange(1, d["life_span"] + 2)[None, None, None, None, None, :]
    u = np.arange(1, d["nu"] + 1)[None, None, None, :, None, None]
    sud = ((u - 1) // (2 * 3 * d["n_smi"])) == 1
    ever = np.minimum((u - 1) // (3 * d["n_smi"]), 1) == 1
    pos = m > 0
    bad = pos & ((vt <= -1e9) | (vn <= -1e9) | ~np.isfinite(vt) | ~np.isfinite(vn))
    if bad.any():
        print("WARNING: %d massed cells (mass %.3g) lack a value in one arm; they are left out" % (bad.sum(), m[bad].sum()))
    ok = pos & ~bad
    dv = np.where(ok, vt - vn, 0.0)

    groups = [
        ("SUD now, ages 26-50", ok & sud & (age <= d["J_K"])),
        ("SUD now, all ages", ok & sud & (age <= d["life_span"])),
        ("ever had a SUD, ages 26-50", ok & ever & (age <= d["J_K"])),
        ("all households, ages 26-50", ok & (age <= d["J_K"])),
        ("all households, all ages", ok & (age <= d["life_span"])),
        ("age 26 households (model age 1)", ok & (age == 1)),
    ]
    tols = [("rel %.0e" % a.rtol, a.rtol * np.abs(vn))] + [("abs %.0e" % t, np.full(vn.shape, t)) for t in a.atol]

    print("TF   : %s (value_function1%s.dat)" % (a.tf, tt))
    print("null : %s (value_function1%s.dat, weights distribution_stationary1%s.dat)" % (a.null, nt, nt))
    out = {}
    print("\n%-34s %10s %9s | %-9s %9s %9s %9s | %11s %11s" % ("group", "mass", "V_TF>V_n", "tolerance", "better",
                                                               "unchanged", "worse", "mean dV", "mean dV/|V|"))
    for name, g in groups:
        w = np.where(g, m, 0.0)
        tot = w.sum()
        if tot <= 0:
            print("%-34s %10.6f  (no mass)" % (name, 0.0))
            continue
        strict = w[dv > 0].sum() / tot
        mean = (w * dv).sum() / tot
        rel = (w * np.where(g, dv / np.maximum(np.abs(vn), 1e-300), 0)).sum() / tot
        out[name] = dict(mass=float(tot), strictly_better=float(strict), mean_dV=float(mean), mean_rel_dV=float(rel))
        for k, (tn, tv) in enumerate(tols):
            b = w[(dv > tv)].sum() / tot
            wo = w[(dv < -tv)].sum() / tot
            un = max(0.0, 1 - b - wo)
            out[name][tn] = dict(better=float(b), unchanged=float(un), worse=float(wo))
            if k == 0:
                print("%-34s %10.6f %9.4f | %-9s %9.4f %9.4f %9.4f | %11.5f %11.3e" % (name, tot, strict, tn, b, un, wo, mean, rel))
            else:
                print("%-34s %10s %9s | %-9s %9.4f %9.4f %9.4f |" % ("", "", "", tn, b, un, wo))
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
        print("\nwrote", a.json)


if __name__ == "__main__":
    main()
