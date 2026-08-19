#!/bin/sh
# Rebuild the stylized model note from nothing.
#
#   calibrate.py  four parameters on four targets    ->  calibrated.json
#   run.py        the two figures                    ->  writing/figures/
#   tables.py     all four tables                    ->  writing/tables/
#   pdflatex      twice, for the cross references    ->  writing/housing_first_children_later.pdf
#
# ablate.py is NOT run here. It recalibrates the whole model once per component;
# run it by hand when a component changes. The two period model is roughly ten
# times faster than the three period one, so it is minutes rather than an hour.
#
#   sh build.sh

set -e
cd "$(dirname "$0")"
ROOT=$(cd ../.. && pwd)

echo "== calibrating"
python3 calibrate.py

echo "== figures"
python3 run.py

echo "== tables"
python3 tables.py

echo "== welfare"
python3 welfare.py

echo "== children"
python3 children.py

echo "== filling the note"
python3 fill.py

echo "== note"
cd "$ROOT/writing"
pdflatex -interaction=nonstopmode housing_first_children_later.tex > /dev/null
pdflatex -interaction=nonstopmode housing_first_children_later.tex > /dev/null
echo "   wrote writing/housing_first_children_later.pdf"
