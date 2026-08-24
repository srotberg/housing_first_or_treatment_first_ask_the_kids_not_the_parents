#!/bin/sh
# Rebuild the note from the calibration outwards.
#
#   run.py         the two stylized figures        ->  writing/figures/
#   tables.py      Tables 1 to 4                   ->  writing/tables/
#   welfare.py     the welfare numbers             ->  (read by fill.py)
#   children.py    the child's penalty             ->  (read by fill.py)
#   transition.py  the transition figure           ->  writing/figures/
#   sync_tables.py Tables 5 and 6 from the Fortran ->  writing/tables/, params_numbers.json
#   fill.py        every @@name@@ in the prose      ->  writing/housing_first_children_later.tex
#   pdflatex       twice, for the cross references ->  writing/housing_first_children_later.pdf
#
# CALIBRATION IS NOT RUN HERE. It takes upwards of half an hour and everything
# below reads calibrated.json, so it is run on its own and this is run after:
#
#   python3 calibrate.py && sh build.sh
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

echo "== figures"
python3 run.py

echo "== tables"
python3 tables.py

echo "== welfare"
python3 welfare.py

echo "== children"
python3 children.py

echo "== transition"
python3 transition.py

echo "== the Fortran's constants, all of them"
python3 "$ROOT/code/paper/export_consts.py"

echo "== the Fortran's parameter tables"
python3 "$ROOT/code/paper/sync_tables.py"

echo "== filling the note"
python3 fill.py

echo "== note"
cd "$ROOT/writing"
pdflatex -interaction=nonstopmode housing_first_children_later.tex > /dev/null
pdflatex -interaction=nonstopmode housing_first_children_later.tex > /dev/null
echo "   wrote writing/housing_first_children_later.pdf"

echo "== checking that nothing in the prose is typed"
python3 check_numbers.py

echo "== checking that every acronym is defined on first use"
python3 check_acronyms.py

echo "== checking the hyphenation of compound modifiers"
python3 check_hyphens.py

echo "== checking that no two words have run together"
python3 check_spacing.py

# THE SET COLUMN AGAINST THE CODE, AND NOT BY EYE. links.py says the mapping is
# "checked by eye once", and TRANSITION_LESSONS records the same check as a
# standing instruction after rho_d was found holding a moment h_2 had taken. An
# instruction to read carefully passes once and then rots: delta_h sat marked
# Int. in Table 11, with its target constant declared in the Fortran and used
# nowhere, while penalty_child_homeless was a compile time parameter that no
# update touched. Nothing re-read the instruction, so nothing caught it. This
# runs every build instead.
echo "== checking the tables' Set column against what the code calibrates"
python3 ../paper/check_alignment.py

echo "== verifying the model"
cd "$ROOT/code/stylized"
python3 verify.py
