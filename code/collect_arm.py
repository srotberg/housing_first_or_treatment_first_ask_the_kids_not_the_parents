#!/usr/bin/env python3
"""collect_arm.py <run.log> [...]

Reads one or more arm logs and prints the converged equilibrium of each, with
the six convergence rules scored. It reports ONE equilibrium per arm -- the
last loop -- and never a best-of across loops.

Sources are the ones QUESTIONS.md names. In particular b, lambda_d and h_1 come
off the single `CF MOMENTS distance=` line, so the three belong to the same
iterate; `MOMENT b` does not exist in an arm's log.
"""
import re, sys, os

SHIFTER = 1.6200147899300992      # drug_supply_shifterbaseline_benchmark.dat, n90
EXPO    = 1.0/1.46                # drug_supply_curvature - 1
RULES = [("CF moments","cfmom",5e-4), ("rental","rental",1e-2),
         ("housing","housing",2e-2), ("budget","budget",2.5e-2),
         ("drug","drug",5e-3),       ("inheritance","inherit",2e-3)]

def nums(t, pat):
    return [float(x) for x in re.findall(pat, t, re.M)]

def read(path):
    t = open(path, errors="ignore").read()
    cf = re.findall(r"^ CF MOMENTS distance=\s*([0-9.E+-]+)\s+b=\s*([0-9.E+-]+)"
                    r"\s+lambda_d=\s*([0-9.E+-]+)\s+h_1=\s*([0-9.E+-]+)", t, re.M)
    d = {
      "loops"  : len(cf),
      "cfmom"  : float(cf[-1][0]) if cf else None,
      "b"      : float(cf[-1][1]) if cf else None,
      "lambda" : float(cf[-1][2]) if cf else None,
      "h1"     : float(cf[-1][3]) if cf else None,
      # the arm prints distance_rental_market(transition_length)=, NOT the bare
      # name -- keying on the bare name silently scores this rule as "not
      # printed" and lets an unconverged rental market pass unnoticed
      "rental" : last(nums(t, r"^ distance_rental_market(?:\(transition_length\))?=\s*([0-9.E+-]+)")),
      "_series": {
        "cfmom"  : nums(t, r"^ CF MOMENTS distance=\s*([0-9.E+-]+)"),
        "rental" : nums(t, r"^ distance_rental_market(?:\(transition_length\))?=\s*([0-9.E+-]+)"),
        "housing": nums(t, r"^ distance_housing_market=\s*([0-9.E+-]+)"),
        "budget" : nums(t, r"^ distance_govt_budget=\s*([0-9.E+-]+)"),
        "drug"   : nums(t, r"^ distance_drug_market=\s*([0-9.E+-]+)"),
        "inherit": nums(t, r"^ distance_inheritance[a-z_]*=\s*([0-9.E+-]+)"),
      },
      "housing": last(nums(t, r"^ distance_housing_market=\s*([0-9.E+-]+)")),
      "budget" : last(nums(t, r"^ distance_govt_budget=\s*([0-9.E+-]+)")),
      "drug"   : last(nums(t, r"^ distance_drug_market=\s*([0-9.E+-]+)")),
      "inherit": last(nums(t, r"^ distance_inheritance[a-z_]*=\s*([0-9.E+-]+)")),
      "price"  : last(nums(t, r"^ price_of_addictive_good=\s*([0-9.E+-]+)")),
      "V"      : last(nums(t, r"^ drug quantity V=\s*([0-9.E+-]+)")),
      "piv"    : last(nums(t, r"^ probability_of_voucher_benchmark_used=\s*([0-9.E+-]+)")),
      "homadd" : last(nums(t, r"^ model_fraction_homeless_and_addicted=\s*([0-9.E+-]+)")),
      "welf"   : last(nums(t, r"^ average_welfare_with_childhood=\s*([0-9.E+-]+)")),
      "ended"  : "simulation ended" in t,
      "crash"  : bool(re.search(r"Backtrace|Fortran runtime error", t)),
      "ignored": len(re.findall(r"HANDOVER IGNORED", t)),
    }
    # THE SIGNED GAP. The log carries only abs(gap), and the price printed in
    # the drug block is the price AFTER the update, not the one V was measured
    # at -- pairing V with it gives the wrong number (0.017694 where the true
    # gap is 0.019016). The block prints V, implied, NEW price, distance in that
    # order, so the price V was measured at is the PREVIOUS block's new price,
    # seeded from the drug_price_start handover.
    blocks = re.findall(r"^ drug quantity V=\s*([0-9.E+-]+)\s*\n"
                        r"^ implied supply price=\s*([0-9.E+-]+)\s*\n"
                        r"^ price_of_addictive_good=\s*([0-9.E+-]+)\s*\n"
                        r"^ distance_drug_market=\s*([0-9.E+-]+)", t, re.M)
    seed = re.search(r"HANDOVER drug_price_start:.*?->\s*([0-9.E+-]+)", t)
    p_before = float(seed.group(1)) if seed else None
    gaps = []
    for V_, imp_, pnew_, dist_ in blocks:
        imp_ = float(imp_)
        gaps.append(imp_ - p_before if p_before is not None else None)
        p_before = float(pnew_)
    d["gap"]       = gaps[-1] if gaps else None
    d["gap_path"]  = gaps
    d["price_in"]  = float(blocks[-1][2]) if blocks else d["price"]
    # cross-check against the Fortran's own abs(gap): they must agree
    if blocks and d["gap"] is not None:
        d["gap_check"] = abs(abs(d["gap"]) - float(blocks[-1][3]))
    else:
        d["gap_check"] = None
    return d

