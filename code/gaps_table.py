#!/usr/bin/env python3
"""The author's gaps table.

Requested 16 September: *"I want you to show me for each gaps table the targets
for all of these: beta, sigma_y, theta, gamma, find_if_addicted, mu_H, pi_eu,
addiction_onset_base, h1, newborn endowment, omega_c, tau_ell, c bar,
kappa_phi_d_level, kappa_find_smi, pi_v, p_m, tau_u, aleph, b, delta_d, h2,
emp_homeless. Can you automate it for me so this is the table you always show
me? i want the parameter value, the model value, the data value, the gap, the
direction of update at the current model and data gap"*.

Five columns per row, exactly as asked: the PARAMETER's current value, the
MODEL's moment, the DATA target, the gap in per cent, and which way the update
rule moves the parameter given that gap.

THE DIRECTION IS READ OUT OF THE FORTRAN, NOT REMEMBERED. Each update is of the
author's form

    parameter = parameter +/- adjuster * (model_moment - data_moment)

so the operator in the source settles the direction. This script finds that
operator by parsing the source, because a direction carried in someone's head
is how a sign gets flipped: on 15 September the onset's sign looked backwards,
was very nearly "fixed", and turned out to be measured and correct, with a note
recording that an earlier round had made exactly that mistake and spent nineteen
loops paying for it.

TWO ROWS ARE NOT SIMPLE MOMENT ROWS AND ARE LABELLED SO.
  theta        reported on the AGGREGATE, sum spend over sum income, on the
               author's instruction. The MOMENT row is a mass-weighted MEAN OF
               RATIOS that runs three to four times the aggregate and reads as
               a huge miss when the aggregate is close.
  emp_homeless has NO INSTRUMENT of its own. It moves as a by-product of h_1,
               so it has no parameter and no direction.

Usage:  python3 code/gaps_table.py <run.log>
"""
import re
import sys
import os

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "housing_first_or_treatment_first_SR_v1.f90")

# author's name -> (fortran parameter, adjuster stem, moment key, pretty target name)
# moment key is either "MOMENT <name>" or a special handled below.
ROWS = [
    ("beta",                 "discount_factor",                  "discount_factor",            "MOMENT:beta"),
    ("sigma_y",              "kkk_sigma_scale",                  "kkk_sigma_scale",            "MOMENT:sigma_y"),
    ("theta",                "relative_share_of_addiction_1",    "relative_share_of_addiction","SPECIAL:theta_aggregate"),
    ("gamma",                "relative_share_of_housing",        "relative_share_of_housing",  "MOMENT:gamma"),
    # THE VALUE COLUMN MUST NAME THE LIVE INSTRUMENT, NOT THE RETIRED ONE.
    # Until 16 September this row read multiple_of_probabilities_of_employment_
    # if_addicted, which is PINNED AT 1 on the author's instruction with
    # employment_multiplier_adjuster=0. The table therefore printed a constant 1
    # beside a moment that was moving, and the author spotted it: "find_if_
    # addicted=1 and it gives the right share of homeless with SUD? it makes no
    # sense". The live instrument is multiple_find_if_addicted, adjuster 2.0.
    ("find_if_addicted",     "multiple_find_if_addicted",
                                                                 "multiple_find",              "MOMENT:sud_homeless"),
    ("mu_H",                 "mu_homeless",                      "mu_homeless",                "MOMENT:mu_H"),
    ("pi_eu",                "probability_becoming_unemployed",  "separation_rate",            "MOMENT:pi_eu"),
    ("addiction_onset_base", "addiction_onset_base",             "onset_base",                 "SPECIAL:sud_per_user"),
    ("h1",                   "size_homelessness",                "size_homelessness",          "MOMENT:h_1"),
    ("newborn_endowment",    "newborn_endowment_scale",          "newborn_endowment",          "SPECIAL:young_homeless"),
    ("omega_c",              "weight_on_child",                  "weight_on_child",            "SPECIAL:none"),
    ("tau_ell",              "labor_income_tax_rate",            "labor_income_tax_rate",      "MOMENT:tau_l"),
    ("c_bar",                "max_food_cost",                    "max_food_cost",              "MOMENT:cbar"),
    ("kappa_phi_d_level",    "kappa_phi_d_level",                "kappa_phi_d_level",          "MOMENT:y_u"),
    ("kappa_find_smi",       "kappa_find_smi",                   "kappa_find_smi",             "MOMENT:lambda_m"),
    ("pi_v",                 "probability_of_voucher_benchmark_used",
                                                                 "voucher_probability",        "MOMENT:pi_V"),
    ("p_m",                  "smi_onset_level",                  "smi_onset_level",            "MOMENT:p_m"),
    ("tau_u",                "utility_cost_of_treatment",        "utility_cost_of_treatment",  "MOMENT:tau_u"),
    ("aleph",                "value_of_life",                    "value_of_life",              "MOMENT:aleph"),
    ("b",                    "addiction_scalar_1",               "addiction_scalar",           "MOMENT:b"),
    ("delta_d",              "penalty_child_addicted",           "penalty_child_addicted",     "SPECIAL:child_sud"),
    ("h2",                   "smallest_rental_relative_to_lowest_income",
                                                                 "smallest_house_size",        "SPECIAL:renter_burden_30"),
    ("emp_homeless",         None,                               None,                         "MOMENT:emp_homeless"),
]


