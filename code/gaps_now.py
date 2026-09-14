#!/usr/bin/env python3
"""The full instrument table, with the parameter-to-moment map DERIVED, not written.

Writing that map by hand put four wrong rows in front of the author on 14
September: relative_share_of_leisure was reported as a 113 per cent gap when
inelastic_labor_supply=1 makes it unreachable, newborn_endowment was put on the
bottom-half wealth share instead of the young's share of the homeless,
kappa_phi_d_level on unemployment-given-SUD instead of y_u, and kappa_uem on the
moment PRINTED under its own name -- at +201 per cent -- instead of the one it is
bracketed on, where it sits within 6 per cent.

The map here comes out of the file: each instrument's own `distance_<param> =`
assignment names the `_data`/`val_` target it is computed against, each MOMENT
print names the target it displays, and the two are matched on that shared token.
A print label and a bracket are allowed to disagree; the bracket is what moves the
parameter, so the bracket is what this reports.

Usage: python3 code/gaps_now.py <run log>
"""
import re
import sys

FORTRAN = "code/housing_first_or_treatment_first_SR_v1.f90"
# Compile-time constants that make whole branches unreachable. A parameter used
# only inside a dead branch is not a gap, it is absent from the model.
FLAGS = {"freeze_to_three_block": 1, "calibrate_size_of_smallest_house_hhld_can_buy": 1,
         "hold_theta": 1, "freeze_relative_share_of_leisure": 1,
         "first_block_only": 0, "inelastic_labor_supply": 1}
# Instruments whose only behavioural sites sit inside a branch the flags above
# switch off. Listed rather than inferred, because proving unreachability from
# the text is harder than reading the two functions.
# Market-clearing adjusters, not calibration instruments: they price a market
# inside the solve rather than hit a target, so they have no gap to report.
NOT_CALIB = {"drug_market", "rental_market", "rent_to_price", "utility_improvement",
             "convexity_of_rental_company", "scaling_of_ss", "standard_deduction",
             "max_initial_endowment", "advantage_to_owning"}
DEAD = {"relative_share_of_leisure": "inelastic_labor_supply=1: leisure_utility and "
        "leisure_marginal_utility both return a hard 0.d0"}
TARGET = re.compile(r"\b(\w*_data|val_\w+|\w+_target)\b")
# Any identifier shared between a distance expression and a MOMENT print, other
# than the model's own outputs and Fortran noise, is that instrument's target.
IDENT = re.compile(r"\b([A-Za-z_]\w{3,})\b")
NOISE = {"abs", "max", "min", "merge", "write", "sum", "real", "then", "else",
         "MOMENT", "model", "target", "sqrt", "log", "exp", "dble", "size"}


def tokens(e):
    out = set(TARGET.findall(e))
    out |= {t for t in IDENT.findall(e)
            if not t.startswith(("model_", "distance_", "gap_", "previous_", "have_"))
            and t not in NOISE}
    return out



def statement(lines, i):
    e = re.sub(r"\s*!.*$", "", lines[i])
    j = i
    while e.rstrip().endswith("&") and j + 1 < len(lines):
        j += 1
        e = e.rstrip().rstrip("&") + re.sub(r"\s*!.*$", "", lines[j])
    return e


def evaluate(e):
    e = re.sub(r"\s*!.*$", "", e).strip().rstrip("&").strip()
    e = re.sub(r"(?<=[\d.])[dD](?=[-+]?\d)", "e", e)
    e = re.sub(r"(\d)\.e", r"\1.0e", e)
    for k, v in FLAGS.items():
        e = re.sub(r"\b%s\b" % k, str(v), e)
    try:
        return float(eval(e))
    except Exception:
        return None


