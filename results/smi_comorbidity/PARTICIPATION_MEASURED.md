# PARTICIPATION MEASURED: 99.75 PER CENT OF SMI HOUSEHOLDS BUY, AND BOTH OF MY
# INFERENCES WERE WRONG

`b_smi_multiple = 1e-12`, block 1, read off the model:

    MOMENT u_any   share buying:        SMI 0.99752    non-SMI 0.12759
    MOMENT u_exp   experimenters only:  SMI 0.76999    non-SMI 0.07091
    MOMENT r_smi   SUD ratio                    4.01404   target 7.30

    raw masses  exp_smi 1.79843676  exp_pop 5.24136191  sud_smi 0.53142710
                sud_pop 3.28383313  mass_smi 2.33565407 mass_pop 50.89340573

The author said every household with income should buy once abstaining costs 170
times using, and 81 per cent of them are employed. They were right: essentially
all of them buy. **My two inferences from stocks, 0.59 and 0.34, were both
wrong**, and the 0.34 was the one offered most confidently.

## THE DECOMPOSITION, AND IT IS EXACT

    SUD | SMI, conditional on buying      0.53142710 / 2.32986386 = 0.22809
    SUD | non-SMI, conditional on buying  2.75240603 / 6.19533116 = 0.44428

    r_smi = participation ratio x conditional ratio
          =   0.99752/0.12759  x   0.22809/0.44428
          =        7.8181      x        0.51340        =  4.01404   (checks)

**PARTICIPATION ALREADY DELIVERS 7.82, ABOVE THE 7.30 TARGET.** The drag is
entirely the second term. Conditional on using, an SMI household is HALF as
likely to carry the disorder as a non-SMI user.

## WHY THE SECOND TERM IS BELOW ONE, AND WHY `b` CANNOT FIX IT

Onset is common -- flat at 0.0336 for any positive quantity, no SMI term. So the
difference is exit, and backing it out of the stationary shares gives

    exit | SMI users      0.0336*(1-0.22809)/0.22809 = 0.1137
    exit | non-SMI users  0.0336*(1-0.44428)/0.44428 = 0.0421

SMI users leave the disorder 2.7 times faster. That is backwards from the
dual-diagnosis evidence the paper cites, and it is SELECTION rather than
preference: at 1e-12 the SMI user pool is 99.75 per cent of SMI households,
including the 81 per cent who are employed and housed, while the non-SMI user
pool is the self-selected 12.76 per cent who are poorest, most homeless and
heaviest. A whole population is being compared against another population's
worst tail.

**SO THE TWO TERMS MOVE AGAINST EACH OTHER.** Every further cut in `b_smi` drags
one more LOW-RISK SMI household into use: participation rises and the
conditional ratio falls by almost exactly as much, and the product sits at 4.
That is the mechanism behind the flat ladder, and it is why 0.001, 1e-5 and
1e-12 settle within 0.16 per cent of each other.

It does NOT follow that nothing can reach 7.30. It follows that PARTICIPATION IS
THE WRONG LEVER -- it is already over-delivering. The second term has to go from
0.513 to about 0.93, and two things do that:

  - **`mu_m` below one**, which acts on the exit hazard directly. It is the
    parameter that exists for exactly this and it is both set to one and unwired
    at eleven of its fifteen call sites;
  - **`kappa_uem`**, which makes SMI households genuinely jobless and poor, so
    their user pool resembles the non-SMI user pool in risk and the conditional
    ratio rises on its own with no preference change at all. It sits at 1.0554
    where one is no penalty, its adjuster is zero in the declaration, and
    employment given SMI reads 0.80731 against a target of 0.30000.

`uem_probe` is testing the second at `kappa_uem = 23.5`, the value the source's
own note quotes, with `zeta_DI` back at zero on the author's instruction.

## THE WIRING SURVEY FOR `mu_m`, DONE BUT NOT APPLIED

Eleven sites pass seven arguments where eight are needed, in two families: seven
in the value function ending `,1,treatment_choice_now)` and four in the
distribution ending `,0,treatment_choice_dist_1)`. Every one of them is enclosed
by a `do unemployment_index=` loop -- at 25265 for the first seven, and at
32597, 33103 and 33974 for the rest -- so `smi_of(unemployment_index)` is the
household's own CURRENT SMI state at each, which is what `mu_m` needs and what
the four already-wired sites use. Ten of the eleven also sit inside a
`future_unemployment_index` loop, which is the inner one and the wrong variable.

Nothing is wired yet. It changes every solved point, the benchmark of record and
the transition, so it waits on the author.
