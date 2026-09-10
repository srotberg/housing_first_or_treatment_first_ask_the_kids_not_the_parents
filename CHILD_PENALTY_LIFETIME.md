# The child's inherited penalty as a state

The author, 10 September: *"you can basically have another state var: 1,2, 3,
where 1 is a child of a panret with SUd, 2 is for a child with parent who was
homeless, and 3 is for a child of a parent with both. and each of these reduces
the productivity of the child in each y productivity it lives"*, and *"you dont
need move productivity grids....you have 7 like before. and then you multiple
the actual productivity by the penalty for each case (1/2/3)"*, and *"1. i want
the persistence to be lifetime persistence (including in retirement)"*.

## Why the old penalty was worth a fraction of its stated size

It was a level shift applied ONCE, to the newborn's productivity draw. The AR(1)
that carries productivity through life then pulled it back toward the mean at
`persistence_employment_surviving = 0.9`. The present value of a shift that
decays at 0.9 over a forty year working life is 41 per cent of a shift that does
not, so a nominal 24 per cent penalty was worth an effective 10.7 per cent, and
the child disorder ratio it had to explain came out at 1.114 against a target of
2.0.

A permanent multiplicative factor cannot be carried by a process whose only
persistence is 0.9. It needs its own index.

## How it is built

`child_penalty_classes` (compile time, 1 = off, 4 = on) and
`employment_base_size = 7`, with

    employment_grid_size = employment_base_size * child_penalty_classes

The class is FOLDED INTO the productivity index rather than added as a new array
rank: index `(c-1)*7 + k` is base node `k` scaled by `child_penalty_factor(c-1)`.
The value function and the distribution are rank seven and every one of the
hundreds of index sites would have had to change for a new rank; folded this
way, every existing `employment_grid(age,employment_index)` site is correct with
no edit at all, because the grid it reads already has the penalty in it.

  * `employment_process` is BLOCK DIAGONAL, so a household never changes class.
    The base block is copied unchanged, which is the author's *"the productivity
    process is the exact same, but there is an indicator"*.
  * the class is assigned at birth from the parent's state at DEATH,
    `c = d_index + 2*(h_index-1)`, which is where `newborn_employment_probability`
    was already indexed and is what TRANSITION_LESSONS requires.
  * the birth shift is DROPPED when the classes are on. Applying both would
    count the penalty twice.
  * the intergenerational AR(1) still reads the parent's ACTUAL productivity,
    penalty included, so a penalty echoes into the grandchild through the
    parent's lower earnings at `rho_intergenerational` and dies out from there.
    It is the class indicator, not this, that makes it permanent within one life.
  * retirement is covered for free: the social security PIA formula reads
    `employment_grid(life_span-retirement_span,employment_index)`, so a penalised
    household carries lower career-average earnings into retirement and is
    caught by the SSI floor rather than by the bend points.

## What it costs

The state space, and so the solve, is `child_penalty_classes` times bigger. At
one class the model is exactly the one that came before.

## The two nulls

  * STRUCTURAL: `child_penalty_classes = 1` must reproduce the benchmark exactly.
  * REPLICATION: `child_penalty_classes = 4` with `include_child_penalty = 0` is
    four identical copies of one economy and must reproduce the one-class run
    with the penalty off.

## Three defects the packing exposed, all live before it

None of these is a consequence of the child penalty. All three were in the model
already and the packing is what made them visible.

| site | what it did |
| --- | --- |
| `financial_grid(financial_grid_size)` | the top of the asset grid was `max_times_labour_income_saved*employment_grid(1,employment_grid_size)`. With classes that is the top node of the LAST class, factor `(1-delta_d)(1-delta_h)`, so the highest asset a household may hold would have been cut by about half -- a change to the wealth distribution and to beta with nothing in the output to say so. |
| the BLS separation profile | it maps education onto productivity by walking the cumulative ergodic mass, and that mass is carried entirely by the base block. Walked over all packed nodes the cumulative sum stops advancing after node 7, every penalised node finds zero overlap with every education group, and the fallback hands all of them a separation multiplier of exactly one -- so the POOREST households in the economy would face the AVERAGE job-loss rate while their unpenalised twins at the same base node faced 2.57 times it. |
| `homeownership_by_employment`, `housing_size_by_employment`, `mass_by_employment_and_tenure` | unguarded `x/mass`. Fine at seven populated nodes; 0/0 at twenty-eight, which is a NaN under -O3 and a trap under the standing -ffpe-trap build. |

## One judgment call, recorded rather than buried

`unconditional_employment_probability` carries the BASE block only, so
`sigma_y`'s bottom half earnings share measures the productivity PROCESS and
does not move when the disorder rate moves. The share of children actually born
into each class is an equilibrium outcome, not a property of the process; the
realised shares are printed as `DIAG child-class mass` instead. Folding them in
would make `sigma_y`'s own moment a function of `b`.
