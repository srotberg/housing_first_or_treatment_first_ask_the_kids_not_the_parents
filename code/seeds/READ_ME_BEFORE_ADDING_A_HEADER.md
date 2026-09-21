# THE DRUG PRICE SEED CANNOT HAVE A COMMENT HEADER. THREE OTHER SEEDS CAN.

21 September, found while staging a no-grandfathering control and fixed in the
same commit. Two committed seeds were unreadable and fell back to the linear ramp
in silence.

## THE ASYMMETRY, WHICH IS THE WHOLE PROBLEM

Four path seeds are read by the transition, and the readers are not the same.

    drug_price_path_seed.txt    unit 97, ~53525   read(97,*) seed_value_1
                                LIST-DIRECTED. No comment handling at all.
    pi_v_path_seed.txt          unit 96, ~53862   read(96,'(A)') seed_line_1
    rent_path_seed.txt          unit 94, ~54002   read(94,'(A)') seed_line_1
    lump_sum_path_seed.txt      unit 94, ~54048   read(94,'(A)') seed_line_1
                                CHARACTER, then adjustl, then
                                  if (len_trim(...)==0) cycle
                                  if (seed_line_1(1:1)=='#') cycle

So three of the four skip blank lines and `#` comments, and the oldest one --
the drug price, the seed that matters most -- does not. A convention was
established for the newer seeds that the original reader does not honour.

## WHAT IT COSTS, AND IT IS SILENT

A `#` is not a valid real, so the list-directed read returns `iostat/=0`, the loop
`exit`s at the FIRST line, and `seed_count_1` is zero. The code then keeps the
linear ramp for every period and says so in one line:

    DRUG PRICE PATH seeded FROM FILE, entries read= 0 of 44
      SHORT FILE. periods 1 to 44 keep the ramp.

That is the silent half-failure `results/transition_t60_gf/CONTROL.md` already
warned about -- "a short seed file is a silent half-failure ... the count in the
log is the only check" -- and the ramp is expensive. `CALIBRATION_RECIPE.md`
measures it at T=30: the faced price walks from 0.994 toward 0.78 at half a per
cent a loop, "so about forty loops, and a transition loop is not four minutes
like a steady state's but closer to three hours".

## MEASURED, NOT ASSUMED

A five-line Fortran program using the drug-price reader's own read statement:

    with the committed header      entries read= 0 of 4
    headerless                     entries read= 4 of 4

## THE TWO FILES THAT WERE BROKEN, AND THE FIX

    drug_price_path_seed_t45.txt        28 comment lines, 44 numeric   -> ramp
    drug_price_path_seed_t60_nogf.txt   20 comment lines, 59 numeric   -> ramp

Both now hold numbers only and both read 4 of 4. Their provenance is preserved
verbatim beside them, as `<name>.provenance.md`, which is where it should have
been: a file the model parses is not the place for documentation the model cannot
parse.

Unaffected, checked rather than assumed: `pi_v_path_seed_t30.txt` (3 comment
lines) is read by the character reader and is fine, and `h1_path_reference_t30.txt`
has no reader at all -- only a writer, `h1_path_reference_out.txt` at ~55010 -- so
it is a reference file and its header is harmless.

## THE BETTER FIX IS IN THE SOURCE, AND IT IS NOT THIS SESSION'S TO MAKE

Three readers already do exactly the right thing. Giving the drug-price reader the
same four lines -- character read, `adjustl`, skip blank, skip `#` -- removes the
trap rather than working around it, and would let every seed carry its own
provenance. That is a source change to a frozen model and belongs with whoever
owns the transition's readers.

Until then: **the drug price seed holds numbers and nothing else.** If a header is
wanted, put it in a sidecar.
