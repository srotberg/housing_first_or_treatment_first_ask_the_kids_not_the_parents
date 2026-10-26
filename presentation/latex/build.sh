#!/bin/sh
# Build the Beamer slides: pdflatex twice (the slide count in the footer needs two passes).
# Writes presentation/housing_first_or_treatment_first_slides.pdf.
set -e
cd "$(dirname "$0")"
for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error slides.tex > build.log 2>&1 || { tail -30 build.log; exit 1; }; done
cp slides.pdf ../housing_first_or_treatment_first_slides.pdf
rm -f slides.aux slides.log slides.nav slides.out slides.snm slides.toc slides.vrb slides.pdf build.log
echo "built ../housing_first_or_treatment_first_slides.pdf"
