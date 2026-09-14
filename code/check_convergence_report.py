#!/usr/bin/env python3
"""The convergence REPORT and the convergence TEST must name the same terms.

WHY THIS EXISTS. The calibration's outer `do while` is forty five .OR.'d terms
long. A term whose parameter is HELD is the documented way for this calibration
to run for ever: the update block is skipped, nothing assigns the distance, it
keeps the 1 its declaration gave it, and the loop cannot close whatever the
other forty four do. make_variant.py says it twice -- "the loop does not fail,
it simply never terminates" -- and the reason it is hard to catch is that it is
invisible in a log. Measured on worker_3110c0fab1.log, a real multi-loop run:
TWENTY ONE of the forty five terms never printed a value at all, so nothing in
the log could distinguish a term stuck at 1 from a term nobody prints.

report_convergence_terms() prints all of them. This asserts that it still
prints ALL of them: a term added to the test and not to the report is a term
that can hold the loop open invisibly again, which is the whole failure this
is here to close.

    python3 code/check_convergence_report.py     ->  exit 0 and one line, or
                                                     exit 1 and what is missing

Run it from anywhere; it finds the source next to itself.
"""
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "housing_first_or_treatment_first_SR_v1.f90")


def do_while_terms(src):
    """(name, guard) for every distance term of the calibration's outer do while."""
    lines = src.split("\n")
    start = None
    for i, l in enumerate(lines):
        if l.strip().startswith("do while((distance_discount_factor"):
            start = i
            break
    if start is None:
        raise SystemExit("check_convergence_report: the calibration's do while was not "
                         "found. Its first term is distance_discount_factor; if that "
                         "changed, change this line with it.")
    blk = []
    i = start
    while True:
        blk.append(lines[i].rstrip())
        if not lines[i].rstrip().endswith("&"):
            break
        i += 1
    txt = " ".join(x.rstrip("&").strip() for x in blk)[len("do while("):]

    parts, depth, cur, k = [], 0, "", 0
    while k < len(txt):
        if txt[k] == "(":
            depth += 1
        if txt[k] == ")":
            depth -= 1
        if depth == 0 and txt[k:k + 5] == ".OR. ":
            parts.append(cur)
            cur = ""
            k += 5
            continue
        cur += txt[k]
        k += 1
    parts.append(cur)

    out = {}
    for p in parts:
        p = p.strip()
        m = re.search(r"distance_(\w+)(\(1\))?\s*>\s*stopping_rule_(\w+)", p)
        if not m:
            continue
        g = re.match(r"\(\((.+?)\)\s*\.AND\.", p)
        out[m.group(1)] = g.group(1) if g else None
    return out


def report_terms(src):
    """(name, guard) for every line of report_convergence_terms()."""
    m = re.search(r"subroutine report_convergence_terms\(\)(.*?)end subroutine",
                  src, re.S)
    if not m:
        raise SystemExit("check_convergence_report: report_convergence_terms() is not "
                         "in the source at all. Every term of the calibration's "
                         "convergence test has to be printed once a loop; see the "
                         "subroutine's own comment for why.")
    body = m.group(1)
    out = {}
    for call in re.finditer(
            r'call one_convergence_term\("(\w+)",\s*&\s*'
            r'distance_\w+(?:\(1\))?,\s*stopping_rule_\w+,\s*&\s*'
            r'(.+?),\s*open_1\)', body, re.S):
        name, scored = call.group(1), call.group(2).strip()
        g = re.match(r"merge\(1,0,(.+)\)$", scored)
        out[name] = g.group(1) if g else None
    return out


def main():
    src = io.open(SRC, encoding="utf-8", errors="surrogateescape").read()
    test = do_while_terms(src)
    rep = report_terms(src)

    bad = []
    for name, guard in sorted(test.items()):
        if name not in rep:
            bad.append(f"  distance_{name} is SCORED by the do while and NOT printed "
                       f"by the report. A held parameter here holds the calibration "
                       f"open with nothing in the log to say so.")
        elif rep[name] != guard:
            bad.append(f"  distance_{name}: the do while guards it on "
                       f"{guard!r} and the report on {rep[name]!r}. The report would "
                       f"call a term open that the test does not score, or the "
                       f"reverse.")
    for name in sorted(rep):
        if name not in test:
            bad.append(f"  distance_{name} is printed by the report and NOT scored by "
                       f"the do while. Either the test lost a term or the report "
                       f"gained one; both are worth knowing.")

    if bad:
        print("CONVERGENCE REPORT OUT OF SYNC WITH THE CONVERGENCE TEST")
        print("\n".join(bad))
        return 1

    print(f"convergence report: all {len(test)} terms of the calibration's do while "
          f"are printed once a loop, with matching guards")
    return 0


if __name__ == "__main__":
    sys.exit(main())
