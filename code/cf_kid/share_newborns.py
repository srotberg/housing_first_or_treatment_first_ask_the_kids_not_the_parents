#!/usr/bin/env python3
"""Share of newborns better off under Treatment First than under Housing First.

    python3 share_newborns.py --tf <TF arm dir> --hf <HF arm dir> [--tag counter_arm]
                              [--tf-tag T] [--hf-tag T] [--tol 1e-3 1e-2] [--json out.json]

Each directory must hold what run_child_value.sh writes:
    child_value_at_birth<tag>.dat       W(1,s): the newborn's ex-ante lifetime value, by the
                                        state s of the parent it is born to (model age 1)
    child_value_at_birth_mass<tag>.dat  Phi_1(s)/M_1: the newborns' distribution over s
    child_value_summary<tag>.txt        the state-space dimensions and a node table

THE COMPARISON IS STATE BY STATE: a newborn born to a parent in state s is better off
under Treatment First when W_TF(1,s) - W_HF(1,s) > tol, worse off when it is < -tol,
and counted as indifferent otherwise. The shares are weighted by the HOUSING FIRST
newborn distribution Phi_1^HF -- the newborns the reform would fall on.

Every household enters the economy clean (no SUD, never had one), employed, with zero
assets, housed and without a voucher, so Phi_1 lives on 2 x 26 cells: SMI at birth or
not, times the parent's productivity node (13 nodes x 2 classes; class 1 = the parent
was itself born to a parent who ever had a SUD before it left home, the delta_d class).
"Newborns whose parent has a SUD" is therefore EMPTY at birth by construction; the
script reports it (as zero mass) and reports the class split, which is the parent's own
inherited penalty, beside it.
"""
import argparse, json, os, sys
import numpy as np

SENTINEL = -1e9  # cells outside the law of motion's domain carry -9999999999


def read_summary(path):
    d = {}
    nodes = {}
    for line in open(path):
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        if p[0] == "node_productivity_age1":
            nodes[int(p[1])] = (float(p[2]), float(p[3]))
        elif p[0] == "push_age":
            continue
        else:
            try:
                d[p[0]] = int(p[1])
            except ValueError:
                d[p[0]] = float(p[1])
    d["nodes"] = nodes
    return d


def read_col(path):
    return np.loadtxt(path, dtype=float)


def load(dirname, tag):
    s = read_summary(os.path.join(dirname, "child_value_summary%s.txt" % tag))
    w = read_col(os.path.join(dirname, "child_value_at_birth%s.dat" % tag))
    m = read_col(os.path.join(dirname, "child_value_at_birth_mass%s.dat" % tag))
    n = ((s["fin_hi"] - s["fin_lo"] + 1) * s["n_unemployment"] * s["n_employment"]
         * (s["housing_hi"] - s["housing_lo"] + 1) * (s["voucher_max"] + 1))
    if len(w) != n or len(m) != n:
        sys.exit("GUARD: %s: %d values of W and %d of Phi for a %d-cell age-1 slice" % (dirname, len(w), len(m), n))
    return s, w, m


