#!/bin/sh
# Build the four response letters. Run from this directory.
set -e
cd "$(dirname "$0")"
for f in response_editor response_AE response_R1 response_R2 response_R3; do
    pdflatex -interaction=nonstopmode -halt-on-error "$f.tex" > /dev/null
    pdflatex -interaction=nonstopmode -halt-on-error "$f.tex" > /dev/null
    echo "built $f.pdf"
done
rm -f *.aux *.log *.out
