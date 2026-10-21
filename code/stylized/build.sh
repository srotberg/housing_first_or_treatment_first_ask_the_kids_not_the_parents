#!/bin/sh
# Rebuild the note from the calibration outwards.
#
#   gradient.py    Section 3, the stylized model stripped to the income gradient (8 October):
#                  its calibration, Tables 1 and 2 and Figure 1 -> writing/tables/, writing/figures/,
#                  gradient_numbers.json (read by fill.py).  run.py, tables.py, welfare.py,
#                  children.py and transition.py are the old staged model's and are no longer run:
#                  they would overwrite Tables 1 and 2 and Figure 1.
#   sync_tables.py Tables 5 and 6 from the Fortran ->  writing/tables/, params_numbers.json
#   fill.py        every @@name@@ in the prose      ->  writing/housing_first_or_treatment_first.tex
#   pdflatex       twice, for the cross references ->  writing/housing_first_or_treatment_first.pdf (named after the title)
#
# The stylized calibration IS run here now: gradient.py fits its four parameters in seconds.
#
# ORDER MATTERS IN TWO PLACES. sync_tables.py has to run before fill.py, because
# fill.py merges params_numbers.json to answer the @@q_*@@ placeholders. And
# check_numbers.py has to run after the fill, because it reads the filled file,
# and check_spacing.py after the typeset, because half of it reads the PDF.
#
# ablate.py is NOT run here either. It recalibrates the whole model once per
# component; run it by hand when a component changes.
#
#   sh build.sh

set -e
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)

echo "== the stylized model: calibration, Tables 1 and 2, Figure 1"
python3 gradient.py

echo "== the Fortran's constants, all of them"
python3 "$ROOT/code/paper/export_consts.py"

echo "== the Fortran's parameter tables"
python3 "$ROOT/code/paper/sync_tables.py"

echo "== filling the note"
python3 fill.py

echo "== note"
cd "$ROOT/writing"
pdflatex -interaction=nonstopmode -jobname=housing_first_or_treatment_first housing_first_or_treatment_first.tex > /dev/null
pdflatex -interaction=nonstopmode -jobname=housing_first_or_treatment_first housing_first_or_treatment_first.tex > /dev/null
echo "   wrote writing/housing_first_or_treatment_first.pdf"

echo "== checking that nothing in the prose is typed"
python3 tools/check_numbers.py

echo "== checking that every acronym is defined on first use"
python3 tools/check_acronyms.py

echo "== checking the hyphenation of compound modifiers"
python3 tools/check_hyphens.py

echo "== checking that no two words have run together"
python3 tools/check_spacing.py

# THE TABLES AGAINST THE PROSE. check_alignment.py below judges the Set column
# against the Fortran; this judges it against the note, which is a different
# claim and drifted three ways at once while nothing was watching: varsigma was
# marked Int. where the prose said set, lambda_m was still Int. against a moment
# that had passed to eta_DI, and omega_m and eta_DI were live calibrated
# parameters appearing in no table at all. sync_tables.py syncs NUMBERS and does
# not add rows or touch the Set column, so none of that was visible to it.
# EVERY SOURCE WITH MORE THAN TWO AUTHORS IS CITED AS ET AL. A three author
# paper written out reads perfectly naturally, which is exactly why the
# convention drifts in a single edit and why this is a checker rather than a
# note. It also now checks the ORDER of the prose entries against the order of
# the table rows, which drifted twice unseen: eta_DI's entry sat in the housing
# block while its row was in the mental illness chain, and varrho came before
# the voucher rules in the text and after them in the table.
# THE MARK ITSELF MUST WORK. strip_red.py rewrites \new to a passthrough so
# that leftovers are inert; that passthrough was committed once and every \new
# written afterwards rendered as black text, so several rounds of marked edits
# were invisible while table cells kept showing red. Both states are valid LaTeX
# and the build stayed green, which is why nothing caught it.
echo "== checking that the red mark actually renders red"
python3 tools/check_red.py

echo "== checking the citation convention"
python3 tools/check_citations.py

echo "== checking that the tables and the prose say the same thing"
python3 tools/check_params.py

# THE SET COLUMN AGAINST THE CODE, AND NOT BY EYE. links.py says the mapping is
# "checked by eye once", and TRANSITION_LESSONS records the same check as a
# standing instruction after rho_d was found holding a moment h_2 had taken. An
# instruction to read carefully passes once and then rots: delta_h sat marked
# Int. in Table 11, with its target constant declared in the Fortran and used
# nowhere, while penalty_child_homeless was a compile time parameter that no
# update touched. Nothing re-read the instruction, so nothing caught it. This
# runs every build instead.
echo "== checking the tables' Set column against what the code calibrates"
python3 "$ROOT/code/paper/check_alignment.py"

echo "== verifying the model"
cd "$ROOT/code/stylized"
python3 verify.py
