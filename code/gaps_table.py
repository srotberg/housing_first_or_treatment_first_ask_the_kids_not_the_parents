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
    ("addiction_onset_base", "addiction_onset_base",             "onset_base",                 "MOMENT:lambda_d"),
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
                                                                 "smallest_house_size",        "MOMENT:h_2"),
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


def adjuster_is_live(src_text, stem):
    """True when <stem>_adjuster is declared non-zero."""
    if stem is None:
        return False
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
        return (float(nums[0].replace("E", "e")), 0.16) if nums else None
    if kind == "young_homeless":
        hits = [l for l in loglines if "homelessness_by_age_group=" in l]
        if len(hits) < 5:
            return None
        m = re.search(r"=\s*([-\d.]+(?:[EeDd][-+]?\d+)?)", hits[-5])
        return (float(m.group(1).replace("E", "e")), 0.260) if m else None
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

    for name, param, stem, key in ROWS:
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

        if param is None:
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
