# `b_smi_multiple = 0` IS A CRASH, NOT A CORNER. THE POINT IS VOID

The author's mechanism is right: at `b_smi = 0` flow utility is `(0+v)^phi_q`,
so `v = 0` gives an index of zero and `u = -1/X` is minus infinity, and every
SMI household must choose `v > 0`. The model cannot REPRESENT that choice, and
the source said so before the run, at the floor it was built with:

    ! b_smi_multiple at or below zero sends flow utility to minus infinity
    ! for every SMI household at q = 0, which is a crash rather than a corner.

## WHAT THE RUN ACTUALLY PRODUCED

    model_value_of_life(1)                                        NaN
    distance_value_of_life                                        NaN
    VALUE OF LIFE FLOOR BINDS: the worst-off household values a
      period of life at                                     -Infinity
      and 2.3364912205987736 of mass is below zero
    model_average_rental_unit_size/model_average_owner_occupied    Infinity
    model_fraction_homeless                                       0.93797
    model_fraction_addicted+model_exprimenters                    0.93224

An economy with 94 per cent of households homeless and 93 per cent using is not
an economy. `MOMENT r_smi` printed 0.1772 and the decoded split reads

                              non-SMI       SMI
    never had a SUD            0.5924     0.9170
    recovered from a SUD       0.0793     0.0248
    has a SUD now              0.3283     0.0582

which has SMI households with a SIXTH the disorder rate of everyone else, the
opposite of every other point measured. **None of it is a number. The point is
void and nothing from it is quoted.**

## WHY THE SINGULARITY BREAKS THE SOLVE RATHER THAN CORNERING IT

The value function is minus infinity on part of the state space, so the solver
has nothing to compare: `Inf` propagates into the value-of-life aggregation,
into the productivity floor that is supposed to rescue households valuing life
below zero, and into the housing ratios. The floor at 1e-6 exists precisely to
keep the model on the side of that where a comparison is still defined.

## THE VALID VERSION OF THE SAME EXPERIMENT IS `1e-12`

At `b_smi_multiple = 1e-12` the shifter is 4.9e-15 and an abstaining SMI
household's Cobb-Douglas factor is `b^-phi_q` = 230 against 1.37 for a
household buying the usual quantity -- abstaining is 170 times worse, which is
the author's "infinitely costly" in every way that matters to a household's
ranking, without a singularity for the solver to trip over. That run carries
zero `NaN` and zero `Infinity` in its log and is converging normally.

The prediction in `B_ZERO_PREDICTION.md` stands and is tested against THAT
point: `r_smi` near 6.2 means everyone who can buy did and the onset/exit
balance is the ceiling; materially below 6 means a large share of SMI
households cannot buy at any price, and `zeta_DI = 0` becomes the question.
