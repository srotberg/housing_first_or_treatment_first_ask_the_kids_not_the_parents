#!/bin/sh
# Build the Beamer slides: fill the paper's numbers into slides.src.tex (fill_slides.py writes slides.tex and the
# gen_*.tex tables), then pdflatex twice (the slide count in the footer needs two passes).
# Writes presentation/housing_first_or_treatment_first_slides.pdf.
set -e
cd "$(dirname "$0")"
python3 fill_slides.py
for i in 1 2; do pdflatex -interaction=nonstopmode -halt-on-error slides.tex > build.log 2>&1 || { tail -30 build.log; exit 1; }; done
grep -E '^(Overfull|Underfull) \\hbox' build.log | sed 's/^/  /' | head -20 || true
cp slides.pdf ../housing_first_or_treatment_first_slides.pdf
rm -f slides.aux slides.log slides.nav slides.out slides.snm slides.toc slides.vrb slides.pdf build.log
echo "built ../housing_first_or_treatment_first_slides.pdf"
