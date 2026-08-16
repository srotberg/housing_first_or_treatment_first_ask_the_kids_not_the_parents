# Round 1 response letters

Draft responses to RED-D-26-00078. Five letters, four of them comment by comment.
Everything we say back to a referee is in **red**; the black italic block above
each response is the referee's own text.

| file | covers |
|---|---|
| `response_editor.tex` | Cover letter to Karabarbounis, plus the big summary of what changed |
| `response_AE.tex` | A1 to A20 |
| `response_R1.tex` | 1(a) to 1(e), 2(a) to 2(f), 3(a) to 3(d), 4(a) to 4(d), and the 10 smaller comments |
| `response_R2.tex` | C1 to C6, D1 |
| `response_R3.tex` | M1(a) to M1(c), M2(a) to M2(d), m1 to m3 |

Build with `./build.sh`. `enumitem` is not in this TeX installation, so list
spacing is set directly in `preamble.tex`.

## House rules

* **No hyphens** anywhere in our own prose. Referee quotes keep theirs, since
  they are verbatim.
* Every response says what was done, not what could be done.
* Four flags mark responses that need a second read before submission:
  `\concede`, `\correction`, `\newresult`, `\open`.

## Numbers still missing

`\tbd{}` marks them and they print in bold, so they cannot be missed on a read
through. Currently two, both the same object:

* the Housing First arm of the Costantini validation, in `response_editor.tex`
  and `response_AE.tex`
* the Treatment First arm of the same

Both come from `hftf_exper` once the calibration finishes.

## What was added after the first draft

`\thisround` marks every place where something that was a plan in the first draft
of these letters is now built and running. There are eleven, across four letters,
and `response_editor.tex` section 0 is the overview: the taste for drugs no longer
changes with addiction in the code as well as on paper, the housing access
elasticity has a parameter of its own, children are valued at every age rather
than at a terminal date, four hazards vary with age, homeownership is out, the
drug supply curve is finite, three numbers were wrong and are corrected, and the
homelessness disamenity has been dropped rather than priced at zero.

That last one is a change of mind against Referee 2, who asked for it and whom we
agreed with at the time. It is argued in `response_R2.tex` under C2 and offered
back: if he would still prefer it carried and reported across a range, restoring
it is small.

## The four places we push back

Worth reviewing together, because pushing back after a rejection is the part
most likely to go wrong in tone.

1. **Costantini (AE, A14).** Neither of his coefficients is our Experiment 1:
   both are local average treatment effects against no housing intervention, so
   both live on the generosity margin. And his Treatment First is Grant and Per
   Diem, time limited transitional housing, whose null he himself attributes to
   the expiry. We do not rest on the argument: we run both of his experiments in
   the model.
2. **Abramson and Van Nieuwerburgh (AE, A15).** Their 2,500 dollars a month is
   an assumption inside their calibration, stated as such, with the components
   in their footnote 11. It cannot validate our number. We report the comparison
   and describe it accurately.
3. **R1 comment 2(c)(i).** His 74 per cent is measured over people with a use
   disorder; the model figure he compares it against is over people who use.
   Different populations. We target both, separately, which is a sharper test.
   His underlying complaint was right.
4. **R1 smaller comment 1.** The cap was on initiation, not on use, so it is not
   inconsistent with the age profile of use. But the previous draft used one word
   for both, so the confusion is ours, and a hard truncation was a poor way to
   represent a smooth regularity in any case. Replaced by an age profile.

## Things we tell them we got wrong

Listed in `response_editor.tex` section 3. Six items. Two of them, the
unemployment rate given a substance use disorder and the homelessness mortality
multiplier, biased the previous version toward R1's rival hypothesis in comment
1(d), which is worth stating plainly rather than burying.
