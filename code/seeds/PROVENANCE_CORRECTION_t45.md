# THE T=45 SEED'S TAIL IS A CONSTRUCTION, NOT A MEASUREMENT

21 September. Raised by the session that wrote the file it descends from, because
the claim is about that file and the authoritative statement is its own header.

## THE CLAIM

`seeds/drug_price_path_seed_t45.txt` says:

> SOURCE: seeds/drug_price_path_seed_t60_nogf.txt, first 44 entries, verbatim.
> It is the measured supply curve evaluated at a T=60 no-grandfathering run's
> own allocation, period by period -- **not a shape chosen here.**

## WHY IT IS WRONG FOR 24 OF THE 44 ENTRIES

`drug_price_path_seed_t60_nogf.txt` is a pinned copy of
`drug_price_path_seed_t60.txt` -- byte-identical over all 59 numeric entries,
checked, and its own header says so. And that file's header says what it is:

> t=1..20 are the T=30 run's measured secant roots verbatim, t=21..59 are
> 0.83349 + 0.03940*0.894614^(t-20), a CONSTRUCTION and not a measurement.

**There has never been a T=60 no-grandfathering run for those entries to be
measured from.** At the time the T=45 seed was written, no T=60 transition of
either arm had produced a path: this session's T=60 grandfathered run has not been
launched, and it is the only T=60 that has been staged.

Entries 1 to 20 ARE measured -- the T=30 run's two-point secant roots, every root
strictly inside its own bracket. Entries 21 to 44 are a geometric decay whose rate
was pinned on lambda_d's own path, which is a defensible construction and is
labelled as one, but is a shape chosen by this session.

## THE ARITHMETIC THAT SETTLES IT

The T=45 seed's own evidence is its entry 44, quoted as 0.83621 and offered as
showing "the tail arrives where T=45's boundary condition sits". That entry is
0.836210849404086, and

    0.83349 + 0.03940 * 0.894614^(44-20) = 0.836211

to six decimal places. **The number cited as evidence of a measurement is the
closed form of the construction**, evaluated 24 periods into the decay.

## WHAT IS AND IS NOT AFFECTED

This does not make the T=45 seed a bad seed. A lambda_d-pinned decay onto the
right terminal value is a reasonable guess and far better than a linear ramp, and
the tail genuinely does arrive near the boundary condition -- by construction,
which is why it does.

What it affects is what may be CONCLUDED from a run seeded with it. A path seeded
from a measurement of a comparable economy can have its loop-0 residuals read as
evidence about that economy. A path seeded from a construction cannot: the residual
measures the distance from my guess, and the guess was chosen to land on the
terminal value, so a small residual in the tail is partly circular.

## THE GENERAL SHAPE, which this project has now paid for three times today

A provenance claim drifted one hop from its source and inverted. The chain was
correct at every link and wrong end to end:

    my file        "a CONSTRUCTION and not a measurement"      correct
    the pinned copy "byte-identical to the shared file"         correct
    the T=45 seed   "the measured supply curve ... not a shape chosen here"  WRONG

Nobody misread anything; the last step simply did not re-read the first. The same
shape as `drug_market_adjuster` living in prose rather than in the script, and as
`kappa_x` at 0.002 in a seed whose README says 0.8139.

**A file's provenance note should name the measurement or say "constructed", and a
copy of a copy should quote the original's own words rather than paraphrase them.**