def last(a): return a[-1] if a else None
def f(x, w=12, p=6):
    return " "*w if x is None else ("%*.*f" % (w, p, x))

for path in sys.argv[1:]:
    d = read(path)
    name = os.path.basename(os.path.dirname(os.path.abspath(path))) or path
    print("="*74)
    print("%s   loops=%d   %s" % (name, d["loops"],
          "simulation ended" if d["ended"] else "STILL RUNNING or stopped early"))
    if d["crash"]:   print("  ** CRASHED: Backtrace / runtime error in the log **")
    if d["ignored"]: print("  ** %d HANDOVER IGNORED -- the run used a model nobody chose **" % d["ignored"])
    # A RULE THAT IS IDENTICALLY ZERO ON EVERY LOOP IS NOT A SATISFIED RULE, IT
    # IS AN UNMEASURED ONE. In this configuration the rent is pinned at 1 on the
    # author's instruction ("the rent is pinned at 1 and does not need to clear
    # the market at all"), rental supply is set equal to demand -- they agree to
    # all sixteen digits -- and housing and inheritance are zeroed too. Reporting
    # "all six rules held" would claim six checks where three were made.
    ok, live, vacuous = True, 0, []
    print("  %-14s %-14s %-12s %s" % ("rule", "value", "tolerance", "verdict"))
    for label, key, tol in RULES:
        v = d[key]
        ser = d["_series"].get(key) or []
        if v is None:
            print("  %-14s %-14s %-12.1e %s" % (label, "not printed", tol, "CANNOT SCORE"))
            ok = False; continue
        if ser and all(x == 0.0 for x in ser):
            print("  %-14s %-14.4e %-12.1e %s" % (label, v, tol,
                  "VACUOUS -- identically zero every loop, nothing was cleared"))
            vacuous.append(label); continue
        good = v <= tol
        ok &= good; live += 1
        print("  %-14s %-14.4e %-12.1e %s" % (label, v, tol, "ok" if good else "OPEN"))
    if vacuous:
        print("  (%s carry no information here -- see the note in this script)"
              % ", ".join(vacuous))
    print("  CONVERGED: %s" % (
          ("YES -- the %d live rules held (%d vacuous, not checks)" % (live, len(vacuous)))
          if ok else "NO. Do not quote the last loop as if it were an equilibrium."))
    chk = d.get("gap_check")
    note = ""
    if chk is not None and chk > 1e-9:
        note = "   ** disagrees with the Fortran's abs(gap) by %.2e -- do not trust it **" % chk
    print("  price %s   V %s   signed gap %s%s"
          % (f(d["price"],9,5), f(d["V"],9,6), f(d["gap"],10,6), note))
    if d.get("gap_path"):
        print("  gap path: %s" % " ".join("%+.5f" % g for g in d["gap_path"][-8:] if g is not None))
    print("  b %s  lambda_d %s  h_1 %s" % (f(d["b"],9), f(d["lambda"],9), f(d["h1"],9)))
    print("  homeless&addicted %s  pi_v %s  welfare %s"
          % (f(d["homadd"],9), f(d["piv"],9), f(d["welf"],12,5)))
