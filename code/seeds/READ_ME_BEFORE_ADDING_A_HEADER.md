# THE DRUG PRICE SEED CAN HAVE A COMMENT HEADER. MEASURED THREE WAYS.

21 September 03:35. This file previously said the opposite -- that the drug price
reader is list-directed, that a `#` makes it read zero entries, and that two
committed seeds "were unreadable and fell back to the linear ramp in silence".
That is not what the source does. Rewritten rather than amended, because a
convention file that is wrong is worse than none.

## WHAT THE READER ACTUALLY IS

There is exactly ONE place the drug price seed is opened -- line 53775 -- and it
reads as character, exactly like the other three:

    read(97,'(A)',iostat=seed_iostat_1) seed_line_1
    seed_line_1=adjustl(seed_line_1)
    if (len_trim(seed_line_1)==0) cycle
    if (seed_line_1(1:1)=='#') cycle
    read(seed_line_1,*,iostat=seed_iostat_1) seed_value_1

The comment directly above it says why, and says it in the past tense:

> A '#' LINE MUST NOT END THE READ. save_transition_paths.py writes a provenance
> header [...] and **the list read that used to be here** would have taken the
> first '#' as a bad record, exited, and fallen back to the ramp having read
> ZERO.

The list-directed reader is the one that was REPLACED. All four readers already
agree.

## THE THREE MEASUREMENTS

**1. The live run.** `hftf` T=45 started 02:49 and staged a copy of
`drug_price_path_seed_t45.txt` carrying a 7-line `#` header. Its log:

    DRUG PRICE PATH seeded FROM FILE, entries read=  44  of  44
    DRUG PRICE PATH seeded: t=0 1.0000  t=1 0.92738703  t=T 0.83283631757376753

Not the ramp. The ramp's t=1 would be near 0.99.

**2. The reader's own logic, standalone**, compiled against that same headered
file: `entries read = 44  last = 0.83621084940408597`.

**3. The naive list read**, for comparison -- `read(97,*,iostat)` with no comment
handling, which is what a test reproduces if it copies the OLD reader:
`naive list read entries = 0`.

**Zero is the number the previous version of this file reported.** It is the
right answer to a different question: what the reader used to do, not what it
does.

## SO THE CONVENTION IS THE ONE THE PROJECT ALREADY HAD

**A seed carries its own provenance header, and the reader skips it.** That is
what `save_transition_paths.py` writes, what the reader was deliberately changed
to accept, and what stops the failure this project has paid for repeatedly -- a
file of numbers whose meaning lives somewhere else and drifts from it. The
`kappa_x` case is the canonical one: 0.002 in a seed whose README said 0.8139.

`drug_price_path_seed_t45.txt` therefore carries its header again.
`drug_price_path_seed_t60_nogf.txt` was stripped in the same commit and is left
as it is, with its `.provenance.md` beside it; it is readable either way and it
is not this session's file to move back.

## WHAT TO DO IF YOU SUSPECT A SEED IS NOT BEING READ

Do not reconstruct the reader. **Read the log line** -- `entries read= N of M`
is printed on every run and is the whole answer -- and if you want a standalone
test, copy the read statement out of the source at the line the `open` is on,
rather than from memory or from a generated `tr.f90` of an older build.