def logical_lines(text):
    """Join Fortran '&' continuations so an update spanning lines is one string."""
    out, buf = [], ""
    for raw in text.split("\n"):
        line = raw.split("!")[0].rstrip() if not raw.lstrip().startswith("!") else ""
        if line.endswith("&"):
            buf += line[:-1].strip()
        else:
            out.append((buf + " " + line.strip()).strip() if buf else line.strip())
            buf = ""
    return out


def update_rule(src_text, stem):
    """Return (op, order) for <stem>_adjuster's update, or (None, None).

    op    '+' or '-', the operator immediately before the adjuster.
    order +1 when the bracket is (model - data), -1 when it is (data - model).

    KEYED ON THE ADJUSTER, not on the left-hand side, because several updates
    assign through an intermediate -- the onset writes onset_step_1 and only
    later lands in addiction_onset_base -- and keying on the parameter missed
    every one of those.

    THE ORDER MATTERS AS MUCH AS THE OPERATOR and is easy to miss. kappa's rule
    is 'kappa - adjuster*(drug_user_income_data - model_avg_income...)': the
    bracket is DATA MINUS MODEL, so reading the minus alone gives exactly the
    wrong direction.
    """
    if stem is None:
        return (None, None)
    pat = re.compile(r"([+-])\s*" + re.escape(stem) + r"_(?:adjuster|adj)\s*\*\s*(.*)")
    for line in logical_lines(src_text):
        if stem + "_adjuster*" not in line.replace(" ", "") and \
           stem + "_adj*" not in line.replace(" ", ""):
            continue
        m = pat.search(line.replace(" ", ""))
        if not m:
            continue
        op, rest = m.group(1), m.group(2)
        # first parenthesised difference after the adjuster
        depth, start = 0, None
        for i, ch in enumerate(rest):
            if ch == "(":
                if depth == 0:
                    start = i + 1
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    inner = rest[start:i]
                    break
        else:
            inner = rest
        # split on the top-level minus
        depth, cut = 0, None
        for i, ch in enumerate(inner):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            elif ch == "-" and depth == 0 and i > 0 and inner[i-1] not in "*+-/(":
                cut = i
                break
        if cut is None:
            return (op, 1)
        left, right = inner[:cut], inner[cut+1:]
        is_data = lambda t: ("_data" in t) or ("_target" in t) or t.endswith("_data(1)")
        if is_data(right) and not is_data(left):
            return (op, 1)
        if is_data(left) and not is_data(right):
            return (op, -1)
        return (op, 1)
    return (None, None)


def band_edge(src_text, name):
    """The value of a Fortran real parameter declared as <name>=<number>d0.

    PARSED, NOT REMEMBERED, like the update operator. h1_band_lo was 0.004,
    then 0.0055 on 17 September, then 0.0080 on 18 September; a copy of it in
    this script is a copy that goes stale silently and prints a direction the
    model does not take.
    """
    m = re.search(r"real\(8\)(?:, parameter)? *:: *" + re.escape(name) +
                  r" *= *([0-9.eEdD+-]+)", src_text)
    if not m:
        return None
    try:
        return float(m.group(1).replace("d", "e").replace("D", "e"))
    except ValueError:
        return None