def main():
    lines = open(FORTRAN, errors="ignore").read().split("\n")
    log = open(sys.argv[1], errors="ignore").read()

    adj = {}
    for i, ln in enumerate(lines):
        m = re.match(r"\s*real\(8\)\s*::\s*(\w+)_adjuster\s*=\s*(.*)$", ln)
        if m and m.group(1) not in adj:
            # the RHS only: statement() returns the whole declaration, and
            # feeding "real(8) :: x_adjuster=2.d0" to eval silently yields None,
            # which reads as "held" for every instrument in the file.
            rhs = statement(lines, i).split("=", 1)[1]
            adj[m.group(1)] = evaluate(rhs)
    # theta's live adjuster is relative_share_of_addiction_adj; the _adjuster of
    # that name is declared zero and never read.
    m = re.search(r"relative_share_of_addiction_adj\s*=\s*([^!\n]+)", "\n".join(lines))
    if m:
        adj["relative_share_of_addiction_1"] = evaluate(m.group(1))
        adj.pop("relative_share_of_addiction", None)

    # A distance is often abs(gap_X), and gap_X is where the _data target
    # actually appears -- so resolve one level of indirection before matching.
    # Without it the whole drug block (b, the onset, multiple_find) plus beta,
    # gamma and delta_d drop out of the table silently, which is worse than a
    # wrong row: the headline instrument simply is not there.
    gap_t = {}
    for i, ln in enumerate(lines):
        m = re.match(r"\s*(gap_\w+)\s*=\s*(.*)$", ln)
        if m:
            t = tokens(statement(lines, i))
            if t:
                gap_t.setdefault(m.group(1), set()).update(t)

    dist, mom_t = {}, {}
    for i, ln in enumerate(lines):
        m = re.match(r"\s*distance_(\w+)\s*=\s*(.*)$", ln)
        if m and m.group(2).strip() not in ("0", "0.d0"):
            e = statement(lines, i)
            t = tokens(e)
            for g in re.findall(r"\bgap_\w+", e):
                t |= gap_t.get(g, set())
            if t:
                dist.setdefault(m.group(1), set()).update(t)
        if "MOMENT" in ln and "write" in ln:
            e = statement(lines, i)
            n = re.search(r'"MOMENT\s+(\S+)', e)
            t = tokens(e)
            if n and t:
                mom_t.setdefault(n.group(1), set()).update(t)

    val = {}
    for m in re.finditer(r"(?m)^\s*([a-zA-Z_]\w*)=\s*([-+]?[\d.]+(?:[eEdD][-+]?\d+)?)\s*$", log):
        if m.group(1).startswith(("distance_", "gap_", "model_", "stopping_")):
            continue
        try:
            val[m.group(1)] = float(m.group(2).replace("D", "E").replace("d", "e"))
        except ValueError:
            pass
    # the productivity floor prints "X -> Y", never a plain assignment
    bpl = re.findall(r"raising the smallest\s+productivity\s+[-\d.eEdD+]+\s*->\s*([-\d.eEdD+]+)", log)
    if bpl:
        val["bottom_productivity_level"] = float(bpl[-1].replace("D", "E"))

    mom = {}
    for m in re.finditer(r"MOMENT\s+(\S+)\s+.*?model=\s*([-\d.eEdD+]+)\s+target=\s*([-\d.eEdD+]+)", log):
        try:
            mom[m.group(1)] = (float(m.group(2).replace("D", "E")),
                               float(m.group(3).replace("D", "E")))
        except ValueError:
            pass
    # newborn_endowment's moment has no MOMENT print of its own
    band = re.findall(r"share of the homeless in band 1\s*=\s*([-\d.eEdD+]+)\s+target\s*=\s*([-\d.eEdD+]+)", log)
    if band:
        mom["band1"] = (float(band[-1][0].replace("D", "E")), float(band[-1][1].replace("D", "E")))
        mom_t["band1"] = {"val_hud_share_1"}

    ALIAS = {"onset_base": "addiction_onset_base", "multiple_find": "multiple_find_if_addicted",
             "addiction_scalar": "addiction_scalar_1",
             "employment_multiplier": "multiple_of_probabilities_of_employment_if_addicted"}
    rows = []
    for a, rate in adj.items():
        if a in DEAD or a in NOT_CALIB or a not in dist:
            continue
        p = ALIAS.get(a, a)
        hits = [k for k, v in mom_t.items() if v & dist[a]]
        mn = "/".join(sorted(hits)) or "(no print)"
        mm = mom.get(hits[0]) if hits else None
        gap = (mm[0] - mm[1]) / mm[1] * 100 if mm and mm[1] else None
        rows.append((rate, p, mn, val.get(p), mm, gap))

    loops = log.count("MOMENT cbar")
    # Name the log, not a run this script cannot know it is reading. The header
    # said "the pinned run" from the day it was written, and went on saying it
    # after the run was replaced -- a label that is right once and wrong after.
    import os
    which = os.path.basename(os.path.dirname(os.path.abspath(sys.argv[1]))) or sys.argv[1]
    print(f"loop {loops} of {which}; gaps are relative, in per cent\n")
    for live, head in ((True, "LIVE"), (False, "HELD -- opens later")):
        sel = [r for r in rows if bool(r[0]) == live]
        print(f"{head}   ({len(sel)})")
        print(f"{'parameter':<42}{'value':>13} {'moment':<13}{'model':>11}{'target':>11}{'gap':>9}")
        print("-" * 100)
        for rate, p, mn, pv, mm, gap in sorted(sel, key=lambda r: -abs(r[5]) if r[5] is not None else 1e9):
            vs = f"{pv:13.6g}" if pv is not None else f"{'--':>13}"
            ms = f"{mm[0]:11.6g}{mm[1]:11.6g}" if mm else f"{'--':>11}{'--':>11}"
            gs = f"{gap:+8.1f}%" if gap is not None else f"{'--':>9}"
            print(f"{p:<42}{vs} {mn:<13}{ms}{gs}")
        print()
    # Moments no live instrument is fitting. They still move, as a by-product of
    # whatever changes the composition behind them, so they are worth reading --
    # but a gap here is not something the search is working on. emp_homeless is
    # the standing example: the author chose h_1 to hit the homelessness rate and
    # accepted whatever employed share fell out of it.
    live_moments = {r[2] for r in rows if r[0]}
    watched = sorted(set(mom) - live_moments)
    if watched:
        print(f"WATCHED -- no live instrument is fitting these   ({len(watched)})")
        print(f"{'moment':<14}{'model':>12}{'target':>12}{'gap':>9}")
        print("-" * 47)
        for k in sorted(watched, key=lambda k: -abs((mom[k][0] - mom[k][1]) / mom[k][1])
                        if mom[k][1] else 1e9):
            md, tg = mom[k]
            gs = f"{(md - tg) / tg * 100:+8.1f}%" if tg else f"{'--':>9}"
            print(f"{k:<14}{md:12.6g}{tg:12.6g}{gs}")
        print()
    for d, why in DEAD.items():
        print(f"DROPPED {d}: {why}")


if __name__ == "__main__":
    main()
