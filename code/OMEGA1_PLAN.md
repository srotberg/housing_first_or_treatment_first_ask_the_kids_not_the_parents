# THE omega_c = 1 EXPERIMENT AND THE MISSING CONTRACT: THE PLAN (6 November)

Written at the author's request ("write out a plan based on our discussion and put in the repo so you dont forget
it"). Times in UTC-4. The running log stays in CALIBRATION_STATE.md; this file is the plan.

## 1. The question

The author, comments on the AE letter (6 November): "we need to understand why welfare rises when omega_c is
higher...and if it rises even when omega_c=1", "I think that with omega_c=1 there are still welfare gains even with
piv and pv held fixed because the child cannot control the parent's decision", "it's a missing market to contract
with the child", "we really have to understand this point before sending this".

**The story to test.** Even at omega_c = 1 the child and the parent are two people. A parent who weighs its child
exactly like itself still trades the child's childhood off against its own drug use, which the child does not value.
A child would pay its parent to abstain if it could borrow against its future income and repay as an adult; it
cannot (children cannot borrow, contract or commit), so that contract is missing (Becker and Murphy, 1988). The
sobriety condition is a crude substitute: every generation is restricted as a parent after benefiting as a child.
Behind the veil, a newborn gets the benefit first (childhood) and bears the cost about 25 years later (its own
restriction as a parent), discounted. So, with pi_V and the drug price held, the PREDICTION is: parents lose (by
revealed preference: the rational, forward-looking point still holds for the parent's own welfare) and newborns
can gain, through childhood (C) against adult life (A).

**Agreed framing (the author, "yes, i think this is good"):**
- Terminology: "a missing intergenerational contract", or "the condition acts as an intergenerational compact that
  a child cannot write with its parent". NOT "intertemporal substitution".
- The condition is NOT the contract: no money changes hands; it is blunter. It also stops parents whose drug use is
  worth more to them than any child could pay, and for those families the restriction is a loss.
- It is not a Pareto gain: the parents alive at the reform pay without the childhood benefit (the mirror image of
  the first old generation under pay-as-you-go). The case rests on the newborn criterion.
- At omega_c = 1 the criterion counts childhood in the newborn's own life (C) and again through V at age 1, which
  holds its weight on its own child (Bernheim, 1989, on double counting). Report the C / A split beside the
  parents' loss, not only the net gain, and say this in Section 6.1.
- "Chiefly": at the benchmark omega_c the externality is still the main reason. Frame as: the case for Treatment
  First survives without any externality, because a child cannot contract with its parent; the externalities
  measured in the data make it larger. Only if the run confirms it.

## 2. The runs

| stage | what | how | expected (UTC-4) |
|---|---|---|---|
| 1 | b scan at omega_c = 1, target the benchmark's own users 8.956 (results/reference/hf_2c_omega_0.085) | `bash code/remote_omega_point.sh 1.0 <b> 1.0 "" 2 omega1_2c`, b = 0.00380, 0.00393, 0.00406, 0.00419, four Sonnet workers launched 10:47 (sessions in CALIBRATION_STATE.md) -> results/omega1_2c/ | ~15:30, 6 Nov |
| 1b | the benchmark at the interpolated b* (skip if a point is within 0.1 pp); then commit `results/omega1_2c/send_bench_<tag>` for its files, `release_<tag>` for the others | same script | ~20:00, 6 Nov |
| 2 | the detection rate at which 61 percent of the users facing the screen stop on impact (Mehay and Pacula's stayers), as the main calibration does | the run_whostops_C_pscan2.sh / run_whostops_C_points.sh machinery with REF = the omega_c = 1 benchmark (a copy, not an edit) | ~midnight |
| 3a | Housing First at omega_c = 1 (null, corrected build), and Treatment First with pi_V AND the drug price HELD; start at detection 0.20 as soon as the benchmark is ready, in parallel with stage 2, and re-run at the calibrated rate if it differs | remote_nish_nodes_Cu.sh pattern (a copy), BENCH_OMEGA 1.0, BENCH_B b* | early 7 Nov |
| 3b | the other three columns, as Table 5 (the author: "piv and pv held, piv held and pv not, pv held and piv not, and both not. like we did with the others"): pi_V held / price clears; price held / pi_V clears; both clear | the decomp_2c_shares_Cu pattern (arm_fixboth, arm_fixp, arm_fixpv, arm_tf) | ~14:00, 7 Nov |
| 4 | per column: newborn CEV, its split into childhood (C) and adult life (A), the externality and the counted part, the parents' own welfare, drug use, SUD, homelessness, children in a homeless shelter, pi_V, price | export_nish_parts.py / export_results.py pattern; welfare_nok.cev_free against the omega_c = 1 benchmark's own curve | after 3b |

Also: detection 0.05 in the main economy already exists (results/counterfactuals_2c/tf_pdet05_Cu, accepted 17 Oct:
drug use -8.9, SUD -8.2, homelessness -3.6 percent, newborn CEV +1.01 on the paper's measure). Its impact share
(who stops at 0.05) is running: `bash code/deter_2c/run_whostops_C_points.sh 0.05`, session_019aHjYeFNdEjhqxwQ7QNCXn
-> results/whostops_2c_C_pts_0p05.

Keep the author posted after each stage (b scan, benchmark, first answer, clearing columns). A check-in fires every
two hours (send_later).

## 3. The paper, once the results are in (in red; numbers as @@names@@; directions from compare())

The author: "the experiment should come also in the paper", "the introduction as well and the abstract should be
slightly rewritten", "we might also need to add to the literature something about the contracting between children
and their parents", "use my academic paper writing style" (srotberg/examples_of_my_own_writing_style,
academic_papers/, and things_I_do_not_want.md). About 3 to 4 pages in all, if the run confirms the story; a
footnote if it does not.

1. **A new subsection after the main long-run experiment** (Section 6.2): omega_c = 1, the four columns, C / A and
   the parents. About 1.5 to 2 pages with one table.
2. **Introduction**: one paragraph with the story and the result; soften "moral hazard alone does not justify it;
   externalities do".
3. **Abstract**: two or three sentences, under 150 words.
4. **Sections 6.2 and 6.3**: reword the 10 to 15 sentences that make the externality the only reason; reinterpret
   the counted part of Table 6.
5. **Section 6.1**: one or two sentences on the criterion at omega_c = 1 (double counting).
6. **Section 7**: a paragraph on the lesson.
7. **Section 2, "Parental altruism towards children"**: two or three sentences on contracting between children and
   parents: Becker and Murphy (1988, JLE, "The Family and the State"); Boldrin and Montes (2005, REStud, "The
   Intergenerational State"); Rangel (2003, AER, "Forward and Backward Intergenerational Goods"); Samuelson (1958)
   and Cigno (1993) as background. VERIFY EACH REFERENCE before it goes in.
8. **Remove the omega_c = 0.69 footnote** (the author: "then we can remove the footnote on omega_c=0.689") and every
   pointer to it: the letters' A6, the robustness lists ("a weight on the child of 0.69", "raise the weight on the
   child" in changes.tex item 14), R2 and R3 where they cite footnote 28.
9. **The quarter detection rate** in footnote fn:halfrate (now, not waiting): the long-run numbers above, and the
   impact share when results/whostops_2c_C_pts_0p05 lands (export_results.py / export_whostops.py, new names).

## 4. The letters (srotberg/hf_or_tf_red_reviews, responses_round1/)

- Updates in BLUE (`\upd{}` in preamble.tex), not red. The shared block (changes.tex, ai_note.tex) changes once for
  all five letters. Acronyms through `\acr{}` so each is spelled out once per letter.
- Remove every [Conceded.], [Still open.], [New result.] flag; explain why I did not do what was asked, and be less
  apologetic (the author, on every letter).
- "A new submission", not a revision or resubmission.
- Use "homeless shelter", not "shelter", for the homeless state.
- Once the omega_c = 1 results are in: the story in the shared block, the AE letter's A6 (now a placeholder: "I am
  testing this further at a weight of one"), and every letter that touches why Treatment First wins.
- AE letter: all 142 comments applied (6 November), except those that wait for omega_c = 1.
- Editor, R1, R2, R3: the author's comment PDFs arrived 6 November; apply them next.

## 5. Open questions for the author (asked in chat, 6 November)

- The SMI use ratio: the paper compares the model's 2.64 with 2.44, but the 2.44 uses a broader definition of use;
  on the model's definition the data give about 4.51. So it is not a match, and I left it out of the micro evidence.
- Users' age: 34.6 against 39.6 is five years, ten on the model's definition (44.6); "slightly younger" would
  understate it, so the letter says "younger".
- Milby's housed against unhoused ratio (1.47 against 1.45) is a calibration target, so the paper cannot list it as
  validation; the letters now say the model matches it, as a target.
- Cohen (2024, AEJ: Applied), Brounstein and Wieselthier (2026, UC Berkeley working paper, labour market effects of
  unconditional housing in Los Angeles) and Humphries et al. (2026, structural eviction model) are relevant; I
  recommend citing them in Section 2 rather than explaining why not.
- Vaillant: the letter now justifies it (a long-run rate; the baseline is scaled by housing and treatment). Saying
  that a faster recovery would favour Treatment First needs a run; offered, not done.
- False positives: the letter now says the author explored the model with them (his words); the paper reports no
  such run.
- Rental sizes (AE A4): the model puts 1.1, about 13 and 85.7 percent of housed households in the three sizes,
  against 13.2, 24.1 and 62.7 percent of occupied units by bedrooms in the 2023 ACS (B25042).