def adjuster_is_live(src_text, stem):
    """True when <stem>_adjuster is declared non-zero."""
    if stem is None:
        return False
    # PREFER THE NAME THE UPDATE USES, NOT THE ONE THAT MERELY EXISTS.
    # theta declares BOTH relative_share_of_addiction_adjuster (0.d0, a decoy
    # nothing reads) and relative_share_of_addiction_adj ((1-hold_theta)*0.05,
    # which line 47435 actually multiplies). Checking _adjuster first found the
    # decoy, reported HELD, and hid the fact that theta had been stepping every
    # block -- the author caught it from the value drifting 0.21 -> 0.20461.
    # So: if the source multiplies <stem>_adj anywhere, that is the live one.
    if re.search(re.escape(stem) + r"_adj\s*\*", src_text):
        m = re.search(r"real\(8\)(?:, parameter)? *:: *" + re.escape(stem) + r"_adj *=\s*([^\n!]+)", src_text)
    else:
        m = re.search(r"real\(8\)(?:, parameter)? *:: *" + re.escape(stem) + r"_adjuster *=\s*([^\n!]+)", src_text)
    if not m:
        m = re.search(r"real\(8\)(?:, parameter)? *:: *" + re.escape(stem) + r"_adj *=\s*([^\n!]+)", src_text)
    if not m:
        return None
    expr = m.group(1).strip().rstrip(",")
    t = expr.replace("d", "e").replace("D", "E")
    t = re.sub(r"(\d)\s*\*\s*10\.e\*\*\(?(-?\d+)\)?", r"\1e\2", t)
    t = re.sub(r"\(1-\w+\)", "(0)", t)
    try:
        return float(eval(t)) > 0
    except Exception:
        return None


def last_moment_block(loglines):
    blocks, cur = [], []
    for l in loglines:
        if "MOMENT " in l:
            cur.append(l)
        if "END OF MOMENTS" in l and cur:
            blocks.append(cur)
            cur = []
    return blocks[-1] if blocks else []


def parse_moments(block):
    d = {}
    for l in block:
        m = re.match(r"\s*MOMENT (\S+)\s+(.*?)\s+model=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)"
                     r"\s+target=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)", l)
        if m:
            d[m.group(1)] = (float(m.group(3).replace("E", "e").replace("D", "e")),
                             float(m.group(4).replace("E", "e").replace("D", "e")))
    return d


def last_param_value(loglines, name):
    """The most recent '<name>= <value>' print in the log."""
    pat = re.compile(r"^\s*" + re.escape(name) + r"=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)")
    val = None
    for l in loglines:
        m = pat.match(l)
        if m:
            val = float(m.group(1).replace("E", "e").replace("D", "e"))
    return val


