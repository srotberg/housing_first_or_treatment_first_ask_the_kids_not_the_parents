# drug price path seed for T=45, periods 1 to 44.
#
# PROVENANCE, CORRECTED. The first version of this header said the whole file
# was "the measured supply curve evaluated at a T=60 no-grandfathering run's own
# allocation ... not a shape chosen here". That is true of 20 of the 44 entries
# and false of the other 24. Quoting the original's own words, as it asks:
#
#   drug_price_path_seed_t60.txt: "t=1..20 are the T=30 run's measured secant
#   roots verbatim, t=21..59 are 0.83349 + 0.03940*0.894614^(t-20), a
#   CONSTRUCTION and not a measurement."
#
# THERE HAS NEVER BEEN A T=60 NO-GRANDFATHERING RUN. drug_price_path_seed_t60_
# nogf.txt is a pinned, byte-identical copy of the shared T=60 file, taken so
# the arms could diverge later; the "nogf" in its name marks which arm may READ
# it, not which arm produced it.
#
# So:
#   t = 1..20   MEASURED. The T=30 run's two-point secant roots, verbatim.
#   t = 21..44  CONSTRUCTED. A geometric decay onto the terminal price, its rate
#               pinned on lambda_d's own path. Checked here: every entry sits
#               within 3.5e-6 of the closed form.
#
# WHAT THIS MEANS FOR READING A RUN SEEDED HERE. A small loop-0 residual in the
# TAIL is partly circular -- the decay was chosen to land on the terminal value,
# so the residual there measures distance from that choice, not evidence about
# the economy. Residuals at t=1..20 carry no such circularity. It remains a far
# better seed than a linear ramp; what it cannot do is testify about its own
# tail.