def labels(s):
    """Decode the column-major flat index (financial fastest, then unemployment,
    employment, housing, voucher) into the parent's characteristics."""
    nf = s["fin_hi"] - s["fin_lo"] + 1
    nu, ne = s["n_unemployment"], s["n_employment"]
    nh = s["housing_hi"] - s["housing_lo"] + 1
    nv = s["voucher_max"] + 1
    nsmi, base = s["number_of_smi_states"], s["employment_base_size"]
    i = np.arange(nf * nu * ne * nh * nv)
    fin = i % nf + s["fin_lo"]
    u = (i // nf) % nu + 1
    e = (i // (nf * nu)) % ne + 1
    h = (i // (nf * nu * ne)) % nh + s["housing_lo"]
    v = i // (nf * nu * ne * nh)
    return dict(fin=fin, u=u, e=e, h=h, v=v,
                emp=(u - 1) % 3 + 1,
                smi=((u - 1) // 3) % nsmi,
                sud=(u - 1) // (2 * 3 * nsmi),
                ever=np.minimum((u - 1) // (3 * nsmi), 1),
                cls=(e - 1) // base,
                node=(e - 1) % base + 1)


def shares(diff, wgt, mask, tol):
    tot = wgt[mask].sum()
    if tot <= 0:
        return dict(mass=0.0, better=None, worse=None, same=None, mean_diff=None)
    d, g = diff[mask], wgt[mask]
    return dict(mass=float(tot),
                better=float(g[d > tol].sum() / tot),
                worse=float(g[d < -tol].sum() / tot),
                same=float(g[np.abs(d) <= tol].sum() / tot),
                mean_diff=float((g * d).sum() / tot))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--tf", required=True, help="Treatment First arm directory (or wherever its W files are)")
    ap.add_argument("--hf", required=True, help="Housing First arm directory")
    ap.add_argument("--tag", default="counter_arm")
    ap.add_argument("--tf-tag", default=None)
    ap.add_argument("--hf-tag", default=None)
    ap.add_argument("--tol", type=float, nargs="+", default=[1e-3, 1e-2])
    ap.add_argument("--json", default=None, help="also write the numbers here")
    a = ap.parse_args()

    st, wt, mt = load(a.tf, a.tf_tag or a.tag)
    sh, wh, mh = load(a.hf, a.hf_tag or a.tag)
    for k in ("fin_lo", "fin_hi", "n_unemployment", "n_employment", "housing_lo", "housing_hi",
              "voucher_max", "number_of_smi_states", "employment_base_size", "J_K"):
        if st[k] != sh[k]:
            sys.exit("GUARD: the two arms have different state spaces (%s %s vs %s)" % (k, st[k], sh[k]))
    if abs(st["discount_factor"] - sh["discount_factor"]) > 1e-12:
        sys.exit("GUARD: the two arms have different discount factors")

    lab = labels(sh)
    w = mh / mh.sum()                      # Housing First newborn distribution
    pos = w > 0
    bad = pos & ((wt <= SENTINEL) | (wh <= SENTINEL) | ~np.isfinite(wt) | ~np.isfinite(wh))
    if bad.any():
        sys.exit("GUARD: %d newborn cells (mass %.3g) have no W in one of the arms" % (bad.sum(), w[bad].sum()))
    diff = np.where(pos, wt - wh, 0.0)

    out = {"tf": os.path.abspath(a.tf), "hf": os.path.abspath(a.hf), "cells_with_newborns": int(pos.sum()),
           "avg_W_tf_weighted_by_hf": float((w * wt)[pos].sum()), "avg_W_hf": float((w * wh)[pos].sum()),
           "avg_W_tf_own_weights": float((mt / mt.sum() * np.where(mt > 0, wt, 0)).sum()),
           "omega_c_tf": st.get("weight_on_child"), "omega_c_hf": sh.get("weight_on_child"),
           "by_tolerance": {}}

    print("Treatment First : %s  (omega_c %s, drug price %.6f, pi_V %.6f)" % (a.tf, st.get("weight_on_child"),
          st.get("price_of_addictive_good"), st.get("probability_of_voucher_benchmark_used_1")))
    print("Housing First   : %s  (omega_c %s, drug price %.6f, pi_V %.6f)" % (a.hf, sh.get("weight_on_child"),
          sh.get("price_of_addictive_good"), sh.get("probability_of_voucher_benchmark_used_1")))
    if st.get("weight_on_child") != sh.get("weight_on_child"):
        print("WARNING: the two arms have different omega_c")
    print("newborn cells (HF Phi_1 > 0): %d;  W_TF - W_HF over them: min %.6f  max %.6f  HF-weighted mean %.6f"
          % (pos.sum(), diff[pos].min(), diff[pos].max(), (w * diff)[pos].sum()))
    print("average W at birth: HF %.6f   TF at HF weights %.6f   TF at its own weights %.6f"
          % (out["avg_W_hf"], out["avg_W_tf_weighted_by_hf"], out["avg_W_tf_own_weights"]))

    groups = [("all newborns", pos),
              ("parent has a SUD at the birth", pos & (lab["sud"] == 1)),
              ("parent ever had a SUD at the birth", pos & (lab["ever"] == 1)),
              ("parent clean at the birth", pos & (lab["ever"] == 0)),
              ("parent in class 0 (its own parent never SUD)", pos & (lab["cls"] == 0)),
              ("parent in class 1 (its own parent ever SUD: delta_d)", pos & (lab["cls"] == 1)),
              ("parent without SMI at the birth", pos & (lab["smi"] == 0)),
              ("parent with SMI at the birth", pos & (lab["smi"] == 1))]
    nb = sh["employment_base_size"]
    for c in range(2):
        for n in range(1, nb + 1):
            e = c * nb + n
            prod = sh["nodes"].get(e, (float("nan"),))[0]
            groups.append(("parent node %2d class %d (y=%.3f)" % (n, c, prod),
                           pos & (lab["cls"] == c) & (lab["node"] == n)))

    for tol in a.tol:
        print("\n=== tolerance %.0e utils: share of newborns (HF weights) ===" % tol)
        print("%-52s %9s %9s %9s %9s %12s" % ("group", "mass", "TF better", "TF worse", "within", "mean W diff"))
        res = {}
        for name, mask in groups:
            r = shares(diff, w, mask, tol)
            res[name] = r
            if r["mass"] == 0:
                print("%-52s %9.5f %9s %9s %9s %12s" % (name, 0.0, "--", "--", "--", "(no mass)"))
            else:
                print("%-52s %9.5f %9.4f %9.4f %9.4f %12.6f" % (name, r["mass"], r["better"], r["worse"],
                                                              r["same"], r["mean_diff"]))
        out["by_tolerance"]["%g" % tol] = res

    print("\nper newborn cell (HF Phi_1 > 0):")
    print("%5s %5s %4s %4s %10s %14s %14s %12s" % ("class", "node", "smi", "fin", "HF share", "W_HF", "W_TF", "TF - HF"))
    cells = []
    for i in np.flatnonzero(pos):
        print("%5d %5d %4d %4d %10.6f %14.6f %14.6f %12.6f" % (lab["cls"][i], lab["node"][i], lab["smi"][i],
              lab["fin"][i], w[i], wh[i], wt[i], diff[i]))
        cells.append(dict(cls=int(lab["cls"][i]), node=int(lab["node"][i]), smi=int(lab["smi"][i]),
                          hf_share=float(w[i]), W_hf=float(wh[i]), W_tf=float(wt[i])))
    out["cells"] = cells
    if a.json:
        json.dump(out, open(a.json, "w"), indent=1)
        print("\nwrote", a.json)


if __name__ == "__main__":
    main()