def special(kind, loglines):
    """Moments that do not print a MOMENT row. Returns (model, target) or None."""
    if kind == "theta_aggregate":
        hits = [l for l in loglines if "drug share, sum spend / sum income" in l]
        if not hits:
            return None
        nums = re.findall(r"([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-1])
        # 0.16 from 17 September: "I suggest to target Theta to 0.16". It was
        # 0.14 from 16 September: "You can set the theta target to 0.14 not
        # 0.16". Typed here AND in the Fortran as drug_spending_share_data,
        # which is a duplication this script cannot avoid -- theta prints as a
        # DIAG line carrying no target, so the number has to come from
        # somewhere. If the Fortran target moves again, move it here too.
        return (float(nums[0].replace("E", "e")), 0.16) if nums else None
    if kind == "young_homeless":
        hits = [l for l in loglines if "homelessness_by_age_group=" in l]
        if len(hits) < 5:
            return None
        m = re.search(r"=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-5])
        return (float(m.group(1).replace("E", "e")), 0.260) if m else None
    if kind == "sud_per_user":
        # THE ONSET IS BRACKETED ON THE RATIO, SO THE ROW REPORTS THE RATIO.
        #
        # Its update at 46449 is
        #     onset_step_1 = onset_at_mean_1 - adjuster *
        #         (model_fraction_addicted/model_total_drug_users
        #          - sud_rate_data/participation_rate_data)
        # which is the author's *"SUD has to be about 41% of b"*. The row used
        # to score the UNCONDITIONAL lambda_d against 0.0368 instead, and that
        # is not the quantity the instrument can see.
        #
        # It is not a cosmetic difference. With the ratio held at r, the two
        # gaps are b/0.089-1 and r*b/0.0368-1, so whenever b is far from target
        # the onset's gap is arithmetically the larger of the two and the pair
        # SPREADS AS b MOVES. At block 36 of n23 that printed as b +184.2 per
        # cent against the onset +207.6, which reads as b and SUD diverging
        # when the ratio behind both had been flat at 0.443 to 0.452 for
        # thirty-five blocks. The author read the table that way and asked.
        # One error reported twice is not two errors.
        num = last_param_value(loglines, "model_fraction_addicted")
        hits = [l for l in loglines if "MOMENT b  " in l]
        if num is None or not hits:
            return None
        nums = re.findall(r"([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-1])
        if len(nums) < 2:
            return None
        b_model = float(nums[0].replace("E", "e").replace("D", "e"))
        b_target = float(nums[1].replace("E", "e").replace("D", "e"))
        lam = [l for l in loglines if "MOMENT lambda_d" in l]
        if not lam:
            return None
        lnums = re.findall(r"([-\d.]+(?:[EeDd][-+]?\d+)?)", lam[-1])
        if len(lnums) < 2:
            return None
        lam_target = float(lnums[1].replace("E", "e").replace("D", "e"))
        if b_model <= 0 or b_target <= 0:
            return None
        # Both targets are read off the log's own MOMENT lines rather than
        # typed here, so this row cannot drift from the Fortran.
        return (num / b_model, lam_target / b_target)
    if kind == "renter_burden_30":
        # h_2 IS BRACKETED ON THE RENTERS' 30 PER CENT CUT, SO THE ROW REPORTS
        # THAT.
        #
        # It was retargeted on 17 September -- the author: *"I want you to
        # retarget h2 to the % spending over 30% on housing. I think it's
        # around 40.6%"* -- and this row went on scoring "MOMENT h_2 above half
        # of spending" against severe_cost_burden_data, which is a different
        # universe (all households, not renters) and a different denominator
        # (spending, not income). At n29 block 7 that printed h_2 as 30.6 per
        # cent off and moving the WRONG WAY: the row said 0.0701 against 0.101,
        # too low, RAISE, while the moment the rule actually reads was 0.6310
        # against 0.406, too high, LOWER.
        #
        # Same fault as the onset row carried this morning. A table that scores
        # a parameter on a moment its update cannot see is worse than no row.
        hits = [l for l in loglines if "renters above 30 pct of income" in l]
        if not hits:
            return None
        # ANCHOR ON THE LABELS, NOT ON POSITION. A bare number sweep picks up
        # the "30" in "30 pct of income" as the model value and prints a gap of
        # 4694 per cent, which is how this was caught.
        m = re.search(r"model=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)"
                      r".*?observed=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-1])
        if not m:
            return None
        return (float(m.group(1).replace("E", "e").replace("D", "e")),
                float(m.group(2).replace("E", "e").replace("D", "e")))
    if kind == "child_sud":
        hits = [l for l in loglines if "child SUD ratio model" in l]
        if not hits:
            return None
        nums = re.findall(r"([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-1])
        return (float(nums[0].replace("E", "e")), float(nums[1].replace("E", "e"))) if len(nums) > 1 else None
    return None


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python3 code/gaps_table.py <run.log>")
    path = sys.argv[1]
    src_text = open(SRC, errors="ignore").read()
    loglines = open(path, errors="ignore").read().split("\n")
    block = last_moment_block(loglines)
    moms = parse_moments(block)
    nblocks = sum(1 for l in loglines if "END OF MOMENTS" in l)

    print("gaps table   log: %s   blocks complete: %d" % (path, nblocks))
    print()
    hdr = ("%-20s %-12s %-12s %-12s %8s  %s"
           % ("parameter", "value", "model", "data", "gap", "update moves it"))
    print(hdr)
    print("-" * len(hdr))

    # ORDERED WORST FIT FIRST, on the author's instruction of 16 September:
    # "when you show me the gaps table, i want it to be ordered from worst fit
    # to best fit". Rows with no moment in the log have no gap to sort on and
    # are printed last, after the ranked rows, rather than being given a
    # position they have not earned.
    ranked, unranked = [], []
    for row in ROWS:
        name, param, stem, key = row
        kind, _, arg = key.partition(":")
        got = moms.get(arg) if kind == "MOMENT" else (
            special(arg, loglines) if arg != "none" else None)
        if got is None:
            unranked.append(row)
            continue
        model, data = got
        ranked.append((abs(model - data) / abs(data) * 100 if data else -1.0, row))
    ranked.sort(key=lambda t: t[0], reverse=True)

    for name, param, stem, key in [r for _, r in ranked] + unranked:
        kind, _, arg = key.partition(":")
        if kind == "MOMENT":
            got = moms.get(arg)
        else:
            got = special(arg, loglines) if arg != "none" else None

        pval = last_param_value(loglines, param) if param else None
        if got is None:
            print("%-20s %-12s %-12s %-12s %8s  %s"
                  % (name, ("%.5g" % pval) if pval is not None else "-",
                     "not printed", "-", "-", "no moment in this log"))
            continue

        model, data = got
        gap = abs(model - data) / abs(data) * 100 if data else float("nan")
        live = adjuster_is_live(src_text, stem)

        # A SCAN-DRIVEN PARAMETER HAS NO ADJUSTER, AND "HELD" IS A LIE ABOUT IT.
        # delta_d is chosen by the PENALTY SCAN over [scan_lo, scan_hi], not by
        # a bracket, so adjuster_is_live() reads zero and the row used to print
        # HELD while the scan ran twenty-one points every block. This is the
        # same class of error as the find_if_addicted row the author caught on
        # 16 September: the direction column described the machinery it expected
        # rather than the machinery that is running.
        if stem == "penalty_child_addicted":
            verdict = [l for l in loglines if "PENALTY SCAN did NOT bracket" in l
                       or "PENALTY SCAN SOLVED" in l]
            if verdict and "did NOT bracket" in verdict[-1]:
                direction = "SCAN [0,0.4]: BEST IN RANGE, target not reachable"
            elif verdict:
                direction = "SCAN [0,0.4]: solved"
            else:
                direction = "SCAN (no verdict in this log)"
        # h_1 IS SCORED AGAINST A BAND, NOT AGAINST ITS TARGET, and reading the
        # operator alone gives the wrong direction whenever the rate sits
        # between fraction_homeless_data and the band floor -- which is exactly
        # where it has sat all of n61 to n66. The Fortran's gap is
        #
        #   rate > h1_band_hi  ->  rate - h1_band_hi
        #   rate < h1_band_lo  ->  rate - h1_band_lo
        #   otherwise          ->  0, and size_homelessness is HELD
        #
        # so at a rate of 0.0053 against a floor of 0.0080 the gap is NEGATIVE
        # and the rule RAISES h_1, while the gap to the 0.004 target is positive
        # and this table printed LOWER. Same class of error as the onset sign:
        # a direction taken from the operator without the bracket it multiplies.
        # The band edges are PARSED, for the same reason the operator is.
        elif stem == "size_homelessness":
            lo = band_edge(src_text, "h1_band_lo")
            hi = band_edge(src_text, "h1_band_hi")
            if lo is None or hi is None:
                direction = "band edges not found in source"
            elif live is False:
                direction = "HELD"
            else:
                band_gap = (model - hi) if model > hi else \
                           ((model - lo) if model < lo else 0.0)
                op, order = update_rule(src_text, stem)
                if op is None:
                    direction = "rule not found in source"
                elif band_gap == 0.0:
                    direction = "HELD (rate inside the band)"
                else:
                    delta = (1 if op == "+" else -1) * order * band_gap
                    direction = "RAISE" if delta > 0 else "LOWER"
                direction += "  [scored on band [%.4g,%.4g], band gap %+.5f]" \
                             % (lo, hi, band_gap)
        elif param is None:
            direction = "NO INSTRUMENT (follows h_1)"
        elif live is False:
            direction = "HELD"
        else:
            op, order = update_rule(src_text, stem)
            if op is None:
                direction = "rule not found in source"
            else:
                # step = op * adjuster * order * (model - data); adjuster > 0
                delta = (1 if op == "+" else -1) * order * (model - data)
                direction = "RAISE" if delta > 0 else ("LOWER" if delta < 0 else "on target")
                if live is None:
                    direction += " (adjuster unreadable)"

        note = ""
        if arg == "theta_aggregate":
            note = "  [aggregate, not mean-of-ratios]"
        # A parameter that did not print in this log is NOT a number. It happens
        # whenever an update was gated -- the cooldown held it, or kappa's gate
        # was shut -- and printing nan invites it to be read as a value.
        vtxt = ("%.5g" % pval) if pval is not None else "not printed"
        print("%-20s %-12s %-12.5g %-12.5g %7.1f%%  %s%s"
              % (name, vtxt, model, data, gap, direction, note))

    print()
    print("direction is parsed from the Fortran update line, not remembered.")
    print("RAISE/LOWER is what the rule does to the PARAMETER at the current gap.")


if __name__ == "__main__":
    main()
