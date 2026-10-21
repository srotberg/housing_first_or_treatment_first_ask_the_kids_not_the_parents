# Housing First or Treatment First? Ask the Kids, Not the Parents

Replication material for **"Housing First or Treatment First? Ask the Kids, Not the Parents"** by Shahar Rotberg
(Canada Mortgage and Housing Corporation). Contact:
[shahar.rotberg@gmail.com](mailto:shahar.rotberg@gmail.com) ·
[www.shaharrotberg.com](http://www.shaharrotberg.com)

## What is here

| Folder | Contents |
| --- | --- |
| `code/` | The Fortran source that solves and calibrates the quantitative model, plus engineering notes. Start with `code/readme.txt` for how to compile and run it. |
| `writing/` | The paper and its predecessors. `writing/housing_first_or_treatment_first_ask_the_kids.src.tex` is the live source; `writing/housing_first_or_treatment_first_ask_the_kids.pdf` is the current build. |
| `data/` | Stata and text code that produces the calibration targets from the public microdata, with a README of its own. |
| `output/` | Saved simulation output from benchmark and counterfactual runs. |
| `related_lit/` | Notes on the literature the paper draws on. |
| `RED_reviews/` | Referee reports and response material from the earlier round. |

## The two models

The paper carries two models, and the distinction matters for reading the code.

A **stylized two period model**, in Section 3 of the paper, is stripped to the
point where its main result can be proved rather than computed, and where the
intergenerational externality can be switched on alone with everything else held
fixed. Its code is in `code/stylized/`.

A **quantitative general equilibrium life cycle model**, in Section 4, puts the
same mechanism in an environment that can be taken to the data: six state
variables and fifty three parameters, with endogenous homelessness, drug use,
disorder, recovery, serious mental illness, employment, mortality, a drug market
that clears, and a government budget that balances. Its code is
`code/housing_first_or_treatment_first_SR_v1.f90`.

## Building the paper

The source uses placeholders of the form `@@name@@` for every number the stylized
model produces, so that no model output is typed by hand. Filling them and
building takes two steps:

1. substitute the values into `writing/housing_first_or_treatment_first_ask_the_kids.tex`;
2. run `pdflatex` twice, so that references and the table of contents resolve.

The committed `writing/housing_first_or_treatment_first_ask_the_kids.tex` is the filled version, so `pdflatex housing_first_or_treatment_first`
twice reproduces the PDF as it stands.

## Compiling and running the model

Full instructions are in `code/readme.txt`. The short version:

```
gfortran housing_first_or_treatment_first_SR_v1.f90 \
    -mcmodel=medium -fopenmp -O2 -ffree-line-length-none \
    -o hftf
ulimit -s unlimited
export OMP_NUM_THREADS=4 OMP_STACKSIZE=512M
./hftf
```

Two of those settings are not optional. `-mcmodel=medium` is needed because the
static arrays exceed the small code model's limit. `ulimit -s unlimited` together
with `OMP_STACKSIZE=512M` is needed because the parallel region allocates large
automatic arrays per thread; without them the run dies partway through a backward
induction with no error message at all. `code/PERFORMANCE_NOTES.md` section 14
documents how that was diagnosed.

The run writes a checkpoint after every calibration loop, so a run that is
interrupted can be resumed by leaving `calibration_state.dat` in the working
directory. Deleting it starts from the declared parameter values.

## Engineering notes

`code/PERFORMANCE_NOTES.md` is a running record of what was measured, what was
wrong, and what was tried and rejected. It is worth reading before changing the
solution method, because several of the obvious optimisations have already been
tested and do not work. Sections 11 and 15 are the ones to read first: the asset
lottery that would have let the asset grid be cut is off, because it moved
expected savings without moving consumption and so violated the household budget
constraint by a measurable amount.
