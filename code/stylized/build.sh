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
# check_numbers.py has to run after the fill, because it reads the filled file.
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

echo "== verifying the model"
cd "$ROOT/code/stylized"
python3 verify.py
