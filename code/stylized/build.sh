#!/bin/sh
# Rebuild the stylized model note from nothing.
#
#   calibrate.py  three parameters on three targets  ->  calibrated.json
#   run.py        the two figures                    ->  writing/figures/
#   tables.py     all four tables                    ->  writing/tables/
#   pdflatex      twice, for the cross references    ->  writing/stylized_note.pdf
#
# ablate.py is NOT run here. It recalibrates the whole model once per component
# and takes about an hour; run it by hand when a component changes.
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

echo "== note"
cd "$ROOT/writing"
pdflatex -interaction=nonstopmode stylized_note.tex > /dev/null
pdflatex -interaction=nonstopmode stylized_note.tex > /dev/null
echo "   wrote writing/stylized_note.pdf"
