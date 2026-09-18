# The child homelessness odds ratio: what the model reports, and what the data say

Written 18 September, for the writing stage. The author: *"I need the
homelessness odds ratio when I give the untargeted moments... It's fine we can
put the 1.8-2.4 and show what the model gives"*, and *"It's ok. The model won't
be perfect!"*. So the decision is taken: the ratio is REPORTED as untargeted
beside the 1.8 to 2.4 range, and nothing is refit to close it. This file is the
evidence behind that sentence, not a proposal to change it.

## The model reports 4.5 to 5.2 against a target of 2.10

n75, two classes, `penalty_child_homeless` = 0:

    block 1   5.2227
    block 2   4.5345

Both are transients on a filling class, so the level is provisional; the
magnitude is not in doubt.

## THE TWO NUMBERS ARE NOT THE SAME OBJECT, and this is the substance

`penalty_child_homeless` (delta_h) IS ZERO in the frozen calibration -- verified
in n76's handover. So the entire 4.5 to 5.2 comes from
`rho_intergenerational` = 0.50, with no housing-specific penalty at all.

The reason it can: at line 10339 the child's productivity node is drawn
CONDITIONAL on the parent's node,

    chom_n_1 = chom_n_1 + newborn_parent_share(cp_index_1,0,2) *
               newborn_employment_probability(k_1,cp_index_1,0,2) *
               percent_homeless_by_employment(1,k_1) / csud_w_1(0,2)

and the comment above it says this was the point: *"the disordered and the clean
sit at different nodes, and it is precisely that difference -- income
persistence -- that used to be missing and that these ratios are now meant to
split from the direct penalty."*

A ratio that carries the parent-child income correlation is a GENERAL POPULATION
ratio. Bassuk et al. (1997) compares 220 homeless mothers with 216 LOW-INCOME
HOUSED mothers precisely so that the poverty is common to both arms and drops
out. So the model's reported quantity is the like-for-like counterpart of
Flatau's 5 to 6, and Bassuk's 2.1 is the selection-purged lower bound of the
same object.

NOTE FOR WHOEVER EDITS THE APPENDIX. `data/DATA_APPENDIX.md` line 238 still says
Bassuk "isolates transmission from the poverty that accompanies it" and that the
model "computes transmission alone ... holding the distribution it is drawn from
fixed". That was true before the conditional draw was added and is no longer a
description of what the Fortran computes. It was left alone deliberately rather
than rewritten unasked.

## The literature, and what each one actually measures

| study | estimate | exposure -> outcome | poverty adjusted |
|---|---|---|---|
| Bassuk et al. (1997), AJPH 87(2):241-248 | OR 1.80 female caretaker, 2.41 male, midpoint **2.1** | parent homeless -> homeless | yes, poor vs poor |
| Bassuk, same table, foster-care row | OR **2.67** [1.49, 4.80] | foster care -> homeless | yes, poor vs poor |
| Flatau et al. (2013), AHURI Final Report 200 | 43.0 per cent of non-Indigenous clients had homeless parents; implies **5 to 6** | parent homeless -> homeless | NO, population base |
| Danish register, out-of-home care, Lancet Reg Health Eur (2025) | adjusted HR **11.8** male, **19.3** female | care placement -> homelessness | yes -- birth year, parental sociodemographics, psychiatric disorders |
| Herman, Susser, Struening and Link (1997), AJPH 87(2):249-255 | OR **13** lack of parental care, **16** physical abuse | childhood adversity -> homelessness | no; n=92 vs 395 |
| Danish register, offspring psychiatry | IRR 2.5 mother, 2.3 father, 2.8 both | parent homeless -> PSYCHIATRIC DISORDER | partly |
| childhood homelessness, commonly cited | OR about 1.4 | homeless as child -> homeless adult | no |

THE LAST ROW BUT ONE IS A TRAP. The 2.5 / 2.3 / 2.8 triple circulates without its
outcome attached and reads as a homelessness transmission estimate. It is not:
the outcome is any psychiatric disorder. Do not put it in the homelessness row.

## What this supports in the paper, and what it does not

SUPPORTED: that 2.1 is the low end of this literature rather than its centre,
because it is the one design that strips poverty out; that poverty-adjusted
designs with a different exposure run far above it; and that the model's own
number is the persistence channel with delta_h contributing nothing.

NOT SUPPORTED: quoting 4 to 5 as an estimated parent-to-child homelessness
transmission ratio. No study found reports one. The closest is Flatau's implied
5 to 6, and that carries selection as well as transmission -- Cobb-Clark and Zhu
(2015) size the contamination, with those first homeless as children more than
twice as likely to have been in foster care.
