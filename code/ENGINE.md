# A GUARD THAT COUNTS CANNOT TELL "ALREADY DONE" FROM "NO LONGER MATCHES", 24 September 02:41

The transition worker found this in our own build tooling and fixed it, and the
rule generalises well beyond the seven scripts it touched.

The transition build scripts guarded themselves by COUNTING the diff lines
between the tracked source and the sed-generated copy. A count cannot separate
two states that look identical to it: the sed applied cleanly, or the source
already carried the value and the sed matched nothing. Only one of those is
safe.

It was measured rather than argued. Moving the horizon literal from 30 to 60 in
a scratch source and running all seven scripts: six refused, and
`build_transition.sh` BUILT -- it had no horizon sed at all, so it inherited the
source's 60 while its own heading and closing message still said 30. That is
exactly the silently-wrong-horizon failure the guard exists to prevent, and the
guard waved it through.

**ASSERT EVERY SWITCH BY VALUE IN THE GENERATED FILE.** Not by diff count, not
by "the sed returned 0". And require the diff to contain NOTHING BUT the lines
the script is allowed to touch, printing the offending line when it does not --
a count can refuse, but it cannot say what it refused over. This is the rule the
repository already applied to `grandfather_voucher_states` and
`window_distributions`; it simply had not been carried across.

## AND THE .f90 DOES NOT HAVE TO BE EDITED AT ALL

I had authorised two edits to the tracked source -- `solve_transition_dynamics`
to 1 and the horizon literal to 60 -- because both are `integer, parameter` and
neither is a handover name, so I could see no other way to stand up a
transition. The worker found the better answer: the build scripts SED THE
TRANSITION-ENABLED SOURCE INTO A BUILD DIRECTORY, so the tracked model is never
touched.

That authorisation is therefore withdrawn as unnecessary. It matters because a
tracked source with transitions switched on would be pulled by the
counterfactual workers and silently build a different model on their next
compile. Generate into a build directory; do not edit the model in place.

