# drug price path seed, T=60, NO GRANDFATHERING arm.
#
# A PINNED COPY of drug_price_path_seed_t60.txt as of 36f5dfd, taken
# because the shared file is about to stop being arm-agnostic.
#
# results/transition_t60_gf/CONTROL.md states that grandfathering leaves
# about 7.1 per cent exempt, that b rose 21.7 per cent against arm 3's
# transition at T=5, and that the grandfathered price path should
# therefore sit ABOVE this one -- roughly +6 per cent by the elasticity
# chain, to be MEASURED by that arm's T=5 probe and shifted 'on that, or
# not at all'. If that shift lands in the shared file, the no-
# grandfathering arm must not read it: a price path built for an economy
# with 7.1 per cent of the population exempt is the wrong seed for one
# where nobody is, and as a column of numbers it is indistinguishable.
#
# Content is byte-identical to the shared file at 36f5dfd: t=1..20 are
# the T=30 run's measured secant roots verbatim, t=21..59 are
# 0.83349 + 0.03940*0.894614^(t-20), a CONSTRUCTION and not a
# measurement. t=60 is not in the file; the code pins it to arm 3's
# cleared 0.833490.
